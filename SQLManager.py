import pymysql

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__dbname = dbname
        self.fill_all_missing_disconnected_time()

    def add_new_admin(self, admin_name, admin_uid, admin_clid):
        query = "INSERT INTO admin SET admin_name = %s, admin_uid = %s, admin_clid = %s"
        return self.__exec(query, (admin_name, admin_uid, admin_clid))

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

    def fill_all_missing_disconnected_time(self):
        query = "UPDATE activity SET activity_endtime = UNIX_TIMESTAMP() WHERE activity_endtime IS NULL"
        return self.__exec(query)

    def __exec(self, query, *args):
        db = pymysql.connect(self.__host, self.__user, self.__password, self.__dbname, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        db.ping(reconnect=True)
        
        cursor = db.cursor()
        cursor.execute(query, *args)

        result = self.__commit(db)
        if result:
            if query.startswith("SELECT"):
                return list(cursor.fetchall())
            elif query.startswith("INSERT"):
                return cursor.lastrowid
        db.close()

    def __commit(self, db):
        try:
            db.commit()
            return True
        except:
            db.rollback()
            return False