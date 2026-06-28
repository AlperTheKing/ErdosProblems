"""Existential SAT-ZMU over all gamma-min connected-B maximum cuts."""

from fractions import Fraction as F
import subprocess

from _h import GENG, dec, maxcut_all, Bconn, bdist_restr, geos, loads
from _zmu import mu_edges


def info_for_side(n, E, side):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    Bset = set((min(u, v), max(u, v)) for u in range(n) for v in adj[u] if side[u] != side[v])
    ell = {}
    cyc = {}
    T = [F(0) for _ in range(n)]
    G = 0
    for f in M:
        Ps = geos(adj, side, f[0], f[1])
        if not Ps:
            return None
        ell[f] = len(Ps[0])
        G += ell[f] ** 2
        sh = F(ell[f], len(Ps))
        cyc[f] = Ps
        for P in Ps:
            for v in P:
                T[v] += sh
    return dict(n=n, adj=adj, side=side, M=M, ell=ell, Bset=Bset, T=T, cyc=cyc, G=G)


def gamma_min_infos(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    cuts = maxcut_all(n, adj)
    best_cut = max(sum(1 for u, v in edges if s[u] != s[v]) for s in cuts)
    bestG = None
    infos = []
    for side in cuts:
        if sum(1 for u, v in edges if side[u] != side[v]) != best_cut:
            continue
        if not Bconn(n, adj, side):
            continue
        info = info_for_side(n, E, side)
        if info is None:
            continue
        if bestG is None or info["G"] < bestG:
            bestG = info["G"]
            infos = [info]
        elif info["G"] == bestG:
            infos.append(info)
    return best_cut, bestG, infos


def violation_count(info):
    N = info["n"]
    T = info["T"]
    O = [v for v, t in enumerate(T) if t > N]
    mu = mu_edges(info)
    count = 0
    bad = []
    for e, val in mu.items():
        if val != 0:
            continue
        u, v = tuple(e)
        for a, b in ((u, v), (v, u)):
            if T[a] == N and (O or T[b] != 0):
                count += 1
                bad.append((a, b))
    return count, bad, O


def test_graph(name, n, E):
    _, G, infos = gamma_min_infos(n, E)
    vals = []
    for info in infos:
        c, bad, O = violation_count(info)
        vals.append((c, bad, O, info["side"], [str(t) for t in info["T"]]))
    vals.sort(key=lambda x: x[0])
    return G, len(infos), vals[0], vals[-1]


def main():
    for N in range(7, 11):
        total = 0
        failures = []
        max_mult = 0
        for g6 in subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            if loads(n, E) is None:
                continue
            G, mult, best, worst = test_graph(g6, n, E)
            max_mult = max(max_mult, mult)
            total += 1
            if best[0] > 0:
                failures.append((g6, G, mult, best))
                break
        print(f"N={N}: tested={total} max_gamma_min_mult={max_mult} existential_failures={len(failures)}")
        if failures:
            print("FIRST", failures[0])
            return

    base = "J?AADBWM_}?"
    n, E = dec(base)
    n2, E2 = n + 1, E + [(8, n)]
    G, mult, best, worst = test_graph(base + "+leaf8", n2, E2)
    print("leaf graph:", "Gamma", G, "gamma_min_mult", mult)
    print("  best", best)
    print("  worst", worst)


if __name__ == "__main__":
    main()
