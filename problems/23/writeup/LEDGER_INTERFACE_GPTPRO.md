# Ledger Interface Lemma (GPT-Pro, 2026-07-02) — Branch B assembly

Status: bookkeeping lemma COMPLETE (no new extremal inequality; a double-count-preventing
ledger). Resolves §A of FAN_LEMMA_GPTPRO.md. ONE interface assertion remains to confirm on the
peel side: (6.1) below — Codex to check against the actual UNIT-FLAT5 peel gate output.

Notation: A = selected protected UNIT-FLAT5 atoms for the fixed L>5 row Q; a = |A|; C_x = the
protected cell of atom x; Σ_L = (L²−25)/50; η = N²/25 − m. Target: R_Q ≤ N + η/2 − Σ_L.

## 1. Global fan inequality (Fan_u) — union form CONFIRMED
F_u = closure of the UNION of all selected atom closures under the same five rules (shared
common-4-cores, shared selected bad leaves, shared blue door endpoints, outside B-protector
paths, blue saturation except declared side doors). F_u need not be connected — flips apply to
any vertex set. D_u = δ_B(F_u) (external blue side doors); L_u = selected bad leaves with
exactly one endpoint in F_u (globally crossing).
  |L_u| ≤ |δ_M(F_u)| ≤ |δ_B(F_u)| = |D_u|      (Fan_u)
NEVER sum per-component fan inequalities: a blue edge between two fan closures would count as
a door for both, but in the union flip it is internal and gives ZERO boundary credit.

## 2. Bad-edge mass ledger (M ledger) — TWO classes only
  M = M_cell ⊔ M_out,  M_cell = ∪_x E_M(C_x),  |M_cell| = 2a,  m = 2a + m_out.
My proposed 4-way split (2k + m_out + crossing + absorbed) REJECTED — correctly: crossing vs
absorbed is a FAN-relative property, not a bad-edge partition; a selected leaf can be internal
to its protected cell while crossing F_u. No bad edge lies in two cells (pairwise ≤1 shared
vertex); δ_M(C_x)=0 kills cell-crossing bad edges. This M ledger is all the cactus bank needs.

## 3. Precharge ledger (P ledger) — fan-paid vs cell-paid UNITS
Each atom contributes one precharge unit π(x)=1; Π = Π_fan ⊔ Π_cell.
Rule: if x's selected bad leaf is globally crossing for F_u AND that leaf edge is not already
used by another fan-paid unit → Π_fan; otherwise → Π_cell.
⟹ Π_fan → L_u injective ⟹ |Π_fan| ≤ |L_u| ≤ |D_u| (3.1–3.3).
Absorbed leaves and shared-leaf multiplicities are ALL in Π_cell, paid by their own protected
cell through the cactus half-bank. F_u is NOT promoted to a protected cell; absorbed leaves do
NOT retreat to m_out and are NOT charged to the length surplus.

## 4. Cactus bank pays Π_cell
Archived half-bank: m_out + 4a ≤ N²/25 (4.1) ⟹ η = N²/25 − m_out − 2a ≥ 2a ⟹ a ≤ η/2 (4.2).
The quadratic bank pays the 2a internal bad edges and leaves ≥2a deficit headroom — one
precharge per cell costs half the remaining headroom. Only fact used: |Π_cell| ≤ a ≤ η/2.

## 5. Door budget — doors are FREE via maximality
Blue side doors are NOT paid by η/2 and NOT by the length surplus. They are paid by the fan
flip inequality itself: |Π_fan| − |D_u| ≤ 0 by (Fan_u). A separate cut-slack budget, not a
quadratic budget.

## 6. Final one-line interface inequality
  (6.1)  R_Q ≤ N − Σ_L + |Π_cell| + |Π_fan| − |D_u|        [what the UNIT-FLAT5 peel gives]
  (6.2)  drop |Π_fan|−|D_u| ≤ 0 (Fan_u), bound |Π_cell| ≤ a ≤ η/2 (4.2):
         **R_Q ≤ N + η/2 − (L²−25)/50** — the Branch-B target, exactly.
⚠ CONFIRMATION OBLIGATION: (6.1) is asserted as the peel's output form. Codex to verify the
existing SLACK-CAGE UNIT-FLAT5 peel gate literally produces (6.1) (base row bank N, minus
length surplus, plus precharge units, minus door credit).

## 7–8. Exactly-once summary + union necessity
Two ledgers, disjoint roles: fan-paid precharges cancel against max-cut side-door credit;
cell-paid precharges (incl. all absorbed leaves) paid by cactus half-bank. Every bad edge in
exactly one of M_cell/M_out. Union form is the only safe global credit (|D_u| = |δ_B(F_u)|,
NOT Σ_C b(C)).

## 9. Stress compatibility
Claimed compatible with N≤11 census gamma-min cuts, two-lane L=12, glued k=1..8 cactus
families (my _claude_cactus_family_gate.py instances).

## Chain position
(Fan_u) [FAN_LEMMA_GPTPRO.md] + cactus half-bank [CACTUS_PACKING_LEMMA_GPTPRO.md, conditional
on §H peel invariant m_out ≤ r²/25] + this ledger ⟹ (6.2) ⟹ GERSH_{L>5}.
Remaining Branch-B: §H peel invariant + (6.1) peel-side confirmation + fan-closure coherence
gate (Claude, queued).
