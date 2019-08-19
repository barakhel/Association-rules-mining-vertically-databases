import numpy as np
import random


class SecureCompSlave(object):

    def __init__(self):
        object.__init__(self)
        self.init()
        self._secretNumbersR = 0

    def init(self, P=None, M=None, vectorId=None, prime=None, maxRi = None):
        self.setBaseP(P)
        self.setPowerM(M)
        self._dataY = vectorId
        self._prime = prime
        if  (maxRi != None):
            self._maxRi = maxRi
        else:
            self._maxRi = self._prime

    def _generateSecretScalar(self):
        self._Ris = np.random.random_integers(0,self._maxRi,size= self.powerM)
        self._secretNumbersR = np.sum(self._Ris, axis = 0)
        moduloR = np.sum(self._Ris, axis = 0) % self._prime
        vectorSize = self._dataY.size
        if moduloR >= self._prime - vectorSize:
            x = self._prime + random.randint(0,self._prime - vectorSize - 1) - moduloR
            moduloR =  (moduloR + x) % self._prime
            while x != 0:
                xi = random.randint(1,x)
                x -= xi
                i = random.randint(0, self.powerM - 1)
                self._Ris[i] += xi
        self._secretNumbersR = moduloR

    def computeVectorZ(self,vectorH):
        self._generateSecretScalar()
        return ((vectorH @ self._dataY.T) + self._Ris.reshape((self._Ris.size,1)))% self._prime

    def checkIfMinsup(self,n):
        return bool(n >= self._secretNumbersR)

    def setPowerM(self, m):
        self.powerM = m

    def setBaseP(self, p):
        self.baseP = p

    def getPowerM(self):
        return self.powerM

    def getBaseP(self):
        return self.baseP

    def setMaxRi(self,maxRi):
        self._maxRi = maxRi