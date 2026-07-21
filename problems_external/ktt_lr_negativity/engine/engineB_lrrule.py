#!/usr/bin/env python3
"""Engine B -- independent exact Littlewood-Richardson coefficient counter.

Counts c(nu; lam, mu) by the CLASSICAL Littlewood-Richardson rule:
  the number of semistandard skew tableaux of shape nu/lam with content mu
  whose reverse reading word (rows top->bottom, each row read right->left)
  is a lattice word (every prefix has #i >= #(i+1) for all i).

Implementation: memoized row-by-row DP. Each row is filled right-to-left so
the lattice condition is checked incrementally at every placed cell (the
placement order IS the reverse-reading-word order).
  - Row-boundary memo key: (row index, slice of previous row lying above the
    next rows' cells, content vector so far).
  - In-row memo key: (column, weak-increase bound, content vector, slice of
    the current row already placed inside the next row's overlap region).
Both memo layers are sound: the constraints on all future cells depend only
on the key components (column-strictness needs only the stored slices;
the lattice and content constraints need only the running content vector).

All arithmetic is native Python big-integer. NO floating point anywhere.

INDEPENDENCE: this engine does not use the hive model and shares no code or
ideas with engine A beyond the CLI contract. The validation ground truth is
an in-file brute-force Schur-polynomial product (SSYT monomial sums + lex
leading-term peeling), which never invokes the LR rule.

CLI (identical contract to engine A):
  python engineB_lrrule.py "lam" "mu" "nu" [cap]   -> one line: exact count, or CAP_EXCEEDED
  python engineB_lrrule.py --batch FILE            -> lines "lam;mu;nu;cap" (cap optional),
                                                      one output line per input line
  python engineB_lrrule.py --selftest              -> full validation, writes BUILD_B.md
Partitions are comma strings, e.g. "5,3,1"; the empty partition is "" or "0".
CAP_EXCEEDED is printed when the exact count provably exceeds the given cap,
or when the DP state count exceeds the internal state limit (triple too fat).
"""

import os
import random
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_STATES_DEFAULT = 20_000_000
SELFTEST_SEED = 20260721


class CapExceeded(Exception):
    pass


# ----------------------------------------------------------------------------
# Partition utilities
# ----------------------------------------------------------------------------

def parse_partition(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    if s in ("", "0", "-", "()", "[]"):
        return ()
    toks = [t for t in s.replace(" ", "").split(",") if t != ""]
    parts = tuple(int(t) for t in toks)
    if any(p < 0 for p in parts):
        raise ValueError("negative part in partition: %r" % (s,))
    for i in range(len(parts) - 1):
        if parts[i] < parts[i + 1]:
            raise ValueError("not weakly decreasing: %r" % (s,))
    return tuple(p for p in parts if p > 0)


def fmt_partition(p):
    return ",".join(str(x) for x in p) if p else "0"


def stretch(p, n):
    return tuple(n * x for x in p) if n > 0 else ()


# ----------------------------------------------------------------------------
# Core counter: classical LR rule (skew LR tableaux), exact big-int DP
# ----------------------------------------------------------------------------

def lr_count(lam, mu, nu, cap=None, max_states=MAX_STATES_DEFAULT):
    """Exact c(nu; lam, mu) via the classical LR rule.

    Raises CapExceeded if cap is not None and the count provably exceeds cap,
    or if the number of DP states exceeds max_states."""
    lam = tuple(lam)
    mu = tuple(mu)
    nu = tuple(nu)
    if sum(lam) + sum(mu) != sum(nu):
        return 0
    r = len(nu)
    if len(lam) > r:
        return 0
    lamp = lam + (0,) * (r - len(lam))
    if any(lamp[i] > nu[i] for i in range(r)):
        return 0
    L = len(mu)
    memo_row = {}
    nstates = [0]

    def bump():
        nstates[0] += 1
        if nstates[0] > max_states:
            raise CapExceeded("state limit exceeded")

    def row_count(i, prev_overlap, content):
        # Number of ways to fill rows i..r-1 given:
        #   prev_overlap = entries of row i-1 at columns [lamp[i-1], nu[i])
        #   content      = letter counts placed so far (tuple, length L)
        if i == r:
            return 1 if content == mu else 0
        key = (i, prev_overlap, content)
        got = memo_row.get(key)
        if got is not None:
            return got
        lo = lamp[i]                      # row i cells: columns lo..hi-1
        hi = nu[i]
        nu_next = nu[i + 1] if i + 1 < r else 0   # next overlap: columns [lo, nu_next)
        has_prev = i > 0
        prev_lo = lamp[i - 1] if has_prev else 0
        local = {}

        def cell(j, bound, content, placed):
            # Cells still to fill in row i: columns lo..j (right-to-left).
            # bound  = entry just placed at column j+1 (weak increase L->R), or L.
            # placed = entries already placed at columns [j+1, nu_next).
            if j < lo:
                return row_count(i + 1, placed, content)
            k = (j, bound, content, placed)
            w = local.get(k)
            if w is not None:
                return w
            above = 0
            if has_prev and j >= prev_lo:
                above = prev_overlap[j - prev_lo]
            in_next = j < nu_next
            total = 0
            for v in range(above + 1, bound + 1):
                cv = content[v - 1]
                if cv >= mu[v - 1]:
                    continue                       # content bound
                if v >= 2 and content[v - 2] <= cv:
                    continue                       # lattice: need #(v-1) > #v before placing v
                nc = content[:v - 1] + (cv + 1,) + content[v:]
                np_ = ((v,) + placed) if in_next else placed
                total += cell(j - 1, v, nc, np_)
                if cap is not None and total > cap:
                    raise CapExceeded("count exceeds cap")
            local[k] = total
            bump()
            return total

        val = cell(hi - 1, L, content, ())
        memo_row[key] = val
        bump()
        return val

    res = row_count(0, (), (0,) * L)
    if cap is not None and res > cap:
        raise CapExceeded("count exceeds cap")
    return res


# ----------------------------------------------------------------------------
# Independent ground truth: brute-force Schur polynomial products.
# Schur polynomial = SSYT monomial sum (textbook definition, straight shapes,
# no lattice words). Expansion of a product in the Schur basis is obtained by
# repeatedly peeling the lex-greatest monomial. No LR rule involved.
# ----------------------------------------------------------------------------

_PARTS_CACHE = {}


def partitions_of(n, max_part=None):
    if max_part is None or max_part > n:
        max_part = n
    key = (n, max_part)
    hit = _PARTS_CACHE.get(key)
    if hit is not None:
        return hit
    if n == 0:
        res = [()]
    else:
        res = []
        for first in range(max_part, 0, -1):
            for rest in partitions_of(n - first, first):
                res.append((first,) + rest)
    _PARTS_CACHE[key] = res
    return res


_SSYT_CACHE = {}


def schur_poly(shape, nvars):
    """dict {exponent tuple (len nvars): multiplicity} of s_shape(x_1..x_nvars),
    computed by direct enumeration of semistandard Young tableaux."""
    key = (tuple(shape), nvars)
    hit = _SSYT_CACHE.get(key)
    if hit is not None:
        return hit
    shape = tuple(shape)
    if len(shape) > nvars:
        _SSYT_CACHE[key] = {}
        return {}
    poly = defaultdict(int)
    rr = len(shape)
    content = [0] * nvars

    def rec(i, prev_row):
        if i == rr:
            poly[tuple(content)] += 1
            return
        m = shape[i]
        row = [0] * m
        pl = len(prev_row)

        def cellf(j, minv):
            if j == m:
                rec(i + 1, tuple(row))
                return
            lb = minv
            if j < pl and prev_row[j] + 1 > lb:
                lb = prev_row[j] + 1
            for v in range(lb, nvars + 1):
                row[j] = v
                content[v - 1] += 1
                cellf(j + 1, v)
                content[v - 1] -= 1

        cellf(0, 1)

    rec(0, ())
    out = dict(poly)
    _SSYT_CACHE[key] = out
    return out


def poly_mul(A, B):
    C = defaultdict(int)
    items_b = list(B.items())
    for e1, c1 in A.items():
        for e2, c2 in items_b:
            C[tuple(x + y for x, y in zip(e1, e2))] += c1 * c2
    return dict(C)


def schur_expand(P, nvars):
    """Expand a symmetric polynomial dict P over nvars variables in the Schur
    basis {s_nu : len(nu) <= nvars} by lex-leading-term peeling."""
    P = dict(P)
    out = {}
    guard = 0
    while P:
        guard += 1
        if guard > 200000:
            raise RuntimeError("peel guard tripped")
        m = max(P)
        if list(m) != sorted(m, reverse=True):
            raise RuntimeError("lex-leading exponent not a partition: %r" % (m,))
        c = P[m]
        nu = tuple(x for x in m if x > 0)
        S = schur_poly(nu, nvars)
        for e, v in S.items():
            newv = P.get(e, 0) - c * v
            if newv:
                P[e] = newv
            else:
                P.pop(e, None)
        if nu in out:
            raise RuntimeError("duplicate peel at %r" % (nu,))
        out[nu] = c
    return out


# ----------------------------------------------------------------------------
# Selftest / validation
# ----------------------------------------------------------------------------

def _cli_smoke():
    """Exercise the actual CLI contract via subprocess. Returns (ok, lines)."""
    py = sys.executable
    script = os.path.abspath(__file__)
    checks = []

    r = subprocess.run([py, script, "2,1", "2,1", "3,2,1"],
                       capture_output=True, text=True, timeout=120)
    checks.append(("single call c((3,2,1);(2,1),(2,1))", r.stdout.strip(), "2",
                   r.returncode == 0 and r.stdout.strip() == "2"))

    r = subprocess.run([py, script, "2,1", "2,1", "3,2,1", "1"],
                       capture_output=True, text=True, timeout=120)
    checks.append(("single call with cap=1", r.stdout.strip(), "CAP_EXCEEDED",
                   r.returncode == 0 and r.stdout.strip() == "CAP_EXCEEDED"))

    r = subprocess.run([py, script, "0", "0", "0"],
                       capture_output=True, text=True, timeout=120)
    checks.append(("empty triple (n=0 sample point)", r.stdout.strip(), "1",
                   r.returncode == 0 and r.stdout.strip() == "1"))

    fd, tmppath = tempfile.mkstemp(suffix=".txt", prefix="engineB_smoke_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("2,1;2,1;3,2,1\n")
            f.write("1;1,1;2,1;10\n")
            f.write("2,1;2,1;3,2,1;1\n")
        r = subprocess.run([py, script, "--batch", tmppath],
                           capture_output=True, text=True, timeout=120)
        gotlines = [x.strip() for x in r.stdout.strip().splitlines()]
        checks.append(("batch mode 3 lines", "|".join(gotlines), "2|1|CAP_EXCEEDED",
                       r.returncode == 0 and gotlines == ["2", "1", "CAP_EXCEEDED"]))
    finally:
        try:
            os.unlink(tmppath)
        except OSError:
            pass

    ok = all(c[3] for c in checks)
    lines = ["  - %s: got %r, expected %r -> %s"
             % (name, got, want, "PASS" if passed else "FAIL")
             for (name, got, want, passed) in checks]
    return ok, lines


def selftest():
    t_all = time.time()
    ok = True
    problems = []
    rep = []

    # ---------------- Phase 1: exhaustive ground truth, |nu| <= 8, r <= 4 ----
    t1 = time.time()
    nvars = 8
    pairs = 0
    triples = 0
    nonzero = 0
    maxc = 0
    pool1 = []
    pool2 = []
    for a in range(9):
        for b in range(9 - a):
            for lam in partitions_of(a):
                for mu in partitions_of(b):
                    pairs += 1
                    exp = schur_expand(
                        poly_mul(schur_poly(lam, nvars), schur_poly(mu, nvars)),
                        nvars)
                    for nu_p, c in exp.items():
                        if c <= 0:
                            ok = False
                            problems.append(
                                "GROUND-TRUTH NONPOSITIVE c=%d at (%s;%s;%s)"
                                % (c, lam, mu, nu_p))
                    s = a + b
                    for nu_p in partitions_of(s):
                        if len(nu_p) > 4:
                            continue
                        want = exp.get(nu_p, 0)
                        got = lr_count(lam, mu, nu_p)
                        triples += 1
                        if want:
                            nonzero += 1
                            if want > maxc:
                                maxc = want
                        if got != want:
                            ok = False
                            problems.append(
                                "MISMATCH lam=%s mu=%s nu=%s want=%d got=%d"
                                % (lam, mu, nu_p, want, got))
                        if want in (1, 2) and s >= 3:
                            (pool1 if want == 1 else pool2).append(
                                (lam, mu, nu_p))
    ph1 = time.time() - t1
    rep.append("## Validation 1: brute-force Schur-product ground truth")
    rep.append("")
    rep.append("Method: for every pair (lam, mu) with |lam|+|mu| <= 8 (all shapes,")
    rep.append("any number of parts), compute s_lam * s_mu in 8 variables where each")
    rep.append("Schur polynomial is the direct SSYT monomial sum (textbook definition,")
    rep.append("straight shapes, no lattice words, no LR rule), then expand the product")
    rep.append("in the Schur basis by exact lex-leading-monomial peeling. 8 variables")
    rep.append(">= any relevant number of parts, so the expansion is complete and every")
    rep.append("extracted coefficient is the true LR coefficient. Engine B is compared")
    rep.append("against this on EVERY triple (lam, mu, nu) with |nu| = |lam|+|mu| <= 8")
    rep.append("and nu having r <= 4 parts (including the c = 0 triples).")
    rep.append("")
    rep.append("- pairs (lam, mu) processed: %d" % pairs)
    rep.append("- triples compared (engine vs ground truth, incl. zeros): %d" % triples)
    rep.append("- triples with nonzero c: %d (max c seen: %d)" % (nonzero, maxc))
    rep.append("- ground-truth coefficients all positive: %s"
               % ("yes" if not any(p.startswith("GROUND-TRUTH") for p in problems) else "NO"))
    n_mm = sum(1 for p in problems if p.startswith("MISMATCH"))
    rep.append("- mismatches: %d" % n_mm)
    rep.append("- phase runtime: %.1f s" % ph1)
    rep.append("- verdict: %s" % ("PASS (100% match)" if n_mm == 0 and ok else "FAIL"))
    rep.append("")

    # ---------------- Phase 1c: high-multiplicity spot checks (c >= 3) -------
    t1c = time.time()
    hi_pairs = [((3, 2, 1), (3, 2, 1)), ((3, 2, 1), (3, 3, 2, 1))]
    hi_triples = 0
    hi_mm = 0
    hi_maxc = 0
    for (lam, mu) in hi_pairs:
        nv = 4
        exp = schur_expand(poly_mul(schur_poly(lam, nv), schur_poly(mu, nv)), nv)
        s = sum(lam) + sum(mu)
        for nu_p in partitions_of(s):
            if len(nu_p) > 4:
                continue
            want = exp.get(nu_p, 0)
            got = lr_count(lam, mu, nu_p)
            hi_triples += 1
            if want > hi_maxc:
                hi_maxc = want
            if got != want:
                ok = False
                hi_mm += 1
                problems.append(
                    "HI-MULT MISMATCH lam=%s mu=%s nu=%s want=%d got=%d"
                    % (lam, mu, nu_p, want, got))
    ph1c = time.time() - t1c
    rep.append("## Validation 1c: high-multiplicity spot checks (c >= 3 territory)")
    rep.append("")
    rep.append("The exhaustive |nu| <= 8 window only reaches c = 2, so engine B is")
    rep.append("additionally compared against the same 4-variable Schur-product ground")
    rep.append("truth on ALL r <= 4 targets of the pairs (3,2,1)x(3,2,1) (|nu| = 12)")
    rep.append("and (3,2,1)x(3,3,2,1) (|nu| = 15).")
    rep.append("")
    rep.append("- triples compared: %d" % hi_triples)
    rep.append("- max multiplicity reached: %d" % hi_maxc)
    rep.append("- mismatches: %d" % hi_mm)
    rep.append("- phase runtime: %.1f s" % ph1c)
    rep.append("- verdict: %s" % ("PASS" if hi_mm == 0 and hi_maxc >= 3 else "FAIL"))
    rep.append("")
    if hi_maxc < 3:
        ok = False
        problems.append("HI-MULT PHASE never reached c >= 3 (max %d)" % hi_maxc)

    # ---------------- Phase 1b: extend c=2 (and c=1 if needed) pools ---------
    t1b = time.time()
    ext_sizes = []
    s_ext = 9
    while (len(set(pool2)) < 60 or len(set(pool1)) < 60) and s_ext <= 14:
        nv = 4
        for a in range(s_ext + 1):
            b = s_ext - a
            for lam in partitions_of(a):
                if len(lam) > 4:
                    continue
                for mu in partitions_of(b):
                    if len(mu) > 4:
                        continue
                    exp = schur_expand(
                        poly_mul(schur_poly(lam, nv), schur_poly(mu, nv)), nv)
                    for nu_p, c in exp.items():
                        if c == 2:
                            pool2.append((lam, mu, nu_p))
                        elif c == 1 and len(pool1) < 20000:
                            pool1.append((lam, mu, nu_p))
        ext_sizes.append(s_ext)
        s_ext += 1
    ph1b = time.time() - t1b
    pool1u = sorted(set(pool1))
    pool2u = sorted(set(pool2))

    # ---------------- Phase 2: 30 random c=1 stretched checks ----------------
    t2 = time.time()
    rng = random.Random(SELFTEST_SEED)
    if len(pool1u) < 30 or len(pool2u) < 30:
        ok = False
        problems.append("POOL SHORTAGE: c=1 pool %d, c=2 pool %d"
                        % (len(pool1u), len(pool2u)))
        sel1 = pool1u[:30]
        sel2 = pool2u[:30]
    else:
        sel1 = rng.sample(pool1u, 30)
        sel2 = rng.sample(pool2u, 30)

    c1_lines = []
    c1_fail = 0
    for (lam, mu, nu_p) in sel1:
        vals = []
        for n in range(0, 6):
            try:
                v = lr_count(stretch(lam, n), stretch(mu, n), stretch(nu_p, n))
            except CapExceeded:
                v = "CAP"
            vals.append(v)
        good = all(v == 1 for v in vals)
        if not good:
            c1_fail += 1
            ok = False
            problems.append("C1-STRETCH FAIL (%s;%s;%s) -> %s"
                            % (lam, mu, nu_p, vals))
        c1_lines.append("  - (%s ; %s ; %s): P(0..5) = %s -> %s"
                        % (fmt_partition(lam), fmt_partition(mu),
                           fmt_partition(nu_p), vals,
                           "PASS" if good else "FAIL"))
    ph2 = time.time() - t2

    rep.append("## Validation 2: 30 random c=1 stretched checks (KTW: c=1 => P == 1)")
    rep.append("")
    rep.append("Triples drawn (seed %d) from the ground-truth-certified c=1 pool" % SELFTEST_SEED)
    rep.append("(%d distinct triples, |nu| >= 3, r <= 4%s). Each is checked to give"
               % (len(pool1u),
                  ", pool extended to |nu| in %s via 4-variable ground truth" % ext_sizes
                  if ext_sizes else ""))
    rep.append("c(n*nu; n*lam, n*mu) = 1 for all n = 0..5.")
    rep.append("")
    rep.extend(c1_lines)
    rep.append("")
    rep.append("- failures: %d / 30" % c1_fail)
    rep.append("- phase runtime: %.1f s" % ph2)
    rep.append("- verdict: %s" % ("PASS" if c1_fail == 0 and len(sel1) == 30 else "FAIL"))
    rep.append("")

    # ---------------- Phase 3: 30 random c=2 stretched checks ----------------
    t3 = time.time()
    c2_lines = []
    c2_fail = 0
    for (lam, mu, nu_p) in sel2:
        vals = []
        for n in range(0, 6):
            try:
                v = lr_count(stretch(lam, n), stretch(mu, n), stretch(nu_p, n))
            except CapExceeded:
                v = "CAP"
            vals.append(v)
        good = all(vals[n] == n + 1 for n in range(0, 6))
        if not good:
            c2_fail += 1
            ok = False
            problems.append("C2-STRETCH FAIL (%s;%s;%s) -> %s"
                            % (lam, mu, nu_p, vals))
        c2_lines.append("  - (%s ; %s ; %s): P(0..5) = %s -> %s"
                        % (fmt_partition(lam), fmt_partition(mu),
                           fmt_partition(nu_p), vals,
                           "PASS" if good else "FAIL"))
    ph3 = time.time() - t3

    rep.append("## Validation 3: 30 random c=2 stretched checks (Ikenmeyer/Sherman: c=2 => P(n) = n+1)")
    rep.append("")
    rep.append("Triples drawn (same seed) from the ground-truth-certified c=2 pool")
    rep.append("(%d distinct triples). Each is checked to give c(n*nu; n*lam, n*mu)"
               % (len(pool2u),))
    rep.append("= n + 1 for all n = 0..5.")
    rep.append("")
    rep.extend(c2_lines)
    rep.append("")
    rep.append("- failures: %d / 30" % c2_fail)
    rep.append("- phase runtime: %.1f s (pool extension: %.1f s)" % (ph3, ph1b))
    rep.append("- verdict: %s" % ("PASS" if c2_fail == 0 and len(sel2) == 30 else "FAIL"))
    rep.append("")

    # ---------------- Phase 4: CLI contract smoke ----------------------------
    smoke_ok, smoke_lines = _cli_smoke()
    if not smoke_ok:
        ok = False
        problems.append("CLI SMOKE FAILURE")
    rep.append("## Validation 4: CLI contract smoke (subprocess)")
    rep.append("")
    rep.extend(smoke_lines)
    rep.append("")
    rep.append("- verdict: %s" % ("PASS" if smoke_ok else "FAIL"))
    rep.append("")

    total = time.time() - t_all

    # ---------------- Report -------------------------------------------------
    head = []
    head.append("# BUILD_B.md -- Engine B (engineB_lrrule.py) build + validation log")
    head.append("")
    head.append("- Date: %s" % time.strftime("%Y-%m-%dT%H:%M:%S"))
    head.append("- File: problems_external/ktt_lr_negativity/engine/engineB_lrrule.py")
    head.append("- Python: %s" % sys.version.split()[0])
    head.append("- Reproduce: `python engineB_lrrule.py --selftest` (writes this file)")
    head.append("- Random seed: %d (deterministic)" % SELFTEST_SEED)
    head.append("- Total selftest runtime: %.1f s" % total)
    head.append("")
    head.append("## Algorithm (independence statement)")
    head.append("")
    head.append("Engine B counts c(nu; lam, mu) directly by the classical")
    head.append("Littlewood-Richardson rule: semistandard skew tableaux of shape nu/lam,")
    head.append("content mu, whose reverse reading word (rows top->bottom, right->left)")
    head.append("is a lattice word. Rows are filled right-to-left, which makes the")
    head.append("placement order equal to the reverse-reading-word order, so the lattice")
    head.append("condition is enforced incrementally at every cell. Memoization:")
    head.append("row-boundary states (row, previous-row overlap slice, content vector)")
    head.append("and in-row states (column, weak-increase bound, content vector, placed")
    head.append("slice inside the next row's overlap). All arithmetic is native Python")
    head.append("big-integer; there is NO floating point in any mathematical decision.")
    head.append("It does NOT use the hive model and reads no other engine code.")
    head.append("CAP_EXCEEDED semantics: printed when the exact count provably exceeds")
    head.append("the user cap (early abort is sound: any completed sub-count is a lower")
    head.append("bound for the total) or when DP states exceed %d." % MAX_STATES_DEFAULT)
    head.append("")

    tail = []
    tail.append("## Overall verdict")
    tail.append("")
    if problems:
        tail.append("FAIL -- %d problem(s):" % len(problems))
        tail.extend("  - " + p for p in problems[:200])
    else:
        tail.append("ALL VALIDATIONS PASS")
        tail.append("")
        tail.append("- Phase 1: %d/%d triples match brute-force Schur ground truth (100%%)."
                    % (triples, triples))
        tail.append("- Phase 1c: %d/%d high-multiplicity triples match (max c = %d)."
                    % (hi_triples, hi_triples, hi_maxc))
        tail.append("- Phase 2: 30/30 random c=1 triples give P(n) = 1 for n = 0..5.")
        tail.append("- Phase 3: 30/30 random c=2 triples give P(n) = n+1 for n = 0..5.")
        tail.append("- Phase 4: CLI contract (single, cap, empty, batch) exercised via")
        tail.append("  subprocess -- all as specified.")
    tail.append("")

    report = "\n".join(head + rep + tail)
    out_path = os.path.join(SCRIPT_DIR, "BUILD_B.md")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(report)

    print("selftest: pairs=%d triples=%d nonzero=%d maxc=%d mismatches=%d"
          % (pairs, triples, nonzero, maxc, n_mm))
    print("selftest: hi-mult triples=%d maxc=%d mismatches=%d"
          % (hi_triples, hi_maxc, hi_mm))
    print("selftest: c1 stretched fails=%d/30, c2 stretched fails=%d/30, cli_smoke=%s"
          % (c1_fail, c2_fail, "PASS" if smoke_ok else "FAIL"))
    print("selftest: pools c1=%d c2=%d (extension sizes: %s)"
          % (len(pool1u), len(pool2u), ext_sizes if ext_sizes else "none needed"))
    print("selftest: report written to %s" % out_path)
    print("selftest: %s (%.1f s)" % ("ALL PASS" if ok else "FAIL", total))
    if problems:
        for p in problems[:50]:
            print("PROBLEM: %s" % p)
    return 0 if ok else 1


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def run_deep(fn):
    """Run fn on a thread with a large stack (deep recursion on long rows)."""
    sys.setrecursionlimit(2_000_000)
    box = {}

    def target():
        try:
            box["v"] = fn()
        except BaseException as e:  # noqa: BLE001 - propagate to main thread
            box["e"] = e

    threading.stack_size(64 * 1024 * 1024)  # < CPython Windows cap of 0x10000000
    t = threading.Thread(target=target)
    t.start()
    t.join()
    if "e" in box:
        raise box["e"]
    return box.get("v", 0)


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return run_deep(selftest)

    if len(argv) >= 2 and argv[1] == "--batch":
        if len(argv) != 3:
            print("usage: engineB_lrrule.py --batch FILE", file=sys.stderr)
            return 2
        path = argv[2]

        def work():
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        fields = [x.strip() for x in line.split(";")]
                        if len(fields) == 3:
                            ls, ms, ns = fields
                            cap = None
                        elif len(fields) == 4:
                            ls, ms, ns, cs = fields
                            cap = int(cs) if cs != "" else None
                        else:
                            raise ValueError("expected 3 or 4 ;-separated fields")
                        lam = parse_partition(ls)
                        mu = parse_partition(ms)
                        nu = parse_partition(ns)
                        try:
                            print(lr_count(lam, mu, nu, cap=cap))
                        except CapExceeded:
                            print("CAP_EXCEEDED")
                    except CapExceeded:
                        print("CAP_EXCEEDED")
                    except Exception as e:  # malformed line: keep 1:1 line mapping
                        print("ERROR:%s" % str(e).replace("\n", " "))
                    sys.stdout.flush()
            return 0

        return run_deep(work)

    if len(argv) in (4, 5):
        try:
            lam = parse_partition(argv[1])
            mu = parse_partition(argv[2])
            nu = parse_partition(argv[3])
            cap = int(argv[4]) if len(argv) == 5 else None
        except Exception as e:
            print("ERROR:%s" % e, file=sys.stderr)
            return 2

        def work():
            try:
                print(lr_count(lam, mu, nu, cap=cap))
            except CapExceeded:
                print("CAP_EXCEEDED")
            return 0

        return run_deep(work)

    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
