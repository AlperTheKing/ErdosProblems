import pickle, time
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

C = pc.load(9)
# Get states deterministically (NOT via cutting_plane). regen needs 'states' and C['moments'] & C['sup'].
# certify_dual uses states from cutting_plane. Let's find what states it returns and reproduce ordering.
states, ns, dedge, t, rows, prov2, v = pc.cutting_plane(C, maxit=15, target=-1e-6, mom_maxvecs=8, verbose=False)
print("ns=%d  cutting_plane eta=%+.4e  t=%.0fs"%(ns, v, time.time()-t0), flush=True)

# Check state ordering is canonical/deterministic: compare to flag_engine enumeration
import flag_engine as fe
states_fe = fe.enumerate_graphs(9, triangle_free=True)
print("flag_engine n9 count:", len(states_fe), " match cutting_plane states:", states==states_fe)

edens = fx.edge_density_exact(states)

# Now regen using the SAVED prov entries (self-contained per atom).
# regen signature: regen(C, states, prov, idx) -> uses prov[idx]
Phi = [mu*(edens[i]-LO) + nu*(HI-edens[i]) for i in range(ns)]
nd_used=0; nm_used=0
for c,i in enumerate(ndix):
    if lam[c]!=0:
        vals = regen(C, states, prov, i)   # SAVED prov
        nd_used+=1
        for j in range(ns):
            if vals[j]!=0: Phi[j]+=lam[c]*vals[j]
for c,i in enumerate(nmix):
    if gam[c]!=0:
        vals = regen(C, states, prov, i)   # SAVED prov
        nm_used+=1
        for j in range(ns):
            if vals[j]!=0: Phi[j]+=gam[c]*vals[j]
print("used deficit atoms:", nd_used, " moment atoms:", nm_used, flush=True)

mx = max(Phi); arg=int(np.argmax([float(p) for p in Phi]))
print("INDEP(saved-prov) max_H Phi =", float(mx))
print("   exact =", mx)
print("delta_saved =", delta_saved, "=", float(delta_saved))
print("mx == delta_saved:", mx==delta_saved)
print("mx <= delta_saved:", mx<=delta_saved)
print("mx < 1/450:", mx < F(1,450))
print("(mx - delta_saved) =", mx-delta_saved)
print("elapsed %.0fs"%(time.time()-t0))
