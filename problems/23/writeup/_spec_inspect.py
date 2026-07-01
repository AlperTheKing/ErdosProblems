"""Inspect the specific N=9 no-descent cut and find, by brute force, ALL admissible descending switches.
Then look at the geometry: which W descends, and how it relates to R, T, Over(Q), the eigenvector of K2."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side
from _csmspec import build_K2

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gamma_of(n,adj,s):
    G=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v)
                if d<0: return None
                G+=(d+1)**2
    return G

# find the N=9 graph whose all-max cut 111111000 has R<0.  Re-scan.
target_side="111111000"
for g6 in subprocess.run([GENG,'-tc','9'],capture_output=True,text=True).stdout.split():
    n,E=dec(g6); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    from _h import maxcut_all
    cuts=maxcut_all(n,adj); mc=max(cutsize(n,adj,s) for s in cuts)
    for s in cuts:
        if cutsize(n,adj,s)!=mc: continue
        if ''.join(map(str,s))!=target_side: continue
        if not Bconn(n,adj,s): continue
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        N=F(n); K2=build_K2(n,M,cyc)
        R=[N*T[v]-sum(K2[v][w]*T[w] for w in range(n)) for v in range(n)]
        if all(R[v]>=0 for v in range(n)): continue
        print("GRAPH g6=",g6," E=",E)
        print("side=",s," cut=",cutsize(n,adj,s)," Gamma=",gamma_of(n,adj,s))
        print("M (bad edges)=",M)
        print("ell=",{f:ell[f] for f in M})
        print("T=",[str(T[v]) for v in range(n)])
        print("R=",[str(R[v]) for v in range(n)])
        for f in M:
            print("  bad edge",f,"ell",ell[f],"#geos",len(cyc[f]))
            for Q in cyc[f]:
                Over=sum(T[u] for u in Q)-N*ell[f]
                print("     geo",Q," Over=",str(Over))
        base_cut=cutsize(n,adj,s); base_G=gamma_of(n,adj,s)
        print("--- brute force ALL admissible descending switches |W|<=4 ---")
        found=[]
        verts=list(range(n))
        for k in range(1,5):
            for W in itertools.combinations(verts,k):
                s2=s[:]
                for v in W: s2[v]^=1
                if cutsize(n,adj,s2)!=base_cut: continue
                if not Bconn(n,adj,s2): continue
                g2=gamma_of(n,adj,s2)
                if g2 is None: continue
                if g2<base_G: found.append((base_G-g2,W))
        found.sort(key=lambda x:(-x[0],len(x[1])))
        print("  # descending admissible switches |W|<=4:",len(found))
        for drop,W in found[:20]:
            print("     W=",W," Gamma-drop=",drop, " R on W=",[str(R[v]) for v in W]," T on W=",[str(T[v]) for v in W])
        raise SystemExit
