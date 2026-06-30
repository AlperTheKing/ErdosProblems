"""Test the STRONGER clean target U+ := Σ_{T>N} T(T-N) <= Γ(N^2/25-|M|), and several non-lossy tail bounds.

Since I_total = U+ - U- and U- >= 0, U+ <= slack  ==>  LRS. So U+<=slack is a clean (stronger) sufficient target.
Hunt counterexamples to U+<=slack across the full gate.

Also probe tail-bound mechanisms that are NOT the lossy delta_B integral:
 (L-lemma)  for overload superlevel A={T>=c}, c>N:  Σ_{v∈A}T(v) <= N*deltaB(A).   [from consult, verified 0-fail]
            => c|A| <= Σ_A T <= N deltaB(A) => |A| <= (N/c) deltaB(A) < deltaB(A).
 Using (L) to bound U+ = ∫_N^∞ (2s-N)|H_s|ds with |H_s| <= (1/s)Σ_{H_s}T... gives a refined tail.
We just (a) confirm U+<=slack 0-fail, (b) measure margins/equality, (c) see if U+ has a clean closed sub-bound.
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

def deltaB(n,adj,side,S):
    d=0
    for u in range(n):
        for v in adj[u]:
            if v>u and ((u in S)!=(v in S)) and side[u]!=side[v]: d+=1
    return d

def test(n,E,side):
    adj=adj_of(n,E)
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); beta=len(M)
    I_total=sum(t*(t-N) for t in T)
    Uplus=sum(t*(t-N) for t in T if t>N)
    slack=Gamma*(F(N*N,25)-beta)
    # L-lemma check on all overload superlevels c>N:  Σ_{A}T <= N*deltaB(A)
    Lviol=[]
    for c in sorted(set(t for t in T if t>N)):
        A=set(v for v in range(n) if T[v]>=c)
        sA=sum(T[v] for v in A); dB=deltaB(n,adj,side,A)
        if sA>N*dB: Lviol.append((str(c),str(sA),dB))
    return dict(N=N,beta=beta,Gamma=Gamma,Uplus=Uplus,slack=slack,
                Uplus_ok=Uplus<=slack, lrs=I_total<=slack, Lviol=Lviol)

def show(lbl,r):
    if r is None: print(f"  {lbl}: no struct"); return
    flag="" if r['Uplus_ok'] else "  <<< U+ > slack"
    lf="" if not r['Lviol'] else f"  L-VIOL {r['Lviol'][:3]}"
    print(f"  {lbl}: N={r['N']} m={r['beta']} U+={r['Uplus']}({float(r['Uplus']):.2f}) "
          f"slack={float(r['slack']):.2f} U+<=slack={r['Uplus_ok']} LRS={r['lrs']}{flag}{lf}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== U+<=slack (stronger clean target) + L-lemma probe ===",flush=True)
    for L in (8,12,20,30):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",test(n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Grotzsch N=11",test(g1[0],g1[1],info['side']))
    print("--- census N=5..10: U+>slack and L-lemma violations ---",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=uv=lv=lrsf=0; worstU=None; firstU=None; firstL=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=test(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['lrs']: lrsf+=1
            if not r['Uplus_ok']: uv+=1; firstU=firstU or (g6,float(r['Uplus']),float(r['slack']))
            if r['Lviol']: lv+=1; firstL=firstL or (g6,r['Lviol'][0])
            m=r['slack']-r['Uplus']
            if worstU is None or m<worstU[1]: worstU=(g6,m)
        print(f"  N={nn}: structs={ng} U+>slack={uv} L_lemma_viol={lv} LRS_viol={lrsf} "
              f"min(slack-U+)={float(worstU[1]) if worstU else 'NA':.3f} at {worstU[0] if worstU else ''}",flush=True)
        if firstU: print(f"     first U+>slack: {firstU}")
        if firstL: print(f"     first L-lemma viol: {firstL}")
    print("=== done ===",flush=True)
