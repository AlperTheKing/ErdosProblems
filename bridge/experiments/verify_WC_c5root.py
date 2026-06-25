#!/usr/bin/env python3
"""
Test GPT Q10's C5-rooted one-cycle sufficient condition (eq 10-12):
  W_C = 2e - (1/2) sum_{i=0}^4 S_{c_i},   S_{c_i} = sum_{u in N(c_i)} d(u),
over induced 5-cycles C=c_0..c_4. Since tau_K <= F_C <= W_C, CF holds for G if
  min over induced C5 of W_C  <=  (N^2/5 - e)/2 = RHS.
Q10's diagnosis: this C5-root bound is TIGHT (=0=RHS) on C5[n] but FAILS on Clebsch
blowups (needs the extra 6th anticomplete root). This script confirms that on:
  - C5[n] (expect min W_C = 0 = RHS, succeeds tight),
  - Clebsch blowup K[t] (in band; expect min W_C > RHS, C5-root FAILS),
  - random band graphs.
"""
import itertools, random
random.seed(5)

def adj_list(N, edges):
    A = [set() for _ in range(N)]
    for u, v in edges:
        A[u].add(v); A[v].add(u)
    return A

def induced_C5_minWC(N, A):
    deg = [len(A[v]) for v in range(N)]
    e = sum(deg) // 2
    # S_v = sum of degrees of neighbors of v
    S = [sum(deg[u] for u in A[v]) for v in range(N)]
    best_sumS = -1
    cnt = 0
    for combo in itertools.combinations(range(N), 5):
        # is induced C5? exactly 5 edges forming a single 5-cycle
        sub = [(a, b) for a, b in itertools.combinations(combo, 2) if b in A[a]]
        if len(sub) != 5:
            continue
        # degree within subset must all be 2 (cycle); and connected
        d = {v: 0 for v in combo}
        for a, b in sub:
            d[a] += 1; d[b] += 1
        if any(d[v] != 2 for v in combo):
            continue
        cnt += 1
        sumS = sum(S[v] for v in combo)
        if sumS > best_sumS:
            best_sumS = sumS
    if best_sumS < 0:
        return None, e, cnt  # no induced C5
    minWC = 2 * e - 0.5 * best_sumS
    return minWC, e, cnt

def c5_blowup(n):
    parts = [list(range(i*n, i*n+n)) for i in range(5)]
    E = []
    for p in range(5):
        for u in parts[p]:
            for v in parts[(p+1)%5]:
                E.append((u, v))
    return 5*n, E

def clebsch_blowup(t):
    # Clebsch = 16 even subsets of [5], A~B iff |A xor B|=4; blow up each vertex to t
    labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
    base = []
    for i in range(16):
        for j in range(i+1, 16):
            if bin(labels[i] ^ labels[j]).count('1') == 4:
                base.append((i, j))
    N = 16 * t
    E = []
    for (a, b) in base:
        for x in range(t):
            for y in range(t):
                E.append((a*t + x, b*t + y))
    return N, E

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
        if elo <= e <= ehi:
            return N, E
    return None

def report(tag, N, E):
    A = adj_list(N, E)
    minWC, e, ncyc = induced_C5_minWC(N, A)
    rhs = (N*N/5 - e)/2
    dens = e/(N*N)
    if minWC is None:
        print(f"  {tag:20s} N={N} e={e} x={dens:.4f} #C5={ncyc}: NO induced C5")
        return
    ok = minWC <= rhs + 1e-9
    print(f"  {tag:20s} N={N} e={e} x={dens:.4f} #inducedC5={ncyc}  min W_C={minWC:.1f}  RHS={rhs:.1f}  C5root_ok={ok}")

def main():
    print("C5-rooted W_C test: min_C W_C <= (N^2/5 - e)/2 ?  (tau_K <= F_C <= W_C)")
    print("Reference C5[n] (expect min W_C = 0 = RHS, tight):")
    for n in (3, 4):
        N, E = c5_blowup(n); report(f"C5[{n}]", N, E)
    print("Clebsch blowup K[t] (in band x->0.156; Q10 says C5-root FAILS here):")
    for t in (1, 2):
        N, E = clebsch_blowup(t); report(f"Clebsch[{t}]", N, E)
    print("Random band graphs:")
    for N in (15, 20):
        C2 = N*(N-1)/2
        lo, hi = int(0.2486*C2)+1, int(0.3197*C2)
        for _ in range(6):
            r = rand_band(N, lo, hi)
            if r: report(f"rand N={N}", r[0], r[1])
    print("DONE")

if __name__ == "__main__":
    main()
