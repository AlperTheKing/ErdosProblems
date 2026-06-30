"""Rigorously confirm the B2 GLOBAL-max breaker and verify PATH/ROW/LRS survive it.
Cases: L=12 k=4 gap=6 (N=65) and L=14 k=4 gap=8 (N=75). Confirm:
  - triangle-free, Bconn
  - CP-SAT OPTIMAL with opt==bound==parity-cut  (global max, exact)
  - exact maxT > 2N (B2 fails) while PATH/ROW/LRS all hold (exact Fraction slacks)
Also enumerate ALL max cuts (CP-SAT solution-count) to report uniqueness/gamma-min context.
"""
from fractions import Fraction as F
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize, cpmax, lrs_check
from _satzmu_conn import struct_for_side
from _h import Bconn
from ortools.sat.python import cp_model

def greedy_chords(L,k,gap):
    base_n,base_E,_,_=build_k_lane(L,k,[])
    adj=[set() for _ in range(base_n)]
    for a,b in base_E: adj[a].add(b); adj[b].add(a)
    chords=[]
    cand=[(a,b) for a in range(0,L+1) for b in range(a+gap,L+1) if (a%2)==(b%2)]
    for (a,b) in cand:
        if b in adj[a] or (adj[a]&adj[b]): continue
        adj[a].add(b);adj[b].add(a);chords.append((a,b))
    return chords

def count_maxcuts(n,edges,opt,cap=50):
    """Count distinct max cuts (up to global complement) with objective==opt."""
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Add(sum(t)==opt); m.Add(x[0]==0)  # fix gauge (kill complement symmetry)
    sols=[]
    class CB(cp_model.CpSolverSolutionCallback):
        def __init__(s):
            cp_model.CpSolverSolutionCallback.__init__(s); s.c=0
        def on_solution_callback(s):
            s.c+=1
            sols.append(tuple(int(s.Value(x[i])) for i in range(n)))
            if s.c>=cap: s.StopSearch()
    sv=cp_model.CpSolver(); sv.parameters.enumerate_all_solutions=True
    sv.parameters.max_time_in_seconds=120
    sv.Solve(m,CB()); return len(sols),sols

for (L,k,gap) in [(12,4,6),(14,4,8)]:
    bad=greedy_chords(L,k,gap)
    n,E,side,bad=build_k_lane(L,k,bad)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    tf=trifree(n,adj); bc=Bconn(n,adj,side); pc=cutsize(n,adj,side)
    opt,bd,iso=cpmax(n,E,120)
    gm=(pc==opt==bd) and iso
    r=lrs_check(n,adj,side)
    nmax,sols=count_maxcuts(n,E,opt,cap=40)
    print("="*70)
    print("L=%d k=%d gap=%d N=%d edges=%d"%(L,k,gap,n,len(E)))
    print("  triangle-free=%s  Bconn=%s"%(tf,bc))
    print("  parity-cut=%d  CP-SAT opt=%d  bound=%d  OPTIMAL=%s  -> GLOBALMAX=%s"%(pc,opt,bd,iso,gm))
    print("  #max-cuts (gauge-fixed x0=0, capped 40)=%d  parity-cut-is-among-them=%s"%(
        nmax, tuple(side) in sols or tuple(1-s for s in side) in sols))
    print("  |M|=%d  N^2/25=%s  |M|/(N^2/25)=%.4f"%(r['absM'],str(r['N2_25']),float(r['ratioM'])))
    print("  EXACT maxT=%s = %.4f ;  2N=%d ;  maxT/2N=%.4f"%(str(r['maxT']),float(r['maxT']),2*n,float(r['maxT']/(2*n))))
    print("  B2 (maxT<=2N): %s   [%s]"%("HOLDS" if r['B2_ok'] else "FAILS", str(r['maxT'])+" vs "+str(2*n)))
    sl=r['pathworst'][0]; print("  PATH-LRS: %s  min exact slack=%s = %.4f"%("HOLDS" if r['PATH_ok'] else "FAILS",str(sl),float(sl)))
    sl=r['rowworst'][0]; print("  ROW-LRS : %s  min exact slack=%s = %.4f"%("HOLDS" if r['ROW_ok'] else "FAILS",str(sl),float(sl)))
    print("  LRS     : %s  lhs=%s rhs=%s slack=%s"%("HOLDS" if r['LRS_ok'] else "FAILS",
          str(r['LRS_lhs']),str(r['LRS_rhs']),str(r['LRS_rhs']-r['LRS_lhs'])))
    # graph6-ish: dump edge list + side for the witness
    print("  side=%s"%side)
    print("  bad(monochromatic)=%s"%bad)
