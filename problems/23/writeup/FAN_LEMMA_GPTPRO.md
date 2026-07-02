# Fan Lemma b(F) ≥ k(F) (GPT-Pro, 2026-07-02) — Branch B

Status: proof COMPLETE as a boundary statement on the completed fan closure; only inequality
input is max-cut maximality. Claude audited the flip algebra (exact). Remaining obligation is
the LEDGER INTERFACE (§A below), not the lemma itself.

## Statement (corrected form)
Let F be a completed selected-fan component (closure ops 1–5 below). Let
  L(F) = distinct selected bad leaf edges still CROSSING F,  k(F) = |L(F) ∩ δ_M(F)|,
  D(F) = blue side-door boundary edges of F,               b(F) = |δ_B(F)|.
Then **b(F) ≥ k(F)**.

## Closure construction (per selected UNIT-FLAT5 atom a: core K_a, bad leaf ℓ_a ∈ M, two old
## blue doors d_a′, d_a″ ∈ B, protected outside B-path R_a)
1. Common-4-core closure: F contains the whole common-4-core; atoms sharing a core merge.
2. Shared-bad-leaf closure: atoms using the same ℓ merge; ℓ counted once in L(F) iff exactly
   one endpoint in F; if both endpoints absorbed, ℓ is internal and contributes 0 to k(F).
3. Blue-door endpoint closure: both endpoints of each selected door edge in F (doors internal).
4. Protected-B-path closure: full R_a ⊆ F (all internal vertices outside the 6-vertex unit
   core). THIS is where protector existence is used — closes the outside side under B so old
   doors and protector edges are internal, not hidden boundary leaks.
5. Blue saturation except side doors: any blue edge with one endpoint in F not declared a side
   door pulls its other endpoint into F. Fixed point ⟹ δ_B(F) = D(F).

## Proof chain (verified)
(2) L(F) ⊆ δ_M(F) ⟹ (3) k(F) ≤ |δ_M(F)| (unselected crossing bad edges only help).
(4) δ_B(F) = D(F) = b(F) by closure 5.
(5) Max-cut flip: flipping S changes cut size by δ_M(S) − δ_B(S) ≤ 0 ⟹ δ_B(S) ≥ δ_M(S)
    [Claude re-derived: crossing cut edge becomes bad, crossing bad edge becomes cut].
Chain: k(F) ≤ δ_M(F) ≤ δ_B(F) = b(F). ∎
Equivalent form (§5 of reply): the completed fan is a legal nonnegative-σ flip set.

## Hypothesis usage (§6 of reply)
- Triangle-freeness + all-ℓ5: upstream only (atom + doors well defined; protector is a B-path,
  no odd-cycle shortcut).
- Protector existence: closure 4.
- Maximality: THE only inequality input (σ(F) ≥ 0).
- Gamma-minimality: NOT in the final inequality; upstream to justify protected-cell selection
  and kill unprotected theta-like configs (the b=2,k=t intended cuts are non-max for t≥3 —
  consistent with the generated stress: their completed closures create more blue boundary,
  destroy the atom, or expose a negative-σ flip).

## Corrected charging (§7 of reply)
- Shared side door: one boundary edge, counted once in b(F) — no injective door-per-atom claim.
- Shared bad leaf: one crossing bad edge, counted once in k(F) (multiplicity would be FALSE).
- Absorbed shared leaf: contributes to neither δ_M(F) nor k(F); its UNIT-FLAT5 precharge moves
  to the protected-cell/cactus bank, NOT the fan boundary inequality.

## §A LEDGER INTERFACE — the remaining Branch-B assembly obligation (Claude audit note)
The lemma is sound but nearly tautological on F; the genuine content moved to the discharge
ledger:
(i)  Every selected bad leaf is either crossing its completed fan (charged to side doors by
     this lemma) or absorbed (must be charged by the cactus/protected-cell bank). The bank
     must be shown to cover absorbed leaves WITHOUT breaking e_M(C)=2 bookkeeping.
(ii) Cross-fan double-counting: two fan components built from different seeds can overlap or
     share a blue door (closures only merge on shared core/leaf/door-endpoints, not on general
     vertex overlap). FIX (Claude): apply the lemma to the UNION of all selected atoms'
     closures as ONE flip set (flip sets need not be connected) ⟹ global
     k_total ≤ δ_M(F_∪) ≤ δ_B(F_∪) = distinct doors, no edge double-counted.
(iii) Global identity needed: (2k cactus-internal) + (m_out) + (crossing leaves ≤ doors) +
     (absorbed leaves → bank) covers ALL bad-edge precharges exactly once.

## Remaining Branch-B checklist (updated)
1. Peel invariant §H m_out ≤ r²/25 (recursion scoping) — Codex.
2. ~~Fan lemma~~ DONE (this file); LEDGER INTERFACE §A — GPT-Pro next.
3. Claude: exact gate — cactus families (k=1..8 gluings) + fan-closure coherence on census
   gamma-min atoms (fixed point terminates; δ_B(F)=D(F); absorbed-leaf frequency).
