"""Exact probe for an effective-neighbor layer envelope.

For a fixed bad edge f and its shortest-geodesic layers, let p_i be the
probability distribution on layer i induced by a uniform shortest f-geodesic.
Let

    a_i   = sum_v p_i(v) S(v)
    eff_i = 1 / sum_v p_i(v)^2.

The complete odd-cycle blow-up proof has a_i = m/n_i and eff_i = n_i, and the
minimum-product inequalities imply

    a_i <= (eff_{i-1}+eff_{i+1})/2

for internal layers, with endpoint analogues a_0 <= eff_1 and
a_{L-1} <= eff_{L-2}.  If true generally, summing would imply ROWSUM because
sum eff_i <= sum |I_i| <= N.

This script is diagnostic only; any failure kills this proof route.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads


def layer_distributions(info, f):
    paths = info["cyc"][f]
    nf = len(paths)
    L = info["ell"][f]
    layers = [dict() for _ in range(L)]
    for path in paths:
        if len(path) != L:
            raise AssertionError((f, path, L))
        for i, v in enumerate(path):
            layers[i][v] = layers[i].get(v, F(0)) + F(1, nf)
    return layers


def all_S(info):
    S = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        for layer in layer_distributions(info, f):
            for v, p in layer.items():
                S[v] += p
    return S


def graph_probe(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return {
            "graphs": 0,
            "rows": 0,
            "checks": 0,
            "fails": 0,
            "worst": (F(-10**9), None),
        }
    S = all_S(info)
    out = {"graphs": 1, "rows": 0, "checks": 0, "fails": 0, "worst": (F(-10**9), None)}
    for f in info["M"]:
        out["rows"] += 1
        layers = layer_distributions(info, f)
        L = len(layers)
        a = [sum(p * S[v] for v, p in layer.items()) for layer in layers]
        eff = []
        for layer in layers:
            q = sum(p * p for p in layer.values())
            eff.append(F(1, 1) / q)
        for i in range(L):
            if L == 1:
                continue
            if i == 0:
                bound = eff[1]
            elif i == L - 1:
                bound = eff[L - 2]
            else:
                bound = (eff[i - 1] + eff[i + 1]) / 2
            excess = a[i] - bound
            out["checks"] += 1
            if excess > 0:
                out["fails"] += 1
            if excess > out["worst"][0]:
                out["worst"] = (
                    excess,
                    {
                        "g6": g6,
                        "n": n,
                        "f": f,
                        "i": i,
                        "L": L,
                        "a": a[i],
                        "bound": bound,
                        "eff": tuple(eff),
                        "avec": tuple(a),
                        "layer": tuple(sorted(layers[i])),
                    },
                )
    return out


def merge(a, b):
    for key in ["graphs", "rows", "checks", "fails"]:
        a[key] += b[key]
    if b["worst"][0] > a["worst"][0]:
        a["worst"] = b["worst"]


def run(nmax, workers):
    acc = {"graphs": 0, "rows": 0, "checks": 0, "fails": 0, "worst": (F(-10**9), None)}
    for n in range(5, nmax + 1):
        graphs = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        before = dict(acc)
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for part in ex.map(graph_probe, graphs, chunksize=32):
                    merge(acc, part)
        else:
            for g6 in graphs:
                merge(acc, graph_probe(g6))
        print(
            f"N={n} graphs+{acc['graphs']-before['graphs']} rows={acc['rows']} "
            f"fails={acc['fails']} worst={float(acc['worst'][0]):+.6f}",
            flush=True,
        )
    print("RESULT", {k: acc[k] for k in ["graphs", "rows", "checks", "fails"]})
    print("WORST", acc["worst"][0], float(acc["worst"][0]))
    print(acc["worst"][1])


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.nmax, args.workers)
