# Flag-SDP Soundness Audit — 2026-06-21 (13-agent adversarial workflow)

Workflow `flagsdp-soundness-audit` (4 dimensions × adversarial verify × synthesis, 13 agents,
1.13M subagent tokens). Audited `flag_margin_sdp.py` and the Step-2 density-band route.

## VERDICT: the relaxation is SOUND (a valid upper bound *within its band*); the blocker is a WEAK localizer, not a bug.

### Soundness (constraint-by-constraint, 0 violations over exhaustive max-cut tests n≤8–9)
- `side_sw0` (2·d_mono−d_edge≤0), `side_sw1` (both roots): valid max-cut switching. SOUND.
- `margin_switch_vec`: a genuine max-cut switching inequality. gsw=0 on the C5[n] extremal
  (does NOT exclude it), gsw>0 only on the non-optimal bad Clebsch cut (=24 at order-16,
  +0.264 at order-6). 0/16720 violations on real max-cut states n≤7. Correct sign/weight/no-double-count. SOUND.
- `localizer_vecs`: always admit an honest feasible split (0/15430 failures n≤9). SOUND but WEAK (below).
- `P_sigma_col`: correct Razborov moment matrix (PSD on graphon limit densities, min eig ≈ −6e-17 on
  C5 blow-up; intentionally non-PSD per single graph). SOUND.

### The edge band is INTENTIONAL, not a bug
Default band (0.2486, 0.32) on e/C(N,2) scale = x=e/N² ∈ [0.1243, 0.16] **deliberately excludes**
C5[n] (x=0.20, d_edge=0.40). Design = density decomposition: **BCL handles the tails (incl. C5[n] in the
high tail); the SDP handles only the medium band.** ⟹ my earlier "band correction" to include 0.40 was WRONG.
In-band the true max d_mono is only ≈0.0494 (N=9)/0.0600 (N=10) ≪ 0.08, so the in-band 0.08 target is
**NON-sharp (strict slack)** — no equality case in-band ⟹ no finite-flag sharpness obstruction ⟹ exact
rational rounding is the EASY part; achieving a floating ≤0.08 is the only blocker.

## THE BLOCKER (flagged by implementation + ceiling + strategy dimensions)
The implemented localizers are the **weakest averaged-scalar form** (one scalar linear ineq per color on the
empty-root density), NOT the **PSD-lifted** form GPT Q16 step-3 requires:
`⟪[[F_i F_j (H_σ − ℓ_c)]]⟫ ⪰ 0` and `⟪[[F_i F_j (u_c − H_σ)]]⟫ ⪰ 0` over rooted indicator flags.
With only the averaged scalar, the abstract color is barely tied to each vertex's true margin, so a
pseudo-graphon satisfies the average while mislabeling vertices ⟹ N=5 gave ZERO gain (0.125 all 3 configs),
and N=6 would re-plateau. Also: t=1/8 is inconsistent with the honest-mark thresholds (h≤1/h≤2) used by the
unit tests (159–263/684 honest marks violate t=1/8) — must be reconciled.

## RECOMMENDATION (do NOT pivot to H2)
1. **Implement PSD-lifted margin localizers** (Q16 step-3) + reconcile t=1/8 with honest-margin marks. ← gating item
2. THEN run N=6 in the **OLD band (0.2486,0.32)**: does it break below 0.09375 toward 0.08?
3. Parallel/cheap, load-bearing: **reconcile e/N² vs e/C(N,2) band normalization** and confirm the SDP band
   exactly covers the full BCL-open window (0.2486, 0.3197) with no uncovered sliver (the one `is_soundness_bug`
   the verify stage took seriously — closure to all-n fails if a density sliver is uncovered).
4. **BCL-finiteness gap** remains: BCL Thm 1.3 (high tail incl. C5[n]) holds only "n≥n0", n0 unspecified.
   Needs an explicit finite-n constant or independent finite-n verification for unconditional all-n closure.

## Strategic facts
- Flag-SDP at strict ≤0.08 **closes #23 for all n** (blow-up transfer β(G[t])=t²β(G), zero o(n²) residue),
  modulo Step 1 (a(30)≤36, a(25)) + band coverage + BCL finiteness.
- All 3 live Step-2 routes (Clebsch CF, C5 master-bound, H2 peeling) hit the SAME wall: an effective
  constant-fraction MaxCut surplus / stability for dense triangle-free graphs near C5[n] (Alon gives only
  Θ(e^{4/5})=o(e)). Flag-SDP is the most tractable, automatable, rounding-complete embodiment.
- N=7 4-color = ~570k states (not ~175k); **N=6 (45,130) is the realistic computational ceiling.**
- HONEST STATUS: Step 2 research-grade OPEN. Best certified bound 1/20; target 1/25; gap real, unhedged.

Full memo + per-dimension findings: workflow run wf_b0cec9bc-7dc (task w40bp4ds3 output).
