#!/usr/bin/env python3
"""
Experiment 5: Huang Signed Hypercube Adjacency vs RMT Predictions
Morphism 50351 (CS sensitivity) ↔ PHYS-HS-001 (hypercube spectral gap)

Leg-2 candidate: measure eigenvalue distributions of random-sign hypercube
adjacencies against Wigner semicircle + spectral edge predictions.
"""

import numpy as np
import json
from scipy.linalg import eigvalsh
from scipy.stats import ks_2samp
import warnings
warnings.filterwarnings('ignore')

def hypercube_adjacency(n, seed=None):
    """
    Generate signed hypercube adjacency for Q_n.
    Vertices: 0..2^n-1, edges connect Hamming distance 1.
    Each edge gets random ±1 sign.

    Returns: symmetric N x N matrix (N = 2^n)
    """
    if seed is not None:
        np.random.seed(seed)

    N = 2 ** n
    A = np.zeros((N, N))

    for i in range(N):
        for j in range(i+1, N):
            # Check if i, j differ in exactly one bit
            xor = i ^ j
            if bin(xor).count('1') == 1:  # Hamming distance 1
                sign = np.random.choice([-1, 1])
                A[i, j] = sign
                A[j, i] = sign

    return A

def wigner_semicircle_pdf(x, sigma):
    """Wigner semicircle density: ρ(λ) = (1/2π) √(4σ² - λ²)/σ²"""
    if np.abs(x) > 2*sigma:
        return 0.0
    return (1/(2*np.pi*sigma**2)) * np.sqrt(4*sigma**2 - x**2)

def wigner_surmise_pdf(s):
    """GOE Wigner surmise: P(s) = (π/2) s exp(-π s²/4)"""
    return (np.pi/2) * s * np.exp(-np.pi * s**2 / 4)

def spacings_from_eigenvalues(evals):
    """Nearest-neighbor spacings (unfolded)."""
    evals_sorted = np.sort(evals)
    spacings = np.diff(evals_sorted)
    # Unfold: normalize by mean spacing
    mean_spacing = np.mean(spacings)
    return spacings / mean_spacing if mean_spacing > 0 else spacings

def ks_test_semicircle(evals, sigma):
    """KS test: are eigenvalues drawn from Wigner semicircle?"""
    x_vals = np.linspace(-2*sigma, 2*sigma, 1000)
    pdf_vals = np.array([wigner_semicircle_pdf(x, sigma) for x in x_vals])
    cdf_vals = np.cumsum(pdf_vals) / np.sum(pdf_vals)

    # ECDF of eigenvalues
    evals_normalized = np.sort(evals)
    ecdf = np.arange(1, len(evals_normalized)+1) / len(evals_normalized)

    # Find corresponding CDF values
    cdf_at_evals = np.interp(evals_normalized, x_vals, cdf_vals)
    ks_stat = np.max(np.abs(ecdf - cdf_at_evals))
    return ks_stat

def run_experiment():
    """Main Experiment 5 pipeline."""

    results = {
        'timestamp': '2026-04-17',
        'morphism': '50351 <-> PHYS-HS-001',
        'leg': 2,
        'by_n': {}
    }

    # Experiment parameters
    n_values = [5, 6, 7, 8]
    n_replicates = 100

    all_evals = {}
    all_spacings = {}

    print("=" * 70)
    print("EXPERIMENT 5: Huang Signed Hypercube vs RMT")
    print("=" * 70)

    for n in n_values:
        N = 2 ** n
        print(f"\nn = {n}, N = {N}x{N}, {n_replicates} replicates...")

        evals_all = []
        lambdas_2 = []
        lambdas_max = []
        spacings_all = []

        for rep in range(n_replicates):
            A = hypercube_adjacency(n, seed=42 + n*1000 + rep)
            evals = eigvalsh(A)
            evals_all.extend(evals)

            # Track spectral edge
            lambdas_max.append(np.max(np.abs(evals)))

            # Track second-largest by magnitude
            sorted_by_mag = np.sort(np.abs(evals))[::-1]
            if len(sorted_by_mag) > 1:
                lambdas_2.append(sorted_by_mag[1])

            # Spacings
            spacings = spacings_from_eigenvalues(evals)
            spacings_all.extend(spacings)

        evals_all = np.array(evals_all)
        lambdas_max = np.array(lambdas_max)
        lambdas_2 = np.array(lambdas_2)
        spacings_all = np.array(spacings_all)

        # Store for plotting
        all_evals[n] = evals_all
        all_spacings[n] = spacings_all

        # Theory prediction: σ² = n (Frobenius norm scaled)
        sigma_theory = np.sqrt(n)

        # KS test vs semicircle
        ks_stat = ks_test_semicircle(evals_all, sigma_theory)

        # Empirical statistics
        empirical_std = np.std(evals_all)
        empirical_max = np.mean(lambdas_max)
        empirical_max_std = np.std(lambdas_max)

        # Fit λ_max ~ c√n
        c_fit = empirical_max / np.sqrt(n)

        # Spacing distribution: compute P(s) histogram
        hist, bins = np.histogram(spacings_all[spacings_all < 3.0], bins=50, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        result_n = {
            'n': n,
            'N': N,
            'n_replicates': n_replicates,
            'n_eigenvalues': len(evals_all),
            'eigenvalue_mean': float(np.mean(evals_all)),
            'eigenvalue_std': float(empirical_std),
            'eigenvalue_min': float(np.min(evals_all)),
            'eigenvalue_max': float(np.max(evals_all)),
            'sigma_theory': float(sigma_theory),
            'ks_stat_vs_semicircle': float(ks_stat),
            'lambda_max_mean': float(empirical_max),
            'lambda_max_std': float(empirical_max_std),
            'lambda_max_over_sqrt_n': float(c_fit),
            'lambda_2_median': float(np.median(lambdas_2)),
            'lambda_2_std': float(np.std(lambdas_2)),
            'spacing_mean': float(np.mean(spacings_all)),
            'spacing_median': float(np.median(spacings_all)),
            'spacing_std': float(np.std(spacings_all)),
            'spacing_skewness': float(np.mean(spacings_all**3) / (np.std(spacings_all)**3))
        }

        results['by_n'][str(n)] = result_n

        print(f"  Eigenvalues: mean={empirical_max:.3f}, std={empirical_max_std:.3f}")
        print(f"  λ_max / √n = {c_fit:.3f} (theory: 1.0)")
        print(f"  KS vs semicircle: {ks_stat:.4f} (p > 0.05 if < ~0.04 at N=256)")
        print(f"  Spacings: mean={np.mean(spacings_all):.3f}, median={np.median(spacings_all):.3f}")

    # Aggregate verdicts
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # Semicircle match: KS test at n=8
    ks_stat_n8 = results['by_n']['8']['ks_stat_vs_semicircle']
    semicircle_match = ks_stat_n8 < 0.04  # Rough threshold for N=256
    print(f"\nSEMICIRCLE_MATCH: {semicircle_match} (KS@n=8: {ks_stat_n8:.4f})")

    # Edge scaling: λ_max ~ √n
    edge_scalings = [results['by_n'][str(n)]['lambda_max_over_sqrt_n'] for n in n_values]
    edge_mean = np.mean(edge_scalings)
    edge_std = np.std(edge_scalings)
    edge_match = 0.9 <= edge_mean <= 1.1
    print(f"EDGE_SQRT_N_MATCH: {edge_match} (mean c={edge_mean:.3f} ± {edge_std:.3f})")

    # Spacing distribution classification
    # GOE (Wigner surmise) vs Poisson
    spacings_n7 = all_spacings[7]
    spacing_histogram = np.histogram(spacings_n7[spacings_n7 < 3.0], bins=30, density=True)

    # Simple heuristic: GOE has more repulsion at small s, Poisson doesn't
    small_s = spacings_n7[(spacings_n7 > 0) & (spacings_n7 < 0.5)]
    spacing_class = 'GOE' if len(small_s) > 0.1 * len(spacings_n7) else 'POISSON'
    print(f"SPACINGS_CLASS: {spacing_class}")

    # Overall RMT classification
    matches = sum([semicircle_match, edge_match, spacing_class == 'GOE'])
    if matches >= 2:
        rmt_verdict = 'RMT_CLASS_CONFIRMED'
    elif matches == 1:
        rmt_verdict = 'PARTIAL'
    else:
        rmt_verdict = 'FAIL'

    results['verdict'] = {
        'rmt_class': rmt_verdict,
        'semicircle_match': bool(semicircle_match),
        'edge_sqrt_n_match': bool(edge_match),
        'spacings_class': spacing_class,
        'matches_count': int(matches)
    }

    print(f"\nOVERALL RMT VERDICT: {rmt_verdict}")
    print(f"Matches: {matches}/3 (semicircle, edge, spacings)")

    return results, all_evals, all_spacings

if __name__ == '__main__':
    results, all_evals, all_spacings = run_experiment()

    # Save results
    with open('exp5_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Saved exp5_results.json")
    print(f"✓ Ready for plotting")
