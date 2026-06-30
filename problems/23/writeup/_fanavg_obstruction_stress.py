"""Stress the FAN-AVERAGING variance inequality n(n-row_f)>=var_f on the NEW obstruction-style constructions
(the kind that just killed scalar NET), to check it is not census-blind. Build odd-cycle blow-ups WITH a
redundant full parallel detour between a bad-edge's endpoints (the merged/full-detour ballast that broke
scalar NET), CP-SAT max-verify the cut, and check the variance inequality on every MULTI-GEODESIC bad row.
Also report the disjoint/full/merged-detour graphs' multi-geodesic rows (if any)."""
from fractions import Fraction as F
from _M_tailswitch_gate import build_pd, cutsize
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _satzmu_conn import struct_for_side
from _h import Bconn, bdist_restr
from _bdef_construct import Cn
from ortools.sat.python import cp_model

def cpmax(n,edges):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=30
    s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()
def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE)),off

def variance_check(name,n,E,side):
    adj=adj_from_edges(n,E)
    if not Bconn(n,adj,side): print("  %s: parity NOT Bconn"%name); return
    opt,bd=cpmax(n,E); pc=cutsize(n,adj,side)
    st=struct_for_side(n,adj,side)
    if st is None: print("  %s: struct None (parity not a valid max-cut structure)"%name); return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    nmulti=0; worst=None
    for f in M:
        if len(cyc[f])<2: continue
        nmulti+=1
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
        var=sum(d[v]*(S[v]-mean)**2 for v in d)
        margin=F(n)*(F(n)-row)-var
        if worst is None or margin<worst[0]: worst=(margin,f,str(row),str(var))
    print("  %s: n=%d parity-cut=%d CPSATmax=%d global-max=%s multi-geo-rows=%d worst-variance-margin=%s"%(
        name,n,pc,opt,pc==opt==bd,nmulti,worst[0] if worst else "na (no multi-geo rows)"))
    if worst and worst[0]<0: print("     *** VARIANCE FAILS: %s ***"%(worst,))

print("=== FAN-AVERAGING variance stress on obstruction-style constructions ===",flush=True)
# odd-cycle blow-ups (multi-geodesic) + redundant full parallel detour between class-0/class-1 vertices
for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,4,2,4,2,4,2],[2,2,2,2,2,2,2]]:
    n,E,off=blowup(parts); side=[ (i if i<len(off)-1 else 0) for i in range(n)]
    # proper parity-ish 2-coloring of the odd cycle blow-up: color by class index parity won't 2-color odd cycle;
    # use the max-cut structure's own side via CP-SAT optimal assignment
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in E:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=20; s.Solve(m)
    side=[int(s.Value(xi)) for xi in x]
    variance_check("C%d%s"%(len(parts),parts),n,E,side)
    # add a redundant detour between two same-class vertices (a bad edge's endpoints under this cut)
    # pick u,v same side, non-adjacent; add an all-cut path of even length
    import itertools
    pair=None
    for u,v in itertools.combinations(range(n),2):
        if side[u]==side[v] and v not in adj_from_edges(n,E)[u]: pair=(u,v); break
    if pair:
        u,v=pair; n2,E2,side2=add_cut_path(n,list(E),list(side),u,v,6)
        variance_check("C%d%s+detour(%d,%d)"%(len(parts),parts,u,v),n2,sorted(set(E2)),side2)
