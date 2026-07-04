# LOOP_STATE.md — volatile loop state (UPDATE EVERY TICK; the /loop text never changes)
# Last update: 2026-07-04T19:20Z (P(math)~87, P(Lean)~82)

## MAILBOX
- CODEX_TO_CLAUDE.md read marker (bytes): 1629435
- My outbox: coordination/CLAUDE_TO_CODEX.md (append-only)

## GPT-PRO THREADS (thread URLs stable; tab IDs go stale — find or recreate via tabs_context/tabs_create)
- MAIN    (theorem design):   https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550  [last tab 1267096329]
- SIBLING (writeup + second): https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526  [last tab 1267096303]

## IN FLIGHT
- MAIN: floor-buffer theta_max=0 diagnosis (full support? per-row buffers? caps? Markowitz-only k0
  fallback?) + RadialHullCert concrete required form (Mode-B skip). DECISIVE for the chart batch.
- SIBLING: paper section 2.2 per assembly plan ([CERT: id] tags for pending artifacts).
- CODEX: floor-buffer redirect posted (full support + easy-chart k5-9 validation first, then k0
  retry; Markowitz+repair = accepted hard-chart fallback); then feasible near-band batch w/
  per-chart SHA ledger; region-emptiness probes (EmptyRegionCert route for non-feasible regions);
  Mode-A per-chart dominance-free monotonicity sweep; corrected InfCerts; O5-EMIT, O6-EMIT,
  O16/O18-EMIT, O13-EMIT, B0-4 lens gates, SB-1, A1 six cones.

## RETASK QUEUES
- MAIN queue: T=2 corridor cert emission spec detail (O6) if gaps surface; O11 2Door / O13 Seed3
  emission spec refresh if Codex hits ambiguity; per critical paths A-D.
- SIBLING queue: sections 3.2+ (Branch-B cert details), 5.x appendices (cert ledger, validation),
  definitions-table finalization per assembly plan.

## EXTRACTION QUEUE (landed in threads, not yet saved to files)
- sibling 1.1+1.2 (5618c)            -> problems/23/writeup/PAPER_SECTIONS_GPTPRO.md
- sibling 1.3 (7867c)                -> same
- sibling 2.1 (3914c; head captured) -> same
- sibling 3.1 (4541c)                -> same
- sibling assembly plan (19210c)     -> problems/23/writeup/DOCUMENT_ASSEMBLY_PLAN_GPTPRO.md
- sibling E1-E7 errata (9738c)       -> problems/23/writeup/BRANCH_A_ERRATA_GPTPRO.md

## LEAN (14 files green; build: cd E:\Projects\ErdosProblems\formal-conjectures; lake env lean <abs path>)
- Done: Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert (NF+checkEq+PosCert+ConeCert), Bank0Algebra, CertGraph (L0-L3 + B6 BankBlocks checker:
  checkBankBlock + product/disjointness fact-extraction).
- NEXT: CorridorPartition checker (O1-O5 obligations over lists; additivity already proven as
  nu0_append) -> CrossCap -> ClosureTrace -> LensGates -> Seed10/SevenCutCone -> Assembly
  (await main-thread review verdicts on A/B/C before typing Bank0Statement).

## MASTER LEDGER (single source of open obligations)
- WRITEUP_REDTEAM_GPTPRO.md tail: Bank0 B0-B10 + ODL O0-O21 + chain T0-T3 + paths A-D + DoD.
- PROVEN: B0,B7,L7,L8,LemmaA,O1-O3,O8-O10,O12,O15,T0(cond), EQ-ODL1 equality stratum end-to-end.
- DESIGN DONE (specs archived, emission pending): O5 (T=1 REC + verified micro-example),
  O16/O18 (master cubes, 3x11 EQ + 3x13 SIB templates explicit). PROGRAM 100% SPECIFIED.
- CERT-PENDING: B1-B6,B10,O4(O6),O5-EMIT,O11,O13,O14(rung-2 charts),O16-O21-EMIT.  HUNT: O7.
- Certified negative datapoint: EQ-ODL1 restricted F1-F4+B0 Farkas cert exact.
- Full rung-1 cone = 1,755,182 columns (not launched; rung-2 primary).


## TICK NOTES (2026-07-04T10:00Z)
- Assembly plan FINAL (verdicts archived in LEAN_CHECKER_DESIGN_GPTPRO.md tail): RowDBFacts Prop-first; GammaMinimal = BConnected-restricted; flip lemma via indicator sums; 3-layer assembly + providers.
- Lean next: badCount_flip_eq (indicator sums) + sigma_nonneg_of_maxcut derivation in CertGraph.lean; then CorridorPartition checker; Assembly statements per archived plan.
- Extraction queue += sibling 4.1 (~landed). Codex: rung-2 basis-extraction exact replay (B) + 300-chart numeric map (A) in flight; then O5-EMIT, O16/O18-EMIT.
- gersh_Lgt5_of_bankL green (BankL.lean).


## TICK NOTES (2026-07-04T11:15Z)
- O6 T=2 format archived + micro-example hand-verified => EVERY cert-pending node in both ledgers has an emission-ready spec (design queue empty).
- Extraction queue += sibling 4.1 (landed).
- Codex: rung-2 near-band feasible all 3 hard dominants at k=0; inf-band guidance sent (spec par.8 reduced form); basis-extraction replay + 300-chart map in flight.
- Lean next: badCount_flip_eq indicator-sum lemma + sigma_nonneg derivation; then CorridorPartition checker; Assembly statements per archived plan.


## TICK NOTES (2026-07-04T12:25Z)
- Interface canon (12 resolutions) archived + BINDING posted to Codex; O13 Seed3 spec = SAME main reply, offsets ~7900-17359 in window.__au — EXTRACT NEXT TICK (structures C5QuotientData etc.).
- Lean: badCount_flip_eq + sigma_nonneg_of_isMaxCut GREEN (Decision-B core done). Next: CorridorPartition checker; then align existing structures to canon (CompletedSwitchCert, two trace types) as new modules land.
- Codex: modular-rational-reconstruction recipe issued (2686-dim core); inf-band s=0 face INFEASIBLE = spec deviation — RELAY TO MAIN pending (ask corrected leading-homogeneous encoding); numeric map subprocess parallelism approved.
- Main in flight: (this reply done). NEXT RETASK: corrected inf-band encoding question + O13 remainder already in reply. Sibling in flight: appendices 5.1/5.2.
- Commits: fa3a97880.


## TICK NOTES (2026-07-04T13:10Z)
- INF-BAND FIX archived (EQ_HEIGHT_LEMMA tail) + Codex patched: G# = H_G*Lambda^(2-d) lift (bug was s^(2-d) killing linear gens on s=0 face); hard-row priority B0/UA/UB-inf; radial-monotonicity skip criterion. Codex's s=0 infeasibility refuted only the face truncation.
- IN FLIGHT: main = O13 witness/completeness completion; sibling = definitions table (appendices 5.1/5.2 landed 14724c, unextracted).
- EXTRACTION QUEUE grows: appendices 5.1/5.2 (14724c), O13 remainder (window.__au offsets ~7900-17359 — cache may die on tab reload; full text stays in-thread), 4.1, 3.1, 2.1, 1.1-1.3, assembly plan, E1-E7. BATCH SEVERAL NEXT TICK.
- Lean next: CorridorPartition checker + canon alignment (CompletedSwitchCert, two trace types) as new modules.
- Codex: modular replay (2686-dim) TOP + corrected inf-band reruns + numeric map + O5/O6-EMIT queue. Marker 1616087.


## TICK NOTES (2026-07-04T14:30Z)
- O13 classifier spec archived (7 witnesses, completeness enum P4/K13/P2+E/3E, priority order) => LAST fuzzy spec closed. O13-EMIT posted.
- Codex basis-quality ASK ruled: (B) Markowitz/denominator-aware modular pivots + early-exit recon (200-prime cap), (A) one glpsol --exact probe if installed, (C) parallel always.
- IN FLIGHT: main = referee FAQ (defense appendix + gap hunt); sibling = definitions table (appendices 5.1/5.2 landed 14724c unextracted).
- EXTRACTION QUEUE: definitions table (when lands), appendices 5.1/5.2, 4.1, 3.1, 2.1, 1.1-1.3, assembly plan, E1-E7 — BATCH-SAVE next tick to PAPER_SECTIONS_GPTPRO.md etc.
- Lean next: CorridorPartition checker + canon alignment. Marker 1618290.


## TICK NOTES (2026-07-04T15:10Z)
- Referee FAQ landed (32 objections; index archived; verbatim extraction at assembly time).
- Exact-replay heights persist across ALL bases (lex-small/lex-large/family/sparse-row: partial ~1790/2686 at 1080 bits) => consult sent to main: is high height by-design + interior small-denominator feasible-point recipe (rounding+repair / analytic center / margin-buffered rounding / coarser multiplier basis). DECISIVE for rung-2.
- IN FLIGHT: main = exact-replay strategy; sibling = definitions table (check + extract next tick).
- LEAN NEXT TICK FIRST: CorridorPartition checker (slid 4 ticks). Then canon alignment.
- Extraction queue unchanged (batch when quiet). Marker 1619911.


## TICK NOTES (2026-07-04T16:15Z)
- FLOOR-BUFFER method archived + full directive to Codex (two-stage BufferLP, safe floor Q>4/theta, exact b>=0 verify, RepairLP fallback; expected 14-17 bit denominators) — replaces ALL vertex/basis extraction.
- Lean: CorridorPartition checker GREEN (pairwiseDisjB + nu0_partition + negative_corridor_of_check) — B2 layer done. 15 modules green. NEXT: CrossCap checker skeleton (canon CompletedSwitchCert + demand/capacity checks) OR canon alignment pass.
- IN FLIGHT: main = radial-monotonicity analysis (formula, chart ranking, skip-cert form, sweep protocol); sibling = definitions table LANDED 27461c (extract at assembly; note in queue).
- Codex: floor-buffer implementation on k=0/B0/near = THE gate; then batch. Marker 1619911 (no new posts last scan).
- FAQ index archived (32 objections). Commits through 55756768a.


## TICK NOTES (2026-07-04T17:25Z)
- **FIRST RUNG-2 CHART EXACTLY CERTIFIED + I reverified independently** (exact_ok=true, 0 neg residuals). Manifest SHA-pinned; 29 Lean shard modules PASS. Batch directive: Markowitz+repair AND floor-buffer, compare on next chart; per-chart ledger artifact requested.
- Radial-monotonicity protocol archived + posted (sweep first, k=5-9 first, k=0/B0 budget full InfCert).
- IN FLIGHT: main = free (radmono done) — RETASK NEXT TICK (queue: first-Codex-artifact adversarial audit when O5/O6 emissions land; or paper section 2.2 Bank0 integration review); sibling = definitions table LANDED 27461c (extract at assembly).
- Lean 15 green. NEXT: CrossCap checker skeleton (canon CompletedSwitchCert + demand/capacity + integer identity).
- Marker 1623735. Commits through 55756768a (this tick's commit next).


## TICK NOTES (2026-07-04T18:15Z)
- Numeric map 108/300 near-band feasible (k5-9 ~15/15 each as ranked; k0/1/2 = 6/2/1); inf-band awaits G# reruns + radmono sweep. Dynamic Markowitz no-go (no 200-prime spend). Codex: floor-buffer vs Markowitz on an easy chart, then batch 108 w/ per-chart SHA ledger.
- Main retasked: O14 ASSEMBLY THEOREM (coverage lemma 10x15x2+stratum, per-chart pullback, final EQ-ODL1 composition, all-or-nothing accounting, Lean shapes).
- Lean: canon CompletedSwitchCert + checkCompletedSwitch + sigma/nuK fact extraction — BUILD IN FLIGHT (bg bvwl8s15n; fix if red next wake).
- Sibling: definitions table landed (extract at assembly); retask queue: paper 2.2/3.2 or idle-fill review.
- Marker 1626385.


## TICK NOTES (2026-07-04T19:25Z)
- O14 ASSEMBLY THEOREM archived (EQ_ODL1_O14_ASSEMBLY_GPTPRO.md): coverage HCover/ChartCover,
  EQODL1CoverCert (300 regions + stratum), region certs direct|skip|empty, SKIP CORRECTION
  (Mode A global-band dominance-free / Mode B radial-hull w/ RadialHullCert; bare dominance
  skips REJECTED), pullback s^11, height-1 -> all heights via h/h^2 scaling + EQ-CERT1,
  all-or-nothing accounting, full Lean statement shapes (9.1-9.10).
- BLOCKER live: floor-buffer theta_max=0.0 on 3x k0 near targets (reduced negative-support
  columns). Redirect posted (full support, easy-chart validation first); designer consult in
  flight (per-row buffers / caps / Markowitz-only k0 fallback). k0/B0/near stays closed (Markowitz).
- Codex also delivered: Branch-B dictionary-audit Lean v7 PASS (33 modules, 0 forbidden).
- Lean: CrossCap layer (B3) written into CertGraph.lean — CrossCapCert (blueprint fields),
  checkCrossCap (recompute boundaries + capacity ineq), checkCrossCap_ineq (DN*sigma <= nu0),
  crossCap_sound (max-cut contradiction), partition_crossCap_sound (dichotomy consumer edge).
  Build in flight. NEXT after green: ClosureTrace replay module (C1-C4), then LensGates.
- EXTRACTION QUEUE unchanged (definitions table 27461c + appendices + sections in-thread).


## TICK NOTES (2026-07-04T20:25Z) — CRITICAL PROCESS FIX + CrossCap green
- FALSE-GREEN DISCOVERY: earlier Bash builds piped `lake env lean | tail` and echoed $? = tail's
  exit code => several past "EXIT=0" Lean claims were FALSE (CertGraph had real errors: List.get?
  removed, left-assoc && projections, simp drift). BUILD RULE from now on (BINDING): PowerShell,
  `lake env lean <path> *> log; "EXIT=$LASTEXITCODE"` — no pipes, check log EMPTY for 0-warning.
- CertGraph.lean NOW TRUE GREEN (EXIT=0, empty log): L0-L3 + B6 + B2 + flip + canon switch +
  NEW B3 CrossCap (checkCrossCap recomputed-boundary + capacity ineq; checkCrossCap_ineq
  DN*sigma <= nu0; crossCap_sound; partition_crossCap_sound consumer edge).
- HONEST RE-AUDIT of the other 11 modules RUNNING (bg bcwb2cq8h -> scratchpad/module_audit.log):
  Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert, Bank0Algebra. READ RESULTS NEXT TICK; fix any red; P(Lean) recalibrate after.
  Codex asked to confirm its own exit-capture method.
- Floor-buffer Q1/Q2 ruling archived (O14 file tail) + relayed: active-set/full support,
  boundary-feasible hybrid, k0 Markowitz default, Mode-B path-domain form unblocked.
- IN FLIGHT: main = skip-soundness Lean bridge (M-polynomial exact-division route: P(s,u) -
  P(1/2,u) = (1/2 - s)*M(s,u), cone-certify M => NO analysis needed — pending designer verdict)
  + FAQ extension 33+. sibling = section 2.2 LANDED 14664c (extract next tick or at assembly).
- NEXT TICK ORDER: (1) module_audit.log -> fix reds; (2) main reply (M-route verdict decides
  RadialSkipCert Lean shape); (3) extract sibling 2.2 + retask sibling (3.2); (4) Codex scan;
  (5) Lean next increment = ClosureTrace replay module (C1-C4) or EQODL1 skeleton per M-verdict.
- AUDIT RESULT (20:40Z): 11/11 true green zero-warning (PolyCert fixed: ih-unfold pattern in
  mulMono_eval/neg_eval; Gamma _C). Skeleton = statements-only (expected sorry on erdos23_delta0
  top target + True-placeholder BranchB stubs — Assembly fills). BUILD RULE addendum: always
  inspect LOGBYTES>0 logs; grep sorry in any new module before recording green.
- Sibling retasked: section 3.2. Extraction queue += sibling 2.2 (14664c).


## TICK NOTES (2026-07-04T21:15Z) — DiffSkipCert supersedes derivative skips
- SKIP ROUTE FINAL: DiffSkipCert = exact division identity (P - Pbdry = (1-sigma)*M right /
  sigma*M0 left; checkEq) + quotient ConeCert (M >= 0; slacks: G#, dominance deltas — REGION-
  LOCAL NOW SOUND, band, box). Pure Q algebra: no deriv/MVT/MonotoneOn/RadialHull. Derivative
  certs = deprecated fallback. Archived at EQ_ODL1_O14_ASSEMBLY_GPTPRO.md tail + BINDING posted.
- FAQ 33-50 landed (index archived; verbatim at assembly). Codex: BranchB v2 denom guard +
  SHA v6 + v9 reproducer PASS acked; exit-capture confirmation requested. Marker 1633308.
- IN FLIGHT: main = O13 Seed3Complete finite-enumeration proof (completeness keystone of the
  3-door branch); sibling = section 3.3 (3.2 landed 6591c -> extraction queue).
- Lean: diffSkip_right/left scalar consumers added to PolyCert.lean — build in flight
  (bg bd81hrrid). NEXT INCREMENT: ClosureTrace replay module (C1-C4); then EQODL1 cover-cert
  skeleton (BandLabel/RegionCert/EQODL1CoverCert + checkers per O14 9.1-9.2 + DiffSkipCert).
- EXTRACTION QUEUE += sibling 2.2 (14664c), 3.2 (6591c).


## TICK NOTES (2026-07-04T22:10Z) — Seed3 completeness architected
- SEED3_COMPLETENESS_GPTPRO.md archived: two-artifact enum cert (Seed3UniverseCert = width
  cert + canonical lookup + candidate list; per-candidate output witnesses, priority order);
  door-type completeness PROVEN (P4/K13/P2uE/3E); survivors=EQ/SIB = computed result.
  Honesty correction adopted: NO hand-enumerated candidate claims.
- IN FLIGHT: main = CONCRETE WIDTH BOUNDS maxBags(i) + overflow lemma (last unproven q=3
  piece; decisive for O13-UNIVERSE-EMIT). sibling = section 3.4 (3.2+3.3 landed, queued).
  Codex = O13-UNIVERSE-EMIT prep directive posted (falsifier watch: any third survivor =>
  STOP+REPORT); chart-batch work remains its top priority.
- LEAN NEXT (sharpened): ClosureTrace needs full C1-C4 step SEMANTICS from the
  WRITEUP_REDTEAM archive before typing (summary spec insufficient — do the archive read
  as the tick-start action). Alternative ready increment: EQODL1/DiffSkip checker skeleton
  once Codex confirms the chart-shard variable-numbering convention (ASK NEXT POST).
- EXTRACTION QUEUE += sibling 3.3 (5561c). Marker 1633308 (no new Codex posts this tick).


## TICK NOTES (2026-07-04T22:55Z) — width bounds honest-form FINAL
- WIDTH VERDICT archived (SEED3_COMPLETENESS tail): |V0|<=3,|V4|<=3 PROVEN; interior bounds
  certificate-backed ONLY (OverflowCert: TwinDuplicate/NotSaturated/Prunable/NoOverfull/
  NegSwitch/FourDoor + coverage table); ladder (3,3,3,3,3) first; row-template/signature
  emitter mandatory (raw bitsets forbidden); non-circularity rules pinned (no ODL/C5-RS/
  GERSH/Seed3 inside width proofs). Expected canonical count 1e3-1e5.
- Codex posted: width directive + falsifier watch + ASK for chart-shard Var numbering
  (needed before EQODL1/DiffSkip Lean instantiation).
- IN FLIGHT: main = ClosureTrace C1-C4 replay semantics (state/preconds/postconds/invariant/
  Lean shapes — my next module blocks on this); sibling = section 3.5+ (3.4 landed 3411c).
- EXTRACTION QUEUE += sibling 3.4 (3411c). Marker 1633308 (no Codex posts for ~2 ticks —
  chart batch presumably grinding; nudge if silent next tick too).
- LEAN NEXT: ClosureTrace module as soon as semantics land; meanwhile candidates:
  Seed3 OverflowCert/WidthCert data skeletons (contract archived) if main is slow.


## TICK NOTES (2026-07-05T00:00Z) — 2nd chart certified + ClosureTrace contract in hand
- K5/G6/NEAR EXACTLY CERTIFIED + independently reverified (SHA match + my exact-checker rerun:
  0 neg residuals). 2/~108 near-band charts done; Markowitz+repair = BATCH DEFAULT (ruled C);
  floor-buffer PARKED (full-support Stage-1 1.5M cols times out, theta 0.0). Codex next:
  generic no-repair/multi-row manifest + Lean emitter, then batch in map order + SHA ledger.
- Var convention BINDING: Var 200 = s/sigma, Var 201+r = active z/u coord r (skip chart k);
  Var 0=N, 1+i=w_i, aux>=1000 unchanged.
- Codex exit-capture confirmed (argv+returncode, no pipes) EXCEPT RECOVERED_OLEAN_FROM path —
  tightening required (fresh re-run or mtime+stderr guard); await confirmation.
- ClosureTrace C1-C4 FULL CONTRACT archived (LEAN_CHECKER_DESIGN tail): state=U only, C4 gets
  explicit trigger field, checkClosed basis-relative, pressureClaim consumer facts.
  LEAN NEXT TICK (FIRST ACTION): type ClosureTrace.lean per the archived contract (structures
  + replay + checkClosed + pressure + soundness), build honestly, zero warnings.
- IN FLIGHT: main = PeelCert + Bank0Statement + checkBank0Cert dispatch + strong-induction
  skeleton (LAST Lean-design gap; unblocks Assembly module). sibling = next paper section.
- Marker 1640540. Commits through 884b66e6e (this tick commit next).


## TICK NOTES (2026-07-05T00:55Z) — Bank0 Lean design COMPLETE
- BANK0 ASSEMBLY + PEELCERT contract archived (LEAN_CHECKER_DESIGN tail): PeelCert P0-P7
  (pendant boundary, blue-only appendage => badCount equal, blue-connected, parity, row
  invisibility, induced RowDB) + preservation lemmas + bank_transfer; Bank0Statement exact
  predicate; checkBank0Cert structural-on-cert dispatch; bank0_all + Nat.strong_induction_on
  wrapper; nch = NCHBankCert scalar-bank wrapper (NOT ODL NCH-def). Bank0 chain 100% typable.
- Codex: k5 Lean package accepted (17 modules PASS); next = multi-row chart-batch ledger.
- IN FLIGHT: main = TOP-LEVEL assembly statement file (LAST design item program-wide:
  BranchAInputs/GERSH_L5 trichotomy, BranchBInputs, Delta0Inputs, all_rows_gersh,
  SimpleGraph<->GraphData bridge for the Skeleton.lean target); sibling = section 3.6+.
- EXTRACTION QUEUE += sibling 3.5 (6042c).
- LEAN NEXT TICK — HARD FIRST ACTION, NO MORE SLIDING: type ClosureTrace.lean from the
  archived C1-C4 contract (structures + replay foldM + checkClosed + pressureClaim +
  soundness), honest build. THEN Peel.lean skeleton per today s contract. Marker 1642734.


## TICK NOTES (2026-07-05T01:50Z) — ClosureTrace module typed; batch at 4/108
- Lean: B1 ClosureTrace layer WRITTEN into CertGraph.lean (RowRef/RowPrefixData/COrientation/
  BankClosureStep C1-C4/basis items/PressureClaim/BankClosureTrace; getRow/orientedVerts/
  absorbV/familyOf/activatedB/famPrefixVerts/checkWitnessRow; stepAdds + replayClosureStep =
  map(absorbV); replayTrace foldlM; checkClosed (membership-only, _G _c); checkPressureClaim;
  checkBankClosureTrace; replayStep_subset via stepAdds-map factoring; replayTrace_subset;
  3 pressure extraction lemmas; bankClosureTrace_sound). First build red (match-iota traps)
  -> restructured; SECOND BUILD IN FLIGHT (bg blot0sqwn). Fix-or-commit on wake.
- Codex: olean recovery FIXED (fresh_rerun+mtime+stderr, verified); k6+k8 charts certified
  (lex-large; lex-small honestly rejected k6); LEDGER v2: 4/108 certified, validator script.
  Marker 1651672. SPOT-CHECK POLICY (set next post): I independently re-verify ~1 in 10 batch
  rows + every repaired/hard row; full aggregate re-verify at assembly.
- UNEXTRACTED (next tick FIRST after build green): main top-level assembly reply (13470c,
  landed) -> archive + retask main; sibling section 3.6 status unknown -> check + retask.
- EXTRACTION QUEUE unchanged + assembly reply. Commits through 2b7a0fc33.
- BUILD ROUND 3 GREEN (02:20Z): ClosureTrace layer PROVEN zero-warning. CertGraph.lean now
  carries L0-L3 + B6 + B2 + B3 CrossCap + flip + canon switch + B1 ClosureTrace, all verified.
  LEAN NEXT: Peel checker layer (contract archived) OR LensGates; extraction of top-level
  assembly reply (13470c, main thread) FIRST next tick, then retask main.


## TICK NOTES (2026-07-05T03:10Z) — DESIGN PHASE CLOSED program-wide
- TOP-LEVEL ASSEMBLY CONTRACT archived (LEAN_CHECKER_DESIGN tail): 19-declaration stable
  interface from etaQ to erdos23_delta0_simpleGraph; C5RS trichotomy skeleton (P=empty via
  bank0/eta>=0; P=univ via odlFull+fullMask iff; proper via a1Proper+2/3<=1); Branch-B via
  green gersh_Lgt5; gamma squeeze (25m <= Gamma <= N^2); GoodCutData; two-stage certified/
  provider discipline; SimpleGraph bridge via V ≃ Fin card. Safe first target =
  erdos23_delta0_graphData_from_good_cut.
- IN FLIGHT: main = exists_good_cut (LAST imported reduction: B-connected max-cut existence,
  gamma-min in class, RowDBFacts supply, all-l5 provenance); sibling = 3.7+ (3.6 queued).
- LEAN NEXT (order): (1) Peel checker layer in CertGraph (contract archived); (2) Assembly.lean
  skeleton per the 19-declaration list — FIRST read BranchAInterface/Row/Gamma modules for
  existing rowSum/XMask/netDW_assembly/gammaOf names; type against them, keep provider
  theorems as hypotheses; (3) EQODL1/DiffSkip instantiation once Codex chart batch completes.
- EXTRACTION QUEUE += sibling 3.6 (4582c). Marker 1651672 (no new Codex posts; batch grinding).


## TICK NOTES (2026-07-05T04:05Z) — exists_good_cut contracted; batch 6/108
- EXISTS_GOOD_CUT archived (LEAN_CHECKER_DESIGN tail): connected-only + component convexity;
  AllBadLengthFive demoted to branch hypothesis (RowDBFactsGeneral.length_ge_five at
  existence); CutFn (Fin n -> Bool) selection; bconnected_of_maxcut uses badCount_flip_eq +
  sigma_nonneg (ALREADY GREEN); rowDB_exists imported first pass, computable rowsOf later.
  I flagged GammaMinimalConnected signature drift (G c rows vs G c) — audit in flight.
- IN FLIGHT: main = cross-contract consistency audit (defect list before I type
  Peel/Assembly — prevents red-cascade); sibling = 3.7+ (check next tick).
- Codex: batch 6/108 (k8/G3 multi-repair exact increments, k5/G3 no-repair); ledger v4.
  Marker 1654861.
- LEAN NEXT TICK: Peel layer + GoodCut/Assembly skeletons WITH audit verdicts in hand.


## TICK NOTES (2026-07-05T05:20Z) — 50-defect audit in; typing shield complete
- CROSS-CONTRACT AUDIT archived (50 defects + resolutions, LEAN_CHECKER_DESIGN tail). TOP-10
  type-critical: GammaMinimalConnected G c (rows dropped); RowDBFactsAll5 vs General;
  BranchAInputs.etaNonneg (not bank0); Delta0Inputs.etaNonneg global; PeelPreservesFacts +=
  hGraphSmall/hCutSmall + All5 rows; canonical CompletedSwitchCert (+oldBad/newBlue fields at
  next touch); trace types distinct; Seed3Route.toODL vs toBank0 + route TREE provider;
  exists_good_cut connected-only; grouped-generator provenance (EQGroupedSlacks_nonneg).
  MY OVERRIDE: List Nat signatures stay (green code wins over Finset proposal).
- NEW OBLIGATION (audit 36-39): ODL provider = Seed3RouteTree (internal nodes NOT_SATURATED/
  PRUNABLE/FOUR_DOOR, leaves EQ/SIB/NO_OVERFULL/NEG_SWITCH, well-founded measure) — main
  designing now. DiffSkip boundary-cover + FaceCert format posted to Codex (audit 41/42).
- Batch 7/108; k6/G3 repaired row personally reverified (3rd). Marker 1657699.
- LEAN NEXT TICK: type Peel layer INTO CertGraph with AUDITED signatures (PeelPreservesFacts
  extended form; GammaMinimalConnected G c; RowDBFactsAll5 for Bank0 side); then Assembly
  skeleton. Sibling: check + retask (3.7+ status unknown this tick).


## TICK NOTES (2026-07-05T06:00Z) — final goal/loop armed; Peel layer green first try
- USER INSTALLED the final /goal (4-conjunct Stop hook) + reissued /loop. Terminal pair live.
- LEAN: B10 Peel layer GREEN FIRST BUILD (audited signatures worked): PeelData, inducedEdges,
  blueReachStep/iterReach, checkPeelSets/Induced/Pendant/BlueApp/Counts/Parity/Reach/Rows,
  checkPeel, checkPeel_badCount_eq, checkPeel_nlt, peel_bank_transfer. CertGraph now carries
  L0-L3 + B6 + B2 + B3 + B1 + B10, all true green zero-warning.
- Sibling: 3.7 Banked-UPO landed (3447c, queued) -> retasked 3.8+ w/ etaNonneg content update.
- IN FLIGHT: main = Seed3 route-tree provider design (audit items 36-39). Codex = batch
  (7/108) + emptiness probes + DiffSkip w/ corrected boundary-cover format.
- LEAN NEXT: Assembly.lean skeleton (Bank0Statement w/ RowDBFactsAll5 + Bank0Cert inductive +
  checkBank0Cert dispatch + bank0_all) — needs GlobalC5/NCHBank/CrossCert stubs decision:
  type the inductive with all five constructors but ROUTE globalC5/nch through existing
  checkers where possible; consult archived dispatch contract first.
- EXTRACTION QUEUE += sibling 3.7 (3447c). Marker 1657699.


## TICK NOTES (2026-07-05T06:45Z) — route-tree provider contracted
- ODL ROUTE-TREE archived (SEED3_COMPLETENESS tail): Seed3RouteTree (5 leaves + absorb/prune),
  AmbientExcess bookkeeping w/ excess-link ConeCerts (D-cleared) at every internal node,
  structural recursion + checked rank decrease (audit metadata), prune Version A (pure) for
  Lean / Version B (prune-and-close w/ BankClosureTrace) for emitters, ODLRouteInputs package,
  Seed3RouteTree.sound + odl_full, distinct Bank0 consumer map, emission rules.
- IN FLIGHT: main = route-tree MICRO EXAMPLE (absorb+prune+EQ leaf, exact numbers — I will
  Fraction-gate every value on landing; it becomes the Codex emitter + Lean checker validation
  instance). sibling = 3.8+ series. Codex = batch 7/108 + emptiness probes queue.
- LEAN NEXT (with all contracts now in hand): Bank0 Assembly skeleton (Bank0Cert inductive +
  checkBank0Cert dispatch + Bank0Statement w/ RowDBFactsAll5 + bank0_all via
  Nat.strong_induction_on) — GlobalC5/NCHBank sub-checkers stubbed as separate Bool checkers
  routed through existing machinery (template cuts via checkBankBlock-style counting; nch as
  wrapper inductive). Marker 1657699 (no new Codex posts this tick).


## TICK NOTES (2026-07-05T07:40Z) — micro example GATED clean
- ROUTE-TREE MICRO EXAMPLE archived + Fraction-gated ALL PASS (SEED3_COMPLETENESS tail):
  N=21 m=12 eta=141/25, overfull row I=64/3, absorb(door 79, excess equal) -> prune(H={7,10},
  T={7}, D=15, defect 15, increment exactly 1) -> EQ leaf (identity contraction, margin
  323/75); final 64/3 <= 666/25, margin 398/75. Validation instance for O13/route-tree
  emissions + Lean Seed3RouteTree module.
- Codex MDS ASK ruled: scope-before-compute (park if superseded; run only for a named live
  node + exact invocation). Marker 1659447.
- IN FLIGHT: main = q=3 completeness paper section; sibling = 3.8+ series.
- LEAN NEXT: Bank0 Assembly skeleton (all contracts + audit fixes in hand; use RowDBFactsAll5,
  GammaMinimalConnected G c, PeelPreservesFacts extended, IsMaxCut structure form).


## TICK NOTES (2026-07-05T08:50Z) — batch 10/108; cross payload green
- Batch 10/108 (k6/F1 NEW highspy_basis_exact method — I reverified personally, SHA+exact
  PASS; k5/F2; k6/B0 no-repair). Method ACCEPTED as standard alongside Markowitz+modular.
  MDS PARKED w/ provenance (thread c/6a44c764, Slack-CAGE era, no live consumer).
- LEAN: Bank0CrossCert wrapper GREEN (checkBank0Cross = partition + corridor-selection +
  crossCap; bank0Cross_sound => False under max-cut). CertGraph constructor payload status:
  bankBlocks (B6+Bank0Algebra) GREEN, cross GREEN, peel (B10 graph-side) GREEN;
  REMAINING for Assembly: GlobalC5Cert checker, NCHBankCert wrapper, BankBlockCoverCert
  (blocks->global composition w/ bads<->badCount linkage), then Bank0Cert inductive +
  checkBank0Cert dispatch + Bank0Statement + bank0_all.
- q=3 paper section landed on main (14978c — extraction at assembly). Main retask NEXT TICK
  (queue: BankBlockCoverCert bads<->badCount linkage detail if fiddly; else FAQ 51+ or
  O5/O6 artifact audit when they land). Sibling 3.8+ status: check next tick.
- Marker 1668917. EXTRACTION QUEUE += main q=3 section (14978c).


## TICK NOTES (2026-07-05T09:35Z) — GlobalC5 payload green; 4/5 payloads done
- Batch 11/108; k5/F4 (repaired, 384-prime lex-large + highspy basis) reverified by me —
  5th personal check, all repaired rows covered. Marker 1670692.
- LEAN: B5 GlobalC5 GREEN first try (partition-size sum + hygiene + pairwise disjoint +
  recomputed bad-edge placement V4-V0 + five cyclic template bounds; fact extractions
  _sizes and _products feed Bank0Algebra.bank_amgm_rat in Assembly). CertGraph payloads:
  bankBlocks GREEN, cross GREEN, peel GREEN, globalC5 GREEN. REMAINING: NCHBankCert
  routing wrapper (inductive over the four green payloads + future non-C5-hom seed bank
  constructor as data) THEN Assembly.lean (Bank0Cert + dispatch + Bank0Statement +
  bank0_all; imports CertGraph + Bank0Algebra — check import path mechanics for the
  standalone-build pattern: may need one merged file or lake package roots per Codex
  harness --root approach).
- Sibling: 3.8 landed (5734c, queued) -> 3.9 tasked. Main: free after q=3 section —
  RETASK NEXT TICK (queue: FAQ 51+ for route-tree/enumeration; or O5/O6 audit when land).
- EXTRACTION QUEUE += sibling 3.8 (5734c).


## TICK NOTES (2026-07-05T10:15Z) — globalC5 SELF-CLOSING; AM-GM spine in CertGraph
- LEAN: globalC5_bound GREEN (EXIT=0, 0 warnings): checkGlobalC5 => 25*badCount <= n^2,
  fully self-contained (AM-GM spine copied into CertGraph: sqrtHalfAdd/bankAmgmReal/
  bank_amgm_nat — Nat-level, reusable for BankBlockCover per-block finish).
- Bank0 constructor status: globalC5 CLOSED (self-closing); cross CLOSED (needs hmax);
  peel graph-side CLOSED (bank_transfer awaits IH wiring); bankBlocks payload green,
  COVER composition remains (bads<->badCount linkage + blocks_to_global); nch wrapper
  remains. THEN Bank0Cert inductive + dispatch + Bank0Statement + bank0_all — all inside
  CertGraph.lean tail (single-file pattern held; bank_amgm_nat now local).
- Codex: BranchB strict audit v10 w/ NEGATIVE GATE (v9 legacy rejected). Batch 11/108.
  Marker 1671272.
- NEXT TICK: BankBlockCoverCert (partition of recomputed bad edges into blocks + per-block
  bank_amgm_nat + sum_sq: need Nat sum-of-squares<=square lemma — trivial via
  Nat.add_mul_le... or copy sum_sq route) THEN nch wrapper THEN Assembly. Main retask due
  (FAQ 51+ queue). Sibling 3.9 pending check.


## TICK NOTES (2026-07-05T11:25Z) — cover groundwork green; batch 12/108
- LEAN: B6b GREEN (EXIT=0, 0 warnings): nodupLt_length_le (toFinset/card route),
  natSumSq_le_sqSum (explicit square expansion — nlinarith failed on Nat, fixed with
  ring + le_add_right), support_length (finRange 5 by decide), BankBlockCoverCert +
  checkBankBlockCover (per-block + exact bad-list eq + id-count partition + joint support
  nodup/range), checkBankBlockCover_badCount.
- NEXT LEAN (single remaining pre-Assembly item list): (1) coverBound theorem: 25*badCount
  <= n^2 from checkBankBlockCover (chain: badCount = bads.length = flatMap-badIds length =
  sum m_alpha; per-block bank_amgm_nat via checkBankBlock_products + support_length;
  List.sum_le_sum pointwise; natSumSq_le_sqSum; nodupLt_length_le + length_flatMap);
  (2) NCHBankCert routing wrapper; (3) Bank0Cert inductive + dispatch + Bank0Statement +
  bank0_all (Nat.strong_induction_on).
- Batch 12/108 (k5/B0 no-repair). Sibling dead-stub nudged (regenerating). Main = FAQ 51+.
  Marker 1672741.


## TICK NOTES (2026-07-05T12:35Z) — ALL 5 Bank0 payloads proven; batch 14/108
- LEAN: coverBound GREEN first try (cover payload UNCONDITIONAL 25m <= n^2) + NCHBank wrapper
  GREEN (nchBank_sound: globalC5/cover routes unconditional, cross route via refutation).
  PAYLOAD SCOREBOARD: globalC5 CLOSED, bankBlocks/cover CLOSED, cross CLOSED (hmax),
  nch CLOSED (hmax), peel graph-side CLOSED + peel_bank_transfer. REMAINING BANK0 LEAN:
  Bank0Cert inductive (peel carries smallBads/smallAtoms/rest) + checkBank0Cert dispatch
  (structural on cert) + bank0_all strong induction — DESIGN DECISION for the peel case:
  small-graph sigma-nonneg hypothesis must come from P-MaxCut preservation (parity extension
  lemma, not yet formalized) OR carried as a per-level hypothesis via a quantified form
  (hmax on every peel-descendant instance). Ask main next tick for the cleanest Lean form
  (likely: state bank0_all with hypothesis on ALL descendant instances reachable through the
  cert's peel chain — a recursive Prop — vs formalize extension+P-MaxCut now).
- Batch 14/108: k6/F3 (384-prime escalation) + HARD k5/G5 pair-repair — k5/G5 reverified by
  me (6th; all repaired rows covered). first_pending = k5/G7_B2_4T (hard). Marker 1676207.
- Main = FAQ 51+ (in flight); sibling = regenerating post-stub section.


## TICK NOTES (2026-07-05T13:15Z) — BANK0 DISPATCH GREEN: checker program complete
- LEAN MILESTONE: Bank0Cert (globalC5/bankBlocks/cross/nch/peel-recursive) + checkBank0Cert
  (structural on cert) + SigmaChain (per-level sigma hypothesis, honest carrier) +
  bank0Cert_sound — GREEN FIRST TRY. CertGraph.lean now contains the ENTIRE Bank0 checker
  program: L0-L3, B6+B6b cover, B2 partition, B3 CrossCap, B1 ClosureTrace, B5 GlobalC5,
  B10 Peel, canon switch layer, flip calculus, AM-GM spine, dispatch + soundness.
- REMAINING BANK0 LINKS (assembly-level): (1) SigmaChain provider — top level via
  sigma_nonneg_of_isMaxCut (GREEN), peel levels via P-MaxCut preservation (parity extension
  lemma — ask main for the Lean-shape or formalize per archived proof); (2) Branch-A
  consumption edge (Bank0 -> etaNonneg -> C5RS trichotomy per top-level contract).
- Batch 15/108 (hard k5/G7 one-increment repair; reverify in flight w/ dominant=14 — the
  dominant=13 launch was MIS-INDEXED, discard claude_k5g7_recheck.json, use _v2). Marker
  1677261. Main = FAQ 51+ still generating (check next tick); sibling = section regen.


## TICK NOTES (2026-07-05T14:15Z) — batch 17/108; SigmaChain provider consult in flight
- Batch 17/108 (k8/F4 clean, k8/F3 repaired — reverified by me, 8th). first_pending k6/G5
  (hard). Marker 1681172.
- Main = SigmaChain provider contract (P-MaxCut preservation: Ext cut-extension data,
  badCount_Ext, the badCount-min <-> sigmaNonneg equivalence via symmetric-difference flips,
  small minimality transfer) — THE LAST BANK0 LINK. FAQ 51+ landed (extraction at assembly).
- Sibling: regenerated section status unknown — CHECK NEXT TICK (was 3.9 regen after stub).
- LEAN NEXT: on SigmaChain-provider landing, type Ext + badCount_Ext + the equivalence +
  sigmaChain_of_isMaxCut_peel; then Bank0 is fully self-contained modulo Branch-A consumption.


## TICK NOTES (2026-07-05T15:10Z) — SigmaChain contracted; Bank0 closure on paper
- SIGMACHAIN PROVIDER archived (LEAN_CHECKER_DESIGN tail): extendCut (range-map, idxOf?,
  parity xor vs SMALL root side), badCount_extendCut_eq (kept-kept bijection + always-blue
  appendage via P5), sigmaNonneg <-> BadCountMinimal (symmDiff flips), transfer chain,
  SigmaChain_of_sigmaNonneg (structural recursion). NOTE: PeelData needs +rootSmallIdx field
  + checker conjunct at typing.
- LEAN NEXT TICK (headline): TYPE the SigmaChain chain into CertGraph (~200 lines: idxOf? +
  extSide/extendCut + validity + badCount_Ext + sides-agreement + equivalence + transfer +
  provider). Then Bank0 = SELF-CONTAINED from IsMaxCut + checks. After: Branch-A consumption
  (etaNonneg edge) + Assembly.lean per top-level contract.
- Main = Lean-architecture paper section (in flight). Sibling = post-stub regen (CHECK).
  Batch 17/108, marker 1681172. FAQ 51+ + q=3 section + sections 2.2-3.8 in extraction queue.
