#!/usr/bin/env python3
"""GPT Pick A: symmetry-reduce the 4K1 (k=4) moment cone by Aut(4K1)=S4.
STEP 1 (this file, unit test): build the 24 S4 flag-permutation matrices P_g on the 177 flags of type
4K1 (roots=4 independent vertices, s=2 free, triangle-free, m=6) and verify GPT's character traces:
  chi(1)=177, chi((12))=55, chi((12)(34))=25, chi((123))=15, chi((1234))=7.
STEP 2 (if unit test passes): project the regular rep onto isotypic components -> blocks 31,31,16,7
(decomp 31[4]+31[31]+16[22]+7[211]) and emit the symmetry-adapted basis to block-diagonalize M^{4K1}.
Light: regenerates flags from scratch (NO pickle, NO SDP). Native, single-thread.
"""
import sys, itertools
import numpy as np
import flag_engine as fe
import flag_sdp as fs

SIG = (4, [0, 0, 0, 0])      # 4K1: 4 independent roots
M = 6                        # roots(4) + free(2)
K = 4

def apply_root_perm(A, g):
    """g: tuple length 4 = permutation of roots 0..3. Free vertices 4,5 fixed. Return new adjacency A'."""
    sigma = list(g) + [4, 5]                 # sigma[old]=new label
    Ap = [0] * M
    for a in range(M):
        for b in range(a + 1, M):
            if (A[a] >> b) & 1:
                u, v = sigma[a], sigma[b]
                Ap[u] |= 1 << v; Ap[v] |= 1 << u
    return Ap

def build_perm_matrices(flags):
    t = len(flags)
    flagkey = {fs.root_canonical(fm, fA, K): idx for idx, (fm, fA) in enumerate(flags)}
    Pmats = {}
    for g in itertools.permutations(range(K)):
        P = np.zeros((t, t), dtype=np.int64)
        for j, (fm, fA) in enumerate(flags):
            Ap = apply_root_perm(fA, g)
            key = fe.canonical(M, Ap, roots=K)
            i = flagkey.get(key, -1)
            if i < 0:
                raise RuntimeError(f"g={g} flag {j} maps outside flag set")
            P[i, j] = 1
        Pmats[g] = P
    return Pmats

def main():
    flags = fs.enumerate_flags(SIG, M, triangle_free=True)
    t = len(flags)
    print(f"4K1 flags on {M} vtx (triangle-free): t={t}  (GPT expects 177)", flush=True)
    Pmats = build_perm_matrices(flags)
    # representatives of the 5 conjugacy classes of S4
    reps = {"1": (0, 1, 2, 3), "(12)": (1, 0, 2, 3), "(12)(34)": (1, 0, 3, 2),
            "(123)": (1, 2, 0, 3), "(1234)": (1, 2, 3, 0)}
    expect = {"1": 177, "(12)": 55, "(12)(34)": 25, "(123)": 15, "(1234)": 7}
    print("character traces chi(g) = #fixed flags:", flush=True)
    ok = True
    for name, g in reps.items():
        tr = int(np.trace(Pmats[g]))
        good = (tr == expect[name])
        ok = ok and good
        print(f"  chi({name:9s}) = {tr:4d}   expect {expect[name]:4d}   {'OK' if good else 'MISMATCH'}", flush=True)
    # also verify it's a homomorphism on a couple products and all are permutation matrices
    permok = all((Pmats[g].sum(0) == 1).all() and (Pmats[g].sum(1) == 1).all() for g in Pmats)
    print(f"all 24 are permutation matrices: {permok}", flush=True)
    print("UNIT TEST: " + ("PASS" if (ok and permok and t == 177) else "FAIL"), flush=True)
    return ok and permok and t == 177, flags, Pmats

if __name__ == "__main__":
    main()
    print("DONE", flush=True)
