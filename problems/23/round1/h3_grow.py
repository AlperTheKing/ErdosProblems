"""Chained growth: take the best certified graph at N-1, add one isolated vertex, and run the
pooled-cut search at N.  Every bip printed here comes from h3_search2.exe, which certifies it by
full Gray-code enumeration of all 2^(N-1) bipartitions.

Usage: python h3_grow.py START END SEEDG6 SECS SEEDS TAG
"""
import subprocess, sys, re, random
from h3_gen import decode_g6, g6

start, end, seedg6, secs, nseeds, tag = (
    int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6])

_n0, _E0 = decode_g6(seedg6)
assert _n0 <= start, f"seed has {_n0} vertices, start is {start}"
cur = g6(start, _E0)          # lift the seed to `start` vertices by adding isolated vertices
rng = random.Random(hash(tag) & 0xFFFF)
for n in range(start, end + 1):
    t = (n * n) // 25 + 1
    best, bestg = -1, None
    for s in range(nseeds):
        r = subprocess.run(["./h3_search2.exe", str(n), str(t), str(rng.randrange(1, 10**9)),
                            secs, "512", "40", cur], capture_output=True, text=True)
        line = [l for l in r.stdout.strip().splitlines() if l.startswith("DONE")]
        if not line:
            print(f"{tag} n={n} seed={s} FAILED {r.stderr.strip()[:80]}", flush=True)
            continue
        m = re.search(r"bestbip=(\d+).*g6=(\S+)", line[-1])
        b, g = int(m.group(1)), m.group(2)
        print(f"{tag} n={n} seed={s} bip={b} g6={g}", flush=True)
        if b > best:
            best, bestg = b, g
    if bestg is None:
        print(f"{tag} ABORT n={n}", flush=True)
        break
    flag = "*** VIOLATION ***" if 25 * best > n * n else "ok"
    print(f"{tag} BEST n={n} bip={best} 25bip={25*best} n2={n*n} {flag} g6={bestg}", flush=True)
    nn, E = decode_g6(bestg)
    cur = g6(nn + 1, E)
