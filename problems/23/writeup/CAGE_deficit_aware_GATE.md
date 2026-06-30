# GATE: GPT-Pro deficit-aware (LOAD-based) closing Farkas certificate — REFUTED as a UNIFORM cone

Workflow: `_wf_deficit_adv.py` (run from `problems/23/writeup`). EXACT Fraction verdicts; floats only to
guess LP solutions, every verdict re-checked as Fractions.

## Setup gated
Per gamma-min connected-B max cut + bad edge `f` with `ell_f=5`, unique shortest blue geodesic
`P=(x0..x4)`, uniform geodesic load `T` from `struct_for_side`:
`25*M(P) = 5*(N^2-Gamma) - 25*sum_i(T[x_i]-N) - S^2 + 25*q`, `h_i=T[x_i]/N`, `S=sum h_i`, `q=min_i h_i h_{i+1}`.
Claim to gate: `25*M = sum_U alpha_U dGamma(U) + sum_W beta_W (deltaB(W)-deltaM(W)) + sum_i lambda_i (h_i h_{i+1}-q)`
with `alpha,beta,lambda >= 0` UNIFORM (position-indexed, same across every row).

## (1) Generator nonnegativity — PASS
Across **244** L=5 unique-geodesic gamma-min rows (battery: C5|C7, C5|C5, C5|C9, C5|C11, C5|C13,
C5+Myc(C7), C5+Grotzsch, nonuniform C5 blowups): **0 generators with negative value.**
Each class is genuinely `>=0`: dGamma(U) for neutral connected switches, deltaB-deltaM, h_i h_{i+1}-q.

## (2) Decisive witness — fix contributes NOTHING here
Glued C5|C7 N=12, bridge (0,5), side `[0,1,0,1,0,1,0,1,0,1,0,0]`, `f=(0,4)`, `P=(0,1,2,3,4)`:
- `Gamma=74`, `T_path=[5,5,5,5,5]` (uniform load) ⟹ `S=25/12`, `q=25/144`, **`C_L=S^2-25q=0`**.
- All 5 product-slacks `(h_i h_{i+1}-q)=0`; all dGamma neutral switches `=0`. `25*M=1225`.
- The product-slack ("deficit-aware") fix is identically zero on the witness. The row is only "reached"
  by scaling ONE O(1) max-cut generator by the row-specific number 1225 — i.e. a degenerate per-row
  scaling, NOT a uniform formula.

## (3) Adversarial result — UNIFORM cone INFEASIBLE (EXACT Farkas)
- **Per-row** (each row in isolation): 0/244 infeasible — but only via the degenerate single-generator
  scaling above; "per-row feasible" is vacuous here.
- **Uniform** (one coefficient vector for all rows): **INFEASIBLE** (HiGHS status 2). Confirmed by an
  **EXACT rational Farkas certificate** `y` supported on 4 rows
  {C5|C7 N=12 [(0,5),(2,7)] f=(0,1); C5|C5 f=(7,8); C5|C9 f=(3,4); C5+Myc(C7) f=(2,3)}:
  exactly `A^T y >= 0` (min component `=0`) and `b^T y = -1 < 0`. Re-checked over Fractions.
- Persists on a broader battery (Grotzsch-embedded C5, C5|C11, C5|C13, 2-bridge glues): still infeasible.

## Root cause (the missing direction)
- Target `25*M = Theta(N^2)` (`25M/N^2 in [5.5, 8.75]`: 875@N=10, 1225@N=12, 1575@N=14, 3125@N=20).
- Every generator value is `O(1)`: `max|deltaB-deltaM|=21`, `max|h_i h_{i+1}-q| < 1`, and crucially
  **every dGamma(U) neutral-switch generator is identically 0** on gamma-min cuts (the only `N^2` lever
  vanishes by gamma-minimality of length-preserving neutral flips).
- A UNIFORM (N-independent) nonnegative combination of `O(1)` generators cannot equal an `N^2` target.
  The deficit-aware (product-slack) fix does not add any `N^2`-scaling generator, so it dies for the
  SAME structural reason the prior SIZE-based cone did — just deferred.

## What is still missing
A generator that carries `Theta(N^2)` mass and is sign-controlled on gamma-min cuts. Candidates: dGamma
for switches that are NOT length-preserving (so dGamma != 0) but whose sign is still forced by
gamma-minimality, or an `N`-scaled max-cut aggregate (e.g. `sum_W (deltaB-deltaM)` weighted by load).
The current three generator families are all `O(1)` (or vanish), so no uniform Farkas certificate exists.
