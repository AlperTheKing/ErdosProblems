"""Classify the 71 N=11 L>5 (BD-UPO) failures:
  (a) does Banked-UPO itself hold there (R_Q - N <= eta/2 - Sigma_L)?
  (b) is the failing row's positive component carrying another bad edge's
      structure (cell/atom proxy: positive component contains >=1 other bad
      edge entirely, or intersects another bad edge's rows)?
Verdict semantics: if Banked-UPO holds on all 71 -> decomposition lossiness
(cell-residual territory; architecture intact). Any Banked-UPO violation ->
genuine counterexample to the Branch-B strengthening -> escalate immediately.
"""
import sys, contextlib, io, subprocess
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec, GENG, Bconn
    from _satzmu_conn import struct_for_side, kcomponents
    from _stark1 import gmins
    from _codex_schur_ec_gate import adj_from_edges
    import _claude_blue_detour_gate as BD
from fractions import Fraction as F

tally = {"fails": 0, "banked_ok": 0, "banked_viol": 0, "poscomp_hits_other_bad": 0,
         "banked_viol_wit": [], "sample": []}
nn = 11
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
                    sigma_L = F(L * L - 25, 50)
                    bank = eta / 2 - sigma_L
                    comps = BD.components_minus_row(n2, E2, sd, tuple(Q))
                    U = F(0)
                    pos = []
                    for K in comps:
                        t = sum(tw.get(v, F(0)) for v in set(Q) & K)
                        if t - len(K) > 0:
                            U += t - len(K)
                            pos.append(K)
                    if U <= bank:
                        continue
                    tally["fails"] += 1
                    R_Q = sum(tw.get(v, F(0)) for v in set(Q))
                    banked = R_Q - n2 <= bank
                    if banked:
                        tally["banked_ok"] += 1
                    else:
                        tally["banked_viol"] += 1
                        if len(tally["banked_viol_wit"]) < 10:
                            tally["banked_viol_wit"].append(
                                (g6, side, f, tuple(Q), R_Q, n2 + bank))
                    hit = False
                    for K in pos:
                        for g in Ms:
                            if g != f and g[0] in K and g[1] in K:
                                hit = True
                    if hit:
                        tally["poscomp_hits_other_bad"] += 1
                    if len(tally["sample"]) < 5:
                        tally["sample"].append(
                            (g6, f, tuple(Q), U, bank, R_Q - n2, hit))
print(f"N=11 L>5 BD-UPO failures={tally['fails']} | Banked-UPO holds={tally['banked_ok']} "
      f"VIOLATIONS={tally['banked_viol']} | poscomp contains other bad edge="
      f"{tally['poscomp_hits_other_bad']}")
for w in tally["banked_viol_wit"]:
    print("BANKED-VIOL:", w)
for w in tally["sample"]:
    print("SAMPLE:", w)
