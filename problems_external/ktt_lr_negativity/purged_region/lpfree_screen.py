#!/usr/bin/env python3
"""
lpfree_screen.py -- LP-FREE exact screening instrument for the
King-Tollu-Toumazet (KTT) stretched Littlewood-Richardson positivity
conjecture (literature item LR(iv); see Gao, arXiv:2101.00984).

TARGET
------
A counterexample is a triple of partitions (lam, mu, nu) with
|lam| + |mu| = |nu| whose stretched LR polynomial

    P(n) = c(n*nu ; n*lam, n*mu)

has a STRICTLY NEGATIVE monomial coefficient.  P is the Ehrhart polynomial
of the Knutson-Tao hive polytope Q(lam,mu,nu), because the hive constraint
matrix depends only on r = #parts(nu) and the right-hand side is linear and
HOMOGENEOUS in (lam,mu,nu); hence Q(n*lam,n*mu,n*nu) = n*Q exactly.

WHY THIS INSTRUMENT EXISTS (the purged region)
----------------------------------------------
The previous ~4.05e8-triple campaign screened with an LP dimension oracle
(14-25 random objectives) plus a "must be a simplex" filter applied BEFORE
h* was ever computed.  Both are biased.  On

    lam=(2,2,1)  mu=(4,3,2,1)  nu=(5,4,3,2,1)

that oracle reported dim_lo = 3 and maxden = 1, whereas the TRUE values are
dim Q = 4 and maxden = 2; the triple was discarded as "c > dim_lo + 1".
Its true data (both LR engines + direct lattice-point enumeration):
dim 4, c = 5 = dim+1 (so h*_1 = 0), SEVEN vertices (NOT a simplex), two of
them half-integral, h* = (1,0,1,0,0), normalized volume 2,
P(n) = (n+1)(n+2)(n^2+3n+6)/12.  An infinite family works:
lam=(2,2,1), mu=(k,3,2,1), nu=(k+1,4,3,2,1) for every k >= 4.

Also note (this killed the old campaign's other heuristic): Ehrhart
negativity is a LATTICE-polytope phenomenon.  The Reeve tetrahedron
T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)} has ALL vertex denominators 1,
satisfies Stanley's h* >= 0, and still has a strictly negative linear
coefficient for q >= 13.  So large vertex denominators are IRRELEVANT to
coefficient signs and h* >= 0 never blocks negativity.  What negativity
needs is a SPIKY h*-vector: h*_1 tiny, mass in the middle entries
(d=3 needs h* like (1,0,>=12,0), i.e. sum h* >= 13; d=4 the campaign
computed the requirement as h* = (1,0,26,0,0), i.e. sum h* = 27).

THE METHOD (LP-free, no dimension oracle, no simplex test)
----------------------------------------------------------
For each triple:
  1. D = (r-1)(r-2)/2 = number of interior hive vertices = ambient bound,
     so deg P <= D.  (A certified smaller bound may be supplied with
     --dbound; the source is recorded in the output.)
  2. Compute the exact profile P(0), P(1), ..., P(D+2) with engine A
     (batch mode, explicit cap; CAP_EXCEEDED is reported honestly and
     never turned into a math verdict).
  3. Interpolate EXACTLY over Q through the D+1 nodes n = 0..D
     (Newton divided differences, Fractions only).
  4. d = deg P after stripping trailing zero coefficients.
  5. Verify the TWO held-out points n = D+1, D+2 against the polynomial.
  6. h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i),  j = 0..d.
     Cross-check: P(n) = sum_j h*_j C(n+d-j, d) on every computed n, and
     h*_j = 0 for j = d+1, d+2.
  7. Report sum h* (normalized volume), h*_1, the exact monomial
     coefficients, and NEG = true iff some coefficient is strictly negative.

NOTHING IS EVER DISCARDED for "not a simplex" or for a small LP dimension.
All arithmetic is exact (int / Fraction).  No float decides anything.
A negative census is NOT evidence for the conjecture and is never described
as such.

CLI
---
  python lpfree_screen.py --triple "2,2,1" "4,3,2,1" "5,4,3,2,1"
  python lpfree_screen.py --batch <file>        # lines "lam;mu;nu"
  python lpfree_screen.py --reeve 13            # unit-test polytope path
  python lpfree_screen.py --validate            # the 4 mandated validations
Options: --cap N (engine A count cap, default 10**12), --dbound D
(certified degree bound override), --out FILE (JSON lines destination).

One JSON line per triple on stdout.
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENGINE_A = os.path.join(ROOT, "engine", "lr_hive.exe")
ENGINE_B = os.path.join(ROOT, "engine", "engineB_lrrule.py")

DEFAULT_CAP = 10 ** 12


# --------------------------------------------------------------------------
# partitions
# --------------------------------------------------------------------------

def parse_partition(s):
    s = s.strip()
    if s in ("", "0", "-"):
        return ()
    parts = [int(x) for x in s.replace(" ", ",").split(",") if x != ""]
    parts = [p for p in parts if p != 0]
    if any(p < 0 for p in parts):
        raise ValueError("negative part in %r" % s)
    if any(parts[i] < parts[i + 1] for i in range(len(parts) - 1)):
        raise ValueError("not weakly decreasing: %r" % s)
    return tuple(parts)


def fmt_partition(p):
    return ",".join(str(x) for x in p) if p else "0"


def scale(p, n):
    return tuple(n * x for x in p)


# --------------------------------------------------------------------------
# engines
# --------------------------------------------------------------------------

class EngineError(RuntimeError):
    pass


def _run_batch(exe_cmd, lines):
    """Run an engine in batch mode.  Returns a list of raw output strings,
    one per input line (CAP_EXCEEDED / ERROR:... preserved verbatim)."""
    if not lines:
        return []
    fd, path = tempfile.mkstemp(suffix=".batch", prefix="lpfree_", text=True)
    try:
        with os.fdopen(fd, "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        proc = subprocess.run(exe_cmd + ["--batch", path],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise EngineError("engine exit %d: %s" %
                              (proc.returncode, proc.stderr.strip()[:400]))
        out = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip() != ""]
        if len(out) != len(lines):
            raise EngineError("engine returned %d lines for %d inputs"
                              % (len(out), len(lines)))
        return out
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def engineA_batch(jobs, cap=DEFAULT_CAP):
    """jobs: list of (lam, mu, nu).  Returns list of int | 'CAP_EXCEEDED' |
    'ERROR:...' -- never silently coerced."""
    lines = ["%s;%s;%s;%d" % (fmt_partition(l), fmt_partition(m),
                              fmt_partition(v), cap) for (l, m, v) in jobs]
    raw = _run_batch([ENGINE_A], lines)
    return [_coerce(x) for x in raw]


def engineB_batch(jobs, cap=DEFAULT_CAP):
    lines = ["%s;%s;%s;%d" % (fmt_partition(l), fmt_partition(m),
                              fmt_partition(v), cap) for (l, m, v) in jobs]
    raw = _run_batch([sys.executable, ENGINE_B], lines)
    return [_coerce(x) for x in raw]


def _coerce(tok):
    try:
        return int(tok)
    except ValueError:
        return tok


# --------------------------------------------------------------------------
# exact interpolation
# --------------------------------------------------------------------------

def newton_interpolate(nodes):
    """nodes: list of (x, y) with exact Fraction/int entries, distinct x.
    Returns monomial coefficients low-to-high as Fractions (trailing zeros
    stripped)."""
    xs = [Fraction(x) for x, _ in nodes]
    ys = [Fraction(y) for _, y in nodes]
    m = len(xs)
    # divided differences
    coef = list(ys)
    for j in range(1, m):
        for i in range(m - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    # expand Newton form into the monomial basis
    poly = [Fraction(0)]
    for k in range(m - 1, -1, -1):
        # poly <- poly * (x - xs[k]) + coef[k]
        new = [Fraction(0)] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new[i + 1] += c
            new[i] -= c * xs[k]
        new[0] += coef[k]
        poly = new
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_eval(coeffs, x):
    x = Fraction(x)
    acc = Fraction(0)
    for c in reversed(coeffs):
        acc = acc * x + c
    return acc


def poly_degree(coeffs):
    d = len(coeffs) - 1
    while d > 0 and coeffs[d] == 0:
        d -= 1
    if d == 0 and coeffs[0] == 0:
        return -1          # identically zero
    return d


def poly_pretty(coeffs, var="n"):
    d = poly_degree(coeffs)
    if d < 0:
        return "0"
    terms = []
    for k in range(d + 1):
        c = coeffs[k]
        if c == 0:
            continue
        sign = "-" if c < 0 else "+"
        a = abs(c)
        if k == 0:
            body = str(a)
        else:
            p = var if k == 1 else "%s^%d" % (var, k)
            body = p if a == 1 else "%s*%s" % (a, p)
        terms.append((sign, body))
    if not terms:
        return "0"
    s = ("-" if terms[0][0] == "-" else "") + terms[0][1]
    for sign, body in terms[1:]:
        s += " %s %s" % (sign, body)
    return s


# --------------------------------------------------------------------------
# h* machinery  (works on ANY Ehrhart profile -- hives or raw polytopes)
# --------------------------------------------------------------------------

def hstar_from_profile(profile, d, extra=2):
    """h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i), j = 0..d+extra.
    profile: dict n -> exact integer value of P(n), must contain 0..d+extra.
    Returns (hstar[0..d], tail[d+1..d+extra])."""
    vals = []
    for j in range(d + extra + 1):
        acc = 0
        for i in range(j + 1):
            acc += (-1) ** i * math.comb(d + 1, i) * profile[j - i]
        vals.append(acc)
    return vals[:d + 1], vals[d + 1:]


def profile_from_hstar(hstar, d, ns):
    """P(n) = sum_j h*_j * C(n + d - j, d)  -- the round-trip check."""
    out = {}
    for n in ns:
        acc = 0
        for j, h in enumerate(hstar):
            top = n + d - j
            acc += h * (math.comb(top, d) if top >= d else 0)
        out[n] = acc
    return out


# --------------------------------------------------------------------------
# the core screen: an Ehrhart profile -> full verdict record
# --------------------------------------------------------------------------

def screen_profile(profile, D, label=None):
    """profile: dict n -> exact int P(n) for n = 0..D+2 (D = degree bound).
    Pure arithmetic; no LP, no dimension oracle, no simplex test."""
    rec = {}
    if label is not None:
        rec["label"] = label
    rec["degree_bound"] = D
    rec["profile"] = [profile[n] for n in range(D + 3)]

    # Empty hive polytope.  NOTE: engine A returns 1 for the all-empty triple
    # (the LR normalization c(0;0,0)=1), so P(0)=1 even when Q is empty; the
    # emptiness test must therefore look at n >= 1 only.
    if profile[1] == 0:
        nz = [n for n in range(1, D + 3) if profile[n] != 0]
        if not nz:
            rec["status"] = "EMPTY"
            rec["c"] = 0
            rec["d"] = -1
            rec["neg"] = False
            rec["note"] = ("Q empty: c=0 and P(n)=0 for all n in 1..D+2 "
                           "(P(0)=1 is the engine's LR normalization, not an "
                           "Ehrhart value)")
            return rec
        # c = 0 but some dilate is nonzero: that contradicts saturation
        # (Knutson-Tao).  Report it loudly; never tune it away.
        rec["status"] = "SATURATION_ANOMALY"
        rec["c"] = 0
        rec["d"] = None
        rec["neg"] = False
        rec["nonzero_dilates"] = nz
        return rec

    nodes = [(n, profile[n]) for n in range(D + 1)]
    coeffs = newton_interpolate(nodes)
    d = poly_degree(coeffs)

    heldout = []
    ok = True
    for n in (D + 1, D + 2):
        pv = poly_eval(coeffs, n)
        match = (pv == profile[n])
        ok = ok and match
        heldout.append({"n": n, "engine": profile[n],
                        "poly": str(pv), "match": match})
    rec["heldout"] = heldout
    rec["heldout_ok"] = ok

    rec["c"] = profile[1]
    rec["d"] = d
    rec["coeffs_low_to_high"] = [str(c) for c in coeffs]
    rec["poly"] = poly_pretty(coeffs)

    if not ok:
        # deg P > D would be a contradiction of the geometry: report, never hide.
        rec["status"] = "HELDOUT_MISMATCH"
        rec["neg"] = False
        return rec

    hstar, tail = hstar_from_profile(profile, d, extra=min(2, D + 2 - d))
    rec["hstar"] = hstar
    rec["hstar_tail_must_be_zero"] = tail
    rec["hstar_sum"] = sum(hstar)
    rec["hstar_1"] = hstar[1] if d >= 1 else None
    rec["hstar_0_is_1"] = (hstar[0] == 1)
    rec["hstar_nonneg"] = all(h >= 0 for h in hstar)
    rec["hstar_tail_zero"] = all(t == 0 for t in tail)

    rt = profile_from_hstar(hstar, d, range(D + 3))
    rec["hstar_roundtrip_ok"] = all(rt[n] == profile[n] for n in range(D + 3))

    negs = [k for k, c in enumerate(coeffs) if c < 0]
    rec["neg_indices"] = negs
    rec["neg"] = len(negs) > 0
    rec["status"] = "OK"
    return rec


# --------------------------------------------------------------------------
# hive path
# --------------------------------------------------------------------------

def ambient_bound(nu):
    r = len(nu)
    return max(0, (r - 1) * (r - 2) // 2)


def screen_triples(triples, cap=DEFAULT_CAP, dbound=None):
    """triples: list of (lam, mu, nu).  Returns list of JSON-ready records.
    One batched engine-A call for the whole set."""
    jobs = []
    index = []
    meta = []
    for (lam, mu, nu) in triples:
        if dbound is not None:
            D = dbound
            src = "user_certified"
        else:
            D = ambient_bound(nu)
            src = "ambient_(r-1)(r-2)/2"
        meta.append((D, src))
        rng = list(range(D + 3))
        index.append((len(jobs), len(rng)))
        for n in rng:
            jobs.append((scale(lam, n), scale(mu, n), scale(nu, n)))

    vals = engineA_batch(jobs, cap=cap)

    out = []
    for t, (lam, mu, nu) in enumerate(triples):
        D, src = meta[t]
        off, cnt = index[t]
        chunk = vals[off:off + cnt]
        head = {
            "lam": list(lam), "mu": list(mu), "nu": list(nu),
            "r": len(nu), "degree_bound": D, "degree_bound_source": src,
            "cap": cap, "engine": "A:lr_hive.exe",
        }
        bad = [n for n, v in enumerate(chunk) if not isinstance(v, int)]
        if sum(lam) + sum(mu) != sum(nu):
            head["status"] = "SIZE_MISMATCH"
            head["neg"] = False
            head["profile_raw"] = [str(v) for v in chunk]
            out.append(head)
            continue
        if bad:
            head["status"] = "CAP_EXCEEDED"
            head["failed_n"] = bad
            head["profile_raw"] = [str(v) for v in chunk]
            head["neg"] = False
            head["note"] = ("engine returned non-numeric at these n; "
                            "this is a SKIP, never a math verdict")
            out.append(head)
            continue
        profile = {n: chunk[n] for n in range(cnt)}
        rec = screen_profile(profile, D)
        rec.pop("degree_bound", None)
        head.update(rec)
        out.append(head)
    return out


# --------------------------------------------------------------------------
# Reeve tetrahedron -- raw-polytope unit test of the h* machinery
# --------------------------------------------------------------------------

def reeve_count(q, n):
    """|n*T_q cap Z^3| for T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)},
    by exact direct lattice-point enumeration (no Ehrhart theory used).

    (x,y,z) in n*T_q  <=>  x,y >= 0, x+y <= n + z/q, 0 <= z <= q*min(x,y).
    Barycentric: d = z/q, b = x - z/q, c = y - z/q, a = n - x - y + z/q >= 0.
    """
    total = 0
    for x in range(0, n + 1):
        for y in range(0, n + 1):
            lo = max(0, q * (x + y - n))
            hi = q * min(x, y)
            if hi >= lo:
                total += hi - lo + 1
    return total


def reeve_record(q, D=3):
    profile = {n: reeve_count(q, n) for n in range(D + 3)}
    rec = screen_profile(profile, D, label="Reeve_T_%d" % q)
    rec["polytope"] = ("conv{(0,0,0),(1,0,0),(0,1,0),(1,1,%d)} "
                       "(all vertices integral)" % q)
    rec["source"] = "direct lattice-point enumeration"
    return rec


# --------------------------------------------------------------------------
# validations
# --------------------------------------------------------------------------

REFUTER = ((2, 2, 1), (4, 3, 2, 1), (5, 4, 3, 2, 1))
REFUTER_PROFILE = [1, 5, 16, 40, 85, 161, 280, 456, 705]


def _v1_refuter(log):
    rec = screen_triples([REFUTER])[0]
    exp_coeffs = [Fraction(1), Fraction(2), Fraction(17, 12),
                  Fraction(1, 2), Fraction(1, 12)]
    checks = {
        "status_OK": rec["status"] == "OK",
        "profile": rec["profile"] == REFUTER_PROFILE,
        "d_is_4": rec["d"] == 4,
        "c_is_5": rec["c"] == 5,
        "hstar": rec.get("hstar") == [1, 0, 1, 0, 0],
        "hstar_sum_2": rec.get("hstar_sum") == 2,
        "hstar_1_zero": rec.get("hstar_1") == 0,
        "heldout_ok": rec.get("heldout_ok") is True,
        "roundtrip": rec.get("hstar_roundtrip_ok") is True,
        "tail_zero": rec.get("hstar_tail_zero") is True,
        "coeffs_match_(n+1)(n+2)(n^2+3n+6)/12":
            [Fraction(c) for c in rec["coeffs_low_to_high"]] == exp_coeffs,
        "c_equals_d_plus_1": rec["c"] == rec["d"] + 1,
        "not_neg": rec["neg"] is False,
    }
    log("V1 refuter record: " + json.dumps(rec))
    for k, v in checks.items():
        log("V1 %-45s %s" % (k, "PASS" if v else "FAIL"))
    return all(checks.values()), rec


def _v2_family(log, ks=range(4, 10)):
    triples = [((2, 2, 1), (k, 3, 2, 1), (k + 1, 4, 3, 2, 1)) for k in ks]
    recs = screen_triples(triples)
    ok = True
    for k, rec in zip(ks, recs):
        good = (rec["status"] == "OK" and rec["d"] == 4 and rec["c"] == 5
                and rec.get("hstar") == [1, 0, 1, 0, 0]
                and rec.get("hstar_sum") == 2 and rec.get("hstar_1") == 0
                and rec["profile"] == REFUTER_PROFILE
                and rec.get("heldout_ok") is True
                and rec.get("hstar_roundtrip_ok") is True)
        ok = ok and good
        log("V2 k=%d  d=%s c=%s h*=%s sum=%s  %s" %
            (k, rec.get("d"), rec.get("c"), rec.get("hstar"),
             rec.get("hstar_sum"), "PASS" if good else "FAIL"))
        log("V2 k=%d record: %s" % (k, json.dumps(rec)))
    return ok


def _v3_reeve(log, qmax=20):
    ok = True
    neg_seen = {}
    for q in range(1, qmax + 1):
        rec = reeve_record(q)
        hs_exp = [1, 0, q - 1, 0]
        lin = Fraction(rec["coeffs_low_to_high"][1]) if rec["d"] >= 1 else None
        neg = (lin is not None and lin < 0)
        neg_seen[q] = neg
        good = (rec["status"] == "OK" and rec["d"] == 3
                and rec.get("hstar") == hs_exp
                and rec.get("hstar_sum") == q
                and rec.get("heldout_ok") is True
                and rec.get("hstar_roundtrip_ok") is True
                and rec.get("hstar_tail_zero") is True
                and neg == (q >= 13))
        ok = ok and good
        log("V3 q=%2d  h*=%s  vol=%s  lin=%s  neg=%s  %s" %
            (q, rec.get("hstar"), rec.get("hstar_sum"), lin, neg,
             "PASS" if good else "FAIL"))
    log("V3 negative-linear-coefficient q values: %s" %
        [q for q, v in neg_seen.items() if v])
    return ok, neg_seen


def _random_triples(count, seed=20260721, cap=DEFAULT_CAP, log=print):
    """Random triples with |lam|+|mu| = |nu| and c(nu;lam,mu) > 0 (nonzero so
    the A-vs-B agreement test is non-vacuous).  Exhaustive partition lists."""
    rnd = random.Random(seed)

    def partitions(N, maxpart=None, maxlen=None):
        if maxpart is None:
            maxpart = N
        out = []

        def rec(rem, mx, cur):
            if rem == 0:
                out.append(tuple(cur))
                return
            if maxlen is not None and len(cur) >= maxlen:
                return
            for p in range(min(rem, mx), 0, -1):
                cur.append(p)
                rec(rem - p, p, cur)
                cur.pop()
        rec(N, maxpart, [])
        return out

    pool = {}
    triples = []
    tried = 0
    while len(triples) < count and tried < count * 60:
        tried += 1
        a = rnd.randint(1, 7)
        b = rnd.randint(1, 7)
        pa = pool.setdefault((a, 4), partitions(a, maxlen=4))
        pb = pool.setdefault((b, 4), partitions(b, maxlen=4))
        lam = rnd.choice(pa)
        mu = rnd.choice(pb)
        N = a + b
        maxlen = min(len(lam) + len(mu), 5)
        pn = pool.setdefault((N, maxlen), partitions(N, maxlen=maxlen))
        nu = rnd.choice(pn)
        key = (lam, mu, nu)
        if key in {tuple(t) for t in triples}:
            continue
        triples.append((lam, mu, nu))
    # keep only the ones with c > 0 at n=1, then top up
    vals = engineA_batch(triples, cap=cap)
    keep = [t for t, v in zip(triples, vals) if isinstance(v, int) and v > 0]
    return keep[:count], len(keep)


def _v4_cross_engine(log, count=200, seed=20260721):
    triples, avail = _random_triples(count * 3, seed=seed, log=log)
    triples = triples[:count]
    log("V4 sampled %d nonzero random triples (pool %d)" % (len(triples), avail))
    if len(triples) < count:
        log("V4 FAIL: only %d triples available" % len(triples))
        return False
    jobs = []
    for (lam, mu, nu) in triples:
        for n in (1, 2, 3):
            jobs.append((scale(lam, n), scale(mu, n), scale(nu, n)))
    va = engineA_batch(jobs)
    vb = engineB_batch(jobs)
    bad = []
    for i, (a, b) in enumerate(zip(va, vb)):
        if a != b:
            bad.append((i, a, b))
    log("V4 compared %d (triple,n) evaluations at n=1,2,3; mismatches=%d"
        % (len(jobs), len(bad)))
    if bad:
        for i, a, b in bad[:20]:
            t = triples[i // 3]
            log("V4 MISMATCH %s n=%d  A=%s  B=%s" %
                (t, (i % 3) + 1, a, b))
        return False
    nonint = [i for i, a in enumerate(va) if not isinstance(a, int)]
    if nonint:
        log("V4 note: %d non-numeric engine results (CAP_EXCEEDED) -- "
            "these agreed between engines" % len(nonint))
    return True


def run_validation(logpath=None):
    lines = []

    def log(s):
        print(s)
        lines.append(s)

    log("== LP-FREE SCREEN VALIDATION ==")
    log("engine A: %s" % ENGINE_A)
    log("engine B: %s" % ENGINE_B)

    log("-- V1: reproduce the known refuter exactly --")
    v1, _ = _v1_refuter(log)
    log("-- V2: infinite family k=4..9 --")
    v2 = _v2_family(log)
    log("-- V3: Reeve tetrahedron T_q, q=1..20 (raw polytope, no hives) --")
    v3, neg_seen = _v3_reeve(log)
    log("-- V4: engine A vs engine B on 200 random triples, n=1,2,3 --")
    v4 = _v4_cross_engine(log)

    allok = v1 and v2 and v3 and v4
    log("RESULT V1=%s V2=%s V3=%s V4=%s -> %s"
        % (v1, v2, v3, v4, "ALL PASS" if allok else "FAILED"))
    log("Reeve negativity at q>=13: %s"
        % ("SEEN (strictly negative linear coefficient for every q in 13..20, "
           "and for no q < 13)"
           if all(neg_seen[q] for q in range(13, 21))
           and not any(neg_seen[q] for q in range(1, 13)) else "NOT SEEN"))
    if logpath:
        with open(logpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return allok


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--triple", nargs=3, metavar=("LAM", "MU", "NU"))
    ap.add_argument("--batch", metavar="FILE",
                    help='lines "lam;mu;nu" (# comments ok)')
    ap.add_argument("--reeve", type=int, metavar="Q",
                    help="screen the Reeve tetrahedron T_Q directly")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--validate-log", metavar="FILE")
    ap.add_argument("--cap", type=int, default=DEFAULT_CAP)
    ap.add_argument("--dbound", type=int, default=None,
                    help="certified degree bound override (default: ambient "
                         "(r-1)(r-2)/2)")
    ap.add_argument("--out", metavar="FILE")
    args = ap.parse_args(argv[1:])

    if args.validate:
        ok = run_validation(args.validate_log)
        return 0 if ok else 1

    recs = []
    if args.reeve is not None:
        recs.append(reeve_record(args.reeve))
    triples = []
    if args.triple:
        triples.append(tuple(parse_partition(x) for x in args.triple))
    if args.batch:
        with open(args.batch, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                fields = [x.strip() for x in line.split(";")]
                if len(fields) < 3:
                    raise SystemExit("bad batch line: %r" % raw)
                triples.append(tuple(parse_partition(x) for x in fields[:3]))
    if triples:
        recs.extend(screen_triples(triples, cap=args.cap, dbound=args.dbound))

    if not recs:
        ap.print_help()
        return 2

    sink = open(args.out, "w", encoding="utf-8") if args.out else None
    try:
        for r in recs:
            line = json.dumps(r)
            print(line)
            if sink:
                sink.write(line + "\n")
    finally:
        if sink:
            sink.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
