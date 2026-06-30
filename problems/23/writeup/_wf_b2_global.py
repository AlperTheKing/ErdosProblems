"""Test GLOBAL/geometric bounds that could prove T[v]<=2N, and check the trend across
larger Mycielskians to see if sup(T/N) stays <2.
 Quantities: Dall[v]=sum_{f: c_f(v)>0} ell_f ; T[v]<=Dall trivially? verify.
 Bounds:
   G1: T[v] <= Dall[v]                        (each c_f(v)<=ell_f)
   G2: Dall[v] <= 2N
   G3: T[v] <= (1/2) sum_{u~v in B} (T[u] adjacency)...  skip
   G4: nbad(v) <= dc[v]                        (#bad edges meeting v's geodesics <= cut-deg? ) - explore
   G5: T[v] <= N + (1/2)D[v] + ...
 Also: scan Myc(C9)=N19, Myc(C11)=N23, Myc(Grotzsch)=N23 to map sup(T/N).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, blow, Bconn
from _bdef_construct import Cn, mycielski, is_triangle_free
from _satzmu_conn import struct_for_side
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees
from ortools.sat.python import cp_model

def vrows(n,adj,side):
    st=struct_for_side(n,adj,side); cd=cut_data(n,adj,side)
    if st is None or cd is None: return None
    M,ell,T,mu,cyc=st; N=n; dc,dm=cut_degrees(cd); rows=[]
    for v in range(N):
        Dall=0; nb=0
        for f in M:
            if any(v in P for P in cyc[f]): Dall+=ell[f]; nb+=1
        rows.append(dict(v=v,T=T[v],dc=dc[v],dm=dm[v],D=cd['D'][v],Dall=Dall,nbad=nb,N=N))
    return rows

def cpcuts(N,E):
    adj=[set() for _ in range(N)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]; tt=[]
    for a,b in E:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); tt.append(z)
    m.Maximize(sum(tt)); sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=90; sv.Solve(m)
    opt=int(sv.ObjectiveValue()); m.Add(sum(tt)==opt)
    class C(cp_model.CpSolverSolutionCallback):
        def __init__(s): super().__init__(); s.sols=[]
        def on_solution_callback(s):
            s.sols.append([int(s.Value(x[i])) for i in range(N)])
            if len(s.sols)>=60: s.StopSearch()
    sv2=cp_model.CpSolver(); sv2.parameters.enumerate_all_solutions=True; sv2.parameters.max_time_in_seconds=90
    c=C(); sv2.Solve(m,c); return adj,[s for s in c.sols if Bconn(N,adj,s)]

if __name__=="__main__":
    G1=G2=None; G1w=G2w=None; supr=F(0); supw=None
    def feed(name,rows):
        global G1,G2,G1w,G2w,supr,supw
        for s in rows:
            r=F(s['T'],s['N'])
            if r>supr: supr=r; supw=(name,s)
            g1=s['T']-s['Dall']; g2=F(s['Dall'])-2*s['N']
            if G1 is None or g1>G1: G1=g1; G1w=(name,s)
            if G2 is None or g2>G2: G2=g2; G2w=(name,s)
    def brute(name,n,E):
        if not is_triangle_free(n,E): return
        adj,cuts=gmin_cuts(n,E)
        for sd in cuts:
            r=vrows(n,adj,sd)
            if r: feed(name,r)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: brute("c"+g6,*dec(g6))
        print(f"  census N={nn} done sup={float(supr):.4f}",flush=True)
    for t in range(1,5): brute(f"C5[{t}]",*blow(t))
    brute("Grotzsch11",*mycielski(5,Cn(5)))
    targets=[("MycC7_15",mycielski(7,Cn(7))),
             ("MycC9_19",mycielski(9,Cn(9))),
             ("MycC11_23",mycielski(11,Cn(11))),
             ("Myc2C5_23",mycielski(*mycielski(5,Cn(5))))]
    for nm,(N,E) in targets:
        if N>23: continue
        adj,cuts=cpcuts(N,E)
        for s in cuts:
            r=vrows(N,adj,s)
            if r: feed(nm,r)
        print(f"  {nm} (N={N}) done sup={float(supr):.4f}",flush=True)
    print("\n=== GLOBAL bounds ===")
    print(f"  sup T/N over gate = {float(supr):.6f}={supr}  @ {supw[0]} v={supw[1]['v']} N={supw[1]['N']} T={float(supw[1]['T']):.3f} dc={supw[1]['dc']} Dall={supw[1]['Dall']} nbad={supw[1]['nbad']}")
    print(f"  G1 T<=Dall: max-resid={float(G1):+.4f} {'HOLDS' if G1<=0 else 'FALSE'} @ {G1w[0]} (T={float(G1w[1]['T']):.2f} Dall={G1w[1]['Dall']})")
    print(f"  G2 Dall<=2N: max-resid={float(G2):+.4f} {'HOLDS' if G2<=0 else 'FALSE'} @ {G2w[0]} v={G2w[1]['v']} N={G2w[1]['N']} Dall={G2w[1]['Dall']} nbad={G2w[1]['nbad']} dc={G2w[1]['dc']}")
