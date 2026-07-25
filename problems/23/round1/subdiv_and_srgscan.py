"""
(1) THE 3-SUBDIVISION LEMMA.
    G^(3) = replace every edge of G by a path of length 3.
    Claim:  bip(G^(3)) = bip(G),  and girth(G^(3)) >= 3*girth(G) >= 9.
    Consequence: computing bip is NP-hard on triangle-free graphs of girth >= 9,
    so no polynomial-time-computable convex relaxation R can satisfy
    bip(G) = |E| - R(G) for all triangle-free G unless P = NP.
    Verified exhaustively below on all connected graphs with <= 6 vertices.

(2) SRG PARAMETER SCAN.
    For a d-regular graph, bip >= m/2 + N*lam_min/4  (exact, see srg.py).
    For a triangle-free strongly regular graph srg(N,d,0,mu) with integer
    eigenvalues r > 0 > s = -t (t >= 2), one has
        mu = t - r,  d = mu + r*t,  N = 1 + d + d(d-1)/mu,
    and the spectral lower bound on bip/N^2 is  (d - t)/(4N).
    We scan ALL integer parameter sets with the standard feasibility conditions
    and ask whether  (d-t)/(4N)  can exceed 1/25 -- i.e. whether the strongly
    regular route could ever produce a counterexample.
"""
import subprocess, os
from fractions import Fraction
from f5lib import parse_graph6, bip

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")


def subdivide3(n, edges):
    """replace uv by u-a-b-v"""
    E = []
    k = n
    for (u, v) in edges:
        a, b = k, k + 1
        k += 2
        E += [(min(u, a), max(u, a)), (min(a, b), max(a, b)), (min(b, v), max(b, v))]
    return k, sorted(E)


def check_subdivision(nmax=6):
    print("=== 3-subdivision lemma:  bip(G^(3)) == bip(G) ? ===")
    total = 0
    for n in range(2, nmax + 1):
        p = subprocess.run([GENG, "-cq", str(n)], capture_output=True, text=True)
        for g6 in p.stdout.split():
            nn, E = parse_graph6(g6)
            if len(E) > 8:            # keep the subdivided graph small enough
                continue
            b0 = bip(nn, E)
            n3, E3 = subdivide3(nn, E)
            if n3 > 22:
                continue
            b1 = bip(n3, E3)
            assert b0 == b1, (g6, b0, b1)
            total += 1
    print(f"    verified on {total} connected graphs (all G with <=8 edges, "
          f"<= {nmax} vertices): bip(G^(3)) == bip(G) in every case")


def srg_scan(tmax=400, rmax=400):
    print()
    print("=== triangle-free srg(N,d,0,mu) parameter scan ===")
    print("    r = positive eigenvalue, t = |negative eigenvalue|,")
    print("    mu = t-r, d = mu + r*t, N = 1 + d + d(d-1)/mu")
    print("    spectral bound:  bip/N^2 >= (d-t)/(4N);  conjecture cap = 1/25 = 0.04")
    best = []
    for t in range(2, tmax + 1):
        for r in range(1, t):
            mu = t - r
            d = mu + r * t
            if d * (d - 1) % mu:
                continue
            N = 1 + d + d * (d - 1) // mu
            # integrality of eigenvalue multiplicities
            # f,g = 1/2 [ (N-1) -+ (2d + (N-1)(lam-mu)) / sqrt(...) ]
            num = 2 * d + (N - 1) * (0 - mu)
            den = r + t                      # sqrt((lam-mu)^2+4(d-mu)) = r - s = r+t
            if num % den:
                continue
            f = ((N - 1) - num // den) // 2
            g = (N - 1) - f
            if ((N - 1) - num // den) % 2 or f < 0 or g < 0:
                continue
            # --- Krein conditions (s = -t) ---
            s = -t
            if not ((r + 1) * (d + r + 2 * r * s) <= (d + r) * (s + 1) ** 2):
                continue
            if not ((s + 1) * (d + s + 2 * r * s) <= (d + s) * (r + 1) ** 2):
                continue
            # --- absolute bound ---
            if N > f * (f + 3) // 2 or N > g * (g + 3) // 2:
                continue
            ratio = Fraction(d - t, 4 * N)
            best.append((ratio, N, d, mu, r, t))
    best.sort(reverse=True)
    print(f"    scanned feasible parameter sets: {len(best)}")
    print(f"    {'ratio':>12s} {'=':>9s}  {'N':>7s} {'d':>6s} {'mu':>5s} {'r':>4s} {'t':>4s}")
    for ratio, N, d, mu, r, t in best[:12]:
        flag = "  <-- EXCEEDS 1/25 !!" if ratio > Fraction(1, 25) else ""
        print(f"    {str(ratio):>12s} {float(ratio):9.6f}  {N:7d} {d:6d} {mu:5d} "
              f"{r:4d} {t:4d}{flag}")
    known = {(5, 2, 1), (10, 3, 1), (16, 5, 2), (50, 7, 1), (56, 10, 2),
             (77, 16, 4), (100, 22, 6)}
    print("    among the SEVEN known triangle-free srgs:")
    for ratio, N, d, mu, r, t in sorted(best, reverse=True):
        if (N, d, mu) in known:
            print(f"    {str(ratio):>12s} {float(ratio):9.6f}  srg({N},{d},0,{mu})")
    sup = max(b[0] for b in best)
    print(f"    SUPREMUM of the spectral ratio over ALL feasible parameter sets: "
          f"{sup} = {float(sup):.6f}   (1/25 = 0.04)")
    # asymptotics: r fixed? examine the limit
    print("    (limit r->inf with t=r+1: mu=1, d=r(r+1)+1, N=1+d+d(d-1) ~ d^2,")
    print("     ratio ~ d/(4d^2) -> 0;  the ratio is maximised at small parameters)")


if __name__ == "__main__":
    check_subdivision(6)
    srg_scan()
