"""Verify Codex's N=12 counterexample to the variance strengthening (block 138):
K??CB@OBDOAp, side 111111000000, f=(6,11): ow_f=12=N, var_f=10/7, margin N(N-row)-var=-10/7<0.
Key structural point to confirm: ROWSUM-O is TIGHT (row=N) with NON-ZERO load variance (nested unique-path row),
so the equality set is richer than the all-tie/blow-up extremal -> any positive-variance correction is dead."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn
from _satzmu_conn import struct_for_side

g6="K??CB@OBDOAp"; side=[1,1,1,1,1,1,0,0,0,0,0,0]
n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
def cutsize(s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
mc=max(cutsize(s) for s in maxcut_all(n,adj))
print(f"g6={g6} N={n} cutsize={cutsize(side)} maxcut={mc} is_maxcut={cutsize(side)==mc} Bconn={Bconn(n,adj,side)}")
st=struct_for_side(n,adj,side)
M,ell,T,mu,cyc=st
print(f"bad edges M={sorted(M)} ell={{f:ell[f] for f in sorted(M)}}")
S=[F(0)]*n; pf={}
for g in M:
    Ps=cyc[g]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    pf[g]=d
    for v,pv in d.items(): S[v]+=pv
print(f"S = {[str(S[v]) for v in range(n)]}")
for f in sorted(M):
    d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
    mean=row/ll; var=sum(d[v]*(S[v]-mean)**2 for v in d)
    margin=F(n)*(F(n)-row)-var
    Ps=cyc[f]
    print(f"  f={f}: #geo={len(Ps)} path(s)={Ps} ell={ll} row={row}={float(row)} (N={n}) var={var}={float(var):.4f} "
          f"N(N-row)-var={margin}={float(margin):.4f} {'*** VAR-FAIL ***' if margin<0 else 'ok'} | ROWSUM-O({row}<=12)={row<=n}")
print("\n=> variance strengthening DEAD: ROWSUM-O tight (row=N) WITH var>0 at a nested unique-path row.")
