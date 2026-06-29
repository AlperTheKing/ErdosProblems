from _M_tailswitch_gate import build_pd, cutsize
from _tail_positive_extra_counterexample import adj_from_edges
from ortools.sat.python import cp_model
def cpmax(n,edges):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=30
    s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()
for name,chords in [("nested",[(0,8),(2,6)]),("crossing",[(0,6),(2,8)])]:
    n,E=build_pd(12,chords); adj=adj_from_edges(n,E); pc=cutsize(n,adj,[v%2 for v in range(n)])
    opt,bd=cpmax(n,E)
    print("%s N=%d: parity-cut=%d CP-SAT-max=%d bound=%d parity-is-global-max=%s"%(name,n,pc,opt,bd,pc==opt==bd))
