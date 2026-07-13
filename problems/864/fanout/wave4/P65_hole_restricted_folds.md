# P65: hole-restricted shifted-sum folds

## Verdict

The conditioned statement remains **open**.  No exact hole-satisfying
falsifier was found, but no proof was obtained.  The finite gate is much
stronger than the earlier unconditioned test:

* every normalized Sidon ruler of width at most 45 was checked;
* all positive-defect translations of 133 P20 rulers were checked; and
* every endpoint-retaining subset of all 18 dense P53 ruler orientations was
  optimized by exact integer CP-SAT whenever a monotone count did not already
  settle the case.

All of these tests satisfy

\[
                         C_S\le 2p-3.                    \tag{1}
\]

The precise obstruction is graph-theoretic.  The hole makes the canonical
outer collision graph bipartite, but it does **not** make it planar,
outerplanar, 2-degenerate, or free of dense local fans.  An exact real
hole instance contains a literal `K_{3,3}` in this graph.  Thus the tempting
Euler/outerplanar proof of (1) is unavailable.  Any proof must use the
complementary inner-edge labels and the globally inactive marks, not just the
outer collision graph.

## 1. Exact reformulations

Let

\[
 B\subseteq\{0,\ldots,h-1\},\qquad \max B=h-1,
 \qquad |B|=p,
\]

and suppose all unordered sums, including the diagonal sums, are distinct.
Put

\[
 S=B+B,\qquad \Delta^+(B)=\{y-x:x,y\in B,\ x<y\}.
\]

The literal hole, with repetitions allowed, has the exact two-set form

\[
 \boxed{
 -b\notin3B-B
 \quad\Longleftrightarrow\quad
 \Delta^+(B)\cap(S+b)=\varnothing.}                    \tag{2}
\]

Indeed, a representation

\[
 x+y+z-w=-b
\]

is equivalent to the positive difference

\[
 w-z=x+y+b.
\]

This proof permits `x=y`, `x=z`, and every other coincidence.  Conversely,
any common value on the right of (2) supplies the literal four-variable
representation.

If `gamma=min(B)`, `Z=B-gamma`, and `W=max(Z)`, then

\[
 h=W+\gamma+1,
 \qquad
 -b\notin3B-B
 \Longleftrightarrow
 \Delta^+(Z)\cap(2\gamma+b+S(Z))=\varnothing.           \tag{3}
\]

This is the exact gap form used by every search.

Because `S` lies in `[0,2h-2]`, its fibers modulo `h` have size at most two,
and therefore

\[
 \boxed{C_S=|\{s\in S:s+h\in S\}|.}                   \tag{4}
\]

For a normalized ruler `Z`, (4) is the integer autocorrelation of `S(Z)` at

\[
                         h=W+\gamma+1.                  \tag{5}
\]

No modular relaxation is used.

## 2. Complete width-45 gate

The program

```text
problems/864/compute/p65/search_hole_restricted_folds.py
```

generates every endpoint-normalized Sidon ruler `Z` of width at most 45.
For each ruler it checks every translation satisfying both

\[
 \delta={3p^2-p+2\over2}-h>0
\]

and `h<=2W`.  Translations with `h>2W` have `C_S=0` identically, so omitting
them cannot omit a falsifier.  Both `b=1` and `b=2` are tested via (3).

The exact totals are

| quantity | value |
|---|---:|
| normalized rulers | 745,733 |
| relevant hole translations | 9,953,261 |
| failures of (1) | 0 |

The ruler-stream SHA-256 is

```text
772e239cc1a5d1a02f7f2d9a63f5e53fab579cb472834c14446d3bd97e2e9e53
```

This independently agrees with the P53 unconditioned ruler stream.  The
result file is

```text
problems/864/compute/p65/hole_restricted_folds_width45.json
```

with SHA-256

```text
5a194c6637f85482886ade2ecd726f14e69341370bccdd0d71d87d752d7a8ce1
```

This is finite evidence only.

## 3. Family and subset gates

### 3.1 P20 translations

Every positive-defect translation of each of the 133 distinct P20 rulers was
tested, including translations for which `C_S=0`.  Exact totals:

\[
 \boxed{165225\text{ hole translations},\qquad0\text{ failures}.} \tag{6}
\]

The output is

```text
problems/864/compute/p65/p20_hole_fold_audit.json
```

with SHA-256

```text
219f62c65ab612dcf319e6069a92fc14439f2ccbafc7902450e46573078993fc
```

### 3.2 Exact optimization inside dense universes

For a fixed ruler universe and fixed `(h,b)`, introduce one Boolean variable
for each retained mark.  Every fold is an exact AND of its two pair labels;
every literal relation `x+y+z+b=w` is a forbidden selected hyperedge.  The
integer objective is

\[
                         C_S-2p.                        \tag{7}
\]

A falsifier to (1) has objective at least `-2`.

For the 26-mark P53 parent, all 984 translation/`b` cases were covered:
110 nontrivial cases were solved `OPTIMAL`, and 874 were settled by the
monotone full-universe count.  The maximum objective was

\[
                             -18.                       \tag{8}
\]

For all 18 listed/reflected dense P53 universes, over every positive-defect
translation, the status totals were

| status | cases |
|---|---:|
| `OPTIMAL` | 1,154 |
| `INFEASIBLE` | 258 |
| monotone upper bound | 14,104 |
| unresolved | 0 |

The maximum objective was

\[
                             -16.                       \tag{9}
\]

Thus none of these universes contains a conditioned falsifier, even after
arbitrary deletion of marks while retaining the top endpoint.  The exact
artifacts are

```text
problems/864/compute/p65/parent_subset_optimization.json
problems/864/compute/p65/dense_subset_optimization.json
```

### 3.3 The unrestricted search did not certify a result

The fully unrestricted model for

\[
 p=25,\qquad h=494,\qquad b=1,\qquad C_S\ge48
\]

has 122,265 diagonal-inclusive pair variables and 121,771 literal hole
constraints.  After 310.26 seconds, 735,450 branches, and 77,453 conflicts,
CP-SAT returned `UNKNOWN`.  This is neither positive nor negative evidence
and is recorded only to delimit the finite gate:

```text
problems/864/compute/p65/unrestricted_p25_H493_b1_target48.json
```

## 4. A stronger linear guess is false

The complete subset optimizer gives the exact conditioned example

\[
\begin{split}
B=\{&23,24,56,127,133,186,272,281,337,341,366,379,409,\\
    &453,479,487,498,510,515\},
\end{split}
\]

with

\[
 p=19,\qquad h=516,\qquad b=2,\qquad \delta=17.
\]

All 190 unordered sums, including the 19 diagonals, are distinct, and

\[
 -2\notin3B-B,\qquad C_S=20.                            \tag{10}
\]

The folds consist of 13 off-diagonal/off-diagonal pairs, four with a low
diagonal, and three with a high diagonal.  Therefore the tempting stronger
claim `C_S<=p-1` is false:

\[
                         20>18.                         \tag{11}
\]

## 5. The exact graph obstruction

For a fold, write its pair labels in increasing order as

\[
 a\le c,qquad u\le v,qquad a+c+h=u+v.
\]

The interval range forces

\[
                         a\le c<u\le v.                 \tag{12}
\]

Indeed, if `u<=c`, then `v-a=h+c-u>=h`, contradicting
`v-a<=h-1`.

Associate to this fold its **outer edge** `{a,v}`.  Its complementary inner
edge is `{c,u}`, and

\[
                         (v-a)+(u-c)=h.                 \tag{13}
\]

The outer edge determines the fold: its length determines the complementary
inner length, and integer Sidonicity gives the unique pair with that positive
difference.  Hence the outer graph is simple and

\[
                         |E(G_{out})|=C_S.              \tag{14}
\]

Moreover the outer interval contains the inner interval, so its length is at
least `h/2`.  Every outer edge therefore joins the lower and upper coordinate
halves.  Thus `G_out` is bipartite.

This does **not** yield (1).  In the exact P20 row

```text
singer-e82f2d6a63ca
```

one has

\[
 p=152,\quad h=29747,\quad b=1,\quad \delta=4834,
 \quad -1\notin3B-B,\quad C_S=256.                     \tag{15}
\]

Its outer graph contains all nine edges of the literal biclique

\[
 \{7469,7994,8476\}\times\{27235,27527,28303\}.         \tag{16}
\]

Thus it contains `K_{3,3}` and is nonplanar.  Its core number is 6.  In
particular, the hole does not imply planarity, outerplanarity, or
2-degeneracy.  These failures occur in a real integer Sidon ruler satisfying
the literal hole, not in an abstract graph relaxation.

The unconditioned P53 counterexample shows why the graph idea was tempting:
its outer graph is also bipartite but nonplanar and has 49 edges on 25 marks,
exceeding `2p-3`.  The hole removes that particular example, but (16) shows
that it does not remove the graph-theoretic mechanism responsible for
nonplanarity.

## 6. Precise remaining obstruction

P65 is now the following exact labeled-graph problem.

> A Sidon ruler `B` defines a simple bipartite graph of long differences.
> Every edge has a uniquely labeled complementary inner difference summing
> with it to `h`.  In addition, `(B+B+b)` is disjoint from the full positive
> difference set.  Prove that the number of long edges is at most `2p-3`.

The unlabeled graph cannot prove this: it may contain `K_{3,3}`, have core
number at least 6, and be nonplanar.  A proof would have to couple three
pieces of information that all failed local graph arguments discard:

1. the complementary inner-edge label in (13);
2. the globally unused marks of `B`, including vertices isolated in
   `G_out`; and
3. the sum/difference disjointness (2) across **all** pair sums, not only the
   folds.

No inequality performing that coupling was established.  Conversely, the
unrestricted CP-SAT timeout supplies no falsifier.  Therefore the correct P65
conclusion is: **the conditioned bound survives every completed exact gate,
while its natural planar/degeneracy proof mechanism is exactly falsified by
(15)--(16).**

## 7. Reproduction

From the repository root:

```powershell
python -B problems/864/compute/p65/search_hole_restricted_folds.py `
  --max-width 45 --skip-parent `
  --output problems/864/compute/p65/hole_restricted_folds_width45.json

python -B problems/864/compute/p65/audit_p20_hole_folds.py

python -B problems/864/compute/p65/optimize_parent_subsets.py `
  --seconds 30 --workers 8 --max-gamma 491

python -B problems/864/compute/p65/optimize_dense_subsets.py `
  --seconds 30 --workers 8

python -B problems/864/compute/p65/verify_p65_artifacts.py
```

The final verifier independently reconstructs (10), checks all nine edges in
(16), and checks the exact census and optimization status fields.
