# Q10 — Attack on CF (Clebsch frustration): GPT Pro ANSWER + Step-2 AUDIT (2026-06-20)

GPT Pro Extended (chat c/6a35f70f), reasoned **80m36s** then produced a full answer.
(NOTE: Step-2 earlier mislabeled Q10 "stalled" — WRONG; it completed. Corrected.)
Question: prove CF = `τ_K(G) ≤ (N²/5−e)/2 + o(N²)` for band triangle-free G, via
flag-algebra / C5-packing / frustration-stability. **Verdict: SOUND, all explicit claims
VERIFIED (`verify_q10_cf_audit.py`). CF NOT proved, but the obstruction is now precisely
characterized + a concrete finite flag target identified.**

## What GPT proved / showed (Step-2 audited)
1. **τ_K(G) ≤ (3/2)β(G) — PROVED (hand-verified + 0 violations/22 graphs).** Max cut (X,Y),
   β=e(G[X])+e(G[Y]); use an induced C4 in Clebsch (cross-edges cost 0; inside-X edges cost
   1+[same a-label], minimized = e(G[X])+β(G[X])). ⟹ τ_K ≤ β+β(G[X])+β(G[Y]) ≤ (3/2)β. With
   BCL β≤N²/23.5: **τ_K ≤ (3/47+o(1))N² ≈ 0.0638N²**. CF needs ≤ (1/5−x)/2 ∈ [0.020,0.0378].
   So 3β/2 is ~2× too weak — and (with the 5-cut bound) caps β at ~1/17.4 (= the SAME wall as
   the radius-2 scalar 1/17.2). The strongest UNCONDITIONAL band-wide bound.
2. **Why raw SDP fails (direction):** the 16×16 cost matrix is PSD (eigenvalues 12,4,4,4,4,4),
   so SDP relaxation LOWER-bounds τ_K (wrong way). Flag algebra has a max_G min_φ quantifier
   problem; a fixed LOCAL ROOTED coloring policy removes it. ⟹ need an explicit rounding rule.
3. **★ C5-rooted rounding F_C (PROVED upper bound):** fix induced C5; types R/S_i/D_i by
   C-neighborhood. Random label ϕ_{ε,j} ⟹ τ_K ≤ F_C(G) (explicit 7-vtx flag functional, eq 7);
   degree form F_C ≤ W_C = vol(R)+½vol(S) = 2e−½Σ_i Σ_{u∈N(c_i)}d(u) (eq 10). ⟹ **CF holds if
   SOME induced C5 has W_C ≤ (N²/5−e)/2**, i.e. Σ_i S_{c_i} ≥ 5e−N²/5. Tight (=0) on C5[n].
4. **★ The "missing 6th coordinate" + RR flag target:** F_C alone FAILS on Clebsch blowups
   (F_C=13 but τ_K=0 — the 5 roots can't distinguish 5 Clebsch twin-pairs). Fix: a unique
   Clebsch vertex z anticomplete to each C5 gives a distinct 6-bit signature; the 6-root
   functional F_{C,z}^(6) (eq 14) is 0 on Clebsch blowups. **Cleanest CF-sufficient statement
   (RR):** `min{ min_C F_C, min_{C,z} F_{C,z}^(6) } ≤ (N²/5−e)/2 + εN²` — a finite 7/8-vertex
   rooted CSP, exact on both C5-blowups and Clebsch-blowups. UNPROVEN (no PSD certificate yet).
5. **★ Synchronization obstruction (VERIFIED via M_2(C5)):** Clebsch = Cayley(Γ, {[5]∖{i}});
   zero-cost edge ⟺ difference is a generator; only dependency g_1△…△g_5=∅. So each packed C5
   forces a generator-permutation + base potential, but these need NOT agree across cycles from
   DIFFERENT packed C5's (cycle-space synchronization; edge-disjointness gives no cross-cycle
   condition). **Explicit gap: M_2(C5) (twice-Mycielskian, N=23, e=71, χ=5 ⟹ non-Clebsch-hom ⟹
   τ_K≥1), with 13 edge-disjoint induced C5's (τ_5≥13 ≫ 7/800·23²=4.63), packing LP value 0.**
   Step-2 VERIFIED: N=23/e=71/triangle-free/4-coloring FAILS; 13 cycles all induced C5 & edge-
   disjoint. ⟹ entropy/LP proofs MUST add cycle-space synchronization; local marginals insufficient.
6. **★ Frustration-stability (sub-target c) is FALSE — VERIFIED.** ρ_K ≤ τ_K ≤ 2ρ_K (ρ_K=edges
   to delete for Clebsch-hom). Small τ_K ⟹ close to the Clebsch-hom class, which is much bigger
   than {C5/Clebsch blowups}. **Counterexample G=C5[m]⊔K_{r,r} (5m=3N/4, 2r=N/4): τ_K=0
   (both Clebsch-hom), density 0.128125 (in band), τ_5/N²=0.0225>7/800, yet ≥(23/320)N² edits
   from C5[n].** Step-2 VERIFIED (N=80: τ_K_ub=0, density 0.128125, triangle-free). ⟹ the right
   stability notion is SATURATION of `e+2τ_K ≥ N²/5−o(N²) ⟹ close to C5[n]`, NOT small τ_K.
7. **Exact MILP falsification for CF:** τ_K(F[k])=k²τ_K(F) (eq 19), τ_5(F[k])≥k²ν_5*(F) (eq 20,
   ν_5*=fractional C5-packing). A finite F with band density, ν_5*≥7/800|F|², and e(F)+2τ_K(F)
   > |F|²/5 (eq 21) would falsify CF via blowups; τ_K(F) by the MILP (eq 22).

## Step-2 AUDIT verdict: SOUND
τ_K≤3β/2 re-derived + 0/22; M_2(C5) (N=23,e=71,χ≥5,13 edge-disjoint induced C5's) verified;
C5[12]⊔K_{10,10} (τ_K=0, density 0.128125, in band) verified. No overclaim — GPT states CF
unproved. **Net:** CF still open, but (a) the strongest unconditional bound τ_K≤3β/2 (caps
1/17, the known wall); (b) the obstruction PINNED (synchronization across packed C5's + the
twin-pair/6th-root issue); (c) frustration-stability REFUTED (corrected to e+2τ_K saturation);
(d) the concrete finite path forward = the RR 7/8-vertex rooted flag inequality (needs a PSD/
flag certificate — flag-algebra SDP software or a further targeted consult); (e) an exact MILP
to hunt a CF counterexample on blowup bases.

## Step-2 follow-up test (verify_WC_c5root.py, 2026-06-20): W_C is too crude
The degree-relaxation one-cycle condition `min_C W_C ≤ (N²/5−e)/2` (Q10 eq 11/12, where
W_C=2e−½Σ_i S_{c_i}, F_C ≤ W_C) is TIGHT (=0=RHS) only at C5[n]; it FAILS on Clebsch blowups
(min W_C=17.5 vs RHS=5.6, confirming the twin-pair/6th-root need) AND on ALL random band
graphs (min W_C≈11–20 vs RHS≈6–13). Since τ_K ≤ F_C ≤ W_C and τ_K ≤ RHS is known to hold,
this means W_C is a LOOSE bound — the CF-sufficient proof must use the TIGHTER rounding F_C
(the full eq-7 functional) and the 6-root F_{C,z}^(6), NOT the degree relaxation W_C. Sharpens
the target: the flag-SDP certificate is for the rooted F_C/F_{C,z} CSP, not the degree form.

**★ ACTUAL F_C TEST (verify_FC_c5root.py, F_C via the 10 explicit (ε,j) maps — robust, tight):
CONFIRMS Q10's RR structure.** min_C F_C = 0 = RHS at C5[n] (tight); **min_C F_C ≤ RHS on ALL
12 random band graphs** (F_C 1–8 vs RHS 6–15.5, 0 failures); **fails ONLY on Clebsch blowups**
(F_C(Clebsch[1])=13 — exactly Q10's claimed value — vs RHS 5.6). So the C5-rooted F_C SUFFICES
generically and breaks exactly where Q10 said (Clebsch-blowups, the twin-pair issue), where the
6-root F_{C,z}^(6) (=0 on Clebsch-blowups per Q10) takes over. ⟹ **RR = min{min_C F_C,
min_{C,z}F_{C,z}} ≤ RHS is computationally well-supported as the correct CF-sufficient target**
(F_C for the generic case, F_{C,z} for the Clebsch case). The remaining gap = a flag-algebra SDP
certificate for RR (research-grade). CF/RR still UNPROVEN — do NOT mark solved.

## Next steps
- The RR flag inequality (using F_C/F_{C,z}^(6), NOT W_C) is the sharpest CF-sufficient target —
  attack via flag-algebra SDP (flagmatic/CSDP) or a focused consult on the 7/8-vertex rooted CSP.
- The MILP falsification: run it on small triangle-free bases F (band density, high ν_5*) to
  hunt e(F)+2τ_K(F) > |F|²/5 — would refute CF if found (none expected; CF strongly evidenced true).
