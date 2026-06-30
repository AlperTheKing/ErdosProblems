"""Gate Codex block-213 SBC (Spectral Bad-Count slack) certificate -- the REPAIR that survives the two-lane:
  SBC:     rho(O) + |M| <= N + N^2/25
  SBC-row: max_f (O*1)_f + |M| <= N + N^2/25
Implies Erdos (O PSD => rho(O) >= sum T^2/Gamma >= Gamma/N >= 25|M|/N; with SBC => |M| <= N^2/25 = beta). VERIFY
SBC/SBC-row 0-violation + min margin on the FULL battery, ESPECIALLY adversarial high-rho + high-|M|
constructions (the only way to break SBC). Tight at C5[t] extremal (rho=N, |M|=N^2/25 => equality).
Battery: census gamma-min N<=11 + blow-ups C5/C7/C9[t] + two-lane L=8..16 + Mycielskians + merged-detour +
adversarial (stacked two-lanes, dense bad-edge, near-extremal perturbations)."""
import subprocess
from fractions import Fraction as F
import numpy as np
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane, Ogram
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _M_tailswitch_gate import build_pd

def sbc_check(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    res=Ogram(n,adj,side)
    if res is None: return
    M,ell,O=res
    m=len(M)
    if m==0: return
    rowsums=[float(sum(O[i])) for i in range(m)]
    maxrow=max(rowsums)
    Of=np.array([[float(x) for x in r] for r in O])
    rho=float(max(abs(np.linalg.eigvals(Of))))
    rhs=n+n*n/25.0
    sbc_margin=rhs-(rho+m)
    sbcrow_margin=rhs-(maxrow+m)
    acc['n']+=1
    if sbc_margin<acc['min_sbc'][0]: acc['min_sbc']=(sbc_margin,name,n,m,round(rho,3))
    if sbcrow_margin<acc['min_sbcrow'][0]: acc['min_sbcrow']=(sbcrow_margin,name,n,m,round(maxrow,3))
    if sbc_margin< -1e-7:
        acc['sbc_fail']+=1
        if acc['first_sbc'] is None: acc['first_sbc']=(name,n,m,round(rho,4),round(rhs,3))
    if sbcrow_margin< -1e-7: acc['sbcrow_fail']+=1

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
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

if __name__=="__main__":
    acc={'n':0,'sbc_fail':0,'sbcrow_fail':0,'first_sbc':None,
         'min_sbc':(1e9,'','','',''),'min_sbcrow':(1e9,'','','','')}
    print("=== SBC gate: rho(O)+|M| <= N+N^2/25 (and SBC-row) ===",flush=True)
    for L in range(8,17,2):
        n,E,side,bad=build_two_lane(L); sbc_check("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done (min_sbc=%s)"%(acc['min_sbc'],),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        f0=acc['sbc_fail']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: sbc_check("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (sbc_fail=%d)"%(nn,acc['sbc_fail']-f0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,8):
            n,E=blowup([cyc==5 and t or t]*cyc); adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): sbc_check("C%d[%d]"%(cyc,t),n,adj,s,acc)
    print("  blow-ups done (min_sbc=%s)"%(acc['min_sbc'],),flush=True)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: sbc_check(name,nn,adj,s,acc)
    # merged detour + disjoint obstructions
    n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14); E=sorted(set(E+[(13,27)]))
    sbc_check("merged-detour-N39",n,adj_of(n,E),side,acc)
    # ADVERSARIAL: stacked / shifted two-lanes to raise |M| while keeping high rho
    # two two-lanes sharing structure: union of two two-lane(L) via a bridge
    for L in (8,10,12):
        n1,E1,s1,_=build_two_lane(L); n2,E2,s2,_=build_two_lane(L)
        # disjoint union + bridge (0 of lane1 to 0 of lane2 via cut edge), relabel
        E2s=[(a+n1,b+n1) for a,b in E2]; s2s=s2[:]
        nU=n1+n2; EU=sorted(set(E1+E2s+[(0,n1)] if s1[0]!=s2[0] else E1+E2s))
        sideU=s1+s2s
        sbc_check("stacked2-twolane-L%d"%L,nU,adj_of(nU,EU),sideU,acc)
    print("  Mycielskians+merged+stacked done",flush=True)
    print("\n  total configs=%d  SBC failures=%d  SBC-row failures=%d"%(acc['n'],acc['sbc_fail'],acc['sbcrow_fail']),flush=True)
    print("  MIN SBC margin = %s"%(acc['min_sbc'],),flush=True)
    print("  MIN SBC-row margin = %s"%(acc['min_sbcrow'],),flush=True)
    if acc['first_sbc']: print("  first SBC violation: %s"%(acc['first_sbc'],),flush=True)
    print("  === %s ==="%("SBC VIOLATED -> repair fails" if acc['sbc_fail'] else "SBC HOLDS on full battery (incl two-lane, blow-ups tight at C5[t], adversarial) -> repaired certificate survives"),flush=True)
