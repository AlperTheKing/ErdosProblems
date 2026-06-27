import io,contextlib,subprocess,itertools,random
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG
from fractions import Fraction as Fr
def getT(n,E,trifree=False):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if trifree:
        for u in range(n):
            for a in adj[u]:
                for b in adj[u]:
                    if a<b and b in adj[a]: return None
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[Fr(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps); share=Fr(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    return n,G,T
def overcheck(n,E,tf=False):
    r=getT(n,E,tf)
    if r is None: return None
    n,G,T=r
    defi=n*n-G
    to=sum(max(Fr(0),t-n) for t in T)
    return defi-to, defi, float(to), n
def cb(sizes,k):
    off=[0]
    for s in sizes: off.append(off[-1]+s)
    n=off[-1]; E=[]
    for i in range(k):
        for a in range(sizes[i]):
            for b in range(sizes[(i+1)%k]): E.append((off[i]+a,off[(i+1)%k]+b))
    return n,E
# C5 blowups
viol=0; mn=None
for sizes in itertools.product(range(1,6),repeat=5):
    if sum(sizes)>17: continue
    r=overcheck(*cb(list(sizes),5),tf=True)
    if r is None: continue
    sl,defi,to,n=r
    if sl<0: viol+=1; print("C5bw VIOL",sizes,sl)
    if mn is None or sl<mn[0]: mn=(float(sl),sizes,defi,to)
print("C5 blowups: total-overshoot<=deficit viol",viol,"tightest",mn)
# C7 blowups
viol7=0; mn7=None
for sizes in itertools.product(range(1,4),repeat=7):
    if sum(sizes)>17: continue
    r=overcheck(*cb(list(sizes),7),tf=True)
    if r is None: continue
    sl,defi,to,n=r
    if sl<0: viol7+=1; print("C7bw VIOL",sizes)
    if mn7 is None or sl<mn7[0]: mn7=(float(sl),sizes)
print("C7 blowups viol",viol7,"tightest",mn7)
# random tri-free
random.seed(3); rv=0; rmn=None; trials=0
for n in range(11,15):
    for _ in range(3000):
        p=random.uniform(0.2,0.45); adj=[set() for _ in range(n)]; E=[]
        for i in range(n):
            for j in range(i+1,n):
                if random.random()<p and not (adj[i]&adj[j]):
                    adj[i].add(j); adj[j].add(i); E.append((i,j))
        r=overcheck(n,E,tf=True)
        if r is None: continue
        trials+=1; sl,defi,to,nn=r
        if sl<0: rv+=1; print("RANDOM VIOL",n,sl)
        if rmn is None or sl<rmn[0]: rmn=(float(sl),n,defi,to)
print(f"random tri-free: trials={trials} viol={rv} tightest={rmn}")
