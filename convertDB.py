import numpy as np
import pandas as pd
import math as mt
import random as rnd


class MyDB(object):
    def __init__(self, pd_db = None, pkl_url = None):
        self._pd_db = pd_db
        if pd_db is None:
            self._pd_db = pd.read_pickle(pkl_url)

        self._IDs = self._pd_db.index.values.tolist()
        self._np_db = self._pandasTonumpy(self._pd_db)

    def _pandasTonumpy(self,db):
        return np.array(db.values)

    def _numpyToPandas(self,numpydb,col_names):
        return pd.DataFrame(numpydb[:,1:], numpydb[:,0],col_names)

    def getPdDb(self):
        return self._pd_db

    def getNpVals(self):
        return self._np_db

    def getIDs(self):
        return self._IDs

    def getAtrrNames(self):
        return self._pd_db.columns

    def transactionNum(self):
        return len(self._IDs)

    def attrNum(self):
        return len(self.getAtrrNames())

    def fakeDB(self,max_dom,private_attr = None):
        if private_attr is None:
            dom = range(max_dom + 1)
            fake_IDs = list(set(dom) - set(self._IDs))
            noise = np.add(np.random.rand(1,self.attrNum()),0.7)[0]
            support = self.attrSupport() * noise
            fake_vals = (np.random.rand(len(fake_IDs),self.attrNum()) < support) + 0
            fake_trans = pd.DataFrame(fake_vals,fake_IDs,self._pd_db.columns)
            pd_db = self._pd_db.copy().append(fake_trans)
            return MyDB(pd_db.sort_index())
        else:
            return MyDB(self._pd_db.drop(private_attr,axis=1)).fakeDB(max_dom)

    def innerJoin(self,other_db):
        pd_join = pd.concat([self._pd_db, other_db], axis=1, join='inner')
        #print(MyDB(pd_join))
        return MyDB(pd_join)

    def IDsVector(self,dom,binary=False):
        if binary:
            id_vec = np.zeros(dom, dtype=bool)
            id_vec[self._IDs] = True
        else:
            id_vec = np.zeros(dom, dtype=int)
            id_vec[self._IDs] = 1
        return id_vec

    def __str__(self):
       return self._pd_db.__str__()

    def attrFrequency(self):
        return np.sum(self._np_db,axis=0)
    def attrSupport(self):
        return np.true_divide(self.attrFrequency(), self.transactionNum())





class convertDB(object):
    def __init__(self,txtpath):

        self._db = self._convert(txtpath)
        self._rows_num = self._db.shape[0]

    def _convert(self,txtpath):
        db = pd.read_csv(txtpath, sep=" ", header=None)
        self._n = db.shape[1]
        names = self._firstAttrNames(self._n)
        db.columns = names
        db = self._convNumericAttr(db,names)
        return self._attrToBinary(db,names)

    def _firstAttrNames(self,n):
        names = []
        for i in range(n):
            names.append("A{}".format(i + 1))
        return names

    def _convNumericAttr(self,db,names):
        make_col = lambda att, f: db[att].apply(lambda x: "{}{}".format(att,mt.floor(f(x))))

        db["A2"] = make_col("A2", lambda x : x /12)
        db["A5"] = make_col("A5", lambda x: x / 5000)
        db["A13"] = make_col("A13", lambda x: x / 25)

        for att in names:
            if isinstance(db[att][0],np.int64):
                db[att] = make_col(att, lambda x: x)
        return  db

    def _attrToBinary(self,db,names):
        binDB = pd.DataFrame()
        for attr in names:
           newattr = sorted(set(db[attr].values))
           for nattr in newattr:
               binDB[nattr] = db[attr].apply(lambda x: int(x == nattr))
        return binDB

    def get(self):
        return self._db

    def _getAsNumpy(self,db,idxs):
        idxs = np.array(idxs)
        vals = np.array(db.values)
        return np.column_stack((idxs, vals))

    def splitDB(self):
        db1_names = self._db.columns[:51]
        db2_names = self._db.columns[51:]
        db1 = self._splitAnd_delete_rows(db1_names)
        db2 = self._splitAnd_delete_rows(db2_names)
        return  [db1, db2]

    def _splitAnd_delete_rows(self,names,save_atlist_prec = 70):
        db = self._db[names]
        save_num = rnd.randint(mt.ceil(self._rows_num * (save_atlist_prec / 100)), self._rows_num)
        save_idxs = sorted(rnd.sample(range(self._rows_num), save_num))
        #save_idxs = sorted(rnd.sample(range(20), save_num))
        pd_db = db.iloc[save_idxs]
        return MyDB(pd_db)


if __name__=="__main__":
   # c = convertDB("german.data.txt")
    #c.get().to_pickle("DBs\\german.pkl")
    #cc = c.splitDB()
    #cc[0].getPdDb().to_pickle("DBs\\party1.pkl")
    #cc[1].getPdDb().to_pickle("DBs\\party2.pkl")
    #print(cc[0].getAtrrNames())
   aa = pd.read_pickle("DBs\\party1.pkl")
   bb = pd.read_pickle("DBs\\party2.pkl")

   print(aa.shape[0])
   print(bb.shape[0])

