#!/usr/bin/env python3
"""Hill-climb directly on the EXACT negativity criterion.

Objective (smaller is better):
    ratio = <u^2> / ((d+1)/3)      with u_j = 2j-(d+1), <.> the h*-average.
`ratio < 1`  <=>  a_{d-2} < 0  <=>  KTT is false.
We also report min_k a_k exactly; ANY negative value is an outright hit.

Moves: single-box and coupled two-box perturbations of (lam, mu, nu) that keep
all three weakly decreasing and |lam|+|mu| = |nu|.
"""
import argparse
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ehr import ehrhart  # noqa: E402


def ok_part(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and (not p or p[-1] >= 0)


def score(lam, mu, nu, volcap, seed=3):
    try:
        r = ehrhart(lam, mu, nu, seed=seed, vol_cap=volcap)
    except Exception:
        return None
    if r["status"] != "OK" or r["d"] < 2:
        return None
    r["lam"], r["mu"], r["nu"] = list(lam), list(mu), list(nu)
    d = r["d"]
    hs = r["hstar"]
    tot = sum(hs)
    if tot <= 0:
        return None
    m2 = Fraction(sum(hs[j] * (2 * j - d - 1) ** 2 for j in range(d + 1)), tot)
    ratio = m2 / Fraction(d + 1, 3)
    minc = min(Fraction(x) for x in r["coeffs"])
    # scale-free per-coefficient margin:  a_{d-k} = (1/d!) sum_j h*_j E_k(d-j)
    # with E_k(m) = e_k(m, m-1, ..., m-d+1).
    marg = []
    for k in range(1, d + 1):
        S = 0
        T = 0
        for j in range(d + 1):
            if hs[j] == 0:
                continue
            e = elem_sym(d - j, d, k)
            S += hs[j] * e
            T += hs[j] * abs(e)
        if T:
            marg.append(Fraction(S, T))
    mm = min(marg) if marg else Fraction(1)
    # DILATION-INVARIANT objective: b_k = a_k / vol^(k/d).  Q(a*lam,a*mu,a*nu)
    # = a*Q, so a_k -> a^k a_k and vol -> a^d vol; b_k is therefore constant
    # along a ray and its SIGN is exactly the sign of a_k.
    import math
    cf = [Fraction(x) for x in r["coeffs"]]
    vol = cf[d]
    bs = []
    for k in range(1, d):
        bs.append(float(cf[k]) / (float(vol) ** (k / d)))
    r["binv"] = min(bs) if bs else 1.0
    r["ratio"] = float(ratio)
    r["minc"] = str(minc)
    r["minc_f"] = float(minc)
    r["mrel"] = float(mm)
    r["obj"] = r["binv"]
    r["nvol"] = tot
    return r


_ES = {}


def elem_sym(m, d, k):
    """e_k(m, m-1, ..., m-d+1) exactly."""
    key = (m, d)
    ev = _ES.get(key)
    if ev is None:
        ev = [1] + [0] * d
        for i in range(d):
            x = m - i
            for t in range(d, 0, -1):
                ev[t] += ev[t - 1] * x
        _ES[key] = ev
    return ev[k]


def neighbours(lam, mu, nu, rng, k=40):
    out = []
    for _ in range(k):
        L, M, N = list(lam), list(mu), list(nu)
        kind = rng.randrange(5)
        if kind == 0:            # move a box inside nu
            i, j = rng.randrange(len(N)), rng.randrange(len(N))
            if i == j:
                continue
            N[i] -= 1
            N[j] += 1
        elif kind == 1:          # move a box inside lam, compensate in nu
            i, j = rng.randrange(len(L)), rng.randrange(len(N))
            L[i] -= 1
            N[j] -= 1
        elif kind == 2:
            i, j = rng.randrange(len(L)), rng.randrange(len(N))
            L[i] += 1
            N[j] += 1
        elif kind == 3:
            i, j = rng.randrange(len(M)), rng.randrange(len(N))
            M[i] += 1
            N[j] += 1
        else:
            i, j = rng.randrange(len(M)), rng.randrange(len(N))
            M[i] -= 1
            N[j] -= 1
        L = [x for x in L if x > 0]
        M = [x for x in M if x > 0]
        if not L or not M or min(N) < 0:
            continue
        if not (ok_part(L) and ok_part(M) and ok_part(N)):
            continue
        if sum(L) + sum(M) != sum(N):
            continue
        if len(L) > len(N) or len(M) > len(N):
            continue
        out.append((L, M, N))
    return out


def climb(lam, mu, nu, rng, volcap, steps=300, log=None):
    cur = score(lam, mu, nu, volcap)
    if cur is None:
        return None
    best = cur
    for _ in range(steps):
        cands = neighbours(cur["lam"], cur["mu"], cur["nu"], rng)
        improved = None
        for L, M, N in cands:
            s = score(L, M, N, volcap)
            if s is None:
                continue
            if s["minc_f"] < 0:
                print("!!! NEGATIVE COEFFICIENT", json.dumps(s), flush=True)
                return s
            if s["obj"] < cur["obj"] - 1e-12:
                if improved is None or s["obj"] < improved["obj"]:
                    improved = s
        if improved is None:
            break
        cur = improved
        if cur["obj"] < best["obj"]:
            best = cur
            if log:
                log.write(json.dumps(best) + "\n")
                log.flush()
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=5)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--hi", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--volcap", type=int, default=400000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    log = open(a.out, "a") if a.out else None
    globalbest = None
    done = 0
    attempts = 0
    while done < a.restarts and attempts < 400 * a.restarts:
        attempts += 1
        r = a.r
        lam = sorted((rng.randint(1, a.hi) for _ in range(rng.randint(2, r))), reverse=True)
        mu = sorted((rng.randint(1, a.hi) for _ in range(rng.randint(2, r))), reverse=True)
        W = sum(lam) + sum(mu)
        L = lam + [0] * (r - len(lam))
        M = mu + [0] * (r - len(mu))
        nu = [L[i] + M[i] for i in range(r)]
        for _ in range(rng.randrange(1, 12)):
            i = rng.randrange(r - 1)
            j = rng.randrange(i + 1, r)
            cand = nu[:]
            cand[i] -= 1
            cand[j] += 1
            if all(cand[k] >= cand[k + 1] for k in range(r - 1)) and cand[-1] >= 0:
                nu = cand
        b = climb(lam, mu, nu, rng, a.volcap, steps=a.steps, log=log)
        if b is None:
            continue
        done += 1
        if b["minc_f"] < 0:
            print("HIT", json.dumps(b), flush=True)
            return
        if globalbest is None or b["obj"] < globalbest["obj"]:
            globalbest = b
            print("best so far binv=%.5f ratio=%.3f d=%d c=%d V=%d minc=%s h*=%s  %s %s %s"
                  % (b["obj"], b["ratio"], b["d"], b["c"], b["nvol"], b["minc"], b["hstar"],
                     b["lam"], b["mu"], b["nu"]), flush=True)
    print("FINAL", json.dumps(globalbest) if globalbest else "none")


if __name__ == "__main__":
    main()
