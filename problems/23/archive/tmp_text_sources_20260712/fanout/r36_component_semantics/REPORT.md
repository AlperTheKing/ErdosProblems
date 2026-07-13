# Component-labelled virtual keys at the R37 sink

## Verdict

Component labelling gives an exact reparameterization of coherent matching,
but it does **not** turn the problem into an ordinary capacitated flow.  The
required constraint is a disjunctive activation law: for each physical base,
at most one component-copy may be active, after which its two half slots have
unit capacity.  That law is not a partition-matroid capacity, its rank is not
submodular, and its natural LP relaxation is fractional.

Consequently, saturation of every physical common-blue/detour half exposed by
an attachment class can coexist with positive coherent defect.  Saturation is
then a Hall obstruction, not an augmentation.  The three-obligation example
below is an exact one-state sink countermodel to the implication

```text
physical source saturation + base-component coherence => augmentation.
```

It is not a counterexample to the graph-facing R37 lemma: R37 additionally
requires the production triangle-free/max-cut/complete-row geometry, and
`CheckedSinkNeutralAttachmentClass` is not yet defined in the Lean tree.
Thus component semantics alone neither proves nor refutes the full real lemma.
It reduces that lemma to the explicit label-purified expansion statement in
Section 6.

## 1. Exact virtual-key equivalence

Fix a row state `omega`.  Write

```text
D                 obligations at omega
B                 physical ordered-pair bases
H = {0,1}         half bits
C                 active-component labels
kappa : D -> C    obligation component
E subset D x (B x H)
                  graph-realized source relation
```

Replace every physical half `(b,h)` by virtual keys

```text
V = B x C x H,
```

and join `d` only to `(b,kappa(d),h)` when `(d,(b,h))` belongs to `E`.
A virtual assignment `m` is valid exactly when it is injective and satisfies

```text
(ACT_b)  |{c : some assigned key has the form (b,c,h)}| <= 1
```

for every `b`.  Erasing the component coordinate maps such an assignment to
an injective physical-half assignment satisfying
`Pattern5StaticOwnership.BaseKeyComponentCoherent`.  Conversely, adding
`kappa(d)` to every assigned physical key gives a virtual assignment satisfying
`ACT_b`.  These maps are inverse.  Hence this is an exact reparameterization
of `CoherentPartialMatching`, including the concrete adapter's physical
`SourceBase x Fin 2` keys.

This also separates two similarly named laws in the current modules.
`CheckedMicroReservationLedger.BaseKeyComponentCoherent` says that serialized
source entries sharing a base have one component.  The collision defect uses
the assignment-level law from `Pattern5StaticOwnership`; the equivalence above
is for that latter law.

## 2. Why the capacity is not a flow capacity

For a fixed base `b`, activating component `c` opens two unit slots
`(b,c,0)` and `(b,c,1)`.  A linear integer formulation needs activation bits:

```text
x[d,b,c,h] <= z[b,c]
sum_c z[b,c] <= 1
sum_d x[d,b,c,h] <= 1
z[b,c] in {0,1}.
```

Replacing integrality by `0 <= z <= 1` permits two components to use one half
each with `z=1/2`; it is not the physical problem.  A shared capacity
`sum_{c,h,d} x <= 2` is also wrong because it permits mixed components.

The induced local capacity on a set `S` of virtual half keys is

```text
q_b(S) = max_c |{h : (b,c,h) in S}|.
```

It is not submodular.  With keys `A0,A1,B0`, put

```text
P={A0,B0}, Q={A1,B0}.
q(P)=q(Q)=1, q(P union Q)=2, q(P intersection Q)=1,
```

so `q(P)+q(Q)=2 < 3`.  Therefore this coupling is not a polymatroidal edge
capacity either.  Component splitting followed by `ACT_b` merely relocates
the non-submodularity found in R35; it does not remove it.

## 3. Exact fixed-label Hall decomposition

Let a total base labelling be `lambda : B -> C`.  Define the ordinary
bipartite graph `G_lambda` with right vertices `B x H` and edge

```text
d -- (b,h)  iff  kappa(d)=lambda(b) and (d,(b,h)) in E.
```

Every coherent matching extends to at least one `lambda` by labelling each
used base with its forced component and choosing arbitrary labels on unused
bases.  Every matching in `G_lambda` is coherent.  Therefore, exactly,

```text
nu_coh = max_lambda nu(G_lambda),

Delta(omega)
  = |D| - nu_coh
  = min_lambda max_{X subset D} (|X|-|N_lambda(X)|).
```

The empty shore makes the inner maximum nonnegative.  For a *fixed* `lambda`,
ordinary Hall, alternating paths, uncrossing, and max flow are all valid.  The
outer maximum over labels is the non-flow, non-submodular part.  In particular,
a maximum of the submodular matching-rank functions indexed by `lambda` need
not be submodular.

This is the strongest exact flow reduction supplied by component semantics:
enumerate or otherwise choose the base labels first, then run ordinary flow.

## 4. Saturated positive-defect sink

Use one physical base `b`, components `A,B`, and obligations

```text
x1,x2 : component A
y     : component B.
```

Let every obligation realize both physical halves `(b,0),(b,1)`.  Match

```text
x1 -> (b,A,0),  x2 -> (b,A,1),
```

and leave `y` unmatched.  Both physical halves are saturated.  The virtual
keys `(b,B,0)` and `(b,B,1)` are unoccupied but unavailable: activating either
would violate `ACT_b`.  Relabelling `b` from `A` to `B` can match `y` only by
evicting both `x1,x2`, so it cannot augment cardinality.

Exact coherent ranks are

| obligation set | coherent rank |
|---|---:|
| `{x1,x2}` | 2 |
| `{x1,y}` | 1 |
| `{x2,y}` | 1 |
| `{x1,x2,y}` | 2 |

Make the neutral state graph a singleton and supply no detour transition.
It is a sink SCC, all two physical structured halves are occupied, and its
coherent defect is `3-2=1`.  Thus physical saturation and positive coherent
defect are exactly compatible at the matching/component interface.

Calling every `(b,c,h)` an independently available source would hide the
failure: the inactive `B` copies are conditional alternatives to the active
`A` copies, not additional physical capacity.

## 5. Consequence for the R37 claim

R37's prose theorem cannot currently be stated against a compiled type:
there is no Lean definition of `CheckedSinkNeutralAttachmentClass`, its node
data, neutral edges, or `CheckedCoherentAugmentation`.  More importantly, the
listed finite/matching axioms do not contain a cardinal expansion law that
excludes Section 4.  The local attachment dichotomy says that a common-blue
source or detour exists; it does not say that its physical base is available
under the component label forced by the current matching.

Therefore the following proposed inference is false:

```text
every attachment probe yields a physical source or neutral detour
+ every yielded physical source is occupied
+ the neutral class is a sink
=> the class contains an augmentation.
```

An occupied source may be owned by the wrong component, and following that
owner may close inside the sink without increasing matching size.  This is
precisely the activation obstruction exposed by virtual keys.

## 6. Exact sufficient replacement

The missing graph theorem can be stated without referring to a non-submodular
coherent rank.  At a node `q=(omega,M)` of a sink class, choose an unmatched
root `r` and extend the component labels forced by `M` to a total `lambda`.
Let `R` be the obligations reachable from `r` by ordinary `M`-alternating
paths in `G_lambda`.

The exact label-purified expansion target is:

```text
realSinkNeutralAttachmentClass_labelExpansion:
  if C is a production-realized sink neutral attachment class and
     0 < C.defect,
  then for some q=(omega,M) in C, unmatched root r, and labelling lambda
  compatible with M,
      |N_lambda(R)| >= |R|.
```

This implies an augmentation.  Indeed, if no augmenting path existed, every
slot in `N_lambda(R)` would be matched; alternating closure maps those matched
slots injectively into `R \ {r}`.  Hence

```text
|N_lambda(R)| <= |R|-1,
```

contradicting label expansion.  The resulting alternating path is an ordinary
augmentation in `G_lambda`, and the fixed-label equivalence makes it a checked
coherent augmentation.

Equivalently, the full R37 lemma needs a graph proof that some node in every
positive-defect sink defeats the wrong-component activation block.  It may do
so by producing enough common-blue bases already carrying the root component,
an unused base, or a neutral detour to a node where one of those conditions
holds.  Mere saturation of the unlabelled physical halves is insufficient.

## Exact answer

Yes: saturation of all structured physical common-blue/detour sources in a
sink SCC can coexist with positive coherent defect under the present
component/matching semantics; Section 4 is the minimal exact witness.  No:
this does not yet refute `realSinkNeutralAttachmentClass_hasAugment` with its
intended real-graph hypotheses.  The exact remaining statement is the
label-purified expansion theorem above, or an equivalent graph theorem that
forces an unused compatible-labelled half somewhere in the sink class.
