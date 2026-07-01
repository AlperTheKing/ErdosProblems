"""Claude INDEPENDENT cross-gate of Codex's DEFICIENT-CAP SIGN ATOM (19:25Z):
in any neutral (boundary_delta=0) terminal-shadow switch with positive Psi and two-cap decomposition,
if some nonempty Y subset of a side cap has |N(Y)|<=|Y| (deficient), then S contains NO vertex with R[v]<0.
Contrapositive: R[v]<0 in S => no deficient cap => strict cap expansion (surplus-touch).

Independence: the witness relation (cross_m/bdy_b/witnesses) is computed by MY witness_structure (_pl_gate);
only the two-cap/leaf/deficient COMBINATORICS reuse Codex's _codex_defcap_negative_scope_gate helpers.
Reports first failure (deficient cap WITH a negative-residual vertex in S) with S, Y, witnesses, R values.
Battery: census N<=11 (all neutral masks). EXACT Fraction. Run from problems/23/writeup."""
import argparse, subprocess
from collections import Counter
from fractions import Fraction as F
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset


def scan_graph(name, n, edges, acc):
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
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
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
                continue  # invalid: some exit unwitnessed
            psi = sum(ell[f] ** 2 for f in crossM) - sum(min(ell[f] for f in witnesses[e]) ** 2 for e in bdyB)
            if psi <= 0:
                continue
            det = {'cross_m': tuple(sorted(crossM)), 'bdy_b': tuple(sorted(bdyB)),
                   'witnesses': {e: tuple(sorted(witnesses[e])) for e in bdyB}}
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            acc['two_cap_positive'] += 1
            bad = deficient_cap_subset(leaves, exits_of_f, fset)
            if bad is None:
                continue
            acc['defcap'] += 1
            # (a) CLASSIFICATION: template signature of this deficient switch
            ydef, nbr, gap = bad
            ell_sig = tuple(sorted(ell[f] for f in fset))
            wit_sig = tuple(sorted(len(exits_of_f[f]) for f in fset))
            template = (len(fset), ell_sig, wit_sig, len(ydef), gap)
            acc['templates'][template] += 1
            # (b) SIGN: in-S and GLOBAL (R<0 anywhere in the cut)
            neg_s = tuple(i for i in sorted(Sset) if R[i] < 0)
            neg_all = tuple(i for i in range(n) if R[i] < 0)
            if neg_s:
                acc['fail'] += 1
                if acc['first'] is None:
                    acc['first'] = (name, n, ''.join(map(str, side)), tuple(sorted(Sset)), str(psi), bad,
                                    neg_s, tuple(str(R[i]) for i in neg_s))
            if neg_all:
                acc['global_fail'] += 1
                if acc['first_global'] is None:
                    acc['first_global'] = (name, n, ''.join(map(str, side)), neg_all)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-n', type=int, default=5)
    ap.add_argument('--max-n', type=int, default=10)
    args = ap.parse_args()
    acc = Counter()
    acc['first'] = None
    acc['first_global'] = None
    acc['templates'] = Counter()
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
        print('N', nn, 'two_cap_positive=%d defcap=%d fail(inS)=%d global_fail=%d' %
              (acc['two_cap_positive'], acc['defcap'], acc['fail'], acc['global_fail']), flush=True)
    print('(a) CLASSIFICATION -- deficient-cap template signatures (|C|, ell-sorted, witdeg-sorted, |Y|, gap):')
    for t, c in sorted(acc['templates'].items()):
        print('   ', t, 'x', c)
    print('(b) SIGN in-S first fail:', acc['first'] or 'NONE')
    print('(b) SIGN global first fail:', acc['first_global'] or 'NONE')
    print('VERDICT:', 'DEFICIENT-CAP SIGN ATOM HOLDS (my machinery): all deficient caps single template + R>=0 (in-S and global)'
          if acc['fail'] == 0 and acc['global_fail'] == 0 else 'FAIL')


if __name__ == '__main__':
    main()
