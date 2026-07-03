# CD CompletionOps Lean Design (GPT-Pro, 2026-07-04, sibling thread 6a45e152; 23k full
# text in-thread — essentials + implementation status)

PRINCIPLE: completion = CHECKED TRACE, not algorithm. CompletionFootprint per op:
{pre/add/post CDStates, disj_pre_add, post = pre u add, outside = univ \ post,
ExchangeQuad with 4 count-equality fields (eB_XS/eM_XS/eB_XO/eM_XO vs
blue/badEdgesBetween counts), sigma_delta_eq : pre.sigma - post.sigma = quad.q}
— EXACTLY the Codex v5/v6 emission format. sigma_delta_eq provable once from counts.
Chain: fold-compatible chainFrom predicate + boolean checkChain w/ decide (NOT
native_decide). rhoSum foldl. Per-op: 25 pre.sigma <= 25 post.sigma + rho => telescope
mechanical. Z for q/rho/sigma (omega); Nat indices + explicit bounds (NOT dependent Fin)
in generated data. Constructor legality (bSegment/noncrossing/twin/flat5) = shape checks
NOT touching the telescope; terminalPrefix carries THE graph bridge (switchedWitnessPath
+ badEdge_ell_ge_five — already verified in Distances). CoreSignature bridge = wiring
rho_a = evalDictionary(signature, env) (24 sigs kernel-checked). Implementation order
par 16: sigmaZ first, then footprints, then chain, then telescope, then bridges.
## IMPLEMENTED (Claude, same tick): CDCore.lean EXIT 0 — OpArith {sigmaPre, sigmaPost,
q, rho, hq, hrho}, OpArith.step (25 spre <= 25 spost + rho), rho_nonneg, chainFrom,
rhoSum, **telescope** (list induction), rhoSum_nonneg, **completion_dominance**
(25 s0 <= nuK + rhoSum given valid-switch 25 s1 <= nuK). NINTH green module.
Remaining CD: footprint legality layer (data-driven vs Codex quads) + terminalPrefix
bridge + core-signature evalDictionary wiring.

## AUTHORITATIVE FULL TEXT (user-relayed 2026-07-04) — key additions beyond my summary
RISK LIST pinned: #1 SIGN (sigma_pre - sigma_post = (eB_XS - eM_XS) - (eB_XO - eM_XO);
reversed sign flips the whole telescope); #2 UNITS (quad counts must match sigmaZ units —
if Codex emits dart counts and sigmaZ is undirected-edge, add quad_edge_of_dart_counts
= dartQuad/2 conversion, do NOT mix); #3 final nuK bridge exactly 25 sigma_final <= nuK
via ONE lemma final_sigma_to_nuK_of_switch (never adjust constants inside telescope);
#4 put coreSigId/coreEnv/coreChecked INSIDE CompletionFootprint (avoid dependent
accessors); #5 only terminalPrefix needs the distance bridge (SwitchedWitnessPath +
badEdge_ell_ge_five), constructor-blind telescope. CompletionTrace carries
final_sigma_to_nuK as a FIELD (generated traces discharge it via the once-proven
switch lemma). CoreSignature bridge: rho_eq_coreDictionary via checked_dictionary_eq;
trace-level rhoSum_eq_coreChargeSum => telescope_coreSignatures (THE theorem CD bank
assembly consumes). Public API lists per file; implementation order 1-10.
## IMPLEMENTED UPDATE (same tick): CDCore.lean extended EXIT 0 — ExchangeQuad
{eB_XS..eM_XO, q, rho, q_eq (SIGN pinned), rho_eq}, ExchangeQuad.toOpArith bridge,
ExchangeQuad.rho_nonneg, foldl_rho + rhoSum_eq_foldl (generated-trace compat).
Remaining CD per design: sigmaZ/CDState/CompletionFootprint (graph counts), the five
constructors + legality, CoreSignature env wiring, CompletionTrace + checkChain decide.
