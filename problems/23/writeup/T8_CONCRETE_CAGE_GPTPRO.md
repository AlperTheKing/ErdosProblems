# T8 concrete cage model — GPT-Pro design (2026-07-09)

*Instantiates the compiled `Ell5PureLensCageInterface.PureLensCageSplit` contract; closes open Prop #2
(`PureLensLedgerSeparation`) once built. Verdict: ALL BOOKKEEPING except one optional graph bridge.
ASCII-sanitized; [C: ...] = Claude notes.*

## Core idea
The pure-lens split is a LEDGER split inside the same ambient (G, c, rows) — never an induced-subgraph problem.
Cage = vertex support + owned atom finset; Surplus = Σ atom surpluses (mass·(ell²−25)); Bank = Σ nonnegative
LOCAL bank terms whose support ⊆ cage verts (kinds: door/vertexSlack/baseLeaf/prune — NO η_C token exists in the
frame at all); Balance = Bank − Surplus (rfl); Proper = ambient prunable subcage (verts ⊂, blue-connected inside
and on the complement) — explicitly NOT induced-max-cut.

## Module plan (all under Erdos23Delta0/Ell5/ConcreteCage/; buildable order)
1. **Basic.lean**: `Atom` (alias to the compiled ell5 atom; [C: API reconciliation needed — Ell5AtomGraph works
   at SimpleGraph level and geodesicSupport is EDGE-support; add the vertex closure per the design's own note]),
   Atom.bad/mass(=1)/vertexSupport/ell/gamma/surplus; `AmbientCage` (verts, atoms, atom_support_subset);
   gammaOf/Surplus. Thms: atom_vertexSupport_nonempty (from bad-edge endpoints),
   atom_surplus_eq_zero_of_ell5(_Atom) (via T2). BOOKKEEPING.
2. **Bank.lean**: LocalBankKind (door|vertexSlack|baseLeaf|prune), LocalBankTerm (kind, support Nonempty,
   cap ≥ 0), BankFrame, termInCage (support ⊆ verts, decidable), Bank = Σ filtered caps, Balance.
   Thms: balance_eq_bank_sub_surplus (rfl); **bank_add_le_of_disjoint_subcages** (the concrete G3: TW, TC'
   disjoint subsets of TC — disjointness via support_nonempty ⟹ Σ+Σ = Σ(∪) ≤ Σ by cap ≥ 0). BOOKKEEPING.
3. **Proper.lean**: `AmbientProperSubcage` (verts_ssubset + BConnectedOn inside + on complement). BOOKKEEPING.
4. **Restrict.lean**: restrict (filter atoms with vertexSupport ⊆ U), restrictCompl. BOOKKEEPING.
5. **PureSplit.lean**: `StrongPureLensAtomSplit` (every atom: support ⊆ W ∨ support ⊆ C\W ∨ surplus = 0 — the
   precise no-escaping-except-zero-surplus condition); **surplus_split_of_strongPure** (atom cannot sit in both
   restrictions — support_nonempty + disjointness; sum splits; zero-surplus remainder free); optional graph
   bridge **strongPureLensAtomSplit_of_noEscaping** (hNoEsc: non-contained atom's bad edge ∈ {e,f} + e,f ell=5
   ⟹ surplus 0 via T2). BOOKKEEPING if hPure input; GRAPH only for the bridge.
6. **PureLensSplit.lean**: lensWcage/lensComplCage (restrict at L.W); lensW_proper/lensCompl_proper (shore/
   co-shore connectivity fields of the compiled BalancedNeutralLens; W proper nonempty from the door pair);
   lens_bank_add_le (disjoint subcages thm); lens_surplus_split; **concretePureLensCageSplit** instantiating the
   compiled interface with gamma := AmbientCage, Balance/Bank/Surplus/Proper as above — field proofs = the five
   theorems. BOOKKEEPING once lens + hPure supplied.

## Consumed compiled surface (verbatim list from the design)
Ell5LensStatement.BalancedNeutralLens (W, door signature, shore/co-shore connectivity, e/f ell5);
Distances.ell + badEdge_ell_ge_five; Ell5GapLemmas (T2 ell_eq_five_of_ell5Atom, surplus_split,
pure_lens_ledgerSep); T5/G2 dist_eq_of_le_of_geodesic_sub (only if deriving strong purity);
Ell5SupportFinset.geodesicSupport; Ell5AtomGraph atom-from-bad-edge; Ell5PureLensCageInterface.PureLensCageSplit.
NO use of CageSuperadditivity needed (local Finset version proven directly); NO η_C anywhere.

## New lemmas (all small): atom_vertexSupport_nonempty, surplus_split_of_strongPure,
bank_add_le_of_disjoint_subcages, lensW_proper, lensCompl_proper (+ optional strongPureLensAtomSplit_of_noEscaping).

## Integration
concretePureLensCageSplit ⟹ (compiled) ledgerSep_of_pureLensCageSplit ⟹ PureLensLedgerSeparation proven ⟹
open Prop #2 CLOSED; with no_pure_lens_of_splitProvider_in_minNeg the pure branch is contradictory in min-neg
cages. Remaining open content after T8: ONLY the wall (impure/full-closure = BankedCutDomination).
