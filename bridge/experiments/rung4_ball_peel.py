#!/usr/bin/env python3
"""
RUNG 4 (refined): combined greedy peel using BOTH moves from Q13:
  - delete vertex v: cost Q(deg(v))            [eq 11]
  - delete 2-centre ball S_xy=N[x]∪N[y]: cost Q(m_xy), m_xy=edges leaving S_xy  [Cor 4, Lemma 3]
At each step pick the move minimizing (resulting tau_K_ub, cost); stop when the remaining graph is
Clebsch-homomorphic (tau_K_ub=0). Total cost C is an upper bound on tau_K (chained eq 11/14).
If C <= RHS=(N^2/5-e)/2 then tau_K<=RHS (CF holds on G). Test on Mycielskians + the small census
extremals where plain vertex-deletion was loose.
"""
import random
random.seed(31)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2
def Q(d): return 3*(d//4) + (1 if d % 4 in (2, 3) else 0)

def tau_ub(verts, A, restarts=50):
    vs = list(verts); nbr = {v: [w for w in A[v] if w in verts] for v in vs}; best = None
    for _ in range(restarts):
        lab = {v: random.choice(labels) for v in vs}; imp = True; sw = 0
        while imp and sw < 35:
            imp = False; sw += 1
            for u in vs:
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in vs for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
        if best == 0: break
    return best

def deg(v, verts, A): return len([w for w in A[v] if w in verts])

def ball(x, y, verts, A):
    return ({x, y} | {w for w in A[x] if w in verts} | {w for w in A[y] if w in verts}) & verts

def combined_peel(N, A):
    verts = set(range(N)); total = 0; steps = 0
    while tau_ub(verts, A, 40) > 0 and len(verts) > 1:
        moves = []
        vl = sorted(verts, key=lambda v: -deg(v, verts, A))
        # vertex moves (shortlist of highest degree, the frustrated core)
        for v in vl[:max(5, len(vl)//3)]:
            moves.append(('v', (v,), Q(deg(v, verts, A))))
        # ball moves: pairs among shortlist; m_xy = edges leaving the ball
        short = vl[:min(8, len(vl))]
        for i in range(len(short)):
            for j in range(i+1, len(short)):
                x, y = short[i], short[j]
                S = ball(x, y, verts, A)
                if len(S) >= len(verts): continue        # would delete everything
                m = sum(1 for u in S for w in A[u] if w in verts and w not in S)
                moves.append(('b', tuple(S), Q(m)))
        # evaluate: pick move minimizing (new tau_K_ub, cost)
        best = None
        for kind, S, c in moves:
            new = verts - set(S)
            if not new: continue
            t2 = tau_ub(new, A, 25)
            key = (t2, c)
            if best is None or key < best[0]:
                best = (key, kind, S, c)
        if best is None: break
        _, kind, S, c = best
        verts -= set(S); total += c; steps += 1
        if steps > 4*N: break
    return total, steps

def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def C5(): return 5, [(i, (i+1) % 5) for i in range(5)]
def myc(N, E):
    z = 2*N; E2 = list(E)
    for u, v in E: E2.append((u+N, v)); E2.append((u, v+N))
    for v in range(N): E2.append((z, v+N))
    return 2*N+1, E2
def decode_g6(s):
    s = s.strip(); data = [ord(c) - 63 for c in s]; n = data[0]; bits = []
    for d in data[1:]:
        for k in range(5, -1, -1): bits.append((d >> k) & 1)
    A = [set() for _ in range(n)]; idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]: A[i].add(j); A[j].add(i)
            idx += 1
    return n, A

def report(tag, N, A):
    e = sum(len(A[v]) for v in range(N)) // 2
    rhs = (N*N/5.0 - e) / 2.0
    C, steps = combined_peel(N, A)
    tk = tau_ub(set(range(N)), A, 120)
    ok = C <= rhs + 1e-9
    print(f"  {tag:22s} N={N:3d} e={e:4d} tau_K_ub={tk:3d} RHS={rhs:6.1f} peel_cost={C:4d} ({steps} steps) "
          f"peel<=RHS={int(ok)}  (peel/RHS={C/rhs:.2f})", flush=True)
    return ok

if __name__ == "__main__":
    print("RUNG 4 refined: combined vertex+2-centre-ball peel cost vs RHS (peel<=RHS => CF on G):")
    n, e = C5(); n2, e2 = myc(n, e); n3, e3 = myc(n2, e2); n4, e4 = myc(n3, e3)
    report("M(M(C5)) 23v", n3, adj(n3, e3))
    report("M^3(C5) 47v", n4, adj(n4, e4))
    for tag, g6 in [("N11 worst R", "J?`@F_{Ubo?"), ("N12 worst R", "K?AA@Bw^DsBw")]:
        nn, AA = decode_g6(g6); report(tag, nn, AA)
    print("DONE")
