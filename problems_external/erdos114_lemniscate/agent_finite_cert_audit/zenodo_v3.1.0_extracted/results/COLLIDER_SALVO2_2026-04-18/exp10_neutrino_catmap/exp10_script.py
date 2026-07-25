#!/usr/bin/env python3
"""
EXPERIMENT 10 — NEUTRINO-CLASS on Arnold cat map (clean chiral test)

EXP9 hit the anomaly sector because the doubling map is 2-to-1 and its
Ulam-Galerkin L has a topologically-protected kernel (σ_min ≈ 0 by
construction). To surface the Banks-Casher / neutrino sector we need
an INJECTIVE hyperbolic operator.

The Arnold cat map  M(x,y) = (2x+y, x+y) mod 1  on T² is:
  - 1-to-1 (det M = 1)
  - Anosov (hyperbolic, uniformly expanding / contracting)
  - measure-preserving
  - canonical model for "quantum chaos" and the chiral random-matrix
    correspondence in the Ulam-Galerkin discretization

State space is the torus T² discretized on a W×W grid → state count
N = W². Same three criteria as EXP9:
  (i)   microscopic scaling σ_min · N → universal
  (ii)  M_L kink at soft edge ε ∝ 1/N dominates bulk ε ∝ 1/√N
  (iii) flavor-mixing oscillation (singular vector basis entropy)
"""

import json, math
from pathlib import Path
import numpy as np

RNG = np.random.default_rng(20260418)
M_L = math.log(2) ** 2  # 0.4805


def build_catmap(W, M=8000):
    """Ulam-Galerkin for cat map on W×W torus grid.

    State index: k = i*W + j for cell (i/W, j/W).
    Map: (x, y) -> (2x + y, x + y) mod 1.
    Returns N×N matrix where N = W².
    """
    N = W * W
    L = np.zeros((N, N))
    for i in range(W):
        for j in range(W):
            src = i * W + j
            # Sample M points uniformly in cell [i/W, (i+1)/W) × [j/W, (j+1)/W)
            xs = (i + RNG.uniform(0, 1, M)) / W
            ys = (j + RNG.uniform(0, 1, M)) / W
            # Apply cat map
            xn = (2 * xs + ys) % 1.0
            yn = (xs + ys) % 1.0
            # Target cell indices
            ti = np.minimum((xn * W).astype(int), W - 1)
            tj = np.minimum((yn * W).astype(int), W - 1)
            tgt = ti * W + tj
            # Accumulate column
            np.add.at(L[:, src], tgt, 1.0 / M)
    return L


def measure(L, eps, n_reps):
    """Same observable set as EXP9."""
    N = L.shape[0]
    smins = []
    micros = []
    mixings = []
    for _ in range(n_reps):
        E = RNG.standard_normal(L.shape) * eps
        Ln = L + E
        U, s, Vt = np.linalg.svd(Ln)
        smin = float(s[-1])
        smins.append(smin)
        micros.append(smin * N)
        v = Vt[-1, :]
        p = np.abs(v) ** 2
        p = p[p > 1e-14]
        H = -np.sum(p * np.log(p))
        mixings.append(float(H / math.log(N)))
    return {
        "sigma_min_mean": float(np.mean(smins)),
        "sigma_min_std": float(np.std(smins)),
        "micro_mean": float(np.mean(micros)),
        "micro_std": float(np.std(micros)),
        "mixing_mean": float(np.mean(mixings)),
        "mixing_std": float(np.std(mixings)),
    }


def find_kink_log(eps_grid, y_grid, eps_star, window=0.4):
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
    # State count N = W²; keep N ≤ 625 (W=25) for SVD tractability
    Ws = [10, 14, 18, 22]
    eps_grid = np.unique(np.round(np.concatenate([
        np.logspace(-4, -2, 10),
        np.logspace(-2, 0, 16),
    ]), 5))
    n_reps = 12

    data = {
        "experiment": "NEUTRINO-CLASS-CATMAP",
        "date": "2026-04-18",
        "description": "Chiral soft-edge test on Arnold cat map (injective)",
        "particle": "sigma_min of Ulam-Galerkin cat-map (neutrino analog)",
        "M_L": M_L,
        "Ws": Ws,
        "state_counts_N": [W * W for W in Ws],
        "eps_grid": eps_grid.tolist(),
        "n_reps": n_reps,
        "by_W": {},
    }

    print("=" * 70)
    print("EXPERIMENT 10: NEUTRINO-CLASS on Arnold cat map")
    print(f"M_L = {M_L:.5f}")
    print("=" * 70)

    clean_micros = []
    for W in Ws:
        N = W * W
        print(f"\nW = {W}  (N = W² = {N})...")
        L = build_catmap(W)

        # Clean measurement
        clean = measure(L, 0.0, n_reps=1)
        clean_micros.append(clean["micro_mean"])
        print(f"  clean σ_min = {clean['sigma_min_mean']:.5f}  "
              f"(σ_min · N = {clean['micro_mean']:.3f})")

        # Sweep noise
        rows = []
        for e in eps_grid:
            r = measure(L, float(e), n_reps=n_reps)
            r["eps"] = float(e)
            rows.append(r)
        data["by_W"][str(W)] = rows

        eps_soft = M_L / N              # chiral soft edge: 1/N
        eps_bulk = M_L / math.sqrt(N)   # bulk: 1/√N
        y_sig = [r["sigma_min_mean"] for r in rows]
        y_mix = [r["mixing_mean"] for r in rows]
        k_soft_sig, s_soft_sig = find_kink_log(eps_grid, y_sig, eps_soft)
        k_bulk_sig, s_bulk_sig = find_kink_log(eps_grid, y_sig, eps_bulk)
        k_soft_mix, s_soft_mix = find_kink_log(eps_grid, y_mix, eps_soft)

        print(f"  σ_min kink @ M_L/N  ≈ {eps_soft:.5f}: loc={k_soft_sig}, str={s_soft_sig:.2f}")
        print(f"  σ_min kink @ M_L/√N ≈ {eps_bulk:.4f}: loc={k_bulk_sig}, str={s_bulk_sig:.2f}")
        print(f"  mixing kink @ M_L/N: loc={k_soft_mix}, str={s_soft_mix:.2f}")

        data.setdefault("kinks", {})[str(W)] = {
            "eps_soft_prediction": eps_soft,
            "eps_bulk_prediction": eps_bulk,
            "sigma_kink_at_soft": {"eps": k_soft_sig, "strength": s_soft_sig},
            "sigma_kink_at_bulk": {"eps": k_bulk_sig, "strength": s_bulk_sig},
            "mixing_kink_at_soft": {"eps": k_soft_mix, "strength": s_soft_mix},
        }

    # Microscopic scaling universality
    print("\nClean microscopic σ_min · N:")
    for W, m in zip(Ws, clean_micros):
        print(f"  W={W} (N={W*W}): {m:.4f}")
    spread = float(np.std(clean_micros) / (abs(np.mean(clean_micros)) + 1e-12))
    print(f"  relative spread: {spread:.3f}  (universal if < ~0.2)")
    data["microscopic_scaling"] = {
        "Ws": Ws, "Ns": [W * W for W in Ws],
        "sigma_min_times_N_clean": clean_micros, "spread": spread,
    }

    # Flavor oscillation
    mixing_ranges = []
    for W in Ws:
        ys = [r["mixing_mean"] for r in data["by_W"][str(W)]]
        mixing_ranges.append({"W": W, "N": W * W, "min": float(min(ys)),
                              "max": float(max(ys)), "range": float(max(ys) - min(ys))})
    data["flavor_oscillation"] = mixing_ranges
    max_range = max(r["range"] for r in mixing_ranges)
    print(f"\nFlavor-mixing range (max across W): {max_range:.3f}")

    # Verdict
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
        msg = ("Cat map exhibits universal microscopic σ_min·N scaling, "
               "soft-edge dominant M_L kink, and nontrivial flavor-mixing. "
               "Third universality class confirmed on injective hyperbolic "
               "operator. Chiral Erdős morphisms form a distinct ν-sector.")
    elif passes == 2:
        verdict = "NEUTRINO_CLASS_PARTIAL"
        msg = f"2/3 criteria: {criteria}. Suggestive; needs stronger operator or wider W."
    elif passes == 1:
        verdict = "NEUTRINO_CLASS_WEAK"
        msg = f"Only 1/3 criteria: {criteria}. Cat map chirality reduces to existing class."
    else:
        verdict = "NEUTRINO_CLASS_NULL"
        msg = "No neutrino signature; cat map chirality is bosonic/fermionic in disguise."

    data["verdict"] = verdict
    data["verdict_msg"] = msg
    data["criteria"] = criteria
    print(f"\nVERDICT: {verdict}")
    print(msg)

    with (outdir / "exp10_results.json").open("w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults: {outdir}/exp10_results.json")

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
            ax.errorbar(eps, y, yerr=ys, marker="o",
                        label=f"W={W}, N={W*W}", color=c,
                        capsize=2, lw=1.1, ms=4)
            ax.axvline(M_L / (W * W), color=c, ls=":", lw=0.8, alpha=0.5)
        ax.axvline(M_L, color="red", ls="--", lw=1.0, label=f"M_L={M_L:.3f}")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("noise ε"); ax.set_ylabel("σ_min")
        ax.set_title("(a) cat-map soft mode σ_min(ε)")
        ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)

        ax = axes[1]
        for W, c in zip(Ws, colors):
            rows = data["by_W"][str(W)]
            eps = [r["eps"] for r in rows]
            y = [r["micro_mean"] for r in rows]
            ax.plot(eps, y, marker="o", label=f"W={W}", color=c, lw=1.1, ms=4)
        ax.axvline(M_L, color="red", ls="--", lw=1.0)
        ax.set_xscale("log")
        ax.set_xlabel("noise ε"); ax.set_ylabel("σ_min · N (microscopic)")
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

        fig.suptitle("EXP10: neutrino-class test on Arnold cat map (injective hyperbolic)",
                     y=1.01, fontsize=12)
        fig.tight_layout()
        fig.savefig(outdir / "exp10_plot.png", dpi=140, bbox_inches="tight")
        print(f"Plot: {outdir}/exp10_plot.png")
    except Exception as e:
        print(f"Plot skipped: {e}")


if __name__ == "__main__":
    main()
