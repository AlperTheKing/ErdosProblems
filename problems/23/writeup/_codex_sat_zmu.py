"""Codex diagnostic: saturated endpoint zero-mu test.

Full ZMU ("zero-mu edge has a T=0 endpoint") is false on glued islands.
This checks the weaker lemma needed for Schur cond(1):

  if O is nonempty and mu(e)=0 for a B-edge e=uv, then T(u)<N and T(v)<N.

Equivalently, no zero-mu B-edge is incident to a saturated vertex T=N.
"""

import subprocess
import sys

from _h import dec, GENG, loads
from _zmu import mu_edges
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges


def sat_zmu_failures(info, name):
    if info is None:
        return []
    n = info["n"]
    T = info["T"]
    O = [v for v, t in enumerate(T) if t > n]
    if not O:
        return []
    mu = mu_edges(info)
    failures = []
    for e, val in mu.items():
        if val != 0:
            continue
        u, v = tuple(e)
        if T[u] == n or T[v] == n:
            failures.append(
                {
                    "name": name,
                    "edge": tuple(sorted((u, v))),
                    "T": (T[u], T[v]),
                    "O": tuple(O),
                }
            )
    return failures


def census(n_min=7, n_max=11):
    total_graphs = 0
    total_zero = 0
    failures = []
    for n in range(n_min, n_max + 1):
        graphs = 0
        zero_edges = 0
        fail = 0
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            graphs += 1
            info = loads(*dec(g6))
            if info is None:
                continue
            if any(t > n for t in info["T"]):
                zero_edges += sum(1 for v in mu_edges(info).values() if v == 0)
            fs = sat_zmu_failures(info, g6)
            fail += len(fs)
            failures.extend(fs)
            if failures:
                break
        total_graphs += graphs
        total_zero += zero_edges
        print(f"census N={n}: graphs={graphs} zero_mu_edges={zero_edges} sat_failures={fail}", flush=True)
        if failures:
            break
    print(f"TOTAL graphs={total_graphs} zero_mu_edges={total_zero}")
    print(f"FIRST_FAILURE={failures[0] if failures else None}")
    return failures


def constructions():
    tests = []
    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(island, g15)
    n, E = add_edges((n, E), [(0, 5)])
    tests.append(("C5+MycC7 bridge", loads(n, E)))
    for name, info in tests:
        zero_edges = []
        if info:
            zero_edges = [
                tuple(sorted(tuple(e)))
                for e, val in mu_edges(info).items()
                if val == 0
            ]
        fs = sat_zmu_failures(info, name)
        print(f"construction {name}: zero_mu_edges={zero_edges} sat_failures={len(fs)}")
        for f in fs:
            print("  FAILURE", f)
    return []


if __name__ == "__main__":
    failures = census()
    constructions()
    sys.exit(1 if failures else 0)
