"""Claude exact gate: PACKET EXCHANGE inequality (1.3)/(1.4) of
PACKET_EXCHANGE_JOINT_BANK_GPTPRO.md.

(1.3)  m_R + h/2 <= r^2/25 + d/2   for ANY packet W on a gamma-min max cut,
where R=V\\W, m_R=e_M(R), h=|delta_M(W)|, d=|delta_B(W)|.
(1.4)  eta >= (N^2-r^2)/25 - p - d/2 - h/2  [algebraically equivalent; asserted too]

Gate A (exhaustive): on witnesses W1,W2,W4 (n=15) and the n=19 contact pair,
check (1.3) for ALL 2^n subsets W (direct inequality; no beta needed).

Gate B (derivation): on curated packets INCLUDING h>0 cases, verify the full
exchange chain: beta(G[R]) <= r^2/25 by enumeration; orientation identity over
the d+h boundary edges (each becomes bad in exactly one orientation);
better orientation <= (d+h)/2; modified bad count p + beta_R + min >= m
(maximality comparison).

Witnesses reuse _claude_shprime_witness_gate builders; plus glue_copies n=19
from _claude_cactus_family_gate.
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction

with contextlib.redirect_stdout(io.StringIO()):
    import _claude_shprime_witness_gate as WG
    import _claude_cactus_family_gate as CG


def bits(mask, n):
    return [v for v in range(n) if (mask >> v) & 1]


def gate_A(name, n, edges, side):
    m = sum(1 for u, v in edges if side[u] == side[v])
    worst = None
    for mask in range(1 << n):
        m_R = 0
        h = 0
        d = 0
        for u, v in edges:
            iu, iv = (mask >> u) & 1, (mask >> v) & 1
            bad = side[u] == side[v]
            if iu and iv:
                pass  # inside W
            elif not iu and not iv:
                if bad:
                    m_R += 1
            else:
                if bad:
                    h += 1
                else:
                    d += 1
        r = n - bin(mask).count("1")
        lhs = Fraction(m_R) + Fraction(h, 2)
        rhs = Fraction(r * r, 25) + Fraction(d, 2)
        assert lhs <= rhs, f"{name}: (1.3) FAILS at W=mask{mask}: {lhs} > {rhs}"
        margin = rhs - lhs
        if worst is None or margin < worst[0]:
            worst = (margin, mask, m_R, h, d, r)
    # (1.4) equivalence spot-check at the worst packet
    margin, mask, m_R, h, d, r = worst
    p = m - m_R - h
    eta = Fraction(n * n, 25) - m
    assert eta >= Fraction(n * n - r * r, 25) - p - Fraction(d, 2) - Fraction(h, 2) \
        or (Fraction(n * n - r * r, 25) - p - Fraction(d, 2) - Fraction(h, 2)) - eta <= 0
    print(f"PACKET-A {name}: all {1 << n} packets satisfy (1.3); "
          f"worst margin={margin} at |W|={n - r} (m_R={m_R},h={h},d={d})")


def gate_B(name, n, edges, side, packets):
    m = sum(1 for u, v in edges if side[u] == side[v])
    for pname, W in packets:
        Wset = frozenset(W)
        R = [v for v in range(n) if v not in Wset]
        r = len(R)
        ridx = {v: i for i, v in enumerate(R)}
        p = sum(1 for u, v in edges if u in Wset and v in Wset and side[u] == side[v])
        m_R = sum(1 for u, v in edges if u not in Wset and v not in Wset and side[u] == side[v])
        bd_bad = [(u, v) for u, v in edges if (u in Wset) != (v in Wset) and side[u] == side[v]]
        bd_blue = [(u, v) for u, v in edges if (u in Wset) != (v in Wset) and side[u] != side[v]]
        h, d = len(bd_bad), len(bd_blue)
        assert p + h + m_R == m
        # beta(G[R]) exact
        redges = [(ridx[u], ridx[v]) for u, v in edges if u not in Wset and v not in Wset]
        beta_R, best = None, []
        for mask in range(1 << r):
            bad_in = sum(1 for u, v in redges if ((mask >> u) & 1) == ((mask >> v) & 1))
            if beta_R is None or bad_in < beta_R:
                beta_R, best = bad_in, [mask]
            elif bad_in == beta_R:
                best.append(mask)
        assert Fraction(beta_R) <= Fraction(r * r, 25), f"{name}/{pname}: beta_R > r^2/25"
        # orientation identity over d+h boundary edges, for every optimal coloring
        for mask in best:
            def bcount(mm):
                c = 0
                for u, v in bd_bad + bd_blue:
                    w, x = (u, v) if u in Wset else (v, u)
                    if ((mm >> ridx[x]) & 1) == side[w]:
                        c += 1
                return c
            b1 = bcount(mask)
            b2 = bcount(mask ^ ((1 << r) - 1))
            assert b1 + b2 == d + h, f"{name}/{pname}: orientation identity fails"
            dmg = min(b1, b2)
            assert Fraction(dmg) <= Fraction(d + h, 2)
            assert p + beta_R + dmg >= m, f"{name}/{pname}: maximality comparison fails"
        lhs = Fraction(m_R) + Fraction(h, 2)
        rhs = Fraction(r * r, 25) + Fraction(d, 2)
        assert lhs <= rhs
        print(f"PACKET-B {name}/{pname}: p={p} h={h} d={d} m_R={m_R} r={r} "
              f"beta_R={beta_R} (1.3) {lhs}<={rhs} chain-OK({len(best)} opt)")


def main():
    w1 = WG.build(1, [], [])
    w2 = WG.build(1, [], [(0, 0, 1)])
    w4 = WG.build(1, [], [(0, 0, 1), (0, 5, 0)])
    n19, e19, s19, cells19 = CG.glue_copies([((0, 0), (1, 0))], 2)

    for name, inst in (("W1", w1), ("W2", w2), ("W4", w4)):
        gate_A(name, inst["n"], inst["edges"], inst["side"])
    gate_A("N19pair", n19, e19, s19)

    # curated packets with h>0: cell + one endpoint of the C5 bad edge (4,0mod)
    # C5 vertices are 10..14 in W1/W2/W4; its bad edge is (10, 14) (=C5 0-4).
    atom = list(range(10))
    for name, inst in (("W1", w1), ("W2", w2), ("W4", w4)):
        packets = [
            ("cells-only(h0)", atom),
            ("cell+c5v14(h1)", atom + [14]),          # bad edge (10,14) crosses
            ("cell+c5v10v11(h1)", atom + [10, 11]),   # bad (10,14) crosses via 10
            ("c5-only", list(range(10, 15))),
            ("cell+wholeC5", list(range(15))),        # R empty
        ]
        packets = [(pn, P) for pn, P in packets if len(P) < inst["n"]]
        gate_B(name, inst["n"], inst["edges"], inst["side"], packets)
    # n19: two cells share vertex 0; packets: one cell (h0), one cell minus glue,
    # cell + 3 vertices of the other
    gate_B("N19pair", n19, e19, s19,
           [("cellA(h0)", sorted(cells19[0])),
            ("cellA-minus-glue", sorted(set(cells19[0]) - {0})),
            ("cellA+3ofB", sorted(set(cells19[0]) | set(sorted(cells19[1])[1:4])))])
    print("PASS packet-exchange gate: (1.3) exhaustive + derivation chain exact")


if __name__ == "__main__":
    main()
