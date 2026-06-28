"""Exact probes for layer/prefix ROWSUM mechanisms.

This is diagnostic only.  It tests candidate inequalities of the form:

  layer contribution a_i := sum_{v in I_i(f)} p_f(v) S(v)

against purely combinatorial layer/prefix capacities and cut-defect terms.
Any failure is an exact witness that the candidate cannot be a proof route.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads
from _layerprice import layers_of


def exact_pf(info, f):
    ps = info["cyc"][f]
    nf = len(ps)
    cnt = {}
    for path in ps:
        for v in path:
            cnt[v] = cnt.get(v, 0) + 1
    return {v: F(c, nf) for v, c in cnt.items()}


def all_pf_and_s(info):
    pfs = {}
    s = {v: F(0) for v in range(info["n"])}
    for f in info["M"]:
        pf = exact_pf(info, f)
        pfs[f] = pf
        for v, val in pf.items():
            s[v] += val
    return pfs, s


def prefix_defect(info, vertices):
    s = set(vertices)
    d_b = sum(1 for a, b in info["Bset"] if (a in s) != (b in s))
    d_m = sum(1 for a, b in info["Mset"] if (a in s) != (b in s))
    return d_b - d_m, d_b, d_m


def graph_stats(g6):
    n, e = dec(g6)
    info = loads(n, e)
    if info is None:
        return None
    pfs, s = all_pf_and_s(info)
    rows = []
    for f in info["M"]:
        lay_float, _, h = layers_of(info, f)
        pf = pfs[f]
        layers = []
        prefix = set()
        for i in range(h + 1):
            verts = sorted(lay_float[i])
            prefix.update(verts)
            contrib = sum(pf[v] * s[v] for v in verts)
            cap = F(len(verts))
            pref_contrib = sum(sum(pf[v] * s[v] for v in sorted(lay_float[j])) for j in range(i + 1))
            pref_cap = F(len(prefix))
            defect, d_b, d_m = prefix_defect(info, prefix)
            layers.append(
                dict(
                    i=i,
                    verts=verts,
                    contrib=contrib,
                    cap=cap,
                    pref_contrib=pref_contrib,
                    pref_cap=pref_cap,
                    defect=F(defect),
                    d_b=d_b,
                    d_m=d_m,
                )
            )
        rows.append((f, layers, sum(x["contrib"] for x in layers)))
    return info, rows


def update_worst(worst, key, value, payload):
    if value > worst.get(key, (None,))[0]:
        worst[key] = (value, payload)


WORST_KEYS = [
    "layer_minus_size",
    "prefix_minus_size",
    "prefix_minus_size_defect",
    "row_minus_support",
    "left_prefix_minus_scale",
    "right_prefix_minus_scale",
    "outer_pairs_minus_scale",
    "center_interval_minus_scale",
    "proper_center_interval_minus_scale",
    "proper_interval_minus_scale_defect",
]


COUNT_KEYS = [
    "graphs",
    "rows",
    "layer_fail",
    "prefix_fail",
    "prefix_defect_fail",
    "row_support_fail",
    "left_prefix_scale_fail",
    "right_prefix_scale_fail",
    "outer_pairs_scale_fail",
    "center_interval_scale_fail",
    "proper_center_interval_scale_fail",
    "proper_interval_scale_defect_fail",
]


def empty_worst():
    return {key: (F(-10**9), None) for key in WORST_KEYS}


def empty_counts():
    return {key: 0 for key in COUNT_KEYS}


def graph_probe(g6):
    worst = {
        key: (F(-10**9), None) for key in WORST_KEYS
    }
    counts = empty_counts()
    got = graph_stats(g6)
    if got is None:
        return counts, worst
    info, rows = got
    counts["graphs"] += 1
    for f, layers, rowsum in rows:
        counts["rows"] += 1
        L = len(layers)
        scale = F(info["n"], L)
        support = set()
        for x in layers:
            support.update(x["verts"])
            val = x["contrib"] - x["cap"]
            if val > 0:
                counts["layer_fail"] += 1
            update_worst(worst, "layer_minus_size", val, (g6, info["n"], f, x))

            valp = x["pref_contrib"] - x["pref_cap"]
            if valp > 0:
                counts["prefix_fail"] += 1
            update_worst(worst, "prefix_minus_size", valp, (g6, info["n"], f, x))

            valpd = x["pref_contrib"] - x["pref_cap"] - x["defect"]
            if valpd > 0:
                counts["prefix_defect_fail"] += 1
            update_worst(worst, "prefix_minus_size_defect", valpd, (g6, info["n"], f, x))

        valr = rowsum - F(len(support))
        if valr > 0:
            counts["row_support_fail"] += 1
        update_worst(worst, "row_minus_support", valr, (g6, info["n"], f, rowsum, len(support)))

        left = F(0)
        right = F(0)
        outer = F(0)
        for k in range(L):
            left += layers[k]["contrib"]
            val_left = left - F(k + 1) * scale
            if val_left > 0:
                counts["left_prefix_scale_fail"] += 1
            update_worst(worst, "left_prefix_minus_scale", val_left, (g6, info["n"], f, k, left, scale))

            right += layers[L - 1 - k]["contrib"]
            val_right = right - F(k + 1) * scale
            if val_right > 0:
                counts["right_prefix_scale_fail"] += 1
            update_worst(worst, "right_prefix_minus_scale", val_right, (g6, info["n"], f, k, right, scale))

            if k < L // 2:
                outer += layers[k]["contrib"] + layers[L - 1 - k]["contrib"]
                val_outer = outer - F(2 * (k + 1)) * scale
                if val_outer > 0:
                    counts["outer_pairs_scale_fail"] += 1
                update_worst(
                    worst,
                    "outer_pairs_minus_scale",
                    val_outer,
                    (g6, info["n"], f, k, outer, scale),
                )

        mid = L // 2
        for r in range(1, mid + 1):
            lo, hi = mid - r, mid + r
            val = sum(layers[i]["contrib"] for i in range(lo, hi + 1))
            bound = F(2 * r + 1) * scale
            excess = val - bound
            if excess > 0:
                counts["center_interval_scale_fail"] += 1
                if r < mid:
                    counts["proper_center_interval_scale_fail"] += 1
            update_worst(
                worst,
                "center_interval_minus_scale",
                excess,
                (g6, info["n"], f, r, val, scale),
                    )

        # All proper contiguous intervals of layers.  Compare normalized
        # contribution to the cut defect of the corresponding vertex set.
        # Full interval is excluded because that is the ROWSUM target.
        for lo in range(L):
            interval_vertices = set()
            interval_contrib = F(0)
            for hi in range(lo, L):
                interval_vertices.update(layers[hi]["verts"])
                interval_contrib += layers[hi]["contrib"]
                if lo == 0 and hi == L - 1:
                    continue
                length = hi - lo + 1
                defect, d_b, d_m = prefix_defect(info, interval_vertices)
                excess = interval_contrib - F(length) * scale - F(defect)
                if excess > 0:
                    counts["proper_interval_scale_defect_fail"] += 1
                update_worst(
                    worst,
                    "proper_interval_minus_scale_defect",
                    excess,
                    (g6, info["n"], f, (lo, hi), interval_contrib, scale, defect, d_b, d_m),
                )
            if r < mid:
                update_worst(
                    worst,
                    "proper_center_interval_minus_scale",
                    excess,
                    (g6, info["n"], f, r, val, scale),
                )
    return counts, worst


def merge_into(counts, worst, part):
    pc, pw = part
    for key in COUNT_KEYS:
        counts[key] += pc[key]
    for key in WORST_KEYS:
        if pw[key][0] > worst[key][0]:
            worst[key] = pw[key]


def run(nmax, workers):
    worst = empty_worst()
    counts = empty_counts()
    for nn in range(5, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for part in ex.map(graph_probe, out, chunksize=32):
                    merge_into(counts, worst, part)
        else:
            for g6 in out:
                merge_into(counts, worst, graph_probe(g6))
    print(f"counts={counts}")
    for key, (value, payload) in worst.items():
        print(f"\n{key}: {value} ({float(value):+.6f})")
        print(payload)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    run(args.nmax, args.workers)
