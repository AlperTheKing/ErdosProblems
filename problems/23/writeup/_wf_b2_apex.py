"""Drill into the binding witnesses (Myc apex, T/N=5/3) to find a PROVABLE bound.
For each vertex v on each gamma-min cut, decompose T[v] = sum_f c_f(v), c_f(v)=w_f*(#f-geos thru v).
Test candidate clean bounds (residual>0 => FALSE):
  (P1) c_f(v) <= w_f*|cyc_f| = ell_f  (per-bad-edge cap; trivially true)  -> verify tight cases
  (P2) #{bad edges f with c_f(v)>0} <= dc[v]   (v on a geo of f => v has a B-edge into the geo)
  (P3) T[v] <= dc[v]*max_f ell_f / 2 ... explore
  (P4) T[v] <= N + (dc[v]/2)*? ...
  Most important: gather (v, T, dc, dm, list of (ell_f, c_f)) at the top-ratio vertices to SEE structure.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, blow, Bconn, bdist_restr
from _bdef_construct import Cn, mycielski, is_triangle_free
from _satzmu_conn import struct_for_side
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees
from ortools.sat.python import cp_model

def per_f_load(n,adj,side):
    """return per-vertex list of (f, ell_f, c_f(v))."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    contrib={v:[] for v in range(n)}
    for f in M:
        Ps=cyc[f]; w=F(ell[f],len(Ps))
        cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): contrib[v].append((f,ell[f],w*c))
    return M,ell,T,contrib

def analyze(name,n,adj,side,top):
    cd=cut_data(n,adj,side)
    if cd is None: return
    pf=per_f_load(n,adj,side)
    if pf is None: return
    M,ell,T,contrib=pf; N=n; dc,dm=cut_degrees(cd)
    for v in range(N):
        r=F(T[v],N)
        top.append((r,name,v,N,float(T[v]),dc[v],dm[v],
                    sorted([(el,float(c)) for (_,el,c) in contrib[v]],reverse=True)[:8],
                    len(contrib[v])))

def brute(name,n,E,top):
    if not is_triangle_free(n,E): return
    adj,cuts=gmin_cuts(n,E)
    for s in cuts: analyze(name,n,adj,s,top)

def cp_connmaxcuts(N,E):
    adj=[set() for _ in range(N)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]; tt=[]
    for a,b in E:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); tt.append(z)
    m.Maximize(sum(tt)); sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=60; sv.Solve(m)
    opt=int(sv.ObjectiveValue()); m.Add(sum(tt)==opt)
    class C(cp_model.CpSolverSolutionCallback):
        def __init__(s): super().__init__(); s.sols=[]
        def on_solution_callback(s):
            s.sols.append([int(s.Value(x[i])) for i in range(N)])
            if len(s.sols)>=100: s.StopSearch()
    sv2=cp_model.CpSolver(); sv2.parameters.enumerate_all_solutions=True; sv2.parameters.max_time_in_seconds=60
    c=C(); sv2.Solve(m,c)
    return adj,[s for s in c.sols if Bconn(N,adj,s)]

if __name__=="__main__":
    top=[]
    for nn in range(8,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: brute("c"+g6,*dec(g6),top)
        print(f"  census N={nn} done",flush=True)
    for t in range(2,5): brute(f"C5[{t}]",*blow(t),top)
    brute("Grotzsch11",*mycielski(5,Cn(5)),top)
    for nm,(N,E) in [("MycC7_15",mycielski(7,Cn(7))),("Myc2C5_23",mycielski(*mycielski(5,Cn(5))))]:
        adj,cuts=cp_connmaxcuts(N,E)
        for s in cuts: analyze(nm,N,adj,s,top)
        print(f"  {nm} done",flush=True)
    top.sort(key=lambda x:x[0],reverse=True)
    print("\n=== TOP-10 highest T/N vertices: (ratio, where, v, N, T, dc, dm, [(ell,c_f)..], #bad-on-v) ===")
    seen=set()
    for rec in top:
        key=(rec[1],round(float(rec[0]),4))
        if key in seen: continue
        seen.add(key)
        r,name,v,N,T,dc,dm,cl,nb=rec
        print(f"  r={float(r):.4f} {name} v={v} N={N} T={T} dc={dc} dm={dm} nbad={nb} contribs(ell,c)={cl}")
        if len(seen)>=12: break
