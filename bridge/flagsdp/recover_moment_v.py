#!/usr/bin/env python3
"""R1: recover the 317 moment-row eigenvectors v (cp_cache kept only the 'moment' tag).
Re-run prove_cert.cutting_plane with the SAME params get_cp used (maxit=12, target=-1e-6, mom_maxvecs=8),
extract the moment cert_prov (which carries vv per row), and CONFIRM the regenerated moment rows match
cp_cache's 317 moment rows (deterministic => same rows). Save the matched (v, lab, sigma, s) for exact recompute."""
import pickle, numpy as np, time
import prove_cert as pc
ns,dedge,rows,provtypes,extra=pickle.load(open("cp_cache.pkl","rb"))
mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
cp_mom=[np.asarray(rows[i],float) for i in mom_idx]
print(f"cp_cache: {len(cp_mom)} moment rows over ns={ns} states",flush=True)
C=pc.load(9)
t0=time.time()
states,ns2,dedge2,t,cert_rows,cert_prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=True)
print(f"re-ran cutting_plane [{time.time()-t0:.0f}s] eta={v:+.6e} ns2={ns2}",flush=True)
re_mom=[(np.asarray(cert_rows[i],float),cert_prov[i]) for i in range(len(cert_rows)) if cert_prov[i][0]=='moment']
print(f"regenerated {len(re_mom)} moment rows",flush=True)
# match each cp_cache moment row to a regenerated one (by nearest L2), confirm exact-ish match
import numpy as np
remat=np.array([r for r,_ in re_mom])
matched=[]; worst=0.0
for k,cr in enumerate(cp_mom):
    diffs=np.linalg.norm(remat-cr[None,:],axis=1)
    j=int(diffs.argmin()); worst=max(worst,diffs[j]); matched.append(j)
nuniq=len(set(matched))
print(f"matched {len(cp_mom)} cp rows to regenerated; worst L2 diff={worst:.3e}; unique matches={nuniq}/{len(cp_mom)}",flush=True)
if worst<1e-6 and nuniq==len(cp_mom):
    out=[]
    for k,cr in enumerate(cp_mom):
        pr=re_mom[matched[k]][1]  # ('moment', lab, sigma, s, vv)
        out.append((pr[1],pr[2],pr[3],np.asarray(pr[4],float)))
    pickle.dump(dict(mom_v=out, mom_idx=mom_idx), open("moment_v_recovered.pkl","wb"))
    print(f"SAVED moment_v_recovered.pkl: {len(out)} (lab,sigma,s,v) tuples matched to cp_cache moment-row order",flush=True)
else:
    print("!! match imperfect -- cutting_plane not reproducing cp_cache rows; need the exact generation params",flush=True)
print("DONE",flush=True)
