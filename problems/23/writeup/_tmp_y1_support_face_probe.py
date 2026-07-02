"""Exploratory SLSQP probe for observed + one-step y=1 support faces.

This is NOT a proof artifact and is intentionally not included in the manifest.
It minimizes Phi on active equality faces generated from the observed supports
and one-step neighbors, using the same seven-variable branch/cap charts as the
basin scanner.  Its only purpose is to identify the next exact FJ/Sturm leaf.
"""

from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


HERE = Path(__file__).resolve().parent
SCAN_PATH = HERE / "_tmp_y1_capacity_basin_scan.py"
INV_PATH = HERE / "_codex_sib_s7_y1_fj_support_inventory.py"

spec = importlib.util.spec_from_file_location("scan", SCAN_PATH)
scan = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(scan)

spec2 = importlib.util.spec_from_file_location("inv", INV_PATH)
inv = importlib.util.module_from_spec(spec2)
assert spec2.loader is not None
spec2.loader.exec_module(inv)

NAMES = ["a1", "b1", "c1", "d1", "e1", "f1", "x1", "v1", "u1", "s1", "s2", "s3", *scan.CAPS]


def fixed_labels(branch: str, cap: str) -> set[str]:
    fixed = {cap}
    if branch in {"s2", "s3", "u1"}:
        fixed.add(branch)
    return fixed


def support_rows() -> list[tuple[str, str, str, tuple[str, ...]]]:
    rows: list[tuple[str, str, str, tuple[str, ...]]] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for row in inv.SUPPORTS:
        name = row["name"]
        branch = row["branch"]
        cap = row["cap"]
        active = tuple(sorted(row["active"]))
        fixed = fixed_labels(branch, cap)
        candidates = [(name, branch, cap, active)]
        for label in sorted(set(active) - fixed):
            candidates.append((name + ":drop:" + label, branch, cap, tuple(sorted(set(active) - {label}))))
        for label in sorted(set(NAMES) - set(active) - fixed):
            candidates.append((name + ":add:" + label, branch, cap, tuple(sorted(set(active) | {label}))))
        for item in candidates:
            key = (item[1], item[2], item[3])
            if key not in seen:
                rows.append(item)
                seen.add(key)
    return rows


def penalty_objective(w, cap: str, branch: str, active: tuple[str, ...]):
    phi, sl, _xquv = scan.eval_branch(w, cap, branch)
    fixed = fixed_labels(branch, cap)
    eq_pen = 0.0
    ineq_pen = 0.0
    for name in active:
        if name not in fixed:
            eq_pen += float(sl[name]) ** 2
    for name in NAMES:
        if name in fixed or name in active:
            continue
        val = float(sl[name])
        if val < 0.0:
            ineq_pen += val * val
    return float(phi) + 1.0e7 * eq_pen + 1.0e7 * ineq_pen


def seed_points(branch: str, cap: str, starts: int):
    rng = np.random.default_rng(abs(hash((branch, cap, starts))) % (2**32))
    base = []
    # all-ones and central all-tight-ish points
    base.append(np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]))
    for t in [1.15, 1.5, 2.0, 2.439376, 3.5, 6.0]:
        base.append(np.array([t + 1 - 1 / t, 1.0, t, 1.0, t, 1.0, t]))
    for _ in range(starts):
        base.append(1.0 + rng.random(7) * 6.0)
    return base


def run_face(label: str, branch: str, cap: str, active: tuple[str, ...], starts: int = 8):
    best = None
    fixed = fixed_labels(branch, cap)
    for w0 in seed_points(branch, cap, starts):
        res = minimize(
            penalty_objective,
            w0,
            args=(cap, branch, active),
            method="L-BFGS-B",
            bounds=[(1.0, 80.0)] * 7,
            options={"maxiter": 1500, "ftol": 1e-12, "maxls": 50},
        )
        if not res.success:
            continue
        phi, sl, xquv = scan.eval_branch(res.x, cap, branch)
        if min(sl.values()) < -1e-5:
            continue
        eqvals = [abs(float(sl[n])) for n in active if n not in fixed]
        eqerr = max(eqvals) if eqvals else 0.0
        if eqerr > 1e-4:
            continue
        active_out = tuple(sorted(k for k, vv in sl.items() if vv < 1e-4))
        row = (float(phi), label, branch, cap, active, active_out, res.x, xquv)
        if best is None or row[0] < best[0]:
            best = row
    return best


def main() -> None:
    results = []
    failures = 0
    for row in support_rows():
        got = run_face(*row)
        if got is None:
            failures += 1
        else:
            results.append(got)
    results.sort(key=lambda r: r[0])

    print(f"PROBED faces={len(results) + failures} solved={len(results)} failures={failures}")
    buckets = defaultdict(int)
    for phi, _label, _branch, _cap, _active, active_out, _w, _xquv in results:
        buckets[active_out] += 1
    print("TOP_ACTIVE_BUCKETS")
    for active, count in sorted(buckets.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        print(" ", count, active)

    print("LOW_RESULTS")
    for phi, label, branch, cap, active, active_out, w, xquv in results[:40]:
        print(
            f" phi={phi:.9f} label={label} branch={branch} cap={cap} "
            f"requested={active} active_out={active_out} w={np.array2string(w, precision=6)} xquv={tuple(round(float(z), 6) for z in xquv)}"
        )
    print("PASS exploratory y=1 support-face probe completed")


if __name__ == "__main__":
    main()

