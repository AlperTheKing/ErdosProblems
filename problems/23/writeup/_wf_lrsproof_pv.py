"""Test the PER-VERTEX sublemma that would prove STAR by summing:
   (PV)   for every v:  25*T(v) <= N²+25N - Γ,   i.e.  T(v) <= (N²+25N-Γ)/25 = N + (N²-Γ)/25.
Summing 25 T(v)·T(v) <= T(v)(N²+25N-Γ) over v gives 25ΣT² <= Γ(N²+25N-Γ) = STAR. EXACT.
PV is tight at C5[t] (T≡N, Γ=N², RHS=N). HUNT counterexamples; if PV fails, STAR has cancellation PV lacks.
Also test the weaker max form:  max_v T(v) <= N + (N²-Γ)/25.
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

def pv(n,E,side):
    st=struct_for_side(n,adj_of(n,E),side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T)
    bound=F(N*N+25*N-Gamma,25)   # = N+(N²-Γ)/25
    viol=[(v,T[v]) for v in range(n) if T[v]>bound]
    return dict(N=N,Gamma=Gamma,bound=bound,Tmax=max(T),
                pv_ok=not viol, viol=viol[:4])

def show(lbl,r):
    if r is None: print(f"  {lbl}: no struct"); return
    print(f"  {lbl}: N={r['N']} G={r['Gamma']} bound=N+(N2-G)/25={float(r['bound']):.3f} "
          f"Tmax={float(r['Tmax']):.3f} PV={'OK' if r['pv_ok'] else 'FAIL'}"
          + (f"  viol={[(v,str(t)) for v,t in r['viol']]}" if not r['pv_ok'] else ""))

if __name__=="__main__":
    from _verify_two_lane import build_two_lane
    print("=== PER-VERTEX sublemma T(v) <= N+(N2-G)/25 (would prove STAR) ===",flush=True)
    for L in (8,12,20):
        n,E,side,bad=build_two_lane(L); show(f"two-lane L={L}",pv(n,E,side))
    g1=mycielski(5,Cn(5)); info=loads(*g1)
    if info: show("Grotzsch N=11",pv(g1[0],g1[1],info['side']))
    for k in (5,7,9):
        for t in (1,2,3):
            n,E=blow_g(k,Cn(k),t)
            if n>20: continue
            info=loads(n,E)
            if info: show(f"C{k}[{t}]",pv(n,E,info['side']))
    print("--- census N=5..10: PV violations ---",flush=True)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=pvf=0; first=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=pv(n,E,info['side'])
            if r is None: continue
            ng+=1
            if not r['pv_ok']: pvf+=1; first=first or (g6,r['viol'],float(r['bound']))
        print(f"  N={nn}: structs={ng} PV_viol={pvf}",flush=True)
        if first: print(f"     first PV viol: g6={first[0]} bound={first[2]} viol={[(v,str(t)) for v,t in first[1]]}")
    print("=== done ===",flush=True)
