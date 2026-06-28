"""Try to create ZERO-SAT-ADJ violations by adding a cut leaf.

If H has a vertex v with T_H(v)=|H|+1, adding a new leaf adjacent to v should
raise N by one and would naively make v saturated while the leaf has T=0.
This script checks whether the gamma-min connected-B maxcut of the new graph
keeps that naive structure or changes.
"""

import subprocess
import sys

from _h import GENG, dec, loads


def add_leaf(n, E, v):
    return n + 1, E + [(v, n)]


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    attempts = 0
    kept_sat = 0
    violations = []
    changed = []
    for N in range(7, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            cand = [v for v, t in enumerate(info["T"]) if t == n + 1]
            if not cand:
                continue
            for v in cand:
                attempts += 1
                n2, E2 = add_leaf(n, E, v)
                info2 = loads(n2, E2)
                if info2 is None:
                    changed.append((g6, v, "no_loads"))
                    continue
                T2 = info2["T"]
                O2 = [x for x, t in enumerate(T2) if t > n2]
                leaf_is_t0 = T2[n] == 0
                edge_is_B = (v, n) in info2["Bset"] or (n, v) in info2["Bset"]
                if T2[v] == n2 and leaf_is_t0 and edge_is_B:
                    kept_sat += 1
                    if O2:
                        violations.append((g6, v, n2, O2, [str(t) for t in T2]))
                        print("VIOLATION", violations[-1])
                        return
                else:
                    changed.append((g6, v, [str(info["T"][v]), str(T2[v]), str(T2[n])], edge_is_B, O2))
    print(f"attempts={attempts} kept_sat_leaf={kept_sat} violations={len(violations)} changed={len(changed)}")
    print("first_changed", changed[:10])


if __name__ == "__main__":
    main()
