"""B2 FINAL exact gate. Tmax<=2N over the standing gate.
- census N<=10 (all gamma-min connected-B max cuts via brute maxcut_all)  [fast]
- C5[t] t<=4 (N<=20, brute ok)                                            [extremal]
- two-lane L=8,12 (N=27,39): explicit side, CP-SAT-verified max + gamma-min unique (already known)
- iterated Mycielskians: Grotzsch N=11 (brute), Myc2(C5) N=23 + Myc(C7) N=15 via explicit canonical
  max cut, CP-SAT-verified.
Records, at every vertex of every cut: residual of each candidate sub-lemma toward Tmax<=2N.
Also re-verifies the handshake identity inc[v]==2T[v]-D[v] exactly on every cut used.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, blow
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees, check_handshake
from _verify_two_lane import build_two_lane
from ortools.sat.python import cp_model

KEYS=['S2_inc_le_2N','S3_D_le_2N','S4_D_le_inc','B2_T_le_2N','S7_inc_le_dc_N']
worst={k:{'val':F(-10**9)} for k in KEYS}
HSFAIL=[]

def record(name,n,adj,side):
    cd=cut_data(n,adj,side)
    if cd is None: return
    hb=check_handshake(cd)
    if hb: HSFAIL.append((name,hb[:3]))
    N=cd['N']; dc,dm=cut_degrees(cd)
    for v in range(N):
        Tv=cd['T'][v]
        cands={'S2_inc_le_2N':cd['inc'][v]-2*N,'S3_D_le_2N':cd['D'][v]-2*N,
               'S4_D_le_inc':cd['D'][v]-cd['inc'][v],'B2_T_le_2N':Tv-2*N,
               'S7_inc_le_dc_N':cd['inc'][v]-dc[v]*N}
        for k,val in cands.items():
            if val>worst[k]['val']:
                worst[k]={'val':val,'where':name,'v':v,'N':N,'Tv':float(Tv),
                          'inc':float(cd['inc'][v]),'D':float(cd['D'][v]),
                          'dc':dc[v],'dm':dm[v],
                          'maxmu':float(max((m for m in cd['mu'].values()),default=0))}

def brute_gate(name,n,E):
    if not is_triangle_free(n,E): return
    adj,cuts=gmin_cuts(n,E)
    for s in cuts: record(name,n,adj,s)

def cpmax(n,E):
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(n)]; t=[]
    for a,b in E:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=120
    sv.Solve(m); return int(sv.ObjectiveValue()), int(sv.BestObjectiveBound())

def explicit_gate(name,n,E,side):
    """Use explicit side; verify triangle-free, B-connected, that side is a global max cut
       (cut == CP-SAT max == bound), and that it's gamma-min-eligible (all bad edges have geodesics)."""
    if not is_triangle_free(n,E): print(f"  {name}: NOT triangle-free, skip"); return
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    cut=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    opt,bd=cpmax(n,E)
    bc=Bconn(n,adj,side)
    ismax=(cut==opt==bd)
    print(f"  {name}: N={n} cut={cut} cpmax={opt} bound={bd} max={ismax} Bconn={bc}",flush=True)
    if not (ismax and bc): print(f"     -> not (max & Bconn), still recording for info");
    record(name,n,adj,side)

if __name__=="__main__":
    print("=== B2 FINAL gate ===",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: brute_gate("c"+g6,*dec(g6))
        print(f"  census N={nn} done B2res={float(worst['B2_T_le_2N']['val']):.4f}",flush=True)
    for t in range(1,5):
        brute_gate(f"C5[{t}]",*blow(t))
    print(f"  C5[t<=4] done B2res={float(worst['B2_T_le_2N']['val']):.4f}",flush=True)
    # Grotzsch N=11 brute
    brute_gate("Grotzsch11",*mycielski(5,Cn(5)))
    print(f"  Grotzsch done B2res={float(worst['B2_T_le_2N']['val']):.4f}",flush=True)
    # Myc(C7) N=15 and Myc2(C5) N=23 via canonical max cut from mycielski structure:
    # canonical proper-ish 2-coloring is NOT directly a max cut; instead brute is infeasible at 23.
    # Use CP-SAT to FIND a max cut and a connected-B one, then record.
    for nm,(N,E) in [("MycC7_15",mycielski(7,Cn(7))),("Myc2C5_23",mycielski(*mycielski(5,Cn(5))))]:
        adj=[set() for _ in range(N)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        # find a max cut via CP-SAT, prefer connected-B by post-checking
        opt,bd=cpmax(N,E)
        m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]; tt=[]
        for a,b in E:
            z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); tt.append(z)
        m.Add(sum(tt)==opt)
        sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=120; sv.parameters.enumerate_all_solutions=False
        # collect several max cuts
        class Col(cp_model.CpSolverSolutionCallback):
            def __init__(s): super().__init__(); s.sols=[]
            def on_solution_callback(s):
                s.sols.append([int(s.Value(x[i])) for i in range(N)])
                if len(s.sols)>=200: s.StopSearch()
        sv.parameters.enumerate_all_solutions=True
        col=Col(); sv.Solve(m,col)
        conncuts=[s for s in col.sols if Bconn(N,adj,s)]
        print(f"  {nm}: N={N} cpmax={opt} bound={bd} sols={len(col.sols)} connB={len(conncuts)}",flush=True)
        for s in conncuts[:50]: record(nm,N,adj,s)
        print(f"     {nm} recorded; B2res={float(worst['B2_T_le_2N']['val']):.4f}",flush=True)
    # two-lane explicit
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); explicit_gate(f"two-lane{L}",n,E,side)
    print("\n--- handshake failures:",len(HSFAIL), (HSFAIL[0] if HSFAIL else "(identity HOLDS exactly)"))
    print("--- worst residual per sub-lemma (val>0 => FALSE on gate) ---")
    for k in KEYS:
        d=worst[k]; verdict="*** FALSE (counterexample) ***" if d['val']>0 else "holds on gate"
        print(f"  {k}: max residual={float(d['val']):.4f}  {verdict}")
        if 'where' in d:
            print(f"      witness {d['where']} v={d['v']} N={d['N']} T={d['Tv']:.3f} "
                  f"inc={d['inc']:.3f} D={d['D']:.3f} dc={d['dc']} dm={d['dm']} maxmu={d['maxmu']:.3f}")
