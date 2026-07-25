#!/usr/bin/env python3
"""
EXPERIMENT 9 — NEUTRINO-CLASS collider test

Third universality class beyond the boson (EXP1/7, smooth resonance bands)
and the fermion (EXP8, Pauli-repulsion gap). In RMT this is CHIRAL
(chGOE/chGUE): an operator with γ₅-like symmetry forcing spectrum to
be ±σᵢ and creating a SOFT EDGE at λ=0 governed by Banks-Casher
ρ(0) ∝ Σ (chiral condensate analog).

Construction:
  L = Ulam-Galerkin doubling-map transfer operator (W×W)
  C = [[0, L], [L†, 0]]   — 2W×2W bipartite (chiral) embedding
  → eig(C) = {±σᵢ(L)}   — spectrum symmetric about 0

PARTICLE: σ_min (smallest singular value of L). This is the "lightest
neutrino mass" of the doubling-map dynamics. In chiral RMT, σ_min·W
follows a universal (Shuryak-Verbaarschot) microscopic distribution
independent of the bulk.

BEHAVIOR TESTS (three):
  1. Microscopic scaling   — σ_min · W → universal distribution vs W
  2. Soft-edge M_L binding — does kink appear at ε ≈ M_L/W (scaled)?
  3. Flavor oscillation    — mixing angle between σ_min eigenvector
                              in local (delta) basis vs eigenmode basis.
                              Nontrivial ε-dependence = "oscillation."

POSSIBLE OUTCOMES:
  (a) BOSONIC   — σ_min collapses into bulk RMT smearing under noise;
                  no distinct soft-edge behavior. Neutrino class is a
                  disguised boson.
  (b) FERMIONIC — soft edge is Pauli-locked; level repulsion at 0 gives
                  fixed σ_min floor; M_L geometry-shielded. Neutrino
                  class is a disguised fermion.
  (c) NEUTRINO  — distinct microscopic universal scaling AND nontrivial
                  flavor-oscillation under noise; M_L may bind at the
                  soft edge (ε_crit ≈ M_L / W) rather than the bulk
                  (ε_crit ≈ 1/√W). Third universality class confirmed.
"""

import json, math
from pathlib import Path
import numpy as np

RNG = np.random.default_rng(20260418)
M_L = math.log(2) ** 2  # 0.4805


def build_doubling(W, M=40000):
    """Ulam-Galerkin for D(x) = 2x mod 1."""
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0, 1, M)) / W
        ys = (2.0 * xs) % 1.0
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / len(xs))
    return L


def chiral_embed(L):
    """C = [[0, L], [L^T, 0]]  — bipartite/chiral. eig(C) = {±σᵢ(L)}."""
    W = L.shape[0]
    Z = np.zeros((W, W))
    top = np.hstack([Z, L])
    bot = np.hstack([L.T, Z])
    return np.vstack([top, bot])


def measure_chiral_particle(L, eps, n_reps=16):
    """Add noise E of amplitude eps to L, form C, measure:
       - σ_min (smallest singular value; soft mode)
       - σ_min · W (microscopic scaling variable)
       - flavor-mixing angle θ: how spread is the σ_min singular vector
         across delta-function basis (|v_k|²-distribution Shannon entropy
         normalized to [0,1]).
       Returns dict of means + stds.
    """
    W = L.shape[0]
    sigma_mins = []
    microscopic = []
    mixings = []
    for _ in range(n_reps):
        E = RNG.standard_normal(L.shape) * eps
        Ln = L + E
        # SVD gives singular values directly (same as |eig(C)|)
        U, s, Vt = np.linalg.svd(Ln)
        smin = float(s[-1])
        sigma_mins.append(smin)
        microscopic.append(smin * W)
        # Flavor mixing = normalized Shannon entropy of singular vector
        # of σ_min in the local (delta) basis. H_max = log(W); fully
        # delocalized ("mass eigenstate") → 1; fully localized
        # ("flavor eigenstate") → 0.
        v = Vt[-1, :]
        p = np.abs(v) ** 2
        p = p[p > 1e-14]
        H = -np.sum(p * np.log(p))
        mixings.append(float(H / math.log(W)))
    return {
        "sigma_min_mean": float(np.mean(sigma_mins)),
        "sigma_min_std": float(np.std(sigma_mins)),
        "micro_mean": float(np.mean(microscopic)),
        "micro_std": float(np.std(microscopic)),
        "mixing_mean": float(np.mean(mixings)),
        "mixing_std": float(np.std(mixings)),
    }


def find_kink_log(eps_grid, y_grid, eps_star, window=0.4):
    """Find kink via peak in |d²y/d(log ε)²| within log-window of eps_star."""
    log_eps = np.log(np.asarray(eps_grid))
    y = np.asarray(y_grid)
    d1 = np.gradient(y, log_eps)
    d2 = np.gradient(d1, log_eps)
    log_star = math.log(eps_star)
    mask = np.abs(log_eps - log_star) < window
    if not mask.any():
        return None, 0.0
    ad2 = np.abs(d2[mask])
    if ad2.size == 0:
        return None, 0.0
    i_loc = int(np.argmax(ad2))
    i_glob = np.where(mask)[0][i_loc]
    norm = float(np.mean(np.abs(d1))) + 1e-12
    return float(eps_grid[i_glob]), float(ad2[i_loc] / norm)


def main():
    outdir = Path(__file__).parent
    Ws = [20, 40, 80, 160]
    # Two eps grids to probe soft-edge (∝1/W) vs bulk (∝1/√W)
    eps_grid = np.unique(np.round(np.concatenate([
        np.logspace(-4, -2, 12),   # soft-edge regime
        np.logspace(-2, 0, 18),    # bulk regime
    ]), 5))
    n_reps = 16

    data = {
        "experiment": "NEUTRINO-CLASS-CHIRAL-DOUBLING",
        "date": "2026-04-18",
        "description": "Third universality class: chiral RMT soft-edge test",
        "particle": "sigma_min of Ulam-Galerkin doubling-map (neutrino analog)",
        "M_L": M_L,
        "Ws": Ws,
        "eps_grid": eps_grid.tolist(),
        "n_reps": n_reps,
        "by_W": {},
    }

    print("=" * 70)
    print("EXPERIMENT 9: NEUTRINO-CLASS chiral soft-edge test")
    print(f"M_L = {M_L:.5f}, particle = σ_min of doubling-map Ulam-Galerkin")
    print("=" * 70)

    for W in Ws:
        print(f"\nW = {W}...")
        L = build_doubling(W)
        rows = []
        for e in eps_grid:
            r = measure_chiral_particle(L, float(e), n_reps=n_reps)
            r["eps"] = float(e)
            rows.append(r)
        data["by_W"][str(W)] = rows

        # Clean σ_min (no noise)
        clean = measure_chiral_particle(L, 0.0, n_reps=1)
        print(f"  clean σ_min = {clean['sigma_min_mean']:.5f}  "
              f"(σ_min·W = {clean['micro_mean']:.3f})")

        # Kink analysis at two predicted scales: M_L / W (soft) vs M_L / √W (bulk)
        eps_soft = M_L / W
        eps_bulk = M_L / math.sqrt(W)
        y_sig = [r["sigma_min_mean"] for r in rows]
        y_mix = [r["mixing_mean"] for r in rows]

        k_soft_sig, s_soft_sig = find_kink_log(eps_grid, y_sig, eps_soft)
        k_bulk_sig, s_bulk_sig = find_kink_log(eps_grid, y_sig, eps_bulk)
        k_soft_mix, s_soft_mix = find_kink_log(eps_grid, y_mix, eps_soft)

        print(f"  σ_min kink @ M_L/W   ≈ {eps_soft:.4f}: loc={k_soft_sig}, str={s_soft_sig:.2f}")
        print(f"  σ_min kink @ M_L/√W  ≈ {eps_bulk:.4f}: loc={k_bulk_sig}, str={s_bulk_sig:.2f}")
        print(f"  mixing kink @ M_L/W: loc={k_soft_mix}, str={s_soft_mix:.2f}")

        data.setdefault("kinks", {})[str(W)] = {
            "eps_soft_prediction": eps_soft,
            "eps_bulk_prediction": eps_bulk,
            "sigma_kink_at_soft": {"eps": k_soft_sig, "strength": s_soft_sig},
            "sigma_kink_at_bulk": {"eps": k_bulk_sig, "strength": s_bulk_sig},
            "mixing_kink_at_soft": {"eps": k_soft_mix, "strength": s_soft_mix},
        }

    # Microscopic scaling test: clean σ_min · W should tend to a constant
    # (universal) as W → ∞ if neutrino-class universality holds.
    clean_micros = [
        measure_chiral_particle(build_doubling(W), 0.0, n_reps=1)["micro_mean"]
        for W in Ws
    ]
    data["microscopic_scaling"] = {
        "Ws": Ws,
        "sigma_min_times_W_clean": clean_micros,
        "spread": float(np.std(clean_micros) / (np.mean(clean_micros) + 1e-12)),
    }
    print("\nMicroscopic scaling σ_min · W (clean):")
    for W, m in zip(Ws, clean_micros):
        print(f"  W={W}: {m:.4f}")
    spread = data["microscopic_scaling"]["spread"]
    print(f"  relative spread: {spread:.3f}  (universal if < ~0.2)")

    # Flavor-mixing range: does the σ_min eigenvector mixing change
    # substantially with noise? Strong oscillation signature = nontrivial ν.
    mixing_ranges = []
    for W in Ws:
        ys = [r["mixing_mean"] for r in data["by_W"][str(W)]]
        mixing_ranges.append({"W": W, "min": float(min(ys)), "max": float(max(ys)),
                              "range": float(max(ys) - min(ys))})
    data["flavor_oscillation"] = mixing_ranges
    max_range = max(r["range"] for r in mixing_ranges)
    print(f"\nFlavor-mixing range (max across W): {max_range:.3f}")

    # Verdict
    # Neutrino-class evidence:
    #   (i)   universal microscopic scaling (spread < 0.2)
    #   (ii)  kink in σ_min at soft scale M_L/W, strength > kink at bulk M_L/√W
    #   (iii) nontrivial flavor-oscillation (mixing range > 0.05)
    criteria = {}
    criteria["microscopic_universal"] = spread < 0.2
    largest_W = str(max(Ws))
    k = data["kinks"][largest_W]
    criteria["soft_kink_dominates_bulk"] = (
        (k["sigma_kink_at_soft"]["strength"] or 0)
        > 1.2 * (k["sigma_kink_at_bulk"]["strength"] or 0)
    )
    criteria["flavor_oscillation_present"] = max_range > 0.05

    passes = sum(criteria.values())
    if passes == 3:
        verdict = "NEUTRINO_CLASS_CONFIRMED"
        msg = ("σ_min particle shows (i) universal microscopic scaling, "
               "(ii) M_L binds at soft edge ε∝1/W not bulk ε∝1/√W, and "
               "(iii) nontrivial flavor-oscillation under noise. "
               "Third universality class confirmed. Chiral Erdős morphisms "
               "form a distinct ν-sector alongside bosonic (transfer "
               "operator resonances) and fermionic (hypercube gaps).")
    elif passes == 2:
        verdict = "NEUTRINO_CLASS_PARTIAL"
        msg = f"2/3 criteria satisfied: {criteria}. Suggestive but not decisive."
    elif passes == 1:
        verdict = "NEUTRINO_CLASS_WEAK"
        msg = f"Only 1/3 criteria: {criteria}. Soft edge likely reduces to existing class."
    else:
        verdict = "NEUTRINO_CLASS_NULL"
        msg = ("No neutrino-class signature: soft edge reduces to existing "
               "bosonic/fermionic behavior. The chiral symmetry does not "
               "create a distinct particle in this operator.")

    data["verdict"] = verdict
    data["verdict_msg"] = msg
    data["criteria"] = criteria
    print(f"\nVERDICT: {verdict}")
    print(msg)

    with (outdir / "exp9_results.json").open("w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults: {outdir}/exp9_results.json")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
        colors = ["#1F3864", "#2E75B6", "#C00000", "#ED7D31"]

        ax = axes[0]
        for W, c in zip(Ws, colors):
            rows = data["by_W"][str(W)]
            eps = [r["eps"] for r in rows]
            y = [r["sigma_min_mean"] for r in rows]
            ys = [r["sigma_min_std"] for r in rows]
            ax.errorbar(eps, y, yerr=ys, marker="o", label=f"W={W}",
                        color=c, capsize=2, lw=1.1, ms=4)
            ax.axvline(M_L / W, color=c, ls=":", lw=0.8, alpha=0.5)
        ax.axvline(M_L, color="red", ls="--", lw=1.0, label=f"M_L={M_L:.3f}")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("noise ε"); ax.set_ylabel("σ_min (soft mode)")
        ax.set_title("(a) soft-edge particle σ_min(ε)")
        ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)

        ax = axes[1]
        for W, c in zip(Ws, colors):
            rows = data["by_W"][str(W)]
            eps = [r["eps"] for r in rows]
            y = [r["micro_mean"] for r in rows]
            ax.plot(eps, y, marker="o", label=f"W={W}", color=c, lw=1.1, ms=4)
        ax.axvline(M_L, color="red", ls="--", lw=1.0)
        ax.set_xscale("log")
        ax.set_xlabel("noise ε"); ax.set_ylabel("σ_min · W (microscopic)")
        ax.set_title("(b) microscopic scaling universality")
        ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)

        ax = axes[2]
        for W, c in zip(Ws, colors):
            rows = data["by_W"][str(W)]
            eps = [r["eps"] for r in rows]
            y = [r["mixing_mean"] for r in rows]
            ax.plot(eps, y, marker="o", label=f"W={W}", color=c, lw=1.1, ms=4)
        ax.axvline(M_L, color="red", ls="--", lw=1.0, label=f"M_L={M_L:.3f}")
        ax.set_xscale("log")
        ax.set_xlabel("noise ε"); ax.set_ylabel("mixing (normalized entropy)")
        ax.set_title("(c) flavor-mixing oscillation")
        ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)

        fig.suptitle("EXP9: NEUTRINO-class chiral soft-edge collider test",
                     y=1.01, fontsize=12)
        fig.tight_layout()
        fig.savefig(outdir / "exp9_plot.png", dpi=140, bbox_inches="tight")
        print(f"Plot: {outdir}/exp9_plot.png")
    except Exception as e:
        print(f"Plot skipped: {e}")


if __name__ == "__main__":
    main()
