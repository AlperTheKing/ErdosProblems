#!/usr/bin/env python3
"""
Stress-test GPT Q15's reduced target: d_5(G) <= (N^2/5 - e)/4 for band triangle-free G.
d_5 = min over psi:V->Z5 of #{uv in E: (psi(u)-psi(v)) mod 5 not in {1,4}}  (C5-frustration).
Local search gives an UPPER bound on d_5, so d_5_ub <= target CONFIRMS the target on that graph.
Reads graph6 (geng -t) from stdin. Reports max d_5_ub/target over in-band graphs + the worst graph.
Usage: geng -tc N elo:ehi | python census_d5.py N
"""
import sys, random
random.seed(5)

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

def d5_ub(n, A, restarts):
    nbr = [list(A[v]) for v in range(n)]
    def good(a, b): return (a - b) % 5 in (1, 4)
    best = None
    for _ in range(restarts):
        c = [random.randrange(5) for _ in range(n)]; imp = True; sw = 0
        while imp and sw < 30:
            imp = False; sw += 1
            for u in range(n):
                bc, bl = None, c[u]
                for col in range(5):
                    bad = sum(0 if good(col, c[w]) else 1 for w in nbr[u])
                    if bc is None or bad < bc: bc, bl = bad, col
                if bl != c[u]: c[u] = bl; imp = True
        tot = sum(0 if good(c[u], c[w]) else 1 for u in range(n) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
        if best == 0: break
    return best

def main():
    N = int(sys.argv[1]); bestR = -1.0; bestg = None; info = None; cnt = 0; pos = 0
    for line in sys.stdin:
        if not line.strip(): continue
        n, A = decode_g6(line)
        e = sum(len(A[v]) for v in range(n)) // 2
        x = e / (n*n)
        if not (0.1243 <= x <= 0.16): continue
        cnt += 1
        target = (n*n/5.0 - e) / 4.0
        if target <= 0: continue
        d = d5_ub(n, A, 20)
        if d > 0:
            pos += 1
            d = min(d, d5_ub(n, A, 120))
        R = d / target
        if R > bestR: bestR = R; bestg = line.strip(); info = (n, e, x, d, target)
    if info:
        n, e, x, d, target = info
        print(f"N={N}: in-band={cnt} (d5>0: {pos})  MAX d5/target={bestR:.4f}  "
              f"[n={n} e={e} x={x:.4f} d5_ub={d} target={target:.2f}]  g6={bestg}  "
              f"{'<<< TARGET FAILS (d5>target)!' if bestR>1+1e-9 else 'target holds'}", flush=True)
    else:
        print(f"N={N}: in-band={cnt} (none with positive target)", flush=True)

if __name__ == "__main__":
    main()
