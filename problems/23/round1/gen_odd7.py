"""Generate all MAXIMAL {C3,C5}-free graphs (odd girth >= 7) on n vertices, connected.

Same monotonicity as before: beta(H) <= beta(H') for H subset H' inside the class, so only
maximal members matter. Used to test the proposed odd-girth hierarchy
        odd girth >= 2k+1  ==>  bip(G) <= N^2/(2k+1)^2 ,
whose k=2 case is Erdos #23 and whose k=3 case predicts bip <= N^2/49 with C7[n] extremal.

Usage: python gen_odd7.py 6 12
"""
import subprocess, sys, os
from gen_maxtf import g6_decode, GENG

OUT = os.path.dirname(os.path.abspath(__file__))


def has_c5(adj, n):
    for a in range(n):
        for b in range(n):
            if b == a or not (adj[a] >> b) & 1:
                continue
            for c in range(n):
                if c in (a, b) or not (adj[b] >> c) & 1:
                    continue
                for d in range(n):
                    if d in (a, b, c) or not (adj[c] >> d) & 1:
                        continue
                    # e adjacent to d and a
                    m = adj[d] & adj[a] & ~(1 << a) & ~(1 << b) & ~(1 << c) & ~(1 << d)
                    if m:
                        return True
    return False


def maximal_in_class(adj, n):
    full = (1 << n) - 1
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1:
                continue
            if adj[u] & adj[v]:      # adding uv makes a triangle
                continue
            adj2 = list(adj)
            adj2[u] |= 1 << v
            adj2[v] |= 1 << u
            if not has_c5(adj2, n):
                return False          # uv could be added: not maximal
    return True


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for n in range(lo, hi + 1):
        p = subprocess.run([GENG, "-t", "-c", "-q", str(n)], capture_output=True, text=True)
        lines = p.stdout.split()
        c5free, keep = 0, []
        for L in lines:
            adj = g6_decode(L, n)
            if has_c5(adj, n):
                continue
            c5free += 1
            if maximal_in_class(adj, n):
                keep.append(L)
        with open(os.path.join(OUT, "maxodd7_%d.g6" % n), "w") as f:
            f.write("\n".join(keep) + ("\n" if keep else ""))
        print("n=%2d  connected tri-free=%8d  odd-girth>=7=%7d  maximal in class=%5d"
              % (n, len(lines), c5free, len(keep)), flush=True)


if __name__ == "__main__":
    main()
