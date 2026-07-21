# Independent referee on the two-block overlap obstruction

Date: 2026-07-21 (Europe/Istanbul)

Verdict: **ACCEPT**.

For a target `u` and root `r in R_u`, the raw equality-cell row equation is

\[
 A_u+M_u=e_r+A_r+e_{\pi_u(r)}.
\]

Both `r` and `pi_u(r)` lie in `R_u`. Thus, at every coordinate `x notin R_u`, both unit-vector terms vanish and

\[
 A[r,x]=A_u[x]+M_u[x].
\]

The right side is independent of `r`; all three adjacency rows agree outside the root block.

A binary row of `Z` has sum three, so every vertex `a` belongs to three fibres belonging to three distinct target coordinates. Linearity for distinct targets makes the corresponding blocks distinct and makes any two of them intersect exactly in `{a}`.

Let `B,C` be two such blocks. Let `b` be the unique out-neighbour of `a` in the directed triangle on `B`, and let `d` be its unique out-neighbour in the triangle on `C`. Then `d notin B` and `b notin C`, so external-row equality gives

\[
 A[b,d]=A[a,d]=1,
 \qquad
 A[d,b]=A[a,b]=1.
\]

This is a forbidden digon. There is no exceptional missing-edge case: the two equalities themselves force both adjacency entries to one.

As an independent finite check, all `3^10=59,049` assignments of the ten unordered pairs on five labelled vertices to `missing`, `forward`, or `reverse` were enumerated for `B={a,b,c}` and `C={a,d,e}`.

Exactly 324 assignments made both blocks directed triangles. Sixteen of those also satisfied the external-row equality for `B`; zero satisfied the external-row equalities for both blocks. No local countermodel exists.

The conclusion is restricted to the fixed equality-cell hypotheses used in the row equation and linearity lemma.