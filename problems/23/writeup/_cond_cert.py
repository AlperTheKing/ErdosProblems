"""ANGLE: explicit per-edge CONDUCTANCE certificate for (H)  D_{N-T}+Lstar >= 0.

Per shortest odd cycle Q (length L=ell), pick conductances c_{Q,e}>=0 on its L edges. Define
    L_{Q,c} = sum_{e=ab in E(Q)} c_{Q,e} (e_a-e_b)(e_a-e_b)^T   (weighted cycle Laplacian).
TWO conditions:
  (Local-SOS)   S_Q(c) := L*D_Q - q_Q q_Q^T - L_{Q,c}  >= 0   for every Q.
  (Global-Hardy) GH(c) := D_{N-T} + sum_{f,Q} (1/|cyc[f]|) L_{Q,c}  >= 0.
If both hold:  K2 = sum (1/|cyc[f]|) q_Q q_Q^T <= D_T - sum (1/|cyc[f]|) L_{Q,c} <= N*I  => (H).
[Proof of the chain: Local-SOS => q_Q q_Q^T <= L*D_Q - L_{Q,c}; average with weight (1/|cyc[f]|) and use
 sum_{f,Q}(1/|cyc[f]|) L*D_Q = D_T (since sum over Q in cyc[f] of L*1_Q averaged = ell[f]*frac = T contributions);
 so K2 <= D_T - sum(1/|cyc[f]|)L_{Q,c}; then N*I - K2 >= D_{N-T} + sum(1/|cyc[f]|)L_{Q,c} = GH(c) >= 0.]

UNIFORM choice c_{Q,e}=beta_L reproduces Lstar exactly: GH = (H) (already validated), and Local-SOS becomes the
PROVEN per-cycle Poincare (max eig of L_Q on 1-perp = 2+2cos(pi/L), so S_Q = L*D_Q - q q^T - beta_L L_Q has min eig 0).

This script:
 (1) verifies uniform Local-SOS S_Q >= 0 EXACT (and that it is TIGHT, min pivot 0) on the focused battery;
 (2) verifies uniform GH = (H) exact (sanity, reuses _hardy_gate build);
 (3) SDP-optimizes c_{Q,e} (cvxpy) maximizing min-eig of GH s.t. Local-SOS, on C5[3]/H?AFBo]/census N=9,
     and inspects whether optimal c are constant / proportional to a local quantity;
 (4) tests CLOSED-FORM guesses for c exactly (Fraction is_psd) on the full focused battery incl N=23.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski
from _csmspec import is_psd
from _hardy_gate import BETA, build_H

import numpy as np
import math

# ----------------------------------------------------------------------------
# cycle edge list: cycle Q is a list of vertices [v0,v1,...,v_{L-1}], edges v_i-v_{i+1 mod L}
def cycle_edges(Q):
    L = len(Q)
    return [(Q[i], Q[(i + 1) % L]) for i in range(L)]

def edge_lap_outer(n, a, b):
    """(e_a-e_b)(e_a-e_b)^T as nxn list (Fraction)."""
    Mx = [[F(0)] * n for _ in range(n)]
    Mx[a][a] += 1; Mx[b][b] += 1; Mx[a][b] -= 1; Mx[b][a] -= 1
    return Mx

# ----------------------------------------------------------------------------
# (1) uniform Local-SOS:  S_Q = L*D_Q - q_Q q_Q^T - beta_L * L_Q   (restricted to vertices of Q)
def local_sos_uniform(Q, beta):
    """Build S_Q on the L vertices of Q (in cycle order). Exact Fraction. Returns LxL matrix."""
    L = len(Q)
    idx = {v: i for i, v in enumerate(Q)}  # Q may repeat? geodesic cycles are simple; assume distinct
    S = [[F(0)] * L for _ in range(L)]
    # L*D_Q  (D_Q = I on Q's vertices)
    for i in range(L):
        S[i][i] += F(L)
    # - q_Q q_Q^T  (all-ones on Q)
    for i in range(L):
        for j in range(L):
            S[i][j] -= F(1)
    # - beta * L_Q  (cycle Laplacian)
    for i in range(L):
        a, b = i, (i + 1) % L
        S[a][a] -= beta; S[b][b] -= beta; S[a][b] += beta; S[b][a] += beta
    return S

# ----------------------------------------------------------------------------
def collect_cycles(n, M, ell, cyc):
    """Return list of (weight_frac, Q_vertex_list) over all shortest cycles, weight = 1/|cyc[f]|."""
    out = []
    for f in M:
        Qs = cyc[f]; w = F(1, len(Qs))
        for Q in Qs:
            out.append((w, list(Q)))
    return out

# ----------------------------------------------------------------------------
# uniform-conductance exact gate (Local-SOS tightness + GH=(H))
def gate_uniform(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    acc['cuts'] += 1
    # Local-SOS per cycle (uniform beta)
    for f in M:
        beta = BETA[ell[f]]
        for Q in cyc[f]:
            if len(set(Q)) != len(Q):
                acc['nonsimple'] += 1
                continue
            S = local_sos_uniform(Q, beta)
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
    # Global-Hardy = (H) via the proven build_H (rational beta')
    H = build_H(n, M, ell, T, cyc, BETA)
    psd, mp = is_psd(H)
    if not psd:
        acc['global_fail'] += 1
        if acc['global_ex'] is None:
            acc['global_ex'] = (name, n, str(mp))

# ----------------------------------------------------------------------------
# (3) SDP optimization of c_{Q,e}: maximize t s.t. GH(c) >= t I, S_Q(c) >= 0 all Q, c>=0.
def sdp_optimize(name, n, adj, side, verbose=True):
    import cvxpy as cp
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    # enumerate all cycles with weights; assign a variable vector c per cycle (one per edge)
    cyclist = []  # (fweight, Q, edge_list)
    for f in M:
        w = F(1, len(cyc[f]))
        for Q in cyc[f]:
            cyclist.append((float(w), list(Q), cycle_edges(Q)))
    nvars = sum(len(ce) for _, _, ce in cyclist)
    cvar = cp.Variable(nvars, nonneg=True)
    # GH = diag(N-T) + sum_cyc fweight * sum_e c_e (e_a-e_b)(e_a-e_b)^T
    GH = cp.diag(np.array([float(n) - float(T[v]) for v in range(n)]))
    constraints = []
    pos = 0
    Sblocks = []
    for fw, Q, ce in cyclist:
        L = len(Q)
        beta = float(ell_to_beta(ell_of(Q, ce)))  # not used; recompute below
        # build local SOS on Q's vertices
        idx = {v: i for i, v in enumerate(Q)}
        # S_Q = L*I - J - sum_e c_e (local edge lap)  on L-dim
        Sloc = float(L) * np.eye(L) - np.ones((L, L))
        for k, (a, b) in enumerate(ce):
            ce_var = cvar[pos + k]
            ia, ib = idx[a], idx[b]
            # subtract c_e * (e_ia - e_ib)(...)^T
            Eab = np.zeros((L, L)); Eab[ia, ia] = 1; Eab[ib, ib] = 1; Eab[ia, ib] = -1; Eab[ib, ia] = -1
            Sloc = Sloc - ce_var * Eab
            # add to GH (full n-dim)
            En = np.zeros((n, n)); En[a, a] = 1; En[b, b] = 1; En[a, b] = -1; En[b, a] = -1
            GH = GH + fw * ce_var * En
        constraints.append(Sloc >> 0)
        Sblocks.append((Q, ce, pos))
        pos += L
    t = cp.Variable()
    constraints.append(GH - t * np.eye(n) >> 0)
    prob = cp.Problem(cp.Maximize(t), constraints)
    try:
        prob.solve(solver=cp.SCS, eps=1e-9, max_iters=200000)
    except Exception as e:
        if verbose:
            print(f"  SDP solve error {name}: {e}")
        return None
    if cvar.value is None:
        if verbose:
            print(f"  SDP no solution {name} status={prob.status}")
        return None
    cval = cvar.value
    if verbose:
        print(f"\n=== SDP-optimal c for {name} (N={n}) status={prob.status} t*={t.value:.6f} ===")
        for Q, ce, p in Sblocks:
            L = len(Q)
            betaL = float(ell_to_beta(L))
            vals = [cval[p + k] for k in range(L)]
            print(f"  cycle Q={Q} (L={L}, beta_L={betaL:.4f}):")
            for k, (a, b) in enumerate(ce):
                print(f"     edge {a}-{b}: c={vals[k]:.5f}  (uniform beta_L={betaL:.4f})")
    return dict(M=M, ell=ell, T=T, cyc=cyc, cval=cval, Sblocks=Sblocks, t=float(t.value) if t.value is not None else None)

def ell_to_beta(L):
    return F(L) / (2 + 2 * cos_rat(L))

def cos_rat(L):
    # exact-ish rational cos via BETA inverse not needed; just float for SDP display
    return F(int(round(math.cos(math.pi / L) * 10**12)), 10**12)

def ell_of(Q, ce):
    return len(Q)

# ----------------------------------------------------------------------------
def main():
    print("beta_5' =", float(BETA[5]), "beta_7' =", float(BETA[7]), "beta_9' =", float(BETA[9]))
    acc = dict(cuts=0, local_fail=0, local_tight=0, local_minpiv=None, local_ex=None, nonsimple=0,
               global_fail=0, global_ex=None)

    # ---- focused battery ----
    cases = []
    # H?AFBo] N=9 Gamma=50
    n, E = dec("H?AFBo]"); cases.append(("HAFBo_N9", n, E))
    # C5[2] N=10, C5[3] N=15 (tight)
    n, E = odd_blowup(5, [2, 2, 2, 2, 2]); cases.append(("C5x2_N10", n, E))
    n, E = odd_blowup(5, [3, 3, 3, 3, 3]); cases.append(("C5x3_N15_TIGHT", n, E))
    # two census N=8/9 graphs (first triangle-free connected with a bad edge)
    cN8 = subprocess.run([GENG, '-tc', '8'], capture_output=True, text=True).stdout.split()[:1]
    cN9 = subprocess.run([GENG, '-tc', '9'], capture_output=True, text=True).stdout.split()[:1]
    for g6 in cN8:
        n, E = dec(g6); cases.append(("cen8_" + g6, n, E))
    for g6 in cN9:
        n, E = dec(g6); cases.append(("cen9_" + g6, n, E))

    # ---- (1)+(2) uniform exact gate over ALL gamma-min cuts of these cases ----
    print("\n--- (1)+(2) UNIFORM conductance c=beta_L: Local-SOS + Global-Hardy exact gate ---")
    for name, n, E in cases:
        adj, cuts = gmins(n, E)
        for side in cuts:
            gate_uniform(name, n, adj, side, acc)
    # Myc(Grotzsch) N=23 guardrail (one max cut)
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
    gate_uniform("MycGrotzsch_N23", m2N, adj23, best, acc)

    print(f"cuts tested: {acc['cuts']}")
    print(f"Local-SOS (uniform) FAILS: {acc['local_fail']}  ex={acc['local_ex']}")
    print(f"Local-SOS TIGHT (min pivot 0) cycles: {acc['local_tight']}  global min local pivot: {acc['local_minpiv']}")
    print(f"non-simple cycles skipped: {acc['nonsimple']}")
    print(f"Global-Hardy=(H) FAILS: {acc['global_fail']}  ex={acc['global_ex']}")

    # ---- (3) SDP optimum for the tight/key cases ----
    print("\n--- (3) SDP-optimal conductances (cvxpy/SCS) ---")
    for name, n, E in [("C5x3_N15_TIGHT", *dec("never")) if False else ("HAFBo_N9", *dec("H?AFBo]"))]:
        adj, cuts = gmins(n, E)
        sdp_optimize(name, n, adj, cuts[0])
    for sizes, nm in [([3, 3, 3, 3, 3], "C5x3_N15_TIGHT"), ([2, 2, 2, 2, 2], "C5x2_N10")]:
        n, E = odd_blowup(5, sizes)
        adj, cuts = gmins(n, E)
        sdp_optimize(nm, n, adj, cuts[0])

if __name__ == "__main__":
    main()
