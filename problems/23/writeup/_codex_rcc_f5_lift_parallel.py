"""Parallel companion for `_claude_rcc_f5_lift.py`.

This file deliberately reuses Claude's exact primitives (`minimal_cores`,
`try_lift`, `realize`) and only parallelizes the independent per-core lift
attempts.  It is intended as a fast exact gate for the T7 parity hint:
minimal 4-uniform Hall-deficient cores at |F|=6 should have no realizable P4
lift in a simple bipartite cut graph.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
from pathlib import Path
from typing import Any


_BASE: Any = None


def _load_base(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("_claude_rcc_f5_lift_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base script: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _init_worker(path_text: str) -> None:
    global _BASE
    _BASE = _load_base(Path(path_text))


def _worker(args: tuple[int, tuple[frozenset[int], ...]]) -> dict[str, Any]:
    if _BASE is None:
        raise RuntimeError("worker base module was not initialized")
    nF, core = args
    lift = _BASE.try_lift(core, nF)
    if lift is None:
        return {"status": "no-lift", "core": [sorted(r) for r in core]}
    graph, msg = _BASE.realize(core, nF, lift)
    if graph is None:
        return {"status": msg, "core": [sorted(r) for r in core]}
    return {"status": "realized", "core": [sorted(r) for r in core], "graph": graph}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nF", type=int, default=6, help="number of support edges")
    parser.add_argument("--workers", type=int, default=48, help="process workers")
    parser.add_argument("--limit", type=int, default=None, help="optional core limit for smoke tests")
    parser.add_argument(
        "--base",
        type=Path,
        default=Path(__file__).with_name("_claude_rcc_f5_lift.py"),
        help="Claude exact primitive script",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("tmp/codex_rcc_f5_lift_parallel_summary.json"),
        help="summary JSON path",
    )
    ns = parser.parse_args()

    base = _load_base(ns.base)
    cores = list(base.minimal_cores(ns.nF))
    if ns.limit is not None:
        cores = cores[: ns.limit]

    counts: dict[str, int] = {}
    realized: list[dict[str, Any]] = []
    total = len(cores)
    print(f"parallel F5 lift nF={ns.nF} cores={total} workers={ns.workers}", flush=True)

    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=ns.workers, initializer=_init_worker, initargs=(str(ns.base),)) as pool:
        for idx, result in enumerate(pool.imap_unordered(_worker, ((ns.nF, c) for c in cores), chunksize=4), 1):
            status = result["status"]
            counts[status] = counts.get(status, 0) + 1
            if status == "realized":
                realized.append(result)
            if idx == total or idx % 100 == 0:
                print(f"{idx}/{total} {counts}", flush=True)

    summary = {
        "nF": ns.nF,
        "cores": total,
        "workers": ns.workers,
        "counts": counts,
        "realized": realized,
    }
    ns.out.parent.mkdir(parents=True, exist_ok=True)
    ns.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {ns.out}", flush=True)
    return 0 if not realized else 2


if __name__ == "__main__":
    raise SystemExit(main())
