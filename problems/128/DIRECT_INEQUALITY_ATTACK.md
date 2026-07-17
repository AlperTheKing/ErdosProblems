# Erdős Problem 128 — direct inequality attack

## Outcome

`DEAD` for the tested neighbourhood-completion averaging lemma.  The exact
triangle-free graph `C5[4]` violates the proposed inequality at every vertex.
This is a method counterexample, not a counterexample to Problem 128: the graph
itself has a 10-set with exactly 8 edges, as the conjecture predicts.

## Direct lemma that was tested

Let `G` be a triangle-free graph on `n` vertices and put
`h=floor(n/2)`.  If some vertex has degree at least `h`, then any `h` of its
neighbours form an independent set.  The remaining case suggested the
following direct averaging lemma.

For a vertex `v` of degree `d<h`, define

- `A=N(v)`;
- `B=V(G)\(A union {v})` and `b=|B|=n-d-1`;
- `t=h-d`;
- `q=e(A,B)` and `r=e(B)`.

If `T` is a uniformly random `t`-subset of `B`, then `A` is independent and

`E[e(G[A union T])] = q*t/b + r*t*(t-1)/(b*(b-1)).`  (1)

Indeed, an `A`--`B` edge is selected with probability `t/b`, while an edge
inside `B` is selected with probability `t(t-1)/(b(b-1))`.  Consequently, the
assertion that some vertex makes the right side of (1) at most `n^2/50` would
prove the full conjecture immediately: some realization of `T` would be the
required half-set.

## Exact finite counterexample to the lemma

Take the balanced blow-up `C5[4]`.  Its vertices are partitioned into five
independent parts `P_0,...,P_4`, each of size 4, and all edges are placed
between consecutive parts cyclically.  It has `n=20`, is triangle-free, and is
vertex-transitive.  Fix any vertex `v`.

- `h=10` and `d(v)=8`;
- `A` is the union of the two parts adjacent to the part of `v`;
- `B` has size `b=20-8-1=11`;
- `t=10-8=2`;
- every vertex of `A` has seven neighbours in `B`, so `q=8*7=56`;
- the only edges internal to `B` are the complete bipartite edges between the
  two parts opposite `v`, so `r=4*4=16`.

Thus every vertex gives

`E[e(G[A union T])] = 56*(2/11) + 16*(2/(11*10)) = 576/55 > 8 = n^2/50.`

The gap is not a rounding artifact: `576/55-8=136/55`.  On the other hand,
choosing both vertices of `T` from either one of the two opposite parts gives
exactly eight edges.  Hence the deterministic optimum is sharp while uniform
averaging misses it.

## Exact parametric check

The same obstruction occurs for every balanced blow-up `C5[2k]`, `k>=1`.
Here `n=10k`, `h=5k`, `d=4k`, `b=6k-1`, `t=k`,

`q=4k(4k-1)` and `r=4k^2`.

The expectation in (1) exceeds the target `n^2/50=2k^2` by exactly

`4k^2(7k^2-6k+1) / ((6k-1)(6k-2)) > 0.`

Nevertheless, choosing all `k` completion vertices from one opposite part
produces exactly `2k^2` edges.  This is an exact family of finite
counterexamples to the averaging lemma, not an asymptotic reformulation.

## Independent executable audit

Run:

```text
python problems/128/verify/neighborhood_completion_counterexample.py
```

The script uses `fractions.Fraction`, enumerates all triples, all possible
neighbourhood completions, and all `C(20,10)=184756` half-sets.  Its checked
output is:

```text
graph=C5[4]
n=20 h=10 triangles=0
all_vertices: d=8 b=11 t=2 q=56 r=16
completion_expectation=576/55 threshold=8
minimum_neighborhood_completion=8
minimum_over_all_half_sets=8
verdict=COUNTEREXAMPLE_TO_AVERAGING_LEMMA
```

Verifier SHA-256:

`F635C4AA65B9BB9437986860D40B7E5FD785993777173DEE95D1B003CB138493`

## Consequence for the proof program

Uniformly filling a neighbourhood, even after optimizing over the root
vertex, cannot reach the sharp `1/50` constant: it already fails on the
standard equality construction and all vertices are equivalent there.
Any viable direct proof must retain structure inside `B` and choose correlated
completion vertices; the aggregate data `(d,b,q,r)` and its first-moment
formula are insufficient.  This result does not rule out a structure-sensitive
deterministic neighbourhood argument, but the present route meets its declared
exit condition and must not be weakened into another averaging formulation.

For context, the official entry still records the full statement as open, and
Razborov's 2022 general bound is `27/1024`, while proving the sharp conjecture
for several special classes:

- https://www.erdosproblems.com/128
- https://arxiv.org/abs/2104.09406
