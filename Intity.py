from AprioriAlgo import *
from SecureComp.SecureCompMaster import SecureCompMaster
from SecureComp.SecureCompSlave import SecureCompSlave


class ConnData(object):
    def __init__(self,dom,minsup,db_url,save_url,M = None,P = None,prime = None,id = 1):
        self.dom = dom
        self.minsup = minsup
        self.db_url = db_url
        self.save_url = save_url
        self.M = M
        self.P = P
        self.prime = prime
        self.log_url = 'log{}.txt'.format(id)
        self.info_url = 'info{}.txt'.format(id)

    def __str__(self):
        return """
        --------------------------------
        CONN DATA:
        dom: {}
        minsup:{}
        M: {}
        P: {}
        prime: {}
        -------------------------
        """.format(self.dom,self.minsup,self.M,self.P,self.prime)

    def toVars(self):
        return [self.P,self.M,self.prime,self.dom]
    def setVars(self,vars):
        self.P = vars[0]
        self.M = vars[1]
        self.prime = vars[2]
        self.dom = vars[3]

class Party(object):
    def __init__(self,db,conn_data: ConnData):
        self._db = db
        self._conn_data = conn_data
        self.apri = None

    def make_fake(self):
        return self._db.fakeDB(self._conn_data.dom).getPdDb()

    def setApri(self,fake):
        self.apri = Apriori2PartySmart(self._db, self._conn_data.dom,self._conn_data.minsup,fake)

    def setApri_revRol(self, LITD):
        self.apri = Apriori2PartySmart(self._db, self._conn_data.dom, self._conn_data.minsup, LITD= LITD)

    def getDbIndicator(self):
        return self._db.IDsVector(self._conn_data.dom, binary=True)

    def getDb(self):
        return self._db

    def getConnData(self):
        return self._conn_data

    def getMinsup(self):
        return self._conn_data.minsup


class Master(Party):
    def __init__(self,db,conn_data: ConnData):
        Party.__init__(self,db,conn_data)
        self.SC = SecureCompMaster()
        self.SC.init(conn_data.M,conn_data.P,conn_data.prime,conn_data.minsup,conn_data.dom)


class Slave(Party):
    def __init__(self,db,conn_data: ConnData):
        Party.__init__(self,db,conn_data)
        self.SC = SecureCompSlave()
        self.SC.init(conn_data.P, conn_data.M, db.IDsVector(conn_data.dom), conn_data.prime)



