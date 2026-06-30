"""EXACT gate of Codex block-237 PREFIX-LOAD-PSC (induction-over-load-levels scaffold for LOAD-PSC-25).
Threshold decomposition of T: distinct values 0=t_0<t_1<...<t_r, widths w_j=t_{j+1}-t_j, superlevels
H_j={v:T_v>t_j}, sigma_j=delta_B(H_j)-delta_M(H_j) (>=0 by max-cut). Per-level:
  A_j = 25*w_j*(2*t_j + w_j - N)*|H_j| + N*w_j*sigma_j,   budget density D = N^2 - 25*|M|.
PREFIX-LOAD-PSC: for every k, sum_{j<k}( D*w_j*|H_j| - A_j ) >= 0. Full prefix => LOAD-PSC-25.
Battery: census gamma-min N<=11 + two-lane + k-lane + C5/C7/C9[t] + non-uniform + Mycielskians N<=23 + glued.
EXACT Fraction. Report min prefix margin + first violation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary(n,adj,side,Hset,badset):
    dB=dM=0
    for u in Hset:
        for v in adj[u]:
            if v in Hset: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M)
    D=F(n*n)-25*m
    vals=sorted(set(T))                      # ascending distinct T-values
    # thresholds t_0=min..., use levels between consecutive distinct values + above max=0 baseline
    # Codex: 0=t_0<t_1<...<t_r distinct h-values; here h=T. Use t_j = vals[j], w_j=vals[j+1]-vals[j].
    levels=[F(0)]+ [v for v in vals if v>0]   # ensure 0 baseline
    levels=sorted(set(levels))
    cum=F(0); minmarg=None
    for j in range(len(levels)-1):
        tj=levels[j]; wj=levels[j+1]-levels[j]
        Hset=set(v for v in range(n) if T[v]>tj)
        if not Hset: continue
        Hsz=len(Hset)
        dB,dM=boundary(n,adj,side,Hset,None)
        sig=dB-dM
        Aj=25*wj*(2*tj+wj-F(n))*Hsz + F(n)*wj*sig
        cum+= D*wj*Hsz - Aj
        if minmarg is None or cum<minmarg: minmarg=cum
        if cum<0:
            acc['viol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,j,str(tj),str(cum))
    acc['n']+=1
    if minmarg is not None and minmarg<acc['min'][0]: acc['min']=(minmarg,name,n,m)

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
    acc={'n':0,'viol':0,'first':None,'min':(F(10**18),'','','')}
    print("=== PREFIX-LOAD-PSC EXACT gate (induction over load levels) ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d minmargin=%s"%(acc['viol'],float(acc['min'][0])),flush=True)
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
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  total configs=%d  PREFIX-LOAD-PSC violations=%d"%(acc['n'],acc['viol']),flush=True)
    print("  MIN prefix margin = %s at %s"%(float(acc['min'][0]),acc['min'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === PREFIX-LOAD-PSC %s ==="%("VIOLATED (induction lemma false)" if acc['viol'] else "HOLDS exactly => induction-over-levels scaffold valid; full prefix => LOAD-PSC-25"),flush=True)
