import time
import ts3
import io
from SQLManager import SQLManager

def parse_cfg(fileName):
    with open(fileName) as file:
        lines = file.read().split("\n")
        lines.remove("")
        file.close()

        if len(lines) >= 5 and "," in lines[4]:
            lines[4] = lines[4].split(",")

        return lines

def intersection(a, b):
    return list(set(a) & set(b))

def start_bot(host, login, password, sid, sql_manager, groupids):
    with ts3.query.TS3Connection(host) as ts3conn:
            ts3conn.login(
                    client_login_name=login,
                    client_login_password=password
            )
            ts3conn.use(sid=sid)

            # Register for events
            ts3conn.servernotifyregister(event="server")

            admins = sql_manager.get_admins()

            while True:
                    event = ts3conn.wait_for_event()

                    # Client connected
                    if event[0]["reasonid"] == "0":
                        print("Client '{}' connected.".format(event[0]["client_nickname"]))
                        name = event[0]["client_nickname"]
                        clid = event[0]["clid"]
                        client_groups = event[0]["client_servergroups"].split(",")
                        uid = event[0]["client_unique_identifier"]

                        if len(intersection(groupids, client_groups)) > 0: # If user is in any admin group
                            admin_id = [admin["admin_uid"] for admin in admins if admin["admin_uid"] == uid] # Try to get admin id from admins
                            if len(admin_id) == 0: # Admin not registered
                                admin_id = sql_manager.add_new_admin(name, uid, clid) # Register new admin
                                admins.append({"admin_id": admin_id, "admin_name": name, "admin_uid": uid, "admin_clid": clid})
                            else:
                                admin_id = admin_id[0] # Admin already registered
                            sql_manager.save_admin_login(admin_id, int(time.time()))

                    # Client disconnected
                    elif event[0]["reasonid"] == "8":
                        clid = event[0]["clid"]
                        admin_clid = [admin["admin_clid"] for admin in admins if admin["admin_clid"] == clid] # Check if it's admin
                        if len(admin_clid) > 0: # If admin then save
                            sql_manager.save_admin_logout(clid, int(time.time()))

if __name__ == "__main__":

    sql_cfg = parse_cfg("ts3bot_sql.cfg")
    sql_manager = SQLManager(sql_cfg[0], sql_cfg[1], sql_cfg[2], sql_cfg[3])
    print("SQL connected")

    query_cfg = parse_cfg("ts3bot_query.cfg")
    print("Bot launched")
    start_bot(query_cfg[0], query_cfg[1], query_cfg[2], query_cfg[3], sql_manager, query_cfg[4])