# Owner-shore transport retry: amortized multi-row endpoint

## Verdict

No complete proof of the global-minimizer theorem was obtained. The valid
reduction is an endpoint/amortized theorem, not Hamming-one descent. The sole
open mathematical gap is named **Amortized owner-shore trade construction**
below.

## Exact definitions used

For a row choice `omega`:

* `scopedCollisionScore G c omega := Fintype.card (ActiveCollisionHalf G c omega)`.
* `scopedHitNeedScore G c omega := Fintype.card (ActiveHitNeed G c omega)`.
* `scopedObligationScore = scopedCollisionScore + scopedHitNeedScore` by
  `scopedObligationScore_eq_parts`.
* A deficient owner shore is a finite owner set `A` with
  `|scopedOwnerSourceSet G c omega A| < |scopedOwnerDemandSet G c omega A|`.
* `ComponentTransportSourceEligible` is exactly the disjunction in
  `ActiveScopedCoordinateTransport.lean`: inheritance through an intersecting
  old active component, or a new component touching an old/new changed row.
* A persistent component is used only through the already proved Lean theorem
  `activeDegree_new_le_old_of_not_touchesChangedRows`; the analogous HitNeed
  monotonicity is part of the supplied exact evidence and must be applied only
  to components avoiding the changed rows.

## Fixture / computation gate

Authoritative new evidence supplied with this retry:

* all **4,801,067** heavy N=12 tuples satisfy component transport;
* every Hall failure among them has strictly negative summed one-coordinate
  variation;
* persistent-component `activeDegree` and HitNeed are Lean-monotone.

This is consistent with the local ingredient below, but it is not evidence for
Hamming-one descent outside N=12. R29 gives a strict local minimum at N=2943:
score 30811, Hall gap 28, and all 459,004 one-row replacements have score at
least 30813. Thus any theorem extracting one negative summand globally is false.

Repository searches performed:

```text
rg -n "4801067|4,801,067|2943|heavy N12|component transport" tmp problems/23 ...
rg -l "4801067|4,801,067|component_transport|component transport" tmp ...
```

No constructor or independently runnable data artifact for fixture 2943 was
found. Therefore fixture 2943 was **not independently recomputed** here; its
numbers are cited only from `WALL_ATTACK_R29_GPTPRO56.md`. No gate result is
invented.

## Proved theorem chain

Artifact `AmortizedOwnerShore.lean` contains two sorry-free proof terms:

1. `scopedObligationScore_lt_of_amortized_banks`: for arbitrary endpoints
   `omega, eta`, strict decrease of the collision bank plus nonincrease of the
   HitNeed bank implies strict scoped-score descent.
2. `scopedObligationScore_lt_of_transport_credit`: if a coordinated trade has
   owner-shore collision credit strictly larger than its nonpersistent
   activation cost, and its HitNeed bank does not increase, then the endpoint
   has smaller scoped score.

This permits intermediate choices to have larger score and hence does not
contradict R29. It is the correct endpoint wrapper for an unbounded simultaneous
trade.

### Build outcome

Command:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\problems\23\lean'
C:\Users\a\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe env lean E:\Projects\ErdosProblems\tmp\fanout\global_min_proof\owner_shore_transport\AmortizedOwnerShore.lean
```

Exact outcome: failure before elaboration because
`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedVariationReduction.olean` does
not exist. Building that dependency would write outside the assigned directory,
which the worker contract forbids. Full stderr is in `lean_build.txt`. Hence the
two proof terms are written but **not compiler-verified in this worker**.

## Conjectural lemma: the only proof gap

**Amortized owner-shore trade construction.** Given a Hall-failing `omega` and a
deficient owner shore `A`, there exist a finite set of coordinates and simultaneous
replacement rows producing `eta`, together with a component-owner transport,
such that:

1. every component persistent through the whole trade is charged using
   `ComponentTransportSourceEligible`; its active degree and HitNeed contribution
   do not increase;
2. every component that touches a changed row is paid from a distinct unit of
   accumulated shore transport credit;
3. total collision credit is strictly greater than the activation cost of all
   such nonpersistent components.

Items (1) and the endpoint arithmetic are proved/local. Items (2)-(3) are open.
They require an amortized injection across the union of changed rows. Per-row
injections cannot simply be summed because their targets may collide; R29's
selector cage is exactly this obstruction. A proof must cancel/reuse transport
targets only after the full coordinated trade, and may allow every proper prefix
to increase the score.

If this lemma holds, `scopedObligationScore_lt_of_transport_credit` yields an
endpoint `eta` of lower score, so a global scoped-score minimizer cannot fail
Hall. No Hamming-one claim is used.

## SHA-256

Inputs relied on:

```text
533cd8772b6f0cd8f667e3388b7baba9a0734f862e41cb01cd6958ac2c296003  tmp/fanout/global_min_proof/COMMON.md
fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04  problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md
f3ffd8b22edd2de55d53664f20b77651df4b35033ba3e1ecb5d029aa11f8a921  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedVariationReduction.lean
6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedCoordinateTransport.lean
```

Artifacts created (hashes before creation of this self-referential report):

```text
3789ad3459c7587c5869410712afb347aa2dc1567d438affe33a4c0824cd6e6e  AmortizedOwnerShore.lean
cde3e015cd41618c75115cd11fa45de8cdb2358bbb89b3e58bd33627b2b968ac  lean_build.txt
```

The SHA-256 of `RESULT.md` itself is reported in the worker handoff because a
file cannot contain its own cryptographic hash without changing it.
