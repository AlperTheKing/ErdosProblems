"""Probe candidate coarea/CD bounding chains for LRS, EXACT, on graphs where the slack is used (two-lane L>=12).

LRS:  ΣT(T-N) <= Γ*(N^2/25 - |M|).
Coarea: ΣT(T-N) = int_0^inf (2s-N)|H_s^>| ds,  H_s^>={v:T(v)>s}.

We tabulate, on two-lane L=12,20 and census, several candidate UPPER bounds B for ΣT(T-N) and
check (a) B >= ΣT(T-N) (valid upper bound?) and (b) B <= Γ*(N^2/25-|M|) (does it close?).

Candidate bounds:
 (C-iso)  using |H_s^>| <= delta_B(H_s) for s>N and |H_s^>| arbitrary for s<=N:
           split int = int_{0}^{N} (2s-N)|H_s| ds + int_{N}^{inf}(2s-N)|H_s|ds.
           The second (overload) integral <= int_N^inf (2s-N) delta_B(H_s) ds.
           BUT the first integral is NEGATIVE-leaning; we keep it exact.
 We compute:
   I_total = ΣT(T-N) (exact, the truth)
   I_over  = int_{s>N} (2s-N)|H_s| ds   (overload tail, exact) = Σ_{v:T>N}(T^2-NT)+ ... careful, see code
   I_over_iso = int_{s>N} (2s-N) delta_B(H_s) ds  (replace |H_s| by delta_B(H_s); needs delta_B as step fn)
 We test:  I_over <= I_over_iso  (per-the-iso-sublemma upper bound on the overload tail) -- should hold
 And the budget question: I_over_iso <= Γ*(N^2/25-|M|) + (under-load credit)?  i.e. does the iso tail bound
 already fit in the slack, or do we still need the under-load region?

Goal: find the SIMPLEST true chain B with I_total <= B <= Γ*(N^2/25-|M|).
"""
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side
import subprocess

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

def step_integral(n,adj,side,T,N,lo_bound, weightfn):
    """int over s in (lo_bound, inf) of (2s-N)*weightfn(H_s^>) ds, where H_s^>={v:T>s}.
    weightfn maps a vertex SET to a number (e.g. |.| or delta_B). Step changes at T-values.
    On band (a,b] with a>=lo_bound: H_s^> for s in (a,b] = {v:T>b}? No: H_s^>={v:T(v)>s}; for s in (a,b),
    threshold strictly between a,b excludes T==a and any T<=s; smallest s just above a -> {v:T(v)>a}=...
    Actually for s in (a,b) with a,b consecutive distinct T-values, {v:T(v)>s} = {v:T(v)>=b} = {v:T(v)>a}.
    Use H = {v:T(v)>=b}. weight constant on band. Integral of (2s-N) over (a,b) = (b^2-a^2)-N(b-a).
    """
    vals=sorted(set(T))
    tot=F(0)
    # bands between consecutive sorted distinct T-values, plus from lo_bound up
    pts=sorted(set([lo_bound]+[t for t in vals if t>lo_bound]))
    # ensure lo_bound is a left endpoint
    for i in range(len(pts)-1):
        a=pts[i]; b=pts[i+1]
        H=set(v for v in range(n) if T[v]>=b)
        if not H: continue
        w=weightfn(H)
        tot += (((b*b-a*a)-N*(b-a)))*w
    return tot

def probe(lbl,n,E,side):
    adj=adj_of(n,E)
    st=struct_for_side(n,adj,side)
    if st is None: print(f"  {lbl}: no struct"); return
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); beta=len(M)
    I_total=sum(t*(t-N) for t in T)
    slack=Gamma*(F(N*N,25)-beta)
    card=lambda H:len(H)
    dB=lambda H:deltaB(n,adj,side,H)
    # overload tail (s>N) with true |H_s| and with delta_B
    I_over=step_integral(n,adj,side,T,N,F(N),card)
    I_over_iso=step_integral(n,adj,side,T,N,F(N),dB)
    # full integral with card from 0 should equal I_total
    I_check=step_integral(n,adj,side,T,N,F(0),card)
    print(f"  {lbl}: N={N} beta={beta} Gamma={Gamma}")
    print(f"     I_total={I_total}  coarea_check={I_check==I_total}")
    print(f"     I_over(s>N,|H|)={I_over}  I_over_iso(s>N,deltaB)={I_over_iso}  iso_tail_ok={I_over<=I_over_iso}")
    print(f"     slack=G(N2/25-|M|)={slack}={float(slack):.1f}  I_over<=slack:{I_over<=slack}  I_over_iso<=slack:{I_over_iso<=slack}")
    print(f"     I_total<=slack (LRS):{I_total<=slack}")

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== coarea bounding chain probe (slack-using regime) ===",flush=True)
    for L in (8,12,20):
        n,E,side,bad=build_two_lane(L); probe(f"two-lane L={L}",n,E,side)
    # a census slack-user? census N<=9 had SM_ok everywhere, so pick a bigger one if any; just show N=8 sample
    print("=== done ===",flush=True)
