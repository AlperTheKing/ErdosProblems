"""Probe whether STAR follows from CD total-variation + handshake (the proven max-cut inputs).

Proven inputs:
 (CD-TV)  for ANY function g on V:  Σ_{xy in M}|g_x-g_y| <= Σ_{xy in B}|g_x-g_y|   (coarea of delta_M<=delta_B)
 (P1) ΣT=Γ ;  (P2) Σ(N-T)=N²-Γ
 (handshake) Σ_{e∋v,e∈B} μ(e) = 2T(v)-D(v),  D(v)=Σ_{f endpoint at v} ell(f);  μ(e)>=0 cut-edge traffic.

Targets to TEST exactly:
 (T1) does CD-TV with g=T give something like Σ_M|ΔT| <= Σ_B|ΔT|, and is Σ_B|ΔT| controllable by sqrt-ish terms?
 (T2) Cauchy-Schwarz on cut edges:  Σ_B (T_x-T_y)² relation to ΣT²? Laplacian quadratic form.
      Define L_B = graph Laplacian of B. Then x^T L_B x = Σ_{xy in B}(x_x-x_y)². For x=T:
        T^T L_B T = Σ_B (ΔT)². Compare to 25ΣT²? and to Γ(N²+25N-Γ)?
 (T3) The KEY quantity from handshake: μ-weighted. Σ_v T(v)*(2T(v)-D(v)) = Σ_v T(v)Σ_{e∋v}μ(e)
        = Σ_{e=xy in B} μ(e)(T_x+T_y). So 2ΣT² - Σ_v T(v)D(v) = Σ_{B} μ(e)(T_x+T_y).
      Report Σ T·D and Σ_B μ(T_x+T_y).
We just TABULATE these exact quantities to look for a clean inequality that yields STAR. No proof claim yet.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def quantities(n,E,side):
    adj=adj_of(n,E)
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); ST2=sum(t*t for t in T)
    # CD-TV with g=T
    tvM=sum(abs(T[u]-T[v]) for u in range(n) for v in adj[u] if v>u and side[u]==side[v])
    tvB=sum(abs(T[u]-T[v]) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    # Laplacian quadratic forms
    LB=sum((T[u]-T[v])**2 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    LM=sum((T[u]-T[v])**2 for u in range(n) for v in adj[u] if v>u and side[u]==side[v])
    # handshake identity check
    D=[F(0)]*n
    for f in M:
        D[f[0]]+=ell[f]; D[f[1]]+=ell[f]
    # mu sum per vertex
    musum=[F(0)]*n
    for e,val in mu.items():
        musum[e[0]]+=val; musum[e[1]]+=val
    hs_ok=all(musum[v]==2*T[v]-D[v] for v in range(n))
    sumTD=sum(T[v]*D[v] for v in range(n))
    sumMuTT=sum(val*(T[e[0]]+T[e[1]]) for e,val in mu.items())
    return dict(N=N,Gamma=Gamma,ST2=ST2,tvM=tvM,tvB=tvB,cdtv_ok=tvM<=tvB,
                LB=LB,LM=LM, hs_ok=hs_ok, sumTD=sumTD, sumMuTT=sumMuTT,
                star_lhs=25*ST2, star_rhs=Gamma*(N*N+25*N-Gamma),
                LMleLB=LM<=LB)

if __name__=="__main__":
    from _bdef_construct import mycielski, Cn
    from _verify_two_lane import build_two_lane
    print("=== CD-TV / Laplacian / handshake quantities ===",flush=True)
    def show(lbl,r):
        if r is None: print(f"  {lbl}: no struct"); return
        print(f"  {lbl}: N={r['N']} G={r['Gamma']} ST2={r['ST2']}")
        print(f"     CD-TV(T): tvM={r['tvM']} tvB={r['tvB']} ok={r['cdtv_ok']}")
        print(f"     Laplacian: LM=Σ_M(ΔT)²={r['LM']} LB=Σ_B(ΔT)²={r['LB']} LM<=LB:{r['LMleLB']}")
        print(f"     handshake ok={r['hs_ok']} ΣT·D={r['sumTD']} Σ_Bμ(Tx+Ty)={r['sumMuTT']} 2ST2-ΣTD={2*r['ST2']-r['sumTD']}")
        print(f"     STAR: 25ST2={r['star_lhs']} <= G(N2+25N-G)={r['star_rhs']} ? {r['star_lhs']<=r['star_rhs']}")
        # candidate: is 25*ST2 <= ... related to LB?  print ratio
        print(f"     LB/ST2={float(r['LB']/r['ST2']) if r['ST2'] else 0:.3f}  (N²+25N-G)-25ST2/G={float((r['N']**2+25*r['N']-r['Gamma'])-F(25*r['ST2'],r['Gamma'])):.3f}")
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",quantities(n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Grotzsch N=11",quantities(g1[0],g1[1],info['side']))
    # one tight blowup
    info=loads(*build_two_lane(8)[:2]) if False else None
    print("=== done ===",flush=True)
