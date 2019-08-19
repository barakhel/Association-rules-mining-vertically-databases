# 1. Check if mining is possible, using secure comp, where x is the server's transaction's indicator (phase1) serverClient
# 2. if so exchange fake DB (phase2) - serverClient
# 3. generate - apriori (phase3) - server
# 4. for each item set, check   freq

from AprioriAlgo import *
from Intity import Master, Slave
from enum import Enum
import pandas as pd
import json


class PHASES(Enum):
    SECURE_COMP_VARS = 0
    MINING_POSSIBLE = 1
    SECURE_COMP_VEC = 2
    SECURE_COMP_ITER = 4
    SECURE_COMP_RES = 3
    EXCHANGE_DB = 5
    START_CHECK_FREQUENT_ITEMSETS = 6
    CONTINUE_CHECK_FREQUENT_ITEMSETS = 7
    CHECK_FREQUENT_ITEMSETS_ANSWER = 8


class DataHandler(object):

    def __init__(self, th, conn_data=None, old_rule=None, pre=None):
        object.__init__(self)
        self._thread = th
        self._conn_data = conn_data
        if pre:
            self._conn_data = old_rule.getConnData()
            self._db = old_rule.getDb()
        else:
            self._conn_data = conn_data
            self._db = db = MyDB(pkl_url=self._conn_data.db_url)

    def dataParser(self, data):
        jsonObj = json.loads(data)
        phase = jsonObj["phase"]
        res = jsonObj["data"]
        if jsonObj["isDF"]:
            res = pd.read_json(res)
        elif jsonObj["isNpArr"]:
            res = np.array(res)
        if isinstance(res, str) and res == '':
            res = None
        return phase, res

    def constructFormat(self, phase, data=None, isNpArr=False, isDF=False):
        jsonObj = json.loads(""" {"phase" : [], "data" : [], "isNpArr" : [], "isDF" : []} """)
        jsonObj["phase"] = phase
        jsonObj["data"] = data
        jsonObj["isNpArr"] = isNpArr
        jsonObj["isDF"] = isDF
        if data is None:
            jsonObj["data"] = ""
        elif isDF:
            jsonObj["data"] = pd.DataFrame.to_json(data)
        elif isNpArr:
            jsonObj["data"] = np.array(data).tolist()
        return json.dumps(jsonObj)


class DataHandlerMaster(DataHandler):

    def __init__(self, th, info, conn_data=None, master=None, pre=False, apri_is_init=True):

        DataHandler.__init__(self,th,conn_data,master,pre)
        self.master = master
        self.Hs_iter = None
        self.preChecked = pre
        self._apri_init = apri_is_init
        self._info = info

        self._thread.add_msg.emit('===============')
        self._thread.add_msg.emit('==   Rule: Master   ==')
        self._thread.add_msg.emit('===============')

    def handleData(self, data= None,):
        res = data
        isNpArr = False
        isDF = False
        if data is None:
            if self.preChecked:
                phase = PHASES.MINING_POSSIBLE.value
            else:
                phase = PHASES.SECURE_COMP_VARS.value
        else:
            phase, res = self.dataParser(data)
        if phase == PHASES.SECURE_COMP_VARS.value:
            if res is None:
                # print("MASTER: sending secure comp variables ")
                from Prime import generatePrime
                self._conn_data.prime = generatePrime(2 * self._conn_data.dom)
                data = self._conn_data.toVars()
                isNpArr = True
            else:
                self._conn_data.setVars(res)
                self._thread.update_vars.emit()
                self.master = Master(self._db, self._conn_data)
                return self.handleData(self.constructFormat(PHASES.MINING_POSSIBLE.value))

        elif phase == PHASES.MINING_POSSIBLE.value:
            # print("MASTER: check if mining is possible")
            self.Hs_iter = self.master.SC.generatHs(np.array([self.master.getDbIndicator()]))
            self.checkIfMiningPossible = True
            # print("MASTER: start secure comp")
            return self.handleData(self.constructFormat(PHASES.SECURE_COMP_ITER.value))

        elif phase == PHASES.SECURE_COMP_VEC.value:
            isNpArr = True
            data = self.Hs_iter.computeZMinusMinsup(res)
            phase = PHASES.SECURE_COMP_RES.value

        elif phase == PHASES.SECURE_COMP_ITER.value:
            if self.Hs_iter.hasNext():
                isNpArr = True
                phase = PHASES.SECURE_COMP_VEC.value
                data = self.Hs_iter.next()
            elif self.checkIfMiningPossible and self.Hs_iter.getVectorResult()[0]:
                self.checkIfMiningPossible = False
                return self.handleData(self.constructFormat(PHASES.EXCHANGE_DB.value))

            elif self.checkFrequntItemsets:
                vector_result = self.Hs_iter.getVectorResult()
                self.master.apri.join_Cross(vector_result)
                self._thread.finish_cs_comp.emit()
                self._thread.found_Lk_msg.emit(self.master.apri.getK()-1,self.master.apri.getLkSize())
                return self.handleData(self.constructFormat(PHASES.CONTINUE_CHECK_FREQUENT_ITEMSETS.value))
            else:
                return 'NoMining'

        elif phase == PHASES.SECURE_COMP_RES.value:
            self.Hs_iter.setResult(res)
            self._thread.inc_cs_progress.emit()
            return self.handleData(self.constructFormat(PHASES.SECURE_COMP_ITER.value))

        elif phase == PHASES.EXCHANGE_DB.value:
            # print("MASTER: send DB")
            if res is not None:
                self.master.setApri(res)
                self.checkFrequntItemsets = True
                return self.handleData(self.constructFormat(PHASES.START_CHECK_FREQUENT_ITEMSETS.value))
            else:
                data = self.master.make_fake()
                isDF = True

        elif phase == PHASES.START_CHECK_FREQUENT_ITEMSETS.value:
            self._thread.start_ck_msg.emit(1)
            self._thread.found_Lk_msg.emit(self.master.apri.getK() - 1, self.master.apri.getLkSize())
            self._thread.start_mining.emit()
            return self.handleData(self.constructFormat(PHASES.CONTINUE_CHECK_FREQUENT_ITEMSETS.value))

        elif phase == PHASES.CONTINUE_CHECK_FREQUENT_ITEMSETS.value:
            if self.master.apri.notAmptyL():
                self._thread.start_ck_msg.emit(self.master.apri.getK())
                ids_to_check = self.master.apri.apriorigen()
                self._thread.found_ck_msg.emit(self.master.apri.getCkSize())
                self.Hs_iter = self.master.SC.generatHs(ids_to_check)
                self._thread.start_cs_comp.emit(self.Hs_iter.size())
                return self.handleData(self.constructFormat(PHASES.SECURE_COMP_ITER.value))

            self._saveResults(self._conn_data.save_url)
            return 'FINISH'

        return self.constructFormat(phase, data, isNpArr, isDF)

    def constructTrVector(self):
        return self._db.IDsVector(self._conn_data.dom) # binary vector with size (dom + 1) and vec_id[i] = true <==> i index in ITD

    def createSlave(self):
        return Slave(self._db,self._conn_data)

    def getMasterLITD(self):
        return self.master.apri.getLITD()


    def _saveResults(self,url):
        writer = pd.ExcelWriter(url, engine='xlsxwriter')
        master_freq = self.master.apri.getLs()
        cross = self.master.apri.getCrossLs()
        first_master_res = pd.DataFrame(master_freq, columns=self.master.apri.getAtrrNames())
        first_master_cross_res = pd.DataFrame(cross, columns=self.master.apri.getAtrrNames())
        first_master_res.to_excel(writer, sheet_name='all freq',header=self.master.apri.getAtrrNames())
        first_master_cross_res.to_excel(writer, sheet_name='cross freq', header=self.master.apri.getAtrrNames())
        writer.save()
        self._info.setItemsets(master_freq.shape[0])
        self._info.setCrossItemsets(cross.shape[0])
        self._thread.finish_mining.emit(first_master_res)


class DataHandlerSlave(DataHandler):

    def __init__(self,th,conn_data = None, slave = None, pre = False):
        DataHandler.__init__(self,th,conn_data,slave,pre)
        self.slave = slave
        self.preChecked = pre
        self._thread.add_msg.emit('==============')
        self._thread.add_msg.emit('==   Rule: Slave   ==')
        self._thread.add_msg.emit('==============')
        self._thread.add_msg.emit('Help Master to do mining')

    def handleData(self, data):
        isNpArr = False
        isDF = False
        phase, res = self.dataParser(data)

        if phase == PHASES.SECURE_COMP_VARS.value:
            isNpArr = True
            from Prime import generatePrime
            self._conn_data.prime = generatePrime(2 * self._conn_data.dom)
            mydata = self._conn_data.toVars()
            for i in range(4):
                res[i] = max(res[i],mydata[i])
            self._conn_data.setVars(res)
            self._thread.update_vars.emit()
            data = res
            self.slave = Slave(self._db,self._conn_data)

        elif phase == PHASES.SECURE_COMP_VEC.value:
            isNpArr = True
            data = self.slave.SC.computeVectorZ(res)

        elif phase == PHASES.SECURE_COMP_RES.value:
            data = self.slave.SC.checkIfMinsup(res)
            phase = PHASES.SECURE_COMP_RES.value

        elif phase == PHASES.EXCHANGE_DB.value:
            self.slave.setApri(res)
            isDF = True
            data = self.slave.make_fake()

        return self.constructFormat(phase, data, isNpArr, isDF)

    def createMaster(self):
        return Master(self._db,self._conn_data)

    def getSlaveLITD(self):
        return self.slave.apri.getLITD()





