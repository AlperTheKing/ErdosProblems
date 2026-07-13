# R38: weak-free sigma gap and label purification

## Verdict

The proposed global surplus-pooling repair is false.  If a probe at owner
`v` returns a free pair `x,y` with `0 <= sigma({x,y}) < 2`, maximum-cut lock
does force a neutral singleton switch among `x,y`.  It does not turn the pair
into a production common-blue source, and combining several weak pairs cannot
pay the two reserved owner edges per terminal.  The neutral singleton switch
also need not be a strict Gamma trade: the exact 20-vertex R36 witness rotates
one bad edge around a C5 and leaves Gamma unchanged.

Thus weak-free cannot be removed from the local outcome list by max-cut
surplus aggregation.  A proof may still show that among *all* probes of an
owner, one is strong (`sigma >= 2`) or is a detour.  That stronger existential
statement has no counterexample in the exact N <= 10 scan below, but it is not
proved here.

This correction precedes label purification: a weak-free pair supplies no
edge in `CommonBlueExtendedMatching`, so there is no physical half to purify
by active-component label.

## 1. Exact lock identity

Let `v` be the scoped owner.  Every active neighbour `x` and selected-support
blue neighbour `y` of `v` lies in `N_B(v)`.  Triangle-freeness makes
`N_B(v)` an independent set in the full graph.  Hence, for every finite
`U subseteq N_B(v)`,

```text
sigma(U) = sum_{z in U} sigma({z}).                    (1)
```

Indeed, the usual cut identity subtracts twice the signed weight of edges
internal to `U`, and there are no such edges.  Maximum-cutness gives
`sigma({z}) >= 0` for every `z`, and all values are integers.

For a weak free pair,

```text
sigma({x}) + sigma({y}) = sigma({x,y}) in {0,1}.       (2)
```

Consequently at least one endpoint has singleton surplus zero.  If the pair
has surplus zero then both endpoints do.  This is the complete conclusion of
max-cut lock equality: flipping a zero-surplus endpoint gives another maximum
cut.

## 2. Pooling cannot create production terminals

`CheckedC5BaseTransfer.TerminalData.Valid` requires

```text
2 <= sigma({x,y}).
```

The two units reserve the blue owner edges `x-v` and `y-v`.  This predicate is
local to the physical base `(x,y)`; surplus on another pair cannot make it
true.

Even under a hypothetical pooled ledger, take `k` vertex-disjoint weak pairs
inside `N_B(v)`.  By (1),

```text
sigma(union of the 2k endpoints)
  = sum_i sigma(pair_i)
  <= k < 2k.
```

The pooled switch therefore has less than the `2k` units needed to reserve
the `2k` distinct owner edges.  Its total adjusted surplus is at most `-k`.
Shared endpoints reduce both the union surplus and the number of distinct
owner edges, but do not make any individual weak base satisfy the compiled
terminal predicate.  Therefore neither physical-half deduplication nor
component labelling repairs the sigma deficit.

## 3. Exact real neutral-switch refutation

Use the graph, cut, complete rows, and selected tuple from
`tmp/fanout/r36_freepair_proof/REPORT.md`.  At owner `v=7`, the probe
`x=0,y=5` has

```text
pairCount(0,5) = 0,
sigma({0}) = 1,
sigma({5}) = 0,
sigma({0,5}) = 1.
```

Thus vertex `5` is the neutral singleton forced by (2).  Flip only vertex
`5`.  The cut still has 20 blue edges, while the bad set changes exactly from

```text
{01, 56, 10-11, 15-16}
```

to

```text
{01, 57, 10-11, 15-16}.
```

Every bad edge still has blue distance four, so before and after the switch

```text
Gamma = 4 * 5^2 = 100.
```

This is a C5 bad-edge rotation, not a strict Gamma trade.  It is also not a
`CheckedCollisionDefectTrade` in the current canonical modules: those fix
`G,c,bads` and vary only `RowChoice bads`, whereas the singleton switch changes
both `c` and the bad-edge carrier.

The same state has other strong probes, so it is not a counterexample to the
stronger assertion that *some* probe at every owner is strong or a detour.  It
is an exact refutation of the proposed implication

```text
weak-free + max-cut lock equality
  => legal common-blue source or strict switch trade.
```

## 4. Exact finite search for the surviving target

An integer-only scan used the pinned graph/cut/row reconstruction in
`p5_core.py` and enumerated all 50,104 row tuples of every eligible connected
triangle-free all-length-five system of orders 5 through 10.  For each
positive-collision active owner it enumerated every pair

```text
x = active off-support neighbour of v,
y = selected-support blue neighbour of v,
x != y.
```

It classified `pairCount(x,y)>0` as detour, a free pair with
`sigma(x,y)>=2` as strong, and a free pair with sigma zero or one as weak.
Results:

```text
row tuples checked                         50,104
owners for which every probe was weak           0
states for which every owner probe was weak      0
```

This is falsifier evidence only.  It does not prove the existential theorem,
and it does not cover N >= 11 or the large cages.

## 5. Corrected frontier

The local result must retain four outcomes:

```text
strong free: pairCount=0 and sigma>=2  -> common-blue terminal;
weak free:   pairCount=0 and sigma<2   -> neutral singleton exists only;
detour:      pairCount>0               -> alternative complete row;
impossible separation-four branch.
```

There are two honest routes forward.

1. Prove the stronger all-probes lemma: every active collision owner has at
   least one strong free probe or one detour probe.  The N <= 10 scan supports
   this exact statement.  The proof must compare all active and support
   neighbours; choosing one arbitrary pair is insufficient.

2. Enlarge the canonical state space to include maximum cuts and prove that a
   zero-surplus singleton switch gives strict decrease in a secondary
   invariant.  Gamma alone cannot be that invariant, by Section 3.  The
   current `CanonicalCollisionProgress` API cannot consume such a cut switch.

Until one route is proved, neither `attachmentStep_total` nor the reduction
to a positive-defect sink neutral attachment SCC is valid.  Label-purified
Hall expansion applies only after every local probe has produced an actual
source or a checked neutral row transition; weak-free presently produces
neither.
