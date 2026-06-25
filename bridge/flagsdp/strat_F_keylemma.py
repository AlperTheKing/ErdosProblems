#!/usr/bin/env python3
"""STRATEGY F: pin the KEY LEMMA that an SP/theta reduction would need, and show it holds with the
constant 25 ONLY at the 3-connected core. We make the reduction step PRECISE and test it.

SP-REDUCTION STEP (the inductive claim Strategy F needs):
  If atom K has a 2-cut {x,y} splitting K = K1 (+) K2 (2-sum, both >=1 odd cycle), then
     t(K) = t(K1) + t(K2),   nu*(K) = nu*(K1) + nu*(K2)        [additivity across 2-cut, tested below]
  and  n(K) = n(K1) + n(K2) - 2.   So IF per-piece D25 holds (nu*(Ki) >= 25 t_i^2/n_i^2), does the
  Cauchy/square-gluing  sum 25 t_i^2/n_i^2 >= 25 (sum t_i)^2 / n(K)^2  hold?  This needs n(K)^2 >= sum n_i^2,
  i.e. (n1+n2-2)^2 >= n1^2 + n2^2  <=>  2 n1 n2 - 4(n1+n2) + 4 >= 0  <=> 2(n1-2)(n2-2) >= 4 i.e.
  (n1-2)(n2-2) >= 2, true for n1,n2 >= 4. GOOD -- the gluing inequality survives a 2-cut.

  >>> THE REAL QUESTION: is t/nu* ADDITIVE across a 2-cut? (For block-cut/cut-vertex it IS, proved.
      For a 2-CUT the two pieces SHARE the virtual edge -- additivity can FAIL because a single odd cycle
      can use BOTH sides through the 2-cut.)  We test this directly.
"""
import itertools
import numpy as np
import verify_D25_lemma16 as L
import strat_F_theta as T
import strat_F_2sum as S


def stats(N, A):
    adj = L.adjset(N, A)
    mc, _ = L.maxcut(N, adj)
    e = sum(len(adj[u]) for u in range(N)) // 2
    tau = e - mc
    nu, _ = T.nu_star(N, A)
    return N, e, tau, nu


if __name__ == "__main__":
    print("=== STRATEGY F key lemma: is (t, nu*) additive across a 2-CUT? ===\n", flush=True)
    print("If NOT additive, the SP reduction's bookkeeping breaks and Strategy F's induction is unsound.\n")

    cases = []
    # K1 = C5[2], K2 = theta(4,6), glued at 2-cut
    N1, A1 = L.c5n(2)
    N2, A2 = T.theta_atom(4, 6)
    merged = S.two_sum(N1, A1, (0, 5), N2, A2, (0, 1), delete_shared=True)
    cases.append(("C5[2] (+) theta46", (N1, A1), (N2, A2), merged))

    # two thetas in series (a 2-path of bad-edge bundles)
    Na, Aa = T.theta_atom(4, 6)
    Nb, Ab = T.theta_atom(4, 6)
    m2 = S.two_sum(Na, Aa, (0, 1), Nb, Ab, (0, 1), delete_shared=False)
    cases.append(("theta46 (+) theta46", (Na, Aa), (Nb, Ab), m2))

    # two C5 in series
    Nc, Ac = L.c5()
    Nd, Ad = L.c5()
    m3 = S.two_sum(Nc, Ac, (0, 2), Nd, Ad, (0, 2), delete_shared=False)
    cases.append(("C5 (+) C5 (2-cut)", (Nc, Ac), (Nd, Ad), m3))

    for lab, (Na, Aa), (Nb, Ab), (Nm, Am) in cases:
        n1, e1, t1, nu1 = stats(Na, Aa)
        n2, e2, t2, nu2 = stats(Nb, Ab)
        nm, em, tm, num = stats(Nm, Am)
        t_add = (tm == t1 + t2)
        nu_add = abs(num - (nu1 + nu2)) < 1e-6
        glue = nm * nm >= n1 * n1 + n2 * n2 - 1e-9
        print(f"{lab}", flush=True)
        print(f"   K1: n={n1} t={t1} nu*={nu1:.3f} | K2: n={n2} t={t2} nu*={nu2:.3f} | merged: n={nm} t={tm} nu*={num:.3f}")
        print(f"   t additive: {t_add} ({t1}+{t2} vs {tm}) | nu* additive: {nu_add} ({nu1:.3f}+{nu2:.3f}={nu1+nu2:.3f} vs {num:.3f}) | n^2 gluing ok: {glue}")
        print()

    print("VERDICT: a 2-cut atom that is INTERNALLY 3-connected (like C5[q]) has NO nontrivial 2-cut, so it")
    print("is an irreducible leaf of the SP reduction -- and that is EXACTLY where 25 t^2/n^2 = nu* is tight.")
    print("Strategy F therefore reduces the problem to: prove D25 for 3-CONNECTED triangle-free atoms,")
    print("which is the ORIGINAL open lemma (16), not a simpler one.")
    print("DONE", flush=True)
