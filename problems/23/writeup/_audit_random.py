"""Out-of-distribution stress: RANDOM triangle-free graphs at N=14..20 (feasible maxcut),
plus geng-enumerated dense triangle-free at N=12,13 (sample). Test full Schur cert exact.
maxcut brute is 2^(N-1); cap N<=20 for random (slow but ok for a handful)."""
import random
from fractions import Fraction as F
from _h import loads
from _audit_stress import full_test, report

def rand_tf(n,p,seed):
    random.seed(seed)
    adj=[set() for _ in range(n)]; E=[]
    verts=list(range(n)); random.shuffle(verts)
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    random.shuffle(pairs)
    for (i,j) in pairs:
        if random.random()<p:
            # add only if no common neighbor (keeps triangle-free)
            if not (adj[i] & adj[j]):
                adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E

if __name__=="__main__":
    print("=== random triangle-free stress (N=14..20) ===",flush=True)
    tested=0; fails=0; sing=0; noO=0; wm=None; wk=None
    for n in range(14,21):
        for seed in range(8):
            nn,E=rand_tf(n,0.45,seed*100+n)
            info=loads(nn,E)
            if info is None: continue
            res=full_test(info)
            if res['status']=='noO': noO+=1; continue
            tested+=1
            if res['status']=='SINGULAR_AQQ': sing+=1; print("  "+report(f"rand_n{n}_s{seed}",nn,res),flush=True)
            elif res['status']=='FAIL': fails+=1; print("  "+report(f"rand_n{n}_s{seed}",nn,res),flush=True)
            else:
                if wm is None or res['minrow']<wm: wm=res['minrow']
                if wk is None or res['mink2']<wk: wk=res['mink2']
    print(f"  random TF N=14..20: tested {tested} overloaded, {noO} noO | FAILS={fails} SING={sing}"
          f" | worst E-rowsum={float(wm) if wm is not None else 'na'} worst k2={float(wk) if wk is not None else 'na'}",flush=True)
