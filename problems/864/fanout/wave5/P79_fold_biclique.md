# P79: exact outer-fold bicliques and the `2p-1` shift candidate

## Verdict

Both proposed biclique exclusions are false on the exact positive-defect,
literal-hole corpus.

* The maximum two-sided pair codegree is `12` over all P20 translations and
  `11` over both stored-row views.  Thus `K_{2,4}` and `K_{4,2}` occur often.
* Literal `K_{4,4}` occurs in all three views.  The failure counts are 1,744,
  11, and 10, respectively.
* The maximum balanced biclique order in every view is exactly 5.  One row
  contains `K_{5,5}`, and exact neighborhood-subset enumeration finds no
  `K_{6,6}`.

Consequently neither the `K_{2,4}` KST route nor the earlier `K_{4,4}` route
can bound the P65 fold count.

The stronger candidate

\[
 |(B+B)\cap(B+B+h)|\le 2|B|-1                         \tag{G}
\]

is also false as stated for arbitrary `h>0`.  The five-mark Sidon set

\[
 B=\{0,2,3,8,12\},\qquad h=4
\]

has `C_S=10>9`.  The natural repaired regime `h>diam(B)`, which is the actual
P53/P75 endpoint regime up to translation, is also false: a P20 ruler has
`p=29`, `h=640`, and `C_S=58>57`.

## 1. Precise P65 outer fold graph

Let

\[
 B\subseteq\{0,\ldots,h-1\},\qquad \max B=h-1,
 \qquad p=|B|,
\]

and suppose the map from unordered pairs (diagonals included) to their sums
is injective.  Write `S=B+B`.  For every `t` such that `t,t+h in S`, let

\[
 t=a+c,\qquad t+h=u+v,qquad a\le c,\quad u\le v.
\]

The interval range forces

\[
                         a\le c<u\le v.                 \tag{1}
\]

Indeed, `u<=c` would give `v-a=h+c-u>=h`, impossible for two marks in
`[0,h-1]`.  The fold has outer edge `(a,v)` and complementary inner edge
`(c,u)`, with

\[
                    (v-a)+(u-c)=h.                      \tag{2}
\]

Define

\[
\begin{aligned}
 L&=\{x\in B:2x<h\},\\
 R&=\{x\in B:2x\ge h\},\\
 E(G_{out})&=\{(a,v):a+c+h=u+v\text{ as in (1)}\}.
\end{aligned}                                           \tag{3}
\]

The outer length is at least `h/2`, so every edge lies in `L x R`.  The edge
determines the fold: `v-a` determines `h-(v-a)=u-c`, and integer Sidonicity
makes the positive-difference label `(c,u)` unique.  Therefore `G_out` is a
simple bipartite graph and

\[
                         |E(G_{out})|=C_S.               \tag{4}
\]

The parameter `b` is not part of the graph.  It filters the audited rows by
the full literal-hole condition

\[
 -b\notin3B-B
 \quad\Longleftrightarrow\quad
 \Delta^+(B)\cap(B+B+b)=\varnothing.                    \tag{5}
\]

All rows below also have positive defect

\[
 \delta=(3p^2-p+2)/2-h>0.                               \tag{6}
\]

## 2. Exact codegree and biclique algorithms

For each right vertex `y`, the auditor increments one counter for every
unordered pair in `N(y)`.  The final counter of `{x,x'}` is exactly
`|N(x) intersect N(x')|`.  Reversing the two sides gives the symmetric
codegrees.  Thus codegree at least 4 is exactly a `K_{2,4}` or `K_{4,2}`
witness.

For `K_{r,r}`, the code first repeatedly removes vertices of degree below
`r`; every `K_{r,r}` survives this exact `r`-core reduction.  On the smaller
enumeration side it then counts every `r`-subset of every neighborhood.
Multiplicity at least `r` is exactly a `K_{r,r}`.  The first absent order
after a present order certifies the maximum balanced biclique size.  No SAT
relaxation, floating-point comparison, or randomized sampling is used.

The audited domains are:

1. every positive-defect literal-hole translation of the 133 distinct P20
   rulers used by P65;
2. all 134 positive-defect stored P46/P20 rows; and
3. the 37 stored P45 large profiles (`p>=72`), reported separately although
   they are a subset of domain 2.

## 3. Exact corpus results

| domain | rows | distinct graphs | max pair codegree | codegree >=4 | `K4,4` | max balanced `r` |
|---|---:|---:|---:|---:|---:|---:|
| all P20 translations | 165,225 | 92,396 | 12 | 92,817 | 1,744 | 5 |
| stored positive P20 rows | 134 | 134 | 11 | 67 | 11 | 5 |
| stored large rows | 37 | 37 | 11 | 37 | 10 | 5 |

The balanced-order distributions, with `0` meaning no `K_{4,4}`, are

| domain | 0 | 4 | 5 |
|---|---:|---:|---:|
| all P20 translations | 163,481 | 1,743 | 1 |
| stored positive P20 rows | 123 | 10 | 1 |
| stored large rows | 27 | 9 | 1 |

The unique order-5 row in every view is `singer-e82f2d6a63ca`:

\[
 (p,h,b,\delta,C_S)=(152,29747,1,4834,256).
\]

It contains

```text
{7469,7994,10098,10243,10294}
  x {28303,28483,28494,29656,29724}.
```

The exact search finds no `K_{6,6}` in any requested row.  This is a finite
corpus fact, not a universal forbidden-biclique theorem.

## 4. Small exact witnesses

### 4.1 Smallest `K_{2,4}` in the full translation corpus

The smallest row in lexicographic order `(p,h,b,B,source_id)` is based on
`singer-cdc2af0ca853`:

```text
B = {104,124,135,162,187,199,208,222,238,264,
     267,300,307,308,355,357,361,374,379,389}
(p,h,b,delta,C_S) = (20,390,1,201,12).
```

The left pair `{104,124}` has the four common neighbors
`{361,374,379,389}`.  Its eight exact folds are

```text
104+222+390=355+361    124+208+390=361+361
104+187+390=307+374    124+124+390=264+374
104+264+390=379+379    124+222+390=357+379
104+162+390=267+389    124+264+390=389+389
```

The smallest stored-row witness has `(p,h,b)=(27,749,2)` and source
`bose-e3149afd6ad7`; the pair `{143,247}` has common neighbors
`{658,693,726,748}`.  The smallest large-row witness has `p=72`.

### 4.2 Smallest `K_{4,4}` in the prescribed corpus

The smallest requested-corpus row is `singer-natural-aaccd2fd8048`:

\[
 (p,h,b,\delta,C_S)=(60,4455,1,916,54),
\]

with biclique

```text
{1169,1291,1520,1697} x {4245,4391,4417,4454}.
```

The JSON certificate stores the complete 60-mark ruler and all 16 uniquely
labeled fold equations.  This is the smallest witness in the stated P20
translation corpus, not a global minimality claim.

The later P75 row is a smaller exact witness outside that archived slice.
It is a positive-defect literal hole with

\[
 (p,h,b,\delta,C_S)=(26,988,1,14,51)
\]

and contains

```text
{3,5,69,211} x {883,915,977,987}.
```

It has maximum pair codegree 7: `{3,5}` has common neighbors
`{689,863,883,915,953,977,987}`.  Therefore Sidonicity, positive defect, and
the literal hole together do not forbid even `K_{4,4}`.

## 5. The global `2p-1` candidate

Statement (G), literally quantified over every positive shift, fails before
CP-SAT is needed.  For

```text
B = {0,2,3,8,12},  h = 4,
B+B = {0,2,3,4,5,6,8,10,11,12,14,15,16,20,24}.
```

All 15 unordered sums are distinct, including the diagonals, while the ten
lower shifted-intersection members are

```text
0,2,4,6,8,10,11,12,16,20.
```

Hence `C_S=10>9=2p-1`.  Exhaustion of every endpoint-normalized Sidon ruler
through width 20 and every relevant shift `1<=h<=2*width` gives

| quantity | value |
|---|---:|
| normalized rulers | 2,342 |
| shifts | 80,032 |
| failures of (G) | 48 |

The same small-width run has zero failures in its 40,016 cases with
`h>diam(B)`.  That does not persist.  A separate exact bitset scan of every
endpoint shift of all 133 P20 rulers gives

| quantity | value |
|---|---:|
| endpoint shifts | 590,650 |
| failures of `C_S<=2p-1` | 122,240 |

The least-order corpus witness is `bose-22e836643a82`:

```text
B = {0,6,13,85,89,121,141,152,196,245,247,257,274,327,345,
     370,404,418,439,444,472,536,558,573,581,582,620,623,639}
(p,h,C_S,2p-1) = (29,640,58,57).
```

All 435 diagonal-inclusive unordered sums are distinct.  Also
`h=640>639=diam(B)`, `max(B)=h-1`, and the P65 defect is positive:

\[
 \delta=(3\cdot29^2-29+2)/2-640=608.
\]

The machine-readable output stores all 58 uniquely labeled folds.  This is
the least-order failure in the 133-ruler P20 endpoint scan, not a global
minimality theorem.

Earlier endpoint gates explain why the candidate looked sharp but do not
survive the larger P20 corpus:

* P53 checks 745,733 rulers and 30,326,669 translations through width 45 with
  zero failures of `C_S<=2p-3`.
* The P53 dense orders 20 through 28 and its exact induced-subset CP-SAT
  optimizations have maximum `C_S-(2p-1)=0`.
* P53 at `p=25` and P75 at `p=26` attain `2p-1` exactly.

Thus both the arbitrary-shift theorem and its endpoint repair

\[
 h>diam(B)\quad\Longrightarrow\quad C_S\le2p-1          \tag{E}
\]

are false.  Consequently no direct translate-intersection proof exists under
only integer Sidonicity and `h>diam(B)`.  The P53/P75 outer graphs already
have many cycles, codegrees 6 and 7, and literal `K_{4,4}`; those failed graph
mechanisms are consistent with the exact `p=29` falsifier.

## 6. Novelty and reproduction

The local Problem 864 literature ledger, the
[Erdos Problems #864 page](https://www.erdosproblems.com/864), and a search
of the primary Sidon-sumset literature, including Erdos--Sarkozy--Sos,
[*On Sum Sets of Sidon Sets, I*](https://doi.org/10.1006/jnth.1994.1040),
did not reveal this inequality or the exact falsifier.  The computation shows
that (E) is false, not merely absent from the searched literature.  A search
of the source id and initial mark prefixes likewise found no prior occurrence
of the `p=29,h=640` fold statement.

From the repository root:

```powershell
python -B problems/864/compute/p79/audit_outer_codegrees.py
python -B problems/864/compute/p79/audit_global_shift_bound.py --max-width 20
python -B problems/864/compute/p79/verify_named_witnesses.py
python -B problems/864/compute/p79/verify_p79_results.py
```

The first command is single-process and uses one CPU worker.  Machine-readable
outputs are

```text
problems/864/compute/p79/outer_codegree_audit.json
problems/864/compute/p79/global_shift_bound_audit.json
problems/864/compute/p79/named_witness_audit.json
```

The P20/P45/P46/P65 input SHA-256 values are embedded in the first output;
the P53/P75 hashes are embedded in the other two.  The final verifier re-hashes
all inputs and reconstructs every extremal and smallest witness.
