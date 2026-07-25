"""Plateau attack: random walk ON the observed minimum level set {6a1 = 11}
and probe every neighbour for a value <= 10.

If 6a1 >= 11 is a genuine wall, every neighbour of every plateau point is
>= 11.  Any single 10 anywhere would break the wall and re-open negativity.
"""
import random, sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from search import a1x6
from descend import descend, ev

STEPS = [4, 8, 16, 32, 64, 256, 1024, 8192, 65536, 2 ** 20, 2 ** 26, 2 ** 32]

def neighbours(g):
    for k in range(9):
        for s in STEPS:
            for sgn in (1, -1):
                h = list(g); h[k] += sgn * s
                if h[k] >= 1: yield tuple(h)
    # pair moves
    for _ in range(60):
        k1, k2 = random.sample(range(9), 2)
        s1 = random.choice(STEPS); s2 = random.choice(STEPS)
        h = list(g)
        h[k1] += random.choice((1, -1)) * s1
        h[k2] += random.choice((1, -1)) * s2
        if all(x >= 1 for x in h): yield tuple(h)

if __name__ == "__main__":
    seed = int(sys.argv[1]); steps = int(sys.argv[2]); K = int(sys.argv[3])
    random.seed(seed)
    t0 = time.time()
    # get onto the plateau
    cur = None
    for _ in range(400):
        g = kt4.fix_gap(tuple(max(1, int(10 ** random.uniform(0, math.log10(K)))) for _ in range(9)))
        v = ev(g)
        if v is None: continue
        v2, g2, _ = descend(g, budget=1500)
        if v2 is not None:
            cur = (v2, g2); break
    if cur is None:
        print(json.dumps({"seed": seed, "err": "no start"})); sys.exit(0)
    floor = 11            # the observed global wall; only <= 10 refutes it
    probes = 0
    plateau_pts = 0
    minseen = floor
    for it in range(steps):
        g = cur[1]
        cands = []
        for h in neighbours(g):
            v = ev(h); probes += 1
            if v is None: continue
            if v < minseen:
                minseen = v
            if v <= 10:
                print(json.dumps({"WALL_BROKEN": True, "value": str(v), "g": list(h)}))
                sys.exit(3)
            if v <= cur[0]:
                cands.append(h)
        plateau_pts += len(cands)
        if not cands:
            # jump: restart elsewhere
            for _ in range(200):
                g0 = kt4.fix_gap(tuple(max(1, int(10 ** random.uniform(0, math.log10(K)))) for _ in range(9)))
                if ev(g0) is None: continue
                v2, g2, _ = descend(g0, budget=1500)
                if v2 is not None:
                    cur = (v2, g2); break
            else:
                break
        else:
            h = random.choice(cands)
            cur = (ev(h), h)
    print(json.dumps({"seed": seed, "K": K, "floor": str(floor),
                      "min_seen": str(minseen), "probes": probes,
                      "plateau_neighbours_found": plateau_pts,
                      "secs": round(time.time() - t0, 1)}))
