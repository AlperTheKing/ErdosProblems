#!/usr/bin/env python3
"""retry the N=21 chunk that hit a transient engine spawn failure"""
import json
import os
import sys
import fractions

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)
from ladder_scan2 import _chunk_job  # noqa: E402

tr = [tuple(map(tuple, t)) for t in json.load(open("runs/fam10/_unres21.json"))]
print("retrying", len(tr), flush=True)
res = []
for s in range(0, len(tr), 50):
    res.extend(_chunk_job((tr[s:s + 50], 10, 4 * 10 ** 9, 3000)))
    print(" ", len(res), flush=True)
bad = [r for r in res if r.get("status") != "OK"]
ok = [r for r in res if r.get("status") == "OK"]
print("still bad", len(bad), (bad[0]["status"] if bad else ""))
print("ok", len(ok), "neg", sum(1 for r in ok if r["neg"]))
if ok:
    print("maxV", max(r["hstar_sum"] for r in ok))
    print("maxV h1=0",
          max([r["hstar_sum"] for r in ok if (len(r["hstar"])>1 and r["hstar"][1] == 0)], default=0))
    print("maxV h1<=2",
          max([r["hstar_sum"] for r in ok if (len(r["hstar"])<2 or r["hstar"][1] <= 2)], default=0))
    print("min coeff",
          min(min(map(fractions.Fraction, r["coeffs_low_to_high"]))
              for r in ok))
with open("runs/fam10/records_ext21_retry.jsonl", "w", encoding="utf-8") as f:
    for r in res:
        f.write(json.dumps(r) + "\n")
print("written")
