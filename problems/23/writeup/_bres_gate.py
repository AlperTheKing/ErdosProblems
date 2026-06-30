"""Independent EXACT gate of the workflow route-(b) side-fact B-RES:
   5*(N^2 - Gamma) >= TV_cut(T) - TV_bad(T),   i.e.  5*sum_v(N - T_v) >= TVcut - TVbad   (sum_v T = Gamma).
Total pressure debt = 5N*(TVcut-TVbad) <= 25N(N^2-Gamma) would follow. Full battery; report viol + min slack."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    Gamma=sum(ell[f]**2 for f in M); m=len(M)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    tvcut=F(0); tvbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: tvcut+=d
                else: tvbad+=d
    slack=5*F(n*n-Gamma)-(tvcut-tvbad)
    acc['nb']+=1
    if slack<acc['minm'][0]: acc['minm']=(slack,name,n,Gamma,m)
    if slack<0:
        acc['viol']+=1
        if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,Gamma,m,str(slack))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    acc={'nb':0,'viol':0,'first':None,'minm':(F(10**18),'','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d minslack=%s"%(acc['viol'],float(acc['minm'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                        ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(name,nn,adj,s,acc)
    print("\n  configs=%d  B-RES violations=%d  MIN slack=%s at %s"%(acc['nb'],acc['viol'],float(acc['minm'][0]),acc['minm'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === B-RES 5(N^2-Gamma) >= TVcut-TVbad %s ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
