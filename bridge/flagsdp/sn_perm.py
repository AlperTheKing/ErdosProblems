#!/usr/bin/env python3
"""General S_k flag-permutation machinery for the kK1 (k independent roots, Aut=S_k) moment cone.
Used by the symmetry-reduction of the order-9 flag-SDP (GPT Pick A -> k=4; Q33 -> k=5). The roots of
kK1 are interchangeable, so S_k permutes them; M^{kK1}(H) is in the commutant for every H.
"""
import itertools
import numpy as np
import flag_engine as fe
import flag_sdp as fs


def kk1_flags(k, triangle_free=True):
    """Flags of type kK1 (k independent roots) with s=2 free vertices, on m=k+2 vertices."""
    sig = (k, [0] * k)
    return fs.enumerate_flags(sig, k + 2, triangle_free=triangle_free), sig


def apply_root_perm(A, g, m, k):
    """g: tuple length k = permutation of roots 0..k-1; free vertices k..m-1 fixed. Return new adj."""
    sigma = list(g) + list(range(k, m))
    Ap = [0] * m
    for a in range(m):
        for b in range(a + 1, m):
            if (A[a] >> b) & 1:
                u, v = sigma[a], sigma[b]
                Ap[u] |= 1 << v; Ap[v] |= 1 << u
    return Ap


def build_perm_matrices(flags, k):
    """The |S_k| flag-permutation matrices P_g (t x t) on the flag set."""
    m = k + 2; t = len(flags)
    flagkey = {fs.root_canonical(fm, fA, k): idx for idx, (fm, fA) in enumerate(flags)}
    Pmats = {}
    for g in itertools.permutations(range(k)):
        P = np.zeros((t, t), dtype=np.int64)
        for j, (fm, fA) in enumerate(flags):
            Ap = apply_root_perm(fA, g, m, k)
            key = fe.canonical(m, Ap, roots=k)
            i = flagkey.get(key, -1)
            if i < 0:
                raise RuntimeError(f"g={g} flag {j} maps outside flag set")
            P[i, j] = 1
        Pmats[g] = P
    return Pmats


# conjugacy-class representatives of S5 (cycle types) for the unit test
S5_CLASSES = {
    "1^5":   (0, 1, 2, 3, 4),
    "2.1^3": (1, 0, 2, 3, 4),
    "2^2.1": (1, 0, 3, 2, 4),
    "3.1^2": (1, 2, 0, 3, 4),
    "3.2":   (1, 2, 0, 4, 3),
    "4.1":   (1, 2, 3, 0, 4),
    "5":     (1, 2, 3, 4, 0),
}
S5_EXPECT_TRACE = {"1^5": 650, "2.1^3": 186, "2^2.1": 66, "3.1^2": 50, "3.2": 18, "4.1": 18, "5": 5}


if __name__ == "__main__":
    import sys
    k = 5
    flags, sig = kk1_flags(k)
    t = len(flags)
    print(f"{k}K1 flags on {k+2} vtx (triangle-free): t={t}  (GPT expects 650)", flush=True)
    Pmats = build_perm_matrices(flags, k)
    print("character traces chi(g) = #fixed flags (GPT unit test):", flush=True)
    ok = True
    for name, g in S5_CLASSES.items():
        tr = int(np.trace(Pmats[g])); exp = S5_EXPECT_TRACE[name]
        good = tr == exp; ok = ok and good
        print(f"  chi({name:6s}) = {tr:4d}   expect {exp:4d}   {'OK' if good else 'MISMATCH'}", flush=True)
    permok = all((Pmats[g].sum(0) == 1).all() and (Pmats[g].sum(1) == 1).all() for g in Pmats)
    print(f"all {len(Pmats)} are permutation matrices: {permok}", flush=True)
    print("5K1 UNIT TEST: " + ("PASS" if (ok and permok and t == 650) else "FAIL"), flush=True)
    print("DONE", flush=True)
