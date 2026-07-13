# R40 strong-probe audit and R41 support monotonicity

## Verdict

I did not prove the requested existential lemma and did not find an exact real
counterexample.  The new singleton-slack reduction is valid and reduces an
all-weak probe rectangle to an entire cut-tight neighbour class, but the
stated hypotheses do not yet supply the needed implication

```text
cut-tight active/support neighbour class
  -> checked row detour or compatible unused source.
```

The exact `N<=10` gate remains positive: all 50,104 tuples and all 5,025
literal `ActiveOwner` occurrences have a strong free probe or a covered pair.
That is finite evidence, not a proof of the missing implication.

The R41 monotone-support observation is proved below.  It eliminates the
multiplicity-saturated neutral rotor from R38: a neutral cycle can contain
only support-preserving detours, and every such detour creates free ordered
halves at its disappearing middle.  The only surviving equality case is a
source-swap rotor whose target matching consumes or coherence-blocks every
created key.

## 1. Exact all-weak reduction

Write

```text
s(z) := sigma({z}) = dB(z)-dM(z).
```

Maximum-cutness gives `s(z)>=0`, integrally, for every vertex.  Let `v` be an
`ActiveOwner`, let `X` be its active off-support blue neighbours, and let `Y`
be its selected-support blue neighbours.  If `x in X`, `y in Y`, and `x!=y`,
then triangle-freeness forbids `xy`: both are blue neighbours of `v`, so an
edge `xy` would complete a triangle.  The two-vertex cut identity therefore
has no internal-edge correction and gives

```text
sigma({x,y}) = s(x)+s(y).                            (1)
```

Suppose every free cross-pair is weak and no cross-pair is covered.  Then
`s(x)+s(y)<=1` for every `(x,y) in X x Y`.  If some `x` and some `y` both had
positive singleton slack, integrality would give a sum at least two.  Hence

```text
(forall x in X, s(x)=0) or (forall y in Y, s(y)=0).  (2)
```

This is sharp: the R36 probe `(0,5)` has singleton slacks `(1,0)` and pair
slack one.  Neither maximum-cutness nor pooling strengthens (2).

If a cross-pair is covered, the old local geometry is sound independently of
slack.  A covering induced shortest row cannot place `x,y` at distance four
(the path `x-v-y` is shorter) or at odd distance (cut parity).  Their row
distance is exactly two; triangle-freeness puts `v` outside that row, and
replacing the middle by `v` is a distinct four-blue-edge row.  Completeness of
the row database supplies the genuine detour row.

Thus the only missing case is exactly (2) together with every cross-pair
free.  Canonicality has not yet been connected to that cut-tight class.

## 2. Incidence pressure in the tight active class

There is a useful exact consequence when the first alternative of (2) holds.
For a tight active neighbour `x`, let `e(x)=dM(x)` be the number of selected
rows in which `x` is a bad endpoint, and let `i(x)` count selected rows in
which `x` is internal.  Endpoint anchoring gives exactly `e(x)` endpoint
occurrences.  Their path-edge incidences at `x`, together with the internal
occurrences, total

```text
e(x) + 2 i(x).
```

Since `s(x)=0`, `dB(x)=e(x)`.  At least one blue edge at `x` is active and
therefore absent from selected support, so at most `e(x)-1` distinct support
edges carry those incidences.  Consequently

```text
sum_u max(0, pairCount(x,u)-1) >= 2 i(x)+1.          (3)
```

In particular every tight active neighbour carries a repeated support label
and positive collision pressure.  Equation (3) is the correct start of a
label-purification chase.  What is still missing is a theorem that the chase
must meet the original probe rectangle or expose a compatible unused half;
coherence can send every repeated base to another active component.

The second alternative of (2), a wholly tight support-neighbour class, does
not even give (3) directly: a tight support neighbour may be a bad endpoint
whose sole support incidence is the edge to `v`.  This is the sharper
remaining subcase.

## 3. Monotone support for genuine detours

Consider a genuine detour replacing

```text
Q  = (..., x,m,y, ...)
Q' = (..., x,v,y, ...),
```

with all other row vertices and all other selected rows fixed.  The new edges
`xv,vy` are active before the move, hence neither belongs to the old selected
support.  The only support edges that can disappear are `xm,my`.  Therefore

```text
|support(omega')| >= |support(omega)|.               (4)
```

Moreover equality in (4) holds exactly when both old edges disappear, which
is equivalent to each having selected-row multiplicity one.  For induced
length-five rows this is

```text
pairCount_omega(m,x)=pairCount_omega(m,y)=1.          (5)
```

If either multiplicity is at least two, that old edge remains in support and
at least one of the genuinely new edges increases support strictly.

Now take a directed cycle of neutral detours.  Summing (4) around the cycle
forces equality on every edge.  Hence every transition satisfies (5).  After
the replacement, the ordered bases `(m,x)` and `(m,y)` have count zero, so
both ordered halves of each base are newly free (subject only to the target
state's reservation/relation/coherence filters).  Thus R38's proposed
`n(m,z)>=2` multiplicity-saturated rotor cannot be a neutral cycle.

The exact surviving obstruction is narrower:

```text
source-swap rotor = every neutral edge preserves support,
                    every disappearing-middle key is newly free,
                    every such compatible key is consumed or blocked
                    by the target state's own optimal matching.
```

Support monotonicity proves creation; it does not prove that a created half is
compatible with the deficient shore or unused in the independently chosen
target matching.

## 4. Counterexample search audit

Two independent bounded searches were run beyond the stated `N<=10` gate:

1. Random connected bipartite blue cores of orders `11..14`, same-shore bad
   pairs, exhaustive maximum-cut checks, complete row reconstruction, and up
   to 500 tuples per retained graph.
2. A native search over orders `11..16` with exhaustive cut checks and the
   same active/support probe test.

An apparent `N=14` all-weak state was rejected on replay: its generator had
enumerated four-edge walks but had not excluded a shorter two-edge blue path.
The alleged bad edges therefore lay in triangles.  It is not a real cage and
is not retained as evidence.  After imposing `dB=4` explicitly, no witness
was found in the bounded runs.  These nonfindings are not an exhaustive
`N>=11` census.

## 5. Remaining exact lemma

The next proof obligation should be stated without the now-dead saturated
case:

```text
tightClass_sourceSwap_escape:
  at a canonical positive-defect real tuple, if an ActiveOwner's entire
  probe rectangle is free and one neighbour class is singleton-tight, then
  the endpoint-incidence chase from (3) reaches either
    (a) a strong compatible free base,
    (b) a support-increasing detour, or
    (c) a support-preserving detour whose newly free disappearing-middle
        half is compatible and unused in the target deficient shore.
```

Cases (a) and (b) give immediate checked progress; (c) excludes the remaining
source-swap rotor.  Proving only that a half is newly free is insufficient,
because target-state matching consumption and component-label coherence are
per-state.
