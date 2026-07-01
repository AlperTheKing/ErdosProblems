# Side-Door Hall Proof Target

This note isolates the matching lemma for the completed seed+moat K2T switch.
It is the current non-computational bottleneck after the exact descent identity.

## Terminal Witness Graph

Let `S` be a neutral terminal-shadow-gated switch.  Define:

```text
F = delta_M(S)        old bad edges crossing S
E = delta_B(S)        old cut edges crossing S
```

For `f in F` and `e in E`, write `f ~ e` if some shortest B-geodesic row of
`f`, oriented from the endpoint of `f` inside `S`, remains in `S` up to its
first exit and exits through `e`.

Let

```text
Wit(f) = { e in E : f ~ e }
lambda(e) = min { ell(f) : f ~ e }.
```

Since every witness of `e` has length at least `lambda(e)`, any matching from
`E` into `F` through this witness graph gives termwise length domination.  A
matched pair with `ell(f)>lambda(e)` gives strict positive `Psi`.

Thus the matching content is Hall:

```text
for every Y subset E,  |{f in F : Wit(f) subset Y}| <= |Y|.
```

## Right-Closed Hall Form

The exact gate uses the length-filtered right-closed version.  For a cutoff
`t` and `Y subset E_<t := {e : lambda(e)<t}`, define

```text
X = { f in F : ell(f)<t and Wit(f) subset Y }.
```

Target:

```text
|X| <= |Y|       for every (t,Y).
```

Taking `t` above all lengths gives ordinary Hall.  The filtered version also
tracks strictness.

## Prefix Hull For A Hypothetical Deficiency

Assume, toward contradiction, that `|X|>|Y|`.  For each `f in X` and each
`e in Wit(f)`, take every terminal prefix inside `S` of each shortest row of
`f` that exits through `e`.  Let

```text
U = union of these terminal prefixes.
```

Then all `f in X` cross the boundary of `U`, and all `e in Y` are allowed
B-boundary exits of `U`.

Write

```text
B_extra = delta_B(U) \ Y,
M_extra = delta_M(U) \ X.
```

If one proves the side-door inequality

```text
|B_extra| <= |M_extra|,
```

then max-cut applied to `U` gives

```text
|Y| + |B_extra| >= |X| + |M_extra|,
```

hence `|Y|>=|X|`, contradiction.

## Side-Door Injection Lemma

It is enough to prove an injection from `B_extra` to `M_extra`.  The exact gate
implements the following candidate relation.

For `b in B_extra`, it may be:

1. an external extra exit of the original switch `S`, i.e. `b in E\Y`; then it
   can be matched to an extra bad edge `g in M_extra` for which `b in Wit(g)`
   and the `S`-side endpoint of `g` lies in `U`;

2. an internal side-door edge, i.e. the first edge by which a terminal segment
   of a row of some `g in M_extra` leaves `U`; then match `b` to such a `g`.

Equivalently, for a right-closed deficient pair `(t,Y)`, define the side-door
graph

```text
Door_t(Y) = (B_extra, M_extra, opens).
```

The local atom is:

```text
SIDE-DOOR HALL.
If X={f : ell(f)<t and Wit(f) subset Y} and |X|>|Y|, then Door_t(Y)
has a matching saturating B_extra.
```

This is deliberately weaker than Hall on arbitrary prefix unions.  The prefix
hull is only used for right-closed trapped sets `X=C_t(Y)`, and every B-boundary
edge not already in `Y` is paid by a side-door bad edge outside `X`.

The resulting contradiction is:

```text
|delta_B(U)| <= |Y| + |B_extra|
              <= |Y| + |M_extra|
              <  |X| + |M_extra|
              =  |delta_M(U)|,
```

contradicting the maximum-cut inequality for `U`.

Exact gate:

```text
python problems/23/writeup/_codex_sidedoor_prefix_hull_gate.py --max-n 10 --h2-allmax --h-inherited 4 --max-add 1 --matching
```

Result:

```text
switches tested: 182
Hall pairs checked: 80008
deficient: 0
fail: 0
```

No deficient pair appears in the battery, so the injection is only a backup
atom; nevertheless it is the local proof mechanism if a deficiency is assumed.

Fresh rerun on 2026-06-30:

```text
python problems/23/writeup/_codex_sidedoor_prefix_hull_gate.py --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1 --matching

cuts with R<0: 13
negative vertices: 182
switches tested: 182
Hall pairs checked: 80008
deficient: 0
skipped thresholds: 89
fail: 0
moat size: {0:154, 1:28}
```

Thus the exact target for the completed seed+moat family can be stated in the
stronger direct form:

```text
NO RIGHT-CLOSED DEFICIENT EXIT SET.
For every completed seed+moat switch S, every cutoff t, and every
Y subset {e : lambda(e)<t},

  |{f in delta_M(S) : ell(f)<t and Wit(f) subset Y}| <= |Y|.
```

The side-door prefix-hull construction remains the contradiction mechanism for
a hypothetical deficient `Y`.

## 2026-06-30 Guardrail: Broad No-Reentry Is False

The prompt-level no-reentry lens claim was tested literally on all cutoff pairs
for completed seed+moat switches:

```text
python problems/23/writeup/_codex_no_reentry_lens_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap-et 14

switches: 119
pairs: 27062
nonterminal: 66388
fail: 28
```

First failure:

```text
t = 6
Y = {(2,14),(2,15),(3,12),(4,12),(5,12)}
X = {(12,16),(12,17)}
U = {2,12}
g = (13,16), ell(g)=5
path = (13,2,14,6,16)
switch = {0,1,2,10,11,12,13}
```

Thus no-reentry cannot be used for arbitrary `Y`.  It may only be invoked,
if proved, inside a minimal right-closed deficient core.  On the existing
completed-switch battery this scoped test is vacuous because there are no
deficient pairs:

```text
python problems/23/writeup/_codex_no_reentry_lens_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap-et 14 --deficient-only

pairs: 0
fail: 0
```

Additional witness-shape mining:

```text
python problems/23/writeup/_codex_witness_shape_mine.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --hall-cap 14

selected switches: 119
shape types: 13
moat size: {0:91, 1:28}
```

For every selected switch in this battery, every nonempty proper right-closed
exit subset has Hall slack at least `1`; equality occurs only at the empty and
full subsets.  Thus the practical proof target may be sharpened to:

```text
STRICT PROPER RIGHT-CLOSED HALL.
If empty != Y != E is right-closed in the completed seed+moat switch, then
|{f : Wit(f) subset Y}| <= |Y|-1.
```

The cutoff version has the same observed strictness for all checked
`Y subset {e : lambda(e)<t}`.

## Proof Tasks

1. Prefix closure: show the prefix hull `U` is well-defined and every `f in X`
   contributes a distinct bad boundary edge of `U`.
2. Boundary localization: show every B-boundary edge of `U` not in `Y` is a
   side-door edge of one of the two types above.
3. Side-door matching: prove the side-door relation from `B_extra` to `M_extra`
   has a matching saturating `B_extra`.  This is the finite local Hall atom.
4. Strictness: use `R[v]<0` and the completed seed+moat selector to prove at
   least one matched witness has `ell(f)>lambda(e)`.
5. Combine with the exact identity `DeltaGamma(S)=-Psi(S)`.

## Current Exact Evidence

Completed switch selector with one moat vertex:

```text
max-n11 + H2 all-max + H inherited to 4 + random200:
negative 193, covered 193, fail 0, moat histogram {0:165,1:28}.
```

Neutralizer rule for one-moat cases:

```text
(delta(A), delta({z}), delta(S), e_B(z,A), e_M(z,A))
= (4,0,0,2,0) or (2,0,0,1,0), with 0 failures over all 28 one-moat cases.
```

## 2026-06-30 Obstruction: Terminal-Shadow Alone Is False

GPT-Pro proposed, and local exact check confirmed, a 17-vertex multi-door fan where
terminal-shadow, neutrality, maximum cut, and component balance all hold, but
right-closed Hall fails.

Witness sets are:

```text
Wit(vu1) = {vb1}
Wit(vu2) = {vb1}
Wit(vu3) = {vb1,vb2,vb3}
```

For `Y={vb1}` and cutoff `t=6`:

```text
X={vu1,vu2}, |X|=2>|Y|=1.
U={v}.
Bextra={vb2,vb3}, Mextra={vu3}.
```

So the side-door inequality fails:

```text
|Bextra|=2 > 1=|Mextra|.
```

The missing condition is a fan-capacity/no-multidoor property: an extra bad
edge outside `X` must not be able to open multiple extra B exits of the prefix
hull.  Therefore the Hall proof must use the special completed length-bundle
seed plus optional one-vertex moat structure, not terminal-shadow axioms alone.

## Candidate Residual-Hall Lemma

The multi-door fan obstruction has no negative residual vertices: exact check gives
`R[v]>0` for every vertex; in the 17-vertex fan above the exact minimum is
`min_v R[v]=50/3`.  Conversely, a brute-force census search found no
Hall-deficient neutral B-connected terminal-shadow switch at all through `N<=10`:

```text
N<=10 terminal switches checked: 129552
deficient right-closed Hall pairs: 0.
```

A cleaner possible theorem is therefore:

```text
If S is a neutral B-connected terminal-shadow switch and S contains a vertex v
with R[v]<0, then the witness graph of S satisfies right-closed Hall.
```

This would separate the proof into:

1. construction: `R[v]<0` gives some completed seed+moat terminal-shadow switch
   `S` containing `v`;
2. residual Hall: any such `S` containing a negative-residual vertex has the
   SDR/right-closed Hall property;
3. strictness: the selected completed switch has at least one strict witness,
   equivalently `Psi(S)>0`.

The GPT fan shows that the negative-residual premise, or a comparably strong
fan-capacity premise, is necessary.

## 2026-06-30 Structural Diagnostics

Chain/Ferrers shortcut is false.  The diagnostic

```text
python problems/23/writeup/_codex_witness_structure_diag.py
```

on the same selected-switch battery produced:

```text
records=182
chainF false in 118
chainE false in 118
induced 2K2 present in 118
```

So Hall cannot be proved by saying the witness graph is a chain/Ferrers graph.
The first non-chain example is an `H?AFBo][2]` switch with an induced `2K2` in
its witness relation.

A more useful equivalent form is the complement-capacity version.  For a cutoff
`t`, let

```text
E_t={e in E : lambda(e)<t}
F_t={f in F : ell(f)<t}.
```

For `Z subset E_t`, define

```text
A(Z)={f in F_t : Wit(f) cap Z = empty}.
```

Then Hall is equivalent to

```text
|A(Z)| + |Z| <= |E_t|       for every Z subset E_t.
```

The diagnostic

```text
python problems/23/writeup/_codex_complement_cap_gate.py
```

checked this form over the selected seed+moat battery:

```text
records=182
checked=8042324
fail=0
```

The only zero slack displayed by the gate is the trivial case `Z=E_t` with
`A(Z)=empty`; proper nonempty subsets have positive slack in the existing
battery.  This suggests the proof target can be restated as:

```text
STRICT PROPER COMPLEMENT-CAP.
For every completed seed+moat switch, cutoff t, and nonempty proper
Z subset E_t,

  |{f in F_t : Wit(f) cap Z = empty}| + |Z| <= |E_t|-1.
```

This is equivalent to strict proper right-closed Hall, but may be easier to
prove geometrically: exits in `Z` cannot be simultaneously avoided by too many
short crossing bad edges.

## 2026-06-30 Witness-Shape Catalogue

The diagnostic

```text
python problems/23/writeup/_codex_witness_canonical_shapes.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --top 30
```

uses a WL-style signature of the actual bipartite witness matrix, seeded by
bad-edge lengths and exit lambdas.  On the selected completed seed+moat
battery it reports:

```text
shape_count: 13
moat: {0:91, 1:28}
psi: {24:21, 48:28, 96:70}
```

The base census shape is the `N=9` `K_{2,2}` witness graph:

```text
F_lens=(5,7), E_lambdas=(5,5), count=21.
```

Every H2 all-max shape in the catalogue is built from length-5 and length-7
witness blocks.  The inherited H2 cut alone gives only five of the thirteen
signatures:

```text
python problems/23/writeup/_codex_witness_canonical_shapes.py --min-n 11 --max-n 10 --h-inherited 2 --max-add 1 --top 10

shape_count: 5
moat: {0:14}
psi: {48:4, 96:10}
```

In every listed shape the Hall profile has `min_slack=0` and exactly three
zero-slack cutoff subsets: the trivial empty/full length-filtered subsets.
Thus the empirical shape catalogue supports a finite-shape proof strategy,
but the signature is diagnostic only; it is not an isomorphism certificate and
does not by itself prove that all future blowups have the same shapes.

## 2026-06-30 Two-Stage Length-Tier SDR

The representative matchings in the witness-shape catalogue have a sharper
common form.  Let

```text
F0 = {f in delta_M(S) : ell(f) is minimum},
E0 = {e in delta_B(S) : lambda(e) is minimum}.
```

The diagnostic

```text
python problems/23/writeup/_codex_length_tier_matching_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

tests the following two-stage construction:

1. match every `f in F0` into `E0`;
2. after removing those used exits, match every remaining exit using only
   `delta_M(S)\F0`.

Result:

```text
tested: 119
status: {'ok': 119}
VERDICT: PASS
```

The exact class summary is:

```text
70 cases: E0=8, F0=4, F1=4, E_rem=4, psi=96
21 cases: E0=2, F0=1, F1=1, E_rem=1, psi=24
16 cases: E0=4, F0=2, F1=4, E_rem=4, psi=48
 8 cases: E0=4, F0=2, F1=3, E_rem=3, psi=48
 4 cases: E0=4, F0=2, F1=2, E_rem=2, psi=48
```

Inherited H2 alone also passes:

```text
tested: 14
status: {'ok': 14}
```

Inherited H3 and H4 stress also pass:

```text
python problems/23/writeup/_codex_length_tier_matching_gate.py --min-n 11 --max-n 10 --h-inherited 3 --max-add 1

tested: 35
status: {'ok': 35}
psi up to 216

python problems/23/writeup/_codex_length_tier_matching_gate.py --min-n 11 --max-n 10 --h-inherited 4 --max-add 1

tested: 63
status: {'ok': 63}
psi up to 384
```

In every checked case, `min_len=min_lam=5`; strict matched pairs are exactly
the `(ell,lambda)=(7,5)` pairs, and `Psi=24*(number of strict pairs)`.

Thus a sharper possible proof target is:

```text
TIER-SDR.
For every completed seed+moat switch, the minimum-length crossing bad edges
can be matched into minimum-lambda exits, and all remaining exits can be
matched using longer crossing bad edges.
```

This makes strictness automatic whenever the completed switch has `Psi>0`.
However, under neutrality `|delta_M(S)|=|delta_B(S)|`, existential TIER-SDR is
equivalent to the ordinary SDR: any SDR saturating exits uses every crossing
bad edge, and a minimum-length bad edge can only witness a minimum-lambda exit.
Thus TIER-SDR is not an independent proof of Hall.  Its value is diagnostic:
it shows that the SDR, when it exists, is length-layered, and suggests a proof
by shortest-layer matching plus longer-edge completion.

Guardrail: the first-stage matching is not arbitrary.  The stronger statement
"every matching of `F0` into `E0` extends" is false:

```text
python problems/23/writeup/_codex_length_tier_matching_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --all-stage0

tested: 119
status: {'ok':115, 'stage1_all':4}
first failure:
  H2-allmax side=001111111111000000, v=2, S={2,12,13}
```

The inspector

```text
python problems/23/writeup/_codex_tier_failure_inspect.py
```

shows `276` first-stage matchings in the first failure, of which `252` extend
and `24` do not.  The non-extending choices consume the two universal exits
asymmetrically and leave too many side-specific exits for the longer bad-edge
classes.  Therefore the proof target is existential TIER-SDR, or a canonical
balanced shortest-stage rule, not robust extension for every first-stage SDR.

## 2026-06-30 Candidate: Rare-Exit First Shortest Tier

The failed robust-stage0 examples suggest a canonical balance rule.  Among all
matchings of minimum-length bad edges `F0` into minimum-lambda exits `E0`,
choose one that consumes exits in increasing order of their degree into the
longer tier

```text
deg_F1(e) = |{ f in F\F0 : f witnesses e }|.
```

Equivalently, take a minimum-cost matching with cost

```text
cost(e) = deg_F1(e) * BIG + deterministic_tiebreak(e).
```

Then ask the longer bad edges `F1` to match all remaining exits.  This avoids
the known non-extending choices, which consume universal exits before
side-specific exits and leave an unbalanced residual for the longer tier.

The diagnostic script is:

```text
python problems/23/writeup/_codex_balanced_stage0_gate.py
```

Exact local gates:

```text
python problems/23/writeup/_codex_balanced_stage0_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested: 119
status: {'ok': 119}

python problems/23/writeup/_codex_balanced_stage0_gate.py --min-n 11 --max-n 10 --h-inherited 4 --max-add 1

tested: 63
status: {'ok': 63}

python problems/23/writeup/_codex_balanced_stage0_gate.py --min-n 5 --max-n 11 --max-add 1

tested: 32
status: {'ok': 32}
```

Candidate lemma:

```text
RARE-EXIT TIER SDR.
For every completed seed+moat switch selected from a negative-residual vertex,
the rare-exit-first minimum-length matching of F0 into E0 leaves a set of exits
that can be saturated by F1.
```

This is still only a proof target.  It should be independently exact-gated on
Claude's full battery before being used in the proof.

The stronger residual shape to keep is not completeness.  A later H2 all-max
check found non-complete residual components, so the complete-block version is
false.  The surviving statement is componentwise strict Hall:

```text
RARE-EXIT COMPONENT-STRICT HALL.
After the rare-exit-first matching of F0, the residual witness graph between
F1 and the remaining exits is a disjoint union of balanced components, and
inside each component the only Hall-tight exit subsets are empty and full.
```

This immediately implies the residual matching step.  It is more proof-friendly
than raw Hall, because the remaining job is component-local and proper subsets
have positive Hall slack.

Diagnostic:

```text
python problems/23/writeup/_codex_rare_exit_profile.py --min-n 11 --max-n 10 --h-inherited 4 --max-add 1

profile_count: 12
all residual components balanced; inherited cases happen to be complete

python problems/23/writeup/_codex_rare_exit_profile.py --min-n 5 --max-n 11 --max-add 1

profile_count: 2
all residual components balanced with Hall zeros=2 per component

python problems/23/writeup/_codex_rare_exit_profile.py --min-n 5 --max-n 10 --h2-allmax --max-add 1

profile_count: 11
non-complete residual components occur, e.g. (4,4,14,False), (4,4,12,False),
but every residual component still has Hall profile (0,2,*).
```

Here a residual component signature is `(left_count,right_count,edge_count,
is_complete,hall_profile)`, where `hall_profile=(min_slack,zero_count,total)`.
The H4 inherited profiles include examples with several balanced components,
e.g.

```text
((4,4,16,True,(0,2,16)), (4,4,16,True,(0,2,16)),
 (4,4,16,True,(0,2,16)))
```

which explains why residual Hall can have more than the two trivial zero-slack
sets while still being controlled componentwise.

The component-strict Hall condition has an even simpler sufficient form.  In a
balanced residual component `C` with `n` longer bad edges and `n` remaining
exits, let the complement record missing witness incidences.  It is enough that:

```text
each longer bad edge misses at most one remaining exit;
each remaining exit is missed by at most n-2 longer bad edges.
```

Indeed, if `|Y|>=2`, then every left vertex sees at least one exit in `Y`,
because it misses at most one exit total.  If `|Y|=1`, the second condition
gives at least two neighbors.  Thus every nonempty proper `Y` has
`|N(Y)|>=|Y|+1`.

Exact gate:

```text
python problems/23/writeup/_codex_rare_exit_complement_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested: 119
status: {'ok': 119}

python problems/23/writeup/_codex_rare_exit_complement_gate.py --min-n 11 --max-n 10 --h-inherited 4 --max-add 1

tested: 63
status: {'ok': 63}

python problems/23/writeup/_codex_rare_exit_complement_gate.py --min-n 5 --max-n 11 --max-add 1

tested: 32
status: {'ok': 32}
```

This is currently the sharpest proof target for the residual matching step:
prove rare-exit stage0 leaves balanced residual components whose missing
witness incidences satisfy the two complement-degree bounds above.

Geometric reading from the first non-complete H2 all-max example:

```text
remaining exits = universal exits seen by every longer edge
                + one side-specific exit on each terminal side;
each longer edge misses only the side-specific exit on the opposite side.
```

Thus the complement-degree proof should be organized as:

1. classify exits of the completed seed+moat switch into universal exits and
   terminal-side exits ordered along the seed boundary;
2. show rare-exit stage0 consumes the earliest/lowest-F1-degree side exits;
3. show every longer crossing bad edge can miss only terminal-side exits on
   the opposite side, and after rare-exit at most one such exit remains in its
   residual component;
4. show every remaining exit has at least two longer witnesses unless the
   component has size one.

These four geometric statements imply the complement-degree bounds and hence
the residual SDR.

## 2026-06-30 Exit-Class Residual Form

The complement-degree residual can be compressed further.  After the rare-exit
stage0 matching, work inside one balanced residual component between longer
bad edges `F1_C` and remaining exits `E_C`.  Partition the exits by their
identical longer-tier witness set:

```text
E_C = disjoint union of classes E_A,
where A = {f in F1_C : f witnesses e} is constant for e in E_A.
```

Let `r_A=|E_A|`.  Then the component complement-degree bounds are equivalent
to the following class inequalities:

```text
for every f in F1_C:
    sum_{A : f notin A} r_A <= 1;

for every class A with r_A>0:
    |F1_C|-|A| <= max(0, |F1_C|-2).
```

The second condition says that a singleton remaining exit has at least two
longer witnesses unless the whole residual component is `K_{1,1}`.  These two
conditions imply strict proper Hall componentwise:

* if `|Y|>=2`, every longer bad edge sees some exit in `Y`, because it misses
  exits of total multiplicity at most one;
* if `|Y|=1`, the chosen exit has at least two longer witnesses unless the
  component has size one.

The exact quotient gate is:

```text
python problems/23/writeup/_codex_rare_exit_class_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested: 119
status: {'ok': 119}

python problems/23/writeup/_codex_rare_exit_class_gate.py --min-n 11 --max-n 10 --h-inherited 4 --max-add 1

tested: 63
status: {'ok': 63}

python problems/23/writeup/_codex_rare_exit_class_gate.py --min-n 5 --max-n 11 --max-add 1

tested: 32
status: {'ok': 32}
```

Fresh side-door Hall rerun on 2026-06-30:

```text
python problems/23/writeup/_codex_sidedoor_prefix_hull_gate.py --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1 --matching

cuts with R<0: 13
negative vertices: 182
switches tested: 182
Hall pairs checked: 80008
deficient: 0
fail: 0
moat size: {0: 154, 1: 28}

python problems/23/writeup/_codex_sidedoor_prefix_hull_gate.py --min-n 11 --max-n 11 --max-add 1 --matching

cuts with R<0: 1
negative vertices: 11
switches tested: 11
Hall pairs checked: 128
deficient: 0
fail: 0
moat size: {0: 11}
```

Combined current side-door battery:

```text
switches tested: 193
right-closed cutoff pairs checked: 80136
deficient pairs: 0
fail: 0
```

The first non-complete H2 all-max residuals have only the following class
shapes, up to component size:

```text
n=4: ((3,1,1), (3,1,1), (4,0,2))
n=4: ((2,2,1), (2,2,1), (4,0,2))
n=3: ((2,1,1), (3,0,2))
```

Each triple is `(class_neighbor_count, class_missing_count, class_size)`.
Thus the geometric proof can target a finite-looking exit-class phenomenon:
rare-exit stage0 leaves only universal classes plus at most one unit of
side-specific missing mass against each longer bad edge.

Sparse residual inspection gives an even smaller canonical list.  After the
stage0 matching, every non-complete residual component found in the current
battery is one of the following matrices, up to row/column relabeling:

```text
3 x 3, 8 edges:
  111
  111
  11.

4 x 4, 14 edges:
  1.11
  .111
  1111
  1111

4 x 4, 12 edges:
  111.
  11.1
  111.
  11.1
```

Equivalently, every sparse component consists of universal exit classes plus
one or two singleton non-universal exit classes, and the missing row sets of
the non-universal classes are disjoint:

```text
(3,8):  one singleton exit misses one row;
(4,14): two singleton exits miss two distinct rows;
(4,12): two singleton exits miss two disjoint pairs of rows.
```

The exact diagnostic command is:

```text
python problems/23/writeup/_codex_rare_exit_sparse_inspect.py --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

sparse signatures: 3
```

The isolated `N=11` census slice has no sparse residual components:

```text
python problems/23/writeup/_codex_rare_exit_sparse_inspect.py --min-n 11 --max-n 11 --max-add 1

sparse signatures: 0
```

These three matrices imply strict proper Hall directly.  Therefore the
geometric proof may be sharpened further:

```text
SPARSE RESIDUAL CLASSIFICATION.
After rare-exit stage0, every residual component is either complete bipartite
or one of the three matrices above.
```

This is stronger than `(CQ1)-(CQ3)` in the tested domain and has a more
concrete geometric interpretation: a completed seed+moat switch has at most
two residual side-exit defects in any component, and if there are two then
their missed longer-edge sets are disjoint.

The same statement can be written without naming the three matrices:

```text
TWO-STAR COMPLEMENT THEOREM.
After rare-exit stage0, in each balanced residual component, the complement of
the witness graph is a disjoint union of at most two stars whose centers are
exit vertices.  Equivalently:

  * every non-universal exit class is a singleton;
  * there are at most two non-universal exit classes in a component;
  * their missing longer-edge sets are pairwise disjoint.
```

The three sparse matrices are exactly the nonempty cases of this theorem that
occur in the current battery: one star of size `1`, two stars of size `1`, or
two disjoint stars of size `2`, with enough universal exits to balance the
component.  This formulation is the likely geometric invariant: residual
defects are side doors, and a completed seed+moat switch has at most one
unconsumed side door on each terminal side.

Exact gate for this formulation:

```text
python problems/23/writeup/_codex_two_star_complement_gate.py --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested: 182
status: {'ok': 182}
non-complete signatures:
  16 x ((4, 14, ((1, 1), (1, 1)), 2))
   8 x ((3,  8, ((1, 1),),        2))
   8 x ((4, 12, ((2, 1), (2, 1)), 2))

python problems/23/writeup/_codex_two_star_complement_gate.py --min-n 11 --max-n 11 --max-add 1

tested: 11
status: {'ok': 11}
components: ((1, 1, (), 1),)
```

Here each residual component signature is

```text
(n, edge_count, complement_star_sizes, number_of_universal_exits).
```

Why this classification proves the residual Hall step:

* A complete `n x n` residual component has `|N(Y)|=n>=|Y|` for every
  nonempty `Y`, with equality only at the full component.
* In the `3 x 3` sparse matrix, the only non-universal column misses one row.
  A singleton column has at least two neighbors, every two-column set has all
  three row-neighbors, and the full set has equality.
* In the `4 x 4, 14-edge` matrix, each non-universal column misses a different
  row.  Singleton columns have at least three neighbors, any two-column set has
  at least three row-neighbors, any three-column proper set has all four, and
  the full set has equality.
* In the `4 x 4, 12-edge` matrix, the two non-universal columns miss disjoint
  row-pairs.  A singleton defect column has two neighbors, the two defect
  columns together have all four row-neighbors, and any proper set containing a
  universal column has all four row-neighbors.  Thus every proper subset has
  nonnegative Hall slack, and every nonempty proper subset has a neighbor set
  of size at least its own size.

So the remaining SDR proof can be split cleanly:

```text
(A) stage0 shortest-tier matching exists and leaves balanced components;
(B) every non-complete residual component is one of the three sparse matrices;
(C) the three matrices and complete components satisfy Hall.
```

Part `(C)` is the elementary finite check above.  Part `(B)` is now the
geometric core: prove that after the rare-exit stage, every residual exit
defect is a singleton terminal side-defect and that two such defects have
disjoint missed longer-edge sets.

Guardrail: `(A)` is not true for an arbitrary shortest-tier matching.  The
stage0 matching must be the rare-exit/min-cost one, i.e. match `F0` into `E0`
while consuming exits of smallest `F1`-degree first.  The stronger
all-stage0 claim is false:

```text
python problems/23/writeup/_codex_length_tier_matching_gate.py --min-n 5 --max-n 10 --h2-allmax --max-add 1 --all-stage0 --enum-cap 100000

tested: 119
status: {'ok': 115, 'stage1_all': 4}
first failing switch:
  H2-allmax side 001111111111000000
  v=2, S=(2,12,13)
  F0=4, F1=4, E0=8, Erem=4, checked_stage0=276, matched=3
```

Thus the proof must justify the canonical rare-exit choice, not a generic
shortest-tier choice.

### Class-Quotient Hall Proposition

The class inequalities above are enough on their own; no further geometry is
needed once they are established.  Equivalently, it is enough to prove the
following three structural facts inside each residual component:

```text
(CQ1) the component is balanced: |F1_C|=|E_C|;
(CQ2) every non-universal exit class has multiplicity one;
(CQ3) the missing sets of the non-universal exit classes are pairwise disjoint,
     and each has size at most |F1_C|-2.
```

Indeed, `(CQ2)` and `(CQ3)` imply that a longer bad edge is missing from exits
of total multiplicity at most one.  Also every exit is witnessed by at least
two longer bad edges unless `|F1_C|=1`; otherwise its class would have missing
set of size `|F1_C|-1`, violating `(CQ3)`.  Therefore every nonempty proper
exit subset has positive Hall slack.

This is the current smallest proof target for the residual matching step:

```text
RARE-EXIT CLASS THEOREM.
For a completed seed+moat switch selected from a negative-residual vertex, the
rare-exit stage0 matching leaves residual components satisfying (CQ1)-(CQ3).
```

The expected geometric interpretation is:

* universal classes are exits seen by every longer crossing bad edge;
* non-universal singleton classes are the last unconsumed side exits on a
  terminal side of the seed boundary;
* a longer bad edge can avoid exits on only one such side, because avoiding two
  residual side exits would give either a shorter terminal lens or a forbidden
  re-entry through the completed seed+moat shadow.

The last bullet is the only genuinely geometric point left in the residual
SDR proof.  It is weaker than the refuted broad no-reentry claim: it is applied
only after rare-exit has consumed all lower-F1-degree exits, and only to the
remaining exit classes of the completed seed+moat switch.

### Guardrail: arbitrary prefix-union star closure is false

The side-door proof must stay inside right-closed Hall-deficient exit sets.
The broader statement "every prefix hull has star-shaped extra B-boundary" is
false even for neutral terminal-shadow switches.

Exact failure:

```text
python problems/23/writeup/_codex_all_terminal_star_gate.py --min-n 10 --max-n 10

N=10 switches=73855 cases=18881 exit_star={True: 18880, False: 1}
first_fail:
  graph I?ABCc]}?
  side 1111100000
  S=(0,1,3,4,7,8,9)
  X={(5,8)}
  extra B={(1,6),(2,9)}
  extra M={(6,7),(6,8)}
```

Inspection shows why this does not threaten the corrected atom.  The witness
graph for this switch has

```text
cross M={(5,8),(6,7),(6,8)}
exits E={(0,5),(1,6),(2,9)}
Wit(0,5)={(5,8)}
Wit(1,6)=Wit(2,9)={(6,7),(6,8)}.
```

For the failing prefix set `X={(5,8)}`, the right-closed exit set is
`Y={(0,5)}` and `C(Y)={(5,8)}`, so `|C(Y)|=|Y|=1`.  It is not a Hall-deficient
pair.  Every right-closed trapped set in this switch is non-deficient:

```text
Y={(0,5)}                  -> |C(Y)|=1, |Y|=1
Y={(1,6),(2,9)}            -> |C(Y)|=2, |Y|=2
Y=E                        -> |C(Y)|=3, |Y|=3
```

Thus this example supports the corrected formulation: arbitrary prefix unions
can have unstarred side doors, but right-closed deficient pairs have not
produced a failure in the exact gate.

### Broad corrected gate

The corrected right-closed side-door gate has now also been run on arbitrary
neutral terminal-shadow switches, not only on selected `R[v]<0` seed+moat
switches:

```text
python problems/23/writeup/_codex_all_terminal_sidedoor_gate.py --min-n 5 --max-n 9 --matching

switches=16048
right-closed pairs=44248
deficient=0
fail=0

python problems/23/writeup/_codex_all_terminal_sidedoor_gate.py --min-n 10 --max-n 10 --matching

switches=113504
right-closed pairs=360696
deficient=0
fail=0
```

So, on the full `N<=10` arbitrary neutral-terminal-shadow census, Hall never
reaches the side-door contradiction stage: there is no right-closed trapped
exit set `Y` with `|C_t(Y)|>|Y|`.

This suggests an even sharper proof target:

```text
NO RIGHT-CLOSED DEFICIENCY.
For every neutral terminal-shadow switch S, every cutoff t, and every
Y subset E_<t, the trapped set

  C_t(Y)={f in C : ell(f)<t and Wit(f) subset Y}

satisfies |C_t(Y)|<=|Y|.
```

The side-door prefix-hull atom remains the max-cut proof route for a
hypothetical deficient pair, but the exact census currently supports the
stronger direct no-deficiency statement.

### Star-door capacity atom for selected blue-closed hulls

For selected seed+moat switches, a stronger reduced-door capacity identity has
been gated.  Given `X subset crossM`, set `Y=Wit(X)`, let `U` be the blue-closed
prefix hull, and put

```text
Z = delta_B(U) \ Y
H = delta_M(U) \ X.
```

In the selected battery, every `h in H` has extra-door set `D(h)` equal to
one of

```text
empty, a singleton {z}, or all of Z.
```

Write

```text
surplus = |Y|-|X|
gap     = |delta_B(U)|-|delta_M(U)|
empty   = #{h in H : D(h)=empty}
full    = #{h in H : D(h)=Z}
missing = #{z in Z : no h has D(h)={z}}
dup     = sum_z max(0, #{h:D(h)={z}} - 1).
```

The exact identity is

```text
full - missing = surplus - empty - dup - gap.
```

Thus the star-door Hall condition `full >= missing` is equivalent to the
capacity inequality

```text
surplus >= empty + dup + gap.
```

Exact gate:

```text
python problems/23/writeup/_codex_star_capacity_decomp.py

switches=119
cases=920
star_fail=0
identity_fail=0
capacity_fail=0
gap={0:920}
capacity_slack={0:12, 1:272, 2:212, 3:216, 4:112, 5:96}
```

The zero-slack atoms are all H?AFBo][2] seed+moat cases with:

```text
|Z|=2, gap=0, full=0, missing=0, dup=2, empty in {0,1}.
```

So the current smallest proof target for selected blue-closed hulls is:

```text
CAPACITY PAYMENT LEMMA.
The original witness surplus |Y|-|X| pays every empty-door extra bad edge
plus every duplicate singleton-door waste, with no selected max-cut gap.
```

This is weaker and more concrete than proving arbitrary reduced multidoor fan
expansion directly.  Once this capacity lemma is proved, the selected
star-door residue has Hall, and the two-star/rare-exit quotient finishes the
residual SDR step.

### Side-clean and reduced fan-core gates

The user's side-clean component lemma splits the quotient argument from the
geometry.  Two exact diagnostics were added.

First, `SC1/SC4` partial gate:

```text
python problems/23/writeup/_codex_side_clean_component_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119
status={'ok':119}
```

This confirms, on the selected finite/H2 battery, the component shadow boundary
identity

```text
delta_M(W_C)=L_C dotcup Z_C
delta_B(W_C)=R_C dotcup mu(Z_C)
```

for either the raw terminal-prefix shadow or its blue-closure inside `S`, and
also confirms the SC4 condition that every non-universal residual exit has at
least two longer-edge witnesses except the `K_{1,1}` atom.

Guardrail: the literal canonical-shadow version is not blow-up stable as
implemented:

```text
python problems/23/writeup/_codex_side_clean_component_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182
status={'ok':175,'SC1':7}
first failure: H3-inherited, v=24.
```

The failing H3 component has 1458 raw terminal-prefix atoms, so SC1 may still
have an existential or quotient version, but the naive canonical union is not
the right proof statement at inherited blow-up scale.

Second, the direct reduced fan-core gate:

```text
python problems/23/writeup/_codex_reduced_fan_core_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

switches=119
cases=920
reduced subsets=1324
fail=0
```

This gates the RFC statement directly.  For each selected blue-closed hull it
builds `B+`, `M+`, computes the first-exit door graph `D_X`, enumerates every
nonempty reduced `Z subset B+`, and checks `|N(Z)|>=|Z|`.  No reduced
deficient fan core appears in the selected finite/H2 battery.

The uncapped inherited H3 RFC run was stopped as too slow; a quotient-aware or
capped blow-up version is still needed for stress testing beyond H2.

### Guardrail: peak terminal-overload selector is false without moat completion

The proposed peak terminal-overload selector was gated directly.  For each
`R[v]<0`, the script computes the exact rational terminal overload
`Omega_{L,sign}(v)`, maximizes `Omega/(L*m_L)`, and tests all tied peak
maximizers for neutrality, B-connectivity after flipping, terminal-shadow
validity, and `Psi>0`.

```text
python problems/23/writeup/_codex_peak_terminal_overload_gate.py \
  --min-n 5 --max-n 4 --h2-allmax --h-inherited 4

H2-allmax neg=28 fail=14
status={'ok': 14, 'no-good-peak': 14}
```

First failure:

```text
graph H?AFBo][2]-allmax
side 011111111111000000
v=2, R[v]=-4
peak score=3/5, Omega=3, L=5, m=1

tied peak maximizers:
  sign -: S=(2,12,13), delta_B-delta_M=4
  sign +: S=(2,6,7,8,9,14,15,16,17), delta_B-delta_M=8
```

For comparison, on the opposite all-max side
`001111111111000000`, the same peak tie includes a good seed
`S=(2,12,13)` with `delta=0` and `Psi=96`; the failure above shows this is
not side-invariant.  Therefore the peak terminal-overload lemma is false as
written.  Peak overload may still identify the correct seed scale, but the
valid descent statement must include the already-tested seed+moat completion
step.

## 2026-06-30 Rare-Exit Two-Star Proof Package

The current sharp SDR proof target can be separated into one elementary Hall
proposition and one geometric residual theorem.

### Rare-exit stage0

For a completed seed+moat switch `S`, let

```text
F = delta_M(S),
E = delta_B(S),
Wit(e) = { f in F : f witnesses e },
lambda(e) = min_{f in Wit(e)} ell(f).
```

Let

```text
L0 = min_{f in F} ell(f),
F0 = { f in F : ell(f)=L0 },
F1 = F \ F0,
E0 = { e in E : lambda(e)=L0 }.
```

The rare-exit stage0 matching is a matching of `F0` into `E0` that minimizes
lexicographically the multiset of longer-tier degrees of the consumed exits,
where

```text
deg1(e) = |Wit(e) cap F1|.
```

Equivalently, it consumes the exits that are least useful to the longer tier
first.  The implementation is `min_cost_stage0` in
`_codex_balanced_stage0_gate.py`.

### Residual two-star theorem (geometric target)

After the rare-exit stage0 matching, delete the used exits and restrict the
witness graph to `F1` and the remaining exits.  Then every connected residual
component is balanced.  Moreover, in every such balanced component, the
complement of the witness graph is a disjoint union of at most two stars whose
centers are exit vertices.

Equivalently, in a residual component with longer bad-edge side `A` and exit
side `B`:

```text
(1) |A|=|B|;
(2) every non-universal exit class has multiplicity one;
(3) there are at most two non-universal exit classes;
(4) their missing subsets of A are pairwise disjoint.
```

This theorem is exact-gated by

```text
python problems/23/writeup/_codex_two_star_complement_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

with

```text
tested=182
status={'ok': 182}
VERDICT: PASS
```

The only non-complete residual matrices seen are:

```text
3 x 3, 8 edges:
  111
  111
  11.

4 x 4, 14 edges:
  1.11
  .111
  1111
  1111

4 x 4, 12 edges:
  111.
  11.1
  111.
  11.1
```

These are exactly the nonempty cases of the two-star complement theorem in the
current battery.

### Elementary Hall consequence

Assume a balanced component satisfies the two-star complement theorem.  Then it
has a matching saturating the exit side.

Proof.  Let `Y` be a nonempty proper subset of exits.

If `Y` contains a universal exit, then every longer bad edge is adjacent to
that exit, so `N(Y)=A` and `|N(Y)|=|A|>|Y|`.

If `Y` contains no universal exit, then `Y` consists of one or two singleton
non-universal exits.  A singleton non-universal exit misses at most `|A|-2`
bad edges, so it has at least two neighbors unless the component is `K_{1,1}`.
For two non-universal exits, their missing sets are disjoint; hence the union
of their neighborhoods is all of `A`, so `|N(Y)|=|A|>=|Y|`, and it is strict
unless `Y=B`.  Therefore every nonempty proper `Y` satisfies Hall with positive
slack, and the full set has equality by balance.  Hall's theorem gives the
matching.

Thus the remaining non-computational work is precisely the geometric proof of
the residual two-star theorem: after consuming rare exits, a longer crossing
bad edge can miss at most one residual side-exit, and the two possible side
exit defects lie on opposite terminal sides with disjoint missed longer-edge
sets.  This is weaker than the refuted broad no-reentry statements because it
is applied only after the canonical rare-exit stage0 and only inside the
completed seed+moat switch selected from `R[v]<0`.

### Guardrail: leftover shortest exits need not be universal

A tempting first proof step is false:

```text
after rare stage0, every unmatched minimum-lambda exit is universal to F1.
```

The diagnostic

```text
python problems/23/writeup/_codex_rare_stage0_universal_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested=182
status={'ok': 163, 'rem_e0_not_universal': 19}
VERDICT: FAIL
```

First failure:

```text
graph H2-allmax
side 001111111111000000
v=2
S=(2,12,13)
F0={(12,16),(12,17),(13,16),(13,17)}
F1={(0,12),(0,13),(1,12),(1,13)}
used stage0 exits={(3,12),(3,13),(4,12),(4,13)}
unmatched short exits (5,12),(5,13) have deg_F1=2<4
```

This is still a valid two-star residual component: `(5,12)` misses exactly the
two longer rows with terminal `13`, while `(5,13)` misses exactly the two longer
rows with terminal `12`.  The proof therefore must allow a surviving paired
short side-door; it cannot argue that all residual non-universal exits have
longer lambda.

### Stronger gated invariant: residual defects are terminal-class defects

Although leftover shortest exits need not be universal, the residual defects
are not arbitrary.  For a completed switch `S`, define the `S`-terminal of a
crossing bad edge `f` to be the endpoint of `f` inside `S`.  Similarly define
the inner endpoint of a boundary exit `e`.

The diagnostic

```text
python problems/23/writeup/_codex_residual_terminal_class_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested=182
status={'ok': 182}
VERDICT: PASS
```

It verifies the following sharper structure in every residual component:

```text
for every non-universal residual exit e,
all longer bad edges missed by e have the same S-terminal;

the number of distinct missed S-terminals in a residual component is at most 2.
```

Thus a non-universal exit is a terminal-class defect, not a mixed arbitrary
subset of longer rows.  The sparse examples become:

```text
3x3/8:  one exit misses one terminal class of size 1;
4x4/14: two exits miss two singleton terminal classes;
4x4/12: two exits miss two opposite terminal classes of size 2.
```

This is a more proof-shaped version of the two-star theorem.  A geometric proof
can target:

1. a shortest-geodesic/no-crossing lemma forbidding a residual exit from missing
   rows based at two different S-terminals;
2. a rare-exit exchange lemma forbidding three distinct missed S-terminal
   classes after the stage0 matching;
3. disjointness of the missed terminal classes, which then follows from the
   same no-crossing/terminal-side argument.

### Strongest current finite statement: terminal-block theorem

The terminal-class statement can be made directly Hall-ready.  The diagnostic

```text
python problems/23/writeup/_codex_residual_terminal_block_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

returns

```text
tested=182
status={'ok': 182}
VERDICT: PASS
```

It verifies:

```text
After rare stage0, in every residual component, the non-universal exits
e_1,...,e_s (s<=2) have pairwise disjoint missing sets M(e_i).
Each M(e_i) is contained in a single S-terminal class of longer crossing
bad edges.
```

This is the strongest exact-tested form currently isolated.  It implies the
two-star complement theorem immediately:

* because the missing sets are pairwise disjoint;
* because there are at most two non-universal exits;
* because each non-universal exit has at least two neighbors unless the whole
  component is the trivial `K_{1,1}` atom.

So the geometric proof can target this terminal-block theorem directly:

```text
Rare stage0 + terminal-shadow shortestness + triangle-free
=> at most two disjoint terminal-block defects in each residual component.
```

This avoids proving any false stronger claim about leftover short exits being
universal, and avoids arbitrary-subdiagram leakage inequalities.

### Terminal-block lemma tree

The terminal-block theorem should be proved by three local claims.

#### TB1: no mixed-terminal defect

Let `e` be a residual exit after rare stage0, and let `f,g in F1` be longer
crossing bad edges with distinct `S`-terminals `a_f != a_g`.  If `e` is not a
witness for both `f` and `g`, while `e` lies in the same residual component as
both, then the terminal rows witnessing the component connectivity force a
crossing pair of shortest geodesic corridors.  The desired local conclusion is:

```text
e cannot miss longer rows based at two distinct S-terminals.
```

This should be a pure shortestness/triangle-free statement: two missed terminal
classes would give two row families that both route around the same boundary
exit, producing either a shorter B-geodesic for one crossing bad edge or a
theta subgraph with an odd shortcut.

#### TB2: no overlapping terminal blocks

Let `e` and `e'` be two residual non-universal exits.  Suppose

```text
h in M(e) cap M(e')
```

for a longer crossing bad edge `h`, where `M(e)` is the set of longer rows missed
by `e`.  By TB1, both `e` and `e'` are defects for the same `S`-terminal of
`h` unless there are already two terminal classes.  The desired conclusion is:

```text
M(e) cap M(e') = empty.
```

Geometrically, one longer row based at a fixed terminal cannot avoid two
residual side exits in the same completed switch.  Otherwise the two avoided
exits are two disjoint side doors around the same terminal prefix; sliding the
row to the nearer door either makes it witness one of them or creates a shorter
odd cycle.

#### TB3: rare stage0 excludes a third terminal block

After TB1 and TB2, every residual non-universal exit owns a disjoint terminal
block of missed longer rows.  The remaining finite possibility to exclude is
three such blocks.

Rare stage0 should be used only here.  If three disjoint residual terminal
blocks survive, then there are at least three unmatched exits whose longer-tier
degrees are smaller than the corresponding universal exits on the same
minimum-lambda tier.  Since stage0 is a minimum-cost matching of `F0` into `E0`
with cost `deg_F1(exit)`, an alternating exchange should replace one used exit
by one of the surviving more-rare exits, contradicting minimality.

The exact exchange statement to prove is:

```text
If a residual component after stage0 has three disjoint terminal-block defects,
then there is an alternating path in the F0-E0 witness graph starting at a
surviving defect exit and ending at a used exit of weakly larger deg_F1, with
strictly smaller total rare cost after toggling.
```

This is the only place where the canonical rare-exit matching is used.  TB1 and
TB2 should be independent of the cost rule and follow from terminal-shadow
shortestness.

Together TB1, TB2, and TB3 imply the terminal-block theorem, hence the two-star
component Hall theorem, hence the SDR for the descent switch.

## 2026-06-30 Terminal-Class Residual Proof Target

The guard-lemma/petal route was exact-gated and failed under the natural
vertex-petal interpretation.  The current surviving rare-exit target is the
terminal-class residual theorem below.

For a selected completed seed+moat switch `S` from `R[v]<0`, let

```text
C = delta_M(S),
E = delta_B(S),
Wit(e) = {f in C : f witnesses e},
lambda(e) = min_{f in Wit(e)} ell(f),
L0 = min_{f in C} ell(f),
F0 = {f in C : ell(f)=L0},
F1 = C \ F0,
E0 = {e in E : lambda(e)=L0}.
```

Run the canonical rare-exit stage0 matching

```text
min_cost_stage0(F0, E0, Wit, deg_F1),
where deg_F1(e)=|Wit(e) cap F1|,
```

which consumes low-`deg_F1` exits first.  Delete the used exits and restrict
`Wit` to `F1` and the remaining exits.

### False strengthening

The tempting statement

```text
every unmatched E0-exit is universal to F1
```

is false:

```text
python problems/23/writeup/_codex_rare_stage0_universal_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

status: {'ok': 163, 'rem_e0_not_universal': 19}
```

So the proof must not use this strengthening.

### Surviving theorem candidate

For every connected residual component `(A,B)` of the restricted witness graph:

1. If an exit `e in B` is non-universal, then

   ```text
   Miss(e) = {f in A : f notin Wit(e)}
   ```

   consists only of longer bad edges whose `S`-inside endpoint is one fixed
   terminal vertex `tau(e)`.

2. At most two distinct missed terminal vertices occur in one residual
   component.

3. After quotienting duplicate exit classes, the complement of the residual
   witness graph is a disjoint union of at most two exit-centered stars, with
   disjoint missed bad-edge sets.  Equivalently, the residual component has a
   matching saturating the remaining exits by the elementary two-star Hall
   argument.

Exact gates:

```text
python problems/23/writeup/_codex_residual_terminal_class_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested: 182
status: {'ok': 182}
VERDICT: PASS
```

```text
python problems/23/writeup/_codex_two_star_complement_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested: 182
status: {'ok': 182}
VERDICT: PASS
```

Endpoint diagnostics show the local geometry.  Example:

```text
python problems/23/writeup/_codex_rare_exit_endpoint_diag.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 3 --max-add 1 --limit 6
```

In `H2-allmax`, side `111111111110000000`, `S=(0,1,11,12)`, the residual
exits `(0,13)` and `(1,13)` miss respectively only longer bad edges with
inside endpoints `1` and `0`; the other residual exits are universal.

### Geometric proof target

Prove from terminal-shadow shortest-geodesic geometry:

* A longer bad edge can fail to witness a residual exit only because all its
  terminal prefixes are trapped on the opposite terminal side of that exit.
* If one residual exit missed longer bad edges from two different inside
  terminals, the two terminal-prefix systems plus a common witnessed exit form
  a theta/lens that gives either a shorter odd cycle for one bad edge or a
  triangle.
* If three missed terminal classes occur in one residual component, two of the
  corresponding prefix systems must cross in the same way, again giving a
  shorter-geodesic or triangle contradiction.

This theorem is weaker than the refuted hereditary-leakage and guard-petal
routes, but strong enough with the two-star Hall consequence to finish the
selected K2T Hall/SDR step.

### Two-terminal strengthening

The terminal-class theorem strengthens further to a two-terminal swap form.
For each residual component, every non-universal exit `e` gives a pair

```text
(inside(e), tau(e)),
```

where `tau(e)` is the common `S`-inside endpoint of all longer bad edges missed
by `e`.  The exact gate confirms:

```text
inside(e) != tau(e),
```

and all such pairs in one component use at most two terminal vertices.  Thus a
non-complete residual component is controlled by a two-terminal pair `{a,b}`;
defects are oriented only from `a` to `b` and/or from `b` to `a`.

Gate:

```text
python problems/23/writeup/_codex_residual_two_terminal_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested: 182
status: {'ok': 182}
VERDICT: PASS
```

This is now the cleanest proof target: prove that rare-exit stage0 leaves only
a two-terminal swap residual.  The two-star Hall matching then follows from the
previous elementary argument.

### Stage0 tie-break guardrail

The two-terminal residual does not appear to depend on the deterministic
rank tie-break inside `min_cost_stage0`, at least on the core finite/H2
battery.  The diagnostic

```text
python problems/23/writeup/_codex_stage0_all_min_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1 --cap 200000
```

enumerates every matching of `F0` into `E0` with minimum total `deg_F1` cost
and checks the two-terminal theorem for each resulting residual.  It returns:

```text
tested=119
status={'ok': 119}
VERDICT: PASS
```

Some switches have many tied minimum matchings, e.g. `F0=4,E0=8,count=1680`,
and all still satisfy the two-terminal residual theorem.  This suggests the
proof should use only the minimum-degree stage0 property, not the arbitrary
exit-id rank tie-break.  The inherited blow-up cases were not exhaustively
enumerated by this gate because the number of tied matchings can explode.

### Component-local single-miss strengthening

The residual Hall theorem has an even smaller sufficient form.  After rare
stage0, in every connected residual component `(A,B)` of the `F1`-to-remaining
exit witness graph:

```text
|A|=|B|,
and every f in A misses at most one e in B.
```

Together with the already-gated column condition

```text
every non-universal e in B is witnessed by at least two f in A
```

this gives Hall directly:

* if `B\Y` has size at least `2`, then every `f` sees some exit outside `Y`,
  so no `f` is trapped in `Y`;
* if `B\Y={e}`, then trapped rows are exactly the rows missing `e`; the column
  condition gives at most `|A|-2=|Y|-1` such rows.

Exact gates:

```text
python problems/23/writeup/_codex_rare_exit_complement_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182
status={'ok': 182}
VERDICT: PASS
```

The diagnostic

```text
python problems/23/writeup/_codex_row_miss_diag.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1 --examples 10
```

confirms that the single-miss property is component-local, not global:

```text
global row_miss_count={0:923,1:72,3:18,8:48}
component_row_miss_count={0:989,1:72}
component_tier_sig: 40 long-lambda singleton misses, 32 min-lambda singleton misses
```

So the next proof target can be split into two local mechanisms:

1. **long-lambda singleton miss:** a row can miss at most one long-lambda exit
   in its residual component by noncrossing terminal-prefix geometry;
2. **min-lambda singleton miss:** rare stage0 consumes all but at most one
   minimum-lambda exit from any side block that a longer row fails to witness.

This is weaker than the two-terminal theorem but sufficient for the SDR.

### Scope check: terminal-shadow alone may suffice

The component-local single-miss condition was also checked on **all** neutral
terminal-shadow switches in the small census, not only on selected R<0
seed+moat switches:

```text
python problems/23/writeup/_codex_all_terminal_singlemiss_gate.py \
  --min-n 5 --max-n 9

switches=16048
status={'skip_no_F1': 16000, 'ok': 48}
VERDICT: PASS
```

and

```text
python problems/23/writeup/_codex_all_terminal_singlemiss_gate.py \
  --min-n 10 --max-n 10

switches=113504
status={'skip_no_F1': 111072, 'ok': 2432}
VERDICT: PASS
```

So the single-miss theorem is not obviously a special artifact of the selected
seed+moat switch.  The likely core is a pure terminal-shadow/no-crossing fact:

```text
In a neutral terminal-shadow switch, after removing one minimum-lambda matching
layer, a longer terminal row cannot have two missed exits in the same residual
component.
```

The proof should still keep the rare stage0 layer, but the small-census scope
check says the geometry may not need the full R<0 or neutral-minimality
machinery.

### Laminarity guardrail

Do not claim full missed-exit laminarity for arbitrary neutral terminal-shadow
switches.  The broad laminar scope gate

```text
python problems/23/writeup/_codex_all_terminal_laminar_gate.py \
  --min-n 5 --max-n 9

switches=16048
status={'ok': 16048}
leaf_hist={0:12960,1:780,2:2308}
VERDICT: PASS
```

but at `N=10` it has a harmless failure:

```text
graph I?ABCc]}?, side 1001101000, S=(1,2,5)
cross=((1,9),(2,9),(5,8)), bdy=((0,5),(1,6),(2,6))
misses={two exits per row in a 3-cycle pattern}
```

Inspection gives

```text
ell(1,9)=ell(2,9)=ell(5,8)=5,
lambda(e)=5 for all boundary exits,
F1=empty,
Psi=0.
```

So arbitrary terminal-shadow laminarity is false, but the counterexample is
outside the tiered residual problem.  The correct statement must keep the
minimum-length tier removal:

```text
after stage0 removes F0 through E0, every mixed-tier residual component has
component-local single-miss.
```
