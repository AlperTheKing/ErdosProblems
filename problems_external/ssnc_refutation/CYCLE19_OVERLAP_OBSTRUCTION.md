# Root-block overlap obstruction in the fixed `K_19-C_19` equality cell

Status: **THE FIXED CELL IS CONTRADICTORY**.

This note uses only the accepted equality-fibre row equation and the accepted
linearity lemma from `CYCLE19_ALGEBRAIC_AUDIT.md`.  It does not inspect the CNF
generator or use a solver.  Its conclusion is restricted to the frozen cell:
an 8-outregular orientation of `K_19-C_19` with three unreachable incidences
in every source row and target column.

## Lemma 1: a root block has identical external adjacency columns

For a target `u`, let `R_u` be its three roots.  For every `v in R_u`, the
accepted row equation is

\[
 A_u+M_u=e_v+A_v+e_{\pi_u(v)}.                       \tag{1}
\]

Both `v` and `pi_u(v)` belong to `R_u`.  Therefore, for every
`x notin R_u`, taking coordinate `x` in (1) gives

\[
 A[v,x]=A_u[x]+M_u[x],                               \tag{2}
\]

whose right-hand side is independent of `v`.  Hence

\[
 \boxed{A[r,x]=A[s,x]\quad
        (r,s\in R_u,\ x\notin R_u).}                 \tag{3}
\]

In words, all three roots of a target have the same direction toward every
vertex outside their root block.  This is an exact integer equality, not only
a congruence modulo three.

## Lemma 2: two root blocks cannot meet

Suppose two distinct root blocks `B` and `C` share a vertex `a`.  The accepted
linearity lemma says that their intersection is exactly `{a}`.  Each root
block induces a directed triangle.  Let

- `b` be the unique out-neighbour of `a` inside `B`; and
- `d` be the unique out-neighbour of `a` inside `C`.

Thus `A[a,b]=A[a,d]=1`.  Since `d notin B`, (3) for block `B` gives

\[
 A[b,d]=A[a,d]=1.                                    \tag{4}
\]

Since `b notin C`, (3) for block `C` gives

\[
 A[d,b]=A[a,b]=1.                                    \tag{5}
\]

Equations (4)--(5) form the forbidden digon `b <-> d`.  Therefore distinct
root blocks are disjoint.

## Theorem: no assignment exists in the fixed cell

Every row of the unreachable matrix `Z` has sum three.  Consequently every
vertex `a` belongs to three distinct root blocks `R_u`, one for each target
`u` with `Z[a,u]=1`.  In particular, two distinct root blocks meet at `a`,
contradicting Lemma 2.

Therefore no orientation can satisfy the frozen `K_19-C_19` equality-cell
hypotheses.  This closes only that fixed connected-missing-cycle cell.  It is
not a proof of Seymour's second-neighborhood conjecture and says nothing
about another missing 2-factor, order, or degree.

