# gt_lr.py — independent ground truth for lr_hive.exe.
# Method: Schur polynomials by exact SSYT monomial expansion in m=8 variables
# (pure Python big-int dicts; NO Littlewood-Richardson rule anywhere, so it is
# independent of the hive model). Product of two Schur polys is decomposed in
# the Schur basis by repeated subtraction at the lex-greatest monomial.
#
# Phase 1: EVERY triple |nu| = |lam|+|mu| <= 8 over ALL partitions (r <= 8)  — exact match required.
# Phase 2: 30 random c=1 triples -> stretched counts identically 1 for n=1..5 (KTW theorem).
#          30 random c=2 triples -> stretched counts exactly n+1 for n=1..5 (Ikenmeyer/Sherman).
# Phase 3: cap semantics + structural-zero edge cases.
# Exit 0 iff every check passes.

import subprocess, sys, random, os
from functools import lru_cache

ENG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lr_hive.exe")
M = 8  # variables; faithful for all partitions with <= 8 parts

@lru_cache(maxsize=None)
def ssyt(shape):
    """dict: weight tuple (len M) -> #SSYT of given shape and weight, entries in 1..M."""
    res = {}
    shape = tuple(shape)
    weight = [0] * M

    def rec(ri, prev):
        if ri == len(shape):
            w = tuple(weight)
            res[w] = res.get(w, 0) + 1
            return
        L = shape[ri]
        row = [0] * L

        def fill(j, lastv):
            if j == L:
                for v in row:
                    weight[v - 1] += 1
                rec(ri + 1, tuple(row))
                for v in row:
                    weight[v - 1] -= 1
                return
            lo = lastv
            if prev is not None:
                lo = max(lo, prev[j] + 1)
            for v in range(lo, M + 1):
                row[j] = v
                fill(j + 1, v)

        fill(0, 1)

    rec(0, None)
    return res

def mul(p, q):
    r = {}
    for w1, c1 in p.items():
        for w2, c2 in q.items():
            w = tuple(a + b for a, b in zip(w1, w2))
            r[w] = r.get(w, 0) + c1 * c2
    return r

def decompose(poly):
    """symmetric poly (weight dict) -> dict partition(tuple, no zeros) -> coeff."""
    poly = {w: c for w, c in poly.items() if c}
    out = {}
    while poly:
        w = max(poly)  # lex-greatest monomial; must be dominant
        c = poly[w]
        assert all(w[i] >= w[i + 1] for i in range(M - 1)), ("non-dominant lead", w)
        assert c > 0, ("negative Schur coeff — internal bug", w, c)
        nu = tuple(x for x in w if x > 0)
        out[nu] = c
        for w2, c2 in ssyt(nu).items():
            nc = poly.get(w2, 0) - c * c2
            if nc:
                poly[w2] = nc
            else:
                poly.pop(w2, None)
    return out

def partitions(s, maxparts):
    def rec(rem, mx, cur):
        if rem == 0:
            yield tuple(cur)
            return
        if len(cur) == maxparts:
            return
        for p in range(min(rem, mx), 0, -1):
            cur.append(p)
            yield from rec(rem - p, p, cur)
            cur.pop()
    yield from rec(s, s, [])

def fmt(p):
    return ",".join(map(str, p)) if p else "0"

def run_batch(lines):
    path = os.path.join(os.path.dirname(ENG), "_gt_batch.tmp")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    r = subprocess.run([ENG, "--batch", path], capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        print("ENGINE FAILED:", r.stderr[:500]); sys.exit(1)
    out = r.stdout.split()
    assert len(out) == len(lines), (len(out), len(lines))
    return out

def main():
    random.seed(20260721)

    # ---------------- Phase 1: exhaustive sweep |nu| <= 8, all r <= 8 ----------------
    P = {s: list(partitions(s, M)) for s in range(1, 9)}
    triples, expect = [], []
    npairs = 0
    for a in range(1, 8):
        for b in range(1, 9 - a):
            for lam in P[a]:
                for mu in P[b]:
                    npairs += 1
                    dec = decompose(mul(ssyt(lam), ssyt(mu)))
                    for nu in P[a + b]:
                        triples.append((lam, mu, nu))
                        expect.append(dec.get(nu, 0))
    lines = [f"{fmt(l)};{fmt(m)};{fmt(n)};1000000000000" for (l, m, n) in triples]
    got = run_batch(lines)
    bad = [(triples[i], expect[i], got[i]) for i in range(len(triples))
           if got[i] != str(expect[i])]
    print(f"PHASE1 sweep: {len(triples)} triples ({npairs} (lam,mu) pairs, m={M} vars), "
          f"mismatches={len(bad)}")
    for t, e, g in bad[:20]:
        print("  MISMATCH", t, "expected", e, "got", g)
    if bad:
        sys.exit(1)

    nonzero = sum(1 for e in expect if e)
    mx = max(expect)
    print(f"  nonzero={nonzero}, zero={len(expect)-nonzero}, max c={mx}")

    # ---------------- Phase 2: stretched c=1 and c=2 spot checks ----------------
    # |nu|<=8 has <30 distinct c=2 triples, so harvest pools from |nu|=9..12 pairs
    # (same independent SSYT ground truth, shuffled deterministically).
    c1 = [triples[i] for i in range(len(triples)) if expect[i] == 1]
    c2 = [triples[i] for i in range(len(triples)) if expect[i] == 2]
    pairs_big = []
    for s in range(9, 13):
        for a in range(1, s):
            b = s - a
            if b < 1 or b > 12:
                continue
            for lam in partitions(a, M):
                for mu in partitions(b, M):
                    pairs_big.append((lam, mu))
    random.shuffle(pairs_big)
    for (lam, mu) in pairs_big:
        if len(c1) >= 200 and len(c2) >= 60:
            break
        dec = decompose(mul(ssyt(lam), ssyt(mu)))
        for nu, c in dec.items():
            if c == 1 and len(c1) < 200:
                c1.append((lam, mu, nu))
            elif c == 2 and len(c2) < 60:
                c2.append((lam, mu, nu))
    print(f"PHASE2 pools: |c1|={len(c1)}, |c2|={len(c2)}")
    s1 = random.sample(c1, 30)
    s2 = random.sample(c2, 30)
    lines2, want2 = [], []
    for (l, m, n) in s1:
        for t in range(1, 6):
            lines2.append(f"{fmt([t*x for x in l])};{fmt([t*x for x in m])};"
                          f"{fmt([t*x for x in n])};1000000000000")
            want2.append("1")
    for (l, m, n) in s2:
        for t in range(1, 6):
            lines2.append(f"{fmt([t*x for x in l])};{fmt([t*x for x in m])};"
                          f"{fmt([t*x for x in n])};1000000000000")
            want2.append(str(t + 1))
    got2 = run_batch(lines2)
    bad2 = [(lines2[i], want2[i], got2[i]) for i in range(len(lines2)) if got2[i] != want2[i]]
    print(f"PHASE2 stretch: 30 c=1 + 30 c=2 triples, n=1..5 -> {len(lines2)} counts, "
          f"mismatches={len(bad2)}")
    for L, w, g in bad2[:20]:
        print("  MISMATCH", L, "expected", w, "got", g)
    if bad2:
        sys.exit(1)

    # ---------------- Phase 3: cap semantics + structural zeros ----------------
    l3 = ["2,1;2,1;3,2,1;1",      # c=2, cap=1  -> CAP_EXCEEDED
          "2,1;2,1;3,2,1;2",      # c=2, cap=2  -> 2
          "1,1,1,1,1;1,1,1;4,4",  # len(lam)>len(nu) -> 0
          "3;2;4",                # sum mismatch -> 0
          "0;0;0",                # empty triple -> 1
          "8,6,4,2;8,6,4,2;9,8,7,6,5,3,2"]  # sum ok (20+20=40): some count, must not error
    want3 = ["CAP_EXCEEDED", "2", "0", "0", "1", None]
    got3 = run_batch(l3)
    ok3 = all(w is None or g == w for g, w in zip(got3, want3)) and got3[5].isdigit()
    print(f"PHASE3 edge cases: got={got3} -> {'PASS' if ok3 else 'FAIL'}")
    if not ok3:
        sys.exit(1)

    print("ALL VALIDATIONS PASSED")

if __name__ == "__main__":
    main()
