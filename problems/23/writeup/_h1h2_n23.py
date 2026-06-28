"""Exact H1/H2 high-split test at N=23 Myc(Grotzsch) -- the witness for Codex block 17.
H1: k1_gap(o) <= surplus(o);  H2: two(o) >= surplus(o);  H1&H2 => k2>=0. Since k2<0 at o=22, one fails."""
from fractions import Fraction as F
from _h import loads
from _schur_spec import pf_exact

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

C5n=5; C5E=[(i,(i+1)%5) for i in range(5)]
n1,E1=mycielski(C5n,C5E); n2,E2=mycielski(n1,E1)
info=loads(n2,E2)
P,M,ell,n=pf_exact(info); N=n
K=[[F(0)]*n for _ in range(n)]
for d in P:
    it=list(d.items())
    for a in range(len(it)):
        va,pa=it[a]
        for b in range(len(it)):
            vb,pb=it[b]; K[va][vb]+=pa*pb
T=[sum(K[v][w] for w in range(n)) for v in range(n)]
O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
u={q:F(N)-T[q] for q in Q}
W={q:sum(K[q][q2]*u[q2] for q2 in Q) for q in Q}
print("N=23 Myc(Grotzsch), O=",O)
for o in O:
    S_o=sum(d.get(o,F(0)) for d in P)
    one=sum(K[o][q]*u[q] for q in Q)/N
    two=sum(K[o][q]*W[q] for q in Q)/(N*N)
    k1_gap=T[o]-N-one
    high=(T[o]+4*S_o > 2*N)
    surplus=(T[o]+4*S_o-2*N)/N
    k2margin=two-k1_gap
    h1m=surplus-k1_gap; h2m=two-surplus
    print(f"  o={o}: high={high} T={float(T[o]):.3f} S={float(S_o):.3f} k1_gap={float(k1_gap):+.4f} two={float(two):+.4f} surplus={float(surplus):+.4f} k2margin={float(k2margin):+.5f}")
    if high:
        print(f"     H1 surplus-k1_gap = {float(h1m):+.5f} (exact {h1m})  {'PASS' if h1m>=0 else '*** FAIL ***'}")
        print(f"     H2 two-surplus    = {float(h2m):+.5f} (exact {h2m})  {'PASS' if h2m>=0 else '*** FAIL ***'}")
