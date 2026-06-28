"""EXTENDED INDEPENDENT EXACT STRESS of Codex's BOUNDARY-DEFICIT lemma (Claude leg, block 23).

LEMMA (boundary-deficit): for every full K-component C (connected comp of graph {K[v,w]>0})
with C disjoint from O={v:T[v]>N},
        deficit(C) := N*|C| - mass(C)   >=   dB(C) := #{B-edges crossing C}.
A "critical" K_QQ-component (forcing cond(1) to fail) would be a Q-only K-component with deficit=0,
K-closed in V (=full comp), and O nonempty => dB(C)>0 => 0>=dB>0 contradiction.

INDEPENDENT REIMPLEMENTATION: I do NOT import _bdef. I rebuild p_f(v) (geodesic-incidence density),
K=P P^T, T=K*1, O, components, mass, deficit, dB all from scratch here. I reuse _h.loads ONLY for the
fixed maxcut+geodesic ground truth (that defines the certificate's input K; the maxcut is not part of the
lemma). Cross-checked against _bdef.analyze on a few graphs (see _xcheck()).

Everything EXACT (Fraction). Reports per family: #graphs, #Q-only comps, #NON-trivial Q-only comps
(|C|>1 or some T>0), how many of THOSE have O nonempty, min(deficit-dB) with witness, #violations.

KEY DISTINCTION: a Q-only component is only relevant to cond(1) when O is NONEMPTY. When O is empty the
whole graph is one comp with T==N everywhere (deficit=0,dB=0): trivially-true, vacuous for the lemma.
We separately track "non-trivial Q-only comp WITH O nonempty" -- that is the real critical-component risk.
"""
import sys, os, subprocess, random, time
from fractions import Fraction as F
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _h import dec, GENG, loads

# ---------- INDEPENDENT geodesic-density p_f, K, T ----------
def pf_K_T(info):
    """Build p_f(v) = (#a-b B-geodesics through v)/(#a-b B-geodesics), K=PP^T, T=K1. All Fraction.
    Independent of _schur_spec.pf_exact: I recompute cnt from info['cyc'] myself."""
    M=info['M']; cyc=info['cyc']; n=info['n']
    P=[]  # list over f: dict v->Fraction
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        cnt={}
        for path in Ps:
            for v in path: cnt[v]=cnt.get(v,0)+1
        P.append({v:F(c,nf) for v,c in cnt.items()})
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for i in range(len(items)):
            va,pa=items[i]
            for j in range(len(items)):
                vb,pb=items[j]
                K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    return K,T,n

# ---------- INDEPENDENT component finder on {K[v,w]>0} ----------
def K_components(K,n):
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        seen[s]=True; stack=[s]; C=[s]
        while stack:
            v=stack.pop()
            for w in range(n):
                if w!=v and (not seen[w]) and K[v][w]>0:
                    seen[w]=True; stack.append(w); C.append(w)
        comps.append(sorted(C))
    return comps

# ---------- INDEPENDENT boundary-deficit analysis ----------
def analyze(info):
    K,T,n=pf_K_T(info); N=n
    O=set(v for v in range(n) if T[v]>N)
    Bset=info['Bset']  # set of (a,b) cut edges, a<b
    comps=K_components(K,n)
    rows=[]  # one per Q-only component
    for C in comps:
        Cs=set(C)
        if Cs & O: continue   # only components disjoint from O
        mass=sum(T[v] for v in C)
        deficit=F(N*len(C))-mass
        dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
        allT0=all(T[v]==0 for v in C)
        single=(len(C)==1)
        nontriv=not(single and allT0)
        rows.append(dict(C=tuple(C),size=len(C),deficit=deficit,dB=dB,mass=mass,
                         allT0=allT0,single=single,nontriv=nontriv,
                         violate=(deficit<dB), O_nonempty=(len(O)>0)))
    return rows,N,n,len(O)

# ---------- accumulator ----------
class Acc:
    def __init__(self):
        self.graphs=0; self.loads_none=0
        self.Qcomps=0; self.nontriv=0; self.nontriv_with_O=0
        self.violations=0; self.worst_slack=None; self.worst_w=None
        self.crit_risk=[]  # (witness) nontrivial Q-only deficit==0 with O nonempty
    def add(self, tag, info):
        if info is None: self.loads_none+=1; return
        self.graphs+=1
        rows,N,n,nO=analyze(info)
        for r in rows:
            self.Qcomps+=1
            if r['nontriv']: self.nontriv+=1
            if r['nontriv'] and r['O_nonempty']: self.nontriv_with_O+=1
            slack=r['deficit']-r['dB']
            if self.worst_slack is None or slack<self.worst_slack:
                self.worst_slack=slack
                self.worst_w=(tag,r['C'][:8],float(r['deficit']),r['dB'],r['O_nonempty'],r['size'])
            if r['violate']:
                self.violations+=1
                if len(self.crit_risk)<5: self.crit_risk.append(('VIOLATE',tag,r['C'][:12],float(r['deficit']),r['dB']))
            # the dangerous case: nontrivial Q-only, deficit==0, O nonempty
            if r['nontriv'] and r['O_nonempty'] and r['deficit']==0:
                if len(self.crit_risk)<10:
                    self.crit_risk.append(('CRIT?',tag,r['C'][:12],float(r['deficit']),r['dB'],'sz=%d'%r['size']))
    def report(self,name):
        ws=float(self.worst_slack) if self.worst_slack is not None else None
        print(f"[{name}] graphs={self.graphs} loadsNone={self.loads_none} | Qcomps={self.Qcomps} "
              f"nontriv={self.nontriv} nontriv_with_O={self.nontriv_with_O} | "
              f"VIOLATIONS={self.violations} | min(deficit-dB)={ws} @ {self.worst_w}", flush=True)
        for cr in self.crit_risk:
            print(f"     {cr}", flush=True)

# ---------- cross-check vs _bdef ----------
def xcheck():
    import _bdef
    print("=== cross-check my analyze vs _bdef.analyze (independent K builds) ===", flush=True)
    ok=True
    tests=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]
    for g6 in tests:
        n,E=dec(g6); info=loads(n,E)
        if info is None: print(f"  {g6}: loads None"); continue
        mine,N,_,_=analyze(info)
        theirs,_,_=_bdef.analyze(info)
        # _bdef returns tuples (C,deficit,dB,mass,allT0,single,fail)
        msd=sorted((tuple(r['C']),r['deficit'],r['dB']) for r in mine)
        tsd=sorted((tuple(t[0]),t[1],t[2]) for t in theirs)
        same=(msd==tsd)
        ok=ok and same
        print(f"  {g6}: match={same} (mine {len(mine)} comps, theirs {len(theirs)})", flush=True)
    # C5 too
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    info=loads(*C5); mine,N,_,_=analyze(info); theirs,_,_=_bdef.analyze(info)
    print(f"  C5: match={sorted((tuple(r['C']),r['deficit'],r['dB']) for r in mine)==sorted((tuple(t[0]),t[1],t[2]) for t in theirs)}", flush=True)
    print(f"  CROSS-CHECK {'PASS' if ok else 'FAIL'}", flush=True)
    return ok

# ---------- triangle-free constructions ----------
def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def circulant(n,conn):
    """circulant C_n(conn): i ~ i+c mod n for c in conn. triangle-free iff no a,b,a+b(or diff) all in conn-closure."""
    E=set()
    for i in range(n):
        for c in conn:
            j=(i+c)%n
            E.add((min(i,j),max(i,j)))
    return n,sorted(E)

def is_triangle_free(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def random_trianglefree(n, p, rng):
    """random triangle-free: add edges in random order, keep if no triangle created."""
    adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    rng.shuffle(pairs)
    E=[]
    for (i,j) in pairs:
        if rng.random()>p: continue
        if adj[i]&adj[j]: continue  # would form triangle
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E

def blow_iid(g6_or_ne, t):
    if isinstance(g6_or_ne,str): n,E=dec(g6_or_ne)
    else: n,E=g6_or_ne
    EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def blow_weighted(g6_or_ne, sizes):
    """non-uniform blow-up: vertex v -> sizes[v] copies; complete bipartite between adjacent classes."""
    if isinstance(g6_or_ne,str): n,E=dec(g6_or_ne)
    else: n,E=g6_or_ne
    off=[0]*(n+1)
    for v in range(n): off[v+1]=off[v]+sizes[v]
    EE=[]
    for (a,b) in E:
        for i in range(sizes[a]):
            for j in range(sizes[b]):
                EE.append((off[a]+i, off[b]+j))
    return off[n],EE

def graph_conn(n,E):
    if n==0: return False
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

# =====================================================================
# FAST faithful loads (for structured graphs with N>24 where 2^(n-1)
# brute force in _h.loads is infeasible). Replicates _h.loads pipeline:
#   max cut VALUE via branch-and-bound, then among max cuts that are
#   B-connected with all-geodesics valid, pick the MIN-Gamma one, then
#   build T,cyc,Bset,Mset exactly as _h.loads does.
# VALIDATED against _h.loads on small Mycielskians (see validate_fast()).
# =====================================================================
def _localsearch_cut_lb(n, adj, restarts=60, seed=11):
    """Local-search lower bound on max-cut value (seeds BB best for strong pruning)."""
    import random as _r
    rng=_r.Random(seed); best=0
    for _ in range(restarts):
        side=[rng.randint(0,1) for _ in range(n)]
        improved=True
        while improved:
            improved=False
            for v in range(n):
                same=sum(1 for w in adj[v] if side[w]==side[v])
                diff=len(adj[v])-same
                if same>diff: side[v]^=1; improved=True
        cut=sum(1 for u in range(n) for w in adj[u] if w>u and side[u]!=side[w])
        if cut>best: best=cut
    return best

def _maxcut_value_bb(n, adj):
    """Exact max-cut value via branch and bound, seeded by a local-search lower bound for pruning."""
    nbr=[sorted(adj[u]) for u in range(n)]
    deg=[len(nbr[u]) for u in range(n)]
    order=sorted(range(n), key=lambda u:-deg[u])
    pos={v:i for i,v in enumerate(order)}
    # adjacency in terms of order index
    adj_ord=[[pos[w] for w in adj[order[i]]] for i in range(n)]
    total_edges=sum(deg)//2
    lb=_localsearch_cut_lb(n,adj)
    best=[lb]   # seed with LS lower bound; rec will still verify/raise to true optimum
    side=[-1]*n
    # precompute, for index i, edges to earlier-decided indices
    earlier=[[j for j in adj_ord[i] if j<i] for i in range(n)]
    # edge (a,b) with order-idx a<b is counted at step b (in earlier[b]).
    # remaining countable edges from step i onward = sum_{j>=i} |earlier[j]|.
    suffix_edges=[0]*(n+1)
    for i in range(n-1,-1,-1):
        suffix_edges[i]=suffix_edges[i+1]+len(earlier[i])
    def rec(i, cut):
        if cut+suffix_edges[i]<=best[0]:
            return
        if i==n:
            if cut>best[0]: best[0]=cut
            return
        for s in (0,1):
            side[i]=s
            add=sum(1 for j in earlier[i] if side[j]!=s)
            rec(i+1, cut+add)
        side[i]=-1
    rec(0,0)
    return best[0]

def _enum_maxcuts(n, adj, target, cap=200000):
    """Enumerate (up to cap) cut sign-vectors (in ORIGINAL vertex indexing) achieving exactly `target`.
    Fix vertex order[0]=side 0 to kill the global flip symmetry."""
    nbr=[sorted(adj[u]) for u in range(n)]
    deg=[len(nbr[u]) for u in range(n)]
    order=sorted(range(n), key=lambda u:-deg[u])
    pos={v:i for i,v in enumerate(order)}
    adj_ord=[[pos[w] for w in adj[order[i]]] for i in range(n)]
    earlier=[[j for j in adj_ord[i] if j<i] for i in range(n)]
    suffix_edges=[0]*(n+1)
    for i in range(n-1,-1,-1):
        suffix_edges[i]=suffix_edges[i+1]+len(earlier[i])
    out=[]; side=[-1]*n; overflow=[False]
    def rec(i,cut):
        if overflow[0]: return
        if cut+suffix_edges[i]<target: return
        if i==n:
            if cut==target:
                sv=[0]*n
                for idx in range(n): sv[order[idx]]=side[idx]
                out.append(sv)
                if len(out)>=cap: overflow[0]=True
            return
        srange=(0,) if i==0 else (0,1)  # fix first vertex side 0
        for s in srange:
            side[i]=s
            add=sum(1 for j in earlier[i] if side[j]!=s)
            rec(i+1,cut+add)
        side[i]=-1
    rec(0,0)
    return out, overflow[0]

def loads_fast(n,E,cap=200000):
    """Faithful-to-_h.loads but using BB max-cut value + bounded enumeration of max cuts.
    Returns same dict shape as _h.loads, or None, or ('OVERFLOW',k) if too many max cuts."""
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    val=_maxcut_value_bb(n,adj)
    cuts, overflow = _enum_maxcuts(n,adj,val,cap=cap)
    if overflow:
        return ('OVERFLOW', len(cuts))
    # mimic _h.gmin: among cuts, B-connected with valid geodesics, min Gamma
    from _h import Bconn, bdist_restr, geos
    best=None
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True; ell={}
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]):
            best=(side,G,M,ell)
    if best is None: return None
    side,G,M,ell=best
    Bset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]!=side[v])
    Mset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]==side[v])
    T=[F(0) for _ in range(n)]; cyc={}; dist={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); cyc[f]=Ps; nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
        d={f[0]:0}; q=deque([f[0]])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
        dist[f]=d
    return dict(n=n,adj=adj,side=side,M=M,ell=ell,Bset=Bset,Mset=Mset,T=T,cyc=cyc,dist=dist,G=G)

def _one_maxcut(n,adj,val):
    """Return ONE sign vector achieving max-cut value `val` (first found, BB order)."""
    nbr=[sorted(adj[u]) for u in range(n)]
    deg=[len(nbr[u]) for u in range(n)]
    order=sorted(range(n), key=lambda u:-deg[u])
    pos={v:i for i,v in enumerate(order)}
    adj_ord=[[pos[w] for w in adj[order[i]]] for i in range(n)]
    earlier=[[j for j in adj_ord[i] if j<i] for i in range(n)]
    suffix_edges=[0]*(n+1)
    for i in range(n-1,-1,-1):
        suffix_edges[i]=suffix_edges[i+1]+len(earlier[i])
    side=[-1]*n; found=[None]
    def rec(i,cut):
        if found[0] is not None: return
        if cut+suffix_edges[i]<val: return
        if i==n:
            if cut==val:
                sv=[0]*n
                for idx in range(n): sv[order[idx]]=side[idx]
                found[0]=sv
            return
        for s in (0,1):
            side[i]=s
            add=sum(1 for j in earlier[i] if side[j]!=s)
            rec(i+1,cut+add)
            if found[0] is not None: return
        side[i]=-1
    rec(0,0)
    return found[0]

def loads_onecut(n,E):
    """Build certificate info from ONE max cut (NOT necessarily the min-Gamma tie-break of _h.loads).
    For structured graphs whose max-cut count makes faithful loads_fast infeasible. Tries multiple
    max cuts (greedy local-search restarts) and keeps the min-Gamma B-connected one found.
    Returns info dict or None. Tag the result as 'onecut' (approximate, single representative cut)."""
    import random as _r
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    val=_maxcut_value_bb(n,adj)
    cand_sides=[]
    s0=_one_maxcut(n,adj,val)
    if s0 is not None: cand_sides.append(s0)
    # local-search restarts to collect a few distinct max cuts
    rng=_r.Random(2027)
    for _ in range(40):
        side=[rng.randint(0,1) for _ in range(n)]
        improved=True
        while improved:
            improved=False
            for v in range(n):
                same=sum(1 for w in adj[v] if side[w]==side[v])
                diff=len(adj[v])-same
                if same>diff:
                    side[v]^=1; improved=True
        cut=sum(1 for u in range(n) for w in adj[u] if w>u and side[u]!=side[w])
        if cut==val: cand_sides.append(side[:])
    from _h import Bconn, bdist_restr, geos
    best=None
    seen=set()
    for side in cand_sides:
        key=tuple(side)
        if key in seen or tuple(1-x for x in side) in seen: continue
        seen.add(key)
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True; ell={}
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M,ell)
    if best is None: return None
    side,G,M,ell=best
    Bset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]!=side[v])
    Mset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]==side[v])
    T=[F(0) for _ in range(n)]; cyc={}; dist={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); cyc[f]=Ps; nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
        d={f[0]:0}; q=deque([f[0]])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
        dist[f]=d
    return dict(n=n,adj=adj,side=side,M=M,ell=ell,Bset=Bset,Mset=Mset,T=T,cyc=cyc,dist=dist,G=G)

def validate_fast():
    """Check loads_fast agrees with _h.loads (same K-component boundary-deficit data) on small graphs."""
    print("=== validate loads_fast vs _h.loads ===", flush=True)
    ok=True
    samples=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","J??CE?{{?]?"]
    for g6 in samples:
        n,E=dec(g6)
        a=loads(n,E); b=loads_fast(n,E)
        if a is None and b is None: print(f"  {g6}: both None"); continue
        if isinstance(b,tuple): print(f"  {g6}: fast OVERFLOW"); ok=False; continue
        ra,_,_,_=analyze(a); rb,_,_,_=analyze(b)
        sa=sorted((r['C'],r['deficit'],r['dB']) for r in ra)
        sb=sorted((r['C'],r['deficit'],r['dB']) for r in rb)
        match=(sa==sb)
        ok=ok and match
        print(f"  {g6}: match={match}", flush=True)
    # Mycielskians up to N=23 (where _h.loads still finishes)
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1)
    for nm,(nn,EE) in [("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2))]:
        a=loads(nn,EE); b=loads_fast(nn,EE)
        if isinstance(b,tuple): print(f"  {nm}: fast OVERFLOW({b[1]})"); continue
        if a is None or b is None: print(f"  {nm}: a none={a is None} b none={b is None}"); ok=False; continue
        ra,_,_,_=analyze(a); rb,_,_,_=analyze(b)
        sa=sorted((r['C'],r['deficit'],r['dB']) for r in ra)
        sb=sorted((r['C'],r['deficit'],r['dB']) for r in rb)
        match=(sa==sb)
        ok=ok and match
        print(f"  {nm}: match={match} (Gamma a={a['G']} b={b['G']})", flush=True)
    print(f"  VALIDATE_FAST {'PASS' if ok else 'FAIL'}", flush=True)
    return ok

# =====================================================================
#  FAMILIES
# =====================================================================
def fam_random(nmin=12,nmax=22,target=2500,seed=12345,Ncap_brute=20):
    """(1) MANY random connected triangle-free graphs N=12..22, exact deficit>=dB."""
    rng=random.Random(seed)
    acc=Acc()
    counts={}
    attempts=0
    while acc.graphs<target and attempts<target*40:
        attempts+=1
        n=rng.randint(nmin,nmax)
        p=rng.uniform(0.22,0.5)
        nn,E=random_trianglefree(n,p,rng)
        if not graph_conn(nn,E): continue
        if len(E)<n: continue  # need cycles / monochromatic structure
        info=loads(nn,E) if n<=Ncap_brute else loads_fast(nn,E,cap=300000)
        if isinstance(info,tuple): continue  # overflow, skip
        acc.add("rand%d"%n, info)
        counts[n]=counts.get(n,0)+1
    acc.report("RANDOM tri-free N=%d..%d (got %d, byN=%s)"%(nmin,nmax,acc.graphs,dict(sorted(counts.items()))))
    return acc

def fam_geng_sample(nmax=18,mod=997,seed=7):
    """(1b) geng res/mod subset of FULL triangle-free connected census N=12..nmax."""
    rng=random.Random(seed)
    for nn in range(12,nmax+1):
        res=rng.randint(0,mod-1)
        out=subprocess.run([GENG,"-tc",str(nn),"%d/%d"%(res,mod)],capture_output=True,text=True).stdout.split()
        acc=Acc()
        cap = 4000 if nn<=14 else (1500 if nn<=16 else 600)
        for g6 in out[:cap]:
            n,E=dec(g6); info=loads(n,E)
            acc.add("geng%d"%nn, info)
        acc.report("GENG census-sample N=%d res=%d/%d (processed %d/%d)"%(nn,res,mod,acc.graphs,len(out)))

def fam_mycielski():
    """(2) iterated Mycielskians to N=47 and Myc(C7)->N=31. Uses loads_fast for N>22."""
    print("=== (2) ITERATED MYCIELSKIANS ===", flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    C7=(7,[(i,(i+1)%7) for i in range(7)])
    chain=[("C5",C5)]
    a=C5
    for k in range(1,4):
        nn,EE=mycielski(*a); a=(nn,EE)
        chain.append(("Myc^%d(C5) N=%d"%(k,nn),(nn,EE)))
    chain.append(("Myc(C7) N=15", mycielski(*C7)))
    m=mycielski(*C7)
    chain.append(("Myc(Myc(C7)) N=31", mycielski(*m)))
    for name,(nn,EE) in chain:
        acc=Acc()
        info = loads(nn,EE) if nn<=22 else loads_fast(nn,EE,cap=2000000)
        if isinstance(info,tuple):
            print("  %s: max-cut OVERFLOW (>%d cuts) -- skipped"%(name,info[1]), flush=True); continue
        acc.add(name, info)
        acc.report(name)

def fam_circulant(nmax=24):
    """(3) triangle-free circulant / vertex-transitive graphs N<=24."""
    print("=== (3) TRIANGLE-FREE CIRCULANTS / VERTEX-TRANSITIVE N<=24 ===", flush=True)
    from itertools import combinations
    acc=Acc(); seen=set(); total=0
    for n in range(5,nmax+1):
        cands=list(range(1,n//2+1))
        for k in range(1,4):
            for conn in combinations(cands,k):
                nn,E=circulant(n,conn)
                if not E: continue
                if not graph_conn(nn,E): continue
                if not is_triangle_free(nn,E): continue
                key=(n,conn)
                if key in seen: continue
                seen.add(key); total+=1
                info=loads(nn,E) if n<=22 else loads_fast(nn,E,cap=500000)
                if isinstance(info,tuple): continue
                acc.add("circ%d%s"%(n,conn), info)
    acc.report("CIRCULANTS (enumerated %d connection-sets, loaded %d)"%(total,acc.graphs))

def fam_blowup(nmax=40):
    """(4) i.i.d. AND non-uniform weighted blow-ups of overloaded census bases, N<=40."""
    print("=== (4) BLOW-UPS (i.i.d. + non-uniform weighted) of overloaded bases N<=40 ===", flush=True)
    rng=random.Random(99)
    bases=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","J??CE?{{?]?","J???E?pNu\\?"]
    acc_iid=Acc(); acc_w=Acc()
    for g6 in bases:
        n0,E0=dec(g6)
        for t in range(2,6):
            nn,EE=blow_iid((n0,E0),t)
            if nn>nmax: break
            info=loads(nn,EE) if nn<=22 else loads_fast(nn,EE,cap=2000000)
            if isinstance(info,tuple): continue
            acc_iid.add("%sx%d"%(g6,t), info)
        for trial in range(8):
            sizes=[1]*n0
            extra=nmax-n0
            for _ in range(extra):
                sizes[rng.randrange(n0)]+=1
            nn,EE=blow_weighted((n0,E0),sizes)
            if nn>nmax: continue
            info=loads(nn,EE) if nn<=22 else loads_fast(nn,EE,cap=2000000)
            if isinstance(info,tuple): continue
            acc_w.add("%sw%s"%(g6,sizes), info)
    acc_iid.report("BLOW-UP i.i.d.")
    acc_w.report("BLOW-UP weighted/non-uniform")

if __name__=="__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv)>1 else "all"
    if mode in ("xcheck","all"): xcheck(); validate_fast()
    if mode in ("myciel","all"): fam_mycielski()
    if mode in ("circ","all"):   fam_circulant(24)
    if mode in ("blow","all"):   fam_blowup(40)
    if mode in ("geng","all"):   fam_geng_sample(18)
    if mode in ("rand","all"):   fam_random(12,22,2500)
