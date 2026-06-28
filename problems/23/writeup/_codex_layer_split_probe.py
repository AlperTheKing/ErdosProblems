"""Probe symmetric layer-split certificates for ROWSUM-O.

For a bad edge f with odd length L=2m+1 and layer contributions
  a_i = sum_{v in I_i(f)} p_f(v) S(v),
test whether there is a symmetric split t (1 <= t <= m) such that

  outer_t := sum_{i<t} a_i + sum_{i>=L-t} a_i <= (2t) N / L
  center_t := sum_{t<=i<L-t} a_i <= (L-2t) N / L.

For t=m the center is the middle layer.  If both inequalities hold for
some t, their sum gives ROWSUM-O for f.  This is diagnostic only.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads
from _layerprice import layers_of


def exact_pf_and_s(info):
    pfs = {}
    s = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, nf) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            s[v] += x
    return pfs, s


def edge_probe(label, n, edges):
    info = loads(n, edges)
    if info is None:
        return None
    pfs, s = exact_pf_and_s(info)
    bad = []
    hist = {}
    late = []
    worst_outer_need = (F(-10**9), None)
    worst_center_need = (F(-10**9), None)
    best_margin = None
    best_payload = None
    for f in info["M"]:
        lay, _, h = layers_of(info, f)
        L = h + 1
        if L % 2 == 0:
            return ("bad_even_length", g6, f, L)
        pf = pfs[f]
        a = []
        for i in range(L):
            a.append(sum(pf[v] * s[v] for v in lay[i]))
        rowsum = sum(a)
        m = L // 2
        bvals = []
        ok = False
        first_ok_t = None
        local_best = None
        local_best_data = None
        for t in range(1, m + 1):
            outer = sum(a[:t]) + sum(a[L - t :])
            center = sum(a[t : L - t])
            outer_gap = outer - F(2 * t * n, L)
            center_gap = center - F((L - 2 * t) * n, L)
            bvals.append(outer_gap)
            margin = max(outer_gap, center_gap)
            if local_best is None or margin < local_best:
                local_best = margin
                local_best_data = (t, outer, center, outer_gap, center_gap, tuple(a), rowsum)
            if outer_gap <= 0 and center_gap <= 0:
                ok = True
                first_ok_t = t
                break
        if best_margin is None or local_best > best_margin:
            best_margin = local_best
            best_payload = (label, n, f, L, local_best_data)
        if not ok:
            bad.append((label, n, f, L, local_best_data))
        else:
            hist[(L, first_ok_t)] = hist.get((L, first_ok_t), 0) + 1
            if first_ok_t != 1:
                late.append((label, n, f, L, first_ok_t, local_best_data))
        row_gap = rowsum - n
        outer_need = min(bvals)
        center_need = row_gap - max(bvals)
        if outer_need > worst_outer_need[0]:
            worst_outer_need = (outer_need, (label, n, f, L, tuple(a), rowsum, tuple(bvals)))
        if center_need > worst_center_need[0]:
            worst_center_need = (center_need, (label, n, f, L, tuple(a), rowsum, tuple(bvals)))
    return {
        "graphs": 1,
        "rows": len(info["M"]),
        "bad": bad,
        "best_margin": best_margin if best_margin is not None else F(-10**9),
        "best_payload": best_payload,
        "hist": hist,
        "late": late,
        "worst_outer_need": worst_outer_need,
        "worst_center_need": worst_center_need,
    }


def graph_probe(g6):
    n, edges = dec(g6)
    return edge_probe(g6, n, edges)


def merge(acc, res):
    if res is None:
        return
    if isinstance(res, tuple):
        acc["errors"].append(res)
        return
    acc["graphs"] += res["graphs"]
    acc["rows"] += res["rows"]
    acc["fail_rows"] += len(res["bad"])
    for key, val in res.get("hist", {}).items():
        acc["hist"][key] = acc["hist"].get(key, 0) + val
    if res["bad"] and acc["first_fail"] is None:
        acc["first_fail"] = res["bad"][0]
    if res.get("late") and acc["first_late"] is None:
        acc["first_late"] = res["late"][0]
    if res.get("worst_outer_need", (F(-10**9), None))[0] > acc["worst_outer_need"][0]:
        acc["worst_outer_need"] = res["worst_outer_need"]
    if res.get("worst_center_need", (F(-10**9), None))[0] > acc["worst_center_need"][0]:
        acc["worst_center_need"] = res["worst_center_need"]
    if res["best_margin"] > acc["worst_margin"]:
        acc["worst_margin"] = res["best_margin"]
        acc["worst_payload"] = res["best_payload"]


def run(max_n, workers):
    acc = {
        "graphs": 0,
        "rows": 0,
        "fail_rows": 0,
        "first_fail": None,
        "worst_margin": F(-10**9),
        "worst_payload": None,
        "errors": [],
        "hist": {},
        "first_late": None,
        "worst_outer_need": (F(-10**9), None),
        "worst_center_need": (F(-10**9), None),
    }
    for nn in range(5, max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for res in ex.map(graph_probe, out, chunksize=32):
                    merge(acc, res)
        else:
            for g6 in out:
                merge(acc, graph_probe(g6))
        print(
            f"N<={nn}: graphs={acc['graphs']} rows={acc['rows']} "
            f"fail_rows={acc['fail_rows']} worst_margin={acc['worst_margin']}",
            flush=True,
        )
    return acc


def blowup(n, edges, t):
    nn = n * t
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return nn, out


def cycle_blowup(length, t):
    n = length * t
    edges = []
    for i in range(length):
        for a in range(t):
            for b in range(t):
                edges.append((i * t + a, ((i + 1) % length) * t + b))
    return n, edges


def run_witnesses():
    cases = [
        ("I?BD@g]Qo", 1),
        ("J???E?pNu\\?", 2),
        ("J?AEB?oE?W?", 2),
        ("H?bB@_W", 2),
        ("I?rFf_{N?", 2),
    ]
    acc = {
        "graphs": 0,
        "rows": 0,
        "fail_rows": 0,
        "first_fail": None,
        "worst_margin": F(-10**9),
        "worst_payload": None,
        "errors": [],
        "hist": {},
        "first_late": None,
        "worst_outer_need": (F(-10**9), None),
        "worst_center_need": (F(-10**9), None),
    }
    for g6, t in cases:
        n, edges = dec(g6)
        if t != 1:
            n, edges = blowup(n, edges, t)
            label = f"{g6}[{t}]"
        else:
            label = g6
        res = edge_probe(label, n, edges)
        merge(acc, res)
        print(
            f"{label}: fail_rows={0 if res is None else len(res['bad'])} "
            f"worst_margin={None if res is None else res['best_margin']}",
            flush=True,
        )
    for length, t in [(5, 4), (7, 3), (9, 2), (11, 2)]:
        n, edges = cycle_blowup(length, t)
        label = f"C{length}[{t}]"
        res = edge_probe(label, n, edges)
        merge(acc, res)
        print(
            f"{label}: fail_rows={0 if res is None else len(res['bad'])} "
            f"worst_margin={None if res is None else res['best_margin']}",
            flush=True,
        )
    print("=== WITNESSES FINAL ===")
    print(f"graphs={acc['graphs']} rows={acc['rows']} fail_rows={acc['fail_rows']}")
    print(f"first_fail={acc['first_fail']}")
    print(f"worst_margin={acc['worst_margin']} ({float(acc['worst_margin']):+.6g})")
    print(f"worst_payload={acc['worst_payload']}")
    print(f"hist={sorted(acc['hist'].items())}")
    print(f"first_late={acc['first_late']}")
    print(f"worst_outer_need={acc['worst_outer_need']}")
    print(f"worst_center_need={acc['worst_center_need']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--witnesses", action="store_true")
    args = ap.parse_args()
    if args.witnesses:
        run_witnesses()
        return
    acc = run(args.max_n, args.workers)
    print("=== FINAL ===")
    print(f"graphs={acc['graphs']} rows={acc['rows']} fail_rows={acc['fail_rows']}")
    print(f"first_fail={acc['first_fail']}")
    print(f"worst_margin={acc['worst_margin']} ({float(acc['worst_margin']):+.6g})")
    print(f"worst_payload={acc['worst_payload']}")
    print(f"hist={sorted(acc['hist'].items())}")
    print(f"first_late={acc['first_late']}")
    print(f"worst_outer_need={acc['worst_outer_need']}")
    print(f"worst_center_need={acc['worst_center_need']}")
    print(f"errors={acc['errors'][:3]}")


if __name__ == "__main__":
    main()
