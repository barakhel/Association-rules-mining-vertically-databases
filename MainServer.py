import sys
from PyQt5.Qt import *
from enum import Enum
from MainGui import MainGui


class InitialValServer(Enum):
    ID = 1
    MINSUP = 450
    DOM = 1100
    DB_URL = 'DBs\\p1.pkl'
    SAVE_RES = 'pq1.xlsx'


if __name__=="__main__":
    app1 = QApplication(sys.argv)
    w1 = MainGui(
        id=InitialValServer.ID.value,
        minsup=InitialValServer.MINSUP.value,
        dom=InitialValServer.DOM.value,
        db_url=InitialValServer.DB_URL.value,
        save_url=InitialValServer.SAVE_RES.value,
        is_server=True)

    w1.show()
    sys.exit(app1.exec_())