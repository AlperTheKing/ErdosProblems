"""Certify the ratio-optimal C5 blow-ups at N = 3 mod 5 (best B(N)/N^2 in the 49..78 window)."""
import json, time
from h5_core import adj_from_edges, certify
from h5_certify import c5_blowup

CASES = [("C5[14,15,14,15,15]  N=73", [14,15,14,15,15], 210),
         ("C5[15,16,15,16,16]  N=78", [15,16,15,16,16], 240)]
out = []
for label, parts, expect in CASES:
    n, adj = c5_blowup(parts)
    t0 = time.time()
    r = certify(n, adj, label=label, workers=40, max_time=3000, model="xor", heur_restarts=200)
    r["seconds"] = round(time.time()-t0,1); r["expected_bip"] = expect
    r["min_adjacent_part_product"] = min(parts[i]*parts[(i+1)%5] for i in range(5))
    print(f"    -> {r['status']} bip={r['bip']} expect={expect} 25bip={25*r['bip']} N^2={n*n} "
          f"ratio={r['ratio']:.6f} ({r['seconds']}s)", flush=True)
    out.append(r)
json.dump(out, open("h5_certificates_extra.json","w"), indent=1, default=str)
