"""Print concrete exit classes for the first non-complete rare-exit residual."""

from collections import Counter

from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components


def main():
    n, edges, _ = h_blowup(2)
    adj = adj_from_edges(n, edges)
    side_s = "001111111111000000"
    side = [int(c) for c in side_s]
    mask = sum(1 << i for i in (2, 12, 13))
    st = struct_for_side(n, adj, side)
    M, ell, _T, _mu, cyc = st
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
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    rem = tuple(e for e in E if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}

    print("side", side_s, "S", tuple(i for i in range(n) if (mask >> i) & 1))
    print("F0", [(f, ell[f]) for f in F0])
    print("F1", [(f, ell[f]) for f in F1])
    print("E0", [(e, "degF1", deg_f1[e], "wit", sorted(witnesses[e])) for e in E0])
    print("stage0", sorted(m0.items()))
    print("remaining", [(e, lamb[e], sorted(witnesses[e])) for e in rem])

    for ci, (cl, cr) in enumerate(components(F1, rem, adj1), 1):
        print("component", ci, "L", cl, "R", cr)
        classes = {}
        for e in cr:
            neigh = tuple(f for f in cl if e in adj1.get(f, set()))
            classes.setdefault(neigh, []).append(e)
        for neigh, exits in sorted(classes.items(), key=lambda kv: (len(kv[0]), kv[0], kv[1])):
            missing = tuple(f for f in cl if f not in neigh)
            print("  class", "neigh", neigh, "missing", missing, "exits", tuple(sorted(exits)))
        print("  row missing", Counter(sum(1 for e in cr if e not in adj1.get(f, set())) for f in cl))
        print("  matrix")
        cr_sorted = tuple(sorted(cr))
        for f in sorted(cl):
            print("   ", f, "".join("1" if e in adj1.get(f, set()) else "." for e in cr_sorted))


if __name__ == "__main__":
    main()
