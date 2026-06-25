# Cross-check: EXACT regen of each USED atom reproduces (to float tol) the FLOAT cut row
# that the LP used. cutting_plane returns 'rows' (float) and 'prov'. The saved cert's
# multipliers were fit against those float rows. The exact verification regenerates atoms
# from prov. If exact != float-row, a prior-style bug (localizer grad) could hide.
import pickle, time
from fractions import Fraction as F
import numpy as np
import prove_cert as pc, flag_exact as fx
from certify_dual import regen

t0=time.time()
d = pickle.load(open("dual_cert_n9.audit_backup.pkl","rb"))
prov_saved=d["prov"]; ndix=d["ndix"]; nmix=d["nmix"]
lam=[F(s) for s in d["lam"]]; gam=[F(s) for s in d["gam"]]

C = pc.load(9)
states, ns, dedge, t, rows, prov2, v = pc.cutting_plane(C, maxit=15, target=-1e-6, mom_maxvecs=8, verbose=False)
print("ns=%d eta=%+.4e t=%.0fs"%(ns,v,time.time()-t0),flush=True)

# The saved prov must be regenerated; cross-check exact-regen(prov2[i]) vs float row rows[i]
# but prov ordering differs. Instead: cross-check that the SAVED-prov exact value equals
# exact value when regenerated independently, AND that the float 'rows' for the live prov2
# atoms matches their exact regen. Use prov2 (matches rows) for the float cross-check.
import random
mom_idx = [i for i in range(len(prov2)) if prov2[i][0]=="moment"]
def_idx = [i for i in range(len(prov2)) if prov2[i][0] in ("deficit","deficit_pmap")]
print("live atoms: moment=%d deficit=%d"%(len(mom_idx),len(def_idx)),flush=True)

worst_mom=0.0
sample = mom_idx[:30]  # check 30 moment atoms exact-vs-float
for i in sample:
    ev = regen(C, states, prov2, i)
    fr = rows[i]
    err = max(abs(float(ev[j])-fr[j]) for j in range(ns))
    worst_mom=max(worst_mom,err)
print("moment exact-vs-floatrow worst abs err (30 atoms): %.3e"%worst_mom,flush=True)

worst_def=0.0
for i in def_idx:   # all deficit atoms
    ev = regen(C, states, prov2, i)
    fr = rows[i]
    err = max(abs(float(ev[j])-fr[j]) for j in range(ns))
    worst_def=max(worst_def,err)
    print("  def idx %d type=%s err=%.3e"%(i,prov2[i][0],err),flush=True)
print("deficit exact-vs-floatrow worst abs err: %.3e"%worst_def,flush=True)
print("elapsed %.0fs"%(time.time()-t0))
