"""Exact piecewise-linear descent on 6*a1 over the 9-dim gap cone.

a1 is homogeneous of degree 1 and linear on each chamber of the normal-fan
(type) decomposition, so a1 < 0 somewhere  <=>  some chamber's gradient is
negative on a ray of that chamber inside the nonnegative orthant.  The discrete
partials of 6*a1 are frequently NEGATIVE (grad.py), so descent is not vacuous.

Moves: single-coordinate line searches with geometric step sizes up to 2^40,
in both directions, plus multi-coordinate steepest combinations.  Steps are
multiples of 4 so realisability (4 | Aw+Bw-Cw) is preserved exactly.
"""
import random, sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from search import a1x6

STEPS = [4 * (2 ** k) for k in range(0, 41)]

def ev(g):
    r = a1x6(g)
    return r[1] if r[0] == "ok" else None

def descend(g, budget=4000):
    cur = ev(g)
    if cur is None:
        return None, None, 0
    used = 1
    while used < budget:
        best = None
        # 1-coordinate line searches
        for k in range(9):
            for sgn in (1, -1):
                prev = cur
                for s in STEPS:
                    h = list(g); h[k] += sgn * s
                    if h[k] < 1: break
                    v = ev(tuple(h)); used += 1
                    if v is None:
                        continue
                    if best is None or v < best[0]:
                        best = (v, tuple(h))
                    if v > prev:
                        break
                    prev = v
                    if used > budget: break
        # steepest multi-coordinate combination from unit partials
        base = cur
        part = []
        for k in range(9):
            h = list(g); h[k] += 4
            v = ev(tuple(h)); used += 1
            part.append((v - base) if v is not None else 0)
        order = sorted(range(9), key=lambda k: part[k])
        for take in (2, 3, 4, 5, 9):
            for s in STEPS[:24]:
                h = list(g)
                for k in order:
                    if part[k] < 0:
                        h[k] += s
                if tuple(h) == tuple(g): break
                v = ev(tuple(h)); used += 1
                if v is not None and (best is None or v < best[0]):
                    best = (v, tuple(h))
            break
        if best is None or best[0] >= cur:
            break
        cur, g = best[0], list(best[1])
    return cur, tuple(g), used

if __name__ == "__main__":
    seed = int(sys.argv[1]); trials = int(sys.argv[2]); K = int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else "iso"
    random.seed(seed)
    gbest = None
    t0 = time.time()
    tot = 0
    for t in range(trials):
        for _ in range(200):
            if mode == "iso":
                g = tuple(random.randint(1, K) for _ in range(9))
            else:
                g = tuple(max(1, int(10 ** random.uniform(0, math.log10(K)))) for _ in range(9))
            g = kt4.fix_gap(g)
            if ev(g) is not None: break
        else:
            continue
        v, gg, used = descend(g)
        tot += used
        if v is None: continue
        if v < 0:
            print("NEGATIVE!!!", v, gg, flush=True)
            print(json.dumps({"NEG": True, "g": list(gg)}))
            sys.exit(3)
        if gbest is None or v < gbest[0]:
            gbest = (v, gg)
    print(json.dumps({"seed": seed, "trials": trials, "K": K, "mode": mode,
                      "min6a1": str(gbest[0]) if gbest else None,
                      "argmin": list(gbest[1]) if gbest else None,
                      "evals": tot, "secs": round(time.time() - t0, 1)}))
