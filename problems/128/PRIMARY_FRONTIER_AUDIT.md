# Erdős Problem 128 - Primary-source frontier audit

Audit date: 2026-07-13.

## Verdict

The three primary papers do not prove Problem 128, either separately or in
combination. They do, however, isolate a direct one-lemma route to the full
theorem: a sparse half of a one-vertex deletion must be lifted by one vertex
when the deleted vertex has minimum degree at most `10n/29`. This is an exact
finite inequality, not an asymptotic surrogate or a list of equivalent
models.

The sharper primary-source consequence for the closed `n=20` certificate
route is

```text
39 <= e(G) <= 69,  delta(G) <= 6,
alpha(G) <= 7,     Delta(G) <= 7.
```

The previous `e(G)<=79` source bound was not sharp: Razborov's independence
number theorem gives `alpha(G)<=7`, and every neighbourhood in a
triangle-free graph is independent, so Delta(G)<=7. Bedenknecht-Mota-
Reiher-Schacht give delta(G)<=6 at this order. Hence
2e(G)<=6+19*7=139; parity gives (G)<=69.
This fact does not reopen the precommitted finite-search route.

## Statement convention

For an `n`-vertex graph `G`, write

```text
b(G) = min { e(G[S]) : |S| = floor(n/2) }.
```

The official problem asks whether every triangle-free graph satisfies
`b(G) <= n^2/50`. The current official page labels the problem open and the
thread records two necessary conventions: the size is `floor(n/2)` and
"subgraph" means induced subgraph.

- Thomas F. Bloom, [Erdős Problem #128](https://www.erdosproblems.com/128),
  accessed 2026-07-13.
- [Official discussion thread](https://www.erdosproblems.com/forum/thread/128),
  accessed 2026-07-13; see the comments incorporated on 31 October 2025.

## Exact primary results

### Keevash-Sudakov (2006)

Peter Keevash and Benny Sudakov, "Sparse halves in triangle-free graphs,"
*Journal of Combinatorial Theory, Series B* **96** (2006), 614-620,
[doi:10.1016/j.jctb.2005.11.003](https://doi.org/10.1016/j.jctb.2005.11.003).

- Theorem 1.1: if `G` is triangle-free, `e(G)>=n^2/5`, and every
  `floor(n/2)`-set spans at least `n^2/50` edges, then `n=10m` and
  `G=C5(2m)`, the uniform blow-up of the 5-cycle. Since that graph has a half
  attaining equality, a strict counterexample to Problem 128 cannot have
  `e(G)>=n^2/5`.
- Proposition 1.2: if `G` is triangle-free and `e(G)<=n^2/12`, then
  `b(G)<=n^2/50`.

The dense statement is a classification under a non-strict local lower
bound, not merely the abstract's informal claim that the conjecture holds in
that range.

### Norin-Yepremyan (2015)

Sergey Norin and Liana Yepremyan, "Sparse halves in dense triangle-free
graphs," *Journal of Combinatorial Theory, Series B* **115** (2015), 1-25,
[doi:10.1016/j.jctb.2015.04.006](https://doi.org/10.1016/j.jctb.2015.04.006),
[arXiv:1311.5818v2](https://arxiv.org/abs/1311.5818).

- Theorem 1.1: every triangle-free `n`-vertex graph with
  `delta(G)>=5n/14` has `b(G)<=n^2/50`.
- Theorem 1.2: there exists an absolute `gamma>0` such that the same
  conclusion holds when `e(G)>=(1/5-gamma)n^2`. The paper does not state a
  numerical value of `gamma`; its proof chooses it through nested stability
  constants, so this theorem must not be used as an unstated explicit
  integer cutoff.
- Theorem 5.1 gives two explicit sufficient alternatives:

  ```text
  (a) (1/n) sum_v d(v)^2 >= ((2/5)n)^2
      and Delta(G) < (2/5 + 1/135)n;

  (b) Delta(G) >= (2/5 + 1/135)n
      and (1/n) sum_v d(v) >= (2/5 - 1/125)n.
  ```

  Either alternative implies a sparse half.
- Theorem 6.3: there exists `delta>0` such that every triangle-free graph
  that is `delta`-approximated, in Definition 4.1's edit-distance sense, by
  the Petersen graph has a sparse half. Again the displayed conclusion is
  existential in `delta`.

### Bedenknecht-Mota-Reiher-Schacht (2019)

Wiebke Bedenknecht, Guilherme Oliveira Mota, Christian Reiher, and Mathias
Schacht, "On the local density problem for graphs of given odd-girth,"
*Journal of Graph Theory* **90**(2) (2019), 137-149,
[doi:10.1002/jgt.22372](https://doi.org/10.1002/jgt.22372),
[arXiv:1609.05712v2](https://arxiv.org/abs/1609.05712).

The paper defines an `n`-vertex graph to be `(1/2,1/50)`-dense when every
set of `floor(n/2)` vertices spans strictly more than `n^2/50` edges, exactly
the counterexample convention on the official page.

- Theorem 1.2: if `G` is homomorphic to any Andrasfai graph `F_d`, then
  `G` is not `(1/2,1/50)`-dense; equivalently, it has a sparse half.
- Corollary 1.3(a): every triangle-free `n`-vertex graph with
  `delta(G)>10n/29` has a sparse half.
- Corollary 1.3(b): if additionally `chi(G)<=3`, the sufficient condition
  improves to `delta(G)>n/3`.

The degree inequalities are strict. Thus a counterexample has
`delta(G)<=10n/29`, not necessarily `<10n/29`. This direct finite theorem
improves the `5n/14` minimum-degree boundary of Norin-Yepremyan.
### Razborov (2022)

Alexander A. Razborov, "More about sparse halves in triangle-free graphs,"
*Sbornik: Mathematics* **213**(1) (2022), 109-128,
[doi:10.1070/SM9615](https://doi.org/10.1070/SM9615),
[arXiv:2104.09406v2](https://arxiv.org/abs/2104.09406).

Razborov normalizes `rho(G)=2e(G)/n^2`,
`alpha(G)=alpha_unscaled(G)/n`, and `beta(G)=b(G)/n^2` (with the standard
fractional half convention at odd order). His exact relevant results are:

- Theorem 3.2: `beta(G)<=27/1024` for every triangle-free graph.
- Theorem 3.3: the conjectured `1/50` bound holds if `G` has no induced
  matching of size two.
- Theorem 3.4: it holds when

  ```text
  rho(G) <= rho_0 := (33-sqrt(161))/116
                    = 0.175098469478883...
  ```

- Theorem 3.5: it holds for every triangle-free strongly regular graph.
- Theorem 3.6: if `alpha(G)>=3/8`, then

  ```text
  beta(G) <= (1/2) alpha(G) (1/2-alpha(G)).
  ```

  Corollary 3.7 gives the conjectured bound when `alpha(G)>=2/5`.
- Theorem 3.8: it holds for every triangle-free graph of girth at least five.

Theorem 3.1's load-bearing flag-algebra inequalities are

```text
C4(G) >= (3/2)rho(G)^2 - (81/256)rho(G),
C4(G) >= (3/2)rho(G)^2 - (6/25)rho(G)
```

in the second line under the absence of an induced two-edge matching. They
feed Theorems 3.2 and 3.3 through Proposition 1.1; they do not by themselves
give the `1/50` bound in the residual class.

## Exact residual profile

Consequently, any counterexample to Problem 128 must simultaneously satisfy

```text
rho(G) > (33-sqrt(161))/116,
e(G) < (1/5-gamma)n^2 for Norin-Yepremyan's absolute gamma,
delta(G) <= 10n/29,
alpha(G) < 2n/5,
Delta(G) < 2n/5,
girth(G) = 4,
G contains an induced matching of size two,
G is not strongly regular.
```

Here `Delta(G)<2n/5` follows from `alpha(G)<2n/5`, because every vertex
neighbourhood is independent. These are necessary audit conditions only;
enumerating subclasses inside this residual profile would be a forbidden
reformulation cascade.

At `n=20`, the already-proved local counting lemma gives `e(G)>=39`.
Razborov's Corollary 3.7 gives `alpha(G)<=7`; hence `Delta(G)<=7` and the
handshake lemma gives `e(G)<=70`. Razborov's universal Theorem 3.2 also says
that some 10-set has at most `floor(27*400/1024)=10` edges, so a putative
certificate's minimum 10-set count is exactly 9 or 10. These restrictions do
not constitute a solution or an infeasibility proof.

## Smallest direct full-theorem frontier

The following is the smallest non-restatement bridge exposed by the primary
results.

**Low-degree one-vertex lift lemma `LDL(10/29)`.** Let `n=2m` be even, let
`G` be a triangle-free `n`-vertex graph, and let `v` be a minimum-degree
vertex with `d(v)<=10n/29`. Define

```text
A_v = { A subseteq V(G)\{v} :
        |A|=m-1 and e(G[A]) <= (n-1)^2/50 }.
```

If `A_v` is nonempty, then

```text
min_{A in A_v} min_{w in V(G)\A}
    ( e(G[A]) + d_A(w) ) <= n^2/50.                 (LDL)
```

The left side is the edge count of the `m`-set `A union {w}`. Thus `(LDL)`
is an exact one-deletion/one-insertion inequality. It is not the statement
"all remaining graphs have sparse halves": it assumes a certified sparse
half at order `n-1` and asks for one explicit local lift.

A baseline part of `(LDL)` is elementary. If
`d(v)<=(2n-1)/50`, choose any `A in A_v` and take `w=v`; then

```text
e(G[A])+d_A(v)
 <= (n-1)^2/50 + (2n-1)/50
 = n^2/50.
```

The genuine frontier is therefore the degree gap

```text
(2n-1)/50 < delta(G) <= 10n/29.
```

No theorem in the three audited papers proves this lift.

## Lemma tree to the full theorem

1. Assume a counterexample `G` of minimum order `n`.
2. If `n` is odd, delete any vertex. Minimality supplies a set of
   `(n-1)/2=floor(n/2)` vertices spanning at most `(n-1)^2/50<n^2/50`, a
   contradiction. Hence `n` is even.
3. Norin-Yepremyan Theorem 1.1 forces `delta(G)<5n/14`; choose a
   minimum-degree vertex `v`.
4. Minimality applied to `G-v` makes `A_v` nonempty.
5. `LDL(10/29)` supplies `A` and `w` with
   `e(G[A union {w}])<=n^2/50`, contradicting that `G` is a counterexample.

Thus a proof of `LDL(10/29)` proves the full Erdős-Rousseau assertion. A
failure of the lift at any finite graph would be a concrete counterexample
to the proposed frontier lemma and must be examined directly; replacing it
by density limits, further equivalent models, or bounded-family exclusions
would not close the displayed lemma tree.

## Source files audited

The complete PDFs, not only abstracts, were read, including the later minimum-degree improvement. SHA-256 values of the
downloaded primary-source PDFs were:

```text
Keevash-Sudakov  97708E67DFA312E4E38DF0C80FBD5345400D25A6501E15037F249D9255722EE6
Norin-Yepremyan   3BA6D0F2BAD685BCB779493623EAAF9CE716EE0926D1C6C20BB09C8F4A7C6D25
Razborov          C9FFC6B1ECA473BBE2B405488B60D03369D0160D9FD25533A5DC17616D28D734
Bedenknecht et al. D1575DAD3F4BB4CC64EE29E8DDCE9ADF9ECCFB1F72B9E94BE6AC81A027173D22
```

## Post-audit correction and stop note

The initial three-paper audit omitted Wiebke Bedenknecht, Guilherme Oliveira Mota, Christian Reiher, and Mathias Schacht, "On the local density problem for graphs of given odd-girth," arXiv:1609.05712. Its stated consequence proves the sparse-half conjecture when `delta(G)>10n/29`, improving the `5n/14` cutoff above. Thus a corrected deletion/lift route would use the gap `(2n-1)/50 < delta(G) <= 10n/29`. This still leaves the open core and supplies no lift mechanism. The easy-target selection was stopped; do not treat the earlier `LDL(5/14)` label as the sharp literature frontier.
