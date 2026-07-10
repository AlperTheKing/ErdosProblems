# Prompt: Concrete Forced-Escape Quotient for Gap#1

We are closing Erdős Problem #23 in Lean. The chart batch is accepted; the
remaining wall is Gap#1:


text
FullBankHall / ShortestSupportExpansion / Ell5FullBankRelaxedCover_exists.


Bare SSE and old local switch/lens routes are refuted except as auxiliary
sublemmas. The active route is the banked relaxed cut-cover / external slack
bank / no-Farkas-dual route.

## Current compiled Lean skeleton

The relevant modules are:


lean
Erdos23Delta0.BankedWallLP
Erdos23Delta0.BankedWallLPRestricted
Erdos23Delta0.BankedWallRoutingFailure
Erdos23Delta0.ClosedShoreExtraction
Erdos23Delta0.ClosedWeightedHall
Erdos23Delta0.BankedWallW3Skeleton


The abstract consumption theorem is:


lean
theorem noStrictRestrictedDual_of_closedHall_and_exchange
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap


Thus the remaining graph-side bridge must supply:


lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad


for the concrete forced-ell=5 escape closure, plus the finite rational
Farkas/almost-squeeze source that constructs DualAlmostSqueeze.

## Existing abstract quotient interface


lean
structure AbstractEscapeQuotient (I : BankedWallLP) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp
  fullClosure : Finset QComp -> Finset QComp
  exposedPorts : Finset QComp -> Finset I.Port
  closure_extensive : forall U, U <= fullClosure U
  closure_idempotent : forall U, fullClosure (fullClosure U) = fullClosure U
  closure_monotone : forall U V, U <= V -> fullClosure U <= fullClosure V


Static search of the current source tree found no concrete
ForcedEll5EscapeStep / forced-escape instantiation of this quotient.

## Concrete cage modules are not enough

T8 modules exist and compile:


lean
Erdos23Delta0.Ell5.ConcreteCage.Basic
Erdos23Delta0.Ell5.ConcreteCage.Bank
Erdos23Delta0.Ell5.ConcreteCage.Proper
Erdos23Delta0.Ell5.ConcreteCage.Restrict
Erdos23Delta0.Ell5.ConcreteCage.PureSplit
Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit


They define AmbientCage, atomSupportedOn, Bank, Balance,
StrongPureLensAtomSplit, and concretePureLensCageSplit. They package
pure-lens split bookkeeping once graph-heavy hypotheses are supplied. They do
not instantiate AbstractEscapeQuotient and do not prove root-locality or
closed-Hall completeness.

## Requested output

Please give a concrete route, in Lean-facing terms, for the missing forced
escape quotient bridge. Do not propose bare SSE, scalar Hall, or local
strict-lens-only arguments; those have been refuted.

Deliver one of the following:

### Route A: concrete quotient construction

Define, using the existing cage/atom/support surfaces if possible:

1. the concrete quotient component type QComp;
2. the exposure map exposedPorts : Finset QComp -> Finset I.Port;
3. the forced-escape closure fullClosure;
4. proofs or exact finite gates for:
   - extensive,
   - monotone,
   - idempotent;
5. a Lean statement of PositiveRootBlockClosedExtraction for this concrete
   quotient, with the exact graph lemma that proves it.

The answer must specify which existing Lean objects represent:


text
component, legal root, port, exposed port, forced escape, closed shore.


### Route B: bypass quotient

Give a theorem that directly implies the W3 skeleton's conclusion


lean
¬ d.StrictGap


from d.RestrictedChecked Allowed, DualAlmostSqueeze, and concrete cage
facts, without going through AbstractEscapeQuotient. It must still explain
how weighted routing failures produce an allowed cut violating D1.

### Route C: falsifier

Produce an exact-testable obstruction showing the current W3 route cannot
prove root-locality as stated. The falsifier must name which input fails:


text
ClosedWeightedHallCompleteness
PositiveRootBlockClosedExtraction
ClosedRootCutViolatesD1
finite-Farkas/almost-squeeze source


and should include a finite model / gate specification that can be checked by
Fraction arithmetic or a small Lean object.

## Acceptance criteria

The answer should be specific enough to become one or more Lean modules. Avoid
new invented APIs unless you define how they map to the current objects. A
usable answer contains:


text
new definitions,
new theorem statements,
which existing theorem consumes them,
exact finite gates or proof outline,
and known failure modes.


The key question: how do we instantiate the abstract closed-shore/root-locality
machinery on the real forced-ell=5 cage closure so that a strict restricted
dual yields an allowed cut D1 violation?
Show less

I’ll ground this in the existing Lean surfaces, locate the cited interfaces and cage definitions, then propose the smallest pasteable bridge with finite gates isolated.

I could not verify the source tree, so I’ll rely only on the prompt’s signatures. The quotient route will use finite reachability for fullClosure, with graph content isolated as certificates.

Thought for 12m 33s
Route A: instantiate AbstractEscapeQuotient by a finite Horn-rule forced-escape closure

The right bridge is not a bare SSE quotient and not a scalar Hall theorem. The quotient should be the finite ell=5 atom-shore closure generated by banked forced-escape rules. The key design point is:

QComp should be the concrete cage atom component type, while root-locality is proved separately by showing that the Horn closure of a positive root atom cannot acquire an atom carrying a different legal root block.

That keeps the port/cut geometry atom-level, while avoiding the known failure mode of quotienting directly by root blocks.

1. Object mapping

Use the current objects as follows.

component      = an ell=5 AmbientCage atom/shoreside atom component
legal root     = I.Root satisfying the concrete Proper/Restrict legal-root predicate
port           = I.Port
exposed port   = boundary port of a selected atom shore, plus external-bank exposure
forced escape  = one finite Horn rule: pre ⊆ U ⇒ post ∈ U
closed shore   = U : Finset QComp with Q.fullClosure U = U

In Lean, do not make bank tokens into quotient components. The bank is represented in exposedPorts and in the relaxed cover/Hall certificate. Components remain real cage atoms.

If the AmbientCage atom type is not literally a field named Atom, add a one-line alias in the new module. The construction below only needs:

lean
-- aliases to existing cage surfaces
K.Atom               -- finite atom/component type
atomSupportedOn      -- existing support relation from ConcreteCage.Basic
Bank / Balance       -- from ConcreteCage.Bank
Proper / Restrict    -- legal-root / allowed-cut side conditions
StrongPureLensAtomSplit
concretePureLensCageSplit
2. Generic finite forced-escape closure

Add a small generic module, for example:

lean
import Erdos23Delta0.BankedWallLP

namespace Erdos23Delta0

open Classical

structure HornRule (α : Type*) [DecidableEq α] where
  pre  : Finset α
  post : α
deriving DecidableEq

def HornClosed {α : Type*} [DecidableEq α]
    (R : Finset (HornRule α)) (U : Finset α) : Prop :=
  ∀ r, r ∈ R → r.pre ⊆ U → r.post ∈ U

noncomputable def HornClosure {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) (U : Finset α) : Finset α :=
  Finset.univ.filter fun a =>
    ∀ V : Finset α, U ⊆ V → HornClosed R V → a ∈ V

theorem HornClosure_extensive
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) :
    ∀ U : Finset α, U ⊆ HornClosure R U := by
  classical
  intro U a ha
  simp [HornClosure]
  intro V hUV hV
  exact hUV ha

theorem HornClosure_min
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) {U V : Finset α}
    (hUV : U ⊆ V) (hV : HornClosed R V) :
    HornClosure R U ⊆ V := by
  classical
  intro a ha
  exact (Finset.mem_filter.mp ha).2 V hUV hV

theorem HornClosure_closed
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) :
    ∀ U : Finset α, HornClosed R (HornClosure R U) := by
  classical
  intro U r hr hpre
  simp [HornClosure]
  intro V hUV hV
  apply hV r hr
  intro a ha
  exact (Finset.mem_filter.mp (hpre ha)).2 V hUV hV

theorem HornClosure_monotone
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) :
    ∀ U V : Finset α, U ⊆ V → HornClosure R U ⊆ HornClosure R V := by
  classical
  intro U V hUV a ha
  simp [HornClosure]
  intro W hVW hW
  exact (Finset.mem_filter.mp ha).2 W (Subset.trans hUV hVW) hW

theorem HornClosure_idempotent
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) :
    ∀ U : Finset α,
      HornClosure R (HornClosure R U) = HornClosure R U := by
  classical
  intro U
  apply Finset.Subset.antisymm
  · exact HornClosure_min R (Subset.rfl) (HornClosure_closed R U)
  · exact HornClosure_extensive R (HornClosure R U)

theorem HornClosure_eq_self_iff
    {α : Type*} [DecidableEq α] [Fintype α]
    (R : Finset (HornRule α)) (U : Finset α) :
    HornClosure R U = U ↔ HornClosed R U := by
  classical
  constructor
  · intro h
    simpa [← h] using HornClosure_closed R U
  · intro hU
    apply Finset.Subset.antisymm
    · exact HornClosure_min R (Subset.rfl) hU
    · exact HornClosure_extensive R U

end Erdos23Delta0

This gives the quotient closure laws without graph work. The graph work is only the finite rule table and its correctness.

3. Concrete ell=5 quotient surface

Add a new module, for example:

lean
import Erdos23Delta0.BankedWallLP
import Erdos23Delta0.ClosedShoreExtraction
import Erdos23Delta0.ClosedWeightedHall
import Erdos23Delta0.Ell5.ConcreteCage.Basic
import Erdos23Delta0.Ell5.ConcreteCage.Bank
import Erdos23Delta0.Ell5.ConcreteCage.Proper
import Erdos23Delta0.Ell5.ConcreteCage.Restrict
import Erdos23Delta0.Ell5.ConcreteCage.PureSplit
import Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit

namespace Erdos23Delta0
namespace Ell5

open Classical

The bridge surface should be an adapter over the existing cage fields, not a new graph theory API.

lean
structure ForcedEll5EscapeSurface (I : BankedWallLP) where
  K : AmbientCage I

  /-- Concrete cage atom components. This should be the atom type already
      exposed by `AmbientCage`; use a subtype only if the cage has junk atoms
      that cannot occur in shores. -/
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp

  /-- Legal root predicate from `Proper`/`Restrict`. -/
  legalRoot : I.Root → Prop

  /-- Existing atom support relation, i.e. wrapper around `atomSupportedOn`. -/
  supportedOn : QComp → I.Root → Prop

  /-- A concrete atom containing a legal root. -/
  compOfRoot : (r : I.Root) → legalRoot r → QComp

  compOfRoot_supported :
    ∀ r (hr : legalRoot r), supportedOn (compOfRoot r hr) r

  /-- Root block index. This is not the quotient component. It is only used
      to prove root-locality of the closure. -/
  RootBlock : Type
  rbDecEq : DecidableEq RootBlock
  rbFintype : Fintype RootBlock

  rootBlockOf : (r : I.Root) → legalRoot r → RootBlock

  /-- Ports incident to a concrete cage atom. -/
  atomPorts : QComp → Finset I.Port

  /-- External bank exposure. This is where the external slack bank enters.
      It should be proved from `Bank` and `Balance`. -/
  bankExposes : Finset QComp → I.Port → Prop

  /-- Finite forced-escape Horn rules. -/
  rules : Finset (HornRule QComp)

The exposed-port map should be atom-boundary plus bank exposure:

lean
noncomputable def ForcedEll5EscapeSurface.incidentComps
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I)
    (p : I.Port) : Finset S.QComp := by
  classical
  letI := S.qDecEq
  letI := S.qFintype
  exact Finset.univ.filter fun c => p ∈ S.atomPorts c

noncomputable def ForcedEll5EscapeSurface.exposedPorts
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I)
    (U : Finset S.QComp) : Finset I.Port := by
  classical
  exact Finset.univ.filter fun p =>
    ((S.incidentComps p ∩ U).Nonempty) ∧
      (((S.incidentComps p).filter fun c => c ∉ U).Nonempty ∨
        S.bankExposes U p)

Then instantiate the abstract quotient:

lean
noncomputable def ForcedEll5EscapeSurface.toQ
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) :
    AbstractEscapeQuotient I := by
  classical
  letI := S.qDecEq
  letI := S.qFintype
  exact
  { QComp := S.QComp
    qDecEq := S.qDecEq
    qFintype := S.qFintype
    fullClosure := HornClosure S.rules
    exposedPorts := S.exposedPorts
    closure_extensive := HornClosure_extensive S.rules
    closure_idempotent := HornClosure_idempotent S.rules
    closure_monotone := HornClosure_monotone S.rules }

Closed shore is then definitionally:

lean
def ForcedEll5EscapeSurface.ClosedShore
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I)
    (U : Finset S.QComp) : Prop :=
  (S.toQ.fullClosure U = U)

and by HornClosure_eq_self_iff, this is equivalent to being closed under every concrete forced-escape rule.

4. The forced-escape rule table

The concrete rule table should be generated from the ell=5 cage facts, but the closure only stores plain finite rules.

lean
inductive ForcedEll5RuleKind where
  | bank
  | restrict
  | pureSplit
  | pureLensSplit
  | properBoundary
deriving DecidableEq, Repr

Do not put proof fields into HornRule, because then Finset equality and decidability become annoying. Instead define a recognizer:

lean
def IsForcedEll5Rule
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I)
    (r : HornRule S.QComp) : Prop :=
  IsBankForcedRule S r ∨
  IsRestrictForcedRule S r ∨
  IsPureSplitForcedRule S r ∨
  IsPureLensForcedRule S r ∨
  IsProperBoundaryForcedRule S r

where each disjunct is a thin wrapper around existing objects:

IsBankForcedRule          uses ConcreteCage.Bank / Balance
IsRestrictForcedRule      uses ConcreteCage.Restrict
IsPureSplitForcedRule     uses ConcreteCage.PureSplit
IsPureLensForcedRule      uses StrongPureLensAtomSplit and concretePureLensCageSplit
IsProperBoundaryForcedRule uses ConcreteCage.Proper

The finite table gate is:

lean
structure ForcedEll5RuleTableCert
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) : Prop where
  rules_exact :
    ∀ r : HornRule S.QComp, r ∈ S.rules ↔ IsForcedEll5Rule S r

This is the replacement for the missing ForcedEll5EscapeStep. The closure is not an inductive graph walk; it is the least fixed point of this finite Horn table.

5. Positive root block extraction

This is the root-locality gate. Define the fiber of a legal root block as the set of atoms that carry no legal root outside that block. Rootless atoms belong to every fiber, which is exactly what we want for bank shields and zero-demand closure atoms.

lean
noncomputable def ForcedEll5EscapeSurface.rootFiber
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I)
    (b : S.RootBlock) : Finset S.QComp := by
  classical
  letI := S.qDecEq
  letI := S.qFintype
  exact Finset.univ.filter fun c =>
    ∀ r (hr : S.legalRoot r),
      S.supportedOn c r → S.rootBlockOf r hr = b

The exact graph lemma needed for PositiveRootBlockClosedExtraction is:

lean
theorem forcedEll5_rootFiber_forcedClosed
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (hRules : ForcedEll5RuleTableCert S)
    -- hypotheses already packaged by the concrete cage modules:
    (hProper : Ell5ProperCage S.K)
    (hBank : Ell5BankBalanced S.K)
    (hPureSplit : Ell5PureSplitOK S.K)
    (hPureLens : StrongPureLensAtomSplit S.K) :
    ∀ b : S.RootBlock, HornClosed S.rules (S.rootFiber b)

The proof is by rule membership:

lean
intro b r hr hpre
rw [hRules.rules_exact] at hr
rcases hr with hBankRule | hRestrictRule | hPureRule | hLensRule | hProperRule

Each case proves that if all premise atoms carry only roots from block b, then the forced target atom also carries only roots from block b.

The second required finite/local gate is atom-root purity:

lean
theorem forcedEll5_atomRootPure
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (hProper : Ell5ProperCage S.K)
    (hRestrict : Ell5RestrictOK S.K) :
    ∀ c r s
      (hr : S.legalRoot r) (hs : S.legalRoot s),
      S.supportedOn c r →
      S.supportedOn c s →
      S.rootBlockOf r hr = S.rootBlockOf s hs

This proves that the component chosen for a positive root lies in its own root fiber:

lean
lemma compOfRoot_mem_rootFiber
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (hPure : ∀ c r s
      (hr : S.legalRoot r) (hs : S.legalRoot s),
      S.supportedOn c r →
      S.supportedOn c s →
      S.rootBlockOf r hr = S.rootBlockOf s hs)
    (r : I.Root) (hr : S.legalRoot r) :
    S.compOfRoot r hr ∈ S.rootFiber (S.rootBlockOf r hr) := by
  classical
  simp [ForcedEll5EscapeSurface.rootFiber]
  intro s hs hsupp
  exact hPure (S.compOfRoot r hr) s r hs hr hsupp
    (S.compOfRoot_supported r hr)

Then positive extraction follows from minimality of HornClosure:

lean
theorem forcedEll5_positiveRootBlockClosedExtraction
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (hFiberClosed : ∀ b : S.RootBlock, HornClosed S.rules (S.rootFiber b))
    (hAtomPure : ∀ c r s
      (hr : S.legalRoot r) (hs : S.legalRoot s),
      S.supportedOn c r →
      S.supportedOn c s →
      S.rootBlockOf r hr = S.rootBlockOf s hs) :
    PositiveRootBlockClosedExtraction S.toQ := by
  classical
  -- unfold PositiveRootBlockClosedExtraction
  -- for a positive legal root r, choose:
  -- U := S.toQ.fullClosure {S.compOfRoot r hr}
  --
  -- closedness:
  --   simpa [ForcedEll5EscapeSurface.toQ] using
  --     HornClosure_idempotent S.rules {S.compOfRoot r hr}
  --
  -- root-locality:
  --   U ⊆ S.rootFiber (S.rootBlockOf r hr)
  -- by HornClosure_min, because the fiber is HornClosed and contains compOfRoot r.
  --
  -- positivity:
  --   compOfRoot r hr ∈ U by HornClosure_extensive.
  --
  -- legal roots supported in U are in the same root block by definition of rootFiber.
  sorry

The sorry is only the unfolding of your existing predicate. The graph-heavy theorem is exactly:

lean
forcedEll5_rootFiber_forcedClosed

plus

lean
forcedEll5_atomRootPure

If either one fails, PositiveRootBlockClosedExtraction is the failing input.

6. Closed weighted Hall completeness

The closed Hall theorem should be proved only for closure-fixed shores.

Define the finite row set:

lean
noncomputable def ForcedEll5EscapeSurface.closedRows
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) :
    Finset (Finset S.QComp) := by
  classical
  letI := S.qDecEq
  letI := S.qFintype
  exact (Finset.univ : Finset S.QComp).powerset.filter fun U =>
    S.toQ.fullClosure U = U

The concrete closed Hall gate should be a banked relaxed cover table:

lean
structure Ell5ClosedBankHallCert
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) : Prop where
  relaxedCover :
    ∀ U : Finset S.QComp,
      U ∈ S.closedRows →
      Ell5FullBankRelaxedCover S.K
        -- root side:
        (Finset.univ.filter fun r =>
          S.legalRoot r ∧ ∃ c ∈ U, S.supportedOn c r)
        -- port side:
        (S.toQ.exposedPorts U)

  cover_valid :
    ∀ U hU, FullBankHall.ValidRelaxedCover (relaxedCover U hU)

Then add the theorem:

lean
theorem forcedEll5_closedWeightedHallCompleteness
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (hHall : Ell5ClosedBankHallCert S) :
    ClosedWeightedHallCompleteness S.toQ := by
  classical
  -- unfold ClosedWeightedHallCompleteness
  -- normalize any candidate U by Q.fullClosure U
  -- use closedRows membership for the normalized U
  -- apply FullBankHall to hHall.relaxedCover U hU
  -- all numerical inequalities are from the relaxed cover certificate
  sorry

This is the correct place to use the old FullBankHall and any auxiliary ShortestSupportExpansion facts. They should appear only inside the proof of a closed-row relaxed cover, not as the quotient closure itself.

The finite gate is therefore:

lean
∀ U ∈ S.closedRows, Ell5FullBankRelaxedCover ... (S.toQ.exposedPorts U)

with rational inequalities checked in the FullBankHall.ValidRelaxedCover rows.

7. Closed shore extraction and D1 violation

For the exchange input, the concrete lemma must turn a closure-fixed atom shore into an allowed cut whose port set is exactly the quotient exposure.

Add a cut gate:

lean
structure Ell5ClosedShoreCutGate
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (Allowed : I.Cut → Prop)
    (d : Dual I)
    (portLoad : I.Port → ℚ) : Prop where

  cutOf :
    ∀ U : Finset S.QComp,
      S.toQ.fullClosure U = U → I.Cut

  allowed :
    ∀ U hU, Allowed (cutOf U hU)

  ports_eq :
    ∀ U hU,
      CutPorts (cutOf U hU) = S.toQ.exposedPorts U

  roots_eq :
    ∀ U hU,
      CutRoots (cutOf U hU) =
        Finset.univ.filter fun r =>
          S.legalRoot r ∧ ∃ c ∈ U, S.supportedOn c r

  d1_row_eq :
    ∀ U hU,
      D1CutExpr d portLoad (cutOf U hU) =
      ClosedRowExpr S.toQ d portLoad U

Here CutPorts, CutRoots, D1CutExpr, and ClosedRowExpr should be the existing names if already present in BankedWallLP, ClosedShoreExtraction, or ClosedWeightedHall. If they are not named, define them by unfolding the current ClosedRootCutViolatesD1 body.

The theorem consumed by the W3 skeleton is:

lean
theorem forcedEll5_closedRootCutViolatesD1
    {I : BankedWallLP}
    {Allowed : I.Cut → Prop}
    {d : Dual I}
    {portLoad : I.Port → ℚ}
    (S : ForcedEll5EscapeSurface I)
    (hCut : Ell5ClosedShoreCutGate S Allowed d portLoad) :
    ClosedRootCutViolatesD1 Allowed S.toQ d portLoad := by
  classical
  -- unfold ClosedRootCutViolatesD1
  -- given a closed quotient row U with a strict D1 row violation,
  -- choose hCut.cutOf U hU
  -- allowed follows from hCut.allowed
  -- rewrite ports and roots using hCut.ports_eq / hCut.roots_eq
  -- rewrite the D1 expression using hCut.d1_row_eq
  -- conclude the allowed cut violates D1
  sorry

The graph lemma behind this gate should live in ClosedShoreExtraction or a new ell=5 module:

lean
theorem forcedEll5_closedShoreCut_exists
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (Allowed : I.Cut → Prop)
    (hRules : ForcedEll5RuleTableCert S)
    (hRestrict : Ell5RestrictOK S.K)
    (hBank : Ell5BankBalanced S.K) :
    ∀ U : Finset S.QComp,
      S.toQ.fullClosure U = U →
      ∃ C : I.Cut,
        Allowed C ∧
        CutPorts C = S.toQ.exposedPorts U ∧
        CutRoots C =
          Finset.univ.filter fun r =>
            S.legalRoot r ∧ ∃ c ∈ U, S.supportedOn c r

This is where weighted routing failures become allowed D1 violations: a Hall/D1 row failure on a closed quotient shore is rewritten into the D1 expression of the extracted allowed cut.

8. Almost-squeeze/Farkas source

Keep the rational certificate separate from the graph quotient.

lean
structure RestrictedAlmostSqueezeCert
    (I : BankedWallLP)
    (Allowed : I.Cut → Prop)
    (d : Dual I) where

  supportCuts : Finset I.Cut
  support_allowed :
    ∀ C ∈ supportCuts, Allowed C

  lambda : I.Cut → ℚ
  lambda_support :
    ∀ C, C ∉ supportCuts → lambda C = 0
  lambda_nonneg :
    ∀ C, 0 ≤ lambda C

  portLoad : I.Port → ℚ

  -- These fields should be the unfolded finite rational equalities/inequalities
  -- required by DualAlmostSqueeze.
  root_squeeze_ok : RestrictedRootSqueezeRows I Allowed d lambda portLoad
  port_squeeze_ok : RestrictedPortSqueezeRows I Allowed d lambda portLoad
  objective_ok : RestrictedObjectiveSqueezeRow I Allowed d lambda portLoad

Then:

lean
theorem dualAlmostSqueeze_of_restrictedCert
    {I : BankedWallLP}
    {Allowed : I.Cut → Prop}
    {d : Dual I}
    (C : RestrictedAlmostSqueezeCert I Allowed d) :
    DualAlmostSqueeze I Allowed d := by
  -- unfold DualAlmostSqueeze
  -- all goals are finite ℚ arithmetic from C
  sorry

This theorem should live near BankedWallLPRestricted or BankedWallRoutingFailure, not in the cage quotient module.

9. Final W3-facing theorem

The final bridge theorem should look like this:

lean
theorem forcedEll5_noStrictRestrictedDual
    {I : BankedWallLP}
    {Allowed : I.Cut → Prop}
    {d : Dual I}
    (S : ForcedEll5EscapeSurface I)
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)

    (hRules : ForcedEll5RuleTableCert S)

    (hFiber :
      ∀ b : S.RootBlock, HornClosed S.rules (S.rootFiber b))

    (hAtomPure :
      ∀ c r s
        (hr : S.legalRoot r) (hs : S.legalRoot s),
        S.supportedOn c r →
        S.supportedOn c s →
        S.rootBlockOf r hr = S.rootBlockOf s hs)

    (hHall : Ell5ClosedBankHallCert S)

    (hCut :
      Ell5ClosedShoreCutGate S Allowed d Z.portLoad) :
    ¬ d.StrictGap := by
  exact
    noStrictRestrictedDual_of_closedHall_and_exchange
      (Allowed := Allowed)
      (Q := S.toQ)
      (d := d)
      hd
      Z
      (forcedEll5_closedWeightedHallCompleteness S hHall)
      (forcedEll5_positiveRootBlockClosedExtraction S hFiber hAtomPure)
      (forcedEll5_closedRootCutViolatesD1 S hCut)

This is the module that BankedWallW3Skeleton should consume.

10. Exact finite failure tests

Add these as diagnostics. They make the route falsifiable.

Root-locality obstruction
lean
noncomputable def badRootFiberRules
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) :
    Finset (S.RootBlock × HornRule S.QComp) := by
  classical
  letI := S.qDecEq
  letI := S.qFintype
  letI := S.rbDecEq
  letI := S.rbFintype
  exact
    (Finset.univ.product S.rules).filter fun br =>
      let b := br.1
      let r := br.2
      r.pre ⊆ S.rootFiber b ∧ r.post ∉ S.rootFiber b

If this finset is nonempty, the failing input is:

PositiveRootBlockClosedExtraction

and the displayed row gives the forced escape that imports a different legal root block.

Atom-root purity obstruction
lean
def badMixedRootAtoms
    {I : BankedWallLP} (S : ForcedEll5EscapeSurface I) : Prop :=
  ∃ c r s
    (hr : S.legalRoot r) (hs : S.legalRoot s),
    S.supportedOn c r ∧
    S.supportedOn c s ∧
    S.rootBlockOf r hr ≠ S.rootBlockOf s hs

If this is inhabited, raw cage atoms are too coarse. Either refine the cage atom decomposition, or the current W3 route cannot prove root-locality as stated.

Closed Hall obstruction
lean
noncomputable def badClosedHallRows
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I) :
    Finset (Finset S.QComp) := by
  classical
  exact S.closedRows.filter fun U =>
    ¬ ClosedWeightedHallRow S.toQ U

If nonempty, the failing input is:

ClosedWeightedHallCompleteness

The row should be checked by rational arithmetic against the external slack bank.

Closed-shore cut obstruction
lean
def badClosedShoreCutRow
    {I : BankedWallLP}
    (S : ForcedEll5EscapeSurface I)
    (Allowed : I.Cut → Prop) : Prop :=
  ∃ U,
    S.toQ.fullClosure U = U ∧
    ¬ ∃ C : I.Cut,
      Allowed C ∧
      CutPorts C = S.toQ.exposedPorts U ∧
      CutRoots C =
        Finset.univ.filter fun r =>
          S.legalRoot r ∧ ∃ c ∈ U, S.supportedOn c r

If inhabited, the failing input is:

ClosedRootCutViolatesD1
Farkas/almost-squeeze obstruction

The finite rational checker should report one of:

negative multiplier
non-Allowed support cut
root coefficient mismatch
port coefficient mismatch
objective squeeze mismatch

If any occurs, the failing input is:

finite-Farkas/almost-squeeze source
Known failure modes to avoid

Do not set QComp := RootBlock. That loses atom-level boundary data, so CutPorts C = Q.exposedPorts U becomes unprovable.

Do not put bank components into QComp. The external slack bank belongs in bankExposes, Ell5FullBankRelaxedCover, and the rational Hall/Farkas rows.

Do not use unary-only forced steps unless the actual forced escape relation is unary. Use Horn rules because banked/lens closure can require multi-premise implications.

Do not prove Hall on all shores. The required theorem is closed weighted Hall completeness for U satisfying Q.fullClosure U = U.

Do not let exposedPorts ignore bank exposure. If bankExposes is missing, ClosedRootCutViolatesD1 will fail at ports_eq.

The essential missing bridge is therefore:

lean
ForcedEll5EscapeSurface.toQ
forcedEll5_rootFiber_forcedClosed
forcedEll5_atomRootPure
forcedEll5_closedWeightedHallCompleteness
forcedEll5_closedRootCutViolatesD1

Once these are in place, the current abstract theorem closes the W3 skeleton by a direct application of noStrictRestrictedDual_of_closedHall_and_exchange.

Pro Extended
ChatGPT can make mistakes. Check important info.