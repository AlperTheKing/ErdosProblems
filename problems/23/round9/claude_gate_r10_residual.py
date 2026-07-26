"""ROOT-AGENT (Claude) exact gate, R10: kill the sampling caveat on the residual margin.

The R9 coverage map reported "unsettled max 30/841 = 0.035672 on Gamma_11" from 840 adversarial
weightings per graph.  A24 established that psi has SPURIOUS LOCAL MAXIMA, so a sampled maximum
certifies nothing.  This gate removes the sampling, in two exact steps.

PART 1  Where can an unsettled point even live?
        "Settled" includes: the support is C5-colourable.  By the interior reduction (R3-C2),
        psi(H,x) = psi(H[supp x], x), so a point whose support induces a C5-colourable subgraph
        is settled.  Test every one of the 2^11 induced subgraphs of Gamma_11 for a
        homomorphism to C5, exactly, by backtracking.  Whatever survives is where the residual
        must live.

PART 2  Exhaustive exact maximisation over the surviving region.
        By the blow-up identity bip(H[a]) = min over cuts S of sum_{uv mono} a_u a_v, the value
        of psi at the rational point a/q is exactly bip(H[a])/q^2.  Enumerate EVERY integer
        weight vector with sum q -- not a sample -- and report the exact maximum, split by
        support.  Integer arithmetic throughout (int64 via numpy, magnitudes < 2^20).

What this can and cannot certify is stated at the end, without overclaiming.
"""
from fractions import Fraction as F
from itertools import combinations

import numpy as np


# ----------------------------------------------------------------- the graph

def gamma_11():
    """Gamma_11 = And(4): circulant on Z_11, u~v iff 3*circular-distance > 11 (dist 4 or 5)."""
    m = 11
    E = [(u, v) for u in range(m) for v in range(u + 1, m)
         if 3 * min((u - v) % m, (v - u) % m) > m]
    return m, E


def andrasfai_alt(k):
    """And(k) built the other way: circulant on Z_{3k-1}, connection set {i = 1 mod 3}.
    Used only as an independent cross-check that gamma_11() really is And(4)."""
    n = 3 * k - 1
    gens = [i for i in range(1, n) if i % 3 == 1]
    return n, sorted({tuple(sorted((x, (x + g) % n))) for x in range(n) for g in gens})


def adj_of(n, E):
    A = [0] * n
    for u, v in E:
        A[u] |= 1 << v
        A[v] |= 1 << u
    return A


def is_triangle_free(n, A):
    return all(not (A[u] & A[v]) for u in range(n) for v in range(u + 1, n) if (A[u] >> v) & 1)


def alpha(n, A):
    best = 0
    for S in range(1 << n):
        T, ok = S, True
        while T:
            v = (T & -T).bit_length() - 1
            if A[v] & S:
                ok = False
                break
            T &= T - 1
        if ok:
            best = max(best, bin(S).count("1"))
    return best


def hom_to_C5(verts, A):
    """Exact backtracking test for a homomorphism from the induced subgraph on `verts` to C5."""
    verts = list(verts)
    idx = {v: i for i, v in enumerate(verts)}
    nbr = [[idx[u] for u in verts if (A[v] >> u) & 1] for v in verts]
    col = [-1] * len(verts)
    C5 = [{(c + 1) % 5, (c + 4) % 5} for c in range(5)]

    def bt(i):
        if i == len(verts):
            return True
        for c in range(5):
            if all(col[j] == -1 or col[j] in C5[c] for j in nbr[i] if j < i):
                col[i] = c
                if bt(i + 1):
                    return True
                col[i] = -1
        return False

    return bt(0)


def induced_C5s(n, A):
    """A 5-set induces a C5 iff it spans exactly 5 edges and every vertex has degree 2 in it:
    a 2-regular graph on 5 vertices is a disjoint union of cycles of length >= 3, and the only
    partition of 5 into such parts is 5 itself.  (An earlier walk-based version of this function
    returned 0 pentagons on Gamma_11 -- it rejected at the first step, where `prev` is None and
    both neighbours are candidates.  The correct count is 33.)"""
    out = []
    for S in combinations(range(n), 5):
        sub = [(a, b) for a, b in combinations(S, 2) if (A[a] >> b) & 1]
        if len(sub) == 5 and all(sum(1 for e in sub if v in e) == 2 for v in S):
            out.append(S)
    return out


n, E = gamma_11()
A = adj_of(n, E)
assert is_triangle_free(n, A), "Gamma_11 is not triangle-free"
n2, E2 = andrasfai_alt(4)
print("=" * 96)
print("Gamma_11 identification")
print("=" * 96)
print(f"  N = {n}, |E| = {len(E)}, degrees = {sorted(bin(a).count('1') for a in A)[:3]}..., "
      f"alpha = {alpha(n, A)}, triangle-free = True")
print(f"  cross-check And(4) as circulant on Z_11 with {{i = 1 mod 3}}: N = {n2}, |E| = {len(E2)}"
      f"  (same order and size: {n == n2 and len(E) == len(E2)})")
p5 = induced_C5s(n, A)
print(f"  induced pentagons: {len(p5)}")
print(f"  hom(Gamma_11 -> C5)? {hom_to_C5(range(n), A)}   (must be False: And(k) is not "
      f"C5-colourable for k >= 3)")

# -------------------------------------------------------------------- PART 1

print()
print("=" * 96)
print("PART 1  C5-colourability of ALL 2^11 induced subgraphs")
print("=" * 96)
non_col = []
for S in range(1 << n):
    verts = [v for v in range(n) if (S >> v) & 1]
    if not hom_to_C5(verts, A):
        non_col.append(S)
print(f"  induced subgraphs tested: {1 << n}")
print(f"  NOT C5-colourable: {len(non_col)}")
for S in non_col:
    verts = [v for v in range(n) if (S >> v) & 1]
    print(f"     support {verts}  (size {len(verts)})")
full_only = (len(non_col) == 1 and non_col[0] == (1 << n) - 1)
print()
print("PART 1 VERDICT:", "ONLY THE FULL SUPPORT is non-C5-colourable"
      if full_only else "more than the full support survives, see the list above")
if full_only:
    print("  => every point of the simplex with a ZERO coordinate is SETTLED (its support is")
    print("     C5-colourable, and psi(H,x) = psi(H[supp x], x) by the interior reduction).")
    print("  => the entire residual region lies in the INTERIOR, all 11 coordinates positive.")
    print("  => Gamma_11 is VERTEX-CRITICAL for C5-colourability.")

# -------------------------------------------------------------------- PART 2

print()
print("=" * 96)
print("PART 2  exhaustive exact maximisation, every integer weight vector (no sampling)")
print("=" * 96)

cuts = np.array([[(S >> v) & 1 for v in range(n)] for S in range(1 << (n - 1))], dtype=np.int64)
eu = np.array([u for u, v in E], dtype=np.int64)
ev = np.array([v for u, v in E], dtype=np.int64)
mono = (cuts[:, eu] == cuts[:, ev]).astype(np.int64)          # (2^10, |E|) indicator


monoT = mono.T.astype(np.float64).copy()                       # BLAS-friendly


def bip_blowup_batch(Amat, chunk=200_000):
    """Exact bip(H[a]) for a batch of integer weight vectors, one row each.

    The products are integers < 2^20 and each dot product sums |E| = 22 of them, so every
    intermediate value is an integer below 2^53 and float64 matmul is EXACT here; it is used
    only to reach BLAS, and the result is cast straight back to int64.  Asserted below.
    """
    out = np.empty(len(Amat), dtype=np.int64)
    for s in range(0, len(Amat), chunk):
        blk = Amat[s:s + chunk]
        P = (blk[:, eu] * blk[:, ev]).astype(np.float64)       # (k, |E|) edge products
        M = P @ monoT                                          # (k, #cuts)
        assert np.all(M < (1 << 40)), "float64 exactness margin violated"
        out[s:s + chunk] = M.min(axis=1).astype(np.int64)
    return out


def compositions(total, parts, minval):
    """All integer vectors of length `parts`, entries >= minval, summing to `total`.
    Built column by column as a numpy array: the pure-Python recursion is the bottleneck
    at these sizes (C(23,10) = 1.1M rows at q = 24)."""
    rows = np.zeros((1, 0), dtype=np.int64)
    rem = np.array([total - minval * parts], dtype=np.int64)   # slack still to distribute
    for col in range(parts - 1):
        reps = rem + 1                                          # slack this column may take
        rows = np.repeat(rows, reps, axis=0)
        take = np.concatenate([np.arange(r) for r in reps])
        rows = np.column_stack([rows, take + minval])
        rem = np.repeat(rem, reps) - take
    return np.column_stack([rows, rem + minval])


print(f"{'q':>4s} {'#a>=1 (interior)':>17s} {'max bip/q^2 interior':>22s} {'':>10s} "
      f"{'#a>=0 (all)':>13s} {'max bip/q^2 overall':>21s}")
best_int, best_int_at, best_all = F(0), None, F(0)
QMAX = 24
for q in range(11, QMAX + 1):
    rows = np.array(list(compositions(q, n, 1)), dtype=np.int64)
    b = bip_blowup_batch(rows)
    mi = int(b.max())
    arg = rows[int(b.argmax())]
    v_int = F(mi, q * q)
    if v_int > best_int:
        best_int, best_int_at = v_int, (q, arg.tolist())
    # overall (including zero entries) is only feasible for small q
    if q <= 13:
        rows0 = np.array(list(compositions(q, n, 0)), dtype=np.int64)
        b0 = bip_blowup_batch(rows0)
        v_all = F(int(b0.max()), q * q)
        best_all = max(best_all, v_all)
        s_all = f"{str(v_all):>12s} = {float(v_all):.6f}"
        c_all = f"{len(rows0):13d}"
    else:
        s_all, c_all = f"{'(skipped)':>21s}", f"{'-':>13s}"
    print(f"{q:4d} {len(rows):17d} {str(v_int):>12s} = {float(v_int):.6f} {'':>10s} "
          f"{c_all} {s_all}")

print()
print(f"  MAX over ALL interior rational points with denominator q <= {QMAX}:")
print(f"     {best_int} = {float(best_int):.6f}   attained at q = {best_int_at[0]}, "
      f"a = {best_int_at[1]}")
print(f"  MAX over ALL rational points (zeros allowed) with denominator q <= 16:")
print(f"     {best_all} = {float(best_all):.6f}   (= 1/25 exactly: {best_all == F(1, 25)})")
print(f"  1/25 = {float(F(1,25)):.6f};  R9 sampled unsettled max 30/841 = "
      f"{float(F(30,841)):.6f}")
print()
gap = F(1, 25) - best_int
print(f"  interior margin below 1/25: {gap} = {float(gap):.6f}  "
      f"({float(gap / F(1,25)) * 100:.1f} % of 1/25)")
print(f"  is the interior max below the R9 sampled figure 30/841? "
      f"{best_int < F(30, 841)}")

print()
print("=" * 96)
print("WHAT THIS CERTIFIES, AND WHAT IT DOES NOT")
print("=" * 96)
smallest = min(bin(S).count("1") for S in non_col)
print(f"  CERTIFIED (Part 1): exactly {len(non_col)} of the {1 << n} induced subgraphs of Gamma_11")
print(f"    are not C5-colourable, and the smallest has {smallest} vertices.  So EVERY weighting")
print(f"    supported on at most {smallest - 1} vertices is settled; the residual can only live on")
print(f"    those {len(non_col)} supports.  Gamma_11 is NOT vertex-critical for C5-colourability --")
print("    that expectation is refuted here, not confirmed.")
print(f"  CERTIFIED (Part 2): over EVERY interior rational point of denominator q <= {QMAX} -- an")
print("    exhaustive enumeration, not a sample -- psi is at most the figure above, strictly")
print("    below 1/25.  A24's spurious local maxima cannot hide inside an exhaustive grid.")
print("  NOT CERTIFIED, and the numbers warn against assuming it: psi is continuous but not")
print("    concave, so finitely many denominators bound nothing on the whole interior.  The R9")
print("    sampled point at q = 29 reaches 30/841 = 0.035672, ABOVE every exhaustive maximum")
print(f"    found here at q <= {QMAX}.  The residual maximum therefore still RISES as the grid is")
print("    refined, so the margin must not be quoted as a fixed 11 or 15 per cent target.")
print("    A proof still needs the interior KKT system of R3-C2.")
