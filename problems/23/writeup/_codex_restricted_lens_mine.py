"""Mine positive per-edge lens entries at negative-residual vertices.

For every exact entry with R[v]<0 and C_g(v)>0, record:
  * ell(g);
  * the longer lengths f whose rows contain a g-row through v;
  * the exact C_g(v) and R[v] values.

This is a diagnostic for the restricted positive-overload lens lemma.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _lens_gate import contig_sub
from _lens_peredge_gate import maxcut_ls, vertex_blowup
from _bdef_construct import Cn, mycielski


def containing_lengths(g, v, M, ell, cyc):
    out = set()
    for Pg in cyc[g]:
        if v not in Pg:
            continue
        Pgl = list(Pg)
        Pgr = Pgl[::-1]
        for f in M:
            if f == g or ell[f] <= ell[g]:
                continue
            for Pf in cyc[f]:
                Pfl = list(Pf)
                if contig_sub(Pgl, Pfl) or contig_sub(Pgr, Pfl):
                    out.add(ell[f])
                    break
    return tuple(sorted(out))


def test_cut(name, n, adj, side, hist, examples, limit):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    for g in M:
        Qs = cyc[g]
        w = F(1, len(Qs))
        for v in range(n):
            if R[v] >= 0:
                continue
            Cg = F(0)
            through = 0
            for Q in Qs:
                if v in Q:
                    through += 1
                    Cg += w * (sum(T[u] for u in Q) - N * ell[g])
            if Cg <= 0:
                continue
            lens_lens = containing_lengths(g, v, M, ell, cyc)
            key = ("ell_g", ell[g], "longer", lens_lens, "through", through, "cyc", len(Qs), "Cg", str(Cg))
            hist[key] += 1
            if len(examples) < limit:
                examples.append(
                    dict(
                        name=name,
                        n=n,
                        side="".join(map(str, side)),
                        g=g,
                        v=v,
                        ell_g=ell[g],
                        longer=lens_lens,
                        Cg=str(Cg),
                        R=str(R[v]),
                        rows=[list(Q) for Q in Qs if v in Q],
                    )
                )


def scan_allmax(name, n, edges, hist, examples, limit):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, hist, examples, limit)


def scan_cut(name, n, edges, side, hist, examples, limit):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    test_cut(name, n, adj, side, hist, examples, limit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h-blowups", type=int, default=3)
    ap.add_argument("--examples", type=int, default=8)
    args = ap.parse_args()

    hist = Counter()
    examples = []
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, hist, examples, args.examples)

    grN, grE = mycielski(5, Cn(5))
    scan_allmax("Grotzsch_N11", grN, grE, hist, examples, args.examples)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for a, b in m2E:
        adj[a].add(b)
        adj[b].add(a)
    test_cut("MycGrotzsch_N23", m2N, adj, maxcut_ls(m2N, adj), hist, examples, args.examples)

    hN, hE = dec("H?AFBo]")
    base_side = [int(c) for c in "111110000"]
    for t in range(2, args.h_blowups + 1):
        n, edges = vertex_blowup(hN, hE, t)
        side = [base_side[v // t] for v in range(n)]
        scan_cut("Hblow_t%d" % t, n, edges, side, hist, examples, args.examples)

    print("hist:")
    for key, count in hist.most_common():
        print(count, key)
    print("examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
