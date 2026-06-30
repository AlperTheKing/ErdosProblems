"""Broader N=23 apex probe for the Psi(W) terminal-shadow descent identity.
Enumerate many neutral switches (all singletons, all pairs, all triples, plus geodesic-prefix
half-switches from cyc) on the documented apex cut. For each gated switch verify dG == -Psi exactly.
Report counts + any FAIL or any Psi>0 (positive surplus would contradict gamma-min => must be 0 here)."""
import itertools
from fractions import Fraction as F
from _h import Bconn
from _bdef_construct import Cn, mycielski, is_triangle_free
from _satzmu_conn import struct_for_side
from _psi_terminal_descent_gate import (
    adj_from_edges, gamma_of, flip, delta_neutral, psi_and_gate,
)


def build_n23():
    E5 = Cn(5)
    n11, E11 = mycielski(5, E5)
    n23, E23 = mycielski(n11, E11)
    assert is_triangle_free(n23, E23)
    return n23, E23


def geodesic_halfswitches(n, adj, side):
    """All terminal prefixes/suffixes of all geodesic paths in cyc (the natural switch family)."""
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, mu, cyc = st
    Ws = set()
    for f, Ps in cyc.items():
        for P in Ps:
            for i in range(len(P)):
                Ws.add(frozenset(P[:i + 1]))   # prefix
                Ws.add(frozenset(P[i:]))       # suffix
    return [sorted(w) for w in Ws]


def main():
    n23, E23 = build_n23()
    adj = adj_from_edges(n23, E23)
    side = [int(c) for c in "10101101011001000000001"]
    assert len(side) == n23
    print("N=23 Bconn=%s gamma0=%s" % (Bconn(n23, adj, side), gamma_of(n23, adj, side)))

    # switch families
    Ws = []
    for v in range(n23):
        Ws.append([v])
    for combo in itertools.combinations(range(n23), 2):
        Ws.append(list(combo))
    for combo in itertools.combinations(range(n23), 3):
        Ws.append(list(combo))
    Ws += geodesic_halfswitches(n23, adj, side)

    gated = 0; exact_eq = 0; fail = 0; pospsi = 0
    first_fail = None
    gamma0 = gamma_of(n23, adj, side)
    seen = set()
    for W in Ws:
        key = frozenset(W)
        if key in seen:
            continue
        seen.add(key)
        if delta_neutral(n23, adj, side, W) != 0:
            continue
        side2 = flip(side, W)
        g1 = gamma_of(n23, adj, side2)
        if g1 is None:
            continue
        res = psi_and_gate(n23, adj, side, W)
        if res is None or not res['ok']:
            continue
        gated += 1
        Psi = res['Psi']
        dG = g1 - gamma0
        if Psi > 0:
            pospsi += 1
        if dG + Psi == 0:
            exact_eq += 1
        elif dG + Psi > 0:
            fail += 1
            if first_fail is None:
                first_fail = (tuple(W), str(Psi), str(dG))
    print("N=23 switches tested (deduped): %d" % len(seen))
    print("N=23 gated switches: %d" % gated)
    print("N=23 EXACT EQ (dG == -Psi): %d" % exact_eq)
    print("N=23 Psi>0 (positive surplus -- must be 0 on a gamma-min cut): %d" % pospsi)
    print("N=23 FAIL (dG > -Psi): %d" % fail, first_fail or "")


if __name__ == "__main__":
    main()
