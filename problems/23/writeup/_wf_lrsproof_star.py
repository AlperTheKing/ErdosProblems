"""Test |M|-free strengthenings of LRS and the structure of the needed cancellation.

LRS:        ΣT² <= Γ(N + N²/25 - |M|).
Since Γ>=25|M| (ell>=5): N²/25 - |M| >= (N²-Γ)/25. So:
 (STAR)     ΣT² <= Γ(N + (N²-Γ)/25)    [STRONGER than LRS; |M|-free, pure in T,Γ].
            <=> ΣT² <= NΓ + Γ(N²-Γ)/25 <=> ΣT(T-N) <= Γ(N²-Γ)/25.
 Note Γ<=N^2 is the goal; if Γ>N^2 then RHS<0. (STAR) does NOT presuppose Γ<=N^2.

Also test the EXACT relation: define D := N^2 - Γ = Σ_v (N - T(v)) = U- - U+ (signed underload).  [P2]
 So Γ(N²-Γ)/25 = Γ*D/25. And ΣT(T-N) = U+ - U-... wait ΣT(T-N)=Σ_{T>N}T(T-N) - Σ_{T<N}T(N-T) = Uw+ - Uw-
 where Uw are T-WEIGHTED. Let me just compute everything and hunt CE to (STAR).

Battery: census N<=10, two-lane, Grotzsch, blowups.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, blow_g

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def test(n,E,side):
    st=struct_for_side(n,adj_of(n,E),side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); beta=len(M)
    ST2=sum(t*t for t in T)
    I=ST2-N*Gamma                      # = ΣT(T-N)
    D=N*N-Gamma                        # signed underload total
    lrs_rhs=Gamma*(F(N*N,25)-beta)
    star_rhs=Gamma*D/25                # |M|-free
    return dict(N=N,beta=beta,Gamma=Gamma,I=I,D=D,
                lrs=(I<=lrs_rhs), star=(I<=star_rhs),
                lrs_marg=lrs_rhs-I, star_marg=star_rhs-I,
                Glong=Gamma>N*N)

def show(lbl,r):
    if r is None: print(f"  {lbl}: no struct"); return
    sf="" if r['star'] else "  <<< STAR FAILS"
    print(f"  {lbl}: N={r['N']} m={r['beta']} G={r['Gamma']} I={r['I']} D=N2-G={r['D']} "
          f"LRS={r['lrs']}(marg {float(r['lrs_marg']):.1f}) STAR={r['star']}(marg {float(r['star_marg']):.1f}){sf}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== STAR (|M|-free) test ===",flush=True)
    for L in (8,12,20,30):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",test(n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Grotzsch N=11",test(g1[0],g1[1],info['side']))
    for k in (5,7,9):
        for t in (1,2,3):
            n,E=blow_g(k,Cn(k),t)
            if n>20: continue
            info=loads(n,E)
            if info: show(f"C{k}[{t}]",test(n,E,info['side']))
    print("--- census N=5..10: STAR vs LRS violations ---",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=sv=lv=0; firstS=None; worstS=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=test(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['lrs']: lv+=1
            if not r['star']: sv+=1; firstS=firstS or (g6,float(r['I']),float(r['star_marg']))
            if worstS is None or r['star_marg']<worstS[1]: worstS=(g6,r['star_marg'])
        print(f"  N={nn}: structs={ng} STAR_viol={sv} LRS_viol={lv} min(STAR margin)={float(worstS[1]) if worstS else 'NA':.3f} at {worstS[0] if worstS else ''}",flush=True)
        if firstS: print(f"     first STAR viol: {firstS}")
    print("=== done ===",flush=True)
