#!/usr/bin/env python3
"""
Test GPT Q10's ACTUAL C5-rooted rounding functional F_C (eq 5-7), computed robustly
as the MIN over the 10 explicit deterministic maps phi_{eps,j} (NOT the loose degree
form W_C, which was already shown insufficient). Q10: tau_K <= F_C <= W_C, and
phi_{eps,j} for eps in {+2,-2}=↦{2,3}, j in Z5:
  v in R   -> label [5]\{j}        (size 4, even)
  v in S_i -> label {i, i+eps}     (size 2)
  v in D_i -> label {i-1, i+1}     (size 2)
F_C(C) = min over the 10 (eps,j) of total edge cost; F_C(G) = min over induced C5 C.
cost(a,b) = (4 - |a xor b|)/2 in {0,1,2}.
CF (C5-root only) would hold for G if min_C F_C(G) <= (N^2/5 - e)/2 = RHS.
Q10 says the C5-root ALONE fails on Clebsch blowups (need the 6th root); test whether
it suffices on OTHER band graphs (where W_C failed but F_C is tighter).
"""
import itertools, random
random.seed(9)

def cost(a, b):
    return (4 - bin(a ^ b).count('1')) // 2

def adj_list(N, edges):
    A = [set() for _ in range(N)]
    for u, v in edges:
        A[u].add(v); A[v].add(u)
    return A

def label_R(j):     return 31 ^ (1 << j)                       # [5]\{j}
def label_S(i, eps): return (1 << i) | (1 << ((i + eps) % 5))   # {i, i+eps}
def label_D(i):     return (1 << ((i - 1) % 5)) | (1 << ((i + 1) % 5))

def FC_of_cycle(N, A, edges_list, deg, C):
    # C = (c0..c4) induced 5-cycle. classify every vertex
    cpos = {C[i]: i for i in range(5)}
    typ = [None] * N  # ('R',), ('S',i), ('D',i)
    for v in range(N):
        P = sorted(i for i in range(5) if C[i] in A[v])
        if len(P) == 0:
            typ[v] = ('R',)
        elif len(P) == 1:
            typ[v] = ('S', P[0])
        elif len(P) == 2:
            a, b = P
            # must be {i-1,i+1} for some i (consecutive-2 apart on C5)
            if (b - a) % 5 == 2:
                typ[v] = ('D', (a + 1) % 5)
            elif (a - b) % 5 == 2:
                typ[v] = ('D', (b + 1) % 5)
            else:
                typ[v] = ('X',)  # adjacent pair => would be triangle; shouldn't happen
        else:
            typ[v] = ('X',)
    best = None
    for eps in (2, 3):
        for j in range(5):
            lab = [0] * N
            for v in range(N):
                t = typ[v]
                if t[0] == 'R': lab[v] = label_R(j)
                elif t[0] == 'S': lab[v] = label_S(t[1], eps)
                elif t[0] == 'D': lab[v] = label_D(t[1])
                else: lab[v] = label_R(j)  # fallback for 'X' (rare)
            tot = 0
            for (u, w) in edges_list:
                tot += cost(lab[u], lab[w])
            if best is None or tot < best:
                best = tot
    return best

def min_FC(N, A, edges_list):
    deg = [len(A[v]) for v in range(N)]
    best = None; ncyc = 0
    for combo in itertools.combinations(range(N), 5):
        sub = [(a, b) for a, b in itertools.combinations(combo, 2) if b in A[a]]
        if len(sub) != 5: continue
        d = {v: 0 for v in combo}
        for a, b in sub: d[a] += 1; d[b] += 1
        if any(d[v] != 2 for v in combo): continue
        # order into a cycle
        start = combo[0]; cyc = [start]; prev = None; cur = start
        for _ in range(4):
            nxts = [w for w in A[cur] if w in d and w != prev]
            nxt = nxts[0] if nxts[0] != start or len(nxts) == 1 else nxts[1]
            # pick neighbor in cycle not equal prev
            cand = [w for w in A[cur] if w in d and w != prev]
            nxt = cand[0]
            cyc.append(nxt); prev, cur = cur, nxt
        ncyc += 1
        fc = FC_of_cycle(N, A, edges_list, deg, tuple(cyc))
        if best is None or fc < best: best = fc
    return best, ncyc

def c5_blowup(n):
    parts = [list(range(i*n, i*n+n)) for i in range(5)]
    E = [(u, v) for p in range(5) for u in parts[p] for v in parts[(p+1)%5]]
    return 5*n, E

def clebsch_blowup(t):
    labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
    base = [(i, j) for i in range(16) for j in range(i+1, 16)
            if bin(labels[i] ^ labels[j]).count('1') == 4]
    E = [(a*t+x, b*t+y) for (a, b) in base for x in range(t) for y in range(t)]
    return 16*t, E

def rand_band(N, elo, ehi):
    for _ in range(200):
        A = [set() for _ in range(N)]
        pairs = [(u, v) for u in range(N) for v in range(u+1, N)]
        random.shuffle(pairs); e = 0; E = []
        tgt = random.randint(elo, ehi)
        for u, v in pairs:
            if e >= tgt: break
            if A[u] & A[v]: continue
            A[u].add(v); A[v].add(u); E.append((u, v)); e += 1
        if elo <= e <= ehi: return N, E
    return None

def report(tag, N, E):
    A = adj_list(N, E)
    el = [(min(u, v), max(u, v)) for u, v in set((min(a,b),max(a,b)) for a,b in E)]
    e = len(el)
    mfc, ncyc = min_FC(N, A, el)
    rhs = (N*N/5 - e)/2
    if mfc is None:
        print(f"  {tag:18s} N={N} e={e} x={e/(N*N):.4f}: NO induced C5"); return
    print(f"  {tag:18s} N={N} e={e} x={e/(N*N):.4f} #C5={ncyc}  min F_C={mfc}  RHS={rhs:.1f}  C5root_ok={mfc<=rhs+1e-9}")

def main():
    print("ACTUAL F_C (10-map) C5-root test: min_C F_C <= (N^2/5-e)/2 ?  (tau_K<=F_C<=W_C)")
    for n in (3, 4): N,E=c5_blowup(n); report(f"C5[{n}]", N, E)
    for t in (1, 2): N,E=clebsch_blowup(t); report(f"Clebsch[{t}]", N, E)
    for N in (15, 20):
        C2=N*(N-1)/2; lo,hi=int(0.2486*C2)+1,int(0.3197*C2)
        for _ in range(6):
            r=rand_band(N,lo,hi)
            if r: report(f"rand N={N}", r[0], r[1])
    print("DONE")

if __name__ == "__main__":
    main()
