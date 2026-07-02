"""Class-uniform blowup stress for Slack-CAGE dynamic bank split.

This lifts selected N=10/11 positive-prebank witness graphs by a uniform clone
factor t, keeps the inherited cut, and tests only class-uniform subsets U.

It is not a full proof or a full max-cut audit for the blowup.  It is a
graphon-scale stress test for whether the dynamic Flat5-bank / Xi2 split stays
stable under uniform blowups of the known positive-bank atoms.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec
    from _stark1 import gmins
    from _codex_slack_cage_prebank_classifier import counted_rows, subset_tw
    from _codex_slack_cage_switch_gate import build_data, sigma_of
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch


def blowup(n, edges, side, t):
    def idx(v, k):
        return v * t + k

    out_edges = []
    for u, v in edges:
        for i in range(t):
            for j in range(t):
                out_edges.append((idx(u, i), idx(v, j)))
    out_side = []
    for v in range(n):
        for k in range(t):
            out_side.append(int(side[v]))
    return n * t, out_edges, out_side


def class_uniform_set(base_mask, base_n, t):
    out = set()
    for v in range(base_n):
        if (base_mask >> v) & 1:
            for k in range(t):
                out.add(v * t + k)
    return frozenset(out)


def base_mask_from_set(S, base_n, t):
    mask = 0
    for v in range(base_n):
        block = {v * t + k for k in range(t)}
        if block <= S:
            mask |= 1 << v
    return mask


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def fmt_rec(rec):
    if rec is None:
        return ""
    out = dict(rec)
    for key in ("eta", "prebank", "pre_after", "bank", "margin", "lhs"):
        if key in out:
            out[key] = fmt_frac(out[key])
    return out


def analyze(g6, cut_index, t):
    base_n, base_edges = dec(g6)
    _adj, cuts = gmins(base_n, base_edges)
    side = cuts[cut_index]
    n, edges, lifted_side = blowup(base_n, base_edges, side, t)
    data = build_data(n, edges, lifted_side)
    if data is None:
        raise RuntimeError("lifted inherited cut did not build")
    E, B, M, Mset, cyc = data
    eta = F(n * n, 25) - len(M)

    subsets = [class_uniform_set(mask, base_n, t) for mask in range(1 << base_n)]
    sigmas = {U: sigma_of(U, B, Mset) for U in subsets}
    tws = {U: subset_tw(n, M, cyc, U) for U in subsets}

    stats = Counter()
    first_fail = None
    first_case = None
    max_prebank = None
    max_bank = None

    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in subsets:
                if not U or len(U) == n:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                if not rows:
                    continue
                lhs = sum(tws[U][v] for v in Q)
                prebank = lhs - len(U) - sigmas[U]
                if prebank <= 0:
                    continue
                stats["positive"] += 1
                rec_base = {
                    "g6": g6,
                    "cut": cut_index,
                    "t": t,
                    "n": n,
                    "m": len(M),
                    "eta": eta,
                    "Q": Q,
                    "U_size": len(U),
                    "lhs": lhs,
                    "prebank": prebank,
                }
                if first_case is None:
                    first_case = dict(rec_base)
                if max_prebank is None or prebank > max_prebank["prebank"]:
                    max_prebank = dict(rec_base)

                stats["needs_bank"] += 1
                best = None
                candidate_count = 0
                for smask in range(1, 1 << base_n):
                    if smask & ~base_mask_from_set(U, base_n, t):
                        continue
                    S = class_uniform_set(smask, base_n, t)
                    if not S or S == U:
                        # Keep proper peels; S=U is not a decomposition step.
                        continue
                    if sigma_of(S, B, Mset) != 0:
                        continue
                    if not is_flat5_switch(n, E, B, Mset, tuple(sorted(S))):
                        continue
                    candidate_count += 1
                    U2 = frozenset(set(U) - set(S))
                    pre_after = sum(tws[U2][v] for v in Q) - len(U2) - sigmas[U2]
                    bank = prebank - max(F(0), pre_after)
                    candidate = dict(rec_base)
                    candidate.update(
                        {
                            "S": tuple(sorted(S)),
                            "pre_after": pre_after,
                            "bank": bank,
                            "margin": eta - bank,
                            "candidate_count": candidate_count,
                        }
                    )
                    if best is None or max(F(0), pre_after) < max(F(0), best["pre_after"]):
                        best = candidate

                if candidate_count:
                    stats["class_flat5_candidates"] += candidate_count

                if best is not None and best["pre_after"] <= 0 and best["bank"] <= eta:
                    stats["flat5_consumes_positive"] += 1
                    if max_bank is None or best["bank"] > max_bank["bank"]:
                        max_bank = best
                else:
                    stats["fail"] += 1
                    if first_fail is None:
                        first_fail = best or dict(rec_base)

    return {
        "stats": stats,
        "first_case": first_case,
        "first_fail": first_fail,
        "max_prebank": max_prebank,
        "max_bank": max_bank,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs", default="I?AAD@wF_,J??CAAoR`Y?")
    ap.add_argument("--t", default="2,3,4")
    ap.add_argument("--cut-index", type=int, default=0)
    args = ap.parse_args()

    total = Counter()
    first_fail = None
    max_prebank = None
    max_bank = None
    first_case = None
    for g6 in [x for x in args.graphs.split(",") if x]:
        for t in [int(x) for x in args.t.split(",") if x]:
            r = analyze(g6, args.cut_index, t)
            total.update(r["stats"])
            if first_case is None and r["first_case"] is not None:
                first_case = r["first_case"]
            if first_fail is None and r["first_fail"] is not None:
                first_fail = r["first_fail"]
            if r["max_prebank"] is not None and (
                max_prebank is None or r["max_prebank"]["prebank"] > max_prebank["prebank"]
            ):
                max_prebank = r["max_prebank"]
            if r["max_bank"] is not None and (max_bank is None or r["max_bank"]["bank"] > max_bank["bank"]):
                max_bank = r["max_bank"]
            print(f"case g6={g6} t={t} stats={dict(r['stats'])}", flush=True)

    print("=== Slack-CAGE uniform blowup class-subset gate ===")
    print("stats:", dict(total))
    print("first_case:", fmt_rec(first_case))
    print("max_prebank:", fmt_rec(max_prebank))
    print("max_bank:", fmt_rec(max_bank))
    print("first_fail:", fmt_rec(first_fail))
    verdict = "PASS_BLOWUP_CLASS_GATE" if total["positive"] and total["fail"] == 0 else "CHECK"
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
