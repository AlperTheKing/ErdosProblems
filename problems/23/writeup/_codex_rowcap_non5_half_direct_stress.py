"""Direct stress for NON5-HALF without rediscovering known cuts.

This reuses the exact row checker from _codex_rowcap_non5_half_gate.py, but
feeds explicit canonical cuts for balanced odd-cycle blowups and lane
families.  It avoids expensive gmins calls on large blowups.
"""

from fractions import Fraction as F
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_rowcap_non5_half_gate import adj_of, blowup, check_cut
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane
    from _wf_lrsbreak_0c import greedy_chords


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def main():
    acc = {
        "rows": 0,
        "viol": 0,
        "surplus_viol": 0,
        "first": None,
        "surplus_first": None,
        "min_margin": (F(10**18),),
        "min_surplus_margin": (F(10**18),),
        "by_len": {},
        "surplus_by_len": {},
    }

    for L in range(8, 101, 2):
        n, edges, side, _ = build_two_lane(L)
        check_cut(f"direct-two-lane-L{L}", n, adj_of(n, edges), side, acc)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check_cut(f"direct-klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc)

    blowup_cases = (
        [(7, t) for t in range(1, 6)]
        + [(9, t) for t in range(1, 4)]
        + [(11, t) for t in range(1, 3)]
        + [(13, t) for t in range(1, 3)]
    )
    for c, t in blowup_cases:
            n, edges = blowup([t] * c)
            side = cycle_blowup_side([t] * c)
            check_cut(f"direct-C{c}[{t}]", n, adj_of(n, edges), side, acc)

    print("=== DIRECT NON5-HALF stress ===")
    print("rows L>5:", acc["rows"])
    print("violations:", acc["viol"])
    print("LONG-SURPLUS violations:", acc["surplus_viol"])
    print("min_margin:", acc["min_margin"])
    print("min_surplus_margin:", acc["min_surplus_margin"])
    print("min_margin_by_len:")
    for L in sorted(acc["by_len"]):
        print(" ", L, acc["by_len"][L])
    print("min_surplus_margin_by_len:")
    for L in sorted(acc["surplus_by_len"]):
        print(" ", L, acc["surplus_by_len"][L])
    print("first:", acc["first"] or "")
    print("surplus_first:", acc["surplus_first"] or "")
    verdict = acc["viol"] == 0 and acc["surplus_viol"] == 0
    print("VERDICT:", "DIRECT NON5-HALF+SURPLUS HOLDS" if verdict else "DIRECT NON5-HALF+SURPLUS FAILS")


if __name__ == "__main__":
    main()
