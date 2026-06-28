"""Stress the '1-step K-adjacency to O' direct lever on LARGER configs (Mycielskians, blow-ups),
where the K-chain from a saturated v to O could be LONG. If 1-step fails there, the direct lever
is N=11-small artifact and the true statement is only 'Kcomp(v) meets O' (= NO-Q-ONLY hard).
Also report the K-distance from each saturated-with-dead-nb v to O.
Exact Fraction.
"""
from fractions import Fraction as F
from collections import deque
from _h import dec, loads
from _satzmu_conn import struct_for_side, kcomponents

def mycielski(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    N2 = 2*n+1; E2 = list(E)
    for u in range(n):
        for v in adj[u]:
            if v > u: E2.append((u, n+v)); E2.append((v, n+u))
    for u in range(n): E2.append((n+u, 2*n))
    return N2, E2

def buildK(n, cyc):
    K = [[F(0)]*n for _ in range(n)]
    for f, Ps in cyc.items():
        nf = len(Ps)
        cnt = [0]*n
        for P in Ps:
            for v in P: cnt[v] += 1
        pf = [F(cnt[v], nf) for v in range(n)]
        for a in range(n):
            if pf[a] == 0: continue
            for b in range(n):
                if pf[b] == 0: continue
                K[a][b] += pf[a]*pf[b]
    return K

def kdist_to_O(K, n, v, O):
    # BFS on K-graph from v to nearest O
    if v in O: return 0
    seen = {v}; q = deque([(v, 0)])
    while q:
        u, d = q.popleft()
        for w in range(n):
            if w != u and K[u][w] > 0 and w not in seen:
                if w in O: return d+1
                seen.add(w); q.append((w, d+1))
    return -1

def analyze(name, n, E):
    info = loads(n, E)
    if info is None:
        print(f"  {name}: loads None"); return
    adj = info['adj']; side = info['side']
    st = struct_for_side(n, adj, side)
    if st is None:
        print(f"  {name}: struct None"); return
    M, ell, T, mu, cyc = st
    N = n
    O = set(v for v in range(N) if T[v] > N)
    if not O:
        print(f"  {name}: O empty"); return
    comp, find = kcomponents(n, cyc)
    K = buildK(n, cyc)
    rows = []
    for v in range(N):
        if T[v] != N: continue
        deadnb = [z for z in adj[v] if side[z] != side[v] and T[z] == 0]
        if not deadnb: continue
        leak = sum(K[v][o] for o in O)
        kd = kdist_to_O(K, n, v, O)
        rows.append((v, deadnb, float(leak), kd))
    print(f"  {name} (N={N}): |O|={len(O)} sat-with-deadnb cases={len(rows)}")
    for (v, dn, leak, kd) in rows:
        print(f"     v={v} deadnb={dn} K-leak-to-O={leak} K-dist-to-O={kd}")

if __name__ == "__main__":
    print("=== 1-step K-adjacency stress on larger configs ===")
    C5 = (5, [(i, (i+1) % 5) for i in range(5)])
    n1, E1 = mycielski(*C5)
    n2, E2 = mycielski(n1, E1)
    n3, E3 = mycielski(n2, E2)
    for name, (nn, EE) in [("Grotzsch11", (n1, E1)), ("MycGrotzsch23", (n2, E2)), ("Myc3_47", (n3, E3))]:
        analyze(name, nn, EE)
    # overloaded blow-ups
    from _superphi import blow
    for g6, t in [("J???E?pNu\\?", 2), ("I?BD@g]Qo", 2), ("G?bF`w", 3)]:
        nn, EE = blow(g6, t)
        if nn > 30: continue
        analyze(f"{g6}[{t}]", nn, EE)
