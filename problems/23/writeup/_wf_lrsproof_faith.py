"""Faithfulness + N=23 iterated-Mycielskian gate for STAR.

STAR: 25*ΣT² <= Γ(N²+25N-Γ),  Γ=ΣT.   (proven => #23 via Cauchy-Schwarz)

(A) FAITHFULNESS: STAR must FAIL on some graphs WITH triangles (else it's a free fact, can't imply #23).
    We build the load struct for graphs WITH triangles (struct_for_side still computes geodesic loads; ell may be<5).
    Use small census of ALL graphs (geng without -t) and report STAR violations among those with a triangle.

(B) N=23 GATE: iterated Mycielskian C5->Grotzsch(11)->Myc(11)=N23. Needs its max cut. We get it via CP-SAT
    (ortools) maxcut, then build struct on that side, exact STAR. This is the standing gate that killed finite-depth.

(C) also confirm STAR uses ell>=5 by checking the per-graph minimal ell on STAR-violating triangle graphs.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def has_tri(n,E):
    adj=adj_of(n,E)
    for a,b in E:
        if adj[a]&adj[b]: return True
    return False

def star_for_side(n,E,side):
    st=struct_for_side(n,adj_of(n,E),side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    Gamma=sum(T); ST2=sum(t*t for t in T)
    lhs=25*ST2; rhs=Gamma*(N*N+25*N-Gamma)
    minell=min(ell.values()) if ell else None
    return dict(N=N,Gamma=Gamma,ST2=ST2,star=lhs<=rhs,margin=rhs-lhs,minell=minell,m=len(M))

def cpmax_side(n,E):
    from ortools.sat.python import cp_model
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(n)]; t=[]
    for a,b in E:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=120
    s.parameters.num_search_workers=8
    st=s.Solve(m)
    return [int(s.Value(x[i])) for i in range(n)], int(s.ObjectiveValue()), s.BestObjectiveBound()

if __name__=="__main__":
    print("=== (A) FAITHFULNESS: STAR on graphs WITH triangles (max cut via loads brute, ALL graphs) ===",flush=True)
    for nn in (5,6,7):
        outg=subprocess.run([GENG,"-c",str(nn)],capture_output=True,text=True).stdout.split()  # all connected, may have triangles
        ntri=0; trifail=0; firstf=None
        for g6 in outg:
            n,E=dec(g6)
            if not has_tri(n,E): continue
            ntri+=1
            info=loads(n,E)
            if info is None: continue
            r=star_for_side(n,E,info['side'])
            if r is None: continue
            if not r['star']:
                trifail+=1; firstf=firstf or (g6,r['minell'],float(r['margin']))
        print(f"  N={nn}: triangle-graphs={ntri} STAR-violating={trifail}",flush=True)
        if firstf: print(f"     first triangle STAR-viol: g6={firstf[0]} minell={firstf[1]} margin={firstf[2]}")
        else: print("     (no triangle violation found at this N -- faithfulness weak here)")
    print("=== (B) N=23 iterated-Mycielskian gate (CP-SAT max cut) ===",flush=True)
    g1=mycielski(5,Cn(5))       # N=11 Grotzsch
    g2=mycielski(*g1)           # N=23
    for (N,E),lbl in [(g1,"Grotzsch N=11"),(g2,"Myc^2(C5) N=23")]:
        n=N
        side,opt,bd=cpmax_side(n,E)
        r=star_for_side(n,E,side)
        if r is None: print(f"  {lbl}: struct None (cut not connected-B?)"); continue
        print(f"  {lbl}: maxcut opt={opt} bound={bd} (optimal={opt==bd}) Gamma={r['Gamma']} "
              f"minell={r['minell']} STAR={r['star']} margin={float(r['margin']):.3f}",flush=True)
    print("=== done ===",flush=True)
