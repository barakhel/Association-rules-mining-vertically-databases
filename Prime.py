import numpy as np
import math


small_primes = np.array([2,3,5,7,9,11,13,17])


def generatePrime(m):
    prims = small_primes
    try:
        prims = np.loadtxt('prims.out', delimiter=',', dtype=int)
    except:
        pass

    if prims[-1] > m:
       return find_prime_in_list(prims,m)
    else:
        return ext_prime_list(prims,m)

def find_prime_in_list(primes,m):
    i,j,k = 0,math.floor(primes.size/2), primes.size
    while i + 1 < k:
        if m >= primes[j]:
            i, j = j, math.floor((k + j)/2)
        else:
            j,k = math.floor((j + i)/2), j
    return primes[k]

def ext_prime_list(prims, m):
    p = prims[-1]
    not_prime = True
    while not_prime or p <= m:
        not_prime = False
        p += 2
        for i in range(1, prims.size):
            if (prims[i] * prims[i-1]) > p:
                break
            if (p % prims[i]) == 0:
                not_prime = True
                break
        if not not_prime:
            prims = np.insert(prims,prims.size,p)
    np.savetxt('prims.out', prims, delimiter=',', fmt="%ld")
    return p

def IsPrime(p):
    return  p == 1 or generatePrime(p-1) == p

