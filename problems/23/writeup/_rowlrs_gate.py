"""EXACT gate of Codex block-218 ROW-LRS (per-bad-edge local form of LRS):
  A_f + |M| <= N + N^2/25   for every bad edge f,   A_f = sum_v p_f(v) T(v) / ell(f).
ROW-LRS => LRS (sum T^2 = sum_f ell(f)^2 A_f; /Gamma = ell^2-weighted avg of A_f). STRONGER (per-edge) than
LRS -- so more likely to be refuted by a structured construction (like ROWSUM-O was). Gate exactly + adversarial
(two-lane, blow-ups, Mycielskians, full/merged detour, stacked, dense). Report max (A_f+|M|)/(N+N^2/25) and
first violation. EXACT Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _M_tailswitch_gate import build_pd

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); rhs=F(n)+F(n*n,25)
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    for f in M:
        d=pf[f]
        Af=sum(d[v]*T[v] for v in d)/ell[f]
        margin=rhs-(Af+m)
        acc['rows']+=1
        if margin<acc['min'][0]: acc['min']=(margin,name,n,m,f,str(Af))
        if margin<0:
            acc['viol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,f,ell[f],str(Af),str(rhs))

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
    acc={'rows':0,'viol':0,'first':None,'min':(F(10**9),'','','','','')}
    print("=== ROW-LRS EXACT gate: A_f + |M| <= N + N^2/25 per bad edge ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done (min margin=%s at %s)"%(float(acc['min'][0]),acc['min'][1:5]),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (viol=%d)"%(nn,acc['viol']-v0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,2,3,2,2,3,2]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    print("  blow-ups done (min=%s)"%(float(acc['min'][0]),),flush=True)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    for tag,wm in [("full-detour",False),("merged-detour",True)]:
        n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14)
        E=sorted(set(E+[(13,27)])) if wm else sorted(set(E)); chk(tag,n,adj_of(n,E),side,acc)
    for L in (10,12,14):
        n1,E1,s1,_=build_two_lane(L); n2,E2,s2,_=build_two_lane(L)
        E2s=[(a+n1,b+n1) for a,b in E2]; br=[(0,n1)] if s1[0]!=s2[0] else [(0,n1+1)]
        chk("stack2-L%d"%L,n1+n2,adj_of(n1+n2,sorted(set(E1+E2s+br))),s1+s2,acc)
    print("\n  total bad-edge rows=%d  ROW-LRS VIOLATIONS=%d"%(acc['rows'],acc['viol']),flush=True)
    print("  MIN ROW-LRS margin = %s at %s"%(float(acc['min'][0]),acc['min'][1:]),flush=True)
    if acc['first']: print("  first ROW-LRS violation: %s"%(acc['first'],),flush=True)
    print("  === ROW-LRS %s ==="%("VIOLATED -> fall back to global LRS" if acc['viol'] else "HOLDS exactly (per-edge local target survives, incl two-lane + adversarial)"),flush=True)
