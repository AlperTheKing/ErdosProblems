# gap#1 SSE direct attack — GPT-Pro reply 1 (Fable-5 era): RELAXED CUT-COVER + EXTERNAL-SLACK BANK

*Harvested 2026-07-08 from MAIN thread (chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61), reply to the Fable-5
retask (ASK A falsifier-first + ASK B angle-pick). Verbatim content, ASCII-sanitized (unicode math folded to ASCII;
`[...]` marks reconstructed seam text from overlapping window pulls). Claude verification notes inline as `[CLAUDE: ...]`.*

## Strategic verdict

The remaining theorem should now be attacked as a **minimal Hall obstruction + external-slack discharging** problem.
The failed cut-cover route required off-support congestion = 0 — too strong, dead. The live route is the relaxed
version: off-support congestion is allowed, but it must be paid by the full bank: Door + vertexSlack + C5/base +
Prune. This is the exact bridge between maximum-cutness and the row-subset Hall inequality.

## ASK A — falsifier-first construction attempts (all die the same way)

A deficient violator needs: triangle-free; maximum cut B; reduced minimal-negative-balance cage C; full escape
closure D=C; ell=5 row set S, |S| >= 6; |S| > |E_short(S)|; and no legal full-bank certificate paying the defect.

- **Attempt 1 (endpoint sunflower):** many ell=5 rows share a small central P4 corridor. For U={x_i}:
  |delta_M(U)|=|Y|, |delta_B(U)|=1 unless x_i has >= |Y| cut-neighbors; adding those cut-neighbors either puts many
  more cut edges into the legal support or creates external slack that must be banked. **Dies at: max-cut vertex
  inequality.**
- **Attempt 2 (dummy cut-edges to force max-cutness):** the dummy cut edges either (1) enter shortest supports —
  |E_short| grows, Hall repaired — or (2) stay outside E_short and become exactly the external slack/bank edges
  paying the defect; they also add structure and tend to destroy negative reserve. **Dies at: external slack edges
  ARE the bank.**
- **Attempt 3 (keep all cut edges inside support):** layered C5-book-like constructions — more rows => more endpoint
  cut-neighborhoods => |E_short(S)| grows at least as fast as |S|. Support expansion restored.
- **Attempt 4 (balanced neutral lens with escaping atoms):** the 11-vtx max-cut escaping-atom example is NOT
  deficient (Gamma=75 < N^2=121). Adding ell=5 atoms to create Hall pressure produces: a proper ledger separator,
  OR extra off-support cut edges paying the defect, OR support-union expansion.

**Surviving abstract falsifier must be:** a minimal full-closure ell=5 support hypergraph with |S|>|E_short(S)|,
max-cut external slack present but NOT legally bankable, and no proper ledger separator. That is the precise object
to search for.

**The repeated obstruction:** every attempted Hall-deficient support produces a max-cut compensating cut-edge
surplus OUTSIDE the support. That is not an accident — it is exactly the theorem to prove:
**Hall defect <= external full-bank capacity.** This is the proof skeleton.

## ASK B — primary recommendation: angle (3), corrected = RELAXED cut-cover

### 1. Normalized ell=5 setting
Atom demand = 1, cut-edge capacity = 1 (after dividing by 25). F = E_short(S). Target |S| <= |F|.
Assume def(S) := |S| - |F| > 0.

### 2. Relaxed cut-cover certificate
Finite family of vertex sets U with rational weights lambda_U >= 0 satisfying:
- **Row coverage:** for each row e in S: sum_{U separates endpoints(e)} lambda_U >= 1.
- **In-support congestion:** for each cut edge c in F: sum_{U : c in delta_B(U)} lambda_U <= 1.
- **Off-support load:** for c notin F: r(c) = sum_{U : c in delta_B(U)} lambda_U, UNCONSTRAINED.

Summing max-cut inequalities:
```
|S| <= sum_U lambda_U |delta_M(U)|          [each covered row is monochromatic, separated => in delta_M(U)]
    <= sum_U lambda_U |delta_B(U)|          [compiled MaxCutVertexIneq, weighted]
     = sum_{c in F} congestion(c) + sum_{c notin F} r(c)
    <= |F| + sum_{c notin F} r(c)
==> def(S) <= sum_{c notin F} r(c) = externalLoad.
```
[CLAUDE: verified the chain — row coverage gives |S| <= sum_e sum_{U sep e} lambda_U <= sum_U lambda_U |delta_M(U)|
since a separated monochromatic edge lies in delta_M(U) and delta_M can only be bigger; the rest is edge-side
re-summation + congestion <= 1. SOUND, Lean-formalizable over the compiled deltaM_card_le_deltaB_card.]

So the Hall defect is exactly paid by external cut-edge slack. **This fixes the failed cut-cover route** (which
demanded r = 0; atom (5,9) killed it).

### 3. Full-bank assignment of external slack
Route each off-support load 25*r(c) to legal sinks: q(c,sink) >= 0, sum_sink q(c,sink) = 25*r(c),
sum_c q(c,sink) <= cap(sink). Legal sinks: **Door** cap 25*sigma; **VertexSlack v** cap = available part of
max(0, N - T(v)) (c may use v only if incident/available per rowDB); **Base/C5** independent base-density tokens;
**Prune** cap = Balance(D) of strict proper descendants. If the assignment exists, the defect is absorbed WITHOUT
the top cage's eta_C.

### 4. Lean-ready chain
- 4.1 `maxcut_weighted_cut_sum`: sum_U lambda_U |deltaM(U)| <= sum_U lambda_U |deltaB(U)| (multiply compiled
  unweighted ineq by lambda_U >= 0, sum).
- 4.2 `RelaxedCutCoverCert` (cuts : Array VertexSet, lambda : Array Rat) + checker (coverage >= 1, congestion <= 1)
  + `relaxedCutCover_defect_bound`: check + max-cut ==> (|S| - |E_short(S)| : Rat) <= sum externalLoad.
- 4.3 `ExternalSlackBankCert` (flows) + checker (per-edge routing exact, per-sink cap, q >= 0, sinks legal) +
  `externalSlackBank_sound`: 25 * sum externalLoad <= DoorCap + VertexSlackCap + BaseDensityCap + PruneCap.
- 4.4 `ell5_hall_absorbed_by_relaxed_cutcover`: both checks + max cut ==>
  25|S| <= 25|E_short(S)| + DoorCap + VertexSlackCap + BaseDensityCap + PruneCap.

### 5. Why better than the dead routes
mQ/T^2 too strong (sunflowers); C1P false; strict cut-cover required separating cuts using only support edges;
relaxed cut-cover exactly matches maximum-cutness — support congestion handles E_short, off-support congestion
becomes full-bank slack. The correct Farkas/discharging formulation.

### 6. THE remaining open core (single theorem)
```
theorem Ell5FullBankRelaxedCover_exists
    (rowDB : RowDB) (C : TerminalCage) (S : RowSet)
    (hMin : MinimalNegBalance rowDB C) (hReduced : ReducedShell rowDB C)
    (hFullClosure : FullEscapingClosure rowDB C S)
    (hS : S subseteq Ell5Atoms rowDB C) :
    exists cover bank,
      checkRelaxedCutCover rowDB S cover = true /\ checkExternalSlackBank rowDB S cover bank = true
```
A certificate-construction theorem with exact algebra. Everything else is algebraic soundness.

### 7. Gating recipe
For every candidate S: solve the relaxed cut-cover LP (coverage >= 1, support congestion <= 1, MINIMIZE external
load) over a cut family (all quotient cuts + endpoint/ball/lens cuts; escalate to all vertex sets if needed); then
solve the external-slack assignment LP into legal bank tokens. Both pass => emit certificates. A TRUE obstruction =
no relaxed cover + bank certificate — not merely Hall defect.

### 8. Counter-schema (decisive abstract falsifier, sharpened)
1. ell=5 row set S with support Hall defect; 2. EVERY relaxed cut-cover of S creates external loads that cannot be
assigned to legal full-bank sinks; 3. no proper ledger-separating subcage; 4. no base leaf; 5. max-cut inequalities
hold; 6. Balance(C) < 0. "Much sharper than before."

## Final answer (GPT-Pro)
Primary = angle (3) as relaxed cut-covers + external slack charged to the full bank; matches the compiled max-cut
capacity lemma; Lean-checkable certificate route. **The one theorem: `Ell5FullBankRelaxedCover_exists`.**

## [CLAUDE next actions]
1. EXACT LP GATE — DONE: _claude_relaxedcover_lp_gate.py, 736/736 real configs L*=0 (strict covers exist
   fractionally, exact certs 736/736), 0 beyond-Door, 0 singleton overflow; C5[t]+CP11 have |X|=0. Binding case
   confirmed counterfactual-only.
2. LEAN — DONE: RelaxedCutCover.lean (abstract soundness, 3 thms) + RelaxedCoverGraphBridge.lean (graph
   instantiation via compiled MaxCutVertexIneq: graph_defect_bound + graph_hall_absorbed + badEdge_mem_deltaM,
   4 thms). Lean = 11 axiom-clean modules.
3. Retask sent (tasks 1-3: anchors / structured existence / dual). Reply 2 below.

---

# REPLY 2 (harvested 2026-07-08): anchors + structured construction + EXACT LP DUAL

## Task 1 — explicit anchor certs (ALL THREE EXACT-VERIFIED, _claude_rcc_anchors_gate.py)

- **1A C5[t]** (Γ-min max cut A0A2A4 | A1A3, bad = A4×A0, all ell=5, geodesics x-a3-a2-a1-y):
  zero-external cover = `{x}` singleton per x ∈ A4, λ=1. Coverage 1 per row; congestion: δB({x}) = {x-a3 : a3∈A3}
  ⊆ E_short, each x-a3 exactly 1. External 0, bank none. **VERIFIED t=1,2,3 exact.**
- **1B odd cycle C_N** (base-leaf density case, m=1, ell=N, Demand=N²−25, σ=N−2): DoorCap=25(N−2),
  BaseCap=max(0,N²−25N+25). N≤23: Demand ≤ Door. N≥25: **Door+Base == Demand EXACTLY (TIGHT)**.
  C_25: 575+25=600; C_41: 975+681=1656. **VERIFIED N=5..41 exact.** ⟹ the bank is exactly balanced on the
  Γ=N² extremals — any proof of the existence theorem must be leak-free there.
- **1C CP11** (escaping-atom max-cut pattern): cover {p},{q} λ=1: coverage e=1,f=1,h=2; δB({p})={p-a,p-r1},
  δB({q})={q-c,q-r3}, all 4 ∈ E_short(S) (p-r1 lies on h's ALTERNATE outside geodesic — multi-geodesic support
  does the work). External 0. **VERIFIED exact incl p-r1 ∈ P_h.** "The escaping lens is not itself a Hall
  obstruction: the support hypergraph expands enough."

## Task 2 — structured family K(S) + hypothesis-consumption map

K(S) = endpoint singletons + quotient cuts (unions of components of B\F) + lens cuts (pair-door/first-split/
last-rejoin from P4-witness pairs) + escaping-closure cuts + optional balls. Consumption: singletons ⟵ ell=5
geometry+cut; quotients ⟵ F; lens ⟵ triangle-free+shortestness; closure ⟵ rowDB ownership; Door ⟵ compiled
MaxCutVertexIneq; VertexSlack ⟵ certified available part of N−T(v); Base ⟵ base-leaf density theorem;
Prune ⟵ compiled descendant balances. **ReducedShell/MinimalNegBalance only forbid proper ledger-sep closures +
justify prune tokens — NOT needed for the raw LP.** Stall = LP infeasible ⟹ Farkas dual = the next sublemma
(cutting-plane loop: add the dual's most violated cut).

## Task 3 — EXACT LP dual (the finite falsifier mechanism)

Normalized (÷25): row demand 1, support capacity 1, sink j capacity κ_j = cap_j/25. Matrices A(e,U)=[U separates
e], B(c,U)=[c ∈ δB(U)], I(c,j)=[c may spend sink j]. Primal: coverage Σ_U A λ ≥ 1; congestion Σ_U B λ ≤ 1 (c∈F);
routing Σ_j q(c,j) ≥ Σ_U B(c,U)λ_U (c∈O); capacity Σ_c q(c,j) ≤ κ_j. **Dual/Farkas infeasibility certificate**:
α_e ≥ 0 (rows), β_c ≥ 0 (support), γ_c ≥ 0 (off-support), δ_j ≥ 0 (sinks) with
- (D1) cut-price domination ∀U ∈ K: Σ_e α_e A(e,U) ≤ Σ_{c∈F} β_c B(c,U) + Σ_{c∈O} γ_c B(c,U)
- (D2) bank-coverable ∀ I(c,j)=1: γ_c ≤ δ_j
- (D3) strict violation: Σ_e α_e > Σ_{c∈F} β_c + Σ_j κ_j δ_j
∃ such (α,β,γ,δ) ⟺ primal infeasible (standard Farkas; Lean-checkable as finite rational linear cert).
**Degenerations:** bank-empty dual = the STRICT cut-cover obstruction (matches Gate-1 atom (5,9)); the direct
b-matching Hall dual (α_e ≤ β_c per incidence, Σα > Σβ) is a DIFFERENT object — do not conflate.
Lean names: RelaxedCoverBankPrimalCert/DualCert, relaxed_cover_bank_dual_infeasible, relaxed_cover_bank_primal_sound.
Workflow: solve primal over K(S) → cert; infeasible → dual; full-family-feasible-but-K(S)-not → cutting-plane;
full family + full bank infeasible → the dual cert IS the exact obstruction.

## [CLAUDE analysis after reply 2]
Singleton-domination (U={v} ∀v) alone forces Σα ≤ Σ_{F}β + Σ_O γ (sum over v, each row/edge counted twice).
With universal Door access (γ_c ≤ δ_door ∀c∈O, κ_door=σ): a dual cert needs Σ_O γ > Σκδ, and |O| − σ = m − |F| =
defect > 0 leaves arithmetic room — so the existence fight is genuinely over (a) richer-cut domination
(quotient/lens/closure), (b) incidence restrictions I(c,j), (c) the structural hypotheses. NEXT RETASK = exactly
this question + dual-side falsifier search harness on abstract counter-schema configs.

---

# REPLY 3 (harvested 2026-07-08): HONEST endpoint — BankedCutDomination = the exact remaining theorem

**Verdict (GPT-Pro, honest):** "I cannot honestly prove no-dual from the current ingredients. The exact no-dual
theorem is now the remaining mathematical statement." The wall is unchanged in difficulty; its sharpest form:

## 1-2. δ-elimination ⟹ the ONE finite inequality
For fixed γ the cheapest δ is `δ_j = max{γ_c : I(c,j)}` (0 if none), giving
`BankCost(γ) = Σ_j κ_j · max{γ_c : I(c,j)}`. **No-dual ⟺ BankedCutDomination**:
> ∀ α,β,γ ≥ 0 satisfying (D1) over the FULL cut family: `Σ_e α_e ≤ Σ_{c∈F} β_c + BankCost(γ)`.
Lean-ready statement given (hypotheses: nonneg + hCutDom; conclusion the inequality).

## 3. Cut-class force map
- **Singletons**: Σα ≤ Σ_Fβ + Σ_Oγ — insufficient when |O| > σ (matches my analysis).
- **Quotient cuts** (unions of components of B\F): δ_B(Y) ⊆ F, γ vanishes ⟹ all quotient-separable α is paid by
  β ALONE. Failure mode: a row with both endpoints in the SAME component of B\F is invisible to quotient cuts —
  exactly the escaping/full-closure phenomenon.
- **Lens/theta cuts**: pure neutral lens has no side-door γ (rows paid by β); impure/escaping lens creates
  side-door γ that must be bank-paid.
- **Closure cuts**: proper ledger-separating closure = killed by compiled minimality (dual mass crossing D paid
  by β or closure-boundary γ); hard case = D = full support (no nontrivial closure cut left) ⟹ full-bank
  obstruction on the whole cage = BankedCutDomination.

## 4. MinimalHallCore (Lean structure)
`bad: |S| > |F|` + `proper_ok: ∀ T ⊂ S, |T| ≤ |E_short(T)|` + `no_private: ∀e∈S, E_e ⊆ E_short(S\{e})`
(= compiled `minimal_hall_obstruction_no_private_edge`). BankedCutDomination should be proved ONLY under
MinimalHallCore + ReducedShell + FullEscapingClosure.

## 5. Anchor dual shapes
Odd cycle: base sink pays exactly (BankCost tight — leak-free requirement). C5[t]: Σα ≤ Σβ, no bank. CP11:
escaping row's dual mass paid by β through the ALTERNATE OUTSIDE support — "a model for how full closure can
still be harmless."

## 6-7. No-dual proof skeleton (3 lemmas)
- **L1 `quotient_cuts_pay_separable_alpha`** (provable now): all quotient-separable row-price mass is support-paid.
- **L2 `remaining_alpha_lies_in_full_escape_closure`** (uses MinimalHallCore + compiled no_ledgerSep): residual
  dual mass lives in the full escaping closure.
- **L3 `full_closure_bank_dominates_dual`** = **THE core** — residual row price not payable by support β is paid
  by legal bank sinks. GPT-Pro: "No. Lemma 3 is exactly the remaining full-bank Hall theorem, in dual form. It is
  the sharp dual form of the wall."

## 8. Falsifier recipe (decisive, finite)
A dual counterexample = finite graph/cut data (tri-free, max-cut) + S,F + sinks (κ, I) + rational α,β,γ,δ with
(D1) ∀U, (D2) ∀incidence, strict (D3), + reduced/minimal/full-closure predicates. **Generate by solving the dual
LP on candidate finite configs.** "No such config is currently known."

## 9. Lean-ready residual (the named hypothesis pair)
`NoDualBankedRelaxedCover` (¬∃ dual cert under hMax+hReduced+hMin+hFull+hMinimalHall) ⟺
`Ell5FullBankRelaxedCover_exists` (∃ cover+bank certs) — equivalent by finite LP duality over ℚ.

## [CLAUDE next after reply 3]
1. Dual-LP falsifier search harness (solve exact dual LP over candidate config families; any rational solution
   satisfying the predicates = decisive falsifier; verifier `_claude_rcc_dual_verify.py` READY).
2. Lean: compile weak duality (primal cert + dual cert ⟹ False) so falsifier verification is machine-checked;
   BankCost δ-elimination lemma; L1 where stateable abstractly.
3. GPT-Pro: path decision (L3 new-idea attack vs dual-config family search vs secondary lanes until GPT-5.6).

---

# REPLIES 4-6 (2026-07-08 evening): path B executed; packing detour opened and closed exact

- **Reply 4 (path decision)**: B — five falsifier families. EXECUTED: F1/F3 guarded books/sunflowers
  **STRUCTURALLY DEAD** (single shared corridor ⟹ odd-cycle packing number 1 ⟹ true max cut separates X|Y;
  book cut E−|R| loses to opposite cut E−1 whenever |R|>1; guards help both sides equally — exact, exhaustive
  ≤2^26). F2 necklace: k=3 = triangle bug (h-edges close C3; valid k=2 or ≥4); k=2 genuine-max but |O|=0. F4
  circulant sweep 7/7: declared cuts never max; true Γ-min max cuts all verdict D with exact certs including the
  FIRST genuinely bank-using covers (ext 9/2, 13/3, 36/11, all ≤ σ). Dual-LP search: 735 real configs, 0 dual
  certs. F5 abstract lifts: not yet run.
- **Reply 5**: L1/L2 Lean-ready designs → **COMPILED** (`RelaxedCoverSkeleton.lean`: quotient_cuts_pay_alpha +
  remaining_alpha_le_closure_alpha + alpha_paid_or_in_closure, axiom-clean first-try). Skeleton compiled except
  exactly L3.
- **Claude mechanism candidate (from F1's failure mode)**: odd-cycle packing/covering duality — unit-weight
  geodesic-5-cycle packing with congestion ≤1 as the cycle-side mirror of the relaxed cover; Guenin/odd-K5 angle.
- **Reply 6 + my gate, CONVERGENT REFUTATION (same hour)**: my `_claude_oddcycle_packing_gate.py` found census
  N=9 violations (t*=2.0, 1.5) among 757 real configs; GPT-Pro independently produced an 18-vtx counterexample —
  **CLAUDE EXACT-VERIFIED** (`_claude_verify_packing_ce.py`): genuine max cut 19 (unique mod flip), Γ-min = 50,
  e=x-y, f=z-w both ell=5 with UNIQUE geodesics sharing exactly a-b ⟹ t*=2 > 1, while Hall holds 2 ≤ 7.
  Factor-4 dead (4|S|=8 > |E_short|=7). Guenin/weakly-bipartite = wrong object (restricted geodesic-cycle family
  ≠ odd-cycle clutter; obstruction is a tiny shared-edge theta, not odd-K5). **DEAD-END TABLE += unit odd-cycle
  packing / factor-4 / Guenin mirror.**
- **What survives (reply 6)**: the b-matching Hall target `|S| ≤ |E_short(S)|` itself (untouched, large slack at
  the CE); `C5BookSupportExpansion` with its clean proof consuming ONLY max-cut vertex ineq + closed-book
  boundary (no Γ-min) — already compiled abstractly (`Ell5CSReduction.c5book_support_expansion`). Live route
  re-confirmed: minimal Hall obstruction → no-private-edge → P4 shared-support classification → C5-book or
  reducible → contradiction; remaining hard node = **the impure balanced-neutral lens / full-bank Hall branch**
  (= BankedCutDomination in dual form; the wall, unchanged).
- **[CLAUDE] Channel pivot**: crux wall re-confirmed identical from primal (P4/lens) and dual (BankedCutDomination)
  sides; GPT-Pro marginal value on the wall exhausted tonight → channel moves to secondary lanes (M6 good-cut
  existence provider design first); the wall goes to GPT-5.6 tomorrow with the updated brief (§8 + this file).
