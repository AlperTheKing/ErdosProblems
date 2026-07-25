#!/usr/bin/env python
"""Split a .batch file into NW chunks and run tier0_screen.py --batch on each
in parallel; concatenate the JSONL outputs."""
import sys, os, subprocess, time

batch = sys.argv[1]
out = sys.argv[2]
NW = int(sys.argv[3]) if len(sys.argv) > 3 else 16
SCREEN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "..", "tier0_screen.py")

lines = [l for l in open(batch).read().splitlines() if l.strip()]
chunks = [[] for _ in range(NW)]
for i, l in enumerate(lines):
    chunks[i % NW].append(l)

procs = []
tag = os.path.splitext(os.path.basename(out))[0]
for w in range(NW):
    if not chunks[w]:
        continue
    cp = "_%s_%02d.batch" % (tag, w)
    op = "_%s_%02d.jsonl" % (tag, w)
    ep = "_%s_%02d.err" % (tag, w)
    with open(cp, "w") as f:
        f.write("\n".join(chunks[w]) + "\n")
    fo = open(op, "w")
    fe = open(ep, "w")
    p = subprocess.Popen([sys.executable, SCREEN, "--batch", cp],
                         stdout=fo, stderr=fe)
    procs.append((p, fo, fe, op))

t0 = time.time()
for (p, fo, fe, op) in procs:
    p.wait()
    fo.close()
    fe.close()

with open(out, "w") as f:
    for (p, fo, fe, op) in procs:
        f.write(open(op).read())
n = sum(1 for _ in open(out))
sys.stderr.write("done %d lines in %.1f s\n" % (n, time.time() - t0))
