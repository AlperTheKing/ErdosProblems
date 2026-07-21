# Independent obstruction to the fixed irregular order-19 lift

Status: **THE FIXED ROOT-INCIDENCE SEED IS CONTRADICTORY**.

This report independently attacks the direct route registered as
`IRREGULAR ORDER-19 INCIDENCE LIFT`.  It starts only from the explicit fibres
in `GENERAL_GOOD_BLOCK_COUNTING_BARRIER.md` and the sharp parameters

\[
 n=19,\qquad d^+(v)=8,\qquad e_v=0,
\]

with saturated target capacities.  It does not inspect or inherit a SAT
encoding, missing-graph seed, or claimed partial orientation.

The contradiction occurs before length-two reachability needs to be encoded.
It closes only this fixed fibre system, not every irregular order-19 pattern
and not Seymour's second-neighborhood conjecture.

## 1. Exact consequence of a saturated target

Fix a target `u` of missing degree `mu_u=m`.  Put

\[
 U_u=V\setminus(\{u\}\cup N^-(u)),\qquad
 C_v=\{v\}\cup N^+(v),
\]

and suppose its stated root fibre is saturated:

\[
 r_u=|R_u|=2m-1.                                    \tag{1}
\]

For every root `v in R_u`, unreachability gives

\[
 C_v\subseteq U_u,
 \qquad |U_u|=8+m,
 \qquad |C_v|=9.
\]

Therefore

\[
 B_v:=U_u\setminus C_v,qquad |B_v|=m-1.             \tag{2}
\]

The fixed-target pair-cover argument gives

\[
 {r_u\choose2}
 \leq\sum_{v\in R_u}|B_v\cap R_u|
 \leq r_u(m-1).                                     \tag{3}
\]

With `r_u=2m-1`, the two endpoints of (3) are equal:

\[
 {2m-1\choose2}=(2m-1)(m-1).                        \tag{4}
\]

Hence equality holds in every step.  This forces all of the following.

1. `B_v` is contained in `R_u` for every root.
2. Every unordered root pair is covered by exactly one ordered exclusion.
3. No root pair is missing; otherwise both ordered exclusions occur.
4. The subgraph induced by `R_u` is a tournament.
5. `B_v` is exactly the set of in-neighbours of `v` in that tournament.
6. Every root has `m-1` in-neighbours and `m-1` out-neighbours in `R_u`;
   the root tournament is regular.

Let `I_u(v)=N^-_{R_u}(v)`.  Taking indicator rows in (2) gives the exact row
equation

\[
 \boxed{
 A_u+M_u=\mathbf e_v+A_v+\mathbf 1_{I_u(v)}
 }
 \qquad(v\in R_u),                                  \tag{5}
\]

where `M_u` indicates the missing neighbours of `u`.

In particular, for every coordinate `x notin R_u`, all unit and
`I_u(v)` terms vanish.  Thus

\[
 \boxed{A[v,x]=A[w,x]
 \quad(v,w\in R_u,\ x\notin R_u).}                  \tag{6}
\]

Every saturated root block is therefore externally row-uniform.

For the three target types in the fixed seed, (5) specializes as follows.

- `m=1`, `r_u=1`: the root tournament is a singleton and
  `A_u+M_u=mathbf e_v+A_v`.
- `m=3`, `r_u=5`: the root block is a regular 5-tournament and
  `I_u(v)` has two elements.
- `m=4`, `r_u=7`: the root block is a regular 7-tournament and
  `I_u(v)` has three elements.

These are exact consequences of saturation, not optional propagation rules.

## 2. The two-fibre contradiction

The fixed incidence seed contains

```text
R_6 = {2,3,4,5,14}
R_7 = {2,3,4,5,11}.
```

Both targets have missing degree three, so both fibres must induce regular
5-tournaments.  Their intersection is

\[
 S=\{2,3,4,5\}.                                     \tag{7}
\]

Vertex 11 is outside `R_6`.  Applying the external row equality (6) for
block `R_6` at coordinate 11 gives

\[
 A[2,11]=A[3,11]=A[4,11]=A[5,11].                  \tag{8}
\]

Thus the four bits in (8) contain either zero or four ones.

On the other hand, vertex 11 lies in the regular 5-tournament on `R_7`.
It has indegree two there, and its other four block vertices are exactly
`S`.  Consequently

\[
 \sum_{s\in S}A[s,11]=2.                            \tag{9}
\]

Equations (8)--(9) are incompatible.  No choice of missing graph, orientation
of the remaining pairs, or length-two reachability variables can repair this
local contradiction.

## 3. Exhaustive finite certificate

The independent audit program `audit_irregular_lift_overlap.py` enumerates all
`2^10=1024` labelled tournaments on `R_7`.  Exactly 24 are regular.  In each
one, the vector

```text
(A[2,11], A[3,11], A[4,11], A[5,11])
```

has exactly two ones; none is uniform.  Its expected terminal output is

```text
regular_tournaments_on_R7=24
uniform_core_to_11=0
certificate=UNSAT_LOCAL
```

The enumeration is only a replay of (9); the displayed counting argument is
the proof.

## 4. Scope and direct bridge

Any lift of the registered seed must realize every stated saturated fibre.
Equations (5)--(6) are necessary for such a realization, while the two fixed
fibres `R_6,R_7` violate them.  Therefore the fixed irregular incidence seed
has no orientation completion and cannot yield the registered adjacency-list
deliverable.

This result does not exclude a different missing graph together with a
different root incidence, even with the same degree multiset.  Under the
registered exit condition, seed disagreement closes this mechanism; it does
not authorize variation of the incidence hierarchy.

