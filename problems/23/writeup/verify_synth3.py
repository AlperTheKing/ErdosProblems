"""Part 3: (a) N=11 census O1 sample (strided), (b) confirm per-cycle bound FAILS
(sum_{v in C} S(v) <= N is false for some cycle C), (c) confirm S(v)<=T(v)/5 holds,
(d) the weak per-vertex bound max_v s(v)*ell(f)<=N FAILS to certify (so a real correlation arg is needed)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from verify_synth import pf_dict, analyze

# (a) N=11 strided census, exact O1 max
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
print(f"N=11 total tri-free conn graphs: {len(out)}; striding /50 for O1 sample")
o1max=None; wg=None; viol=0; cnt=0
for g6 in out[::50]:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    cnt+=1
    r=analyze(info)
    if r['O1_viol']: viol+=1
    if o1max is None or r['O1_max']>o1max: o1max=r['O1_max']; wg=g6
print(f"  sampled={cnt} O1_viol={viol} max O1={o1max} ({float(o1max):.4f}) @ {wg} (N=11)",flush=True)

# (b) per-cycle bound sum_{v in C} S(v) <= N : look for a violation in N=10 census
print("--- per-cycle bound sum_{v in C} S(v) <= N : seeking violation (expect FAIL) ---")
out10=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
found=False
for g6 in out10:
    n,E=dec(g6); info=loads(n,E); N=n
    if info is None: continue
    M,pfs=pf_dict(info)
    S={v:F(0) for v in range(n)}
    for d in pfs:
        for v,p in d.items(): S[v]+=p
    for f in info['M']:
        for C in info['cyc'][f]:
            # C is a B-geodesic path a..b; the odd cycle = path + the bad edge (a,b). vertices = set(C)
            tot=sum(S[v] for v in set(C))
            if tot>N:
                print(f"  PER-CYCLE FAIL: {g6} f={f} cycle-verts={set(C)} sum S={tot} ({float(tot):.4f}) > N={N}",flush=True)
                found=True; break
        if found: break
    if found: break
if not found: print("  no per-cycle violation found in N=10 census (would contradict agents -- investigate)",flush=True)

# (c) S(v) <= T(v)/5 since ell>=5: S(v)=sum_g p_g(v), T(v)=sum_g ell(g)p_g(v) >= 5 S(v).
print("--- S(v) <= T(v)/5 (ell>=5) check on N=9 census ---")
out9=subprocess.run([GENG,"-tc","9"],capture_output=True,text=True).stdout.split()
bad=0; cnt=0
for g6 in out9:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    cnt+=1
    M,pfs=pf_dict(info); T=info['T']
    S={v:F(0) for v in range(n)}
    for d in pfs:
        for v,p in d.items(): S[v]+=p
    for v in range(n):
        if 5*S[v] > T[v]: bad+=1; break
print(f"  graphs={cnt} with some 5*S(v)>T(v): {bad} (expect 0)",flush=True)

# (d) weak bound max_v S(v)*max_f ell(f) <= N : does it certify O1<=N? S=sum_g p_g; O1_f=sum_v p_f(v)S(v)<=ell(f)*max S
print("--- weak bound ell(f)*max_v S(v) >= O1 always but <= N FAILS to certify (count fails N=9) ---")
fail=0; cnt=0
for g6 in out9:
    n,E=dec(g6); info=loads(n,E); N=n
    if info is None: continue
    cnt+=1
    M,pfs=pf_dict(info)
    S={v:F(0) for v in range(n)}
    for d in pfs:
        for v,p in d.items(): S[v]+=p
    Smax=max(S.values()) if S else F(0)
    for f in info['M']:
        if info['ell'][f]*Smax > N: fail+=1; break
print(f"  graphs={cnt}; ell(f)*maxS > N on {fail} (these need genuine p_f-S correlation, not the weak bound)",flush=True)
