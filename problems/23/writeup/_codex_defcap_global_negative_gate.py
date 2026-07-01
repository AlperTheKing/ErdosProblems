"""Gate: deficient cap implies no negative residual anywhere in the cut.

This is a stronger variant of _codex_defcap_negative_scope_gate.py.

For every connected-B maximum cut in the small census, enumerate neutral
terminal-shadow switches with positive Psi and the two-cap decomposition.  If a
side cap has a nonempty subset Y with |N(Y)| <= |Y|, check that the whole cut
has no vertex with R[v] < 0.

If true, selected R[v] < 0 seed+moat switches cannot have deficient caps at
all, independent of whether the negative vertex lies inside the particular
switch being inspected.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, T, _mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        global_neg = tuple(v for v, rv in enumerate(R) if rv < 0)

        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            bad = deficient_cap_subset(leaves, exits_of_f, fset)
            if bad is None:
                continue
            acc["defcap"] += 1
            if global_neg:
                acc["global_fail"] += 1
                if acc["first"] is None:
                    acc["first"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        tuple(i for i in range(n) if (mask >> i) & 1),
                        det["psi"],
                        bad,
                        global_neg,
                        tuple(str(R[i]) for i in global_neg),
                    )
                return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    args = ap.parse_args()

    acc = Counter()
    acc["first"] = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N", nn, "defcap", acc["defcap"], "global_fail", acc["global_fail"], flush=True)
        if acc["first"] is not None:
            break

    print("=" * 60)
    print("defcap:", acc["defcap"])
    print("global_fail:", acc["global_fail"])
    print("first:", acc["first"])
    print("VERDICT:", "PASS" if acc["global_fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
