"""
exp9_v2 — Chiral-RMT soft-edge test, Path B: genuinely chiral operator (bipartite Gaussian).

Pre-registered at:
  erdos-experiments/results/CLASSIFIER_BACKPROP_2026-04-19/TRACK_A_PREREGISTRATION.json

Obeys pre-registered thresholds literally. No post-hoc tuning.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy.stats import ks_2samp, spearmanr  # spearmanr unused but imported for parity with track A

# ---------------------------------------------------------------------------
# Pre-registered parameters (DO NOT EDIT — see TRACK_A_PREREGISTRATION.json)
# ---------------------------------------------------------------------------

PREREG_REF = "TRACK_A_PREREGISTRATION.json :: exp9_v2"
DATE = "2026-04-19"
WS = [20, 40, 80, 160, 320]
N_REAL = 100
SEED_BASE = 20260419
SIGMA_MIN_FLOOR = 1e-10
KS_MAX_THRESHOLD = 0.10         # C1
SOFT_OVER_BULK_MIN = 1.0        # C2 (apply to every W)
BETA_FLOOR_2SIGMA = -0.10       # C3

HERE = Path(__file__).resolve().parent
RESULTS_JSON = HERE / "exp9_v2_results.json"
REPORT_MD = HERE / "EXP9_V2_REPORT.md"


def seed_for(W: int, idx: int) -> int:
    return SEED_BASE + W * 10000 + idx


def bipartite_sigma_min(W: int, idx: int) -> tuple[float, np.ndarray]:
    """Return (sigma_min, full singular-value vector) for one realization."""
    rng = np.random.default_rng(seed_for(W, idx))
    M = 2 * W
    N = W
    scale = 1.0 / np.sqrt(W)
    A = rng.normal(0.0, scale, size=(M, N))
    # full_matrices=False gives min(M,N)=W singular values; descending.
    s = np.linalg.svd(A, full_matrices=False, compute_uv=False)
    return float(s[-1]), s  # s[-1] is smallest


def piecewise_kink_strengths(s_sorted_asc: np.ndarray) -> tuple[float, float]:
    """Numerical-derivative kink strength in the bottom 5% (soft) vs the 40-60% band (bulk).

    Operationalization per pre-registered description's 'Simpler reproducible version':
      - sort singular values ascending
      - compute first-difference derivative d[i] = s[i+1]-s[i]
      - take max |second difference| (change in derivative) restricted to each region
    """
    W = s_sorted_asc.size
    d1 = np.diff(s_sorted_asc)                    # length W-1
    d2 = np.abs(np.diff(d1))                      # length W-2, "derivative change"

    # Regions defined on the INDEX axis of d2 (which corresponds to singular-value position).
    # bottom 5% -> indices [0, floor(0.05*(W-2))] ; middle 40-60% -> floor(0.4*(W-2)) .. floor(0.6*(W-2))
    n = d2.size
    if n < 5:
        # too small to resolve; return NaNs so upstream flags it
        return float("nan"), float("nan")

    soft_hi = max(1, int(np.floor(0.05 * n)))
    bulk_lo = int(np.floor(0.40 * n))
    bulk_hi = int(np.ceil(0.60 * n))
    soft_kink = float(np.max(d2[:soft_hi]))
    bulk_kink = float(np.max(d2[bulk_lo:bulk_hi]))
    return soft_kink, bulk_kink


def run() -> dict:
    t0 = time.time()
    by_W: dict[int, dict] = {}

    # storage for C1 (filtered sigma_min * W samples) and C2/C3 (per-realization spectra stats)
    scaled_samples: dict[int, np.ndarray] = {}
    soft_bulk_ratios: dict[int, float] = {}
    range_by_W: dict[int, float] = {}

    for W in WS:
        sigma_mins = np.empty(N_REAL, dtype=np.float64)
        soft_list = np.empty(N_REAL, dtype=np.float64)
        bulk_list = np.empty(N_REAL, dtype=np.float64)

        for i in range(N_REAL):
            smin, svec = bipartite_sigma_min(W, i)
            sigma_mins[i] = smin
            s_sorted = np.sort(svec)  # ascending
            sk, bk = piecewise_kink_strengths(s_sorted)
            soft_list[i] = sk
            bulk_list[i] = bk

        # numerical floor filter for C1
        keep_mask = sigma_mins >= SIGMA_MIN_FLOOR
        n_excluded = int((~keep_mask).sum())
        sigma_kept = sigma_mins[keep_mask]
        scaled = sigma_kept * W
        scaled_samples[W] = scaled

        # C3 canonical range (P95 - P5) on filtered sigma_min * W
        if scaled.size >= 5:
            p5, p95 = np.percentile(scaled, [5.0, 95.0])
            rng_range = float(p95 - p5)
        else:
            rng_range = float("nan")
        range_by_W[W] = rng_range

        # C2 soft/bulk ratio, averaged across realizations (guard div-by-zero)
        soft_mean = float(np.nanmean(soft_list))
        bulk_mean = float(np.nanmean(bulk_list))
        ratio = soft_mean / bulk_mean if bulk_mean > 0 else float("inf")
        soft_bulk_ratios[W] = ratio

        by_W[W] = {
            "W": W,
            "n_realizations_used": int(keep_mask.sum()),
            "n_excluded_floor": n_excluded,
            "exclusion_fraction": n_excluded / N_REAL,
            "sigma_min_stats": {
                "mean": float(np.mean(sigma_mins)),
                "median": float(np.median(sigma_mins)),
                "min": float(np.min(sigma_mins)),
                "max": float(np.max(sigma_mins)),
                "std": float(np.std(sigma_mins, ddof=1)),
            },
            "sigma_min_times_W_stats": {
                "mean": float(np.mean(scaled)) if scaled.size else None,
                "median": float(np.median(scaled)) if scaled.size else None,
                "p5": float(np.percentile(scaled, 5)) if scaled.size else None,
                "p95": float(np.percentile(scaled, 95)) if scaled.size else None,
                "range_p95_minus_p5": rng_range,
                "std": float(np.std(scaled, ddof=1)) if scaled.size >= 2 else None,
            },
            "soft_kink_strength_mean": soft_mean,
            "bulk_kink_strength_mean": bulk_mean,
            "soft_over_bulk": ratio,
        }

    # ------------------------------------------------------------------
    # Criterion 1 — KS distance between consecutive W pairs on sigma_min*W
    # ------------------------------------------------------------------
    ks_pairs = []
    for a, b in zip(WS[:-1], WS[1:]):
        ks_stat, _ = ks_2samp(scaled_samples[a], scaled_samples[b], alternative="two-sided", mode="auto")
        ks_pairs.append({"pair": [a, b], "ks": float(ks_stat)})
    ks_max = max(p["ks"] for p in ks_pairs)
    c1_pass = ks_max <= KS_MAX_THRESHOLD

    # ------------------------------------------------------------------
    # Criterion 2 — soft_over_bulk ≥ 1 at EVERY W
    # ------------------------------------------------------------------
    c2_per_W = {W: (soft_bulk_ratios[W] >= SOFT_OVER_BULK_MIN) for W in WS}
    c2_pass = all(c2_per_W.values())

    # ------------------------------------------------------------------
    # Criterion 3 — log(range) = α + β log(W); β_lower (2σ) ≥ -0.1
    # ------------------------------------------------------------------
    logW = np.log(np.array(WS, dtype=float))
    ranges = np.array([range_by_W[W] for W in WS], dtype=float)
    # Guard: any nonpositive range? log would fail. Bipartite Gaussian at N_REAL=100
    # is numerically guaranteed positive, but check explicitly.
    if np.any(ranges <= 0) or np.any(~np.isfinite(ranges)):
        beta = float("nan")
        beta_se = float("nan")
        beta_lower_2sigma = float("nan")
        c3_pass = False
        c3_note = "nonpositive range encountered; cannot fit log-log model"
    else:
        logR = np.log(ranges)
        # OLS on design [1, logW]
        X = np.column_stack([np.ones_like(logW), logW])
        coef, *_ = np.linalg.lstsq(X, logR, rcond=None)
        alpha, beta = float(coef[0]), float(coef[1])
        resid = logR - X @ coef
        dof = len(WS) - 2
        sigma2 = float(np.sum(resid**2) / dof) if dof > 0 else float("nan")
        cov = sigma2 * np.linalg.inv(X.T @ X)
        beta_se = float(np.sqrt(cov[1, 1]))
        beta_lower_2sigma = beta - 2.0 * beta_se
        c3_pass = beta_lower_2sigma >= BETA_FLOOR_2SIGMA
        c3_note = "OLS on log(range_p95_p5) vs log(W); 5 points, dof=3"

    # ------------------------------------------------------------------
    # Methodology flag: exclusion fraction
    # ------------------------------------------------------------------
    max_excl_frac = max(by_W[W]["exclusion_fraction"] for W in WS)
    methodology_flag = bool(max_excl_frac > 0.05)

    # ------------------------------------------------------------------
    # Verdict (pre-registered rules)
    # ------------------------------------------------------------------
    if c1_pass and c2_pass and c3_pass:
        verdict = "CHIRAL_CLASS_CONFIRMED"
    elif not c2_pass:
        verdict = "CHIRAL_CLASS_REJECTED"
    else:
        verdict = "CHIRAL_CLASS_WEAK"

    wall = time.time() - t0

    results = {
        "experiment": "exp9_v2_chiral_rmt_bipartite_gaussian",
        "date": DATE,
        "preregistration_ref": PREREG_REF,
        "hypothesis": (
            "σ_min of genuinely chiral (bipartite Gaussian) random matrix lands in chiral-RMT "
            "universality: (C1) microscopic universality of σ_min·W after floor-filtering, "
            "(C2) soft-edge kink dominates bulk at every W, (C3) flavor-oscillation range stable "
            "or growing in W (β_lower_2σ ≥ -0.1)."
        ),
        "operator_used": "bipartite_gaussian",
        "fallback_used": False,
        "Ws": WS,
        "n_realizations_per_W": N_REAL,
        "random_seed_base": SEED_BASE,
        "numerical_floor": SIGMA_MIN_FLOOR,
        "by_W": {str(W): by_W[W] for W in WS},
        "criterion_1_KS_distances": {
            "pairs": ks_pairs,
            "max_KS": ks_max,
            "threshold": KS_MAX_THRESHOLD,
            "pass": bool(c1_pass),
        },
        "criterion_2_soft_over_bulk_by_W": {
            "ratios": {str(W): soft_bulk_ratios[W] for W in WS},
            "per_W_pass": {str(W): bool(c2_per_W[W]) for W in WS},
            "threshold": SOFT_OVER_BULK_MIN,
            "apply_to_all_W": True,
            "pass": bool(c2_pass),
        },
        "criterion_3_beta_fit": {
            "statistic": "range = P95(sigma_min*W) - P5(sigma_min*W) per W",
            "fit": "log(range) = alpha + beta * log(W), OLS, 5 points",
            "alpha": float(alpha) if "alpha" in locals() else None,
            "beta": float(beta) if isinstance(beta, float) else beta,
            "beta_se": beta_se,
            "beta_lower_2sigma": beta_lower_2sigma,
            "threshold_beta_lower_2sigma": BETA_FLOOR_2SIGMA,
            "pass": bool(c3_pass),
            "note": c3_note,
        },
        "criteria_results": {
            "C1_microscopic_universal": {
                "pass": bool(c1_pass),
                "max_KS": ks_max,
                "threshold": KS_MAX_THRESHOLD,
            },
            "C2_soft_kink_dominates_bulk": {
                "pass": bool(c2_pass),
                "ratios_by_W": {str(W): soft_bulk_ratios[W] for W in WS},
                "threshold": SOFT_OVER_BULK_MIN,
            },
            "C3_stable_flavor_oscillation": {
                "pass": bool(c3_pass),
                "beta_lower_2sigma": beta_lower_2sigma,
                "threshold": BETA_FLOOR_2SIGMA,
            },
        },
        "methodology_flag_exclusion_above_5pct": methodology_flag,
        "max_exclusion_fraction": max_excl_frac,
        "verdict": verdict,
        "wall_time_sec": wall,
        "implementation_notes": (
            "Primary operator (bipartite Gaussian M=2W, N=W, entries N(0,1/sqrt(W))) used "
            "per pre-reg rule — no implementation blocker encountered. SVD via "
            "numpy.linalg.svd(full_matrices=False). Soft and bulk kink strengths operationalized "
            "as the pre-reg 'Simpler reproducible version': max |second difference| of the "
            "ascending-sorted spectrum restricted to the bottom 5% (soft) and the middle 40-60% "
            "band (bulk), averaged across realizations. C3 range operationalized as the canonical "
            "P95−P5 of the filtered σ_min·W distribution per W (documented in output)."
        ),
    }

    RESULTS_JSON.write_text(json.dumps(results, indent=2))
    return results


def write_report(results: dict) -> None:
    c1 = results["criteria_results"]["C1_microscopic_universal"]
    c2 = results["criteria_results"]["C2_soft_kink_dominates_bulk"]
    c3 = results["criteria_results"]["C3_stable_flavor_oscillation"]

    ks_lines = "\n".join(
        f"| ({p['pair'][0]},{p['pair'][1]}) | {p['ks']:.4f} |"
        for p in results["criterion_1_KS_distances"]["pairs"]
    )

    c2_lines = "\n".join(
        f"| W={W} | {results['criterion_2_soft_over_bulk_by_W']['ratios'][str(W)]:.3f} | "
        f"{'PASS' if results['criterion_2_soft_over_bulk_by_W']['per_W_pass'][str(W)] else 'FAIL'} |"
        for W in results["Ws"]
    )

    excl_lines = "\n".join(
        f"| W={W} | {results['by_W'][str(W)]['n_excluded_floor']}/{results['n_realizations_per_W']} | "
        f"{results['by_W'][str(W)]['exclusion_fraction']*100:.1f}% |"
        for W in results["Ws"]
    )

    verdict = results["verdict"]

    md = f"""# exp9_v2 — Chiral-RMT Soft-Edge Test (Bipartite Gaussian)

**Date:** {results['date']}
**Preregistration:** `{results['preregistration_ref']}`
**Operator used:** {results['operator_used']} (primary, no fallback)
**Wall time:** {results['wall_time_sec']:.1f} s

## Verdict

**{verdict}**

Rule: C1 AND C2 AND C3 → CHIRAL_CLASS_CONFIRMED; C2 fails → CHIRAL_CLASS_REJECTED; C2 passes but C1 or C3 fails → CHIRAL_CLASS_WEAK.

## Criteria evidence

| Criterion | Threshold | Observed | Pass? |
|---|---|---|---|
| C1 microscopic universality (max KS across consecutive W) | ≤ 0.10 | {c1['max_KS']:.4f} | {"PASS" if c1['pass'] else "FAIL"} |
| C2 soft/bulk kink at every W | ≥ 1.0 at every W | min = {min(results['criterion_2_soft_over_bulk_by_W']['ratios'].values()):.3f}, max = {max(results['criterion_2_soft_over_bulk_by_W']['ratios'].values()):.3f} | {"PASS" if c2['pass'] else "FAIL"} |
| C3 flavor oscillation β_lower_2σ | ≥ −0.10 | {c3['beta_lower_2sigma']:.4f} (β = {results['criterion_3_beta_fit']['beta']:.4f}, SE = {results['criterion_3_beta_fit']['beta_se']:.4f}) | {"PASS" if c3['pass'] else "FAIL"} |

### C1 — KS distances between consecutive W

| pair | KS |
|---|---|
{ks_lines}

### C2 — soft_over_bulk per W

| W | ratio | per-W verdict |
|---|---|---|
{c2_lines}

### Floor-filter exclusion rates per W

| W | excluded / total | rate |
|---|---|---|
{excl_lines}

Max exclusion fraction: {results['max_exclusion_fraction']*100:.2f}% — methodology flag {"RAISED" if results['methodology_flag_exclusion_above_5pct'] else "not raised"} (pre-reg threshold 5%).

## Implementation notes

{results['implementation_notes']}

Seeds: `seed(W, idx) = {results['random_seed_base']} + W*10000 + idx`. Deterministic.

Artifacts: `exp9_v2_results.json` (full numerics, this directory).
"""
    REPORT_MD.write_text(md)


if __name__ == "__main__":
    res = run()
    write_report(res)
    print(f"VERDICT: {res['verdict']}")
    print(f"C1 max KS: {res['criterion_1_KS_distances']['max_KS']:.4f} (threshold {KS_MAX_THRESHOLD}) -> "
          f"{'PASS' if res['criterion_1_KS_distances']['pass'] else 'FAIL'}")
    c2_ratios = res['criterion_2_soft_over_bulk_by_W']['ratios']
    print(f"C2 soft/bulk per W: " + ", ".join(f"W={W}:{c2_ratios[str(W)]:.3f}" for W in res['Ws'])
          + f"  -> {'PASS' if res['criteria_results']['C2_soft_kink_dominates_bulk']['pass'] else 'FAIL'}")
    print(f"C3 beta = {res['criterion_3_beta_fit']['beta']:.4f} ± {res['criterion_3_beta_fit']['beta_se']:.4f}, "
          f"lower_2σ = {res['criterion_3_beta_fit']['beta_lower_2sigma']:.4f} "
          f"-> {'PASS' if res['criterion_3_beta_fit']['pass'] else 'FAIL'}")
    print(f"Max exclusion: {res['max_exclusion_fraction']*100:.2f}% "
          f"(methodology flag {'RAISED' if res['methodology_flag_exclusion_above_5pct'] else 'not raised'})")
    print(f"Wall time: {res['wall_time_sec']:.1f}s")
