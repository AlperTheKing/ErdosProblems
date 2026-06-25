import pickle
from fractions import Fraction as F
new = pickle.load(open("dual_cert_n9.pkl","rb"))
old = pickle.load(open("dual_cert_n9.audit_backup.pkl","rb"))
nn=F(new["maxPhi_num"],new["maxPhi_den"]); oo=F(old["maxPhi_num"],old["maxPhi_den"])
print("new maxPhi:", nn)
print("old maxPhi:", oo)
print("new == old:", nn==oo)
print("lam same:", new["lam"]==old["lam"])
print("gam same:", new["gam"]==old["gam"])
print("ndix same:", new["ndix"]==old["ndix"])
print("nmix same:", new["nmix"]==old["nmix"])
print("mu,nu same:", new["mu"]==old["mu"], new["nu"]==old["nu"])
