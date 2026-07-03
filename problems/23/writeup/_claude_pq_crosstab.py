"""Claude P_Q sign cross-tab (pressure identity, BANKL addendum 4).
Per L>5 row: bare row packet W = V(Q): p = e_M(W), h = |dM(W)|, d = |dB(W)|, r = N-L;
  P_Q = 25(p-1) + 25(d+h)/2 - 2Lr        [pressure; Bank-L <=> rho_Q >= P_Q]
  rho_Q = 25*(eta - ((N^2-r^2)/25 - p - (d+h)/2))   [packet exchange residual >= 0]
Verify the identity -Delta_Q = (2Lr - 25(p-1) - 25(d+h)/2) + rho_Q exactly per row.
Cross-tab by scope (underfull/equal/overfull) x sign(P_Q); collect the P_Q>0 hard set
with structure (n, L, p, h, d, r, P_Q, rho_Q, margin rho-P).
Census N=7..11 all gamma-min B-connected cuts + C-cycles + two-lane p198."""
import sys, contextlib, io, subprocess
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec, GENG, Bconn
    from _satzmu_conn import struct_for_side, kcomponents
    from _stark1 import gmins
    from _codex_schur_ec_gate import adj_from_edges
    import _claude_nocell_pu_gate as NPG
from fractions import Fraction as F
from collections import Counter

tab = Counter()
hard = []
ident_fail = 0
rows = 0


def process(n, edges, sd, Ms, cyc, label):
    global ident_fail, rows
    m_all = sum(1 for u, v in edges if sd[u] == sd[v])
    eta = F(n * n, 25) - m_all
    tw = {}
    for g in Ms:
        mm = len(cyc[g])
        cnt2 = {}
        for P in cyc[g]:
            for v in set(P):
                cnt2[v] = cnt2.get(v, 0) + 1
        for v, cc in cnt2.items():
            tw[v] = tw.get(v, F(0)) + F(cc, mm)
    for f in Ms:
        for Q in cyc[f]:
            L = len(set(Q))
            if L <= 5:
                continue
            rows += 1
            W = set(Q)
            r = n - L
            p = sum(1 for u, v in edges if sd[u] == sd[v] and u in W and v in W)
            h = sum(1 for u, v in edges if sd[u] == sd[v] and (u in W) != (v in W))
            d = sum(1 for u, v in edges if sd[u] != sd[v] and (u in W) != (v in W))
            P_Q = F(25 * (p - 1)) + F(25 * (d + h), 2) - 2 * L * r
            rho = 25 * (eta - (F(n * n - r * r, 25) - p - F(d + h, 2)))
            Delta = 25 * m_all + L * L - 25 - n * n
            lhs = (2 * L * r - 25 * (p - 1) - F(25 * (d + h), 2)) + rho
            if lhs != -Delta:
                ident_fail += 1
            assert rho >= 0, f"{label}: rho<0!"
            R_Q = sum(tw.get(v, F(0)) for v in set(Q))
            scope = "overfull" if R_Q > n else ("equal" if -Delta == 0 else "underfull")
            sign = "P>0" if P_Q > 0 else ("P=0" if P_Q == 0 else "P<0")
            tab[f"{scope}:{sign}"] += 1
            if P_Q > 0 and len(hard) < 40:
                hard.append((label, n, L, p, h, d, r, str(P_Q), str(rho), str(rho - P_Q)))


def run_graph(n, edges, side, label):
    adj = adj_from_edges(n, edges)
    sd = list(side)
    st = struct_for_side(n, adj, sd)
    if st is None or not st[0]:
        return
    M, ell, T, mu, cyc = st
    comp, find = kcomponents(n, cyc)
    Mc = {}
    for f in M:
        Mc.setdefault(find(f[0]), []).append(f)
    for c, Ms in Mc.items():
        process(n, edges, sd, Ms, cyc, label)


for L in (7, 9, 11):
    edges = [tuple(sorted((i, (i + 1) % L))) for i in range(L)]
    run_graph(L, edges, [i % 2 for i in range(L)], f"C{L}")
n, edges, side = NPG.build_two_lane_p198()
run_graph(n, edges, side, "two-lane")
for nn in range(7, 12):
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
            run_graph(n2, E2, sd, g6)
    print(f"N={nn} done: rows={rows} tab={dict(tab)} ident_fail={ident_fail}", flush=True)
print("FINAL:", dict(sorted(tab.items())), "ident_fail:", ident_fail, "rows:", rows)
for hh in hard:
    print("HARD:", hh)
