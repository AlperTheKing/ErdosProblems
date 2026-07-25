#!/usr/bin/env python3
"""fam9b -- the mandated family proper: BEAM SEARCH minimising Sum h*
subject to h*_d >= 1, i.e. small volume WITH an interior lattice point.

Population = only records with h*_d >= 1 and d >= 2 (a d <= 1 record has
h*_1 = h*_d identically, margin 0 forced, and is excluded by the mandate).
Score = (Sum h*, h*_1 - h*_d, -d).  Sampled, NOT exhaustive.

Seeded from mid-size random triples, which is where interior lattice points
first appear at all (small polytopes have none).
"""
import json, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "..", "..", "tier0_screen.py")
SH = os.environ.get("SH", "b")
rng = random.Random(90090 + int(os.environ.get("SEEDOFF", "0")))


def norm(p):
    return tuple(sorted([x for x in p if x > 0], reverse=True))


def valid(lam, mu, nu):
    if not nu or not lam or not mu:
        return False
    r = len(nu)
    if r < 5 or r > 6:
        return False
    if len(lam) > r or len(mu) > r:
        return False
    if sum(lam) + sum(mu) != sum(nu):
        return False
    if nu[0] < lam[0] or nu[0] < mu[0]:
        return False
    if sum(nu) > 70:
        return False
    return True


def key(lam, mu, nu):
    a, b = (lam, mu) if lam >= mu else (mu, lam)
    return (a, b, nu)


def fmt(t):
    return ";".join(",".join(map(str, p)) for p in t)


def seed_pool(n):
    out = set()
    tries = 0
    while len(out) < n and tries < 80 * n:
        tries += 1
        r = 5 if rng.random() < 0.8 else 6
        mx = rng.randint(3, 16)
        la = norm([rng.randint(1, mx) for _ in range(rng.randint(3, r))])
        mb = norm([rng.randint(1, mx) for _ in range(rng.randint(3, r))])
        nu = [0] * r
        for i, v in enumerate(la):
            nu[i] += v
        for i, v in enumerate(mb):
            nu[i] += v
        for _ in range(rng.randint(2, 8 * r)):
            i = rng.randrange(r - 1)
            j = rng.randrange(i + 1, r)
            c = list(nu)
            c[i] -= 1
            c[j] += 1
            if all(c[k] >= c[k + 1] for k in range(r - 1)) and c[-1] >= 0:
                nu = c
        nu = tuple(nu)
        if nu[-1] <= 0:
            continue
        if valid(la, mb, nu):
            out.add(key(la, mb, nu))
    return list(out)


def mutate(t):
    lam, mu, nu = list(t[0]), list(t[1]), list(t[2])
    r = len(nu)
    m = rng.randrange(7)
    try:
        if m == 0:
            i, j = rng.randrange(r), rng.randrange(r)
            if i == j:
                return None
            nu[i] -= 1
            nu[j] += 1
        elif m == 1:
            i = rng.randrange(len(lam) + 1)
            j = rng.randrange(r)
            if i == len(lam):
                lam.append(1)
            else:
                lam[i] += 1
            nu[j] += 1
        elif m == 2:
            i, j = rng.randrange(len(lam)), rng.randrange(r)
            lam[i] -= 1
            nu[j] -= 1
        elif m == 3:
            i = rng.randrange(len(mu) + 1)
            j = rng.randrange(r)
            if i == len(mu):
                mu.append(1)
            else:
                mu[i] += 1
            nu[j] += 1
        elif m == 4:
            i, j = rng.randrange(len(mu)), rng.randrange(r)
            mu[i] -= 1
            nu[j] -= 1
        elif m == 5:
            if rng.random() < 0.5:
                lam, mu = mu, lam
            i, j = rng.randrange(len(lam)), rng.randrange(len(mu) + 1)
            lam[i] -= 1
            if j == len(mu):
                mu.append(1)
            else:
                mu[j] += 1
        else:                       # flatten a step of nu (make a plateau)
            i = rng.randrange(r - 1)
            if nu[i] > nu[i + 1]:
                delta = nu[i] - nu[i + 1]
                nu[i] -= delta
                j = rng.randrange(r)
                nu[j] += delta
            else:
                return None
    except (IndexError, ValueError):
        return None
    if any(x < 0 for x in nu + lam + mu):
        return None
    nu = tuple(sorted([x for x in nu if x > 0], reverse=True))
    t2 = (norm(lam), norm(mu), nu)
    if not valid(*t2):
        return None
    return key(*t2)


def screen(triples, tag):
    if not triples:
        return []
    path = os.path.join(HERE, "_b9_%s_%s.txt" % (SH, tag))
    with open(path, "w") as f:
        for t in triples:
            f.write(fmt(t) + "\n")
    p = subprocess.run([sys.executable, SCREEN, "--batch", path, "--cap", "2000000"],
                       capture_output=True, text=True)
    recs = []
    for line in p.stdout.splitlines():
        if line.strip().startswith("{"):
            try:
                recs.append(json.loads(line))
            except Exception:
                pass
    try:
        os.remove(path)
    except OSError:
        pass
    return recs


def dedup(pop):
    out, s = [], set()
    for sc, t in pop:
        if t in s:
            continue
        s.add(t)
        out.append((sc, t))
    return out


def main():
    t_end = time.time() + float(sys.argv[1])
    seen = set()
    tested = 0
    stats = {}
    best_hd = (-1, None)
    best_margin = (10 ** 9, None, None, None, None)
    best_margin_int = (10 ** 9, None, None, None, None)   # among h*_d >= 1
    hits = []
    margin_hist = {}
    nonfull = 0
    pop = []
    interior_seen = 0

    def absorb(recs):
        nonlocal tested, best_hd, best_margin, best_margin_int, nonfull, interior_seen
        new = []
        for rec in recs:
            tested += 1
            st = rec.get("status")
            stats[st] = stats.get(st, 0) + 1
            if st != "OK":
                continue
            d, r = rec["d"], rec["r"]
            if d < (r - 1) * (r - 2) // 2:
                nonfull += 1
            h1, hd = rec["hstar_1"], rec["hstar_d"]
            t = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
            if hd is not None and hd > best_hd[0]:
                best_hd = (hd, t)
            if d >= 2 and h1 is not None:
                m = h1 - hd
                margin_hist[m] = margin_hist.get(m, 0) + 1
                if m < best_margin[0]:
                    best_margin = (m, t, rec["hstar"], d, rec["c"])
                if hd >= 1:
                    interior_seen += 1
                    if m < best_margin_int[0]:
                        best_margin_int = (m, t, rec["hstar"], d, rec["c"])
                    new.append(((rec["hstar_sum"], m, -d), t))
            if rec.get("TIER0") or rec.get("JACKPOT") or rec.get("NEG"):
                hits.append(rec)
                print("!!! HIT", t, rec["hstar"], flush=True)
        return new

    gen = 0
    while time.time() < t_end:
        gen += 1
        batch = []
        if pop:
            parents = [t for _, t in pop]
            guard = 0
            while len(batch) < 500 and guard < 30000:
                guard += 1
                c = parents[rng.randrange(len(parents))]
                for _ in range(rng.choice([1, 1, 2, 2, 3, 4])):
                    c2 = mutate(c)
                    if c2 is None:
                        break
                    c = c2
                else:
                    if c not in seen:
                        seen.add(c)
                        batch.append(c)
        fresh = [s for s in seed_pool(500 if not pop else 250) if s not in seen]
        for s in fresh:
            seen.add(s)
        batch += fresh
        new = absorb(screen(batch, "g%d" % gen))
        pop = dedup(sorted(pop + new, key=lambda x: x[0]))[:200]
        if gen % 10 == 0 or gen < 3:
            print("gen%d tested=%d pop=%d best=%s bestHd=%s minMargin=%s "
                  "minMarginInt=%s interiorSeen=%d hits=%d" %
                  (gen, tested, len(pop), pop[0][0] if pop else None,
                   best_hd[0], best_margin[0], best_margin_int[0],
                   interior_seen, len(hits)), flush=True)

    out = {"family": "fam9b: beam min Sum h* s.t. h*_d>=1, d>=2 (sampled)",
           "generations": gen, "triplesTested": tested, "status_counts": stats,
           "interiorRecords_d_ge_2": interior_seen,
           "bestHstarD": {"value": best_hd[0],
                          "triple": [list(x) for x in best_hd[1]] if best_hd[1] else None},
           "minH1MinusHD": {"value": best_margin[0],
                            "triple": [list(x) for x in best_margin[1]] if best_margin[1] else None,
                            "hstar": best_margin[2], "d": best_margin[3], "c": best_margin[4]},
           "minH1MinusHD_amongInterior": {
               "value": best_margin_int[0],
               "triple": [list(x) for x in best_margin_int[1]] if best_margin_int[1] else None,
               "hstar": best_margin_int[2], "d": best_margin_int[3], "c": best_margin_int[4]},
           "margin_histogram": {str(k): v for k, v in sorted(margin_hist.items())},
           "nonFullDimCount": nonfull,
           "top": [[list(s), [list(x) for x in t]] for s, t in pop[:30]],
           "hits": hits}
    with open(os.path.join(HERE, "beam9b_result_%s.json" % SH), "w") as f:
        json.dump(out, f, indent=1)
    print("DONE", tested, "interior", interior_seen, "minMarginInt",
          best_margin_int[0], "hits", len(hits))


if __name__ == "__main__":
    main()
