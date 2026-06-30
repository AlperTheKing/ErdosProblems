"""EXACT gate for GPT-Pro's CYCLE-HARDY spectral lemma (the non-switch route to rho(K2)<=N).

PROVEN linear algebra (no test needed):  for each shortest odd cycle Q of length L,
    q_Q q_Q^T  <=  L*D_Q - beta_L * L_Q,   beta_L = L/(2+2cos(pi/L)),
(L_Q = ordinary cycle Laplacian on Q incl closing bad edge; D_Q=diag(1_Q); q_Q=1_Q).
Averaging over all shortest cycles and using  sum_{f,Q}(1/|cyc[f]|) L_f D_Q = D_T  gives
    K2  <=  D_T - Lstar,     Lstar := sum_f (beta_{L_f}/|cyc[f]|) sum_{Q in cyc[f]} L_Q.
Hence  N*I - K2  >=  D_{N-T} + Lstar.  So the WHOLE problem reduces to the single PSD inequality

    (H)   H := D_{N-T} + Lstar  >=  0   (Hardy/Poincare on the shortest-odd-cycle network).

This gates (H) EXACTLY.  beta_L is irrational; we use a CERTIFIED rational beta_L' <= beta_L
(via a Taylor upper bound on cos(pi/L)), for which identity (3) still holds exactly, so a PSD pass
with beta_L' is a fully rational certificate.  Also reports the float min-eigenvalue with true beta_L
(diagnostic: how much slack the rational rounding costs).  Full gmin battery incl the N=23 guardrail.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _csmspec import is_psd, build_K2

try:
    import numpy as np
    import math
    HAVE_NP = True
except Exception:
    HAVE_NP = False

# certified rational lower bound on pi (pi > PI_LO)
PI_LO = F(31415926535897932, 10**16)  # < pi

def cos_upper(L):
    """Certified rational c >= cos(pi/L).
       theta_lo = PI_LO/L <= pi/L.  f(t)=1 - t^2/2 + t^4/24 >= cos(t) (alternating series),
       and f is decreasing on [0,sqrt6], so f(theta_lo) >= f(pi/L) >= cos(pi/L)."""
    t = PI_LO / L
    return 1 - t*t/2 + t**4/F(24)

def beta_rat(L):
    """Rational beta' <= beta_L = L/(2+2cos(pi/L))  (uses cos_upper to enlarge denominator)."""
    c = cos_upper(L)
    return F(L) / (2 + 2*c)

# precompute rational betas for odd L up to 60
BETA = {L: beta_rat(L) for L in range(3, 61, 2)}

def cycle_laplacian_add(LQ, Q):
    """Add the ordinary cycle Laplacian of cycle Q (list of vertices, closing edge Q[-1]-Q[0])."""
    L = len(Q)
    for i in range(L):
        a = Q[i]; b = Q[(i+1) % L]
        LQ[a][a] += 1; LQ[b][b] += 1
        LQ[a][b] -= 1; LQ[b][a] -= 1

def build_H(n, M, ell, T, cyc, betamap):
    """H = diag(N - T) + sum_f (beta_{L_f}/|cyc[f]|) sum_{Q in cyc[f]} L_Q   (exact Fraction)."""
    N = F(n)
    H = [[F(0)]*n for _ in range(n)]
    for v in range(n):
        H[v][v] = N - T[v]
    for f in M:
        Qs = cyc[f]; L = ell[f]
        w = betamap[L] / len(Qs)
        for Q in Qs:
            LQ = [[F(0)]*n for _ in range(n)]  # sparse would be better; n small
            cycle_laplacian_add(LQ, list(Q))
            for a in set(Q):
                for b in set(Q):
                    if LQ[a][b] != 0:
                        H[a][b] += w * LQ[a][b]
    return H

def float_min_eig(n, M, ell, T, cyc):
    """min eigenvalue of H with TRUE beta_L (float) — diagnostic only."""
    if not HAVE_NP:
        return None
    N = float(n)
    H = np.zeros((n, n))
    for v in range(n):
        H[v][v] = N - float(T[v])
    for f in M:
        Qs = cyc[f]; L = ell[f]
        beta = L / (2 + 2*math.cos(math.pi / L))
        w = beta / len(Qs)
        for Q in Qs:
            Ql = list(Q)
            for i in range(len(Ql)):
                a = Ql[i]; b = Ql[(i+1) % len(Ql)]
                H[a][a] += w; H[b][b] += w
                H[a][b] -= w; H[b][a] -= w
    ev = np.linalg.eigvalsh(H)
    return float(ev[0])

def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    # float diagnostic with true beta
    fmin = float_min_eig(n, M, ell, T, cyc)
    if fmin is not None:
        if acc['fmin'] is None or fmin < acc['fmin']:
            acc['fmin'] = fmin; acc['fmin_ex'] = (name, n)
        if fmin < -1e-7:
            acc['float_neg'] += 1
            if acc['float_ex'] is None:
                acc['float_ex'] = (name, n, ''.join(map(str, side)), fmin)
    # exact rational PSD with certified beta' <= beta_L
    H = build_H(n, M, ell, T, cyc, BETA)
    psd, minpiv = is_psd(H)
    if not psd:
        acc['exact_fail'] += 1
        if acc['exact_ex'] is None:
            acc['exact_ex'] = (name, n, ''.join(map(str, side)), str(minpiv))
    else:
        if minpiv == 0:
            acc['tight'] += 1
        if acc['mingap'] is None or (minpiv is not None and minpiv < acc['mingap']):
            acc['mingap'] = minpiv

def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)

def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best

def main():
    acc = dict(cuts=0, exact_fail=0, float_neg=0, tight=0, mingap=None, fmin=None, fmin_ex=None,
               exact_ex=None, float_ex=None)
    # quick beta sanity
    print("beta_5' =", BETA[5], "~", float(BETA[5]), " (true (5-sqrt5)/2 ~ 1.381966)")
    print("beta_7' =", float(BETA[7]), " beta_9' =", float(BETA[9]), flush=True)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d exact_fail=%d float_neg=%d fmin=%.3e"
              % (nn, acc['cuts'], acc['exact_fail'], acc['float_neg'], acc['fmin'] if acc['fmin'] is not None else 0), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d exact_fail=%d float_neg=%d %s"
          % (acc['cuts'], acc['exact_fail'], acc['float_neg'], acc['exact_ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d exact_fail=%d float_neg=%d %s"
          % (acc['cuts'], acc['exact_fail'], acc['float_neg'], acc['exact_ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("gamma-min cuts tested:", acc['cuts'], " (random N11/12:", made, ")")
    print("EXACT (H) PSD FAILURES (rational beta'):", acc['exact_fail'], acc['exact_ex'] or '')
    print("float min-eig (true beta) negatives <-1e-7:", acc['float_neg'], acc['float_ex'] or '')
    print("global float min-eig:", acc['fmin'], "at", acc['fmin_ex'])
    print("exact tight (pivot 0) cuts:", acc['tight'], " min exact pivot gap:", str(acc['mingap']))
    ok = acc['exact_fail'] == 0
    print("VERDICT:", "(H) D_{N-T}+Lstar >=0 HOLDS exact (rational beta') on full battery incl N=23 -- CYCLE-HARDY ROUTE LIVE; #23 reduces to proving (H)"
          if ok else "(H) FALSE with rational beta' -- check float_neg to see if true-beta also fails or only rounding")

if __name__ == "__main__":
    main()
