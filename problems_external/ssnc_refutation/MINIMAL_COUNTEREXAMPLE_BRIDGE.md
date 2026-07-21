# Primary-source bridge audit for a minimum SSNC counterexample

Status: **BLOCKED -- no theorem-closing bridge found.**

Audit date: 2026-07-21. This is a theorem-scope audit, not a proof of SSNC,
not a counterexample claim, and not authorization for another search. Only
primary papers and the publisher's primary article page were used.

## Decision

No audited theorem forces

\[
  n\le 2\delta^+(D)+2
\]

for a minimum counterexample. Hence no published reduction found here
contradicts the accepted packing consequence

\[
  n\ge 2\delta^+(D)+3.
\]

The exact connected equality class consisting of orientations of
`K_19-C_19` is also **not covered** by the audited missing-graph theorems.
In particular, being Eulerian is not sufficient for the available Eulerian
result, and the dependency-digraph path/cycle lemma is specific to a missing
matching.

"Not covered" has its literal scope: none of the theorem statements checked
below applies to every orientation of `K_19-C_19`. It is not a claim that an
unindexed or future result cannot exist.

## Normalized minimum counterexample

Assume SSNC is false. Choose a counterexample `D` with globally minimum
order `n`, and among those choose one with a minimum number of arcs. Put
`delta=delta+(D)`.

This choice permits the following statements simultaneously.

1. **Strong connectivity.** Espuny Diaz--Girao--Granet--Kronenberg observe
   immediately before Proposition 4 that every vertex-minimal counterexample
   is strongly connected: a sink strong component would itself be a smaller
   counterexample.
2. **Set inequality.** Seacrest, Lemma 4, states that in an edge-minimal
   lambda-counterexample, every set `S` with nonempty first out-neighborhood
   satisfies `d_2^+(S)<lambda d_1^+(S)`. At `lambda=1` it applies to the
   edge-minimal choice above.
3. **Quadratic lower-degree restriction.** Espuny Diaz et al., Proposition 4,
   gives `delta>sqrt(n)`, equivalently `n<delta^2`.
4. **Finite-order reduction.** Seacrest, Corollary 5, says that from a
   counterexample of minimum outdegree `delta` one obtains a counterexample
   on, in the paper's words, "at most binom(delta+1,2) vertices." Since `D`
   was chosen globally minimum in order,

   \[
      n\le {\delta+1\choose 2}.
   \]

   This application does not assume that the smaller graph produced in
   Seacrest's proof preserves the original minimum outdegree.

Combining these results with the accepted fixed-target packing theorem gives

\[
  2\delta+3\le n\le {\delta+1\choose 2}.
\]

Both inequalities are compatible for all relevant values of `delta`. For the
specific layer `delta=8`, they give `19<=n<=36`. If the unrefereed 2026
computer-assisted preprint of Sadhukhan--Sandeep--Sen is accepted only at its
stated scope, its Theorem 1.1 excludes `delta<=7`; it supplies no further
order or missing-graph restriction.

## Exact primary theorem ledger

### Seacrest (2019)

- Lemma 4: the edge-minimal set inequality described above.
- Corollary 5: existence of a counterexample on at most
  `binom(delta+1,2)` vertices.
- Consequence here: a quadratic upper bound for a globally minimum-order
  counterexample, but no control of the packing variables `b,q,s` and no
  linear bound `n<=2delta+2`.

### Espuny Diaz, Girao, Granet, and Kronenberg (2025)

- Proposition 4: a vertex-minimal counterexample has
  `delta+(D)>sqrt(|V(D)|)`.
- Proposition 5: if SSNC is false, then for every `d(n)=omega(1)` there are
  infinitely many strongly connected `n`-vertex counterexamples with
  `delta+(D)<d(n)`.
- Consequence here: Proposition 4 is weaker than Seacrest's order bound in the
  relevant range. Proposition 5 concerns nonminimal blow-ups and shows why a
  universal linear order bound cannot hold for arbitrary counterexamples;
  any useful linear bound must be explicitly minimality-specific.

### Zelenskiy, Darmosiuk, and Nalivayko (2021)

- Lemma 2.1 preserves a counterexample under the directed-cycle blow-up.
- Theorems 2.2 and 2.3 produce strongly connected counterexamples of
  arbitrarily low and arbitrarily high density, conditional on one
  counterexample existing.
- Lemma 3.1 proves that diameter two has a Seymour vertex.
- Theorem 3.2 produces a counterexample of every diameter `k>=3`, conditional
  on one existing.
- Consequence here: these are amplification theorems for arbitrary
  counterexamples, not restrictions on a globally minimum one. They do not
  yield the missing linear order bridge.

## The sharp `n=19`, `delta=8` equality cell

The accepted packing identities admit the sharp data

\[
 n=19,\quad \delta=8,\quad q=19,\quad e_v=0,\quad \mu_v=2
 \quad\hbox{for every }v.
\]

Thus every vertex has outdegree eight and missing degree two. The aggregate
data force the missing graph to be a 2-factor, not necessarily a single
cycle. Choosing its connected 2-factor cell gives `H=C_19`; the present-edge
graph is `G=K_19-C_19`, a connected 16-regular graph. A balanced orientation
has indegree and outdegree eight at every vertex and is Eulerian and strongly
connected. This establishes structural feasibility only; it does not say
that such an orientation is an SSNC counterexample.

Here and below, the **missing graph** `H` consists of unordered nonadjacent
pairs of the oriented graph. It is not the present-edge graph `G`.

## Does a known missing-graph theorem cover `K_19-C_19`?

**Answer: no, for every primary theorem checked.**

### Fidler--Yuster (2007)

Theorem 1.2 proves SSNC for:

1. orientations of `n`-vertex graphs with minimum underlying degree `n-2`;
2. orientations of complete graphs missing a star; and
3. orientations of pseudocliques, defined there as complete graphs with the
   edges of a smaller clique deleted.

For `G=K_19-C_19`, every vertex has underlying degree 16, not 17; the missing
graph is neither a star nor a clique. Therefore none of Theorem 1.2(i)--(iii)
applies.

Proposition 2.1 is the weighted tournament theorem and also does not apply,
because `G` has 19 missing pairs.

Most importantly, Fidler--Yuster Lemma 3.1 proves that the dependency digraph
has maximum in- and outdegree one in the section whose standing hypothesis is
that the missing graph is a matching. It cannot be transferred to `H=C_19`,
whose missing edges share endpoints. Thus one may not infer that the
`C_19` dependency digraph is a disjoint union of directed paths and cycles.

### Ghazal (2013)

- Theorem 2: every digraph "missing a comb" satisfies SSNC.
- Theorem 3: every digraph whose missing graph is `K-tilde_4` satisfies SSNC.
- Theorem 4: every digraph whose missing graph is `K-tilde_5` satisfies SSNC.
- Corollary 1 records the small cases `P_3,C_3,C_4,C_5`.

`C_19` is not a comb: in Ghazal's Definition of a comb, every vertex of the
stable part `A` has degree one, while `C_19` is 2-regular; with `A` empty the
remaining graph would be complete. It is not either finite exceptional graph,
and the cycle corollary stops at `C_5`. No theorem in this paper states the
result for cycles of arbitrary length.

### Daamouch--Al-Mniny--Ghazal (2025)

- Theorem 2.6 concerns a missing matching.
- Theorem 3.2 proves SSNC for an oriented graph missing two stars.
- Theorem 4.22 assumes that the missing graph is a disjoint union of paths of
  length at most two and imposes an additional double-cycle condition in the
  dependency digraph.
- Theorem 4.25 has the same missing-path hypothesis and additionally assumes
  that the dependency digraph consists only of directed cycles and double
  cycles.

The vertex-cover number of `C_19` is 10, so it is not the union of two stars.
It is a cycle, not a disjoint union of paths. Therefore Theorems 3.2, 4.22,
and 4.25 do not apply. The dependency-digraph conditions in 4.22 and 4.25 do
not remove their missing-path hypotheses.

### Wang--Lu (2026)

The primary publisher abstract states that SSNC holds for
`D_{0,3} union D_{1,1}`; the full theorem number is not visible on the
publisher page, so none is invented here. It defines `D_{s,t}` by a vertex
partition into parts inducing an `s`-degenerate and a `t`-degenerate graph.
The abstract also reproves the missing-matching and missing-star cases.

These classes do not contain `G=K_19-C_19`. For every `m`-vertex induced
subgraph `G[S]`, each vertex loses at most its two cycle neighbors, hence

\[
  \delta(G[S])\ge m-3.
\]

If `G[S]` is `s`-degenerate, applying the definition to `G[S]` itself gives
`m<=s+3`. Consequently each 1-degenerate part has size at most four, so a
`D_{1,1}` partition covers at most eight vertices. A 3-degenerate part has
size at most six; the 0-degenerate part is independent and has size at most
`alpha(K_19-C_19)=2`, so a `D_{0,3}` partition also covers at most eight.
The earlier `D_{0,2}` class mentioned in the abstract covers at most seven.
All totals are below 19.

### Cary (2019): the Eulerian issue

Theorem 2.7 says that every vertex has the SNP if an Eulerian digraph
"admits a simple dicycle intersection graph." The paper explicitly notes
that this restriction does not prove that all Eulerian digraphs have a
Seymour vertex. Theorem 2.9 concerns regular tournaments, not regular
orientations with missing pairs.

A balanced orientation of `K_19-C_19` is Eulerian, but no audited theorem
forces it to admit the additional simple dicycle-intersection decomposition.
Therefore Eulerianity does not close the class.

## Exact missing implication

The general packing route would close SSNC if one could prove either of the
following genuinely new implications.

1. **Minimum-order bridge:** every false instance has a globally
   minimum-order counterexample satisfying `n<=2delta+2`. Combined with the
   proved `n>=2delta+3`, this is an immediate contradiction. Proposition 5
   shows why the word "minimum" is essential.
2. **Packing-saturation bridge:** with the notation of
   `GENERAL_PACKING_ROUTE.md`, minimality or another global theorem implies

   \[
      kb+2q<n+s
   \]

   for every remaining `k>=3`. This would contradict the accepted necessary
   inequality `kb+2q>=n+s`.

For the connected first equality cell only, an adequate finite theorem would
be:

> Every orientation of `K_19-C_19` has a Seymour vertex.

No audited primary theorem supplies that statement. Proving it would exclude
only the connected missing-2-factor cell; the aggregate equality data allow
other 2-factors on 19 vertices, so even that theorem would not close the full
`n=19` layer or SSNC.

**Precise obstruction:** published minimal-counterexample results do not
control the packing saturation variables, and published missing-graph results
do not cover a missing cycle of length 19.

## Primary sources

1. Tyler Seacrest, *Seymour's Second Neighborhood Conjecture for Subsets of
   Vertices*, arXiv:1808.06293v3 (2019), Lemma 4 and Corollary 5.
   https://arxiv.org/pdf/1808.06293
2. Alberto Espuny Diaz, Antonio Girao, Bertille Granet, and Gal Kronenberg,
   *Seymour's second neighbourhood conjecture: random graphs and reductions*,
   Random Structures & Algorithms 66 (2025), e21251, Propositions 4--5.
   https://arxiv.org/pdf/2403.02842
3. Doron Fidler and Raphael Yuster, *Remarks on the Second Neighborhood
   Problem*, Journal of Graph Theory 55 (2007), 208--220, Proposition 2.1,
   Theorem 1.2, and Lemma 3.1.
   https://math.haifa.ac.il/raphy/papers/snp.pdf
4. Salman Ghazal, *A Contribution to the Second Neighborhood Problem*,
   Graphs and Combinatorics 29 (2013), 1365--1375, Theorems 2--4 and
   Corollary 1. https://arxiv.org/pdf/1106.5462
5. Moussa Daamouch, Darine Al-Mniny, and Salman Ghazal, *About the Second
   Neighborhood Conjecture for Tournaments Missing Two Stars or Disjoint
   Paths*, Contributions to Discrete Mathematics 20 (2025), 363--383,
   Theorems 2.6, 3.2, 4.22, 4.24, and 4.25.
   https://cdm.ucalgary.ca/article/download/77499/58529/271837
6. Michael Cary, *Vertices with the second neighborhood property in Eulerian
   digraphs*, Opuscula Mathematica 39 (2019), 765--772, Theorems 2.7 and 2.9.
   https://www.opuscula.agh.edu.pl/vol39/6/art/opuscula_math_3943.pdf
7. Oleksiy Zelenskiy, Valentyna Darmosiuk, and Illia Nalivayko, *A note on
   possible density and diameter of counterexamples to the Seymour's second
   neighborhood conjecture*, Opuscula Mathematica 41 (2021), 601--605,
   Lemmas 2.1 and 3.1 and Theorems 2.2, 2.3, and 3.2.
   https://www.opuscula.agh.edu.pl/vol41/4/art/opuscula_math_4128.pdf
8. Haozhe Wang and Mei Lu, *Seymour's second neighborhood conjecture for some
   oriented graphs*, Graphs and Combinatorics 42 (2026), Article 19; primary
   publisher abstract. https://doi.org/10.1007/s00373-026-03014-y
9. Arpan Sadhukhan, R. B. Sandeep, and Sagnik Sen, *A proof of Seymour's
   second neighborhood conjecture for oriented graphs with minimum out-degree
   equal to 7*, arXiv:2606.30588v1 (2026), Theorem 1.1 only.
   https://arxiv.org/pdf/2606.30588
