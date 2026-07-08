# gap#1 — DEFINITIVE escalation brief: ShortestSupportExpansion / FullBankHall

*Written 2026-07-09T04:45Z after an all-night reduction sequence (GPT-Pro + a 9-angle workflow, cross-checked by exact
computation) that definitively localized gap#1. This is the ONE theorem to attack. Reads standalone; supersedes the
impure-lens framing of GAP1_IMPURE_LENS_ESCALATION_BRIEF.md (that path is resolved — see §2).*

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
