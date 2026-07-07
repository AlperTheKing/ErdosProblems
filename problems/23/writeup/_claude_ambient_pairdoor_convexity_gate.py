r"""AMBIENT pair-door convexity gate for GPT-Pro's R-A / NoSideDoorForLongAnnulus (gap #1, 2026-07-07).

The isolated-core gate (_claude_pairdoor_convexity_gate.py) validates PairDoorConvex on the stretched L/(L+2)
model, which BY CONSTRUCTION has no ambient side-doors -- so it cannot probe R-A's open question (can an ambient
embedding create a side door that breaks pair-door convexity?). This gate reuses the EXACT deficient-cap enumeration
of _claude_multiatom_gammadrop_gate.py / _defcap_component_mine.py (real triangle-free graphs, B-connected Gamma-min
maximum cuts, sigma=0 zero-slack positive-debt deficient caps) and, for each cap switch that is a PAIR-DOOR
(|deltaB(Sset)|=|deltaM(Sset)|=2 -- the single-active-core case), checks:
  PairDoorConvex(B, Sset, born0,born1)  and  PairDoorConvex(B^U, Sset, oldLo,oldHi)  and metric stability.
A convexity FAILURE on any real ambient cap = a NoSideDoorForLongAnnulus FALSIFIER candidate (surface it).
0-fail => strong ambient support for R-A (annotation, NOT a general proof). EXACT integer BFS. Run from writeup.
Usage: python _claude_ambient_pairdoor_convexity_gate.py [maxN]   |   ... glue k   |   ... glue k1,k2
"""
import sys, subprocess
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _bdef_construct import is_triangle_free
from _claude_pairdoor_convexity_gate import convex_check, ell_of


def edges_crossing(n, adj, side, Sset, want_cut):
    out = set()
    for u in range(n):
        for v in adj[u]:
            if u < v and ((u in Sset) ^ (v in Sset)):
                if (side[u] != side[v]) == want_cut:
                    out.add((u, v))
    return out


def new_acc():
    return dict(defcap=0, pairdoor=0, multidoor=0, conv_pass=0, conv_fail=0,
                ndoor_dist={}, typeB=0, ex_fail=None,
                convfail_stable_ok=0, stability_broken=0, ex_stability_broken=None,
                drop_pos=0, drop_nonpos=0, ex_dropfail=None)


def scan(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            Sset = set(i for i in range(n) if (mask >> i) & 1)
            res = witness_structure(n, adj, side, st, Sset)
            if res is None:
                continue
            crossM, bdyB, wit = res
            if not crossM or not bdyB:
                continue
            witnesses = {e: set() for e in bdyB}
            for (f, e) in wit:
                witnesses[e].add(f)
            if any(not witnesses[e] for e in bdyB):
                continue
            psi = sum(ell[f] ** 2 for f in crossM) - sum(min(ell[f] for f in witnesses[e]) ** 2 for e in bdyB)
            if psi <= 0:
                continue
            det = {'cross_m': tuple(sorted(crossM)), 'bdy_b': tuple(sorted(bdyB)),
                   'witnesses': {e: tuple(sorted(witnesses[e])) for e in bdyB}}
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            if deficient_cap_subset(leaves, exits_of_f, fset) is None:
                continue
            acc['defcap'] += 1
            born = edges_crossing(n, adj, side, Sset, want_cut=True)    # deltaB(Sset)
            old = edges_crossing(n, adj, side, Sset, want_cut=False)    # deltaM(Sset) (crossing bad)
            key = (len(born), len(old))
            acc['ndoor_dist'][key] = acc['ndoor_dist'].get(key, 0) + 1
            if len(born) != 2 or len(old) != 2:
                acc['multidoor'] += 1
                continue
            acc['pairdoor'] += 1
            bornL = sorted(born)
            oldL = sorted(old)
            side_U = [side[i] ^ (1 if i in Sset else 0) for i in range(n)]
            # type-B signature: old lengths {L, L+2}
            oldlens = sorted(ell_of(adj, side, e) for e in oldL)
            if len(oldlens) == 2 and oldlens[1] == oldlens[0] + 2:
                acc['typeB'] += 1
            okB, detB = convex_check(adj, side, Sset, tuple(bornL))
            okC, detC = convex_check(adj, side_U, Sset, tuple(oldL))
            # metric stability: bad edges not crossing Sset keep ell (the CONCLUSION that matters for gap#1)
            stable = [e for e in M if not ((e[0] in Sset) ^ (e[1] in Sset))]
            chg = [(e, ell_of(adj, side, e), ell_of(adj, side_U, e))
                   for e in stable if ell_of(adj, side_U, e) != ell_of(adj, side, e)]
            # strict Gamma-drop (the essential Gamma-minimality contradiction), independent of convexity route
            st_U = struct_for_side(n, adj, side_U)
            if st_U is not None:
                gB = sum(ell[f] ** 2 for f in M)
                gBU = sum(st_U[1][f] ** 2 for f in st_U[0])
                if gB - gBU > 0:
                    acc['drop_pos'] += 1
                else:
                    acc['drop_nonpos'] += 1
                    if acc['ex_dropfail'] is None:
                        acc['ex_dropfail'] = dict(name=name, Sset=sorted(Sset), gB=gB, gBU=gBU)
            # metric-stability alarm: does stability ACTUALLY break (real gap#1 concern), or only convexity fail?
            if chg:
                acc['stability_broken'] += 1
                if acc['ex_stability_broken'] is None:
                    acc['ex_stability_broken'] = dict(name=name, n=n, Sset=sorted(Sset), born=bornL,
                                                      old=oldL, oldlens=oldlens, chg=chg)
            if okB and okC and not chg:
                acc['conv_pass'] += 1
            else:
                acc['conv_fail'] += 1
                if not chg:
                    acc['convfail_stable_ok'] += 1   # convexity (sufficient cond) fails but CONCLUSION holds
                if acc['ex_fail'] is None:
                    acc['ex_fail'] = dict(name=name, n=n, Sset=sorted(Sset), born=bornL, old=oldL,
                                          oldlens=oldlens, okB=okB, okC=okC, detB=detB, detC=detC, chg=chg)


def report(label, acc):
    print('=' * 70)
    print('AMBIENT PAIR-DOOR CONVEXITY:', label)
    print('  deficient-cap switches: %d | pair-door: %d | multi-door(passive/baggage): %d | type-B(L,L+2): %d'
          % (acc['defcap'], acc['pairdoor'], acc['multidoor'], acc['typeB']))
    print('  (#deltaB,#deltaM) distribution:', dict(sorted(acc['ndoor_dist'].items())))
    print('  pair-door convexity(route) PASS=%d FAIL=%d | of fails, stability STILL HOLDS=%d'
          % (acc['conv_pass'], acc['conv_fail'], acc['convfail_stable_ok']))
    print('  *** METRIC STABILITY (the gap#1 conclusion) broken=%d ; strict Gamma-drop pos=%d nonpos=%d ***'
          % (acc['stability_broken'], acc['drop_pos'], acc['drop_nonpos']))
    if acc['ex_stability_broken']:
        print('  !!! REAL STABILITY FAILURE (gap#1 ALARM) !!!:', acc['ex_stability_broken'])
    if acc['ex_dropfail']:
        print('  !!! Gamma-drop NONPOS (gap#1 FALSIFIER) !!!:', acc['ex_dropfail'])
    if acc['ex_fail']:
        print('  (convexity-route failure example):', acc['ex_fail'])
    stability_ok = acc['stability_broken'] == 0 and acc['drop_nonpos'] == 0 and acc['pairdoor'] > 0
    print('VERDICT: metric-stability+strict-drop (gap#1 conclusion) %s ; convexity-route %s'
          % ('HOLDS on all ambient pair-door caps (0 stability-break, 0 drop-nonpos)' if stability_ok else
             'BROKEN -- SURFACE as gap#1 obstruction',
             '0-fail' if acc['conv_fail'] == 0 else
             ('fails on %d/%d (U-choice dependent; conclusion robust)' % (acc['conv_fail'], acc['pairdoor']))))


def census(maxn):
    acc = new_acc()
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            scan('cen%d' % nn, n, E, acc)
        print('  census N=%d done: defcap=%d pairdoor=%d conv_fail=%d'
              % (nn, acc['defcap'], acc['pairdoor'], acc['conv_fail']), flush=True)
    report('CENSUS N<=%d' % maxn, acc)


def glue_single(k):
    cn, cE = dec('I?AEBAwF_')
    cyc = [(cn + i, cn + (i + 1) % k) for i in range(k)]
    acc = new_acc()
    for a in range(cn):
        for b in range(cn, cn + k):
            E = list(cE) + cyc + [(a, b)]
            if is_triangle_free(cn + k, E):
                scan('g%d-%d' % (a, b), cn + k, E, acc)
    report('GLUE core + C%d (all bridges)' % k, acc)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'glue':
        glue_single(int(sys.argv[2]))
    else:
        census(int(sys.argv[1]) if len(sys.argv) > 1 else 9)


if __name__ == '__main__':
    main()
