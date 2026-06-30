"""HARDEN ROUTE A: stress CYCLE-SM (rho(O)<=N) on nonuniform odd-cycle fans -- the family that killed the
sandwich (N=22) and net_H (N=30). For each fan: enumerate part-respecting cuts (2^L), take max-cut value, then
gamma-min among them; verify LOCAL max (no single-vertex improving move); exact-test Cycle-SM per bad edge.
Report ANY violation (would kill rho(O)<=N like the sandwich died). Deterministic pseudo-random sizes (no RNG)."""
from itertools import product
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side

def build_blowup(sizes):
    L=len(sizes); off=[0]
    for s in sizes: off.append(off[-1]+s)
    n=off[-1]; parts=[list(range(off[i],off[i+1])) for i in range(L)]
    E=set()
    for i in range(L):
        j=(i+1)%L
        for a in parts[i]:
            for b in parts[j]: E.add((min(a,b),max(a,b)))
    return n,sorted(E),parts

def cut_size(n,E,side):
    return sum(1 for x,y in E if side[x]!=side[y])

def local_max(n,adj,side):
    # no single-vertex flip increases cut
    for v in range(n):
        same=sum(1 for w in adj[v] if side[w]==side[v])
        diff=sum(1 for w in adj[v] if side[w]!=side[v])
        if same>diff: return False
    return True

def cycle_sm(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return ('nobad',)
    worst=F(-1); viol=0; arg=None
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        num=sum(F(c,nf)*T[v] for v,c in cnt.items())
        den=F(n)*ell[f]
        r=num/den
        if r>worst: worst=r; arg=(f,str(num),str(den))
        if num>den: viol+=1
    return ('ok',viol,worst,arg,sum(T),max(T),len(M))

def test_fan(sizes,acc):
    L=len(sizes); n,E,parts=build_blowup(sizes)
    if n>34: return
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    # enumerate part-respecting assignments
    best=-1; cuts=[]
    for combo in product((0,1),repeat=L):
        side=[0]*n
        for i in range(L):
            for v in parts[i]: side[v]=combo[i]
        c=cut_size(n,E,side)
        if c>best: best=c; cuts=[combo]
        elif c==best: cuts.append(combo)
    # gamma-min among max cuts
    cand=[]
    for combo in cuts:
        side=[0]*n
        for i in range(L):
            for v in parts[i]: side[v]=combo[i]
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        cand.append((sum(T),combo,side))
    if not cand: return
    gmin=min(c[0] for c in cand)
    for G,combo,side in cand:
        if G!=gmin: continue
        if not local_max(n,adj,side):
            acc['notlocalmax']+=1; continue   # part-respecting not even locally max -> skip (not a real max cut)
        res=cycle_sm(n,adj,side)
        if res is None or res[0]!='ok': continue
        _,viol,worst,arg,Gam,maxT,m=res
        acc['tested']+=1
        if worst>acc['worst'][0]:
            acc['worst']=(worst,tuple(sizes),combo,str(Gam),str(maxT))
        if viol>0:
            acc['viol']+=1
            acc['vlist'].append((tuple(sizes),combo,viol,str(worst),str(Gam),str(maxT)))

# deterministic family of nonuniform size profiles
PROFILES=[]
# the killers + structured variants
for c in [(3,9,1,9,3),(9,3,1,3,9),(1,9,1,9,1),(5,1,9,1,5),(9,1,1,1,9),(2,8,1,8,2),(4,10,1,10,4),
          (3,9,2,9,3),(3,8,1,8,3),(6,6,1,6,6),(1,10,2,10,1),(7,2,1,2,7),(3,7,3,7,3),(2,9,3,9,2)]:
    PROFILES.append(list(c))
# C7 nonuniform
for c in [(3,5,1,5,1,5,3),(1,6,1,6,1,6,1),(4,1,4,1,4,1,4),(2,5,1,5,1,5,2),(5,1,5,1,1,1,5)]:
    PROFILES.append(list(c))
# pseudo-random (LCG, no RNG import)
seed=12345
def rnd():
    global seed; seed=(1103515245*seed+12345)%(2**31); return seed
for _ in range(80):
    L=5 if rnd()%2 else 7
    sizes=[1+rnd()%9 for _ in range(L)]
    if sum(sizes)<=33: PROFILES.append(sizes)

if __name__=="__main__":
    acc=dict(tested=0,viol=0,notlocalmax=0,worst=(F(-1),None,None,'',''),vlist=[])
    for sizes in PROFILES:
        test_fan(sizes,acc)
    print("  fans tested(gamma-min,local-max)=%d  not-local-max skipped=%d"%(acc['tested'],acc['notlocalmax']))
    print("  CYCLE-SM violations=%d"%acc['viol'])
    w=acc['worst']
    print("  worst ratio=%s=%s @ sizes=%s combo=%s Gamma=%s maxT=%s"%(str(w[0]),str(float(w[0]))[:7],w[1],w[2],w[3],w[4]))
    if acc['vlist']:
        print("  VIOLATIONS (sizes,combo,nviol,worstratio,Gamma,maxT):")
        for d in acc['vlist'][:20]: print("    %s"%(d,))
    print("  === CYCLE-SM on nonuniform fans %s ==="%("HOLDS (rho(O)<=N robust)" if acc['viol']==0 else "*** FAILS -- ROUTE A DEAD ***"))
