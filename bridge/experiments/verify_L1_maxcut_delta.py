#!/usr/bin/env python3
"""
Verify Claim L1: triangle-free G  =>  MaxCut(G) >= e/2 + Delta/2
   equivalently  beta(G) = e - MaxCut <= floor((e - Delta)/2).

Exhaustive over ALL triangle-free graphs on n=5..9 vertices via nauty geng -t.
Exact MaxCut by 2^(n-1) brute force (fix vertex 0 in side L).

Also reports the tightest cases (where beta == floor((e-Delta)/2)) and the
corollary thresholds for the n=30 base case.

TRY-TO-BREAK-IT artifact for the bridge.
"""
import subprocess, sys, os

GENG = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "nauty2_8_9", "geng.exe")

def decode_graph6(s):
    """Return (n, adj) where adj is list of int bitmasks, from a graph6 string."""
    data = [ord(c) - 63 for c in s.strip()]
    n = data[0]
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0]*n
    idx = 0
    # graph6 column-major order: for j in 1..n-1, for i in 0..j-1
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i] |= (1 << j)
                adj[j] |= (1 << i)
            idx += 1
    return n, adj

def max_cut(n, adj):
    """Exact MaxCut by brute force; fix vertex 0 in side 0."""
    best = 0
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if (adj[i] >> j) & 1:
                edges.append((i, j))
    for mask in range(1 << (n-1)):
        side = mask << 1  # vertex 0 -> side 0
        c = 0
        for (i, j) in edges:
            if ((side >> i) ^ (side >> j)) & 1:
                c += 1
        if c > best:
            best = c
    return best, len(edges)

def main():
    worst = []
    tight_examples = []
    total = 0
    for n in range(5, 10):
        # -t : triangle-free
        try:
            out = subprocess.run([GENG, "-t", str(n)], capture_output=True, text=True, timeout=1800)
        except Exception as ex:
            print(f"n={n}: geng failed: {ex}")
            continue
        cnt = 0
        viol = 0
        tight_n = 0
        for line in out.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            nn, adj = decode_graph6(line)
            mc, e = max_cut(nn, adj)
            beta = e - mc
            delta = max((bin(adj[v]).count("1") for v in range(nn)), default=0)
            bound = (e - delta) // 2
            cnt += 1
            total += 1
            if beta > bound:
                viol += 1
                if len(worst) < 20:
                    worst.append((line, nn, e, delta, beta, bound))
            elif beta == bound:
                tight_n += 1
                if len(tight_examples) < 5:
                    tight_examples.append((line, nn, e, delta, beta))
        print(f"n={n}: {cnt} triangle-free graphs, violations(beta>floor((e-Delta)/2))={viol}, tight={tight_n}")
    print(f"\nTOTAL triangle-free graphs checked (n=5..9): {total}")
    if worst:
        print("VIOLATIONS FOUND (LEMMA FALSE):")
        for w in worst:
            print("  ", w)
        sys.exit(1)
    else:
        print("NO VIOLATIONS — L1 holds on all triangle-free graphs n=5..9.")
    print("Sample tight cases (beta == floor((e-Delta)/2)):")
    for t in tight_examples:
        print("  g6=%s n=%d e=%d Delta=%d beta=%d" % t)

if __name__ == "__main__":
    main()
