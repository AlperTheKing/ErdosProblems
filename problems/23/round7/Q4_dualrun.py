"""Q4: EXACT dual certificate -- proves an upper bound on the value c* of the degree-2d scheme.

By the elementary weak duality proved in Q4_dual.py, for any rational z >= 0 whose parity blocks
Z_b = [z_{(beta+gamma)/2}] are PSD,   c*  <=  num(z)/den(z)  with
num = sum_alpha muT(alpha) z_alpha,  den = sum_m muD(m) * min_S zhat_S(m).
Producing such a z with num/den < 25 REFUTES the scheme at that degree for that pattern, exactly.

Usage: python Q4_dualrun.py <m> <d> [denominator]
"""
import sys, time
from fractions import Fraction as F
import numpy as np
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts
from Q4_dual import dual_problem, ratio_exact, psd_blocks_exact, z_interior
from Q4_sos import monomials

m = int(sys.argv[1]) if len(sys.argv) > 1 else 11
d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
den = int(sys.argv[3]) if len(sys.argv) > 3 else 10**7

n, E = gamma_graph(m)
cuts = nondominated_cuts(all_cuts(n, E))
print(f"Gamma_{m} d={d}: {len(cuts)} inclusion-minimal cuts", flush=True)
t0 = time.time()
prob, z, w, monsD, monsT = dual_problem(n, E, cuts, d)
print(f"   dual build {time.time()-t0:.1f}s   ({len(monsT)} moments, {len(monsD)} weights)",
      flush=True)
t0 = time.time()
prob.solve(solver='CLARABEL', verbose=False)
print(f"   dual solve {time.time()-t0:.1f}s status={prob.status}  value = {prob.value}", flush=True)

zi = z_interior(n, d)
si = max(zi.values())
zn = np.asarray(z.value)
scale = max(abs(float(v)) for v in zn) or 1.0
best = None
for t in [F(0), F(1, 10**7), F(1, 10**6), F(1, 10**5), F(1, 10**4), F(1, 10**3), F(1, 100)]:
    zq = {a: F(int(round(zn[i] / scale * den)), den) + t * zi[a] / si for i, a in enumerate(monsT)}
    ok, info = psd_blocks_exact(n, d, zq)
    if not ok:
        print(f"   t={t}: not PSD ({info[:60]})", flush=True)
        continue
    num, dn, r = ratio_exact(n, E, cuts, d, zq)
    print(f"   t={t}: PSD, exact ratio num/den = {r} = {float(r):.9f}", flush=True)
    if dn > 0 and (best is None or r < best[2]):
        best = (num, dn, r, t, zq)
    break
if best:
    num, dn, r, t, zq = best
    print(f"EXACT DUAL CERTIFICATE Gamma_{m} degree {2*d}:  c* <= {r} = {float(r):.9f}"
          f"   ({'REFUTES c=25' if r < 25 else 'does not refute 25'})")
    import pickle
    pickle.dump(dict(m=m, d=d, z=zq, num=num, den=dn, ratio=r),
                open(f"Q4_dualcert_g{m}_d{d}.pkl", "wb"))
    print(f"   saved Q4_dualcert_g{m}_d{d}.pkl")
else:
    print("no exact dual certificate obtained")
