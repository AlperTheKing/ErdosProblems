#!/usr/bin/env python3
"""fam10_pool.py -- build the family-10 pool: exhaustive (r,N) triples, keep the
nonempty ones (c >= 2) via ONE exact engine-A call each.

c = 0 -> no lattice point at all (screen reports EMPTY).
c = 1 -> Fulton / Knutson-Tao-Woodward: P == 1, d = 0, h*_1 = h*_d = 0, margin 0.
Both are recorded in the counts but carry no tier-0 information.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENGINE_A = os.path.join(ROOT, "engine", "lr_hive.exe")
sys.path.insert(0, HERE)
from fam10_gen import gen                       # noqa: E402

CAP = 10 ** 18


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def engine_batch(lines, timeout=1200):
    fd, path = tempfile.mkstemp(suffix=".batch", prefix="f10_", text=True)
    try:
        with os.fdopen(fd, "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        proc = subprocess.run([ENGINE_A, "--batch", path], capture_output=True,
                              text=True, timeout=timeout)
        if proc.returncode != 0:
            raise SystemExit("engine exit %d" % proc.returncode)
        out = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
        if len(out) != len(lines):
            raise SystemExit("line count %d vs %d" % (len(out), len(lines)))
        return out
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def main(argv):
    r = int(argv[1])
    Nlo, Nhi = int(argv[2]), int(argv[3])
    dst = argv[4]
    trips = []
    for N in range(Nlo, Nhi + 1):
        t = gen(r, N)
        print("r=%d N=%d -> %d" % (r, N, len(t)), flush=True)
        trips.extend(t)
    print("pool %d" % len(trips), flush=True)
    n_empty = n_one = n_keep = 0
    idx = 0
    with open(dst, "w", encoding="utf-8") as f:
        CH = 200000
        for s in range(0, len(trips), CH):
            chunk = trips[s:s + CH]
            out = engine_batch(["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), CAP)
                                for (l, m, v) in chunk])
            for (l, m, v), tok in zip(chunk, out):
                try:
                    c = int(tok)
                except ValueError:
                    continue
                if c == 0:
                    n_empty += 1
                    continue
                if c == 1:
                    n_one += 1
                    continue
                f.write(json.dumps({"idx": idx, "lam": list(l), "mu": list(m),
                                    "nu": list(v), "c": c}) + "\n")
                idx += 1
                n_keep += 1
            print("stage1 %d/%d keep=%d empty=%d c1=%d"
                  % (min(s + CH, len(trips)), len(trips), n_keep, n_empty, n_one),
                  flush=True)
    print(json.dumps({"pool": len(trips), "keep": n_keep, "empty": n_empty,
                      "c_eq_1": n_one}), flush=True)


if __name__ == "__main__":
    main(sys.argv)
