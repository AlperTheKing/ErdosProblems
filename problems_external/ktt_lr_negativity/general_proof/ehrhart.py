#!/usr/bin/env python3
"""
Validated general-r hive Ehrhart engine.

P(n) = c(n*nu; n*lam, n*mu) computed by engine A (lr_hive.exe), then the exact
h*-vector and monomial coefficients are recovered by interpolation.  Degree is
detected by finite differences (P is a genuine polynomial, period 1).  Every
h* is HELD-OUT verified against extra evaluation points.  All arithmetic exact.
"""
import os, subprocess, sys, tempfile
from fractions import Fraction
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ENGINE = os.path.join(ROOT, "engine", "lr_hive.exe")
sys.path.insert(0, os.path.join(ROOT, "hstar_spread"))
from crit import wrow  # noqa


def _fmt(part, n):
    v = [n * x for x in part]
    v = [x for x in v if x != 0]
    return ",".join(map(str, v)) if v else "0"


def eval_batch(triples_stretches, node_cap=None):
    """triples_stretches: list of (lam,mu,nu,n).  Returns list of ints/None
    (None = CAP_EXCEEDED / ERROR)."""
    lines = []
    for lam, mu, nu, n in triples_stretches:
        lines.append("%s;%s;%s" % (_fmt(lam, n), _fmt(mu, n), _fmt(nu, n)))
    fd, bf = tempfile.mkstemp(suffix=".batch", prefix="_eh_%d_" % os.getpid(),
                              dir=HERE)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        env = dict(os.environ)
        if node_cap is not None:
            env["LR_HIVE_NODE_CAP"] = str(node_cap)
        out = subprocess.run([ENGINE, "--batch", bf], capture_output=True,
                             text=True, env=env).stdout.split("\n")
    finally:
        try:
            os.remove(bf)
        except OSError:
            pass
    res = []
    for s in out:
        s = s.strip()
        if s == "":
            continue
        if s in ("CAP_EXCEEDED", "ERROR"):
            res.append(None)
        else:
            res.append(int(s))
    return res


def hstar_from_values(P, d):
    return [sum((-1) ** i * comb(d + 1, i) * P[j - i] for i in range(j + 1))
            for j in range(d + 1)]


def analyze(lam, mu, nu, node_cap=20 * 10 ** 8):
    """Return dict with hstar, coeffs, degree, R1, verified.  Raises on cap."""
    r = len(nu)
    D = (r - 1) * (r - 2) // 2           # full-dim upper bound on degree
    N = D + 2                            # evaluate n=0..N
    vals = eval_batch([(lam, mu, nu, n) for n in range(N + 1)], node_cap)
    if len(vals) != N + 1:
        raise RuntimeError("engine returned %d/%d lines (truncated/CAP)" %
                           (len(vals), N + 1))
    if any(v is None for v in vals):
        raise RuntimeError("CAP at n in %s" %
                           [n for n, v in enumerate(vals) if v is None])
    # detect degree via finite differences
    diff = list(vals)
    d = 0
    for k in range(1, N + 1):
        diff = [diff[i + 1] - diff[i] for i in range(len(diff) - 1)]
        if all(x == 0 for x in diff):
            d = k - 1
            break
    else:
        d = N
    h = hstar_from_values(vals, d)
    # held-out verification on n=d+1..N
    for n in range(d + 1, N + 1):
        pred = sum(h[j] * comb(n + d - j, d) for j in range(d + 1))
        if pred != vals[n]:
            raise RuntimeError("heldout FAIL n=%d pred=%d act=%d" %
                               (n, pred, vals[n]))
    R1 = _ratio(h, 1) if d >= 2 else Fraction(0)
    return dict(hstar=h, degree=d, values=vals, R1=R1, M=sum(h),
                verified=True)


def _ratio(h, k):
    d = len(h) - 1
    W = wrow(d, k)
    pos = sum(h[j] * W[j] for j in range(d + 1) if W[j] > 0)
    neg = sum(-h[j] * W[j] for j in range(d + 1) if W[j] < 0)
    if pos == 0:
        return None
    return Fraction(neg, pos)


def maxR(h):
    d = len(h) - 1
    best = Fraction(0); bk = -1
    for k in range(1, d):
        r = _ratio(h, k)
        if r is not None and r > best:
            best = r; bk = k
    return best, bk


if __name__ == "__main__":
    # quick smoke on c=2 family (P=n+1) and a known r=5 triple
    r = analyze([2, 1], [2, 1], [3, 2, 1])
    print("c=2 smoke: deg", r["degree"], "hstar", r["hstar"], "(expect deg1 [1,1])")
    r = analyze([8, 6, 5, 4, 2, 1], [8, 6, 5, 4, 2, 1], [12, 11, 9, 8, 7, 5],
                node_cap=10 ** 11)
    print("champion: deg", r["degree"], "R1", float(r["R1"]),
          "M", r["M"], "hstar", r["hstar"])
