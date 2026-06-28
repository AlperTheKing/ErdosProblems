"""Part 2: stress harder blow-ups + non-blowup high-chromatic; confirm CD-cut failure law;
verify SPEC and ROWSUM-O on N=18..25, exact Fraction. Also independent N=11 census O1 spot."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from verify_synth import analyze, pf_dict

def blow_odd(p,t):
    """C_p[t] blow-up, p odd cycle length, t per part."""
    nn=p*t; E=[]
    for i in range(p):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, ((i+1)%p)*t+b))
    return nn,E

def grotzsch():
    # Grotzsch graph (Mycielskian of C5), 11 vertices, triangle-free chi=4. Standard edge list.
    # vertices 0..4 = C5 outer, 5..9 = mirrors, 10 = apex
    E=[]
    for i in range(5):
        E.append((i,(i+1)%5))              # outer C5
    for i in range(5):
        E.append((5+i,(i+1)%5))            # mirror i ~ neighbors of outer i
        E.append((5+i,(i-1)%5))
        E.append((5+i,10))                 # mirror ~ apex
    return 11,E

print("--- harder odd blow-ups (exact) ---")
for (p,t) in [(7,2),(7,3),(9,2),(9,3),(11,2),(5,4),(5,5)]:
    nn,E=blow_odd(p,t); info=loads(nn,E)
    if info is None: print(f"C{p}[{t}] N={nn}: None"); continue
    r=analyze(info)
    print(f"C{p}[{t}] N={nn}: O1max={r['O1_max']} ({float(r['O1_max']):.4f}) "
          f"Gamma={info['G']} N^2={nn*nn} ratioGam={float(F(info['G'],nn*nn)):.4f} | "
          f"O1viol={r['O1_viol']} CYCLE_SM={r['CYCLE_SM_viol']} GAMMA={r['GAMMA_viol']} WFid={r['WF_id_on_support']}",flush=True)

print("--- non-blowup high-chromatic (Grotzsch N=11) ---")
nn,E=grotzsch(); info=loads(nn,E)
r=analyze(info)
print(f"Grotzsch N={nn}: O1max={r['O1_max']} ({float(r['O1_max']):.4f}) Gamma={info['G']} N^2={nn*nn} "
      f"| O1viol={r['O1_viol']} CYCLE_SM={r['CYCLE_SM_viol']} GAMMA={r['GAMMA_viol']} WFid={r['WF_id_on_support']} WFeq={r['WF_equiv']}",flush=True)

print("--- SPEC vs CYCLE-SM matrix-fact check: is SPEC strictly weaker? ---")
# Build a synthetic PSD O (Gram) with rho<=N but skewed ell making (O ell)_f/ell_f > N -> shows
# SPEC alone does NOT imply CycleSM; we rely on rho(O)<=N => ell^T O ell <= N||ell||^2 => SM (Rayleigh), NOT per-edge.
import numpy as np
# Confirm the actual chain uses ell^T O ell <= rho ||ell||^2, i.e. SM not per-edge CycleSM.
# Check sum_v T^2 = ell^T O ell? No: sum_v T^2 = sum_f ell_f (Oell)_f = ell^T O ell. Yes (ID_ST).
# So SM <= rho(O)*sum ell^2 = rho(O)*Gamma <= N*Gamma if rho<=N. Confirm numerically on a census graph.
out=subprocess.run([GENG,"-tc","9"],capture_output=True,text=True).stdout.split()
bad=0
for g6 in out:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    M,pfs=pf_dict(info); m=len(M); ell=info['ell']; T=info['T']; N=n
    O=np.zeros((m,m))
    for i in range(m):
        for j in range(m):
            di,dj=pfs[i],pfs[j]
            O[i][j]=float(sum(di[v]*dj[v] for v in (di.keys()&dj.keys())))
    rho=max(np.linalg.eigvalsh(O))
    ellv=np.array([float(ell[f]) for f in M])
    sumT2=float(sum(t*t for t in T))
    lhs=ellv@O@ellv
    if abs(lhs-sumT2)>1e-6: bad+=1
    if rho>N+1e-6: print("  rho>N!",g6,rho);
print(f"  ell^T O ell == sum T^2 mismatches: {bad} (expect 0); chain SM<=rho*Gamma<=N*Gamma sound via Rayleigh.",flush=True)

print("--- CD-cut failure law spot-check: F?o~_ N=7 ---")
from _crofton_lp import overlap_matrix, all_cuts, lp_f
n,E=dec("F?o~_"); info=loads(n,E)
O,P,pf=overlap_matrix(info); cuts=all_cuts(n,info)
for j,f in enumerate(info['M']):
    opt,target=lp_f(info,O,cuts,j)
    pf2=float((P[:,j]@P[:,j]))  # ||p_f||^2 = O_ff
    print(f"  f={f} ell={info['ell'][f]} O_ff={pf2:.3f} LP_opt={opt:.3f} N*ell={target} (Oell)_f={float(O[j]@[info['ell'][info['M'][k]] for k in range(len(info['M']))]):.3f}",flush=True)
