import pickle
from fractions import Fraction as F

d = pickle.load(open("dual_cert_n9.pkl","rb"))
print("keys:", sorted(d.keys()))
prov = d["prov"]; ndix = d["ndix"]; nmix = d["nmix"]
lam = [F(s) for s in d["lam"]]
gam = [F(s) for s in d["gam"]]
mu = F(d["mu"]); nu = F(d["nu"])
num = d["maxPhi_num"]; den = d["maxPhi_den"]
delta_saved = F(num, den)

print("n prov atoms:", len(prov))
print("len(ndix):", len(ndix), " len(lam):", len(lam))
print("len(nmix):", len(nmix), " len(gam):", len(gam))

# nonnegativity
lam_neg = [(i,x) for i,x in enumerate(lam) if x < 0]
gam_neg = [(i,x) for i,x in enumerate(gam) if x < 0]
print("lam negatives:", lam_neg)
print("gam negatives:", gam_neg)
print("mu >= 0:", mu >= 0, "mu =", mu)
print("nu >= 0:", nu >= 0, "nu =", nu)

# count nonzero
print("nonzero lam:", sum(1 for x in lam if x!=0))
print("nonzero gam:", sum(1 for x in gam if x!=0))

# sum lambda
slam = sum(lam)
print("sum(lam) =", slam, " == 1 exactly:", slam == 1)

# delta value
print("delta_saved =", delta_saved)
print("float(delta_saved) =", float(delta_saved))
print("1/450 =", float(F(1,450)))
print("delta_saved < 1/450:", delta_saved < F(1,450))
print("delta_saved < 2/25? (sanity):", delta_saved < F(2,25))

# integrality margin: (25/2) n^2 delta < 1 iff n <= ?
for n in [36,37]:
    val = F(25,2)*n*n*delta_saved
    print(f"n={n}: (25/2)n^2 delta = {float(val):.6f}  < 1: {val < 1}")
