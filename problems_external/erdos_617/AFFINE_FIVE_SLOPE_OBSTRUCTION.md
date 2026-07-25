# Obstruction to the five-fixed-slope affine family

## Proposition

Let the old vertices be `F_5^2` and add one vertex `infinity`. Colour every
old edge joining `(x,y)` and `(x',y')` with `x != x'` by its finite slope

`c = (y'-y)/(x'-x) in F_5`.

There is no way to colour the 50 remaining vertical old edges and the 25
edges incident with `infinity` by the five colours so that every six vertices
contain every colour.

## Proof

Fix a colour `c`. Let `N_c` be the old vertices joined to `infinity` by an
edge of colour `c`. For a point `(x,y)`, put

`b_c(x,y) = y-cx`.

The map `(x,y) -> (x,b_c(x,y))` identifies the 25 old points with the edges
of `K_(5,5)`.

Consider five old points having all five distinct `x`-coordinates and all
five distinct `b_c`-coordinates. They form a perfect matching under this
identification. Among these five points there is neither a vertical edge nor
an old edge of finite slope `c`. Consequently their union with `infinity`
can contain colour `c` only on an edge from `infinity`. Hence `N_c` meets
every perfect matching of `K_(5,5)`.

At least five edges must be deleted from `K_(5,5)` to destroy all perfect
matchings. Therefore `|N_c| >= 5`. The five sets `N_c` partition the 25 old
vertices, so every one has size exactly five.

Moreover, a five-edge set meeting every perfect matching of `K_(5,5)` is a
star. Indeed, after deleting it Hall's theorem gives a set `X` on one side
with `|Gamma(X)| <= |X|-1`. At least

`|X|(5-|Gamma(X)|) >= |X|(6-|X|)`

edges were deleted. For `|X|=2,3,4` this lower bound is respectively
`8,9,8`, whereas for `|X|=1` or `5` equality at five forces a star.

Translated back to `F_5^2`, each `N_c` is therefore either a vertical column
or a line of finite slope `c`. The five `N_c` are pairwise disjoint. If one
is a vertical column, every nonvertical affine line meets it, so all five
must be vertical columns. If none is vertical, two of them have distinct
finite slopes and hence meet. Thus the only possible case is that the five
sets `N_c` are precisely the five vertical columns, in some order.

Let the column assigned to colour `c` be `X_c`. Fix a vertical old edge `e`
in a column `r`. For any colour `c` with `X_c != r`, construct five old
points as follows. Include the two endpoints of `e`; omit column `X_c`; use
one point in each of the other three columns; and choose those three points
so that the five values `b_c` are all distinct. This is possible because the
two endpoints of `e` already have distinct `b_c`-values, and the remaining
three values can be assigned arbitrarily to the three remaining columns.

This five-set avoids `N_c`, has `e` as its only vertical pair, and has no
finite-slope-`c` edge. Therefore its union with `infinity` contains colour
`c` only if `e` itself has colour `c`. There are four colours whose assigned
column differs from `r`, so the same edge `e` would have to receive four
different colours, a contradiction.

## Scope

This eliminates only the construction family in which the five finite slope
classes are fixed as the five colours. It does not prove Erdős Problem 617
and does not exclude recolouring finite-slope edges.

