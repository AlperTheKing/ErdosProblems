"""Gate the restricted positive per-edge lens lemma.

The broad per-edge lemma

    C_g(v)>0 => g is a short member of a strict lens through v

is false on the N=23 Mycielski witness.  The proof route only needs the
negative-residual version:

    R[v] < 0 and C_g(v)>0
      => g is a short member of a strict lens through v.

Here

    C_g(v) = avg_{Q in cyc[g], v in Q} (sum_{u in Q} T[u] - N*ell[g])
    R[v]   = N*T[v] - (K2*T)[v].

This script reuses the independent strict-lens detector from _lens_peredge_gate
and exact Fraction arithmetic.
"""

import argparse
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _Klocal_gate import glued_c5_chain
from _wf_deficit_farkas import odd_blowup
from _lens_peredge_gate import maxcut_ls, short_member_verts, vertex_blowup


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc["cuts"] += 1
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    smv = short_member_verts(M, ell, cyc)
    for g in M:
        Qs = cyc[g]
        w = F(1, len(Qs))
        for v in range(n):
            if R[v] >= 0:
                continue
            Cg = F(0)
            for Q in Qs:
                if v in Q:
                    Cg += w * (sum(T[u] for u in Q) - N * ell[g])
            if Cg <= 0:
                continue
            acc["pos_neg"] += 1
            if g in smv and v in smv[g]:
                acc["covered"] += 1
            else:
                acc["fail"] += 1
                if acc["first"] is None:
                    acc["first"] = dict(
                        name=name,
                        n=n,
                        side="".join(map(str, side)),
                        g=g,
                        v=v,
                        Cg=str(Cg),
                        R=str(R[v]),
                        g_short_member=(g in smv),
                    )


def scan_allmax(name, n, edges, acc):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def scan_cut(name, n, edges, side, acc):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    test_cut(name, n, adj, side, acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--h-blowups", type=int, default=3)
    ap.add_argument("--random", type=int, default=0)
    args = ap.parse_args()

    acc = {"cuts": 0, "pos_neg": 0, "covered": 0, "fail": 0, "first": None}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, acc)
        print("census N=%d cuts=%d pos_neg=%d covered=%d fail=%d" %
              (nn, acc["cuts"], acc["pos_neg"], acc["covered"], acc["fail"]), flush=True)

    grN, grE = mycielski(5, Cn(5))
    scan_allmax("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for a, b in m2E:
        adj[a].add(b)
        adj[b].add(a)
    test_cut("MycGrotzsch_N23", m2N, adj, maxcut_ls(m2N, adj), acc)
    print("after Myc cuts=%d pos_neg=%d covered=%d fail=%d" %
          (acc["cuts"], acc["pos_neg"], acc["covered"], acc["fail"]), flush=True)

    hN, hE = dec("H?AFBo]")
    base_side = [int(c) for c in "111110000"]
    for t in range(2, args.h_blowups + 1):
        n, edges = vertex_blowup(hN, hE, t)
        side = [base_side[v // t] for v in range(n)]
        scan_cut("Hblow_t%d" % t, n, edges, side, acc)
        print("after Hblow_t%d cuts=%d pos_neg=%d covered=%d fail=%d" %
              (t, acc["cuts"], acc["pos_neg"], acc["covered"], acc["fail"]), flush=True)

    for q in range(2, 14):
        n, edges, side = glued_c5_chain(q)
        scan_cut("chain_q%d" % q, n, edges, side, acc)

    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3),
                  (4, 3, 4, 3, 4), (2, 2, 2, 2, 2), (3, 3, 3, 3, 3)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 16:
            scan_allmax("blow%s" % (sizes,), n, edges, acc)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(isl, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    assert is_triangle_free(n, edges)
    scan_allmax("island", n, edges, acc)

    print("cuts:", acc["cuts"])
    print("positive entries at R<0 vertices:", acc["pos_neg"])
    print("covered:", acc["covered"])
    print("fail:", acc["fail"])
    print("first:", acc["first"])
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
