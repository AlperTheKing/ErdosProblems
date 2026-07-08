import Mathlib

/-!
# Neutral-lens ledger separation: the balance-sign-agnostic minimality lever (2026-07-09, GPT-Pro reduction)

The gap#1 crux `BalancedNeutralTheta_book_or_reducible` was walled by the IMPURE lens: extra owned atoms in the lens `W`
add DEMAND (`Surplus(W) = Σ_owned (ℓ²−25) ≥ 0`, and `Balance(W) = Bank(W) − Surplus(W)`), so `Balance(W)` may be
negative and no sign follows from neutrality. The naive "surplus makes `W` nonnegative" idea is sign-wrong.

The fix (GPT-Pro): do NOT try to prove `Balance(W) ≥ 0`. Instead show `W` is a proper LEDGER-SEPARATING prunable
subcage — then minimality kills it **regardless of its balance sign**: both `W` and the pruned complement `C'` are
proper descendants, so minimality forces both balances `≥ 0`, whence `Balance(C) = Balance(C') + Balance(W) + rem ≥ 0`
contradicts `Balance(C) < 0`. This module compiles that lever and the resulting crux reduction: the whole crux becomes
the single open local lemma `book_or_ledgerSep` (equivalently `NoEscapingAtomThroughBalancedNeutralLens`), with the
balance-sign difficulty removed. Abstract, axiom-clean; no `sorry`/`admit`/`native_decide`.
-/

namespace Erdos23Delta0
namespace NeutralLensLedger

/-- A ledger-separating prunable subcage `W` of `C` with pruned complement `C'` and nonnegative prune remainder,
    packaged abstractly over a balance function and a "proper valid descendant" predicate: `W` and `C'` are proper
    descendants of `C`, and the ledger splits additively `Balance C = Balance C' + Balance W + rem` with `rem ≥ 0`. -/
structure LedgerSep {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C W C' : γ) (rem : ℚ) : Prop where
  wProper : Proper W
  cProper : Proper C'
  remNonneg : 0 ≤ rem
  pruneIdentity : Balance C = Balance C' + Balance W + rem

/-- **Balance-sign-agnostic minimality lemma.** A minimal-negative-balance cage `C` (`Balance C < 0` and no proper
    descendant has negative balance, encoded as `hMin : ∀ D, Proper D → 0 ≤ Balance D`) contains NO proper
    ledger-separating prunable subcage. No hypothesis on the sign of `Balance W` is needed — that is the whole point,
    and it is what dissolves the impure-lens wall. -/
theorem no_ledgerSep_in_minNeg {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C W C' : γ) (rem : ℚ)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hLS : LedgerSep Balance Proper C W C' rem) :
    False := by
  have hW := hMin W hLS.wProper
  have hC' := hMin C' hLS.cProper
  have hid := hLS.pruneIdentity
  have hrem := hLS.remNonneg
  linarith

/-- **Crux reduction.** If a balanced-neutral non-book theta lens is always either book-parallel OR a ledger-separating
    prunable subcage, then inside a minimal-negative-balance cage it is ALWAYS book (the ledger-separating alternative is
    impossible). This turns `BalancedNeutralTheta_book_or_reducible` into the single open local lemma `book_or_ledgerSep`
    — equivalently `NoEscapingAtomThroughBalancedNeutralLens` — with the balance-sign difficulty removed entirely. -/
theorem book_of_book_or_ledgerSep {γ : Type*} {Book : Prop} (Balance : γ → ℚ) (Proper : γ → Prop)
    (C W C' : γ) (rem : ℚ)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hDichotomy : Book ∨ LedgerSep Balance Proper C W C' rem) :
    Book := by
  rcases hDichotomy with hBook | hLS
  · exact hBook
  · exact (no_ledgerSep_in_minNeg Balance Proper C W C' rem hCneg hMin hLS).elim

/-- **The escape-closure dichotomy closes the lens.** (GPT-Pro's definitive reduction, 2026-07-09.) The escape closure
    `D` of a balanced-neutral lens in a minimal-negative-balance cage `C` is either PROPER (a ledger-separating subcage,
    killed by `no_ledgerSep_in_minNeg`) or FULL (`D = C`), in which case the only possible contradiction is full-bank
    absorption `0 ≤ Balance C`. Given that dichotomy, a min-negative-balance cage has no such lens. This compiles the
    settled reduction; the SOLE remaining mathematical obligation is the full branch's `0 ≤ Balance C` — i.e.
    `FullBankHall` / `ShortestSupportExpansion` for the full escape closure (all local shortcuts to it are refuted). -/
theorem no_balanced_neutral_lens_of_dichotomy {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hDich : (∃ W C' rem, LedgerSep Balance Proper C W C' rem) ∨ 0 ≤ Balance C) :
    False := by
  rcases hDich with ⟨W, C', rem, hLS⟩ | hAbs
  · exact no_ledgerSep_in_minNeg Balance Proper C W C' rem hCneg hMin hLS
  · linarith

#print axioms no_ledgerSep_in_minNeg
#print axioms book_of_book_or_ledgerSep
#print axioms no_balanced_neutral_lens_of_dichotomy

end NeutralLensLedger
end Erdos23Delta0
