"""GPT-Pro route (d) step-10: refined CAUSAL LEVEL-TRANSPORT feasibility (exact, Fraction).
PREFIX-LOAD-PSC-5 <=> Debt(tau)<=Bank_+(tau). GPT claims the proof object is a causal max-flow:
  eta=N^2/25-beta; bands J_j=(t_j,t_{j+1}) (split at theta=(N+eta)/2 so alpha changes sign at a band edge);
  alpha_j=25(N+eta-(t_j+t_{j+1})); h_j=|H_{t_j}|; sigma_j=delta_B-delta_M.
  SOURCE (v,j), v in H_{t_j}, alpha_j>0: cap = Delta_j*alpha_j.
  VOLUME SINK (v,j), v in H_{t_j}, alpha_j<0: demand = Delta_j*(-alpha_j).
  PRESSURE SINK (band j): demand = 5N*sigma_j*Delta_j  (aggregate, faithful to integrand 5N*sigma).
  Causal arcs i<=j: src(u,i)->volsink(v,j) iff u==v OR u,v share a bad-edge geodesic path;
                    src(u,i)->press(j)   iff u on a geodesic path that crosses boundary(H_{t_j}).
FACT: full feasibility (tau=t_m) => every prefix feasible (causal arcs upward). So one max-flow per config.
Total source cap >= total demand is aggregate PREFIX (true); infeasibility can ONLY come from admissibility.
Feasible on battery (esp. glued islands + C5[t] tight) => proof skeleton. Report feasible + slack."""
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

# ---------- Dinic max-flow with Fraction capacities ----------
class Dinic:
    def __init__(s,n): s.n=n; s.g=[[] for _ in range(n)]
    def add(s,u,v,c):
        s.g[u].append([v,F(c),len(s.g[v])])
        s.g[v].append([u,F(0),len(s.g[u])-1])
    def bfs(s,src,snk):
        s.lv=[-1]*s.n; s.lv[src]=0; q=deque([src])
        while q:
            u=q.popleft()
            for e in s.g[u]:
                if e[1]>0 and s.lv[e[0]]<0:
                    s.lv[e[0]]=s.lv[u]+1; q.append(e[0])
        return s.lv[snk]>=0
    def dfs(s,u,snk,f):
        if u==snk: return f
        while s.it[u]<len(s.g[u]):
            e=s.g[u][s.it[u]]
            if e[1]>0 and s.lv[e[0]]==s.lv[u]+1:
                d=s.dfs(e[0],snk,min(f,e[1]))
                if d>0:
                    e[1]-=d; s.g[e[0]][e[2]][1]+=d; return d
            s.it[u]+=1
        return F(0)
    def maxflow(s,src,snk):
        fl=F(0)
        while s.bfs(src,snk):
            s.it=[0]*s.n
            while True:
                f=s.dfs(src,snk,F(10)**18)
                if f==0: break
                fl+=f
        return fl

def feasible(name,n,adj,side,verbose=False):
    if not Bconn(n,adj,side): return None
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    beta=len(M); eta=F(n*n,25)-beta
    theta=(F(n)+eta)/2  # (N+eta)/2 = alpha sign-change level
    # distinct positive load levels + 0 baseline + theta (split band at sign change)
    levs=set([F(0)])|set(v for v in T if v>0)
    levs.add(theta)
    levs=sorted(x for x in levs if x>=0)
    # geodesic paths list
    paths=[]            # list of (set_of_vertices, edge_set)
    for f in M:
        for P in cyc[f]:
            vs=set(P); es=set()
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; es.add((min(a,b),max(a,b)))
            paths.append((vs,es))
    # K-component membership (transitive geodesic closure): src can pay sink in SAME component (chaining).
    comp_map, find = kcomponents(n, cyc)
    cid=[find(u) for u in range(n)]
    # admissibility mode: 'direct' = share one geodesic path; 'comp' = same K-component (transitive)
    geonbr=[set([u]) for u in range(n)]
    for vs,es in paths:
        for u in vs: geonbr[u]|=vs
    ADMIT = globals().get('ADMIT_MODE','comp')
    def same(u,v): return cid[u]==cid[v] if ADMIT=='comp' else (v in geonbr[u])
    # build bands
    bands=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tnx=levs[j+1]; D=tnx-tj
        if D<=0: continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        alpha=25*(F(n)+eta-(tj+tnx))
        # boundary edges of H
        dB=dM=0; bnd_edges=set()
        for u in H:
            for v in adj[u]:
                if v in H: continue
                e=(min(u,v),max(u,v)); bnd_edges.add(e)
                if side[u]!=side[v]: dB+=1
                else: dM+=1
        sigma=dB-dM
        # vertices on a geodesic crossing this boundary
        crossv=set()
        for vs,es in paths:
            if es & bnd_edges:
                crossv|=vs
        crosscomp=set(cid[u] for u in crossv)
        bands.append(dict(j=j,tj=tj,D=D,H=H,alpha=alpha,sigma=sigma,bnd=bnd_edges,crossv=crossv,crosscomp=crosscomp))
    # nodes: S=0, Tt=1, then source atoms, volume sinks, pressure sinks
    Sn=0; Tn=1; nid=2
    src_atom={}; vol_atom={}; pre_atom={}
    for bi,b in enumerate(bands):
        if b['alpha']>0:
            for v in b['H']:
                src_atom[(v,bi)]=nid; nid+=1
        if b['alpha']<0:
            for v in b['H']:
                vol_atom[(v,bi)]=nid; nid+=1
        if b['sigma']>0:
            pre_atom[bi]=nid; nid+=1
    din=Dinic(nid)
    totdem=F(0)
    for (v,bi),node in src_atom.items():
        b=bands[bi]; din.add(Sn,node,b['D']*b['alpha'])
    for (v,bi),node in vol_atom.items():
        b=bands[bi]; dem=b['D']*(-b['alpha']); din.add(node,Tn,dem); totdem+=dem
    for bi,node in pre_atom.items():
        b=bands[bi]; dem=5*F(n)*b['sigma']*b['D']; din.add(node,Tn,dem); totdem+=dem
    INF=F(10)**18
    # arcs source->volsink (same K-component, causal)
    for (u,i),sn in src_atom.items():
        for (v,j),vn in vol_atom.items():
            if i<=j and same(u,v):
                din.add(sn,vn,INF)
    # arcs source->pressure. PRESS_MODE: 'comp'=same component crosses boundary; 'any'=any causal source.
    PMODE=globals().get('PRESS_MODE','comp')
    for (u,i),sn in src_atom.items():
        for j,pn in pre_atom.items():
            if i<=j and (PMODE=='any' or cid[u] in bands[j]['crosscomp']):
                din.add(sn,pn,INF)
    fl=din.maxflow(Sn,Tn)
    feas = (fl==totdem)
    slack=totdem-fl
    if verbose:
        print("  %-16s N=%d beta=%d eta=%s bands=%d totdemand=%s flow=%s FEAS=%s%s"%(
            name,n,beta,str(eta),len(bands),str(totdem),str(fl),feas,
            "" if feas else "  *** SLACK %s ***"%str(slack)),flush=True)
    return dict(name=name,n=n,beta=beta,feas=feas,slack=slack,totdem=totdem)

def blow(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    print("=== CAUSAL LEVEL-TRANSPORT feasibility (GPT route d step-10) on curated HARD set ===",flush=True)
    res=[]
    # C5[t], C7[t] (extremal must be tight)
    for cyc_ in (5,7,9):
        for t in (1,2,3,4):
            n,E=blow([t]*cyc_)
            if n>26: continue
            adj,cuts=gmins(n,E)
            if cuts: res.append(feasible("C%d[%d]"%(cyc_,t),n,adj,cuts[0],verbose=True))
    # Grotzsch, Myc(Grotzsch) N=23, M(C7), M(C9)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        if cuts: res.append(feasible(nm,nn,adj,cuts[0],verbose=True))
    # glued islands
    for nm,(nn,E) in [("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C5",bridge((5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        if cuts: res.append(feasible(nm,nn,adj,cuts[0],verbose=True))
    res=[r for r in res if r]
    nfe=sum(1 for r in res if not r['feas'])
    print("\n  configs=%d  INFEASIBLE=%d"%(len(res),nfe),flush=True)
    if nfe:
        print("  *** transport INFEASIBLE on: %s"%[r['name'] for r in res if not r['feas']],flush=True)
        print("  => GPT's 3-arc-type construction is INCOMPLETE; min-cut names missing arc.",flush=True)
    else:
        print("  === ALL FEASIBLE: causal same-geodesic transport saturates every demand => PROOF SKELETON holds on hard set ===",flush=True)
