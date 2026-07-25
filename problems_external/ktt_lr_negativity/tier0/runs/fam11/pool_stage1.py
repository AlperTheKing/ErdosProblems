#!/usr/bin/env python3
"""fam11 arm E: large-weight random pool, stage-1 c-measurement (1 engine call
per triple, batched) so the full screen can be aimed at the triples whose
profile is actually computable inside the cap."""
import sys, os, json, random, subprocess, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
ENGA = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe"

def fmt(p):
    return ",".join(str(x) for x in p)

def valid(lam, mu, nu):
    r = len(nu)
    if len(lam) > r or len(mu) > r:
        return False
    for p in (lam, mu, nu):
        if not p or any(x <= 0 for x in p):
            return False
        if any(p[i] < p[i + 1] for i in range(len(p) - 1)):
            return False
    return (sum(lam) + sum(mu) == sum(nu) and lam[0] <= nu[0] and mu[0] <= nu[0])

def rand_parts(rng, W, k):
    cuts = sorted(rng.randint(1, W) for _ in range(k - 1))
    parts, prev = [], 0
    for c in cuts + [W]:
        parts.append(c - prev)
        prev = c
    return sorted((p for p in parts if p > 0), reverse=True)

def gen(rng, r, W, want):
    out, seen = [], set()
    tries = 0
    while len(out) < want and tries < want * 40:
        tries += 1
        nu = rand_parts(rng, W, r)
        if len(nu) != r:
            continue
        L = rng.randint(max(1, W // 5), W - max(1, W // 5))
        lam = rand_parts(rng, L, rng.randint(2, r))
        mu = rand_parts(rng, W - L, rng.randint(2, r))
        if not valid(lam, mu, nu):
            continue
        k = (tuple(lam), tuple(mu), tuple(nu))
        if k in seen:
            continue
        seen.add(k)
        out.append((lam, mu, nu))
    return out

def engineA_c(trips, cap):
    fd, path = tempfile.mkstemp(suffix=".batch")
    os.close(fd)
    with open(path, "w") as fh:
        for l, m, n in trips:
            fh.write("%s;%s;%s;%d\n" % (fmt(l), fmt(m), fmt(n), cap))
    p = subprocess.run([ENGA, "--batch", path], capture_output=True, text=True)
    os.unlink(path)
    out = []
    for line in p.stdout.splitlines():
        s = line.strip()
        out.append(int(s) if s.lstrip("-").isdigit() else s)
    return out

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 110711
    rng = random.Random(seed)
    CAP = 10 ** 8
    pool = []
    for r in (5, 6, 7):
        for W in (40, 60, 90, 130, 190, 280, 400, 600):
            pool.extend((r, W, t) for t in gen(rng, r, W, 700))
    trips = [t for (_, _, t) in pool]
    t0 = time.time()
    cs = engineA_c(trips, CAP)
    el = time.time() - t0
    recs = []
    for (r, W, t), c in zip(pool, cs):
        recs.append({"r": r, "W": W, "lam": t[0], "mu": t[1], "nu": t[2], "c": c})
    with open(os.path.join(HERE, "pool_stage1.jsonl"), "w") as fh:
        for x in recs:
            fh.write(json.dumps(x) + "\n")
    from collections import Counter
    cnt = Counter()
    for x in recs:
        c = x["c"]
        if not isinstance(c, int):
            cnt["CAP/ERR"] += 1
        elif c == 0:
            cnt["empty"] += 1
        elif c <= 300:
            cnt["thin<=300"] += 1
        elif c <= 10 ** 6:
            cnt["mid"] += 1
        else:
            cnt["fat"] += 1
    print(json.dumps({"pool": len(recs), "seconds": round(el, 1),
                      "buckets": dict(cnt)}))

if __name__ == "__main__":
    main()
