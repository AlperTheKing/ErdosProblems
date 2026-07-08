# gap#1 — DEFINITIVE escalation brief: ShortestSupportExpansion / FullBankHall

*Written 2026-07-09T04:45Z after an all-night reduction sequence (GPT-Pro + a 9-angle workflow, cross-checked by exact
computation) that definitively localized gap#1. This is the ONE theorem to attack. Reads standalone; supersedes the
impure-lens framing of GAP1_IMPURE_LENS_ESCALATION_BRIEF.md (that path is resolved — see §2).*

> **⚠ 2026-07-08 UPDATE (Fable-5 session) — READ §8 (appended at bottom) FIRST.** The theorem below is unchanged,
> but the ATTACK FRAME advanced decisively: the relaxed cut-cover + external-slack-bank mechanism is now the
> primary route, its soundness is COMPILED end-to-end in Lean (11 axiom-clean modules), its anchors are
> exact-verified, and the open core is a single certificate-existence theorem with a FINITE Farkas-dual falsifier
> criterion. §6's angle list is superseded by §8. Full detail: `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`.

## 1. THE THEOREM (attack this directly)

> **ShortestSupportExpansion.** In a reduced triangle-free Γ-minimal **maximum** cut, for every set `S` of ell=5 atoms
> (bad edges with blue-distance 4) of a K2-component, `|S| ≤ |E_short(S)|`, where `E_short(S)` = the union over atoms
> in `S` of the cut edges of ALL their shortest blue geodesics.

Equivalent **FullBankHall** form (GPT-Pro's sharpest, b-matching/Hall):
```
∀ A ⊆ OwnedAtoms(C):  Demand(A) ≤ DoorCap(A) + VertexSlackCap(A) + C5BaseCap(A) + PruneCap(A)
  Demand(A)        = Σ_{a∈A} (ell(a)² − 25)
  DoorCap(A)       = 25 · σ-neighborhood available to A          (σ = #cut edges − m)
  VertexSlackCap(A)= support-constrained Σ max(0, N − T(v))
  C5BaseCap(A)     = independent base-density tokens only (single full-support leaves, from ell ≤ |V_D|)
  PruneCap(A)      = balances of strict proper descendant subcages
  *** NEVER the top cage's own reserve η_C = N²/25 − m (that would beg the conjecture) ***
```
`FullBankHall(C) ⟺ Balance(C) ≥ 0`, and for the ell=5 multi-atom full-support part it **specializes to
ShortestSupportExpansion**. Either ⟹ `Γ = Σ ell² ≤ N²` ⟹ `β ≤ N²/25` (Erdős #23 δ=0).

## 2. Why this is THE core (the reduction is settled + compiled)

The whole "impure balanced-neutral lens" saga reduces, via the **escape-closure dichotomy**, to exactly this:
- Escape closure `D = EscClosure(C, lens W)` (least set closed under atoms whose support straddles it).
- **Proper** (`D < C`): ledger-separating ⟹ killed by minimality — **COMPILED**
  (`NeutralLensLedger.no_ledgerSep_in_minNeg`, axiom-clean).
- **Full** (`D = C`): the only possible contradiction is `FullBankHall(C)` = ShortestSupportExpansion. **← this theorem.**

GPT-Pro final verdict: *no local shortcut* forces the closure proper (not maximality, not Γ-minimality, not deficiency,
not reducedness). So the full branch is genuinely live and equals the original difficulty.

## 3. ⚠ Counterfactual — do NOT search real graphs

The binding case is a **deficient** cage (`Γ > N²`), which exists in **no** real triangle-free graph (that IS the
conjecture). Every empirical Hall/expansion battery shows feasibility on 71910 cages with 0 failures precisely because
no gate reaches the binding regime. **Reason deductively.** Abstract configs may be tested for internal consistency
with exact `Fraction` arithmetic; real-graph search is futile.

## 4. Compiled scaffolding (already done — 8 axiom-clean Lean modules, `{propext,Classical.choice,Quot.sound}`)

- `|S| ≤ 5` base case end-to-end at the real blueGraph (`Ell5AtomBase.ell5_base_case`, `Ell5AtomGraph`,
  `Ell5CSReduction`, `Ell5GraphBridge`) + path rigidity (`PathRigidity.edges_determine_badedge`).
- Capacity `|δ_M(U)| ≤ |δ_B(U)|` for a max cut (`MaxCutVertexIneq.deltaM_card_le_deltaB_card`) + maximality lever
  (`not_isMaxCut_of_improving_flip`).
- Minimality lever (`NeutralLensLedger.no_ledgerSep_in_minNeg`, `book_of_book_or_ledgerSep`).
- Aggregation arithmetic (`CageSuperadditivity`: `Σ N_i² ≤ N²`, `Γ ≥ 25m`, `badCount ≤ N²/25`).
So the remaining content is exactly the **general-`|S|` expansion** (the base case is the compiled endpoint).

## 5. DEAD ENDS — refuted with exact facts (do NOT re-tread)

| Route | Killed by |
|---|---|
| surplus-sign / "owned surplus makes W nonneg" | SIGN ERROR: Surplus is demand; `Balance(W)=Bank−Surplus` (owned atoms LOWER it). |
| `NoEscapingAtomAtMaxCut` / direct maximality | **FALSE** — exact 11-vtx counterpattern: escaping atom at a genuine Γ-min max cut (alternate outside geodesic blocks the improving flip). Claude-verified. |
| deficiency/minimality ⟹ closure proper | **FALSE** — deficiency is scalar, creates no separator; full closure genuinely live (D=C realized at a max cut). |
| switch premise (over-congested ⟹ switch) | counterfactual, 0/71910. |
| cut-cover (separating cut per atom, δ_B ⊆ E_short) | FALSIFIED; strictly stronger than Hall (atom (5,9) no separating cut). |
| `m·Q ≤ T²` (Cauchy–Schwarz) | sufficient, NOT necessary (sunflower breaks it, Hall holds). |
| S1ThetaPattern via Γ-decrease | FALSE — balanced ell=5 theta is Γ-NEUTRAL. |
| medium-band BCL bypass | deficiency = length-square density ≠ edge-density; lemmas as hard as original. |

## 6. Genuinely untried angles for the DIRECT attack

1. **Full mixed-bank Hall / b-matching**: prove `Demand(A) ≤ Σ caps` via a fractional matching / max-flow on the
   (atom → support-edge) bipartite incidence, using girth-4 + max-cut to bound overlaps. The RIGHT weighting must be
   exactly Hall-tight (not `m·Q≤T²`, not cut-cover).
2. **Sunflower-freeness** of the shortest-support hypergraph from triangle-free + max-cut (bounds core multiplicity).
3. **Global discharging / Farkas** certificate for `Γ ≤ N²` directly (dual of the single-commodity Gale–Hoffman).
4. **Spectral** (induced P3:P4 ratio, signless-Laplacian, arXiv 2204.00093) on the support hypergraph.
5. **Stability/compactness**: near-extremal (near-deficient) ⟹ structurally close to C5[t], where expansion is tight-but-holds.

## 7. The ask
Prove `ShortestSupportExpansion` / `FullBankHall` for the full escape closure, or exhibit a **deficient** minimal-negative
cage violating it (the decisive falsifier — note every counterpattern found so far is non-deficient, hence consistent
with δ=0). Reason deductively (§3). On success, the compiled scaffolding (§4) + `book_of_book_or_ledgerSep` wire it to
close gap#1 ⟹ Γ≤N² ⟹ β≤N²/25.

## 8. 2026-07-08 UPDATE — the relaxed cut-cover frame (CURRENT; supersedes §6)

GPT-Pro (replies 1-2, archive `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`) recast the theorem as a **certificate
existence** problem, and the whole soundness reduction is now **compiled** (Lean modules `RelaxedCutCover`,
`RelaxedCoverGraphBridge`, `Ell5SupportFinset` — 11 axiom-clean total):

- **Relaxed cut-cover**: weights λ_U ≥ 0 on vertex sets; row coverage ≥ 1; in-support congestion ≤ 1; off-support
  load r(c) FREE but charged to the legal bank (Door 25σ + VertexSlack + C5Base + Prune, never η_C). Compiled:
  `defect(S) ≤ Σ_{c∉F} r(c)` and `25|S| ≤ 25|F| + Bank` (graph-level, only `IsMaxCut` + cert data needed).
- **Anchors exact-verified** (`_claude_rcc_anchors_gate.py`): C5[t] singleton-A4 cover (ext=0); odd cycles
  **Door+Base == Demand exactly (TIGHT) for N ≥ 25** — the bank has zero slack at the Γ=N² extremals, so any
  existence argument must be leak-free there; CP11 escaping-pattern cover {p},{q} (ext=0, the alternate outside
  geodesic carries the congestion). LP gate: 736/736 real configs have strict covers (L*=0), exact certs.
- **THE open core**: `Ell5FullBankRelaxedCover_exists` — every minimal full-closure ell=5 obstruction admits
  cover + bank certs. By LP duality (exact, rational) this is EQUIVALENT to: **no Farkas dual certificate**
  (α_e, β_c, γ_c, δ_j ≥ 0 with (D1) per-cut price domination over the full cut family, (D2) γ_c ≤ δ_j on allowed
  incidences, (D3) Σα > Σβ + Σκ_jδ_j) **coexists with the structural hypotheses** (minimal-neg-balance, reduced,
  full escape closure, max cut, triangle-free). The falsifier search is therefore FINITE per abstract config:
  search dual certificates, not "every cover".
- **Known dual arithmetic** (Claude): singleton-domination alone gives Σα ≤ Σβ + Σ_Oγ; defect>0 leaves room, so
  the proof must be won by richer-cut domination (quotient/lens/closure cuts) + incidence restrictions + the
  minimality/no-private-edge structure (`minimal_hall_obstruction_no_private_edge`, compiled).
- **Ask (updated)**: prove the no-dual theorem, or construct an abstract dual-carrying config satisfying the
  counter-schema (ell=5 defect + every cover un-bankable + no proper ledger-sep + no base leaf + max-cut ineqs +
  Balance<0) — exact rationals, machine-checkable either way.
