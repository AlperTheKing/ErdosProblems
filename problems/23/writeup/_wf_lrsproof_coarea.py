"""WF LRS-proof: coarea/CD attack, robust (explicit cut sides for large graphs).

Validates intermediates of a coarea/CD attack on
    (LRS)  sum_v T(v)(T(v)-N) <= Gamma*(N^2/25 - |M|).

For each (n, E, side) we use struct_for_side (NO brute-force maxcut) to get
T, ell, M, geodesic measure p_f. Then we exact-check:
  - handshake:  sum_v T(v) == sum_f ell(f)^2 == Gamma
  - coarea identity: sum_v T(T-N) == int_0^inf (2s-N)|H_s| ds
  - CD-superlevel sublemma: delta_M(H_s) <= delta_B(H_s) for all s  (HUNT CE)
  - overload-isoperimetry: |H_s| <= delta_B(H_s) for s>N            (HUNT CE)
  - LRS itself.

We never assume Erdos / |M|<=N^2/25 / LRS.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def coarea_rhs(T,N):
    allv=sorted(set([F(0)]+list(T)))
    tot=F(0)
    for i in range(len(allv)-1):
        lo=allv[i]; hi=allv[i+1]
        cnt=sum(1 for t in T if t>=hi)
        tot += ((hi*hi-lo*lo) - N*(hi-lo))*cnt
    return tot

def boundary(n,adj,side,S):
    dM=dB=0
    for u in range(n):
        for v in adj[u]:
            if v>u and ((u in S)!=(v in S)):
                if side[u]!=side[v]: dB+=1
                else: dM+=1
    return dM,dB

def analyze(n,E,side):
    adj=adj_of(n,E)
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); Gamma2=sum(ell[f]**2 for f in M)
    beta=len(M)
    lhs=sum(t*(t-N) for t in T)
    rhs=Gamma*(F(N*N,25)-beta)
    ca=coarea_rhs(T,N)
    cd_viol=[]; iso_viol=[]
    for s in sorted(set(T)):
        Hs=set(v for v in range(N) if T[v]>=s)
        if not Hs or len(Hs)==N: continue
        dM,dB=boundary(n,adj,side,Hs)
        if dM>dB: cd_viol.append((str(s),dM,dB,len(Hs)))
        if s>N and len(Hs)>dB: iso_viol.append((str(s),len(Hs),dB))
    return dict(N=N,beta=beta,Gamma=Gamma,Gamma2=Gamma2,
                handshake=(Gamma==Gamma2),lhs=lhs,rhs=rhs,
                lrs_ok=lhs<=rhs, coarea_ok=ca==lhs,
                cd_viol=cd_viol, iso_viol=iso_viol, Tmax=max(T),
                over=[v for v in range(N) if T[v]>N])

def show(lbl,r):
    if r is None: print(f"  {lbl}: (no struct / no bad edges)"); return
    print(f"  {lbl}: N={r['N']} beta={r['beta']} handshake={r['handshake']} "
          f"coarea={'OK' if r['coarea_ok'] else 'FAIL'} LRS={'OK' if r['lrs_ok'] else 'FAIL'} "
          f"Tmax={float(r['Tmax']):.3f} |over|={len(r['over'])}")
    if not r['handshake']: print(f"     HANDSHAKE FAIL Gamma={r['Gamma']} Gamma2={r['Gamma2']}")
    if r['cd_viol']: print(f"     CD-superlevel VIOL delta_M>delta_B: {r['cd_viol'][:6]}")
    if r['iso_viol']: print(f"     OVERLOAD-ISO VIOL |H_s|>delta_B (s>N): {r['iso_viol'][:6]}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== coarea + CD/iso on explicit-side constructions ===",flush=True)
    for L in (8,12,20,30):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",analyze(n,E,side))
    print("--- Mycielskians (loads brute for N<=11) ---",flush=True)
    g1=mycielski(5,Cn(5))   # Grotzsch N=11
    info=loads(*g1)
    if info: show("Myc(C5)=Grotzsch N=11",analyze(g1[0],g1[1],info['side']))
    print("--- census N=5..9 gamma-min: CD/iso violation hunt ---",flush=True)
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=cdv=isov=lrsf=caf=hsf=0; fcd=fiso=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=analyze(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['handshake']: hsf+=1
            if not r['coarea_ok']: caf+=1
            if not r['lrs_ok']: lrsf+=1
            if r['cd_viol']: cdv+=1; fcd=fcd or (g6,r['cd_viol'][0])
            if r['iso_viol']: isov+=1; fiso=fiso or (g6,r['iso_viol'][0])
        print(f"  N={nn}: structs={ng} handshake_fail={hsf} coarea_fail={caf} LRS_fail={lrsf} "
              f"CD_viol={cdv} iso_viol={isov}",flush=True)
        if fcd: print(f"     first CD viol: {fcd}")
        if fiso: print(f"     first iso viol: {fiso}")
    print("=== done ===",flush=True)
