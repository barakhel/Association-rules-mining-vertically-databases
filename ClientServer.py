import socket
from ConnectionHandler import ConnectionHandlerServer, ConnectionHandlerClient
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
import pandas
from Statistics import Log, MiningStatistics


class ThreadStruct(QObject):
    add_msg = pyqtSignal(str)
    start_mining = pyqtSignal()
    finish_mining = pyqtSignal(pandas.DataFrame)
    ch_rule = pyqtSignal(bool)
    start_ck_msg = pyqtSignal(int)
    found_ck_msg = pyqtSignal(int)
    found_Lk_msg = pyqtSignal(int,int)
    start_cs_comp = pyqtSignal(int)
    inc_cs_progress = pyqtSignal()
    finish_cs_comp = pyqtSignal()
    finish_algo = pyqtSignal()
    update_vars = pyqtSignal()
    failed_to_connect = pyqtSignal()

    def __init__(self,host,port,connData):
        QObject.__init__(self)
        self._host = host
        self._port = port
        self._connData = connData
        self._log = Log(connData.log_url)

    def _encode(self,res):
        self._log.addSend(res)
        return "{}\n".format(res).encode('utf-8')

    def _decode(self,data):
        data = str(data.decode('utf-8'))[:-1]
        self._log.addReceive(data)
        return data

    def run(self):
        pass

    def _myreceive(self, c):
        chunks = []
        bytes_recd = 0
        MSGLEN = 40000000
        chunk = c.recv(min(MSGLEN - bytes_recd, 2048))
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
        # while bytes_recd < MSGLEN:
        while b'\n' not in chunk:
            chunk = c.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

class ServerThread(ThreadStruct):
    def __init__(self,host,port,connData):
        ThreadStruct.__init__(self,host,port,connData)
        self._host = host
        self._port = port
        self._connData = connData
        self._info = MiningStatistics()

        self._s = None

    def _start(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.bind((self._host, self._port))
        self._s.settimeout(50000)
        self._s.listen(10)
        # print("socket is listening")
        connected = True
        self.add_msg.emit('waiting for connection...')
        c, addr = self._s.accept()
        self._info.setConnStart()
        self.add_msg.emit('connected!')
        return c

    @pyqtSlot()
    def run(self):
        c = self._start()
        connectionHandler = ConnectionHandlerServer(self._connData,self._info,self)
        while True:
            data = self._myreceive(c)
            data = self._decode(data)
            if data == 'disconnect':
                c.close()
                self._s.close()
                self._log.finish()
                self._info.setConnEnd()
                self._info.save(self._connData.info_url)
                self.finish_algo.emit()
                break

            response = connectionHandler.handleConnection(data)
            c.send(self._encode(response))


class ThreadClient(ThreadStruct):
    def __init__(self,host,port,connData):
        ThreadStruct.__init__(self,host,port,connData)
        self._s = None
        self._info = MiningStatistics()

    def _initConnection(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((self._host, self._port))
        self._s.settimeout(50000)

        self._info.setConnStart()
        self.add_msg.emit('connected!')
        response = "connected"
        self._s.send(self._encode(response))
        self._connectionHandler = ConnectionHandlerClient(self._connData,self._info,self)

    @pyqtSlot()
    def run(self):

        self.add_msg.emit('try to connect...')
        try:
            self._initConnection()
        except:
            self.failed_to_connect.emit()
            return

        while True:
            data = self._myreceive(self._s)
            data = self._decode(data)
            response = self._connectionHandler.handleConnection(data)
            self._s.send(self._encode(response))
            if response == "disconnect":
                self._s.close()
                self._log.finish()
                self._info.setConnEnd()
                self._info.save(self._connData.info_url)
                self.finish_algo.emit()
                break