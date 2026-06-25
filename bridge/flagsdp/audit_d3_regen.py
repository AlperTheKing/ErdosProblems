import pickle, time
from math import comb
from fractions import Fraction as F
import numpy as np
import prove_cert as pc
import flag_exact as fx
from certify_dual import regen, LO, HI, T

t0=time.time()
d = pickle.load(open("dual_cert_n9.audit_backup.pkl","rb"))
prov = d["prov"]; ndix=d["ndix"]; nmix=d["nmix"]
lam=[F(s) for s in d["lam"]]; gam=[F(s) for s in d["gam"]]
mu=F(d["mu"]); nu=F(d["nu"])
delta_saved=F(d["maxPhi_num"], d["maxPhi_den"])

# Load cache (provides moments, states via cutting_plane? We need the SAME states ordering)
C = pc.load(9)
print("loaded cache, t=%.0fs"%(time.time()-t0), flush=True)

# Reproduce states/dedge the SAME way certify_dual does: via cutting_plane
states, ns, dedge, t, rows, prov2, v = pc.cutting_plane(C, maxit=15, target=-1e-6, mom_maxvecs=8, verbose=False)
print("cutting_plane done ns=%d t=%.0fs eta=%+.3e"%(ns, time.time()-t0, v), flush=True)

# Sanity: prov from cutting_plane must match saved prov (same atom ordering for regen by index)
print("prov2 len:", len(prov2), " saved prov len:", len(prov))
same = (prov2 == prov)
print("prov ordering identical to saved:", same)
if not same:
    # check the indices we actually use
    print("WARNING prov differs; checking used indices")
    for i in ndix:
        if prov2[i]!=prov[i]: print("  ndix mismatch at",i)
    for i in nmix:
        if prov2[i]!=prov[i]: print("  nmix mismatch at",i)

edens = fx.edge_density_exact(states)
print("nstates =", len(states))

# Build Phi independently using SAVED multipliers and regen over prov2 (the live atoms)
Phi = [mu*(edens[i]-LO) + nu*(HI-edens[i]) for i in range(ns)]
for c,i in enumerate(ndix):
    if lam[c]!=0:
        vals = regen(C, states, prov2, i)
        for j in range(ns):
            if vals[j]!=0: Phi[j]+=lam[c]*vals[j]
for c,i in enumerate(nmix):
    if gam[c]!=0:
        vals = regen(C, states, prov2, i)
        for j in range(ns):
            if vals[j]!=0: Phi[j]+=gam[c]*vals[j]

mx = max(Phi); arg=int(np.argmax([float(p) for p in Phi]))
print("INDEP max_H Phi =", float(mx), "=", mx, flush=True)
print("argmax state:", arg)
print("delta_saved   =", float(delta_saved), "=", delta_saved)
print("INDEP max == delta_saved:", mx==delta_saved)
print("INDEP max <= delta_saved:", mx<=delta_saved)
print("INDEP max < 1/450:", mx < F(1,450))
print("diff (mx - delta_saved) =", mx-delta_saved, "=", float(mx-delta_saved))
print("elapsed %.0fs"%(time.time()-t0))
