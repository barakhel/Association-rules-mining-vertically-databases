import datetime as dtime
import time



class MiningStatistics(object):
    def __init__(self):
        self.conn_start = None
        self.conn_end = None
        self.mining_start = None
        self.mining_end = None
        self.mining_work = None
        self.work_buff = None
        self.itemsets = 0
        self.cross_itemsets = 0

    def setConnStart(self):
        self.conn_start = dtime.datetime.now()
    def setConnEnd(self):
        self.conn_end = dtime.datetime.now()
    def totalConn(self):
        return self.conn_end - self.conn_start
    def setMiningStart(self):
        self.mining_start = dtime.datetime.now()
        self.mining_work = self.mining_start - self.mining_start

    def setMiningEnd(self):
        self.mining_end = dtime.datetime.now()

    def totalMining(self):
        return self.mining_end - self.conn_start
    def setItemsets(self,n):
        self.itemsets = n

    def setCrossItemsets(self, n):
        self.cross_itemsets = n

    def miningWorkStart(self):
        self.work_buff = dtime.datetime.now()

    def miningWorkEnd(self):
        self.mining_work += dtime.datetime.now() - self.work_buff

    def str_info(self):
        a0 = self.conn_start.time()
        a1 = self.conn_end.time()
        a2 = self.totalConn()
        a3 = self.mining_start.time()
        a4 = self.conn_end.time()
        a5 = self.totalMining()
        a6 = self.mining_work
        a7 = a5 - self.mining_work
        a8 = self.itemsets
        a9 = self.cross_itemsets
        return """
        ================================================
        start connection at: {0}
        end connection at: {1}
        total connection time: {2}
        ------------------------------------------------
        start mining at: {3}
        end mining at: {4}
        total mining time: {5}
        
        time complexity in mining: {6}
        communication complexity in mining: {7}
        ------------------------------------------------
        total Number of frequent itemset: {8}
        number of cross frequent itemset: {9}
        ================================================
        """.format(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9)

    def save(self,url):
        file = open(url,'w')
        file.write(self.str_info())
        file.close()




class LogInterface(object):
    def __init__(self,url):
        object.__init__(self)
        self._url = url
        self._file = open(self._url,'w')
        self._MAX_BUFF = 100000

    def _addToLog(self,s):
        self._file.write(s)

    def finish(self):
        self._file.close()


class LogConn(LogInterface):
    def __init__(self,n):
        LogInterface.__init__(self,n)
        self._buff = ""
    def _addTimeStamp(self,s):
      return "{} - {}\n".format(dtime.datetime.now(),s)

    def _addToBuff(self,s):
        self._buff += self._addTimeStamp(s)
        if len(self._buff) > self._MAX_BUFF:
            self._addToLog(self._buff)
            self._buff = ""

    def addReceive(self,s):
            self._addToBuff('receive: ' + s)

    def addSend(self,s):
        self._addToBuff('send: ' + s)

    def finish(self):
        self._addToLog(self._buff)
        self._buff = ""
        LogInterface.finish(self)


class Log(LogConn):
    def __init__(self,n):
        LogConn.__init__(self,n)

