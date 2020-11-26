#!/usr/bin/env python3
import time
import ts3
import io
from SQLManager import SQLManager
from datetime import datetime
from Logger import Logger
import sys
import traceback
import threading
import os

# Global TS3 handler object and connection details
global ts3conn
global host
global login
global password
global sid
global logger

def parse_cfg(file_name):
    with open(file_name) as file:
        lines = file.read().split("\n")
        lines.remove("")
        file.close()

        if len(lines) >= 5 and "," in lines[4]:
            lines[4] = lines[4].split(",")

        return lines

def intersection(a, b):
    return list(set(a) & set(b))

def killSelf():
    if os.name == "nt":
        os.system("taskkill /im py.exe /f")
    elif os.name == "posix":
         os.system("pkill python3.8")

def report_status():
    try:
        sql_manager.report_status()
        logger.log_info("Activity reported to database")
        threading.Timer(300.0, report_status).start()
    except Exception as e:
        logger.log_info("Exception in report_status occured")
        logger.log_critical(str(e) + traceback.format_exc())
        killSelf()

def keep_bot_alive():
    try:
        if not ts3conn.is_connected():
            ts3conn.open(host)
            ts3conn.login(
                client_login_name = login,
                client_login_password = password
            )
            ts3conn.use(sid=sid)
            ts3conn.servernotifyregister(event="server")

        ts3conn.send_keepalive()
        threading.Timer(60.0, keep_bot_alive).start()
    except Exception as e:
        logger.log_info("Exception in keep_bot_alive occured")
        logger.log_critical(str(e) + " " + traceback.format_exc())
        killSelf()

def update_admin_clid(admins, admin_id, clid):
    for admin in admins:
        if admin["admin_id"] == admin_id:
            admin["admin_clid"] = clid
            break
    return admins

def prepare_players(clients, db_clients):
    # Transform raw data into dicts
    final_clients = dict()
    final_db_clients = dict()
    for client in clients:
        final_clients[client["clid"]] = client["client_nickname"]
    for db_client in db_clients:
        final_db_clients[db_client["player_clid"]] = db_client["player_name"]

    # Make set difference
    player_to_add = list()
    for client_clid, client_nickname in final_clients.items():
        if client_nickname not in set(final_db_clients.values()):
            player_to_add.append([client_clid, client_nickname])

    player_to_remove = list()
    for client_clid, client_nickname in final_db_clients.items():
        if client_nickname not in set(final_clients.values()):
            player_to_remove.append([client_clid, client_nickname])

    # Execute SQL
    sql_manager.insert_players(player_to_add)
    sql_manager.remove_players(player_to_remove)

    # Log info
    logger.log_info("Players prepared on boot")

def is_player_valid(name):
    blocked = ["KILLER", "CSKatowice BOT", "Unknown", "serveradmin", "GameTracker", "TS3index.com #242738"]
    return name not in blocked

def start_bot(sql_manager, group_ids):
    global ts3conn
    global host
    global login
    global password
    global sid
    ts3conn = ts3.query.TS3Connection(host)
    ts3conn.login(
            client_login_name = login,
            client_login_password = password
    )
    ts3conn.use(sid=sid)

    # Register for events
    ts3conn.servernotifyregister(event="server")

    admins = sql_manager.get_admins()
    clients = ts3conn.clientlist(uid=True)
    sql_manager.fix_old_admins(clients, admins)

    # todo: match players on server with players in db on restart
    dbClients = sql_manager.get_players()
    prepare_players(clients, dbClients)

    report_status()
    keep_bot_alive()

    while True:
            event = ts3conn.wait_for_event()

            # Check if correct event
            if "reasonid" in event[0]:
                # Client connected
                if event[0]["reasonid"] == "0":
                    name = event[0]["client_nickname"]

                    if not is_player_valid(name):
                        continue
                    
                    clid = int(event[0]["clid"])
                    client_groups = event[0]["client_servergroups"].split(",")
                    uid = event[0]["client_unique_identifier"]
                    logger.log_info(f"Client {name} connected")

                    if len(intersection(group_ids, client_groups)) > 0: # If user is in any admin group
                        admin_id = [admin["admin_id"] for admin in admins if admin["admin_name"] == name] # Try to get admin id from admins
                        if len(admin_id) == 0: # Admin not registered
                            admin_id = sql_manager.add_new_admin(name, uid, clid) # Register new admin
                            admins.append({"admin_id": admin_id, "admin_name": name, "admin_uid": uid, "admin_clid": clid})
                        else:
                            admin_id = admin_id[0] # Admin already registered
                            admins = update_admin_clid(admins, admin_id, clid)
                            sql_manager.update_admin_clid(admin_id, clid)

                        sql_manager.save_admin_login(admin_id, int(time.time()))

                    # Save any player entered to server event
                    if name != "Unknown" and name != "KILLER":
                        sql_manager.add_new_player(clid, name)

                # Client disconnected
                elif event[0]["reasonid"] == "8":
                    clid = int(event[0]["clid"])
                    admin_id = [admin["admin_id"] for admin in admins if admin["admin_clid"] == clid] # Check if it's admin
                    if len(admin_id) > 0: # If admin then save
                        sql_manager.save_admin_logout(admin_id, int(time.time()))
                    
                    # Remove any player leaving server
                    sql_manager.remove_player(clid)

if __name__ == "__main__":
    try:
        logger = Logger()
        logger.log_info("Logger created")

        dir_path = os.path.dirname(os.path.abspath(__file__))

        sql_cfg = parse_cfg(os.path.join(dir_path, "ts3bot_sql.cfg"))
        sql_manager = SQLManager(sql_cfg[0], sql_cfg[1], sql_cfg[2], sql_cfg[3])
        logger.log_info("SQL manager created")

        query_cfg = parse_cfg(os.path.join(dir_path, "ts3bot_query.cfg"))
        logger.log_info("Bot launched")
        
        host = query_cfg[0]
        login = query_cfg[1]
        password = query_cfg[2]
        sid = query_cfg[3]

        start_bot(sql_manager, query_cfg[4])

    except Exception as e:
        logger.log_info("Exception occured. Stopping " + str(e))
        logger.log_critical(str(e) + " " + traceback.format_exc())
        killSelf()
