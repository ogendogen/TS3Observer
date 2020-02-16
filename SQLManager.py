import pymysql

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        db = pymysql.connect(host, user, password, dbname, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        self.__cursor = db.cursor()

    def save_admin_login(self, name, uid, timestamp, clid = None):
        raise NotImplementedError

    def save_admin_logout(self, clid, timestamp):
        raise NotImplementedError

    def get_admins(self):
        query = "SELECT admin_name, admin_uid FROM admin"
        self.__cursor.execute(query)
        return self.__cursor.fetchall()

    def __save_admin_clid(self, name, clid):
        raise NotImplementedError