"""Parametric shared-path Flat5 fan stress for UNIT-FLAT5.

The intended cut has t length-5 bad rows sharing the same terminal 4-vertex
blue path:

    p_i - a - b - c - d - p_i

with p_i d bad and all path edges blue.  Extra blue leaves at a and d make the
obvious fan switch neutral.  The expected UNIT-FLAT5 mechanism is:

    t = 2  -> two-row unit atom can be positive;
    t >= 3 -> any two-row union has extra boundary slack and no positive
              row-union prebank.

This is only a generated-family stress gate, not a proof.
"""

from __future__ import annotations

import argparse
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_slack_cage_unit_pack_group_gate import check_side, fmt_rec


def norm(u, v):
    return (u, v) if u < v else (v, u)


def build_fan(t: int):
    # vertices:
    #   p_i: 0..t-1, a=t, b=t+1, c=t+2, d=t+3,
    #   x=t+4 attached to a, y_j=t+5..t+5+(t-2) attached to d.
    p = list(range(t))
    a, b, c, d = t, t + 1, t + 2, t + 3
    x = t + 4
    y0 = t + 5
    n = t + 5 + max(0, t - 1)
    edges = []
    # shared blue path
    edges += [norm(a, b), norm(b, c), norm(c, d)]
    # private row starts: blue p_i-a and bad p_i-d under the intended cut
    for pi in p:
        edges.append(norm(pi, a))
        edges.append(norm(pi, d))
    # one a-side blue leaf and t-1 d-side blue leaves.
    edges.append(norm(x, a))
    for j in range(max(0, t - 1)):
        edges.append(norm(y0 + j, d))

    # Intended cut sides: p_i,b,d,x are 0; a,c,y_j are 1.
    side = [0] * n
    side[a] = 1
    side[c] = 1
    for j in range(max(0, t - 1)):
        side[y0 + j] = 1
    return n, sorted(set(edges)), "".join(str(v) for v in side)


def build_theta(t: int):
    # vertices:
    #   p_i: 0..t-1, a=t, b=t+1, c=t+2, d=t+3,
    #   o1..o4 = t+4..t+7.
    #
    # Intended cut makes p_i-d bad, with two length-4 blue corridors from p_i
    # to d:
    #   p_i-a-b-c-d and p_i-a-o1-o2-o3-o4-d.
    # For t>=3 this intended cut is usually not a maximum cut; checking gmins
    # is the point of this guardrail.
    p = list(range(t))
    a, b, c, d = t, t + 1, t + 2, t + 3
    o1, o2, o3, o4 = t + 4, t + 5, t + 6, t + 7
    n = t + 8
    edges = [norm(a, b), norm(b, c), norm(c, d), norm(a, o1), norm(o1, o2), norm(o2, o3), norm(o3, o4), norm(o4, d)]
    for pi in p:
        edges.append(norm(pi, a))
        edges.append(norm(pi, d))

    # Intended side: p_i,b,d,o1,o3 are 0; a,c,o2,o4 are 1.
    side = [0] * n
    side[a] = 1
    side[c] = 1
    side[o2] = 1
    side[o4] = 1
    return n, sorted(set(edges)), "".join(str(v) for v in side)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-t", type=int, default=12)
    ap.add_argument("--max-cuts", type=int, default=64)
    ap.add_argument("--family", choices=("fan", "theta"), default="fan")
    ap.add_argument("--gmins", action="store_true", help="also enumerate gmins cuts; slow for large fans")
    args = ap.parse_args()

    print("=== shared-path Flat5 fan stress ===")
    any_fail = False
    if args.gmins:
        from _stark1 import gmins
    for t in range(2, args.max_t + 1):
        if args.family == "theta":
            n, edges, intended = build_theta(t)
        else:
            n, edges, intended = build_fan(t)
        if args.gmins:
            _adj, cuts = gmins(n, edges)
            cuts = cuts[: args.max_cuts]
        else:
            cuts = [intended]
        acc_total = None
        intended_seen = intended in cuts
        rows = []
        for idx, side in enumerate(cuts):
            acc = check_side(f"fan-t{t}#cut{idx}", n, edges, side, max_union_rows=2)
            rows.append(acc)
            if acc_total is None:
                acc_total = acc
            else:
                # local merge, enough for this small stress
                for key in ("cuts", "candidates", "positive", "unit_cases", "nonunit_positive", "fails"):
                    acc_total[key] += acc[key]
                acc_total["atom_count_hist"].update(acc["atom_count_hist"])
                if acc_total["first_fail"] is None:
                    acc_total["first_fail"] = acc["first_fail"]
        positives = acc_total["positive"] if acc_total else 0
        unit_cases = acc_total["unit_cases"] if acc_total else 0
        nonunit = acc_total["nonunit_positive"] if acc_total else 0
        fails = acc_total["fails"] if acc_total else 0
        hist = dict(sorted(acc_total["atom_count_hist"].items())) if acc_total else {}
        print(
            f"t={t} n={n} cuts_checked={len(cuts)} intended_in_checked={intended_seen} "
            f"positive={positives} unit={unit_cases} nonunit={nonunit} fails={fails} atom_hist={hist}"
        )
        if acc_total and acc_total["first_fail"] is not None:
            print("  first_fail:", fmt_rec(acc_total["first_fail"]))
            any_fail = True
    print("VERDICT:", "FAIL_FLAT5_FAN_STRESS" if any_fail else "PASS_FLAT5_FAN_STRESS")


if __name__ == "__main__":
    main()
