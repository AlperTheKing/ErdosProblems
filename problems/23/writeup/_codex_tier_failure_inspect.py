"""Inspect the first non-robust TIER-SDR failure.

The existential two-stage matching passes, but not every shortest-stage
matching extends.  This prints the witness matrix and extension counts for the
first known failing H2 all-max example.
"""

from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import enumerate_matchings, stage1_extends


def main():
    n, edges, _ = h_blowup(2)
    adj = adj_from_edges(n, edges)
    side_s = "001111111111000000"
    side = [int(c) for c in side_s]
    mask = sum(1 << i for i in (2, 12, 13))
    st = struct_for_side(n, adj, side)
    M, ell, _T, _mu, _cyc = st
    det = terminal_shadow_details(n, adj, side, st, mask)
    F = tuple(sorted(det["cross_m"]))
    E = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E}
    min_len = min(ell[f] for f in F)
    min_lam = min(lamb[e] for e in E)
    F0 = tuple(f for f in F if ell[f] == min_len)
    F1 = tuple(f for f in F if ell[f] > min_len)
    E0 = tuple(e for e in E if lamb[e] == min_lam)

    print("side", side_s, "S", tuple(i for i in range(n) if (mask >> i) & 1))
    print("F", [(f, ell[f]) for f in F])
    print("E", [(e, lamb[e], sorted(witnesses[e])) for e in E])
    print("F0", F0, "F1", F1, "E0", E0)
    print("F0 x E0 matrix")
    for f in F0:
        print(f, "".join("1" if f in witnesses[e] else "." for e in E0))
    print("F1 x E matrix")
    for f in F1:
        print(f, "".join("1" if f in witnesses[e] else "." for e in E))

    adj0 = {f: {e for e in E0 if f in witnesses[e]} for f in F0}
    all_m = enumerate_matchings(F0, adj0, 1000000)
    good = []
    bad = []
    for m in all_m:
        ok, erem, matched = stage1_extends(E, F1, witnesses, set(m.values()))
        item = tuple(sorted((f, e) for f, e in m.items()))
        (good if ok else bad).append((item, erem, matched))
    print("stage0 total", len(all_m), "good", len(good), "bad", len(bad))
    print("first good")
    for item in good[:5]:
        print(item)
    print("first bad")
    for item in bad[:10]:
        print(item)


if __name__ == "__main__":
    main()
