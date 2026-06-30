"""Rigidity diagnostic for the WITHDRAWAL half: does near-extremal beta force near-uniform load?
Test envelope of load-variance vs budget:  V2 = sum_v (T_v - N)^2  vs  Gamma*(N^2/25 - beta).
If V2 <= K * Gamma * (N^2/25 - beta) with a clean constant K, that IS the rigidity modulus (route c).
Also report overload OV=sum (T_v-N)_+ and underload UN=sum (N-T_v)_+, and OV / (N^2/25-beta).
EXACT Fraction. Battery = standing battery. Print max ratios + where attained."""
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
    m=len(M); Gamma=sum(ell[f]**2 for f in M)
    budget=F(n*n,25)-m            # N^2/25 - beta  (>=0 on real graphs)
    V2=sum((t-F(n))**2 for t in T)
    OV=sum(max(t-F(n),F(0)) for t in T)
    UN=sum(max(F(n)-t,F(0)) for t in T)
    acc['n']+=1
    if budget>0:
        rV=V2/(Gamma*budget)
        if rV>acc['maxrV'][0]: acc['maxrV']=(rV,name,n,m,str(budget))
        rO=OV/budget
        if rO>acc['maxrO'][0]: acc['maxrO']=(rO,name,n,m)
    else:  # budget==0 => extremal; must have V2==0 (rigidity at the boundary)
        acc['b0']+=1
        if V2!=0:
            acc['b0bad']+=1
            if acc['b0first'] is None: acc['b0first']=(name,n,m,str(V2))
    # also OV vs Gamma (scale-free)
    if Gamma>0:
        rOG=OV/Gamma
        if rOG>acc['maxrOG'][0]: acc['maxrOG']=(rOG,name,n,m)

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
    acc={'n':0,'b0':0,'b0bad':0,'b0first':None,
         'maxrV':(F(-1),'','','',''),'maxrO':(F(-1),'','',''),'maxrOG':(F(-1),'','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (b0bad=%d)"%(nn,acc['b0bad']),flush=True)
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
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("\n  configs=%d"%acc['n'],flush=True)
    print("  RIGIDITY at boundary: budget==0 configs=%d, with V2!=0 (VIOLATIONS)=%d %s"%(acc['b0'],acc['b0bad'],acc['b0first'] or ''),flush=True)
    print("  MAX  V2 / (Gamma*budget)  = %s ~ %.5f  at %s"%(acc['maxrV'][0],float(acc['maxrV'][0]),acc['maxrV'][1:]),flush=True)
    print("  MAX  OV / budget          = %s ~ %.5f  at %s"%(acc['maxrO'][0],float(acc['maxrO'][0]),acc['maxrO'][1:]),flush=True)
    print("  MAX  OV / Gamma           = %s ~ %.5f  at %s"%(acc['maxrOG'][0],float(acc['maxrOG'][0]),acc['maxrOG'][1:]),flush=True)
    print("  => if V2/(Gamma*budget) bounded by a clean K, that is the rigidity modulus (route c).",flush=True)
