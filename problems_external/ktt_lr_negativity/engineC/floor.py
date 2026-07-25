import sys, random, json, argparse
sys.path.insert(0,'engineC')
from ehr import ehrhart
from fractions import Fraction
ap=argparse.ArgumentParser()
ap.add_argument("--seed",type=int); ap.add_argument("--secs",type=int,default=180)
ap.add_argument("--rmin",type=int,default=4); ap.add_argument("--rmax",type=int,default=6)
ap.add_argument("--volcap",type=int,default=60000); a=ap.parse_args()
import time; t0=time.time()
rng=random.Random(a.seed); floor={}; n=0
while time.time()-t0<a.secs:
    r=rng.randint(a.rmin,a.rmax); hi=rng.randint(2,10)
    lam=sorted((rng.randint(1,hi) for _ in range(rng.randint(2,r))),reverse=True)
    mu=sorted((rng.randint(1,hi) for _ in range(rng.randint(2,r))),reverse=True)
    L=lam+[0]*(r-len(lam)); M=mu+[0]*(r-len(mu)); nu=[L[i]+M[i] for i in range(r)]
    for _ in range(rng.randrange(1,3*r)):
        i=rng.randrange(r-1); j=rng.randrange(i+1,r)
        c=nu[:]; c[i]-=1; c[j]+=1
        if all(c[k]>=c[k+1] for k in range(r-1)) and c[-1]>=0: nu=c
    try: res=ehrhart(lam,mu,nu,vol_cap=a.volcap)
    except Exception: continue
    if res["status"]!="OK": continue
    d=res["d"]
    if d<3: continue
    n+=1
    hs=res["hstar"]; V=sum(hs)
    m2=Fraction(sum(hs[j]*(2*j-d-1)**2 for j in range(d+1)),V)
    m1=Fraction(sum(hs[j]*(2*j-d-1) for j in range(d+1)),V)
    cf=[Fraction(x) for x in res["coeffs"]]; vol=cf[d]
    binv=min(float(cf[k])/(float(vol)**(k/d)) for k in range(1,d))
    m2rel=float(m2/Fraction(d+1,3)); m1f=float(m1)
    if m2rel<1 or m1f>0 or binv<0:
        print("HIT",json.dumps(dict(lam=lam,mu=mu,nu=nu,d=d,m2rel=m2rel,m1=m1f,binv=binv,V=V,c=res["c"],hs=hs)),flush=True)
    e=floor.get(d)
    if e is None: floor[d]=[m2rel,m1f,binv,1,(lam,mu,nu,hs,V,res["c"])]
    else:
        e[3]+=1
        if m2rel<e[0]: e[0]=m2rel; e[4]=(lam,mu,nu,hs,V,res["c"])
        if m1f>e[1]: e[1]=m1f
        if binv<e[2]: e[2]=binv
print("SEED",a.seed,"n_ok",n)
for d in sorted(floor):
    e=floor[d]
    print("d=%2d cnt=%6d min_m2rel=%.4f max_m1=%.4f min_binv=%.4f"%(d,e[3],e[0],e[1],e[2]),flush=True)
    print("   arg:",e[4],flush=True)
