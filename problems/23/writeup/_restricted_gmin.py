"""TEST: for a bad-carrying K-component C in the global gamma-min cut, is the restricted cut sigma|_C
a GAMMA-MIN (connected) max cut of G[C]?  i.e. does it minimize internal Gamma among max cuts of G[C]?

If global gamma-minimality forces restricted-gamma-min on each K-component (because boundary edges are
zero-mu so re-cutting C internally doesn't disturb outside geodesics), THEN by IH Gamma_C = Gamma_min(G[C])
<= |C|^2, closing the induction for critical components (which give Gamma_C = N|C| > |C|^2).

Method: for each bad-carrying K-comp C (|C|<=14), enumerate ALL max cuts of G[C], compute each's internal
Gamma (with B|_C distances), find the gamma-min among CONNECTED-B ones, and compare to restricted Gamma_C.
Report whether restricted Gamma_C == gamma-min(G[C]) and Gamma_C <= |C|^2.  EXACT Fraction.
Census N<=10 loads-cut + bridge witness."""
from fractions import Fraction as F
from itertools import product
from collections import deque
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import Kcomponents, build_K_T, mycielski, union_disjoint, add_edges, Cn, blow_g

def island_gamma_min(C, adj):
    """Min internal Gamma over connected-B max cuts of G[C]. Returns (gmin, maxcut_size)."""
    C=list(C); m=len(C); idx={v:i for i,v in enumerate(C)}
    iadj=[[] for _ in range(m)]
    iedges=[]
    for u in C:
        for v in adj[u]:
            if v in idx and v>u:
                a,b=idx[u],idx[v]; iadj[a].append(b); iadj[b].append(a); iedges.append((a,b))
    # max cut size
    best=-1; cuts=[]
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        c=sum(1 for a,b in iedges if s[a]!=s[b])
        if c>best: best=c; cuts=[s]
        elif c==best: cuts.append(s)
    def bconn(s):
        seen={0};q=deque([0])
        while q:
            u=q.popleft()
            for v in iadj[u]:
                if s[u]!=s[v] and v not in seen: seen.add(v);q.append(v)
        return len(seen)==m
    def bdist(s,a,b):
        d={a:0};q=deque([a])
        while q:
            u=q.popleft()
            for v in iadj[u]:
                if s[u]!=s[v] and v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(b,-1)
    gmin=None
    for s in cuts:
        if not bconn(s): continue
        Mloc=[(a,b) for a,b in iedges if s[a]==s[b]]
        G=0; ok=True
        for a,b in Mloc:
            dd=bdist(s,a,b)
            if dd<0: ok=False;break
            G+=(dd+1)**2
        if ok and (gmin is None or G<gmin): gmin=G
    return gmin, best

def gammaC_restricted(C, info):
    """Internal Gamma of C under the global restricted cut, using B|_C distances."""
    C=set(C); adj=info['adj']; side=info['side']
    # B|_C adjacency
    def bdist(a,b):
        d={a:0};q=deque([a])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v in C and side[u]!=side[v] and v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(b,-1)
    Mloc=[(u,v) for u in C for v in adj[u] if v in C and v>u and side[u]==side[v]]
    G=0
    for u,v in Mloc:
        dd=bdist(u,v)
        if dd<0: return None
        G+=(dd+1)**2
    return G

def run(name,n,E):
    info=loads(n,E)
    if info is None: return
    adj=info['adj']
    K,T,M,ell,N=build_K_T(info); O=set(v for v in range(N) if T[v]>N)
    out=[]
    for C in Kcomponents(K,N):
        Cs=set(C)
        if not any(f[0] in Cs and f[1] in Cs for f in M): continue
        if len(C)>14: continue
        gmin,mc=island_gamma_min(C,adj)
        gC=gammaC_restricted(C,info)
        crit=all(T[v]==N for v in C)
        out.append((len(C),gC,gmin,gC==gmin,gC<=len(C)**2,crit,bool(Cs&O)))
    return out

if __name__=="__main__":
    print("=== restricted Gamma_C vs island gamma-min, and Gamma_C<=|C|^2 ===")
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
    for name,(n_,E_) in [("bridge",(n,E))]+[(f"C5[{t}]",blow_g(5,Cn(5),t)) for t in [2]]:
        o=run(name,n_,E_)
        for (sz,gC,gm,eq,le,crit,mO) in o or []:
            print(f"  [{name}] |C|={sz} GammaC={gC} island_gmin={gm} restricted-IS-gmin={eq} GammaC<=|C|^2={le} crit={crit} meetsO={mO}")
    print("--- census N=7..10 loads-cut: count restricted!=island-gmin AND GammaC>|C|^2 (on bad-carrying comps) ---")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        neq=0; tot=0; gtv=0; crit_total=0; crit_eq=0
        for g6 in outg:
            n,E=dec(g6); o=run(g6,n,E)
            for (sz,gC,gm,eq,le,crit,mO) in o or []:
                tot+=1
                if not eq: neq+=1
                if not le: gtv+=1
                if crit:
                    crit_total+=1
                    if eq: crit_eq+=1
        print(f"  N={nn}: bad-carrying comps={tot} restricted!=island_gmin={neq} GammaC>|C|^2={gtv} "
              f"| critical: total={crit_total} restricted-IS-island-gmin={crit_eq}",flush=True)
