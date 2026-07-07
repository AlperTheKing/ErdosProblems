# AGGREGATION-COMPLETENESS DESIGN (GPT-Pro MAIN, 2026-07-07, 16811c in-thread) — closes audit gap #1

MAIN's design for the #1 gap. INDEPENDENTLY CONFIRMS Claude's GammaChargeGraft approach (additive module,
gammaUpper_from_chargeCertV2 route, drop the unsatisfiable totalRowSum route). Adds the missing cert-existence piece.

## Correct route (verbatim head)
NOT `Σ rowSum <= N^2` from per-row GERSH (structurally false at the extremal scale). Instead:
  all-row GERSH  +  checked reserve residual nonnegativity  +  checked LengthSurplusChargeCertV2 over ResidualFormulas F
  -> GammaAggregation.gammaUpper_from_chargeCertV2  -> Γ <= N².

## Module structure
- NEW module `CertGraphGammaCharge.lean` (does NOT edit CertGraph; final assembly imports it instead of the old
  active theorem). [= Claude's Erdos23Delta0/GammaChargeGraft.lean, already BUILT green+axiom-clean.]
- "1. Do not use the old route gammaBetaProvider_of_rowDB" (CONFIRMS the audit).
- "2. New provider: checked charge route" `namespace CertGraphGammaCharge` [= gammaBetaProvider_of_chargeCert, DONE].

## 2.1 Reserve token-bank certificate (THE NEW / crux piece)
  structure ReserveTokenCert ...
  structure ReserveBankCert { tokens : Array ReserveTokenCert }
  def reserveResidualNFOfRowDB (gd) (rowDB) : NF   -- COMPILED structural token-bank residual for this good cut/rowDB
The reserve residual is NOT stored/supplied per-instance; it is a COMPILED STRUCTURAL FUNCTION of the good cut,
appended to ResidualFormulas as the extra residual source. Its NONNEGATIVITY must be PROVEN (a theorem of code) —
this is the extra nonneg term that row-GERSH slacks alone do NOT provide (slacks give only Γ <= N(N+η)).
"If the actual types are not named GammaData and RowDB, use the exact types already in gammaBetaProvider_of_rowDB."

## STATUS / what remains
- Claude's GammaChargeGraft.gammaBetaProvider_of_chargeCert already provides the provider skeleton (green, axiom-clean).
- REMAINING crux = build `reserveResidualNFOfRowDB` + PROVE its nonnegativity structurally, and show the resulting
  LengthSurplusChargeCertV2 passes checkLengthSurplusChargeCertV2 for every good cut. That nonneg proof is the open
  research core of gap #1 (the "bank-reserve" the memory flagged). Full 16.8k detail in MAIN thread — extract when building.
- CROSS-CHECK: SIBLING was tasked with the same theorem in math prose (may be depleted per user 2026-07-07).

## RESERVE-NONNEG VERDICT (MAIN, 2026-07-07, 12394c) — gap #1 reduces to ONE named open obligation
MAIN HONESTLY DECLINES TO SORRY: "the unconditional reserveResidual_nonneg cannot be produced from the current
green API alone; it is exactly the remaining mathematical/combinatorial obligation." So gap #1 (aggregation Γ<=N²)
reduces to ONE precise named lemma:
  theorem reserveResidual_nonneg_core : 0 <= NF.eval env (reserveResidualNFOfRowDB rowDB)   (under good-cut hyps)
where reserveResidualNFOfRowDB rowDB = the COMPILED token-bank balance (sumNF of per-token residuals), each token
balance structurally nonneg under the good-cut hypotheses (Γ-minimal B-connected max cut).
Charge identity the checkEq verifies internally:
  25*eta - Σ_f (ell(f)^2 - 25) = Σ_realrows a_r*rowResidual_r + a_reserve*reserveResidualNFOfRowDB + Σ_cone b_j*coneResidual_j   (all coeffs >= 0)
WHY the reserve is essential: row-GERSH residuals ALONE give only Γ <= N(N+η) (N²-Γ >= -Nη, too weak); the nonneg
reserve residual supplies the extra ~Nη "bank" that upgrades to Γ <= N² (N²-Γ >= 0). This is EXACTLY the bank-reserve
the memory flagged as the deepest open node ([[erdos23-gersh-aggregation-completeness]]).
STATUS: GammaChargeGraft provides the satisfiable STRUCTURE; reserveResidual_nonneg_core is the single remaining
open MATH obligation for gap #1 - genuinely hard (known-open), NOT plumbing, NOT sorry-able. The honest Lean form is
a NAMED hypothesis/obligation isolated as the non-fake gate, never a sorry.

## DECISIVE GAP-#1 RECONCILIATION (Claude audit, 2026-07-07) — reserve-nonneg = the OPEN aggregation core (CV/LRS)
Verified against problems/23/writeup/LOAD_PSC_COMPONENT_CRUX.md + memory erdos23-loadpsc-firstmoment-target:
- MAIN's reserveResidual_nonneg_core (upgrade Γ<=N(N+η) to Γ<=N²) IS the aggregation step β<=N²/25 <= LRS(ΣT²<=L·Γ) <= (CV) Σ_C T²<=L·Σ_C T. MAIN was CORRECT it is genuinely open (not plumbing).
- CRUX FILE: (CV) is OPEN — all 4 attack angles proof_complete=false; "same odd-girth global anti-concentration hardness as the original ROWSUM problem"; C5-colorable subcase PROVEN, non-C5 residual = open core, "no known proof in the literature (best published N²/23.5, Balogh-Clemen-Lidicky)". => the aggregation may be CONJECTURE-HARD.
- THE ONE HOPE (memory 2026-07-01 sharpening, line 26): CV <=> ℓ^T(L·I - O_C)ℓ >= 0; Gershgorin rowsum_f(O_C)=ROWSUM(f)<=L => ρ(O_C)<=L => L·I-O_C PSD => CV. IF this reduction is AIRTIGHT (rowsum(O_C)=ROWSUM exactly, cross-component overlaps vanish, O_C symmetric nonneg), then CV/reserve FOLLOWS from per-row ROWSUM<=L (which the 108 charts + Branch-A/B prove) — gap #1 becomes FORMALIZE-GERSHGORIN (hard-but-bounded, needs Mathlib PSD over Q/R), NOT open math.
- DECISIVE QUESTION for MAIN (next retask after its current LRS reply): is the Gershgorin CV<=ROWSUM<=L reduction airtight? If yes, reserveResidual_nonneg_core is PROVABLE from the charts' per-row bounds via Gershgorin, and gap #1 is closeable. If the rowsum(O_C)=ROWSUM identity leaks or O_C isn't PSD-amenable, gap #1 = the deep anti-concentration core (conjecture-hard).
- HONEST IMPLICATION: gap #1 is NOT "one quick lemma"; it is either (a) formalize-Gershgorin-from-charts, or (b) a conjecture-hard aggregation. This is the true crux of whether δ=0 is close or genuinely open. P(Lean-complete) stays ~30-40, gated on this reconciliation.

## GAP-#1 REDUCED TO A CONCRETE SWITCHING LEMMA (MAIN, 2026-07-07, 13550c) — better than conjecture-hard
MAIN refuted the easy routes (per-row GERSH sums to m(N+eta) NOT N^2; LRS slack is -Neta short) and REDUCED gap #1 to:
  TerminalCageReserve Lemma: for a canonical terminal cage C of a B-connected Gamma-minimal max cut (tri-free),
    Gamma_C <= n_C^2  (equiv. Sum_{e in M_C}(ell^2-25) <= 25(n_C^2/25 - |M_C|)). Summed over cages => Gamma <= N^2.
  Reduces (Gamma-minimality contradiction: minimal positive-debt cage has sigma=0) to the HARD LOCAL sublemma:
  ZeroSlackNonBalancedSwitch Lemma: if C is a minimal positive-debt terminal cage and sigma(C)=0, the canonical
  switch of its terminal side gives another B-connected max cut with strictly SMALLER Gamma. Requires 3 exact facts:
    (1) max-cut preservation: sigma(C)=0 => switch preserves cut size;
    (2) B-connectivity preservation: switched cut graph still connected;
    (3) SQUARE-LENGTH DECREASE: Gamma(switched) - Gamma(B) < 0.
KEY: item (3) is the CAP-side "Core Recut" square-length comparison (L^2+(L+2)^2 -> L^2) which memory
[[erdos23-surplus-touch-single-atom]] records as PROVEN + exact-verified (GPT-Pro thread 6a436806; gates
_l5forcing_gate/_rex_theta_mine/_stretched_test). If ZeroSlackNonBalancedSwitch item 3 = Core Recut, gap #1 CLOSES
via proven machinery. VERIFICATION TARGET (mine): exact-gate square-length decrease on census/two-lane minimal-
positive-debt sigma=0 cages before trusting. RETASK MAIN: connect the 3 sub-facts to the proven CAP-side recut/theta
switching lemmas; if they match, gap #1 is provable, not open.
STATUS shift: gap #1 goes from "vague anti-concentration, no lit proof" to "3 concrete switching sub-facts, item 3
plausibly = proven Core Recut." More hopeful but UNVERIFIED - the connection must be exact-checked.

## CAVEAT on the Core-Recut connection (Claude audit of erdos23-surplus-touch-single-atom, 2026-07-07)
Before trusting MAIN's "gap#1 item3 = proven Core Recut": the CAP-side Core Recut (L^2+(L+2)^2->L^2) is:
 (a) PER-ROW level (the 5/7-core recut used for L=5-FORCING, i.e. proving no L>=7 deficient CAP sits on a gamma-min
     cut) - NOT an aggregation-level terminal-CAGE switch. MAIN's ZeroSlackNonBalancedSwitch is aggregation (Gamma_C<=n_C^2
     over a whole cage of many bad edges). LEVEL MISMATCH - must verify the cage-switch is core-recut-equivalent or a
     strict generalization (larger cages, multiple bad edges).
 (b) PROSE-ONLY, NOT Lean-proven; and L=5-forcing had a REMAINING piece (Shared-Corridor Hit for ARBITRARY L>=7).
 (c) From the 2026-06-30 CAP/surplus-touch route that the current 108-chart/GERSH program SUPERSEDED.
=> MAIN's "closes via proven machinery" is OPTIMISTIC. VERIFY when mapping lands: (1) is the cage-switch the SAME square
-length comparison as Core Recut or a generalization? (2) is the Core Recut prose actually rigorous + does it cover
arbitrary cage size? (3) does the per-row->aggregation level jump introduce new obligations? Only if all clear does gap#1
close. Honest: gap#1 reduced to a CONCRETE lemma (good) but closure NOT established; P(Lean) unchanged ~30-40 pending this.

## GAP-#1 FINAL CHARACTERIZATION (MAIN mapping, 2026-07-07, 12854c) — reduces to ONE completed-switch assembly lemma
MAIN honestly confirmed the level-jump (my caveat correct). State of the 3 ZeroSlackNonBalancedSwitch sub-facts:
 - item 1 (max-cut preservation): PROVEN GENERALLY (not just single-atom). Universal switch identity |B^U|-|B| = -sigma(U);
   sigma(U)=0 => |B^U|=|B| => B^U is a max cut. No CAP classification needed.
 - item 2 (B-connectivity preservation): proven for ONE boundary-compatible CAP atom; multi-atom cage needs a
   completed-switch CONNECTIVITY assembly lemma.
 - item 3 (Gamma decrease): EXACTLY Core Recut L^2+(L+2)^2->L^2 for ONE surplus-touch CAP atom [PROVEN single-atom];
   multi-atom cage needs a completed-switch GAMMA-DROP assembly lemma.
THE PRECISE RESIDUAL OPEN OBLIGATION (gap #1 = this): "Does every minimal-positive-debt zero-slack terminal cage
admit a completed CAP switch whose active atoms are K2-disjoint, boundary-compatible, and whose local Core Recut
drops ADD WITHOUT INTERFERENCE (net Gamma drop + connectivity preserved)?" If in the CompletedSwitchCert /
surplus-touch package => gap #1 closes; else it is the residual open obligation.
ASSESSMENT (Claude): the sign-atom K2-support-component decomposition (deficient switch -> K2-disjoint type-A odd-cycle
baggage / type-B 5/7 core; R_full=R_local+(N-|Vcomp|)T) EXISTS in the package but was for the SIGN atom, NOT the
Gamma-drop assembly. So the completed-switch Gamma-drop + connectivity assembly is a NEW multi-atom obligation, NOT
obviously already proven. Gap #1 = this assembly lemma. VERIFY: exact-gate multi-atom cage Core-Recut-drop non-
interference on census. P(Lean) unchanged ~30-40 (precise but unproven multi-atom assembly).

## GAP-#1 DECISIVE GATE (MAIN full reply, 2026-07-07, 12854c) — MultiAtomCoreRecutGammaDrop
MAIN completed the assembly analysis. The 3 sub-facts:
 - item 1 max-cut preservation: PROVEN GENERAL (|B^U|-|B|=-sigma(U); sigma(U)=0 => max cut).
 - item 2 B-connectivity: single-atom proven; multi-atom needs CompletedCageSwitchConnected theorem (or per-instance
   spanning-tree cert: T' inside B^U_C, every T'-edge is a B^U_C cut edge, every vertex incident).
 - item 3 square-length decrease:
     single atom (PROVEN = Core Recut): CoreRecut_K2Disjoint_GammaDrop: Gamma(B^U_atom)-Gamma(B) <= -(L+2)^2 < 0 (strict L>=5).
     MULTI-ATOM (THE GATE): MultiAtomCoreRecutGammaDrop:
        Gamma(B^U_C) - Gamma(B) <= - sum_{alpha in Active(C)} (L_alpha+2)^2,  Active(C) nonempty.
=> This single inequality, if it holds, makes the completed switch strictly Gamma-decreasing => contradicts
   Gamma-minimality => forces S_C <= 25 bank_C => TerminalCageReserve (Gamma_C<=n_C^2) => Gamma<=N^2 => gap #1 CLOSES.
MY VERIFICATION TARGET (MAIN explicitly asked): EXACT-GATE MultiAtomCoreRecutGammaDrop on census + two-lane multi-atom
minimal-positive-debt zero-slack terminal cages, BEFORE trusting the reserve theorem. Build by extending
_defcap_component_mine.py (has build_K2, k2_components, R_full, deficient-switch enumeration) to also compute Gamma(B),
Gamma(B^U_C), and Active(C) atom lengths L_alpha. CAUTION: reconcile MAIN's "terminal cage / completed switch U_C /
Active(C)" terminology with the existing "deficient-cap switch / K2-component" objects FIRST - do not rush a wrong gate.
If the gate holds 0-fail: strong evidence (battery != proof); then MAIN proves it + CompletedCageSwitchConnected => gap#1.
STATUS: gap #1 = MultiAtomCoreRecutGammaDrop + CompletedCageSwitchConnected. Concrete, gateable. P(Lean)~30-40 pending gate+proof.

## GATE RESULT: MultiAtomCoreRecutGammaDrop (Claude exact-gate, 2026-07-07) — essential claim VALIDATED, MAIN's quant bound WRONG
Gate _claude_multiatom_gammadrop_gate.py (extends _defcap_component_mine.py; EXACT Fraction). GLUE core+C5 battery,
36000 deficient-cap (sigma=0 boundary_delta=0, positive-debt psi>0) switches on B-connected max cuts:
 (E) STRICT Gamma DECREASE  Gamma(B^U) < Gamma(B):  36000/36000 PASS (0 fail, 0 dG==0). => the completed switch of
     a deficient cap ALWAYS strictly reduces Gamma => contradicts Gamma-minimality => no deficient cap on the Gamma-min
     cut => TerminalCageReserve (Gamma_C<=n_C^2) => Gamma<=N^2. This is the ESSENTIAL, CORRECT claim, empirically validated.
 (Q) MAIN's QUANTITATIVE bound  dG <= -sum(L_alpha+2)^2:  36000/36000 FAIL. Example g0-10 N=15: actual dG = -24, MAIN's
     rhs = -(5+2)^2 = -49; -24 <= -49 is FALSE. MAIN CONFLATED the LOCAL core-recut drop (-(L+2)^2=-49, the L^2+(L+2)^2->L^2
     local comparison) with the GLOBAL Gamma drop (-24): switching changes OTHER edges' bad/cut status + ell too, partly
     OFFSETTING the local drop. The quantitative bound is WRONG but UNNECESSARY - only strict decrease is needed for the
     Gamma-minimality contradiction.
=> CORRECTED LEMMA for gap #1: "every deficient-cap (sigma=0 positive-debt) terminal-cage switch strictly decreases Gamma"
   (dG < 0), NOT MAIN's -sum(L_alpha+2)^2. battery!=proof: 36000/36000 is strong evidence; MAIN must PROVE strict decrease.
   Multi-atom glue (5,5 / 5,5,5) run pending (bkq0lzzrl) to confirm strict decrease on multi-core cages.

## GATE CENSUS CONFIRM + EXACT ACCOUNTING (Claude, 2026-07-07) — resolves the 24-vs-49 discrepancy
Census N<=10: 16 deficient-cap switches (all at N=10), (E) STRICT Gamma-decrease 16/16 PASS, dG distribution {-24:16},
|Active| distribution {1:16}. Combined with glue (36000 single + 6800 multi): 42816 switches, strict-decrease 0 fail.
UNIFORM: every deficient-cap switch has exactly 1 active L=5 core and global drop dG = -24.
EXACT ACCOUNTING (resolves the 49-vs-24): dG = -24 = -(L+2)^2 + L^2 = -49 + 25. The completed switch drops the
5/7-core's Gamma contribution by (L+2)^2=49 (Core Recut) BUT creates exactly ONE new length-5 bad edge adding L^2=25,
netting -24. THAT +25 is the "cross"/new-affected-edge term GPT-Pro's R3 (no-cross accounting) ASSUMED AWAY - which is
why the pure (L+2)^2=49 bound over-counts. Correct per-core accounting: dG_core = -(L+2)^2 + (new bad edges)*25 = -24.
=> The right lemma is STRICT DECREASE dG<0, provable as dG = -24k for k active cores (k>=1, active_empty=0 confirmed),
   NOT the falsified >=49 bound. R3 must account for the +25 new-bad-edge cross term. |Active|>=2 did NOT occur in
   census+glue (denser graphs untested), so the multi-atom-assembly worry is currently unexercised.

## GAP-#1 CORRECTED REDUCTION (MAIN, 2026-07-07, 13071c) — 49-bound dropped, matches Claude's gate
MAIN ACCEPTED the gate correction: "Yes. The 49-bound must be dropped for the completed terminal-shadow flip. It was
the bound for the partial Core Recut atom, not the full switch." Correct per-core accounting (the +25 = new born bad edge
my gate found): drop = 5^2+7^2-5^2-5^2 = 49-25 = 24 (old 5/7 core -> two length-5 edges). CORRECTED ASSEMBLY TARGET:
  Gamma(B) - Gamma(B^U)  >=  24 * activeB57Count(C)  > 0   (strict, since activeB57Count>=1).
Matches Claude census+glue EXACTLY: dG=-24, |Active|=1 => 24*1=24, 42816/42816. (|Active|>=2 untested - would give 24k.)
PRECISE U_C: Door_B(C) = B-door edges of the cage; delta_G(U_C) = graph edges with one endpoint in U_C; under the switch
old bad edges crossing U_C -> cut, old cut edges crossing -> bad, noncrossing unchanged. The exact global Gamma-drop
identity for this U_C "is exact. It is the right thing to gate first." Strictness source = the checker gate
isTerminalCage & isMinimalPositiveDebt & sigma=0 & isDeficientCap => 0 < activeB57Count(C).
=> gap #1 reduction is now CORRECT + gate-consistent. REMAINING = PROVE: (i) the exact identity Gamma(B)-Gamma(B^U) =
24*activeB57Count (the no-cross accounting R1/R3 with the +25 included); (ii) R2 activeB57Count>=1; (iii) R4 connectivity.
Claude gate confirms (i) for |Active|=1 (all 42816); extend to denser |Active|>=2 families + census N=11.

## GAP-#1 PROOF DECOMPOSITION (MAIN, 2026-07-07, 13477c) — reduces to TS-CTI (gate-able) + R2 + R4
MAIN gave the proof structure for the exact identity Gamma(B)-Gamma(B^U_C) = 24*activeB57Count(C):
U_C def: Door_B(C)=B-edges as terminal-shadow doors; H_C=(V_C, B[V_C]\Door_B(C)); B^U=B (symdiff) delta_G(U_C).
CRUX = TS-CTI (TerminalShadowCrossTermIsolation), precisely stated: for a min-positive-debt sigma=0 deficient terminal
cage, there are bijections old7, born5, stable5 : A(C) -> edges with (1) M cap delta(U_C) = {old7(a)} [ell_B=7],
(2) B cap delta(U_C) = {born5(a)} [ell_{B^U}=5], (3) stable5(a) has ell=5 both sides, (4) every non-crossing old bad
edge keeps its ell, (5) NO other born bad edge, no other old bad edge killed. => per core: -7^2(old7 leaves M) +5^2
(born5 enters) = -49+25 = -24. Net dG = -24*|A(C)|. [This is EXACT-GATEABLE structurally; my existing gate already
confirms the NET dG=-24*count 0-fail on census N<=11 + glue = 37142 switches.]
R2 (activeB57Count>=1): the CAP-side classification (deficient cap => nested 5/7 core via theta + odd-girth>=5).
R4 (connectivity): MAIN proved DoorQuotientConnected (B^U_C connected iff quotient Q_C connected) => R4 reduces to
"Q_C connected"; for ONE active core this follows from the proven CAP boundary-compat blockers. Since |Active|=1
UNIFORMLY (my gate, census N<=11 + glue), the single-core R4 case is all that occurs.
STATUS: gap #1 = {TS-CTI [stated precisely, net gate-confirmed, PROOF via theta pending] + R2 [CAP classification,
likely proven prose] + R4 [single-core, from CAP boundary-compat]}. TS-CTI is the crux to PROVE + structurally gate.

## TS-CTI STRUCTURAL GATE — switch-set nuance (Claude, 2026-07-07)
Built the TS-CTI structural gate (verify killed=old7[ell7], born=born5[ell5], stable ell-invariant). On glue-C5 36000:
net dG=-24 + exact-identity PASS as before, BUT TS-CTI structural CHECK: killed=2, born=2 per k=1 core (NOT killed=1/
born=1). Reason: my gate flips the FULL deficient-cap terminal-shadow Sset, which kills BOTH core edges (5 and 7,
5^2+7^2=74) and births TWO length-5 edges (2*25=50), net -24. GPT-Pro's U_C=Door_B is a DIFFERENT, more surgical
switch (kill 7 only, KEEP the 5 as stable5, birth ONE 5), also net -24. So Sset != Door_B U_C; both are sigma=0 and
both strictly decrease Gamma by 24. stable_ell_changed=0 (ell-locality clause c holds for MY switch too - no non-crossing
bad edge changed ell). KEY IMPLICATION: the net strict-decrease is SWITCH-ROBUST => the SUFFICIENT lemma for the
Gamma-minimality contradiction is just "SOME sigma=0 switch strictly decreases Gamma" (my terminal-shadow flip, net -24,
validated 37142/0), which is WEAKER/EASIER than TS-CTI's exact Door_B structural identity. To structurally gate TS-CTI
itself I must implement Door_B(C) exactly. Tell MAIN: net strict-decrease suffices + is switch-robust; TS-CTI is a
stronger-than-necessary route (clean exact identity, but the contradiction only needs net<0 of any sigma=0 switch).

## SINGLE-CORE TS-CTI PROOF (MAIN, 2026-07-07, 12533c) — reduces to TypeB57Theta (CAP) + R2 exactly-1
MAIN proved the SINGLE-CORE case (|A(C)|=1). Precise U_C: H_C=(V_C, B[V_C]\Door_B(C)); r = terminal-shadow root of the
unique active core; U_C = connected component of r in H_C; B^U = B (symdiff) delta_G(U_C). Single-core TS-CTI reduces to:
 (i) ONE-DOOR LOCALITY [MAIN PROVED, clean]: a shortest path between two same-side vertices of a one-edge boundary
     cannot use that boundary edge => distances computed inside the unchanged side => ell-locality (clause c).
     [Claude gate confirms: stable_ell_changed=0 on 36000 - clause c holds empirically.]
 (ii) TypeB57Theta (H1-H3): delta_B(U_C)={born5}, old7 in delta_M(U_C), ell_B(old7)=7; maxcut forces delta_M(U_C)={old7}.
     MAIN: "if already proven in the CAP package, the single-core TS-CTI proof is closed."
REMAINING for gap #1 single-core closure:
 (a) confirm TypeB57Theta (H1-H3) ARE proven CAP-package lemmas (cite exact names) or prove them.
 (b) R2: prove activeB57Count = EXACTLY 1 for every min-positive-debt sigma=0 deficient terminal cage (classification:
     deficient cap => EXACTLY one nested 5/7 core). Claude gate: |Active|=1 on all 37142 census N<=11 + glue - if provable,
     MULTI-CORE is moot and single-core TS-CTI closes gap #1.
 (c) ell definition: graph boundary delta_G(U_C)={born5,old7} is 2 edges, but ell-changes=0. Clarify: is ell(f) the
     shortest odd cycle through f in the FIXED graph G (cut-invariant => clause c TRIVIAL), or cut-dependent (needs
     one-door locality)? Claude gate suggests near-cut-invariance.
 (d) R4 single-core connectivity: MAIN reduced to Q_C connected via CAP boundary-compat [prev msg].
=> gap #1 single-core = {one-door locality DONE + TypeB57Theta[CAP?] + R2 exactly-1 + R4[CAP]}. Close to done IF (a),(b) hold.

## ell DEFINITION RESOLVED (Claude, 2026-07-07) — ell is cut-dependent; one-door locality is correct+necessary
Read geos() (AUDIT_*.py): geos(adj,side,s,t) does BFS using ONLY CUT edges (side[u]!=side[v]). So for a bad edge
f=(s,t) [monochromatic], ell[f] = (shortest cut-path s->t) + f = shortest odd cycle through f USING CUT EDGES. =>
ell is CUT-DEPENDENT (not a graph invariant). Switching U flips cut edges => cut-paths change => ell CAN change.
Therefore TS-CTI clause (c) (ell-locality) is GENUINELY NON-TRIVIAL, and MAIN's ONE-DOOR LOCALITY is the CORRECT +
NECESSARY tool: a shortest cut-path between two same-side vertices cannot use a boundary cut-edge, so distances
inside the unchanged induced side are preserved. Claude gate confirms clause (c) HOLDS: stable_ell_changed=0 on
36000 - a non-trivial validation of MAIN's clause-(c) proof (NOT free, as I had briefly hypothesized). => MAIN's
single-core TS-CTI clause-(c) proof approach is SOUND + gate-confirmed. My earlier "is ell cut-invariant?" question
is RESOLVED (no): one-door locality is needed. Remaining single-core gaps: TypeB57Theta (H1-H3, = CAP package?) + R2
exactly-1. (This clarification supersedes the ell-invariance line in the SINGLE-CORE TS-CTI PROOF note above.)

## GAP-#1 CLOSURE: REDUCES TO CAP PACKAGE (MAIN, 2026-07-07, 17691c) — major consolidation
MAIN closed the single-core gap#1 chain by mapping EVERY TypeB57Theta clause to a named CAP-package lemma (the
2026-06-30 surplus-touch route, [[erdos23-surplus-touch-single-atom]]):
  S1 four-door theta->Ferrers  => H1: delta_B(U_alpha)={born5} (single B-door)
  boundary-compat blockers     => the door is the ONLY cut-boundary edge
  S2 annulus-increment=2       => paired core lengths L, L+2
  L=5-forcing / Shared-Corridor Hit = S2 => forces L=5 (paired 5,7)
  nested 5/7 core classification => old7 = killed crossing bad edge, ell_B(old7)=7
  Core Recut / glue-C5 corridor => length-4 B^U path between born5 endpoints
  triangle-free                => rules out length-2 path, so ell_{B^U}(born5)=5
  + max-cutness => uniqueness of crossing bad edge (NOT a CAP lemma, follows from maxcut).
Bridge: CAP_TypeB57ThetaGate_sound (S1_Ferrers + boundary_compat + S2 + L5forcing + nested + CoreRecut + trifree => TypeB57Theta).
R2 SIMPLIFICATION: only EXISTENCE (>=1 active core) needed, NOT exactly-one - switch ONE core at a time => single-core
switch => contradiction; multi-core no-cross theorem UNNEEDED. Chain: negative_reserve_yields_minPositive_sigma0_deficient_cage
=> >=1 active 5/7 core => single-core Door_B switch [sigma=0 + one-door-locality(ell) + TypeB57Theta] => Gamma drops 24 =>
contradicts Gamma-minimality => reserve>=0 => TerminalCageReserve => Gamma<=N^2 => gap#1. ell CONFIRMED cut-dependent (matches my geos read).
HONEST STATUS: gap#1 math REDUCES CLEANLY to the CAP package + new PROVED pieces (one-door locality, TS-CTI single-core,
reserve chain). BUT the CAP lemmas (S1,S2,L=5-forcing/Shared-Corridor-Hit,boundary-compat,Core Recut) are PROSE-ONLY
(2026-06-30), NOT Lean, and L=5-forcing/Shared-Corridor-Hit had a REMAINING piece (arbitrary L>=7) per memory - MUST
re-verify its rigor. So gap#1 = "reduce to CAP work + verify CAP rigor + Lean-formalize", NOT new open research. NEXT:
(1) re-audit CAP lemma rigor (esp Shared-Corridor Hit L>=7); (2) Lean-formalize the chain (CAP gates + new pieces).

## GAP-#1 HONEST CAP-RIGOR VERDICT (MAIN, 2026-07-07, 15980c) — NOT CLOSED; open geometric lemma remains
MAIN honest: "The CAP package is NOT yet a fully closed Lean-ready proof of 'active core is always 5/7.' Shared-Corridor
Hit / L=5-forcing for arbitrary L>=7 remains THE decisive open geometric lemma unless you replace the exact-24 route by
the strict-drop route." TWO routes for gap #1:
 (A) EXACT-24 route: switch old{L,L+2}->new{L,L}... wait for L=5 gives -24; REQUIRES L=5-forcing (rule out L>=7). NOT
     CLOSED - Shared-Corridor Hit L>=7 is OPEN.
 (B) STRICT-DECREASE route: does NOT require L=5-forcing. For ANY active type-B L/(L+2) core, the switch old{L,L+2}->new
     {L,L} drops Gamma by (L+2)^2 - L^2 = 4L+4 > 0 (strict, all L). PROVIDED the CAP gate gives a one-door type-B
     L/(L+2) core for ARBITRARY odd L>=5 (variable-L TypeBThetaGate) + active core existence. Then strict decrease =>
     Gamma-min contradiction => reserve>=0 => gap #1. "Gap #1 should NOT depend on proving L=5 unless you insist on exact 24."
=> HONEST STATUS: gap #1 is NOT CLOSED. Reduces to an OPEN CAP obligation, EITHER (A) Shared-Corridor Hit L>=7 [the
   flagged open geometric atom], OR (B) variable-L TypeBThetaGate (one-door type-B L/(L+2) core for arbitrary L>=5) +
   core existence. Route (B) AVOIDS the harder L=5-forcing (promising) but needs the variable-L theta structure proven.
   CORRECTS the earlier "materially de-risked" framing: an open geometric lemma remains either way. My CAP re-audit
   (_l5forcing_gate + _stretched_test) battery-CONFIRMS L=5-forcing on canonical L=5..15 but that is annotation, not the
   arbitrary-L>=7 PROOF. NEXT: pursue route (B) - is variable-L TypeBThetaGate provable from S1/S2 (theta -> Ferrers works
   for general L)? + core existence? This is now the single open piece for gap #1.

## GAP-#1 ROUTE-B PRECISE (MAIN, 2026-07-07, 14145c) — WeakTypeBThetaGate, gate-able on stretched cores
Route (B) avoids L=5-forcing entirely. It needs only the WEAK variable-L gate (weaker than TS-CTI - inequality not equality, no L=5):
  WeakTypeBThetaGate(G,B,U,oldHi,bornLo,L): L odd >=5;
    H1.  delta_B(U) = {bornLo}                 (cut-boundary is exactly one born edge)
    H2a. oldHi is a bad edge and crosses U
    H3a. ell_B(oldHi) = L+2
    H3b. in B^U, bornLo is bad and ell_{B^U}(bornLo) <= L   (INEQUALITY - not =L, and NO L=5 needed)
  => maxcut gives delta_M(U)={oldHi} => drop >= (L+2)^2 - L^2 = 4L+4 > 0 => strict decrease.
MAIN: "If your stretched L=5,7,9,11 gates confirm H1-H3 for each L, that directly supports the wrapper
CAP_WeakTypeBThetaGate_LUniform." The ONLY possible failure points (the 3 real blockers for route B):
  NoSideDoorForLongAnnulus ; TypeBHighEdgeGeodesicExact_uniform ; CoreRecutBornPath_uniform.
=> MY DECISIVE TASK: build a gate checking WeakTypeBThetaGate (H1,H2a,H3a,H3b) on the stretched L/(L+2) cores
L=5,7,9,11 (from _l5forcing_gate.py). If it PASSES for each L => route B empirically supported => gap#1 reduces to
proving CAP_WeakTypeBThetaGate_LUniform (which S1/S2 theta->Ferrers should give L-uniformly). If it FAILS at some L,
the failure = one of the 3 named blockers = the true residual open lemma.

## ROUTE-B EMPIRICALLY VALIDATED + H1 CORRECTED (Claude gate, 2026-07-07)
Built _claude_weaktypebtheta_gate.py (searches switch sets U on the stretched L/(L+2) cores). FIRST run with MAIN's
ONE-DOOR H1 (delta_B(U)={bornLo}, single born): NO witness for ANY L (incl L=5). Since L=5 provably works + my earlier
TS-CTI gate found the natural switch is TWO-door (kill 2, born 2), MAIN's one-door H1 is TOO STRONG (same error class as
the falsified 49-bound). CORRECTED condition (only core edges killed deltaM subset {f0,f1}, born ell<=L, drop>0) =>
WITNESS for EACH L=5,7,9,11 with UNIFORM switch U={s,u,a1}={0,1,5}: kills both core edges f0(L),f1(L+2), births TWO
ell-L edges, drop = (L^2+(L+2)^2)-(L^2+L^2) = (L+2)^2-L^2 = 4L+4 > 0. Exact: L=5 drop24, L=7 drop32, L=9 drop40, L=11 drop48.
=> ROUTE B is EMPIRICALLY VALIDATED L-uniformly on the canonical stretched cores (0-fail L=5..11): the variable-L
TWO-door switch strictly decreases Gamma by 4L+4>0 uniformly, AVOIDING L=5-forcing. gap#1 does NOT need the open
Shared-Corridor-Hit lemma. CAVEATS (battery!=proof): (1) this is the CANONICAL stretch only; the general proof (arbitrary
L/(L+2) core in any deficient cage, U-analog exists + born ell<=L) is still MAIN's structural argument from S1/S2. (2)
MAIN's one-door H1 CORRECTED to two-door here. (3) core-existence + Lean formalization remain. NEXT: MAIN prove the
variable-L TWO-door WeakTypeBThetaGate L-uniformly from S1/S2 theta->Ferrers; then formalize.

## CONVERGENCE: PAIR-DOOR SWITCH (MAIN + Claude gate agree, 2026-07-07) — gap#1 residual = pair-door no-cross lemma
MAIN's U-reply INDEPENDENTLY converged with Claude's gate: the switch is a PAIR-DOOR (two-door) switch, NOT one-door.
MAIN: "Gamma(B^U) < Gamma(B) follows immediately, with exact drop 4L+4 in the isolated core. The earlier one-door
locality proof does NOT apply to this pair-door switch. For a larger ambient graph, exact TS-CTI still needs a
pair-door no-cross / metric-stability lemma, or you keep this as a checked structural gate." Matches Claude
_claude_weaktypebtheta_gate.py exactly (U={s,u,a1}, kills f0(L)+f1(L+2), births two ell-L, drop 4L+4, L=5..11 0-fail).
=> gap#1 RESIDUAL (single open geometric lemma): the PAIR-DOOR NO-CROSS / METRIC-STABILITY lemma for the general
   ambient graph: under the pair-door core switch, (i) NO other bad edge is killed/born (no-cross), (ii) NO non-crossing
   bad edge's ell changes (metric-stability). Claude gates ALREADY battery-validate both: stable_ell_changed=0 on 36000
   (metric-stability) + deltaM subset {f0,f1} witnesses (no-cross) on canonical cores. GENERAL PROOF pending (MAIN, from
   S1/S2 + odd-girth>=5). For finite N a checked structural gate suffices; for delta=0 (all N) the GENERAL lemma is needed.
   Then Lean formalization. gap#1 = {pair-door no-cross lemma [battery-validated, general proof pending] + core-existence + Lean}.
