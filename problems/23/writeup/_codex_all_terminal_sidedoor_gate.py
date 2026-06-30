"""Gate SIDE-DOOR PREFIX HULL on all neutral terminal-shadow switches.

This is the broad analogue of _codex_sidedoor_prefix_hull_gate.py.  It does not
select R<0 seed+moat switches.  Instead, for every connected-B maximum cut in
the small census, it enumerates every neutral terminal-shadow-valid switch and
tests the corrected right-closed deficient-pair side-door atom:

    X = {f in C : ell[f] < t and Wit(f) subset Y},  Y subset E_<t
    |X| > |Y|  ==>  |delta_B(U) \\ Y| <= |delta_M(U) \\ X|.

Optionally it also tests the side-door matching from extra B-boundary edges to
extra bad-boundary edges.  A failure here would mean the corrected atom needs
the seed+moat selector; a pass says the right-closed condition is the relevant
restriction, not the selector.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import mask_tuple, test_sidedoor_for_switch


def scan_graph(name, n, edges, acc, max_et, want_matching):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None:
                continue
            if not det["cross_m"] or len(det["cross_m"]) != len(det["bdy_b"]):
                continue
            res = test_sidedoor_for_switch(n, adj, side, st, mask, max_et, want_matching)
            acc["switches"] += 1
            acc["checked"] += res.get("checked", 0)
            acc["deficient"] += res.get("deficient", 0)
            acc["skipped"] += res.get("skipped", 0)
            acc["status"][res["status"]] += 1
            if res.get("count_fail", 0) or res.get("match_fail", 0) or res["status"] != "ok":
                acc["fail"] += 1
                if acc["first"] is None:
                    acc["first"] = dict(
                        name=name,
                        n=n,
                        side="".join(map(str, side)),
                        S=mask_tuple(n, mask),
                        res=res,
                    )
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument("--max-et", type=int, default=14)
    parser.add_argument("--matching", action="store_true")
    args = parser.parse_args()

    acc = {
        "switches": 0,
        "checked": 0,
        "deficient": 0,
        "skipped": 0,
        "fail": 0,
        "first": None,
        "status": Counter(),
    }

    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        before_def = acc["deficient"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc, args.max_et, args.matching)
            if acc["first"] is not None:
                break
        print(
            "N=%d switches=%d deficient=%d fail=%d"
            % (nn, acc["switches"] - before, acc["deficient"] - before_def, acc["fail"]),
            flush=True,
        )
        if acc["first"] is not None:
            break

    print("=" * 72)
    print("switches:", acc["switches"])
    print("Hall pairs checked:", acc["checked"], "deficient:", acc["deficient"], "skipped:", acc["skipped"])
    print("status:", dict(acc["status"]))
    print("fail:", acc["fail"], acc["first"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
