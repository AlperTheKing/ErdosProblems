#!/usr/bin/env python3
"""Reeve-cell hunt: minimise the dilation-invariant coefficient margin

    binv = min_{1<=k<=d-1}  a_k / V^(k/d)          (V = normalised volume)

over FULL-DIMENSIONAL hive polytopes (dim Q = D := (r-1)(r-2)/2).  binv < 0 is
an outright KTT counterexample; its sign is dilation invariant, so we optimise
over shapes only.  A secondary "spike" reward pushes toward the Reeve regime
c = d+1 (h*_1 = 0) with large V, which is where a middle coefficient can go
negative.

Simulated annealing with box moves; dimension is HELD at full D (moves that
drop the dimension are rejected).
"""
import argparse
import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ehr import ehrhart  # noqa: E402


def ok_part(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and (not p or p[-1] >= 0)


def evaluate(lam, mu, nu, r, volcap):
    D = (r - 1) * (r - 2) // 2
    try:
        res = ehrhart(lam, mu, nu, vol_cap=volcap)
    except Exception:
        return None
    if res["status"] != "OK":
        return None
    d = res["d"]
    if d != D:
        return None
    cf = [Fraction(x) for x in res["coeffs"]]
    vol = cf[d]
    binv = min(float(cf[k]) / (float(vol) ** (k / d)) for k in range(1, d))
    hs = res["hstar"]
    V = sum(hs)
    c = res["c"]
    # exact criterion statistics (F1)
    m1 = Fraction(sum(hs[j] * (2 * j - d - 1) for j in range(d + 1)), V)
    m2 = Fraction(sum(hs[j] * (2 * j - d - 1) ** 2 for j in range(d + 1)), V)
    res["m1"] = float(m1)                    # a_{d-1} < 0  iff  m1 > 0
    res["m2rel"] = float(m2 / Fraction(d + 1, 3))   # a_{d-2} < 0  iff  < 1
    res["binv"] = binv
    res["V"] = V
    res["maxden"] = res.get("maxden", 1)
    res["hstar1"] = c - (d + 1)
    res["hstard"] = hs[d]
    res["lam"], res["mu"], res["nu"] = list(lam), list(mu), list(nu)
    return res


def objective(res):
    # Directly chase the two exact negativity criteria plus deep coeffs.
    # target1 = -m1        (want m1 -> +,  a_{d-1} negative)
    # target2 = m2rel      (want -> below 1, a_{d-2} negative)
    # target3 = binv       (deep coefficients)
    # reward non-lattice vertices (maxden>=2), where lattice inequalities lapse.
    t = min(-res["m1"], res["m2rel"] - 1.0, res["binv"] * 0.5)
    t -= 0.05 * (res["maxden"] - 1)
    t -= 0.03 * res["hstard"]
    return t


def move(lam, mu, nu, rng, r):
    L, M, N = list(lam), list(mu), list(nu)
    for _ in range(1):
        kind = rng.randrange(6)
        if kind == 0:
            i = rng.randrange(len(N) - 1)
            N[i] += 1
            N[rng.randrange(i + 1, len(N))] -= 1
        elif kind == 1:
            i = rng.randrange(len(L))
            j = rng.randrange(len(N))
            L[i] += 1
            N[j] += 1
        elif kind == 2:
            i = rng.randrange(len(L))
            j = rng.randrange(len(N))
            L[i] -= 1
            N[j] -= 1
        elif kind == 3:
            i = rng.randrange(len(M))
            j = rng.randrange(len(N))
            M[i] += 1
            N[j] += 1
        elif kind == 4:
            i = rng.randrange(len(M))
            j = rng.randrange(len(N))
            M[i] -= 1
            N[j] -= 1
        else:  # coupled: grow lam, shrink mu, keep |nu| by moving a box in nu
            i = rng.randrange(len(L))
            j = rng.randrange(len(M))
            a = rng.randrange(len(N))
            b = rng.randrange(len(N))
            L[i] += 1
            M[j] -= 1
            N[a] += 1
            N[b] -= 1
    L = [x for x in L if x > 0]
    M = [x for x in M if x > 0]
    if not L or not M or min(N) < 0:
        return None
    if not (ok_part(L) and ok_part(M) and ok_part(N)):
        return None
    if sum(L) + sum(M) != sum(N):
        return None
    if len(L) > len(N) or len(M) > len(N) or len(N) != r:
        return None
    return L, M, N


def start(rng, r, hi):
    lam = sorted((rng.randint(1, hi) for _ in range(r - 1)), reverse=True)
    mu = sorted((rng.randint(1, hi) for _ in range(r - 1)), reverse=True)
    W = sum(lam) + sum(mu)
    L = lam + [0] * (r - len(lam))
    M = mu + [0] * (r - len(mu))
    nu = [L[i] + M[i] for i in range(r)]
    for _ in range(rng.randrange(1, 3 * r)):
        i = rng.randrange(r - 1)
        j = rng.randrange(i + 1, r)
        cand = nu[:]
        cand[i] -= 1
        cand[j] += 1
        if all(cand[k] >= cand[k + 1] for k in range(r - 1)) and cand[-1] >= 0:
            nu = cand
    return lam, mu, nu


def anneal(rng, r, hi, volcap, iters, log, best_holder):
    for _tries in range(200):
        s = start(rng, r, hi)
        cur = evaluate(*s, r, volcap)
        if cur is not None:
            break
    if cur is None:
        return None
    curobj = objective(cur)
    best = cur
    T0 = 1.5
    for it in range(iters):
        T = T0 * (1 - it / iters) + 0.02
        m = move(cur["lam"], cur["mu"], cur["nu"], rng, r)
        if m is None:
            continue
        cand = evaluate(*m, r, volcap)
        if cand is None:
            continue
        if cand["binv"] < 0 or cand["m1"] > 0 or cand["m2rel"] < 1.0:
            print("!!! NEGATIVE", json.dumps(cand), flush=True)
            best_holder["hit"] = cand
            return cand
        co = objective(cand)
        if co < curobj or rng.random() < math.exp(-(co - curobj) / max(T, 1e-3)):
            cur, curobj = cand, co
        if objective(cand) < objective(best):
            best = cand
            if log:
                log.write(json.dumps(cand) + "\n")
                log.flush()
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=5)
    ap.add_argument("--hi", type=int, default=6)
    ap.add_argument("--restarts", type=int, default=40)
    ap.add_argument("--iters", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--volcap", type=int, default=1500000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    log = open(a.out, "a") if a.out else None
    holder = {}
    gb = None
    for t in range(a.restarts):
        b = anneal(rng, a.r, a.hi, a.volcap, a.iters, log, holder)
        if holder.get("hit"):
            print("HIT", json.dumps(holder["hit"]), flush=True)
            return
        if b is None:
            continue
        if gb is None or objective(b) < objective(gb):
            gb = b
            print("R=%d obj=%.4f m1=%.4f m2rel=%.4f binv=%.3f d=%d c=%d V=%d q=%d h*d=%d h*=%s  %s %s %s"
                  % (a.r, objective(b), b["m1"], b["m2rel"], b["binv"], b["d"], b["c"],
                     b["V"], b["maxden"], b["hstard"], b["hstar"],
                     b["lam"], b["mu"], b["nu"]), flush=True)
    print("FINAL", a.r, json.dumps(gb) if gb else "none")


if __name__ == "__main__":
    main()
