# Q17 ANSWER + AUDIT — 2026-06-21 (GPT Pro "Kapsamlı"; chat "Beta Bound Plateau Analysis")

GPT's recommendation: **do NOT run the 45,130-var order-6 4-color monolith.** Instead build a
**two-side-color ORDER-5 core SDP** + minimal-counterexample degree reduction + new
**bipartite-block recoloring (BR) inequalities**, enforce PSD by **rank-one spectral cuts (→ sparse LP)**,
and go to order-6 only if the strengthened order-5 stays > 0.08.

## VERIFIED CLAIMS (audited)

### (A) Minimal-counterexample degree lemma — SOUND (hand-proof)
`β(G) ≤ β(G−v) + d(v)/2` (extend an optimal cut of G−v by placing v on its cheaper side).
⟹ a vertex-minimal counterexample (β > n²/25, n = #vertices) has **δ(G) > (4n−2)/25**, i.e. min-degree
density ≥ 4/25 = 0.16 a.e. Cheap one-root localizer `⟨[[F·(D − 4/25)]]⟩ ≥ 0`. Peeling low-degree
vertices raises e/n² (pushes toward the BCL high-density zone).

### (B) Bipartite-block recoloring (BR) — SOUND (hand-proof)
For a GLOBAL max cut and U with G[U] bipartite: **m(U) + m(U,Ū) ≤ ½·e(U,Ū)** (mono = same side).
Proof: properly 2-color G[U] (keep outside fixed), average the coloring and its swap → all internal U
edges cut, half the boundary cut; both are valid cuts ≤ MaxCut ⟹ the inequality. A bundled 2nd-order switch.
Local forms (EX, minimal-counterexample core): `25 T(v) − 4 D(v) + 2 D(v)² ≥ 0` (order-3 rooted);
`25 B_ab − 4 s_ab + 2 s_ab² ≥ 0` (order-4 two-root).

### (C) ★ Order-5 mono-P₃ BR cut excludes the bad Clebsch cut WITHOUT margin colors — VERIFIED COMPUTATIONALLY
(`verify_BR_clebsch.py`) Root a monochromatic P₃ `1-3-2` (13,23∈E, 12∉E, all same side); U = N(1)△N(2)
(bipartite: N(1)∖N(2), N(2)∖N(1) each independent). Add BR for this U. Results:
- **bad 28-edge Clebsch cut:** 12 mono-P₃ embeddings, **ALL 12 violate BR by exactly +1.0** → excluded.
- **genuine Clebsch max cut (=32):** 0 mono-P₃ embeddings → 0 violations → SOUND.
- **C5[n] extremal:** 0 mono-P₃ embeddings → SOUND.
⟹ a single ORDER-5, TWO-COLOR inequality kills the 30%-mono Clebsch obstruction; the whole 4-color
margin lift (A_L/A_H/B_L/B_H) is **unnecessary**. This is the tractability breakthrough.

### (D) Why the earlier order-5 margin lift was vacuous — explained
The PSD margin localizer `q²(H−τ)` with q of flag-order ℓ needs master order 2ℓ; at N=5 only ℓ=2,
so the PSD localizer first correlates two 3-vertex configs at N=6. BUT order-5 supports richer **linear
margin cylinder localizers** `⟨[[F·(τ−H)]]⟩ ≥ 0` (F order ≤4, one fresh vertex for H) — use those.

## COMPUTE RECIPES (for when SDP is needed)
- **Z2 isotypic reduction done right** (my Stage A densified because I materialized S·O): accumulate orbit
  AVERAGES directly; for a self-paired type split the block via the flag-involution π into M₊ (size (m+r)/2)
  and M₋ (size (m−r)/2), 210 → 105+105; each transformed entry uses ≤4 original entries (no dense B^TAB).
  Drop one cone from every (σ,τσ) pair.
- **Rank-one PSD spectral cutting planes:** replace each PSD cone by linear cuts `vᵀM_j(y)v ≥ 0`; solve
  sparse LP; add negative-eigenvector cuts; repeat. Every LP is a WEAKER relaxation ⟹ a sound UPPER bound;
  once an LP gives ≤0.08 the proof is done (no full PSD convergence needed). Seeds: eigenvectors of the
  low-accuracy SCS dual Q_j.
- **Dual is NOT automatically smaller** (still ~22,726 state constraints) — use dual constraint generation
  (active set + separate over all orbits) if going that route.
- **Rational certification from low-accuracy solve:** Q_j = RᵀR, round R to dyadic rationals, Q̂=R̂ᵀR̂
  (exactly PSD); compute exact residuals ρ_O; bump λ ← λ + max(0, max_O ρ_O) to repair (normalization
  coeff is 1 per state). Needs final value strictly < 0.08 with margin.
- Solver engineering: SCS one-core is the bundled QDLDL; MKL-Pardiso / cuDSS (GPU) parallelize — but build
  pain on Windows. **The rank-one-cut LP route sidesteps all of this.**

## SAFE / UNSAFE state reduction
SAFE: merge exact τ-orbits; merge states with identical rational signatures (objective+band+active cuts),
refine as cuts are added; drop one cone per (σ,τσ) pair; project moment blocks onto common-kernel z^⊥.
UNSAFE: deleting arbitrary states / keeping only numerically-massed states (restricts the primal → false low bound).

## ACTION PLAN (GPT's boxed sequence)
order-5 two-color core → BR/EX separation → rank-one PSD LP → order-6 only if necessary.
Order-5 core constraints: order-5 moments (2-color), SW0 + side switches, degree localizers D(v)≥4/25,
neighborhood EX `25T−4D+2D²≥0`, the mono-P₃ BR cut, and BR(q)≤0 / EX(q)≥0 for all Boolean profiles q on
N(1)∪N(2) (≤2^12=4096 cases per 3-root type, exact enumeration — no coordinate ascent).
Fallback: a BCL-style rooted-cut program on 2-side-colored order-5 states with adaptive BR/EX generation
(NOT a 16-color Clebsch flag algebra — that's larger).

Full answer: in the chat (chatgpt.com/c/6a370bb0). Decision rule: if the strengthened order-5 certifies
0.08, stop; order-6 only if a quadratic conditional-margin relation is the surviving violation.
