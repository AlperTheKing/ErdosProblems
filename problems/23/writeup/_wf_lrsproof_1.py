"""WF LRS-proof validation step 1.

Goal: validate EVERY intermediate of a coarea/CD attack on
    (LRS)  sum_v T(v)(T(v)-N) <= Gamma*(N^2/25 - |M|).

We compute exactly (Fraction) for each test graph:
  - T(v) loads, Gamma = sum_v T(v), Gamma2 = sum ell^2 (handshake: equal)
  - the coarea identity:  sum_v T(T-N) = int_0^inf (2s-N)|H_s| ds
    with H_s = {v : T(v) >= s}.  We evaluate the RHS exactly as a sum over
    the distinct breakpoints of |H_s| (a step function of s).
  - boundary counts delta_M(S), delta_B(S) for S a vertex set:
        delta_X(S) = # edges of family X with exactly one endpoint in S.
    Claimed CD inequality on super-level sets: delta_M(H_s) <= delta_B(H_s).
  - overload-isoperimetry: |H_s| <= delta_B(H_s) for s>N  (TEMPTING SUBLEMMA -- HUNT CE)

We DO NOT assume Erdos / |M|<=N^2/25 / LRS. We only test which sub-claims hold.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, blow
from _bdef_construct import mycielski, Cn, blow_g

def struct(n,E):
    return loads(n,E)

def coarea_rhs(T,N):
    """ int_0^inf (2s-N)|H_s| ds, H_s={v:T[v]>=s}.
    |H_s| is a right-continuous step function decreasing in s.
    Breakpoints at the distinct T-values. On (a,b] where a,b consecutive
    sorted distinct values (ascending), need |H_s| for s in that band.
    Easier: sum_v T(v)(T(v)-N) has closed form; we instead verify the
    integral form by direct antiderivative on each band.
    int_a^b (2s-N) ds = (b^2-a^2) - N(b-a).
    For s in (a,b], H_s = {v: T[v]>=s}. For s slightly >a, threshold excludes
    value a. We integrate over s from 0 to max(T). Use distinct values.
    """
    vals=sorted(set([F(0)]+[t for t in T]))
    # add 0 boundary; integrate band by band between consecutive thresholds
    tot=F(0)
    # For band (lo,hi], |H_s| = #{v: T[v]>=s} = #{v: T[v]>=hi} (since no T-value in (lo,hi) strictly, but T-value could equal hi). For s in (lo,hi], v counts iff T[v]>=s; the smallest s is just above lo so excludes T[v]==lo, includes T[v]>=hi... careful: T[v] in (lo,hi) impossible. T[v]==hi: included when s<=hi i.e. all of band. T[v]==lo: excluded for s>lo. So count = #{v:T[v]>=hi}.
    sv=sorted(set(T))
    allv=sorted(set([F(0)]+sv))
    for i in range(len(allv)-1):
        lo=allv[i]; hi=allv[i+1]
        cnt=sum(1 for t in T if t>=hi)
        tot += ((hi*hi-lo*lo) - N*(hi-lo))*cnt
    return tot

def delta(n,adj,memberX,S):
    """# edges in family X crossing S boundary. memberX(u,v)->bool for u<v adjacency in X."""
    c=0
    for u in range(n):
        for v in adj[u]:
            if v>u and memberX(u,v):
                if (u in S) != (v in S): c+=1
    return c

def run_one(label,n,E):
    info=struct(n,E)
    if info is None: return None
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; Bset=info['Bset']; Mset=info['Mset']
    Gamma=sum(T)                      # handshake total
    Gamma2=sum(ell[f]**2 for f in M)
    beta=len(M)
    lhs=sum(t*(t-N) for t in T)       # weighted overload
    rhs=Gamma*(F(N*N,25)-beta)
    lrs_ok = lhs<=rhs
    # coarea check
    ca=coarea_rhs(T,N)
    coarea_ok = (ca==lhs)
    # CD on superlevels + overload-isoperimetry tail
    isM=lambda u,v:(min(u,v),max(u,v)) in Mset
    isB=lambda u,v:(min(u,v),max(u,v)) in Bset
    vals=sorted(set(T))
    cd_viol=[]; iso_viol=[]
    for s in vals:
        Hs=set(v for v in range(N) if T[v]>=s)
        if not Hs or len(Hs)==N: continue
        dM=delta(N,adj,isM,Hs); dB=delta(N,adj,isB,Hs)
        if dM>dB: cd_viol.append((float(s),dM,dB))
        if s>N and len(Hs)>dB: iso_viol.append((float(s),len(Hs),dB))
    return dict(label=label,N=N,beta=beta,Gamma=Gamma,Gamma2=Gamma2,
                handshake=(Gamma==Gamma2),lhs=lhs,rhs=rhs,lrs_ok=lrs_ok,
                coarea_ok=coarea_ok, cd_viol=cd_viol, iso_viol=iso_viol,
                Tmax=max(T))

def show(r):
    if r is None: print("  (no struct)"); return
    print(f"  {r['label']}: N={r['N']} beta={r['beta']} handshake={r['handshake']} "
          f"LRS={'OK' if r['lrs_ok'] else 'FAIL'} coarea={'OK' if r['coarea_ok'] else 'FAIL'} "
          f"Tmax={float(r['Tmax']):.3f}")
    if r['cd_viol']: print(f"     CD-superlevel VIOL (delta_M>delta_B): {r['cd_viol'][:5]}")
    if r['iso_viol']: print(f"     OVERLOAD-ISO VIOL (|H_s|>delta_B, s>N): {r['iso_viol'][:5]}")

if __name__=="__main__":
    print("=== coarea identity + CD/iso sublemma exact validation ===")
    # blow-ups C5[t]
    for t in (1,2,3):
        n,E=blow(t); show(run_one(f"C5[{t}]",n,E))
    # two-lane
    from _verify_two_lane import build_two_lane
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); show(run_one(f"two-lane L={L}",n,E))
    # Mycielskians (Grotzsch = Myc(C5); Myc^2(C5))
    c5=(5,Cn(5))
    g1=mycielski(*c5); g2=mycielski(*g1)
    show(run_one("Myc(C5)=Grotzsch",*g1))
    show(run_one("Myc^2(C5)",*g2))
    # census gamma-min N<=9 (CD/iso hunt)
    print("--- census N=5..9: count CD-superlevel and overload-iso violations among gamma-min ---")
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=0; cdv=0; isov=0; lrsf=0; cav=0; first_cd=None; first_iso=None
        for g6 in outg:
            n,E=dec(g6); r=run_one(g6,n,E)
            if r is None: continue
            ng+=1
            if not r['coarea_ok']: cav+=1
            if not r['lrs_ok']: lrsf+=1
            if r['cd_viol']: cdv+=1; first_cd=first_cd or (g6,r['cd_viol'][0])
            if r['iso_viol']: isov+=1; first_iso=first_iso or (g6,r['iso_viol'][0])
        print(f"  N={nn}: structs={ng} coarea_fail={cav} LRS_fail={lrsf} "
              f"CD_superlevel_viol={cdv} overload_iso_viol={isov}",flush=True)
        if first_cd: print(f"     first CD viol: {first_cd}")
        if first_iso: print(f"     first iso viol: {first_iso}")
