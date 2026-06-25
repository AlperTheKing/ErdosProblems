#!/usr/bin/env python3
"""Compute the Z2 orbit-reduction matrix O once and cache it (O is ns x n_orb sparse)."""
import time, pickle
import scipy.sparse as sp
import flag_symmetry as fsym

t0 = time.time()
states, key2idx = fsym.build_states_and_index(6)
pi = fsym.tau_perm(states, key2idx)
O, reps, n_fixed = fsym.orbit_reduction(pi)
print(f"ns={len(states)} orbits={O.shape[1]} ({n_fixed} fixed) [{time.time()-t0:.0f}s]", flush=True)
sp.save_npz("sym_O.npz", O)
with open("sym_meta.pkl", "wb") as f:
    pickle.dump(dict(pi=pi, reps=reps, n_fixed=n_fixed, ns=len(states), n_orb=O.shape[1]), f)
print(f"saved sym_O.npz + sym_meta.pkl [{time.time()-t0:.0f}s] DONE", flush=True)
