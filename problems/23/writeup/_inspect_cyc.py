from _h import dec, loads
n,E=dec("I?BD@g]Qo"); info=loads(n,E)
print("keys:", list(info.keys()))
print("M:", info.get("M"))
print("ell:", info.get("ell"))
c=info.get("cyc")
print("cyc type:", type(c))
if isinstance(c,dict):
    k=list(c.keys())[0]; print("cyc key", k, "n_paths", len(c[k]), "path0", c[k][0])
elif isinstance(c,list):
    print("cyc[0]:", c[0])
print("Bset[:5]:", list(info["Bset"])[:5])
print("T:", info.get("T"))
print("n:", info.get("n"))
