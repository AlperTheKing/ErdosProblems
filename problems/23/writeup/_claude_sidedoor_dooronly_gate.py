r"""DECISIVE door-only gate for gap#1 R-D (GPT-Pro P1-P6 side-door subcage construction, 2026-07-08).

If every prunable side-door subcage D satisfies Demand(D) <= 25*sigma(D) (SmallSideDoorSubcage), then R-D collapses
to door-only absorption (Claude's green doorOnly_balance_nonneg) and the full Ferrers-Hall theorem is BYPASSED.

This gate enumerates the graph-only inclusion-minimal side-door candidates per GPT-Pro P1-P6:
  D subset V, B[D] and B[V\D] connected (cut-graph), |delta_B(D)| = 2 (exactly two B-doors), sigma(D)=2-|delta_M(D)|>0
  (so |delta_M(D)| <= 1), inclusion-minimal (no proper subset with the SAME two B-doors + sigma>0 + connectivity).
  OwnedBad(D) = delta_M(D) union M_internal(D); Demand(D) = sum (ell_B(e)^2-25); CHECK Demand(D) <= 25*sigma(D).
PASS (all D) => door-only absorption CONFIRMED (SmallSideDoorSubcage battery-validated) => R-D collapses.
A minimal side-door D with Demand(D) > 25*sigma(D) = the hard case (full Hall needed) OR a candidate obstruction -- SURFACE.
EXACT integer (ell = cut-geodesic +1). NOTE: this is a SUPERSET of the true side-door subcages (it drops the parent-cage
anchoring), so PASS is genuinely sufficient; a FAIL D must be checked against the true P1 anchoring before calling it a
refutation. Run from problems/23/writeup. Usage: python _claude_sidedoor_dooronly_gate.py [maxN] | ... glue k
"""
import sys, subprocess
from itertools import combinations
from collections import deque, Counter
from _h import Bconn, GENG, dec, maxcut_all
from _codex_k2t_switch_probe import adj_from_edges
from _bdef_construct import is_triangle_free
from _claude_pairdoor_convexity_gate import ell_of, edge


def deltas(n, adj, side, D):
    dB, dM = [], []
    for u in range(n):
        inu = u in D
        for v in adj[u]:
            if v > u and (inu ^ (v in D)):
                (dB if side[u] != side[v] else dM).append(edge(u, v))
    return dB, dM


def internal_bad(adj, side, D):
    out = []
    for u in D:
        for v in adj[u]:
            if v > u and v in D and side[u] == side[v]:
                out.append(edge(u, v))
    return out


def conn_cut(adj, side, S):
    """B[S] connected via CUT edges within S (GPT-Pro B = cut graph)."""
    S = list(S)
    if len(S) <= 1:
        return True
    Ss = set(S)
    seen = {S[0]}
    q = deque([S[0]])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in Ss and side[u] != side[v] and v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(Ss)


def deltaB_set(n, adj, side, D):
    s = set()
    for u in range(n):
        inu = u in D
        for v in adj[u]:
            if v > u and (inu ^ (v in D)) and side[u] != side[v]:
                s.add(edge(u, v))
    return s


def is_min_two_door(n, adj, side, D, doors):
    """inclusion-minimal: no proper nonempty subset D' with the SAME two B-doors + sigma>0 + B[D'] connected."""
    Dl = sorted(D)
    for r in range(1, len(Dl)):
        for combo in combinations(Dl, r):
            Dp = set(combo)
            if deltaB_set(n, adj, side, Dp) != doors:
                continue
            _, dMp = deltas(n, adj, side, Dp)
            if 2 - len(dMp) <= 0:
                continue
            if conn_cut(adj, side, Dp):
                return False  # smaller candidate exists
    return True


def scan(name, n, edges, adj, side, acc, maxD):
    verts = list(range(n))
    for r in range(2, maxD + 1):
        for combo in combinations(verts, r):
            D = set(combo)
            dB, dM = deltas(n, adj, side, D)
            if len(dB) != 2:
                continue
            sigma = 2 - len(dM)
            if sigma <= 0:
                continue
            comp = set(verts) - D
            if not conn_cut(adj, side, D) or not conn_cut(adj, side, comp):
                continue
            doors = set(dB)
            if not is_min_two_door(n, adj, side, D, doors):
                continue
            owned = dM + internal_bad(adj, side, D)
            demand = sum(ell_of(adj, side, e) ** 2 - 25 for e in owned)
            acc['minimal'] += 1
            for e in owned:
                acc['owned_ell'][ell_of(adj, side, e)] += 1
            slack = demand - 25 * sigma
            acc['slack_dist'][slack] += 1
            if slack > 0:
                acc['fail'] += 1
                if acc['ex_fail'] is None:
                    acc['ex_fail'] = dict(name=name, n=n, D=sorted(D), dB=sorted(doors), dM=sorted(dM),
                                          sigma=sigma, demand=demand,
                                          owned_ell=sorted(ell_of(adj, side, e) for e in owned))
            else:
                acc['ok'] += 1


def new_acc():
    return dict(minimal=0, ok=0, fail=0, owned_ell=Counter(), slack_dist=Counter(), ex_fail=None)


def report(label, acc):
    print('=' * 70)
    print('DOOR-ONLY SIDE-DOOR GATE:', label)
    print('  inclusion-minimal 2-B-door sigma>0 candidates D: %d' % acc['minimal'])
    print('  Demand(D) <= 25*sigma(D): OK=%d  FAIL=%d' % (acc['ok'], acc['fail']))
    print('  owned bad-edge ell distribution:', dict(sorted(acc['owned_ell'].items())))
    print('  (Demand-25*sigma) distribution:', dict(sorted(acc['slack_dist'].items())))
    if acc['ex_fail']:
        print('  *** FAIL (door-only violated -- HARD case or obstruction candidate) ***:', acc['ex_fail'])
    ok = acc['fail'] == 0 and acc['minimal'] > 0
    print('VERDICT: door-only absorption %s'
          % ('CONFIRMED (SmallSideDoorSubcage battery-validated; R-D collapses, full Ferrers-Hall BYPASSED)'
             if ok else ('FAIL: %d minimal side-door subcages have Demand>25*sigma -- check anchoring, else HARD case'
                         % acc['fail'] if acc['fail'] else 'no minimal 2-door candidates found')))


def do_graph(name, n, E, acc, maxD):
    adj = adj_from_edges(n, E)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
            continue
        scan(name, n, E, adj, side, acc, maxD)


def census(maxn, maxD):
    acc = new_acc()
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            do_graph('cen%d' % nn, n, E, acc, maxD)
        print('  census N=%d done: minimal=%d ok=%d fail=%d' % (nn, acc['minimal'], acc['ok'], acc['fail']), flush=True)
    report('CENSUS N<=%d (|D|<=%d)' % (maxn, maxD), acc)


def glue_single(k, maxD):
    cn, cE = dec('I?AEBAwF_')
    cyc = [(cn + i, cn + (i + 1) % k) for i in range(k)]
    acc = new_acc()
    for a in range(cn):
        for b in range(cn, cn + k):
            E = list(cE) + cyc + [(a, b)]
            if is_triangle_free(cn + k, E):
                do_graph('g%d-%d' % (a, b), cn + k, E, acc, maxD)
    report('GLUE core + C%d (|D|<=%d)' % (k, maxD), acc)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'glue':
        glue_single(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 7)
    else:
        census(int(sys.argv[1]) if len(sys.argv) > 1 else 9, int(sys.argv[2]) if len(sys.argv) > 2 else 7)


if __name__ == '__main__':
    main()
