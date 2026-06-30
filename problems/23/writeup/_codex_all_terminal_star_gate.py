"""Gate star-door structure for all neutral terminal-shadow switches.

This broadens the one-hub star diagnostic beyond the selected seed+moat
switches.  It is a falsification/strength test for the cleaner theorem:

  every blue-closed hull extra-exit set from a neutral terminal-shadow switch
  is a one-hub star, and every nonempty right-door set is singleton or full.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary
from _codex_blueclosed_hull_gate import blue_close_inside_s


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def scan_switch(name, n, adj, side, st, mask_s, acc):
    cyc = st[4]
    det = terminal_shadow_details(n, adj, side, st, mask_s)
    if det is None or not det["cross_m"] or len(det["cross_m"]) != len(det["bdy_b"]):
        return
    cross = list(det["cross_m"])
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: set() for f in cross}
    for e, fs in witnesses.items():
        for f in fs:
            exits_of_f[f].add(e)
    prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in cross}

    acc["switches"] += 1
    for bits in range(1, 1 << len(cross)):
        x_set = {cross[i] for i in range(len(cross)) if (bits >> i) & 1}
        y_set = set().union(*(exits_of_f[f] for f in x_set))
        mask_u = 0
        for f in x_set:
            for e in exits_of_f[f]:
                for pmask in prefixes[f].get(e, ()):
                    mask_u |= pmask
        mask_u = blue_close_inside_s(n, adj, side, mask_s, mask_u)
        bdu, mdu = edge_boundary(n, adj, side, mask_u)
        extra_b = tuple(sorted(bdu - y_set))
        extra_m = tuple(sorted(mdu - x_set))
        if not extra_b:
            continue
        acc["cases"] += 1

        common = set(extra_b[0])
        for e in extra_b[1:]:
            common &= set(e)
        if common:
            acc["exit_star"][True] += 1
        else:
            acc["exit_star"][False] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (
                    "exit_nonstar",
                    name,
                    n,
                    "".join(map(str, side)),
                    mask_tuple(n, mask_s),
                    tuple(sorted(x_set)),
                    extra_b,
                    extra_m,
                )
            return

        full = set(extra_b)
        for f in extra_m:
            doors = {e for e in extra_b if f in witnesses.get(e, set())}
            if doors and len(doors) != 1 and doors != full:
                acc["door_star_fail"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        "door_nonstar",
                        name,
                        n,
                        "".join(map(str, side)),
                        mask_tuple(n, mask_s),
                        tuple(sorted(x_set)),
                        extra_b,
                        f,
                        tuple(sorted(doors)),
                    )
                return


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        for mask_s in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask_s) != 0:
                continue
            scan_switch(name, n, adj, side, st, mask_s, acc)
            if acc["first_fail"] is not None:
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=9)
    args = parser.parse_args()
    acc = {
        "switches": 0,
        "cases": 0,
        "exit_star": Counter(),
        "door_star_fail": 0,
        "first_fail": None,
    }
    for nn in range(args.min_n, args.max_n + 1):
        before = dict(acc)
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first_fail"] is not None:
                break
        print(
            "N=%d switches=%d cases=%d exit_star=%s door_fail=%d"
            % (nn, acc["switches"], acc["cases"], dict(acc["exit_star"]), acc["door_star_fail"]),
            flush=True,
        )
        if acc["first_fail"] is not None:
            break
    print("first_fail:", acc["first_fail"])
    print("VERDICT:", "PASS" if acc["first_fail"] is None else "FAIL")


if __name__ == "__main__":
    main()
