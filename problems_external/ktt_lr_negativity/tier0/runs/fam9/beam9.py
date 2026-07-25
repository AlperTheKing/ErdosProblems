#!/usr/bin/env python3
"""fam9 -- BEAM SEARCH minimising Sum h* subject to h*_d >= 1.

Independent seed (rng 9009) and mutation law.  Sampled, NOT exhaustive.

Two populations are carried:
  POP_I  records with h*_d >= 1 (an interior lattice point exists)
         score = (hstar_sum, h*_1 - h*_d)          -> minimise volume
  POP_B  records with h*_d == 0 and d >= 3         (TIER0-adjacent boundary)
         score = (h*_1, hstar_sum)                 -> drive h*_1 to 0

Tracked: max h*_d, min (h*_1 - h*_d), every TIER0 / JACKPOT / NEG triple.
"""
import json, random, subprocess, sys, os, time, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "..", "..", "tier0_screen.py")

rng = random.Random(9009)


# ---------------------------------------------------------------- triples
def norm(p):
    p = [x for x in p if x > 0]
    return tuple(sorted(p, reverse=True))


def valid(lam, mu, nu):
    if not nu:
        return False
    r = len(nu)
    if r < 5:
        return False
    if len(lam) > r or len(mu) > r:
        return False
    if not lam or not mu:
        return False
    if sum(lam) + sum(mu) != sum(nu):
        return False
    # trivial necessary conditions for c > 0
    if nu[0] < lam[0] or nu[0] < mu[0]:
        return False
    return True


def key(lam, mu, nu):
    a, b = (lam, mu) if lam >= mu else (mu, lam)
    return (a, b, nu)


def fmt(t):
    lam, mu, nu = t
    return "%s;%s;%s" % (",".join(map(str, lam)),
                         ",".join(map(str, mu)),
                         ",".join(map(str, nu)))


# ---------------------------------------------------------------- seeds
def seed_pool(n_target):
    """Independent seed: nu = lam + mu componentwise, then k dominance-lowering
    box moves inside nu (row i -> row j>i).  Guarantees nu in the right size
    class and biases towards the LR support interior."""
    out = set()
    tries = 0
    while len(out) < n_target and tries < 60 * n_target:
        tries += 1
        r = rng.choice([5, 5, 5, 5, 6])
        # lam, mu drawn as partitions with at most r parts, small entries
        mx = rng.choice([2, 3, 3, 4, 5, 6])
        la = norm([rng.randint(0, mx) for _ in range(rng.randint(2, r))])
        mb = norm([rng.randint(0, mx) for _ in range(rng.randint(2, r))])
        if not la or not mb:
            continue
        nu = [0] * r
        for i, v in enumerate(la):
            nu[i] += v
        for i, v in enumerate(mb):
            nu[i] += v
        # dominance-lowering moves
        for _ in range(rng.randint(0, 3 * r)):
            i = rng.randrange(r - 1)
            j = rng.randrange(i + 1, r)
            if nu[i] - 1 >= (nu[i + 1] if i + 1 < r else 0) and nu[i] - 1 >= 0:
                cand = list(nu)
                cand[i] -= 1
                cand[j] += 1
                if all(cand[k] >= cand[k + 1] for k in range(r - 1)) and cand[-1] >= 0:
                    nu = cand
        nu = tuple(nu)
        if len(nu) != r or nu[-1] < 0:
            continue
        if any(nu[k] < nu[k + 1] for k in range(r - 1)):
            continue
        if nu[-1] == 0:
            continue
        t = (la, mb, nu)
        if valid(*t):
            out.add(key(*t))
    return list(out)


# ---------------------------------------------------------------- mutation
def mutate(t):
    """my mutation law: 6 moves, each preserving |lam|+|mu| = |nu|."""
    lam, mu, nu = list(t[0]), list(t[1]), list(t[2])
    r = len(nu)
    m = rng.randrange(6)
    try:
        if m == 0:                       # nu box move (dominance)
            i = rng.randrange(r)
            j = rng.randrange(r)
            if i == j:
                return None
            nu[i] -= 1
            nu[j] += 1
        elif m == 1:                     # grow lam and nu together
            i = rng.randrange(len(lam) + 1)
            j = rng.randrange(r)
            if i == len(lam):
                lam.append(1)
            else:
                lam[i] += 1
            nu[j] += 1
        elif m == 2:                     # shrink lam and nu together
            i = rng.randrange(len(lam))
            j = rng.randrange(r)
            lam[i] -= 1
            nu[j] -= 1
        elif m == 3:                     # grow mu and nu together
            i = rng.randrange(len(mu) + 1)
            j = rng.randrange(r)
            if i == len(mu):
                mu.append(1)
            else:
                mu[i] += 1
            nu[j] += 1
        elif m == 4:                     # shrink mu and nu together
            i = rng.randrange(len(mu))
            j = rng.randrange(r)
            mu[i] -= 1
            nu[j] -= 1
        else:                            # transfer a box lam <-> mu
            if rng.random() < 0.5:
                lam, mu = mu, lam
            i = rng.randrange(len(lam))
            j = rng.randrange(len(mu) + 1)
            lam[i] -= 1
            if j == len(mu):
                mu.append(1)
            else:
                mu[j] += 1
    except (IndexError, ValueError):
        return None
    if any(x < 0 for x in nu) or any(x < 0 for x in lam) or any(x < 0 for x in mu):
        return None
    nu = [x for x in nu if x > 0]
    nu = tuple(sorted(nu, reverse=True))
    la = norm(lam)
    mb = norm(mu)
    t2 = (la, mb, nu)
    if not valid(*t2):
        return None
    return key(*t2)


# ---------------------------------------------------------------- screen
def screen(triples, tag):
    if not triples:
        return []
    path = os.path.join(HERE, "_batch_%s.txt" % tag)
    with open(path, "w") as f:
        for t in triples:
            f.write(fmt(t) + "\n")
    p = subprocess.run([sys.executable, SCREEN, "--batch", path],
                       capture_output=True, text=True)
    recs = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
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


# ---------------------------------------------------------------- main
def main():
    t_end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 3000)
    seen = set()
    tested = 0
    stats = {}
    best_hd = (-1, None)
    best_margin = (10 ** 9, None)
    nonlattice = 0          # d < D = (r-1)(r-2)/2  ->  provably not full-dim
    hits = []
    pop_i = []              # [(score, triple, rec-lite)]
    pop_b = []
    margin_hist = {}

    def absorb(recs):
        nonlocal tested, best_hd, best_margin, nonlattice
        new_i, new_b = [], []
        for rec in recs:
            tested += 1
            st = rec.get("status")
            stats[st] = stats.get(st, 0) + 1
            if st != "OK":
                continue
            d = rec["d"]
            r = rec["r"]
            D = (r - 1) * (r - 2) // 2
            if d < D:
                nonlattice += 1
            h1 = rec["hstar_1"]
            hd = rec["hstar_d"]
            t = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
            if hd is not None and hd > best_hd[0]:
                best_hd = (hd, t)
            if d >= 2 and h1 is not None and hd is not None:
                mrg = h1 - hd
                margin_hist[mrg] = margin_hist.get(mrg, 0) + 1
                if mrg < best_margin[0]:
                    best_margin = (mrg, t, rec["hstar"], d, rec["c"])
            if rec.get("TIER0") or rec.get("JACKPOT") or rec.get("NEG"):
                hits.append(rec)
                print("!!! HIT", rec.get("TIER0"), rec.get("JACKPOT"),
                      rec.get("NEG"), t, rec["hstar"], flush=True)
            # POP_I : the mandated family -- interior point present, minimise
            # Sum h*.  POP_A (carried in new_b) : minimise the margin h*_1-h*_d
            # at d >= 4, tie-broken towards more interior points and larger d.
            if hd is not None and hd >= 1 and d >= 2:
                new_i.append(((rec["hstar_sum"], h1 - hd, -d), t))
            if d >= 4 and h1 is not None and hd is not None:
                new_b.append(((h1 - hd, -hd, rec["hstar_sum"], -d, sum(rec["nu"])), t))
        return new_i, new_b

    # ---- generation 0
    seeds = seed_pool(3000)
    seeds = [s for s in seeds if s not in seen]
    for s in seeds:
        seen.add(s)
    print("seeds", len(seeds), flush=True)
    for i in range(0, len(seeds), 400):
        ni, nb = absorb(screen(seeds[i:i + 400], "g0_%d" % i))
        pop_i += ni
        pop_b += nb
    pop_i = dedup(sorted(pop_i, key=lambda x: x[0]))[:150]
    pop_b = dedup(sorted(pop_b, key=lambda x: x[0]))[:250]
    print("gen0 tested", tested, stats, "popI", len(pop_i), "popB", len(pop_b),
          "bestmargin", best_margin[0], "besthd", best_hd[0], flush=True)

    gen = 0
    while time.time() < t_end:
        gen += 1
        parents = [t for _, t in pop_i] * 2 + [t for _, t in pop_b]
        if not parents:
            parents = seed_pool(200)
        batch = []
        guard = 0
        while len(batch) < 700 and guard < 40000:
            guard += 1
            p = parents[rng.randrange(len(parents))]
            c = p
            for _ in range(rng.choice([1, 1, 1, 2, 2, 3])):
                c2 = mutate(c)
                if c2 is None:
                    break
                c = c2
            else:
                if c not in seen:
                    seen.add(c)
                    batch.append(c)
        # 15% fresh blood
        fresh = [s for s in seed_pool(120) if s not in seen]
        for s in fresh:
            seen.add(s)
        batch += fresh
        ni, nb = absorb(screen(batch, "g%d" % gen))
        pop_i = dedup(sorted(pop_i + ni, key=lambda x: x[0]))[:150]
        pop_b = dedup(sorted(pop_b + nb, key=lambda x: x[0]))[:250]
        if gen % 5 == 0 or gen < 4:
            print("gen%d tested=%d popI=%d popB=%d bestI=%s bestA=%s "
                  "bestHd=%s minMargin=%s hits=%d" %
                  (gen, tested, len(pop_i), len(pop_b),
                   pop_i[0][0] if pop_i else None,
                   pop_b[0][0] if pop_b else None,
                   best_hd[0], best_margin[0], len(hits)), flush=True)

    out = {
        "family": "fam9: beam search minimising Sum h* subject to h*_d >= 1 "
                  "(sampled, NOT exhaustive)",
        "seed": 9009,
        "generations": gen,
        "triplesTested": tested,
        "status_counts": stats,
        "bestHstarD": {"value": best_hd[0],
                       "triple": [list(x) for x in best_hd[1]] if best_hd[1] else None},
        "minH1MinusHD": {"value": best_margin[0],
                         "triple": [list(x) for x in best_margin[1]] if len(best_margin) > 1 and best_margin[1] else None,
                         "hstar": best_margin[2] if len(best_margin) > 2 else None,
                         "d": best_margin[3] if len(best_margin) > 3 else None,
                         "c": best_margin[4] if len(best_margin) > 4 else None},
        "margin_histogram": {str(k): v for k, v in sorted(margin_hist.items())},
        "nonFullDimCount": nonlattice,
        "hits": hits,
        "topI": [[list(s), [list(x) for x in t]] for s, t in pop_i[:25]],
        "topB": [[list(s), [list(x) for x in t]] for s, t in pop_b[:25]],
    }
    with open(os.path.join(HERE, "beam9_result.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in
                      ("triplesTested", "status_counts", "bestHstarD",
                       "minH1MinusHD", "nonFullDimCount", "margin_histogram")},
                     indent=1))
    print("hits", len(hits))


if __name__ == "__main__":
    main()
