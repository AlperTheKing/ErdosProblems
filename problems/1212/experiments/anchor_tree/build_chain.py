from sympy import isprime, factorint, primerange
import json, time, sys
SMALL=list(primerange(2,2001))
def rough_composites(lo, hi, Tro=2000):
    n=hi-lo
    mark=bytearray(n)
    for p in SMALL:
        if p>Tro: break
        start=((lo+p-1)//p)*p
        for m in range(start, hi, p): mark[m-lo]=1
    out=[]
    for i in range(n):
        if not mark[i]:
            v=lo+i
            if v>3 and not isprime(v):
                out.append((v,sorted(factorint(v).keys())))
    return out
def clr_above(factors,pos):
    return min(q-(pos%q) for q in factors)
def H_ok(bfac,lo,hi):
    return all(((lo-1)//q+1)*q>hi for q in bfac)
t0=time.time()
START=10**7; GOAL=10**9
init=rough_composites(START,START+20000)
chain=[init[0],init[1]]
fails=0
while chain[-1][0]<GOAL and time.time()-t0<3000:
    (an,fn),(an1,fn1)=chain[-2],chain[-1]
    clr=clr_above(fn,an1)
    lo,hi=an1+1,an1+min(clr,30000)
    found=None
    if hi>lo+2:
        for (b,fb) in rough_composites(lo,hi):
            if H_ok(fb,an,an1): found=(b,fb); break
    if not found:
        # backtrack: drop last anchor, try a later alternative (simple: drop and extend window beyond previous pick)
        fails+=1
        if fails>500: break
        prev=chain.pop()
        (an,fn),(an1,fn1)=chain[-2],chain[-1]
        clr=clr_above(fn,an1)
        lo,hi=prev[0]+1,an1+min(clr,30000)
        got=None
        if hi>lo+2:
            for (b,fb) in rough_composites(lo,hi):
                if H_ok(fb,an,an1): got=(b,fb); break
        if got: chain.append(got)
        else: break
    else:
        chain.append(found)
print(f"chain length={len(chain)}, top={chain[-1][0]:,}, backtracks={fails}, time={time.time()-t0:.0f}s")
json.dump([[a,f] for a,f in chain], open('chain.json','w'))
# FULL verification of EVERY consecutive triple (every vertex of the infinite path prefix)
from math import gcd
bad=0
for i in range(len(chain)-2):
    an,_=chain[i]; an1,_=chain[i+1]; an2,_=chain[i+2]
    if isprime(an) or isprime(an2): bad+=1; print("prime anchor!?",i); break
    for s in range(an1,an2+1):
        if gcd(an,s)!=1: bad+=1; print("V",i,an,s); break
    for s in range(an,an1+1):
        if gcd(s,an2)!=1: bad+=1; print("H",i,s,an2); break
    if bad: break
print(f"FULL path verification: triples={len(chain)-2}, violations={bad}")
