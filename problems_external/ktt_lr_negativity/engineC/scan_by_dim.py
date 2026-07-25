#!/usr/bin/env python3
"""Broad fast scan: for each ACTUAL dimension d, record the minimum m2rel and
minimum binv and maximum m1 observed, to see how the negativity floor moves
with d.  No full-dim constraint; dimension floats."""
import sys, random, json, argparse
sys.path.insert(0,'engineC')
from ehr import ehrhart
from fractions import Fraction

def stats(lam,mu,nu,volcap):
    try: r=ehrhart(lam,mu,nu,vol_cap=volcap)
    except Exception: return None
    if r["status"]!="OK": return None
    d=r["d"]
    if d<3: return None
    hs=r["hstar"]; V=sum(hs)
    if V<=0: return None
    m1=Fraction(sum(hs[j]*(2*j-d-1) for j in range(d+1)),V)
    m2=Fraction(sum(hs[j]*(2*j-d-1)**2 for j in range(d+1)),V)
    cf=[Fraction(x) for x in r["coeffs"]]; vol=cf[d]
    binv=min(float(cf[k])/(float(vol)**(k/d)) for k in range(1,d))
    return d, float(m2/Fraction(d+1,3)), float(m1), binv, V, r["c"], hs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=int,default=1)
    ap.add_argument("--n",type=int,default=100000)
    ap.add_argument("--rmax",type=int,default=6)
    ap.add_argument("--hi",type=int,default=9)
    ap.add_argument("--volcap",type=int,default=250000)
    ap.add_argument("--out",default=None)
    a=ap.parse_args()
    rng=random.Random(a.seed)
    floor={}  # d -> [min_m2rel, max_m1, min_binv, count, argmin_m2 record]
    out=open(a.out,"w") if a.out else None
    for it in range(a.n):
        r=rng.randint(4,a.rmax)
        lam=sorted((rng.randint(1,a.hi) for _ in range(rng.randint(2,r))),reverse=True)
        mu=sorted((rng.randint(1,a.hi) for _ in range(rng.randint(2,r))),reverse=True)
        L=lam+[0]*(r-len(lam)); M=mu+[0]*(r-len(mu))
        nu=[L[i]+M[i] for i in range(r)]
        for _ in range(rng.randrange(1,3*r)):
            i=rng.randrange(r-1); j=rng.randrange(i+1,r)
            c=nu[:]; c[i]-=1; c[j]+=1
            if all(c[k]>=c[k+1] for k in range(r-1)) and c[-1]>=0: nu=c
        s=stats(lam,mu,nu,a.volcap)
        if s is None: continue
        d,m2rel,m1,binv,V,c,hs=s
        if m2rel<1.0 or m1>0 or binv<0:
            print("!!! HIT",json.dumps(dict(lam=lam,mu=mu,nu=nu,d=d,m2rel=m2rel,m1=m1,binv=binv,V=V,c=c,hs=hs)),flush=True)
        e=floor.get(d)
        if e is None:
            floor[d]=[m2rel,m1,binv,1,(lam,mu,nu,hs,V,c)]
        else:
            e[3]+=1
            if m2rel<e[0]: e[0]=m2rel; e[4]=(lam,mu,nu,hs,V,c)
            if m1>e[1]: e[1]=m1
            if binv<e[2]: e[2]=binv
        if it%5000==0 and it:
            print("  progress",it,{d:round(v[0],3) for d,v in sorted(floor.items())},flush=True)
    for d in sorted(floor):
        e=floor[d]
        print("d=%2d  count=%6d  min_m2rel=%.4f  max_m1=%.4f  min_binv=%.4f"%(d,e[3],e[0],e[1],e[2]),flush=True)
        print("      argmin_m2rel:",e[4],flush=True)
        if out: out.write(json.dumps(dict(d=d,count=e[3],min_m2rel=e[0],max_m1=e[1],min_binv=e[2],rec=e[4]))+"\n")
    if out: out.close()

if __name__=="__main__": main()
