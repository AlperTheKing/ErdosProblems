#!/usr/bin/env python3
"""
Build the N=6 4-color SDP pieces ONCE and cache to disk (sparse), so the cvxpy solve can be
iterated cheaply (the dense build is ~6.6 min). Moment + PSD-localizer blocks are stored as
scipy.sparse CSC of shape (t*t, ns); constraint vectors as dense arrays.
"""
import time, pickle
import numpy as np
import scipy.sparse as sp
import flag_engine_kcol as kc
import flag_sdp_col as fs
import flag_margin_sdp as ms
import flag_psd_localizer as pl

t0 = time.time()
N = 6
TAU = 1.0/8
SMAX_LOC = 1
CACHE = "n6_cache.pkl"
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
ns = len(states)
tf = ms.kcolored_types(N, kmax=2)
print(f"states={ns} types={len(tf)} [{time.time()-t0:.0f}s]", flush=True)

dmono = ms.d_mono_vec(states); dedge = ms.d_edge_vec(states)
basic = np.stack([ms.side_sw0_vec(states, dmono, dedge), ms.side_sw1_vec(states, 0), ms.side_sw1_vec(states, 1)])
weakloc = np.stack(ms.localizer_vecs(states))
gsw = ms.margin_switch_vec(states)

def to_sparse(mats):
    # mats: list over states of (t,t) arrays -> CSC (t*t, ns)
    t = mats[0].shape[0]
    cols = [sp.csc_matrix(m.reshape(t*t, 1)) for m in mats]
    return sp.hstack(cols, format='csc'), t

print("building moment blocks ...", flush=True)
moment = []
tot_nnz = 0; tot_ent = 0
for (sigma, flags) in tf:
    if len(flags) < 2: continue
    mats = fs.P_sigma_col(states, sigma, flags)
    S, t = to_sparse(mats)
    tot_nnz += S.nnz; tot_ent += t*t*ns
    moment.append((S, t))
print(f"  {len(moment)} moment blocks, sparsity nnz/ent = {tot_nnz}/{tot_ent} = {tot_nnz/tot_ent:.4f} [{time.time()-t0:.0f}s]", flush=True)

print("building PSD localizer blocks ...", flush=True)
locblocks = pl.build_all_localizers(states, TAU, smax=SMAX_LOC)
loc = []
for (c, low, flags, mats) in locblocks:
    S, t = to_sparse(mats)
    loc.append((S, t, int(c), bool(low)))
print(f"  {len(loc)} localizer blocks [{time.time()-t0:.0f}s]", flush=True)

with open(CACHE, "wb") as f:
    pickle.dump(dict(ns=ns, dmono=dmono, dedge=dedge, basic=basic, weakloc=weakloc, gsw=gsw,
                     moment=moment, loc=loc, tau=TAU, band=(0.2486, 0.32)), f)
print(f"cached -> {CACHE} [{time.time()-t0:.0f}s] DONE", flush=True)
