import pickle, numpy as np, collections
import prove_cert as pc
cert = pickle.load(open("dual_cert_n9.pkl","rb"))
print("type:", type(cert))
if isinstance(cert,dict):
    print("keys:", list(cert.keys()))
    for k,v in cert.items():
        try: print(f"  {k}: shape={np.shape(v)}" if hasattr(v,'__len__') else f"  {k}={v}")
        except: print(f"  {k}: {type(v)}")
    # provenance of moment atoms
    prov = cert.get("prov") or cert.get("cert_prov")
    if prov:
        sig_count = collections.Counter()
        for p in prov:
            if p[0]=="moment":
                # (moment, lab, sigma, s, vv)
                sigma = p[2]; s = p[3]
                sig_count[(str(sigma), s)] += 1
        print("\nMOMENT atoms by (sigma, s):")
        for k,c in sorted(sig_count.items()): print(f"   sigma={k[0]}  s={k[1]}  -> {c} atoms")
        defc = sum(1 for p in prov if p[0] in ("deficit","deficit_pmap"))
        print(f"deficit atoms: {defc}; total prov: {len(prov)}")
