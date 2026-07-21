# The first order-19 packing mechanism

## Status

**Concrete finite mechanism, but no orientation witness.**  The sharp
`q = 19`, `e_v = 0`, `mu_v = 2` cell is internally consistent at the
degree, missing-edge, and unreachable-incidence levels.  It reduces one
connected missing-graph case to a direct finite decision problem on
orientations of `K_19 - C_19`.  It does not itself give a counterexample.

The natural translation-invariant templates and their complete one-triangle
degree-preserving neighbourhood contain no hit.  Therefore explicit
construction is currently **BLOCKED**.  A single proof-capable exact decision
run for the fixed `C_19` cell is a justified next falsifiable action; no other
order or missing-cycle type follows automatically.

## Exact order-19 incidence accounting

Let `D` be an oriented graph on 19 vertices with minimum outdegree 8, and put

```
d+(v) = 8 + e_v,
mu_v  = missing degree of v,
t_v   = e_v + mu_v.
```

If `q` is the number of missing unordered pairs, then

\[
  \sum_v e_v = 19-q,
  \qquad
  \sum_v \mu_v = 2q,
  \qquad
  \sum_v t_v = 19+q.                                 \tag{1}
\]

For a source `v`, let

```
C_v = {v} union N+(v),
W_v = V minus (C_v union N++(v)).
```

Under strict SSNC failure, `|N++(v)| <= 7+e_v`, whereas the complement of
`C_v` has size `10-e_v`.  Hence

\[
  |W_v| \geq \max(0,3-2e_v).                          \tag{2}
\]

Thus an excess-0 source requires at least three unreachable targets and an
excess-1 source requires at least one.

For a fixed target `u`, define

```
T_u = V minus ({u} union N-(u)),
R_u = {v : u is in W_v},
r_u = |R_u|.
```

Then `|T_u| = 8+t_u`.  If `v in R_u`, the exact source-target orientation
gives

\[
  C_v\subseteq T_u,
  \qquad
  |T_u\setminus C_v|=t_u-e_v-1.                       \tag{3}
\]

For distinct roots `v,w in R_u`, a digon would result if both `w in C_v` and
`v in C_w`.  Counting the required ordered exclusions gives the strengthened
target inequality

\[
  {r_u\choose2}
  \leq r_u(t_u-1)-\sum_{v\in R_u}e_v.                 \tag{4}
\]

This is the coarse exact integer/incidence model.  It retains source excesses
inside the target capacity; dropping the last sum creates false feasible
patterns.

## The sharp regular cell

Take

```
q = 19,
e_v = 0 for all v,
mu_v = 2 for all v.
```

Then every vertex has outdegree 8, indegree 8, and missing degree 2.  The
missing graph is therefore a 2-factor.  In the connected 2-factor cell it is
`C_19`, and every target has `t_u=2`.

Equation (2) requires at least `19*3=57` ordered unreachable incidences.
Equation (4) gives `r_u<=3`, hence at most `19*3=57`.  Consequently any
counterexample in this cell must satisfy all of the following equalities:

1. every source has exactly three unreachable targets;
2. every target has exactly three unreachable roots;
3. every vertex has exactly seven new second out-neighbours;
4. for each target `u`, the three vertices in `R_u` induce a directed
   3-cycle; and
5. for `v in R_u`, the singleton `T_u minus C_v` is the unique in-neighbour
   of `v` inside that directed root triangle.

Items 4--5 are not optional heuristics.  Equality in the pair-cover count
forces every one of the three singleton exclusion sets to cover a different
pair of roots.  In particular, no missing pair can occur inside `R_u`.

This is substantially stronger than feasibility of the scalar inequalities:
it specifies a 3-regular source-target incidence relation whose target fibres
must be directed triangles and whose 9-element source sets must differ from
the corresponding 10-element target sets by exactly one prescribed root.

## Important scope boundary

`mu_v=2` implies only that the missing graph is a disjoint union of cycles.
It does **not** imply that it is one 19-cycle.  Fixing missing pairs

\[
  \{i,i+1\}\quad(i\in\mathbb Z/19\mathbb Z)
\]

therefore studies the connected missing-2-factor subfamily only.  An UNSAT
result for this fixed family cannot be reported as UNSAT for every
`q=19, mu=2` graph, much less for all order-19 graphs.

## Explicit templates tested

### Translation-invariant family

On `Z/19Z`, omit the inverse pair `+/-1` and choose one direction from each
of the remaining eight inverse pairs.  This gives exactly `2^8=256`
orientations of `K_19-C_19`, all with outdegree 8.

The complete enumeration returned

```
|N++(v)| = 8 :   2 templates
|N++(v)| = 9 :  14 templates
|N++(v)| = 10: 240 templates
strict hits: 0
```

Allowing all nine choices of omitted inverse pair produces 2,304 labelled
templates and the histogram `{8:18, 9:126, 10:2160}`.

One closest template is

\[
 S=\{2,4,6,8,10,12,14,16\},
 \qquad v\to v+s\quad(s\in S).
\]

For source 0 it has

```
N+(0)          = {2,4,6,8,10,12,14,16}
N++(0)         = {1,3,5,7,9,11,13,18}
unreachable(0) = {15,17}
```

and the same cardinalities at every translate.  It is an exact global
near-miss, with equality `|N++|=|N+|=8`, but it lacks the third unreachable
target required by the mechanism.

### Complete one-triangle switch neighbourhood

Reversing all three arcs of a directed triangle preserves every outdegree and
the fixed missing cycle.  For both closest circulants, every such one-step
move was checked: 266 templates in total.  There was no strict hit.  Every
switched graph still had all 19 vertices non-strict, and the best maximum
value of `|N++(v)|-|N+(v)|` was 2.  Thus this local move moves away from the
required incidence pattern.

The executable audit is `engine/search_incidence.py`.  It is a finite
template checker, not a general order-19 graph search.

## Safe fixed-missing-cycle encoding

For a future exact decision run, label vertices by `Z/19Z` and fix only the
missing pairs `{i,i+1}`.  The following constraints are sound.

1. **Orientation variables.**  For every present ordered pair use `x_vw`.
   Set loops and fixed missing directions to false, and impose
   `x_vw + x_wv = 1` on every remaining unordered pair.
2. **Regularity.**  Impose `sum_w x_vw = 8` for every vertex.  Indegree 8
   follows, but may be asserted redundantly.
3. **Literal two-step variables.**  Define
   `p_vwu iff (x_vw and x_wu)`, in both directions.  Define
   `reach2_vu iff OR_w p_vwu`, also in both directions.  One-way reachability
   implications are unsafe.
4. **Literal unreachable variables.**  For `u != v`, define
   `z_vu iff (not x_vu and not reach2_vu)`; set `z_vv=false`.
5. **Forced equality ledger.**  Impose
   `sum_u z_vu = 3` for every source and `sum_v z_vu = 3` for every target.
   With the biconditional definitions, the row constraints are equivalent to
   `|N++(v)|=7`, so any satisfying assignment is already a literal strict
   SSNC counterexample.
6. **Redundant structural propagation.**  If useful, add the proved
   consequences that a target's three roots contain no fixed missing pair,
   induce a directed triangle, and satisfy
   `T_u minus C_v = {the in-neighbour of v in that triangle}`.  These may
   accelerate solving, but the final certificate must not depend on an
   unchecked implementation of them.
7. **Symmetry.**  Dihedral relabellings of the fixed cycle are safe.  The
   single condition `0 -> 2` is safe after a dihedral relabelling.  Fixing a
   particular root triple is not safe without branching over its dihedral
   orbits.  Global arc reversal is not used as a symmetry.

## Frozen direct route

### 1. Exact final deliverable

One canonical adjacency list for an orientation of `K_19-C_19` that passes
both independent SSNC verifiers, including the 19-row
`(outdegree, new-second-degree, unreachable-count)` ledger.

### 2. Frontier finite certificate

The exact fixed-cycle Boolean system above, with all 19 source and target
unreachable sums equal to 3.

### 3. Logical bridge

A satisfying assignment has outdegree 8 and exactly three vertices outside
`{v} union N+(v) union N++(v)` for every source.  The remaining complement
therefore has size seven, so `|N++(v)|=7<8=|N+(v)|` at every vertex.  After
independent replay, that one graph literally refutes SSNC.

An independently checked UNSAT proof has a much narrower bridge: it excludes
only orientations whose missing graph is the fixed connected 19-cycle.

### 4. Next falsifiable action

Run one bounded, proof-capable SAT instance for the fixed `C_19` encoding,
with exact biconditional reachability and the equality ledger.  Validate any
SAT assignment with both existing independent verifiers; validate any UNSAT
claim with an independent proof checker.  This report does not launch that
production run.

### 5. Exit condition

- Verified SAT: stop immediately and rerun the live novelty gate.
- Independently checked UNSAT: mark only the connected missing-cycle
  mechanism dead and stop this lane.
- Timeout, `UNKNOWN`, unchecked UNSAT, or no hit: mark this mechanism
  `BLOCKED`; do not continue through other 2-factor types, other values of
  `q`, or higher orders without a new separately registered direct mechanism.

## Decision

The equality mechanism is sound enough to justify exactly one finite direct
decision action.  It is not an explicit counterexample mechanism yet: the
best concrete orientation has two, not three, unreachable targets per
vertex, and every tested symmetry-preserving one-step perturbation is worse.
No SSNC result is claimed here.
