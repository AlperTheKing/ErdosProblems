
---

## UPDATE 2026-07-09T04:30Z — DEFINITIVE: no local shortcut; core = FullBankHall / ShortestSupportExpansion

GPT-Pro final verdict on "does deficiency+minimality force the escape closure proper?": **NO.** *"The full-closure
branch is genuinely live and is not killed by reducedness or minimal negative balance."* Deficiency is a SCALAR
condition (`Balance(C)<0` = demand exceeds bank); it does not create a separator. Reducedness removes separators but
does not guarantee one exists. Proving `EscClosure(C,W)=C is impossible` would itself be the full-bank Hall theorem.

**Exact equivalence (the definitive localization):**
```
EscapingClosureDichotomy(C,W):  D = EscClosure(C,W).
  PROPER (D<C, ledger-separating)  => killed by minimality (no_ledgerSep_in_minNeg, COMPILED).
  FULL   (D=C)                     => the only contradiction is FullBankHall(C) i.e. Balance(C) >= 0,
                                      = the full mixed-bank Hall theorem for the whole closure.
```
GPT-Pro: for the ell=5 multi-atom full-support part, FullBankHall SPECIALIZES to `∀ ell=5 row subset S, |S| <= |E_short(S)|`
= **ShortestSupportExpansion** (the original gap#1 core). So *full escape closure absorption ⟺ ShortestSupportExpansion*.

**Sharpest Lean-ready core (GPT-Pro):**
```lean
def FullBankHall (rowDB) (C) : Prop :=
  ∀ A : Finset SurplusAtom, A ⊆ OwnedAtoms rowDB C →
    Demand rowDB A ≤ DoorCap rowDB C A + VertexSlackCap rowDB C A + C5BaseCap rowDB C A + PruneCap rowDB C A
-- DoorCap = 25·σ-neighborhood; VertexSlackCap = support-constrained max(0,N−T(v)); C5BaseCap = independent base-density
-- tokens (single full-support leaves from ell ≤ |V_D|), NEVER the top cage's eta_C; PruneCap = balances of strict proper
-- descendants.  Then FullBankHall.balance_nonneg + hMin.balance_neg discharges the full branch.
```

### Honest endpoint of the 2026-07-08→09 deep sequence
- PERMANENT GAINS (real, compiled): surplus-sign wall DISSOLVED (`no_ledgerSep_in_minNeg`); the ESCAPE-CLOSURE DICHOTOMY
  is the correct localization; the maximality lever (`not_isMaxCut_of_improving_flip`) compiled; the |S|<=5 base case +
  aggregation arithmetic + rigidity compiled (8 axiom-clean modules).
- ALL LOCAL SHORTCUTS RULED OUT (exact counterpatterns): surplus-nonneg (sign error); NoEscapingAtomAtMaxCut (11-vtx
  max-cut escaping atom, CLAUDE-verified); deficiency/minimality-forces-proper (full closure genuinely live).
- THE CORE IS UNCHANGED: `FullBankHall / ShortestSupportExpansion` for the full escape closure = the original gap#1
  difficulty, now PRECISELY stated and cleanly localized (proper case compiled-away). No reduction in essential
  difficulty; the night reframed + de-walled + mapped, it did not close.

**NEXT (escalation): attack `ShortestSupportExpansion` / `FullBankHall` DIRECTLY** with the stronger models
(GPT-5.6/Fable-5) + a focused ULTRACODE workflow. This is the honest irreducible core. P(gap#1 math) ~45 (core =
original ShortestSupportExpansion; reframe + compiled levers are genuine but the essential theorem is the same).
