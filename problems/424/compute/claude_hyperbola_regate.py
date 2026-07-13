"""Independent re-gate of Codex C00 full-hyperbola census (my acceptance lane).
r_X(p) = #{(a,b) in G0 x G2 : ab = p}, p <= X. P = sum r, Q = #{p : r>0}, E = sum r^2,
kappa = E*X/P^2. G by the proven truncated closure; divisor pairs via SPF factorization.
Compare at X = 10^3..10^6 against Codex table:
  1e3: P/X=.124    Q/X=.118    E/P=1.09677  kappa=8.84495
  1e4: P/X=.1856   Q/X=.1591   E/P=1.30388  kappa=7.02521
  1e5: P/X=.27214  Q/X=.20391  E/P=1.57485  kappa=5.78692
  1e6: P/X=.370812 Q/X=.239195 E/P=1.93151  kappa=5.20886
"""
import bisect, sys, hashlib

B = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
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

N = B + 1
spf = list(range(N))
i = 2
while i * i < N:
    if spf[i] == i:
        for j in range(i * i, N, i):
            if spf[j] == j: spf[j] = i
    i += 1

def divisors(m):
    ds = [1]
    while m > 1:
        p = spf[m]; e = 0
        while m % p == 0:
            m //= p; e += 1
        ds = [d * p**k for d in ds for k in range(e + 1)]
    return ds

P = Q = E = 0
checkpoints = {10**t for t in range(3, 12) if 10**t <= B}
cps = sorted(checkpoints)
ci = 0
out = []
for p in range(2, B + 1):
    if p % 3 == 0:
        r = 0
        for a in divisors(p):
            if a % 3 == 0:
                b = p // a
                if b % 3 == 2 and a in inset and b in inset:
                    r += 1
        if r:
            P += r; Q += 1; E += r * r
    while ci < len(cps) and p == cps[ci]:
        X = cps[ci]
        out.append((X, P, Q, E, P / X, Q / X, E / P if P else 0, E * X / P**2 if P else 0))
        ci += 1
for X, Pv, Qv, Ev, px, qx, ep, kap in out:
    print(f"X=1e{len(str(X))-1}: P={Pv} Q={Qv} E={Ev}  P/X={px:.6f}  Q/X={qx:.6f}  E/P={ep:.5f}  kappa={kap:.5f}")
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
