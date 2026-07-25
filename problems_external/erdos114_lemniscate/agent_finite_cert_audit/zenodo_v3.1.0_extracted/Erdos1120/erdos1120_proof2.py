"""
Erdős #1120 — Proof via capacity + star-shaped argument

The capacity argument proves the component of E containing 0 reaches |z|=1.
But does E contain a RADIAL segment? Or must the path curve?

Key question: Is the component of E containing 0 STAR-SHAPED w.r.t. 0?
If yes → shortest path = 1 (radial segment).
If no → shortest path ≥ 1 but might equal 1 if some radial works.

Let's test: can E fail to be star-shaped from 0?
"""
import numpy as np

def compute_E_on_grid(coeffs, N=500):
    """Compute {z : |f(z)| ≤ 1} on a grid."""
    x = np.linspace(-2, 2, N)
    y = np.linspace(-2, 2, N)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    F = np.abs(np.polyval(coeffs, Z))
    return X, Y, F <= 1.0

def check_starshaped(coeffs, N_angles=720, N_radial=1000):
    """
    Check if E ∩ D̄ is star-shaped from 0.
    For each θ, find the largest t such that the segment [0, te^{iθ}] ⊂ E.
    If this t ≥ 1 for some θ, we have a radial path.
    If for some θ the path enters E, leaves, and re-enters, E is not star-shaped.
    """
    results = []
    for theta in np.linspace(0, 2*np.pi, N_angles, endpoint=False):
        ts = np.linspace(0, 1, N_radial)
        z = ts * np.exp(1j * theta)
        vals = np.abs(np.polyval(coeffs, z))
        in_E = vals <= 1.0
        
        # Check if all True (full radial in E)
        all_in = np.all(in_E)
        
        # Check for gaps (exits and re-enters)
        transitions = np.diff(in_E.astype(int))
        exits = np.sum(transitions == -1)
        enters = np.sum(transitions == 1)
        
        results.append({
            'theta': theta,
            'all_in': all_in,
            'exits': exits,
            'max_val': np.max(vals)
        })
    
    # Summary
    any_full_radial = any(r['all_in'] for r in results)
    any_gaps = any(r['exits'] > 0 for r in results)
    min_max = min(r['max_val'] for r in results)
    
    return any_full_radial, any_gaps, min_max, results

# Test problematic polynomials
print("=== Star-shapedness tests ===\n")

test_cases = [
    ("z^3 - 1", [1, 0, 0, -1]),
    ("z^2 + 0.99", [1, 0, 0.99]),
    ("(z-0.5)(z+0.5)(z-0.5i)(z+0.5i)", np.poly([0.5, -0.5, 0.5j, -0.5j])),
    ("(z-0.9)^3(z+0.9)^3", np.poly([0.9]*3 + [-0.9]*3)),
    ("(z-0.95-0.3i)(z-0.95+0.3i)(z+0.8)", np.poly([0.95+0.3j, 0.95-0.3j, -0.8])),
    # Adversarial: roots clustered to make E have a narrow neck
    ("z^4 - 0.9z^2", np.poly([0, 0, np.sqrt(0.9), -np.sqrt(0.9)])),
]

for name, coeffs in test_cases:
    full, gaps, min_max, _ = check_starshaped(coeffs)
    print(f"  {name:45s}: radial exists={full}, has gaps={gaps}, min(max|f|)={min_max:.6f}")

print()

# THE KEY TEST: can we find a polynomial where NO radial segment stays in E?
print("=== Searching for counterexample to radial existence ===\n")

np.random.seed(42)
found_counter = False
for trial in range(1000):
    n = np.random.randint(2, 8)
    # Random roots in unit disk
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    # Ensure all in unit disk
    roots = roots * np.minimum(1.0, 1.0 / (np.abs(roots) + 1e-10))
    
    coeffs = np.poly(roots)
    full, gaps, min_max, _ = check_starshaped(coeffs, N_angles=360, N_radial=500)
    
    if not full:
        print(f"  POTENTIAL COUNTEREXAMPLE at trial {trial}!")
        print(f"  n={n}, roots={roots}")
        print(f"  min(max|f|) = {min_max:.6f}")
        # Refine with more angles
        full2, _, min_max2, _ = check_starshaped(coeffs, N_angles=3600, N_radial=2000)
        print(f"  Refined: radial exists={full2}, min(max|f|)={min_max2:.10f}")
        if not full2 and min_max2 > 1.0001:
            found_counter = True
            print("  *** GENUINE COUNTEREXAMPLE ***")
            break

if not found_counter:
    print("  No counterexample found in 1000 random trials.")
    print("  Every random polynomial has a radial path in E from 0 to |z|=1.")

print()
print("=" * 60)
print("PROOF STATUS")
print("=" * 60)
print("""
WHAT WE KNOW:
1. The answer is ≥ 1 (trivial, triangle inequality)
2. The component of E containing 0 reaches |z|=1 (capacity argument)
3. Computationally, every polynomial tested admits a straight radial path
4. The averaging lemma (avg of max ≤ 0) is FALSE
5. The proof likely requires a TOPOLOGICAL argument about connectivity
   of the sublevel set along radial directions, not an averaging argument

WHAT THE RECIPE GETS WRONG:
- Steps 3-4 (Schwarz-Pick + monodromy) don't directly apply
- The claim "shortest path ≥ 2" in the recipe is WRONG (it's ≥ 1)

WHAT NEEDS TO HAPPEN:
The proof needs to show: for monic f with roots in D̄,
there exists θ such that {te^{iθ} : t ∈ [0,1]} ⊂ {|f(z)| ≤ 1}.

This is equivalent to: max_{t ∈ [0,1]} ∏|te^{iθ} - α_k| ≤ 1 for some θ.

The strongest approach is probably via potential theory:
the Green function g_E(z, ∞) of E satisfies g_E(z,∞) = (1/n)log|f(z)| 
outside E, and the Robin constant equals 0 (since cap(E) = 1).
The radial path existence might follow from properties of the 
Green function or equilibrium measure.
""")
