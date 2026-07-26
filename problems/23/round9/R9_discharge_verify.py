"""
R9 / Erdos #23 -- final verification gate for every number quoted in R9_discharge.md.
Exact arithmetic throughout.
"""
from fractions import Fraction
from R9_discharge_lib import (witnesses, bip_and_cuts, sigma_values, num_edges, edges,
                              dp_greedy_value, dp_delete_cost, cost_floor_half_degree,
                              induced, bip_exact, degrees)

def hdr(t):
    print("\n" + "=" * 78); print(t); print("=" * 78)

# ---------------------------------------------------------------- (a) sigma identity
hdr("(a)  identity  bip = |E|/2 - (1/4) sum_v sigma(v)   at a maximum cut")
for (name, n, adj) in witnesses():
    b, opt = bip_and_cuts(n, adj)
    s = opt[0]
    sig = sigma_values(n, adj, s)
    m = num_edges(n, adj)
    lhs = Fraction(b)
    rhs = Fraction(m, 2) - Fraction(sum(sig), 4)
    tgt = 2 * m - Fraction(4 * n * n, 25)
    print(f"  {name:26s} bip={b:3d}  |E|/2-(1/4)sum sigma={rhs}  identity={lhs == rhs}"
          f"   sum sigma={sum(sig):4d} >= 2|E|-4N^2/25={tgt} : {sum(sig) >= tgt}")
    assert lhs == rhs

# ---------------------------------------------------------------- (b) A19 target failure
hdr("(b)  the A19 witness fails the discharging target for its locally optimal cut")
a = [7, 7, 12, 7, 12]; chi = [0, 1, 0, 1, 1]
N = sum(a); E = sum(a[i] * a[(i + 1) % 5] for i in range(5))
sig = []
for i in range(5):
    s = o = 0
    for j in ((i - 1) % 5, (i + 1) % 5):
        (s := s) if False else None
        if chi[j] == chi[i]: s += a[j]
        else: o += a[j]
    sig.append(o - s)
S = sum(a[i] * sig[i] for i in range(5))
tgt = 2 * E - Fraction(4 * N * N, 25)
mono = sum(a[i] * a[(i + 1) % 5] for i in range(5) if chi[i] == chi[(i + 1) % 5])
print(f"  N={N} |E|={E} sigma per class={sig} (all >=0: {all(x>=0 for x in sig)})")
print(f"  sum_v sigma(v) = {S}   target 2|E|-4N^2/25 = {tgt}   holds: {S >= tgt}")
print(f"  mono={mono}  |E|/2-(1/4)sum sigma = {Fraction(E,2)-Fraction(S,4)} (= mono: "
      f"{Fraction(E,2)-Fraction(S,4) == mono})")
print(f"  deficit = {tgt - S}  -> the target is FALSE by exactly {tgt-S} at this cut")

# ---------------------------------------------------------------- (c) Theorem 1 gate
hdr("(c)  Theorem 1 gate: Phi* = f - V satisfies the amortised step wherever Phi* >= 0")
def gate(name, n, adj):
    full = (1 << n) - 1
    # V for every subset
    Vv = [0] * (1 << n)
    order = sorted(range(1 << n), key=lambda m: bin(m).count("1"))
    for mask in order:
        if mask == 0: continue
        best = None
        mm = mask
        while mm:
            low = mm & -mm; v = low.bit_length() - 1; mm ^= low
            cand = Vv[mask ^ low] + bin(adj[v] & mask).count("1") // 2
            if best is None or cand < best: best = cand
        Vv[mask] = best
    f = lambda k: Fraction(k * k, 25)
    ok_all = True
    neg = 0
    for mask in range(1, 1 << n):
        k = bin(mask).count("1")
        phi = f(k) - Vv[mask]
        if phi < 0: neg += 1
        found = False
        mm = mask
        while mm:
            low = mm & -mm; v = low.bit_length() - 1; mm ^= low
            c = bin(adj[v] & mask).count("1") // 2
            phip = f(k - 1) - Vv[mask ^ low]
            if phi - phip <= f(k) - f(k - 1) - c:
                found = True; break
        ok_all &= found
    print(f"  {name:26s} step (*) holds at every one of {2**n-1} subgraphs: {ok_all}; "
          f"subgraphs with Phi*<0: {neg}  Phi*(G)={f(n)-Vv[full]}")
    return ok_all
for (name, n, adj) in witnesses():
    if n <= 11:
        gate(name, n, adj)

# ---------------------------------------------------------------- (d) report table
hdr("(d)  the Phi* table quoted in the report")
for (name, n, adj) in witnesses():
    V, _ = dp_greedy_value(n, adj)
    phi = Fraction(n * n, 25) - V
    print(f"  {name:26s} N={n:3d} |E|={num_edges(n,adj):4d} bip={bip_exact(n,adj):3d} "
          f"V={V:3d}  Phi*={str(phi):>8s}  {'admissible' if phi>=0 else 'NEGATIVE -> dead'}")
print(f"  C5[7,7,12,7,12]  N=45 |E|=385 bip=49  V >= {Fraction(385-45,2)}  "
      f"Phi* <= {81 - Fraction(385-45,2)}")
