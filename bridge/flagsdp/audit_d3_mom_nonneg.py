# Independent check: are the moment atoms m_j(H) >= 0 on all states?
# The dual closure: sum lam*g + sum gam*m + band <= delta for ALL H, gam>=0.
# To conclude sum lam*g <= delta on band, need (gam*m + band) >= 0 on band states.
# Since band terms here have mu=nu=0, we need sum gam_j m_j(H) >= 0 on band graphons.
# Moment atoms m_j(H) = v^T P^sigma(H) v / norm. P^sigma(H) is PSD per graphon (it's a
# Gram-type moment matrix), so v^T P v >= 0 for each H that is a genuine graph sample.
# Verify numerically: for each used moment atom, min over states of m_j(H).
import pickle
from fractions import Fraction as F
import prove_cert as pc, flag_exact as fx
from certify_dual import regen
from math import comb

d = pickle.load(open("dual_cert_n9.audit_backup.pkl","rb"))
prov=d["prov"]; nmix=d["nmix"]; gam=[F(s) for s in d["gam"]]
C = pc.load(9)
states = C["states"]; ns=len(states)
print("ns=",ns)
# check a handful of used moment atoms for nonnegativity over all states
used = [(c,i) for c,i in enumerate(nmix) if gam[c]!=0]
print("used moment atoms:", len(used))
import sys
neg_atoms=0
mins=[]
for cnt,(c,i) in enumerate(used):
    vals = regen(C, states, prov, i)
    mn = min(vals)
    mins.append(float(mn))
    if mn < 0:
        neg_atoms+=1
    if cnt < 5 or mn < 0:
        print(f"  atom nmix[{c}] (prov idx {i}): min_H m = {float(mn):.3e}  gam={float(gam[c]):.3e}")
    sys.stdout.flush()
print("moment atoms with negative min:", neg_atoms, "/", len(used))
print("overall min of per-atom minima:", min(mins))
