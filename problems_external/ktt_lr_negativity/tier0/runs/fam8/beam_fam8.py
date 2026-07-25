#!/usr/bin/env python
"""fam8 = BEAM SEARCH maximising fitness = h*_d - h*_1  (JACKPOT iff > 0).

Single-box mutations on (lam,mu,nu) preserving |lam|+|mu|=|nu|.
Seeds: the verified half-integral refuter family (h*=(1,0,1,0,0), margin 0)
plus every margin-0 near miss mined from prior campaign records.

All screening is delegated to the mandated LP-free instrument
tier0_screen.py (engine A profile, exact interpolation, two held-out
points, exact h*).  No LP oracle, no simplex filter anywhere.

COST filter (declared, not a mathematical verdict): candidates whose
c = c(nu;lam,mu) exceeds CMAX are full-screened only with probability
SAMPLE_ABOVE, because the D+3-point profile cost grows like c.
"""
import json, os, random, subprocess, sys, time, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "..", "..", "tier0_screen.py")
SCREEN = os.path.normpath(SCREEN)
PY = sys.executable

OUT = os.path.join(HERE, "fam8_records.jsonl")
LOG = os.path.join(HERE, "fam8_beam.log")
STATE = os.path.join(HERE, "fam8_state.json")

POP = 40
CMAX = 400
SAMPLE_ABOVE = 0.05
NU_MAX = 30
R_MIN, R_MAX = 5, 7
GEN_BUDGET_S = float(os.environ.get("FAM8_BUDGET", "2400"))

SEEDS = [
    ([2, 2, 1], [4, 3, 2, 1], [5, 4, 3, 2, 1]),
    ([2, 2, 1], [9, 3, 2, 1], [10, 4, 3, 2, 1]),
    ([2, 2, 1], [5, 4, 3, 2, 1], [6, 5, 4, 3, 2]),
    ([6, 4, 3, 2], [2, 2, 1], [7, 5, 4, 3, 1]),
    ([7, 4, 3, 1], [2, 2, 1], [8, 5, 4, 2, 1]),
    ([7, 5, 2, 1], [2, 2, 1], [8, 6, 3, 2, 1]),
    ([2, 2, 1], [8, 4, 2, 1], [9, 5, 3, 2, 1]),
    ([6, 5, 3, 1], [2, 2, 1], [7, 6, 4, 2, 1]),
    ([4, 3, 2, 1], [2, 2, 2, 1], [5, 4, 3, 2, 2, 1]),
    ([2, 2, 1], [6, 4, 2, 1, 1], [7, 5, 3, 2, 1, 1]),
    ([7, 3, 2, 1, 1], [2, 2, 1], [8, 4, 3, 2, 1, 1]),
    ([5, 4, 2, 1, 1], [2, 2, 1], [6, 5, 3, 2, 1, 1]),
    ([2, 2, 1], [4, 3, 2, 2, 1], [5, 4, 3, 2, 2, 1]),
    ([5, 4, 3, 1, 1], [2, 2, 1], [6, 5, 4, 2, 1, 1]),
    ([2, 2, 1], [5, 4, 2, 1, 1], [6, 5, 3, 2, 1, 1]),
    ([6, 4, 3, 1, 1], [2, 2, 1], [7, 5, 4, 2, 1, 1]),
]


def norm(p):
    p = [x for x in p if x > 0]
    return p


def ok_part(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and all(x > 0 for x in p)


def valid(lam, mu, nu):
    lam, mu, nu = norm(lam), norm(mu), norm(nu)
    if not (lam and mu and nu):
        return None
    if not (ok_part(lam) and ok_part(mu) and ok_part(nu)):
        return None
    r = len(nu)
    if not (R_MIN <= r <= R_MAX):
        return None
    if len(lam) > r or len(mu) > r:
        return None
    if sum(lam) + sum(mu) != sum(nu):
        return None
    if sum(nu) > NU_MAX:
        return None
    return (tuple(lam), tuple(mu), tuple(nu))


def bump(p, i, delta):
    q = list(p)
    while len(q) <= i:
        q.append(0)
    q[i] += delta
    return q


def mutations(t, rng, k=24):
    lam, mu, nu = [list(x) for x in t]
    out = []
    # (A) move a single box inside nu
    for i in range(len(nu) + 1):
        for j in range(len(nu)):
            if i == j:
                continue
            v = valid(lam, mu, bump(bump(nu, i, 1), j, -1))
            if v:
                out.append(v)
    # (B/C/D) single box added to / removed from lam or mu, matched in nu
    for which in (0, 1):
        base = lam if which == 0 else mu
        for i in range(len(base) + 1):
            for s in (1, -1):
                nb = bump(base, i, s)
                for j in range(len(nu) + (1 if s > 0 else 0)):
                    nn = bump(nu, j, s)
                    v = valid(nb, mu, nn) if which == 0 else valid(lam, nb, nn)
                    if v:
                        out.append(v)
    rng.shuffle(out)
    return out[:k]


def run(cmd, inp_lines, path, timeout):
    with open(path, "w") as f:
        f.write("\n".join(inp_lines) + "\n")
    try:
        p = subprocess.run(cmd + [path], capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return []
    recs = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            recs.append(json.loads(line))
        except Exception:
            pass
    return recs


def fmt(t):
    return ";".join(",".join(str(x) for x in part) for part in t)


def key(t):
    return fmt(t)


def main():
    rng = random.Random(8)
    t0 = time.time()
    seen = set()
    pop = []
    for s in SEEDS:
        v = valid(list(s[0]), list(s[1]), list(s[2]))
        if v:
            pop.append(v)
            seen.add(key(v))
    out = open(OUT, "a")
    log = open(LOG, "a")

    best_hd = (-1, None)
    best_fit = (-10**9, None)
    min_margin = (10**9, None)   # min of h*_1 - h*_d
    hits = []
    tested = 0
    nonlattice = 0
    gen = 0

    def emit(msg):
        log.write(msg + "\n")
        log.flush()
        print(msg, flush=True)

    emit("### fam8 beam start %s screen=%s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), SCREEN))

    while time.time() - t0 < GEN_BUDGET_S:
        gen += 1
        cands = []
        for t in pop:
            for m in mutations(t, rng, k=max(6, 240 // max(1, len(pop)))):
                if key(m) not in seen:
                    seen.add(key(m))
                    cands.append(m)
        if not cands:
            emit("gen %d: no new candidates; injecting random restarts" % gen)
            for _ in range(200):
                s = rng.choice(SEEDS)
                t = valid(list(s[0]), list(s[1]), list(s[2]))
                for _ in range(rng.randint(1, 6)):
                    ms = mutations(t, rng, k=40)
                    if not ms:
                        break
                    t = rng.choice(ms)
                if t and key(t) not in seen:
                    seen.add(key(t))
                    cands.append(t)
            if not cands:
                emit("gen %d: exhausted mutation ball; stop" % gen)
                break
        rng.shuffle(cands)
        cands = cands[:260]

        pf = run([PY, SCREEN, "--prefilter"], [fmt(c) for c in cands],
                 os.path.join(HERE, "_pf.batch"), 600)
        pf = [r for r in pf if r.get("mode") == "prefilter"] or pf
        keep = []
        cost_skipped = 0
        for r in pf:
            t = (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
            c = r.get("c")
            if c is None or c == 0:
                continue
            if c <= CMAX or rng.random() < SAMPLE_ABOVE:
                keep.append(t)
            else:
                cost_skipped += 1
        if not keep:
            emit("gen %d: 0 keep (prefilter %d)" % (gen, len(pf)))
            continue

        recs = run([PY, SCREEN, "--batch"], [fmt(t) for t in keep],
                   os.path.join(HERE, "_full.batch"), 900)
        okrecs = []
        for r in recs:
            out.write(json.dumps(r) + "\n")
            tested += 1
            if r.get("status") != "OK":
                continue
            okrecs.append(r)
            d = r.get("d")
            h1, hd = r.get("hstar_1"), r.get("hstar_d")
            if h1 is None or hd is None or d is None or d < 1:
                continue
            if hd > best_hd[0]:
                best_hd = (hd, r)
            fit = hd - h1
            if fit > best_fit[0]:
                best_fit = (fit, r)
            if h1 - hd < min_margin[0]:
                min_margin = (h1 - hd, r)
            if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG"):
                hits.append(r)
                emit("!!! HIT %s TIER0=%s JACKPOT=%s NEG=%s h*=%s" %
                     (fmt((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))),
                      r.get("TIER0"), r.get("JACKPOT"), r.get("NEG"), r.get("hstar")))
                with open(os.path.join(HERE, "HITS.jsonl"), "a") as hf:
                    hf.write(json.dumps(r) + "\n")
        out.flush()

        # selection
        def fkey(r):
            h1, hd, d = r["hstar_1"], r["hstar_d"], r["d"]
            return (hd - h1, hd, -h1, -r.get("hstar_sum", 0), rng.random())
        def tkey(r):
            # track B: among polytopes that HAVE interior lattice points,
            # push h*_1 (= boundary-deficiency) down.
            return (1 if r["hstar_d"] > 0 else 0, -r["hstar_1"], r["hstar_d"], rng.random())
        pool = [r for r in okrecs if r.get("hstar_1") is not None and r.get("d", 0) >= 2]
        A = sorted(pool, key=fkey, reverse=True)
        B = sorted(pool, key=tkey, reverse=True)
        tri = lambda r: (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
        newpop, sset = [], set()
        for r in A[:POP // 2] + B[:POP // 4]:
            if key(tri(r)) not in sset:
                sset.add(key(tri(r)))
                newpop.append(tri(r))
        rest = pool[:]
        rng.shuffle(rest)
        for r in rest:
            if len(newpop) >= POP:
                break
            if key(tri(r)) not in sset:
                sset.add(key(tri(r)))
                newpop.append(tri(r))
        if newpop:
            # keep a few elite parents so the beam cannot regress
            pop = (newpop + pop)[:POP]
        emit("gen %d t=%.0fs cand=%d kept=%d costskip=%d tested=%d OK=%d "
             "bestfit=%d best_hd=%d minmargin=%d hits=%d pop=%d" %
             (gen, time.time() - t0, len(cands), len(keep), cost_skipped, tested,
              len(okrecs), best_fit[0], best_hd[0], min_margin[0], len(hits), len(pop)))
        json.dump({"gen": gen, "tested": tested, "best_fit": best_fit[0],
                   "best_hd": best_hd[0], "min_margin": min_margin[0],
                   "hits": len(hits), "seen": len(seen)}, open(STATE, "w"))

    def strip(r):
        if r is None:
            return None
        return {k: r.get(k) for k in ("lam", "mu", "nu", "r", "d", "c", "hstar",
                                      "hstar_sum", "hstar_1", "hstar_d", "INTERIOR",
                                      "TIER0", "JACKPOT", "NEG", "coeffs_low_to_high",
                                      "degree_bound")}
    summary = {"family": "fam8 beam-search on h*_d - h*_1",
               "generations": gen, "tested": tested, "seen": len(seen),
               "best_fit": best_fit[0], "best_fit_triple": strip(best_fit[1]),
               "best_hd": best_hd[0], "best_hd_triple": strip(best_hd[1]),
               "min_h1_minus_hd": min_margin[0],
               "min_margin_triple": strip(min_margin[1]),
               "hits": [strip(h) for h in hits]}
    json.dump(summary, open(os.path.join(HERE, "fam8_summary.json"), "w"), indent=1)
    emit("### done " + json.dumps({k: summary[k] for k in
         ("generations", "tested", "best_fit", "best_hd", "min_h1_minus_hd")}))


if __name__ == "__main__":
    main()
