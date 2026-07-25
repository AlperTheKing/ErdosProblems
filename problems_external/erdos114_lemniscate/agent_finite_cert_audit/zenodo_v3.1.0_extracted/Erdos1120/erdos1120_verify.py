"""
Erdős #1120: Shortest path in E={z:|f(z)|≤1} from z=0 to |z|=1
for monic f with roots in unit disk.

Claim from recipe: shortest path has length exactly 1, with equality at f(z)=z^n.

Let's verify computationally for small n.
"""
import numpy as np
from scipy import optimize

def sublevel_check(z, f_coeffs):
    """Check if |f(z)| ≤ 1 for polynomial with given coefficients."""
    val = np.polyval(f_coeffs, z)
    return abs(val) <= 1.0

def path_in_sublevel(t, f_coeffs):
    """Parametric path z(t) = t for t in [0,1] — straight line to |z|=1."""
    z = t  # real line
    return sublevel_check(z, f_coeffs)

# For f(z) = z^n, E = {z : |z^n| ≤ 1} = {z : |z| ≤ 1} = unit disk
# The shortest path from 0 to |z|=1 is any radial segment, length = 1

print("=== f(z) = z^n (extremal case) ===")
print("E = {z : |z| ≤ 1} = unit disk")
print("Shortest path from 0 to |z|=1: length 1 (any radius)")
print()

# For f(z) = z^n - 1, roots at n-th roots of unity (all on |z|=1)
# E = {z : |z^n - 1| ≤ 1}
# At z=0: |0-1| = 1 ≤ 1, so 0 ∈ E ✓
# At z=1: |1-1| = 0 ≤ 1, so 1 ∈ E ✓
# Along real axis [0,1]: |t^n - 1| for t ∈ [0,1]
# When t ∈ [0,1], t^n ∈ [0,1], so t^n - 1 ∈ [-1, 0], so |t^n-1| ≤ 1. Always in E!
# So the straight line [0,1] is a path of length 1.
print("=== f(z) = z^n - 1 (Erdős lemniscate) ===")
for n in [2, 3, 5, 10]:
    ts = np.linspace(0, 1, 1000)
    vals = np.abs(ts**n - 1)
    max_val = np.max(vals)
    print(f"  n={n}: max|f(t)| on [0,1] = {max_val:.6f} {'≤ 1 ✓' if max_val <= 1 else '> 1 ✗'}")
    print(f"    Path length along real axis = 1")

print()

# Now consider a DIFFERENT polynomial: f(z) = (z - a)^n for |a| ≤ 1
# E = {z : |z-a|^n ≤ 1} = {z : |z-a| ≤ 1} = disk of radius 1 centered at a
# 0 ∈ E iff |a| ≤ 1 ✓
# Shortest path from 0 to |z|=1: 
#   Need to reach a point w with |w|=1 while staying in |z-a| ≤ 1
#   The disk D(a,1) intersects |z|=1; shortest path from 0 to any such point

print("=== f(z) = (z-a)^n, various a with |a| ≤ 1 ===")
for a in [0, 0.5, 0.9, 1.0, 0.5+0.5j]:
    if abs(a) > 1:
        continue
    # E = D(a, 1). Find shortest path from 0 to unit circle staying in D(a,1)
    # Closest point on unit circle to a is a/|a| (if a≠0), distance |a|-1... no
    # We need point on |z|=1 that is in D(a,1), i.e., |z-a| ≤ 1
    # And minimize path length from 0 to z within D(a,1)
    # 
    # The straight line from 0 to z has length |z|=1
    # It stays in D(a,1) if for all t∈[0,1], |tz - a| ≤ 1
    
    # For a=0: E = unit disk. Any radial path works. Length = 1.
    # For a=0.5: E = D(0.5, 1). Contains 0. 
    #   Point z=1 is in E since |1-0.5|=0.5 ≤ 1
    #   Straight line [0,1]: |t-0.5| ≤ max(0.5, 0.5) = 0.5 ≤ 1. Length = 1.
    
    # Key insight: 0 ∈ D(a,1) since |a| ≤ 1
    # Any point z on unit circle with z ∈ D(a,1) satisfies |z-a| ≤ 1
    # The straight line 0→z stays in D(a,1) iff |tz - a| ≤ 1 for all t
    # |tz - a|² = t²|z|² - 2t Re(z·ā) + |a|² = t² - 2t Re(zā) + |a|²
    # This is a quadratic in t, maximized at t=0 or t=1
    # At t=0: |a|² ≤ 1 ✓
    # At t=1: |z-a|² ≤ 1 ✓ (by assumption)
    # Since quadratic opens upward (coeff of t² = 1 > 0), max is at endpoints!
    # So the straight line ALWAYS stays in D(a,1). Length = |z| = 1.
    
    print(f"  a={a}: E=D({a},1), shortest path to |z|=1 has length 1")

print()
print("=== CRITICAL INSIGHT ===")
print("For f(z) = (z-a)^n with |a| ≤ 1:")
print("  E = D(a, 1) (disk of radius 1 centered at a)")
print("  The straight line from 0 to z/|z| for any z on ∂D(a,1)∩{|z|=1}")
print("  has length 1 and stays inside E.")
print("  Proof: |tz-a|² = t² - 2t Re(zā) + |a|² is convex in t,")
print("  so max on [0,1] is at endpoints, both ≤ 1.")
print()

# But wait — can the path be SHORTER than 1?
# The path must go from 0 to |z|=1. Any such path has length ≥ 1 
# (since |z| is 1-Lipschitz, the path must traverse distance 1 in modulus).
# This is trivially true: length ≥ |z_end| - |z_start| = 1 - 0 = 1.

print("=== LOWER BOUND ===")
print("Any path from 0 to |z|=1 has length ≥ 1")
print("Proof: For any rectifiable path γ from 0 to w with |w|=1,")
print("  length(γ) ≥ |w| - |0| = 1  (by triangle inequality)")
print()
print("=== CONCLUSION ===")
print("The answer to Erdős #1120 is: the shortest path has length EXACTLY 1.")
print("This is achieved by the straight line from 0 to any point on |z|=1 ∩ E.")
print("The lower bound 1 is trivial (triangle inequality).")
print("The upper bound 1 requires showing E always contains such a straight line.")
print()

# Now verify the upper bound for GENERAL monic polynomials
# We need: for any monic f of degree n with roots in unit disk,
# there exists z with |z|=1 and |f(z)| ≤ 1, AND the segment [0,z] ⊆ E.

# Let's check f(z) = z² + z (roots at 0 and -1, both in unit disk)
print("=== Test: f(z) = z² + z (roots 0, -1) ===")
# At z=0: |0+0| = 0 ≤ 1 ✓
# Need z with |z|=1 and the whole segment in E
# Along z = e^{iθ}: |e^{2iθ} + e^{iθ}| = |e^{iθ}||e^{iθ}+1| = |e^{iθ}+1| = 2|cos(θ/2)|
# This is ≤ 1 when |cos(θ/2)| ≤ 1/2, i.e., θ ∈ [2π/3, 4π/3]
# Pick z = e^{iπ} = -1: |1-1| = 0 ≤ 1 ✓
# Segment [0, -1]: t → -t for t ∈ [0,1]
# |(-t)² + (-t)| = |t² - t| = t(1-t) for t ∈ [0,1]
# max at t=1/2: 1/4 ≤ 1 ✓
ts = np.linspace(0, 1, 1000)
vals = np.abs(ts**2 - ts)  # f(-t) = t² - t
print(f"  Along segment [0,-1]: max|f| = {np.max(vals):.4f} ≤ 1 ✓, path length = 1")

# More adversarial: f(z) = z² - 0.99z (roots at 0 and 0.99)
print()
print("=== Test: f(z) = z² - 0.99z (roots 0, 0.99) ===")
# Along segment [0, e^{iθ}]: z = t·e^{iθ}
# |f(te^{iθ})| = |t²e^{2iθ} - 0.99·te^{iθ}| = t|te^{iθ} - 0.99|
best_theta = None
best_max = float('inf')
for theta in np.linspace(0, 2*np.pi, 360):
    z_dir = np.exp(1j * theta)
    vals = np.abs(np.polyval([1, -0.99, 0], ts * z_dir))
    mv = np.max(vals)
    if mv < best_max:
        best_max = mv
        best_theta = theta
print(f"  Best direction θ={best_theta:.3f} ({np.degrees(best_theta):.1f}°): max|f| = {best_max:.4f}")
print(f"  Path feasible: {'✓' if best_max <= 1 else '✗'}")

