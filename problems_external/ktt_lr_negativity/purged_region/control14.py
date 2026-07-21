#!/usr/bin/env python3
"""
control14.py -- FAMILY 14 = CONTROL lane of the corrected KTT hunt.

NOT a hunting family.  Purpose: measure, on UNBIASED random hive triples,
  (i)   the base rate of h*_1 = 0   (h*_1 = c - (d+1))
  (ii)  the distribution of normalized volume  V = sum h*
  (iii) the global minimum monomial coefficient
  (iv)  every triple with ANY strictly negative coefficient
so that the exploit families can be judged against a null model.

SAMPLING (stated precisely so the control is reproducible and honest)
---------------------------------------------------------------------
A cell is a pair (r, N).  Its population is

  Pop(r,N) = { (lam,mu,nu) :  nu |- N with EXACTLY r parts,
                              lam |- a, mu |- N-a  for some 0<=a<=N,
                              len(lam) <= r, len(mu) <= r,
                              lam subset nu, mu subset nu }

(the containment conditions are exactly the classical necessary conditions
for c(nu;lam,mu) != 0; dropping them would only add triples with P == 0).
Pop(r,N) is streamed and K triples are drawn from it by RESERVOIR SAMPLING,
which is exactly uniform on Pop(r,N).  Nothing else is filtered: triples
with c = 0 are kept and reported (by the saturation theorem c = 0 implies
P == 0, so they are the "empty" stratum of the control).

Every kept triple is then profiled with the MANDATED instrument
lpfree_screen.screen_profile via remine._profile_job: exact engine-A profile
P(0..D+2), exact Newton interpolation over Q, two held-out verification
points, h* from the standard alternating sum.  No LP oracle, no simplex
filter, no discarding.
"""
import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from remine import _profile_job, ambient_bound  # noqa: E402


# ---------------------------------------------------------------- partitions
def parts_exact(N, k, maxpart=None):
    if maxpart is None:
        maxpart = N
    out = []

    def rec(rem, k, mx, cur):
        if k == 0:
            if rem == 0:
                out.append(tuple(cur))
            return
        if rem < k:
            return
        for p in range(min(mx, rem - (k - 1)), 0, -1):
            cur.append(p)
            rec(rem - p, k - 1, p, cur)
            cur.pop()

    rec(N, k, maxpart, [])
    return out


def parts_upto(N, kmax):
    if N == 0:
        return [()]
    out = []
    for k in range(1, kmax + 1):
        out.extend(parts_exact(N, k))
    return out


def contained(p, nu):
    for i, x in enumerate(p):
        if i >= len(nu) or x > nu[i]:
            return False
    return True


_PCACHE = {}


def _pu(a, r):
    key = (a, r)
    if key not in _PCACHE:
        _PCACHE[key] = parts_upto(a, r)
    return _PCACHE[key]


def draw_twostage(r, N, K, rnd):
    """Two-stage UNBIASED design, used for every cell:
         stage 1: nu uniform among the partitions of N with exactly r parts;
         stage 2: (lam,mu) uniform among ALL pairs compatible with that nu,
                  i.e. a drawn with prob proportional to L(a,nu)*L(N-a,nu)
                  and then lam, mu uniform in their (containment-filtered) lists.
    No filter of any kind is applied afterwards.  Cost is O(K) cluster builds
    instead of enumerating the whole product, which is what makes r=7 with
    |nu| ~ 34 reachable at all.
    """
    nus = parts_exact(N, r)
    if not nus:
        return [], 0
    subcache = {}
    seen = set()
    out = []
    tries = 0
    while len(out) < K and tries < 40 * K:
        tries += 1
        nu = nus[rnd.randrange(len(nus))]
        if nu not in subcache:
            sub = [[p for p in _pu(a, r) if contained(p, nu)] for a in range(N + 1)]
            w = []
            tot = 0
            for a in range(N + 1):
                tot += len(sub[a]) * len(sub[N - a])
                w.append(tot)
            subcache[nu] = (sub, w, tot)
        sub, w, tot = subcache[nu]
        if tot == 0:
            continue
        import bisect
        a = bisect.bisect_right(w, rnd.randrange(tot))
        lam = sub[a][rnd.randrange(len(sub[a]))]
        mu = sub[N - a][rnd.randrange(len(sub[N - a]))]
        key = (lam, mu, nu)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out, len(nus)


def build_cell(r, N):
    """EXACT uniform sampler data for Pop(r,N).

    Returns (index, total) where index is a list of
    (cumulative_weight, nu, a, list_lam, list_mu).  |Pop(r,N)| = total is
    computed combinatorially (no enumeration of the product), so a uniform
    draw is O(log #blocks) and the whole population is representable even
    when it has billions of elements.
    """
    index = []
    total = 0
    for nu in parts_exact(N, r):
        sub = {}
        for a in range(0, N + 1):
            sub[a] = [p for p in _pu(a, r) if contained(p, nu)]
        for a in range(0, N + 1):
            la, mb = sub[a], sub[N - a]
            w = len(la) * len(mb)
            if w == 0:
                continue
            total += w
            index.append((total, nu, la, mb))
    return index, total


def draw(index, total, K, rnd):
    """K i.i.d. uniform draws from Pop(r,N) (duplicates removed at the end)"""
    import bisect
    cum = [x[0] for x in index]
    seen = set()
    out = []
    tries = 0
    while len(out) < K and tries < 60 * K:
        tries += 1
        j = rnd.randrange(total)
        b = bisect.bisect_right(cum, j)
        _, nu, la, mb = index[b]
        lam = la[rnd.randrange(len(la))]
        mu = mb[rnd.randrange(len(mb))]
        key = (lam, mu, nu)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


# ---------------------------------------------------------------- driver
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True,
                    help='semicolon list "r:Nlo-Nhi:K" e.g. "4:8-16:40;5:10-18:30"')
    ap.add_argument("--seed", type=int, default=20260721)
    ap.add_argument("--out", required=True)
    ap.add_argument("--node-cap", type=int, default=2 * 10 ** 9)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--popcap", type=int, default=4000000)
    args = ap.parse_args(argv[1:])

    rnd = random.Random(args.seed)
    triples = []
    meta = []
    for spec in args.cells.split(";"):
        spec = spec.strip()
        if not spec:
            continue
        rs, Ns, Ks = spec.split(":")
        r = int(rs)
        K = int(Ks)
        lo, hi = [int(x) for x in Ns.split("-")]
        for N in range(lo, hi + 1):
            if N < r:
                continue
            t0 = time.time()
            samp, nnu = draw_twostage(r, N, K, rnd)
            if not samp:
                continue
            meta.append({"r": r, "N": N, "n_nu": nnu, "drawn": len(samp),
                         "gen_secs": round(time.time() - t0, 1)})
            print("cell r=%d N=%d #nu=%d drawn=%d (%.1fs)"
                  % (r, N, nnu, len(samp), time.time() - t0), flush=True)
            for (lam, mu, nu) in samp:
                triples.append((r, N, lam, mu, nu))

    print("total control triples: %d" % len(triples), flush=True)
    with open(args.out + ".cells.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)

    jobs = [(i, l, m, v, args.node_cap, args.timeout)
            for i, (_, _, l, m, v) in enumerate(triples)]
    done = 0
    t0 = time.time()
    with open(args.out, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_profile_job, j): j[0] for j in jobs}
            for fut in as_completed(futs):
                rec = fut.result()
                i = rec["idx"]
                rec["cell_r"] = triples[i][0]
                rec["cell_N"] = triples[i][1]
                f.write(json.dumps(rec) + "\n")
                f.flush()
                done += 1
                if done % 200 == 0:
                    print("%d/%d  %.0fs" % (done, len(jobs), time.time() - t0),
                          flush=True)
    print("wrote %d in %.0fs" % (done, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
