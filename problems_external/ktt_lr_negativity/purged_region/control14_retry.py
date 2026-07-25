#!/usr/bin/env python3
"""Re-run every UNRESOLVED control record serially with a bigger budget.
UNRESOLVED is a search-effort outcome, never a math verdict; nothing is dropped."""
import json
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from remine import _profile_job  # noqa: E402


def main(argv):
    srcs = argv[1:-1]
    dst = argv[-1]
    todo = []
    for p in srcs:
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            if str(r.get("status", "")).startswith("UNRESOLVED"):
                todo.append(r)
    print("retrying %d" % len(todo), flush=True)
    from concurrent.futures import ProcessPoolExecutor, as_completed
    jobs = [(i, tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]),
             8 * 10 ** 9, 300) for i, r in enumerate(todo)]
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=14) as ex:
            futs = [ex.submit(_profile_job, j) for j in jobs]
            for fut in as_completed(futs):
                rec = fut.result()
                src = todo[rec["idx"]]
                rec["cell_r"] = src.get("cell_r")
                rec["cell_N"] = src.get("cell_N")
                f.write(json.dumps(rec) + "\n")
                f.flush()
                n += 1
                print("%d/%d %s %s %s -> %s" % (n, len(todo), rec["lam"],
                                                rec["mu"], rec["nu"],
                                                rec["status"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
