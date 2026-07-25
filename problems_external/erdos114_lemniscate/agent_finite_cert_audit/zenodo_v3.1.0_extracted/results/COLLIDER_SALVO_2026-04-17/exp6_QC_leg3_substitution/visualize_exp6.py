#!/usr/bin/env python3
"""Generate visualization: 4x2 grid of subword complexity and diffraction plots."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.fft import fft
import json

# Load results
with open("exp6_results.json", "r") as f:
    results = json.load(f)

# Re-generate substitutions for plotting
class SubstitutionSystem:
    def __init__(self, rules, start='a'):
        self.rules = rules
        self.start = start
        self.alphabet = set(rules.keys())

    def iterate(self, n_iterations):
        word = self.start
        for _ in range(n_iterations):
            word = ''.join(self.rules.get(c, c) for c in word)
        return word

    def get_long_word(self, target_length=100000):
        n_iter = 1
        word = self.iterate(n_iter)
        while len(word) < target_length:
            n_iter += 1
            word = self.iterate(n_iter)
        return word[:target_length]

substitutions = {
    "Fibonacci": SubstitutionSystem({"a": "ab", "b": "a"}),
    "Thue-Morse": SubstitutionSystem({"a": "ab", "b": "ba"}),
    "Tribonacci": SubstitutionSystem({"a": "ab", "b": "ac", "c": "a"}),
    "SALVO_target": SubstitutionSystem({"a": "aab", "b": "b"})
}

# Create figure with 4x2 grid
fig = plt.figure(figsize=(14, 16))
gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.25)

sub_names = ["Fibonacci", "Thue-Morse", "Tribonacci", "SALVO_target"]

for idx, name in enumerate(sub_names):
    # Get word
    word = substitutions[name].get_long_word(100000)

    # ===== Left: Subword Complexity =====
    ax_left = fig.add_subplot(gs[idx, 0])

    p_n = results["substitutions"][name]["subword_complexity"]
    n_vals = sorted([int(k) for k in p_n.keys()])
    p_vals = [p_n[str(n)] for n in n_vals]

    ax_left.plot(n_vals, p_vals, 'o-', linewidth=2, markersize=6, label='p(n)')
    ax_left.set_xlabel('Length n', fontsize=10)
    ax_left.set_ylabel('Distinct subwords p(n)', fontsize=10)
    ax_left.set_title(f'{name} - Subword Complexity\n({results["substitutions"][name]["complexity_growth"]})',
                      fontsize=11, fontweight='bold')
    ax_left.grid(True, alpha=0.3)
    ax_left.legend(fontsize=9)

    # ===== Right: Diffraction Intensity =====
    ax_right = fig.add_subplot(gs[idx, 1])

    # Compute diffraction
    indicator = np.array([1.0 if c == 'a' else 0.0 for c in word])
    N = len(word)
    fft_vals = fft(indicator)
    S_q = fft_vals / N
    intensity = np.abs(S_q[:N//2])**2
    q_vals = 2 * np.pi * np.arange(N//2) / N

    ax_right.semilogy(q_vals, intensity + 1e-12, linewidth=1, alpha=0.7, label='|S(q)|²')
    ax_right.set_xlabel('Wavevector q', fontsize=10)
    ax_right.set_ylabel('Intensity |S(q)|² (log)', fontsize=10)
    ax_right.set_title(f'{name} - Diffraction\n({results["substitutions"][name]["diffraction_class"]})',
                       fontsize=11, fontweight='bold')
    ax_right.grid(True, alpha=0.3, which='both')
    ax_right.set_xlim([0, 2*np.pi])

plt.suptitle('EXP6: PHYS-QC-001 Leg-3 Generalization — Substitution Invariants',
             fontsize=14, fontweight='bold', y=0.995)

plt.savefig("exp6_plot.png", dpi=150, bbox_inches='tight')
print("[VIZ] Saved exp6_plot.png")
plt.close()
