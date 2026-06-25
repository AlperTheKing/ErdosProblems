#!/usr/bin/env python3
"""
RUNG 1 census: read triangle-free graphs (graph6) from stdin (geng -t), compute
R(G)=tau_K_ub(G)/RHS(G) for in-band graphs, track the MAX R and the worst graphs.
Any R>1 with a confirmed lower bound would be a CF counterexample (local search gives only an
UPPER bound on tau_K, hence only an upper bound on R — so R<=1 here just CONFIRMS CF on the graph;
a high R flags a graph to re-examine with exact tau_K).
Usage: geng -tc N elo:ehi | python census_R.py N
"""
import sys, random
random.seed(5)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2

def decode_graph6(s):
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    A = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                A[i].add(j); A[j].add(i)
            idx += 1
    return n, A

def tau_K_ub(n, A, restarts):
    nbr = [list(A[v]) for v in range(n)]; best = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(n)]; imp = True; sw = 0
        while imp and sw < 40:
            imp = False; sw += 1
            for u in range(n):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(n) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
        if best == 0: break
    return best

def main():
    N = int(sys.argv[1])
    bestR = -1.0; bestg = None; bestinfo = None; cnt = 0; pos = 0
    for line in sys.stdin:
        if not line.strip(): continue
        n, A = decode_graph6(line)
        e = sum(len(A[v]) for v in range(n)) // 2
        x = e / (n * n)
        if not (0.1243 <= x <= 0.16): continue
        cnt += 1
        rhs = (n*n/5.0 - e) / 2.0
        # cheap pass first; escalate restarts if tau_K>0
        tk = tau_K_ub(n, A, 25)
        if tk > 0:
            pos += 1
            tk = min(tk, tau_K_ub(n, A, 150))   # tighten for non-zero cases
        if rhs <= 0: continue
        R = tk / rhs
        if R > bestR:
            bestR = R; bestg = line.strip(); bestinfo = (n, e, x, tk, rhs)
    if bestinfo:
        n, e, x, tk, rhs = bestinfo
        print(f"N={N}: in-band={cnt} (tau_K>0: {pos})  MAX R={bestR:.4f}  "
              f"[n={n} e={e} x={x:.4f} tau_K_ub={tk} RHS={rhs:.1f}]  g6={bestg}", flush=True)
    else:
        print(f"N={N}: in-band={cnt} (no in-band graphs)", flush=True)

if __name__ == "__main__":
    main()
