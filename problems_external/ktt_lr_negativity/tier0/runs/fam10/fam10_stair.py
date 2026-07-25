#!/usr/bin/env python3
"""fam10_stair.py -- targeted staircase probe for the fractional-vertex family.

The maximally-fractional triples found by the sweep all sit on staircase nu:
  lam=(2,2,1), mu=(4,3,2,1)=stair(4), nu=(5,4,3,2,1)=stair(5)   ratio 2/7
so this probe walks nu = stair(k+1), mu = stair(k) and ALL lam with |lam|=k+1
(plus the mirrored variants), for k = 3..7, measuring vertex fractionality.
Also probes nu = stair(k+1) with all (lam,mu) of small size.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fam10_gen import parts_upto, contained          # noqa: E402
from fam10_vsweep import measure                     # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed


def stair(k):
    return tuple(range(k, 0, -1))


def _job(a):
    lam, mu, nu, K, seed = a
    rec = {"lam": list(lam), "mu": list(mu), "nu": list(nu)}
    try:
        rec.update(measure(lam, mu, nu, K, seed))
    except Exception as ex:                            # noqa: BLE001
        rec["vstatus"] = "EXC:" + repr(ex)[:120]
    return rec


def main(argv):
    dst = argv[1]
    kmax = int(argv[2]) if len(argv) > 2 else 6
    jobs = []
    seen = set()
    for k in range(3, kmax + 1):
        nu = stair(k + 1)
        N = sum(nu)
        for a in range(1, N):
            for lam in parts_upto(a, k + 1):
                if not contained(lam, nu):
                    continue
                for mu in parts_upto(N - a, k + 1):
                    if not contained(mu, nu):
                        continue
                    if lam > mu:
                        continue
                    # keep the probe cheap: only near-staircase partners
                    if not (mu == stair(k) or lam == stair(k)
                            or sum(1 for i in range(min(len(mu), k))
                                   if mu[i] == stair(k)[i]) >= k - 1):
                        continue
                    key = (lam, mu, nu)
                    if key in seen:
                        continue
                    seen.add(key)
                    jobs.append((lam, mu, nu, 200, 11 + len(jobs)))
    print("probe jobs %d" % len(jobs), flush=True)
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=24) as ex:
            futs = [ex.submit(_job, j) for j in jobs]
            for fut in as_completed(futs):
                f.write(json.dumps(fut.result()) + "\n")
                n += 1
                if n % 200 == 0:
                    f.flush()
                    print(n, flush=True)
    print("wrote %d" % n, flush=True)


if __name__ == "__main__":
    main(sys.argv)
