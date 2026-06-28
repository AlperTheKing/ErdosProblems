"""Find and dump the FIRST census-N=9 row-Hall (RH) failure witness in detail, to check if it is a checker bug
   or a real failure of Codex's c_f(o) transport certificate."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def pf_dict(cyc, f):
    Ps=cyc[f]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d

def examine(g6, adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T2,mu,cyc=st
    K,T=build_K(adj,side,n); N=n
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    pf={f:pf_dict(cyc,f) for f in M}
    supp={f:set(pf[f].keys()) for f in M}
    Xf={f:sum(pf[f].get(o,F(0)) for o in O) for f in M}
    s={q:sum(K[o][q] for o in O) for q in Q}
    Ml=list(M)
    for o in O:
        psi={q:(K[o][q]/(F(N)-T[q]+s[q])) for q in Q if (F(N)-T[q]+s[q])>0}
        cf={f: Xf[f]*(pf[f].get(o,F(0)) + sum(psi.get(q,F(0))*pf[f].get(q,F(0)) for q in Q)) for f in M}
        for r in range(1,1<<len(Ml)):
            H=[Ml[i] for i in range(len(Ml)) if r>>i&1]
            dem=sum(cf[f] for f in H)
            unionsupp=set().union(*[supp[f] for f in H])
            if dem>len(unionsupp):
                print(f"RH-FAIL g6={g6} side={''.join(map(str,side))} N={N}")
                print(f"  O={O} T_O={[ (o,str(T[o])) for o in O]}")
                print(f"  bad edges M={Ml}  ell={[ell[f] for f in Ml]}")
                print(f"  fixed o={o}")
                print(f"  subset H={H}")
                print(f"  sum c_f(o) over H = {dem} = {float(dem):.4f}")
                print(f"  |union supp| = {len(unionsupp)}  union={sorted(unionsupp)}")
                print(f"  per-f in H: " + "; ".join(f"f={f} Xf={Xf[f]} cf={float(cf[f]):.4f} supp={sorted(supp[f])}" for f in H))
                print(f"  full-set sum c_f(o) = {float(sum(cf.values())):.4f} vs N={N} (ROW-SUM full-set)")
                print(f"  ROW-SUM check: sum_q K[o,q]R_q/(R_q+s_q) = {float(sum(K[o][q]*(F(N)-T[q])/(F(N)-T[q]+s[q]) for q in Q if (F(N)-T[q]+s[q])>0)):.4f} vs T(o)-N={float(T[o]-N):.4f}")
                return True
    return False

if __name__=="__main__":
    outg=subprocess.run([GENG,"-tc","9"],capture_output=True,text=True).stdout.split()
    found=0
    for g6 in outg:
        n,E=dec(g6)
        adj,cuts=gmins(n,E)
        for s in cuts:
            if examine(g6,adj,s,n):
                found+=1; break
        if found>=2: break
    print(f"\n(examined; printed {found} witnesses)")
