"""Gate the off-path B-component closed-tail repair for lemma (M).

For a raw path tail S on P_f, close S by absorbing every off-path component of
the cut graph B whose B-attachments to P_f all lie in S.  This absorbs
dangling cut branches that falsify the naked positive-extra bound while
leaving detours attached to both sides of P_f outside the switch.
"""

import subprocess

from _h import Bconn, GENG, dec
from _M_tailswitch_gate import boundary_gain
from _overlap_switch_probe import contained_intervals, interior_pair
from _satzmu_conn import struct_for_side


def b_closed_tail(n, adj, side, path, raw_tail):
    path_set = set(path)
    raw_tail = set(raw_tail)
    seen = set()
    absorbed = set()

    for v in range(n):
        if v in path_set or v in seen:
            continue

        stack = [v]
        seen.add(v)
        component = []
        attachments = set()

        while stack:
            x = stack.pop()
            component.append(x)
            for y in adj[x]:
                if side[x] == side[y]:
                    continue
                if y in path_set:
                    attachments.add(y)
                elif y not in seen:
                    seen.add(y)
                    stack.append(y)

        if attachments and attachments <= raw_tail:
            absorbed.update(component)

    return raw_tail | absorbed


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
        left = b_closed_tail(n, adj, side, path, set(path[: p2 + 1]))
        right = b_closed_tail(n, adj, side, path, set(path[r:]))
        gain_l = boundary_gain(n, adj, side, left)
        gain_r = boundary_gain(n, adj, side, right)

        acc["overlap"] += 1
        acc["min_sum"] = min(acc["min_sum"], gain_l + gain_r)
        if gain_l > 0 or gain_r > 0:
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
                    gain_l,
                    gain_r,
                    sorted(left),
                    sorted(right),
                )


def run():
    acc = {"overlap": 0, "caught": 0, "miss": 0, "first": None, "min_sum": 10**9}
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
    print("=== CLOSED-TAIL SWITCH gate ===", flush=True)
    print(
        f"overlaps={acc['overlap']} caught={acc['caught']} miss={acc['miss']} "
        f"min_gain_sum={acc['min_sum']}",
        flush=True,
    )
    print(f"first miss={acc['first']}", flush=True)


if __name__ == "__main__":
    run()
