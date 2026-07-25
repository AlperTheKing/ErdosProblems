"""Generate all MAXIMAL graphs of odd girth >= 2k+1 on n vertices (connected).

odd girth is computed exactly on the bipartite double cover:
    oddgirth(G) = min_v dist_{G x K2}( (v,0), (v,1) ).

Usage: python gen_oddg.py <2k+1> <nlo> <nhi>
Writes maxoddg<2k+1>_<n>.g6
"""
import subprocess, sys, os
from collections import deque
from gen_maxtf import g6_decode, GENG

OUT = os.path.dirname(os.path.abspath(__file__))


def odd_girth(adj, n):
    best = 10 ** 9
    for s in range(n):
        dist = [-1] * (2 * n)
        dist[2 * s] = 0
        q = deque([2 * s])
        while q:
            x = q.popleft()
            v, p = divmod(x, 2)
            if dist[x] >= best:      # (shortest odd cycle through s IS dist((s,0),(s,1)))
                break
            m = adj[v]
            while m:
                b = m & -m
                u = b.bit_length() - 1
                m ^= b
                y = 2 * u + (1 - p)
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        if dist[2 * s + 1] >= 0:
            best = min(best, dist[2 * s + 1])
    return best


def main():
    g = int(sys.argv[1]); lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for n in range(lo, hi + 1):
        p = subprocess.run([GENG, "-t", "-c", "-q", str(n)], capture_output=True, text=True)
        lines = p.stdout.split()
        inclass, keep = 0, []
        for L in lines:
            adj = g6_decode(L, n)
            if odd_girth(adj, n) < g:
                continue
            inclass += 1
            ok = True
            for u in range(n):
                if not ok:
                    break
                for v in range(u + 1, n):
                    if (adj[u] >> v) & 1:
                        continue
                    a2 = list(adj); a2[u] |= 1 << v; a2[v] |= 1 << u
                    if odd_girth(a2, n) >= g:
                        ok = False; break
            if ok:
                keep.append(L)
        with open(os.path.join(OUT, "maxoddg%d_%d.g6" % (g, n)), "w") as f:
            f.write("\n".join(keep) + ("\n" if keep else ""))
        print("oddgirth>=%d  n=%2d  triangle-free=%8d  in class=%7d  maximal=%5d"
              % (g, n, len(lines), inclass, len(keep)), flush=True)


if __name__ == "__main__":
    main()
