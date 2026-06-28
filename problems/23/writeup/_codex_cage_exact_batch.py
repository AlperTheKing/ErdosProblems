"""Batch exact-rational CAGE certificate attempts on census slices.

This is a scaling harness around _codex_cage_exact.py.  It still uses the
floating CAGE solve only as a guide, then checks every accepted certificate
with exact Fraction arithmetic.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from fractions import Fraction as F
from math import exp

from _codex_cage import GENG, build_instance, solve_cage
from _codex_cage_exact import build_exact_instance, repair_alpha, verify_exact, write_certificate
from _h import dec, loads


def cert_name(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", label)


def try_exact(info, label: str, g6: str, blow: int, rounds: int, restarts: int, denom: int, save_dir: str | None):
    fl = build_instance(info, label)
    if fl is None:
        return None
    ex = build_exact_instance(info, label)
    row = solve_cage(fl, rounds=rounds, restarts=restarts)
    alpha_sources = [("lp", row["alpha"])]
    for eps in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
        alpha_sources.append((f"mix{eps:g}", (1.0 - eps) * row["alpha"] + eps * fl.alpha0))

    attempts = 0
    last = None
    for rden in [10**4, 10**5, 10**6, denom]:
        r = [F(exp(float(x))).limit_denominator(rden) for x in row["x"]]
        for src_name, alpha_src in alpha_sources:
            for aden in [10**4, 10**5, 10**6, denom]:
                attempts += 1
                alpha, pivots = repair_alpha(ex, alpha_src, aden)
                ok, kind, detail = verify_exact(ex, alpha, r)
                last = (kind, detail)
                if ok:
                    path = None
                    if save_dir:
                        os.makedirs(save_dir, exist_ok=True)
                        path = os.path.join(save_dir, f"{cert_name(label)}.cage.json")
                        write_certificate(
                            path,
                            ex=ex,
                            g6=g6,
                            blow=blow,
                            alpha=alpha,
                            r=r,
                            src_name=src_name,
                            rden=rden,
                            aden=aden,
                            pivots=pivots,
                            min_slack=detail,
                        )
                    return {
                        "label": label,
                        "float_gap": row["gap"],
                        "vars": len(ex.vars),
                        "gates": len(ex.gates),
                        "attempts": attempts,
                        "src": src_name,
                        "rden": rden,
                        "aden": aden,
                        "min_slack": detail,
                        "path": path,
                    }
    return {
        "label": label,
        "float_gap": row["gap"],
        "vars": len(ex.vars),
        "gates": len(ex.gates),
        "attempts": attempts,
        "failed": last,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=8)
    ap.add_argument("--nmax", type=int, default=8)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--denom", type=int, default=10**7)
    ap.add_argument("--save-dir", default=None)
    args = ap.parse_args()

    total = ok = fail = 0
    for n in range(args.nmin, args.nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True, check=True).stdout.split()
        used = 0
        for g6 in g6s:
            info = loads(*dec(g6))
            if info is None:
                continue
            used += 1
            if args.limit and used > args.limit:
                break
            total += 1
            result = try_exact(info, f"{g6}[1]", g6, 1, args.rounds, args.restarts, args.denom, args.save_dir)
            if result is None:
                continue
            if "failed" in result:
                fail += 1
                kind, detail = result["failed"]
                print(
                    f"FAIL {result['label']} gap={result['float_gap']:+.3e} "
                    f"vars={result['vars']} gates={result['gates']} kind={kind} detail={detail}",
                    flush=True,
                )
            else:
                ok += 1
                print(
                    f"OK {result['label']} gap={result['float_gap']:+.3e} "
                    f"vars={result['vars']} gates={result['gates']} src={result['src']} "
                    f"rden={result['rden']} aden={result['aden']} slack={result['min_slack']} "
                    f"path={result['path']}",
                    flush=True,
                )
    print(f"SUMMARY total={total} ok={ok} fail={fail}", flush=True)


if __name__ == "__main__":
    main()
