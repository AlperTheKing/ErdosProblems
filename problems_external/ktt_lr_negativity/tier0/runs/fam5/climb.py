#!/usr/bin/env python
"""fam5 beam search: minimise  h*_1 - h*_d  (distance to JACKPOT) over
SHORT-vs-LONG triples, using ONLY the mandated exact screen for scoring.

Neighbours: +1 on one part of nu and +1 on one part of lam or mu (keeping
|lam|+|mu| = |nu| and partition shape), or -1 on both, or a unit transfer
inside one partition compensated inside nu.  Everything is re-screened
exactly; no float and no LP oracle anywhere.
"""
import os, sys, json, argparse, random, math
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import tier0_screen as T
from drive import stage2_chunk, chunks


def is_part(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and (not p or p[-1] >= 0)


def norm(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def neighbours(tri, wmax):
    lam, mu, nu = [list(x) for x in tri]
    out = []
    for src, si in (("lam", None), ("mu", None)):
        base = lam if src == "lam" else mu
        for i in range(len(base) + 1):
            for dv in (1, -1):
                b = list(base) + ([0] if i == len(base) else [])
                if i >= len(b):
                    continue
                b[i] += dv
                if b[i] < 0 or b[i] > wmax:
                    continue
                if not is_part(b):
                    continue
                bb = norm(b)
                if not bb:
                    continue
                if src == "lam" and not (2 <= len(bb) <= 3):
                    continue
                if src == "mu" and not (4 <= len(bb) <= 7):
                    continue
                for j in range(len(nu) + 1):
                    v = list(nu) + ([0] if j == len(nu) else [])
                    if j >= len(v):
                        continue
                    v[j] += dv
                    if v[j] < 0 or v[j] > wmax + wmax:
                        continue
                    if not is_part(v):
                        continue
                    vv = norm(v)
                    if not (5 <= len(vv) <= 7):
                        continue
                    nl = bb if src == "lam" else lam
                    nm = bb if src == "mu" else mu
                    if sum(nl) + sum(nm) != sum(vv):
                        continue
                    out.append((tuple(nl), tuple(nm), tuple(vv)))
    # unit transfers inside nu (size preserved)
    for i in range(len(nu)):
        for j in range(len(nu)):
            if i == j:
                continue
            v = list(nu)
            v[i] -= 1
            v[j] += 1
            if v[i] < 0:
                continue
            if not is_part(v):
                continue
            vv = norm(v)
            if not (5 <= len(vv) <= 7):
                continue
            out.append((tuple(lam), tuple(mu), tuple(vv)))
    return list(dict.fromkeys(out))


def score(rec):
    """lower is better: (margin, -d)"""
    if rec.get("status") != "OK" or rec.get("hstar_1") is None:
        return (10 ** 6, 0)
    return (rec["hstar_1"] - rec["hstar_d"], -rec["d"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--beam", type=int, default=40)
    ap.add_argument("--fanout", type=int, default=60)
    ap.add_argument("--wmax", type=int, default=30)
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--cap", type=int, default=10 ** 15)
    a = ap.parse_args()
    rng = random.Random(7)

    seeds = []
    for ln in open(a.seeds):
        r = json.loads(ln)
        seeds.append((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"])))
    seen = set(seeds)
    beam = seeds[:a.beam]
    fout = open(a.out, "w")
    best = None
    ex = ProcessPoolExecutor(max_workers=a.workers)
    for rd in range(a.rounds):
        cand = []
        for t in beam:
            nb = neighbours(t, a.wmax)
            rng.shuffle(nb)
            for x in nb[:a.fanout]:
                if x not in seen:
                    seen.add(x)
                    cand.append(x)
        if not cand:
            break
        sys.stderr.write("round %d: %d candidates\n" % (rd, len(cand)))
        parts = chunks([tuple(map(list, c)) for c in cand],
                       max(1, len(cand) // 6 + 1))
        recs = []
        for rr in ex.map(stage2_chunk, [(p, a.cap) for p in parts]):
            recs.extend(rr)
        for r in recs:
            fout.write(json.dumps(r) + "\n")
        fout.flush()
        scored = sorted(((score(r), r) for r in recs), key=lambda z: z[0])
        good = [r for s, r in scored if s[0] < 10 ** 6]
        if good:
            s0 = score(good[0])
            if best is None or s0 < best[0]:
                best = (s0, good[0])
            sys.stderr.write("  best this round margin=%s d=%s  overall=%s\n"
                             % (s0[0], -s0[1], best[0]))
        hits = [r for r in recs if r.get("JACKPOT") or r.get("TIER0") or r.get("NEG")]
        if hits:
            sys.stderr.write("  *** HITS %d\n" % len(hits))
        beam = [(tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
                for s, r in scored[:a.beam] if s[0] < 10 ** 6]
        if not beam:
            break
    ex.shutdown()
    fout.close()


if __name__ == "__main__":
    main()
