import random, subprocess, sys
random.seed(99)
def rnd_part(W,strictish):
    cuts=sorted(random.randint(0,W) for _ in range(3))
    p=sorted([cuts[0],cuts[1]-cuts[0],cuts[2]-cuts[1],W-cuts[2]],reverse=True)
    return p
def degen(p):
    q=[x for x in p if x>0]
    if not q: return True
    if len(set(q))!=len(q): return True
    if all(x==1 for x in q[1:]): return True
    return False
def mkdeg(W):
    """random DEGENERATE partition of W with <=4 parts"""
    k=random.randint(0,3)
    if k==0:   return sorted([W,0,0,0],reverse=True)                      # row
    if k==1:
        r=random.randint(1,4)
        if W%r: return None
        return [W//r]*r+[0]*(4-r)                                          # rectangle
    if k==2:
        h=random.randint(1,3)
        if W-h<1: return None
        return [W-h]+[1]*h+[0]*(3-h)                                       # hook
    p=rnd_part(W,False)
    return p if degen(p) else None
rows=[]
tot=0
while len(rows)<600000:
    W=random.randint(61,400)
    nu=rnd_part(W,True)
    if nu[0]==0: continue
    a=random.randint(0,W)
    # make lam degenerate and contained in nu
    lam=mkdeg(a)
    if lam is None: continue
    lam=sorted(lam,reverse=True)
    if any(lam[i]>nu[i] for i in range(4)): continue
    # mu: random contained partition of W-a
    b=W-a
    mu=None
    for _ in range(40):
        c=[random.randint(0,nu[i]) for i in range(4)]
        c.sort(reverse=True); c=[min(c[i],nu[i]) for i in range(4)]; c.sort(reverse=True)
        if sum(c)==b: mu=c; break
    if mu is None: continue
    assert degen(lam) or degen(mu) or degen(nu)
    def f(p):
        q=[x for x in p if x>0]
        return ",".join(map(str,q)) if q else "0"
    rows.append("%s;%s;%s"%(f(lam),f(mu),f(nu)))
open('_highW.batch','w').write("\n".join(rows)+"\n")
out=subprocess.run(['./band12_scan.exe','--check','_highW.batch'],capture_output=True,text=True)
lines=[l for l in out.stdout.splitlines() if l.startswith('dim=')]
from collections import Counter
c=Counter(int(l.split(' ')[0].split('=')[1]) for l in lines)
neg=[l for l in lines if '-' in l.split('P=')[1].split(' ')[0]]
print("high-W band-12 sample: %d triples, dim histogram %s"%(len(lines),sorted(c.items())))
print("triples with a negative coefficient: %d"%len(neg))
