"""Make 'chorded hub => f shortens' a PROVEN step, and pin the remaining gap.
For EVERY k-chord interval-Hall failure, at the max-load hub x*=x_{i*}:
  (S1) x* has exactly two incident BAD edges g1=(y,x*), g2=(x*,z) with y,z on P and pos(y)<i*<pos(z)
       (across-straddle), both P-contained.
  (S2) CONSTRUCT explicit path Q = P[0..pos(y)] + [x*] + P[pos(z)..end] using chords (y,x*),(x*,z);
       verify after flipping x* that Q is a valid ALTERNATING path f0->f1 and len(Q) < L. (proves ell'(f)<L)
  (S3) cut-tight: #incident cut-edges == #incident bad-edges at x* (so cutsize preserved); Bconn after flip.
If S1&S2&S3 hold on all failures, 'chorded hub => strict Gamma-descent' is constructive; the ONLY
remaining obligation is 'interval-Hall failure => max-load hub satisfies S1&S3'. Exact."""
from collections import deque
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def is_alt_path(adj,side,Q):
    for i in range(len(Q)-1):
        u,v=Q[i],Q[i+1]
        if v not in adj[u]: return False
        if side[u]==side[v]: return False
    return True

def run():
    acc={'fail':0,'S1':0,'S2':0,'S3':0,'all':0,'firstbad':None}
    for clen in (4,5,6,7):
        for k in (3,4,6):
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
            Pcontained=set()
            badset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if u<v and s[u]==s[v])
            for f in M:
                if len(cyc[f])!=1: continue
                P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
                dvec=[S[v]-1 for v in P_f]
                Pcont=set()
                for g in M:
                    if g==f: continue
                    for Q in cyc[g]:
                        if set(Q)<=Pset: Pcont.add((min(g),max(g))); break
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
                seen=set()
                for a in range(L):
                    for b in range(a,L):
                        dem=sum(dvec[i] for i in range(a,b+1))
                        cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                        if dem<=cap: continue
                        m=max(dvec[i] for i in range(a,b+1))
                        istar=[i for i in range(a,b+1) if dvec[i]==m][0]
                        if istar in seen: continue
                        seen.add(istar)
                        acc['fail']+=1
                        xstar=P_f[istar]
                        # incident bad edges
                        inc_bad=[(min(xstar,w),max(xstar,w)) for w in adj[xstar] if s[w]==s[xstar]]
                        # straddling, both endpoints on P, P-contained
                        straddle=[]
                        for e in inc_bad:
                            other=e[0] if e[1]==xstar else e[1]
                            if other in pos and e in Pcont: straddle.append((pos[other],other,e))
                        backs=[t for t in straddle if t[0]<istar]; fwds=[t for t in straddle if t[0]>istar]
                        S1 = len(inc_bad)==2 and len(backs)>=1 and len(fwds)>=1
                        if S1: acc['S1']+=1
                        # S2: construct explicit Q after flip
                        ok2=False
                        if backs and fwds:
                            y=max(backs,key=lambda t:t[0]); z=min(fwds,key=lambda t:t[0])
                            yi,yv=y[0],y[1]; zi,zv=z[0],z[1]
                            Q=P_f[:yi+1]+[xstar]+P_f[zi:]
                            s2=s[:]; s2[xstar]^=1
                            ok2 = is_alt_path(adj,s2,Q) and Q[0]==f[0] and Q[-1]==f[1] and len(Q)<L
                        if ok2: acc['S2']+=1
                        # S3 cut-tight + Bconn
                        dB=sum(1 for w in adj[xstar] if s[w]!=s[xstar]); dM=len(inc_bad)
                        s2=s[:]; s2[xstar]^=1
                        S3 = (dB==dM) and cutsize(n,adj,s2)==cutsize(n,adj,s) and Bconn(n,adj,s2)
                        if S3: acc['S3']+=1
                        if S1 and ok2 and S3: acc['all']+=1
                        elif acc['firstbad'] is None:
                            acc['firstbad']=(k,clen,f,istar,xstar,inc_bad,S1,ok2,S3)
    print("=== STRADDLE-SHORTCUT gate: chorded hub => constructive strict descent ===",flush=True)
    print(f"  interval-Hall failures (distinct hub) = {acc['fail']}",flush=True)
    print(f"  S1 across-straddle two incident P-contained bad chords: {acc['S1']}/{acc['fail']}",flush=True)
    print(f"  S2 explicit alternating shorter f-path after flip:      {acc['S2']}/{acc['fail']}",flush=True)
    print(f"  S3 cut-tight (dB==dM) + cutsize preserved + Bconn:       {acc['S3']}/{acc['fail']}",flush=True)
    print(f"  ALL (S1&S2&S3):                                          {acc['all']}/{acc['fail']}",flush=True)
    if acc['firstbad']: print(f"  first not-all: {acc['firstbad']}",flush=True)
    print(f"  === {'CONSTRUCTIVE: chorded-straddle hub => explicit shorter f-route => strict Gamma-descent (remaining gap: failure => S1&S3)' if acc['all']==acc['fail'] else 'GAP: see first not-all'} ===",flush=True)

if __name__=="__main__": run()
