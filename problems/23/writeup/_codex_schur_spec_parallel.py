"""Codex runner: parallel exact Schur-spec test over a geng census level.

This calls Claude's exact `_schur_spec.test(info)` implementation but runs the
graph list in a process pool.  It is a runner only; it does not change the
certificate logic.
"""

import argparse
from multiprocessing import Pool
import subprocess
import time

from _h import GENG, dec, loads
from _schur_spec import test


def one(g6):
    n, e = dec(g6)
    info = loads(n, e)
    if info is None:
        return ("skip", g6, None)
    st, data = test(info)
    if st in ("FAIL", "SINGULAR_AQQ"):
        return ("bad", g6, (st, data, n, info["G"], len(info["M"])))
    margin = None
    if st == "ok" and data is not None:
        margin = data["minrow"]
    return ("ok", g6, (st, margin, n, info["G"], len(info["M"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chunksize", type=int, default=16)
    args = ap.parse_args()

    graphs = subprocess.run(
        [GENG, "-tc", str(args.n)], capture_output=True, text=True
    ).stdout.split()
    if args.limit:
        graphs = graphs[: args.limit]
    start = time.time()
    count = skip = bad = 0
    worst = None
    first_bad = None
    with Pool(processes=args.workers) as pool:
        for status, g6, payload in pool.imap_unordered(one, graphs, chunksize=args.chunksize):
            if status == "skip":
                skip += 1
            else:
                count += 1
            if status == "bad":
                bad += 1
                if first_bad is None:
                    first_bad = (g6, payload)
            elif status == "ok" and payload is not None:
                st, margin, n, gamma, m = payload
                if margin is not None:
                    item = (margin, g6, n, gamma, m)
                    if worst is None or item[0] < worst[0]:
                        worst = item
            done = count + skip
            if done and done % 1000 == 0:
                elapsed = time.time() - start
                print(
                    f"done={done}/{len(graphs)} count={count} skip={skip} bad={bad} "
                    f"elapsed={elapsed:.1f}s worst={worst}",
                    flush=True,
                )
    elapsed = time.time() - start
    print(
        f"FINAL n={args.n} graphs={len(graphs)} count={count} skip={skip} bad={bad} "
        f"elapsed={elapsed:.1f}s worst={worst} first_bad={first_bad}",
        flush=True,
    )


if __name__ == "__main__":
    main()
