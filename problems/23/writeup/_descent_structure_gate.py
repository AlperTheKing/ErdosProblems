"""Exact-gate Codex's FINER structural certificate (block 173) for singleton Gamma-descents.
For each interval-Hall failure with a singleton descent x in [a,b]: old bad set M (lengths ell_old), flip x ->
new bad set M' (lengths ell_new). IncOld = bad edges of M incident to x (removed); IncNew = bad edges of M'
incident to x (added); cut-tight => |IncOld|=|IncNew|. Check:
 (3) incident exchange: a matching IncNew->IncOld with ell_new<=ell_old (sorted ascending, ell_new[i]<=ell_old[i]).
 (4) retained shortcut: sum over M cap M' of (ell_new^2 - ell_old^2) < 0 with >=1 strict shorten.
Report which is the obstruction if any. Battery: k-chord family k=3..9 chord-len 5,7. Exact."""
from fractions import Fraction as F
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def gamma_and_lengths(n,adj,s):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
    L={}
    for (u,v) in M:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None,None
        L[(u,v)]=d+1
    return M,L
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def kchord(k, clen=4):
    pend=clen*k
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def check(n,adj,s,acc):
    base_cut=cutsize(n,adj,s); M0,L0=gamma_and_lengths(n,adj,s)
    if M0 is None: return
    G0=sum(v*v for v in L0.values())
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
        compinfo=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),len(C)))
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in compinfo if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                # find a singleton descent x in [a,b]
                got=False
                for i in range(a,b+1):
                    x=P_f[i]; s2=s[:]; s2[x]^=1
                    if cutsize(n,adj,s2)!=base_cut or not Bconn(n,adj,s2): continue
                    M1,L1=gamma_and_lengths(n,adj,s2)
                    if M1 is None: continue
                    G1=sum(v*v for v in L1.values())
                    if G1>=G0: continue
                    got=True
                    # finer decomposition
                    M0s=set(M0); M1s=set(M1)
                    IncOld=[e for e in M0s if x in e]; IncNew=[e for e in M1s if x in e]
                    lo=sorted(L0[e] for e in IncOld); ln=sorted(L1[e] for e in IncNew)
                    cond3 = (len(lo)==len(ln)) and all(ln[j]<=lo[j] for j in range(len(ln)))
                    retained = M0s & M1s
                    rsum = sum(L1[e]**2 - L0[e]**2 for e in retained)
                    rstrict = any(L1[e] < L0[e] for e in retained)
                    cond4 = (rsum < 0) and rstrict
                    if not cond3: acc['c3fail']+=1
                    if not cond4: acc['c4fail']+=1
                    if cond3 and cond4: acc['ok']+=1
                    if (not cond3 or not cond4) and acc['first'] is None:
                        acc['first']=(f,(a,b),x,'c3' if not cond3 else 'c4',lo,ln,str(rsum),rstrict)
                    break
                if not got: acc['nosingleton']+=1
    return

if __name__=="__main__":
    print("=== singleton-descent FINER structure (block 173): incident-exchange (3) + retained-shortcut (4) ===",flush=True)
    acc={'fail':0,'ok':0,'c3fail':0,'c4fail':0,'nosingleton':0,'first':None}
    for clen in (4,6):
        for k in (3,5,7,9):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            check(n,adj,s,acc)
    print(f"  failures={acc['fail']} no-singleton={acc['nosingleton']} BOTH-(3)&(4)-hold={acc['ok']}",flush=True)
    print(f"  cond(3) incident-exchange failures={acc['c3fail']}  cond(4) retained-shortcut failures={acc['c4fail']}",flush=True)
    print(f"  === {'OBSTRUCTION: '+str(acc['first']) if acc['first'] else 'EVERY singleton descent decomposes as neutral incident-exchange + strict retained-shortcut'} ===",flush=True)
