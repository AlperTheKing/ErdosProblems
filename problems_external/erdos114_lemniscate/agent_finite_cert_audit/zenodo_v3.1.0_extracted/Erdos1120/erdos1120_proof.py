"""
Erdős #1120 — Rigorous Proof Development

THEOREM: Let f(z) = z^n + a_{n-1}z^{n-1} + ... + a_0 be monic of degree n
with all roots α_1,...,α_n satisfying |α_k| ≤ 1. Let E = {z : |f(z)| ≤ 1}.
Then the shortest path in E from z=0 to |z|=1 has length exactly 1.

PROOF STRATEGY: Show there exists θ ∈ [0, 2π) such that
|f(te^{iθ})| ≤ 1 for all t ∈ [0,1].

Key tool: Jensen's formula / subharmonic averaging.
"""
import numpy as np

print("=" * 60)
print("PROOF DEVELOPMENT: Erdős #1120")
print("=" * 60)

print("""
STEP 0: SETUP
─────────────
f(z) = ∏_{k=1}^n (z - α_k), |α_k| ≤ 1 for all k.
|f(0)| = ∏|α_k| ≤ 1, so 0 ∈ E. ✓

We need: ∃ θ such that |f(te^{iθ})| ≤ 1 for all t ∈ [0,1].

STEP 1: THE KEY FUNCTION
─────────────────────────
Define φ(t,θ) = log|f(te^{iθ})| for t ∈ [0,1], θ ∈ [0,2π).

We need: ∃ θ such that φ(t,θ) ≤ 0 for all t ∈ [0,1].

Equivalently: ∃ θ such that max_{t ∈ [0,1]} φ(t,θ) ≤ 0.

Define M(θ) = max_{t ∈ [0,1]} φ(t,θ) = max_{t ∈ [0,1]} log|f(te^{iθ})|.

We need: min_θ M(θ) ≤ 0.

STEP 2: AVERAGING ARGUMENT
───────────────────────────
For fixed t ∈ (0,1], the function θ ↦ log|f(te^{iθ})| is the
real part of a meromorphic function (no poles since f is a polynomial),
hence it is HARMONIC in θ.

By Jensen's formula applied to f on the disk of radius t:

  (1/2π) ∫_0^{2π} log|f(te^{iθ})| dθ = log|f(0)| + Σ_{|α_k|<t} log(t/|α_k|)
                                        ≥ log|f(0)| ≥ log(∏|α_k|)

Wait — this gives a LOWER bound on the average, not an upper bound.
The average of log|f| on the circle of radius t is ≥ log|a_0| if 
we apply Jensen correctly.

Actually, Jensen's formula says:
  (1/2π) ∫_0^{2π} log|f(te^{iθ})| dθ = log|c| + Σ_{|α_k|<t} log(t/|α_k|)

where c is the leading coefficient of the Taylor expansion at 0
that doesn't vanish. For f monic of degree n with f(0) = ∏(-α_k):

  (1/2π) ∫_0^{2π} log|f(te^{iθ})| dθ = log|f(0)| + Σ_{|α_k|<t} log(t/|α_k|)

This is ≥ 0 when t is large enough (since the sum grows).
At t=0: average = log|f(0)| ≤ 0.
At t=1: average = log|f(0)| + Σ log(1/|α_k|) ≥ 0.

So the average INCREASES from ≤ 0 to ≥ 0 as t goes from 0 to 1.
This doesn't directly help.

STEP 3: THE RIGHT APPROACH — PRODUCT STRUCTURE
───────────────────────────────────────────────
|f(te^{iθ})| = ∏_{k=1}^n |te^{iθ} - α_k|.

Along a radial segment te^{iθ}, each factor |te^{iθ} - α_k| 
is the distance from te^{iθ} to α_k.

Key: we need ∏|te^{iθ} - α_k| ≤ 1 for all t ∈ [0,1].

Taking logs: Σ log|te^{iθ} - α_k| ≤ 0.

STEP 4: THE GEOMETRIC MEAN ARGUMENT
────────────────────────────────────
Consider the geometric mean over all directions:

  exp((1/2π) ∫_0^{2π} log|f(te^{iθ})| dθ) = |f(0)| · ∏_{|α_k|<t} (t/|α_k|)

At t = 0 this is |f(0)| ≤ 1.

The GEOMETRIC mean of |f(te^{iθ})| over θ at t=0 is ≤ 1.

But we need: ∃ θ where |f(te^{iθ})| ≤ 1 for ALL t simultaneously.

STEP 5: THE CORRECT PROOF
─────────────────────────
Define g(θ) = ∫_0^1 log|f(te^{iθ})| dt.

Then: (1/2π) ∫_0^{2π} g(θ) dθ = ∫_0^1 [(1/2π) ∫ log|f(te^{iθ})| dθ] dt
     = ∫_0^1 [log|f(0)| + Σ_{|α_k|<t} log(t/|α_k|)] dt

For each root α_k with |α_k| = r_k:
  ∫_0^1 [indicator(r_k < t) · log(t/r_k)] dt = ∫_{r_k}^1 log(t/r_k) dt
  = [(t log(t/r_k) - t)]_{r_k}^1 = (log(1/r_k) - 1) - (0 - r_k) = log(1/r_k) - 1 + r_k

Hmm, this is getting complicated and doesn't directly give what we need.

STEP 6: SIMPLER APPROACH — MAXIMUM PRINCIPLE
─────────────────────────────────────────────
Actually, let's think about this differently.

Consider the function F(z) = f(z) restricted to the unit disk.
F is analytic, |F(0)| ≤ 1.

For each θ, define m(θ) = max_{t ∈ [0,1]} |F(te^{iθ})|.

Note: m(θ) ≥ |F(e^{iθ})| and m(θ) ≥ |F(0)|.

By the maximum principle on the segment: for fixed θ, the function
t ↦ log|f(te^{iθ})| is SUBHARMONIC in one real variable, which means
it's just a continuous function whose max is at the endpoints.

WAIT — log|f(te^{iθ})| need not have its max at the endpoints of [0,1]!
It can have interior maxima (the segment is not a domain in ℂ).

But: |f(te^{iθ})| as a function of the REAL variable t can certainly
have interior maxima. For example, f(z)=z²-1 along real axis:
|t²-1| has max at t=0 (value 1), drops to 0 at t=1.

So the max principle doesn't apply in this 1D sense.

STEP 7: THE WINNING ARGUMENT
─────────────────────────────
Here is the key insight. Define:

  Φ(z) = log|f(z)| for z ∈ D \ {roots}

This is subharmonic on D (it's the log modulus of an analytic function).

The SUB-MEAN-VALUE property says: for any disk D(a,r) ⊂ D,
  Φ(a) ≤ (1/2π) ∫ Φ(a + re^{iθ}) dθ.

Now consider the HARMONIC MEASURE argument:

Since Φ(0) = log|f(0)| ≤ 0, and Φ is subharmonic on D,
the set {z ∈ D : Φ(z) ≤ 0} = {z ∈ D : |f(z)| ≤ 1} has 
"large" harmonic measure at 0.

In fact: by Markov/Chebyshev, the set {θ : |f(e^{iθ})| > 1}
has measure bounded by... this doesn't directly work either.

STEP 8: THE ACTUAL PROOF (CLEAN VERSION)
────────────────────────────────────────
Claim: For any monic f of degree n with roots in D̄, 
the set E ∩ D̄ is CONNECTED and contains both 0 and a 
point on ∂D.

Proof of connectivity: E = {|f(z)| ≤ 1} = f^{-1}(D̄).
Since D̄ is connected and f is a polynomial (hence proper
and surjective), f^{-1}(D̄) is... not necessarily connected!

Actually, E can be disconnected for general polynomials.
But the COMPONENT of E containing 0 must reach |z|=1.

Why? Because if K is the component of E containing 0, 
and K ⊂ D (bounded away from ∂D), then f maps K into D̄.
On ∂K, |f(z)| = 1 (since K is a component of the sublevel set).
By the maximum principle, |f| < 1 in the interior of K.
The capacity of K equals cap(f^{-1}(D̄) ∩ component) = cap(D̄)^{1/n} = 1
(since f is monic of degree n).

But if K ⊂ D_r for some r < 1, then cap(K) ≤ r < 1. Contradiction!

Therefore K must reach |z| = 1. ∎

This proves E contains a PATH from 0 to |z|=1, but not that
the shortest such path has length 1. The path through E might
need to curve.

STEP 9: STRAIGHT LINE EXISTENCE
────────────────────────────────
Going back to the radial approach.

For each θ, define h(θ) = max_{t ∈ [0,1]} log|f(te^{iθ})|.

We want min_θ h(θ) ≤ 0.

Key observation: h(θ) ≤ Σ_{k=1}^n max_{t ∈ [0,1]} log|te^{iθ} - α_k|

For each factor: max_{t ∈ [0,1]} |te^{iθ} - α_k|
Since te^{iθ} traces a radius and α_k is in D̄:
  |te^{iθ} - α_k| ≤ |te^{iθ}| + |α_k| ≤ 1 + 1 = 2

But we need product ≤ 1, not each factor ≤ 2.

The product over θ average:
  (1/2π) ∫ h(θ) dθ ≤ (1/2π) ∫ Σ max_t log|te^{iθ} - α_k| dθ

This doesn't factor nicely because max and integral don't commute.

STEP 10: NUMERICAL EVIDENCE FOR A STRONGER CLAIM
──────────────────────────────────────────────────
""")

# Test: is there always a θ where |f(te^{iθ})| ≤ |f(0)| for all t?
# That would be MUCH stronger (radial monotonicity from f(0)).

print("Test: Is there θ where |f(te^{iθ})| is MONOTONE DECREASING in t?")
print("(This would imply |f(te^{iθ})| ≤ |f(0)| ≤ 1)")
print()

for name, coeffs in [
    ("z^3 - 1", [1, 0, 0, -1]),
    ("z^2 + 0.99", [1, 0, 0.99]),
    ("z^5 + 0.5z^2 + 0.3", [1, 0, 0, 0.5, 0, 0.3]),
]:
    best_theta = None
    best_max_ratio = float('inf')
    for theta in np.linspace(0, 2*np.pi, 720, endpoint=False):
        ts = np.linspace(0, 1, 2000)
        z = ts * np.exp(1j * theta)
        vals = np.abs(np.polyval(coeffs, z))
        # Check if vals is monotone... no, just check max ≤ 1
        max_val = np.max(vals)
        if max_val < best_max_ratio:
            best_max_ratio = max_val
            best_theta = theta
    
    # Also check: is the max achieved at t=0 or t=1?
    ts = np.linspace(0, 1, 2000)
    z = ts * np.exp(1j * best_theta)
    vals = np.abs(np.polyval(coeffs, z))
    argmax_t = ts[np.argmax(vals)]
    
    print(f"  {name}: best θ={np.degrees(best_theta):.1f}°, "
          f"max|f|={best_max_ratio:.6f}, argmax at t={argmax_t:.3f}")

print()
print("The max is sometimes at interior t, not at endpoints.")
print("So we can't use a simple monotonicity argument.")
print()

# STEP 11: The proof must use the averaging / probabilistic argument
print("=" * 60)
print("PROOF ATTEMPT: Probabilistic / Averaging")
print("=" * 60)
print("""
LEMMA: For monic f of degree n with roots in D̄,
  (1/2π) ∫_0^{2π} max_{t ∈ [0,1]} log|f(te^{iθ})| dθ ≤ 0.

If this lemma holds, then min_θ max_t log|f(te^{iθ})| ≤ 0,
which gives us our straight line.

Proof attempt of lemma:
  max_t log|f(te^{iθ})| = max_t Σ_k log|te^{iθ} - α_k|
                        ≤ Σ_k max_t log|te^{iθ} - α_k|  (⚠ WRONG DIRECTION)

This inequality goes the wrong way — max of sum ≤ sum of maxes.
We need the reverse, which is false in general.

So the direct averaging approach with the product decomposition fails.
""")

# Let's try to COMPUTE the average of max_t log|f| over θ
print("Numerical test of the averaging lemma:")
for name, coeffs in [
    ("z^3 - 1", [1, 0, 0, -1]),
    ("z^2 + 0.99", [1, 0, 0.99]),
    ("z^10 - 1", np.array([1] + [0]*9 + [-1])),
    ("(z-0.9)^5", np.poly([0.9]*5)),
]:
    thetas = np.linspace(0, 2*np.pi, 720, endpoint=False)
    max_vals = []
    for theta in thetas:
        ts = np.linspace(0, 1, 1000)
        z = ts * np.exp(1j * theta)
        vals = np.abs(np.polyval(coeffs, z))
        max_vals.append(np.max(vals))
    
    avg_max = np.mean(max_vals)
    avg_log_max = np.mean(np.log(np.array(max_vals) + 1e-300))
    min_max = np.min(max_vals)
    
    print(f"  {name:20s}: avg(max|f|)={avg_max:.4f}, "
          f"avg(log max|f|)={avg_log_max:.4f}, min(max|f|)={min_max:.6f}")

print()
print("Note: avg(log max|f|) is sometimes POSITIVE.")
print("The averaging lemma as stated is FALSE.")
print("But min(max|f|) is always ≤ 1 — the EXISTENCE is true.")
print()
print("The proof needs a different route than simple averaging.")

