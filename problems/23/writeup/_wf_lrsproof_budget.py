"""CRUX budget inequality test (EXACT), the last link of the coarea/CD chain for LRS.

Chain:  ΣT(T-N) <= U+ := Σ_{T>N}T(T-N) = ∫_N^inf (2s-N)|H_s^>| ds          [drop under-load <=0]
                  <= ∫_N^inf (2s-N) deltaB(H_s^>) ds  =: J                 [overload-iso |H|<=deltaB, s>N]
                  <= Γ*(N^2/25 - |M|)                                       [BUDGET, the new crux]

We test, EXACT, on the full standing gate:
  - U+ <= J  (iso tail), and J <= slack (BUDGET), and U+ <= slack, and the full LRS.
  - report margins, equality cases, and HUNT for any BUDGET violation (J > slack).
  - also a WEAKER but maybe-true budget: J <= slack ? if it fails, try J <= Γ*N^2/25 - something.

If BUDGET fails anywhere, the chain is broken there: report the exact witness.
Battery: census N<=10 (loads cut), two-lane L<=30, Mycielskians (Grotzsch N=11; Myc^2 N=23 via explicit cut from
loads on N=23 -- too big; instead use known max cut = the proper 4-coloring side? Mycielskian needs its max cut).
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

def J_and_Uplus(n,adj,side,T,N):
    """J=int_{s>N}(2s-N)deltaB(H_s^>)ds ; Uplus=int_{s>N}(2s-N)|H_s^>|ds.
    bands between consecutive distinct T-values > N; on (a,b] H=={v:T>=b}."""
    vals=sorted(set(t for t in T if t>N))
    pts=[F(N)]+vals
    J=F(0); U=F(0)
    for i in range(len(pts)-1):
        a=pts[i]; b=pts[i+1]
        H=set(v for v in range(n) if T[v]>=b)
        if not H: continue
        w=(b*b-a*a)-N*(b-a)
        J += w*deltaB(n,adj,side,H)
        U += w*len(H)
    return J,U

def test(lbl,n,E,side):
    adj=adj_of(n,E)
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); beta=len(M)
    I_total=sum(t*(t-N) for t in T)
    Uplus_direct=sum(t*(t-N) for t in T if t>N)
    J,U=J_and_Uplus(n,adj,side,T,N)
    slack=Gamma*(F(N*N,25)-beta)
    return dict(N=N,beta=beta,Gamma=Gamma,I_total=I_total,Uplus=Uplus_direct,
                Uint=U,J=J,slack=slack,
                iso_ok=(U<=J), Uplus_match=(U==Uplus_direct),
                budget_ok=(J<=slack), full_ok=(I_total<=slack),
                Uplus_le_slack=(Uplus_direct<=slack))

def show(lbl,r):
    if r is None: print(f"  {lbl}: no struct"); return
    flag="" if r['budget_ok'] else "  <<< BUDGET VIOLATION"
    print(f"  {lbl}: N={r['N']} m={r['beta']} G={r['Gamma']} U+={r['Uplus']} J={r['J']} "
          f"slack={r['slack']} iso={r['iso_ok']} U+match={r['Uplus_match']} "
          f"budget(J<=slack)={r['budget_ok']} LRS={r['full_ok']}{flag}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== BUDGET crux test ===",flush=True)
    for L in (8,12,20,30):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",test(f"L{L}",n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Grotzsch N=11",test("gr",g1[0],g1[1],info['side']))
    # odd blowups
    for k in (5,7,9):
        for t in (1,2,3):
            n,E=blow_g(k,Cn(k),t)
            if n>20: continue
            info=loads(n,E)
            if info: show(f"C{k}[{t}]",test("b",n,E,info['side']))
    print("--- census N=5..10: BUDGET + iso violation hunt (loads cut) ---",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=bv=iv=fv=0; worst=None; firstb=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=test(g6,n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['iso_ok']: iv+=1
            if not r['full_ok']: fv+=1
            if not r['budget_ok']:
                bv+=1; firstb=firstb or (g6,r['J'],r['slack'])
            # track min budget margin (slack-J)
            marg=r['slack']-r['J']
            if worst is None or marg<worst[1]: worst=(g6,marg)
        print(f"  N={nn}: structs={ng} iso_viol={iv} BUDGET_viol={bv} LRS_viol={fv}  min(slack-J)={worst[1] if worst else 'NA'} at {worst[0] if worst else ''}",flush=True)
        if firstb: print(f"     first BUDGET viol: {firstb}")
    print("=== done ===",flush=True)
