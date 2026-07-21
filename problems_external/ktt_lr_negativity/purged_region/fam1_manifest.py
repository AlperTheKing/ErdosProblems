#!/usr/bin/env python3
"""Build runs/fam1/manifest.json from all fam1 jsonl shards."""
import sys, os, json, glob, hashlib, collections
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fam1_score import score

RUN = os.path.join(HERE, "runs", "fam1")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def main():
    shards = sorted(glob.glob(os.path.join(RUN, "*.jsonl")))
    n = 0
    status = collections.Counter()
    perd = collections.defaultdict(lambda: {"n": 0, "maxM1": None, "minS": None,
                                            "maxV_h1z": 0, "maxs_h1z": 0})
    best_sum = None; best_h1z = None; best_h1le2 = None
    min_coeff = None; min_nonlead = None
    hits = []
    seen = set()
    for p in shards:
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            key = (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
            if key in seen:
                continue
            seen.add(key)
            n += 1
            status[r.get("status")] += 1
            if r.get("status") != "OK" or r.get("d") is None or r["d"] < 0:
                continue
            d = r["d"]; V = r["hstar_sum"]; h1 = r["hstar_1"]
            tag = [r["lam"], r["mu"], r["nu"]]
            cs = [Fraction(c) for c in r["coeffs_low_to_high"]]
            mc = min(cs)
            if min_coeff is None or mc < min_coeff[0]:
                min_coeff = (mc, tag, r["poly"], r["hstar"], d)
            if d >= 1:
                mnl = min(cs[:-1])
                if min_nonlead is None or mnl < min_nonlead[0]:
                    min_nonlead = (mnl, tag, r["poly"], r["hstar"], d)
            if best_sum is None or V > best_sum[0]:
                best_sum = (V, tag, r["hstar"], d)
            if h1 == 0 and (best_h1z is None or V > best_h1z[0]):
                best_h1z = (V, tag, r["hstar"], d)
            if h1 is not None and h1 <= 2 and (best_h1le2 is None or V > best_h1le2[0]):
                best_h1le2 = (V, tag, r["hstar"], d)
            if r.get("neg"):
                hits.append(r)
            if d >= 2:
                S, Sk, M1, s = score(r)
                e = perd[d]; e["n"] += 1
                if e["maxM1"] is None or M1 > e["maxM1"]:
                    e["maxM1"] = M1
                if e["minS"] is None or S < Fraction(e["minS"]):
                    e["minS"] = str(S)
                if h1 == 0:
                    e["maxV_h1z"] = max(e["maxV_h1z"], V)
                    e["maxs_h1z"] = max(e["maxs_h1z"], s)
            else:
                perd[d]["n"] += 1

    man = {
        "family": "fam1: refuter cell lam=(2,2,1), mu=(k,3,2,1), nu=(k+1,4,3,2,1), "
                  "k=4..40, plus all 1-box and 2-box size-balanced perturbations "
                  "of all three partitions (3-box exhaustive at k=4; beam climb "
                  "from every h*_1=0, V=2 carrier)",
        "instrument": "purged_region/lpfree_screen.py (LP-free, exact; no dimension "
                      "oracle, no simplex filter)",
        "engine": "A: engine/lr_hive.exe (batch), exact integer counts",
        "shards": [{"file": os.path.basename(p), "sha256": sha(p),
                    "bytes": os.path.getsize(p)} for p in shards],
        "distinct_triples_screened": n,
        "status_counts": dict(status),
        "negative_coefficient_hits": len(hits),
        "hits": hits,
        "best_sum_hstar": {"sum": best_sum[0], "triple": best_sum[1],
                           "hstar": best_sum[2], "d": best_sum[3]} if best_sum else None,
        "best_at_hstar1_zero": {"sum": best_h1z[0], "triple": best_h1z[1],
                                "hstar": best_h1z[2], "d": best_h1z[3]} if best_h1z else None,
        "best_at_hstar1_le2": {"sum": best_h1le2[0], "triple": best_h1le2[1],
                               "hstar": best_h1le2[2], "d": best_h1le2[3]} if best_h1le2 else None,
        "min_coefficient": {"value": str(min_coeff[0]), "triple": min_coeff[1],
                            "poly": min_coeff[2], "hstar": min_coeff[3],
                            "d": min_coeff[4]} if min_coeff else None,
        "min_nonleading_coefficient": {"value": str(min_nonlead[0]), "triple": min_nonlead[1],
                                       "poly": min_nonlead[2], "hstar": min_nonlead[3],
                                       "d": min_nonlead[4]} if min_nonlead else None,
        "per_dimension": {str(k): {kk: vv for kk, vv in v.items()}
                          for k, v in sorted(perd.items())},
        "ladder_target_h1_zero": {
            "3": {"minV": 13, "hstar": [1, 0, 12, 0]},
            "4": {"minV": 7, "hstar": [1, 0, 0, 6, 0]},
            "5": {"minV": 5, "hstar": [1, 0, 0, 0, 4, 0]},
            "6": {"minV": 4, "hstar": [1, 0, 0, 0, 0, 3, 0]},
            "7": {"minV": 4, "hstar": [1, 0, 0, 0, 0, 0, 3, 0]},
            "8": {"minV": 3, "hstar": [1, 0, 0, 0, 0, 0, 0, 2, 0]},
            ">=8": {"minV": 3, "hstar": "top spike at j=d-1, mass 2"},
        },
        "note": "A negative census is NOT evidence for the KTT conjecture.",
    }
    with open(os.path.join(RUN, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    print(json.dumps({k: v for k, v in man.items()
                      if k not in ("shards", "hits")}, indent=1))

if __name__ == "__main__":
    main()
