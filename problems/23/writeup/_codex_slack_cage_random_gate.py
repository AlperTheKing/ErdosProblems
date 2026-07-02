"""Random/substructured subset stress for slack-CAGE.

The full slack-CAGE candidate says, for a fixed row Q and every U subset V,

    D_Q(U) <= |U| + sigma(U) + eta,

where D_Q(U) counts only rows P fully contained in U, weighted by
|P cap Q|/|cyc[g]|.  Exhaustive subset checks are too expensive on larger
named graphs; this script samples deterministic random subsets at several
densities and checks all rows exactly.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import random
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _h import Bconn
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane
    from _wf_lrsbreak_0c import greedy_chords


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def canonical_subset(U):
    return tuple(sorted(U))


def sampled_subsets(n, rng, samples):
    out = [set(), set(range(n))]
    probs = [0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9]
    for p in probs:
        for _ in range(samples):
            U = {v for v in range(n) if rng.random() < p}
            out.append(U)
    # Add contiguous-looking index intervals; useful for constructed lane graphs.
    for _ in range(samples):
        a = rng.randrange(n)
        b = rng.randrange(a, n)
        out.append(set(range(a, b + 1)))
    seen = set()
    uniq = []
    for U in out:
        key = canonical_subset(U)
        if key not in seen:
            seen.add(key)
            uniq.append(U)
    return uniq


def check_side(name, n, edges, side, subsets, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return

    bad = {tuple(sorted(e)) for e in M}
    blue = {tuple(sorted(e)) for e in edges if side[e[0]] != side[e[1]]}
    eta = F(n * n, 25) - len(M)
    row_sets = {
        g: [(tuple(P), set(P)) for P in cyc[g]]
        for g in M
    }

    acc["sides"] += 1
    local_checks = 0
    for U in subsets:
        dB = sum(((u in U) ^ (v in U)) for u, v in blue)
        dM = sum(((u in U) ^ (v in U)) for u, v in bad)
        rhs = F(len(U) + dB - dM) + eta
        tw = [F(0) for _ in range(n)]
        for g in M:
            mass = F(1, len(cyc[g]))
            for P, pset in row_sets[g]:
                if pset <= U:
                    for v in P:
                        tw[v] += mass
        for f in M:
            for Q in cyc[f]:
                lhs = sum(tw[v] for v in Q)
                margin = rhs - lhs
                local_checks += 1
                acc["checks"] += 1
                if margin < acc["min"][0]:
                    acc["min"] = (
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(Q),
                        canonical_subset(U),
                        lhs,
                        rhs,
                        len(U),
                        dB - dM,
                        eta,
                    )
                if margin < 0:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "f": f,
                            "Q": tuple(Q),
                            "U": canonical_subset(U),
                            "lhs": str(lhs),
                            "rhs": str(rhs),
                            "size": len(U),
                            "slack": dB - dM,
                            "excess": str(lhs - rhs),
                        }
                    print("FAIL", acc["first"], flush=True)
                    return
    print(f"{name}: subsets={len(subsets)} checks={local_checks} ok", flush=True)


def scan_gmins(name, n, edges, subsets, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    for side in cuts[:max_cuts]:
        check_side(name, n, edges, side, subsets, acc)
        if acc["first"]:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--max-cuts", type=int, default=2)
    ap.add_argument("--two-lane-max", type=int, default=40)
    ap.add_argument("--include-mycg", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    acc = {"sides": 0, "checks": 0, "viol": 0, "first": None, "min": (F(10**18),)}

    families = []
    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _ = build_two_lane(L)
        families.append((f"two-lane-L{L}", n, edges, [side], False))
    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        families.append((f"klane-L{Ll}k{k}", n, edges, [side], False))
    for parts in ([2, 1, 2, 1, 2], [3, 2, 3, 2, 3], [4, 3, 4, 3, 4]):
        n, edges = blowup(parts)
        # The natural parity cut is not maximum for these unbalanced blowups.
        families.append((f"gmin-blowup-{parts}", n, edges, None, True))

    named = [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
    ]
    if args.include_mycg:
        grot = mycielski(5, Cn(5))
        named.append(("Myc(Grotzsch)", mycielski(grot[0], grot[1])))
    for nm, (n, edges) in named:
        families.append((nm, n, edges, None, True))

    for name, n, edges, sides, use_gmins in families:
        subsets = sampled_subsets(n, rng, args.samples)
        if use_gmins:
            scan_gmins(name, n, edges, subsets, args.max_cuts, acc)
        else:
            for side in sides:
                check_side(name, n, edges, side, subsets, acc)
        if acc["first"]:
            break

    print("=== random slack-CAGE gate ===")
    print("sides:", acc["sides"])
    print("checks:", acc["checks"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "HOLDS" if acc["viol"] == 0 else "FAILS")


if __name__ == "__main__":
    main()

