# Independent referee report on the two-block contradiction

Status: **ACCEPT FOR THE FROZEN EQUALITY CELL**, with one dependency that
must be stated explicitly: the assertion that every point lies in three
blocks uses the frozen row ledger `Z 1 = 3 1` (equivalently, the `3`-regular
part of “linear `19_3`”), not linearity by itself.

This report uses only the already audited row equation

\[
 A_u+M_u=e_v+A_v+e_{\pi_u(v)}\qquad(v\in R_u),       \tag{2}
\]

the fact that each `R_u` is a directed root triangle, linearity of the root
blocks, the frozen row sum three, and the oriented-graph no-digon axiom.  It
does not inspect or modify either CNF implementation.

## 1. Equality of root rows outside a block

Fix a target `u`, roots `v,w in R_u`, and a coordinate `x notin R_u`.
Because both `v` and `pi_u(v)` belong to `R_u`, the two unit-vector terms in
(2) vanish at coordinate `x`.  Hence

\[
 A_{v,x}=A_{u,x}+M_{u,x}=A_{w,x}.                    \tag{15}
\]

Thus every two adjacency rows indexed by roots of `R_u` agree at every
coordinate outside `R_u`.  This is an equality of outgoing-arc indicators:
`A_{v,x}=1` means `v -> x`.

No claim about coordinates inside `R_u` is used.

## 2. Quantifiers on the two chosen blocks

For every vertex `a`, the frozen equality ledger gives exactly three targets
`u` with `a in R_u`.  These give three distinct block sets.  Indeed, two
blocks indexed by different targets cannot be equal, because then their
intersection would have size three, contradicting linearity.

Choose any two of these blocks and call them `B,C`.  They both contain `a`,
so linearity gives

\[
 B\cap C=\{a\}.                                      \tag{16}
\]

Let `b` be the unique out-neighbour of `a` in the directed triangle on `B`,
and let `d` be the unique out-neighbour of `a` in the directed triangle on
`C`.  Then

```text
b in B minus {a},   d in C minus {a},
A[a,b]=1,           A[a,d]=1.
```

Equation (16) gives `d notin B`, `b notin C`, and `b != d`.

Apply (15) to the two roots `a,b` of block `B` at the outside coordinate
`d`.  It gives

\[
 A_{b,d}=A_{a,d}=1,                                  \tag{17}
\]

so `b -> d`.  Apply (15) to roots `a,d` of block `C` at coordinate `b`:

\[
 A_{d,b}=A_{a,b}=1,                                  \tag{18}
\]

so `d -> b`.  Since `b != d`, (17)--(18) are a forbidden digon.

The direction is not reversible or ambiguous: rows of `A` are outgoing
adjacency rows, and `b,d` were explicitly chosen as out-neighbours of `a`.
Whether `{b,d}` is a present or missing fixed-cycle pair is immaterial.  In
the latter case either forced arc already contradicts the support; in the
former case the two forced arcs contradict orientedness.

## 3. Exhaustive relaxed local countermodel search

The script

```text
engine/audit_cycle19_local_contradiction.py
```

enumerates all graphs on labelled vertices `{a,b,c,d,e}` in which every one
of the ten unordered pairs independently has one of three states: missing,
low-to-high, or high-to-low.  This is a relaxation of the fixed
`K_19-C_19` support.  It retains only

- `B={a,b,c}` and `C={a,d,e}` as directed triangles; and
- equality of the three outgoing rows of each block on the two local
  coordinates outside that block.

The exact counts are

```text
all oriented-or-missing graphs:                       59049
B a directed triangle:                                 4374
B and C directed triangles:                             324
both triangles plus B outside-row equality:               16
both triangles plus C outside-row equality:               16
both outside-row equalities simultaneously:                0
```

There is therefore no countermodel even after arbitrary missing edges are
allowed on all four cross pairs.  The symbolic proof above explains the
zero: in each of the four choices of the two triangle directions, the two
outside-row equalities force the corresponding chosen out-neighbours in both
directions.

## Decision

**ACCEPT.**  The frozen fixed-cycle equality cell is inconsistent.  The
contradiction needs no rank, girth, potential, circulant, or solver claim.
It closes only the registered `K_19-C_19`, outdegree-eight, row-and-column
unreachable-exact-three cell.  It does not resolve Seymour's conjecture or
exclude other supports or orders.
