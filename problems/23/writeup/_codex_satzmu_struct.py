"""Structure dump for saturated zero-mu cut-edge incidences.

This is a diagnostic for the SAT-ZMU-CLASS proof route. It enumerates small
census graphs, finds cut edges uv with mu(uv)=0 and T(u)=N, and prints the
local exact structure around u and v.
"""

from collections import Counter, defaultdict, deque
from fractions import Fraction as F
import subprocess

from _h import GENG, dec, loads
from _zmu import mu_edges


def fmt(x):
    if isinstance(x, F):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    return str(x)


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def components_after_removing_bedge(info, removed_edge):
    n = info["n"]
    B = set(info["Bset"])
    B.discard(edge_key(*removed_edge))
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        q = deque([s])
        seen[s] = True
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in info["adj"][u]:
                if edge_key(u, v) in B and not seen[v]:
                    seen[v] = True
                    q.append(v)
        comps.append(sorted(comp))
    return sorted(comps, key=lambda c: (len(c), c))


def incidences(info):
    n = info["n"]
    T = info["T"]
    mu = mu_edges(info)
    out = []
    for e, val in mu.items():
        if val != 0:
            continue
        u, v = tuple(e)
        if T[u] == n:
            out.append((u, v))
        if T[v] == n:
            out.append((v, u))
    return out


def summarize(name, limit=6):
    n, E = dec(name)
    info = loads(n, E)
    if info is None:
        return []
    incs = incidences(info)
    if not incs:
        return []
    mu = mu_edges(info)
    Mdeg = [0] * n
    Bdeg = [0] * n
    for u, v in info["M"]:
        Mdeg[u] += 1
        Mdeg[v] += 1
    for u, v in info["Bset"]:
        Bdeg[u] += 1
        Bdeg[v] += 1
    O = [v for v, t in enumerate(info["T"]) if t > n]
    rows = []
    for sat, other in incs[:limit]:
        other_mu = {
            edge_key(other, x): fmt(mu[frozenset((other, x))])
            for x in info["adj"][other]
            if edge_key(other, x) in info["Bset"]
        }
        sat_mu = {
            edge_key(sat, x): fmt(mu[frozenset((sat, x))])
            for x in info["adj"][sat]
            if edge_key(sat, x) in info["Bset"]
        }
        comps = components_after_removing_bedge(info, (sat, other))
        rows.append(
            {
                "g6": name,
                "N": n,
                "O": O,
                "M": info["M"],
                "side": info["side"],
                "Gamma": info["G"],
                "sat": sat,
                "other": other,
                "T_sat": fmt(info["T"][sat]),
                "T_other": fmt(info["T"][other]),
                "Bdeg": (Bdeg[sat], Bdeg[other]),
                "Mdeg": (Mdeg[sat], Mdeg[other]),
                "sat_mu": sat_mu,
                "other_mu": other_mu,
                "B_components_without_edge": comps,
            }
        )
    return rows


def main():
    totals = Counter()
    examples = []
    graph_count = 0
    for N in (10, 11):
        ngraphs = 0
        ninc = 0
        nwith = 0
        bdeg_pairs = Counter()
        other_bdeg = Counter()
        for g6 in subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split():
            info = loads(*dec(g6))
            if info is None:
                continue
            incs = incidences(info)
            if not incs:
                continue
            nwith += 1
            ninc += len(incs)
            Bdeg = [0] * N
            for u, v in info["Bset"]:
                Bdeg[u] += 1
                Bdeg[v] += 1
            for sat, other in incs:
                bdeg_pairs[(Bdeg[sat], Bdeg[other])] += 1
                other_bdeg[Bdeg[other]] += 1
            if len(examples) < 10:
                examples.extend(summarize(g6, limit=3))
            ngraphs += 1
        graph_count += ngraphs
        totals[N] = ninc
        print(f"N={N}: graphs_with_incidences={nwith} incidences={ninc}")
        print(f"  Bdeg(sat,other): {dict(sorted(bdeg_pairs.items()))}")
        print(f"  Bdeg(other): {dict(sorted(other_bdeg.items()))}")
    print(f"TOTAL incidence counts: {dict(totals)}")
    print("\nEXAMPLES")
    for row in examples:
        print(row)


if __name__ == "__main__":
    main()
