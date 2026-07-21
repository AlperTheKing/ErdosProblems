"""Band-12 cross-engine gate: for a random sample of BAND-12 triples, verify that
the stretched LR counts c(n nu; n lam, n mu) produced by the two independent exact
LR engines agree with the polynomial P produced by band12_scan.exe (which mirrors
hive4.py).  Nothing is tuned; every disagreement is reported."""
import random, subprocess, sys, os
from fractions import Fraction
random.seed(31337)
ENG = os.path.abspath('../engine')
A = os.path.join(ENG, 'lr_hive.exe')
B = os.path.join(ENG, 'engineB_lrrule.py')

def parts_le(N,k=4):
    out=[]
    def rec(rem,mx,cur):
        if rem==0: out.append(tuple(cur)+(0,)*(k-len(cur))); return
        if len(cur)==k: return
        for v in range(min(rem,mx),0,-1):
            cur.append(v); rec(rem-v,v,cur); cur.pop()
    rec(N,N,[]); return out

def degenerate(p):
    q=[x for x in p if x>0]
    if not q: return True
    if len(set(q))!=len(q): return True
    if all(x==1 for x in q[1:]): return True
    return False

pool=[]
for W in range(6,25):
    nus=parts_le(W)
    for _ in range(4000):
        nu=random.choice(nus)
        a=random.randint(0,W)
        cand=[p for p in parts_le(a) if all(p[i]<=nu[i] for i in range(4))]
        if not cand: continue
        lam=random.choice(cand)
        cand2=[p for p in parts_le(W-a) if all(p[i]<=nu[i] for i in range(4))]
        if not cand2: continue
        mu=random.choice(cand2)
        if not (degenerate(lam) or degenerate(mu) or degenerate(nu)): continue
        pool.append((list(lam),list(mu),list(nu)))
random.shuffle(pool)

def fmtp(p, n=1):
    q=[x*n for x in p if x>0]
    return ",".join(map(str,q)) if q else "0"

# score the pool with the census engine, keep nontrivial (dim >= 1) ones
with open('_gate_pool.batch','w') as f:
    for lam,mu,nu in pool[:60000]:
        f.write("%s;%s;%s\n"%(fmtp(lam),fmtp(mu),fmtp(nu)))
out=subprocess.run(['./band12_scan.exe','--check','_gate_pool.batch'],capture_output=True,text=True)
lines=[l for l in out.stdout.splitlines() if l.startswith('dim=')]
sel=[]
for t,l in zip(pool[:60000],lines):
    d=int(l.split(' ')[0].split('=')[1])
    if d>=1: sel.append((t,l))
random.shuffle(sel)
sel=sel[:200]
print("band-12 sample with dim>=1: %d selected (pool %d)"%(len(sel),len(lines)))

# batch for engine A / B at n = 1..4
batch=[]
for (lam,mu,nu),l in sel:
    for n in (1,2,3,4):
        batch.append("%s;%s;%s;100000000"%(fmtp(lam,n),fmtp(mu,n),fmtp(nu,n)))
open('_gate_stretch.batch','w').write("\n".join(batch)+"\n")
ra=subprocess.run([A,'--batch','_gate_stretch.batch'],capture_output=True,text=True)
va=[x.strip() for x in ra.stdout.split() if x.strip()]
rb=subprocess.run([sys.executable,B,'--batch','_gate_stretch.batch'],capture_output=True,text=True)
vb=[x.strip() for x in rb.stdout.split() if x.strip()]
print("engine A values %d, engine B values %d, expected %d"%(len(va),len(vb),len(batch)))
bad=0; checked=0
i=0
for (lam,mu,nu),l in sel:
    tok=dict(kv.split('=',1) for kv in l.split(' '))
    P=[Fraction(s) for s in tok['P'].split(',')]
    for n in (1,2,3,4):
        want=sum(c*n**k for k,c in enumerate(P))
        assert want.denominator==1
        want=int(want)
        gota=va[i]; gotb=vb[i]; i+=1
        checked+=1
        if gota!=str(want) or gotb!=str(want):
            bad+=1
            if bad<=10: print("DISAGREE",lam,mu,nu,"n=",n,"poly:",want,"A:",gota,"B:",gotb)
print("cross-engine checks: %d, disagreements: %d"%(checked,bad))
sys.exit(1 if bad else 0)
