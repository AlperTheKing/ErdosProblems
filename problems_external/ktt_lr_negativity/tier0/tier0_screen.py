#!/usr/bin/env python3
"""
tier0_screen.py -- TIER-0 extension of the mandated LP-FREE exact screen.

This file is a COPY of purged_region/lpfree_screen.py with FIELDS ADDED.
The validated core (exact profile via engine A -> exact Newton interpolation
-> two held-out points -> d = deg P -> exact h*) is untouched: no LP
dimension oracle, no simplex filter, no float decides anything.

WHAT TIER-0 HUNTS
-----------------
Write d = deg P = dim Q and h*_j for the h*-vector of P.  Always
h*_0 = 1 and h*_1 = c - (d+1) with c = P(1) = #(Q cap Z^N).  At Ehrhart
period 1 (Derksen-Weyman: hive polytopes have period 1) Ehrhart-Macdonald
reciprocity gives

        h*_d = (-1)^d P(-1) = #(INTERIOR lattice points of Q).

The campaign-wide volume thresholds (Sum h* >= 13 at d=3, 27 at d=4, 19 at
d=5, 37 at d=6, 25 at d=7) rest ENTIRELY on inequalities valid only for
LATTICE polytopes: Stanley monotonicity, Hibi, and h*_d <= h*_1.  Assuming
only Stanley nonnegativity h*_j >= 0, the cheapest negativity configuration
collapses to

        Sum h* = 3,   h* = (1, 0, ..., 0, 2),   any d >= 4,

which makes [n^{d-2}]P strictly negative.  That configuration requires
h*_d > h*_1, i.e. a polytope with exactly d+1 lattice points AT LEAST ONE
OF WHICH IS INTERIOR.  For a LATTICE polytope this is impossible (its
>= d+1 vertices are lattice points on the boundary, so an interior lattice
point forces c > d+1).  Hive polytopes are RATIONAL, not lattice: the
verified triple lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1) has dim 4, c = 5,
seven vertices, TWO OF THEM HALF-INTEGRAL.  So nothing excludes it, and it
has never been searched.

        TIER0   :=  (h*_1 == 0)  AND  (h*_d > 0)
        JACKPOT :=  (h*_d > h*_1)          [strictly weaker, still fatal to
                                            the lattice-polytope inequalities]

NEGATIVITY CRITERIA (exact, derived from P(n) = sum_j h*_j C(n+d-j,d))
---------------------------------------------------------------------
With u_j := 2j - (d+1) and <.> the h*-weighted average (weights h*_j,
total Sum h*):

        [n^{d-1}]P = -(d / (2*d!)) * Sum_h* * <u>
                     < 0   iff   <u> > 0
        [n^{d-2}]P =  (d(d-1) / (8*d!)) * Sum_h* * (<u^2> - (d+1)/3)
                     < 0   iff   <u^2> < (d+1)/3

(the linear-in-u term of the second elementary symmetric function of the
roots of C(n+d-j,d) cancels identically).  Both are RECOMPUTED against the
interpolated monomial coefficients on every record: field
`moment_criteria_consistent` must be true, or the record is suspect.

ADDED FIELDS (per triple / per polytope)
----------------------------------------
  hstar, hstar_sum, hstar_1, hstar_d, INTERIOR (= hstar_d),
  JACKPOT, TIER0, u_mean, u2_mean (exact Fractions as strings),
  coeffs_low_to_high, NEG (strictly negative monomial coefficient),
  plus the audit flags hstar_1_identity_ok, interior_check_ok,
  moment_criteria_consistent.

MODES
-----
  --triple LAM MU NU              one hive triple
  --batch FILE                    lines "lam;mu;nu", one JSON per line
  --prefilter FILE                cheap TIER0 decision (see below)
  --reeve Q                       Reeve tetrahedron T_Q (lattice control)
  --synthetic                     the built-in RATIONAL-polytope controls
  --rsimplex "v;v;..." --den K    any rational simplex conv{v_i / K}
  --validate                      the four mandated validations

FAST PRE-FILTER (--prefilter)
-----------------------------
h*_1 = c - d - 1 needs only c and d, and d <= D = (r-1)(r-2)/2 always.
Stage 1 therefore spends ONE engine call per triple (n = 1 only): if
c > D + 1 then h*_1 >= c - D - 1 > 0, so TIER0 is impossible and the triple
is rejected without ever computing a profile.  Only survivors (and the
empty ones, which are rejected too) reach the full D+3-call screen.  Every
record carries stage1_calls / stage2_calls so the saving is auditable.

WARNING -- the pre-filter is a TIER0 filter ONLY.  A triple with
c > D + 1 has h*_1 > 0 but may still satisfy h*_d > h*_1 (JACKPOT).  Those
records carry jackpot_undetermined = true.  The JACKPOT hunt must run the
FULL --batch screen.  This file exists because a previous campaign screen
purged a population with a cheap pre-test; do not repeat that by treating a
pre-filter rejection as a mathematical verdict.

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
import itertools
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


def hstar_moments(hstar, d):
    """(<u>, <u^2>) with u_j = 2j - (d+1), weights h*_j, total Sum h*.
    Returns (None, None) when Sum h* = 0 (no weighted average exists)."""
    S = sum(hstar)
    if S == 0:
        return None, None
    us = [2 * j - (d + 1) for j in range(d + 1)]
    m1 = Fraction(sum(h * u for h, u in zip(hstar, us)), S)
    m2 = Fraction(sum(h * u * u for h, u in zip(hstar, us)), S)
    return m1, m2


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

TIER0_DEFAULTS = ("hstar_1", "hstar_d", "INTERIOR", "u_mean", "u2_mean")


def _tier0_defaults(rec):
    """Uniform tier-0 fields on every non-OK exit path, so downstream
    consumers never have to test for key existence.  Flags are FALSE, not
    unknown-as-true: a skipped triple is never a hit."""
    rec["NEG"] = bool(rec.get("neg", False))
    rec["JACKPOT"] = False
    rec["TIER0"] = False
    for k in TIER0_DEFAULTS:
        rec.setdefault(k, None)
    return rec


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
            _tier0_defaults(rec)
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
        _tier0_defaults(rec)
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
        _tier0_defaults(rec)
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
    rec["NEG"] = rec["neg"]
    rec["status"] = "OK"

    # ---------------- TIER-0 FIELDS (added; core above untouched) --------
    h1 = hstar[1] if d >= 1 else None
    hd = hstar[d] if d >= 0 else None
    rec["hstar_1"] = h1
    rec["hstar_d"] = hd
    # At Ehrhart period 1 (hive polytopes: Derksen-Weyman), Ehrhart-Macdonald
    # reciprocity gives h*_d = (-1)^d P(-1) = #interior lattice points of Q.
    rec["INTERIOR"] = hd
    rec["interior_from_reciprocity"] = str((-1) ** d * poly_eval(coeffs, -1))
    rec["interior_check_ok"] = ((-1) ** d * poly_eval(coeffs, -1) == hd)
    rec["hstar_1_identity_ok"] = (h1 is None) or (h1 == rec["c"] - d - 1)

    rec["JACKPOT"] = bool(d >= 1 and hd > h1)
    rec["TIER0"] = bool(d >= 1 and h1 == 0 and hd > 0)

    m1, m2 = hstar_moments(hstar, d)
    rec["u_mean"] = None if m1 is None else str(m1)
    rec["u2_mean"] = None if m2 is None else str(m2)
    rec["hstar_sum_positive"] = (sum(hstar) > 0)

    # negativity criteria in h*-moment form, and the audit that they agree
    # with the actual interpolated monomial coefficients
    pred = {}
    cons = True
    if m1 is not None and d >= 1:
        pred["coeff_d_minus_1_neg_predicted"] = bool(m1 > 0)
        actual = coeffs[d - 1] < 0
        pred["coeff_d_minus_1_neg_actual"] = bool(actual)
        cons = cons and (bool(m1 > 0) == actual)
    if m2 is not None and d >= 2:
        pred["coeff_d_minus_2_neg_predicted"] = bool(m2 < Fraction(d + 1, 3))
        actual = coeffs[d - 2] < 0
        pred["coeff_d_minus_2_neg_actual"] = bool(actual)
        cons = cons and (bool(m2 < Fraction(d + 1, 3)) == actual)
    rec["moment_criteria"] = pred
    rec["moment_criteria_consistent"] = cons
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
            _tier0_defaults(head)
            head["profile_raw"] = [str(v) for v in chunk]
            out.append(head)
            continue
        if bad:
            head["status"] = "CAP_EXCEEDED"
            head["failed_n"] = bad
            head["profile_raw"] = [str(v) for v in chunk]
            head["neg"] = False
            _tier0_defaults(head)
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
    rec["is_lattice_polytope"] = True
    return rec


# --------------------------------------------------------------------------
# RATIONAL simplices -- the JACKPOT-detector unit test
#
# Q = conv{ v_i / den : i = 0..d }, v_i integer vectors in Z^d.  A lattice
# point p lies in n*Q iff there are barycentric weights mu_i >= 0 with
# sum mu_i = n and sum mu_i v_i = den * p; p is INTERIOR iff all mu_i > 0.
# Everything is solved exactly over Q (Fractions).  No LP, no float.
# --------------------------------------------------------------------------

def _mat_inverse(M):
    """Exact inverse of a square Fraction matrix by Gauss-Jordan.
    Returns None if singular."""
    n = len(M)
    A = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(n)]
         for i, row in enumerate(M)]
    for c in range(n):
        piv = None
        for r in range(c, n):
            if A[r][c] != 0:
                piv = r
                break
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [row[n:] for row in A]


class RationalSimplex(object):
    """conv{ v_i / den }, v_i in Z^dim, exactly d+1 affinely independent
    vertices (d = dim)."""

    def __init__(self, verts, den, name=None):
        self.verts = [tuple(int(x) for x in v) for v in verts]
        self.den = int(den)
        self.dim = len(self.verts[0])
        self.name = name
        if len(self.verts) != self.dim + 1:
            raise ValueError("need exactly dim+1 vertices for a simplex")
        if any(len(v) != self.dim for v in self.verts):
            raise ValueError("ragged vertex list")
        M = [[self.verts[i][k] for i in range(self.dim + 1)]
             for k in range(self.dim)]
        M.append([1] * (self.dim + 1))
        self.Minv = _mat_inverse(M)
        if self.Minv is None:
            raise ValueError("degenerate simplex (vertices not affinely "
                             "independent)")

    def is_lattice(self):
        return all(x % self.den == 0 for v in self.verts for x in v)

    def classify(self, p, n):
        """1 interior of n*Q, 0 on the boundary, -1 outside."""
        rhs = [Fraction(self.den * p[k]) for k in range(self.dim)]
        rhs.append(Fraction(n))
        mu = [sum(self.Minv[i][j] * rhs[j] for j in range(self.dim + 1))
              for i in range(self.dim + 1)]
        if any(m < 0 for m in mu):
            return -1
        return 1 if all(m > 0 for m in mu) else 0

    def counts(self, n):
        """(#(n*Q cap Z^dim), #interior), exact enumeration over the box."""
        lo = []
        hi = []
        for k in range(self.dim):
            xs = [Fraction(n * v[k], self.den) for v in self.verts]
            lo.append(math.ceil(min(xs)))
            hi.append(math.floor(max(xs)))
        tot = 0
        itr = 0
        ranges = [range(lo[k], hi[k] + 1) for k in range(self.dim)]
        for p in itertools.product(*ranges):
            c = self.classify(p, n)
            if c >= 0:
                tot += 1
                if c == 1:
                    itr += 1
        return tot, itr

    def vertex_strings(self):
        return ["(" + ",".join(str(Fraction(x, self.den)) for x in v) + ")"
                for v in self.verts]


def rsimplex_record(S, D=None, extra_check_upto=12):
    """Screen a rational simplex with the SAME core as the hive path, and
    additionally verify the reported INTERIOR against direct enumeration and
    the polynomiality beyond the two mandated held-out points."""
    if D is None:
        D = S.dim
    prof = {}
    ints = {}
    for n in range(max(D + 3, extra_check_upto + 1)):
        t, i = S.counts(n)
        prof[n] = t
        ints[n] = i
    rec = screen_profile({n: prof[n] for n in range(D + 3)}, D,
                         label=S.name or "rational_simplex")
    rec["polytope"] = "conv{" + ", ".join(S.vertex_strings()) + "}"
    rec["denominator"] = S.den
    rec["is_lattice_polytope"] = S.is_lattice()
    rec["source"] = "direct exact lattice-point enumeration"
    rec["interior_direct"] = ints[1]
    rec["interior_direct_matches_hstar_d"] = (rec.get("INTERIOR") == ints[1])
    rec["interior_profile"] = [ints[n] for n in range(min(6, D + 3))]
    if rec.get("status") == "OK":
        co = [Fraction(x) for x in rec["coeffs_low_to_high"]]
        extra = [{"n": n, "enum": prof[n], "poly": str(poly_eval(co, n)),
                  "match": poly_eval(co, n) == prof[n]}
                 for n in range(D + 3, extra_check_upto + 1)]
        rec["extra_period1_checks"] = extra
        rec["extra_period1_ok"] = all(e["match"] for e in extra)
        # reciprocity, checked constituent-free against enumeration
        rec["reciprocity_ok"] = all(
            (-1) ** rec["d"] * poly_eval(co, -n) == ints[n]
            for n in range(1, min(6, D + 3)))
    return rec


# The built-in RATIONAL controls.  S1 is the JACKPOT/TIER0 detector test:
# a NON-lattice triangle with exactly d+1 = 3 lattice points, ONE OF THEM
# INTERIOR -- the exact configuration that is impossible for a lattice
# polytope.  S2 is a JACKPOT that is not a TIER0.  Reeve is the lattice
# negative control (h*_d = 0, so JACKPOT must be false).
SYNTHETIC = [
    ("S1_tier0_triangle", [(-1, -1), (0, 2), (2, 0)], 2),
    ("S2_jackpot_triangle", [(-4, -4), (-3, 3), (6, 2)], 2),
]


def synthetic_records():
    return [rsimplex_record(RationalSimplex(v, den, name=nm))
            for (nm, v, den) in SYNTHETIC]


# --------------------------------------------------------------------------
# fast TIER0 pre-filter
# --------------------------------------------------------------------------

def prefilter_triples(triples, cap=DEFAULT_CAP, dbound=None,
                      stage1_only=False):
    """Stage 1 spends ONE engine call per triple (n = 1) and yields c.
    Since d <= D always, c > D + 1 forces h*_1 = c - d - 1 >= c - D - 1 > 0,
    so TIER0 is impossible: reject without a profile.  c = 0 (empty Q) is
    likewise rejected.  Survivors go to the full mandated screen unless
    stage1_only."""
    Ds = []
    for (lam, mu, nu) in triples:
        Ds.append(dbound if dbound is not None else ambient_bound(nu))

    n1 = [(scale(l, 1), scale(m, 1), scale(v, 1)) for (l, m, v) in triples]
    cs = engineA_batch(n1, cap=cap)

    recs = []
    survivors = []
    for t, (lam, mu, nu) in enumerate(triples):
        D = Ds[t]
        r = {"lam": list(lam), "mu": list(mu), "nu": list(nu), "r": len(nu),
             "degree_bound": D, "c": cs[t], "stage1_calls": 1,
             "stage2_calls": 0, "mode": "prefilter"}
        if sum(lam) + sum(mu) != sum(nu):
            r["stage1_verdict"] = "REJECT_SIZE_MISMATCH"
        elif not isinstance(cs[t], int):
            r["stage1_verdict"] = "SKIP_CAP_EXCEEDED"
            r["c_raw"] = str(cs[t])
            r["note"] = "engine cap hit; a SKIP, never a math verdict"
        elif cs[t] == 0:
            r["stage1_verdict"] = "REJECT_EMPTY"
        elif cs[t] > D + 1:
            r["stage1_verdict"] = "REJECT_HSTAR1_POSITIVE"
            r["hstar_1_lower_bound"] = cs[t] - D - 1
            r["tier0_possible"] = False
            # h*_d > h*_1 > 0 is NOT excluded by this test.  The pre-filter is
            # a TIER0 filter ONLY; it does not decide JACKPOT, and the
            # JACKPOT hunt must use the full --batch screen.
            r["jackpot_undetermined"] = True
            r["note"] = ("c=%d > D+1=%d and d<=D, so h*_1 = c-d-1 >= %d > 0: "
                         "TIER0 impossible without computing a profile. "
                         "JACKPOT (h*_d > h*_1) is NOT decided here."
                         % (cs[t], D + 1, cs[t] - D - 1))
        else:
            r["stage1_verdict"] = "SURVIVOR"
            # c = 1 can never be TIER0 (either d = 0, a point, or d >= 1 and
            # then h*_1 = -d < 0), but it is a strong JACKPOT candidate via
            # h*_1 < 0, so it is NOT dropped: it goes to the full screen.
            r["tier0_possible"] = (cs[t] >= 2)
            survivors.append(t)
        _tier0_defaults(r)
        r["neg"] = False
        recs.append(r)

    if stage1_only or not survivors:
        return recs

    full = screen_triples([triples[t] for t in survivors], cap=cap,
                          dbound=dbound)
    for t, frec in zip(survivors, full):
        frec["mode"] = "prefilter"
        frec["stage1_calls"] = 1
        frec["stage2_calls"] = Ds[t] + 3
        frec["stage1_verdict"] = "SURVIVOR"
        recs[t] = frec
    return recs


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
        # -------- tier-0 fields --------
        "hstar_d_zero": rec.get("hstar_d") == 0,
        "INTERIOR_zero": rec.get("INTERIOR") == 0,
        "TIER0_false": rec.get("TIER0") is False,
        "JACKPOT_false": rec.get("JACKPOT") is False,
        "NEG_false": rec.get("NEG") is False,
        "hstar_1_identity_ok": rec.get("hstar_1_identity_ok") is True,
        "interior_check_ok": rec.get("interior_check_ok") is True,
        "moment_criteria_consistent":
            rec.get("moment_criteria_consistent") is True,
        # h*=(1,0,1,0,0), d=4: u=(-5,-3,-1,1,3); <u>=(-5-1)/2=-3, <u^2>=13
        "u_mean_is_-3": rec.get("u_mean") == "-3",
        "u2_mean_is_13": rec.get("u2_mean") == "13",
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
    """Mandated validation 2: the Reeve tetrahedron fed DIRECTLY as a
    polytope.  h* = (1,0,q-1,0), <u^2> = 16/q, and the LINEAR coefficient is
    strictly negative exactly for q >= 13, with q = 12 giving exactly 0."""
    ok = True
    neg_seen = {}
    for q in range(1, qmax + 1):
        rec = reeve_record(q)
        hs_exp = [1, 0, q - 1, 0]
        lin = Fraction(rec["coeffs_low_to_high"][1]) if rec["d"] >= 1 else None
        neg = (lin is not None and lin < 0)
        neg_seen[q] = neg
        # d=3: [n^{d-2}] = [n^1]; criterion <u^2> < (d+1)/3 = 4/3 <=> q > 12
        good = (rec["status"] == "OK" and rec["d"] == 3
                and rec.get("hstar") == hs_exp
                and rec.get("hstar_sum") == q
                and rec.get("heldout_ok") is True
                and rec.get("hstar_roundtrip_ok") is True
                and rec.get("hstar_tail_zero") is True
                and rec.get("u2_mean") == str(Fraction(16, q))
                and rec.get("u_mean") == str(Fraction(-4, q))
                and rec.get("INTERIOR") == 0
                and rec.get("hstar_d") == 0
                and rec.get("hstar_1") == 0
                and rec.get("JACKPOT") is False
                and rec.get("TIER0") is False
                and rec.get("interior_check_ok") is True
                and rec.get("moment_criteria_consistent") is True
                and rec.get("NEG") is neg
                and neg == (q >= 13)
                and (q != 12 or lin == 0))
        ok = ok and good
        log("V2 q=%2d  h*=%s  vol=%s  <u^2>=%s (16/q=%s)  lin=%s  neg=%s  "
            "JACKPOT=%s  %s" %
            (q, rec.get("hstar"), rec.get("hstar_sum"), rec.get("u2_mean"),
             Fraction(16, q), lin, neg, rec.get("JACKPOT"),
             "PASS" if good else "FAIL"))
    z12 = Fraction(reeve_record(12)["coeffs_low_to_high"][1])
    log("V2 q=12 linear coefficient = %s (must be exactly 0): %s"
        % (z12, "PASS" if z12 == 0 else "FAIL"))
    ok = ok and (z12 == 0)
    log("V2 negative-linear-coefficient q values: %s" %
        [q for q, v in neg_seen.items() if v])
    return ok, neg_seen


def _v3_synthetic(log):
    """Mandated validation 3: a RATIONAL (non-lattice) polytope built here,
    with an interior lattice point and few boundary lattice points, to prove
    the JACKPOT detector actually FIRES when h*_d > h*_1 holds.

    S1 = conv{(-1/2,-1/2), (0,1), (1,0)}  -- non-lattice, 3 lattice points
         ((0,0) INTERIOR; (1,0),(0,1) on the boundary), P(n) = n^2+n+1,
         d = 2, c = 3 = d+1, h* = (1,0,1): h*_1 = 0 < 1 = h*_d.
         This is the tier-0 configuration itself, one dimension down.
    S2 = conv{(-2,-2), (-3/2,3/2), (3,1)}  -- non-lattice, c = 10,
         8 interior, h* = (1,7,8): JACKPOT but not TIER0.
    Negative control: the LATTICE Reeve tetrahedra of validation 2, where
    h*_d = 0 = h*_1 and JACKPOT is correctly false."""
    recs = synthetic_records()
    exp = {
        "S1_tier0_triangle": dict(
            d=2, c=3, hstar=[1, 0, 1], hstar_sum=2, hstar_1=0, hstar_d=1,
            INTERIOR=1, JACKPOT=True, TIER0=True, NEG=False,
            coeffs=["1", "1", "1"]),
        "S2_jackpot_triangle": dict(
            d=2, c=10, hstar=[1, 7, 8], hstar_sum=16, hstar_1=7, hstar_d=8,
            INTERIOR=8, JACKPOT=True, TIER0=False, NEG=False,
            coeffs=["1", "1", "8"]),
    }
    ok = True
    fired = {}
    for rec in recs:
        e = exp[rec["label"]]
        good = (rec["status"] == "OK"
                and rec["is_lattice_polytope"] is False
                and rec["d"] == e["d"] and rec["c"] == e["c"]
                and rec.get("hstar") == e["hstar"]
                and rec.get("hstar_sum") == e["hstar_sum"]
                and rec.get("hstar_1") == e["hstar_1"]
                and rec.get("hstar_d") == e["hstar_d"]
                and rec.get("INTERIOR") == e["INTERIOR"]
                and rec.get("JACKPOT") is e["JACKPOT"]
                and rec.get("TIER0") is e["TIER0"]
                and rec.get("NEG") is e["NEG"]
                and rec["coeffs_low_to_high"] == e["coeffs"]
                and rec.get("heldout_ok") is True
                and rec.get("hstar_roundtrip_ok") is True
                and rec.get("hstar_tail_zero") is True
                and rec.get("interior_check_ok") is True
                and rec.get("interior_direct_matches_hstar_d") is True
                and rec.get("extra_period1_ok") is True
                and rec.get("reciprocity_ok") is True
                and rec.get("moment_criteria_consistent") is True)
        fired[rec["label"]] = bool(rec.get("JACKPOT"))
        ok = ok and good
        log("V3 %-22s %s  lattice=%s c=%s d=%s h*=%s INTERIOR=%s "
            "h*_1=%s h*_d=%s JACKPOT=%s TIER0=%s  %s"
            % (rec["label"], rec["polytope"], rec["is_lattice_polytope"],
               rec.get("c"), rec.get("d"), rec.get("hstar"),
               rec.get("INTERIOR"), rec.get("hstar_1"), rec.get("hstar_d"),
               rec.get("JACKPOT"), rec.get("TIER0"),
               "PASS" if good else "FAIL"))
        log("V3 %s record: %s" % (rec["label"], json.dumps(rec)))
    # negative control: a LATTICE polytope with the same d must NOT fire
    ctrl = reeve_record(17)
    ctrl_ok = (ctrl["is_lattice_polytope"] if "is_lattice_polytope" in ctrl
               else True) and ctrl.get("JACKPOT") is False
    log("V3 negative control Reeve T_17 (LATTICE): h*=%s JACKPOT=%s  %s"
        % (ctrl.get("hstar"), ctrl.get("JACKPOT"),
           "PASS" if ctrl_ok else "FAIL"))
    ok = ok and ctrl_ok
    log("V3 JACKPOT detector FIRED on: %s"
        % [k for k, v in fired.items() if v])
    return ok, fired


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


def _v5_prefilter(log, count=60, seed=20260722):
    """The cheap pre-filter must never disagree with the full screen about
    TIER0: every triple it rejects must really have TIER0 false."""
    rnd, _ = _random_triples(count * 3, seed=seed, log=log)
    rnd = rnd[:count]
    # 2-dilates: same polytope 2Q, so c jumps well past D+1 and stage 1 must
    # reject them.  Keeps the test non-vacuous in BOTH directions.
    big = [(scale(l, 2), scale(m, 2), scale(v, 2)) for (l, m, v) in rnd]
    triples = ([REFUTER] + [((2, 2, 1), (k, 3, 2, 1), (k + 1, 4, 3, 2, 1))
                            for k in (4, 5, 6)] + rnd + big)
    pre = prefilter_triples(triples)
    full = screen_triples(triples)
    bad = []
    saved = 0
    for t, (p, f) in enumerate(zip(pre, full)):
        if p.get("stage1_verdict") != "SURVIVOR":
            saved += f.get("degree_bound", 0) + 3 - 1
        if bool(p.get("TIER0")) != bool(f.get("TIER0")):
            bad.append((t, triples[t], p.get("stage1_verdict"),
                        p.get("TIER0"), f.get("TIER0")))
        if bool(p.get("JACKPOT")) and not bool(f.get("JACKPOT")):
            bad.append((t, triples[t], "JACKPOT", p.get("JACKPOT"),
                        f.get("JACKPOT")))
    surv = sum(1 for p in pre if p.get("stage1_verdict") == "SURVIVOR")
    rej = len(triples) - surv
    log("V5 %d triples: %d survived stage 1 (1 engine call each), %d "
        "rejected; %d engine calls saved; TIER0 disagreements=%d"
        % (len(triples), surv, rej, saved, len(bad)))
    for b in bad[:10]:
        log("V5 DISAGREEMENT %s" % (b,))
    if surv == 0 or rej == 0:
        log("V5 FAIL: test is vacuous (needs both survivors and rejections)")
        return False
    return not bad


def run_validation(logpath=None):
    lines = []

    def log(s):
        print(s)
        lines.append(s)

    log("== TIER-0 SCREEN VALIDATION (LP-free core + tier-0 fields) ==")
    log("engine A: %s" % ENGINE_A)
    log("engine B: %s" % ENGINE_B)

    log("-- V1: reproduce the known refuter exactly (+ tier-0 fields) --")
    v1, _ = _v1_refuter(log)
    log("-- V1b (inherited): infinite family k=4..9 --")
    v1b = _v2_family(log)
    log("-- V2: Reeve tetrahedron T_q fed DIRECTLY as a polytope, q=1..20 --")
    v2, neg_seen = _v3_reeve(log)
    log("-- V3: own RATIONAL polytope with an interior lattice point: does "
        "the JACKPOT detector fire? --")
    v3, fired = _v3_synthetic(log)
    log("-- V4: engine A vs engine B on 200 random triples, n=1,2,3 --")
    v4 = _v4_cross_engine(log)
    log("-- V5 (extra): pre-filter agrees with the full screen --")
    v5 = _v5_prefilter(log)

    allok = v1 and v1b and v2 and v3 and v4 and v5
    log("RESULT V1=%s V1b=%s V2=%s V3=%s V4=%s V5=%s -> %s"
        % (v1, v1b, v2, v3, v4, v5, "ALL PASS" if allok else "FAILED"))
    log("Reeve negativity at q>=13: %s"
        % ("SEEN (strictly negative linear coefficient for every q in 13..20, "
           "and for no q < 13; q=12 exactly 0)"
           if all(neg_seen[q] for q in range(13, 21))
           and not any(neg_seen[q] for q in range(1, 13)) else "NOT SEEN"))
    log("JACKPOT detector on the synthetic rational polytopes: %s"
        % ("FIRED on " + ", ".join(sorted(k for k, v in fired.items() if v))
           if any(fired.values()) else "DID NOT FIRE"))
    log("NOTE: a null census is NOT evidence for the KTT conjecture and is "
        "never to be described as such.")
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
    ap.add_argument("--prefilter", metavar="FILE",
                    help='lines "lam;mu;nu": cheap TIER0 decision (1 engine '
                         'call per triple in stage 1)')
    ap.add_argument("--stage1-only", action="store_true",
                    help="with --prefilter: stop after the 1-call stage")
    ap.add_argument("--reeve", type=int, metavar="Q",
                    help="screen the Reeve tetrahedron T_Q directly")
    ap.add_argument("--synthetic", action="store_true",
                    help="emit the built-in RATIONAL-polytope controls")
    ap.add_argument("--rsimplex", metavar="VERTS",
                    help='rational simplex conv{v_i/den}, vertices as '
                         '"x,y,..;x,y,..;.." (use --den)')
    ap.add_argument("--den", type=int, default=1,
                    help="denominator for --rsimplex (default 1)")
    ap.add_argument("--tier0-only", action="store_true",
                    help="print only records with TIER0 or JACKPOT true")
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

    def read_triples(path):
        out = []
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                fields = [x.strip() for x in line.split(";")]
                if len(fields) < 3:
                    raise SystemExit("bad batch line: %r" % raw)
                out.append(tuple(parse_partition(x) for x in fields[:3]))
        return out

    recs = []
    if args.reeve is not None:
        recs.append(reeve_record(args.reeve))
    if args.synthetic:
        recs.extend(synthetic_records())
    if args.rsimplex:
        verts = [tuple(int(t) for t in v.replace(" ", ",").split(",")
                       if t != "")
                 for v in args.rsimplex.split(";") if v.strip()]
        recs.append(rsimplex_record(RationalSimplex(verts, args.den,
                                                    name="rsimplex")))
    triples = []
    if args.triple:
        triples.append(tuple(parse_partition(x) for x in args.triple))
    if args.batch:
        triples.extend(read_triples(args.batch))
    if triples:
        recs.extend(screen_triples(triples, cap=args.cap, dbound=args.dbound))
    if args.prefilter:
        recs.extend(prefilter_triples(read_triples(args.prefilter),
                                      cap=args.cap, dbound=args.dbound,
                                      stage1_only=args.stage1_only))

    if not recs:
        ap.print_help()
        return 2

    if args.tier0_only:
        recs = [r for r in recs if r.get("TIER0") or r.get("JACKPOT")]

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
