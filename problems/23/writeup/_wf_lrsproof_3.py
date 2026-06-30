"""LRS algebraic-proof validation harness (EXACT Fraction).

Target LRS:  sum_v T(v)^2 <= Gamma * (N + N^2/25 - m),   Gamma=sum ell_f^2, m=|M|, N=n.

Algebra:  P[v,f]=p_f(v) (frac of f's geodesics through v).  T = P ell  (T(v)=sum_f ell_f p_f(v)).
  O = P^T P  (m x m).   sum_v T^2 = T^T T = ell^T O ell.
  O_ff = ||p_f||^2 = sum_v p_f(v)^2  in (0, ell_f].
  (O ell)_f = sum_v p_f(v) T(v) = ell_f * A_f   (row sum weighted).
  trace(O) = sum_f O_ff.   1^T O 1 = sum_v (sum_f p_f(v))^2.

This script:
 1. Builds P,O exactly for every config on the standing gate.
 2. Validates the elementary identities (sum T^2 = ell^T O ell, etc.) EXACTLY.
 3. Tests a sequence of candidate sub-lemmas for an algebraic LRS proof and
    HUNTS counterexamples on census gamma-min N<=11, two-lane, Mycielskians, blow-ups.
 4. Reports, for each sub-lemma, exact min margin + first violation.

A sub-lemma is "proof-grade" only if it (a) holds exactly on the WHOLE battery and
(b) chains to LRS WITHOUT assuming Erdos / m<=N^2/25 / the target.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane

def build_PO(n, adj, side):
    """Return (M, ell list, T list, P dict[f]->{v:frac}, O matrix) exactly, or None."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    P = {}
    for f in M:
        k = len(cyc[f]); d = {}
        for Pp in cyc[f]:
            for v in Pp: d[v] = d.get(v, F(0)) + F(1, k)
        P[f] = d
    m = len(M)
    O = [[F(0)]*m for _ in range(m)]
    for i, f in enumerate(M):
        for j, g in enumerate(M):
            if j < i:
                O[i][j] = O[j][i]; continue
            common = set(P[f]) & set(P[g])
            O[i][j] = sum(P[f][v]*P[g][v] for v in common)
    ellv = [ell[f] for f in M]
    return M, ellv, [T[v] for v in range(n)], P, O

def configs():
    """Yield (name, n, adj, side) over the standing gate."""
    def adj_of(n, E):
        a = [set() for _ in range(n)]
        for x, y in E: a[x].add(y); a[y].add(x)
        return a
    # two-lane
    for L in range(8, 21, 2):
        n, E, side, _ = build_two_lane(L)
        yield ("two-lane-L%d" % L, n, adj_of(n, E), side)
    # census gamma-min N<=11
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); adj, cuts = gmins(n, E)
            for s in cuts:
                yield ("cen%s" % g6, n, adj, s)
    # blow-ups (uniform + non-uniform), gmins-feasible N<=26
    def blowup(parts):
        mm = len(parts); off = [0]*(mm+1)
        for i in range(mm): off[i+1] = off[i]+parts[i]
        nn = off[mm]; EE = []
        for i in range(mm):
            j = (i+1) % mm
            for a in range(off[i], off[i+1]):
                for b in range(off[j], off[j+1]): EE.append((min(a, b), max(a, b)))
        return nn, sorted(set(EE))
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t]*cyc)
            if n > 26: continue
            adj, cuts = gmins(n, E)
            if cuts: yield ("C%d[%d]" % (cyc, t), n, adj, cuts[0])
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,2,3,2,2,3,2]]:
        n, E = blowup(parts)
        if n > 26: continue
        adj, cuts = gmins(n, E)
        if cuts: yield ("nu%s" % parts, n, adj, cuts[0])
    # Mycielskians
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
                          ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9)))]:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]: yield (name, nn, adj, s)


# ---- candidate sub-lemmas ----
# Each returns dict of named (lhs<=rhs) margins; margin = rhs - lhs (>=0 wanted).

def lemmas(n, M, ell, T, P, O):
    m = len(M); N = F(n)
    Gamma = sum(e*e for e in ell)
    sumT2 = sum(t*t for t in T)
    res = {}
    # identity checks (margin should be exactly 0)
    ellTOell = sum(ell[i]*O[i][j]*ell[j] for i in range(m) for j in range(m))
    res['ID:sumT2=ellTOell'] = sumT2 - ellTOell           # ==0
    # row-sum identity (O ell)_f = ell_f A_f, A_f=sum_v p_f(v)T(v)/ell_f
    for i, f in enumerate(M):
        Oell_i = sum(O[i][j]*ell[j] for j in range(m))
        Af_times_ell = sum(P[f][v]*T[v] for v in P[f])
        res['ID:Oell_row'] = (res.get('ID:Oell_row', F(0))) + abs(Oell_i - Af_times_ell)
    # ---- the TARGET ----
    res['LRS'] = Gamma*(N + N*N/25 - m) - sumT2
    # ---- candidate building blocks ----
    # (a) diagonal bound: O_ff <= ell_f  (always true; p_f(v)<=1 and sum p_f = ell_f)
    res['Odiag<=ell'] = min((ell[i]-O[i][i] for i in range(m)), default=F(1))
    # (b) trace(O) <= Gamma  (sum O_ff <= sum ell_f)? NO -- want vs Gamma. test both.
    trO = sum(O[i][i] for i in range(m))
    res['trO<=sum_ell'] = sum(ell) - trO
    res['trO<=Gamma'] = Gamma - trO
    # (c) Rayleigh: sumT2 = ellTOell <= rho(O) * Gamma. We want a usable rho bound.
    #     PSD => sumT2 <= rho * Gamma. The DEAD route claimed rho<=N. Test rho vs N+N^2/25-m.
    Of = [[float(x) for x in r] for r in O]
    import numpy as np
    rho = float(max(np.linalg.eigvalsh(np.array(Of)))) if m else 0.0
    res['_rho'] = rho
    res['_N+N2/25-m'] = float(N + N*N/25 - m)
    # (d) Schur/Gershgorin-type: ellTOell <= sum_i ell_i (O ell)_i = sum_i ell_i^2 A_i.
    #     This is exact equality (ellTOell = sum_i ell_i (Oell)_i). So sumT2 = sum_i ell_i^2 A_i.
    rowweighted = sum(ell[i]*sum(O[i][j]*ell[j] for j in range(m)) for i in range(m))
    res['ID:sumT2=sum_ell2_A'] = sumT2 - rowweighted   # ==0
    # (e) ROW-LRS per-edge:  A_f + m <= N + N^2/25, A_f = (Oell)_f/ell_f
    rowlrs_min = None
    for i in range(m):
        Af = sum(O[i][j]*ell[j] for j in range(m)) / ell[i]
        marg = (N + N*N/25 - m) - Af
        rowlrs_min = marg if rowlrs_min is None else min(rowlrs_min, marg)
    res['ROW-LRS'] = rowlrs_min if rowlrs_min is not None else F(1)
    # (f) KEY tempting sub-lemma toward LRS via Cauchy-Schwarz on rows:
    #     sumT2 = sum_i ell_i^2 A_i <= (max_i A_i) * Gamma.  If max A_i <= N+N^2/25-m => LRS.
    #     i.e. ROW-LRS => LRS. (chain check). max A_i:
    maxA = max((sum(O[i][j]*ell[j] for j in range(m))/ell[i] for i in range(m)), default=F(0))
    res['_maxA'] = float(maxA)
    res['ROW-LRS=>LRS chain'] = Gamma*(N+N*N/25-m) - maxA*Gamma  # >=0 iff maxA<=N+N2/25-m
    res['_Gamma'] = Gamma; res['_m'] = m; res['_sumT2'] = sumT2
    res['_maxT'] = max(T); res['_N'] = n
    return res

if __name__ == "__main__":
    print("=== LRS algebraic-proof validation (EXACT) ===", flush=True)
    keys = ['ID:sumT2=ellTOell', 'ID:Oell_row', 'ID:sumT2=sum_ell2_A',
            'Odiag<=ell', 'trO<=sum_ell', 'trO<=Gamma',
            'LRS', 'ROW-LRS', 'ROW-LRS=>LRS chain']
    agg = {k: {'min': F(10**12), 'minname': None, 'viol': 0, 'first': None} for k in keys}
    ntot = 0
    rho_excess_max = (-10.0, None)   # max of (rho - (N+N2/25-m))
    for name, n, adj, side in configs():
        if not Bconn(n, adj, side): continue
        po = build_PO(n, adj, side)
        if po is None: continue
        M, ell, T, P, O = po
        L = lemmas(n, M, ell, T, P, O)
        ntot += 1
        for k in keys:
            v = L[k]
            if v < agg[k]['min']: agg[k]['min'] = v; agg[k]['minname'] = name
            if v < 0:
                agg[k]['viol'] += 1
                if agg[k]['first'] is None:
                    agg[k]['first'] = (name, n, L['_m'], str(L['_Gamma']), str(L['_sumT2']))
        rex = L['_rho'] - L['_N+N2/25-m']
        if rex > rho_excess_max[0]:
            rho_excess_max = (rex, (name, n, L['_m'], round(L['_rho'], 4), round(L['_N+N2/25-m'], 4), round(L['_maxA'], 4)))
    print("  configs tested = %d" % ntot, flush=True)
    for k in keys:
        a = agg[k]
        flag = "EXACT-0" if (k.startswith('ID:') and a['min'] == 0 and a['viol'] == 0) else ("HOLDS" if a['viol'] == 0 else "VIOLATED")
        print("  %-22s min=%s  viol=%d  at=%s  %s" % (k, str(a['min'])[:30], a['viol'], a['minname'], flag), flush=True)
        if a['first']: print("      first viol: %s" % (a['first'],), flush=True)
    print("  rho(O) - (N+N^2/25-m): max excess = %.4f at %s" % rho_excess_max, flush=True)
