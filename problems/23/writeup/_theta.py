"""Codex ASK (20:21:10Z): variable-size theta-cluster hypothesis. Does max_y L(y) always live on ONE cluster?
Cluster notions on the bad-edge graph (vertices=bad edges):
 (1) support-overlap: f~g iff O_fg>0. [L separable over these components -> max on one component, EXACT. baseline]
 (2) endpoint/strong-overlap: f~g iff share an endpoint OR O_fg>=1.
 (3) theta-star: for endpoint a, star(a)={edges incident a} U {edges h: O_hg>0 for >=2 incident edges g}.
For each: maxL restricted to the cluster's vertex-support; best cluster vs global maxL; report gap & failures + dump.
O_fg=sum_v p_f(v)p_g(v)."""
import numpy as np, subprocess, itertools
from _h import dec, GENG, loads
from _kktcore2 import setup, maximizeL

def Omat(L):
    m=len(L); P=[dict(pf) for (f,lay,pf,h) in L]
    O=np.zeros((m,m))
    for a in range(m):
        for b in range(m):
            O[a,b]=sum(P[a].get(v,0)*P[b].get(v,0) for v in P[a])
    return O,P

def comps(m, adj):
    seen=[-1]*m; c=0
    for s in range(m):
        if seen[s]<0:
            st=[s]; seen[s]=c
            while st:
                u=st.pop()
                for v in range(m):
                    if adj(u,v) and seen[v]<0: seen[v]=c; st.append(v)
            c+=1
    groups={}
    for i in range(m): groups.setdefault(seen[i],[]).append(i)
    return list(groups.values())

def thetastars(L,M,O):
    m=len(L)
    inc={}  # endpoint -> edges incident
    for ei,f in enumerate(M):
        inc.setdefault(f[0],[]).append(ei); inc.setdefault(f[1],[]).append(ei)
    stars=[]
    for a,edges in inc.items():
        star=set(edges)
        for h in range(m):
            cnt=sum(1 for g in edges if O[h,g]>1e-9)
            if cnt>=2: star.add(h)
        stars.append(sorted(star))
    return stars

def cluster_max(L,n,M,cluster_edges):
    allowed=set()
    for ei in cluster_edges:
        allowed|=set(L[ei][2].keys())  # supp(p_f)
    v,_=maximizeL(L,n,allowed=allowed,restarts=5)
    return v

def analyze(g6,info):
    L,n,M=setup(info)
    if len(M)<2: return None
    O,P=Omat(L)
    gmax,_=maximizeL(L,n,restarts=12)
    # (1) support-overlap components
    c1=comps(len(M),lambda a,b: O[a,b]>1e-9)
    best1=max(cluster_max(L,n,M,comp) for comp in c1)
    # (2) endpoint OR O>=1
    def adj2(a,b):
        fa,fb=M[a],M[b]
        return (set(fa)&set(fb)) or O[a,b]>=1.0-1e-9
    c2=comps(len(M),adj2)
    best2=max(cluster_max(L,n,M,comp) for comp in c2)
    # (3) theta-stars
    stars=thetastars(L,M,O)
    best3=max((cluster_max(L,n,M,st) for st in stars), default=0.0)
    return gmax,best1,best2,best3,len(M),[len(c) for c in c1],[len(c) for c in c2],max((len(s) for s in stars),default=0)

if __name__=="__main__":
    print("=== theta-cluster: does ONE cluster attain max L? (gap = global - best-cluster) ===")
    for g6 in ["J?`@C_W{Ck?","J?AA@AW^?}?","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); r=analyze(g6,info)
        if r is None: print(f"  {g6}: |M|<2"); continue
        gmax,b1,b2,b3,nm,c1s,c2s,smax=r
        print(f"  {g6:13} N={n} |M|={nm} | maxL={gmax:.4f} | (1)supp gap={gmax-b1:+.3f} comps={c1s} | (2)endpt/O>=1 gap={gmax-b2:+.3f} comps={c2s} | (3)theta-star gap={gmax-b3:+.3f} maxstar={smax}")
    # census N<=10 full + N=11 sample
    for nn,stride in [(9,1),(10,4),(11,40)]:
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; f2=0; f3=0; g2=None; mg2=None; g3=None; mg3=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=analyze(g6,info)
            if r is None: continue
            nt+=1; gmax,b1,b2,b3,nm,c1s,c2s,smax=r
            if gmax-b2>1e-3: f2+=1
            if gmax-b3>1e-3: f3+=1
            if mg2 is None or gmax-b2>mg2: mg2=gmax-b2; g2=g6
            if mg3 is None or gmax-b3>mg3: mg3=gmax-b3; g3=g6
        print(f"  N={nn}(stride{stride}): cfg={nt} | (2) single-cluster FAILS:{f2} maxgap={mg2:+.4f}@{g2} | (3) theta-star FAILS:{f3} maxgap={mg3:+.4f}@{g3}",flush=True)
