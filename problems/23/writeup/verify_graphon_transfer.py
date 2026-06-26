#!/usr/bin/env python3
"""Verify the exact graphon-transfer identity underpinning the H2-retirement / all-N assembly:

    d_mono(W_G) = 2 beta(G) / N^2   exactly, for every finite triangle-free G,

where W_G is the N-cell {0,1} step graphon of G and beta(G)=e(G)-maxcut(G).

Crux = NO FRACTIONAL GAP: the monochromatic functional
    f(x) = sum_{ij in E} [ x_i x_j + (1-x_i)(1-x_j) ]    on the box [0,1]^N
is MULTILINEAR (affine in each x_i), so its minimum over [0,1]^N is attained at a
vertex x in {0,1}^N = an integer 2-colouring, whose value is exactly beta(G). Hence the
graphon (fractional) min equals the integer min -- the fractional MaxCut buys nothing.

This script checks, on a battery of triangle-free graphs:
  (a) min over {0,1}^N of f  ==  beta(G) = e - maxcut(G)            [definition]
  (b) coordinate-descent global vertex min (many restarts) == beta(G)
  (c) 200k random INTERIOR points x in [0,1]^N all have f(x) >= beta(G)   [no frac gap]
If (c) ever found f < beta, the identity would be false. It never does.
"""
import itertools, numpy as np

def maxcut_bruteforce(N, edges):
    best = 0
    E = np.array(edges)
    for mask in range(1 << N):
        side = np.array([(mask >> i) & 1 for i in range(N)])
        cut = int(sum(1 for (a, b) in edges if side[a] != side[b]))
        if cut > best: best = cut
    return best

def f_mono(x, edges):
    return sum(x[a]*x[b] + (1-x[a])*(1-x[b]) for (a, b) in edges)

def coord_descent_min(N, edges, restarts=60, rng=None):
    adj = [[] for _ in range(N)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    best = None
    for _ in range(restarts):
        x = (rng.random(N) < 0.5).astype(float)
        improved = True
        while improved:
            improved = False
            for i in range(N):
                # f is affine in x_i: coeff c_i = sum_{j in N(i)} (2 x_j - 1)
                c = sum(2*x[j]-1 for j in adj[i])
                xi = 0.0 if c > 0 else 1.0   # minimise
                if xi != x[i]:
                    x[i] = xi; improved = True
        v = f_mono(x, edges)
        if best is None or v < best: best = v
    return best

def random_interior_min(N, edges, samples=200000, rng=None):
    lo = np.inf
    E = edges
    for _ in range(samples):
        x = rng.random(N)
        v = sum(x[a]*x[b] + (1-x[a])*(1-x[b]) for (a, b) in E)
        if v < lo: lo = v
    return lo

# ---- triangle-free test graphs --------------------------------------------
def cycle(n):
    return n, [(i, (i+1) % n) for i in range(n)]

def blowup_C5(t):
    # C5[t]: parts P_i = {t*i .. t*i+t-1}; complete bipartite between consecutive parts
    N = 5*t; E = []
    for i in range(5):
        j = (i+1) % 5
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, j*t+b))
    return N, E

def petersen():
    out = [(i, (i+1) % 5) for i in range(5)]                 # outer C5
    inn = [(5+i, 5+((i+2) % 5)) for i in range(5)]            # inner pentagram
    spokes = [(i, 5+i) for i in range(5)]
    return 10, out+inn+spokes

def grotzsch():
    # Mycielskian of C5: v0..v4 cycle, u0..u4 shadow, w apex (11 vtx, triangle-free, chi=4)
    E = [(i, (i+1) % 5) for i in range(5)]                    # C5 on v
    for i in range(5):                                        # u_i ~ neighbours of v_i
        E.append((5+i, (i-1) % 5)); E.append((5+i, (i+1) % 5))
    for i in range(5):
        E.append((10, 5+i))                                  # apex w=10 ~ all u
    return 11, E

def random_trianglefree(N, p, rng):
    E = set()
    adj = [set() for _ in range(N)]
    order = [(a, b) for a in range(N) for b in range(a+1, N)]
    rng.shuffle(order)
    for a, b in order:
        if rng.random() < p and not (adj[a] & adj[b]):       # adding ab makes no triangle
            E.add((a, b)); adj[a].add(b); adj[b].add(a)
    return N, sorted(E)

def has_triangle(N, edges):
    adj = [set() for _ in range(N)]
    for a, b in edges: adj[a].add(b); adj[b].add(a)
    for a, b in edges:
        if adj[a] & adj[b]: return True
    return False

def main():
    rng = np.random.default_rng(20260626)
    graphs = [("C5", *cycle(5)), ("C5[2]", *blowup_C5(2)), ("C5[3]", *blowup_C5(3)),
              ("Petersen", *petersen()), ("Grotzsch", *grotzsch()), ("C7", *cycle(7))]
    for k in range(5):
        N = int(rng.integers(8, 13)); p = float(rng.uniform(0.25, 0.6))
        n, e = random_trianglefree(N, p, rng)
        graphs.append((f"rand{k}(N={n},m={len(e)})", n, e))

    print(f"{'graph':22} {'N':>3} {'e':>4} {'maxcut':>6} {'beta':>5} "
          f"{'vtxmin':>7} {'frac_inf':>9} {'no-gap?':>8}")
    allok = True
    for name, N, E in graphs:
        assert not has_triangle(N, E), f"{name} not triangle-free!"
        e = len(E)
        mc = maxcut_bruteforce(N, E)
        beta = e - mc
        vtx = coord_descent_min(N, E, restarts=80, rng=rng)
        frac = random_interior_min(N, E, samples=120000, rng=rng)
        ok = (abs(vtx - beta) < 1e-9) and (frac >= beta - 1e-9)
        allok = allok and ok
        print(f"{name:22} {N:3d} {e:4d} {mc:6d} {beta:5.0f} "
              f"{vtx:7.1f} {frac:9.4f} {'OK' if ok else 'FAIL':>8}")
    print()
    print("RESULT:", "ALL PASS -- d_mono(W_G)=2beta/N^2 exact; fractional MaxCut buys nothing."
          if allok else "FAIL -- a fractional point beat the integer beta (identity broken).")

if __name__ == "__main__":
    main()
