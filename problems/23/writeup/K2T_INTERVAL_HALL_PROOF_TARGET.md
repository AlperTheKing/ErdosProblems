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

## 2026-06-30 Guardrail: Alien-Door Fans Are L2 Failures, Not L1 Failures

The component-boundary identity plus max-cut still does not imply Hall, even
with biconvexity or missed-exit laminarity.  The smallest model is the
three-spoke multi-door fan:

```text
Wit(f1)={e1}
Wit(f2)={e1}
Wit(f3)={e1,e2,e3}
```

The witness graph is biconvex, and the missed-exit sets are laminar:

```text
Miss(f1)=Miss(f2)={e2,e3},   Miss(f3)=empty.
```

Nevertheless Hall fails in the closed-left form with

```text
X={f1,f2},   Y=N(X)={e1},   |X|>|Y|.
```

The prefix hull exposes alien exits:

```text
delta_B(U_X)\Y={e2,e3},   delta_M(U_X)\X={f3},
```

so the interval-hull side-door inequality has slack `1-2=-1`.  Thus the fan is
a pure L2 obstruction.  Any proof that stops at biconvexity or two-leaf
laminarity is insufficient; the selected seed+moat geometry must prove the
interval-hull side-door inequality.

The narrow selected-family verifier now lives in:

```text
python problems/23/writeup/_codex_selected_interval_hall_gate.py --min-n 5 --max-n 10 --hblow 2
```

Current exact result:

```text
neg: 119
selected switches: 119
miss_not_laminar: 0
too_many_leaves: 0
no_order: 0
leaf_hist: [(0, 39), (1, 12), (2, 68)]
intervals: 399
interval_fail: 0
slack: [(0, 119), (1, 26), (2, 68), (3, 68), (4, 54), (5, 64)]
VERDICT: PASS
```

So the live theorem is:

```text
R[v]<0 selected seed+moat switch
=> two-leaf missed-exit laminarity
=> consecutive exit order
=> interval-hull side-door inequality for every consecutive interval
=> Hall/SDR
=> Psi>0 descent
```

The alien-door fan shows precisely where the selected seed+moat hypothesis is
needed: it must forbid a Hall-closed family of bad crossings whose blue-closed
prefix hull exposes more unusable side exits than unusable bad crossings.

## 2026-06-30 Sharpening: Side-Cap Hall Margin Is Strict

Because missed-exit sets are laminar in the selected family, Hall can also be
tested directly on laminar side caps.  For a nonempty missed-exit node `Z`, put

```text
A(Z) = { f in C : Z subset Miss(f) }
     = { f in C : Wit(f) cap Z = empty }.
```

Hall is equivalent to `|A(Z)| + |Z| <= |E|` after reducing to these laminar
nodes.  The alien-door fan violates this with

```text
Z={e2,e3},   A(Z)={f1,f2},   |A(Z)|+|Z|-|E|=1.
```

The selected-family miner:

```text
python problems/23/writeup/_codex_selected_sidecap_mine.py
```

gives:

```text
neg 119
switches 119
caps 160
no_cap 39
fail 0
margin [(1, 26), (2, 58), (3, 28), (4, 6), (5, 42)]
```

where

```text
margin(Z) = |E| - |Z| - |A(Z)|.
```

Thus every nonempty selected side cap has strict margin at least `1`.  A smaller
L2 proof target is therefore:

```text
STRICT SIDE-CAP HALL.
In a completed seed+moat switch selected from R[v]<0, every nonempty laminar
missed-exit node Z satisfies

    |A(Z)| + |Z| <= |E|-1.
```

This strict side-cap margin plus two-leaf missed-exit laminarity implies Hall.
The interval-hull side-door inequality is still the robust geometric route to
prove it; the side-cap form isolates the exact count that the alien-door fan
breaks.

## 2026-06-30 Sharpening: Internal Side-Cap Expansion

The side-cap miner now checks every nonempty subset of every selected side cap,
not only whole laminar nodes.  For a side cap `Z` and `Y subset Z`, put

```text
N_Z(Y) = { f in C : Wit(f) cap Y != empty }.
```

Exact result on the same selected battery:

```text
cap_hall_min [(1, 30), (2, 54), (3, 28), (4, 6), (5, 42)]
cap_hall_surplus_fail 0
```

where `cap_hall_min` records

```text
min_{empty != Y subset Z} ( |N_Z(Y)| - |Y| ).
```

Thus every nonempty side-cap subset has strict expansion:

```text
|N_Z(Y)| >= |Y| + 1.
```

This is stronger than whole-cap Hall margin.  Combined with the two-leaf
missed-exit structure, it gives a very compact Hall proof:

* middle exits are universal, so any interval containing a middle exit is
  witnessed by all bad edges;
* intervals avoiding the middle lie inside one side cap, where strict
  side-cap expansion gives Hall;
* arbitrary exit sets reduce to intervals by the consecutive-order lemma.

So the proof burden can be reduced again:

```text
SELECTED TWO-CAP EXPANSION.
In a completed seed+moat switch selected from R[v]<0, the exits decompose into
left cap, universal middle, and right cap.  Every nonempty subset of either cap
has strictly more bad-edge witnesses than exits.
```

The alien-door fan fails exactly here: for the cap `{e2,e3}`, its witness set is
`{f3}`, so `|N_Z(Y)|-|Y|=-1`.

### Formal Hall Reduction From Two-Cap Expansion

Let the selected switch have exit set

```text
E = L dotcup M dotcup R
```

where `L,R` are the two possibly empty side caps and every `m in M` is
universal:

```text
N({m}) = C.
```

Assume the cap expansion condition

```text
empty != Y subset L  =>  |N(Y)| >= |Y|+1,
empty != Y subset R  =>  |N(Y)| >= |Y|+1.
```

Also assume missed-exit sets are unions of the two caps:

```text
Miss(f) in {empty, L, R, L union R}.
```

Then Hall on the exit side follows.  For any `Y subset E`:

* If `Y cap M` is nonempty, then `N(Y)=C`, so `|N(Y)|=|C|=|E|>=|Y|`.
* If `Y subset L`, cap expansion gives `|N(Y)|>|Y|`.
* If `Y subset R`, cap expansion gives `|N(Y)|>|Y|`.
* If `Y=Y_L dotcup Y_R` with nonempty parts in both caps and no middle exit,
  then any `f` missed by both parts has `Miss(f)` containing a nonempty subset
  of `L` and a nonempty subset of `R`; by the union-of-caps property, such an
  `f` misses all of `L union R`.  Therefore

```text
N(Y) = N(Y_L) union N(Y_R)
```

and the only possible overlap is the set of bad edges witnessing both caps.
The interval reduction avoids needing this two-sided case: `Y` has two
consecutive blocks in the left-middle-right order, so if Hall failed for `Y`,
one block would already fail.  Each block lies in a single cap and is covered
by cap expansion.

Thus for the proof it is enough to establish:

```text
(A) Miss(f) is always empty, L, R, or L union R;
(B) middle exits are universal;
(C) every nonempty subset of L or R has strict expansion.
```

The updated verifier checks (A), (B), and (C) exactly on the selected battery:

```text
python problems/23/writeup/_codex_selected_interval_hall_gate.py --min-n 5 --max-n 10 --hblow 2
python problems/23/writeup/_codex_selected_sidecap_mine.py
```

## 2026-06-30 Guardrail: Positive-Psi Two-Cap Is Still Too Broad

The strict cap-expansion theorem must remain scoped to the negative-residual
selected seed+moat switch.  It is false for arbitrary neutral terminal-shadow
switches, even if they have positive `Psi` and the same two-cap decomposition.

Scope gate:

```text
python problems/23/writeup/_codex_cap_expansion_scope_gate.py --min-n 5 --max-n 10
```

First counterexample:

```text
graph I?AEBAwF_
N=10
side=0011111000
S=(0,1,6)
Psi=24
crossM={(0,8),(1,7)}
bdyB={(0,5),(6,9)}
Wit(0,5)={(0,8)}
Wit(6,9)={(0,8),(1,7)}
```

It has a singleton side cap `{(0,5)}` with exactly one witness, so strict
cap expansion fails with gap `0`.  But this cut has no negative-residual
vertex:

```text
neg=[]
```

Thus the missing proof input is not merely positive `Psi`; it is the
`R[v]<0` selected seed+moat construction.

## 2026-06-30 Sharpening: Deficient Cap Excludes Negative Residual

A better scope statement survived a broader finite gate.  In any neutral
terminal-shadow switch with positive `Psi` and the two-cap decomposition, if a
side cap has a nonempty subset `Y` with

```text
|N(Y)| <= |Y|,
```

then the switch contains no negative-residual vertex:

```text
R[x] >= 0  for every x in S.
```

Gate:

```text
python problems/23/writeup/_codex_defcap_negative_scope_gate.py --min-n 5 --max-n 10
```

Result:

```text
two_cap_positive 1608
defcap 16
fail 0
VERDICT: PASS
```

This formulation explains why the broader `I?AEBAwF_` positive-`Psi` switch is
not a counterexample to the selected theorem: it has a deficient singleton cap,
but `neg=[]`.

The selected proof can therefore be factored as:

```text
R[v]<0 and v in S
+ neutral terminal-shadow positive-Psi two-cap switch
+ deficient-cap-excludes-negative-residual
=> no deficient side cap
=> strict side-cap expansion
=> Hall/SDR.
```

This may be easier to prove than raw cap expansion, because the conclusion of a
deficient side cap is a residual sign statement rather than a matching
statement.

## 2026-06-30 Guardrail: Alien-Door Fan Kills Component Balance Alone

A 3-spoke multi-door fan shows that the component-boundary identity plus
max-cut does not imply Hall.  In the fan, a singleton terminal switch has

```text
Wit(f1)={e1}
Wit(f2)={e1}
Wit(f3)={e1,e2,e3}
```

with `|F|=|E|=3`, connected witness graph, exact component boundary identity

```text
delta_M({s})={f1,f2,f3}
delta_B({s})={e1,e2,e3},
```

and a maximum cut certified by edge-disjoint blue paths.  Hall fails on
`Y={e2,e3}` because `N(Y)={f3}`.  Equivalently, for the closed bad set
`X={f1,f2}`, the physical prefix hull exposes alien exits:

```text
A_B={e2,e3},    A_M={f3},
|X|-|N(X)| = |A_B|-|A_M| = 1.
```

Thus any proof that only sees the whole component boundary is too weak.  The
missing geometry must rule out alien-door surplus for the selected
`R[v]<0` seed+moat switches, or prove the equivalent right-closed Hall
condition directly.

The exact selected-domain gate remains clean:

```text
python problems/23/writeup/_codex_sidedoor_prefix_hull_gate.py \
  --min-n 5 --max-n 10 --max-add 1 --max-et 18 --h2-allmax --matching
```

Result:

```text
negative vertices: 119
switches tested: 119
Hall pairs checked: 37800
deficient: 0
fail: 0
VERDICT: PASS
```

So the alien-door fan is a necessary guardrail and a falsifier for broad
component-balance proofs, but it is not a selected `R[v]<0` descent example.

### 2026-06-30 Noncomplete Side-Cap Templates

The selected side-cap witness graph is complete in `148/160` cases.  The remaining `12` noncomplete cases have only two templates:

```text
8 cases:  |cap|=2, |touch|=4, degrees=(3,3), common witnesses=2, private=(1,1)
4 cases:  |cap|=2, |touch|=4, degrees=(2,2), common witnesses=0, private=(2,2)
```

Thus every noncomplete selected cap is still strictly expanding for the most elementary reason: a two-exit cap has four touching bad edges, with either two shared/universal plus one private witness per exit, or two disjoint private pairs.  This suggests an even sharper proof target:

```text
SELECTED SIDE-CAP TEMPLATE LEMMA.
For a completed seed+moat switch selected by R[v]<0, every side-cap witness graph is either complete, or one of the two 2-by-4 templates above.
```

This template lemma implies the strict side-cap expansion condition immediately.

## 2026-06-30 Guardrail: Deficient-Cap Cases Collapse to a Nested 2-by-2 Template

The broader deficient-cap sign gate passes:

```text
python problems/23/writeup/_codex_defcap_negative_scope_gate.py --min-n 5 --max-n 10
```

with

```text
two_cap_positive=1608
defcap=16
fail=0
VERDICT: PASS
```

The detail miner

```text
python problems/23/writeup/_codex_defcap_detail_mine.py --min-n 5 --max-n 10
```

shows that all `16` deficient-cap examples are the same nested two-edge
template:

```text
|C|=|E|=2,
E={e0,e1},
C={f0,f1},
Wit(e0)={f0},
Wit(e1)={f0,f1},
ell(f0)=5,
ell(f1)=7.
```

The deficient cap is the singleton `{e0}`, with gap `|N({e0})|-1=0`.
In every such switch all vertices of `S` have positive residual; the exact
minimum in the finite gate is

```text
min_{v in S} R[v] >= 25/4.
```

Thus deficient caps are not selected by `R[v]<0`.  A proof route for the
selected theorem can equivalently show:

```text
R[v]<0 and v in S
=> the completed seed+moat switch is not a nested short/long deficient-cap
   template
=> every side-cap subset has strict expansion.
```

This is only an exact-mined guardrail so far, not a proof.  Its value is that it
pinpoints the broad positive-`Psi` switches excluded by the negative-residual
selector.

The precise contrapositive atom suggested by the detail miner is:

```text
DEFICIENT-CAP SIGN ATOM.
Let S be a neutral terminal-shadow positive-Psi two-cap switch with the
two-cap/leaf-union structure.  If some nonempty side-cap subset Y has
|N(Y)| <= |Y|, then the switch contains no negative-residual vertex:

    R[u] = N*T(u) - (K2*T)(u) >= 0  for every u in S.
```

In the exact N<=10 search, every deficient-cap instance is the same nested
short/long template:

```text
C={f0,f1}, E={e0,e1},
ell(f0)=5, ell(f1)=7,
Wit(e0)={f0}, Wit(e1)={f0,f1},
Y={e0}, |N(Y)|=|Y|=1.
```

The residual values on `S` are always positive; the smallest printed exact
value is

```text
min_{u in S} R[u] = 25/4.
```

For the canonical graph `I?AEBAwF_`, the full bad-edge set is exactly the two
template rows.  With `f0` the length-5 row and `f1` the length-7 row, the exact
`K2` residual types are:

```text
(p_f0(u), p_f1(u), T(u), (K2*T)(u), R(u))   multiplicity
(0,   1,   7,    121/2, 19/2)              3
(1/2, 0,   5/2,  75/4,  25/4)              1
(1/2, 1/2, 6,    203/4, 37/4)              2
(1/2, 1,   19/2, 331/4, 49/4)              1
(1,   0,   5,    41,    9)                 1
(1,   1,   12,   203/2, 37/2)              2
```

Thus the algebraic endpoint of the sign atom is explicit: once a deficient cap
is reduced to the nested `5/7` two-row template, every possible vertex type has
strictly positive residual.

So another route to surplus-touch is to prove the sign atom directly.  This
would avoid constructing a clean pruned sub-switch: the bad deficient cap is
allowed, but it is incompatible with the negative-residual selector.

## 2026-06-30 Replacement-Exit Corner Lemma

A new exact-supported local handle for the two-terminal residual theorem is the
following replacement-exit rule after rare stage0.

Let `e` be a residual exit and `f` a longer residual crossing bad edge in the
same residual component such that `e` does not witness `f`.  Orient every
crossing edge with respect to the completed seed+moat switch `S`:

```text
e = (e_in -> e_out),        f = (f_in -> f_out).
```

Then there is a residual exit `e'` witnessed by `f` satisfying at least one of

```text
outside(e') = e_out,        (same outside side-door)
inside(e')  = f_in,         (same missed terminal)
e' = (e_in -> f_out).       (corner side-door)
```

The first two alternatives alone are false.  The corner alternative is needed;
the first counterexample before adding it was

```text
H2-allmax, side 101111111111000000,
S=(0,2,3,4,5,6,7,8,9,12,13,14,15,16),
e=(16 -> 10), f=(0 -> 11), and e'=(16 -> 11).
```

Exact gates:

```text
python problems/23/writeup/_codex_replacement_exit_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested: 182
status: {'ok': 182}
stats: {'missing': 72, 'same_out': 56, 'same_terminal': 64, 'ok': 72, 'corner': 8}
VERDICT: PASS
```

The tie-break independent all-minimum-stage0 version

```text
python problems/23/writeup/_codex_replacement_exit_allmin_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap 100000
```

returns

```text
tested: 119
status: {'ok': 119}
stats: {'missing': 1632, 'same_out': 672, 'same_terminal': 1536, 'ok': 1632, 'corner': 96}
VERDICT: PASS
```

This lemma is weaker than the final two-terminal theorem, but it gives a
geometric proof target: every missed row can be re-routed through a same-door,
same-terminal, or rectangle-corner witnessed exit.  A crossing pattern with no
such replacement should form a terminal lens/theta and therefore a shorter
blue geodesic or a triangle.

## 2026-06-30 Minimalized Selector Gate

Claude's neutral-minimality suggestion is not literally true for the raw
`find_seedmoat` selected switch: two selected H2 switches are not
inclusion-minimal among neutral terminal-shadow Gamma-decreasing subsets
containing the negative-residual vertex.

Gate:

```text
python problems/23/writeup/_codex_selected_minimality_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

returns

```text
tested: 119
minimal: 117
nonminimal: 2
first: H?AFBo]x2, side 001111111111000000, v=12,
       selected S=(0,1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17)
       shrinks to U=(12,) with the same Gamma drop 48.
VERDICT: FAIL
```

However, if each selected switch is replaced by an inclusion-minimal neutral
terminal-shadow Gamma-decreasing subset inside it and still containing the
negative vertex, the full selected interval-Hall structure survives.

Gate:

```text
python problems/23/writeup/_codex_minimalized_hall_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

returns

```text
neg: 119
switches: 119
shrunk: 2
miss_not_laminar: 0
too_many_leaves: 0
nonuniversal_middle: 0
non_leaf_union_miss: 0
no_order: 0
leaf_hist: [(0, 39), (1, 12), (2, 68)]
intervals: 399
interval_fail: 0
slack: [(0, 119), (1, 26), (2, 68), (3, 68), (4, 54), (5, 64)]
VERDICT: PASS
```

Thus the minimality route should be formulated with a modified selector:

```text
R[v]<0 -> choose a seed+moat descent switch, then replace it by an
inclusion-minimal neutral terminal-shadow Gamma-decreasing subset containing v.
```

The live proof atom becomes:

```text
In a minimalized selected switch, a deficient side cap would allow deleting
that cap (or replacing it by its complement-side terminal shadow) to obtain a
proper smaller neutral terminal-shadow Gamma-decreasing switch through v,
contradicting minimality.
```

This avoids the false boundary-pruning identities while keeping the exact
Hall/interval structure.

Minimalized strict side-cap expansion was gated directly:

```text
python problems/23/writeup/_codex_minimalized_sidecap_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

returns

```text
switches: 119
shrunk: 2
caps: 148
no_cap: 39
bad_terminal: 0
no_seedmoat: 0
gap: [(1, 26), (2, 46), (3, 28), (4, 6), (5, 42)]
VERDICT: PASS
```

Here `gap` is

```text
min_{empty != Y subset cap} ( |N(Y)| - |Y| ).
```

Thus every nonempty side-cap subset still has strict expansion after
minimalizing the selected switch.  This is the exact count to prove via
neutral-minimality.

## 2026-06-30 Minimalized Complete-Cap Classification

After switching from the raw selected seed+moat switch to the inclusion-minimal
neutral terminal-shadow Gamma-decreasing subset containing the negative-residual
vertex, the side-cap structure becomes stronger than in the raw selector.

The classifier

```text
python problems/23/writeup/_codex_minimalized_cap_template_mine.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

returns

```text
neg: 119 switches: 119 shrunk: 2
caps: 148 complete: 148 noncomplete: 0 no_cap: 39
bad_terminal: 0 no_seedmoat: 0
gap: [(1,26),(2,46),(3,28),(4,6),(5,42)]
```

Thus every side-cap witness graph in the minimalized selected battery is
complete bipartite between the cap exits and the bad edges that touch the cap.
The old raw-selector noncomplete two-by-four templates disappear after
minimalization.

The surviving cap signatures are exactly:

```text
(|cap|, |touch|, gap, complete, min_deg, max_deg, touch_lengths, lambdas)
(1,6,5,True,6,6,(5,5,7,7,7,7),(5,)) 42
(3,5,2,True,5,5,(5,5,7,7,7),(5,5,5)) 26
(3,6,3,True,6,6,(5,5,7,7,7,7),(5,5,5)) 22
(1,3,2,True,3,3,(7,7,7),(7,)) 16
(1,2,1,True,2,2,(7,7),(7,)) 16
(3,4,1,True,4,4,(5,5,7,7),(5,5,5)) 10
(1,4,3,True,4,4,(5,5,7,7),(5,)) 6
(1,5,4,True,5,5,(5,5,7,7,7),(5,)) 6
(2,4,2,True,4,4,(7,7,7,7),(7,7)) 4
```

So strict cap expansion for the minimalized selector reduces to two sharper
geometric proof atoms:

```text
(Complete cap)  every bad edge that witnesses one exit in a side cap witnesses
                every exit in that cap;
(Surplus touch) |touch(cap)| > |cap|.
```

Once these hold, every nonempty `Y subset cap` has
`N(Y)=touch(cap)`, hence `|N(Y)|>|Y|`.  This is stronger and more rigid than
proving Hall expansion directly.

## 2026-06-30 Dirty-Cap-Defect Accounting Audit

Claude/GPT-Pro proposed the direct dirty-cap-defect inequality

```text
DCD(K) := |missing_allowed| + |M_leak| - |B_leak| >= 1
```

for the prefix-union `U_K` of cap-missing rows.  The exact gate

```text
python problems/23/writeup/_dcd_gate.py
```

shows that this inequality is false as stated on the selected minimalized
battery:

```text
switches: 80 caps: 148
DCD value histogram: [(-3,32),(-2,31),(-1,20),(1,26),(2,15),(3,6),(4,6),(5,12)]
DCD < 1 failures: 83
first failure: H2x, cap size 3, dcd=-1, gap=1, |dB|-|dM|=2
```

The failure is not mysterious.  A Codex identity gate

```text
python problems/23/writeup/_codex_dcd_identity_gate.py
```

returns

```text
switches: 80 caps: 148
identity_fail: 0
fk_not_boundary: 0
triples (DCD, maxcut_slack, gap):
  (-3,6,3) x22
  (-3,8,5) x10
  (-2,4,2) x31
  (-1,2,1) x20
  (1,0,1) x6
  (1,4,5) x20
  (2,0,2) x15
  (3,0,3) x6
  (4,0,4) x6
  (5,0,5) x12
```

So the exact relation is

```text
|N(K)| - |K| = DCD(K) + (|delta_B(U_K)| - |delta_M(U_K)|).
```

DCD alone is too strong because ordinary max-cut slack of `U_K` may pay the
cap surplus.  The accounting identity is useful, but it is not a closure proof:
proving strict cap expansion still requires a structural reason why the right
side is positive.  The complete-cap classification above is currently the
sharper target.

### Complete-cap is already contained in the leaf-union theorem

The `Complete cap` half of the classification is not an independent proof
atom.  It follows immediately from the already-gated property that every missed
exit set is a union of laminar leaves.

Indeed, let `K` be a leaf cap and let `Miss(f)=E\exits(f)`.  Since `Miss(f)` is
a union of leaves, either `K subset Miss(f)` or `K cap Miss(f)=empty`.  Therefore
if `f` touches `K`, i.e. `exits(f) cap K` is nonempty, the first alternative is
impossible and `K cap Miss(f)=empty`; hence `K subset exits(f)`.  Thus every
bad edge touching one cap exit witnesses all exits of that cap.

So after the laminar/leaf-union theorem, the only remaining cap atom is

```text
(Surplus touch) |touch(K)| > |K|.
```

This is exactly the strict side-cap surplus and is the piece that still needs a
geometric/minimality proof.

### Cap Encloser Diagnostics

The door-owner/encloser gate

```text
python problems/23/writeup/_doorowner_gate.py
```

confirms the hard certificate on the minimalized selected battery:

```text
caps=148, noncomplete=0, sdr_fail=0, surplus_fail=0,
enc_v_ok=148, enc_seed_no=94.
```

The failed part `enc_seed_no=94` is important: the surplus row is not separated
by being the unique strictly longest touching row.  In many caps there are
several touching rows at the seed length.

Two extra diagnostics sharpen what the encloser can and cannot mean.

First,

```text
python problems/23/writeup/_codex_cap_owner_avoid_seed_gate.py
```

shows that avoiding *all* rows whose shortest geodesic bundle touches the
negative vertex `v` is impossible:

```text
avoid_all_seed_fail=148.
```

In fact every cap-touching row has a shortest geodesic through `v` in this
diagnostic.  The meaningful excludability statement is only:

```text
there exists rho in touch(K) with p_rho(v)>0 such that
K still has an SDR into touch(K)\{rho}.
```

That holds for all caps, but it is a consequence of complete-cap plus
`|touch(K)|>|K|`, not an independent proof of surplus.

Second,

```text
python problems/23/writeup/_codex_cap_touch_v_mine.py
```

records exact `p_f(v)` for cap-touching rows:

```text
caps=148
zero_count=0
min p_f(v) is 1/4 in 112 caps and 1/2 in 36 caps.
```

Thus the cap-touch set is entirely inside the negative vertex's geodesic
bundle, with `p_f(v)` values only `1/4` or `1/2` on the selected battery.  This
is a useful guardrail for the eventual surplus-touch proof: the strict `+1`
does not come from length separation, and it does not come from a disjoint
owner/encloser row class.  It must use the completed switch minimality or the
negative-residual vertex's geodesic-bundle structure directly.

## 2026-06-30 No-Two-Hole Residual Corridor Atom

The earlier leaf/component separation formulation is too strong.  The gate

```text
python problems/23/writeup/_codex_leaf_component_gate.py \
  --min-n 5 --max-n 10 --h2-selected --h-inherited 4 --max-add 1
```

finds a selected H2-allmax counterboundary:

```text
status = leaf_multi_in_component
side   = 111111111100000000
v      = 2
S      = (0,1,2,10,11,12,13)
leaf   = ((3,13),(4,13),(5,13))
cr     = ((4,12),(4,13),(5,12),(5,13))
k      = 2
```

Thus one laminar missed-exit leaf can meet a residual component twice.  That
does **not** create a Hall obstruction, because the row-level theorem is still
true: no single residual row has two holes in one component.

The sharper live atom is therefore the no-two-hole residual corridor lemma.
For a residual component `(A,B)` after rare stage0, define the exit
co-witness graph on `B` by joining two exits when some `g in A` witnesses both.
If a row `f in A` missed two exits in the same component, a shortest
co-witness path between two missed exits would give

```text
e0, g1, e1, ..., gk, ek
```

with endpoint exits missed by `f` and all internal exits witnessed by `f`.
The proposed proof splits such a corridor into:

```text
long-lambda endpoint  -> two-hinge lens / shorter B-geodesic;
min-lambda endpoints  -> rare-cost alternating exchange in the F0-E0 matching.
```

The exact diagnostic

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested: 182
status: {'ok': 182}
stats: {('row_miss', 0): 989, ('row_miss', 1): 72}
VERDICT: PASS
```

So the selected battery contains no double-miss residual corridor at all.
This is the strongest current finite shadow of the desired theorem:

```text
For every residual component (A,B) and every f in A,
|{e in B : f does not witness e}| <= 1.
```

Together with component balance and the already-gated fact that every
non-universal residual exit is witnessed by at least two residual rows, this
implies residual Hall componentwise.

### Terminal-Slack TH-Corridor Split

For an exit `e=(x_e,y_e)` with `x_e in S` and `y_e outside S`, and a crossing
bad edge `f=(tau_f,sigma_f)` with `tau_f in S`, set

```text
D_f = ell(f)-1
s_f(e) =
  d_{B[S]}(tau_f,x_e) + 1 + d_{B[V\S]}(y_e,sigma_f) - D_f.
```

Terminal-shadow validity says

```text
f witnesses e  iff  s_f(e)=0.
```

Every nonzero slack is even and at least `2`, by bipartiteness of the cut
graph.  Thus a double miss of `f` in one residual component gives two positive
slack exits.  Choosing a closest such pair in the exit co-witness graph yields
a minimal TH-corridor

```text
e0, g1, e1, ..., gk, ek
```

with

```text
g_i witnesses e_{i-1} and e_i,
s_f(e0)>0, s_f(ek)>0,
s_f(e_i)=0 for 1<=i<=k-1.
```

The attached proof atom splits exactly on the endpoint tier.

**Long-door case.**  If either endpoint has `lambda(e)>L0`, the union of
terminal rows for the hinges `g_i` and the tight internal `f` exits should
contain either a triangle or a `B`-path between the endpoints of one involved
bad edge `h in {f,g_1,...,g_k}` of length at most `D_h-2`.  This is the
two-hinge lens obstruction.

**Minimum-door case.**  If both endpoint exits have `lambda(e)=L0`, then the
stage0 rare-cost matching on `(F0,E0)` should admit a negative alternating
exchange.  In the one-root diagnostic this is the reachable matched exit
condition:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e)
such that deg_F1(u) > deg_F1(e).
```

The current gate implements these two certificates if a double-miss corridor
appears.  On the selected proof battery the stronger outcome holds: there is
no double-miss corridor at all.  Therefore the proof still needs the geometric
argument, not another scalar Hall inequality:

```text
TH-Corridor = long-door two-hinge lens OR minimum-door rare exchange.
```

One tempting smaller high-tier atom is false.  GPT-Pro suggested:

```text
f misses high-tier p, f sees q,
g sees p and q, and p-g-q is the first hinge from p to an f-seen exit
=> some f-row through q and g-row through p have both inside and outside contact.
```

The diagnostic

```text
python problems/23/writeup/_codex_ht_endpoint_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns a counterexample:

```text
status: ht_no_two_contact
name: H2-allmax, n=18, side=111111111110000000, v=12, S=(0,1,11,12)
f=(0,10), p=(1,13), q=(0,13),
g candidates=((11,16),(11,17)), lambda(p)=7, L0=5.
```

So the long-door proof cannot rely on a single endpoint hinge having both
contacts.  The surviving long-door target must use the whole two-hole corridor
or the replacement-exit bridge, not this one-hinge HT shortcut.

### Component Hall from Single-Miss

Let `(A,B)` be a residual connected component after stage0.  The currently
gated scalar facts are:

```text
|A| = |B|,                                      (balance)
deg_A(e) >= 2 for every non-universal e in B,   (no one-witness exit)
each f in A misses at most one e in B.          (single-miss)
```

These imply Hall for the component.  For `Y subset B`, let

```text
X(Y) = { f in A : N(f) subset Y }.
```

Equivalently, `f in X(Y)` iff `f` misses every exit in `B\Y`.

If `Y=B`, then `|X(Y)|=|A|=|B|=|Y|`.

If `|B\Y|>=2`, single-miss gives `X(Y)=empty`, hence Hall is strict.

If `B\Y={e}`, then

```text
X(Y)=A\N(e).
```

If `e` is universal, this is empty.  Otherwise `deg_A(e)>=2`, so

```text
|X(Y)| <= |A|-2 = |B|-2 = |Y|-1 < |Y|.
```

Thus every proper `Y` has strict Hall.  Therefore the whole residual SDR
follows from the single-miss theorem.  The no-two-hole residual corridor lemma
is exactly the row-level geometric statement needed for this final step.

### Replacement-Exit Bridge for Singleton Holes

A singleton residual miss is allowed, so the no-two-hole proof must not try to
eliminate every missed exit.  The exact replacement gate

```text
python problems/23/writeup/_codex_replacement_exit_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested=182
status ok=182
missing=72
same_out=56
same_terminal=64
corner=8
```

and every residual miss `(f,e)` has a witnessed residual replacement exit
`e'` in the same component of one of three forms:

```text
same outside:    outside(e') = outside(e);
same terminal:   inside(e')  = inside(f);
corner:          e' = (inside(e), outside(f)).
```

Thus the row-side proof can be aimed at the following smaller geometric
replacement lemma.

```text
REX.  Let (A,B) be a residual component after the rare stage0 matching.
Let f in A miss a residual exit e in B.  Then f witnesses another residual
exit e' in the same component such that one of the three replacement
identities above holds.
```

`REX` is weaker than proving that the missed exit itself is impossible; the
72 exact misses in the selected battery show that singleton holes are real.
The target is to prove that every singleton hole is geometrically paired to a
same-outside, same-terminal, or corner replacement.  Two holes of the same row
inside one co-witness component would then give two such replacements.  Their
terminal-prefix lenses must either cross, producing the long-door shortcut
certificate, or remain separated, producing the minimum-door rare-cost
exchange.  This is the current proof compression of the attached
TH-corridor atom.

The diagnostic

```text
python problems/23/writeup/_codex_replacement_exit_mine.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

shows that the selected battery is even narrower:

```text
32  ell(f)=7, lambda(e)=5, component=(4,4), f sees 3 exits, replacement=OT
24  ell(f)=7, lambda(e)=7, component=(4,4), f sees 3 exits, replacement=OT
 8  ell(f)=7, lambda(e)=7, component=(3,3), f sees 2 exits, replacement=T
 8  ell(f)=7, lambda(e)=7, component=(4,4), f sees 3 exits, replacement=C
```

Here `O`, `T`, and `C` mean same-outside, same-terminal, and corner.  Thus the
finite shadow of `REX` has only four shapes, all with the missed row of length
`7`.  The proof should still be stated length-free, but the exact obstruction
to explain is the `5/7` terminal theta geometry.

The path-level strengthening is even sharper:

```text
python problems/23/writeup/_codex_rex_theta_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested=182
misses=72
ok=72
fail=0
ell_hist={7:72}
strong_f0_theta=72
weak_any_theta=72
VERDICT=PASS
```

Here `strong_f0_theta` means:

```text
for every residual singleton miss (f,e),
  ell(f)=7, and
  some shortest row P in cyc[f] contains contiguously a shortest row Q in
  cyc[g] for a length-5 crossing stage-0 edge g in F0.
```

The first examples are literally of the form

```text
g=(12,16), ell(g)=5, Q=(12,2,14,6,16)
f=(1,10), ell(f)=7, P=(1,12,2,14,6,16,10)
```

so the missed row is a two-edge terminal extension of the short row.  Thus the
row-side singleton replacement theorem can be stated in the same normal form
as the cap-side deficient core:

```text
REX-Theta.
Every residual singleton miss in a selected R[v]<0 terminal-shadow switch is a
5/7 terminal theta whose short side is an F0 edge already consumed by the
stage-0 rare matching.
```

Proving `REX-Theta` plus the stage-0 rare-exchange obstruction for two
different singleton misses should imply the no-two-hole theorem: two holes of
one row would give two terminal 5/7 extensions of F0 rows in one co-witness
component; either their annuli cross, giving a shorter B-geodesic/triangle, or
they stay separated, giving a negative rare-cost alternating exchange.

The all-minimum-stage0 version

```text
python problems/23/writeup/_codex_replacement_exit_allmin_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap 200000
```

also passes:

```text
tested=119
status ok=119
missing=1632
```

So the rare-stage tie break is not hiding the replacement phenomenon.  A
possible proof route for the no-two-hole lemma is:

1. prove the replacement rule geometrically for every singleton residual miss;
2. show that two misses of the same row in one co-witness component force two
   replacement corridors whose terminal-prefix lenses cross;
3. the crossing gives either a shorter B-geodesic for one of the involved bad
   edges or a rare-cost stage0 exchange.

This keeps the proof row-local and avoids the false stronger statement that a
residual component meets each laminar leaf at most once.

The residual two-terminal shape is also robust under all minimum-cost stage0
matchings:

```text
python problems/23/writeup/_codex_stage0_all_min_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap 200000
```

returns

```text
tested=119
status ok=119
```

with match-counts up to `1680` minimum-cost stage0 matchings in one switch.
Thus the proof should use only minimum total rare cost

```text
sum_{matched e} deg_F1(e)
```

and should not depend on the deterministic rank tie-break used by
`min_cost_stage0`.

### Deficient-Cap Sign Atom

The cap side now has a cleaner contrapositive target than a distinguished
encloser row.  In a neutral terminal-shadow switch with positive `Psi` and the
two-cap / leaf-union decomposition, call a side-cap subset deficient if

```text
empty != Y subset K,
|N(Y)| <= |Y|,
N(Y) = { f in C=delta_M(S) : Wit(f) cap Y != empty }.
```

Exact gates support the following atom:

```text
Deficient-cap sign atom:
If such a deficient Y exists, then no vertex of the switch has negative
residual R[u]=N*T(u)-(K2*T)(u).
```

The stronger census gate also passed:

```text
python problems/23/writeup/_codex_defcap_global_negative_gate.py \
  --min-n 5 --max-n 10
```

returned

```text
defcap=16
global_fail=0
VERDICT PASS
```

Claude independently confirmed the switch-local sign atom in a separate
witness implementation:

```text
two_cap_positive=1608
defcap=16
fail=0
```

Thus for selected switches containing a vertex `v` with `R[v]<0`, deficient
caps are forbidden.  With leaf-union giving complete-cap, this yields strict
side-cap expansion / surplus-touch.

The current proof task is therefore:

1. classify every deficient cap in a neutral positive-`Psi` two-cap
   terminal-shadow switch as the nested short/long two-row template

```text
C={f0,f1},  ell(f0)=5, ell(f1)=7,
Wit(e0)={f0},  Wit(e1)={f0,f1},  Y={e0};
```

2. prove the residual sign in that template:

```text
R[u] >= 0
```

on the switch, or globally in the stronger form.

#### Local Sign Lemma After Classification

The algebraic half is already finite once the classification produces the
canonical nested component.  Name the short bad edge `f0` and the long bad edge
`f1`.  The canonical component has:

```text
ell(f0)=5,  |cyc(f0)|=4,
ell(f1)=7,  |cyc(f1)|=2.
```

One concrete labelled model is:

```text
f0=(0,8):
  0-5-9-3-8
  0-6-9-3-8
  0-5-9-4-8
  0-6-9-4-8

f1=(1,7):
  1-6-9-3-8-2-7
  1-6-9-4-8-2-7
```

For this model the exact residual table is:

```text
(p_f0(u), p_f1(u), T(u), (K2*T)(u), R(u))   multiplicity
(0,   1,   7,    121/2, 19/2)              3
(1/2, 0,   5/2,  75/4,  25/4)              1
(1/2, 1/2, 6,    203/4, 37/4)              2
(1/2, 1,   19/2, 331/4, 49/4)              1
(1,   0,   5,    41,    9)                 1
(1,   1,   12,   203/2, 37/2)              2
```

Here

```text
R(u) = N*T(u) - (K2*T)(u),  N=10.
```

Every type has strict positive residual, with minimum `25/4`.  The script

```text
python problems/23/writeup/_codex_defcap_template_cert.py
```

asserts exactly this finite normal form:

```text
deficient_cases: 16
type_counter: {((5, 7), (1, 2), 24, 0): 16}
min_switch_R: 25/4
VERDICT: PASS
```

Therefore the remaining mathematical burden is the geometric classification:

```text
deficient cap
=> the positive geodesic component touched by the switch is the nested 5/7
   component above, possibly with disjoint appendages that do not reduce R on S.
```

Once that classification is proved, the sign conclusion follows by this table.

#### Guardrail: Deficient Caps Can Live in Zero-Psi Baggage

The phrase "deficient cap classifies as the nested 5/7 component" is too narrow
globally.  A stress graph formed by gluing the canonical deficient component to
an extra `C5` by a cut bridge gives:

```text
n=15, defcap=720, global_fail=0
crossing length types:
  (5,7)   x80
  (5,5,7) x640
```

In a representative `(5,5,7)` switch,

```text
crossM = {(0,8),(1,7),(13,14)}
ell    = {5,7,5}
bdyB   = {(3,8),(4,8),(12,13)}
Wit(3,8)=Wit(4,8)={(0,8),(1,7)}
Wit(12,13)={(13,14)}
```

The deficient singleton cap is `{(12,13)}`, touched only by the pure `C5` bad
edge `(13,14)`.  It contributes zero `Psi`; the positive value `Psi=24` comes
from the disjoint nested `5/7` core.  All residuals are still nonnegative.

So the classification target must be:

```text
deficient cap
=> either a zero-Psi pure odd-cycle baggage cap,
   or the positive nested 5/7 deficient core;
and zero-Psi baggage cannot create negative residual when combined with a
positive core because it is K-disjoint or only raises the ambient N term.
```

This is the correct form of the deficient-cap sign atom.  The N<=10 census sees
only the positive nested core because there is no room for extra pure-cycle
baggage.

#### Algebraic Baggage Lemma

The sign part is stable under `K2`-disjoint sums.  Suppose the bad-edge set
splits into geodesic-support components `M=M_1 dotcup ... dotcup M_r`, meaning
no shortest row of a bad edge in `M_a` shares a vertex with a shortest row of a
bad edge in `M_b` for `a!=b`.  Let `V_a` be the union of the row supports in
component `a`, and let

```text
T_a, K2_a, R_a^loc
```

be the load, second-moment matrix, and residual computed using only `M_a` and
ambient size `|V_a|`:

```text
R_a^loc(u) = |V_a|*T_a(u) - (K2_a*T_a)(u).
```

For the full graph on `N` vertices, if `u in V_a`, then

```text
T(u) = T_a(u),
(K2*T)(u) = (K2_a*T_a)(u),
R(u) = R_a^loc(u) + (N-|V_a|)*T_a(u).
```

Therefore a component with nonnegative local residual remains nonnegative after
gluing to any K-disjoint baggage.

Two local components are already settled:

* A pure odd-cycle row of length `L` on exactly `L` vertices has

```text
T(u)=L,  (K2*T)(u)=L^2,  R^loc(u)=0.
```

* The canonical nested `5/7` component has the six-type table above and
  `min R^loc = 25/4`.

Thus, once the geometric classification proves that every deficient-cap switch
is a K-disjoint sum of pure odd-cycle baggage plus possibly one canonical
nested `5/7` component, the deficient-cap sign atom follows immediately.

#### Positive-Core Normal Form To Prove

When the deficient cap lives in the positive component itself, the exact
canonical geometry is more specific than the component signature
`(2,(5,7),Psi=24,exits=2)`.  Up to reversing the switch and relabelling the two
exits, it is:

```text
bad rows:       f0, f1
lengths:        ell(f0)=5, ell(f1)=7
exits:          e_private, e_shared
witness sets:   Wit(e_private)={f0},  Wit(e_shared)={f0,f1}
deficient cap:  Y={e_private}
```

In the labelled canonical atom one instance is:

```text
S=(0,1,6)
f0=(0,8), ell=5, rows:
  0-5-9-3-8
  0-6-9-3-8
  0-5-9-4-8
  0-6-9-4-8
f1=(1,7), ell=7, rows:
  1-6-9-3-8-2-7
  1-6-9-4-8-2-7
e_private=(0,5), e_shared=(6,9)
```

However, when the deficient cap lives in a disjoint pure odd-cycle baggage
component, the positive `5/7` component can appear with both of its exits
shared:

```text
Wit(e1)={f0,f1},  Wit(e2)={f0,f1}.
```

It has the same component surplus

```text
ell(f0)^2+ell(f1)^2 - 2*ell(f0)^2 = ell(f1)^2-ell(f0)^2 = 24
```

and the same nonnegative local residual table.  Thus the remaining geometric
classification should be split into:

```text
DC1. Deficient cap equality |N(Y)|<=|Y| in a neutral positive-Psi
     terminal-shadow switch forces each support component to be either
     zero-Psi pure odd-cycle baggage or a positive nested two-row core.

DC2. A positive deficient support component cannot have three or more crossing
     bad edges.  Otherwise two private/shared terminal corridors form a reduced
     theta, giving either a shorter B-geodesic or a smaller neutral descent.

DC3. A positive nested two-row core has lengths L and L+2.  Its restricted
     exit witness sets are either
       {short}, {short,long}       (cap-local deficient core)
     or
       {short,long}, {short,long}  (disjoint positive core).
     The no-shortcut/odd-girth specialization observed in the census gives
     L=5.
```

The algebraic sign table above already covers the slightly broader `L,L+2`
incidence core for every odd `L>=5`, so `DC3` does not need to prove `L=5`
for the sign atom.  It only needs the nested `L,L+2` incidence with one of the
two witness patterns above.

The refined component-class gate is:

```text
python problems/23/writeup/_codex_defcap_component_class_gate.py \
  --min-n 5 --max-n 10 --glued-c5
```

It returns:

```text
defcap: 736
fail: 0
signatures:
  640 ((2, (5, 7), 24, 2), (1, (5,), 0, 1))
   96 ((2, (5, 7), 24, 2),)
VERDICT: PASS
```

Here each component signature is

```text
(number of crossing bad edges, sorted lengths, component Psi, number of exits).
```

Thus the exact finite shadow of the classification is:

```text
positive deficient-cap core: (2, (5,7), Psi=24, exits=2);
optional zero-Psi baggage:  (1, (L),   Psi=0,  exits=1), L odd.
```

The path-level normal form of the positive component is:

```text
python problems/23/writeup/_codex_defcap_theta_gate.py \
  --min-n 5 --max-n 10 --glued-c5
```

which returns:

```text
defcap=736
positive=736
baggage=640
theta=736
fail=0
theta_sig={(5,7,'trim_left',5,7):736}
VERDICT=PASS
```

Here `trim_left` means that for the two-row positive component, a shortest
row of the length-7 edge contains contiguously a shortest row of the length-5
edge after one terminal endpoint of the short row is removed.  A canonical
example is:

```text
short row Q = (0,6,9,3,8)
long  row P = (1,6,9,3,8,2,7)
contained core = (6,9,3,8)
```

So the cap-side deficient core is also a 5/7 terminal theta, but it is not the
same subpath relation as the row-side REX gate:

```text
row REX:   full length-5 row is a contiguous block of the length-7 row;
cap core:  a one-ended length-5 row core is a contiguous block of the
           length-7 row.
```

The geometric proof must allow this distinction.  Both forms say the same
structural thing: the long row is obtained from a short row/corridor by one
triangle-free two-edge terminal annulus.

The N=11 deficient-cap signature risk was checked by a 16-shard exact run:

```text
python problems/23/writeup/_codex_defcap_signature_mine.py \
  --n 11 --shard i --nshards 16
```

Aggregated result:

```text
defcap=1110
single signature only:
  (|C|=2, ell=(5,7), witness degrees=(1,2), |Y|=1, gap=0)
```

So the N=11 census introduces many more host occurrences but no new deficient
template such as `(5,9)`, `|C|=3`, or `|Y|=2`.

The sign calculation is not numerically fragile in the literal `5/7` values.
Keeping the same canonical incidence pattern but replacing the row lengths by
`L` and `L+2` gives:

```text
vertex type        R(L)
(p0,p1)=(1,0)      3L-6
(0,1)              L/2+7
(1/2,1/2)          7L/4+1/2
(1/2,0)            7L/4-5/2
(1/2,1)            7L/4+7/2
(1,1)              7L/2+1
```

Hence the same incidence core has positive residual for every odd `L>=5`.
If the geometric classification naturally yields a nested `L/(L+2)` core
before the no-shortcut argument specializes it to `5/7`, the algebraic sign
part still survives.

A fixed-cut stress with canonical core plus a glued `C7` gives:

```text
total defcap=52
48 ((2, (5, 7), 24, 2), (1, (7,), 0, 1))
 4 ((2, (5, 7), 24, 2),)
```

so the zero-Psi baggage allowance must be arbitrary pure odd-cycle length, not
only length `5`.

#### Restricted Positive-Overload Lens Guardrail

Claude's 20:16 GPT-Pro route invokes a positive-overload lens mechanism.  The
unrestricted per-edge version is false: the exact gate

```text
python problems/23/writeup/_lens_peredge_gate.py
```

finds `40` failures on the `MycGrotzsch_N23` stress cut, all with
`C_g(v)>0` but `g` not a short member of a strict lens through `v`.

The version that matches the selected proof domain is restricted to negative
residual vertices:

```text
R[v] < 0,  C_g(v)>0
=> g is a short member of a strict lens through v.
```

The reproducible gate is:

```text
python problems/23/writeup/_codex_restricted_peredge_lens_gate.py \
  --min-n 5 --max-n 10 --h-blowups 3
```

and returns:

```text
cuts=18569
positive entries at R<0 vertices=222
covered=222
fail=0
VERDICT=PASS
```

Thus any proof using positive-overload lenses must explicitly use the
`R[v]<0` hypothesis.  The broad statement `C_g(v)>0 => lens` should not be
used.

The sharper miner

```text
python problems/23/writeup/_codex_restricted_lens_mine.py \
  --min-n 5 --max-n 10 --h-blowups 3
```

shows that every positive per-edge contribution at a negative-residual vertex
comes from the same length pattern:

```text
ell(g)=5, longer enclosing lengths=(7,)
```

with exact histogram:

```text
108  through=18/108, C_g(v)=3/2
 32  through=8/32,   C_g(v)=3/2
 27  through=36/108, C_g(v)=3
 18  through=108/108,C_g(v)=9
 12  through=2/4,    C_g(v)=3/2
  9  through=4/4,    C_g(v)=3
  8  through=32/32,  C_g(v)=6
  8  through=16/32,  C_g(v)=3
```

Total positive entries: `222`, all covered by a `5/7` strict lens.  This is
the same terminal theta that appears in the deficient-cap and REX diagnostics.

#### Unified 5/7 Terminal-Theta Rigidity Target

Claude's 20:35 cross-check and the restricted-lens mine collapse the remaining
geometry to one local object.

The current proof target is:

```text
RIGID-5/7.
In a gamma-minimal connected-B maximum cut of a triangle-free graph, every
terminal-shadow obstruction that is relevant at a vertex with R[v]<0 reduces
to a nested 5/7 terminal theta:

  a short bad edge g with ell(g)=5,
  a longer bad edge h with ell(h)=7,
  and a row Q in cyc[g] occurring as a contiguous subpath of a row P in cyc[h].

The difference P \ Q is a single triangle-free two-edge terminal annulus.
Any third terminal row, longer annulus, two-hole residual corridor, or larger
deficient support component gives either a triangle, a shorter B-geodesic for
one of the involved bad edges, or a smaller neutral Gamma-decreasing switch.
```

This is not a broad lens statement.  The exact gate
`_lens_peredge_gate.py` shows that `C_g(v)>0 => lens` is false on the
`MycGrotzsch_N23` stress cut.  The rigidity target must use at least one of
the selected-switch hypotheses:

```text
R[v] < 0,
terminal-shadow obstruction,
neutrality/Gamma minimality,
stage-0 rare matching minimality.
```

The same 5/7 theta appears in all three remaining finite shadows:

```text
cap deficient positive core:
  (2 crossing bad edges, lengths (5,7), Psi=24, two exits);

row singleton residual miss:
  the missed-row edge has ell=7 and contains contiguously an ell=5 F0 row;

restricted positive-overload lens:
  every positive C_g(v) with R[v]<0 has ell(g)=5 and an enclosing length-7 row.
```

Thus the cap sign atom is already algebraic once the component classification
is proved:

```text
R_full(u) = R_local(u) + (N - |V_component|) T(u),
R_local = 0       for pure odd-cycle baggage,
R_local = 25/4    for the 5/7 nested positive core.
```

The remaining cap-side geometry is therefore only:

```text
DC-classification.
A deficient cap in a neutral positive-Psi terminal-shadow switch has K2-support
components that are disjoint sums of:
  type A: one pure odd-cycle baggage edge, arbitrary odd length, Psi=0;
  type B: one nested 5/7 terminal-theta core, Psi=24.
```

The earlier `L,L+2` algebraic table remains a harmless guardrail, but the
finite gates through N=11, glued C5/C7 batteries, and the restricted-lens mine
show no realized `7/9`, `9/11`, ... core.  The geometric proof should aim for
`L=5` directly, not for a general stretched core.

#### Row-Side TH-Corridor Atom

The attached 20:36 GPT-Pro note gives the row-side version of the same
rigidity.  It is the proof atom for the exact gate:

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182, row_miss={0:989,1:72}, two-hole=0, VERDICT=PASS
```

For a terminal-shadow switch `S`, a crossing bad edge `f`, and an exit
`e = x_e y_e` with `x_e in S`, define the terminal slack

```text
s_f(e) =
  d_{B[S]}(tau_f, x_e) + 1 + d_{B[V\S]}(y_e, sigma_f)
  - d_B(tau_f, sigma_f).
```

Then `f` witnesses `e` iff `s_f(e)=0`, and every positive slack is at least
`2` by parity.  In one residual connected component `(A,B)`, form the
exit co-witness graph `J(A,B)` on exits:

```text
e ~ e'  iff  some g in A witnesses both e and e'.
```

Since the residual witness component is connected, `J(A,B)` is connected.
A row missing two exits yields a shortest co-witness corridor

```text
e0, g1, e1, g2, ..., gk, ek
```

with

```text
s_f(e0)>0, s_f(ek)>0, and s_f(ei)=0 for 1<=i<=k-1.
```

The row proof target is:

```text
TH-Corridor.
No such shortest two-hole residual corridor exists.
```

It splits into two exact-testable subatoms.

```text
TH-long.
If lambda(e0)>L0 or lambda(ek)>L0, the terminal row disk made from f and the
hinge rows gi contains either a triangle or a B-path for some h in {f,g_i}
of length at most d_B(endpoints(h))-2.
```

This is the reduced two-hinge lens.  In the 5/7 cases it is exactly the
terminal theta: one hinge improves the slack of `f`, the other worsens it, and
the smaller diagonal saves two B-edges unless the annulus is the rigid 5/7
one already accounted for.

```text
TH-rare.
If both missed endpoints have lambda=L0, then the stage-0 F0-E0 rare matching
has a negative-cost alternating exchange rooted at one of these unmatched
minimum exits:

  sum_{z in Z} deg_F1(z) < sum_{u in U} deg_F1(u).
```

This kills the minimum-lambda double miss.  A single minimum-lambda miss can
survive, matching the finite gate's `row_miss<=1`.

Together:

```text
two row misses
=> shortest TH-corridor
=> TH-long contradiction or TH-rare contradiction
=> component-local single-miss theorem.
```

This is the row analogue of the cap component classification.  Both should be
proved by the same terminal theta/no-shortcut geometry, plus the stage-0
min-cost matching only in the minimum-door case.
