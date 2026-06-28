"""Unequal blow-up stress for SAT-ZMU around N=11 near-witnesses.

This is intentionally small: clone one or two vertices of the closest
SAT-ZMU non-vacuous census witnesses and recompute the gamma-min connected-B
maxcut exactly via _h.loads.
"""

import itertools
import sys

from _h import dec, loads
from _codex_sat_zmu import sat_zmu_failures
from _zmu import mu_edges


BASE = [
    "J?AAF@SBrw?",  # closest Q endpoint margin 1/3
    "J?AADBWeay?",
    "J?ABBBWVCu?",
    "J?`D@_w{EB?",
]


def blow_by_weights(n, E, weights):
    offsets = []
    s = 0
    for w in weights:
        offsets.append(s)
        s += w
    out = []
    for a, b in E:
        for ia in range(weights[a]):
            for ib in range(weights[b]):
                out.append((offsets[a] + ia, offsets[b] + ib))
    return s, out


def summarize(info):
    if info is None:
        return "loads=None"
    n = info["n"]
    z = [tuple(sorted(tuple(e))) for e, val in mu_edges(info).items() if val == 0]
    sat = [v for v, t in enumerate(info["T"]) if t == n]
    O = [v for v, t in enumerate(info["T"]) if t > n]
    return f"O={len(O)} sat={len(sat)} zero={len(z)}"


def main():
    checked = 0
    first = None
    for g6 in BASE:
        n, E = dec(g6)
        patterns = []
        # Single doubled vertex.
        for v in range(n):
            w = [1] * n
            w[v] = 2
            patterns.append((f"{g6} double {v}", w))
        # Two doubled vertices for selected near-zero edge neighborhoods.
        for a, b in itertools.combinations(range(n), 2):
            if a > 5 or b > 10:
                continue
            w = [1] * n
            w[a] = 2
            w[b] = 2
            patterns.append((f"{g6} double {a},{b}", w))
        for name, weights in patterns:
            nn, EE = blow_by_weights(n, E, weights)
            if nn > 15:
                continue
            info = loads(nn, EE)
            checked += 1
            fs = sat_zmu_failures(info, name)
            if fs:
                first = fs[0]
                print("FAIL", first)
                print("pattern", name, "weights", weights, summarize(info))
                return 1
        print(f"base {g6}: checked {checked} patterns so far", flush=True)
    print("checked", checked, "FIRST_FAILURE", first)
    return 0


if __name__ == "__main__":
    sys.exit(main())
