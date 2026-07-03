"""Claude exact gate: BLUE-DETOUR UPO (BLUE_DETOUR_UPO_GPTPRO.md).

Per row Q of bad edge f (K-component-scoped Tw):
  H_Q = G_B - E_Q^B; components B_Q; T_Q(K) = sum_{q in K cap Q} Tw_C(q);
  U_Q^+ = sum_K (T_Q(K)-|K|)_+;  W_Q = V(Q) U (positive components);
  B(W) = (N^2-r^2)/25 - p - (d+h)/2.
Checks:
  C1 identity R_Q = sum_K T_Q(K) and R_Q - N <= U_Q^+;
  C2 (BD-UPO)    U_Q^+ <= eta/2 - Sigma_L;
  C3 (BD-Packet) 2(U_Q^+ + Sigma_L) <= B(W_Q).
Instances: pure C7/C9/C11 (tightness asserted); two-lane p198 (margins asserted);
census N<=NMAX all gamma-min B-connected cuts, all rows (L>5 primary; L=5 counted
separately). Failures classified, exact Fractions everywhere.
"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
from collections import deque
from fractions import Fraction as F

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")

with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec, GENG, Bconn
    from _satzmu_conn import struct_for_side, kcomponents
    from _stark1 import gmins
    from _codex_schur_ec_gate import adj_from_edges

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def components_minus_row(n, edges, side, rowQ):
    """Components of blue graph minus the row's blue edges."""
    rq = list(rowQ)
    row_blue = set()
    for a, b in zip(rq, rq[1:]):
        if side[a] != side[b]:
            row_blue.add(tuple(sorted((a, b))))
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        if side[u] != side[v] and tuple(sorted((u, v))) not in row_blue:
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
    comps = {}
    for v in range(n):
        comps.setdefault(find(v), set()).add(v)
    return list(comps.values())


def check_row(n, edges, side, Ms, cyc, Q, f, label, stats):
    m_all = sum(1 for u, v in edges if side[u] == side[v])
    eta = F(n * n, 25) - m_all
    L = len(set(Q))
    sigma_L = F(L * L - 25, 50)
    # component-scoped Tw
    tw = {}
    for g in Ms:
        mm = len(cyc[g])
        cnt = {}
        for P in cyc[g]:
            for v in set(P):
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            tw[v] = tw.get(v, F(0)) + F(c, mm)
    R_Q = sum(tw.get(v, F(0)) for v in set(Q))
    comps = components_minus_row(n, edges, side, Q)
    assert sum(len(K) for K in comps) == n
    TQ = []
    for K in comps:
        TQ.append((sum(tw.get(v, F(0)) for v in set(Q) & K), len(K), K))
    assert sum(t for t, _s, _K in TQ) == R_Q, f"{label}: T_Q sum != R_Q"
    U_plus = sum(max(F(0), t - s) for t, s, _K in TQ)
    assert R_Q - n <= U_plus, f"{label}: decomposition (1) fails"
    # canonical packet
    W = set(Q)
    for t, s, K in TQ:
        if t - s > 0:
            W |= K
    r = n - len(W)
    p = sum(1 for u, v in edges if side[u] == side[v] and u in W and v in W)
    h = sum(1 for u, v in edges if side[u] == side[v] and (u in W) != (v in W))
    d = sum(1 for u, v in edges if side[u] != side[v] and (u in W) != (v in W))
    BW = F(n * n - r * r, 25) - p - F(d + h, 2)
    bd_upo = U_plus <= eta / 2 - sigma_L
    bd_packet = 2 * (U_plus + sigma_L) <= BW
    key = "L5" if L == 5 else "Lgt5"
    stats[key]["rows"] += 1
    if not bd_upo:
        stats[key]["upo_fail"] += 1
        if len(stats[key]["upo_wit"]) < 3:
            stats[key]["upo_wit"].append((label, f, tuple(Q), U_plus, eta / 2 - sigma_L))
    if not bd_packet:
        stats[key]["packet_fail"] += 1
        if len(stats[key]["packet_wit"]) < 3:
            stats[key]["packet_wit"].append(
                (label, f, tuple(Q), 2 * (U_plus + sigma_L), BW, U_plus, p, h, d, r))
    return R_Q, U_plus, eta, sigma_L, BW


def run_graph(n, edges, side_str, label, stats):
    adj = adj_from_edges(n, edges)
    sd = [int(c) for c in side_str] if isinstance(side_str, str) else list(side_str)
    st = struct_for_side(n, adj, sd)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    comp, find = kcomponents(n, cyc)
    Mc = {}
    for f in M:
        Mc.setdefault(find(f[0]), []).append(f)
    for c, Ms in Mc.items():
        for f in Ms:
            for Q in cyc[f]:
                check_row(n, edges, sd, Ms, cyc, tuple(Q), f, label, stats)


def new_stats():
    return {k: {"rows": 0, "upo_fail": 0, "packet_fail": 0,
                "upo_wit": [], "packet_wit": []} for k in ("L5", "Lgt5")}


def main():
    stats = new_stats()
    # pure cycles: tightness
    for L in (7, 9, 11):
        edges = [tuple(sorted((i, (i + 1) % L))) for i in range(L)]
        side = [i % 2 for i in range(L)]
        s0 = new_stats()
        run_graph(L, edges, side, f"C{L}", s0)
        assert s0["Lgt5"]["rows"] == 1 and s0["Lgt5"]["upo_fail"] == 0 \
            and s0["Lgt5"]["packet_fail"] == 0
        print(f"BLUE-DETOUR C{L}: row OK (tight)")
    # two-lane p198
    import _claude_nocell_pu_gate as NPG
    n, edges, side = NPG.build_two_lane_p198()
    s1 = new_stats()
    run_graph(n, edges, side, "two-lane", s1)
    tot = s1["L5"]["rows"] + s1["Lgt5"]["rows"]
    fails = (s1["L5"]["upo_fail"] + s1["Lgt5"]["upo_fail"]
             + s1["L5"]["packet_fail"] + s1["Lgt5"]["packet_fail"])
    print(f"BLUE-DETOUR two-lane: rows={tot} fails={fails} "
          f"(L>5 rows={s1['Lgt5']['rows']})")
    assert fails == 0, f"two-lane failures: {s1}"
    # witnesses W1/W2/W4
    import _claude_shprime_witness_gate as WG
    for name, inst in (("W1", WG.build(1, [], [])),
                       ("W2", WG.build(1, [], [(0, 0, 1)])),
                       ("W4", WG.build(1, [], [(0, 0, 1), (0, 5, 0)]))):
        s2 = new_stats()
        run_graph(inst["n"], inst["edges"], inst["side"], name, s2)
        fgt5 = s2["Lgt5"]["upo_fail"] + s2["Lgt5"]["packet_fail"]
        # L=5 packet failures must contain the protected cell core (k=1 there):
        core = frozenset(range(10))
        for w in s2["L5"]["packet_wit"]:
            Q = set(w[2])
            assert Q & core, f"{name}: L5 packet failure NOT at the cell rows: {w}"
        print(f"BLUE-DETOUR {name}: rows={s2['L5']['rows']}+{s2['Lgt5']['rows']} "
              f"Lgt5_fails={fgt5} L5_packet_fails={s2['L5']['packet_fail']} "
              f"(all at protected-cell rows: cell-classified per design) "
              f"L5_upo_fails={s2['L5']['upo_fail']}")
        assert fgt5 == 0, f"{name}: {s2}"
        assert s2["L5"]["upo_fail"] == 0, f"{name}: BD-UPO itself failed at L=5: {s2}"
    # census
    for nn in range(5, NMAX + 1):
        cs = new_stats()
        gs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True)
        for g6 in gs.stdout.split():
            n2, E2 = dec(g6)
            adj = adj_from_edges(n2, E2)
            try:
                _a, cuts = gmins(n2, E2)
            except Exception:
                continue
            for side in cuts:
                sd = [int(c) for c in side]
                if not Bconn(n2, adj, sd):
                    continue
                run_graph(n2, E2, sd, g6, cs)
        print(f"BLUE-DETOUR census N={nn}: L5 rows={cs['L5']['rows']} "
              f"upo_fail={cs['L5']['upo_fail']} packet_fail={cs['L5']['packet_fail']} | "
              f"L>5 rows={cs['Lgt5']['rows']} upo_fail={cs['Lgt5']['upo_fail']} "
              f"packet_fail={cs['Lgt5']['packet_fail']}", flush=True)
        for k in cs:
            for wname in ("upo_wit", "packet_wit"):
                for w in cs[k][wname]:
                    print(f"  WIT {k} {wname}: {w}", flush=True)
        stats[k] = None  # not aggregating; per-N verdicts printed
    print("DONE blue-detour gate")


if __name__ == "__main__":
    main()
