"""ROOT-AGENT GATE on the two Round-1 claims that change the campaign.

CLAIM A (blow-up identity).  bip(H[t]) = t^2 * bip(H) for every graph H and every integer t >= 1,
where H[t] is the balanced blow-up (each vertex replaced by t independent copies).

CLAIM B (consequence).  a(N) <= N^2/25 for every N <= 40, including the 32 non-multiples of five,
given the published a(5m) = m^2 for m <= 40.  Reason: a(5N) >= 25*a(N) by Claim A with t = 5, and
a(5N) = N^2 for N <= 40, so 25*a(N) <= N^2.

CLAIM C (no asymptotic slack).  If a(N0) > N0^2/25 for some N0, then a(t*N0) > (t*N0)^2/25 for
every t, so "the conjecture for all N >= some threshold" is equivalent to "the conjecture for all
N".  Any threshold route is vacuous.

This script verifies Claim A by brute force (exact maximum cut over all 2^(n-1) bipartitions of
the blow-up) on every small graph it can afford, and then checks the arithmetic of B and C against
the exact values a(4..14) established by my own censuses.
"""

from itertools import combinations
import subprocess

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def maxcut(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best = cut
    return best


def bip_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return len(edges) - maxcut(n, adj)


def blowup(n, edges, t):
    N = n * t
    E = []
    for u, v in edges:
        for i in range(t):
            for j in range(t):
                a, b = u * t + i, v * t + j
                E.append((min(a, b), max(a, b)))
    return N, E


def g6_decode(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for byte in b[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


print("=" * 70)
print("CLAIM A: bip(H[t]) = t^2 * bip(H)   -- brute force, exact")
print("=" * 70)
fails = 0
tested = 0
# all graphs (not only triangle-free -- the claim is general) on 4..6 vertices, t = 2;
# and on 4..5 vertices, t = 3
for n, t in ((4, 2), (5, 2), (6, 2), (4, 3), (5, 3)):
    if n * t > 20:
        continue
    out = subprocess.run([GENG, "-q", str(n)], capture_output=True, text=True).stdout
    for line in out.split():
        if not line:
            continue
        nn, edges = g6_decode(line)
        b = bip_from_edges(nn, edges)
        N, E = blowup(nn, edges, t)
        B = bip_from_edges(N, E)
        tested += 1
        if B != t * t * b:
            fails += 1
            print(f"   MISMATCH n={nn} t={t} g6={line}: bip(H)={b}, bip(H[t])={B}, t^2*bip={t*t*b}")
    print(f"   n={n}, t={t}: done")
print(f"   tested {tested} (graph, t) pairs, mismatches: {fails}")
print(f"   CLAIM A: {'CONFIRMED' if fails == 0 else 'REFUTED'}")

print()
print("=" * 70)
print("CLAIM B arithmetic: a(N) <= a(5N)/25 = N^2/25 for N <= 40")
print("=" * 70)
a_exact = {4: 0, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2, 10: 4, 11: 4, 12: 5, 13: 6, 14: 7, 15: 9}
print("   consistency of the deduction with my own exact censuses:")
bad = 0
for N, a in sorted(a_exact.items()):
    lim = N * N / 25.0
    ok = a * 25 <= N * N
    if not ok:
        bad += 1
    print(f"     N={N:2d}  a(N)={a:2d}  a(5N)=N^2={N*N:4d}  bound a(5N)/25={lim:6.2f}  "
          f"a(N) <= bound: {ok}")
print(f"   violations: {bad}")
print()
print("   the deduction, for the orders my hunt was targeting:")
for N in (16, 17, 18, 19, 21, 22, 23, 24, 26):
    print(f"     N={N:2d}: a({N}) <= a({5*N})/25 = {N}^2/25 = {N*N/25:6.2f}  "
          f"=> a({N}) <= {(N*N)//25}   [needs published a({5*N})={N*N}, i.e. {N} <= 40: {N <= 40}]")

print()
print("=" * 70)
print("CLAIM C: a violation at N0 propagates to every multiple t*N0")
print("=" * 70)
print("   If a(N0) >= N0^2/25 + d with d > 0 then a(t*N0) >= t^2*a(N0) >= (t*N0)^2/25 + t^2*d.")
print("   So violations occur at arbitrarily large orders, and a threshold statement")
print("   'conjecture holds for all N >= N0' implies it for ALL N. Threshold routes are vacuous.")
print()
print("   Corollary actually used: a violation at N <= 40 would force a violation at 5N <= 200,")
print("   a multiple of five, contradicting the published a(5m) = m^2 for m <= 40.")
print("   Hence the conjecture is PROVED for every N <= 40, not only the multiples of five.")
print("   The smallest orders where the published data leaves the question OPEN are therefore")
print("   N > 40 with 5 not dividing N and 5N > 200.")
