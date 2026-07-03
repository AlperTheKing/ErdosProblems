"""SIB-CERT1 exact identity gate (seed-bank reply, 2026-07-04).

Verifies with sympy (exact) every identity in the SIB grouped AM-GM proof:
  (1.5)  UZ - T = G12 + (w0*w5 - 1)
  (1.6)  UV - T = G23 + (w0*w3 - 1)
  (1.7)  XY - T = w2*w7 - 1
  (1.8)  VZ - XY = Z*GV + X*GZ
  (1.10) (U+V+Z)^2 - 9T = 1/2[(U-V)^2+(U-Z)^2+(V-Z)^2] + 3[(UV-T)+(UZ-T)+(VZ-T)]
  (1.11) (X+Y)^2 - 4T = (X-Y)^2 + 4(XY-T)
  (1.12) (AB+6T)((A+B)^2-25T) = UA(AB+14T) + UB(AB+24T) + 2*UA*UB
plus the assembly: A+B = N, T = m+1, so nonneg of UA, UB and AB+6T>0 give
N^2 >= 25(m+1), i.e. SIB-CERT1  N^2 - 25m >= 25.  Also numeric spot-check of the
whole chain on random integer weights >= 1 satisfying the generator inequalities.
"""

from fractions import Fraction as F
import random

import sympy as sp

w = sp.symbols("w0 w1 w2 w3 w4 w5 w6 w7 w8 w9", positive=True)
w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w

m = w1 * w7 + w1 * w9 + w2 * w9
T = m + 1
U = w0 + w8
V = w3 + w4
Z = w5 + w6
X = w1 + w2
Y = w7 + w9
A = U + V + Z
B = X + Y
N = A + B

E12 = w0 * w6 + w5 * w8 + w6 * w8
E23 = w0 * w4 + w3 * w8 + w4 * w8
G12 = E12 - m
G23 = E23 - m
GV = V - X
GZ = Z - Y

UA = A**2 - 9 * T
UB = B**2 - 4 * T

checks = {
    "(1.5)": (U * Z - T) - (G12 + (w0 * w5 - 1)),
    "(1.6)": (U * V - T) - (G23 + (w0 * w3 - 1)),
    "(1.7)": (X * Y - T) - (w2 * w7 - 1),
    "(1.8)": (V * Z - X * Y) - (Z * GV + X * GZ),
    "(1.10)": (A**2 - 9 * T)
    - (
        sp.Rational(1, 2) * ((U - V) ** 2 + (U - Z) ** 2 + (V - Z) ** 2)
        + 3 * ((U * V - T) + (U * Z - T) + (V * Z - T))
    ),
    "(1.11)": (B**2 - 4 * T) - ((X - Y) ** 2 + 4 * (X * Y - T)),
    "(1.12)": (A * B + 6 * T) * ((A + B) ** 2 - 25 * T)
    - (UA * (A * B + 14 * T) + UB * (A * B + 24 * T) + 2 * UA * UB),
}

ok = True
for name, expr in checks.items():
    d = sp.expand(expr)
    if d != 0:
        print(f"FAIL {name}: {d}")
        ok = False
    else:
        print(f"{name}: OK")

# assembly spot-check on random exact weights with generators enforced
rng = random.Random(23)
tested = 0
for _ in range(20000):
    vals = {v: rng.randint(1, 6) for v in w}
    g12 = G12.subs(vals)
    g23 = G23.subs(vals)
    gv = GV.subs(vals)
    gz = GZ.subs(vals)
    if g12 < 0 or g23 < 0 or gv < 0 or gz < 0:
        continue
    tested += 1
    Nv = N.subs(vals)
    mv = m.subs(vals)
    if Nv**2 - 25 * mv < 25:
        print("ASSEMBLY FAIL at", vals)
        ok = False
        break
print(f"assembly spot-check: {tested} generator-feasible points, all N^2-25m >= 25")

# sharpness at all-ones seed
ones = {v: 1 for v in w}
print("all-ones seed: N =", N.subs(ones), " m =", m.subs(ones),
      " N^2-25m =", (N**2 - 25 * m).subs(ones))

print("ALL PASS" if ok else "FAILURES PRESENT")
