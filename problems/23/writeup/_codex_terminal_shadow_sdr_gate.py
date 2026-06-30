"""Gate Hall/SDR for arbitrary neutral terminal-shadow switches.

This is broader than the seed+moat construction: for every connected-B maximum
cut in the small census, enumerate every neutral switch S that is terminal-
shadow valid, then test whether its witness graph

    crossing bad edges delta_M(S)  --  boundary B exits delta_B(S)

has a matching saturating the boundary exits.  Empirically this appears to be a
pure theorem of terminal-shadow neutrality, not of the special construction.
"""

import argparse
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import max_bipartite_matching, terminal_shadow_details


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


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
            cross = det["cross_m"]
            exits = det["bdy_b"]
            if not cross or len(cross) != len(exits):
                continue
            witness_adj = {f: [] for f in cross}
            for e, fs in det["witnesses"].items():
                for f in set(fs):
                    witness_adj[f].append(e)
            match_size, _matching = max_bipartite_matching(cross, exits, witness_adj)
            acc["switches"] += 1
            if match_size < len(exits):
                acc["fail"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        mask_tuple(n, mask),
                        match_size,
                        len(exits),
                    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    args = parser.parse_args()

    acc = dict(switches=0, fail=0, first_fail=None)
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["switches"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
        print(
            "N=%d switches=%d fail=%d"
            % (nn, acc["switches"] - before, acc["fail"]),
            flush=True,
        )
    print("=" * 72)
    print("switches:", acc["switches"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
