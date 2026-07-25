#!/usr/bin/env python3
"""Family-7 local descent: starting from interior-positive triples, walk to
neighbours (unit moves inside lam, mu, nu keeping |lam|+|mu|=|nu|) and keep
the smallest c that still has an interior lattice point (h*_d > 0).

Every candidate is decided by the exact tier0 screen (engine A profile,
exact interpolation, two held-out points).  No float decides anything.
"""
import json, subprocess, sys, os, itertools

SCREEN = "E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/tier0_screen.py"
CAP = 10 ** 12


def fmt(p):
    p = [x for x in p if x > 0]
    return ",".join(str(x) for x in p) if p else "0"


def valid(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and all(x >= 0 for x in p)


def neighbours(lam, mu, nu, r):
    """unit moves that preserve |lam|+|mu| = |nu| and partition shape."""
    L = list(lam) + [0] * (r - len(lam))
    M = list(mu) + [0] * (r - len(mu))
    N = list(nu) + [0] * (r - len(nu))
    out = set()
    # (a) move one box inside lam (or inside mu, or inside nu): totals unchanged
    for vec, which in ((L, 0), (M, 1), (N, 2)):
        for i in range(r):
            for j in range(r):
                if i == j:
                    continue
                v = list(vec)
                v[i] -= 1
                v[j] += 1
                if min(v) < 0:
                    continue
                w = sorted(v, reverse=True)
                if w == sorted(vec, reverse=True) and v != vec:
                    pass
                v = w
                trip = [list(L), list(M), list(N)]
                trip[which] = v
                out.add((tuple(trip[0]), tuple(trip[1]), tuple(trip[2])))
    # (b) add a box to lam (or mu) and to nu simultaneously
    for which in (0, 1):
        for i in range(r):
            for j in range(r):
                trip = [list(L), list(M), list(N)]
                trip[which][i] += 1
                trip[2][j] += 1
                trip[which] = sorted(trip[which], reverse=True)
                trip[2] = sorted(trip[2], reverse=True)
                out.add((tuple(trip[0]), tuple(trip[1]), tuple(trip[2])))
    # (c) remove a box from lam (or mu) and from nu simultaneously
    for which in (0, 1):
        for i in range(r):
            for j in range(r):
                trip = [list(L), list(M), list(N)]
                trip[which][i] -= 1
                trip[2][j] -= 1
                if min(trip[which]) < 0 or min(trip[2]) < 0:
                    continue
                trip[which] = sorted(trip[which], reverse=True)
                trip[2] = sorted(trip[2], reverse=True)
                out.add((tuple(trip[0]), tuple(trip[1]), tuple(trip[2])))
    res = []
    for lam2, mu2, nu2 in out:
        nu2s = tuple(x for x in nu2 if x > 0)
        if len(nu2s) != r:
            continue
        if sum(lam2) + sum(mu2) != sum(nu2):
            continue
        if any(lam2[i] > nu2[i] for i in range(r)) or any(mu2[i] > nu2[i] for i in range(r)):
            continue
        res.append((tuple(x for x in lam2 if x > 0), tuple(x for x in mu2 if x > 0), nu2s))
    return res


def screen(batch, tmp):
    with open(tmp + ".batch", "w") as f:
        for lam, mu, nu in batch:
            f.write("%s;%s;%s;%d\n" % (fmt(lam), fmt(mu), fmt(nu), CAP))
    subprocess.run([sys.executable, SCREEN, "--batch", tmp + ".batch",
                    "--out", tmp + ".jsonl"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)
    recs = []
    with open(tmp + ".jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def main():
    starts = json.load(open(sys.argv[1]))
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    tmp = sys.argv[3] if len(sys.argv) > 3 else "_climb"
    best = {}       # d -> (c, rec)
    minmarg = {}    # d -> (margin, rec)
    hits = []
    seen = set()
    frontier = [tuple(map(tuple, s)) for s in starts]
    for rd in range(rounds):
        cand = []
        for lam, mu, nu in frontier:
            r = len(nu)
            for t in neighbours(lam, mu, nu, r):
                if t in seen:
                    continue
                seen.add(t)
                cand.append(t)
        if not cand:
            break
        recs = screen(cand, tmp)
        newfront = []
        for rec in recs:
            if rec.get("status") != "OK":
                continue
            d = rec["d"]
            hd = rec.get("hstar_d")
            h1 = rec.get("hstar_1")
            if d is None or d < 2 or hd is None or h1 is None:
                continue
            marg = h1 - hd
            key = str(d)
            if marg < minmarg.get(key, (10 ** 9,))[0]:
                minmarg[key] = (marg, rec)
            if rec.get("TIER0") or rec.get("JACKPOT") or rec.get("NEG"):
                hits.append(rec)
            if hd > 0:
                cur = best.get(key)
                if cur is None or rec["c"] < cur[0]:
                    best[key] = (rec["c"], rec)
                newfront.append((tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"])))
        # keep the interior-positive frontier with smallest c (per d)
        scored = []
        for rec in recs:
            if rec.get("status") == "OK" and rec.get("hstar_d") and rec["d"] >= 2:
                scored.append((rec["c"], (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))))
        scored.sort()
        frontier = [t for _, t in scored[:40]]
        sys.stderr.write("round %d: %d cand, %d interior-positive, frontier %d\n"
                         % (rd, len(cand), len(scored), len(frontier)))
        if not frontier:
            break
    out = {"n_screened": len(seen),
           "best_c_with_interior": {k: {"c": v[0], "lam": v[1]["lam"], "mu": v[1]["mu"],
                                        "nu": v[1]["nu"], "hstar": v[1]["hstar"],
                                        "hstar_1": v[1]["hstar_1"], "hstar_d": v[1]["hstar_d"],
                                        "margin": v[1]["hstar_1"] - v[1]["hstar_d"]}
                                    for k, v in best.items()},
           "min_margin": {k: {"margin": v[0], "lam": v[1]["lam"], "mu": v[1]["mu"],
                              "nu": v[1]["nu"], "d": v[1]["d"], "c": v[1]["c"],
                              "hstar": v[1]["hstar"]} for k, v in minmarg.items()},
           "hits": hits}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
