from PyQt5.Qt import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog
import random as rnd
import math
from ClientServer import ServerThread, ThreadClient
from Intity import ConnData
from Assoc import AssoGui
import os

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)



def generateMP():
    M = rnd.randint(2,9)
    P = math.ceil(math.log(math.pow(2,64),M))
    return M, P


class MainGui(QMainWindow):
    def __init__(self, id, minsup, dom, db_url, save_url,is_server=False):
        super(MainGui,self).__init__()
        loadUi('app.ui', self)
        self._id = id
        self.minsup = minsup
        self.dom = dom
        self.lineEdit_db_url.setText(db_url)
        self.lineEdit_save_url.setText(save_url)
        self._init_butt_acts()
        self._init_react()
        self._init_vals(is_server)
        self._connData = None
        self._thread = None
        self._thread_obj = None
        self._assoc = None
        self.th = None
        self.pd_res = None

    def _init_vals(self, is_server):
        self.checkBox_server.setChecked(is_server)
        self.spinBox_minsup.setValue(self.minsup)
        self.spinBox_dom.setValue(self.dom)
        self._progress_bar_visibility(False)
        self._result_bt_visibility(False)
        self._log_info_bt_visibility(False)
        M, P = generateMP()
        self.spinBox_M.setValue(M)
        self.spinBox_P.setValue(P)

    def _init_butt_acts(self):
        self.BT_start.clicked.connect(self._start_clicked)
        self.pushButton_results.clicked.connect(self._open_assoc)
        self.pushButton_results_file.clicked.connect(self._open_results)
        self.pushButton_Log.clicked.connect(self._open_log)
        self.pushButton_info.clicked.connect(self._open_info)
        self.pushButton.clicked.connect(self._open_browse_db_file)
        self.pushButton_3.clicked.connect(self._open_browse_save_file)

    def _init_react(self):
        self.spinBox_minsup.valueChanged.connect(self._minsup_change)
        self.spinBox_dom.valueChanged.connect(self._dom_change)

    def _start_clicked(self):
        self.BT_start.setVisible(False)
        ip_port, conn_data = self._make_ip_port_conn_data()

        if self.checkBox_server.isChecked():
            self._thread_obj = ServerThread(ip_port[0],int(ip_port[1]),conn_data)
        else:
            self._thread_obj = ThreadClient(ip_port[0],int(ip_port[1]),conn_data)

        self._start_thread()

    def _progress_bar_visibility(self, vis: bool):
        self.progressBar.setVisible(vis)
        self.label_cs_prog.setVisible(vis)

    def _result_bt_visibility(self,vis : bool):
        self.pushButton_results_file.setVisible(vis)
        self.pushButton_results.setVisible(vis)

    def _log_info_bt_visibility(self,vis : bool):
        self.pushButton_info.setVisible(vis)
        self.pushButton_Log.setVisible(vis)

    def _input_visibility(self,enbl : bool):
        self.lineEdit_IPPort.setEnabled(enbl)
        self.spinBox_minsup.setEnabled(enbl)
        self.spinBox_dom.setEnabled(enbl)
        self.spinBox_M.setEnabled(enbl)
        self.spinBox_P.setEnabled(enbl)
        self.lineEdit_db_url.setEnabled(enbl)
        self.lineEdit_save_url.setEnabled(enbl)
        self.pushButton.setEnabled(enbl)
        self.pushButton_3.setEnabled(enbl)
        self.checkBox_server.setEnabled(enbl)


    def _make_ip_port_conn_data(self):
        M,P = 6,30
        ip_port = self.lineEdit_IPPort.text().split(',')
        if ip_port[0] == 'IP':
            ip_port[0] = '127.0.0.1'
        if ip_port[1] == 'Port':
            ip_port[1] = '7777'
        db_url = str(self.lineEdit_db_url.text())
        save_url = str(self.lineEdit_save_url.text())
        self._connData = ConnData(self.dom,self.minsup,db_url,save_url,M,P,id= self._id)
        return ip_port, self._connData

    def _open_browse_db_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        db_url, _ = QFileDialog.getOpenFileName(self, "open Database", "",
                                                "Pkl Files (*.pkl)", options=options)
        if db_url:
            self.lineEdit_db_url.setText(db_url)

    def _open_browse_save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        save_url, _ = QFileDialog.getSaveFileName(self, "save result to", "",
                                                "Xlsx Files (*.xlsx)", options=options)
        if save_url:
            self.lineEdit_save_url.setText(save_url)

    def _minsup_change(self,v= None):
        self.minsup = v
        self.can_start()

    def _dom_change(self,v= None):
        self.dom = v
        self.can_start()

    def can_start(self):
        if 0 < self.minsup <= self.dom:
            self.BT_start.setEnabled(True)
        else:
            self.BT_start.setEnabled(False)

    # def updatep(self, n):
    #     self.spinBox_minsup.setValue(n)

    def _open_assoc(self):
        self._assoc = AssoGui(itemset= self.pd_res,minsup= self.minsup)
        self._assoc.ComputeAsso()
        self._assoc.show()

    def _open_results(self):

        os.startfile(str(self.lineEdit_save_url.text()))

    def _open_log(self):
        os.startfile(self._connData.log_url)

    def _open_info(self):
        os.startfile(self._connData.info_url)

    def _start_thread(self):
        self._thread = QThread()
        self._input_visibility(False)
        self._thread_obj.moveToThread(self._thread)
        self._connect_sig()
        self._thread.started.connect( self._thread_obj.run)
        self._thread.start()

    def _connect_sig(self):
        self._thread_obj.add_msg.connect(self._add_msg)
        self._thread_obj.start_mining.connect(self._start_mining)
        self._thread_obj.finish_mining.connect(self._th_finish)
        self._thread_obj.start_ck_msg.connect(self._start_ck_msg)
        self._thread_obj.found_ck_msg.connect(self._found_ck_msg)
        self._thread_obj.found_Lk_msg.connect(self._found_lk_msg)
        self._thread_obj.start_cs_comp.connect(self._start_cs_comp)
        self._thread_obj.inc_cs_progress.connect(self._inc_cs_progress)
        self._thread_obj.finish_cs_comp.connect(self._finish_cs_comp)
        self._thread_obj.ch_rule.connect(self._change_rules)
        self._thread_obj.finish_algo.connect(self._finish_algo)
        self._thread_obj.update_vars.connect(self._update_vars)
        self._thread_obj.failed_to_connect.connect(self._failed_to_connect)

    @pyqtSlot(str)
    def _add_msg(self, msg):
        self.textBrowser.append(">{}\n".format(msg))

    def _th_finish(self,pd_res):
        print("mining finished")
        self.pd_res = pd_res
        self._progress_bar_visibility(False)
        self._result_bt_visibility(True)

    @pyqtSlot(int)
    def _start_ck_msg(self,i):
        self._add_msg("Start finding candidates to be L_{}".format(i))

    @pyqtSlot()
    def _start_mining(self):
        print("mining start")
        self._progress_bar_visibility(True)

    @pyqtSlot(int)
    def _found_ck_msg(self, n):
        self._add_msg("Found {} candidates".format(n))

    @pyqtSlot(int, int)
    def _found_lk_msg(self, i, n):
        self._add_msg("L_{0} found, there is {1} frequent itemsets of size {0}".format(i, n))

    @pyqtSlot(int)
    def _start_cs_comp(self,n):
        self.label_cs_prog.setText('CS Progress ({} ID vec):'.format(n))
        self.progressBar.setRange(0,n)
        self.progressBar.setValue(0)

    @pyqtSlot()
    def _inc_cs_progress(self):
        self.progressBar.setValue((self.progressBar.value() + 1))

    @pyqtSlot()
    def _finish_cs_comp(self):
        self.label_cs_prog.setText('No CS computations')
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 0)

    @pyqtSlot(bool)
    def _change_rules(self, is_master):
        old_r = 'Master'
        new_r = 'Slave'
        if not is_master:
            old_r, new_r = new_r, old_r
        self.textBrowser.append("-------------------------------------\n")
        self.textBrowser.append("Change rules: {} become {}\n".format(old_r, new_r))
        self.textBrowser.append("-------------------------------------\n")

    @pyqtSlot()
    def _finish_algo(self):
        self._log_info_bt_visibility(True)
        self.textBrowser.append("-------------------------------------\n")
        self.textBrowser.append("Finish  algorithm :)")
        self.textBrowser.append("-------------------------------------\n")

    @pyqtSlot()
    def _update_vars(self):
        self.spinBox_dom.setValue(self._connData.dom)
        self.spinBox_M.setValue(self._connData.M)
        self.spinBox_P.setValue(self._connData.P)

    @pyqtSlot()
    def _failed_to_connect(self):
        self._add_msg("failed to connect!")
        self._thread.terminate()
        self.BT_start.setVisible(True)
        self._input_visibility(True)

