import random, subprocess, sys, os, itertools
sys.path.insert(0,'.')
import hive4
from fractions import Fraction

random.seed(20260721)
HERE=os.path.abspath('.')

def rand_nu(W):
    # random partition of W into <=4 parts
    while True:
        cuts=sorted(random.randint(0,W) for _ in range(3))
        p=sorted([cuts[0],cuts[1]-cuts[0],cuts[2]-cuts[1],W-cuts[2]],reverse=True)
        if p[0]>0: return p

def rand_sub(nu,w):
    # random lam <= nu with |lam| = w  (rejection)
    for _ in range(200):
        l=[random.randint(0,nu[i]) for i in range(4)]
        l=sorted(l,reverse=True)
        l=[min(l[i],nu[i]) for i in range(4)]
        l=sorted(l,reverse=True)
        if sum(l)==w and all(l[i]<=nu[i] for i in range(4)) and all(l[i]>=l[i+1] for i in range(3)):
            return l
    return None

trips=[]
# (a) random over a wide weight range
while len(trips)<2500:
    W=random.randint(4,60)
    nu=rand_nu(W)
    a=random.randint(0,W)
    lam=rand_sub(nu,a); mu=rand_sub(nu,W-a)
    if lam is None or mu is None: continue
    trips.append((lam,mu,nu))
# (b) exhaustive-ish small weights (every triple at W=13,14 sampled)
def parts_le(N,k=4):
    out=[]
    def rec(rem,mx,cur):
        if rem==0: out.append(tuple(cur)); return
        if len(cur)==k: return
        for v in range(min(rem,mx),0,-1):
            cur.append(v); rec(rem-v,v,cur); cur.pop()
    rec(N,N,[])
    return out
small=[]
for W in (13,14):
    for nu in parts_le(W):
        nun=list(nu)+[0]*(4-len(nu))
        for a in range(W+1):
            for lam in parts_le(a):
                lamn=list(lam)+[0]*(4-len(lam))
                if any(lamn[i]>nun[i] for i in range(4)): continue
                for mu in parts_le(W-a):
                    mun=list(mu)+[0]*(4-len(mu))
                    if any(mun[i]>nun[i] for i in range(4)): continue
                    small.append((lamn,mun,nun))
random.shuffle(small)
trips += small[:3500]
# (c) degenerate-shape heavy sample (band 12 focus)
band=[]
while len(band)<2500:
    W=random.randint(6,60)
    nu=rand_nu(W)
    kind=random.randint(0,4)
    a=random.randint(0,W)
    if kind==0: lam=[a,0,0,0]                       # single row
    elif kind==1: lam=[1]*min(a,4)+[0]*(4-min(a,4)) # column (a<=4)
    elif kind==2:
        k=random.randint(1,4)
        if a%k: continue
        lam=[a//k]*k+[0]*(4-k)                      # rectangle
    elif kind==3:
        if a<1: continue
        k=random.randint(0,3); 
        if a-k<1: continue
        lam=[a-k]+[1]*k+[0]*(3-k)                   # hook
    else:
        lam=rand_sub(nu,a)
        if lam is None: continue
    lam=sorted(lam,reverse=True)
    if any(lam[i]>nu[i] for i in range(4)): continue
    mu=rand_sub(nu,W-a)
    if mu is None: continue
    band.append((lam,mu,nu))
trips+=band

def fmtp(p):
    q=[x for x in p if x>0]
    return ",".join(map(str,q)) if q else "0"

with open('_band12_val.batch','w') as f:
    for lam,mu,nu in trips:
        f.write("%s;%s;%s\n"%(fmtp(lam),fmtp(mu),fmtp(nu)))

out=subprocess.run(['./band12_scan.exe','--check','_band12_val.batch'],
                   capture_output=True,text=True)
lines=[l for l in out.stdout.splitlines() if l.startswith('dim=')]
assert len(lines)==len(trips), (len(lines),len(trips))

bad=0; ndim3=0; nnonempty=0
for (lam,mu,nu),line in zip(trips,lines):
    r=hive4.analyze(lam,mu,nu)
    tok=dict()
    for kv in line.split(' '):
        k,v=kv.split('=',1); tok[k]=v
    cdim=int(tok['dim']); cc=int(tok['c']); cV=int(tok['V'])
    if r['empty']:
        hdim=-1; hc=0; hV=0; hP=[Fraction(0)]
    else:
        hdim=r['dim']; hc=r['c']; hV=int(r['volume_normalized']) if r['dim']==3 else 0
        hP=r['poly']
    ok = (cdim==hdim) and (cc==hc) and (cV==hV)
    if cdim>=0:
        cP=[Fraction(s) for s in tok['P'].split(',')]
        ok = ok and (cP==list(hP))
        nnonempty+=1
        if cdim==3:
            ndim3+=1
            hs=[int(x) for x in tok['h*'].split(',')]
            ok = ok and (hs==[int(x) for x in r['hstar']])
        if not r['verified']: ok=False
    else:
        ok = ok and (tok['P']=='0')
    if not ok:
        bad+=1
        if bad<=10:
            print("MISMATCH",lam,mu,nu,"| cpp:",line,"| hive4: dim",hdim,"c",hc,"V",hV,"P",[str(x) for x in hP],
                  "h*",r.get('hstar'))
print("checked %d triples: nonempty %d, dim3 %d, MISMATCHES %d"%(len(trips),nnonempty,ndim3,bad))
sys.exit(1 if bad else 0)
