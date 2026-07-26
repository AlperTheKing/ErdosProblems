"""TASK 2 (step 3) -- THEOREM F : the radius 1/13 is improved to 4/25.

THEOREM F.  H triangle-free, C an induced C5, T = full twins, R = rest outside C,
tau = x(T), rho = x(R), eta = tau + rho.  Put
     e_RT = sum over edges u~v with u in R, v in T   of x_u x_v ,
     e_RR = sum over edges u~v with u,v in R         of x_u x_v .
If
     50 e_RT + 125 e_RR  <=  1 - (1-rho)^10                        (*)
then psi(H,x) <= 1/25.   Since e_RT <= rho*tau and e_RR <= rho^2/4 (Motzkin-Straus,
H[R] triangle-free), (*) holds whenever  50 rho tau + (125/4) rho^2 <= 1-(1-rho)^10,
and in particular whenever  eta <= 4/25 = 0.16   (old radius: 1/13 = 0.0769...).

Proof ingredients, each verified exactly below:
 (F1)  cut_i has monochromatic weight <= z_i z_{i+1} + K_i,
       K_i = sum_{v in R} x_v d_i(v) + RR_i,  d_i(v) = min over the two sides of
       x(N(v) cap (C u T) cap side),  RR_i = mono R-R weight <= e_RR.
 (F2)  sum_i K_i <= 2 e_RT + 5 e_RR .
 (F3)  if z_i z_{i+1} + K_i > 1/25 for all i then 25 sum_i K_i > 1 - (1-rho)^10.
       [product/AM-GM step: prod_i (z_i z_{i+1}) = (prod z)^2 <= ((1-rho)/5)^10]
 (F4)  eta <= 4/25  ==>  (*) .
"""
from fractions import Fraction as Fr
import random
import R9_thmD_lib as L

# ---------------------------------------------------------------- (F4) ------

def phi_over_rho(rho):
    """psi(rho) := (1-(1-rho)^10)/rho - 8 + (75/4) rho  = sum_{k<10}(1-rho)^k - 8 + 75rho/4."""
    s = sum((1 - rho) ** k for k in range(10))
    return s - 8 + Fr(75, 4) * rho


def verify_F4():
    """exact: 50 rho tau + (125/4) rho^2 <= 1-(1-rho)^10 for all tau,rho>=0, tau+rho <= 4/25.

    Worst case tau = 4/25 - rho gives  8 rho - (75/4) rho^2 <= 1-(1-rho)^10,
    i.e. phi(rho) = 1-(1-rho)^10 - 8 rho + (75/4) rho^2 >= 0 on [0,4/25];
    equivalently phi_over_rho >= 0 there.  Lipschitz grid, exact rationals.
    """
    hi = Fr(4, 25)
    Nsteps = 4000
    delta = hi / Nsteps
    # |d/drho phi_over_rho| <= sum_{k=1}^{9} k + 75/4 = 45 + 18.75 = 63.75 on [0,1]
    Lip = Fr(255, 4)
    worst = None
    for k in range(Nsteps + 1):
        rho = hi * k / Nsteps
        val = phi_over_rho(rho)
        if worst is None or val < worst[0]:
            worst = (val, rho)
        if val < Lip * delta:
            return False, (val, rho)
    return True, worst


# ---------------------------------------------------------------- (F1,F2) ---

def thmF_data(G, C, a):
    n, adj = G
    T, R, Rj, Rnone = L.classify(G, C)
    if Rj is None:
        return None
    Tset = set(v for t in T for v in t)
    CT = set(C) | Tset
    P = [set([C[i]]) | set(T[i]) for i in range(5)]
    z = [sum(a[v] for v in P[i]) for i in range(5)]
    rho = sum(a[v] for v in R)
    tau = sum(a[v] for v in Tset)
    e_RT = sum(a[u] * a[v] for u in R for v in adj[u] if v in Tset)
    e_RR = sum(a[u] * a[v] for u in R for v in adj[u] if v in R) // 2
    return T, R, Rj, Rnone, P, z, rho, tau, e_RT, e_RR, CT, Tset


def cut_and_K(G, C, a, i, data):
    """build cut i with the 'best side w.r.t. C u T' rule for R; return
    (actual mono weight, z_i z_{i+1} + K_i, K_i)."""
    n, adj = G
    T, R, Rj, Rnone, P, z, rho, tau, e_RT, e_RR, CT, Tset = data
    side = {}
    for m in range(5):
        s = 0 if (m - i) % 5 in (0, 1, 3) else 1
        for v in P[m]:
            side[v] = s
    K = 0
    for v in R:
        c0 = sum(a[w] for w in adj[v] if w in CT and side[w] == 0)
        c1 = sum(a[w] for w in adj[v] if w in CT and side[w] == 1)
        side[v] = 0 if c0 <= c1 else 1
        K += a[v] * min(c0, c1)                      # sum_v x_v d_i(v)
    mono = 0
    RR = 0
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] == side[v]:
                mono += a[u] * a[v]
                if u in R and v in R:
                    RR += a[u] * a[v]
    K += RR
    return mono, z[i] * z[(i + 1) % 5] + K, K


def check_thmF(G, C, a):
    """returns list of failures among (F1),(F2),(F3-consequence)."""
    data = thmF_data(G, C, a)
    if data is None:
        return ['classify']
    T, R, Rj, Rnone, P, z, rho, tau, e_RT, e_RR, CT, Tset = data
    q = sum(a)
    fails = []
    Ks, bounds = [], []
    for i in range(5):
        mono, bnd, K = cut_and_K(G, C, a, i, data)
        Ks.append(K); bounds.append(bnd)
        if mono > bnd:
            fails.append(('F1', i, mono, bnd))
        if L.psi_int(G, a) > mono:
            fails.append(('F1-cut-legal', i))
    if sum(Ks) > 2 * e_RT + 5 * e_RR:
        fails.append(('F2', sum(Ks), 2 * e_RT + 5 * e_RR))
    # (F3) consequence + theorem F conclusion, in integers (x = a/q)
    lhs = Fr(50 * e_RT + 125 * e_RR, q * q)
    rhs = 1 - (1 - Fr(rho, q)) ** 10
    if lhs <= rhs:
        if 25 * L.psi_int(G, a) > q * q:
            fails.append(('THMF-conclusion', L.psi_int(G, a), q))
    # eta <= 4/25  ==>  conclusion
    eta = Fr(q - sum(a[c] for c in C), q)
    if eta <= Fr(4, 25) and 25 * L.psi_int(G, a) > q * q:
        fails.append(('THMF-radius-4/25', L.psi_int(G, a), q))
    return fails


if __name__ == '__main__':
    print("=" * 78)
    print("J. (F4) exact verification that eta <= 4/25 implies the hypothesis of Theorem F")
    print("=" * 78)
    ok, w = verify_F4()
    print("   exact Lipschitz-grid check on [0,4/25]:  %s   (min of phi(rho)/rho = %s at rho=%s)"
          % ("PASS" if ok else "FAIL", float(w[0]), float(w[1])))
    # and the same for the OLD radius, for comparison, plus the first failing radius
    for c in [Fr(1, 13), Fr(4, 25), Fr(41, 250), Fr(17, 100), Fr(1, 5)]:
        # worst case tau = c - rho :  50 rho (c-rho) + 125/4 rho^2 <= 1-(1-rho)^10
        bad = None
        for k in range(1, 2001):
            rho = c * k / 2000
            lhs = 50 * rho * (c - rho) + Fr(125, 4) * rho * rho
            rhs = 1 - (1 - rho) ** 10
            if lhs > rhs:
                bad = rho
                break
        print("   radius eta <= %-8s : %s" % (str(c), "OK" if bad is None else
                                              "FAILS at rho=%.4f" % float(bad)))

    print("=" * 78)
    print("K. (F1),(F2) and the conclusion of Theorem F, exact, on the whole battery")
    print("=" * 78)
    import R9_thmD_adversarial as A
    N = L.named_graphs()
    allfails = []
    tot = 0
    for name, G in N.items():
        C5s = L.induced_C5s(G)
        if not C5s:
            continue
        W = A.rand_weights(G[0], 12, 25, seed=hash(name) % 907) + [[1] * G[0]]
        for C in C5s:
            for a in W:
                if sum(a) == 0:
                    continue
                f = check_thmF(G, C, a)
                tot += 1
                if f:
                    allfails.append((name, C, a, f))
        print("  %-18s pentagons=%3d : cumulative failures %d" % (name, len(C5s), len(allfails)))
    fams = [("R0->T2,T3,T0", A.fam_twins_plus_R([1, 1, 1, 1, 1], [(0, [(2, 0), (3, 0), (0, 0)])])[0]),
            ("Rempty->all twins", A.fam_twins_plus_R([1, 1, 1, 1, 1], [(None, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])])[0]),
            ("dense twins+2R", A.fam_twins_plus_R([2, 2, 2, 2, 2], [(0, [(2, 0), (3, 1)]), (2, [(4, 0), (0, 1)])])[0])]
    for nm, G in fams:
        W = A.rand_weights(G[0], 12, 25, seed=hash(nm) % 887) + [[1] * G[0]]
        for C in L.induced_C5s(G):
            for a in W:
                f = check_thmF(G, C, a)
                tot += 1
                if f:
                    allfails.append((nm, C, a, f))
    for n in range(7, 12):
        for seed in range(20):
            G = A.rand_trianglefree(n, seed * 613 + n, dens=0.85)
            C5s = L.induced_C5s(G)
            if not C5s:
                continue
            W = A.rand_weights(n, 10, 6, seed=seed) + [[1] * n]
            for C in C5s:
                for a in W:
                    f = check_thmF(G, C, a)
                    tot += 1
                    if f:
                        allfails.append(('rand n=%d' % n, C, a, f))
    print("  purpose-built + random triangle-free graphs done")
    print("=" * 78)
    print("Theorem F instances checked: %d ; FAILURES: %d" % (tot, len(allfails)))
    for f in allfails[:10]:
        print("   ", f)
