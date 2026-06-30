"""ADVERSARIAL INDEPENDENT VERIFY of route 'hotcore_bundle' for (CV).

Claim under test:
  (BND)  For every bad edge f in K-component c:   <u_f, T> <= N + eta,
         eta = N^2/25 - beta,  u_f = (w_f/ell_f^2) * p_f,  w_f = ell_f/|cyc_f|,
         p_f(v) = #shortest alternating geodesics of f through v,  T = full component load.
  Claimed: (BND) holds on the full battery with 0 violations AND implies (CV).

This file is a from-scratch reimplementation. It does NOT import _cv_gate.py.
It re-derives geodesics, T, K-components, the (BND) LHS, AND independently verifies
the algebraic identity   sum_{v in c} T_v^2 == sum_{f in c} ell_f^2 * <u_f,T>   (exact Fraction),
which is what makes (BND) => (CV). Both checked. Counterexample hunt over the standing battery
plus extra adversarial graphs. ALL arithmetic in fractions.Fraction; floats only for display.

Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import subprocess, itertools
from fractions import Fraction as F
from collections import deque

GENG = "E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

# ----------------------------------------------------------------------------
# Independent primitives (graph6 decode, max-cut enum, B-connectivity, geodesics)
# ----------------------------------------------------------------------------
def dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[]; i=0
    for j in range(1,n):
        for ii in range(j):
            if i<len(bits) and bits[i]: E.append((ii,j))
            i+=1
    return n,E

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E:
        if x!=y: a[x].add(y); a[y].add(x)
    return a

def all_maxcuts(n,adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for m in range(1<<(n-1)):                      # fix vertex 0 on side 0 (kill complement)
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return cuts

def Bconn(n,adj,side):
    """B-graph (only bichromatic edges) connected on all n vertices?"""
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def bdist(adj,side,s,t):
    """shortest path in B-graph (alternating cut edges)."""
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:
                d[v]=d[u]+1
                if v==t: return d[v]
                q.append(v)
    return d.get(t,-1)

def geos(adj,side,s,t):
    """ALL shortest alternating (cut-edge) s-t paths, as vertex lists (length ell = #vertices)."""
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[])
    return out

# ----------------------------------------------------------------------------
# Independent structure: M (bad edges), p_f, ell_f, |cyc_f|, T, K-components
# ----------------------------------------------------------------------------
def structure(n,adj,side):
    """Return None if any bad edge has no alternating geodesic (cut not 'gamma-min-valid')."""
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    pf={}; ell={}; ncyc={}
    T=[F(0)]*n
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        ell[f]=len(Ps[0]); ncyc[f]=len(Ps)
        # sanity: all geodesics equal length
        if any(len(P)!=ell[f] for P in Ps): return None
        cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf[f]=cnt                                   # p_f(v) = integer count
        w=F(ell[f],ncyc[f])                         # w_f
        for v,c in cnt.items(): T[v]+=w*c           # T_v += w_f * p_f(v)
    return dict(M=M,pf=pf,ell=ell,ncyc=ncyc,T=T)

def kcomponents(n,adj,side,st):
    """Union-find: every geodesic path is a clique => union all its vertices."""
    par=list(range(n))
    def find(x):
        r=x
        while par[r]!=r: r=par[r]
        while par[x]!=r: par[x],x=r,par[x]
        return r
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: par[ra]=rb
    for f in st['M']:
        for P in geos(adj,side,f[0],f[1]):
            for v in P[1:]: union(P[0],v)
    comp={}
    for v in range(n): comp.setdefault(find(v),[]).append(v)
    fid={v:find(v) for v in range(n)}
    return comp,fid

# ----------------------------------------------------------------------------
# THE GATE: check (BND) per bad edge, the identity, and (CV) directly.
# ----------------------------------------------------------------------------
def check(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=structure(n,adj,side)
    if st is None: return
    M,pf,ell,ncyc,T=st['M'],st['pf'],st['ell'],st['ncyc'],st['T']
    beta=len(M)
    N=n
    eta=F(N*N,25)-beta
    A=F(N)+eta                                       # bound N+eta
    comp,fid=kcomponents(n,adj,side,st)
    # group bad edges and vertices by component
    comp_of_edge={}
    for f in M:
        comp_of_edge[f]=fid[f[0]]
    # ---- (BND) per bad edge ----
    for f in M:
        w=F(ell[f],ncyc[f])
        scale=w/(F(ell[f])**2)                       # u_f = scale * p_f
        # sanity: u_f is a probability vector  sum_v u_f(v)==1
        mass=scale*sum(pf[f].values())
        assert mass==1, (name,f,mass)
        bnd_lhs=scale*sum(F(c)*T[v] for v,c in pf[f].items())   # <u_f,T>
        acc['nb']+=1
        margin=A-bnd_lhs
        if margin<acc['bnd_min'][0]:
            acc['bnd_min']=(margin,name,N,beta,str(bnd_lhs),str(A),f)
        if margin<0:
            acc['bnd_viol']+=1
            if acc['bnd_first'] is None:
                acc['bnd_first']=(name,N,beta,f,str(bnd_lhs),str(A),''.join(map(str,side)))
    # ---- (CV) directly + identity  sum_v T_v^2 == sum_f ell_f^2 <u_f,T> ----
    for cid,vs in comp.items():
        S2=sum(T[v]*T[v] for v in vs)
        G=sum(T[v] for v in vs)
        if G==0: continue
        acc['nc']+=1
        cvmargin=A*G-S2
        if cvmargin<acc['cv_min'][0]:
            acc['cv_min']=(cvmargin,name,N,beta,len(vs),str(G))
        if cvmargin<0:
            acc['cv_viol']+=1
            if acc['cv_first'] is None:
                acc['cv_first']=(name,N,beta,len(vs),str(cvmargin),''.join(map(str,side)))
        # identity check: sum_{v in c} T_v^2  ==  sum_{f in c} ell_f^2 * <u_f,T>
        fsum=F(0)
        for f in M:
            if comp_of_edge[f]!=cid: continue
            w=F(ell[f],ncyc[f]); scale=w/(F(ell[f])**2)
            bnd=scale*sum(F(c)*T[v] for v,c in pf[f].items())
            fsum+=F(ell[f])**2*bnd
        if fsum!=S2:
            acc['id_fail']+=1
            if acc['id_first'] is None:
                acc['id_first']=(name,N,cid,str(S2),str(fsum))
        # also: Gamma_c == sum_{f in c} ell_f^2 ?
        gcheck=sum(F(ell[f])**2 for f in M if comp_of_edge[f]==cid)
        if gcheck!=G:
            acc['g_fail']+=1
            if acc['g_first'] is None:
                acc['g_first']=(name,N,cid,str(G),str(gcheck))

# ----------------------------------------------------------------------------
# gamma-min cuts (connected-B, smallest Gamma=sum ell^2)
# ----------------------------------------------------------------------------
def gmins(n,E):
    adj=adj_of(n,E)
    cuts=[s for s in all_maxcuts(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

# ----------------------------------------------------------------------------
# Constructors (independent)
# ----------------------------------------------------------------------------
def Cn(k,off=0): return [(off+i,off+(i+1)%k) for i in range(k)]

def union_disjoint(*blocks):
    n=0; E=[]
    for (bn,bE) in blocks:
        E+=[(a+n,b+n) for (a,b) in bE]; n+=bn
    return n,E

def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]
    return nn,E+[(u,n1+v)]

def mycielski(n,E):
    a=adj_of(n,E); N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in a[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

def is_trifree(n,E):
    a=adj_of(n,E)
    for x,y in E:
        if x!=y and (a[x]&a[y]): return False
    return True

# two-lane and k-lane (independent reimplementation matching _verify_two_lane)
def build_two_lane(L):
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    for e in [(0,L-2),(0,L),(2,L-2),(2,L)]: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side

def build_k_lane(L,k,bad):
    def lv(j,i): return (L+1)+j*(L+1)+i
    n=(L+1)+k*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        for j in range(k):
            u,v=i,lv(j,i); E.add((min(u,v),max(u,v)))
    for i in range(L):
        for ja in range(k):
            for jb in range(k):
                u,v=lv(ja,i),lv(jb,i+1); E.add((min(u,v),max(u,v)))
    for e in bad:
        a,b=e; E.add((min(a,b),max(a,b)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1):
        for j in range(k): side[lv(j,i)]=1-(i%2)
    return n,sorted(E),side

def greedy_chords(L,k,gap):
    bn,bE,_=build_k_lane(L,k,[])
    adj=adj_of(bn,bE); chords=[]
    cand=[(a,b) for a in range(0,L+1) for b in range(a+gap,L+1) if (a%2)==(b%2)]
    for (a,b) in cand:
        if b in adj[a] or (adj[a]&adj[b]): continue
        adj[a].add(b); adj[b].add(a); chords.append((a,b))
    return chords

# ----------------------------------------------------------------------------
# MAIN battery
# ----------------------------------------------------------------------------
if __name__=="__main__":
    acc=dict(nb=0,nc=0,bnd_viol=0,cv_viol=0,id_fail=0,g_fail=0,
             bnd_first=None,cv_first=None,id_first=None,g_first=None,
             bnd_min=(F(10**18),'','','','','',None),
             cv_min=(F(10**18),'','','','',''))

    # --- two-lane L=8..20 ---
    for L in range(8,21,2):
        n,E,side=build_two_lane(L); check("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    # --- k-lane dense ---
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side=build_k_lane(Ll,k,bad)
        check("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  [two-lane+k-lane] bnd_viol=%d cv_viol=%d id_fail=%d"%(acc['bnd_viol'],acc['cv_viol'],acc['id_fail']),flush=True)

    # --- odd-cycle blow-ups C5/C7/C9 t=1..5 ---
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: check("C%d[%d]"%(c,t),n,adj,s,acc)
    # --- non-uniform blow-ups (asymmetric) ---
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],
                  [1,6,1,6,1],[1,1,5,5,1],[4,1,4,1,4],[2,5,1,5,2],
                  [1,8,1,1,1,1,1],[6,1,1,1,1,1,1]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: check("nu%s"%parts,n,adj,s,acc)
    print("  [blow-ups + non-uniform] bnd_viol=%d cv_viol=%d id_fail=%d"%(acc['bnd_viol'],acc['cv_viol'],acc['id_fail']),flush=True)

    # --- Mycielskians + Grotzsch + glued bridges ---
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    named=[("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),
           ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
           ("bridgeC7-Grotzsch",bridge((7,Cn(7)),grot,0,0)),
           ("bridgeC9-C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
           ("bridgeC5-C7",bridge((5,Cn(5)),(7,Cn(7)),0,0)),
           ("bridgeC7-C7",bridge((7,Cn(7)),(7,Cn(7)),0,0)),
           ("bridgeC5-C9",bridge((5,Cn(5)),(9,Cn(9)),0,0)),
           ("bridgeGrotzsch-Grotzsch",bridge(grot,grot,0,0))]
    for nm,(nn,E) in named:
        if not is_trifree(nn,E):
            print("  [skip non-trifree] %s"%nm); continue
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: check(nm,nn,adj,s,acc)
    print("  [Mycielskians+glued] bnd_viol=%d cv_viol=%d id_fail=%d"%(acc['bnd_viol'],acc['cv_viol'],acc['id_fail']),flush=True)

    # --- census geng -tc N=7..11, ALL gamma-min cuts ---
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['cv_viol']; b0=acc['bnd_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check("cen-%s"%g6,n,adj,s,acc)
        print("  census N=%d  (bnd+%d cv+%d)"%(nn,acc['bnd_viol']-b0,acc['cv_viol']-v0),flush=True)

    print("\n  === RESULTS ===")
    print("  bad-edges tested = %d   K-components tested = %d"%(acc['nb'],acc['nc']))
    print("  (BND) <u_f,T> <= N+eta   violations = %d"%acc['bnd_viol'])
    print("  (CV)  sum T^2 <= (N+eta)Gamma_c violations = %d"%acc['cv_viol'])
    print("  IDENTITY  sum_v T_v^2 == sum_f ell_f^2 <u_f,T>  failures = %d"%acc['id_fail'])
    print("  Gamma_c == sum_{f in c} ell_f^2  failures = %d"%acc['g_fail'])
    print("  MIN (BND) margin (A - <u_f,T>) = %s  at %s"%(float(acc['bnd_min'][0]),acc['bnd_min'][1:]))
    print("  MIN (CV)  margin (A*G - S2)     = %s  at %s"%(float(acc['cv_min'][0]),acc['cv_min'][1:]))
    if acc['bnd_first']: print("  FIRST (BND) violation: %s"%(acc['bnd_first'],))
    if acc['cv_first']:  print("  FIRST (CV)  violation: %s"%(acc['cv_first'],))
    if acc['id_first']:  print("  FIRST identity failure: %s"%(acc['id_first'],))
    if acc['g_first']:   print("  FIRST Gamma failure: %s"%(acc['g_first'],))
    print("\n  (BND) %s ;  (CV) %s ;  IDENTITY (BND=>CV) %s"%(
        "HOLDS" if not acc['bnd_viol'] else "FAILS",
        "HOLDS" if not acc['cv_viol'] else "FAILS",
        "EXACT" if not acc['id_fail'] and not acc['g_fail'] else "BROKEN"))
