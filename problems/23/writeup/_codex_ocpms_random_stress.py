"""Parallel random stress for the OC-PMS overload-collapse certificate.

This script samples connected triangle-free graphs on N=11..13, enumerates
gamma-min connected-B maximum cuts via existing helpers, and applies the
same row checks as `_codex_ocpms_gate.py`.

It is intentionally a stress tool, not a proof artifact.
"""

import argparse
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

from _bdef_construct import is_triangle_free
from _codex_ocpms_gate import gfam


def sample_graph(seed, ns, ps, min_edges):
    rng = random.Random(seed)
    for _ in range(500):
        n = rng.choice(ns)
        p = rng.choice(ps)
        E = [
            (a, b)
            for a in range(n)
            for b in range(a + 1, n)
            if rng.random() < p
        ]
        if len(E) < min_edges:
            continue
        if not is_triangle_free(n, E):
            continue
        deg = [0] * n
        for a, b in E:
            deg[a] += 1
            deg[b] += 1
        if min(deg) == 0:
            continue
        return n, E
    return None


def one(seed, ns, ps, min_edges):
    got = sample_graph(seed, ns, ps, min_edges)
    acc = dict(
        rows=0,
        over_rows=0,
        collapse_fail=0,
        collapse_ex=None,
        pms_rows=0,
        pms_fail=0,
        pms_ex=None,
        pms_min=None,
        pms_min_ex=None,
    )
    if got is None:
        acc["sampled"] = 0
        return acc
    n, E = got
    gfam(f"randstress_{seed}", n, E, acc)
    acc["sampled"] = 1
    return acc


def merge(dst, src):
    for k in [
        "rows",
        "over_rows",
        "collapse_fail",
        "pms_rows",
        "pms_fail",
        "sampled",
    ]:
        dst[k] += src.get(k, 0)
    for k in ["collapse_ex", "pms_ex"]:
        if dst[k] is None and src.get(k) is not None:
            dst[k] = src[k]
    if src.get("pms_min") is not None and (
        dst["pms_min"] is None or src["pms_min"] < dst["pms_min"]
    ):
        dst["pms_min"] = src["pms_min"]
        dst["pms_min_ex"] = src["pms_min_ex"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20260630)
    ap.add_argument("--ns", default="11,12,13")
    ap.add_argument("--ps", default="0.12,0.16,0.20,0.24,0.28,0.32")
    ap.add_argument("--min-edges", type=int, default=8)
    args = ap.parse_args()

    ns = [int(x) for x in args.ns.split(",") if x]
    ps = [float(x) for x in args.ps.split(",") if x]
    seeds = [args.seed + i for i in range(args.trials)]

    total = dict(
        sampled=0,
        rows=0,
        over_rows=0,
        collapse_fail=0,
        collapse_ex=None,
        pms_rows=0,
        pms_fail=0,
        pms_ex=None,
        pms_min=None,
        pms_min_ex=None,
    )

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(one, s, ns, ps, args.min_edges) for s in seeds]
        for i, fut in enumerate(as_completed(futs), 1):
            merge(total, fut.result())
            if i % 100 == 0:
                print(
                    "done",
                    i,
                    "sampled",
                    total["sampled"],
                    "rows",
                    total["rows"],
                    "over",
                    total["over_rows"],
                    "cfail",
                    total["collapse_fail"],
                    "pfail",
                    total["pms_fail"],
                    flush=True,
                )

    print("OC-PMS random stress")
    for k in [
        "sampled",
        "rows",
        "over_rows",
        "collapse_fail",
        "pms_rows",
        "pms_fail",
    ]:
        print(k, total[k])
    print("collapse_ex", total["collapse_ex"] or "")
    print("pms_ex", total["pms_ex"] or "")
    print("pms_min", total["pms_min"], total["pms_min_ex"] or "")
    print(
        "VERDICT",
        "FAIL" if total["collapse_fail"] or total["pms_fail"] else "no failure",
    )


if __name__ == "__main__":
    main()

