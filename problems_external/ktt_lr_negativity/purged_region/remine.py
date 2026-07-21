#!/usr/bin/env python3
"""
remine.py -- THEORY-3 driver: re-mine the population the old (wave-4) screen
purged, using ONLY the mandated LP-free instrument (lpfree_screen.screen_profile).

No dimension oracle, no simplex filter, nothing discarded for "not a simplex".
All arithmetic exact.  Engine-A node budget is a SEARCH-EFFORT cap only; a
triple that exhausts it is reported as UNRESOLVED, never as a math verdict.

Stages
  --stage c        : exact c = P(1) for every triple in the population
  --stage profile  : full exact profile P(0..D+2) + screen_profile record,
                     parallel, per-triple wall-clock budget
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENGINE_A = os.path.join(ROOT, "engine", "lr_hive.exe")
sys.path.insert(0, HERE)
from lpfree_screen import screen_profile  # noqa: E402

COUNT_CAP = 10 ** 18


def parse_p(s):
    return tuple(int(x) for x in s.split(",") if x.strip() not in ("", "0"))


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def ambient_bound(nu):
    r = len(nu)
    return max(0, (r - 1) * (r - 2) // 2)


def engine_batch(lines, node_cap, timeout):
    fd, path = tempfile.mkstemp(suffix=".batch", prefix="rm_", text=True)
    try:
        with os.fdopen(fd, "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        env = dict(os.environ)
        env["LR_HIVE_NODE_CAP"] = str(node_cap)
        try:
            proc = subprocess.run([ENGINE_A, "--batch", path],
                                  capture_output=True, text=True,
                                  env=env, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, "TIMEOUT"
        if proc.returncode != 0:
            return None, "ENGINE_EXIT_%d" % proc.returncode
        out = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
        if len(out) != len(lines):
            return None, "LINE_COUNT_%d_vs_%d" % (len(out), len(lines))
        return out, None
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _profile_job(arg):
    idx, lam, mu, nu, node_cap, timeout = arg
    D = ambient_bound(nu)
    lines = []
    for n in range(D + 3):
        lines.append("%s;%s;%s;%d" % (fmt(tuple(n * x for x in lam)),
                                      fmt(tuple(n * x for x in mu)),
                                      fmt(tuple(n * x for x in nu)), COUNT_CAP))
    t0 = time.time()
    out, err = engine_batch(lines, node_cap, timeout)
    dt = time.time() - t0
    head = {"idx": idx, "lam": list(lam), "mu": list(mu), "nu": list(nu),
            "r": len(nu), "D": D, "secs": round(dt, 2),
            "node_cap": node_cap}
    if err is not None:
        head["status"] = "UNRESOLVED_" + err
        return head
    vals = []
    for tok in out:
        try:
            vals.append(int(tok))
        except ValueError:
            vals.append(tok)
    bad = [n for n, v in enumerate(vals) if not isinstance(v, int)]
    if bad:
        head["status"] = "UNRESOLVED_NODECAP"
        head["failed_n"] = bad
        head["partial_profile"] = [v for v in vals if isinstance(v, int)]
        return head
    rec = screen_profile({n: vals[n] for n in range(D + 3)}, D)
    rec.pop("degree_bound", None)
    head.update(rec)
    return head


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", required=True, help="json list of {lam,mu,nu,...}")
    ap.add_argument("--stage", required=True, choices=["c", "profile"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--filter-idx", help="json list of indices to process")
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--workers", type=int, default=48)
    args = ap.parse_args(argv[1:])

    pop = json.load(open(args.pop))
    items = []
    for i, rec in enumerate(pop):
        items.append((i, parse_p(rec["lam"]), parse_p(rec["mu"]), parse_p(rec["nu"])))
    if args.filter_idx:
        keep = set(json.load(open(args.filter_idx)))
        items = [x for x in items if x[0] in keep]

    if args.stage == "c":
        lines = ["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), COUNT_CAP)
                 for (_, l, m, v) in items]
        out, err = engine_batch(lines, args.node_cap, args.timeout * 100)
        if err:
            raise SystemExit("stage c failed: %s" % err)
        with open(args.out, "w", encoding="utf-8") as f:
            for (i, l, m, v), tok in zip(items, out):
                f.write(json.dumps({"idx": i, "c": tok,
                                    "D": ambient_bound(v)}) + "\n")
        print("stage c wrote %d" % len(items))
        return 0

    jobs = [(i, l, m, v, args.node_cap, args.timeout) for (i, l, m, v) in items]
    done = 0
    t0 = time.time()
    with open(args.out, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(_profile_job, j) for j in jobs]
            for fut in as_completed(futs):
                rec = fut.result()
                f.write(json.dumps(rec) + "\n")
                f.flush()
                done += 1
                if done % 100 == 0:
                    print("%d/%d  %.0fs" % (done, len(jobs), time.time() - t0),
                          flush=True)
    print("stage profile wrote %d in %.0fs" % (done, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
