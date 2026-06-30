"""Exact worst Tmax/N over the B2 gate, plus the inc/D split at the argmax vertex.
Also tests the combined sub-lemma  inc[v] <= dc[v]*N  (S7, tight) and
  D[v] <= dm[v]*N  with the max-cut handshake  dc[v] >= dm[v].
Reuses the cuts from the FINAL gate but reports the actual max ratio and its witness."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, blow, Bconn
from _bdef_construct import Cn, mycielski, is_triangle_free
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees
from ortools.sat.python import cp_model

best={'r':F(0)}
# S7 per-edge: is mu(e) <= N for EVERY cut-edge? (stronger than the averaged S7)
muedge={'val':F(-10**9)}
# does dc[v] >= dm[v] (max-cut local optimality) hold? and dc>=#bad-incident?
maxcut_local_fail=[]

def scan(name,n,adj,side):
    cd=cut_data(n,adj,side)
    if cd is None: return
    N=cd['N']; dc,dm=cut_degrees(cd)
    for v in range(N):
        r=F(cd['T'][v],N)
        if r>best['r']:
            best.update(r=r,name=name,v=v,N=N,T=float(cd['T'][v]),
                        inc=float(cd['inc'][v]),D=float(cd['D'][v]),dc=dc[v],dm=dm[v])
        if dc[v]<dm[v]: maxcut_local_fail.append((name,v,dc[v],dm[v]))
    for e,val in cd['mu'].items():
        if val-N>muedge['val']: muedge.update(val=val-N,where=name,e=e,muval=float(val),N=N)

def brute(name,n,E):
    if not is_triangle_free(n,E): return
    adj,cuts=gmin_cuts(n,E)
    for s in cuts: scan(name,n,adj,s)

def cp_connmaxcuts(N,E,cap=50):
    adj=[set() for _ in range(N)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]; tt=[]
    for a,b in E:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); tt.append(z)
    m.Maximize(sum(tt)); sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=60; sv.Solve(m)
    opt=int(sv.ObjectiveValue())
    m.Add(sum(tt)==opt)
    class C(cp_model.CpSolverSolutionCallback):
        def __init__(s): super().__init__(); s.sols=[]
        def on_solution_callback(s):
            s.sols.append([int(s.Value(x[i])) for i in range(N)])
            if len(s.sols)>=200: s.StopSearch()
    sv2=cp_model.CpSolver(); sv2.parameters.enumerate_all_solutions=True; sv2.parameters.max_time_in_seconds=60
    c=C(); sv2.Solve(m,c)
    return adj,[s for s in c.sols if Bconn(N,adj,s)]

if __name__=="__main__":
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: brute("c"+g6,*dec(g6))
        print(f"  census N={nn} done worstratio={float(best['r']):.4f}",flush=True)
    for t in range(1,5): brute(f"C5[{t}]",*blow(t))
    brute("Grotzsch11",*mycielski(5,Cn(5)))
    print(f"  small+blowups done worstratio={float(best['r']):.4f}",flush=True)
    for nm,(N,E) in [("MycC7_15",mycielski(7,Cn(7))),("Myc2C5_23",mycielski(*mycielski(5,Cn(5))))]:
        adj,cuts=cp_connmaxcuts(N,E)
        for s in cuts: scan(nm,N,adj,s)
        print(f"  {nm} done worstratio={float(best['r']):.4f}",flush=True)
    print("\n=== WORST Tmax/N over gate ===")
    print(f"  ratio={float(best['r']):.6f} = {best['r']}  at {best.get('name')} v={best.get('v')} "
          f"N={best.get('N')} T={best.get('T')} inc={best.get('inc')} D={best.get('D')} dc={best.get('dc')} dm={best.get('dm')}")
    print(f"  per-edge mu(e)<=N: max(mu-N)={float(muedge['val']):.4f} "
          f"{'FALSE '+str(muedge) if muedge['val']>0 else 'HOLDS'}")
    print(f"  max-cut local opt dc>=dm: {'FAILS '+str(maxcut_local_fail[:3]) if maxcut_local_fail else 'HOLDS everywhere'}")
