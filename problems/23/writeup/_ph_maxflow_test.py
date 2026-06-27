"""GPT round-12 PH (prefix-Hall, 2-to-1) max-flow test -- Step-1's INDEPENDENT gate (NOT touching Step-2 files).
Tests: for every triangle-free G (Gamma-min connected-B max cut), does the 2-to-1 transport
   overshoot atoms (f,C,w), supply 2*m(f,C,w)  -->  underloaded sinks z in sh(f,C,w), capacity u(z)=(N-T(z))_+
admit a feasible flow (max-flow == 2*U_over)?  PASS => explicit transport => COUPLE holds (per-graph).
FAIL => min-cut = the exact obstruction (a set A of atoms with capacity(union sh(A)) < 2 m(A)).

SHADOW reading (Step-1's, flagged to Step-2): for overshoot atom (f,C,w=c_j), prefix P_j=[c_0..c_j] of cycle C,
S=max_obstruction(C) (residual CD-split of R=V\\C); sh = { z in R : T(z)<N and z touched by a B- or M-edge counted
in e(C\\P_j,S)+e(P_j,R\\S) }. MASS m(f,C,w)=(T(w)-N)*(ell(f)/n_f)/T(w) (sums to U_over).  Float caps + tolerance.
"""
from fractions import Fraction as F
from collections import deque, defaultdict
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def loads_atoms(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    Bset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]!=side[v])
    Mset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]==side[v])
    # uniform-split T
    T=[F(0) for _ in range(n)]; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); cyc[f]=Ps; nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    N=n
    Uover=sum((t-N) for t in T if t>N); Uunder=sum((N-t) for t in T if t<N)
    return dict(n=n,adj=adj,side=side,M=M,ell=ell,Bset=Bset,Mset=Mset,T=T,cyc=cyc,Uover=Uover,Uunder=Uunder,G=G)

def max_obstruction(n,adj,side,M,C):
    Cset=set(C); K=[v for v in range(n) if v not in Cset]; idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    best=0; arg=[]
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM-dB>best: best=dM-dB; arg=[u for u in K if (mask>>idx[u])&1]
    return best,set(arg)

def touched(P, D, Bset, Mset):
    """R-vertices in D touched by a B- or M-edge with the other endpoint in P (the 'counted' edges of e(P,D))."""
    Ps=set(P); out=set()
    for (u,v) in Bset|Mset:
        if u in Ps and v in D: out.add(v)
        elif v in Ps and u in D: out.add(u)
    return out

def shadow(info, f, C, j):
    n=info['n']; adj=info['adj']; side=info['side']; M=info['M']; T=info['T']; Bset=info['Bset']; Mset=info['Mset']
    Cset=set(C); R=set(x for x in range(n) if x not in Cset)
    eta,S=max_obstruction(n,adj,side,M,C)
    Pj=set(C[:j+1]); CmP=set(C[j+1:]); RmS=R-S
    # counted edges: e(C\P_j, S) and e(P_j, R\S) -> R-endpoints touched
    tt = touched(CmP, S, Bset, Mset) | touched(Pj, RmS, Bset, Mset)
    return set(z for z in tt if T[z] < n), eta

# ---- simple max-flow (Edmonds-Karp, float) ----
def maxflow(cap, s, t, V):
    flow=0.0
    while True:
        par={s:None}; q=deque([s])
        while q:
            u=q.popleft()
            if u==t: break
            for v in V:
                if v not in par and cap[u].get(v,0)>1e-12:
                    par[v]=u; q.append(v)
        if t not in par: break
        # bottleneck
        b=float('inf'); v=t
        while par[v] is not None: u=par[v]; b=min(b,cap[u][v]); v=u
        v=t
        while par[v] is not None:
            u=par[v]; cap[u][v]-=b; cap[v][u]=cap[v].get(u,0)+b; v=u
        flow+=b
    return flow

def ph_test(info, verbose=False):
    n=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    N=n; Uover=info['Uover']
    if Uover==0: return ('trivial', 0.0, 0.0, None)
    # nodes: 'S', 'Z'+z for underloaded z, atom nodes a#, sink 'T'
    cap=defaultdict(lambda: defaultdict(float)); V=set(['__S','__T'])
    demand=0.0; atoms=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        for C in Ps:
            for j,w in enumerate(C):
                if T[w]>N:
                    m = (T[w]-N)*F(ell[f],nf)/T[w]   # mass, sums to U_over
                    sh,eta = shadow(info,f,C,j)
                    aid='A%d'%len(atoms); atoms.append((f,tuple(C),w,float(m),sh,eta))
                    V.add(aid)
                    cap['__S'][aid]+=2.0*float(m)    # 2-to-1 demand
                    demand+=2.0*float(m)
                    for z in sh:
                        zid='Z%d'%z; V.add(zid); cap[aid][zid]=float('inf')
    for z in range(n):
        if T[z]<N:
            zid='Z%d'%z
            if zid in V: cap[zid]['__T']+=float(N-T[z])   # underload capacity u(z)
    mf=maxflow(cap,'__S','__T',V)
    ok = mf >= demand-1e-7
    if verbose and not ok:
        # report a deficient atom set crudely
        print(f"      FAIL: maxflow={mf:.4f} < demand={demand:.4f} (2*Uover={2*float(Uover):.4f})")
    return ('feasible' if ok else 'INFEASIBLE', mf, demand, float(Uover))

def run(name,n,E):
    info=loads_atoms(n,E)
    if info is None: print(f"  {name}: skip"); return None
    status,mf,dem,uo=ph_test(info,verbose=True)
    print(f"  {name:9}: N={n} Uover={float(info['Uover']):.4f} Uunder={float(info['Uunder']):.4f} | PH {status} (maxflow={mf:.4f} demand={dem:.4f})")
    return status

print("=== PH (prefix-Hall 2-to-1) max-flow test -- Step-1 independent gate (shadow reading pending Step-2) ===")
for q in (2,3): run(f"C5[{q}]",*blow(q))
run("n8",*dec("G?\x60F\x60w"))
run("N11a",*dec("J?BD@g]Qvo?")); run("N11b",*dec("J?AAD@ON@[?")); run("N11c",*dec("J?AAD@WM_{?"))
print("--- census N=8,9 (count PH-infeasible) ---")
for nn in (8,9):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    inf=0; nt=0; triv=0
    for g6 in out:
        n,E=dec(g6); info=loads_atoms(n,E)
        if info is None: continue
        nt+=1
        st,_,_,_=ph_test(info)
        if st=='trivial': triv+=1
        elif st=='INFEASIBLE': inf+=1
    print(f"  N={nn}: configs={nt} | PH-infeasible={inf} | trivial(Uover=0)={triv}")
print("\nPH-infeasible=0 => the 2-to-1 transport exists per-graph (under Step-1's shadow reading) => COUPLE certified on tested set.")
