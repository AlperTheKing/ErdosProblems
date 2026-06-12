# Erdos problem #23 finite exact result: a(25)=25

Status: PROVED, conditional only on the cited published/computational sources
for the already-known n=23 extremal catalogue.

Date: 2026-06-10

Formal Conjectures PR: https://github.com/google-deepmind/formal-conjectures/pull/4216

## Target

Let

`beta(G) = e(G) - maxcut(G)`

and let `a(n)` be the maximum of `beta(G)` over triangle-free graphs on `n`
vertices. Erdos problem #23 asks whether `a(5m) <= m^2`; the finite target
here is

`a(25) = 25`.

The lower bound is the balanced blow-up of `C5` with five parts of size 5.
It has 125 edges and every bipartition leaves at least one adjacent pair of
parts monochromatic, so `beta >= 25`; deleting the 25 edges between one
adjacent pair makes it bipartite, so `beta = 25`.

## Sources checked

- Erdos Problems #23 states the triangle-free bipartization problem and cites
  the Balogh-Clemen-Lidicky bound:
  https://www.erdosproblems.com/latex/23
- Balogh, Clemen, Lidicky, "Max Cuts in Triangle-free Graphs",
  arXiv:2103.14179. The abstract says the Erdos `n^2/25` conjecture is proved
  for triangle-free graphs with edge density at least 0.3197:
  https://arxiv.org/abs/2103.14179
- OEIS A389646 lists values only through `n=23` and gives `a(23)=20`:
  https://oeis.org/A389646
- McKay's data page says `minbip N_Ax.g6` contains all triangle-free graphs on
  `N` vertices achieving `a(N)=A`, and without `x` only the maximal subset:
  https://users.cecs.anu.edu.au/~bdm/data/graphs.html

## Independent data check

Downloaded:

`https://users.cecs.anu.edu.au/~bdm/data/minbip.tar`

Local files:

- `E:\Projects\ErdosProblems\search23\mckay_minbip\minbip.tar`
- `E:\Projects\ErdosProblems\search23\mckay_minbip\minbip23_20x.g6`
- `E:\Projects\ErdosProblems\search23\verify_mckay23.cpp`

SHA256:

- `minbip.tar`: `0424C19D8A4B00EB449B4C148D27FF38E53A9F1348850451D925B9312F6F7215`
- `minbip23_20x.g6`: `2669D02B2A83838913D00DD2B2C76D3D7C49929F3B7F0D39F32B32EA58B9BD96`
- `verify_mckay23.cpp`: `964EFC5E714177B0689BF3A7783A560D36BB4723431176285A7606B9EEE96140`

Command:

```powershell
g++ -O3 -std=c++17 -march=native search23\verify_mckay23.cpp -o search23\verify_mckay23.exe
.\search23\verify_mckay23.exe .\search23\mckay_minbip\minbip23_20x.g6
```

Output summary:

```text
SUMMARY	count=6	min_edges=100	max_edges=105	min_beta=20	max_beta=20
```

Each of the six graph6 entries was also checked triangle-free by the verifier.

## Proof

Assume for contradiction that `G` is a triangle-free graph on 25 vertices with
`beta(G) >= 26`.

By the high-density case of Balogh-Clemen-Lidicky, any triangle-free graph on
25 vertices with edge density at least `0.3197` can be made bipartite by
deleting at most `25^2/25 = 25` edges. Since `0.3197 * binom(25,2) = 95.91`,
the assumed counterexample must have

`e(G) <= 95`.

Therefore its average degree is at most `2*95/25 = 7.6`, so choose a vertex
`v` with `d_G(v) <= 7`. Let `H = G - v`.

For any graph `X` and vertex `x`,

`beta(X) <= beta(X-x) + floor(d_X(x)/2)`.

Indeed, take an optimal bipartition of `X-x`, then put `x` on the side that
creates no more than half of its incident edges as monochromatic edges.

Apply this first to `v` in `G`. Since `floor(7/2)=3`,

`beta(H) >= 26 - 3 = 23`.

Also `e(H) <= 95`, so the average degree of `H` is at most `2*95/24 < 8`.
Choose a vertex `u` of `H` with `d_H(u) <= 7`, and let `F = H - u`.
Applying the same deletion inequality again gives

`beta(F) >= 23 - 3 = 20`.

The graph `F` is triangle-free on 23 vertices. OEIS/McKay give `a(23)=20`,
so `beta(F)=20`; hence `F` is one of the graphs in McKay's complete
`minbip23_20x.g6` catalogue. The independent C++ check above shows that every
graph in that catalogue has at least 100 edges.

But `F` is an induced subgraph of `G`, so `e(F) <= e(G) <= 95`, contradiction.
Thus every triangle-free graph on 25 vertices has `beta(G) <= 25`.

Together with the balanced `C5` blow-up lower bound, this proves

`a(25)=25`.

## Novelty memo

This appears to be a new finite value for A389646: OEIS currently lists the
sequence only through `n=23`, and the McKay catalogue is advertised as complete
only up to 23 vertices. The proof above does not enumerate 25-vertex graphs;
it combines the known high-density BCL theorem with the complete 23-vertex
extremal catalogue and a two-vertex deletion argument.
