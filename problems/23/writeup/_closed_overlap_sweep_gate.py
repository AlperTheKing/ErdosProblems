"""Gate a closed-prefix/suffix sweep for P-contained interior-overlap.

For intervals [p1,q1], [p2,q2] with p1 <= p2 < r=min(q1,q2), the raw
two-tail switch fixes the left boundary at p2 and right boundary at r.  Local
ballast can kill those fixed tails.  This gate lets the boundary slide through
the overlap and closes each prefix/suffix by absorbing off-path B-components
whose path attachments are contained in the switched path segment.
"""

import subprocess

from _closed_tail_switch_gate import b_closed_tail
from _h import Bconn, GENG, dec
from _M_tailswitch_gate import boundary_gain
from _overlap_switch_probe import contained_intervals, interior_pair
from _satzmu_conn import struct_for_side


def check_cut(n, adj, side, name, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    for f in M:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        pair = interior_pair(contained_intervals(M, cyc, f, path))
        if pair is None:
            continue
        p1, q1, g1, p2, q2, g2, _lo, _hi = pair
        if p2 < p1:
            p1, q1, g1, p2, q2, g2 = p2, q2, g2, p1, q1, g1
        r = min(q1, q2)

        best = (-10**9, None, None)
        for k in range(p2, r):
            left = b_closed_tail(n, adj, side, path, set(path[: k + 1]))
            gain_l = boundary_gain(n, adj, side, left)
            if gain_l > best[0]:
                best = (gain_l, "prefix", k)

            right = b_closed_tail(n, adj, side, path, set(path[k + 1 :]))
            gain_r = boundary_gain(n, adj, side, right)
            if gain_r > best[0]:
                best = (gain_r, "suffix", k + 1)

        acc["overlap"] += 1
        acc["min_best"] = min(acc["min_best"], best[0])
        if best[0] > 0:
            acc["caught"] += 1
        else:
            acc["miss"] += 1
            if acc["first"] is None:
                acc["first"] = (
                    name,
                    "".join(map(str, side)),
                    f,
                    path,
                    (p1, q1, g1, p2, q2, g2),
                    best,
                )


def run():
    acc = {"overlap": 0, "caught": 0, "miss": 0, "first": None, "min_best": 10**9}
    for nn in range(6, 10):
        before = dict(acc)
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, edges = dec(g6)
            adj = [set() for _ in range(n)]
            for a, b in edges:
                adj[a].add(b)
                adj[b].add(a)
            for mask in range(1 << (n - 1)):
                side = [(mask >> v) & 1 for v in range(n)]
                check_cut(n, adj, side, g6, acc)
        print(
            f"census N={nn}: overlaps={acc['overlap'] - before['overlap']} "
            f"caught={acc['caught'] - before['caught']} "
            f"miss={acc['miss'] - before['miss']}",
            flush=True,
        )
    print("=== CLOSED-OVERLAP SWEEP gate ===", flush=True)
    print(
        f"overlaps={acc['overlap']} caught={acc['caught']} miss={acc['miss']} "
        f"min_best_gain={acc['min_best']}",
        flush=True,
    )
    print(f"first miss={acc['first']}", flush=True)


if __name__ == "__main__":
    run()
