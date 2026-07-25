"""Exact certification of bip(G) for the H1 Cayley candidates.

Reads lines produced by claude_h1_cayley.exe --dump (fields:  ... <graph6> ...), decodes the
graph6, re-checks triangle-freeness from scratch, and computes maxcut EXACTLY:
  * N <= 26  -> exhaustive enumeration of all 2^(N-1) bipartitions (pure integer);
  * N >  26  -> OR-Tools CP-SAT solved to proven optimality (status OPTIMAL required);
                for N <= 26 the CP-SAT value is additionally cross-checked against exhaustion.

Usage:  python claude_h1_verify.py FILE [--workers W] [--limit L] [--maxtime S]
"""
import sys, argparse
from itertools import combinations


def decode_g6(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert 0 <= n < 63, "only graph6 with N<63 handled here"
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0] * n
    i = 0
    for j in range(1, n):
        for k in range(j):
            if bits[i]:
                adj[k] |= 1 << j
                adj[j] |= 1 << k
            i += 1
    return n, adj


def is_triangle_free(n, adj):
    for u in range(n):
        au = adj[u]
        v = au
        while v:
            b = v & -v
            vi = b.bit_length() - 1
            v ^= b
            if vi > u and (adj[vi] & au):
                return False
    return True


def maxcut_exhaustive(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]
            S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a
            S |= 1 << v
        if cut > best:
            best = cut
    return best


def maxcut_cpsat(n, adj, workers=32, maxtime=0.0):
    from ortools.sat.python import cp_model
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(n)]
    m.Add(x[0] == 0)
    y = []
    for (u, v) in edges:
        t = m.NewBoolVar("")
        m.Add(t <= x[u] + x[v])
        m.Add(t <= 2 - x[u] - x[v])
        y.append(t)
    m.Maximize(sum(y))
    s = cp_model.CpSolver()
    s.parameters.num_search_workers = workers
    if maxtime:
        s.parameters.max_time_in_seconds = maxtime
    st = s.Solve(m)
    return (st == cp_model.OPTIMAL), int(s.ObjectiveValue()), len(edges)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--maxtime", type=float, default=0.0)
    ap.add_argument("--only-best", action="store_true")
    a = ap.parse_args()

    rows = []
    for line in open(a.file):
        p = line.split()
        if not p or p[0] not in ("CAND", "BEST"):
            continue
        if a.only_best and p[0] != "BEST":
            continue
        g6 = [t for t in p if t and ord(t[0]) - 63 == int(p[1])][-1]
        rows.append((p[0], int(p[1]), p[2], g6, line.strip()))
    # dedupe by graph6
    seen = set()
    uniq = []
    for r in rows:
        if r[3] in seen:
            continue
        seen.add(r[3])
        uniq.append(r)
    uniq.sort(key=lambda r: -r[1])
    if a.limit:
        uniq = uniq[:a.limit]

    best = {}
    for kind, N, gname, g6, raw in uniq:
        n, adj = decode_g6(g6)
        assert n == N, (n, N)
        tf = is_triangle_free(n, adj)
        E = sum(bin(x).count("1") for x in adj) // 2
        if n <= 26:
            mc = maxcut_exhaustive(n, adj)
            proven, how = True, "exhaustive 2^%d" % (n - 1)
            ok, mc2, _ = maxcut_cpsat(n, adj, a.workers, a.maxtime)
            if ok and mc2 != mc:
                print("!! CP-SAT/exhaustive DISAGREE", g6, mc, mc2)
            elif ok:
                how += " + CP-SAT OPTIMAL (agree)"
        else:
            proven, mc, _ = maxcut_cpsat(n, adj, a.workers, a.maxtime)
            how = "CP-SAT OPTIMAL" if proven else "CP-SAT NOT PROVEN (upper bd on bip only)"
        bip = E - mc
        ratio = bip / (n * n)
        viol = 25 * bip > n * n
        print("N=%-4d %-14s |E|=%-5d maxcut=%-5d bip=%-5d 25bip=%-6d N^2=%-6d ratio=%.6f TF=%s [%s]%s"
              % (n, gname, E, mc, bip, 25 * bip, n * n, ratio, tf, how,
                 "  *** VIOLATION ***" if (viol and tf and proven) else ""))
        print("      g6=%s" % g6)
        if tf and proven and (n not in best or bip > best[n][0]):
            best[n] = (bip, g6, gname, E, mc)
    print("\n--- certified best per order ---")
    for n in sorted(best):
        bip, g6, gname, E, mc = best[n]
        print("N=%-4d bip=%-5d ratio=%.6f  (N^2/25=%.2f)  group=%s  |E|=%d maxcut=%d"
              % (n, bip, bip / (n * n), n * n / 25.0, gname, E, mc))


if __name__ == "__main__":
    main()
