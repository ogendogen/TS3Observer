import pymysql

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        self.__db = pymysql.connect(host, user, password, dbname, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        self.__cursor = self.__db.cursor()

    def add_new_admin(self, admin_name, admin_uid, admin_clid):
        query = "INSERT INTO admin SET admin_name = %s, admin_uid = %s, admin_clid = %s"
        self.__cursor.execute(query, (admin_name, admin_uid, admin_clid))
        self.__commit()
        return self.__cursor.lastrowid

    def save_admin_login(self, admin_id, timestamp):
        query = "INSERT INTO activity SET activity_adminid = %s, activity_starttime = %s"
        self.__cursor.execute(query, (admin_id, timestamp))
        self.__commit()

    def save_admin_logout(self, admin_id, timestamp):
        query = "UPDATE activity SET activity_endtime = %s WHERE activity_endtime IS NULL AND activity_adminid = %s"
        self.__cursor.execute(query, (timestamp, admin_id))
        self.__commit()

    def get_admins(self):
        query = "SELECT admin_id, admin_name, admin_uid, admin_clid FROM admin"
        self.__cursor.execute(query)
        self.__commit()
        return list(self.__cursor.fetchall())

    def __commit(self):
        try:
            self.__db.commit()
        except:
            self.__db.rollback()