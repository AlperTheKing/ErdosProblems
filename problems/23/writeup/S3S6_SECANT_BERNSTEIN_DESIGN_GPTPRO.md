# s3,s6 Hard-Chart Closure Design (GPT-Pro, 2026-07-02) — Branch A / SIB S7 y=1

Status: certificate DESIGN complete (option c: certify Φ ≥ 0 itself, compactified; secant
primary + Bernstein fallback + KKT/Sturm residue). Codex to implement. Involution REJECTED as
proof primitive (c↔e reflection breaks m, s1, s2, denominators Y,Z — diagnostics only).
The negative dΦ/dR witness is NOT an obstruction: it only kills monotone descent to R=0.

## §1 Exact chart D6 (y=1, s3=0, s6=0)
Mirror normal coords: e = c+R (R≥0), H = b+c−d−e = b−d−R ≥ 0 ⟹ b = d+R+H.
Slack map: (s4,s5,s6,s7) = (fH, aR+fH, 0, aR). x = b+c−1 = d+c+R+H−1.
Active m: M0 = ac+df+ef = ac+df+f(c+R); m = x(u+v)+v ⟹ u = (M0−(x+1)v)/x... [u eliminated].
Chart variables (a,c,d,f,R,H,v): a,c,d,f ≥ 1, R,H ≥ 0, v ≥ 1, plus polynomial feasibility
  G2 = e−v = c+R−v ≥ 0,  G3 = M0−(x+1)v−x ≥ 0 [u≥1 cleared],  G4 = x(d+e)−M0+... ≥ 0 [s2≥0
  cleared]. No derivative condition is part of the chart.

## §2 Target polynomial
Denominator-cleared numerator P6 = M·Φ6 with M = x·e·Y·Z·(vB) > 0 on the feasible region.
MACHINE TARGET: **P6 ≥ 0 on D6**.

## §3 Path parametrization + why the derivative failure is harmless
G = R+H total gap; R = tG, H = (1−t)G, t∈[0,1]. G=0 ⟹ s4=s5=s6=s7=0 (lower-dim, closed).
∂P6/∂t may be negative — harmless; certify P6(t) ≥ 0, NOT the derivative sign.

## §4+§8 SECANT certificate (primary)
Identity (Sec): P6(t) = (1−t)·P6(0) + t·P6(1) + t(1−t)·W6(t), W6 polynomial (numerator
divisible by t(1−t)). STRONG: certify P6(0) ≥ 0, P6(1) ≥ 0, W6 ≥ 0 on the PROJECTED feasible
region — endpoints are NOT assumed feasible (avoids the trap that varying t violates
s1,s2,u≥1); each with Bernstein-positive multipliers: P6(0) − Σ σ0j·Gj ≥ 0 (all Bernstein
coeffs ≥ 0), same for P6(1), W6. Meaning: the chart lies above the secant between the R=0 and
H=0 boundary charts; pointwise negative derivative allowed. WEAK fallback: direct Bernstein
subdivision of P6 on failure cells.

## §5 Boundary routing
R=0 → common ridge with s3,s7 (certify separately at R=0 if not already closed); H=0 →
s3=s4=s6=0 face → route to s4 boundary chart; G=0 ridge (contained in both); v=1, e−v=0, u=1,
s2=0 terminal faces → route to active-bound charts or include as boundary Bernstein cells;
infinity → projective compactification (no informal asymptotics).

## §6 Compactification
Shift a=1+A, c=1+C, d=1+D, f=1+F, v=1+V (A,..,V,G ≥ 0); simplex λ0+λA+λC+λD+λF+λV+λG=1,
λi ≥ 0; domain Δ6 × [0,1]_t. Homogenize P6 and G2,G3,G4 by powers of λ0. Cell certificate
types: (i) infeasible cell (some Gj all-Bernstein-negative), (ii) positive cell (P6
all-Bernstein-nonneg), (iii) constrained-positive cell (P6 − Σ σj·Gj Bernstein-nonneg with
Bernstein-positive multipliers σj), (iv) boundary cell (lies in routed face). Output = finite
exact rational certificate list: (support T, chart id, rational simplex cell, type, bound).

## §7 Rank-support split
Rank 7/8 positive-dimensional supports (1242+1291 of 4269) → compactified Bernstein cells
(Groebner alone inefficient — not isolated). Rank-9 isolated residue (615) → exact KKT ideal
I_T = <∇P6 − Σ μj∇Gj, active Gj, μj·Gj> + strict positivity of inactive constraints →
rational univariate representation → Sturm isolation → verify root real, feasible, P6 > 0.

## §9 Geometry rationale
s3,s7 face: positive R ridge derivative ⟹ close by descent to R=0. s3,s6 face: slack map
(fH, aR+fH, 0, aR) — increasing R moves mass s4→s7, derivative can be negative; closure is by
positivity above the secant, not descent. "This closes the s3,s6 chart without requiring any
false derivative sign, face involution, or class width majorization."

## Implementation checklist (Codex)
1. Build D6 chart + P6, G2, G3, G4 exactly (sympy, Fraction).
2. Secant split: compute P6(0), P6(1), W6; attempt strong certificate on projection.
3. Bernstein engine: simplex-cell subdivision + multiplier search (LP over Bernstein coeffs).
4. Rank-9 cleanup: KKT + RUR + Sturm per isolated support.
5. Wire into _codex_sib_s7_y1_manifest.py; Claude exact-audits every artifact.
