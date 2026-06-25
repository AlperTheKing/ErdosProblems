#!/usr/bin/env python3
"""Validate generalized egr_gen reduces to the C5-specialized egr_and_gr (must match exactly on the C5
type), on a small subset of n=9 states (light under load). Also sanity-check the disjoint product:
mean(EG) should ~ mean(E)*mean(GR) on a uniform graphon-ish subset is NOT exact per-state, so we only
assert egr_gen == egr_and_gr (the soundness-critical identity)."""
import sys, pickle
import numpy as np
import density_slice as ds
import flag_cutgen as fc

C = pickle.load(open("cache_n9.pkl", "rb"))
states = C["states"]; t = C["t"]; C5 = C["C5"]
classes5 = fc.profile_classes(*C5)
sup_full = list(C["sup"])
sub = sup_full[:40]                                  # light
# an arbitrary-but-fixed profile vector over the C5 classes
nc = len(classes5)
p = np.array([0.5 + 0.3 * np.cos(i) for i in range(nc)])   # deterministic, in (0,1)-ish
p = np.clip(p, 0.05, 0.95)

EG1, GR1 = ds.egr_and_gr(states, C5, p, t, classes5, sub)
EG2, GR2 = ds.egr_gen(states, C5, p, t, classes5, sub)
dEG = max(abs(EG1[i] - EG2[i]) for i in sub)
dGR = max(abs(GR1[i] - GR2[i]) for i in sub)
print(f"C5: egr_gen vs egr_and_gr  maxdiff EG={dEG:.2e}  GR={dGR:.2e}  (over {len(sub)} states)", flush=True)
print("PASS" if (dEG < 1e-12 and dGR < 1e-12) else "FAIL", flush=True)
print("DONE", flush=True)
