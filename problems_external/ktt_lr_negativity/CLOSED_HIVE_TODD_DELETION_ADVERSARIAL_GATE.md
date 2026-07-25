# Adversarial gate for CLOSED-HIVE-TODD-DELETION

Date: 2026-07-22

## Verdict

The requested finite falsification gate is **not yet well-defined**.  No
coarsening was enumerated and no Farkas LP was solved.  Doing either would
require choosing mathematical definitions that are absent from the direct
route and would therefore test an invented move rather than
`CLOSED-HIVE-TODD-DELETION`.

This is a definition-level stop, not a computational `NO_HIT`.

## First missing object: the move

The registry refers to an "admissible rank-reducing planar ear/strip deletion"
but supplies none of the data needed to decide whether a coarsening admits
one.  A falsification predicate requires, at minimum:

1. the finite labelled subcomplex that is called an ear or a strip;
2. the allowed incidences of that subcomplex with the rest of the triangular
   hive complex;
3. the exact cells/rhombi removed or contracted;
4. the induced map from the old flat-rhombus set to the new one;
5. the boundary update and the proof that the output is again a hive
   coarsening;
6. the condition called "admissible"; and
7. the rank statistic that must strictly decrease.

Without these items, "has no admissible deletion" is not a decidable
statement, so exit condition 1 in the registry cannot be tested.

## The coarsening class is also not specified

The phrases "closed flat-rhombus coarsening", "primitive-interior",
"2-connected", and "minimal" are not defined as finite predicates.  The
following choices materially change the enumeration:

- whether closure means all exact nonnegative linear implications among
  rhombus slacks, all implications valid for a fixed boundary, or a local
  combinatorial propagation rule;
- whether realizability means existence of some real hive, some rational
  hive, an integral partition boundary, or a relative-interior witness having
  exactly the prescribed zero slacks;
- which planar graph is tested for 2-connectivity;
- what primitive-interior excludes; and
- the partial order under which a realizable closed coarsening is minimal.

Consequently there is presently no canonical finite set described by
"realizable minimal closed coarsenings".

## The Farkas system is underdetermined

The displayed formula

```text
W_q(Sigma) = {w >= 0 : partial_q w = 0}
```

does not define `partial_q`.  An exact rational matrix requires:

1. the oriented basis `Sigma(q)` and the oriented target basis `E_q`;
2. the incidence convention;
3. the intrinsic lattice attached to every cone and face;
4. the lattice-index factors in each incidence coefficient; and
5. whether `Sigma` is a complete fan, a local normal complex, or a
   coarsening of a specified complete fan.

The Todd vector is likewise not determined until the complement map, normal
versus feasible-cone convention, and intrinsic quotient lattice are fixed.

There is an additional logical ambiguity.  The prose calls `W_q(Sigma)` the
cone of "balanced realizable" face weights, but nonnegativity and the
Minkowski boundary equations alone define all nonnegative balanced weights.
If realizability is a proper additional restriction, its exact equations or
inequalities are missing and ordinary rational Farkas duality does not apply
to the displayed cone as written.  If every balanced weight is intended,
"realizable" must be deleted and the stronger theorem stated explicitly.

## Missing deletion algebra

Even after defining the two complexes, the proposed induction cannot be
tested until it provides:

- a rational chain map between their boundary complexes;
- a lift from `W_q(Sigma')` to `W_q(Sigma)`;
- an exact finite list of local star/corridor generators, including their
  orientations and lattice normalizations; and
- the formula expressing the old Todd pairing as the lifted pairing plus
  local corrections.

These data are precisely what would make "a correction necessarily has a
negative generator" an exact finite certificate.  None currently appears in
the registry or the cited project audits.

## Smallest sufficient input contract for a genuine gate

A future adversarial run can start as soon as one candidate move is supplied
as the following rank-independent tuple:

```text
(pattern, embedding predicate, closure operator, realizability predicate,
 deletion map, rank statistic, chain bases, partial matrices,
 intrinsic-lattice maps, Todd convention, lift matrix,
 local-generator matrix, correction identity)
```

Each entry must be an exact combinatorial or rational-linear definition.  The
smallest-rank embeddings of that tuple can then be enumerated, exact closure
and realizability witnesses can be checked, and the rational alternatives

```text
a_q + partial_q^T y >= 0
```

or

```text
w >= 0,  partial_q w = 0,  <a_q,w> < 0
```

can be certified by exact primal/dual witnesses.

Until that tuple exists, any enumeration or LP would violate the direct-proof
guard by replacing the frontier lemma with an arbitrary finite model.
