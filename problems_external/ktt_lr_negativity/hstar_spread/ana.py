#!/usr/bin/env python3
"""Analyse lpfree_screen .out files: exact Hurwitz verdict + sector angle."""
import json, sys, math, collections
import numpy as np
from crit import coeffs_from_hstar
from hurwitz import routh

ok = bad = skip = 0
per = collections.defaultdict(lambda: (-9, None))
fails = []
neg = []
for path in sys.argv[1:]:
    for l in open(path):
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("status") != "OK" or not o.get("heldout_ok"):
            skip += 1
            continue
        h = o["hstar"]
        d = len(h) - 1
        if d < 2:
            skip += 1
            continue
        a = coeffs_from_hstar(h)
        if any(x < 0 for x in a):
            neg.append((o["lam"], o["mu"], o["nu"], h, [str(x) for x in a]))
        v, _ = routh([a[d - i] for i in range(d + 1)])
        if v == "STRICT":
            ok += 1
        else:
            bad += 1
            fails.append((v, d, h, o["lam"], o["mu"], o["nu"]))
        rts = np.roots([float(x) for x in reversed(a)])
        mc = max(z.real / abs(z) for z in rts)
        if mc > per[d][0]:
            per[d] = (mc, (h, o["lam"], o["mu"], o["nu"]))
print("usable=%d  HURWITZ=%d  NOT-HURWITZ=%d  skipped=%d" % (ok + bad, ok, bad, skip))
print("NEGATIVE COEFFICIENT (KTT counterexample candidates): %d" % len(neg))
for n in neg[:5]:
    print("   ", n)
for d in sorted(per):
    mc, i = per[d]
    print("  d=%2d worst cos=%+.4f  half-angle=%5.1f deg  h*=%s (%s|%s|%s)" %
          ((d, mc, math.degrees(math.acos(min(1, max(-1, -mc))))) + i))
for f in fails[:12]:
    print("  NOT HURWITZ:", f)
