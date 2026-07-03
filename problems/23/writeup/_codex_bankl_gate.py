"""Exact Bank-L gate for Branch-B.

Bank-L is the L>5 row bank inequality

    eta >= 2*Sigma_L,

where

    eta = N^2/25 - |M|,
    Sigma_L = (L^2 - 25)/50.

Equivalently,

    25|M| <= N^2 - L^2 + 25.

This script is intentionally independent of the Blue-Detour surplus packet:
it checks the pure Bank-L node over cycles, two-lane/k-lane stress graphs,
selected named graphs, and census gamma-min connected-B cuts.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
import sys
from fractions import Fraction as F

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_banked_upo_gate import greedy_chords
    from _codex_interval_failure_switch_lab import adj_from_edges
    from _codex_rowcap_non5_half_gate import blowup
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane


def cycle_blowup_side(parts: list[int]) -> list[int]:
    side: list[int] = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1: tuple[int, list[tuple[int, int]]], block2: tuple[int, list[tuple[int, int]]], u: int, v: int):
    n1, e1 = block1
    n2, e2 = block2
    return n1 + n2, e1 + [(a + n1, b + n1) for a, b in e2] + [(u, n1 + v)]


def check_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], acc: dict) -> None:
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return

    m_bad = sum(1 for u, v in edges if side[u] == side[v])
    eta = F(n * n, 25) - m_bad
    assert m_bad == len(M)
    for f in M:
        for Q in cyc[f]:
            L = len(set(Q))
            if L <= 5:
                continue
            acc["rows"] += 1
            rhs = F(L * L - 25, 25)
            margin = eta - rhs
            if margin < acc["min_margin"][0]:
                acc["min_margin"] = (margin, name, n, m_bad, f, tuple(Q), eta, rhs)
            if margin < 0:
                acc["viol"] += 1
                if acc["first"] is None:
                    acc["first"] = {
                        "name": name,
                        "n": n,
                        "side": "".join(map(str, side)),
                        "m": m_bad,
                        "f": f,
                        "row": tuple(Q),
                        "L": L,
                        "eta": str(eta),
                        "required": str(rhs),
                        "margin": str(margin),
                    }


def check_gmins(name: str, n: int, edges: list[tuple[int, int]], acc: dict, max_cuts: int | None) -> None:
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_side(name, n, edges, [int(c) for c in side], acc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--direct-only", action="store_true")
    args = ap.parse_args()

    acc = {"rows": 0, "viol": 0, "first": None, "min_margin": (F(10**9),)}

    # Tight cycle calibration.
    for L in (7, 9, 11, 13, 15, 17, 19):
        n, edges = blowup([1] * L)
        check_side(f"C{L}[1]", n, edges, cycle_blowup_side([1] * L), acc)

    # Stress families.
    for L in range(8, 31, 2):
        n, edges, side, _bad = build_two_lane(L)
        check_side(f"two-lane-L{L}", n, edges, side, acc)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check_side(f"klane-L{Ll}k{k}", n, edges, side, acc)

    if not args.direct_only:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            check_gmins(name, n, edges, acc, args.max_cuts)

    if not args.skip_census and not args.direct_only:
        for nn in range(args.min_n, args.max_n + 1):
            before_rows = acc["rows"]
            before_viol = acc["viol"]
            gs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True)
            for g6 in gs.stdout.split():
                n, edges = dec(g6)
                check_gmins(f"cen{g6}", n, edges, acc, args.max_cuts)
            print(
                f"BANK-L census N={nn}: rows+={acc['rows'] - before_rows} "
                f"viol+={acc['viol'] - before_viol}",
                flush=True,
            )

    print("=== BANK-L gate ===")
    print("rows:", acc["rows"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min_margin"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "BANK-L HOLDS" if acc["viol"] == 0 else "BANK-L FAILS")


if __name__ == "__main__":
    main()
