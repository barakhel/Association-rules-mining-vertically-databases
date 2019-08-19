from DataHandler import DataHandlerMaster, DataHandlerSlave


class ConnectionHandlerServer(object):
    def __init__(self,conn_data,info,th):
        object.__init__(self)
        self._thread = th
        self._info = info
        self.dataHandler = DataHandlerMaster(th = self._thread,info = self._info,conn_data= conn_data)
        self.start = True

    def handleConnection(self, data):
        if self.start == True:
            self.start = False
            self._info.setMiningStart()
            return self.dataHandler.handleData(None)

        self._info.miningWorkStart()
        res = self.dataHandler.handleData(data)
        self._info.miningWorkEnd()

        if "FINISH" == res or res == "NoMining":
            self._thread.ch_rule.emit(True)
            new_slave = self.dataHandler.createSlave()
            if data != "NoMining" in res:
                new_slave.setApri_revRol(self.dataHandler.getMasterLITD())
            self.dataHandler = DataHandlerSlave(th = self._thread, slave=new_slave, pre=True)
            self._info.setMiningEnd()
        return res


class ConnectionHandlerClient(object):
    def __init__(self, conn_data, info, th):
        object.__init__(self)
        self._thread = th
        self.dataHandler = DataHandlerSlave(th= self._thread,conn_data= conn_data)
        self._info = info

    def handleConnection(self, data):
        if "FINISH" == data or data == "NoMining":
            self._info.setMiningStart()
            self._thread.ch_rule.emit(False)
            new_master = self.dataHandler.createMaster()
            if data != "NoMining" in data:
                new_master.setApri_revRol(self.dataHandler.getSlaveLITD())
            self.dataHandler = DataHandlerMaster(th= self._thread,info= self._info,master=new_master, pre=True, apri_is_init= data == "NoMining")
            return self.dataHandler.handleData(None)
        res =  self.dataHandler.handleData(data)
        if "FINISH" in res or data == "NoMining" in res:
            self._info.setMiningEnd()
            return "disconnect"
        return res