# W144-S cut-family selection audit: three exact obstructions

Date: 2026-07-18.

This note does **not** give a counterexample to the registered Steiner-radius
statement

\[
  \operatorname{srad}_{g-1}(G)\ge g-2+e,
  \qquad e=\max_x d(x,C(G)).
\]

It records why the present complement/cut-family attack has no remaining
structural selection lemma.  In every graph below the exact Steiner-radius
bound itself holds.  What fails is each proposed rule for selecting the
required complement `X`.

Recall that `p=n-g+1`, `k=g-1`, and

    b(X)=min{|Y| : Y subset X and G[(V-X) union Y] is connected}.

For a prescribed root `v`, the target is a `p`-set `X` avoiding `v` with
`b(X)>=e`.  By the proved cut-family equivalence, this is exactly the target
in the registry, not a relaxation.

## 1. A single terminal pair cannot carry the required cost

A natural sufficient construction chooses terminals
`S={v,w} union T`, where `|T|=g-3`, and asks that every `v`--`w` path have
at least `e` internal vertices outside `T`.  Then every connector of `S`
uses at least `e` nonterminals, so its complement is a valid cut-family
witness.

This sufficient condition is false in graph6 graph

    F?bao

with vertices `0,...,6` and edges

    04, 05, 15, 16, 25, 36, 46.

The graph has girth `5`, radius `2`, center `{1}`, and `e=2`.  For root
`v=1`, exhaustive 0--1 shortest-path evaluation over every choice of `w`
and every two-set `T` finds no such pair witness.  Nevertheless

    S={0,1,2,3},   X={4,5,6},   b(X)=2.

Indeed, deleting any two vertices of `X` disconnects the graph: deleting
`{4,5}` isolates terminal `0`, deleting `{4,6}` isolates terminal `3`, and
deleting `{5,6}` isolates terminal `1`.  Thus the valid witness is genuinely
branched; its two required nonterminals cannot be charged to one terminal
pair by the proposed rule.

The deterministic verifier is
`test_cutfamily_two_terminal_sr.py`.  It encounters this obstruction after
five cyclic girth-at-least-five graphs and 31 rooted instances.

## 2. The exact objective has suboptimal one-swap local maxima

One might instead begin with any complement and repeatedly exchange one
terminal with one nonterminal whenever this raises `b(X)`.  The required
strict ascent property is false in graph6 graph

    F?q`o

with edges

    04, 05, 14, 25, 26, 36, 46.

This graph has girth `5`, radius `2`, center `{4,6}`, and `e=2`.  For root
`v=4`, let

    X={1,5,6},   V-X={0,2,3,4}.

Restoring vertex `6` connects the four terminals, while restoring no vertex
does not, so `b(X)=1`.  The values after swapping, in the order

    removed x in (1,5,6), inserted s in (0,2,3),

are

    (1,1,1), (1,1,0), (0,0,0).

Hence `X` is a strict-ascent local maximum with `b(X)=1<e`.  The exact target
still holds: `X'={0,2,6}` avoids `v` and has `b(X')=2`.

The deterministic verifier is `test_cutfamily_exchange.py`.

## 3. Taking the most central available vertices is insufficient

The remaining canonical choice is to minimize
`sum_{x in X} d(x,C(G))` among all `p`-sets avoiding the root.  It fails in
graph6 graph

    G?`F?w

with edges

    04, 06, 15, 16, 26, 37, 47, 57.

Here `n=8`, `g=6`, `p=3`, the radius is `3`, the center is
`{0,1,4,5}`, and the center-distance vector is

    (0,0,2,2,0,0,1,1),

so `e=2`.  At root `v=0`, the unique minimum-weight complement is
`X={1,4,5}`.  Exact connected-superset enumeration gives `b(X)=1<2`.
Again the Steiner-radius target survives: for example `X'={1,4,6}` has
`b(X')=2`.

The deterministic verifier is `test_cutfamily_central_complement.py`.

## 4. Disposition

The cut-family equivalence remains correct and useful as a certificate, but
it supplies no selection principle.  The three direct principles available
from it -- concentration on one terminal pair, local exchange ascent, and a
canonical center-layer choice -- have exact obstructions of orders at most
eight.  Replacing them by “choose an `X` maximizing `b(X)`” merely restates
the unproved Steiner-radius inequality and gives no bridge from the ordinary
center distance `e`.

Under the direct-proof guard, this branch is therefore

    DEAD: reformulation maze -- no structural rule forces a complete
    q-uniform cut family from ecc(G,C)=e.

This disposition is only for the present cut-family selection attack.  It
does not mark (SR), W144, or any other registered direct route false.
