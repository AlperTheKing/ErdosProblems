"""Pin down the counting lemma for (ZMU-SUM-both).
Define for a zero-mu both-pos edge uv:
  F_u={f:p_f(u)>0}, F_v sym; U_u=union supp(F_u), U_v=union supp(F_v).  (support-disjoint: u notin U_v, v notin U_u)
Test the candidate chain:
  (C-union) T(u)+T(v) <= |U_u ∪ U_v|   [then <= N trivially since U⊆V]
  (C-budget-u) T(u) <= |U_u|    (per-side)
  (C-strong) T(u) <= |U_u| - |U_u ∩ U_v| + (overlap-adjusted)?  -- examine overlap behaviour.
Also: is T(u) <= (#vertices of B reachable from u via F_u-geodesics ON u's SIDE of the edge)? Decompose by side.
Loads-cut census N<=11. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def analyze(g6, info):
    N=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; mu=mu_edges(info); side=info['side']
    pf={}; supp={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); s=set()
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
    out=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if not (T[u]>0 and T[v]>0): continue
        Fu=[f for f in M if pf.get((f,u),0)>0]; Fv=[f for f in M if pf.get((f,v),0)>0]
        Uu=set().union(*[supp[f] for f in Fu]) if Fu else set()
        Uv=set().union(*[supp[f] for f in Fv]) if Fv else set()
        union=Uu|Uv
        c_union = (T[u]+T[v] <= len(union))
        c_bud_u = (T[u] <= len(Uu)); c_bud_v=(T[v]<=len(Uv))
        out.append((g6,u,v,str(T[u]),str(T[v]),len(Uu),len(Uv),len(union),N,c_union,c_bud_u,c_bud_v))
    return out

if __name__=="__main__":
    print("=== counting lemma probes for ZMU-SUM-both ===")
    tot=0; cu=0; bu=0; bv=0; worstgap=None
    for nn in range(10,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(g6,info):
                tot+=1
                if r[9]: cu+=1
                if r[10]: bu+=1
                if r[11]: bv+=1
                # track tightest union-gap
                gap=r[7]-(F(r[3])+F(r[4]))  # |union| - (Tu+Tv)
    print(f"both-pos zero-mu edges: total={tot}")
    print(f"  (C-union) T(u)+T(v)<=|U_u∪U_v|: holds {cu}/{tot}")
    print(f"  (C-budget-u) T(u)<=|U_u|: {bu}/{tot}    (C-budget-v) T(v)<=|U_v|: {bv}/{tot}")
