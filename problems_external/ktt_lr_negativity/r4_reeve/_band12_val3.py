import random, subprocess, sys, os
sys.path.insert(0,'.')
import hive4
from fractions import Fraction
random.seed(777)

def rand_nu(W):
    while True:
        cuts=sorted(random.randint(0,W) for _ in range(3))
        p=sorted([cuts[0],cuts[1]-cuts[0],cuts[2]-cuts[1],W-cuts[2]],reverse=True)
        if p[0]>0: return p
def rand_sub_w(nu,w):
    for _ in range(60):
        l=[random.randint(0,nu[i]) for i in range(4)]
        l.sort(reverse=True)
        l=[min(l[i],nu[i]) for i in range(4)]
        l.sort(reverse=True)
        if sum(l)==w and all(l[i]<=nu[i] for i in range(4)): return l
    return None

pool=[]
while len(pool)<400000:
    W=random.randint(8,60)
    nu=rand_nu(W)
    a=random.randint(0,W)
    lam=rand_sub_w(nu,a)
    if lam is None: continue
    mu=rand_sub_w(nu,W-sum(lam))
    if mu is None: continue
    if sum(lam)+sum(mu)!=W: continue
    pool.append((lam,mu,nu))

def fmtp(p):
    q=[x for x in p if x>0]
    return ",".join(map(str,q)) if q else "0"
with open('_v3pool.batch','w') as f:
    for lam,mu,nu in pool: f.write("%s;%s;%s\n"%(fmtp(lam),fmtp(mu),fmtp(nu)))
out=subprocess.run(['./band12_scan.exe','--check','_v3pool.batch'],capture_output=True,text=True)
lines=[l for l in out.stdout.splitlines() if l.startswith('dim=')]
assert len(lines)==len(pool)
d3=[(t,l) for t,l in zip(pool,lines) if l.startswith('dim=3')]
d2=[(t,l) for t,l in zip(pool,lines) if l.startswith('dim=2')]
print("pool %d -> dim3 %d, dim2 %d"%(len(pool),len(d3),len(d2)))
random.shuffle(d3); random.shuffle(d2)
sample=d3[:4000]+d2[:1000]
bad=0
for (lam,mu,nu),line in sample:
    r=hive4.analyze(lam,mu,nu)
    tok=dict(kv.split('=',1) for kv in line.split(' '))
    cP=[Fraction(s) for s in tok['P'].split(',')]
    ok=(int(tok['dim'])==r['dim'] and int(tok['c'])==r['c'] and cP==list(r['poly'])
        and r['verified'] and r['deg_eq_dim'])
    if int(tok['dim'])==3:
        ok = ok and int(tok['V'])==int(r['volume_normalized']) and r['vol_crosscheck']
        ok = ok and [int(x) for x in tok['h*'].split(',')]==[int(x) for x in r['hstar']]
    if not ok:
        bad+=1
        if bad<=8: print("MISMATCH",lam,mu,nu,line,r['dim'],r['c'],str(r['volume_normalized']),[str(x) for x in r['poly']],r['hstar'],r['verified'])
print("dim-3/dim-2 cross-check: %d triples, MISMATCHES %d"%(len(sample),bad))
sys.exit(1 if bad else 0)
