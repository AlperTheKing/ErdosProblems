#!/usr/bin/env python3
"""Parallel driver: split a fam4 batch file into chunks and run the mandated
tier-0 screen (full --batch mode, NOT the pre-filter) on every chunk.

Full screen on every triple is deliberate: the pre-filter decides TIER0 only
and explicitly does not decide JACKPOT (h*_d > h*_1), which is the quantity
this run must track.
"""
import argparse, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

SCREEN = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                      "..", "..", "tier0_screen.py"))


def run_chunk(args):
    idx, lines, outdir, cap = args
    bf = os.path.join(outdir, "chunk_%05d.batch" % idx)
    of = os.path.join(outdir, "chunk_%05d.jsonl" % idx)
    if os.path.exists(of + ".done"):
        return (idx, "cached")
    with open(bf, "w") as f:
        f.writelines(lines)
    t0 = time.time()
    p = subprocess.run([sys.executable, SCREEN, "--batch", bf,
                        "--out", of, "--cap", str(cap)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return (idx, "FAIL:" + p.stderr.decode()[:200])
    open(of + ".done", "w").write("%.1f\n" % (time.time() - t0))
    try:
        os.remove(bf)
    except OSError:
        pass
    return (idx, "%.1fs" % (time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--chunk", type=int, default=250)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--cap", type=int, default=10**12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    lines = [l for l in open(a.batch) if l.strip()]
    if a.limit:
        lines = lines[:a.limit]
    chunks = [(i // a.chunk, lines[i:i + a.chunk], a.outdir, a.cap)
              for i in range(0, len(lines), a.chunk)]
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for idx, st in ex.map(run_chunk, chunks):
            done += 1
            if done % 20 == 0:
                sys.stderr.write("[%6.1fs] %d/%d chunks\n"
                                 % (time.time() - t0, done, len(chunks)))
    sys.stderr.write("DONE %d triples in %.1fs\n" % (len(lines), time.time() - t0))


if __name__ == "__main__":
    main()
