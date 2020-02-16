import pymysql

class SQLManager(object):

    def __init__(self, host, user, password, dbname):
        db = pymysql.connect(host, user, password, dbname)
        self.__cursor = db.cursor()

    def save_admin_login(self, name, uid, timestamp, clid = None):
        raise NotImplementedError

    def save_admin_logout(self, clid, timestamp):
        raise NotImplementedError

    def get_admins(self):
        raise NotImplementedError

    def __save_admin_clid(self, name, clid):
        raise NotImplementedError