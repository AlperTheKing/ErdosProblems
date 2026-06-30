"""Confirm the RIGOROUS, non-circular deductive chain (the proven scaffolding around the open STAR).

We verify symbolically/numerically that EACH implication below is a valid identity/inequality:
  STAR:  25*ΣT² <= Γ(N²+25N-Γ),  Γ=ΣT.
  (S1)  STAR => ΣT² <= Γ(N + (N²-Γ)/25)              [divide by 25, rearrange]   -- algebra
  (S2)  Cauchy-Schwarz + P1:  ΣT² >= Γ²/N             [proven]
  (S3)  combine: Γ²/N <= Γ(N+(N²-Γ)/25) => Γ <= N²    [algebra, shown by hand]
  (S4)  ell>=5 (triangle-free) => 25|M| <= Γ => |M| <= Γ/25 <= N²/25 = beta bound.   [proven]
Also: STAR => LRS (since N²/25-|M| >= (N²-Γ)/25 by S4), so STAR is the stronger sufficient target.

We numerically confirm S2,S3,S4 hold and that the closure Γ<=N² is implied, on the gate, WITHOUT assuming the goal.
This documents that the ONLY open link is STAR itself.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def chain(n,E,side):
    st=struct_for_side(n,adj_of(n,E),side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); ST2=sum(t*t for t in T); beta=len(M)
    star = 25*ST2 <= Gamma*(N*N+25*N-Gamma)
    # S2 Cauchy-Schwarz
    cs = ST2*N >= Gamma*Gamma
    # S3: if STAR and CS then Gamma<=N^2 (closure). Derive: assume star=>ST2<=Γ(N+(N²-Γ)/25); CS=>Γ²/N<=ST2
    #   => Γ²/N <= Γ(N+(N²-Γ)/25) => Γ/N <= N+(N²-Γ)/25 => 25Γ <= 25N²+N(N²-Γ) => 25Γ+NΓ<=25N²+N³
    #   => Γ(25+N) <= N²(25+N) => Γ<=N². Confirm Gamma<=N² holds whenever star holds (it must).
    closure_consistent = (not star) or (Gamma <= N*N)
    # S4: ell>=5
    ell_ok = all(ell[f] >= 5 for f in M)
    beta_bound = (25*beta <= Gamma)   # => beta <= Γ/25
    # STAR => LRS link: N²/25-|M| >= (N²-Γ)/25
    star_ge_lrs = (F(N*N,25)-beta) >= F(N*N-Gamma,25)
    return dict(N=N,Gamma=Gamma,beta=beta,star=star,cs=cs,
                closure_consistent=closure_consistent, ell_ok=ell_ok,
                beta_bound=beta_bound, star_ge_lrs=star_ge_lrs,
                GleN2=Gamma<=N*N)

if __name__=="__main__":
    from _bdef_construct import mycielski, Cn
    from _verify_two_lane import build_two_lane
    print("=== rigorous chain scaffolding (all PROVEN links) confirmation ===",flush=True)
    bad=0; tot=0; details=[]
    tests=[]
    for L in (8,12,20):
        n,E,side,b=build_two_lane(L); tests.append((f"two-lane L={L}",n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: tests.append(("Grotzsch N=11",g1[0],g1[1],info['side']))
    for lbl,n,E,side in tests:
        r=chain(n,E,side)
        if r is None: continue
        ok = r['cs'] and r['closure_consistent'] and r['ell_ok'] and r['beta_bound'] and r['star_ge_lrs']
        print(f"  {lbl}: CS={r['cs']} closure_consistent={r['closure_consistent']} ell>=5={r['ell_ok']} "
              f"beta<=G/25={r['beta_bound']} STAR>=LRS={r['star_ge_lrs']} | STAR={r['star']} G<=N2={r['GleN2']}")
    print("--- census N=5..10: confirm ALL proven links hold (CS,closure,ell,beta,star>=lrs) ---",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=cf=clf=ef=bf=slf=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=chain(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['cs']: cf+=1
            if not r['closure_consistent']: clf+=1
            if not r['ell_ok']: ef+=1
            if not r['beta_bound']: bf+=1
            if not r['star_ge_lrs']: slf+=1
        print(f"  N={nn}: structs={ng} CS_fail={cf} closure_fail={clf} ell_fail={ef} "
              f"beta_fail={bf} STAR>=LRS_fail={slf}",flush=True)
    print("=== done ===",flush=True)
