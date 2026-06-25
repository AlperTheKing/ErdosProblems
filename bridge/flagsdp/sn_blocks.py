#!/usr/bin/env python3
"""General S_k symmetry-adapted block reduction for the kK1 moment cone (GPT Q33: k=5).
Young's orthogonal representation (built by BFS over the Cayley graph from adjacent transpositions) ->
isotypic first-copy projectors P^lam_11 = (d/|G|) sum_g rho_lam(g)[0,0] P_g -> B_lam (basis of its image,
dim = multiplicity m_lam). Reduction M^{kK1}(x)>=0 <=> B_lam^T M(x) B_lam >=0 for each irrep lam (exact,
sound: M^{kK1}(H) in the commutant for every H). VALIDATED by eig(M(H)) reconstruction to ~1e-12.
Saves sk_basis_<k>K1.pkl. Light: P_sigma only for a few sample states.
"""
import sys, itertools, pickle
import numpy as np
import flag_engine as fe
import flag_sdp as fs
import sn_perm as sp

# ---------- partitions, standard Young tableaux, Young orthogonal irreps ----------
def partitions(n):
    def gen(n, mx):
        if n == 0:
            yield []
            return
        for first in range(min(n, mx), 0, -1):
            for rest in gen(n - first, first):
                yield [first] + rest
    return [tuple(p) for p in gen(n, n)]

def syts(shape):
    """All standard Young tableaux of `shape` (row lengths). Tableau = tuple of rows (tuples of values 1..n)."""
    n = sum(shape); nrows = len(shape)
    results = []
    rows = [[] for _ in range(nrows)]
    def rec(v):
        if v > n:
            results.append(tuple(tuple(r) for r in rows)); return
        for r in range(nrows):
            if len(rows[r]) < shape[r] and (r == 0 or len(rows[r]) < len(rows[r - 1])):
                rows[r].append(v); rec(v + 1); rows[r].pop()
    rec(1)
    return results

def pos_of(T, val):
    for r, row in enumerate(T):
        for c, x in enumerate(row):
            if x == val:
                return r, c
    raise KeyError(val)

def rho_adjacent(shape, T_list, idx, i):
    """Young orthogonal matrix of the adjacent transposition s_i=(i,i+1) (1-indexed values)."""
    dim = len(T_list); R = np.zeros((dim, dim))
    for T in T_list:
        a = idx[T]
        rk, ck = pos_of(T, i); rk1, ck1 = pos_of(T, i + 1)
        d = (ck1 - rk1) - (ck - rk)
        R[a, a] = 1.0 / d
        if rk != rk1 and ck != ck1:
            # swap values i,i+1 -> another SYT
            Tp = tuple(tuple(i + 1 if x == i else (i if x == i + 1 else x) for x in row) for row in T)
            b = idx[Tp]
            R[b, a] = (1.0 - 1.0 / (d * d)) ** 0.5
    return R

def young_orthogonal(shape, k):
    """Return {g: rho(g)} for all g in S_k, g a tuple (g[x]=image of x), via BFS from adjacent transpositions."""
    T_list = syts(shape); idx = {T: i for i, T in enumerate(T_list)}; dim = len(T_list)
    gens = {}
    for i in range(1, k):                      # s_i = (i,i+1), 1-indexed; as 0-indexed perm tuple:
        g = list(range(k)); g[i - 1], g[i] = g[i], g[i - 1]
        gens[tuple(g)] = rho_adjacent(shape, T_list, idx, i)
    ident = tuple(range(k))
    rho = {ident: np.eye(dim)}
    frontier = [ident]
    while frontier:
        nf = []
        for p in frontier:
            for sg, Rs in gens.items():
                q = tuple(p[sg[x]] for x in range(k))   # q = p o s  (q[x]=p[s[x]])
                if q not in rho:
                    rho[q] = rho[p] @ Rs; nf.append(q)
        frontier = nf
    return rho, dim

# ---------- block builder + validation ----------
def build_blocks(flags, Pmats, k):
    t = len(flags); elems = list(Pmats.keys()); G = len(elems)
    blocks = {}; dims = {}
    for shape in partitions(k):
        rho, d = young_orthogonal(shape, k)
        Proj = np.zeros((t, t))
        for g in elems:
            Proj += rho[g][0, 0] * Pmats[g]
        Proj *= d / G
        U, s, _ = np.linalg.svd(Proj)
        r = int((s > 1e-8).sum())
        if r > 0:
            blocks[shape] = U[:, :r].copy(); dims[shape] = d
        print(f"  irrep {shape} dim={d}: multiplicity m={r}", flush=True)
    return blocks, dims

def validate(blocks, dims, flags, sig, k, sample):
    states = fe.enumerate_graphs(9, triangle_free=True)
    allok = True
    for gi in sample:
        n, A = states[gi]
        Mh = np.array(fs.P_sigma(n, [(n, A)], sig, flags)[0]); Mh = 0.5 * (Mh + Mh.T)
        full = np.sort(np.linalg.eigvalsh(Mh))
        red = []
        for shape, B in blocks.items():
            Mb = B.T @ Mh @ B; Mb = 0.5 * (Mb + Mb.T)
            red.extend(list(np.linalg.eigvalsh(Mb)) * dims[shape])
        red = np.sort(np.array(red))
        err = np.abs(full - red).max() if len(full) == len(red) else 9e9
        ok = err < 1e-7; allok = allok and ok
        print(f"  state {gi}: |eig|={len(full)} recon err={err:.2e} {'OK' if ok else 'FAIL'}", flush=True)
    return allok

def main(k=5):
    flags, sig = sp.kk1_flags(k)
    t = len(flags)
    print(f"{k}K1: t={t} flags", flush=True)
    Pmats = sp.build_perm_matrices(flags, k)
    blocks, dims = build_blocks(flags, Pmats, k)
    sizes = {str(s): B.shape[1] for s, B in blocks.items()}
    print(f"block sizes: {sizes}", flush=True)
    print("VALIDATION (eig reconstruction on sample graphs):", flush=True)
    val_ok = validate(blocks, dims, flags, sig, k, [0, 5, 17, 123, 800, 1500, 1896])
    tot = sum(B.shape[1] * dims[s] for s, B in blocks.items())
    print(f"sum m_lam*dim_lam = {tot} (must = {t})", flush=True)
    ok = val_ok and tot == t
    print(f"STEP RESULT: {'PASS' if ok else 'FAIL'}", flush=True)
    if ok:
        with open(f"sk_basis_{k}K1.pkl", "wb") as f:
            pickle.dump({'blocks': {str(s): B for s, B in blocks.items()},
                         'dims': {str(s): dims[s] for s in dims}}, f, protocol=4)
        print(f"saved sk_basis_{k}K1.pkl", flush=True)

if __name__ == "__main__":
    main(5)
    print("DONE", flush=True)
