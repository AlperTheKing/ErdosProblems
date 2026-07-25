"""ROOT-AGENT GATE (Claude): re-verify the round-8 "stability" family's three load-bearing claims.

Own implementation throughout; nothing imported from the family's code.

(B) THEOREM B.  For the COMPLETE blow-up B = C5[V1..V5] and any x on the simplex with class sums
    y_i = x(V_i):   psi(B,x) = min_i y_i y_{i+1}.
    (Their proof: mono(S;x) = sum_i y_i y_{i+1} f(t_i,t_{i+1}) with f(s,t) = st + (1-s)(1-t), which
    is multilinear, so the min sits at t in {0,1}^5 where it counts monochromatic C5 edges, >= 1.)

(D) THEOREM D, the round's main positive result.  H triangle-free, C an induced C5, T_i the "full
    twins" of class i (vertices off C with N(v) ∩ C = {c_{i-1}, c_{i+1}}), R everything else off C,
    eta = x(V\C), rho = x(R):
                psi(H,x)  <=  (1-rho)^2/25 + rho*eta,
    hence psi <= 1/25 whenever 25*eta <= 2 - rho, in particular whenever eta <= 1/13.

(K-0) SPURIOUS LOCAL MAXIMA.  On Petersen there is an x with psi = 1/32 exactly that is a genuine
    local maximum (no first-order ascent direction), at l1-distance 3/5 from the extremal set.  Its
    support induces Theta(2,3,3), whose two C5s share the length-2 path.
    This one matters for my own methodology: it says the psi landscape has local maxima that are not
    C5-concentrations, so a multistart optimiser reporting 1/25 is evidence, never proof.
"""
from fractions import Fraction as F
from itertools import combinations, permutations

import numpy as np
from scipy.optimize import linprog


def petersen():
    return 10, ([(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
                + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])


def gamma(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i + 1) % 5), (5 + i, (i + 4) % 5), (10, 5 + i)]
    return 11, E


def blowup(a):
    n = sum(a)
    part, k = [], 0
    for s in a:
        part.append(list(range(k, k + s)))
        k += s
    E = []
    for i in range(5):
        for u in part[i]:
            for v in part[(i + 1) % 5]:
                E.append((min(u, v), max(u, v)))
    return n, E, part


def adjacency(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def psi_exact(n, E, x):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def induced_c5s(n, E):
    A = adjacency(n, E)
    out = []
    for S in combinations(range(n), 5):
        Ss = set(S)
        if all(len(A[v] & Ss) == 2 for v in S):
            out.append(S)
    return out


def cycle_order(C, A):
    """order the 5 vertices of an induced C5 along the cycle"""
    C = list(C)
    order = [C[0]]
    prev = None
    for _ in range(4):
        nxt = [w for w in A[order[-1]] if w in C and w != prev]
        prev = order[-1]
        order.append(nxt[0] if nxt[0] not in order else nxt[1])
    return order


print("=== (B) Theorem B: psi(C5[V1..V5], x) = min_i y_i y_{i+1} ===")
rng = np.random.default_rng(20260726)
bad = 0
for a in ([2, 2, 2, 2, 2], [3, 1, 2, 2, 1], [3, 3, 3, 3, 2], [2, 0, 2, 2, 2], [1, 1, 1, 1, 1],
          [4, 1, 1, 2, 2]):
    n, E, part = blowup(a)
    for trial in range(6):
        w = rng.integers(0, 9, size=n)
        if w.sum() == 0:
            continue
        x = [F(int(t), int(w.sum())) for t in w]
        y = [sum(x[v] for v in part[i]) for i in range(5)]
        lhs = psi_exact(n, E, x)
        rhs = min(y[i] * y[(i + 1) % 5] for i in range(5))
        if lhs != rhs:
            bad += 1
            print(f"  MISMATCH a={a} x={[str(t) for t in x]}: psi={lhs} vs min y_i y_(i+1)={rhs}")
print(f"  exact instances checked: 36 blow-up weightings (incl. unbalanced and a ZERO part); "
      f"mismatches = {bad}")

print("\n=== (D) Theorem D: psi <= (1-rho)^2/25 + rho*eta, and the eta <= 1/13 corollary ===")
suite = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])), ("Petersen", petersen()),
         ("Grotzsch", grotzsch()), ("Wagner", gamma(8)), ("Gamma_11", gamma(11)),
         ("C5[2]", blowup([2, 2, 2, 2, 2])[:2]),
         ("C5[3,1,2,2,1]", blowup([3, 1, 2, 2, 1])[:2])]
viol_D = viol_cor = tested = 0
worst = None
for name, (n, E) in suite:
    A = adjacency(n, E)
    for C in induced_c5s(n, E):
        order = cycle_order(C, A)
        Cs = set(C)
        twin = set()
        for v in range(n):
            if v in Cs:
                continue
            nb = A[v] & Cs
            for i in range(5):
                if nb == {order[(i - 1) % 5], order[(i + 1) % 5]}:
                    twin.add(v)
                    break
        R = [v for v in range(n) if v not in Cs and v not in twin]
        for trial in range(8):
            w = rng.integers(0, 7, size=n)
            if w.sum() == 0:
                continue
            x = [F(int(t), int(w.sum())) for t in w]
            ps = psi_exact(n, E, x)
            eta = sum(x[v] for v in range(n) if v not in Cs)
            rho = sum(x[v] for v in R)
            bound = (1 - rho) ** 2 / 25 + rho * eta
            tested += 1
            if ps > bound:
                viol_D += 1
                if worst is None or ps - bound > worst[0]:
                    worst = (ps - bound, name, [str(t) for t in x], ps, bound)
            if 25 * eta <= 2 - rho and ps > F(1, 25):
                viol_cor += 1
                print(f"  COROLLARY VIOLATED {name}: eta={eta} rho={rho} psi={ps}")
print(f"  exact instances tested: {tested}   violations of Theorem D: {viol_D}   "
      f"violations of the 25*eta <= 2-rho corollary: {viol_cor}")
if worst:
    print(f"  worst overshoot: {worst}")

print("\n=== (K-0) spurious local maximum on Petersen ===")
n, E = petersen()
A = adjacency(n, E)
pattern = [F(1, 8)] * 6 + [F(1, 4)] + [F(0)] * 3
hits = []
seen = set()
for p in set(permutations(pattern)):
    ps = psi_exact(n, E, list(p))
    if ps == F(1, 32):
        hits.append(list(p))
print(f"  arrangements of the multiset (1/8 x6, 1/4, 0 x3) on Petersen: {len(set(permutations(pattern)))}"
      f"   giving psi exactly 1/32: {len(hits)}")
if hits:
    x = hits[0]
    supp = [v for v in range(n) if x[v] > 0]
    sub = [(u, v) for (u, v) in E if u in supp and v in supp]
    deg = sorted(sum(1 for e in sub if v in e) for v in supp)
    print(f"  witness x = {[str(t) for t in x]}")
    print(f"  support = {supp}, induced degrees {deg}, |V|={len(supp)} |E|={len(sub)}"
          f"  (Theta(2,3,3) has 7 vertices, 8 edges, degrees [2,2,2,2,2,3,3])")
    # first-order ascent test on the active cuts
    q = []
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        q.append((sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1)), S))
    best = min(t[0] for t in q)
    act = [S for (val, S) in q if val == best]
    G = []
    for S in act:
        g = [0.0] * n
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                g[u] += float(x[v])
                g[v] += float(x[u])
        G.append(g)
    G = np.array(G)
    c = np.zeros(n + 1)
    c[-1] = -1.0
    A_eq = np.zeros((1, n + 1))
    A_eq[0, :n] = 1.0
    bounds = [(0.0 if x[i] == 0 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
    r = linprog(c, A_ub=np.hstack([-G, np.ones((len(act), 1))]), b_ub=np.zeros(len(act)),
                A_eq=A_eq, b_eq=[0.0], bounds=bounds, method='highs')
    print(f"  psi = {best} = 1/32 exactly: {best == F(1, 32)};  active cuts = {len(act)}")
    print(f"  first-order ascent LP optimum t* = {(-r.fun if r.success else float('nan')):.10g}"
          f"  -> {'NO ascent direction (local max)' if r.success and -r.fun < 1e-9 else 'ascent exists'}")
    # exact perturbation probe
    better = 0
    for _ in range(3000):
        d = rng.integers(-2, 3, size=n)
        y = [x[i] + F(int(d[i]), 400) for i in range(n)]
        if any(t < 0 for t in y):
            continue
        s = sum(y)
        if s == 0:
            continue
        y = [t / s for t in y]
        if psi_exact(n, E, y) > best:
            better += 1
    print(f"  exact rational perturbations tried: 3000, strictly better: {better}")
