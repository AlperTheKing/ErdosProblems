#!/usr/bin/env python3
"""GPT Pick A, STEP 2: build the S4 symmetry-adapted basis that block-diagonalizes the 177x177 4K1
moment cone into blocks 31,31,16,7 (irreps [4],[31],[22],[211]; [1111] absent), and VALIDATE it on
sample order-9 graphs: M^{4K1}(H) is in the commutant of the S4 flag-rep, so
   eig(M(H)) == union over irreps lambda of eig(B_lambda^T M(H) B_lambda), each repeated dim(lambda).
If validation passes, B = {B_lambda} reduces the PSD constraint M^{4K1}(x)>=0  <=>  B_l^T M(x) B_l >= 0
for each l (sizes 31,31,16,7) -- exact, sound (M(x) in commutant for ALL x). Saves s4_basis_4k1.pkl.
Light: regenerates flags + builds P_g (already unit-tested); P_sigma for a few sample H only.
"""
import sys, itertools, pickle
import numpy as np
import flag_engine as fe
import flag_sdp as fs
import s4_block_4k1 as s4

SIG = (4, [0, 0, 0, 0]); M = 6; K = 4

# ---- S4 irreducible representations (real orthogonal) ----
def perm_matrix(n, g):
    """4x4 (or nxn) permutation matrix: (rho(g)v)_i = v_{g^{-1}(i)} => P[g[j],j]=1."""
    P = np.zeros((n, n))
    for j in range(n):
        P[g[j], j] = 1.0
    return P

def orth_sumzero(n):
    """n x (n-1) matrix with orthonormal columns spanning {sum x_i = 0}."""
    A = np.eye(n) - np.ones((n, n)) / n
    w, V = np.linalg.eigh(A)
    cols = [V[:, i] for i in range(n) if w[i] > 0.5]   # eigenvalue 1 (mult n-1)
    return np.column_stack(cols)

def sign_perm(g):
    # parity of permutation g (tuple)
    seen = [False] * len(g); s = 1
    for i in range(len(g)):
        if seen[i]:
            continue
        j = i; clen = 0
        while not seen[j]:
            seen[j] = True; j = g[j]; clen += 1
        if clen % 2 == 0:
            s = -s
    return s

def s3_image(g):
    """Map g in S4 to its action on the 3 pair-partitions -> permutation of {0,1,2}."""
    parts = [frozenset([frozenset([0, 1]), frozenset([2, 3])]),
             frozenset([frozenset([0, 2]), frozenset([1, 3])]),
             frozenset([frozenset([0, 3]), frozenset([1, 2])])]
    pidx = {p: i for i, p in enumerate(parts)}
    tau = [0, 0, 0]
    for a, p in enumerate(parts):
        gp = frozenset(frozenset(g[x] for x in pair) for pair in p)
        tau[pidx[gp]] = a       # tau as image: where a goes... build proper perm
    # build tau so that tau[i] = image of i
    tau2 = [0, 0, 0]
    for a, p in enumerate(parts):
        gp = frozenset(frozenset(g[x] for x in pair) for pair in p)
        tau2[a] = pidx[gp]
    return tuple(tau2)

def build_irreps():
    B4 = orth_sumzero(4)        # 4x3
    B3 = orth_sumzero(3)        # 3x2
    irreps = {}
    elems = list(itertools.permutations(range(4)))
    # [4] trivial
    irreps['[4]'] = {g: np.array([[1.0]]) for g in elems}
    # [31] standard
    irreps['[31]'] = {g: B4.T @ perm_matrix(4, g) @ B4 for g in elems}
    # [211] = [31] tensor sign
    irreps['[211]'] = {g: sign_perm(g) * (B4.T @ perm_matrix(4, g) @ B4) for g in elems}
    # [22] via S4->S3 on pair-partitions, 2-dim standard rep of S3
    irreps['[22]'] = {g: B3.T @ perm_matrix(3, s3_image(g)) @ B3 for g in elems}
    return irreps

def check_irreps(irreps):
    """Verify characters per conjugacy class against the S4 table."""
    reps = {"1": (0, 1, 2, 3), "(12)": (1, 0, 2, 3), "(12)(34)": (1, 0, 3, 2),
            "(123)": (1, 2, 0, 3), "(1234)": (1, 2, 3, 0)}
    table = {'[4]': {"1": 1, "(12)": 1, "(12)(34)": 1, "(123)": 1, "(1234)": 1},
             '[31]': {"1": 3, "(12)": 1, "(12)(34)": -1, "(123)": 0, "(1234)": -1},
             '[22]': {"1": 2, "(12)": 0, "(12)(34)": 2, "(123)": -1, "(1234)": 0},
             '[211]': {"1": 3, "(12)": -1, "(12)(34)": -1, "(123)": 0, "(1234)": 1}}
    ok = True
    for lab, mats in irreps.items():
        for cname, g in reps.items():
            tr = np.trace(mats[g]); exp = table[lab][cname]
            if abs(tr - exp) > 1e-9:
                ok = False; print(f"  IRREP CHAR MISMATCH {lab} {cname}: {tr:.3f} vs {exp}", flush=True)
        # orthogonality of the rep matrices (should be orthogonal)
        for g in [reps["(1234)"], reps["(123)"]]:
            R = mats[g]
            if np.abs(R @ R.T - np.eye(R.shape[0])).max() > 1e-9:
                ok = False; print(f"  IRREP NOT ORTHOGONAL {lab} {g}", flush=True)
    return ok

def build_blocks(flags, Pmats, irreps):
    """B_lambda = orthonormal basis of Image((d/24) sum_g rho_lambda(g)[0,0] P_g). dim = m_lambda."""
    t = len(flags); elems = list(Pmats.keys())
    blocks = {}
    for lab, mats in irreps.items():
        d = mats[elems[0]].shape[0]
        Proj = np.zeros((t, t))
        for g in elems:
            Proj += mats[g][0, 0] * Pmats[g]
        Proj *= d / len(elems)
        # orthonormal basis of column space of Proj (it's a projector onto first-copy isotypic)
        U, s, _ = np.linalg.svd(Proj)
        r = int((s > 1e-8).sum())
        blocks[lab] = U[:, :r].copy()
        print(f"  block {lab}: dim(B)={r}", flush=True)
    return blocks

def Msigma_one(n, A, flags):
    return np.array(fs.P_sigma(n, [(n, A)], SIG, flags)[0])

def validate(blocks, flags):
    """For sample order-9 graphs, check eig(M) == union_lambda eig(B_l^T M B_l) x dim(lambda)."""
    dimm = {'[4]': 1, '[31]': 3, '[22]': 2, '[211]': 3}
    states = fe.enumerate_graphs(9, triangle_free=True)
    import random
    idxs = [0, 5, 17, 123, 800, 1500, len(states) - 1]
    allok = True
    for gi in idxs:
        n, A = states[gi]
        Mh = Msigma_one(n, A, flags); Mh = 0.5 * (Mh + Mh.T)
        full = np.sort(np.linalg.eigvalsh(Mh))
        red = []
        for lab, B in blocks.items():
            Mb = B.T @ Mh @ B; Mb = 0.5 * (Mb + Mb.T)
            ev = np.linalg.eigvalsh(Mb)
            red.extend(list(ev) * dimm[lab])
        red = np.sort(np.array(red))
        err = np.abs(full - red).max() if len(full) == len(red) else 9e9
        ok = err < 1e-7
        allok = allok and ok
        print(f"  state {gi}: |eig(M)|={len(full)} reconstructed err={err:.2e} {'OK' if ok else 'FAIL'}", flush=True)
    return allok

def main():
    flags = fs.enumerate_flags(SIG, M, triangle_free=True)
    Pmats = s4.build_perm_matrices(flags)
    irreps = build_irreps()
    print("irrep character check:", "OK" if check_irreps(irreps) else "FAIL", flush=True)
    blocks = build_blocks(flags, Pmats, irreps)
    sizes = {lab: B.shape[1] for lab, B in blocks.items()}
    print(f"block sizes: {sizes}  (expect [4]:31 [31]:31 [22]:16 [211]:7)", flush=True)
    sz_ok = sizes == {'[4]': 31, '[31]': 31, '[22]': 16, '[211]': 7}
    print("VALIDATION (block-diagonalization on sample graphs):", flush=True)
    val_ok = validate(blocks, flags)
    print(f"STEP2 RESULT: sizes_ok={sz_ok} blockdiag_ok={val_ok} -> {'PASS' if (sz_ok and val_ok) else 'FAIL'}", flush=True)
    if sz_ok and val_ok:
        with open("s4_basis_4k1.pkl", "wb") as f:
            pickle.dump({lab: B for lab, B in blocks.items()}, f, protocol=4)
        print("saved s4_basis_4k1.pkl", flush=True)

if __name__ == "__main__":
    main()
    print("DONE", flush=True)
