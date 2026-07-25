"""
Erdős #1120 — Hammering the radial lemma

The gap: E = {|f(z)| ≤ 1} contains 0 and reaches |z|=1.
Must E contain a radial segment [0, e^{iθ}]?

NEW ANGLE: Don't prove E contains a radius.
Prove the shortest path in E from 0 to |z|=1 has length 1
WITHOUT requiring a straight line.

Key: ANY path from 0 to |z|=1 has length ≥ 1 (triangle inequality).
So we need: infimum of path lengths in E from 0 to ∂D = 1.

This means: for any ε > 0, there exists a path in E from 0 to 
|z|=1 of length < 1 + ε.

This is WEAKER than "E contains a radius" but EQUIVALENT to
"shortest path = 1".

And we know E is connected and reaches |z|=1 (capacity argument).

NEW APPROACH: The infimum of path lengths from 0 to ∂D through 
a connected set K ⊂ D̄ that contains 0 and meets ∂D is exactly 1
iff K contains a point w ∈ ∂D such that the INNER DISTANCE
d_K(0, w) = 1.

The inner distance in K is the infimum of lengths of paths in K
connecting 0 to w. By the triangle inequality, d_K(0,w) ≥ |w| = 1.
Equality holds iff there exist paths in K from 0 to w of length
arbitrarily close to 1 — i.e., "nearly straight" paths.

This holds iff w and 0 can be connected by paths in K that 
stay close to the segment [0,w].

QUESTION: For polynomial sublevel sets, is the inner distance
from 0 to ∂D always 1?
"""
import numpy as np

print("=" * 60)
print("HAMMER SESSION: Inner distance in polynomial sublevel sets")
print("=" * 60)
print()

def compute_inner_distance(coeffs, target_theta, N_paths=50, N_points=500):
    """
    Estimate the inner distance from 0 to e^{iθ} through E = {|f| ≤ 1}.
    Uses a family of piecewise-linear paths that try to approximate
    the straight line while staying in E.
    """
    target = np.exp(1j * target_theta)
    
    # First check: is the straight line in E?
    ts = np.linspace(0, 1, N_points)
    z_straight = ts * target
    vals = np.abs(np.polyval(coeffs, z_straight))
    if np.max(vals) <= 1.0:
        return 1.0, True  # Straight line works
    
    # The straight line exits E somewhere. Find where.
    in_E = vals <= 1.0
    
    # Try paths that detour slightly
    best_length = float('inf')
    for _ in range(N_paths):
        # Random perturbation of the straight-line path
        perturbation = np.random.normal(0, 0.1, N_points) + \
                       1j * np.random.normal(0, 0.1, N_points)
        perturbation[0] = 0
        perturbation[-1] = 0
        
        z_path = z_straight + perturbation * ts * (1 - ts)  # zero at endpoints
        
        # Check if path stays in E
        vals = np.abs(np.polyval(coeffs, z_path))
        if np.max(vals) <= 1.0:
            # Compute path length
            diffs = np.diff(z_path)
            length = np.sum(np.abs(diffs))
            best_length = min(best_length, length)
    
    if best_length < float('inf'):
        return best_length, False
    else:
        return float('inf'), False  # couldn't find a path

# For each polynomial, find the BEST direction (lowest inner distance)
np.random.seed(42)
print("Testing inner distances for random polynomials:\n")

all_min_distances = []
for trial in range(200):
    n = np.random.randint(2, 12)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    coeffs = np.poly(roots)
    
    # Find the best direction
    best_dist = float('inf')
    best_theta = 0
    best_straight = False
    
    for theta in np.linspace(0, 2*np.pi, 72, endpoint=False):
        dist, is_straight = compute_inner_distance(coeffs, theta)
        if dist < best_dist:
            best_dist = dist
            best_theta = theta
            best_straight = is_straight
    
    all_min_distances.append(best_dist)
    
    if best_dist > 1.01:
        print(f"  Trial {trial}: n={n}, best inner dist = {best_dist:.6f} "
              f"{'(straight)' if best_straight else '(curved)'} *** INTERESTING")

print()
finite_dists = [d for d in all_min_distances if d < float('inf')]
print(f"Results over {len(all_min_distances)} trials:")
print(f"  Finite inner distance found: {len(finite_dists)}/{len(all_min_distances)}")
if finite_dists:
    print(f"  Min inner distance: {min(finite_dists):.6f}")
    print(f"  Max inner distance: {max(finite_dists):.6f}")
    print(f"  Mean: {np.mean(finite_dists):.6f}")
    print(f"  All ≤ 1.001: {sum(d <= 1.001 for d in finite_dists)}/{len(finite_dists)}")

print()
print("=" * 60)
print("HAMMER: The n=1 proof generalization")
print("=" * 60)
print("""
For n=1: f(z) = z - α. E = D(α, 1). Convex. Radial path exists. ✓

For general n: f(z) = ∏(z - α_k).

NEW IDEA: Prove by induction on n.

f(z) = (z - α_n) · g(z) where g has n-1 roots in D̄.

E_f = {|f| ≤ 1} = {|(z-α_n)| · |g(z)| ≤ 1}

Let E_g = {|g| ≤ 1}. We know (by induction) E_g contains a radial 
segment [0, e^{iθ}] for some θ.

Along this segment: |g(te^{iθ})| ≤ 1 for all t ∈ [0,1].
So |f(te^{iθ})| = |te^{iθ} - α_n| · |g(te^{iθ})| ≤ |te^{iθ} - α_n|.

For this to be ≤ 1, we need |te^{iθ} - α_n| ≤ 1 for all t ∈ [0,1].
This means the segment [0, e^{iθ}] ⊂ D(α_n, 1).

So we need: ∃ θ such that [0, e^{iθ}] ⊂ E_g AND [0, e^{iθ}] ⊂ D(α_n, 1).

i.e., ∃ θ such that [0, e^{iθ}] ⊂ E_g ∩ D(α_n, 1).

This FAILS when the good θ for g doesn't align with D(α_n, 1).
The induction doesn't directly work.

BUT: E_f is bigger than E_g ∩ D(α_n, 1).
On the boundary of D(α_n, 1), |z - α_n| = 1, so |f(z)| = |g(z)|.
Outside D(α_n, 1), |z - α_n| > 1, but |g(z)| might be very small.

So E_f includes regions OUTSIDE D(α_n, 1) where |g| is small enough.
""")

# Test the induction idea more carefully
print("Testing induction failure/success rates:")
np.random.seed(99)
induction_works = 0
for trial in range(500):
    n = np.random.randint(3, 10)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    
    # Pick last root
    alpha_n = roots[-1]
    g_roots = roots[:-1]
    g_coeffs = np.poly(g_roots)
    
    # Find θ where [0, e^{iθ}] ⊂ E_g
    for theta in np.linspace(0, 2*np.pi, 360, endpoint=False):
        ts = np.linspace(0, 1, 1000)
        z = ts * np.exp(1j * theta)
        
        # Check g condition
        g_vals = np.abs(np.polyval(g_coeffs, z))
        if np.max(g_vals) > 1.0:
            continue
        
        # Check D(α_n, 1) condition
        disk_vals = np.abs(z - alpha_n)
        if np.max(disk_vals) <= 1.0:
            induction_works += 1
            break
    
print(f"  Induction (E_g ∩ D(α_n,1) has a radius): {induction_works}/500")
print()

# The induction doesn't always work, but let's see how often E_f 
# contains a radius even when E_g ∩ D(α_n, 1) doesn't
f_works = 0
for trial in range(500):
    n = np.random.randint(3, 10)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    coeffs = np.poly(roots)
    
    for theta in np.linspace(0, 2*np.pi, 720, endpoint=False):
        ts = np.linspace(0, 1, 1000)
        z = ts * np.exp(1j * theta)
        vals = np.abs(np.polyval(coeffs, z))
        if np.max(vals) <= 1.0:
            f_works += 1
            break

print(f"  Direct (E_f has a radius): {f_works}/500")
print()

print("=" * 60)
print("HAMMER: Topological degree argument")  
print("=" * 60)
print("""
Consider f : D̄ → ℂ. The image f(∂D) winds around 0 exactly n times
(since f is monic of degree n and all roots are in D).

f(0) = ∏(-α_k), with |f(0)| ≤ 1.

The set {z ∈ D̄ : |f(z)| = 1} is the 1-level set.
The set E = {|f| ≤ 1} is bounded by this level set plus parts of ∂D.

KEY TOPOLOGICAL FACT:
The map z ↦ f(z)/|f(z)| from ∂E → S¹ has degree n 
(counting the winding of f around D̄).

Now, along any radius [0, e^{iθ}], the function t ↦ |f(te^{iθ})|
starts at |f(0)| ≤ 1 and ends at |f(e^{iθ})|.

If |f(e^{iθ})| ≤ 1, the entire radius might be in E.
If |f(e^{iθ})| > 1, the radius exits E at some point.

The set of θ where |f(e^{iθ})| ≤ 1 has some angular measure.
By the argument principle or winding number:

  (1/2π) ∫_0^{2π} log|f(e^{iθ})| dθ = log|f(0)| + Σ log(1/|α_k|) ≥ 0

So the AVERAGE of log|f| on ∂D is ≥ 0.
The set where |f(e^{iθ})| ≤ 1 (i.e., log|f| ≤ 0) has measure ≤ 2π,
but it must exist (since at θ = arg(α_k), |f(e^{iθ})| is small 
near that root).

THE REAL QUESTION: Among the θ where |f(e^{iθ})| ≤ 1,
is there one where the ENTIRE radius [0, e^{iθ}] stays in E?

This is where the argument NEEDS to use the polynomial structure.
A connected E that reaches ∂D could conceivably reach it
only through curved tentacles, not through any radius.

BUT: polynomial sublevel sets have bounded complexity.
The number of connected components of {|f| ≤ 1} ∩ {|z| = r}
is at most 2n for each r (since f maps circles to curves of degree n).

So on each circle |z|=r, E intersects in at most 2n arcs.
As r varies from 0 to 1, these arcs move continuously.
At r=0, the entire circle is in E (since |f(0)| ≤ 1).
At r=1, some arcs remain.

By the intermediate value theorem applied to the 
angular position of these arcs... this is getting close!
""")

# Visualize the arc structure
print("Arc structure of E on circles |z| = r:")
test_coeffs = np.poly([0.8, -0.5, 0.3+0.7j, 0.3-0.7j, -0.9])
print(f"f(z) = poly with 5 roots in D̄")

for r in [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]:
    thetas = np.linspace(0, 2*np.pi, 3600, endpoint=False)
    z = r * np.exp(1j * thetas) if r > 0 else np.zeros(1)
    vals = np.abs(np.polyval(test_coeffs, z))
    if r == 0:
        print(f"  r={r:.1f}: |f(0)| = {vals[0]:.4f}, in E: {'Yes' if vals[0] <= 1 else 'No'}")
        continue
    in_E = vals <= 1.0
    # Count arcs
    transitions = np.diff(in_E.astype(int))
    n_arcs = max(np.sum(transitions == 1), np.sum(transitions == -1))
    coverage = np.mean(in_E) * 360
    print(f"  r={r:.1f}: {n_arcs} arcs, coverage = {coverage:.1f}°, "
          f"min|f| = {np.min(vals):.4f}, max|f| = {np.max(vals):.4f}")

print()
print("=" * 60)
print("HAMMER: The continuity-of-arcs argument")
print("=" * 60)
print("""
CLAIM: At r=0, the arc is a full circle (all 360°).
As r increases, the arc shrinks but remains connected 
(for the component containing the "good" directions).

If at r=1 the arc still has positive measure, 
then there exists θ in the arc for ALL r ∈ [0,1],
meaning the radius at angle θ stays in E.

Is the arc monotone decreasing? Not necessarily.
But: the set {θ : |f(re^{iθ})| ≤ 1} varies continuously in r.

Define A(r) = {θ ∈ [0,2π) : |f(re^{iθ})| ≤ 1}.
At r=0: A(0) = [0,2π) (full circle, since |f(0)| ≤ 1).
At r=1: A(1) = {θ : |f(e^{iθ})| ≤ 1} ≠ ∅.

We want: ∩_{r ∈ [0,1]} A(r) ≠ ∅.

This is the intersection of a family of closed sets indexed by r.
If they're nested (A(r₁) ⊇ A(r₂) when r₁ < r₂), the intersection 
is nonempty by compactness. But they're NOT nested in general!

However, if we think of Θ(r) = A(r) as a set-valued function,
and if Θ is upper semicontinuous... the intersection of a 
decreasing (in some sense) family of nonempty compact sets 
is nonempty. But Θ is not decreasing.

COUNTEREXAMPLE ATTEMPT: Can A(r₁) and A(r₂) be DISJOINT for some r₁, r₂?
If so, no single θ works for all r.
""")

# Check: can A(r1) and A(r2) be disjoint?
print("Testing: can A(r1) and A(r2) be disjoint?")
np.random.seed(77)
found_disjoint = False
for trial in range(200):
    n = np.random.randint(3, 10)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    coeffs = np.poly(roots)
    
    thetas = np.linspace(0, 2*np.pi, 720, endpoint=False)
    
    # Compute A(r) for various r
    A_sets = {}
    for r in np.linspace(0.1, 1.0, 10):
        z = r * np.exp(1j * thetas)
        vals = np.abs(np.polyval(coeffs, z))
        A_sets[r] = set(np.where(vals <= 1.0)[0])
    
    # Check pairwise intersections
    rs = sorted(A_sets.keys())
    for i in range(len(rs)):
        for j in range(i+1, len(rs)):
            inter = A_sets[rs[i]] & A_sets[rs[j]]
            if len(inter) == 0 and len(A_sets[rs[i]]) > 0 and len(A_sets[rs[j]]) > 0:
                found_disjoint = True
                print(f"  DISJOINT! Trial {trial}, r1={rs[i]:.1f} ({len(A_sets[rs[i]])} pts), "
                      f"r2={rs[j]:.1f} ({len(A_sets[rs[j]])} pts)")
                break
        if found_disjoint:
            break
    if found_disjoint:
        break

if not found_disjoint:
    print("  No disjoint A(r1), A(r2) found in 200 trials!")
    print("  This suggests ∩ A(r) is ALWAYS nonempty.")
    print()
    print("  If ∩_{r ∈ [0,1]} A(r) ≠ ∅, the theorem is proved!")
    print("  We need: for all 0 < r1 < r2 ≤ 1, A(r1) ∩ A(r2) ≠ ∅.")
    print("  Equivalently: the radial sections of E are a COHERENT family.")

print()

# More refined test: compute ∩ A(r) for many r values
print("Computing ∩_{r} A(r) for random polynomials:")
np.random.seed(42)
always_nonempty = 0
total_tests = 500

for trial in range(total_tests):
    n = np.random.randint(2, 15)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    coeffs = np.poly(roots)
    
    thetas = np.linspace(0, 2*np.pi, 720, endpoint=False)
    
    # Compute intersection of A(r) for r = 0.01, 0.02, ..., 1.0
    intersection = np.ones(len(thetas), dtype=bool)
    for r in np.linspace(0.01, 1.0, 100):
        z = r * np.exp(1j * thetas)
        vals = np.abs(np.polyval(coeffs, z))
        intersection &= (vals <= 1.0001)
    
    if np.any(intersection):
        always_nonempty += 1

print(f"  ∩ A(r) nonempty: {always_nonempty}/{total_tests}")
print()

if always_nonempty == total_tests:
    print("*** ∩ A(r) is ALWAYS nonempty across 500 random polynomials! ***")
    print()
    print("This means: there ALWAYS exists θ such that")
    print("|f(re^{iθ})| ≤ 1 for ALL r ∈ [0,1].")
    print()
    print("THE THEOREM IS: ∩_{r ∈ [0,1]} {θ : |f(re^{iθ})| ≤ 1} ≠ ∅")
    print()
    print("This is equivalent to: the sublevel set E = {|f| ≤ 1}")
    print("contains a complete radial segment from 0 to |z|=1.")
    print()
    print("PROOF STRATEGY: Show this intersection is nonempty.")
    print("Since each A(r) is a closed subset of [0,2π) and A(0) = [0,2π),")
    print("it suffices to show the family {A(r)} has the finite intersection property.")
    print("i.e., any finite subfamily has nonempty intersection.")
else:
    print(f"Some failures: {total_tests - always_nonempty}")

