"""Does the g^k hierarchy actually close the recorded failure cases?  And is it ever needed?

Two questions, both answered exactly:
 (1) for the witnesses in the failure region (A > 1/25 and bound_0 > 1/25), how large must k be?
 (2) FLAT MEASURES: if g is constant on supp mu then bound_k = bound_0 = W - 4W^2 for EVERY k
     (proved: m(b) = W - int_{N(b)} g dmu = W - c*g(b) = W - c^2 is then also constant).
     So the hierarchy is useless on any flat measure with W in (1/20,1/5).  Search for a flat
     measure with A > 1/25 -- that would refute item 7 as literally stated.
"""
from fractions import Fraction as F
from P1_engine import Meas, gamma, WITNESSES, TARGET, show

print("=== (1) hierarchy levels on the witnesses that are in the failure region ===")
for name, m, w in WITNESSES:
    mu = gamma(m, w)
    if mu.A > TARGET and mu.bound(0) > TARGET:
        ks = [k for k in range(0, 41)]
        vals = [mu.bound(k) for k in ks]
        good = [k for k, v in zip(ks, vals) if v <= TARGET]
        print(f"{name}: W={float(mu.W):.6f} A={float(mu.A):.6f} Varg={float(mu.Varg):.6g}")
        print(f"    bound_k, k=0..8: {[round(float(v), 6) for v in vals[:9]]}")
        print(f"    smallest k with bound_k <= 1/25: {good[0] if good else 'NONE up to k=40'}"
              f"   (B = {float(mu.B):.6f})")

print()
print("=== (2) flat circulants: g constant, so every bound_k = W - 4W^2 ===")
print("     m  deg   W          A          W-4W^2     A>1/25?")
for m in range(4, 61):
    mu = gamma(m, [1] * m)
    deg = sum(1 for j in range(m) if mu.adj[0][j])
    flat = len(set(mu.g)) == 1
    b0 = mu.bound(0)
    assert flat
    assert all(mu.bound(k) == b0 for k in (1, 2, 3)), m
    mark = "  <<< FAILURE REGION" if (mu.A > TARGET and b0 > TARGET) else ""
    print(f"    {m:3d} {deg:3d}   {float(mu.W):.6f}   {float(mu.A):.6f}   {float(b0):.6f}"
          f"   {'yes' if mu.A > TARGET else 'no '}{mark}")
