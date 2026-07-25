"""Generate all MAXIMAL triangle-free graphs on n vertices (connected), via nauty geng -t -c + filter.

Maximal triangle-free = triangle-free and every non-adjacent pair has a common neighbour
(so adding any missing edge creates a triangle).

Rationale: for the blow-up functional beta(H) = max_x bip(H[x])/(sum x)^2 we have H subset H'
(same vertex set) => beta(H) <= beta(H'), so only maximal triangle-free templates matter.

Usage:  python gen_maxtf.py 5 12    -> writes maxtf_n.g6 for n=5..12
"""
import subprocess, sys, os

GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")
OUT = os.path.dirname(os.path.abspath(__file__))


def g6_decode(line, n):
    """Return adjacency bitmask list for a graph6 string (n known)."""
    data = [ord(c) - 63 for c in line[1:]] if line[0] == chr(63 + n) else None
    if data is None:
        # header byte is n itself (n<=62 => single byte)
        raise ValueError("unexpected graph6 header: %r" % line[:1])
    adj = [0] * n
    bits = []
    for d in data:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return adj


def is_maximal_tf(adj, n):
    full = (1 << n) - 1
    for u in range(n):
        nonadj = full & ~adj[u] & ~(1 << u)
        v = 0
        m = nonadj
        while m:
            b = m & -m
            v = b.bit_length() - 1
            m ^= b
            if v > u and (adj[u] & adj[v]) == 0:
                return False
    return True


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for n in range(lo, hi + 1):
        p = subprocess.run([GENG, "-t", "-c", "-q", str(n)], capture_output=True, text=True)
        lines = p.stdout.split()
        keep = []
        for L in lines:
            adj = g6_decode(L, n)
            if is_maximal_tf(adj, n):
                keep.append(L)
        with open(os.path.join(OUT, "maxtf_%d.g6" % n), "w") as f:
            f.write("\n".join(keep) + ("\n" if keep else ""))
        print("n=%2d  connected triangle-free=%8d   maximal triangle-free=%6d" % (n, len(lines), len(keep)), flush=True)


if __name__ == "__main__":
    main()
