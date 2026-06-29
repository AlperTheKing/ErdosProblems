"""Exact-gate Codex block-183 deterministic bracket-shortcut + incident-neutrality formulas, on the
descent-decomposition corpus (k-chord interval-Hall failures, max-load hub x_i).
Bracket rows: the two P-contained bad edges incident to hub x_i, other endpoints x_p,x_q with p<i<q,
contained geodesics P[p..i], P[i..q]. Checks:
 (1) bracket rows exist with p<i<q and geodesics exactly P[p..i], P[i..q];
 (2) shortcut seq x_0..x_p, x_i, x_q..x_{L-1} is a valid alternating path after flipping x_i;
 (3) ell_{s'}(f) == L-(q-p-2)  (exact);
 (4) rotated incident path  x_{i-1},...,x_p,x_i  is alt after flip with ell == old ell(x_p,x_i);
     rotated incident path  x_i,x_q,...,x_{i+1}  is alt after flip with ell == old ell(x_i,x_q);
 (5) first obstruction. Exact BFS for ell'."""
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

def is_alt(adj,side,Q):
    for i in range(len(Q)-1):
        u,v=Q[i],Q[i+1]
        if v not in adj[u] or side[u]==side[v]: return False
    return True

def run():
    acc={'cases':0,'c1':0,'c2':0,'c3':0,'c4':0,'all':0,'first':None}
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
                        acc['cases']+=1
                        xstar=P_f[istar]
                        # incident P-contained bad bracket rows
                        inc=[w for w in adj[xstar] if s[w]==s[xstar] and w in pos]
                        ps=[pos[w] for w in inc if pos[w]<istar]; qs=[pos[w] for w in inc if pos[w]>istar]
                        s2=s[:]; s2[xstar]^=1
                        if not ps or not qs:
                            if acc['first'] is None: acc['first']=('no-bracket',clen,k,f,istar,inc); continue
                        p=max(ps); q=min(qs)
                        # (1) contained geodesics exactly P[p..i], P[i..q]?
                        g1=(min(P_f[p],xstar),max(P_f[p],xstar)); g2=(min(xstar,P_f[q]),max(xstar,P_f[q]))
                        cyc_g1=cyc.get(g1,[]); cyc_g2=cyc.get(g2,[])
                        geo1=[P_f[t] for t in range(p,istar+1)]; geo2=[P_f[t] for t in range(istar,q+1)]
                        c1 = any(list(Q)==geo1 for Q in cyc_g1) and any(list(Q)==geo2 for Q in cyc_g2)
                        if c1: acc['c1']+=1
                        # (2) shortcut seq valid alt path after flip
                        seqf=P_f[:p+1]+[xstar]+P_f[q:]
                        c2 = is_alt(adj,s2,seqf) and seqf[0]==f[0] and seqf[-1]==f[1]
                        if c2: acc['c2']+=1
                        # (3) ell'(f) == L-(q-p-2)
                        d=bdist_restr(adj,s2,f[0],f[1]); ellp = d+1 if d>=0 else None
                        c3 = (ellp is not None and ellp == L-(q-p-2))
                        if c3: acc['c3']+=1
                        # (4) rotated incident paths after flip have predicted ell == old bracket ell
                        rot1=[P_f[t] for t in range(istar-1,p-1,-1)]+[xstar]   # x_{i-1}..x_p, x_i
                        rot2=[xstar]+[P_f[t] for t in range(q,istar,-1)]       # x_i, x_q..x_{i+1}
                        old1=bdist_restr(adj,s,g1[0],g1[1])+1; old2=bdist_restr(adj,s,g2[0],g2[1])+1
                        # ell of new incident bad edges after flip:
                        e1=(min(P_f[istar-1],xstar),max(P_f[istar-1],xstar)); e2=(min(xstar,P_f[istar+1]),max(xstar,P_f[istar+1]))
                        ne1=bdist_restr(adj,s2,e1[0],e1[1]); ne2=bdist_restr(adj,s2,e2[0],e2[1])
                        ne1=ne1+1 if ne1>=0 else None; ne2=ne2+1 if ne2>=0 else None
                        c4 = (is_alt(adj,s2,rot1) and is_alt(adj,s2,rot2)
                              and len(rot1)==old1 and len(rot2)==old2
                              and ne1==old1 and ne2==old2)
                        if c4: acc['c4']+=1
                        if c1 and c2 and c3 and c4: acc['all']+=1
                        elif acc['first'] is None:
                            acc['first']=(clen,k,f,istar,(p,q),c1,c2,c3,c4,'ellp',ellp,'Lqp',L-(q-p-2),
                                          'rot_ells',(len(rot1),old1,ne1),(len(rot2),old2,ne2))
    print("=== block-183 deterministic bracket-shortcut + neutrality gate ===",flush=True)
    print(f"  cases={acc['cases']}",flush=True)
    print(f"  (1) bracket rows p<i<q with contained geodesics P[p..i],P[i..q]: {acc['c1']}/{acc['cases']}",flush=True)
    print(f"  (2) shortcut seq valid alt B-path after flip:                    {acc['c2']}/{acc['cases']}",flush=True)
    print(f"  (3) ell'(f) == L-(q-p-2) exactly:                                {acc['c3']}/{acc['cases']}",flush=True)
    print(f"  (4) rotated incident paths alt + ell == old bracket ell:         {acc['c4']}/{acc['cases']}",flush=True)
    print(f"  ALL (1-4): {acc['all']}/{acc['cases']}",flush=True)
    if acc['first']: print(f"  first obstruction: {acc['first']}",flush=True)
    print(f"  === {'block-183 formulas CONFIRMED exact: deterministic bracket rows => Gamma descent; sole gap = overload => bracket rows at hub' if acc['all']==acc['cases'] else 'OBSTRUCTION (see first)'} ===",flush=True)

if __name__=="__main__": run()
