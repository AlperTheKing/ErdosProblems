# K2T Interval Hall Proof Target

This note records the current broad replacement for the special star-door
residue proof.  It targets arbitrary neutral terminal-shadow switches, not only
the selected seed+moat switches.

## Setup

Let `S` be a neutral terminal-shadow switch in a connected-`B` maximum cut.
Write

```text
C = delta_M(S)
E = delta_B(S)
```

with `|C|=|E|`.  For `f in C`, orient every shortest `B`-row of `f` from the
endpoint inside `S`.  Terminal-shadow validity says the row meets `S` in an
initial segment and exits through a unique `e in E`.

Define the witness relation

```text
f ~ e  iff  some shortest row of f exits S through e.
Wit(f) = { e in E : f ~ e }.
```

The remaining matching target is Hall on the exit side:

```text
|{f in C : Wit(f) subset Y}| <= |Y|     for every Y subset E.
```

## Lemma 1: Interval Reduction

Assume there is an order `<` of `E` such that every `Wit(f)` is a consecutive
interval in that order.  Then it is enough to prove Hall for consecutive
intervals `Y`.

Proof.  Decompose an arbitrary `Y subset E` into its maximal consecutive
blocks

```text
Y = I_1 disjoint union ... disjoint union I_k.
```

If an interval `Wit(f)` is contained in `Y`, then it is contained in one block
`I_j`; otherwise it would contain a gap between two blocks.  Hence

```text
C(Y) = disjoint union_j C(I_j),
```

where `C(I)={f: Wit(f) subset I}`.  If `|C(Y)|>|Y|`, then
`|C(I_j)|>|I_j|` for some block.  Thus every Hall violation has a consecutive
interval violation.

## Lemma 2: Interval Hull Side-Door

For every consecutive interval `Y subset E`, put

```text
X = { f in C : Wit(f) subset Y }.
```

Let `U0` be the union of all terminal prefixes inside `S` of all shortest rows
of all `f in X` exiting through exits in `Wit(f)`.  Let `U` be the blue-closed
hull of `U0` inside `S`.

The required side-door inequality is

```text
|delta_B(U) \ Y| <= |delta_M(U) \ X|.      (IH)
```

Then max-cut gives

```text
|Y| + |delta_B(U)\Y| >= |X| + |delta_M(U)\X|.
```

Together with `(IH)`, this gives `|Y|>=|X|`, proving Hall for intervals and
therefore Hall for all exit sets by Lemma 1.

## Exact Gate

Diagnostic script:

```text
python problems/23/writeup/_codex_interval_hull_gate.py --min-n 5 --max-n 9 --cap 8
```

Result:

```text
N 5 switches 40 intervals 40 fail 0 no_order 0
N 6 switches 92 intervals 92 fail 0 no_order 0
N 7 switches 432 intervals 432 fail 0 no_order 0
N 8 switches 2464 intervals 2864 fail 0 no_order 0
N 9 switches 16048 intervals 21444 fail 0 no_order 0
slack: [(0, 21444)]
VERDICT: PASS
```

and

```text
python problems/23/writeup/_codex_interval_hull_gate.py --min-n 10 --max-n 10 --cap 8
```

Result:

```text
N 10 switches 113504 intervals 168252 fail 0 no_order 0
slack: [(0, 166110), (1, 1902), (2, 240)]
VERDICT: PASS
```

Here `slack = |delta_M(U)\X| - |delta_B(U)\Y|`.

## Proof Burden

The proof now splits cleanly into two geometric statements.

### A. No-Crossing Exit Order

For every neutral terminal-shadow switch, prove there is an order of the exits
`E` such that each witness set `Wit(f)` is consecutive.

Expected mechanism: if two shortest rows for bad edges `f,g` force a crossing
pattern

```text
e_1, e_2, e_3, e_4
with f witnessing e_1,e_3 and g witnessing e_2,e_4,
```

then the two terminal prefix systems form a theta/lens inside the old cut graph.
Splicing the lens gives either a shorter `B`-geodesic for one bad edge or a
triangle, contradicting shortestness or triangle-freeness.

### B. Interval Hull Side-Door

For a consecutive interval `Y`, prove `(IH)`.

Expected mechanism: all extra `B`-boundary edges of the blue-closed interval
hull lie at the two interval sides.  A side-door extra exit not paid by an
extra bad boundary edge would create a terminal row whose witness interval
crosses from outside `Y` into `Y` and back out.  The same lens splicing gives a
shorter bad-edge row or a forbidden triangle.

Unlike the refuted hereditary leakage inequality, `(IH)` is only required for
consecutive intervals in a no-crossing exit order.  The exact gate shows it is
false neither on arbitrary neutral terminal-shadow switches through `N<=10` nor
on any interval produced by the brute consecutive-ones orders.

## 2026-06-30 Guardrail: Arbitrary H-Blowup Neutral Masks Are Too Broad

The `N<=10` arbitrary neutral-terminal-shadow census passes `(IH)`, but the
statement is false if extended to all neutral terminal-shadow masks in the
`H?AFBo][2]` all-max blowup.

Direct call of `_codex_interval_hull_gate.scan_graph` on all `H?AFBo][2]`
neutral terminal-shadow masks gives:

```text
switches 617
intervals 2641
fail 1
slack {0:684, 1:148, 2:276, 3:460, 4:592, 5:480, -1:1}
first failure:
  side 001111111111100000
  S=(0,1,12)
  Y=((0,10),(0,11),(12,16),(12,17))
  X=((0,13),(2,12),(3,12),(4,12),(5,12))
  extra_B=((1,10),(1,11))
  extra_M=((1,13),)
  slack=-1
```

Thus the proof must not state `(IH)` for every neutral terminal-shadow switch
in arbitrary blowups.

Restricting to the completed seed+moat switches selected by `R[v]<0` in the
same `H?AFBo][2]` battery restores the gate:

```text
switches 98
intervals 378
fail 0
no_order 0
slack {0:98, 1:26, 2:68, 3:68, 4:54, 5:64}
VERDICT: PASS
```

So the live interval theorem should be stated for the selected
negative-residual seed+moat family, or with an equivalent geometric hypothesis
capturing that selector. The selected-family strengthening also has a sharper
observed invariant: the complements `E \ Wit(f)` are pairwise laminar in all
`119/119` selected switches, while this complement-laminar statement fails for
one arbitrary `N=10` neutral terminal-shadow switch.

## Selected-Family L1': Two-Leaf Missed-Exit Laminarity

For the selected negative-residual seed+moat switches, a sharper form of the
no-crossing order appears to hold.

For `f in C=delta_M(S)`, define the missed-exit set

```text
Miss(f) = E \ Wit(f).
```

Exact selected-family gate on census plus `H?AFBo][2]` all-max switches:

```text
switches 119
pairwise-laminar Miss(f): 119/119
nonempty Miss-size signatures:
  ()        : 39
  (3,3)    : 29
  (1,1)    : 27
  (1,1,2)  : 12
  (1,)     : 8
  (2,)     : 4
```

Thus the nonempty missed-exit sets form a laminar family with at most two leaf
branches.  Geometrically these are the two terminal side caps of the completed
seed+moat switch.  The observed cases are:

* no side cap;
* one side cap;
* two disjoint side caps;
* two singleton side caps plus their union.

This immediately gives a consecutive exit order for the selected family: put
one leaf branch at the left end of the exit order, the other at the right end,
and put all universal exits in the middle.  Then every complement
`E \ Miss(f)=Wit(f)` is a consecutive interval.

It also gives a Hall-critical reduction in complement form.  Put

```text
A(Z) = { f in C : Wit(f) cap Z = empty }
     = { f in C : Z subset Miss(f) }.
```

Hall is equivalent to

```text
|A(Z)| + |Z| <= |E|      for every Z subset E.
```

If this fails for some `Z`, enlarge `Z` to the intersection of all `Miss(f)`
that contain it.  By laminarity this enlarged set is itself one of the laminar
missed-exit nodes and keeps the same counted family `A(Z)` while increasing
`|Z|`.  Therefore a Hall failure would be witnessed by a laminar side-cap node.
The complement of such a node is consecutive in the left-middle-right exit
order, so the interval hull side-door lemma applies.

Proof burden for L1' is therefore geometric and selected-family-specific:

```text
TWO-LEAF MISSED-EXIT LAMINARITY.
In a completed seed+moat switch selected from R[v]<0, the sets Miss(f) are
laminar and their laminar tree has at most two leaves.
```

Expected shortening proof: if two missed-exit sets cross, choose exits
`e in Miss(f)\Miss(g)`, `e' in Miss(g)\Miss(f)`, and `h in Miss(f) cap Miss(g)`.
Then rows of `f` and `g` witnessing the side exits `e'` and `e` but avoiding
`h` form two terminal lenses around the common skipped exit.  Splicing the two
lenses either produces a shorter `B`-geodesic for one bad edge or a triangle.
A third leaf branch similarly gives three mutually separated side doors; the
single seed+moat corridor has only two terminal sides, so two branches splice to
make a shorter lens.  This is the precise uncrossing step still to formalize.
