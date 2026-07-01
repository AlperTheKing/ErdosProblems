"""Broad replacement-exit gate for all neutral terminal-shadow switches.

This extends _codex_replacement_exit_gate beyond selected R[v]<0 switches.
It checks every mixed-tier neutral terminal-shadow switch in the small census:
after rare stage0, each residual miss (f,e) has a replacement exit witnessed
by f of same-outside, same-terminal, or corner type.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_replacement_exit_gate import gate


def scan_graph(name, n, edges, acc):
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
            ok, status, info = gate(st, det, mask)
            # gate() returns ok for no missing cases too; skip pure single-tier
            # switches for a cleaner mixed-tier count.
            if status == "ok" and info.get("stats", {}).get("missing", 0) == 0:
                acc["skip_no_missing"] += 1
            else:
                acc["switches"] += 1
                acc["status"][status] += 1
                acc["stats"].update(info.get("stats", {}))
            if not ok and acc["first"] is None:
                acc["first"] = {
                    "name": name,
                    "n": n,
                    "side": "".join(map(str, side)),
                    "S": tuple(i for i in range(n) if (mask >> i) & 1),
                    "status": status,
                    "info": info,
                }
                return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    args = ap.parse_args()
    acc = {"switches": 0, "skip_no_missing": 0, "status": Counter(), "stats": Counter(), "first": None}
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        before_skip = acc["skip_no_missing"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N=%d switches=%d skip_no_missing=%d first=%s" % (nn, acc["switches"] - before, acc["skip_no_missing"] - before_skip, bool(acc["first"])), flush=True)
        if acc["first"] is not None:
            break
    print("switches:", acc["switches"])
    print("skip_no_missing:", acc["skip_no_missing"])
    print("status:", dict(acc["status"]))
    print("stats:", dict(acc["stats"]))
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
