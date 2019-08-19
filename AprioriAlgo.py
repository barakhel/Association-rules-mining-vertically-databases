import numpy as np
from convertDB import MyDB


class Apriori(object):
    def __init__(self, db, minsup):
        self._db = db
        self._attr = 0
        self._minsup = minsup

    # pre: curr and next are different binary vectors of length m and k ones (k <= m)
    # pre: idx1 < idx2 where
    # idx1 = max(i) where curr[i] = 1
    # idx2 = max(i) where next[i] = 1
    # post: true <=> (curr[0 : idx1] = next[0 : idx1])
    def _cond(self, curr, next):
        idxs = np.argwhere(curr)  # find all the index i where curr[i] = 1
        kidx = idxs[-1, 0]  # find max(i) where curr[i] = 1
        return np.array_equal(curr[0:kidx], next[0:kidx])  # return true <=> (curr[0 : idx1] = next[0 : idx1])

    # pre: mtx is matrix of nXm
    # post: return nmtx of (n*2)Xm
    # post: nmtx[0:(n + 1),:] = mtx
    def _resizeMtr(self, mtx):
        return np.concatenate((mtx, np.zeros(np.shape(mtx), dtype=int)), axis=0)

    # pre: lastL is matrix of nXm with different line vectors
    # pre: for all line l in lastL, l is vector of length m with k-1 ones
    # pre: lastL lines sorted from largest to smallest
    # post: return matrix C with different line vectors, where
    # forall line l in C:
    # l vector of length m with k ones
    # exist i,j: l = lastL[i,:] | lastL[j,:]
    def _apriorigen_join(self, lastL):
        idx = 0
        c = np.zeros((2, np.size(lastL, axis=1)), dtype=int)  # init matrix c of 2Xm
        for i in range(np.size(lastL, axis=0)):
            curr = lastL[i, :]
            for nxt in lastL[i + 1:, :]:
                if self._cond(curr, nxt):
                    if idx == np.size(c, axis=0):
                        c = self._resizeMtr(c)
                    c[idx, :] = np.bitwise_or(curr, nxt)
                    idx = idx + 1
                else:
                    break

        return c[:idx, :]

    def _apriorigen_prun(self, lastL, c, k):
        subset_num_vec = np.sum((lastL @ c.T) == (k - 1), axis=0) == k
        return c[subset_num_vec, :]

    def apriorigen(self, lastL, k):
        cjoin = self._apriorigen_join(lastL)
        return self._apriorigen_prun(lastL, cjoin, k)

    def makeLk(self, c, k):
        frec = np.sum((self._db @ c.T) == k, axis=0)
        supported = frec >= self._minsup
        return c[supported, :]

    def initApriori(self):
        atr_num = np.size(self._db, axis=1)
        c = np.eye(atr_num, dtype=int)
        return self.makeLk(c, 1)

    def aprioriAlg(self):
        L = self.initApriori()
        LJoin = L
        k = 2
        while np.size(L, axis=0) != 0:
            ck = self.apriorigen(L, k)
            L = self.makeLk(ck, k)
            LJoin = np.concatenate((LJoin, L), axis=0)
            k = k + 1
        return LJoin


class Apriori2PartySmart(object):

    def __init__(self, ITD: MyDB, dom, minsup, FITD=None, LITD=None):
        self._ITD = ITD  # my database
        if LITD is None:
            self._LITD = ITD.innerJoin(FITD)  # my_db inner join other_db

        else:
            self._LITD = LITD

        self._minsup = minsup
        self._dom = dom  # max domin of the keys
        self._initVecs()
        self._apri = Apriori(self._LITD.getNpVals(), self._minsup)
        self._my_idx = []
        self._cross_idx = []
        self._k = 1
        self._initApriori()

    def getLITD(self):
        return self._LITD

    def _initVecs(self):
        self._vec_ids = self._ITD.IDsVector(
            self._dom)  # binary vector with size (dom + 1) and vec_id[i] = true <==> i index in ITD
        att_vec = list(x in self._ITD.getAtrrNames() for x in
                       self._LITD.getAtrrNames())  # binary list with size: (totel number if attributes) and atrr_vec[i] = true <==> atrribute i in LITD is attribute in ITD
        self.my_att_vec = np.array(att_vec, dtype=bool)  # att_vec as binary vector
        self.other_att_vec = (self.my_att_vec == False)  # other attributs vector

    # pre: _initApriori() was activated
    # post:
    #   return true <==>
    #   exist true value in _my_idx <==>
    #   exist l in _L with at list one attribute from my attributes
    def notAmptyL(self):
        return np.any(self._my_idx)

    def _initApriori(self):
        self._L = self._apri.initApriori()
        self._split_cross_gen()
        self._Ls = np.array(self._L[self._my_idx])
        self._k += 1

    def apriorigen(self):
        ck = self._apri.apriorigen(self._L, self._k)
        self._L = self._apri.makeLk(ck, self._k)
        self._split_cross_gen()
        id_check = self._idsToCheck(self._k)
        self._k += 1
        return id_check

    def getLs(self):
        return self._Ls

    def getCrossLs(self):
        self._L = self._Ls
        self._split_cross_gen()
        return self._Ls[self._cross_idx]

    def join_Cross(self, t_vecs):
        true_idx = np.logical_not(self._cross_idx)
        true_idx[self._cross_idx] = t_vecs
        self._my_idx[self._cross_idx] = t_vecs
        self._Ls = np.concatenate((self._Ls, self._L[self._my_idx]), axis=0)
        self._L = self._L[true_idx]

    def _split_cross_gen(self):
        my_vecs = (self._L @ self.my_att_vec) != 0
        other_vecs = (self._L @ self.other_att_vec) != 0
        self._cross_idx = np.logical_and(my_vecs, other_vecs)
        self._my_idx = (my_vecs + 0 + self._cross_idx) == 1

    def _idsToCheck(self, k):
        id_vec = (self._L[self._cross_idx] @ self._LITD.getNpVals().T) == k
        id_ext_vec = np.zeros((id_vec.shape[0], self._dom), dtype=bool)
        id_ext_vec[:, self._LITD.getIDs()] = id_vec
        return id_ext_vec

    def getAtrrNames(self):
        return self._LITD.getAtrrNames()

    def getK(self):
        return self._k

    def getCkSize(self):
        return np.sum(self._my_idx + self._cross_idx)

    def getLkSize(self):
        return np.sum(self._my_idx + 0)

    def getLsSize(self):
        return Ls.shape[0]
