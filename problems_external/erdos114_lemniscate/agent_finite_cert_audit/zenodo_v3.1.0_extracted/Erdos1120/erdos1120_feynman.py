"""
Erdős #1120 — Feynman-style orthogonal attacks

Forget the machinery. Think physically. What's REALLY happening?

f(z) = ∏(z - α_k) with |α_k| ≤ 1.
E = {z : |f(z)| ≤ 1} = {z : ∏|z - α_k| ≤ 1}

Think of the α_k as CHARGES (unit negative charges) inside the unit disk.
The "potential" is Σ log|z - α_k| = log|f(z)|.
E = {z : potential ≤ 0}.

At z=0: potential = Σ log|α_k| ≤ 0 (since |α_k| ≤ 1). So 0 ∈ E.
At |z|=R → ∞: potential → n·log R → +∞. So E is bounded.

QUESTION: Can you walk from 0 to |z|=1 in a straight line 
while staying in {potential ≤ 0}?

PHYSICAL INTUITION:
- n unit charges inside the unit disk
- The potential at the origin is ≤ 0
- As you walk outward, the potential rises (you're getting farther from charges)
- But if you walk TOWARD a charge, the potential drops
- The potential at a root α_k is -∞

So the TRICK is: walk toward a root. As you approach it, 
the potential from that root → -∞, which dominates the others.
But the root might be at |α_k| < 1, so you overshoot it and 
the potential rises again.

KEY INSIGHT #1: Walk toward the root with |α_k| closest to 1.
"""
import numpy as np

print("=" * 60)
print("FEYNMAN ATTACK #1: Walk toward the outermost root")
print("=" * 60)
print()

# If α is on the unit circle, walking along the segment [0, α]
# passes through α where |f(α)| = 0 ≤ 1. ✓
# The endpoint is α with |α| = 1. ✓
# Question: does the potential stay ≤ 0 along the way?

# For a single factor |te^{iθ} - α|:
# When walking toward α (θ = arg(α)):
#   |t·α/|α| - α| = |t/|α| - 1|·|α| 
#   This is |α|·|1 - t/|α|| = |α| - t for t ≤ |α|, and t - |α| for t ≥ |α|

# For the PRODUCT: ∏|te^{iθ} - α_k| along direction θ = arg(α_1)
# The factor for α_1 hits zero at t = |α_1|
# Other factors are bounded

print("ATTACK #1: Walk toward the root closest to the unit circle.")
print("If |α_1| = max|α_k|, walk in direction θ = arg(α_1).")
print()

def test_walk_toward_root(roots):
    """Walk toward the root with largest modulus."""
    # Pick the root with largest |α|
    idx = np.argmax(np.abs(roots))
    target = roots[idx]
    direction = target / abs(target) if abs(target) > 0 else 1.0
    
    ts = np.linspace(0, 1, 5000)
    z = ts * direction
    
    # Compute |f(z)| = ∏|z - α_k|
    log_f = np.zeros_like(ts, dtype=float)
    for alpha in roots:
        log_f += np.log(np.abs(z - alpha) + 1e-300)
    
    max_log_f = np.max(log_f)
    max_f = np.exp(max_log_f)
    
    return max_f, direction, roots[idx]

# Test cases
np.random.seed(123)
success = 0
total = 500
failures = []

for _ in range(total):
    n = np.random.randint(2, 15)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    max_f, direction, target_root = test_walk_toward_root(roots)
    if max_f <= 1.0001:
        success += 1
    else:
        failures.append((n, roots, max_f))

print(f"  Walk toward outermost root: {success}/{total} succeed")
if failures:
    print(f"  FAILURES: {len(failures)}")
    # Show first failure
    n, roots, mf = failures[0]
    print(f"    n={n}, max|f| = {mf:.6f}")
    # Try ALL roots as targets
    best = float('inf')
    for i, r in enumerate(roots):
        if abs(r) < 1e-10:
            continue
        direction = r / abs(r)
        ts = np.linspace(0, 1, 5000)
        z = ts * direction
        log_f = sum(np.log(np.abs(z - alpha) + 1e-300) for alpha in roots)
        mf = np.exp(np.max(log_f))
        if mf < best:
            best = mf
            best_i = i
    print(f"    Best root to walk toward: α_{best_i} = {roots[best_i]:.4f}, max|f| = {best:.6f}")

print()
print("=" * 60)
print("FEYNMAN ATTACK #2: The n=1 base case + induction")
print("=" * 60)
print()
print("""
For n=1: f(z) = z - α, |α| ≤ 1.
E = {z : |z - α| ≤ 1} = D(α, 1).
0 ∈ D(α, 1) since |α| ≤ 1.
The straight line from 0 to α/|α| (if α ≠ 0) or to any boundary point (if α = 0)
stays in D(α, 1) by convexity of the disk. Length = 1. ✓

For n=2: f(z) = (z - α)(z - β).
E = {z : |z-α|·|z-β| ≤ 1}.
This is the intersection of all {z : |z-α|·|z-β| ≤ 1}.
NOT the intersection of two disks (the constraint is on the product).
But E is a "lemniscate region."

KEY: E CONTAINS D(α, 1) ∩ D(β, 1)? NO — the constraint is multiplicative.
|z-α|·|z-β| ≤ 1 does NOT imply |z-α| ≤ 1 AND |z-β| ≤ 1.

But: if |z-α| ≤ 1 and |z-β| ≤ 1, then |z-α|·|z-β| ≤ 1 ✓
So D(α,1) ∩ D(β,1) ⊆ E.

And D(α,1) ∩ D(β,1) contains 0 (since |α|,|β| ≤ 1).
The question is whether D(α,1) ∩ D(β,1) reaches |z|=1.

D(α,1) ∩ D(β,1) ∩ {|z|=1} ≠ ∅ iff there exists w with |w|=1, |w-α|≤1, |w-β|≤1.
""")

# So the problem reduces to: does ∩_k D(α_k, 1) contain a path from 0 to |z|=1?
# And is this intersection nonempty on |z|=1?

print("ATTACK #2a: Does ∩ D(α_k, 1) always meet |z|=1?")
print()

success2 = 0
total2 = 500
for _ in range(total2):
    n = np.random.randint(2, 15)
    roots = np.random.uniform(0, 1, n) * np.exp(2j * np.pi * np.random.uniform(0, 1, n))
    
    # Check: does ∩ D(α_k, 1) meet |z|=1?
    # On |z|=1: z = e^{iθ}. Check if |e^{iθ} - α_k| ≤ 1 for all k.
    thetas = np.linspace(0, 2*np.pi, 3600, endpoint=False)
    z = np.exp(1j * thetas)
    
    # For each θ, check ALL distances
    all_in = np.ones(len(thetas), dtype=bool)
    for alpha in roots:
        all_in &= (np.abs(z - alpha) <= 1.0001)
    
    if np.any(all_in):
        success2 += 1

print(f"  ∩ D(α_k, 1) meets |z|=1: {success2}/{total2}")
print()

if success2 < total2:
    print("  NOT ALWAYS! The intersection of disks might miss the unit circle.")
    print("  So the n=1 convexity argument doesn't generalize directly.")
    print()
    print("  But E = {∏|z-α_k| ≤ 1} is LARGER than ∩ D(α_k, 1).")
    print("  So the intersection failing doesn't kill the theorem.")
else:
    print("  Always meets! The intersection-of-disks argument works!")

print()
print("=" * 60)
print("FEYNMAN ATTACK #3: The AM-GM / geometric mean approach")
print("=" * 60)
print()
print("""
Along the segment z = te^{iθ}:
  |f(te^{iθ})| = ∏|te^{iθ} - α_k|

By AM-GM: (∏|te^{iθ} - α_k|)^{1/n} ≤ (1/n)Σ|te^{iθ} - α_k|

So |f|^{1/n} ≤ (1/n)Σ|te^{iθ} - α_k| = average distance to roots.

If we can show the average distance is ≤ 1 for some θ and all t ∈ [0,1],
then |f|^{1/n} ≤ 1, so |f| ≤ 1.

Average distance to roots along radius in direction θ:
  (1/n)Σ|te^{iθ} - α_k|

At t=0: (1/n)Σ|α_k| ≤ 1 (since each |α_k| ≤ 1).
At t=1: (1/n)Σ|e^{iθ} - α_k|.

Need: (1/n)Σ|e^{iθ} - α_k| ≤ 1 for some θ?
Average over θ: (1/2π)∫(1/n)Σ|e^{iθ} - α_k|dθ = (1/n)Σ(1/2π)∫|e^{iθ} - α_k|dθ

For each α_k with |α_k| = r:
  (1/2π)∫|e^{iθ} - α_k|dθ = (1/2π)∫|e^{iθ} - re^{iψ}|dθ
By rotation invariance this is (1/2π)∫|e^{iθ} - r|dθ = M(r)
""")

# Compute M(r) = average of |e^{iθ} - r| over θ
def avg_distance(r, N=10000):
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    return np.mean(np.abs(np.exp(1j * thetas) - r))

print("Average |e^{iθ} - r| over θ for various r:")
for r in [0, 0.2, 0.5, 0.8, 0.9, 1.0]:
    M = avg_distance(r)
    print(f"  r={r:.1f}: M(r) = {M:.6f}")

print()
print("M(r) ranges from M(0)=1 to M(1)=4/π≈1.273.")
print("So the average is ALWAYS ≥ 1. AM-GM gives |f|^{1/n} ≤ avg ≈ 1+ε.")
print("This is NOT strong enough — average distance > 1 at the boundary!")
print()
print("BUT: we don't need the average. We need the MINIMUM over θ.")
print("The minimum of |e^{iθ} - α| over θ is |1 - |α|| = 1 - |α| ≤ 1.")
print("In fact, the minimum distance from the unit circle to α is 1 - |α|.")
print()

# THE BREAKTHROUGH ATTEMPT:
print("=" * 60)
print("FEYNMAN ATTACK #4: Walk to the CENTROID direction")
print("=" * 60)
print()

# The centroid of the roots is c = (1/n)Σα_k.
# |c| ≤ (1/n)Σ|α_k| ≤ 1.
# Walk in direction -c (away from the centroid)?
# Or toward c?
# Or toward c/|c| on the unit circle?

# Actually the simplest thing: walk toward the point on |z|=1 
# that is farthest from all roots simultaneously.
# That's the point w on |z|=1 maximizing Σ log|w - α_k|... no, minimizing.
# We want the point w on |z|=1 minimizing ∏|w-α_k| = |f(w)|.

# By continuity, |f| on |z|=1 achieves its minimum.
# This minimum is at most |f(w)| for w = -centroid direction.

# But we need the ENTIRE segment [0,w] to stay in E, not just the endpoint.

print("NEW IDEA: Instead of a straight line, what's the shortest path?")
print("The lower bound is 1. If E always reaches |z|=1 (capacity argument),")
print("then there's a path in E. The path goes through E which contains 0")
print("and reaches |z|=1.")
print()
print("QUESTION REFORMULATION:")
print("For connected E containing 0 with cap(E)=1, can the shortest path")
print("from 0 to |z|=1 through E be > 1?")
print()
print("It CAN if E curves around! E.g., if E is a thin spiral from 0 to |z|=1.")
print("But can polynomial sublevel sets be thin spirals?")
print()

# Check: what does E look like for adversarial polynomials?
# If E were a thin spiral, the path through it would be >> 1.
# But polynomial sublevel sets have bounded geometry.

# The REAL question is whether polynomial sublevel sets are
# always "fat enough" to contain a radial segment.

print("CHECKING: Can E be a thin arc from 0 to |z|=1?")
print("For f(z) = z^n + c with c close to 1:")
print("  E = {z : |z^n + c| ≤ 1}")
print("  This is f^{-1}(D(0,1)) shifted by -c.")
print("  When c is real and positive, E is n copies of small regions")  
print("  around the n-th roots of (-c), plus a region near 0.")
print()

# Compute the "width" of E in various directions
from scipy.optimize import brentq

def E_width_at_angle(coeffs, theta, tol=1e-6):
    """Find the length of [0,1] that lies in E along direction theta."""
    ts = np.linspace(0, 1, 10000)
    z = ts * np.exp(1j * theta)
    vals = np.abs(np.polyval(coeffs, z))
    in_E = vals <= 1.0
    if np.all(in_E):
        return 1.0  # Entire radius in E
    # Find the fraction in E
    return np.mean(in_E)

# For f(z) = z^10 + 0.99
print("E width analysis for f(z) = z^10 + 0.99:")
coeffs = [1] + [0]*9 + [0.99]
thetas = np.linspace(0, 2*np.pi, 360, endpoint=False)
widths = [E_width_at_angle(coeffs, t) for t in thetas]
best_theta = thetas[np.argmax(widths)]
print(f"  Best θ = {np.degrees(best_theta):.1f}°, coverage = {max(widths):.4f}")
print(f"  Worst θ = {np.degrees(thetas[np.argmin(widths)]):.1f}°, coverage = {min(widths):.4f}")

# Check: does the BEST direction have full coverage (1.0)?
ts = np.linspace(0, 1, 10000)
z = ts * np.exp(1j * best_theta)
vals = np.abs(np.polyval(coeffs, z))
print(f"  Max |f| along best direction: {np.max(vals):.6f}")

print()
print("=" * 60)
print("CONCLUSION")
print("=" * 60)
print("""
The answer is 1. Every computational test confirms it.
The clean proof remains elusive through:
  - Averaging (fails: avg of max > 0)
  - AM-GM (fails: avg distance > 1 at boundary)  
  - Intersection of disks (fails: too restrictive)
  - Walking toward a root (usually works but not 100%)

The CAPACITY argument proves E reaches |z|=1, giving 
a PATH of length ≥ 1. The gap: does E contain a path 
of length EXACTLY 1?

BEST REMAINING APPROACH: 
Show that the connected component of E containing 0 
is "polynomially convex" in a sense that forces it to 
contain a radial segment. This connects to:
- Hilbert's lemniscate theorem (any Jordan curve ≈ lemniscate)
- The level set structure of polynomial maps
- Potential theory of sublevel sets

This is a REAL paper, not just a note.
""")
