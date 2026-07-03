"""Overfull-scoped blue-detour check, N<=11 census L>5 rows:
restricted to rows with R_Q > N (the only rows where Banked-UPO needs more
than Bank-L), verify (BD-UPO) U_Q^+ <= eta/2 - Sigma_L and (BD+) packet.
Also count: overfull rows total, underfull failures discarded."""
import sys, contextlib, io, subprocess
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec, GENG, Bconn
    from _satzmu_conn import struct_for_side, kcomponents
    from _stark1 import gmins
    from _codex_schur_ec_gate import adj_from_edges
    import _claude_blue_detour_gate as BD
from fractions import Fraction as F

for nn in range(7, 12):
    t = {"rows": 0, "overfull": 0, "upo_fail": 0, "packet_fail": 0, "wit": []}
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
            st = struct_for_side(n2, adj, sd)
            if st is None or not st[0]:
                continue
            M, ell, T, mu, cyc = st
            m_all = sum(1 for u, v in E2 if sd[u] == sd[v])
            eta = F(n2 * n2, 25) - m_all
            comp, find = kcomponents(n2, cyc)
            Mc = {}
            for f in M:
                Mc.setdefault(find(f[0]), []).append(f)
            for c, Ms in Mc.items():
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
                        t["rows"] += 1
                        R_Q = sum(tw.get(v, F(0)) for v in set(Q))
                        if R_Q <= n2:
                            continue
                        t["overfull"] += 1
                        sigma_L = F(L * L - 25, 50)
                        bank = eta / 2 - sigma_L
                        comps = BD.components_minus_row(n2, E2, sd, tuple(Q))
                        U = F(0)
                        W = set(Q)
                        for K in comps:
                            tt = sum(tw.get(v, F(0)) for v in set(Q) & K)
                            if tt - len(K) > 0:
                                U += tt - len(K)
                                W |= K
                        if U > bank:
                            t["upo_fail"] += 1
                            if len(t["wit"]) < 5:
                                t["wit"].append(("UPO", g6, f, tuple(Q), U, bank))
                        r = n2 - len(W)
                        p = sum(1 for u, v in E2 if sd[u] == sd[v] and u in W and v in W)
                        h = sum(1 for u, v in E2 if sd[u] == sd[v] and (u in W) != (v in W))
                        d = sum(1 for u, v in E2 if sd[u] != sd[v] and (u in W) != (v in W))
                        BW = F(n2 * n2 - r * r, 25) - p - F(d + h, 2)
                        if 2 * (U + sigma_L) > BW:
                            t["packet_fail"] += 1
                            if len(t["wit"]) < 5:
                                t["wit"].append(("PKT", g6, f, tuple(Q), U, BW))
    print(f"N={nn}: L>5 rows={t['rows']} OVERFULL={t['overfull']} "
          f"upo_fail={t['upo_fail']} packet_fail={t['packet_fail']}", flush=True)
    for w in t["wit"]:
        print("  WIT:", w, flush=True)
