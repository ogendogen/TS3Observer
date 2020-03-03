import time
import ts3
import io
from SQLManager import SQLManager
from datetime import datetime
from Logger import Logger
import sys
import traceback
import threading

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

def report_status():
    try:
        sql_manager.report_status()
        logger.log_info("Activity reported to database")
        threading.Timer(300.0, report_status).start()
    except Exception as e:
        logger.log_critical(str(e) + traceback.format_exc())

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
        logger.log_critical(str(e) + " " + traceback.format_exc())

def update_admin_clid(admins, admin_id, clid):
    for admin in admins:
        if admin["admin_id"] == admin_id:
            admin["admin_clid"] = clid
            break
    return admins

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

    report_status()
    keep_bot_alive()

    while True:
            event = ts3conn.wait_for_event()

            # Client connected
            if event[0]["reasonid"] == "0":
                name = event[0]["client_nickname"]
                clid = int(event[0]["clid"])
                client_groups = event[0]["client_servergroups"].split(",")
                uid = event[0]["client_unique_identifier"]
                clientinfo = f"{str(datetime.now())} Client {name} connected"
                print(clientinfo)
                logger.log_info(clientinfo)

                if len(intersection(group_ids, client_groups)) > 0: # If user is in any admin group
                    admin_id = [admin["admin_id"] for admin in admins if admin["admin_uid"] == uid] # Try to get admin id from admins
                    if len(admin_id) == 0: # Admin not registered
                        admin_id = sql_manager.add_new_admin(name, uid, clid) # Register new admin
                        admins.append({"admin_id": admin_id, "admin_name": name, "admin_uid": uid, "admin_clid": clid})
                    else:
                        admin_id = admin_id[0] # Admin already registered
                        admins = update_admin_clid(admins, admin_id, clid)
                        sql_manager.update_admin_clid(admin_id, clid)

                    sql_manager.save_admin_login(admin_id, int(time.time()))

            # Client disconnected
            elif event[0]["reasonid"] == "8":
                clid = int(event[0]["clid"])
                admin_id = [admin["admin_id"] for admin in admins if admin["admin_clid"] == clid] # Check if it's admin
                if len(admin_id) > 0: # If admin then save
                    sql_manager.save_admin_logout(admin_id, int(time.time()))

if __name__ == "__main__":
    try:
        logger = Logger()
        print("Logger created")

        sql_cfg = parse_cfg("ts3bot_sql.cfg")
        sql_manager = SQLManager(sql_cfg[0], sql_cfg[1], sql_cfg[2], sql_cfg[3])
        print("SQL manager created")

        query_cfg = parse_cfg("ts3bot_query.cfg")
        print("Bot launched")
        
        host = query_cfg[0]
        login = query_cfg[1]
        password = query_cfg[2]
        sid = query_cfg[3]

        start_bot(sql_manager, query_cfg[4])

    except Exception as e:
        print("Exception occured. Stopping")
        logger.log_critical(str(e) + " " + traceback.format_exc())
