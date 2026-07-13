"""R-C L9: first exact multiplicative-energy probe for G0 x G2 reservoirs.
G computed to B=10^6 by the proven truncated closure (G0 lemma). Reservoirs:
U = G0 cap (Y/2, Y]  (G0 = G cap 3N),  V = G2 cap (Z/2, Z]  (G2 = G cap {2 mod 3}).
E(U,V) = #{(u,v,u',v') in UxVxUxV : uv = u'v'}  (exact, via product multiplicities).
kappa = E * X / (|U|^2 |V|^2) with X = YZ (all products in (YZ/4, YZ]).
Gate (48)-(51): kappa bounded along scales => d(G0*G2) >= alpha/kappa > 0 => d(G) >= d(G0)+d(G0*G2-1).
Ford predicts balanced shapes have kappa -> infinity (like a power of log); the question
is whether UNBALANCED shapes flatten kappa. If |U||V| > CAP, thin the LARGER side by
every k-th element (a subset is a legitimate reservoir; thinning is REPORTED).
Exact integer E; numpy only for sort/run-length counting.
"""
import bisect, sys, hashlib
import numpy as np

B = 10**6
pool = [2, 3]; inset = {2, 3}; work = [2, 3]
while work:
    x = work.pop()
    lim = (B + 1) // x
    idx = bisect.bisect_right(pool, lim)
    for y in pool[:idx]:
        if y == x: continue
        z = x * y - 1
        if z <= B and z not in inset:
            inset.add(z); bisect.insort(pool, z); work.append(z)

arr = np.array(pool, dtype=np.int64)
g0 = arr[arr % 3 == 0]
g2 = arr[arr % 3 == 2]
print(f"B={B} |G|={len(arr)} |G0|={len(g0)} |G2|={len(g2)}")

CAP = 4 * 10**8

def window(a, hi):
    lo = hi // 2
    return a[(a > lo) & (a <= hi)]

def energy(U, V):
    P = (U[:, None] * V[None, :]).ravel()
    P.sort()
    # run-length: E = sum multiplicity^2
    diff = np.flatnonzero(np.diff(P)) + 1
    starts = np.concatenate(([0], diff, [len(P)]))
    cnt = np.diff(starts)
    return int((cnt.astype(np.int64) ** 2).sum()), len(cnt)

print(f"{'Y':>8} {'Z':>8} {'|U|':>7} {'|V|':>7} {'thin':>5} {'E':>14} {'|U*V|':>12} {'kappa':>10}")
for (Y, Z) in [(10**3, 10**3), (10**4, 10**4), (10**5, 10**5), (10**6, 10**6),
               (10**3, 10**4), (10**3, 10**5), (10**3, 10**6),
               (10**4, 10**5), (10**4, 10**6), (10**5, 10**6)]:
    U = window(g0, Y); V = window(g2, Z)
    if len(U) == 0 or len(V) == 0:
        print(f"{Y:>8} {Z:>8} empty window"); continue
    thin = 1
    while len(U) * (len(V) // thin + 1) > CAP:
        thin += 1
    Vt = V[::thin]
    E, distinct = energy(U, Vt)
    X = Y * Z
    kappa = E * X / (len(U) ** 2 * len(Vt) ** 2)
    print(f"{Y:>8} {Z:>8} {len(U):>7} {len(Vt):>7} {thin:>5} {E:>14} {distinct:>12} {kappa:>10.3f}")

print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
