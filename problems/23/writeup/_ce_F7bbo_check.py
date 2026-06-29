"""Scrutinize the Codex-B*-lemma counterexample F?bbo side 0001110 f=(1,6) P=[1,5,0,4,6] I=(0,2).
Decide: is this cut a connected-B GLOBAL MAX cut? Does ANY flip (single vertex / arbitrary subset) increase
the cut (=> non-max)? Does a NON-path-interval flip gain cut (=> Codex's path-interval form too narrow but
cut still non-max)?  Only a GLOBAL-MAX no-hub no-any-cutgain IH-failure would break (B*)."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn
from _satzmu_conn import struct_for_side

g6="F?bbo"; n,E=dec(g6); adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
s=[int(c) for c in "0001110"]
def cutsize(s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
cs=cutsize(s)
allmax=maxcut_all(n,adj); mx=cutsize(list(allmax[0]))
print(f"n={n} edges={E}")
print(f"cut side={s} cutsize={cs} GLOBAL-max={mx} is-global-max={cs==mx} Bconn={Bconn(n,adj,s)}")
# any single-vertex flip increasing cut?
sv=[]
for v in range(n):
    s2=s[:]; s2[v]^=1
    if cutsize(s2)>cs: sv.append((v,cutsize(s2)))
print(f"single-vertex cut-increasing flips: {sv}")
# any subset flip increasing cut (n=7 small, enumerate)?
best=None
for m in range(1,1<<n):
    s2=[s[v]^((m>>v)&1) for v in range(n)]
    c=cutsize(s2)
    if c>cs and (best is None or c>best[1]):
        S=[v for v in range(n) if (m>>v)&1]; best=(S,c)
print(f"any subset flip increasing cut (max): {best}")
# the path P and is the gain subset a path-interval of P?
st=struct_for_side(n,adj,s)
if st:
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])==1 and cyc[f][0]==[1,5,0,4,6]:
            print(f"f={f} P={cyc[f][0]} ell={ell[f]}")
            # show contained chords + S(v) and demand vs cap on I=(0,2)
            S=[F(0)]*n
            for g in M:
                k=len(cyc[g])
                for P in cyc[g]:
                    for v in P: S[v]+=F(1,k)
            P_f=cyc[f][0]; print(f"  S on P = {[str(S[v]) for v in P_f]}")
print("VERDICT: if is-global-max=False, this is NOT a (B*) counterexample -- just a non-max cut where the",
      "cut-gain needs a non-path-interval flip (Codex's path-interval form is too narrow, (B*) survives).")
