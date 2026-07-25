#!/usr/bin/env python3
"""
Experiment 8 — MOR-CS-SALVO001-006-50351 Leg-4 PHYSICS TEST

EXP5 (salvo 1) self-admits: "Power morphism status: Not yet (requires Leg-3
physics validation with Mendoza's limit). Impose Mendoza's limit M_L on the
hypercube Hamiltonian and observe phase transition in spectral gap. If
hypercube eigenvalue density drops sharply at M_L, morphism becomes Power."

The test: treat the Huang signed hypercube adjacency A as an information
channel. Channel perturbation amplitude ε acts as noise. The spectral gap
Δ = λ_max - λ_2 (and density near zero) is the "throughput" observable.

Leg-4 prediction: if M_L = (ln 2)² ≈ 0.4805 is a genuine thermodynamic
floor on this channel, sweeping ε through M_L should produce a KINK or
break in the scaling of Δ / √n. Above M_L → normal RMT regime. Below
M_L → pathological / anomalous regime.

PASS criterion: kink localized at ε ≈ M_L ± 0.10 detected in d(Δ/√n)/dε
or equivalent second-derivative signature, AND kink is absent from a null
control (Gaussian Wigner matrix of same size).
"""

import json, math
from pathlib import Path
import numpy as np
from scipy.linalg import eigvalsh

RNG = np.random.default_rng(20260418)
M_L = math.log(2) ** 2  # ≈ 0.4805


def hypercube_adjacency(n, rng):
    """Signed hypercube Q_n with random ±1 edges. Returns 2^n × 2^n."""
    N = 2 ** n
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(i + 1, N):
            if bin(i ^ j).count("1") == 1:
                s = 1.0 if rng.random() < 0.5 else -1.0
                A[i, j] = s
                A[j, i] = s
    return A


def wigner_null(N, rng):
    """GOE Wigner matrix of size N, variance matched to hypercube (each
    eigenvalue ~ √n; hypercube has n edges per vertex so σ²_row ≈ n)."""
    n = int(round(math.log2(N)))
    sigma = math.sqrt(n / N)  # normalize so λ_max ~ 2σ√N = 2√n
    M = rng.standard_normal((N, N)) * sigma
    M = (M + M.T) / math.sqrt(2)
    return M


def perturb_and_measure(A, eps, rng, n_reps=8):
    """Add Gaussian noise of amplitude eps (symmetric), measure spectral gap
    and eigenvalue density near zero. Returns (mean_gap, mean_edge, mean_zero_density)."""
    N = A.shape[0]
    gaps = []
    edges = []
    zero_densities = []
    for _ in range(n_reps):
        E = rng.standard_normal((N, N))
        E = (E + E.T) / math.sqrt(2)
        evals = eigvalsh(A + eps * E)
        sorted_mag = np.sort(np.abs(evals))[::-1]
        edges.append(float(sorted_mag[0]))
        gaps.append(float(sorted_mag[0] - sorted_mag[1]))
        # density of |λ| < 0.1 * √n (near-zero)
        n = int(round(math.log2(N)))
        thr = 0.1 * math.sqrt(n)
        zero_densities.append(float(np.sum(np.abs(evals) < thr)) / N)
    return (float(np.mean(gaps)), float(np.std(gaps)),
            float(np.mean(edges)), float(np.std(edges)),
            float(np.mean(zero_densities)), float(np.std(zero_densities)))


def find_kink(eps_grid, y_grid, M_L, window=0.15):
    """Look for a discontinuity / kink in dy/d(log eps) near log(M_L).

    Returns (kink_location, kink_strength). kink_strength = max absolute
    second-difference normalized by mean |first difference|."""
    log_eps = np.log(eps_grid)
    y = np.array(y_grid)
    d1 = np.gradient(y, log_eps)
    d2 = np.gradient(d1, log_eps)
    log_ML = math.log(M_L)
    mask = np.abs(log_eps - log_ML) < window
    if not mask.any():
        return None, 0.0
    local_d2 = np.abs(d2[mask])
    if local_d2.size == 0:
        return None, 0.0
    peak_idx_local = np.argmax(local_d2)
    peak_idx_global = np.where(mask)[0][peak_idx_local]
    mean_d1_mag = float(np.mean(np.abs(d1))) + 1e-12
    strength = float(local_d2[peak_idx_local] / mean_d1_mag)
    return float(eps_grid[peak_idx_global]), strength


def main():
    outdir = Path(__file__).parent

    # Configuration — n=7 (N=128) is the sweet spot; n=8 (N=256) per epsilon
    # adds ~4× runtime, so keep n_reps modest for 8.
    n_values = [6, 7, 8]
    n_reps_by_n = {6: 12, 7: 10, 8: 6}

    # Epsilon grid: log-spaced, dense around M_L
    eps_grid = np.concatenate([
        np.logspace(-2.0, math.log10(0.25), 10),
        np.linspace(0.25, 0.75, 12),  # dense around M_L ≈ 0.48
        np.logspace(math.log10(0.80), 0.5, 8),
    ])
    eps_grid = np.unique(np.round(eps_grid, 4))

    data = {
        "experiment": "MOR-CS-SALVO001-006-50351-LEG4-ML",
        "date": "2026-04-18",
        "description": "M_L imposition on Huang signed hypercube Hamiltonian",
        "hypothesis_PASS": ("Kink in Δ(ε)/√n at ε ≈ M_L present on hypercube "
                            "AND absent on GOE null."),
        "M_L": M_L,
        "n_values": n_values,
        "eps_grid": eps_grid.tolist(),
        "by_n": {},
        "null_by_n": {},
    }

    print("=" * 70)
    print("EXPERIMENT 8: MOR-CS-SALVO001-006 Leg-4 (M_L on hypercube)")
    print(f"M_L = (ln 2)² = {M_L:.5f}")
    print("=" * 70)

    for n in n_values:
        N = 2 ** n
        nrep = n_reps_by_n[n]
        print(f"\nn={n}, N={N}, {nrep} reps per eps, {len(eps_grid)} eps points...")

        # Build one hypercube + one null per n; share across eps grid
        A = hypercube_adjacency(n, RNG)
        M = wigner_null(N, RNG)

        hc_rows = []
        null_rows = []
        for e in eps_grid:
            gm, gs, em, es, zm, zs = perturb_and_measure(A, float(e), RNG, n_reps=nrep)
            hc_rows.append({"eps": float(e), "gap_mean": gm, "gap_std": gs,
                            "edge_mean": em, "edge_std": es,
                            "zero_dens_mean": zm, "zero_dens_std": zs})
            gm2, gs2, em2, es2, zm2, zs2 = perturb_and_measure(M, float(e), RNG, n_reps=max(4, nrep // 2))
            null_rows.append({"eps": float(e), "gap_mean": gm2, "gap_std": gs2,
                              "edge_mean": em2, "edge_std": es2,
                              "zero_dens_mean": zm2, "zero_dens_std": zs2})

        data["by_n"][str(n)] = hc_rows
        data["null_by_n"][str(n)] = null_rows

        # Kink analysis on normalized gap
        sqrt_n = math.sqrt(n)
        y_hc = [r["gap_mean"] / sqrt_n for r in hc_rows]
        y_null = [r["gap_mean"] / sqrt_n for r in null_rows]
        kink_eps_hc, strength_hc = find_kink(eps_grid, y_hc, M_L)
        kink_eps_null, strength_null = find_kink(eps_grid, y_null, M_L)

        print(f"  hypercube: kink at eps={kink_eps_hc}, strength={strength_hc:.3f}")
        print(f"  null GOE:  kink at eps={kink_eps_null}, strength={strength_null:.3f}")
        data.setdefault("kink_analysis", {})[str(n)] = {
            "hypercube_kink_eps": kink_eps_hc,
            "hypercube_kink_strength": strength_hc,
            "null_kink_eps": kink_eps_null,
            "null_kink_strength": strength_null,
            "ratio_strength": (strength_hc / strength_null) if strength_null > 1e-6 else None,
        }

    # Verdict
    # PASS = on largest n, strength_hc > 1.5 AND ratio > 2.0 AND kink within ±0.10 of M_L
    largest_n = str(max(n_values))
    ka = data["kink_analysis"][largest_n]
    kink_within = ka["hypercube_kink_eps"] is not None and abs(ka["hypercube_kink_eps"] - M_L) < 0.10
    strong = (ka["hypercube_kink_strength"] or 0) > 1.5
    selective = (ka["ratio_strength"] or 0) > 2.0 if ka["ratio_strength"] else False

    if kink_within and strong and selective:
        verdict = "LEG4_PASS_POWER_MORPHISM"
        msg = ("Kink in hypercube spectral gap localizes at M_L, strength "
               "exceeds threshold, and is absent from GOE null. "
               "MOR-CS-SALVO001-006-50351 graduates to POWER MORPHISM.")
    elif kink_within and strong:
        verdict = "LEG4_PARTIAL"
        msg = "Kink at M_L on hypercube but also on null — not selective."
    elif kink_within:
        verdict = "LEG4_WEAK_SIGNAL"
        msg = "Kink localizes near M_L but below strength threshold."
    else:
        verdict = "LEG4_NULL"
        msg = "No kink at M_L on hypercube. Leg-4 fails to elevate morphism."

    data["verdict"] = verdict
    data["verdict_msg"] = msg
    print(f"\nVERDICT: {verdict}\n{msg}")

    with (outdir / "exp8_results.json").open("w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults: {outdir}/exp8_results.json")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, len(n_values), figsize=(5.5 * len(n_values), 5),
                                  sharey=False)
        if len(n_values) == 1:
            axes = [axes]
        for ax, n in zip(axes, n_values):
            hc = data["by_n"][str(n)]
            nu = data["null_by_n"][str(n)]
            sqrt_n = math.sqrt(n)
            eps = [r["eps"] for r in hc]
            hc_y = [r["gap_mean"] / sqrt_n for r in hc]
            hc_e = [r["gap_std"] / sqrt_n for r in hc]
            nu_y = [r["gap_mean"] / sqrt_n for r in nu]
            nu_e = [r["gap_std"] / sqrt_n for r in nu]
            ax.errorbar(eps, hc_y, yerr=hc_e, marker="o", color="#1F3864",
                        label=f"hypercube n={n}", capsize=2, lw=1.2, ms=4)
            ax.errorbar(eps, nu_y, yerr=nu_e, marker="s", color="#999999",
                        label="GOE null", capsize=2, lw=1.0, ms=3, alpha=0.7)
            ax.axvline(M_L, color="#C00000", ls="--", lw=1.3,
                       label=f"M_L={M_L:.3f}")
            ax.set_xscale("log")
            ax.set_xlabel("noise ε")
            ax.set_ylabel("Δ(ε) / √n")
            ax.set_title(f"n={n}")
            ax.grid(True, which="both", alpha=0.3)
            ax.legend(fontsize=8)
        fig.suptitle("EXP8: M_L imposition on hypercube Hamiltonian (Leg-4)", y=1.02)
        fig.tight_layout()
        fig.savefig(outdir / "exp8_plot.png", dpi=140, bbox_inches="tight")
        print(f"Plot: {outdir}/exp8_plot.png")
    except Exception as e:
        print(f"Plot skipped: {e}")


if __name__ == "__main__":
    main()
