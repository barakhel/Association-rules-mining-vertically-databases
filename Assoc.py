import numpy as np
import pandas as pd
from PyQt5.Qt import *
from PyQt5.uic import loadUi
from functools import reduce
from convertDB import MyDB
import sys



class AssoGui(QMainWindow):
    def __init__(self,itemset=None, xlsx_url=None,minsup = None):
        super(AssoGui,self).__init__()
        loadUi('assoGui.ui',self)
        self._init_butt_acts()
        if itemset is None:
           itemset = pd.read_excel(xlsx_url, index_col=0)
        if minsup is None:
            self.label_minsup.setText("minsup: undefined")
        else:
            self.label_minsup.setText("minsup: {}".format(minsup))

        self._itemset = MyDB(itemset)
        self._npitem = self._itemset.getNpVals() == 1
        self._att = self._itemset.getAtrrNames()

        self._range = np.arange(len(self._att))
        self.resize(750,400)

    def ComputeAsso(self,some = None):
        self.listWidget.clear()
        if not (some is None):
            idx = self._npitem @ some.T == np.sum(some)
            npitem = self._npitem[idx]
        else:
            npitem = self._npitem

        self.label_num.setText("number of itemsets: {}".format(npitem.shape[0]))
        for i in range(npitem.shape[0]):
          self.print_item(npitem[i])


    def print_item(self,item):
        att = ", ".join(self._att[self._range[item]])
        self.listWidget.addItem('{}{}{}'.format('{',att,'}'))

    def _init_butt_acts(self):
        self.pushButton.clicked.connect(self.butt_find_clicked)

    def butt_find_clicked(self):
        if self.lineEdit.text() == "":
            self.ComputeAsso()
        else:
            att = self.lineEdit.text().split(" ")
            some = np.array(list(map(lambda x: x in att,self._att))) + 0

            self.ComputeAsso(some)
