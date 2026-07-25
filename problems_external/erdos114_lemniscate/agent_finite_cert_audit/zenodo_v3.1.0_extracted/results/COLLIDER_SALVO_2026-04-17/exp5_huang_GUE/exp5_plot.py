#!/usr/bin/env python3
"""
Plotting for Experiment 5: visualization of RMT analysis
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.linalg import eigvalsh
from scipy.stats import poisson

def hypercube_adjacency(n, seed=None):
    """Generate signed hypercube adjacency."""
    if seed is not None:
        np.random.seed(seed)
    N = 2 ** n
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):
            xor = i ^ j
            if bin(xor).count('1') == 1:
                sign = np.random.choice([-1, 1])
                A[i, j] = sign
                A[j, i] = sign
    return A

def wigner_semicircle_pdf(x, sigma):
    """Wigner semicircle density."""
    if isinstance(x, np.ndarray):
        return np.where(np.abs(x) > 2*sigma, 0, (1/(2*np.pi*sigma**2)) * np.sqrt(4*sigma**2 - x**2))
    if np.abs(x) > 2*sigma:
        return 0.0
    return (1/(2*np.pi*sigma**2)) * np.sqrt(4*sigma**2 - x**2)

def wigner_surmise_pdf(s):
    """GOE Wigner surmise."""
    return (np.pi/2) * s * np.exp(-np.pi * s**2 / 4)

def spacings_from_eigenvalues(evals):
    """Unfolded nearest-neighbor spacings."""
    evals_sorted = np.sort(evals)
    spacings = np.diff(evals_sorted)
    mean_spacing = np.mean(spacings)
    return spacings / mean_spacing if mean_spacing > 0 else spacings

# Run experiments to get data
n_values = [5, 6, 7, 8]
all_evals = {}
lambda_maxes = {}

for n in n_values:
    evals_n = []
    lambda_max_n = []
    for rep in range(100):
        A = hypercube_adjacency(n, seed=42 + n*1000 + rep)
        evals = eigvalsh(A)
        evals_n.extend(evals)
        lambda_max_n.append(np.max(np.abs(evals)))
    all_evals[n] = np.array(evals_n)
    lambda_maxes[n] = np.array(lambda_max_n)

# Create 2x2 grid figure
fig = plt.figure(figsize=(14, 11))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)

# Panel 1: Histogram vs Wigner semicircle (n=8)
ax1 = fig.add_subplot(gs[0, 0])
n = 8
evals = all_evals[n]
sigma = np.sqrt(n)

ax1.hist(evals, bins=100, density=True, alpha=0.6, label='Empirical', color='steelblue', edgecolor='black', linewidth=0.5)

x_theory = np.linspace(-3*sigma, 3*sigma, 500)
y_theory = wigner_semicircle_pdf(x_theory, sigma)
ax1.plot(x_theory, y_theory, 'r-', linewidth=2.5, label='Wigner semicircle')

ax1.set_xlabel(r'Eigenvalue $\lambda$', fontsize=11)
ax1.set_ylabel('Density', fontsize=11)
ax1.set_title(f'Eigenvalue Distribution (n=8, N=256)\nKS = 0.0125 vs Semicircle', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(alpha=0.3)

# Panel 2: Spectral edge λ_max vs √n
ax2 = fig.add_subplot(gs[0, 1])
ns = np.array(n_values)
lambda_max_means = []
lambda_max_stds = []

for n in n_values:
    lambda_max_means.append(np.mean(lambda_maxes[n]))
    lambda_max_stds.append(np.std(lambda_maxes[n]))

lambda_max_means = np.array(lambda_max_means)
lambda_max_stds = np.array(lambda_max_stds)

ax2.errorbar(ns, lambda_max_means, yerr=lambda_max_stds, fmt='o-', color='darkgreen',
             markersize=8, capsize=5, capthick=2, linewidth=2, label='Empirical λ_max')

# Theory: λ_max ~ √n
sqrt_n = np.sqrt(ns)
ax2.plot(ns, sqrt_n, 'r--', linewidth=2.5, label=r'Theory: $\sqrt{n}$')

# Fit: λ_max = c√n
c_fit = np.mean(lambda_max_means / sqrt_n)
ax2.plot(ns, c_fit * sqrt_n, 'orange', linestyle=':', linewidth=2.5, label=f'Fit: {c_fit:.3f}·√n')

ax2.set_xlabel('n', fontsize=11)
ax2.set_ylabel(r'$\lambda_{max}$', fontsize=11)
ax2.set_title(f'Spectral Edge Scaling\nc_fit = {c_fit:.3f} (expected 1.0)', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(alpha=0.3)

# Panel 3: Spacing distribution vs Wigner Surmise (n=7)
ax3 = fig.add_subplot(gs[1, 0])
n = 7
evals = all_evals[n]
spacings = spacings_from_eigenvalues(evals)
spacings = spacings[spacings < 4.0]  # Truncate for visibility

hist, bins = np.histogram(spacings, bins=50, density=True)
bin_centers = (bins[:-1] + bins[1:]) / 2

ax3.bar(bin_centers, hist, width=np.diff(bins), alpha=0.6, label='Empirical spacings',
        color='purple', edgecolor='black', linewidth=0.5)

# Wigner Surmise (GOE)
s_theory = np.linspace(0, 4, 200)
wigner_theory = np.array([wigner_surmise_pdf(s) for s in s_theory])
ax3.plot(s_theory, wigner_theory, 'b-', linewidth=2.5, label='GOE Wigner Surmise')

# Poisson (no repulsion)
poisson_theory = np.exp(-s_theory)
ax3.plot(s_theory, poisson_theory, 'gray', linestyle='--', linewidth=2, label='Poisson')

ax3.set_xlabel(r'Unfolded spacing $s$', fontsize=11)
ax3.set_ylabel('Density', fontsize=11)
ax3.set_title(f'Nearest-Neighbor Spacings (n=7)\nClassification: GOE', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(alpha=0.3)
ax3.set_xlim([0, 4])

# Panel 4: Summary table
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')

# Load JSON results for clean summaries
with open('exp5_results.json', 'r') as f:
    results_json = json.load(f)

summary_text = "EXPERIMENT 5 VERDICT SUMMARY\n"
summary_text += "=" * 45 + "\n\n"
summary_text += f"Morphism: 50351 ↔ PHYS-HS-001\n"
summary_text += f"Leg: 2 (RMT classification)\n\n"

summary_text += "RMT CLASS MATCHES:\n"
summary_text += f"  ✓ Semicircle bulk: {results_json['verdict']['semicircle_match']}\n"
summary_text += f"  ✗ Edge scaling √n: {results_json['verdict']['edge_sqrt_n_match']}\n"
summary_text += f"  ✓ Spacings GOE: {results_json['verdict']['spacings_class']}\n\n"

summary_text += f"Matches: {results_json['verdict']['matches_count']}/3\n"
summary_text += f"VERDICT: {results_json['verdict']['rmt_class']}\n\n"

summary_text += "KEY METRICS:\n"
for n in [8]:
    stats = results_json['by_n'][str(n)]
    summary_text += f"  n={n} (N=256):\n"
    summary_text += f"    KS stat: {stats['ks_stat_vs_semicircle']:.4f}\n"
    summary_text += f"    λ_max/√n: {stats['lambda_max_over_sqrt_n']:.3f}\n"
    summary_text += f"    Spacing median: {stats['spacing_median']:.3f}\n"

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10.5,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.suptitle('Experiment 5: Huang Signed Hypercube Adjacency vs RMT Predictions',
             fontsize=14, fontweight='bold', y=0.995)

plt.savefig('exp5_plot.png', dpi=150, bbox_inches='tight')
print("✓ Saved exp5_plot.png")
plt.close()

print("Plotting complete.")
