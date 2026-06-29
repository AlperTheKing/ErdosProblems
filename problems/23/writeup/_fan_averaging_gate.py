"""FAN-AVERAGING half of ROWSUM-O: for multi-geodesic bad edges f (|cyc(f)|>1) on gamma-min cuts,
ROWSUM-O is  rowsum(f) = sum_v p_f(v) S(v) = (1/k) sum_j UPO_j,  UPO_j = sum_{v in P_j} S(v), k=|cyc(f)|.
QUESTION: does per-geodesic UPO_j <= N hold for EACH geodesic (=> fan-averaging trivial by averaging),
or only the AVERAGE rowsum(f) <= N (=> need a genuine variance/Jensen argument)?
Battery: census N<=11 gamma-min + glued islands + Mycielskians. Exact Fraction. Report, over multi-geodesic
f: #f, max rowsum(f)/N, whether all per-geodesic UPO_j<=N, and worst per-geodesic UPO_j/N."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        k=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,k)
    N=n
    for f in M:
        k=len(cyc[f])
        if k<=1: continue
        acc['multi_f']+=1
        # per-geodesic UPO_j
        ups=[sum(S[v] for v in P) for P in cyc[f]]
        rowsum=sum(ups)/k   # = sum_v p_f(v) S(v)
        # track
        if rowsum>acc['max_rowsum'][0]: acc['max_rowsum']=(rowsum,N,name,f,float(rowsum/N))
        worst_up=max(ups)
        if worst_up>acc['max_perg'][0]: acc['max_perg']=(worst_up,N,name,f,float(worst_up/N))
        if rowsum>N:
            acc['rowsum_viol']+=1
            if acc['firstrv'] is None: acc['firstrv']=(name,f,str(rowsum),N)
        if any(u>N for u in ups):
            acc['perg_viol']+=1
            if acc['firstpv'] is None: acc['firstpv']=(name,f,[str(u) for u in ups],N)

def run():
    acc={'multi_f':0,'rowsum_viol':0,'perg_viol':0,'max_rowsum':(F(-1),0,'',None,0),
         'max_perg':(F(-1),0,'',None,0),'firstrv':None,'firstpv':None}
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        m0=acc['multi_f']; rv0=acc['rowsum_viol']; pv0=acc['perg_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} gmin: multi-geo f(+{acc['multi_f']-m0}) rowsum-viol(+{acc['rowsum_viol']-rv0}) perg-UPO-viol(+{acc['perg_viol']-pv0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    glued=[("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in glued+[("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); m0=acc['multi_f']; rv0=acc['rowsum_viol']; pv0=acc['perg_viol']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin ({len(cuts)} cuts): multi-geo f(+{acc['multi_f']-m0}) rowsum-viol(+{acc['rowsum_viol']-rv0}) perg-UPO-viol(+{acc['perg_viol']-pv0})",flush=True)
    print(f"\n  total multi-geodesic f = {acc['multi_f']}",flush=True)
    print(f"  ROWSUM-O (average) violations rowsum(f)>N : {acc['rowsum_viol']}  | max rowsum/N = {acc['max_rowsum'][4]:.4f} at {acc['max_rowsum'][2]} f={acc['max_rowsum'][3]}",flush=True)
    print(f"  PER-GEODESIC UPO_j>N violations          : {acc['perg_viol']}  | max per-geo UPO/N = {acc['max_perg'][4]:.4f} at {acc['max_perg'][2]} f={acc['max_perg'][3]}",flush=True)
    if acc['firstrv']: print(f"  first rowsum violation: {acc['firstrv']}",flush=True)
    if acc['firstpv']: print(f"  first per-geodesic UPO violation: {acc['firstpv']}",flush=True)
    if acc['perg_viol']==0:
        print(f"  === FAN-AVERAGING TRIVIAL: per-geodesic UPO_j<=N holds for every geodesic => average <=N by averaging ===",flush=True)
    elif acc['rowsum_viol']==0:
        print(f"  === FAN-AVERAGING needs VARIANCE: some per-geodesic UPO_j>N but average rowsum(f)<=N always ===",flush=True)
    else:
        print(f"  === ROWSUM-O VIOLATION on gamma-min (would break the reduction) ===",flush=True)

if __name__=="__main__": run()
