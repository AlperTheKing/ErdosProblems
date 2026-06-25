#!/usr/bin/env python3
"""
Z2 symmetry (A<->B side swap) of the N=6 4-color flag SDP.
tau swaps colors 0<->2 (A_L<->B_L), 1<->3 (A_H<->B_H): preserves d_mono, d_edge, all switches,
localizers (Low/High fixed, sides swapped). The problem is tau-invariant and convex, so an optimal
tau-symmetric x exists -> restrict to x_H = x_{tau H} (orbit variables). Halves the free variables.
(Stage B: block-diagonalize the moment matrices by the tau-action on flags to split the 210-block.)

This module builds:
  - state index permutation pi (involution) from the tau color-swap + recanonicalization,
  - the orbit reduction matrix O (ns x n_orbits, 0/1), x = O @ y for tau-symmetric x.
"""
import numpy as np
import scipy.sparse as sp
import flag_engine as fe, flag_engine_col as fc, flag_engine_kcol as kc

SWAP = {0: 2, 2: 0, 1: 3, 3: 1}   # tau on colors


def build_states_and_index(N=6):
    states = kc.enumerate_kcolored(N, 4, triangle_free=True)
    key2idx = {}
    for i, (n, A, col) in enumerate(states):
        key2idx[fc.canonical_col(n, A, col, roots=0)] = i
    return states, key2idx


def tau_perm(states, key2idx):
    """Involution pi over state indices induced by the A<->B color swap."""
    pi = np.empty(len(states), dtype=np.int64)
    for i, (n, A, col) in enumerate(states):
        tcol = [SWAP[c] for c in col]
        pi[i] = key2idx[fc.canonical_col(n, A, tcol, roots=0)]
    return pi


def orbit_reduction(pi):
    """Return (O, reps, n_fixed). O is ns x n_orbits 0/1 with x = O @ y for tau-symmetric x;
    each orbit (fixed point or 2-cycle) is one column."""
    ns = len(pi)
    seen = np.zeros(ns, dtype=bool)
    cols = []; reps = []; n_fixed = 0
    rows_i = []; cols_j = []
    j = 0
    for i in range(ns):
        if seen[i]:
            continue
        k = int(pi[i])
        if k == i:
            seen[i] = True; n_fixed += 1
            rows_i.append(i); cols_j.append(j); reps.append(i)
        else:
            seen[i] = True; seen[k] = True
            rows_i.append(i); cols_j.append(j)
            rows_i.append(k); cols_j.append(j)
            reps.append(i)
        j += 1
    O = sp.csc_matrix((np.ones(len(rows_i)), (rows_i, cols_j)), shape=(ns, j))
    return O, np.array(reps), n_fixed


if __name__ == "__main__":
    import time
    t0 = time.time()
    states, key2idx = build_states_and_index(6)
    print(f"states={len(states)} [{time.time()-t0:.0f}s]")
    pi = tau_perm(states, key2idx)
    assert np.all(pi[pi] == np.arange(len(pi))), "pi not an involution!"
    n_self = int(np.sum(pi == np.arange(len(pi))))
    O, reps, n_fixed = orbit_reduction(pi)
    print(f"tau involution OK; self-symmetric states={n_self}; orbits={O.shape[1]} "
          f"(={n_fixed} fixed + {(len(states)-n_fixed)//2} pairs)  -> var reduction {len(states)}/{O.shape[1]} = {len(states)/O.shape[1]:.2f}x")
    print(f"[{time.time()-t0:.0f}s] DONE")
