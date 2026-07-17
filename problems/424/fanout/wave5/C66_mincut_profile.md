# C66: exact profiles of the C60 canonical minimum cut

## Verdict

The C60 contracted network was profiled at

```text
54, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000.
```

At every cutoff, an integral maximum flow was followed by an independent
integer reconstruction of its residual source shore.  The reconstructed cut
has no infinite-capacity edge, contains every splitless root, is closed under
every unary generated-factor selector, and satisfies

\[
 \operatorname{cap}(S)=|K_X\setminus S|+|\partial_D^+(S)|
 =\kappa_X.
\]

In particular, all eleven cuts satisfy

\[
 |K_X\cap S|\le |\partial_D^+(S)|.
\]

This is finite evidence, not a proof for arbitrary `X`.

The most useful new observation is a seed-chain decomposition.  It reduces
the reserve to the difference of two concrete chain classes.  A coordinatewise
rank pairing between those classes holds at every cutoff `2 <= X <= 2000` and
at all five larger cutoffs.  This is the simplest surviving candidate invariant.

## 1. Exact extraction and verification

Let `S` be the hole vertices reachable from the source in the residual graph
of an integral maximum flow.  The script independently checks the following
using the original Python-integer capacity dictionary.

1. The sink is not residual-reachable.
2. Every structural splitless hole lies in `S`.
3. For every unary selector `(n,g,p)` with `n in S`, where `g` is generated
   and `n=gp-1`, one has `p in S`.
4. Direct summation of all capacity edges leaving the residual shore equals
   the maximum-flow value.
5. The only finite cut edges are source arcs to `K_X\S` and outgoing seed
   arcs from `S`.
6. The exact reserve identity

   \[
   \kappa_X-|K_X|=|\partial_D^+(S)|-|K_X\cap S|
   \]

   holds.

The JSON contains the complete sorted source-side hole set, the complete
hard-hole set inside it, every outgoing seed arc, and every active closure
selector triple `(output, generated factor, hole factor)`.

## 2. Scalar profiles

Write `K(S)=|K_X cap S|`, `D(S)=|partial_D^+(S)|`, `HT` for hard truncated
seed chains, and `NE` for nonhard exiting seed chains.

| X | S size | K(S) | D(S) | reserve | HT | NE | max unary depth |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 54 | 20 | 1 | 1 | 0 | 1 | 1 | 2 |
| 100 | 37 | 2 | 3 | 1 | 2 | 3 | 3 |
| 200 | 74 | 6 | 6 | 0 | 6 | 6 | 4 |
| 500 | 169 | 17 | 23 | 6 | 16 | 22 | 5 |
| 1,000 | 339 | 38 | 41 | 3 | 34 | 37 | 6 |
| 2,000 | 652 | 93 | 93 | 0 | 82 | 82 | 7 |
| 5,000 | 1,491 | 226 | 247 | 21 | 195 | 216 | 8 |
| 10,000 | 2,802 | 455 | 497 | 42 | 388 | 430 | 9 |
| 20,000 | 5,104 | 885 | 1,030 | 145 | 755 | 900 | 10 |
| 50,000 | 11,457 | 2,103 | 2,613 | 510 | 1,792 | 2,302 | 11 |
| 100,000 | 21,067 | 3,890 | 5,191 | 1,301 | 3,301 | 4,602 | 12 |

The maximum observed global ratio `K(S)/D(S)` is exactly `1`, first attained
at `X=54`.  At the five cutoffs from `5000` through `100000`, the ratios are

```text
226/247, 455/497, 885/1030, 2103/2613, 3890/5191.
```

Thus the sampled canonical cuts exhibit a coefficient far below `2`, but
the fact that the ratio is at most `1` is the C60 cut inequality itself and
cannot be used as its proof.

## 3. Exact seed-chain decomposition

Inside `S`, retain the seed map

\[
 D(m)=2m-1.
\]

It is injective and increasing, so its internal edges partition `S` into
disjoint directed paths.  Every noninitial path vertex is odd.  Since every
hard-shaped value is even, each seed path contains at most one hard hole,
and that hard hole is its root.

Every path has one of two terminal types.

* It exits through a unique outgoing seed arc before the cutoff.
* Its next seed child exceeds `X`, so the path is truncated.

Let `HE`, `HT`, `NE`, and `NT` count hard exiting, hard truncated, nonhard
exiting, and nonhard truncated paths.  Then, for every source shore `S`,

\[
 |K_X\cap S|=HE+HT,
 \qquad
 |\partial_D^+(S)|=HE+NE,
\]

and therefore

\[
 \boxed{\operatorname{reserve}=NE-HT.}
\]

The profiler verifies these identities from the explicit path partition at
every cutoff.  At `X=100000`, for example,

```text
HE = 589, HT = 3301, NE = 4602, reserve = 4602 - 3301 = 1301.
```

This isolates the remaining combinatorics: hard truncated chains must be
paid by nonhard exiting chains.

## 4. Candidate rank-pairing invariant

For one cutoff, list the roots of hard truncated chains as

\[
 h_1<h_2<\cdots<h_t
\]

and the roots of nonhard exiting chains as

\[
 e_1<e_2<\cdots<e_r.
\]

The exact profiles satisfy

\[
 \boxed{r\ge t\quad\hbox{and}\quad e_i\le h_i\ (1\le i\le t).}
\tag{C66-RANK}
\]

This was checked at every one of the 1999 cutoffs `2,...,2000`, with no
failure, and at `5000, 10000, 20000, 50000, 100000`.  The assertion is
strictly stronger than the needed cardinality comparison `NE>=HT` and gives
an order-preserving injection from hard truncated chains to nonhard exits.

`C66-RANK` is not proved.  It is the main invariant suggested by the
canonical minimizers.  A proof would immediately establish the C60 cut
inequality for the canonical source shore.  To prove the full cut theorem,
one must also explain why this pairing applies to an arbitrary admissible
closed shore, or justify reduction to the canonical shore.

## 5. Componentwise approaches fail

The unary-selector graph cannot be discharged component by component with a
coefficient strictly below `2`.

At `X=100000`, the unary component

```text
{8898, 17795, 88974}
```

has two hard holes and one outgoing seed arc.  Its closure selectors are

```text
(17795, 2, 8898)
(88974, 5, 17795)
```

so its exact local ratio is `2/1`.  Moreover, 478 unary components contain a
hard hole but no outgoing seed arc.  The first three are

```text
{25062, 50123}, {25238, 50475}, {30066, 60131}.
```

Global compensation between components is therefore essential.  Adding
internal seed edges does not merge unary components: whenever both `m` and
`2m-1` are holes, the seed edge `m -> 2m-1` has the reverse unary selector
`2m-1 -> m`, supplied by the generated factor `2`.

## 6. Depth, selectors, and residues at 100000

The source shore has 21,067 holes and 21,148 active unary selectors.  There
are 9,372 undirected unary components, 9,152 of them singletons.  The maximum
unary depth is 12.  Of 12,687 unary terminals, 11,928 are structural
splitless roots and 759 are nonsplitless terminals whose available factor
rows all have two hole factors.

The exact `mod 6` distributions are

| class mod 6 | 0 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|
| source shore | 12,181 | 3,949 | 1,817 | 3,120 |
| hard holes in shore | 3,335 | 555 | 0 | 0 |
| outgoing seed origins | 3,155 | 1,246 | 189 | 601 |

No residue class by itself supplies the required pairing.  In particular,
the nonhard exits include both even and odd roots, while all hard truncated
roots are even.  The full JSON records parity and residues modulo
`3,6,9,12` for all principal classes.

## 7. Reproduction

~~~powershell
python problems/424/fanout/wave5/C66_mincut_profile.py `
  --output problems/424/fanout/wave5/C66_mincut_profile.json
~~~

The default run profiles the eleven displayed cutoffs and performs the dense
rank scan through `2000`.  All arithmetic used for acceptance is integral;
the only rational objects in the output are numerator/denominator records.

~~~text
C66_mincut_profile.py
2CC54435C2DFAA63FFF87E261C325CA97FFFF098DEF08ABD1FF55FF3299A2DD6

C66_mincut_profile.json
CE8ED11C0C9DF91BF6A639E49EBFF212341526BECD7FD7E26B0F8B93997EB88A
~~~
