"""Codex diagnostic: filtered K-island restriction checks.

For the active Schur condition (1) / NO-Q-ONLY route.

Filtered island C:
  - O={v:T[v]>N} is nonempty,
  - C is a full K-component disjoint from O,
  - C carries at least one bad edge, i.e. some geodesic support is contained in C.

Checks:
  RMAX: inherited cut restricted to G[C] is a max cut of G[C].
  BEND: every B-boundary edge from such C has the outside endpoint T=0.

The second check follows from ZMU if accepted, but this script tests it directly
from the computed loads and components.
"""

from fractions import Fraction as F
import itertools
import subprocess
import sys

from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges


def cut_inside(adj, side, C):
    Cs = set(C)
    return sum(
        1
        for u in C
        for v in adj[u]
        if v in Cs and v > u and side[u] != side[v]
    )


def induced_edges(adj, C):
    C = list(C)
    idx = {v: i for i, v in enumerate(C)}
    edges = []
    for i, u in enumerate(C):
        for v in adj[u]:
            j = idx.get(v)
            if j is not None and i < j:
                edges.append((i, j))
    return C, edges


def maxcut_induced(adj, C):
    C, edges = induced_edges(adj, C)
    m = len(C)
    best = -1
    # All tested components are small in the intended diagnostic gate.
    # Keep this exact and simple.
    for mask in range(1 << m):
        val = sum(1 for i, j in edges if ((mask >> i) & 1) != ((mask >> j) & 1))
        if val > best:
            best = val
    return best


def filtered_components(info):
    if info is None:
        return []
    B = build(info)
    n = B["n"]
    O = B["O"]
    if not O:
        return []
    out = []
    for C in components(B["K"], n):
        Cs = set(C)
        if Cs & O:
            continue
        carries = any(B["supp"][fi] and B["supp"][fi] <= Cs for fi in range(len(B["M"])))
        if carries:
            out.append((B, C))
    return out


def check_info(info, name):
    failures = []
    n = info["n"] if info else None
    for B, C in filtered_components(info):
        Cs = set(C)
        current = cut_inside(info["adj"], info["side"], C)
        induced = maxcut_induced(info["adj"], C)
        d = analyze_one(B, C)
        boundary = [
            (a, b)
            for a, b in info["Bset"]
            if (a in Cs) ^ (b in Cs)
        ]
        bad_boundary = []
        for a, b in boundary:
            inside = a if a in Cs else b
            outside = b if a in Cs else a
            if B["T"][outside] != 0:
                bad_boundary.append((a, b, B["T"][inside], B["T"][outside]))
        if current != induced:
            failures.append(
                {
                    "name": name,
                    "n": n,
                    "C": tuple(C),
                    "O": tuple(sorted(B["O"])),
                    "current_cut": current,
                    "induced_maxcut": induced,
                    "GammaC": d["GammaC"],
                    "dB": d["dB"],
                    "bad_boundary": tuple(bad_boundary),
                }
            )
        elif bad_boundary:
            print(
                f"boundary_nonzero_mu_warning {name}: C={tuple(C)} "
                f"bad_boundary={tuple(bad_boundary)}",
                flush=True,
            )
    return failures


def census(n_min=5, n_max=11):
    total_graphs = 0
    total_islands = 0
    failures = []
    for n in range(n_min, n_max + 1):
        graphs = 0
        islands = 0
        fail = 0
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            graphs += 1
            info = loads(*dec(g6))
            comps = filtered_components(info)
            islands += len(comps)
            fs = check_info(info, g6)
            fail += len(fs)
            failures.extend(fs)
            if failures:
                break
        total_graphs += graphs
        total_islands += islands
        print(f"census N={n}: graphs={graphs} filtered_islands={islands} failures={fail}", flush=True)
        if failures:
            break
    print(f"TOTAL graphs={total_graphs} filtered_islands={total_islands}")
    print(f"FIRST_FAILURE={failures[0] if failures else None}")
    return failures


def constructions():
    tests = []
    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(island, g15)
    n, E = add_edges((n, E), [(0, 5)])
    tests.append(("C5+MycC7 bridge", loads(n, E)))
    # Variants copied from _bdef_bigisland.py.
    c5_2_n = 10
    c5_2_E = []
    for i in range(5):
        for a in range(2):
            for b in range(2):
                c5_2_E.append((i * 2 + a, ((i + 1) % 5) * 2 + b))
    gn, gE = dec("G?`F`w")
    n0, E0 = union_disjoint((c5_2_n, c5_2_E), (gn, gE))
    for bridges in [
        [(0, 10)],
        [(0, 11)],
        [(0, 12)],
        [(0, 10), (5, 12)],
        [(0, 10), (2, 11), (4, 13)],
        [(0, 10), (1, 11), (2, 12), (3, 13)],
    ]:
        n, E = add_edges((n0, E0), bridges)
        tests.append((f"C5[2]+G?`F`w br{bridges}", loads(n, E)))
    for name, info in tests:
        fs = check_info(info, name)
        comps = filtered_components(info)
        print(f"construction {name}: filtered_islands={len(comps)} failures={len(fs)}")
        for B, C in comps:
            d = analyze_one(B, C)
            print(
                f"  C={C} current={cut_inside(info['adj'], info['side'], C)} "
                f"max={maxcut_induced(info['adj'], C)} GammaC={d['GammaC']} dB={d['dB']}"
            )
        for f in fs:
            print("  FAILURE", f)
    return []


if __name__ == "__main__":
    failures = census()
    constructions()
    sys.exit(1 if failures else 0)
