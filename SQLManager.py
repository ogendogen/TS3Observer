import pymysql

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        db = pymysql.connect(host, user, password, dbname, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        self.__cursor = db.cursor()

    def add_new_admin(self, admin_name, admin_uid, admin_clid):
        query = "INSERT INTO admin SET admin_name = %s, admin_uid = %s, admin_clid = %s"
        self.__cursor.execute(query, (admin_name, admin_uid, admin_clid))
        return self.__cursor.lastrowid

    def save_admin_login(self, admin_id, timestamp):
        query = "INSERT INTO activity SET activity_adminid = %s, activity_starttime = %s"
        self.__cursor.execute(query, (admin_id, timestamp))

    def save_admin_logout(self, clid, timestamp):
        query = "UPDATE activity SET activity_endtime = %s WHERE activity_endtime = null AND activity_adminid = (SELECT admin_id FROM admin WHERE admin_clid = %s)"
        self.__cursor.execute(query, (timestamp, clid))

    def get_admins(self):
        query = "SELECT admin_id, admin_name, admin_uid, admin_clid FROM admin"
        self.__cursor.execute(query)
        return list(self.__cursor.fetchall())