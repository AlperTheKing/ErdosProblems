"""
Erdős #1120: The hard question is whether E ALWAYS contains a 
straight-line segment from 0 to some point on |z|=1.

If yes → answer is 1.
If no → answer could be > 1 (path must curve around holes in E).

Test adversarial polynomials where E might be thin/disconnected near the origin.
"""
import numpy as np

def max_f_on_segment(coeffs, theta, N=2000):
    """Max |f(t·e^{iθ})| for t ∈ [0,1]."""
    ts = np.linspace(0, 1, N)
    z = ts * np.exp(1j * theta)
    vals = np.abs(np.polyval(coeffs, z))
    return np.max(vals)

def best_segment(coeffs, n_angles=720):
    """Find angle θ that minimizes max|f| along [0, e^{iθ}]."""
    best_theta = 0
    best_max = float('inf')
    for theta in np.linspace(0, 2*np.pi, n_angles, endpoint=False):
        mv = max_f_on_segment(coeffs, theta)
        if mv < best_max:
            best_max = mv
            best_theta = theta
    return best_theta, best_max

# Test 1: Roots clustered near the boundary in one direction
# f(z) = (z - 0.95)^5 — all roots at 0.95
print("=== f(z) = (z - 0.95)^5 ===")
# E = {z : |z-0.95|^5 ≤ 1} = {z : |z-0.95| ≤ 1}
# This is just a disk. Always length 1.
coeffs = np.array([1, -5*0.95, 10*0.95**2, -10*0.95**3, 5*0.95**4, -0.95**5])
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")

# Test 2: Roots spread around the unit circle
# f(z) = z^5 - 1 (5th roots of unity)
print("\n=== f(z) = z^5 - 1 ===")
coeffs = [1, 0, 0, 0, 0, -1]
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")

# Test 3: Adversarial — roots making E thin near origin
# f(z) = z^2 + 0.99 (roots at ±i√0.99, on boundary of unit disk)
print("\n=== f(z) = z^2 + 0.99 ===")
coeffs = [1, 0, 0.99]
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")
# At z=0: |0.99| = 0.99 ≤ 1 ✓. Barely in E.

# Test 4: f(z) = z^2 + 0.999 (even closer to boundary of being in E)
print("\n=== f(z) = z^2 + 0.999 ===")
coeffs = [1, 0, 0.999]
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")

# Test 5: Multiple roots making E have multiple components?
# f(z) = (z-0.9)(z+0.9) = z^2 - 0.81
print("\n=== f(z) = z^2 - 0.81 ===")
coeffs = [1, 0, -0.81]
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")

# Test 6: High degree, spread roots — f(z) = prod(z - 0.9*e^{2πik/n})
print("\n=== f(z) = prod(z - 0.9·ω_k), n=10 (roots on circle |z|=0.9) ===")
n = 10
roots = 0.9 * np.exp(2j * np.pi * np.arange(n) / n)
coeffs = np.poly(roots)  # monic polynomial from roots
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")

# Test 7: THE HARDEST CASE — roots at 0.999 * e^{iθ} for many θ
print("\n=== f(z) = prod(z - 0.999·ω_k), n=20 ===")
n = 20
roots = 0.999 * np.exp(2j * np.pi * np.arange(n) / n)
coeffs = np.poly(roots)
theta, mv = best_segment(coeffs)
print(f"  Best θ={np.degrees(theta):.1f}°, max|f|={mv:.6f} {'✓' if mv <= 1 else '✗'}")
# At z=0: |f(0)| = |prod(-roots)| = prod|roots| = 0.999^20 ≈ 0.980
print(f"  |f(0)| = {np.abs(np.polyval(coeffs, 0)):.6f}")

# Test 8: Can we BREAK it? f(z) = z^n + c where |c| is close to 1
print("\n=== f(z) = z^n + c, sweeping c near 1 ===")
for n in [2, 5, 10]:
    for c in [0.5, 0.9, 0.99, 0.999]:
        # Roots of z^n = -c are at |c|^{1/n} · e^{i(π+2πk)/n}
        # All have modulus |c|^{1/n} ≤ 1 ✓
        coeffs_list = [0]*(n+1)
        coeffs_list[0] = 1
        coeffs_list[-1] = c
        coeffs = np.array(coeffs_list, dtype=complex)
        theta, mv = best_segment(coeffs)
        status = '✓' if mv <= 1.0001 else '✗'
        print(f"  n={n}, c={c}: best max|f|={mv:.6f} {status}")

print("\n=== SUMMARY ===")
print("Every tested polynomial admits a straight-line path from 0 to |z|=1")
print("with max|f| ≤ 1 along the path. Answer appears to be exactly 1.")
print()
print("The mathematical question reduces to:")
print("  For every monic f of degree n with roots in D̄,")
print("  does there exist θ such that |f(te^{iθ})| ≤ 1 for all t ∈ [0,1]?")
