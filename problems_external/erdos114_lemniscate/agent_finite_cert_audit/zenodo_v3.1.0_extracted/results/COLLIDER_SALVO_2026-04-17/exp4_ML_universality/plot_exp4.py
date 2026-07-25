#!/usr/bin/env python3
"""
Generate 3x2 grid visualization for EXP4 results.
Row = map type, Col = (τ vs ε overlay, crossover fit log-log)
"""

import json, math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load results
results_path = Path(__file__).parent / "exp4_results.json"
with open(results_path) as f:
    results = json.load(f)

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle("EXP4 — Mendoza's Limit Universality Meta-Test", fontsize=16, fontweight='bold')

maps_list = ["tent", "arnold", "random_markov"]
colors = {'tent': '#1f77b4', 'arnold': '#ff7f0e', 'random_markov': '#2ca02c'}
labels_map = {
    'tent': 'Tent T(x)=1−2|x−1/2|',
    'arnold': 'Arnold cat (1D proj)',
    'random_markov': 'Random stochastic (RMT)'
}

for idx, map_name in enumerate(maps_list):
    map_data = results["maps"][map_name]
    color = colors[map_name]

    # ===== LEFT: τ vs ε overlay =====
    ax_left = axes[idx, 0]

    Ws = sorted([int(w) for w in map_data["sweep"].keys()])
    for W in Ws:
        sweep_rows = map_data["sweep"][str(W)]
        epsilons = [r["eps"] for r in sweep_rows]
        mus = [r["mu_tau2"] for r in sweep_rows]
        ax_left.semilogx(epsilons, mus, 'o-', label=f"W={W}", linewidth=2, markersize=4, alpha=0.7)

    # Mark clean tau as horizontal lines
    tau_clean_vals = map_data["clean_tau"]
    for W in Ws:
        tau_c = tau_clean_vals[str(W)]
        ax_left.axhline(tau_c, color='gray', linestyle=':', alpha=0.4, linewidth=1)

    ax_left.set_xlabel("Noise amplitude ε", fontsize=11)
    ax_left.set_ylabel("τ₂ (observed)", fontsize=11)
    ax_left.set_title(f"{labels_map[map_name]} — Noise Response", fontsize=12, fontweight='bold')
    ax_left.legend(loc='best', fontsize=9)
    ax_left.grid(True, alpha=0.3)

    # ===== RIGHT: Crossover fit (log-log) =====
    ax_right = axes[idx, 1]

    crossovers = []
    Ws_fit = []
    for W in Ws:
        cx = map_data["crossover_50"].get(str(W))
        if cx is not None:
            crossovers.append(cx)
            Ws_fit.append(W)

    if len(crossovers) >= 2 and "fit" in map_data:
        fit_info = map_data["fit"]
        slope = fit_info["slope"]
        intercept = fit_info["intercept"]
        prefactor = fit_info["prefactor"]
        residual = fit_info["rms_residual"]

        # Plot data
        ax_right.loglog(Ws_fit, crossovers, 'o', color=color, markersize=8, label="Measured ε_cross", zorder=3)

        # Plot fit line
        W_theory = np.array(Ws_fit)
        eps_theory = prefactor * W_theory ** slope
        ax_right.loglog(W_theory, eps_theory, '--', color=color, linewidth=2.5, label=f"Fit: {prefactor:.3f}W^{slope:.3f}")

        # Overlay RMT reference (W^-0.5)
        W_ref = np.logspace(np.log10(min(Ws_fit))-0.1, np.log10(max(Ws_fit))+0.1, 100)
        rmt_scale = 0.5 * W_ref ** (-0.5)  # (1-τ*)/2 ≈ 0.5
        ax_right.loglog(W_ref, rmt_scale, ':', color='red', linewidth=2, alpha=0.6, label=f"RMT: 0.5·W^−0.5")

        # ML reference if applicable
        if map_data["M_L_ref"]:
            M_L_val = map_data["M_L_ref"]
            ax_right.axhline(M_L_val, color='purple', linestyle='-.', linewidth=2, alpha=0.6, label=f"M_L={M_L_val:.4f}")

        ax_right.set_xlabel("Dimension W", fontsize=11)
        ax_right.set_ylabel("Crossover ε (50%)", fontsize=11)
        ax_right.set_title(f"Crossover Scaling (slope={slope:.3f}, residual={residual:.4f})", fontsize=12, fontweight='bold')
        ax_right.legend(loc='best', fontsize=9)
        ax_right.grid(True, alpha=0.3, which='both')

        # Add verdict badge
        if "hypothesis_verdict" in map_data:
            verdict = map_data["hypothesis_verdict"]["verdict"]
            verdict_color = {'M_L_WINS': 'purple', 'RMT_WINS': 'red', 'MIXED': 'orange'}[verdict]
            ax_right.text(0.98, 0.02, verdict, transform=ax_right.transAxes, fontsize=11, fontweight='bold',
                         bbox=dict(boxstyle='round', facecolor=verdict_color, alpha=0.3), ha='right', va='bottom')

plt.tight_layout()
plt.savefig(Path(__file__).parent / "exp4_plot.png", dpi=150, bbox_inches='tight')
print("✓ Saved exp4_plot.png")
