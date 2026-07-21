import random, subprocess, sys
from collections import Counter
random.seed(4242)
def degen(p):
    q=[x for x in p if x>0]
    if not q: return True
    if len(set(q))!=len(q): return True
    return all(x==1 for x in q[1:])
def sub_exact(nu,w):
    """largest-first constructive random lam <= nu with |lam| = w (or None)"""
    if w<0 or w>sum(nu): return None
    rem=w; lam=[0,0,0,0]; cap=10**9
    for i in range(4):
        hi=min(nu[i],cap,rem)
        lo=max(0, rem-sum(nu[i+1:]) if i<3 else rem)
        lo=max(lo,0)
        if lo>hi: return None
        v=random.randint(lo,hi)
        # keep weakly decreasing
        lam[i]=v; cap=v; rem-=v
    if rem!=0: return None
    for i in range(3):
        if lam[i]<lam[i+1]: return None
    return lam
def f(p):
    q=[x for x in p if x>0]
    return ",".join(map(str,q)) if q else "0"
rows=[]; tries=0
while len(rows)<300000 and tries<6000000:
    tries+=1
    W=random.randint(61,400)
    cuts=sorted(random.randint(0,W) for _ in range(3))
    nu=sorted([cuts[0],cuts[1]-cuts[0],cuts[2]-cuts[1],W-cuts[2]],reverse=True)
    if nu[0]==0: continue
    a=random.randint(0,W)
    k=random.randint(0,3)
    if k==0: lam=[a,0,0,0]
    elif k==1:
        r=random.randint(1,4)
        if a%r: continue
        lam=sorted([a//r]*r+[0]*(4-r),reverse=True)
    elif k==2:
        h=random.randint(1,3)
        if a-h<1: continue
        lam=[a-h]+[1]*h+[0]*(3-h)
    else:
        lam=sub_exact(nu,a)
        if lam is None or not degen(lam): continue
    if any(lam[i]>nu[i] for i in range(4)): continue
    mu=sub_exact(nu,W-a)
    if mu is None: continue
    if not (degen(lam) or degen(mu) or degen(nu)): continue
    rows.append("%s;%s;%s"%(f(lam),f(mu),f(nu)))
open('_hw2.batch','w').write("\n".join(rows)+"\n")
out=subprocess.run(['./band12_scan.exe','--check','_hw2.batch'],capture_output=True,text=True)
lines=[l for l in out.stdout.splitlines() if l.startswith('dim=')]
c=Counter(int(l.split(' ')[0].split('=')[1]) for l in lines)
neg=[l for l in lines if l.split('P=')[1].split(' ')[0].find('-')>=0]
print("high-W band-12 sample (61<=W<=400): %d triples, dim histogram %s"%(len(lines),sorted(c.items())))
print("dim-3 count: %d ; triples with a negative coefficient: %d"%(c.get(3,0),len(neg)))
