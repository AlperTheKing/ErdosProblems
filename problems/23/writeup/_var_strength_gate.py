"""Exact gate for Codex's VARIANCE strengthening of ROWSUM-O (block 137):
for every bad edge f:  n*(n - row_f) >= var_f,  where
  p_f(v)=fraction of f-geodesics through v, S(v)=sum_g p_g(v),
  row_f=sum_v p_f(v)S(v), ell_f=sum_v p_f(v), mean=row_f/ell_f,
  var_f=sum_v p_f(v)*(S(v)-mean)^2.
Implies ROWSUM-O; vanishes on all-tie. Full battery: census N<=11 (uncapped), witnesses, Mycielskians N<=23,
glued islands, explicit medium blow-ups. Reports first counterexample (g6, side, f, row, ell, var, margin)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint, blow_g

def rows_var(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    out=[]
    for f in M:
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
        mean=row/ll
        var=sum(d[v]*(S[v]-mean)**2 for v in d)
        ok = F(n)*(F(n)-row) >= var
        out.append((f,row,ll,var,F(n)*(F(n)-row)-var,ok))
    return out

def test_graph(name,n,E,first=[None]):
    adj,cuts=gmins(n,E)
    fails=0; tot=0; worstmargin=None
    for s in cuts:
        rv=rows_var(n,adj,s)
        if rv is None: continue
        for (f,row,ll,var,margin,ok) in rv:
            tot+=1
            if worstmargin is None or margin<worstmargin: worstmargin=margin
            if not ok:
                fails+=1
                if first[0] is None:
                    first[0]=(name,''.join(map(str,s)),f,str(row),ll,str(var),str(margin))
    return tot,fails,worstmargin

if __name__=="__main__":
    print("=== VARIANCE strengthening gate: n*(n-row_f) >= var_f (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        T=Fl=0; wm=None
        for g6 in outg:
            n,E=dec(g6)
            t,f,w=test_graph(g6,n,E,first)
            T+=t; Fl+=f
            if w is not None and (wm is None or w<wm): wm=w
        print(f"  census N={nn}: rows={T} FAILS={Fl} worst-margin={wm}({float(wm) if wm is not None else None:.4f})",flush=True)
    # witnesses + structured
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("GDSKVG",)+dec("GDSKVG"),
           ("Grotzsch",)+mycielski(5,Cn(5)),
           ("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           # explicit medium blow-ups (build graph): C5[t] balanced + a couple unbalanced
           ("C5[3]",)+blow_g(5,Cn(5),3),
           ("C5[4]",)+blow_g(5,Cn(5),4),
           ("C7[3]",)+blow_g(7,Cn(7),3)]
    print("  [witnesses/structured]",flush=True)
    for it in extra:
        t,f,w=test_graph(*it,first)
        print(f"    {it[0]}: rows={t} FAILS={f} worst-margin={float(w) if w is not None else None}",flush=True)
    print(f"\n=== FIRST COUNTEREXAMPLE: {first[0]} ===" if first[0] else "\n=== NO COUNTEREXAMPLE on battery (census N<=11 + witnesses + Mycielskians N<=23 + glued + blowups) ===",flush=True)
