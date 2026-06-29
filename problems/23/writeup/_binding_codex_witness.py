"""Check my 'binding I always interval' claim on Codex's block-145 N=10 witnesses (I???CB?^o, I?AAD@ON_):
does an interval achieve the GLOBAL min Hall slack? (If yes, min-over-intervals = min-over-all-I, so interval-Hall
<=> full Hall on these too -- no conflict with his 'interval-sandwich' technique failure, which is a different claim.)"""
import itertools
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def analyze(g6):
    n,E=dec(g6); adj,cuts=gmins(n,E)
    print(f"g6={g6} N={n} gmin-cuts={len(cuts)}")
    for s in cuts:
        st=struct_for_side(n,adj,s)
        if st is None: continue
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
            d=[S[P_f[i]]-1 for i in range(L)]
            rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
            def find(x):
                while par[x]!=x: par[x]=par[par[x]]; x=par[x]
                return x
            for u in rest:
                for w in adj[u]:
                    if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
            comps={}
            for v in rest: comps.setdefault(find(v),set()).add(v)
            compinfo=[]
            for root,C in comps.items():
                A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
                if A: compinfo.append((min(A),max(A),len(C)))
            # global min slack + all argmins; is any argmin an interval?
            gmin=None; argmins=[]
            for r in range(1,L+1):
                for I in itertools.combinations(range(L),r):
                    lhs=sum(d[i] for i in I)
                    rhs=sum(c for (lo,hi,c) in compinfo if any(lo<=i<=hi for i in I))
                    sl=rhs-lhs
                    if gmin is None or sl<gmin: gmin=sl; argmins=[I]
                    elif sl==gmin: argmins.append(I)
            def isint(I): return len(I)<=1 or list(I)==list(range(I[0],I[0]+len(I)))
            any_int=any(isint(I) for I in argmins)
            n_int=sum(isint(I) for I in argmins)
            print(f"  side={''.join(map(str,s))} f={f} P={P_f} d={[str(x) for x in d]} | min-slack={gmin} "
                  f"#argmins={len(argmins)} interval-argmins={n_int} ANY-INTERVAL-ARGMIN={any_int}")

if __name__=="__main__":
    print("=== verify binding-interval on Codex block-145 witnesses ===")
    for g6 in ["I???CB?^o","I?AAD@ON_"]:
        analyze(g6)
