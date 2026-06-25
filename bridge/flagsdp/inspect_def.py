import pickle
from fractions import Fraction as F
cert=pickle.load(open("dual_cert_n9.pkl","rb"))
prov=cert["prov"]; lam=cert["lam"]; ndix=cert["ndix"]
print("deficit rules (nonzero lam):")
for c,idx in enumerate(ndix):
    l=F(str(lam[c])) if not isinstance(lam[c],F) else lam[c]
    if l==0: continue
    p=prov[idx]
    # p = ("deficit_pmap", k, A, pmap)  or ("deficit", k, A, cls, pvec)
    if p[0]=="deficit_pmap":
        _,k,A,pmap=p
        print(f"  lam={float(l):.5f}  k={k}  sigma_adj={A}  pmap={ {tuple(sorted(kk)):str(vv) for kk,vv in pmap.items()} }")
    else:
        _,k,A,cls,pv=p
        print(f"  lam={float(l):.5f}  k={k}  sigma_adj={A}  cls={cls} p={list(pv)}")
print(f"\nsum lam = {sum(F(str(x)) if not isinstance(x,F) else x for x in lam)}")
