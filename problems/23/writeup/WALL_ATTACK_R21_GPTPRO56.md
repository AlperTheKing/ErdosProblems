# WALL ATTACK — R21: exit (c) — the minimal priced field = ONE allowed-cut key (PricedCutCert);
# routing terms CANCEL exactly; prove-or-break target now finite and irreducible: G_all >= Def_d(P)
# (GPT-5.6 Pro, 2026-07-11, HARVESTED VIA IN-APP BROWSER, ~10 min turnaround)

**[CLAUDE GATE HEADER:**
- **ROUTING-INDEPENDENCE IDENTITY (1)** (strengthens R20b's sign-flip): for ANY checked partial routing ρ,
  R_D2(ρ) + R_cap(ρ) − (M_ρ − Λ_d(X)) = Λ_d(X) − Def_d(P). ALL ρ-dependent terms cancel ⟹ changing the
  transfer matching, terminal assignment, or routing CANNOT improve the required margin. The only datum
  that matters is an actual cut X and its dual price. [ALGEBRA: immediate from R20b's decomposition (4)/(5)
  rearranged — M − Λ = Def + R_D2 + R_cap − cutGap... consistent ✓; compile will certify.]
- **MINIMAL NEW FIELD: `structure PricedCutCert (Cut) where cut : Cut`** — carries NO claimed reserve, NO
  cut value, NO coefficients, NO inequality, NO routing, NO allowedness proof. Exact Boolean checker
  recomputes everything: `checkPricedCut I d L P cert = I.allowedCutB cert.cut && decide
  (I.scaledDeficiency d L P ≤ I.cutGap d cert.cut)`; r := cutGap − Def recomputed, never supplied.
  Transfer-facing variant checkPricedBoundary (tests M − cutGap ≤ R_D2 + R_cap) equivalent by (1), useful
  only for reporting the first failed signed term; the direct checker is canonical.
- **SOUNDNESS + CONTRADICTION (full Lean proofs given, compile-ready against BankedWallLP + small defs)**:
  checkPricedCut_sound (accept ⟹ AllowedCut ∧ ∃ r ≥ 0, cutGap = scaledDeficiency + r; proof =
  and_eq_true/of_decide_eq_true/sub_nonneg/ring) and **noCheckedDual_of_pricedCut** (Def > 0 + accept ⟹
  False via hd.cutGap_nonpos cert.cut — the violated D1 row IS the supplied cut's own row, no uncrossing,
  no summed surrogate; linarith). Needs API additions: allowedCutB (+_sound), scaledDeficiency, cutGap,
  Checked.cutGap_nonpos accessor.
- **EXACT FINITE CONSTRUCTOR** findPricedCut: enumerate allowed cuts (Cut finite), exact-rational argmax of
  score(X) = Λ_d(X) − Def_d(P); return cert iff score(X*) ≥ 0; a FAILED search returns the strongest
  falsifier (max-gap witness). No LP, no floats, no tolerance.
- **ATLAS CANDIDATE MODE** (graph-derived candidates first): corner cuts, producer rows, owner/petal
  shores, actual trace switch masks, symmetric differences thereof. Trichotomy: G_atlas ≥ 0 ⟹ field
  produced immediately; G_atlas < 0 ≤ G_all ⟹ atlas incomplete AS A CONSTRUCTOR but W3 conclusion true;
  **G_all < 0 ⟹ the W3 cut conclusion is FALSE on that fully checked instance** — decisive falsifier
  ε = Def_d(P) − max Λ_d > 0 (4), full record spec (cage hash, dual, shore, Def, X*, α/β/γ totals, ε; plus
  transfer diagnostics ρ, M, R_D2, R_cap, boundaryDebt − availableReserve = ε).
- **VERBATIM BOTTOM LINE**: "Nothing purely unweighted can replace this check... Equation (1) additionally
  shows that no rearrangement of transfer routing can repair the sign. So the exact remaining graph-side
  prove-or-break target is now finite and irreducible: max_{X allowed} Λ_d(X) ≥ Def_d(P). The operational
  field proving it is one checked allowed-cut key."

## MY RECONCILIATION + NEXT
- THE WALL, final sharpened form: (L1) stage-3 base-pattern matching completeness (sameFirst + commonBad +
  rowCompanion, prune only if residual) — 311 gate DONE (base-only false, rowCompanion repairs); (L2)
  **G_all ≥ Def_d(P) on every canonical instance** — per-instance finite exact gate, cut-key certificate,
  compiled contradiction consumer. Both layers now have COMPLETE certificate architectures with soundness
  theorems; the remaining research content is whether canonical cages always pass, and if so WHY (the
  structural theorem the paper needs).
- NEXT (me): (i) compile PricedCutCert + checkPricedCut + checkPricedCut_sound + noCheckedDual_of_pricedCut
  + the decomposition theorems into BankedWallLP surface (or hand to Codex lane with exact statements —
  they are self-contained); (ii) implement the h_boundary gate (Def vs G_atlas vs G_all) — needs concrete
  wall-LP instances from real cages: the allowed-cut family + duals come from the compiled W3 skeleton;
  fixtures 167/175/311/3892; (iii) staged 4-pattern matching gate; (iv) R22 retask AFTER gates produce
  data (falsifier-first: no more theory until the fixtures speak).**]
