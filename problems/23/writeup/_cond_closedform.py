"""EXACT (Fraction) test of CLOSED-FORM conductance choices c_{Q,e} for the two-condition certificate:
   (Local-SOS)   S_Q(c) = L*D_Q - q_Q q_Q^T - L_{Q,c} >= 0  (on Q's L vertices)
   (Global-Hardy) GH(c) = D_{N-T} + sum_{f,Q}(1/|cyc[f]|) L_{Q,c} >= 0
Both PSD => (H).  We test several explicit c-rules on the focused battery incl N=23.

Rules tested (c as function of cycle Q, edge index i, length L, deficits R):
  'uniform_beta'   c = beta_L'         (rational beta', the KNOWN tight Local-SOS; GH=(H))
  'unit'           c = 1               (integer conductance)
  'beta_minus_eps' c = beta_L' (control, identical to uniform_beta)
  'cap_min_pos'    c = min(beta_L', ...) experimental
We report, for each rule: Local-SOS fails, Global-Hardy fails, exact min pivots, tightness.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski
from _csmspec import is_psd
from _hardy_gate import BETA

def cycle_edges(Q):
    L = len(Q)
    return [(Q[i], Q[(i + 1) % L]) for i in range(L)]

def local_sos(Q, cvec):
    """S_Q = L*D_Q - q q^T - sum_i cvec[i]*edge_lap_i, on L vertices in cycle order. cvec aligned to cycle_edges."""
    L = len(Q)
    S = [[F(0)] * L for _ in range(L)]
    for i in range(L):
        S[i][i] += F(L)
    for i in range(L):
        for j in range(L):
            S[i][j] -= F(1)
    for i in range(L):
        a, b = i, (i + 1) % L
        ci = cvec[i]
        S[a][a] -= ci; S[b][b] -= ci; S[a][b] += ci; S[b][a] += ci
    return S

def build_GH(n, M, ell, T, cyc, crule):
    """GH = diag(N-T) + sum_{f,Q}(1/|cyc[f]|) sum_i c_i (e_a-e_b)(e_a-e_b)^T."""
    N = F(n)
    GH = [[F(0)] * n for _ in range(n)]
    for v in range(n):
        GH[v][v] = N - T[v]
    R = {v: N - T[v] for v in range(n)}
    for f in M:
        Qs = cyc[f]; L = ell[f]; w = F(1, len(Qs))
        for Q in Qs:
            ce = cycle_edges(Q)
            cvec = crule(Q, ce, L, R)
            for i, (a, b) in enumerate(ce):
                ci = w * cvec[i]
                GH[a][a] += ci; GH[b][b] += ci; GH[a][b] -= ci; GH[b][a] -= ci
    return GH

# ---- closed-form rules ----
def rule_uniform_beta(Q, ce, L, R):
    return [BETA[L]] * L

def rule_unit(Q, ce, L, R):
    return [F(1)] * L

def rule_two_unit_alt(Q, ce, L, R):
    # experimental: c=2 on edges with an overloaded (R<0) endpoint, 1 elsewhere -- mirrors SDP corner
    out = []
    for (a, b) in ce:
        if R[a] < 0 or R[b] < 0:
            out.append(F(2))
        else:
            out.append(F(1))
    return out

RULES = {
    'uniform_beta': rule_uniform_beta,
    'unit': rule_unit,
    'two_if_over': rule_two_unit_alt,
}

def gate(name, n, adj, side, accmap):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    R = {v: F(n) - T[v] for v in range(n)}
    for rname, crule in RULES.items():
        acc = accmap[rname]
        acc['cuts'] += 1
        # Local-SOS per cycle
        for f in M:
            for Q in cyc[f]:
                if len(set(Q)) != len(Q):
                    continue
                ce = cycle_edges(Q)
                cvec = crule(Q, ce, ell[f], R)
                S = local_sos(Q, cvec)
                psd, mp = is_psd(S)
                if not psd:
                    acc['local_fail'] += 1
                    if acc['local_ex'] is None:
                        acc['local_ex'] = (name, n, tuple(Q), str(mp))
                else:
                    if mp == 0:
                        acc['local_tight'] += 1
                    if acc['local_minpiv'] is None or mp < acc['local_minpiv']:
                        acc['local_minpiv'] = mp
        # Global-Hardy
        GH = build_GH(n, M, ell, T, cyc, crule)
        psd, mp = is_psd(GH)
        if not psd:
            acc['global_fail'] += 1
            if acc['global_ex'] is None:
                acc['global_ex'] = (name, n, str(mp))
        else:
            if acc['global_minpiv'] is None or mp < acc['global_minpiv']:
                acc['global_minpiv'] = mp

def newacc():
    return dict(cuts=0, local_fail=0, local_tight=0, local_minpiv=None, local_ex=None,
                global_fail=0, global_minpiv=None, global_ex=None)

def main():
    accmap = {r: newacc() for r in RULES}

    cases = []
    cases.append(("HAFBo_N9", *dec("H?AFBo]")))
    cases.append(("C5x2_N10", *odd_blowup(5, [2, 2, 2, 2, 2])))
    cases.append(("C5x3_N15_TIGHT", *odd_blowup(5, [3, 3, 3, 3, 3])))
    cases.append(("C5_21212_N8", *odd_blowup(5, [2, 1, 2, 1, 2])))
    cases.append(("C5_32323_N13", *odd_blowup(5, [3, 2, 3, 2, 3])))
    # two census graphs N=8, N=9
    for g6 in subprocess.run([GENG, '-tc', '8'], capture_output=True, text=True).stdout.split()[:2]:
        cases.append(("cen8_" + g6, *dec(g6)))
    for g6 in subprocess.run([GENG, '-tc', '9'], capture_output=True, text=True).stdout.split()[:2]:
        cases.append(("cen9_" + g6, *dec(g6)))

    for name, n, E in cases:
        adj, cuts = gmins(n, E)
        for side in cuts:
            gate(name, n, adj, side, accmap)

    # N=23 guardrail
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj23 = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj23[x].add(y); adj23[y].add(x)
    rng = random.Random(9); best = None; bv = -1
    for _ in range(80):
        s = [rng.randint(0, 1) for _ in range(m2N)]; imp = True
        while imp:
            imp = False
            for v in range(m2N):
                if sum(1 for w in adj23[v] if s[w] == s[v]) > sum(1 for w in adj23[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(m2N) for w in adj23[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    gate("MycGrotzsch_N23", m2N, adj23, best, accmap)

    print("=" * 70)
    for rname in RULES:
        acc = accmap[rname]
        print(f"\nRULE '{rname}':  cuts={acc['cuts']}")
        print(f"   Local-SOS  fails={acc['local_fail']}  tight={acc['local_tight']}  "
              f"min_pivot={acc['local_minpiv']}  ex={acc['local_ex']}")
        print(f"   Global-Hardy fails={acc['global_fail']}  min_pivot={acc['global_minpiv']}  ex={acc['global_ex']}")
        verdict = "BOTH PSD 0-FAIL => proves (H)" if acc['local_fail'] == 0 and acc['global_fail'] == 0 else "FAILS"
        print(f"   VERDICT: {verdict}")

if __name__ == "__main__":
    main()
