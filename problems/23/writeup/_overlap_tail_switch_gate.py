"""Gate a local switch candidate for lemma (M).

Candidate M-switch:
  If two P-contained bad chord intervals [p1,q1], [p2,q2] interior-overlap
  on a unique geodesic P, order p1 <= p2 and put r=min(q1,q2).  Then one of
  the two tail switches

      L = P[0..p2],        R = P[r..end]

  strictly increases cutsize.  Therefore an interior-overlap cannot occur in
  a global maximum cut.

This is stronger than "some subset improves" and is exact-testable.
"""

import subprocess

from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side
from _overlap_switch_probe import contained_intervals, interior_pair, cutsize


def gain(n, adj, side, verts):
    base = cutsize(n, adj, side)
    side2 = side[:]
    for v in verts:
        side2[v] ^= 1
    return cutsize(n, adj, side2) - base


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
        P = cyc[f][0]
        pair = interior_pair(contained_intervals(M, cyc, f, P))
        if pair is None:
            continue
        p1, q1, g1, p2, q2, g2, _lo, _hi = pair
        if p2 < p1:
            p1, q1, g1, p2, q2, g2 = p2, q2, g2, p1, q1, g1
        r = min(q1, q2)
        left = set(P[: p2 + 1])
        right = set(P[r:])
        gl = gain(n, adj, side, left)
        gr = gain(n, adj, side, right)
        acc["overlap"] += 1
        if gl > 0 or gr > 0:
            acc["caught"] += 1
            if gl > 0:
                acc["left"] += 1
            if gr > 0:
                acc["right"] += 1
        else:
            acc["miss"] += 1
            if acc["first"] is None:
                acc["first"] = (name, "".join(map(str, side)), f, P, (p1, q1, g1, p2, q2, g2), gl, gr)


def run():
    acc = {"overlap": 0, "caught": 0, "left": 0, "right": 0, "miss": 0, "first": None}
    for nn in range(6, 10):
        before = acc.copy()
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for a, b in E:
                adj[a].add(b)
                adj[b].add(a)
            for mask in range(1 << (n - 1)):
                side = [(mask >> v) & 1 for v in range(n)]
                check_cut(n, adj, side, g6, acc)
        print(
            f"  census N={nn}: overlaps={acc['overlap']-before['overlap']} "
            f"caught={acc['caught']-before['caught']} miss={acc['miss']-before['miss']}",
            flush=True,
        )
    print("=== OVERLAP TAIL-SWITCH gate ===", flush=True)
    print(
        f"  overlaps={acc['overlap']} caught={acc['caught']} "
        f"left={acc['left']} right={acc['right']} miss={acc['miss']}",
        flush=True,
    )
    print(f"  first miss={acc['first']}", flush=True)


if __name__ == "__main__":
    run()
