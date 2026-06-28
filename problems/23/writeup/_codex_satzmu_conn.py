"""Check SAT-ZMU-CONN over all gamma-min connected-B maximum cuts."""

from fractions import Fraction as F
import subprocess

from _h import GENG, dec
from _codex_exist_satzmu import gamma_min_infos
from _zmu import mu_edges


def k_components(info):
    n = info["n"]
    cols = []
    for f in info["M"]:
        paths = info["cyc"][f]
        col = [F(0) for _ in range(n)]
        for P in paths:
            for v in P:
                col[v] += F(1, len(paths))
        cols.append(col)
    seen = [False] * n
    comps = []
    comp_id = [-1] * n
    for s in range(n):
        if seen[s] or info["T"][s] == 0:
            continue
        stack = [s]
        seen[s] = True
        comp = []
        while stack:
            u = stack.pop()
            comp_id[u] = len(comps)
            comp.append(u)
            for v in range(n):
                if seen[v] or info["T"][v] == 0:
                    continue
                kv = sum(col[u] * col[v] for col in cols)
                if kv > 0:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps, comp_id


def violations(info):
    n = info["n"]
    T = info["T"]
    O = [v for v, t in enumerate(T) if t > n]
    if not O:
        return []
    comps, comp_id = k_components(info)
    comp_has_o = [False] * len(comps)
    for o in O:
        if comp_id[o] >= 0:
            comp_has_o[comp_id[o]] = True
    out = []
    mu = mu_edges(info)
    for e, val in mu.items():
        if val != 0:
            continue
        u, v = tuple(e)
        for sat, other in ((u, v), (v, u)):
            if T[sat] == n:
                cid = comp_id[sat]
                if cid < 0 or not comp_has_o[cid]:
                    out.append((sat, other, comps[cid] if cid >= 0 else []))
    return out


def test_graph(name, n, E):
    _, G, infos = gamma_min_infos(n, E)
    worst = 0
    for info in infos:
        bad = violations(info)
        worst = max(worst, len(bad))
        if bad:
            return False, G, len(infos), info, bad
    return True, G, len(infos), None, []


def main():
    for N in range(7, 11):
        tested = 0
        max_mult = 0
        for g6 in subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            ok, G, mult, info, bad = test_graph(g6, n, E)
            max_mult = max(max_mult, mult)
            tested += 1
            if not ok:
                print("FAIL", g6, "Gamma", G, "mult", mult, "bad", bad, "side", info["side"], "T", [str(t) for t in info["T"]])
                return
        print(f"N={N}: tested={tested} max_gamma_min_mult={max_mult} failures=0")

    base = "J?AADBWM_}?"
    n, E = dec(base)
    ok, G, mult, info, bad = test_graph(base + "+leaf8", n + 1, E + [(8, n)])
    print("leaf graph", "ok", ok, "Gamma", G, "mult", mult, "bad", bad)


if __name__ == "__main__":
    main()
