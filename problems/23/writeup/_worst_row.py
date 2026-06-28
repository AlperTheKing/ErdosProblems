"""Microscope on the worst row: cut 3 side 000011111100, f=(2,11), ROWSUM=56/5=11.2, margin 0.8.
For each vertex v: p_f(v), S(v), p_f(v)*S(v), and the breakdown S(v) = sum_g p_g(v).
GOAL: see the dilution. The high-S vertices on f's interval should have p_f(v)<1 (shared), so their
contribution p_f(v)*S(v) is bounded; the p_f(v)=1 vertices (only on f's geodesics) have small S(v)."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side

n, E = dec("K??CE@A{?]Fc")
adj = [set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
adj2, cuts = gmins(n, E)
s = cuts[3]
st = struct_for_side(n, adj2, s)
M, ell, T, mu, cyc = st
pf = {}; S = [F(0)]*n
for g in M:
    Ps = cyc[g]; k = len(Ps); d = {}
    for P in Ps:
        for v in P: d[v] = d.get(v, F(0)) + F(1,k)
    pf[g] = d
    for v,pv in d.items(): S[v] += pv

print(f"side = {''.join(map(str,s))}")
print(f"M = {M}, ell = {[ell[f] for f in M]}")
print(f"\ngeodesics:")
for g in M:
    print(f"  {g}: {cyc[g]}")

f = (2,11)
d = pf[f]
print(f"\n=== WORST EDGE f={f}, ROWSUM = {sum(pv*S[v] for v,pv in d.items())} ===")
print(f"{'v':>3} {'p_f(v)':>8} {'S(v)':>6} {'p_f*S':>8}   S(v)=sum_g p_g(v) breakdown")
for v in sorted(d):
    parts = {g: pf[g].get(v,F(0)) for g in M if pf[g].get(v,F(0))>0}
    bd = ", ".join(f"{g}:{pv}" for g,pv in parts.items())
    print(f"{v:>3} {str(d[v]):>8} {str(S[v]):>6} {str(d[v]*S[v]):>8}   {bd}")
print(f"\nROWSUM = sum p_f(v)*S(v) = {sum(pv*S[v] for v,pv in d.items())}")
print(f"check: sum where p_f(v)=1 (private high-mult) vs p_f(v)<1 (shared):")
hi = sum(pv*S[v] for v,pv in d.items() if pv==1)
lo = sum(pv*S[v] for v,pv in d.items() if pv<1)
print(f"  p_f=1 vertices contribute {hi}={float(hi):.3f}")
print(f"  p_f<1 vertices contribute {lo}={float(lo):.3f}")

# THE DILUTION TEST: at every v, is p_f(v) + (S(v)-p_f(v)) bounded so that p_f(v)*S(v) is controlled?
# Test: sum_v p_f(v)*S(v) <= sum_v S(v) - (something)?  Compare to sum_v S(v)=sum ell.
print(f"\nsum_v S(v) = {sum(S)} = sum ell = {sum(ell[g] for g in M)}")
print(f"max_v S(v) = {max(S)} at v={[v for v in range(n) if S[v]==max(S)]}")
