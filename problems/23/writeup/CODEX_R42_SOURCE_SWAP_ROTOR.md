# R42 residual source-swap rotor (superseded as the live R37 surface)

> **Live-surface correction, 2026-07-11.**  This note analyzes a conditional
> detour class in which both entering edges are absent from selected support.
> The exact N<=12 R37 census found zero attachment detours with that premise.
> In the actual R37 construction, `xv` is active/new but `vy` is already a
> selected-support edge.  Across 7,600,710 genuine detours,
> `genuinelyNewEdges=1` and support delta has histogram
> `-1:3,364,027`, `0:3,066,915`, `+1:1,169,768`.  Therefore support is not
> monotone and the two-new-edge source-swap model below is not the live wall.
> The identities remain valid only under their explicitly stronger premise.

## Reduction from support monotonicity

For a two-edge detour

```text
Q  = (a,x,m,y,b)
Q' = (a,x,v,y,b),
```

the new edges `xv,vy` are active before the move and therefore absent from
selected support. Replacing `Q` adds both. Only `xm,my` can disappear, so
selected-support cardinality never decreases.

Hence every transition on a directed neutral cycle must preserve support
cardinality. Both old edges are then unique selected-row occurrences:

```text
pairCount(m,x) = pairCount(m,y) = 1.
```

The multiplicity-saturated R38 rotor is therefore impossible. Every surviving
cycle is fully unsaturated on its two square edges.

## Exact source swap

At a support-constant transition, the target tuple frees the four ordered
pairs

```text
(m,x), (x,m), (m,y), (y,m),
```

and covers the analogous four ordered pairs through `v`. Each ordered pair has
two physical half keys before reservation filtering. The total physical free
key count can therefore remain constant: the transition swaps old `v` keys
for new `m` keys.

The diagonal `(m,m)` is not a `FreeHalf` in the production API because
`FreeHalf.distinct` requires distinct coordinates; it must not be counted as
Exposure.

When `xm` or `my` becomes an active edge, its half-zero orientation may be
`ScopedReserved`; only the exact production relation and component label decide
which of the newly free halves are usable. Thus “new key” alone does not imply
augmentation.

## Remaining falsifier shape

A genuine zero-Exposure counterexample must provide a finite directed SCC of
defect-minimal row tuples and optimal coherent matchings such that every edge:

1. is a support-constant two-edge detour;
2. swaps the four ordered middle-endpoint bases above;
3. immediately matches or component-blocks every newly usable physical half;
4. has no production common-blue probe with `sigma >= 2`;
5. has no strict defect trade and no rank-checked lex trade leaving the SCC.

Weak probes with `sigma` zero or one are not production common-blue sources.
The exhaustive `N<=12` gate contains 229 such probes but zero positive-defect
canonical states.

The historical conditional target was:

```text
NoPositiveDefectSourceSwapRotor:
  no real triangle-free connected maximum-cut cage with complete anchored
  shortest rows admits the zero-Exposure SCC above.
```

This statement is strictly narrower than R38's saturated-rotor lemma and is
not the current target.  The live target is the four-state,
family-alternating R37/R39 rotor with one genuinely new edge per attachment
detour and even owner fibers.
