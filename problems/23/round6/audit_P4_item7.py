"""audit_P4_item7 — attack P4.md's headline: item 7 refuted by W8/W9/W10 on Gamma_20.

Independent exact verification of every number in P4.md's witness table, plus the two hypotheses
of item 7, plus the claim that no bound_k closes them, plus the claim that sliding b over the
whole circle does not repair it, plus psi/ARCBOUND (so that Erdos 23 itself is untouched).
"""
import sys
from fractions import Fraction as F
from audit_P4_core import (adj_matrix, normalise, W_of, T_of, A_of, A_direct, g_of, m_of,
                           m_as_cut, bound_k, var_g, arcbound, psi_bruteforce, mono,
                           sliding_third_arcs, sliding_half_arcs, far_set, dist)

ONE25 = F(1, 25)

WIT = {
    "W8":  (20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    "W9":  (20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
    "W10": (20, [0, 5, 5, 0, 0, 0, 0, 6, 4, 5, 0, 0, 0, 0, 5, 4, 6, 0, 0, 0]),
}

# P4.md's claimed values
CLAIM = {
    "W8":  dict(W=F(14, 75), A=F(403, 9000), minm=F(2, 45),  psi=F(7, 225), ming=F(1, 3)),
    "W9":  dict(W=F(3, 16),  A=F(3, 64),     minm=F(3, 64),  psi=F(1, 32),  ming=F(3, 8)),
    "W10": dict(W=F(3, 16),  A=F(73, 1600),  minm=F(7, 160), psi=F(1, 32),  ming=F(7, 20)),
}


def report(name, M, w):
    adj = adj_matrix(M)
    x = normalise(w)
    supp = [i for i in range(M) if x[i] != 0]
    g = g_of(x, adj)
    W = W_of(x, adj)
    T = T_of(x, adj, M)
    A = A_of(x, adj, M)
    Ad = A_direct(x, adj, M)
    V = var_g(x, adj)
    ms = {b: m_of(b, x, adj, M) for b in supp}
    ms_cut = {b: m_as_cut(b, x, adj, M) for b in supp}
    minm = min(ms.values())
    ab = arcbound(x, adj, M)
    ps = psi_bruteforce(x, adj, M)

    print(f"===== {name}  Gamma_{M}  weights {w}  (q={sum(w)}) =====")
    print(f"  support            {supp}   ({len(supp)} atoms)")
    print(f"  g on support       {[str(g[b]) for b in supp]}")
    print(f"  min_supp g         {min(g[b] for b in supp)} = {float(min(g[b] for b in supp)):.6f}"
          f"   (>1/3? {min(g[b] for b in supp) > F(1,3)})")
    print(f"  W                  {W} = {float(W):.6f}   in (0.12,0.2)? "
          f"{F(3,25) < W < F(1,5)}")
    print(f"  T                  {T} = {float(T):.6f}   T/W = {float(T/W):.6f}")
    print(f"  A = W-2T           {A} = {float(A):.6f}    (direct double integral: {Ad}) "
          f"match={A == Ad}")
    print(f"  Var(g)             {V} = {float(V):.6f}")
    print(f"  m(b) via formula   {[str(ms[b]) for b in supp]}")
    print(f"  m(b) as a CUT      {[str(ms_cut[b]) for b in supp]}   agree={ms == ms_cut}")
    print(f"  min_b m(b)         {minm} = {float(minm):.6f}   > 1/25? {minm > ONE25}")
    print(f"  ARCBOUND           {ab} = {float(ab):.6f}   <= 1/25? {ab <= ONE25}")
    print(f"  psi (all cuts)     {ps} = {float(ps):.6f}   ARCBOUND==psi? {ab == ps}")

    # --- item 7's two hypotheses, verbatim
    h1 = 2 * T < W - ONE25
    h2 = 4 * W * W + V < W - ONE25
    print(f"  HYP1  2T < W-1/25  : {2*T} < {W-ONE25}  -> {h1}   [equivalently A>1/25: {A > ONE25}]")
    print(f"  HYP2  4W^2+Var < W-1/25 : {4*W*W+V} < {W-ONE25} -> {h2} "
          f"[equivalently bound_0>1/25]")

    # --- the whole hierarchy
    bs = {k: bound_k(k, x, adj, M) for k in [0, 1, 2, 3, 5, 10, 50, 200, 1000]}
    print("  bound_k            " + "  ".join(f"k={k}:{float(v):.6f}" for k, v in bs.items()))
    ok = all(v > ONE25 for v in bs.values())
    print(f"  every listed bound_k > 1/25 ? {ok}     (structural floor: bound_k >= min_b m(b) "
          f"= {float(minm):.6f})")
    # bound_0 must equal W - int g^2
    b0_alt = W - sum(x[b] * g[b] ** 2 for b in range(M))
    print(f"  bound_0 == W - int g^2 ? {bound_k(0,x,adj,M) == b0_alt}  ({b0_alt})")

    # --- sliding the neighbourhood cut over the WHOLE circle
    third = min(mono(x, adj, inA) for inA in sliding_third_arcs(M))
    half = min(mono(x, adj, inA) for inA in sliding_half_arcs(M))
    print(f"  min over ALL 1/3-arcs (b anywhere on the circle): {third} = {float(third):.6f} "
          f" > 1/25? {third > ONE25}")
    print(f"  min over ALL half-arcs                          : {half} = {float(half):.6f} "
          f" > 1/25? {half > ONE25}")
    print(f"  min(half,third)  = {min(half,third)} = {float(min(half,third)):.6f}  "
          f"<= 1/25? {min(half,third) <= ONE25}")

    # --- against P4's claimed numbers
    if name not in CLAIM:
        print()
        return dict(W=W, A=A, minm=minm, psi=ps, ab=ab, h1=h1, h2=h2, third=third, half=half)
    c = CLAIM[name]
    print(f"  CLAIM CHECK  W:{W == c['W']}  A:{A == c['A']}  min_m:{minm == c['minm']}  "
          f"psi:{ps == c['psi']}  min_g:{min(g[b] for b in supp) == c['ming']}")
    print()
    return dict(W=W, A=A, minm=minm, psi=ps, ab=ab, h1=h1, h2=h2, third=third, half=half)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        M = int(sys.argv[1])
        w = [int(t) for t in sys.argv[2].split(",")]
        report("CLI", M, w)
    else:
        res = {}
        for name, (M, w) in WIT.items():
            res[name] = report(name, M, w)
        print("SUMMARY (item 7 is refuted by a witness iff W in (0.12,0.2), HYP1, HYP2, "
              "and min_b m(b) > 1/25):")
        for name, r in res.items():
            refutes = (F(3, 25) < r['W'] < F(1, 5)) and r['h1'] and r['h2'] and r['minm'] > ONE25
            print(f"  {name}: refutes item 7 = {refutes};  psi = {r['psi']} "
                  f"({float(r['psi']):.6f}) <= 1/25 so Erdos 23 untouched: {r['psi'] <= ONE25}")
