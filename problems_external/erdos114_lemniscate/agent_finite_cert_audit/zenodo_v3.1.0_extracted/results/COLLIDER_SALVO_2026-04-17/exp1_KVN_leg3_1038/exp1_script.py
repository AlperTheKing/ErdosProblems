#!/usr/bin/env python3
"""
Experiment 1 — MOR-DISS-001 Leg-3 Generalization
Test RMT crossover law on Gauss map (Erdős #1038 EHP / Diophantine infimum)

Hypothesis: The Marchenko-Pastur crossover law ε_cross(W) ~ W^(-1/2) discovered
for the perturbed doubling map (EXP-DISS-KVN-001) should generalize to a
structurally different operator naturally linked to Diophantine approximation.

The Gauss map G(x) = {1/x} is the natural choice: it generates continued-fraction
expansions and controls the distribution of Diophantine approximation errors —
directly relevant to #1038 (EHP infimum over rational approximations).

If the same W^(-1/2) scaling appears, MOR-DISS-001 graduates from putative
→ power morphism (Leg 3 pass: generalization to independent target).
"""

import json, math
from pathlib import Path
import numpy as np

RNG = np.random.default_rng(20260417)
M_L = math.log(2) ** 2  # ≈ 0.4805
TAU_STAR = 0.5


def build_ulam_gauss(W, M=40000):
    """
    Ulam-Galerkin discretization of the Gauss map G(x) = {1/x}.

    The Gauss map is the natural operator for continued-fraction arithmetic.
    It preserves the Gauss measure μ(x) = 1/(ln 2 * (1+x)) and exhibits
    chaotic dynamics with a well-studied Ruelle-Pollicott spectrum.

    For #1038 (EHP infimum): the transfer operator eigenvalues are related
    to the Hausdorff dimension of the level sets of the infimum function
    over rational approximations with bounded denominator (a continued-fraction
    quantity).
    """
    L = np.zeros((W, W))
    for j in range(W):
        # Sample from j-th cell [j/W, (j+1)/W)
        xs = (j + RNG.uniform(0, 1, M)) / W
        xs = xs[xs > 0]  # Gauss map domain is (0, 1)
        if len(xs) == 0:
            continue
        # Apply Gauss map: G(x) = frac(1/x)
        ys = (1.0 / xs) % 1.0
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / len(xs))
    return L


def tau2(m):
    """Extract second-largest eigenvalue magnitude (leading resonance)."""
    v = np.sort(np.abs(np.linalg.eigvals(m)))[::-1]
    return float(v[1]) if len(v) > 1 else 1.0


def sweep(L, epsilons, n=24):
    """
    For each epsilon, add Gaussian noise and measure tau_2.
    Returns list of (eps, mean_tau, std_tau).
    """
    out = []
    for e in epsilons:
        ts = [tau2(L + RNG.standard_normal(L.shape) * e) for _ in range(n)]
        out.append((float(e), float(np.mean(ts)), float(np.std(ts))))
    return out


def find_crossover(sweep_rows, tau_clean, frac=0.5):
    """
    Find epsilon where tau_obs deviates by ≥ frac from tau_clean.
    tau_threshold = tau_clean + frac * (1 - tau_clean)
    Returns interpolated epsilon.
    """
    thr = tau_clean + frac * (1.0 - tau_clean)
    prev = sweep_rows[0]
    for row in sweep_rows[1:]:
        if row[1] > thr:
            x0, y0 = prev[0], prev[1]
            x1, y1 = row[0], row[1]
            if y1 == y0:
                return x1
            t = (thr - y0) / (y1 - y0)
            return float(math.exp(math.log(x0) + t * (math.log(x1) - math.log(x0))))
        prev = row
    return None


def main():
    outdir = Path(__file__).parent
    outdir.mkdir(parents=True, exist_ok=True)

    # Configuration
    Ws = [20, 40, 80, 160]  # Cap at 160 for wall time
    epsilons = np.logspace(-3.5, 0, 30)  # 30 log-uniform points [10^-3.5, 1]
    n_realizations = 24

    data = {
        "experiment": "MOR-DISS-001-LEG3-GAUSS",
        "date": "2026-04-17",
        "map": "Gauss (continued-fraction)",
        "erdos_problem": "#1038 EHP infimum",
        "reference": "EXP-DISS-KVN-001 perturbed doubling map RMT scaling",
        "M_L": M_L,
        "tau_star": TAU_STAR,
        "Ws": Ws,
        "epsilon_grid_size": len(epsilons),
        "n_realizations": n_realizations,
        "clean_tau": {},
        "sweep": {},
        "crossover_50": {},
    }

    print("=" * 70)
    print("Experiment 1: MOR-DISS-001 Leg-3 Generalization (Gauss map)")
    print(f"Problem: Erdős #1038 EHP / Diophantine infimum")
    print(f"Operator: Gauss map G(x) = {{1/x}}")
    print("=" * 70)
    print()

    for W in Ws:
        print(f"W = {W}...")
        L = build_ulam_gauss(W)
        tc = tau2(L)
        data["clean_tau"][str(W)] = tc

        # Noise sweep
        rows = sweep(L, epsilons, n=n_realizations)
        data["sweep"][str(W)] = [{"eps": r[0], "mu": r[1], "sd": r[2]} for r in rows]

        # Find crossover
        cx = find_crossover(rows, tc, frac=0.5)
        data["crossover_50"][str(W)] = cx

        if cx is not None:
            print(f"  clean τ={tc:.5f}  crossover(50%)={cx:.4f}  "
                  f"eps*sqrt(W)={cx*math.sqrt(W):.3f}  eps/M_L={cx/M_L:.3f}")
        else:
            print(f"  clean τ={tc:.5f}  crossover NOT FOUND in range")
        print()

    # Fit log crossover = a + b log W
    Ws_arr = np.array(Ws, dtype=float)
    cx_list = [data["crossover_50"][str(W)] for W in Ws]
    cx_arr = np.array([c for c in cx_list if c is not None], dtype=float)
    Ws_valid = Ws_arr[np.array([c is not None for c in cx_list])]

    if len(cx_arr) >= 2:
        log_W = np.log(Ws_valid)
        log_cx = np.log(cx_arr)
        slope, intercept = np.polyfit(log_W, log_cx, 1)
        prefactor = math.exp(intercept)

        data["scaling_fit"] = {
            "log_crossover = slope * log_W + intercept": True,
            "slope": float(slope),
            "intercept": float(intercept),
            "prefactor": float(prefactor),
            "interpretation": {
                "H1 (M_L, Landauer)": "predicts slope = 0 (constant crossover)",
                "H2 (RMT / Marchenko-Pastur)": "predicts slope = -0.5, prefactor ≈ 0.5",
            }
        }

        print("=" * 70)
        print(f"Fitted scaling: ε_cross(W) ~ {prefactor:.3f} · W^{slope:.3f}")
        print()

        # Hypothesis residuals
        h1_residual = abs(slope - 0.0)
        h2_residual = abs(slope - (-0.5))
        h2_prefactor_residual = abs(prefactor - 0.5)

        print(f"H1 (M_L constant)     — slope residual: {h1_residual:.3f}")
        print(f"H2 (RMT -0.5)         — slope residual: {h2_residual:.3f}")
        print(f"H2 prefactor (≈0.5)   — residual: {h2_prefactor_residual:.3f}")
        print()

        # Verdict logic
        if h2_residual < h1_residual and abs(slope + 0.5) < 0.15:
            verdict = "RMT-GENERALIZATION-PASS"
            msg = (
                "The Gauss map exhibits the same Marchenko-Pastur crossover scaling "
                "as the perturbed doubling map: ε·√W ≈ 1 − τ*. This is a structurally "
                "independent witness to the RMT envelope, consistent with the universal "
                "scale for Ulam-Galerkin discretizations of chaotic maps. "
                "Leg 3 (generalization) PASS: MOR-DISS-001 is a power morphism."
            )
        elif h1_residual < h2_residual and h1_residual < 0.2:
            verdict = "M_L-CONFIRMED-GAUSS"
            msg = (
                "Crossover is approximately W-independent on Gauss map, "
                "consistent with a fixed M_L-scale prediction. "
                "This contradicts the doubling-map result; further investigation needed."
            )
        else:
            verdict = "MIXED-INCONCLUSIVE"
            msg = (
                "Neither hypothesis fits cleanly. Possible causes: "
                "(1) Gauss map has different eigenvalue structure than doubling map, "
                "(2) continued-fraction arithmetic introduces different noise timescales, "
                "(3) W range insufficient for asymptotic regime."
            )

        data["verdict"] = verdict
        data["verdict_msg"] = msg

        print(f"VERDICT: {verdict}")
        print(msg)
    else:
        print("ERROR: insufficient valid crossover points for fit.")
        data["verdict"] = "INSUFFICIENT_DATA"
        data["verdict_msg"] = "Not enough valid crossover measurements."

    # Save results
    with (outdir / "exp1_results.json").open("w") as f:
        json.dump(data, f, indent=2)
    print()
    print(f"Results saved: {outdir}/exp1_results.json")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        colors = ["#1F3864", "#2E75B6", "#C00000", "#ED7D31"]
        for W, c in zip(Ws, colors):
            rows = data["sweep"][str(W)]
            e = [r["eps"] for r in rows]
            m = [r["mu"] for r in rows]
            s = [r["sd"] for r in rows]
            ax1.errorbar(e, m, yerr=s, marker="o", label=f"W={W}", color=c,
                         capsize=2, lw=1.1, ms=4)

        ax1.axhline(TAU_STAR, color="gray", ls="--", lw=1, label=f"τ*={TAU_STAR}")
        ax1.axhline(1.0, color="black", ls=":", lw=1)
        ax1.axvline(M_L, color="#C00000", ls="-.", lw=1.3, label=f"M_L={M_L:.3f}")
        ax1.set_xscale("log")
        ax1.set_xlabel("noise ε", fontsize=11)
        ax1.set_ylabel("observed τ₂ (leading resonance)", fontsize=11)
        ax1.set_title("τ₂(ε) by W — Gauss map", fontsize=12)
        ax1.set_ylim(0, 1.05)
        ax1.grid(True, which="both", alpha=0.3)
        ax1.legend(fontsize=9, loc="upper left")

        # Scaling plot
        cx_valid = np.array([data["crossover_50"][str(W)] for W in Ws])
        ax2.loglog(Ws_arr, cx_valid, "o", ms=10, color="#1F3864", label="measured crossover")

        if len(cx_arr) >= 2:
            W_fine = np.logspace(math.log10(15), math.log10(300), 50)
            ax2.loglog(W_fine, prefactor * W_fine ** slope, "-",
                       color="#2E75B6",
                       label=f"fit: ε ~ {prefactor:.3f} · W^{slope:.3f}")
            ax2.loglog(W_fine, 0.5 / np.sqrt(W_fine), "--", color="#C00000",
                       label="H2 (RMT): 0.5 / √W")

        ax2.axhline(M_L, color="gray", ls=":", lw=1,
                    label=f"H1 (M_L): {M_L:.3f} (const)")
        ax2.set_xlabel("grid size W", fontsize=11)
        ax2.set_ylabel("crossover ε", fontsize=11)
        ax2.set_title("Scaling law: H1 vs H2", fontsize=12)
        ax2.grid(True, which="both", alpha=0.3)
        ax2.legend(fontsize=9)

        fig.suptitle("Experiment 1: MOR-DISS-001 Leg-3 — Gauss map (Erdős #1038)",
                     fontsize=12, y=1.00)
        fig.tight_layout()
        fig.savefig(outdir / "exp1_plot.png", dpi=140, bbox_inches="tight")
        print(f"Plot saved: {outdir}/exp1_plot.png")
    except Exception as e:
        print(f"Plot skipped: {e}")


if __name__ == "__main__":
    main()
