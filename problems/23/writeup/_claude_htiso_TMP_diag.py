import sys
from collections import Counter
from _bdef_construct import Cn, mycielski
from _h import Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_length_tier_matching_gate import best_seed_moat_mask, residuals
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def build(level):
    E5 = Cn(5)
    n11, E11 = mycielski(5, E5)
    n23, E23 = mycielski(n11, E11)
    n47, E47 = mycielski(n23, E23)
    return {11: (n11, E11), 23: (n23, E23), 47: (n47, E47)}[level]


def diag(level, max_add):
    n, edges = build(level)
    adj = adj_from_edges(n, edges)
    sides = list(maxcut_all(n, adj))
    print("level", level, "num_maxcut_sides", len(sides), "max_add", max_add)
    c = Counter()
    for side in sides:
        if not Bconn(n, adj, side):
            c["not_Bconn"] += 1
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            c["struct_None"] += 1
            continue
        R = residuals(n, adj, side)
        if R is None:
            c["resid_None"] += 1
            continue
        neg = [v for v, rv in enumerate(R) if rv < 0]
        c["Bconn_ok"] += 1
        if not neg:
            c["no_neg_resid"] += 1
            continue
        c["has_neg_resid"] += 1
        for v in neg:
            got = best_seed_moat_mask(n, adj, side, st, v, max_add)
            if got is None:
                c["no_switch_v"] += 1
                continue
            _seed, mask, _psi = got
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None:
                c["bad_terminal_v"] += 1
                continue
            c["tested_v"] += 1
    print("diag", dict(c))
    sys.stdout.flush()


if __name__ == "__main__":
    level = int(sys.argv[1])
    max_add = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    diag(level, max_add)
