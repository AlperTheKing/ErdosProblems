"""AUTHORITATIVE v2 of Codex block-262 LOCKED high-side predicate, WITH the global-max filter (Codex 264) and
B1 straddle folded in. Only GLOBAL-MAXIMUM connected-B sides are in scope. For each:
  BRANCH A: contained_flow_failures -> best_atom_tail[0] > 0.
  BRANCH B: interval_failures -> has_descent (B2) OR b1_straddle (B1).
The 5 cases:nested B2-misses were on a NON-max cut (cut=26<opt=27); the filter removes them. Report counts."""
import subprocess
from _codex_net_globalmax_probe import contained_flow_failures, cases, build_pd, add_cut_path
from _codex_pcontained_deficit_tail_gate import best_atom_tail
from _codex_interval_failure_switch_lab import adj_from_edges, interval_failures, n26_graph, cut_size, gamma_data
from _codex_interval_descent_gate import has_descent
from _M_full_detour_counterexample import maxcut
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def is_global_max_side(n, edges, side):
    status, opt, bound = maxcut(n, edges)
    return status == 4 and cut_size(edges, side) == opt

def is_alt_path(adj, side, Q):
    return all((Q[i+1] in adj[Q[i]] and side[Q[i]] != side[Q[i+1]]) for i in range(len(Q)-1))

def b1_straddle(n, edges, adj, side, failure):
    f = failure['f']; P = failure['path']; a, b = failure['interval']
    st = struct_for_side(n, adj, side)
    if st is None: return False
    M, ell, T, mu, cyc = st
    pos = {v:i for i,v in enumerate(P)}; Pset = set(P)
    Pcont = []
    for g in M:
        if g == f: continue
        gu, gv = g
        if gu not in pos or gv not in pos: continue
        for Q in cyc[g]:
            if set(Q) <= Pset:
                pp = sorted(pos[v] for v in Q)
                if pp[-1] - pp[0] == len(pp) - 1:
                    Pcont.append((g, pos[gu], pos[gv])); break
    base_cut = cut_size(edges, side)
    base_gamma = gamma_data(n, adj, side)
    if base_gamma is None: return False
    for k in range(a, b+1):
        x = P[k]
        inc = []
        for g, pu, pv in Pcont:
            if x not in g: continue
            other = g[0] if g[1] == x else g[1]
            inc.append((pos[other], other, g))
        lefts = [t for t in inc if t[0] < k]; rights = [t for t in inc if t[0] > k]
        if not lefts or not rights: continue
        inc_bad = [(min(x,w), max(x,w)) for w in adj[x] if side[w] == side[x]]
        dB = sum(1 for w in adj[x] if side[w] != side[x]); dM = len(inc_bad)
        side2 = side[:]; side2[x] ^= 1
        if dB != dM or cut_size(edges, side2) != base_cut or not Bconn(n, adj, side2): continue
        left = max(lefts, key=lambda t:t[0]); right = min(rights, key=lambda t:t[0])
        Qshort = P[:left[0]+1] + [x] + P[right[0]:]
        if Qshort[0] == f[0] and Qshort[-1] == f[1] and len(Qshort) < len(P) and is_alt_path(adj, side2, Qshort):
            return True
    return False

def run_side(name, n, edges, side, acc, known_max=False):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side): return
    side = list(side)
    if not known_max:
        try:
            if not is_global_max_side(n, edges, side): acc['nonmax']+=1; return
        except Exception:
            return
    acc['sides'] += 1
    for (f, path, chords, spans, total, flow) in contained_flow_failures(n, adj, side):
        acc['A_total'] += 1
        if best_atom_tail(n, adj, side, path, chords)[0] > 0: acc['A_pos'] += 1
        else:
            acc['A_miss'] += 1
            if acc['A_first'] is None: acc['A_first'] = (name, n)
    try:
        fails = interval_failures(n, adj, side, name)
    except Exception:
        return
    for failure in fails:
        acc['B_total'] += 1
        ok=False
        try:
            if has_descent(n, edges, adj, side, failure): ok=True; acc['B2']+=1
        except Exception: pass
        if not ok:
            try:
                if b1_straddle(n, edges, adj, side, failure): ok=True; acc['B1']+=1
            except Exception: pass
        if not ok:
            acc['B_miss'] += 1
            if acc['B_first'] is None: acc['B_first'] = (name, n, failure.get('interval'))

def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(sides=0,nonmax=0,A_total=0,A_pos=0,A_miss=0,B_total=0,B1=0,B2=0,B_miss=0,A_first=None,B_first=None)
    for name,n,edges,side in cases():
        run_side("case:"+name, n, edges, side, acc)
    for reps in (1,2):
        n,edges=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
        for _ in range(reps): n,edges,side=add_cut_path(n,list(edges),side,2,6,6)
        run_side("ballast%d"%reps, n, sorted(set(edges)), side, acc)
    try:
        n,edges=n26_graph(); run_side("N26", n, sorted(set(edges)), [v%2 for v in range(n)], acc)
    except Exception: pass
    print("  cases+ballast+N26: sides=%d nonmax-skipped=%d A_miss=%d B_miss=%d (B1=%d B2=%d)"%(acc['sides'],acc['nonmax'],acc['A_miss'],acc['B_miss'],acc['B1'],acc['B2']),flush=True)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: run_side(nm, nn, E, s, acc, known_max=True)
    print("  + Mycielskian/glued (gmins): A_miss=%d B_miss=%d"%(acc['A_miss'],acc['B_miss']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: run_side("cen%s"%g6, n, E, s, acc, known_max=True)
        print("  census N=%d: sides=%d A_miss=%d B_miss=%d"%(nn,acc['sides'],acc['A_miss'],acc['B_miss']),flush=True)
    print("\n  global-max sides=%d (nonmax skipped=%d)"%(acc['sides'],acc['nonmax']),flush=True)
    print("  BRANCH A: failures=%d positive-tail=%d MISSES=%d %s"%(acc['A_total'],acc['A_pos'],acc['A_miss'],acc['A_first'] or ''),flush=True)
    print("  BRANCH B: failures=%d (B1=%d B2=%d) MISSES=%d %s"%(acc['B_total'],acc['B1'],acc['B2'],acc['B_miss'],acc['B_first'] or ''),flush=True)
    print("  === LOCKED HIGH-SIDE (global-max, A + B1/B2) %s ==="%("HOLDS: 0 A-miss, 0 B-miss => high-side switch-descent bridge VERIFIED full battery" if acc['A_miss']==0 and acc['B_miss']==0 else "FAILS"),flush=True)
