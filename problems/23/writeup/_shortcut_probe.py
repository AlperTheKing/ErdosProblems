"""Probe (B-iii): WHY does flipping the argmax-load hub x* shorten f's own geodesic?
For each k-chord interval-Hall failure: print f, old geodesic P (length L), failing interval I,
hub position i*, hub load; then f's NEW shortest alternating geodesic P' after flipping x*, its length,
and the set of edges P' uses that are NOT on P (the 'activated' chords/detour edges). Goal: see the
general shortcut certificate tying the Hall deficit at x* to the shortened f-route. Exact BFS."""
from collections import deque
from fractions import Fraction as F
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def shortest_alt_path(adj,side,src,dst):
    # BFS over cut edges, reconstruct one shortest alternating path
    prev={src:None}; q=deque([src])
    while q:
        u=q.popleft()
        if u==dst: break
        for v in adj[u]:
            if side[u]!=side[v] and v not in prev: prev[v]=u; q.append(v)
    if dst not in prev: return None
    path=[]; u=dst
    while u is not None: path.append(u); u=prev[u]
    return path[::-1]

def run():
    print("=== (B-iii) shortcut probe: f old geodesic vs new geodesic after hub flip ===",flush=True)
    for clen in (4,6):
        for k in (3,):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            st=struct_for_side(n,adj,s)
            if st is None: continue
            M,elld,T,mu,cyc=st
            S=[F(0)]*n
            for g in M:
                kk=len(cyc[g])
                for P in cyc[g]:
                    for v in P: S[v]+=F(1,kk)
            for f in M:
                if len(cyc[f])!=1: continue
                P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
                dvec=[S[v]-1 for v in P_f]
                Pedges=set((min(P_f[i],P_f[i+1]),max(P_f[i],P_f[i+1])) for i in range(L-1))
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
                done=False
                for a in range(L):
                    if done: break
                    for b in range(a,L):
                        dem=sum(dvec[i] for i in range(a,b+1))
                        cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                        if dem<=cap: continue
                        m=max(dvec[i] for i in range(a,b+1))
                        istar=[i for i in range(a,b+1) if dvec[i]==m][0]
                        xstar=P_f[istar]
                        s2=s[:]; s2[xstar]^=1
                        Pnew=shortest_alt_path(adj,s2,f[0],f[1])
                        Lnew=len(Pnew) if Pnew else None
                        newedges=set()
                        if Pnew:
                            for i in range(len(Pnew)-1):
                                e=(min(Pnew[i],Pnew[i+1]),max(Pnew[i],Pnew[i+1]))
                                if e not in Pedges: newedges.add(e)
                        print(f"  k={k} clen={clen} f={f}: L={L} I=[{a},{b}] hub i*={istar} x*={xstar} load={float(m)}",flush=True)
                        print(f"      P(old)={P_f}",flush=True)
                        print(f"      P'(new len {Lnew})={Pnew}",flush=True)
                        print(f"      activated non-P edges in P': {sorted(newedges)}",flush=True)
                        # which off-path components do the activated edges touch?
                        print(f"      off-path components (lo,hi,|C|): {comps}",flush=True)
                        done=True; break

if __name__=="__main__": run()
