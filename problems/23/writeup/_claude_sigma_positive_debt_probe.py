r"""Probe: do sigma>0 POSITIVE-DEBT deficient cages exist? (gap #1 R-D key risk, 2026-07-07).

GPT-Pro's PositiveSlackAbsorption (the single irreducible residual PositiveSlackHallPrefix) only has content for
sigma(C) > 0 cages: "a single sigma>0 / Balance<0 cage would break the extraction." The extraction produces a
sigma=0 (zero-slack) deficient cage. So the KEY question is whether sigma>0 positive-debt deficient cages exist at
all -- if NONE do, the sigma>0 branch is VACUOUS and R-D nearly evaporates.

My deficient-cap enumeration (reused from the ambient gate) filters boundary_delta==0 (= sigma=0). For a MAXIMUM cut,
flipping any set changes the cut by boundary_delta <= 0; so boundary_delta==0 <=> sigma=0 (cut-preserving) and
boundary_delta<0 <=> sigma>0 (cut-losing, sigma = -boundary_delta, up to the sigma(C) convention to be confirmed with
GPT-Pro). This probe RELAXES the filter and classifies every positive-debt (psi>0) deficient cap by boundary_delta,
reporting for the sigma>0 (bd<0) class: count + Surplus(C)=sum_{e in crossM}(ell(e)^2-25) distribution.
EXACT integer. NOTE: sigma=-boundary_delta is an INFERENCE pending GPT-Pro confirmation; frame results as
"boundary_delta<0 positive-debt deficient caps", not a proof. Run from problems/23/writeup.
Usage: python _claude_sigma_positive_debt_probe.py [maxN]   |   ... glue k
"""
import sys, subprocess
from collections import Counter
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _bdef_construct import is_triangle_free


def new_acc():
    return dict(defcap=0, bd_dist=Counter(), sigma0_posdebt=0, sigmapos_posdebt=0,
                sigmapos_surplus=Counter(), ex_sigmapos=None,
                sigmapos_masks=0, sigmapos_reached_witness=0, sigmapos_posdebt_prewit=0)


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
            bd = boundary_delta(n, adj, side, mask)  # bd = dB - dM = sigma(C) >= 0 for a max cut
            if bd < 0:
                continue  # anomaly (should not happen for a max cut); skip
            Sset = set(i for i in range(n) if (mask >> i) & 1)
            if bd > 0:
                acc['sigmapos_masks'] += 1
            res = witness_structure(n, adj, side, st, Sset)
            if res is None:
                continue
            crossM, bdyB, wit = res
            if not crossM or not bdyB:
                continue
            if bd > 0:
                acc['sigmapos_reached_witness'] += 1
            witnesses = {e: set() for e in bdyB}
            for (f, e) in wit:
                witnesses[e].add(f)
            if any(not witnesses[e] for e in bdyB):
                continue
            psi = sum(ell[f] ** 2 for f in crossM) - sum(min(ell[f] for f in witnesses[e]) ** 2 for e in bdyB)
            if psi <= 0:
                continue  # positive-debt only
            det = {'cross_m': tuple(sorted(crossM)), 'bdy_b': tuple(sorted(bdyB)),
                   'witnesses': {e: tuple(sorted(witnesses[e])) for e in bdyB}}
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            if deficient_cap_subset(leaves, exits_of_f, fset) is None:
                continue
            acc['defcap'] += 1
            acc['bd_dist'][bd] += 1
            surplus = sum(ell[e] ** 2 - 25 for e in crossM)
            if bd == 0:
                acc['sigma0_posdebt'] += 1
            else:  # bd > 0  => sigma(C) = bd > 0
                acc['sigmapos_posdebt'] += 1
                acc['sigmapos_surplus'][surplus] += 1
                if acc['ex_sigmapos'] is None:
                    acc['ex_sigmapos'] = dict(name=name, n=n, Sset=sorted(Sset), bd=bd, surplus=surplus,
                                              psi=psi, crossM=sorted(crossM),
                                              ell_crossM=sorted(ell[e] for e in crossM))


def report(label, acc):
    print('=' * 70)
    print('SIGMA>0 POSITIVE-DEBT DEFICIENT-CAGE PROBE:', label)
    print('  positive-debt deficient caps (all bd<=0): %d' % acc['defcap'])
    print('  boundary_delta distribution:', dict(sorted(acc['bd_dist'].items(), reverse=True)))
    print('  sigma=0 (bd==0) positive-debt: %d' % acc['sigma0_posdebt'])
    print('  sigma>0 (bd<0)  positive-debt: %d' % acc['sigmapos_posdebt'])
    print('  [bias diagnostic] sigma>0 masks enumerated: %d ; reached witness_structure (nonempty cross/bdy): %d'
          % (acc['sigmapos_masks'], acc['sigmapos_reached_witness']))
    if acc['sigmapos_posdebt']:
        print('  sigma>0 Surplus(C) distribution:', dict(sorted(acc['sigmapos_surplus'].items())))
        print('  *** sigma>0 positive-debt cap EXISTS -- the object PositiveSlackAbsorption must handle ***:',
              acc['ex_sigmapos'])
    # sigma(C) = boundary_delta = dB - dM (GPT-Pro-confirmed). sigma>0 <=> bd>0.
    print('VERDICT: sigma>0 positive-debt deficient caps %s'
          % (('DO NOT OCCUR here despite %d sigma>0 masks reaching witness => POSSIBLE BYPASS (positive-debt=>sigma=0)'
              % acc['sigmapos_reached_witness'])
             if acc['sigmapos_posdebt'] == 0 and acc['sigma0_posdebt'] > 0 and acc['sigmapos_reached_witness'] > 0 else
             ('EXIST (%d) => PositiveSlackAbsorption non-trivially needed (the objects it must handle)'
              % acc['sigmapos_posdebt'] if acc['sigmapos_posdebt'] else
              ('sigma>0 masks never reached deficient-detection (%d masks, %d reached witness) => inconclusive/bias'
               % (acc['sigmapos_masks'], acc['sigmapos_reached_witness'])))))


def census(maxn):
    acc = new_acc()
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            scan('cen%d' % nn, n, E, acc)
        print('  census N=%d done: defcap=%d sigma0=%d sigmapos=%d'
              % (nn, acc['defcap'], acc['sigma0_posdebt'], acc['sigmapos_posdebt']), flush=True)
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
