# Q18 — order-5/6 two-color core caps at 0.125; BR/EX do not bind. Now what? (2026-06-21)

## Result of your Q17 pivot (audited)
- Your COMPUTE advice works: order-5 2-color = 212 states, order-6 2-color = 1031 states, solves <1s–50s.
- Your new MATH is sound & verified: degree lemma (β(G)≤β(G−v)+d(v)/2 ⟹ min-deg ≥ (4n−2)/25) and the
  bipartite-block recoloring BR (verified: the mono-P3 BR cut excludes the bad Clebsch cut by exactly +1
  per embedding; sound/vacuous on Clebsch max-cut and on C5[n]).

## BUT the bound does NOT reach 0.08. It is stuck at d_mono = 0.125 (β/N² = 1/16):
Order-5 AND order-6 two-color core, band d_edge∈[0.2486,0.3197), objective d_mono:
- moments+band: 0.3198
- +SW0 (2 d_mono − d_edge ≤ 0): 0.15985  (β/N² = 0.0799)
- +SW0+SW1 (1-root side switch): 0.12500  (β/N² = 0.0625)
- +SW0+SW1 + mono-P3 BR: 0.12500  (UNCHANGED)
- +SW0+SW1 + BR-profiles (all same-side 2-root U=N(a)△N(b)): 0.12500 (UNCHANGED)
- +SW0+SW1 + EX (25T−4D+2D² ≥ 0): 0.12500 (UNCHANGED)
- +SW0+SW1 + degree cylinders ⟨[[F(D−4/25)]]⟩≥0: 0.12500 (UNCHANGED)
NONE of the new cuts bind. (All sound — the bound never drops below 0.08.)

## Diagnosis of the +SW0+SW1 optimum (d_mono=0.125, d_edge=0.25, SW0 TIGHT: 2 d_mono = d_edge)
Top mass: (i) edge-less 2-colored 5-states (e=0, balanced colors); (ii) all-ONE-side 5-vertex states
with e=3 (d_mono=0.30, both endpoints same side). On this returned optimum:
   BR@x = +0.214 > 0,  BR-profiles@x = +0.638 > 0  (it VIOLATES the aggregated BR functional!),
   EX@x = −3.44 (satisfied).
Yet adding the constraint BR@x ≤ 0 still returns 0.125 — the SDP rebalances to a DIFFERENT 0.125 point
with BR@x ≤ 0. So the scalar aggregated BR ≤ 0 does not bind: 0.125 is BR-feasible.

## CAVEAT (important)
I used only SW0 (a=b=½) + a simple 1-root side SW1. I did NOT port the EXACT 2-root binary switching
(separation oracle) that previously reached the d_mono=0.10 plateau in the 2-color SDP. So my 0.125 is
LOOSER than the prior 0.10. The 4-color order-6 margin lift reached 0.10 but is compute-heavy and also
short of 0.08.

## QUESTIONS
1. The SW0-saturating d_mono=0.125 optimum (mixture of empty 2-colored clusters + single-side e=3
   mono-clusters, 2 d_mono = d_edge exactly): what IS this obstruction graphon, and is there a TARGETED
   sound inequality that kills it? It is not the Clebsch cut.
2. Why doesn't BR bind even though the optimum VIOLATES the aggregated ⟨BR⟩? Must BR be imposed as a
   PSD-LIFTED / localized constraint conditioned on the mono-P3 root —
   ⟪[[ F_i F_j · BR_σ ]]⟫ ⪰ 0 — rather than the single scalar ⟨BR⟩ ≤ 0? If so, give the exact
   localized form (what multiplies BR_σ, what is the moment matrix).
3. Does porting the EXACT 2-root binary switching + a PSD-lifted BR actually reach 0.08, or does the
   two-color route GENUINELY WALL at ~0.10? Concretely: is the d_mono=0.125→0.10→0.08 descent achievable
   with order ≤6 two-color + the right cut, or is the margin (4-color) lift unavoidable?
4. If it walls: the single most promising move — (a) rank-one-cut LP on the 4-color order-6 (combine the
   margin-lift 0.10 with BR/EX), (b) a higher-root ANALYTIC argument for the medium band, or (c) pivot
   from flag-SDP to the degree-lemma + minimal-counterexample reduction (peel min-degree < 0.16n,
   raise density into the BCL high-density zone)?
5. HONEST VERDICT: is d_mono ≤ 0.08 reachable by ANY tractable flag-SDP for the medium band, or is the
   gap from the 0.10 plateau to the 0.08 target a genuine wall that needs a different idea?

Please be concrete and decisive. If a PSD-lifted BR or a specific new inequality kills the 0.125
SW0-saturating optimum, give its exact form.
