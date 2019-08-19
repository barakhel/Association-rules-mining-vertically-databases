import numpy as np
from enum import Enum


class PROTOCOL_VARIABLES(Enum):
    P = 2
    M = 64


class SecureCompMaster(object):

    def __init__(self):
        object.__init__(self)
        self.init()

    def init(self,M=None,P=None,prime=None,minsup=None,dom=None):
        self._powerM = M
        self._baseP = P
        self._prime = prime
        self._minsup = minsup
        self._vectorsLen = dom

    def _generateVs(self,vecs):
        Vs = []
        for v in vecs:
            Vs.append(self._generateVectorsData(v))
        return Vs

    def _generateVectorsData(self,vec):
        V = np.random.random_integers(1,self._prime - 1,size= (self._powerM,vec.size))
        remainder = (self._prime - (np.sum(V, axis=0) % self._prime)) + vec
        for j in range(vec.size):
           i = np.random.choice(self._powerM, 2)
           x = remainder[j]
           if V[i[0], j] + remainder[j] != self._prime:
               V[i[0], j] = (V[i[0], j] + x) % self._prime
           elif V[i[1], j] + remainder[j] != self._prime:
               V[i[1], j] = (V[i[1], j] + x) % self._prime
           else:
               if x %2 != 0:
                   x = self._prime + x
               x = x/2
               V[i[0], j] = V[i[0], j] + x
               V[i[1], j] = V[i[1], j] + x

        return V

    def generatHs(self,vecs):
    ########################################
    # m = powerM, n = maxdom p = baseP     #
    # t = number of vectors to perform SC  #
    # returns: iterator over list (size t) #
    # on element H shape (m,p,n)           #
    ########################################
        Vs = self._generateVs(vecs)
        Hs =[]
        locationsList= []
        for i in range(len(Vs)):
            loc = self._generateLocationK()
            locationsList.append(loc)
            Hs.append(self._generateVectorH(Vs[i],loc))
        return CheckIterator(Hs,locationsList,self._minsup,self._prime)

    def _generateVectorH(self,V,loc):
        ######################################
        # m = powerM, n = maxdom, p = baseP  #
        # V: Matrix shape (m,n)              #
        # loc Vector shape (1,m)             #
        # loc elements in range (0,p)        #
        # returns: 3D Matrix shape (m,p,n)   #
        ######################################
        # generate secret location
        vectorH = np.random.random_integers(1,self._prime,size= (self._powerM,self._baseP,self._vectorsLen))
        for i in range(self._powerM):
            vectorH[i,loc[i]] = V[i]
        return vectorH

    def setPowerM(self, m):
        self._powerM = m

    def setPrime(self,prime):
        self._prime = prime

    def setBaseP(self, p):
        self._baseP = p


    def getPowerM(self):
        return self._powerM

    def getBaseP(self):
        return self._baseP

    def _generateLocationK(self):
         return np.random.random_integers(0,self.getBaseP() - 1,self.getPowerM())

    def varifyMPcombination(self):
        if pow(self.getBaseP(), self.getPowerM()) > pow(PROTOCOL_VARIABLES.P.value, PROTOCOL_VARIABLES.M.valueF):
            return True
        return False

class CheckIterator(object):
    def __init__(self,Hs,locs,minsup,prime):
        self._Hs = Hs
        self._locationsList = locs
        self._minsup = minsup
        self._iterNum = len(Hs)
        self._prime = prime
        self._shuffleVec = self._generateShuffleVec()
        self._vectorResult = np.zeros(self._iterNum, dtype= bool)
        self._iterIndex = 0

    def _generateShuffleVec(self):
       return np.random.permutation(range(self._iterNum))

    def _currIndex(self):
        # print("shuffleVEc={}".format(self._shuffleVec))
        # print("shuffleVEclen={}".format(len(self._shuffleVec)))
        return self._shuffleVec[self._iterIndex]

    def hasNext(self):
        return  self._iterIndex < self._iterNum

    def next(self):
        return self._Hs[self._currIndex()]

    def computeZMinusMinsup(self,Z):
        #print("loc list = {}".format(self._locationsList))
        # print("loc list len = {}".format(len(self._locationsList)))
        # print("ind = {}".format(self._currIndex()))
        loc = self._locationsList[self._currIndex()]
        z_range = np.array(range(0,Z.shape[0]))
        compResult = np.sum(Z[z_range,loc])
        return (compResult % self._prime) - self._minsup

    def setResult(self,res):
        self._vectorResult[self._currIndex()] = res
        self._iterIndex += 1

    def getVectorResult(self):
        return self._vectorResult

    def size(self):
        return len(self._Hs)


