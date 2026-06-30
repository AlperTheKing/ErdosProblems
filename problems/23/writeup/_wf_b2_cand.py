"""Search for the binding PROVABLE upper bound on T[v]. Test many candidate RHS forms
exactly on the gate; report which hold (max residual<=0) and how tight.
Quantities at v on a cut: T, dc(cut-deg), dm(mono-deg), D=sum_{f thru v as endpoint}ell_f,
 inc=sum_{e at v}mu(e), nbad=#bad edges f with c_f(v)>0, g=#distinct geodesic-edges at v,
 ellmax_v=max ell over bad edges with c_f(v)>0, N.
Candidates (must be PROVABLE from structure, not Erdos):
  C_A: T <= dc*N
  C_B: T <= N + D                       (T-D<=N ?)  [D=own bad-edge ell-sum]
  C_C: 2T <= dc*ellmax_v + D
  C_D: T <= (ellmax_v/2)*dc             (=5/2*dc when girth5)
  C_E: T <= N + (dc-dm)*?  ...
  C_F: T <= N + (1/2)sum_{e at v}(mu(e)-?)  ...
  C_G: inc <= dc*ellmax_v               (avg mu per edge <= ellmax_v)
  C_H: T <= ellmax_v * dc - (ellmax_v-1)*1 ...
We just print residuals for the family and the witness.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, blow, Bconn
from _bdef_construct import Cn, mycielski, is_triangle_free
from _satzmu_conn import struct_for_side
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees
from ortools.sat.python import cp_model

def vstats(n,adj,side):
    st=struct_for_side(n,adj,side)
    cd=cut_data(n,adj,side)
    if st is None or cd is None: return None
    M,ell,T,mu,cyc=st; N=n; dc,dm=cut_degrees(cd)
    out=[]
    for v in range(N):
        contribs=[]  # (ell_f) for bad edges with c_f(v)>0
        gedges=set()
        for f in M:
            Ps=cyc[f]; thru=False
            for P in Ps:
                if v in P:
                    thru=True
                    i=P.index(v)
                    if i>0: gedges.add((min(P[i-1],v),max(P[i-1],v)))
                    if i<len(P)-1: gedges.add((min(P[i+1],v),max(P[i+1],v)))
            if thru: contribs.append(ell[f])
        ellmax=max(contribs) if contribs else 0
        out.append(dict(v=v,T=T[v],dc=dc[v],dm=dm[v],D=cd['D'][v],inc=cd['inc'][v],
                        nbad=len(contribs),g=len(gedges),ellmax=ellmax,N=N))
    return out

CANDS={
 'C_A T<=dc*N':       lambda s: s['T']-s['dc']*s['N'],
 'C_B T<=N+D':        lambda s: s['T']-s['N']-s['D'],
 'C_C 2T<=dc*ellmax+D':lambda s: 2*s['T']-s['dc']*s['ellmax']-s['D'],
 'C_D 2T<=ellmax*dc': lambda s: 2*s['T']-s['ellmax']*s['dc'],
 'C_G inc<=dc*ellmax':lambda s: s['inc']-s['dc']*s['ellmax'],
 'C_I T<=g*ellmax/2':  lambda s: 2*s['T']-s['g']*s['ellmax'],
 'C_J 2T<=g*ellmax':   lambda s: 2*s['T']-s['g']*s['ellmax'],
 'C_K T<=(ellmax/2)*dc + N - ?':lambda s: 2*s['T']-s['ellmax']*s['dc'],
 'C_L 2T<=dc*N/... B2':lambda s: s['T']-2*s['N'],
}

if __name__=="__main__":
    worst={k:{'val':F(-10**12)} for k in CANDS}
    def feed(name,n,adj,side):
        st=vstats(n,adj,side)
        if st is None: return
        for s in st:
            for k,fn in CANDS.items():
                val=fn(s)
                if val>worst[k]['val']: worst[k]={'val':val,'where':name,**s}
    def brute(name,n,E):
        if not is_triangle_free(n,E): return
        adj,cuts=gmin_cuts(n,E)
        for sd in cuts: feed(name,n,adj,sd)
    def cpcuts(N,E):
        adj=[set() for _ in range(N)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]; tt=[]
        for a,b in E:
            z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); tt.append(z)
        m.Maximize(sum(tt)); sv=cp_model.CpSolver(); sv.parameters.max_time_in_seconds=60; sv.Solve(m)
        opt=int(sv.ObjectiveValue()); m.Add(sum(tt)==opt)
        class C(cp_model.CpSolverSolutionCallback):
            def __init__(s): super().__init__(); s.sols=[]
            def on_solution_callback(s):
                s.sols.append([int(s.Value(x[i])) for i in range(N)])
                if len(s.sols)>=100: s.StopSearch()
        sv2=cp_model.CpSolver(); sv2.parameters.enumerate_all_solutions=True; sv2.parameters.max_time_in_seconds=60
        c=C(); sv2.Solve(m,c); return adj,[s for s in c.sols if Bconn(N,adj,s)]
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: brute("c"+g6,*dec(g6))
        print(f"  census N={nn} done",flush=True)
    for t in range(1,5): brute(f"C5[{t}]",*blow(t))
    brute("Grotzsch11",*mycielski(5,Cn(5)))
    for nm,(N,E) in [("MycC7_15",mycielski(7,Cn(7))),("Myc2C5_23",mycielski(*mycielski(5,Cn(5))))]:
        adj,cuts=cpcuts(N,E)
        for s in cuts: feed(nm,N,adj,s)
        print(f"  {nm} done",flush=True)
    print("\n=== candidate bounds (residual<=0 => HOLDS on gate) ===")
    for k in CANDS:
        d=worst[k]; ok = d['val']<=0
        print(f"  {k:24s} max-resid={float(d['val']):+.4f}  {'HOLDS' if ok else '*** FALSE ***'}  "
              f"@ {d.get('where')} v={d.get('v')} N={d.get('N')} T={float(d.get('T',0)):.2f} "
              f"dc={d.get('dc')} dm={d.get('dm')} D={float(d.get('D',0)):.2f} g={d.get('g')} ellmax={d.get('ellmax')} nbad={d.get('nbad')}")
