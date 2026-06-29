"""Exact-gate Codex's LOCAL HUB structure (block 175) at max-load vertices of interval-Hall failures.
For each failure, each max-load vertex x=x_i in I=[a,b], test version B:
  (i) x internal on P (0<i<L-1);
  (ii) d_B(x)=2 and d_M(x)=2 (degree 4, cut-tight);
  (iii) the two B-neighbors of x are exactly x_{i-1},x_{i+1};
  (iv) the two M-(bad)-neighbors of x are endpoints of P-contained bad rows (geodesic subset of P).
Report B-pass count, and if B fails the actual local type (d_B,d_M, incident bad lengths, P-contained?).
Battery: k-chord k=3,6,9,12 chord-len 5,7. Exact."""
from fractions import Fraction as F
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gamma_of(n,adj,s):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]; G=0
    for (u,v) in M:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def check(n,adj,s,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        # P-contained bad rows: g with a geodesic that is a subpath of P
        Pcontained=set()
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset: Pcontained.add(g); break
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                m=max(dvec[i] for i in range(a,b+1))
                H=[i for i in range(a,b+1) if dvec[i]==m]
                for i in H:
                    x=P_f[i]; acc['hub']+=1
                    dB=sum(1 for w in adj[x] if s[w]!=s[x]); dM=sum(1 for w in adj[x] if s[w]==s[x])
                    internal = 0<i<L-1
                    bnb=set(w for w in adj[x] if s[w]!=s[x])
                    pathnb = {P_f[i-1],P_f[i+1]} if internal else set()
                    mnb=[(min(x,w),max(x,w)) for w in adj[x] if s[w]==s[x]]
                    mn_contained = all(e in Pcontained for e in mnb)
                    B = internal and dB==2 and dM==2 and bnb==pathnb and mn_contained
                    if B: acc['Bok']+=1
                    else:
                        acc['Bfail']+=1
                        if acc['first'] is None:
                            badlens={e: bdist_restr(adj,s,e[0],e[1])+1 for e in mnb}
                            acc['first']=(f,(a,b),i,internal,dB,dM,bnb==pathnb,mnb,badlens,mn_contained)
    return

if __name__=="__main__":
    print("=== LOCAL HUB structure gate (block 175 version B): max-load vertex = internal, dB=dM=2, path B-nbrs, P-contained bad nbrs ===",flush=True)
    acc={'fail':0,'hub':0,'Bok':0,'Bfail':0,'first':None}
    for clen in (4,6):
        for k in (3,6,9,12):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            check(n,adj,s,acc)
    print(f"  failures={acc['fail']} max-load hub-checks={acc['hub']} B-OK={acc['Bok']} B-FAIL={acc['Bfail']}",flush=True)
    print(f"  === {'B-OBSTRUCTION: '+str(acc['first']) if acc['first'] else 'version B holds: every max-load vertex is internal, dB=dM=2, path B-nbrs, 2 P-contained bad nbrs'} ===",flush=True)
