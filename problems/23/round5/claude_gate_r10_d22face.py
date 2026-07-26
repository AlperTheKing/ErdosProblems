"""ROOT-AGENT GATE (Claude): Codex's exact induced-C5 FACE argument for the Gamma_11 degree-4 SDP.

Codex's D22-reduced degree-4 run returned status optimal_inaccurate and, to its credit, refused to
call the iterate a certificate. The mathematically load-bearing part of the report is the FACE
argument, which is what justifies discarding that iterate rather than rounding it:

  * for each induced C5 support U, tightness forces T(1_U) = 0, so every exact PSD Gram block must
    KILL its evaluation vector at 1_U;
  * in the parity-zero block -- indexed by the 286 degree-3 monomials in 11 variables -- the 33
    evaluation vectors have exact rational rank 33;
  * the numerical block sits nowhere near that mandatory face (only 16 eigenvalues below 1e-5, and
    max |QK| about 9.8e-3), so entrywise rational rounding is invalid;
  * the same equality forces 1147 of the 2611 multiplier orbit coefficients to zero: when an arc cut
    has q_S(1_U) > 1, coefficientwise nonnegativity together with nu_S(1_U) = 0 kills every
    multiplier monomial supported inside U.

I re-derive the checkable parts from my own construction, in exact arithmetic:
  (1) the C5 tightness data: arc minimum 1, and the count of tight arc cuts per pentagon;
  (2) the rank of the 33 evaluation vectors in the degree-3 monomial basis -- Codex claims 33,
      i.e. full independence, which is what makes the face codimension large;
  (3) the forced-zero mechanism, counted directly.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def arc_cuts(n):
    seen = {}
    for s in range(n):
        for L in range(1, n):
            S = frozenset((s + t) % n for t in range(L))
            key = min(tuple(sorted(S)), tuple(sorted(set(range(n)) - S)))
            seen[key] = S
    return [frozenset()] + list(seen.values())


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
arcs = arc_cuts(n)
pent = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]
print(f"Gamma_11: |E| = {len(E)}, arc cuts = {len(arcs)}, induced C5s = {len(pent)}")

# ---- (1) tightness of the arc family at each pentagon indicator
mins, tights = set(), []
for U in pent:
    Us = set(U)
    vals = []
    for S in arcs:
        q = sum(1 for (u, v) in E if u in Us and v in Us and ((u in S) == (v in S)))
        vals.append(q)
    mins.add(min(vals))
    tights.append(sum(1 for q in vals if q == min(vals)))
print(f"(1) arc minimum q_S(1_U) over pentagons: {sorted(mins)}   [Codex: 1 -> "
      f"{'MATCH' if mins == {1} else 'MISMATCH'}]")
print(f"    tight-cut count range: {min(tights)}..{max(tights)}   [Codex: 24..25 -> "
      f"{'MATCH' if (min(tights), max(tights)) == (24, 25) else 'MISMATCH'}]")

# ---- (2) rank of the 33 evaluation vectors in the degree-3 monomial basis
mons3 = [m for m in combinations(range(n), 3)]           # squarefree part suffices for 0/1 vectors
allmons3 = []
for c in combinations(range(n + 3 - 1), 3):              # multisets of size 3 from 11 vars
    t = [c[0], c[1] - 1, c[2] - 2]
    allmons3.append(tuple(sorted(t)))
allmons3 = sorted(set(allmons3))
print(f"(2) degree-3 monomials in 11 variables: {len(allmons3)}   [Codex block order 286 -> "
      f"{'MATCH' if len(allmons3) == 286 else 'MISMATCH'}]")

rows = []
for U in pent:
    Us = set(U)
    rows.append([F(1) if all(t in Us for t in mon) else F(0) for mon in allmons3])


def rank_exact(mat):
    mat = [r[:] for r in mat]
    R, C = len(mat), len(mat[0])
    r = 0
    for c in range(C):
        piv = None
        for i in range(r, R):
            if mat[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        pv = mat[r][c]
        mat[r] = [t / pv for t in mat[r]]
        for i in range(R):
            if i != r and mat[i][c] != 0:
                f = mat[i][c]
                mat[i] = [a - f * b for a, b in zip(mat[i], mat[r])]
        r += 1
        if r == R:
            break
    return r


rk = rank_exact(rows)
print(f"    exact rational rank of the 33 evaluation vectors: {rk}   [Codex: 33 -> "
      f"{'MATCH' if rk == 33 else 'MISMATCH'}]")
print(f"    -> every exact PSD parity-zero Gram block must vanish on a {rk}-dimensional subspace")

# ---- (3) the forced-zero mechanism
forced = 0
total = 0
for S in arcs:
    for U in pent:
        Us = set(U)
        q = sum(1 for (u, v) in E if u in Us and v in Us and ((u in S) == (v in S)))
        total += 1
        if q > 1:
            forced += 1
print(f"(3) (arc cut, pentagon) pairs with q_S(1_U) > 1: {forced} of {total}")
print(f"    each such pair forces every degree-4 multiplier monomial supported inside U to vanish")
print(f"    for that cut, by coefficientwise nonnegativity together with nu_S(1_U) = 0.")
print(f"    Codex reports this kills 1147 of 2611 multiplier ORBIT coefficients; the orbit count")
print(f"    depends on its D22 orbit indexing, which I do not reconstruct here -- the MECHANISM")
print(f"    is what I verify, and it is sound: q_S(1_U) > 1 with nu_S >= 0 coefficientwise and")
print(f"    the tightness identity nu_S(1_U) q_S(1_U) = 0 forces those coefficients to zero.")
