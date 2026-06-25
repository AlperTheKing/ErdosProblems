#!/usr/bin/env python3
"""
Lambda5(F) finite H2-test  (GPT Q9 section 6, Step-2 implementation).

For a triangle-free base F on r vertices, the balanced blow-up F[k] (5n vertices,
n=rk/5) tests the peeling lemma H2.  Deleting a 5-set = a multiplicity vector
s in Z>=0^r, sum s_i = 5.  For an OPTIMAL cut sigma of F (minimizing monochromatic
edges = beta(F)), let B_sigma be its bad-edge (monochromatic) graph; define
  L_sigma(s) = sum_i s_i * deg_{B_sigma}(i),
  R_sigma(s) = sum_{ij in E(B_sigma)} s_i s_j.
For large k:  beta(F[k]) - beta(F[k]-S) = max_{sigma in O(F)} [ k*L_sigma(s) - R_sigma(s) ].
H2 needs a 5-set with drop <= 2n-1 = 2rk/5 - 1.  Define
  Lambda5(F) = min_{s, sum=5} max_{sigma in O(F)} L_sigma(s).
Then (leading order in k):
  Lambda5(F) > 2r/5  ==> large blow-ups F[k] FALSIFY H2   (H2 IS FALSE)
  Lambda5(F) < 2r/5  ==> H2 holds for large blow-ups
  Lambda5(F) = 2r/5  ==> boundary; H2 holds on blow-ups iff there is an s attaining
                         max L = 2r/5 with R_sigma(s) >= 1 on EVERY optimal cut sigma
                         that attains L_sigma(s) = 2r/5  (the exact -1).
This script enumerates ALL triangle-free F on r vertices (geng -t) and flags any
F with Lambda5(F) > 2r/5 (an H2 counterexample base) or a failing boundary.
"""
import subprocess, itertools, sys

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


def graph6_to_adj(line):
    data = line.strip()
    if not data:
        return None
    b = [ord(c) - 63 for c in data]
    n = b[0]
    bits = []
    for x in b[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj


def optimal_cuts(n, adj):
    """Return beta(F) and list of bad-edge graphs (each as a list of (i,j) mono edges)
    over all MAX cuts (minimizing mono edges). Fix vertex 0 to side 0."""
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]
    best = None
    cuts = []
    for mask in range(1 << (n - 1)):
        side = mask << 1  # vertex 0 on side 0
        mono = [(i, j) for (i, j) in edges if ((side >> i) & 1) == ((side >> j) & 1)]
        m = len(mono)
        if best is None or m < best:
            best = m
            cuts = [mono]
        elif m == best:
            cuts.append(mono)
    return best, cuts


def lambda5(n, adj):
    beta, cuts = optimal_cuts(n, adj)
    # precompute per-cut degree vectors
    degs = []
    for mono in cuts:
        d = [0] * n
        for (i, j) in mono:
            d[i] += 1
            d[j] += 1
        degs.append((d, mono))
    target = 2 * n / 5.0
    best_lam = None
    best_s = None
    # enumerate s in Z>=0^n with sum 5 : place 5 indistinguishable units into n bins
    # (multisets of size 5 from n fibres)
    for combo in itertools.combinations_with_replacement(range(n), 5):
        s = [0] * n
        for c in combo:
            s[c] += 1
        # max over optimal cuts of L_sigma(s)
        mx = 0
        for (d, mono) in degs:
            L = sum(s[i] * d[i] for i in range(n))
            if L > mx:
                mx = L
        if best_lam is None or mx < best_lam:
            best_lam = mx
            best_s = s
    # boundary R check: if best_lam == target (integer), does best_s give R>=1 on every
    # optimal cut attaining L = target? (need to also confirm best_s is the minimizer)
    boundary_ok = None
    if abs(best_lam - target) < 1e-9:
        # find an s with max L = target and R>=1 on all tight cuts
        boundary_ok = False
        for combo in itertools.combinations_with_replacement(range(n), 5):
            s = [0] * n
            for c in combo:
                s[c] += 1
            tight = []
            mx = 0
            for (d, mono) in degs:
                L = sum(s[i] * d[i] for i in range(n))
                if L > mx:
                    mx = L
            if abs(mx - target) > 1e-9:
                continue
            ok = True
            for (d, mono) in degs:
                L = sum(s[i] * d[i] for i in range(n))
                if abs(L - target) < 1e-9:  # tight optimal cut
                    R = sum(s[i] * s[j] for (i, j) in mono)
                    if R < 1:
                        ok = False
                        break
            if ok:
                boundary_ok = True
                break
    return beta, best_lam, target, best_s, boundary_ok, len(cuts)


def main():
    rvals = [int(x) for x in sys.argv[1:]] or (5, 6, 7, 8)
    for r in rvals:
        try:
            out = subprocess.run([GENG, "-t", str(r)], capture_output=True, text=True, timeout=600)
        except Exception as e:
            print(f"r={r}: geng failed {e}")
            continue
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        tot = 0
        viol = []      # Lambda5 > 2r/5  => H2 FALSE on blow-ups
        boundary_fail = []
        lam_hist = {}
        for line in lines:
            res = graph6_to_adj(line)
            if res is None:
                continue
            n, adj = res
            # triangle-free guaranteed by -t
            beta, lam, target, s, bok, ncuts = lambda5(n, adj)
            tot += 1
            lam_hist[lam] = lam_hist.get(lam, 0) + 1
            if lam > target + 1e-9:
                viol.append((line, beta, lam, target, s, ncuts))
            elif abs(lam - target) < 1e-9 and bok is False:
                boundary_fail.append((line, beta, lam, target, s, ncuts))
        print(f"r={r} (2r/5={2*r/5:.2f}): tested {tot} triangle-free graphs; "
              f"Lambda5 hist={dict(sorted(lam_hist.items()))}")
        print(f"   #(Lambda5 > 2r/5  -> H2 FALSE): {len(viol)}")
        for v in viol[:10]:
            print("   *** H2-FALSIFYING BASE:", v)
        print(f"   #(boundary Lambda5=2r/5 with R-condition FAIL): {len(boundary_fail)}")
        for b in boundary_fail[:10]:
            print("   boundary-fail:", b)
        sys.stdout.flush()
    print("DONE")


if __name__ == "__main__":
    main()
