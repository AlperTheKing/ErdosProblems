# No-Naked-Leaf RFC Target

This is the live row-side geometry target after the hard `h_blowup(3)` side
falsified component-local single-miss / no-two-hole.

The exact residual Hall conclusion survives.  The proof route is now:

```text
NL no-naked-leaf
=> RFC: no reduced deficient multidoor fan core
=> Extra-door Hall for the blue-closed prefix hull
=> residual Hall
=> stage-0 residual matching exists.
```

The finite cardinal bridge is machine-checked in:

```text
problems/23/lean/ResidualHallScratch.lean
```

In particular, the NL finite-descent wrapper is machine-checked there as

```text
no_reduced_deficient_of_reduced_descent
no_hall_deficient_set_of_reduced_descent
```

So the remaining non-formal content is only the geometry that turns a reduced
positive-Euler fan core into a strictly smaller reduced deficient core.

There is also a separate extra-charge wrapper in the same Lean file:

```text
no_hall_deficient_set_of_reduced_extra_charge
```

That is an alternate route requiring cardinal extra-charge inequalities on
reduced cores.  It is not part of the NL finite-descent route below.

So this file isolates only the remaining geometric statement.

## Setup

Work in one completed terminal-shadow switch `S`.

Let

```text
C = delta_M(S)       crossing old bad edges,
E = delta_B(S)       old blue boundary exits.
```

For `f in C` and `e in E`, write

```text
Wit(f,e)
```

when `e` is the first exit of a shortest blue row of `f` through `S`.
For such a witness, let

```text
Pref_S(f,e)
```

be the terminal prefix inside `S` from the `S`-endpoint of `f` to the inner
endpoint of `e`.

For any nonempty `X subset C`, set

```text
Y = Wit(X) = union_{f in X} Wit(f),

U0 = union_{f in X, e in Wit(f)} Pref_S(f,e),

U = cl_B^S(U0),
```

where `cl_B^S` is the union of all blue connected components of `B[S]` meeting
`U0`.

Define the extra boundaries

```text
B+ = delta_B(U) \ Y,
M+ = delta_M(U) \ X.
```

For `g in M+`, orient `g` from its endpoint in `U` to its endpoint outside
`U`.  Define the door set

```text
D_U(g) = {
  e=xy in B+ :
    x in U, y notin U, and some shortest blue row Q of g
    has Q cap U equal to the initial segment ending at x
}.
```

The extra-door graph is the bipartite graph

```text
D_X = (B+, M+),     e ~ g iff e in D_U(g).
```

## RFC

The reduced fan-core statement is:

```text
For every nonempty Z subset B+,
if every g in N_D_X(Z) has at least two Z-doors,
then |N_D_X(Z)| >= |Z|.
```

Equivalently, there is no reduced deficient `Z` with

```text
|N_D_X(Z)| < |Z|,
and
|D_U(g) cap Z| >= 2 for every g in N_D_X(Z).
```

This is exactly what `_rfc_gate.py` tests.

The gate includes singleton `Z`.  Thus an isolated extra door

```text
e in B+ with N_D_X({e}) = empty
```

is treated as a reduced deficient core and is an immediate RFC falsifier.

## NL: The Geometric Atom To Prove

Assume for contradiction that a reduced deficient `Z` exists.

Let

```text
H = N_D_X(Z).
```

For each `g in H` and `e in D_U(g) cap Z`, choose one shortest row

```text
Q(g,e)
```

whose initial `U`-segment exits through `e`.  Let `Q_U(g,e)` be this initial
segment inside `U`.

Build the fan complex

```text
F_Z = union_{g in H, e in D_U(g) cap Z} Q_U(g,e),
```

with door leaves `Z` and hyperedges indexed by `H`.

Choose a connected fan component `K` with positive Euler surplus:

```text
|Z_K| > |H_K|.
```

A **leaf branch** of `K` is a nonempty proper door set `Z0 subset Z_K` such
that, after removing one splitting row `g in H_K`, the branch containing `Z0`
does not meet the rest of `Z_K`.  More concretely, there are two doors

```text
e0 in Z0,  e1 in Z_K \ Z0,  e0,e1 in D_U(g),
```

whose chosen rows first split inside `U`, and the branch toward `e0` contains
exactly the doors in `Z0`.

### NL Statement

Every leaf branch contains a strictly trapped bad edge:

```text
exists g' in H_K \ {g} such that
  empty != D_U(g') cap Z subset Z0.
```

Moreover, `g'` is strictly inside the leaf branch: all of its chosen
`Z`-doors lie in `Z0`, and at least one such door exists.

## Why NL Proves RFC

If RFC fails, take a reduced deficient `Z` and a positive-Euler fan component
`K`.  A finite connected hypergraph with more door leaves than row hyperedges
has a leaf branch.  NL gives a strictly trapped bad edge inside that branch.

If this trapped edge has only one door in the branch, reducedness is violated.
If it has at least two, it creates a strictly smaller leaf branch.  Iterating
produces a strictly descending chain of nonempty finite door sets, impossible.

Therefore no reduced deficient `Z` exists, proving RFC.

## The Only Geometric Gap

The intended proof of NL uses shortest-path splicing inside the completed
seed+moat switch.

Take a leaf branch of a multidoor row `g`.  Since `U` is the blue closure of
the selected terminal prefixes, some selected prefix from `X` reaches the
branch.  There are two cases:

1. It reaches the branch terminally through a door in `Y`.  This contradicts
   that the leaf door lies in `B+ = delta_B(U) \ Y`.

2. It crosses the branch as a middle interval.  Then shortest-path exchange
   between the two `g`-rows and the selected row should produce a strictly
   trapped bad edge `g'` inside the branch.  Triangle-freeness rules out the
   degenerate length-2 splice.

This second case is the real geometric proof obligation.  It is the current
row-side frontier.

## Exact Regression Gates

The RFC gate:

```text
python problems/23/writeup/_rfc_gate.py --h3-hard --max-cross 15
```

Current result:

```text
switches=120
(X,U) instances=1367
rfc_fail=0
toobig=0
VERDICT: RFC HOLDS
```

This run includes the singleton-door check above.

The executable NL leaf-branch gate:

```text
python problems/23/writeup/_nl_leaf_gate.py --h3-hard --max-cross 15
```

Current result:

```text
switches=120
(X,U) instances=1367
reduced deficient cores=0
leaf checks=0
NL failures=0
VERDICT: no executable NL leaf-branch falsifier on this battery
```

This gate is vacuous when RFC has no reduced deficient core, but it fixes the
data model for future falsifiers:

```text
(S, X, U, B+, M+, Z, H, Q_U(g,e), K, g, split vertex s, Z0, trapped g')
```

The checker builds `Q_U(g,e)` as clean initial `U`-segments of shortest rows,
choosing one deterministic segment per `(g,e)`.  It then uses the fan graph on
`U`-vertices, computes split vertices from common prefixes, removes the split
vertex and the sibling branch of the splitting row, and tests whether every
detected leaf branch has a trapped row.

Hard H3 itself contributes:

```text
crossM=15
bdyB=15
nontrivial prefix-hull instances=447
max_Bplus=9
max_Mplus=14
reduced deficient Z=0
minimum reduced margin |N(Z)|-|Z| = 3
```

These gates are evidence and regression checks only.  The proof must establish
NL from terminal-prefix shortest-row geometry, blue closure, max-cut
optimality, and triangle-freeness.
