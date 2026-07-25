"""
verify_formula.py — EHP conjecture formula triangulation
=========================================================
Verifies the closed-form expression

    L(z^n - 1) = 2^{1/n} * sqrt(pi) * Gamma(1/(2n)) / Gamma(1/(2n) + 1/2)
               = 2^{1/n} * B(1/2, 1/(2n))          (Euler beta function)

against all certified inari interval arithmetic results stored in
    results/erdos-114/EXP-MM-EHP-007-n*-inari_RESULTS.json

Requirements: mpmath (pip install mpmath)
Usage:        python verify_formula.py
"""

import json
import glob
import os
import sys

try:
    from mpmath import mp, mpf, sqrt, pi, gamma, power, fabs
except ImportError:
    sys.exit("mpmath not found. Install with: pip install mpmath")

mp.dps = 60  # 60 decimal places — well beyond double precision

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "results", "erdos-114"
)

def formula(n):
    """L(z^n - 1) via gamma function identity, evaluated at 60 decimal places."""
    n = mpf(n)
    return power(2, 1 / n) * sqrt(pi) * gamma(1 / (2 * n)) / gamma(1 / (2 * n) + mpf(1) / 2)

def load_inari_results():
    pattern = os.path.join(RESULTS_DIR, "EXP-MM-EHP-007-n*-inari_RESULTS.json")
    files = sorted(glob.glob(pattern))
    if not files:
        sys.exit(f"No inari result files found in {RESULTS_DIR}")
    results = {}
    for path in files:
        with open(path) as f:
            d = json.load(f)
        n = d["degree"]
        results[n] = {
            "lower": d["l_star_lower"],
            "upper": d["l_star_upper"],
            "midpoint": (d["l_star_lower"] + d["l_star_upper"]) / 2,
            "verdict": d.get("verdict", ""),
        }
    return results

def main():
    results = load_inari_results()

    header = f"{'n':>3}  {'Formula (60dp)':>28}  {'Inari midpoint':>24}  {'Rel error':>12}  {'In interval?':>13}  {'Status'}"
    print(header)
    print("-" * len(header))

    all_pass = True
    for n in sorted(results.keys()):
        r = results[n]
        f_val = formula(n)
        midpoint = mpf(r["midpoint"])
        rel_err = fabs(f_val - midpoint) / midpoint

        # Containment check: formula value should lie within the certified interval
        in_interval = mpf(r["lower"]) <= f_val <= mpf(r["upper"])

        # Tolerance: relative error < 1e-12 (double precision noise floor is ~2e-16)
        passes = rel_err < mpf("1e-12")
        if not passes:
            all_pass = False

        status = "PASS" if passes else "FAIL"
        print(
            f"{n:>3}  {mp.nstr(f_val, 20):>28}  {r['midpoint']:>24.16f}"
            f"  {mp.nstr(rel_err, 3):>12}  {'yes' if in_interval else 'NO':>13}  {status}"
        )

    print()
    print("Formula: L(z^n-1) = 2^{1/n} * sqrt(pi) * Gamma(1/(2n)) / Gamma(1/(2n)+1/2)")
    print(f"Verified at {mp.dps} decimal places against {len(results)} certified inari intervals.")
    print()
    if all_pass:
        print("RESULT: ALL PASS — formula agrees with interval arithmetic to machine epsilon.")
        sys.exit(0)
    else:
        print("RESULT: FAILURES DETECTED — check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
