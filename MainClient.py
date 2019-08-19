import sys
from PyQt5.Qt import *
from enum import Enum
from MainGui import MainGui


class INITIAL_VAL_CLIENT(Enum):
    ID = 2
    MINSUP = 450
    DOM = 1100
    DB_URL = 'DBs\\p2.pkl'
    SAVE_RES = 'pq2.xlsx'

if __name__=="__main__":
    app1 = QApplication(sys.argv)
    w1 = MainGui(
        id=INITIAL_VAL_CLIENT.ID.value,
        minsup=INITIAL_VAL_CLIENT.MINSUP.value,
        dom=INITIAL_VAL_CLIENT.DOM.value,
        db_url=INITIAL_VAL_CLIENT.DB_URL.value,
        save_url=INITIAL_VAL_CLIENT.SAVE_RES.value,
        is_server=False)

    w1.show()
    sys.exit(app1.exec_())