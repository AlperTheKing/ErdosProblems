# Q17 — Make the medium-band flag SDP tractable + any reducing lemma (2026-06-21)

## Setup (Erdős #23, Step 2, medium-density band)
We bound β/N² = d_mono/2 over triangle-free graphs equipped with a GLOBAL max-cut 2-coloring
(sides A,B; mono edge = same side), restricted to the MEDIUM edge-density band
x = e/N² ∈ [0.1243, 0.16] (d_edge = 2e/N² ∈ [0.2486, 0.32]). Balogh–Clemen–Lidický Thm 1.3 handles
the low/high tails (the sharp extremal C5[n] sits at x=0.2, in the high tail). Goal: certify
**d_mono ≤ 2/25 = 0.08** in the medium band, then extract an exact rational certificate.

We built a Razborov flag-algebra SDP at order **N=6** with a **4-color margin lift**:
colors 0=A_L,1=A_H,2=B_L,3=B_H (side = c//2, mark = c%2, mark by margin H(v)=cutdeg−monodeg,
threshold τ=1/8). Constraints:
- PSD moment matrices M^σ(x) ⪰ 0 for 48 colored types σ (k=1,2 roots);
- edge band; macroscopic max-cut SWITCHING inequalities (side SW0: 2 d_mono − d_edge ≤ 0; side SW1);
- a margin-conditioned **low-low cut-edge switch** gsw·x ≤ 0;
- **PSD-lifted margin localizers** L_c(x) = ⟪[[ F_i F_j (H_σ − τ) ]]⟫ ⪰ 0 (High c) / (τ − H_σ) (Low c),
  H_σ a degree-1 rooted-flag margin density.
VALIDATED (order-6 graphon densities): the localizers+switch EXCLUDE the bad 28-edge Clebsch cut
under every marking (honest → switch fires gsw=+0.26; evasive all-High remark → L_{A_H} not PSD,
min-eig −0.8) while the true extremal C5[n] stays feasible (all L_c PSD, min-eig −0.0). The 2-color
SDP plateaus at d_mono ≤ 0.10 (=1/20); the margin machinery should push toward 0.08.

## COMPUTE WALL (the blocker)
Primal SDP: **45,130 variables** (order-6 4-colored triangle-free states), **52 PSD cones**, largest
moment block **210×210** (Σ size = 4052, Σ size² ≈ 645,592). Hardware: Threadripper 64C/128T, 384 GB.
- **SCS** (first-order, sparse): converges to the band+moments baseline **0.125** in ~54 min, but runs
  at **~1 core** (sparse-direct QDLDL factorization is serial; the small cone projections don't
  parallelize); a full psdloc solve ≈ 54 min. Indirect mode also ~1 core.
- **CLARABEL** (interior-point): **OOMs** trying to allocate **627 GB** (dense KKT / Schur complement).
- **Z2 symmetry** (A↔B color swap; 45,130 → 22,726 orbits): halved variables but **densified** the
  moment matrices (S·O sums orbit columns), making SCS *slower* (timed out at 90 min).
- No CSDP / SDPA / MOSEK available (Windows, native; pip-only).

## QUESTIONS

**1. Make this SDP tractable / shorten the compute — concrete recipes:**
 (a) Correct **isotypic block-diagonalization** of the 210×210 block under the Z2 (A↔B) action,
     WITHOUT densifying: exact recipe to split M^σ into symmetric/antisymmetric sub-blocks in the
     flag basis (how to compute the τ-action on the flags of a self-paired type and the change of
     basis), so the cones genuinely shrink (210 → ~105+105).
 (b) Is the **DUAL** formulation (small PSD variables Q^σ, total dim 4052, + 45,130 linear
     constraints + a few multipliers) more tractable for an IPM than the primal, or does the
     45,130-constraint Schur complement also blow up? Any way to keep the dual small?
 (c) Can the **45,130-state primal be shrunk** soundly — a sufficient sub-family of states, or a
     merge of states indistinguishable to the objective + all constraints (beyond the Z2 orbit)?
 (d) Practical certification: can a **low-accuracy** SCS solve (eps ~1e-3) + a-posteriori rational
     rounding give a CERTIFIED ≤ 0.08, or must we converge to high accuracy first? Best rounding
     recipe (Flagmatic-style) without a dedicated solver?

**2. A reducing LEMMA — does the medium-band bound need the full order-6 SDP?**
 (a) Would a SMALLER flag order (N=5, ~4,660 states, fast) + the margin localizers already certify
     ≤ 0.08 in the medium band, making N=6 unnecessary? (At N=5 the margin machinery was vacuous —
     localizers didn't bind below the 0.10 plateau; is that fixable at N=5, or is N=6 essential?)
 (b) Is there an ANALYTIC (non-SDP) argument specific to the medium band — a weighted local
     switching / symmetrization inequality, or a 5-coloring/pentagon-frustration bound — that gives
     d_mono ≤ 0.08 directly there, bypassing the big SDP?
 (c) Can the medium-band claim be reduced to a much smaller "core" SDP (a few types, small flags)
     by a structural lemma, with the rest handled analytically?

**3.** If the flag-SDP at the needed order is genuinely too heavy, what is the single most promising
     alternative to close ONLY the medium band x ∈ [0.1243, 0.16] (the sole remaining gap, given BCL
     handles the tails)?

Please be concrete: exact formulas/recipes for the block-diagonalization and the
primal-shrink/dual, and a definite recommendation on whether N=6 is needed or N=5 / an analytic
argument suffices.
