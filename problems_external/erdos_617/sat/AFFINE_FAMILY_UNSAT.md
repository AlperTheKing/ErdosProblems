# Exact obstruction to the 75-free-edge affine family

This note concerns only the following restricted `K_26` family. Label the old
vertices by `(x,y) in F_5^2` and the new vertex by `infinity`. Give every
nonvertical old edge the colour

`c = (y_2-y_1)/(x_2-x_1) in F_5`.

The 50 vertical old edges and the 25 edges incident with `infinity` may be
coloured arbitrarily. No member of this family has every colour in every
six-set.

## Proof

For each colour `c`, let `N_c` be the set of old vertices whose edge to
`infinity` has colour `c`. The five sets `N_c` partition the 25 old vertices.

Use coordinates `(x,b)` for a point, where `b=y-cx`. A set of five old
vertices containing one point from each `c`-slope line and one point from each
vertical column is exactly a perfect matching in the bipartite graph
`K_(5,5)` with parts indexed by `x` and `b`.

Such a five-set has no fixed edge of colour `c` and no vertical edge.
Consequently, the corresponding six-set with `infinity` contains colour `c`
only if the matching meets `N_c`. Thus `N_c`, viewed as an edge set of
`K_(5,5)`, meets every perfect matching.

Any edge set meeting every perfect matching of `K_(5,5)` has size at least
five. Indeed, `K_(5,5)` decomposes into five edge-disjoint perfect matchings.
Hence `|N_c|>=5` for all five colours. Since the `N_c` partition 25 points,
every `N_c` has size exactly five.

A five-edge set meeting every perfect matching of `K_(5,5)` is a star. To see
this, delete those five edges and apply Hall's theorem. If a Hall-deficient
set has size `a` and has at most `a-1` remaining neighbours, at least
`a(6-a)` edges were deleted. This equals five only for `a=1` or `a=5`; the
deleted edges are respectively a left or right star.

Translated back to the affine plane, `N_c` is therefore either a vertical
column or one `c`-slope line. Distinct finite-slope lines of different slopes
intersect, and every finite-slope line intersects every vertical column.
Because the five `N_c` are disjoint, all of them must be the five distinct
vertical columns. Write `N_c={x=a_c}`, where `c -> a_c` is a permutation.

Fix any vertical old edge `e` in column `r`. For each of the four colours `c`
with `a_c != r`, construct a `c`-transversal as follows. Include both endpoints
of `e`. They occupy two distinct `c`-slope lines. Match the other three
`c`-slope lines bijectively to the three columns different from both `r` and
`a_c`, and take the corresponding three points. The resulting five-set:

1. avoids `N_c`, so none of its infinity edges has colour `c`;
2. has no fixed nonvertical edge of colour `c`; and
3. has `e` as its only vertical edge.

The six-set obtained by adjoining `infinity` therefore forces `e` to have
colour `c`. The same edge is forced to have each of four different colours,
contradicting exactly-one edge-colour semantics. This proves the stated
restricted-family obstruction.

## Computational cross-check

`encode_affine_family.cpp` independently enumerates all old five-sets and
produces 375 Boolean variables and 16,450 clauses: 825 exactly-one clauses
and 15,625 six-set requirements. `audit_affine_family_cnf.cpp` reconstructs
the requirements through the perfect-matching/transversal parameterisation,
not through the encoder's five-subset loop. CaDiCaL 3.0.0 reports UNSAT, and
`drat-trim` independently accepts the text DRAT proof.

This obstruction does not exclude arbitrary five-colourings of `K_26`.
