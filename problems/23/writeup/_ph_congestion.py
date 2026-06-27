"""Test the CONGESTION/cycle transport (Step-2's fix for PH): charge each overshoot atom (f,C,w), T(w)>N,
mass m=(T(w)-N)(ell/n_f)/T(w), to underloaded vertices ON its cycle C (sinks z in C with T(z)<N, cap u(z)=N-T(z)),
demand 2m (the 2-to-1). Variant B: sinks = underloaded vertices on ANY shortest cycle of f (broader). Max-flow
feasible (>=2 U_over) ?  This replaces the prefix-defect CD shadow with the geodesic/congestion structure."""
from fractions import Fraction as F
from collections import defaultdict, deque
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def loads(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); cyc[f]=Ps
        if not Ps: return None
        sh=F(ell[f],len(Ps))
        for P in Ps:
            for v in P: T[v]+=sh
    Uover=sum((t-n) for t in T if t>n)
    return dict(n=n,M=M,ell=ell,T=T,cyc=cyc,Uover=Uover,G=G)

def maxflow(cap,s,t,V):
    flow=0.0
    while True:
        par={s:None}; q=deque([s])
        while q:
            u=q.popleft()
            if u==t: break
            for v in V:
                if v not in par and cap[u].get(v,0)>1e-12: par[v]=u; q.append(v)
        if t not in par: break
        b=float('inf'); v=t
        while par[v] is not None: u=par[v]; b=min(b,cap[u][v]); v=u
        v=t
        while par[v] is not None: u=par[v]; cap[u][v]-=b; cap[v][u]=cap[v].get(u,0)+b; v=u
        flow+=b
    return flow

def test(info, variant='cycle'):
    n=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; N=n; Uover=info['Uover']
    if Uover==0: return ('trivial',0.0,0.0)
    cap=defaultdict(lambda: defaultdict(float)); V=set(['__S','__T']); demand=0.0; k=0
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        # set of underloaded sinks for f
        if variant=='edge':   # broader: underloaded on ANY shortest cycle of f
            fund=set(z for P in Ps for z in P if T[z]<N)
        for C in Ps:
            csink = set(z for z in C if T[z]<N) if variant=='cycle' else fund
            for j,w in enumerate(C):
                if T[w]>N:
                    m=float((T[w]-N)*F(ell[f],nf)/T[w])
                    aid='A%d'%k; k+=1; V.add(aid)
                    cap['__S'][aid]+=2.0*m; demand+=2.0*m
                    for z in csink:
                        zid='Z%d'%z; V.add(zid); cap[aid][zid]=1e18
    for z in range(n):
        if T[z]<N:
            zid='Z%d'%z
            if zid in V: cap[zid]['__T']+=float(N-T[z])
    mf=maxflow(cap,'__S','__T',V)
    return ('feasible' if mf>=demand-1e-7 else 'INFEASIBLE', mf, demand)

if __name__=="__main__":
    fails=["I?BD@g]Qo","J?AADagROl?","J?ABA_we`Y?","J?ABAqoeaX?","J?ABCfGM@h?"]
    print("=== CONGESTION transport on the PH-failing graphs ===")
    for g6 in fails:
        n,E=dec(g6); info=loads(n,E)
        if info is None: print(f"  {g6}: skip"); continue
        sc,mc,dc=test(info,'cycle'); se,me,de=test(info,'edge')
        print(f"  {g6:13} N={n} Uover={float(info['Uover']):.3f} | CYCLE {sc} (mf{mc:.3f}/{dc:.3f}) | EDGE-broad {se} (mf{me:.3f}/{de:.3f})")
    print("--- census N=10,11: count CONGESTION-infeasible (cycle / edge-broad) ---")
    for nn in (10,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ic=ie=triv=nt=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            sc,_,_=test(info,'cycle'); se,_,_=test(info,'edge')
            if sc=='trivial': triv+=1
            else:
                if sc=='INFEASIBLE': ic+=1
                if se=='INFEASIBLE': ie+=1
        print(f"  N={nn}: configs={nt} | CYCLE-infeasible={ic} | EDGE-broad-infeasible={ie} | trivial={triv}",flush=True)
