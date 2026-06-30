"""Does LRS genuinely USE the bad-count slack, or is the bare SM (ΣT(T-N)<=0) already true?

If SM (ΣT(T-N)<=0) holds everywhere on the gate, then LRS is 'morally SM' = Gamma<=N^2 hardness.
If SM FAILS somewhere (ΣT(T-N)>0) while LRS still holds, the slack Gamma*(N^2/25-|M|) is doing real work,
and proving LRS is strictly easier than SM. We need the second case for a non-circular easier route.

Report per test:  lhs=ΣT(T-N), slack=Gamma*(N^2/25-|M|), SM_ok (lhs<=0), LRS_ok (lhs<=slack),
and the SM 'deficit' lhs (positive => SM fails => slack used).
Battery: two-lane, Mycielskians (Grotzsch N=11; Myc^2 N=23 via explicit cut), C5/C7/C9 blowups, census N<=9.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, blow
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, blow_g

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def metrics(n,E,side):
    st=struct_for_side(n,adj_of(n,E),side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); beta=len(M)
    lhs=sum(t*(t-N) for t in T)
    slack=Gamma*(F(N*N,25)-beta)
    return dict(N=N,beta=beta,Gamma=Gamma,lhs=lhs,slack=slack,
                SM=lhs<=0, LRS=lhs<=slack, Tmax=max(T))

def odd_blow(k,t):  # C_k blow-up
    return blow_g(k, Cn(k), t)

def show(lbl,r):
    if r is None: print(f"  {lbl}: no struct"); return
    sm="SM_OK" if r['SM'] else "SM_FAIL(slack used)"
    print(f"  {lbl}: N={r['N']} beta={r['beta']} lhs(SM)={r['lhs']} slack={r['slack']} "
          f"{sm} LRS={'OK' if r['LRS'] else 'FAIL'}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== does LRS use the bad-count slack? ===",flush=True)
    for L in (8,12,20,30):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",metrics(n,E,side))
    # Mycielskians via loads (N<=11 brute). For Myc^2 (N=23) need explicit max cut: derive from loads? too big.
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Myc(C5)=Grotzsch N=11",metrics(g1[0],g1[1],info['side']))
    # odd-cycle blowups (loads brute up to N~20)
    for k in (5,7,9):
        for t in (1,2,3):
            n,E=odd_blow(k,t)
            if n>20: continue
            info=loads(n,E)
            if info: show(f"C{k}[{t}]",metrics(n,E,info['side']))
    print("--- census N=5..9: count SM_fail (slack genuinely used) vs LRS_fail ---",flush=True)
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=smf=lrsf=0; worst=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=metrics(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['SM']:
                smf+=1
                if worst is None or r['lhs']>worst[1]: worst=(g6,r['lhs'],r['slack'])
            if not r['LRS']: lrsf+=1
        print(f"  N={nn}: structs={ng} SM_fail(slack-used)={smf} LRS_fail={lrsf}",flush=True)
        if worst: print(f"     worst SM-deficit: {worst[0]} lhs={worst[1]} slack={worst[2]}")
    print("=== done ===",flush=True)
