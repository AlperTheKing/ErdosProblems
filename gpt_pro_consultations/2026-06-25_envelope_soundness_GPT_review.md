# GPT-Pro envelope-soundness review (2026-06-25, chat 6a3b8a74) — VERDICT + punch-list

Follow-up to the G4 referee read that correctly killed the deficit cert. Asked GPT to adversarially
verify the NEW per-root-MaxCut envelope (d_mono <= U_7) + the cert structure. GPT thought 18m22s.

## VERDICT: **NO FATAL ERROR FOUND IN THE NEW ENVELOPE ARCHITECTURE. SOUND.**
"The envelope genuinely repairs the old averaging defect. The old certificate effectively optimized the
cut after seeing each finite order-9 sample; the new construction fixes one rule for an entire root type
before averaging over the ambient graphon. That change is mathematically substantive and blocks the
weighted-C11 counterexample mechanism." Envelope soundness core inequality: SOUND, no fatal averaging trap.
Dual normalization (per-type sum_c lambda_{sigma,c}=1) = "the normalization missing from the old deficit
approach" — CONFIRMED correct.

## GAP-TO-FILL items (writeup precision + pending exact audit; NONE fatal). Fixes APPLIED to §3 unless noted:
1. **Profile well-definedness.** "profile in {0,1}^7" is literal only for {0,1} step graphons, not general W.
   FIX (GPT's safest repair, APPLIED): state Lemma 3.1 for {0,1} step graphons W_G (all the finite theorem
   needs; every finite G transfers to such). [Full-graphon version via independent rounding exists; unused.]
2. **Theorem 3.2 = vs <=.** The order-9 LP is a RELAXATION: eta_graphon <= eta_LP <= delta_dual. Even exact
   primal-dual equality proves only eta_LP = delta, NOT eta_graphon = delta. FIX (APPLIED): state eta <= delta
   (upper bound; only it is needed). "moment rows restrict x to genuine band graphons" -> "every genuine band
   graphon induces a feasible x" (converse can fail). Does NOT weaken the finite theorem.
3. **"107 triangle-free graphs on a labelled 7-set" is FALSE.** 107 = UNLABELLED iso classes on 7 vertices.
   FIX (APPLIED): canonical-isomorphism convention (sample ordered tuple -> canonical rep sigma by lex-least
   iso -> profile in canonical coords -> automorphisms/root-embeddings in the density).
4. **U_7 vs U_8 MISMATCH.** The prompt/validation report U_8 (8 anchors: validate_dmono_le_u8.py, u8sound.txt,
   c11_check.txt) but the theorem/cert is U_7 (7 roots, envelope_k7.py). COSMETIC if notation; GAP if the test
   used 8 roots — IT DID. >> RECONCILE WITH STEP-2: need d_mono <= U_7 validated (7 roots), not just U_8.
   (Holds by the same k-uniform argument; need the U_7-specific n=6,7 exact + zoo for the paper.)
5. **Profile-graph loops / C5 tightness.** Verification should confirm min_c E[C|sigma,c] = 2/25 at C5
   (the all-roots-in-one-class example detects omitted profile self-loops). Add to §6.
6. **Anti-recurrence (item 8): the rule must be FIXED before the order-9 averaging.** The verifier must
   reconstruct each stored (sigma,c) as ONE explicit Boolean table {0,1}^7->{0,1}, NOT re-optimized per flag
   (else the old fatal bug recurs). FIX (APPLIED to §3 dual wording: "each c a fixed Boolean rule, not
   re-optimised per flag"); regen_verify_u7 must confirm.
7. **Exact rational dual audit (PENDING — the remaining gate).** For n<=11 need delta_exact < 2/3025 =
   6.6116e-4. Float ~6.06e-4 is ~8.3% under (plausible) but "exact rational pending = not yet proved." If the
   rational reconstruction exceeds 2/3025, only n<=10 (N<=50, threshold 8e-4) follows. >> RUN regen_verify_u7
   on the CONVERGED cert -> exact rational delta -> confirm < 2/3025.

## STATUS
Architecture SOUND (GPT-validated). §3 fixes 1,2,3,6 applied. Remaining: item 4 (Step-2 reconcile U_7 valid),
item 5 (§6 C5-loop test), item 7 (exact dual audit on the converged cert — gating the n<=11 claim).
