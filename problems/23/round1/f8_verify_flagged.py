"""
f8_verify_flagged.py -- resolve every pattern that a *truncated* working set flagged as
possibly exceeding 1/25.  Uses the FULL antichain of minimal monochromatic sets as the
separation oracle inside a cutting-plane loop.

max_a min_{F in W}  is an UPPER bound on max_a psi for every W, so the loop only has to
drive the working-set value down to <= 1/25 to settle a graph.

Usage: python f8_verify_flagged.py file_of_graph6
"""
import sys
import numpy as np
from f8_core import g6_decode, mono_sets_any_m, edges_of
from f8_wopt3 import maxmin

TARGET = 1.0 / 25.0


def tensor_for(n, E, sets):
    T = np.zeros((len(sets), n, n))
    for k, S in enumerate(sets):
        for b in S:
            i, j = E[b]
            T[k, i, j] = T[k, j, i] = 1.0
    return T


def psi_full(pairsI, pairsJ, offs, a):
    """min over all minimal sets of sum a_i a_j, vectorised via a ragged CSR layout"""
    prod = a[pairsI] * a[pairsJ]
    cs = np.concatenate([[0.0], np.cumsum(prod)])
    return cs[offs[1:]] - cs[offs[:-1]]


def main():
    fn = sys.argv[1]
    lines = [l.strip() for l in open(fn) if l.strip() and l[0] != '>']
    worst = 0.0
    for line in lines:
        n, adj = g6_decode(line)
        E, sets = mono_sets_any_m(n, adj)
        # ragged layout for the full oracle
        pi, pj, offs = [], [], [0]
        for S in sets:
            for b in S:
                i, j = E[b]
                pi.append(i); pj.append(j)
            offs.append(len(pi))
        pi = np.array(pi); pj = np.array(pj); offs = np.array(offs)
        widx = list(range(min(250, len(sets))))
        t = 1.0
        for rnd in range(30):
            T = tensor_for(n, E, [sets[i] for i in widx])
            t, a = maxmin(n, T, 30)
            if t <= TARGET + 1e-9:
                break
            q = psi_full(pi, pj, offs, a)
            viol = np.argsort(q)[:40]
            new = [int(i) for i in viol if int(i) not in widx]
            if not new:
                break
            widx += new
        worst = max(worst, t)
        status = '*** STILL EXCEEDS 1/25 ***' if t > TARGET + 1e-9 else 'ok (<=1/25)'
        print(f"{line:>30s} n={n:2d} m={len(E):3d} |M|={len(sets):6d} |W|={len(widx):5d} "
              f"UB={t:.10f}  {status}", flush=True)
    print(f"# max over file = {worst:.12f}")


if __name__ == '__main__':
    main()
