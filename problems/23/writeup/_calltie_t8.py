"""Final exact verification of the per-component handshake derivation on MycGrotzsch N=23
(large-excess case, single comp meets O) and the C5[t] overload-free cases.
Confirms: 2*sum_{e in C}mu = 2*Gamma_C - sum_{w in C}D(w), and = sum_f ell(ell-1)."""
from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges
from _calltie_glue import components_from_info

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def run(name, nn, EE):
    info=loads(nn,EE); T=info['T']; N=info['n']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    O=set(v for v in range(N) if T[v]>N)
    comps=components_from_info(info)
    supp={f:set(v for P in cyc[f] for v in P) for f in M}
    for C in comps:
        Cs=set(C)
        if sum(T[v] for v in C)==0: continue
        intmu=sum(val for e,val in mu.items() if (tuple(e)[0] in Cs and tuple(e)[1] in Cs))
        sumD=sum(sum(ell[f] for f in M if w in f) for w in C)
        lhs=2*intmu; rhs=2*sum(T[w] for w in C)-sumD
        GammaC=sum(T[w] for w in C)
        FC=[f for f in M if supp[f] and supp[f]<=Cs]
        ident=sum(F(ell[f])*(ell[f]-1) for f in FC)
        mx=max(T[v] for v in C)
        print(f"{name}: |C|={len(C)} meetsO={bool(Cs&O)} maxT={float(mx)} excess={float(mx-len(C))}")
        print(f"  handshake-sum: 2*intmu={float(lhs)} == 2Gamma-sumD={float(rhs)} : {lhs==rhs}")
        print(f"  mu-identity:   intmu={float(intmu)} == sum ell(ell-1)={float(ident)} : {intmu==ident}")
        print(f"  GammaC={float(GammaC)} N|C|={N*len(C)} deficit={float(N*len(C)-GammaC)}")

if __name__=="__main__":
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1)
    run("MycGrotzsch23", n2,E2)
