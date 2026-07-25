"""Q4: the exact zero set Z of a tight certificate, and the exact rational kernel it forces.

psi is concave along any direction whose positive and negative supports are independent sets
(ACCEPTED BASE 6), and psi <= 1/25 with equality at every induced-C5 concentration (PLATEAU).
Hence every convex combination of C5-concentrations that stays at 1/25 is also a maximiser, and
a tight certificate T must vanish on the whole of that set Z:  T(x) = 0 for x in Z, so the Gram
must kill v(x) for every x in Z.

This module computes, in exact rationals:
  - Zpts: a spanning sample of Z (convex combinations of the C5-concentrations with psi = 1/25);
  - per parity block, a rational basis of span{ v_b(x) : x in Z }  = the forced kernel.
"""
from fractions import Fraction as F
from itertools import combinations
from Q4_graphs import graph_by_key as gamma_graph, all_cuts, nondominated_cuts, induced_C5s
from Q4_sos import monomials, parity_blocks


def psi_exact(n, E, cuts, x):
    return min(sum(x[E[k][0]] * x[E[k][1]] for k in mono) for _m, mono in cuts)


def zero_points(n, E, cuts, denom=6):
    """All convex combinations of the C5-concentrations with weights of denominator `denom`
    that are still maximisers (psi = L^2/25).  Returns list of exact rational vectors."""
    C5s = induced_C5s(n, E)
    base = []
    for C in C5s:
        base.append([F(1, 5) if v in C else F(0) for v in range(n)])
    pts = [tuple(b) for b in base]
    # pairs
    for i, j in combinations(range(len(base)), 2):
        for a in range(1, denom):
            w = F(a, denom)
            x = tuple(w * base[i][v] + (1 - w) * base[j][v] for v in range(n))
            if psi_exact(n, E, cuts, x) == F(1, 25):
                pts.append(x)
    # triples (cheap, catches higher-dimensional faces)
    for i, j, k in combinations(range(len(base)), 3):
        x = tuple((base[i][v] + base[j][v] + base[k][v]) / 3 for v in range(n))
        if psi_exact(n, E, cuts, x) == F(1, 25):
            pts.append(x)
    return sorted(set(pts))


def rational_rank(rows):
    """Exact rank + a row-echelon basis of a list of rational vectors."""
    rows = [list(r) for r in rows]
    basis, pivots = [], []
    for r in rows:
        for b, p in zip(basis, pivots):
            if r[p] != 0:
                f = r[p] / b[p]
                r = [ri - f * bi for ri, bi in zip(r, b)]
        nz = [i for i, v in enumerate(r) if v != 0]
        if nz:
            basis.append(r)
            pivots.append(nz[0])
    return basis


def kernel_bases(n, d, Zpts):
    """For each parity block of degree-(2d+2) exponents, the exact kernel basis forced by Z."""
    out = []
    for B in parity_blocks(n, 2 * d + 2):
        rows = []
        for x in Zpts:
            # v_b(x)_beta = y^beta with y_i^2 = x_i ; within a block all entries share one sign
            row = []
            ok = True
            for b in B:
                val = F(1)
                for i in range(n):
                    if b[i]:
                        if x[i] == 0:
                            val = F(0)
                            break
                        # half-integer powers only appear through the parity, which is constant
                        # inside a block: use x^{(beta - p)/2} * prod_{i in p} sqrt(x_i).
                        val = val  # handled below
                row.append(val)
            rows.append(row)
        out.append((B, rows))
    return out


def block_kernel(n, B, Zpts):
    """Exact kernel vectors for one parity block: for x in Z, v_beta = x^{(beta-p)/2} * s(x,p),
    where s(x,p) = prod_{i: p_i=1} sqrt(x_i) is a common factor of the whole block (and is 0 iff
    some coordinate of p is outside supp(x)).  Dropping the common factor keeps it rational."""
    p = tuple(b % 2 for b in B[0])
    rows = []
    for x in Zpts:
        if any(x[i] == 0 for i in range(n) if p[i]):
            continue                      # whole block vector is zero: no condition
        row = []
        for b in B:
            val = F(1)
            for i in range(n):
                e = (b[i] - p[i]) // 2
                if e:
                    val *= x[i] ** e
            row.append(val)
        rows.append(row)
    return rational_rank(rows)


if __name__ == "__main__":
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else 8
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    n, E = gamma_graph(m)
    cuts = nondominated_cuts(all_cuts(n, E))
    Z = zero_points(n, E, cuts)
    print(f"Gamma_{m}: |Z sample| = {len(Z)} (C5 concentrations + maximising convex combinations)")
    sup = {}
    for x in Z:
        sup.setdefault(tuple(sorted(i for i in range(n) if x[i])), 0)
        sup[tuple(sorted(i for i in range(n) if x[i]))] += 1
    for s, c in sorted(sup.items(), key=lambda t: (len(t[0]), t[0])):
        print(f"   support {list(s)}: {c} points")
    tot = 0
    for B in parity_blocks(n, 2 * d + 2):
        K = block_kernel(n, B, Z)
        tot += len(K)
        if len(B) > 1:
            print(f"   block size {len(B)} parity {tuple(b%2 for b in B[0])}: forced kernel dim {len(K)}")
    print(f"   total forced kernel dimension = {tot}")
