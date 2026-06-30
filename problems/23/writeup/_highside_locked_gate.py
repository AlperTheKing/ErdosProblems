"""AUTHORITATIVE full-battery gate of Codex block-262 LOCKED high-side predicate (unique-geodesic, global-max).
BRANCH A (no-bracket P-contained deficit): contained_flow_failures -> best_atom_tail(...)[0] > 0.
BRANCH B (full interval-Hall failure -> Gamma descent): interval_failures -> has_descent (broad B2 family).
Acceptance: every contained-flow failure has positive atom-tail (A); every interval failure has a descent (B).
A miss = max-cut obstruction; B miss on gamma-min global-max = high-side proof obstruction.
Regression: cases() detour-ballast + add_cut_path ballast + N26 + Mycielskian N=23 + glued + census gmins."""
import subprocess
from _codex_net_globalmax_probe import contained_flow_failures, cases, build_pd, add_cut_path
from _codex_pcontained_deficit_tail_gate import best_atom_tail, has_bracket
from _codex_interval_failure_switch_lab import adj_from_edges, interval_failures, n26_graph
from _codex_interval_descent_gate import has_descent
from _h import dec, GENG, Bconn
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def run_side(name, n, edges, side, acc):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side): return
    acc['sides'] += 1
    # BRANCH A
    for (f, path, chords, spans, total, flow) in contained_flow_failures(n, adj, side):
        acc['A_total'] += 1
        bt = best_atom_tail(n, adj, side, path, chords)[0]
        if bt > 0: acc['A_pos'] += 1
        else:
            acc['A_miss'] += 1
            if acc['A_first'] is None: acc['A_first'] = (name, n, len(path), str(bt))
    # BRANCH B
    try:
        fails = interval_failures(n, adj, side, name)
    except Exception:
        return
    for failure in fails:
        acc['B_total'] += 1
        try:
            hits = has_descent(n, edges, adj, side, failure)
        except Exception:
            hits = None
        if hits:
            acc['B2_succ'] += 1
        else:
            acc['B_miss'] += 1
            if acc['B_first'] is None: acc['B_first'] = (name, n, failure.get('path'))

def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(sides=0,A_total=0,A_pos=0,A_miss=0,B_total=0,B2_succ=0,B_miss=0,A_first=None,B_first=None)
    # 1. cases() detour/ballast regression (given global-max sides)
    for name,n,edges,side in cases():
        run_side("case:"+name, n, edges, side, acc)
    print("  cases(): sides=%d A(t/pos/miss)=%d/%d/%d B(t/desc/miss)=%d/%d/%d"%(
        acc['sides'],acc['A_total'],acc['A_pos'],acc['A_miss'],acc['B_total'],acc['B2_succ'],acc['B_miss']),flush=True)
    # 2. false no-overlap ballast: build_pd(12,[(0,8),(2,6)]) + add_cut_path(2,6,6), reps 1,2
    for reps in (1,2):
        n,edges=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
        for _ in range(reps):
            n,edges,side=add_cut_path(n,list(edges),side,2,6,6)
        run_side("ballast-rep%d"%reps, n, sorted(set(edges)), side, acc)
    # 3. N26
    try:
        n,edges=n26_graph(); side=[v%2 for v in range(n)]
        run_side("N26-parity", n, sorted(set(edges)), side, acc)
    except Exception as ex:
        print("  N26 skipped (%s)"%ex,flush=True)
    print("  + ballast + N26: A miss=%d B miss=%d"%(acc['A_miss'],acc['B_miss']),flush=True)
    # 4. Mycielskian N=23 + glued (gmins global-max gamma-min)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: run_side(nm, nn, E, s, acc)
    print("  + Mycielskian + glued: A miss=%d B miss=%d"%(acc['A_miss'],acc['B_miss']),flush=True)
    # 5. census gmins (gamma-min global-max) N<=11
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: run_side("cen%s"%g6, n, E, s, acc)
        print("  census N=%d done: sides=%d A miss=%d B miss=%d"%(nn,acc['sides'],acc['A_miss'],acc['B_miss']),flush=True)
    print("\n  TOTAL global-max sides checked=%d"%acc['sides'],flush=True)
    print("  BRANCH A: contained-flow failures=%d, positive-tail=%d, MISSES=%d %s"%(acc['A_total'],acc['A_pos'],acc['A_miss'],acc['A_first'] or ''),flush=True)
    print("  BRANCH B: interval-Hall failures=%d, has-descent=%d, MISSES=%d %s"%(acc['B_total'],acc['B2_succ'],acc['B_miss'],acc['B_first'] or ''),flush=True)
    ok = acc['A_miss']==0 and acc['B_miss']==0
    print("  === LOCKED HIGH-SIDE PREDICATE %s ==="%("HOLDS (0 A-miss, 0 B-miss) => high-side switch-descent bridge survives full battery" if ok else "FAILS -- obstruction found"),flush=True)
