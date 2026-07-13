#!/usr/bin/env python3
'''Exhaustive gate for the duplicated-difference identity in Problem 864.'''
from collections import Counter
from itertools import combinations
from math import comb

def sums(A):
    c=Counter()
    for i,a in enumerate(A):
        for b in A[i:]: c[a+b]+=1
    return c

def check(A):
    sc=sums(A)
    repeated=[s for s,r in sc.items() if r>=2]
    if len(repeated)>1: return False
    k=len(A)
    dc=Counter(a-b for a in A for b in A if a>b)
    if any(r>2 for r in dc.values()):
        raise AssertionError(('difference multiplicity',A,dc))
    if not repeated:
        expected=comb(k,2)
    else:
        sigma=repeated[0]
        aset=set(A)
        P=[a for a in A if sigma-a in aset]
        p=len(P)
        q=sum(1 for a in P if a<sigma-a and sigma-a in aset)
        numerator=comb(p,2)-q
        if numerator%2: raise AssertionError(('parity',A,sigma,P,q))
        expected=comb(k,2)-numerator//2
        for d,r in dc.items():
            if r==2:
                reps=[(a,b) for a in A for b in A if a>b and a-b==d]
                (x,y),(u,v)=reps
                if {u,v}!={sigma-y,sigma-x}:
                    raise AssertionError(('reflection',A,sigma,d,reps))
    if len(dc)!=expected:
        raise AssertionError(('identity',A,repeated,len(dc),expected))
    return True

def main(limit=16):
    admissible=0
    for n in range(1,limit+1):
        for mask in range(1<<n):
            A=[i+1 for i in range(n) if mask>>i&1]
            if check(A): admissible+=1
    print({'N_max':limit,'subsets_checked':(1<<(limit+1))-2,
           'admissible_checked':admissible,'status':'PASS'})

if __name__=='__main__': main()
