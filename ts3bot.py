import time
import ts3

def start_bot(host, login, password, sid):
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

if "__name__" == "__main__":
    host = "127.0.0.1"
    login = "login"
    password = "secret"
    serverid = 1
    start_bot(host, login, password, serverid)