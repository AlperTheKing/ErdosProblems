"""phi(N) = max { bip(G) : G triangle-free and homomorphic to C5, |V|=N }
         = max { min_i t_i t_{i+1} : t_i >= 0 integers, sum t_i = N }   (Lemma D)

and comparison with the exact values a(N) computed by f1_exact_a.exe.
Also: C5-colourability test for the exact extremal witnesses.
"""
from itertools import product
from f1_bip import g6_decode, bip_bruteforce

WIT = {5: "DUW", 6: "ECxo", 7: "F?bro", 8: "G?rF`w", 9: "H?BEFo}",
       10: "I?rFf_{N?", 11: "J?BEFo}}@{?", 12: "K?ABBBwerwBw",
       13: "L??FFB_~?~^_Fw", 14: "M?AE@bH{AYN_LgBs?"}
AEXACT = {5: 1, 6: 1, 7: 1, 8: 2, 9: 2, 10: 4, 11: 4, 12: 5, 13: 6, 14: 7}


def phi(N):
    best, arg = -1, None
    for a in range(N + 1):
        for b in range(N + 1 - a):
            for c in range(N + 1 - a - b):
                for d in range(N + 1 - a - b - c):
                    e = N - a - b - c - d
                    t = (a, b, c, d, e)
                    v = min(t[i] * t[(i + 1) % 5] for i in range(5))
                    if v > best:
                        best, arg = v, t
    return best, arg


def c5_colourable(n, E):
    """Brute-force test for a homomorphism G -> C5 (5^n, n small)."""
    adjC5 = [[(i - j) % 5 in (1, 4) for j in range(5)] for i in range(5)]
    col = [-1] * n
    adj = [[] for _ in range(n)]
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)

    def rec(v):
        if v == n:
            return True
        lo = 5 if v else 1          # fix colour of vertex 0 (C5 is vertex-transitive)
        for c in range(lo):
            ok = True
            for w in adj[v]:
                if w < v and not adjC5[c][col[w]]:
                    ok = False
                    break
            if ok:
                col[v] = c
                if rec(v + 1):
                    return True
                col[v] = -1
        return False
    return rec(0)


print(" N   a(N)  floor(N^2/25)  phi(N)=max C5-blowup   argmax t          a>phi?  witness C5-col?")
for N in range(5, 30):
    p, t = phi(N)
    a = AEXACT.get(N)
    n5, r = divmod(N, 5)
    pred = n5 * n5 + (n5 if r >= 3 else 0)
    assert p == pred, (N, p, pred)
    extra = ""
    if a is not None:
        nn, E = g6_decode(WIT[N])
        assert bip_bruteforce(nn, E) == a
        extra = f"   {'YES' if a > p else 'no ':3s}    {c5_colourable(nn, E)}"
    print(f"{N:3d}  {str(a):>4s}   {N*N//25:6d}      {p:6d}   {str(t):20s}{extra}")
print()
print("phi(5n+r) = n^2 for r=0,1,2 and n^2+n for r=3,4   (checked N<=29)")
