"""For CRITICAL components specifically, is the restricted cut always a gamma-min connected MAX cut of G[C]?
Test on the critical family: C(2k+1)[t] blow-ups (T==N, C=V), and census criticals.
Since proper critical components don't occur, all criticals are C=V; we test that for these the global cut
IS the gamma-min max cut (sanity: gamma-min cut of a critical graph has Gamma=N^2=|V|^2, tight).
We also do a HARDER test: can a critical graph have a connected max cut whose restricted-to-a-K-subcomponent
... (n/a since C=V). Instead we test the GAP's contrapositive proxy: for EVERY triangle-free G and EVERY K-comp
C (any), if T==N on C then restricted cut is internally max AND gamma-min. Census N<=10 + odd-cycle blowups."""
from fractions import Fraction as F
from itertools import product
from collections import deque
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import Kcomponents, build_K_T

def oddcycle_blow(k,t):
    nn=k*t; E=[]
    for i in range(k):
        for a in range(t):
            for b in range(t): E.append((i*t+a,((i+1)%k)*t+b))
    return nn,E

def island_maxcut_gmin(C, adj, side):
    C=list(C); m=len(C); idx={v:i for i,v in enumerate(C)}
    iedges=[]; iadj=[[] for _ in range(m)]
    for u in C:
        for v in adj[u]:
            if v in idx and v>u:
                a,b=idx[u],idx[v]; iedges.append((a,b)); iadj[a].append(b); iadj[b].append(a)
    best=-1; cuts=[]
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        c=sum(1 for a,b in iedges if s[a]!=s[b])
        if c>best: best=c; cuts=[s]
        elif c==best: cuts.append(s)
    def conn(s):
        ad=[[] for _ in range(m)]
        for x,y in iedges:
            if s[x]!=s[y]: ad[x].append(y);ad[y].append(x)
        seen={0};q=deque([0])
        while q:
            u=q.popleft()
            for v in ad[u]:
                if v not in seen: seen.add(v);q.append(v)
        return len(seen)==m
    def bdist(s,a,b):
        ad=[[] for _ in range(m)]
        for x,y in iedges:
            if s[x]!=s[y]: ad[x].append(y);ad[y].append(x)
        d={a:0};q=deque([a])
        while q:
            u=q.popleft()
            for v in ad[u]:
                if v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(b,-1)
    gmin=None
    for s in cuts:
        if not conn(s): continue
        Mloc=[(a,b) for a,b in iedges if s[a]==s[b]]
        G=0;ok=True
        for a,b in Mloc:
            dd=bdist(s,a,b)
            if dd<0: ok=False;break
            G+=(dd+1)**2
        if ok and (gmin is None or G<gmin): gmin=G
    # restricted cut value
    sR=[side[v] for v in C]
    cR=sum(1 for a,b in iedges if sR[a]!=sR[b])
    return best, cR, gmin

def restrictedGamma(C,info):
    C=set(C); adj=info['adj']; side=info['side']
    def bd(a,b):
        d={a:0};q=deque([a])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v in C and side[u]!=side[v] and v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(b,-1)
    Ml=[(u,v) for u in C for v in adj[u] if v in C and v>u and side[u]==side[v]]
    G=0
    for u,v in Ml:
        dd=bd(u,v)
        if dd<0: return None
        G+=(dd+1)**2
    return G

def test(name,n,E):
    info=loads(n,E)
    if info is None: print(f"[{name}] loads None"); return
    adj=info['adj']; side=info['side']; K,T,M,ell,N=build_K_T(info)
    for C in Kcomponents(K,N):
        if not all(T[v]==N for v in C): continue   # critical only
        if len(C)>14:
            print(f"[{name}] critical |C|={len(C)} (too big to brute, skip island maxcut)"); continue
        mc,rc,gm=island_maxcut_gmin(C,adj,side)
        gC=restrictedGamma(C,info)
        print(f"[{name}] critical |C|={len(C)} N={N} restricted-cut={rc} island-maxcut={mc} is_max={rc==mc} "
              f"GammaC={gC} island_gmin={gm} restricted-is-gmin={gC==gm} GammaC=|C|^2:{gC==len(C)**2}")

if __name__=="__main__":
    print("=== critical components: restricted cut max & gamma-min on G[C]? ===")
    for k in [5,7,9]:
        for t in [1,2]:
            if k*t<=14: test(f"C{k}[{t}]",*oddcycle_blow(k,t))
    print("--- census N=7..10 criticals ---")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,M,ell,N=build_K_T(info)
            for C in Kcomponents(K,N):
                if all(T[v]==N for v in C) and any(f[0] in set(C) and f[1] in set(C) for f in M):
                    test(g6,n,E); break
