# Terminal-Shadow SDR Proof Target

This note isolates the current Hall lemma in the `K2T` switch route.

## Theorem To Prove

Let `S` be a neutral terminal-shadow switch in a connected-`B` maximum cut.
Write

```text
C = delta_M(S)   crossing old bad edges,
E = delta_B(S)   old B-boundary exits.
```

For `f in C`, orient every row `Q in cyc[f]` from the endpoint `s(f)` inside
`S`.  Terminal-shadow validity says `Q cap S` is an initial segment and exits
through a unique `e in E`.  Let

```text
Wit(f) = { e in E : some row of f exits S through e }.
```

Then the witness graph

```text
C -- E,     f~e iff e in Wit(f)
```

has a matching saturating `E`.

Exact gate:

```text
python problems/23/writeup/_codex_terminal_shadow_sdr_gate.py --min-n 5 --max-n 10
```

Result:

```text
129552 neutral terminal-shadow switches checked, 0 SDR failures.
```

## Why This Closes The Switch Route

For an exit `e`, define

```text
lambda(e)=min{ell(f): e in Wit(f)}.
```

Every witness `f~e` automatically satisfies `ell(f)>=lambda(e)`.  Thus an SDR
saturating `E`, together with one strict matched witness, gives

```text
sum_{f in C} ell(f)^2 > sum_{e in E} lambda(e)^2,
```

so `Psi(S)>0`.  For neutral terminal-shadow switches the already verified
identity gives

```text
Gamma(after flipping S) <= Gamma - Psi(S).
```

Therefore a gamma-minimal cut cannot contain the completed switch.

## Hall Dual Form

Since `|C|=|E|`, Hall is equivalent to the right-closed form:

```text
for every Y subset E,
|C(Y)| <= |Y|,

C(Y)={f in C : Wit(f) subset Y}.
```

A length cutoff version is also useful:

```text
E_t={e:lambda(e)<t},
C_t(Y)={f in C : ell(f)<t and Wit(f) subset Y},
|C_t(Y)|<=|Y|    for every Y subset E_t.
```

The seed+moat gate found no deficient right-closed residuals at all:

```text
census N<=10 + H?AFBo][2] all max cuts, max_add=1:
  37800 cutoff Hall pairs checked
  deficient=0
  fail=0
```

## Component Boundary Identity

For a connected component `C0` of the witness graph, let

```text
Y_C0 = crossing bad edges in C0,
X_C0 = boundary exits in C0,
U_C0 = union of all terminal prefixes Pref_S(f,e), f in Y_C0, e in X_C0.
```

Exact gate on completed seed+moat switches:

```text
119 witness components checked, 0 failures:
delta_M(U_C0)=Y_C0 and delta_B(U_C0)=X_C0.
```

If this identity is proved for arbitrary neutral terminal-shadow switches, then
max-cut gives

```text
|X_C0| >= |Y_C0|.
```

Neutrality gives equality after summing over components, hence every component
is balanced.  Balance alone does not imply Hall; the next step is the
right-closed subset argument below.

## Minimal Hall-Violator Route

Assume a Hall violator exists and choose `Y subset E` minimal by inclusion with

```text
X=C(Y),     |X|>|Y|.
```

Define the trapped prefix hull

```text
U = union_{f in X} union_{e in Wit(f)} Pref_S(f,e).
```

Then

```text
X subset delta_M(U).
```

If one can prove the side-door inequality

```text
|delta_B(U) \ Y| <= |delta_M(U) \ X|,
```

then max-cut contradicts deficiency:

```text
|delta_B(U)|-|delta_M(U)|
 <= |Y| + |delta_M(U)\X| - |X| - |delta_M(U)\X|
 = |Y|-|X| < 0.
```

So the remaining proof atom is:

```text
MINIMAL SIDE-DOOR LEMMA.
For a minimal right-closed Hall violator Y, every extra B-boundary edge of the
trapped prefix hull U is paid by an extra bad boundary edge.
```

The corresponding statement is false for arbitrary non-deficient `Y`; a local
gate found many arbitrary `Y` with unmatched extra B-boundary.  Minimal
deficiency is therefore an essential hypothesis.

## Proposed Geometric Sublemma

The missing geometric statement should be a no-reentry lens lemma:

```text
NO-REENTRY LENS.
Let U be the trapped prefix hull of a minimal right-closed Hall violator Y.
If a terminal row Q of a crossing bad edge g intersects U in a non-terminal
middle interval, then there is a shorter crossing bad edge h with
Wit(h) subset Y.
```

In the cutoff version, if `ell(h)<ell(g)<t`, then `h in X`, so the corresponding
terminal prefix was already included in `U`.  Thus nontrapped rows can only
touch `U` terminally and their first exit from `U` supplies a side-door bad
edge in `delta_M(U)\X`.

Triangle-freeness and shortestness are expected to enter in the splice:

1. two separated intersections of a shortest row with `U` define a lens;
2. replacing one side of the lens by the other cannot increase both rows;
3. equality would create an alternate trapped prefix, while strict inequality
   creates the shorter bad edge `h`;
4. odd-girth `>=5` rules out the degenerate triangle shortcut.

This is the current non-computational bottleneck.

## Stronger Candidate: Blue-Closed Bad-Subset Hull

The right Hall direction can be attacked from the bad-edge side instead of the
exit side.

Let `X subset C` be any nonempty subfamily of crossing bad edges and set

```text
Y = Wit(X) = union_{f in X} Wit(f).
```

Build `U0` from all terminal prefixes of all rows of `f in X` exiting through
their witness exits.  Then close inside `S` under old cut edges:

```text
U = minimal set with U0 subset U subset S such that
    if u in U, w in S, and uw in B, then w in U.
```

Exact gate:

```text
python problems/23/writeup/_codex_blueclosed_hull_gate.py --min-n 5 --max-n 9

subsets=28008
extra_cases=3116
fail=0
```

The corresponding `N=10` ad hoc run checked all `239208` subfamilies and all
`34648` extra-boundary matching cases, also with zero failures.

The checked sufficient conditions are:

```text
(BH1) X subset delta_M(U).

(BH2) The extra-exit witness graph
     delta_B(U)\Y  --  delta_M(U)\X
     has a matching saturating delta_B(U)\Y.
```

These imply Hall immediately.  Max-cut gives

```text
|delta_B(U)| >= |delta_M(U)|.
```

Since `delta_B(U)` is contained in `Y union (delta_B(U)\Y)` and `delta_M(U)`
contains the disjoint union `X union (delta_M(U)\X)`, while `(BH2)` gives

```text
|delta_B(U)\Y| <= |delta_M(U)\X|,
```

we get

```text
|Y| >= |X|.
```

Thus Hall follows for every bad-edge subfamily `X`.

The remaining proof atom is therefore sharper than the old side-door lemma:

```text
BLUE-CLOSED HULL LEMMA.
For every neutral terminal-shadow switch S and every X subset delta_M(S),
the blue-closed prefix hull U satisfies (BH1) and (BH2).
```

The geometric intuition:

* Blue closure makes all internal cut-edge leaks inside `S` disappear.
* If an extra exit `e in delta_B(U)\Y` remains, any witness row for `e` has its
  whole terminal prefix pulled into `U` by blue closure, so its bad edge lies in
  `delta_M(U)\X`.
* The nontrivial part is the matching/injectivity in `(BH2)`: two extra exits
  sharing all extra bad witnesses should create a theta/lens of shortest
  geodesics, forcing either a shorter bad cycle or a triangle.

This route avoids the refuted paid-leakage inequality.  It uses max-cut only
once, after the blue-closed hull and extra-exit matching have been established.

## Refuted Simplification: No-Multidoor

One tempting strengthening was that, after blue closure, each extra bad edge in
`delta_M(U)\X` opens at most one extra exit in `delta_B(U)\Y`.  This would turn
`(BH2)` into coverage plus an injection.  It is false on the completed
seed+moat battery.

Exact gate:

```text
python problems/23/writeup/_codex_blueclosed_degree_mine.py --min-n 5 --max-n 10 --h2-allmax --max-add 1

switches: 119
extra cases: 920
max right degree histogram: {1:556, 2:36, 3:328}
multidoor cases: 364
uncovered cases: 0
```

Thus blue closure gives coverage of every extra exit, but not a degree-one
right side.  The remaining atom is the full Hall theorem for the extra graph,
not a simple one-exit-per-bad-edge injection.

## Current Positive Structure: Right-Laminar Door Sets

The failed no-multidoor test suggests replacing pointwise injectivity with a
laminar-capacity proof.

Exact gate:

```text
python problems/23/writeup/_codex_blueclosed_structure_mine.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --convex-cap 8

switches: 119
extra cases: 920
matching_fail: 0
left_laminar: {True:896, False:24}
right_laminar: {True:920}
left_convex: {True:920}
right_convex: {True:920}
lamcap_root: {0:920}
lamcap_min_margin: {-1:340, 0:36, 1:152, 2:64, 3:120, 4:112, 5:96}
```

Here the "right" neighborhoods are the sets

```text
D_U^+(h) = { e in delta_B(U)\Y : some terminal row of h first exits U through e }
```

for `h in delta_M(U)\X`.

Thus every checked extra graph has a laminar family of bad-edge door sets.
It is not locally injective: some laminar nodes have margin `-1`, so their
deficit is paid by an ancestor door set.  But the laminar tree has root demand
zero in every case.

This gives a sharper proof decomposition:

```text
RIGHT-DOOR LAMINARITY.
For the blue-closed hull U, the sets D_U^+(h) are laminar.

LAMINAR CAPACITY.
Build the laminar tree on delta_B(U)\Y from the nonempty sets D_U^+(h),
including all singleton leaves and the root.  Let m(A) be the number of
h with D_U^+(h)=A.  Define bottom-up demand

  demand(leaf) = max(0, 1 - m(leaf)),
  demand(A)    = max(0, sum_child demand(child) - m(A)).

Then demand(root)=0.
```

For laminar set systems, `demand(root)=0` is equivalent to a matching
saturating all exits.  So `(BH2)` can be proved by the two bullets above plus
the elementary laminar matching lemma.

### Elementary Laminar Matching Lemma

Let `Z` be a finite set of exits and let `H` be a multiset of nonempty laminar
subsets of `Z`.  Build the laminar tree whose root is `Z`, whose leaves are the
singletons `{z}`, and whose internal nodes are the non-singleton sets appearing
in `H`, ordered by inclusion.  For a node `A`, let

```text
m(A) = #{h in H : D(h)=A}.
```

Define demand bottom-up by

```text
demand({z}) = max(0, 1 - m({z})),
demand(A)   = max(0, sum_{B child of A} demand(B) - m(A)).
```

Then there is a matching from `Z` into `H`, with each exit matched to a set
containing it, iff `demand(Z)=0`.

Proof.  For a node `A`, `demand(A)` is the minimum number of matching edges
from strict ancestors of `A` needed to saturate all leaves of `A` after using
only hyperedges whose sets are contained in `A`.  This statement is proved by
induction on the laminar tree.

For a leaf `{z}`, one local hyperedge `{z}` can saturate it; otherwise exactly
one ancestor edge is needed.  This is the displayed leaf formula.

For an internal node `A`, the child subtrees are disjoint.  By induction, child
`B` requires `demand(B)` edges from `A` or its ancestors.  A hyperedge equal to
`A` can cover one such unsatisfied child-leaf demand, and it cannot be used
twice.  Therefore the number of demands passed to strict ancestors of `A` is
exactly

```text
max(0, sum_child demand(B) - m(A)).
```

At the root there are no ancestors, so a global matching exists exactly when
`demand(Z)=0`.  The constructive greedy matching is obtained by assigning the
`m(A)` copies at each node `A` to any currently unsatisfied child demands,
bottom-up; the induction ensures this succeeds precisely when the root demand
vanishes.

The remaining geometric burden is now clearer:

1. prove shortest-row/triangle-free geometry forces laminarity of the first
   extra-door sets `D_U^+(h)`;
2. prove max-cut or completed-seed+moat structure forces the laminar capacity
   recursion to close at the root.

## Candidate Geometric Proof: Reduced Fan-Core Descent

GPT-Pro's current useful suggestion can be stated as a finite descent lemma.
It is not accepted until exact-gated.

For a blue-closed hull `U`, write

```text
Z = delta_B(U)\Y,
H = delta_M(U)\X,
D_U^+(h) = {e in Z : some terminal row of h first exits U through e}.
```

If Hall failed in the extra graph `Z -- H`, then by repeatedly deleting any
exit `e` that is the unique remaining door of some `h`, one obtains a
nonempty reduced deficient core `Z*` with

```text
|N(Z*)| < |Z*|,
|D_U^+(h) cap Z*| >= 2       for every h in N(Z*).
```

This reduction is purely graph-theoretic: unique-door exits can be greedily
matched and removed, preserving deficiency if any deficiency remains.

The proposed geometric lemma is:

```text
REDUCED FAN-CORE DESCENT (RFC/NL).
No completed seed+moat blue-closed hull contains a reduced deficient core Z*.
```

More explicitly, for a reduced deficient core, form the first-split fan complex
of terminal shortest rows of the bad edges in `N(Z*)`.  A positive-Euler
component has more door leaves than bad edges.  The candidate shortest-path
claim is that some leaf branch of such a component contains a strictly trapped
bad edge `g'` whose door set is a nonempty proper subset of that leaf branch.
Iterating gives a strictly descending chain of nonempty door branches, which is
impossible in the finite laminar tree.

The geometric exchange behind the claim:

* if a selected terminal prefix uses the leaf door, that door would lie in
  `Y`, contradicting that it is extra;
* if it crosses the leaf branch as a middle interval, splicing two shortest
  rows either shortens a bad-edge geodesic or creates a strictly smaller
  trapped bad edge inside the branch;
* triangle-freeness rules out the degenerate length-2 equality case.

Exact falsification gate:

```text
for every completed seed+moat switch S and every X subset C:
    build Y=Wit(X), U=blue_close(prefix_hull(X))
    Z=delta_B(U)\Y
    H=delta_M(U)\X
    build D(h)=first-extra-exit set in Z for each h in H

    search for nonempty Z* subset Z with:
        |N(Z*)| < |Z*|
        |D(h) cap Z*| >= 2 for every h in N(Z*)

    if found, build its first-split fan complex and check whether every
    positive component has a leaf branch containing a strictly smaller trapped
    bad edge g' with nonempty door set contained in that branch.
```

The first search should find no `Z*` in the current completed-switch battery,
because the extra graph already has a matching.  The value of the gate is on
stress/falsifier families: the 17-vertex multi-door fan should produce such a
reduced core and should fail the "smaller trapped bad edge" clause, explaining
why terminal-shadow axioms alone are insufficient.

## 2026-06-30 Refinement: No Internal Laminar Deficit

A follow-up diagnostic sharpened the laminar-capacity target.  The script

```text
python problems/23/writeup/_codex_lamcap_example.py
```

prints the first case where the laminar recursion uses ancestor capacity.  The
first example has three singleton door deficits and one non-singleton root set
with enough bad edges to pay all three.  Concretely, in an `H?AFBo][2]` all-max
cut the extra doors are three exits, each singleton has margin `-1`, and the
full three-door node has margin `+3` from six bad edges with the full door set.

The stricter diagnostic

```text
python problems/23/writeup/_codex_lamcap_internal_example.py
```

searches for a non-root, non-singleton laminar node with negative local margin.
On the same completed seed+moat battery it returns:

```text
NO_EXAMPLE
```

Thus the empirically sharp capacity statement is stronger than
`demand(root)=0`:

```text
NO INTERNAL LAMINAR DEFICIT.
For every blue-closed hull extra graph, every non-root, non-singleton node A
of the right-door laminar tree satisfies

    m(A) >= sum_child demand(child).
```

Equivalently, every positive demand is born at singleton doors, and each
non-singleton fan node pays all demand passed up from its immediate children.
This removes the need for a multi-level ancestor-credit proof in the tested
family.  The remaining geometric proof target becomes:

1. prove right-door laminarity of the sets `D_U^+(h)`;
2. prove no internal laminar deficit by applying max-cut/shortest-row geometry
to the fan branch corresponding to a non-singleton door node;
3. apply the elementary laminar matching lemma.

This refinement does not replace exact verification of the full root-demand
statement, but it identifies the smaller local inequality that all observed
capacity cases satisfy.

## 2026-06-30 Refinement: Star-Door Form

The laminar target simplified further under a direct star-shape diagnostic.

```text
python problems/23/writeup/_codex_star_laminar_stats.py
```

on the completed seed+moat battery gives:

```text
switches: 119
cases: 920
star_fail: 0
reduced_hall_fail: 0
z_size: {3: 328, 1: 544, 2: 48}
missing_singletons: {3: 328, 1: 544, 2: 12, 0: 36}
full_minus_missing: {3: 216, 2: 212, 4: 112, 1: 272, 5: 96, 0: 12}
empty_count: {1: 408, 0: 160, 3: 80, 2: 272}
```

Here `star_fail=0` means every nonempty right-door set is either a singleton
or the full extra-exit set `Z`.  Thus the extra graph is not merely laminar;
it is a star laminar hypergraph.

In this form Hall is equivalent to the count inequality

```text
full_count >= #{z in Z : no bad edge has door set {z}}.
```

The diagnostic checks this as `reduced_hall_fail=0`.  Moreover, when the number
of missing singleton exits is positive, the inequality is always strict in the
current battery: the only `full_minus_missing=0` cases have
`missing_singletons=0`.

So the smallest current proof target is:

```text
STAR-DOOR HULL LEMMA.
For every blue-closed hull from a completed seed+moat switch:
  (1) every nonempty D_U^+(h) is either a singleton or all of Z;
  (2) full_count >= missing_singleton_count, strictly if the latter is positive.
```

Together with the elementary star-hypergraph matching lemma, this proves BH2.
This is stronger and more concrete than the previous right-laminar + capacity
recursion statement.

### 2026-06-30 Addendum: Extra Exits Are a One-Hub Star

The star-door diagnostic was extended to test whether the extra exits themselves
share a common endpoint.  The same command now reports:

```text
exit_star: {True: 920}
first_nonstar: None
```

Thus in every checked blue-closed hull extra case, the set
`Z=delta_B(U)\Y` is an edge-star.  All extra exits are incident with one hub
vertex.  The current smallest geometric lemma is therefore a one-hub fan
statement:

```text
ONE-HUB STAR-DOOR FAN.
Let Z be the extra B-exit star of a blue-closed hull U from a completed
seed+moat switch.  Then every extra bad edge h has D_U^+(h) equal to
empty, one spoke of Z, or all spokes of Z.  Moreover, if some spoke has no
singleton-door bad edge, the number of all-spoke bad edges is larger than the
number of such missing singleton spokes.
```

This implies the star-door Hall condition directly.  It is currently the most
concrete proof target for `(BH2)`.

### Elementary Star-Hypergraph Matching Lemma

Let `Z` be a finite set of exits and let `H` be a multiset of door sets, each
of which is either empty, a singleton `{z}`, or the full set `Z`.  Let

```text
s(z) = #{h in H : D(h)={z}},
F    = #{h in H : D(h)=Z},
missing = #{z in Z : s(z)=0}.
```

Then there is a matching saturating `Z` iff

```text
F >= missing.
```

Proof.  Match every `z` with `s(z)>0` to one singleton-door edge.  The remaining
unmatched exits are exactly the `missing` exits, and each can only be matched by
a full-door edge.  Thus `F>=missing` is necessary and sufficient.

For the current one-hub star-door fan, this means the full SDR proof is reduced
to the two geometric assertions:

```text
(A) Door-set trichotomy: D_U^+(h) is empty, singleton, or all of Z.
(B) Fan capacity: F >= missing, strictly if missing>0 in the checked battery.
```

The branch-shape cross-tab from `_codex_star_laminar_stats.py` is:

```text
('inU', 3, 3): 328
('outU', 1, 1): 281
('inU', 1, 1): 263
('outU', 2, 2): 12
('outU', 2, 0): 24
('inU', 2, 0): 12
```

where the tuple is `(hub side, |Z|, missing)`.  Thus the only genuinely hard
case in the checked battery is the hub-inside, three-spoke fan with all
singleton doors missing; it is paid entirely by full-door bad edges.  The
one-spoke cases are tautological under the star lemma, and the two-spoke cases
are either fully singleton-covered or have two missing singleton doors paid by
full-door edges.

### Boundary Check: Star-Door Is Not Fully General

A broader gate tests the one-hub star-door property for all neutral
terminal-shadow switches, not just the selected completed seed+moat switches:

```text
python problems/23/writeup/_codex_all_terminal_star_gate.py --min-n 5 --max-n 9
```

passes with:

```text
switches=16048
cases=3116
exit_star True=3116
door_fail=0
```

but at `N=10` the fully general theorem fails once:

```text
python problems/23/writeup/_codex_all_terminal_star_gate.py --min-n 10 --max-n 10
```

```text
N=10 switches=73855 cases=18881 exit_star={True:18880, False:1}
first_fail = graph I?ABCc]}?, side 1111100000,
             S=(0,1,3,4,7,8,9), X={(5,8)},
             extra_b={(1,6),(2,9)}, extra_m={(6,7),(6,8)}.
```

This counterexample has no negative residual vertices:

```text
neg=[]
```

so the selected `R<0`/completed seed+moat hypothesis remains essential.  The
one-hub star-door fan lemma should not be stated for arbitrary neutral
terminal-shadow switches.

## 2026-06-30 Broad Structure: Biconvex Witness Graphs

A broader diagnostic tests the full witness graph of every neutral
terminal-shadow switch, not only selected seed+moat switches:

```text
python problems/23/writeup/_codex_terminal_witness_convexity.py --min-n 5 --max-n 10 --cap 8
```

Results:

```text
N<=9: switches=16048, fconv=True all, econv=True all, sdr=True all
N=10: switches=113504, fconv=True all, econv=True all, sdr=True all
```

Here `fconv` means the family of witness sets `Wit(f) subset E` has a
consecutive-ones ordering of the exits, and `econv` means the dual family
`{f:e in Wit(f)}` has a consecutive-ones ordering of the crossing bad edges.
Thus every checked neutral terminal-shadow witness graph is biconvex.

This is broader than the one-hub star-door property.  The one-hub property fails
for a single `N=10` neutral terminal-shadow switch with no negative residual,
but biconvexity survives it.

Important caveat: biconvexity plus component balance alone is not logically
sufficient for a perfect matching; e.g. a balanced biconvex graph can have two
right vertices with the same singleton neighborhood.  The proof still needs the
shortest-geodesic/max-cut input.  The likely route is:

```text
1. NO-CROSSING ORDER LEMMA:
   terminal-shadow shortest rows admit orders of C=delta_M(S) and E=delta_B(S)
   for which the witness relation is biconvex.  This should follow from a
   no-reentry lens / theta-shortening argument.

2. INTERVAL HALL LEMMA:
   in these geometric biconvex orders, every Hall-critical bad-edge subset can
   be chosen as an interval; the prefix hull of a bad-edge interval gives the
   required max-cut contradiction if |Wit(X)|<|X|.
```

This biconvex route may be a cleaner proof of the full Terminal-Shadow SDR
Theorem than the selected-switch star-door fan route.  It also explains why the
N=10 non-star boundary case still has SDR.
