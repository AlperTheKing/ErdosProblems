#!/usr/bin/env python3
"""Chunked driver: run lpfree_screen in small blocks so one engine failure
does not destroy the whole batch.  Appends JSON lines to <out>."""
import os, subprocess, sys

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCREEN = os.path.join(BASE, "purged_region", "lpfree_screen.py")
HERE = os.path.dirname(os.path.abspath(__file__))

batch, out, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
lines = [l for l in open(batch) if l.strip()]
fo = open(out, "w")
nfail = 0
for i in range(0, len(lines), size):
    blk = lines[i:i + size]
    tmp = os.path.join(HERE, "_chunk.batch")
    open(tmp, "w").writelines(blk)
    try:
        p = subprocess.run([sys.executable, SCREEN, "--batch", tmp],
                           capture_output=True, text=True,
                           cwd=os.path.dirname(SCREEN), timeout=900)
        if p.stdout.strip():
            fo.write(p.stdout)
            fo.flush()
        else:
            nfail += len(blk)
    except subprocess.TimeoutExpired:
        nfail += len(blk)
    sys.stderr.write("\r%d/%d done, %d unusable" % (i + len(blk), len(lines), nfail))
    sys.stderr.flush()
fo.close()
sys.stderr.write("\n")
