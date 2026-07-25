"""Exhaustive scan of extreme-anisotropy 'corner' patterns.

Because a1 is homogeneous of degree 1 and piecewise linear on the gap cone,
its minimum over the cone is attained on extreme rays of the linearity
chambers.  Those rays are maximally anisotropic: many coordinates tiny, a few
enormous.  This scans EVERY assignment of the 9 gaps to a fixed ladder of
magnitudes, which is exactly the family of corner rays of such ladders.
"""
import sys, os, itertools, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from search import a1x6

def scan(vals, shard, nshard):
    best = None
    stats = {}
    n = 0
    t0 = time.time()
    for idx, tup in enumerate(itertools.product(vals, repeat=9)):
        if idx % nshard != shard: continue
        g = kt4.fix_gap(tup)
        r = a1x6(g)
        stats[r[0]] = stats.get(r[0], 0) + 1
        if r[0] != "ok": continue
        n += 1
        v = r[1]
        if v < 0:
            print(json.dumps({"NEGATIVE": True, "g": list(g), "v": str(v)}))
            sys.exit(3)
        if best is None or v < best[0]:
            best = (v, g)
    return best, stats, n, time.time() - t0

if __name__ == "__main__":
    ladder = [int(x) for x in sys.argv[1].split(",")]
    shard = int(sys.argv[2]); nshard = int(sys.argv[3])
    best, stats, n, secs = scan(ladder, shard, nshard)
    print(json.dumps({"ladder": ladder, "shard": shard, "ok": n,
                      "stats": stats,
                      "min6a1": str(best[0]) if best else None,
                      "argmin": list(best[1]) if best else None,
                      "secs": round(secs, 1)}))
