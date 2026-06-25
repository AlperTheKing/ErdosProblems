import pickle, numpy as np, collections
import prove_cert as pc
C = pc.load(9)
moms = C["moments"]   # (lab, tt, sigma, flags, s, Pf, Pint)
print("num moment types:", len(moms))
for (lab, tt, sigma, flags, s, Pf, Pint) in moms:
    print(f"  lab={lab!r}  sigma={sigma}  s={s}  t(#flags)={tt}  flags[0]={flags[0]}")
cert = pickle.load(open("dual_cert_n9.pkl","rb"))
prov = cert["prov"]; gam = cert["gam"]; nmix = cert["nmix"]
# moment atoms: prov entries with [0]=="moment"
mom_atoms = [(i,p) for i,p in enumerate(prov) if p[0]=="moment"]
print("\nnum moment prov entries:", len(mom_atoms), " gam len:", len(gam))
# map: which gam index aligns to which prov moment atom? deficits first (75), then moments
nz = [(i, gam[i]) for i in range(len(gam)) if abs(float(gam[i]))>0]
print("nonzero gam:", len(nz))
# group atoms by lab/sigma with nonzero gam
by_sig = collections.Counter()
for j,(i,p) in enumerate(mom_atoms):
    g = gam[j] if j < len(gam) else 0
    if abs(float(g))>0:
        by_sig[(p[1], str(p[2]), p[3])] += 1   # (lab, sigma, s)
print("nonzero-gam atoms by (lab,sigma,s):")
for k,c in by_sig.items(): print("   ", k, "->", c)
# sample vv length
i0,p0 = mom_atoms[0]; print("\nsample moment prov:", p0[0], p0[1], p0[2], p0[3], "vv-len", len(p0[4]))
