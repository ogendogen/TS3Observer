import pymysql
import time

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__dbname = dbname
        self.__fill_all_missing_disconnected_time()

    def add_new_admin(self, admin_name, admin_uid, admin_clid):
        query = "INSERT INTO admin SET admin_name = %s, admin_uid = %s, admin_clid = %s ON DUPLICATE KEY UPDATE admin_name = %s, admin_uid = %s, admin_clid = %s"
        return self.__exec(query, (admin_name, admin_uid, admin_clid, admin_name, admin_uid, admin_clid))

    def save_admin_login(self, admin_id, timestamp):
        query = "INSERT INTO activity SET activity_adminid = %s, activity_starttime = %s"
        return self.__exec(query, (admin_id, timestamp))

    def save_admin_logout(self, admin_id, timestamp):
        query = "UPDATE activity SET activity_endtime = %s WHERE activity_endtime IS NULL AND activity_adminid = %s"
        return self.__exec(query, (timestamp, admin_id))

    def report_status(self):
        query = "UPDATE status SET last_report = UNIX_TIMESTAMP()"
        return self.__exec(query)

    def get_admins(self):
        query = "SELECT admin_id, admin_name, admin_uid, admin_clid FROM admin"
        return self.__exec(query)

    def __fill_all_missing_disconnected_time(self):
        query = "UPDATE activity SET activity_endtime = UNIX_TIMESTAMP() WHERE activity_endtime IS NULL"
        return self.__exec(query)
    
    def update_admin_clid(self, admin_id, admin_clid):
        query = "UPDATE admin SET admin_clid = %s WHERE admin_id = %s"
        return self.__exec(query, (admin_clid, admin_id))

    def fix_old_admins(self, clientslist, admins):
        for client in clientslist.parsed:
            clientUID = client["client_unique_identifier"]
            for admin in admins:
                if admin["admin_uid"] == clientUID:
                    self.save_admin_login(admin["admin_id"], int(time.time()))

    def add_new_player(self, player_clid, player_name):
        query = "INSERT INTO players SET player_clid = %s, player_name = %s, player_entered = UNIX_TIMESTAMP() ON DUPLICATE KEY UPDATE player_clid = %s, player_entered = UNIX_TIMESTAMP()"
        return self.__exec(query, (player_clid, player_name, player_clid))

    def remove_player(self, player_clid):
        query = "DELETE FROM players WHERE player_clid = %s"
        return self.__exec(query, (player_clid))

    def insert_players(self, players):
        for player in players:
            query = "INSERT INTO players (player_id, player_clid, player_name, player_entered) VALUES (null, %s, %s, UNIX_TIMESTAMP())"
            self.__exec(query, (player[0], player[1]))
        return True

    def remove_all_players(self):
        query = "TRUNCATE TABLE players"
        return self.__exec(query)

    def remove_players(self, players):
        players = ["'"+n[1]+"'" for n in players]
        str_players = '(' + ','.join(players) + ')'
        
        # I'm aware it may be unsafe, but that's only way it works
        query = "DELETE FROM players WHERE player_name IN " + str_players
        return self.__exec(query)

    def get_players(self):
        query = "SELECT player_clid, player_name FROM players"
        return self.__exec(query)

    def __exec(self, query, *args):
        db = pymysql.connect(self.__host, self.__user, self.__password, self.__dbname, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        db.ping(reconnect=True)
        
        cursor = db.cursor()
        cursor.execute(query, *args)

        result = self.__commit(db)
        ret_value = None
        if result:
            if query.startswith("SELECT"):
                ret_value = list(cursor.fetchall())
            elif query.startswith("INSERT"):
                ret_value = cursor.lastrowid

        db.close()
        return ret_value

    def __commit(self, db):
        try:
            db.commit()
            return True
        except:
            db.rollback()
            return False