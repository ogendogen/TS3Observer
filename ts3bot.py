import time
import ts3
import io
from SQLManager import SQLManager

def parse_cfg(fileName):
    with open(fileName) as file:
        lines = file.read().split("\n")
        lines.remove("")
        file.close()
        return lines

def start_bot(host, login, password, sid, sql_manager):
    with ts3.query.TS3Connection(host) as ts3conn:
            ts3conn.login(
                    client_login_name=login,
                    client_login_password=password
            )
            ts3conn.use(sid=sid)

            # Register for events
            ts3conn.servernotifyregister(event="server")

            while True:
                    event = ts3conn.wait_for_event()

                    # Client connected
                    if event[0]["reasonid"] == "0":
                        print("Client '{}' connected.".format(event[0]["client_nickname"]))
                        clid = event[0]["clid"]

                    # Client disconnected
                    elif event[0]["reasonid"] == "8":
                        clid = event[0]["clid"]

if __name__ == "__main__":

    sql_cfg = parse_cfg("ts3bot_sql.cfg")
    sql_manager = SQLManager(sql_cfg[0], sql_cfg[1], sql_cfg[2], sql_cfg[3])
    print("SQL connected")

    query_cfg = parse_cfg("ts3bot_query.cfg")
    print("Bot launched")
    start_bot(query_cfg[0], query_cfg[1], query_cfg[2], query_cfg[3], sql_manager)