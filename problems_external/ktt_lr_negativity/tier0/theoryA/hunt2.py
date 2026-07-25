#!/usr/bin/env python3
"""
hunt2.py -- scaled TIER-0 / JACKPOT hunt.

Stage 0: engine A (lr_hive.exe, batch) gives c = #lattice points for a huge
         random triple pool in one process call.  Keep 2 <= c <= CMAX.
         (c = 1 is provably dead: Fulton's conjecture, proved by
          Knutson-Tao-Woodward, gives c = 1 ==> P == 1 ==> d = 0.)
Stage A: exact integer enumeration of all hives; T = rhombi tight at EVERY
         hive; n_int_lat = #{p : tight(p) == T} >= true #interior, so
         n_bdy_lat <= true #boundary.  A JACKPOT needs #bdry <= d <= D, so
         keeping n_bdy_lat <= D cannot discard a JACKPOT.
Survivors go to hive_aff.py (exact affine hull) and tier0_screen.py.
"""
import sys, os, json, random, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hive_struct import build, slacks, enumerate_hives, affine_rank

ENGA = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe"


def fmt(p): return ",".join(str(x) for x in p)


def gen(r, nmax, count, seed):
    rng = random.Random(seed)
    seen = set(); out = []
    for _ in range(count * 6):
        if len(out) >= count: break
        nu = sorted((rng.randint(1, nmax) for _ in range(r)), reverse=True)
        N = sum(nu)
        kl = rng.randint(2, r)
        lam = sorted((rng.randint(1, nmax) for _ in range(kl)), reverse=True)
        L = sum(lam)
        if L < 1 or L >= N: continue
        M = N - L
        km = rng.randint(1, r)
        cuts = sorted(rng.randint(0, M) for _ in range(km - 1))
        parts = []; prev = 0
        for c0 in cuts + [M]:
            parts.append(c0 - prev); prev = c0
        mu = sorted((p for p in parts if p > 0), reverse=True)
        if not mu or sum(mu) != M: continue
        if mu[0] > nu[0] or lam[0] > nu[0]: continue
        k = (tuple(lam), tuple(mu), tuple(nu))
        if k in seen: continue
        seen.add(k); out.append((lam, mu, nu))
    return out


def engineA_c(trips):
    fd, path = tempfile.mkstemp(suffix=".batch"); os.close(fd)
    with open(path, "w") as fh:
        for l, m, n in trips:
            fh.write("%s;%s;%s;100000\n" % (fmt(l), fmt(m), fmt(n)))
    p = subprocess.run([ENGA, "--batch", path], capture_output=True, text=True)
    os.unlink(path)
    out = []
    for line, t in zip(p.stdout.splitlines(), trips):
        s = line.strip()
        out.append((t, int(s) if s.isdigit() else None))
    return out


def stageA(lam, mu, nu, cap):
    P = build(lam, mu, nu)
    if P is None: return None
    pts = enumerate_hives(P, cap)
    if not pts: return None
    S = [slacks(P, p) for p in pts]
    ncon = len(P["cons"])
    T = frozenset(k for k in range(ncon) if all(s[k] == 0 for s in S))
    n_int = sum(1 for s in S
                if frozenset(k for k in range(ncon) if s[k] == 0) == T)
    rows = [[P["cons"][k][0][i] for i in range(P["D"])] for k in T]
    dlo = P["D"] - (affine_rank([[0] * P["D"]] + rows) if rows else 0)
    return dict(c=len(pts), D=P["D"], n_int_lat=n_int,
                n_bdy_lat=len(pts) - n_int, d_lower=dlo, nT=len(T))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=14)
    ap.add_argument("--count", type=int, default=60000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cmax", type=int, default=400)
    ap.add_argument("--cap", type=int, default=6000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    trips = gen(a.r, a.nmax, a.count, a.seed)
    sys.stderr.write("generated %d\n" % len(trips)); sys.stderr.flush()
    res = engineA_c(trips)
    pool = [t for t, c in res if c is not None and 2 <= c <= a.cmax]
    sys.stderr.write("nonempty 2<=c<=%d : %d\n" % (a.cmax, len(pool))); sys.stderr.flush()
    best = None; nint = 0
    with open(a.out, "w") as fh:
        for lam, mu, nu in pool:
            try:
                r = stageA(lam, mu, nu, a.cap)
            except Exception:
                continue
            if r is None or r["n_int_lat"] < 1: continue
            nint += 1
            r.update(lam=lam, mu=mu, nu=nu)
            r["opt_margin"] = r["D"] + 1 - r["n_bdy_lat"]
            fh.write(json.dumps(r) + "\n")
            if best is None or r["opt_margin"] > best["opt_margin"]:
                best = r
    sys.stderr.write("with interior-candidate: %d  best_opt_margin=%s\n" %
                     (nint, json.dumps(best) if best else "none"))
