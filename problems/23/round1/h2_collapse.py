"""H2: structural validation of the h<=15 result.

Claim tested: for every base H in the enumeration, every optimal weight vector w found
by h2_opt.exe with 25*bip/N^2 = 1 has the following shape -- the support of w carries a
homomorphism phi to C5 whose five fibres have EQUAL total weight N/5, and all edges of
H[supp w] run between cyclically consecutive fibres.  In that case
    bip(H[w]) = (N/5)^2 = N^2/25
exactly, i.e. the optimum is a C5 blow-up in disguise and nothing else.

Reads the HIT lines produced by h2_opt.exe.
"""
import sys, re
from h2_lib import g6_decode


def hom_to_C5_support(n, adj, supp):
    """All homomorphisms supp -> C5 (as colourings), found by backtracking."""
    verts = sorted(supp)
    col = {}
    out = []

    def rec(k):
        if k == len(verts):
            out.append(dict(col))
            return True
        v = verts[k]
        rng = range(5) if k > 0 else [0]
        for c in rng:
            ok = True
            for u in verts[:k]:
                if (adj[v] >> u) & 1 and (col[u] - c) % 5 not in (1, 4):
                    ok = False
                    break
            if ok:
                col[v] = c
                if rec(k + 1):
                    return True
                del col[v]
        return False

    return out[0] if rec(0) else None


def check(g6, w):
    n, adj = g6_decode(g6)
    N = sum(w)
    supp = [i for i in range(n) if w[i] > 0]
    phi = hom_to_C5_support(n, adj, supp)
    if phi is None:
        return "NO_C5_HOM_ON_SUPPORT"
    tot = [0] * 5
    for v in supp:
        tot[phi[v]] += w[v]
    if N % 5 == 0 and all(t == N // 5 for t in tot):
        return "C5_BALANCED"
    return "C5_HOM_UNBALANCED " + str(tot)


if __name__ == "__main__":
    pat = re.compile(r"g6=(\S+).*?N=(\d+) bip=(\d+) 25bip/N2=([0-9.]+) w=\[([0-9,]+)\]")
    counts = {}
    bad = []
    total = 0
    for fn in sys.argv[1:]:
        for line in open(fn):
            m = pat.search(line)
            if not m:
                continue
            g6, N, bip, ratio, ws = m.groups()
            if float(ratio) < 0.9999999:
                continue
            w = [int(x) for x in ws.split(",")]
            total += 1
            r = check(g6, w)
            key = r.split()[0]
            counts[key] = counts.get(key, 0) + 1
            if key != "C5_BALANCED":
                bad.append((g6, N, bip, w, r))
    print("optimal (ratio=1) weight vectors examined:", total)
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    for b in bad[:20]:
        print("  NOT a balanced C5 collapse:", b)
