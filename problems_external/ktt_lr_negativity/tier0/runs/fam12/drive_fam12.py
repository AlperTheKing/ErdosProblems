#!/usr/bin/env python3
"""fam12 parallel driver: shard a batch file, run tier0_screen.py on each
shard as a separate process, concatenate the JSONL output.

The screen itself is untouched (no LP oracle, no simplex filter); this only
splits the input and joins the output.
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.abspath(os.path.join(HERE, "..", "..", "tier0_screen.py"))


def run_shard(args):
    idx, lines, tag, timeout = args
    bf = os.path.join(HERE, "shards", "%s_%03d.batch" % (tag, idx))
    of = os.path.join(HERE, "shards", "%s_%03d.jsonl" % (tag, idx))
    open(bf, "w").write("\n".join(lines) + "\n")
    if os.path.exists(of) and os.path.getsize(of) > 0:
        return of, 0, "cached"
    cmd = [sys.executable, SCREEN, "--batch", bf, "--out", of]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return of, p.returncode, (p.stderr or "")[-300:]
    except subprocess.TimeoutExpired:
        return of, -9, "TIMEOUT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--per-shard", type=int, default=25)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    os.makedirs(os.path.join(HERE, "shards"), exist_ok=True)
    lines = [ln.strip() for ln in open(a.batch) if ln.strip()]
    shards = [lines[i:i + a.per_shard]
              for i in range(0, len(lines), a.per_shard)]
    jobs = [(i, s, a.tag, a.timeout) for i, s in enumerate(shards)]
    sys.stderr.write("%s: %d triples -> %d shards, %d workers\n"
                     % (a.tag, len(lines), len(shards), a.workers))

    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for k, r in enumerate(ex.map(run_shard, jobs)):
            results.append(r)
            if (k + 1) % 20 == 0:
                sys.stderr.write("  %d/%d shards done\n" % (k + 1, len(shards)))

    nbad = 0
    with open(a.out, "w") as fo:
        for of, rc, err in results:
            if rc != 0:
                nbad += 1
                sys.stderr.write("SHARD FAIL rc=%s %s %s\n" % (rc, of, err))
                continue
            if os.path.exists(of):
                fo.write(open(of).read())
    sys.stderr.write("%s: wrote %s ; failed/timeout shards = %d\n"
                     % (a.tag, a.out, nbad))


if __name__ == "__main__":
    main()
