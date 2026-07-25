#!/usr/bin/env python3
"""
Experiment 6 — PHYS-QC-001 Leg-3 Generalization Across Substitution Systems
Tests whether PHYS-QC-001 (quasicrystal/Meyer set) is universal on Pisot substitutions

Substitutions under test:
1. Fibonacci: a→ab, b→a (Pisot, λ=φ≈1.618)
2. Thue-Morse: a→ab, b→ba (non-Pisot, eigenvalues 2,0)
3. Tribonacci: a→ab, b→ac, c→a (Pisot, λ≈1.839)
4. SALVO target: a→aab, b→b (non-primitive, eigenvalues 2,1)

Invariants computed per substitution:
- Subword complexity p(n) for n=1..20
- Substitution matrix eigenvalues
- Pisot/non-Pisot classification
- Diffraction intensity |S(q)|² for q∈[0,2π]
- Classification: PURE_POINT / SINGULAR_CONTINUOUS / ABSOLUTELY_CONTINUOUS
"""

import numpy as np
import json
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# Substitution System Generators
# =============================================================================

class SubstitutionSystem:
    """Generate long words by iterative substitution."""

    def __init__(self, rules: Dict[str, str], start: str = 'a'):
        self.rules = rules
        self.start = start
        self.alphabet = set(rules.keys())

    def iterate(self, n_iterations: int) -> str:
        """Generate word by n iterations of substitution."""
        word = self.start
        for _ in range(n_iterations):
            word = ''.join(self.rules.get(c, c) for c in word)
        return word

    def get_long_word(self, target_length: int = 100000) -> str:
        """Generate word of at least target_length."""
        n_iter = 1
        word = self.iterate(n_iter)
        while len(word) < target_length:
            n_iter += 1
            word = self.iterate(n_iter)
        return word[:target_length]

    def substitution_matrix(self) -> np.ndarray:
        """
        Return substitution matrix M where M[i,j] = # of symbol j in σ(symbol_i).
        Alphabet ordering: sorted(self.alphabet)
        """
        alphabet_list = sorted(self.alphabet)
        n = len(alphabet_list)
        M = np.zeros((n, n), dtype=int)

        for i, sym in enumerate(alphabet_list):
            image = self.rules.get(sym, sym)
            for sym2 in image:
                j = alphabet_list.index(sym2)
                M[i, j] += 1

        return M

# =============================================================================
# Invariant Extraction
# =============================================================================

def subword_complexity(word: str, max_n: int = 20) -> Dict[int, int]:
    """
    Count distinct subwords of each length n=1..max_n.
    Returns {n: count_distinct_length_n_subwords}
    """
    complexity = {}
    for n in range(1, min(max_n + 1, len(word) // 2)):
        subwords = set(word[i:i+n] for i in range(len(word) - n + 1))
        complexity[n] = len(subwords)
    return complexity

def classify_complexity_growth(p_dict: Dict[int, int]) -> str:
    """
    Classify growth pattern:
    - Linear (Sturmian): p(n) ≈ cn+d
    - Polynomial: p(n) ≈ n^k, k>1
    - Exponential: p(n) ≈ λ^n
    """
    if len(p_dict) < 3:
        return "insufficient_data"

    n_vals = np.array(sorted(p_dict.keys()))
    p_vals = np.array([p_dict[n] for n in n_vals])

    # Try linear fit
    z_lin = np.polyfit(n_vals, p_vals, 1)
    p_lin = np.polyval(z_lin, n_vals)
    rmse_lin = np.sqrt(np.mean((p_vals - p_lin)**2))
    r2_lin = 1 - np.sum((p_vals - p_lin)**2) / np.sum((p_vals - np.mean(p_vals))**2)

    # Try exponential: log(p) ≈ a*n + b
    if np.all(p_vals > 0):
        z_exp = np.polyfit(n_vals, np.log(p_vals), 1)
        p_exp = np.exp(np.polyval(z_exp, n_vals))
        rmse_exp = np.sqrt(np.mean((p_vals - p_exp)**2))
        r2_exp = 1 - np.sum((p_vals - p_exp)**2) / np.sum((p_vals - np.mean(p_vals))**2)
    else:
        r2_exp = -1

    # Classify
    if r2_lin > 0.95:
        return "linear"
    elif r2_exp > 0.95:
        return "exponential"
    else:
        return "polynomial"

def diffraction_intensity(word: str, n_q: int = 256) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute diffraction intensity |S(q)|² for wavevectors q∈[0,2π].
    S(q) = (1/N) Σ_{n=0}^{N-1} χ_{a_n=a} e^{2πi q n}

    Returns: (q_values, |S(q)|²)
    """
    N = len(word)
    # Indicator sequence: 1 if symbol is 'a', 0 otherwise
    indicator = np.array([1.0 if c == 'a' else 0.0 for c in word])

    # Compute FFT
    fft_vals = fft(indicator)
    # Normalize
    S_q = fft_vals / N
    # Intensity
    intensity = np.abs(S_q[:N//2])**2

    # Wavevectors q ∈ [0, 2π]
    q_vals = 2 * np.pi * np.arange(N//2) / N

    return q_vals, intensity

def classify_diffraction(q_vals: np.ndarray, intensity: np.ndarray) -> Tuple[str, List[float]]:
    """
    Classify diffraction spectrum and identify Bragg peaks.

    Pure-point (quasicrystal): sharp peaks at discrete q values
    Singular-continuous: fractal structure, no isolated peaks
    Absolutely continuous: smooth background
    """
    # Identify peaks: local maxima with height > mean + 2*std
    threshold = np.mean(intensity) + 2 * np.std(intensity)

    # Simple peak detection
    peaks_bool = (intensity > threshold)
    peaks_idx = np.where(peaks_bool)[0]

    # Filter: isolated peaks (not neighboring)
    isolated_peaks = []
    i = 0
    while i < len(peaks_idx):
        start = peaks_idx[i]
        while i + 1 < len(peaks_idx) and peaks_idx[i+1] - peaks_idx[i] <= 2:
            i += 1
        isolated_peaks.append(q_vals[peaks_idx[i]])
        i += 1

    n_peaks = len(isolated_peaks)
    peak_ratio = n_peaks / len(q_vals)

    # Classify
    if peak_ratio > 0.01:  # >1% of spectrum is peaks
        classification = "PURE_POINT"
    elif np.std(intensity) / (np.mean(intensity) + 1e-10) > 1.0:
        classification = "SINGULAR_CONTINUOUS"
    else:
        classification = "ABSOLUTELY_CONTINUOUS"

    return classification, isolated_peaks

def pisot_classification(M: np.ndarray) -> Tuple[str, List[complex], bool]:
    """
    Compute eigenvalues of substitution matrix M.
    Pisot condition: one eigenvalue λ>1 (the dominant root, Pisot root or Salem number),
    all others have absolute value <1.

    Returns: (classification, eigenvalues, is_pisot)
    """
    evals = np.linalg.eigvals(M)
    evals_sorted = sorted(evals, key=lambda x: abs(x), reverse=True)

    # Check Pisot condition
    # Dominant eigenvalue > 1
    is_pisot = False
    if len(evals_sorted) > 0:
        dominant = evals_sorted[0]
        if abs(dominant.imag) < 1e-10:  # Real eigenvalue
            dominant = dominant.real
            if dominant > 1.0:
                # Check that all others have |λ| < 1
                if all(abs(e) < 1.0 for e in evals_sorted[1:]):
                    is_pisot = True

    classification = "Pisot" if is_pisot else "non-Pisot"
    return classification, evals_sorted, is_pisot

# =============================================================================
# Main Experiment
# =============================================================================

def run_experiment() -> Dict:
    """Execute Experiment 6: test PHYS-QC-001 universality."""

    results = {
        "experiment": "EXP6_QC_LEG3_SUBSTITUTION",
        "date": "2026-04-17",
        "target_word_length": 100000,
        "substitutions": {}
    }

    # Define substitutions
    substitutions = {
        "Fibonacci": SubstitutionSystem({"a": "ab", "b": "a"}),
        "Thue-Morse": SubstitutionSystem({"a": "ab", "b": "ba"}),
        "Tribonacci": SubstitutionSystem({"a": "ab", "b": "ac", "c": "a"}),
        "SALVO_target": SubstitutionSystem({"a": "aab", "b": "b"})
    }

    # Process each substitution
    for name, subsys in substitutions.items():
        print(f"\n[EXP6] Processing {name}...")

        # Generate long word
        word = subsys.get_long_word(100000)
        word_length = len(word)
        print(f"  Word length: {word_length}")

        # Subword complexity
        p_n = subword_complexity(word, max_n=20)
        complexity_class = classify_complexity_growth(p_n)
        print(f"  Complexity growth: {complexity_class}")

        # Substitution matrix & eigenvalues
        M = subsys.substitution_matrix()
        pisot_class, evals, is_pisot = pisot_classification(M)
        evals_str = [f"{e.real:.6f}+{e.imag:.6f}i" if abs(e.imag) > 1e-10
                     else f"{e.real:.6f}" for e in evals]
        print(f"  Eigenvalues: {evals_str}")
        print(f"  Classification: {pisot_class}")

        # Diffraction
        q_vals, intensity = diffraction_intensity(word, n_q=256)
        diff_class, bragg_peaks = classify_diffraction(q_vals, intensity)
        print(f"  Diffraction class: {diff_class}")
        print(f"  Bragg peaks found: {len(bragg_peaks)}")

        # Store results
        results["substitutions"][name] = {
            "word_length": word_length,
            "subword_complexity": p_n,
            "complexity_growth": complexity_class,
            "substitution_matrix": M.tolist(),
            "eigenvalues": evals_str,
            "pisot_classification": pisot_class,
            "is_pisot": is_pisot,
            "diffraction_class": diff_class,
            "bragg_peak_count": len(bragg_peaks),
            "bragg_peak_locations": [float(q) for q in bragg_peaks[:10]]  # Top 10
        }

    return results

if __name__ == "__main__":
    results = run_experiment()

    # Save JSON
    output_file = "/sessions/magical-peaceful-ramanujan/mnt/Math/erdos-experiments/results/COLLIDER_SALVO_2026-04-17/exp6_QC_leg3_substitution/exp6_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[EXP6] Results saved to {output_file}")
