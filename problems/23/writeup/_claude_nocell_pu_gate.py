"""Claude exact gate: (PU-packet)/(NoCell-PU) of PURE_UPO_HALL_ROUTE_GPTPRO.md.

  (PU-packet)  2*(D_Q(Y) - |Y| + Sigma_L) <= B(Y),
  B(Y) = (N^2 - r_Y^2)/25 - e_M(Y) - (|dB(Y)| + |dM(Y)|)/2,   r_Y = |V \\ Y|,
  D_Q(Y) = sum_g |cyc g|^-1 * sum_{P in cyc[g], V(P) subseteq Y} |V(P) cap V(Q)|,
  Sigma_L = (L^2 - 25)/50, L = |V(Q)|.

cyc[g] = ALL shortest paths between g's endpoints in the B-graph (cut edges);
V(P) includes both endpoints. Row Q = a chosen element of cyc[f].

Instances:
  P1  pure odd cycles C7, C9, C11 (alternating cut, one bad edge): k=0 -> the
      inequality must hold for ALL 2^n subsets Y; Y=V must be TIGHT (=2*Sigma_L).
  P2  SH' witnesses W1, W2, W4 (n=15, L=5 rows, Sigma_5=0): all 2^15 subsets;
      failures allowed ONLY for packets containing a positive UNIT-FLAT5 cell -
      report failure count + verify every failure contains the atom core.
  P3  two-lane p198 instance (n=27, bad rows L=7/9, R_Q((0,8))=28>N): k=0 (unit
      atoms are not FLAT5) -> NO failures allowed on the tested family:
      all Y built from structured pieces (x-intervals x attachment choices x
      slab-lane prefixes) + 300000 deterministic LCG samples + Y=V.
Also reports the Banked-UPO margin at Y=V per instance.
"""

from __future__ import annotations

import contextlib
import io
from collections import deque
from fractions import Fraction
from itertools import combinations

with contextlib.redirect_stdout(io.StringIO()):
    import _claude_shprime_witness_gate as WG


def bgraph_paths(n, edges, side, g):
    """All shortest paths between endpoints of bad edge g in the B-graph."""
    B = [[] for _ in range(n)]
    for u, v in edges:
        if side[u] != side[v]:
            B[u].append(v)
            B[v].append(u)
    s, t = g
    dist = [-1] * n
    dist[s] = 0
    dq = deque([s])
    while dq:
        x = dq.popleft()
        for y in B[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                dq.append(y)
    assert dist[t] >= 0, "endpoints not B-connected"
    # enumerate all shortest paths s->t by DFS on the BFS DAG
    paths = []
    stack = [(t, (t,))]
    while stack:
        x, acc = stack.pop()
        if x == s:
            paths.append(frozenset(acc))
            continue
        for y in B[x]:
            if dist[y] == dist[x] - 1:
                stack.append((y, acc + (y,)))
    return paths, dist[t] + 1  # vertex count L


def atom_table(n, edges, side):
    """Per bad edge: (weight, list of (frozenset V(P)))."""
    bad = [tuple(sorted(e)) for e in edges if side[e[0]] == side[e[1]]]
    table = {}
    for g in bad:
        paths, L = bgraph_paths(n, edges, side, g)
        table[g] = (Fraction(1, len(paths)), paths, L)
    return bad, table


def check_packet(Ymask, n, edges, side, bad, table, Q, sigma_L):
    Y = [(Ymask >> v) & 1 for v in range(n)]
    ysz = bin(Ymask).count("1")
    r = n - ysz
    D = Fraction(0)
    for g in bad:
        w, paths, _L = table[g]
        for P in paths:
            if all(Y[v] for v in P):
                D += w * len(P & Q)
    eM = sum(1 for u, v in edges if side[u] == side[v] and Y[u] and Y[v])
    dB = sum(1 for u, v in edges if side[u] != side[v] and Y[u] != Y[v])
    dM = sum(1 for u, v in edges if side[u] == side[v] and Y[u] != Y[v])
    lhs = 2 * (D - ysz + sigma_L)
    rhs = Fraction(n * n - r * r, 25) - eM - Fraction(dB + dM, 2)
    return lhs, rhs, D


def pure_cycle(L):
    edges = [(i, (i + 1) % L) for i in range(L)]
    side = [i % 2 for i in range(L)]  # edge (L-1,0) bad
    return L, [tuple(sorted(e)) for e in edges], side


def run_pure(L):
    """Split verdicts: BSH(Y) [2(D-|Y|+Sigma_L) <= eta] must hold for ALL Y
    (fatal otherwise); (PU-packet) [<= B(Y)] must hold for POSITIVE-DEFECT
    packets (D_Q(Y) > |Y|) — defect<=0 packets are covered by the bank case
    (BSH(defect<=0) <=> eta/2 >= Sigma_L, the k=0 joint-bank statement)."""
    n, edges, side = pure_cycle(L)
    bad, table = atom_table(n, edges, side)
    assert len(bad) == 1
    f = bad[0]
    _w, paths, Lrow = table[f]
    assert Lrow == L and len(paths) == 1
    Q = paths[0]
    sigma_L = Fraction(L * L - 25, 50)
    eta = Fraction(n * n, 25) - len(bad)
    bsh_fails = 0
    pu_pos_fails = 0
    pu_nonpos_fails = 0
    for mask in range(1 << n):
        lhs, rhs, D = check_packet(mask, n, edges, side, bad, table, Q, sigma_L)
        ysz = bin(mask).count("1")
        if lhs > eta:
            bsh_fails += 1
        if lhs > rhs:
            if D > ysz:
                pu_pos_fails += 1
            else:
                pu_nonpos_fails += 1
    full = (1 << n) - 1
    lhs, rhs, D = check_packet(full, n, edges, side, bad, table, Q, sigma_L)
    assert bsh_fails == 0, f"C{L}: {bsh_fails} BSH failures (FATAL)"
    assert pu_pos_fails == 0, f"C{L}: {pu_pos_fails} positive-defect PU failures"
    assert lhs == rhs == 2 * sigma_L, f"C{L}: Y=V not tight"
    print(f"NOCELL-PU C{L}: BSH all {1 << n} OK; PU pos-defect OK; "
          f"PU nonpos-defect fails={pu_nonpos_fails} (bank-case covered); "
          f"Y=V tight={lhs}")


def run_witness(name, inst):
    n, edges, side = inst["n"], inst["edges"], inst["side"]
    bad, table = atom_table(n, edges, side)
    # row of the C5 bad edge (10,14) (L=5) — the longest-row bad edge here
    f = (10, 14)
    assert f in table
    _w, paths, L = table[f]
    Q = paths[0]
    sigma_L = Fraction(L * L - 25, 50)
    atom_core = frozenset(inst.get("core", range(10)))
    eta = Fraction(n * n, 25) - len(bad)
    bsh_fails = 0
    pu_pos_fails = 0
    pu_pos_fails_no_core = 0
    pu_nonpos_fails = 0
    for mask in range(1 << n):
        lhs, rhs, D = check_packet(mask, n, edges, side, bad, table, Q, sigma_L)
        ysz = bin(mask).count("1")
        if lhs > eta:
            bsh_fails += 1
        if lhs > rhs:
            if D > ysz:
                pu_pos_fails += 1
                Yset = {v for v in range(n) if (mask >> v) & 1}
                if not atom_core <= Yset:
                    pu_pos_fails_no_core += 1
            else:
                pu_nonpos_fails += 1
    print(f"NOCELL-PU {name}: L={L} BSH_fails={bsh_fails} "
          f"PU_posdefect_fails={pu_pos_fails} (without_atom_core="
          f"{pu_pos_fails_no_core}) PU_nonpos_fails={pu_nonpos_fails}")
    assert bsh_fails == 0, f"{name}: BSH fails (FATAL)"
    return pu_pos_fails, pu_pos_fails_no_core


def build_two_lane_p198():
    edges = set()
    for i in range(8):
        edges.add(tuple(sorted((i, i + 1))))
    for i in range(9):
        edges.add(tuple(sorted((i, 9 + i))))
        edges.add(tuple(sorted((i, 18 + i))))
    for i in range(8):
        for a in (9 + i, 18 + i):
            for b in (9 + i + 1, 18 + i + 1):
                edges.add(tuple(sorted((a, b))))
    for g in ((0, 8), (0, 6), (2, 6), (2, 8)):
        edges.add(g)
    side = [0] * 27
    for i in range(9):
        side[i] = i % 2
        side[9 + i] = 1 - side[i]
        side[18 + i] = 1 - side[i]
    return 27, sorted(edges), side


def run_two_lane():
    n, edges, side = build_two_lane_p198()
    # triangle-free check
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for u, v in edges:
        assert not (adj[u] & adj[v])
    bad, table = atom_table(n, edges, side)
    assert set(bad) == {(0, 8), (0, 6), (2, 6), (2, 8)}
    m = len(bad)
    # row of f=(0,8)
    _w, paths, L = table[(0, 8)]
    Q = max(paths, key=lambda P: len(P))
    sigma_L = Fraction(L * L - 25, 50)
    eta = Fraction(n * n, 25) - m
    # R_Q at Y=V
    full = (1 << n) - 1
    lhs, rhs, D = check_packet(full, n, edges, side, bad, table, Q, sigma_L)
    print(f"TWO-LANE: n={n} m={m} L={L} |cyc(0,8)|={len(paths)} R_Q={D} "
          f"banked_margin={Fraction(n) + eta / 2 - sigma_L - D}")
    assert lhs <= rhs, "TWO-LANE fails at Y=V (Banked-UPO violation!)"
    fails = 0
    nonpos_fails = 0
    tested = 0
    worst = None

    def test(mask):
        nonlocal fails, tested, worst, nonpos_fails
        lhs, rhs, D = check_packet(mask, n, edges, side, bad, table, Q, sigma_L)
        tested += 1
        if lhs > eta:
            print(f"  BSH-FAIL mask={mask:x} lhs={lhs} eta={eta}")
            fails += 1
            return
        if lhs > rhs:
            if D > bin(mask).count("1"):
                fails += 1
                print(f"  PU-POSDEFECT-FAIL mask={mask:x} lhs={lhs} rhs={rhs}")
            else:
                nonpos_fails += 1
        else:
            marg = rhs - lhs
            if worst is None or marg < worst[0]:
                worst = (marg, mask)

    # structured: x-interval [i..j] + per-index attachment choice bits + Y=V
    for i in range(9):
        for j in range(i, 9):
            base = 0
            for x in range(i, j + 1):
                base |= 1 << x
            for att in range(4):  # 0 none, 1 +a lane, 2 +b lane, 3 both
                mask = base
                for x in range(i, j + 1):
                    if att & 1:
                        mask |= 1 << (9 + x)
                    if att & 2:
                        mask |= 1 << (18 + x)
                test(mask)
    # lane-only prefixes and full lanes
    for lane in (9, 18):
        for j in range(9):
            mask = 0
            for x in range(j + 1):
                mask |= 1 << (lane + x)
            test(mask)
    # LCG sample
    state = 123456789
    for _ in range(300000):
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        test(state % (1 << 27))
    assert fails == 0, f"TWO-LANE: {fails} BSH/pos-defect failures (route dead)"
    print(f"NOCELL-PU TWO-LANE: {tested} packets OK (structured+300k LCG), "
          f"nonpos_bankcase_fails={nonpos_fails}, worst margin={worst[0]}")


def main():
    for L in (7, 9, 11):
        run_pure(L)
    for name, inst in (("W1", WG.build(1, [], [])),
                       ("W2", WG.build(1, [], [(0, 0, 1)])),
                       ("W4", WG.build(1, [], [(0, 0, 1), (0, 5, 0)]))):
        run_witness(name, inst)
    run_two_lane()
    print("PASS NoCell-PU gate")


if __name__ == "__main__":
    main()
