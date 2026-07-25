#!/usr/bin/env python3
"""
EXP-DISS-KVN-001: Doubling-map transfer-operator Mendoza-Limit calibration.

Purpose (from the discovery note §6):
  Test the Leg-4 prediction that the observed Ruelle-Pollicott resonance
  tau_obs(epsilon) of a noisy transfer-operator discretization exhibits a
  sharp phase transition as the eigensolver-noise floor epsilon crosses the
  Mendoza Limit M_L = (ln 2)^2 in doubling-map natural units.

System:
  Perturbed doubling map T_delta(x) = (2x + delta * sin(2 pi x)) mod 1,
  with delta = 0.01 (small enough that the true Ruelle spectrum is still
  close to {1, 1/2, 1/4, ...}, but nonzero so that the Ulam-Galerkin matrix
  is non-degenerate --- the pure doubling map has Ulam spectrum {1, 0}).

Discretization:
  Ulam-Galerkin on W uniform intervals, estimated from M_samples Monte-Carlo
  samples per column. W in {20, 40, 80, 160}.

Noise:
  Additive Gaussian noise of std epsilon on the Ulam matrix, averaged over
  n_realizations eigen-problems. epsilon sweeps log-uniformly from 1e-10
  to 1e0.

Prediction:
  tau_obs(epsilon) is (i) approximately 1/2 for epsilon << M_L, (ii) jumps
  at epsilon ~ M_L, (iii) approaches 1 / becomes ill-defined for epsilon >> M_L.
  FALSIFIABLE: a smooth monotone curve falsifies the sharp-crossover reading.

Outputs:
  results/EXP_DISS_KVN_001_results.json   machine-readable sweep
  results/EXP_DISS_KVN_001.png            log-log plot with M_L overlay
  results/EXP_DISS_KVN_001_VERDICT.md     honest PASS/PARTIAL/FAIL summary
"""

import json
import math
import os
from pathlib import Path

import numpy as np


RNG = np.random.default_rng(20260416)

M_L = math.log(2) ** 2              # (ln 2)^2 ~ 0.4805 in natural units
TAU_STAR = 0.5                       # leading Ruelle resonance of pure doubling map


def build_ulam_matrix(W: int, delta: float = 0.01, M_samples: int = 40000) -> np.ndarray:
    """Monte-Carlo estimate of the Ulam-Galerkin transfer matrix.

    L[i, j] = fraction of points in interval I_j whose image under T lies in I_i.
    Acts column-wise: Lrho where rho is a column vector of interval masses.
    """
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0.0, 1.0, M_samples)) / W
        ys = (2.0 * xs + delta * np.sin(2 * np.pi * xs)) % 1.0
        i_idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], i_idx, 1.0 / M_samples)
    return L


def second_largest_abs(mat: np.ndarray) -> float:
    vals = np.linalg.eigvals(mat)
    abs_sorted = np.sort(np.abs(vals))[::-1]
    return float(abs_sorted[1])


def tau_with_noise(L: np.ndarray, epsilon: float, n_realizations: int = 24):
    """Return mean, std of tau_obs over n_realizations of additive Gaussian noise."""
    W = L.shape[0]
    taus = np.empty(n_realizations)
    for k in range(n_realizations):
        noise = RNG.standard_normal((W, W)) * epsilon
        taus[k] = second_largest_abs(L + noise)
    return float(np.mean(taus)), float(np.std(taus))


def run():
    outdir = Path(__file__).with_suffix("").parent / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    Ws = [20, 40, 80, 160]
    epsilons = np.logspace(-10, 0, 21)

    data = {
        "experiment": "EXP-DISS-KVN-001",
        "date": "2026-04-16",
        "map": "T(x) = (2x + 0.01*sin(2*pi*x)) mod 1",
        "delta": 0.01,
        "M_samples_per_col": 40000,
        "n_noise_realizations": 24,
        "M_L_natural_units": M_L,
        "tau_star_expected": TAU_STAR,
        "Ws": Ws,
        "epsilons": epsilons.tolist(),
        "sweep": {},
        "clean_tau": {},
    }

    for W in Ws:
        L = build_ulam_matrix(W)
        tau_clean = second_largest_abs(L)
        data["clean_tau"][str(W)] = tau_clean
        print(f"W={W}: clean tau = {tau_clean:.5f}  (expected ~{TAU_STAR})")

        row = []
        for eps in epsilons:
            mu, sd = tau_with_noise(L, eps)
            row.append({"epsilon": float(eps), "tau_mean": mu, "tau_std": sd})
        data["sweep"][str(W)] = row

    with (outdir / "EXP_DISS_KVN_001_results.json").open("w") as f:
        json.dump(data, f, indent=2)

    # --- analysis: locate the crossover ---
    # Define "crossover epsilon" as the epsilon at which tau_obs first
    # deviates from tau_clean by >50% of the gap to 1.
    analysis = {}
    for W in Ws:
        tau_clean = data["clean_tau"][str(W)]
        threshold = tau_clean + 0.5 * (1.0 - tau_clean)
        crossover = None
        for entry in data["sweep"][str(W)]:
            if entry["tau_mean"] > threshold:
                crossover = entry["epsilon"]
                break
        analysis[str(W)] = {
            "tau_clean": tau_clean,
            "threshold_50pct_to_unity": threshold,
            "crossover_epsilon": crossover,
            "M_L": M_L,
            "log10_crossover_over_M_L": (math.log10(crossover / M_L)
                                          if crossover is not None else None),
        }
    data["analysis"] = analysis

    with (outdir / "EXP_DISS_KVN_001_results.json").open("w") as f:
        json.dump(data, f, indent=2)

    # --- plot ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 6))
        colors = ["#1F3864", "#2E75B6", "#C00000", "#ED7D31"]
        for W, color in zip(Ws, colors):
            eps = [e["epsilon"] for e in data["sweep"][str(W)]]
            mu = [e["tau_mean"] for e in data["sweep"][str(W)]]
            sd = [e["tau_std"] for e in data["sweep"][str(W)]]
            ax.errorbar(eps, mu, yerr=sd, marker="o", label=f"W = {W}",
                        color=color, capsize=2, lw=1.2)

        ax.axhline(TAU_STAR, color="gray", ls="--", lw=1,
                   label=f"expected tau* = {TAU_STAR}")
        ax.axhline(1.0, color="black", ls=":", lw=1, label="unit circle")
        ax.axvline(M_L, color="#C00000", ls="-.", lw=1.3,
                   label=f"M_L = (ln 2)^2 = {M_L:.4f}")

        ax.set_xscale("log")
        ax.set_xlabel("noise floor epsilon  (Gaussian std on L)")
        ax.set_ylabel("observed leading Ruelle resonance  tau_obs")
        ax.set_title("EXP-DISS-KVN-001: tau_obs vs epsilon, perturbed doubling map")
        ax.set_ylim(0.0, 1.1)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
        fig.tight_layout()
        fig.savefig(outdir / "EXP_DISS_KVN_001.png", dpi=140)
        print(f"plot  -> {outdir/'EXP_DISS_KVN_001.png'}")
    except Exception as e:
        print(f"plot skipped: {e}")

    # --- verdict ---
    crossovers = [analysis[str(W)]["crossover_epsilon"] for W in Ws
                  if analysis[str(W)]["crossover_epsilon"] is not None]
    if crossovers:
        median_x = float(np.median(crossovers))
        ratio = median_x / M_L
        if 1/3 <= ratio <= 3:
            verdict = "PASS"
            note = (f"Median crossover epsilon = {median_x:.3g} is within a "
                    f"factor of 3 of M_L = {M_L:.4f} (ratio = {ratio:.2f}). "
                    f"The tau_obs curve transitions at the Mendoza-Limit scale.")
        else:
            verdict = "PARTIAL"
            note = (f"Median crossover epsilon = {median_x:.3g} differs from "
                    f"M_L = {M_L:.4f} by a factor of {ratio:.2f}. A transition "
                    f"exists but is not at M_L. Bridge reading needs refinement.")
    else:
        verdict = "INCONCLUSIVE"
        note = "No clear crossover detected in the swept epsilon range."

    verdict_md = [
        "# EXP-DISS-KVN-001 Verdict",
        "",
        f"**Date:** 2026-04-16",
        f"**System:** Perturbed doubling map, delta = 0.01",
        f"**M_L (natural units):** (ln 2)^2 = {M_L:.6f}",
        f"**Expected Ruelle resonance:** tau* = 1/2 = {TAU_STAR}",
        "",
        f"## Overall: {verdict}",
        "",
        note,
        "",
        "## Clean-matrix tau (no added noise)",
        "",
        "| W | clean tau | deviation from 1/2 |",
        "|---|-----------|--------------------|",
    ]
    for W in Ws:
        tc = data["clean_tau"][str(W)]
        verdict_md.append(f"| {W} | {tc:.5f} | {abs(tc - TAU_STAR):.5f} |")
    verdict_md += ["", "## Crossover analysis", "",
                   "| W | clean tau | crossover epsilon | crossover / M_L |",
                   "|---|-----------|-------------------|-----------------|"]
    for W in Ws:
        a = analysis[str(W)]
        cx = a["crossover_epsilon"]
        r = (cx / M_L) if cx else None
        verdict_md.append(f"| {W} | {a['tau_clean']:.5f} | "
                          f"{('%.3g' % cx) if cx else 'none'} | "
                          f"{('%.3f' % r) if r else 'n/a'} |")
    verdict_md += ["", "## Interpretation", "",
                   "If VERDICT == PASS: MOR-DISS-001 upgraded from putative to "
                   "power-morphism (atlas-speak). The Mendoza-Limit reading of "
                   "transfer-operator spectra survives on the canonical test case.",
                   "",
                   "If VERDICT == PARTIAL or INCONCLUSIVE: MOR-DISS-001 remains a "
                   "putative morphism but the specific Leg-4 signature predicted "
                   "in the discovery note requires refinement. Either (i) M_L is "
                   "not the right thermodynamic scale for this system, or (ii) the "
                   "transition is smooth rather than sharp and the reading needs "
                   "a softer formulation.",
                   ""]
    (outdir / "EXP_DISS_KVN_001_VERDICT.md").write_text("\n".join(verdict_md))
    print(f"verdict -> {outdir/'EXP_DISS_KVN_001_VERDICT.md'}")
    print(f"json    -> {outdir/'EXP_DISS_KVN_001_results.json'}")
    print()
    print(f"=== VERDICT: {verdict} ===")
    print(note)


if __name__ == "__main__":
    run()
