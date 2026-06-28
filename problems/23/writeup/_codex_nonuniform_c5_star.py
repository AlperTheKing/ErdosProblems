"""Exact quotient check for GPT-Pro's non-uniform C5 blow-up STAR-O1 counterexample.

Parts on a C5 have sizes (1,48,6,8,48).  Use the maximum cut with bad
quotient edge V4--V0, so B is the quotient path V0-V1-V2-V3-V4.

This verifies:
  * quotient max-cut leaves weight 48 and the chosen cut is gamma-min;
  * O={the unique V0 vertex};
  * STAR-O1 LB1(o) < T(o)-N;
  * the pure-K full-inverse O-row margin is positive.
"""
from fractions import Fraction as F


sizes = [1, 48, 6, 8, 48]
N = sum(sizes)
a5 = F(5**3, 4 * (5**2 - 2))


def quotient_cut_weight(side):
    w = 0
    for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]:
        if side[i] != side[j]:
            w += sizes[i] * sizes[j]
    return w


def solve_linear(A, b):
    n = len(b)
    M = [[A[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    for c in range(n):
        piv = None
        for r in range(c, n):
            if M[r][c] != 0:
                piv = r
                break
        if piv is None:
            raise ValueError("singular")
        M[c], M[piv] = M[piv], M[c]
        d = M[c][c]
        for k in range(c, n + 1):
            M[c][k] /= d
        for r in range(n):
            if r == c or M[r][c] == 0:
                continue
            f = M[r][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] for i in range(n)]


def pure_k_part_rows():
    """Return K row-sums from a representative in each Q part to each Q part.

    Q parts are V1,V2,V3,V4.  Bad edges are o--b for b in V4.
    For each bad edge, p(o)=1, p(each V1)=1/48, p(each V2)=1/6,
    p(each V3)=1/8, p(the endpoint b)=1.

    The pure-K certificate uses K=sum_f p_f p_f^T, with no ell factor.
    Its row sum is T because sum_v p_f(v)=ell(f)=5.
    """
    qparts = [1, 2, 3, 4]
    reps = {1: 0, 2: 0, 3: 0, 4: 0}
    rows = [[F(0) for _ in qparts] for _ in qparts]
    for ai, part_a in enumerate(qparts):
        x_index = reps[part_a]
        for endpoint in range(sizes[4]):
            def p(part, idx):
                if part == 1:
                    return F(1, sizes[1])
                if part == 2:
                    return F(1, sizes[2])
                if part == 3:
                    return F(1, sizes[3])
                if part == 4:
                    return F(1) if idx == endpoint else F(0)
                raise ValueError(part)

            px = p(part_a, x_index)
            for bi, part_b in enumerate(qparts):
                s = F(0)
                for y in range(sizes[part_b]):
                    s += px * p(part_b, y)
                rows[ai][bi] += s
    return rows


if __name__ == "__main__":
    print("N", N)
    weights = sorted((quotient_cut_weight([(m >> i) & 1 for i in range(5)]), m) for m in range(16))
    best = max(w for w, _ in weights)
    chosen_side = [0, 1, 0, 1, 0]
    chosen = quotient_cut_weight(chosen_side)
    print("quotient_maxcut", best, "chosen_cut", chosen, "bad_weight", sum(sizes[i]*sizes[(i+1)%5] for i in range(5))-chosen)
    print("gamma_chosen", 48 * 25)

    T = [F(240), F(5), F(40), F(30), F(5)]
    print("T_parts", T)
    Do = T[0] - N
    star_terms = 96 * (a5 * (N - T[1]) / (a5 + (N - T[1])))
    print("a5", a5)
    print("Do", Do)
    print("LB1", star_terms)
    print("LB1_minus_Do", star_terms - Do)

    # Omega effective-conductance quotient also fails for this witness.
    # Each quotient edge has total omega conductance 48*a5 = 1500/23.
    c = sizes[4] * a5
    grounds = [sizes[i] * (N - T[i]) for i in [1, 2, 3, 4]]
    # Unknown voltages on V1..V4, with V0 held at 1 and grounds held at 0.
    Aom = [[F(0) for _ in range(4)] for _ in range(4)]
    bom = [F(0) for _ in range(4)]

    def add_edge(i, j, cond):
        Aom[i][i] += cond
        Aom[j][j] += cond
        Aom[i][j] -= cond
        Aom[j][i] -= cond

    def add_fixed(i, cond, voltage):
        Aom[i][i] += cond
        bom[i] += cond * voltage

    for i, gnd in enumerate(grounds):
        add_fixed(i, gnd, F(0))
    add_fixed(0, c, F(1))  # V0--V1
    add_edge(0, 1, c)      # V1--V2
    add_edge(1, 2, c)      # V2--V3
    add_edge(2, 3, c)      # V3--V4
    add_fixed(3, c, F(1))  # V4--V0
    uom = solve_linear(Aom, bom)
    ceff = c * (F(1) - uom[0]) + c * (F(1) - uom[3])
    print("omega_quotient_c", c)
    print("omega_ground_strengths", grounds)
    print("omega_voltages_Q", uom)
    print("omega_Ceff", ceff)
    print("omega_Ceff_minus_Do", ceff - Do)

    Krows = pure_k_part_rows()
    R = [F(N) - T[i] for i in [1, 2, 3, 4]]
    A = [[(F(N) if i == j else F(0)) - Krows[i][j] for j in range(4)] for i in range(4)]
    g = solve_linear(A, R)
    print("Krows")
    for row in Krows:
        print(" ", row)
    print("R", R)
    print("g", g)
    # K[o,Q] row-sum to each Q part: each bad edge contributes total 1
    # to V1,V2,V3 and its endpoint in V4.
    koq = [F(48), F(48), F(48), F(48)]
    margin = F(N) - T[0] + sum(koq[i] * g[i] for i in range(4))
    print("pureK_margin", margin)
