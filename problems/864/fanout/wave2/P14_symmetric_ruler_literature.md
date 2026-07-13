# P14 prior-art audit: symmetric rulers, `(3,1)`-sum-free Sidon sets, and `3B-B` holes

## Scope and verdict

This audit concerns the exact construction problem isolated in lane P14.  In
the normalized notation, one seeks integers

```text
Z = {0 = z_0 < z_1 < ... < z_{p-1} = W},   G > 0,
L = G + 2W,
```

such that

```text
D(Z) = {z_j-z_i : i<j}
S(Z) = {z_i+z_j : i<=j}
```

satisfy

```text
Z is Sidon,                         (P14.1)
D(Z) cap (G+S(Z)) is empty.         (P14.2)
```

The target relevant to Erdős Problem 864 is an infinite family with

```text
L/p^2 < 3-delta
```

for one fixed `delta>0` and arbitrarily large `p`.

**Audit verdict.** No verified primary source located in this audit gives an
infinite family satisfying (P14.1)-(P14.2) with `L/p^2 < 3-delta`.  The exact
object has a clean existing vocabulary: it is a **same-parity Sidon set that
is `(3,1)`-sum-free**.  If the set is odd, it is a special case of a
4-independent set.  The closest coefficient-3 statement in that literature
is a conjecture for subsets of cyclic groups, not a theorem or an interval
construction.  Generic `2`-Golomb rulers have much smaller asymptotic
diameter, but they omit the cross-disjointness condition and therefore do not
give admissible sets for Problem 864.

This is a documented prior-art search result, not a proof that no such result
exists under every possible terminology.

## 1. Exact reformulation

Define

```text
H := G + 2Z = {G+2z : z in Z}.
```

Then all elements of `H` have the same parity, `|H|=p`, and

```text
min(H)=G,   max(H)=G+2W=L.
```

The following equivalence is exact.

### Proposition 1 (P14 as a `(3,1)`-sum-free Sidon problem)

For the data above:

1. `Z` is Sidon if and only if `H` is Sidon.
2. `D(Z) cap (G+S(Z))` is empty if and only if `H cap 3H` is empty,
   where repetitions are allowed in `3H`.

Indeed,

```text
G+2z_k = (G+2z_i)+(G+2z_j)+(G+2z_l)
```

is equivalent, after division by two, to

```text
z_k-z_l = G+z_i+z_j.
```

Thus P14 asks for a same-parity set `H` which is simultaneously Sidon and
`(3,1)`-sum-free, while minimizing `max(H)`.

There is an equivalent formulation which is particularly natural for the
ruler and carrier-frequency literature.

### Proposition 2 (joint sum-difference spectrum)

For a finite set `E` of positive integers, let

```text
U(E) = {e_i+e_j : i<=j} union {e_j-e_i : i<j}.
```

Every displayed occurrence in `U(E)` is distinct from every other occurrence
(including across the sum and difference classes) if and only if

```text
E is Sidon,   and   E cap 3E = empty.                 (P14.3)
```

The within-sum condition is exactly Sidonicity. Over the integers,
Sidonicity is equivalent to uniqueness of positive differences: an equality
`e_j-e_i=e_l-e_k` rearranges to `e_j+e_k=e_l+e_i`, and the only trivial
Sidon solution gives the same oriented pair. Finally, a cross collision

```text
e_j-e_i = e_k+e_l
```

is equivalent to

```text
e_j = e_i+e_k+e_l,
```

including all repetitions and diagonal cases. This proves (P14.3).

For the P14 set `E=G+2Z`, all entries have one parity and `max(E)=L`.
Consequently the exact search object can also be described as a
**same-parity ruler whose unordered two-sums and positive differences form
one collision-free spectrum**. No stable primary-source name for that full
joint spectrum was verified. The additive-combinatorics conditions
"Sidon and `(3,1)`-sum-free" or "Sidon and mixed `B(3,1)`" are less
ambiguous.

In the unnormalized reflected-construction notation, the same condition is

```text
M notin 3B-B,   M>2 max(B),
```

with `B` Sidon.  The phrase "a hole in `3B-B`" is therefore exact, but it is
not by itself a standard named ruler class.

If `H` consists of odd integers, parity also gives `H cap 2H = empty`; together
with Sidonicity and positivity, the required low-weight additive relations are
excluded.  This places the odd subcase inside the 4-independent framework of
Bajnok and Ruzsa.  The converse must not be used without checking the ambient
group and parity conditions.

## 2. Closest verified primary literature

### 2.1 Independent sets in abelian groups

B. Bajnok and I. Z. Ruzsa, **The independence number of a subset of an abelian
group**, *Integers* **3** (2003), A02.

- Primary article: <https://www.emis.de/journals/INTEGERS/papers/d2/d2.pdf>
- Author-posted/arXiv version: <https://arxiv.org/abs/1512.03037>
- EuDML record: <https://eudml.org/doc/122918>
- Archival DOI: <https://doi.org/10.5281/zenodo.7596341>

Their exact definition is: a subset `A` of an abelian group is `t`-independent
if every relation

```text
sum_i lambda_i a_i = 0,   sum_i |lambda_i| <= t,
```

is trivial.  They equivalently decompose this into zero-sum-free,
`(h,k)`-sum-free, and generalized Sidon requirements.  In particular, their
notation explicitly includes

```text
hA cap kA = empty
```

as the `(h,k)`-sum-free condition.  Hence `(3,1)`-sum-free is the correct
literature term for `H cap 3H=empty`.

For the cyclic group `Z_n`, their Corollary 3.2 (Corollary 14 in the 2003
typesetting) proves, for every `epsilon,delta>0` and all sufficiently large
`n`,

```text
(1/sqrt(8)-epsilon) sqrt(n) <= s(Z_n,4)
                               <= (1/sqrt(2)+delta) sqrt(n),

(1/sqrt(15)-epsilon) sqrt(n) <= s(Z_n,5)
                                <= (1/sqrt(2)+delta) sqrt(n).
```

Their Conjecture 3.3 (Conjecture 15 in the 2003 typesetting) states

```text
lim_{n->infinity} s(Z_n,4)/sqrt(n) = 1/sqrt(3).
```

This is the closest verified occurrence of the coefficient `3`.  It is not a
known construction with coefficient below `3`: it is a conjecture, it is
modular, and 4-independence is stronger than the exact interval P14 condition.
Modular wraparound also prevents directly identifying the cyclic diameter
parameter with `L`.

### 2.2 Exact extremal size of `(3,1)`-sum-free cyclic sets

B. Bajnok, **On the maximum size of a `(k,l)`-sum-free subset of an abelian
group**, *International Journal of Number Theory* **5** (2009), 953-971.

- Primary preprint: <https://arxiv.org/abs/0803.4486>
- DOI: <https://doi.org/10.1142/S1793042109002481>

Theorem 6 gives the exact formula

```text
lambda_{3,1}(Z_n)
  = max_{d|n, d not congruent to 2 (mod 4)}
      floor((d+2)/4) * n/d.
```

Equivalently, if `n` is divisible by a prime `p=3 (mod 4)`, and `p` is the
smallest such prime, the value is

```text
((p+1)/p) * n/4;
```

otherwise it is `floor(n/4)`.  Consequently

```text
n/5 <= lambda_{3,1}(Z_n) <= n/3,
```

with the stated endpoint cases in the paper.  This theorem imposes no Sidon
condition and optimizes cardinality in a cyclic group rather than span in an
integer interval.  It therefore does not imply a P14 construction.

### 2.3 Counting integer `(k,1)`-sum-free sets

N. J. Calkin and A. C. Taylor, **Counting Sets of Integers, No `k` of Which
Sum to Another**, *Journal of Number Theory* **57** (1996), 323-327.

- Primary repository record and manuscript: <https://repository.gatech.edu/entities/publication/e901762e-cb96-43ca-b08a-1d6acee4df21>
- DOI: <https://doi.org/10.1006/jnth.1996.0051>

For each fixed `k>=3`, they prove that the number of subsets of `[1,n]` with no
solution

```text
x_1+...+x_k=y
```

(repetitions allowed) is at most

```text
c * 2^(((k-1)/k)n)
```

for a constant `c` depending on `k`.  This verifies that `(k,1)`-sum-free is
an established integer-set object, but the theorem neither imposes Sidonicity
nor optimizes the quadratic span of a sparse set.

### 2.4 Sum-free Sidon sets

M. B. Nathanson, **N-graphs, modular Sidon and sum-free sets, and partition
identities**, *Ramanujan Journal* **4** (2000), 59-67.

- Primary manuscript: <https://www.theoryofnumbers.com/melnathanson/pdfs/nath2000-97.pdf>
- arXiv: <https://arxiv.org/abs/math/0002173>
- DOI: <https://doi.org/10.1023/A:1009830023023>

Nathanson defines a sum-free Sidon set `S` by the conjunction

```text
S cap 2S = empty
```

and uniqueness of unordered two-term sums; a modular analogue is also
defined.  The paper derives partition identities from such sets.  P14 instead
needs `H cap 3H=empty`.  For odd `H`, ordinary sum-freeness is automatic by
parity, so this literature does not supply the missing three-sum exclusion.

### 2.5 Sidon bibliography used for terminology and citation tracing

K. O'Bryant, **A Complete Annotated Bibliography of Work Related to Sidon
Sequences**, *Electronic Journal of Combinatorics*, Dynamic Survey DS11
(2004), 39 pp.

- Primary survey page: <https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS11>
- Author PDF: <https://www.math.csi.cuny.edu/~obryant/Mathematician/Papers/SidonBib/Sidon.pdf>
- DOI: <https://doi.org/10.37236/32>

This was used as a primary bibliographic corpus and for backward citation
tracing.  Its failure to list an exact P14 construction is evidence about the
searched vocabulary, not a proof of nonexistence.
### 2.6 Mixed Sidon sets: the exact unequal-sum equation

A. Godbole, C. M. Lim, V. Lyzinski, and N. G. Triantafillou,
**Sharp Threshold Asymptotics for the Emergence of Additive Bases**,
*Integers* **13** (2013), A14.

- Published primary PDF: <https://math.colgate.edu/~integers/n14/n14.pdf>
- arXiv article: <https://arxiv.org/abs/1110.1745>
- Book reprint DOI: <https://doi.org/10.1515/9783110298161.195>
- Author-uploaded extended manuscript containing Definition 18 and Theorem
  19: <https://www.researchgate.net/publication/51943738_Sharp_Threshold_Asymptotics_for_the_Emergence_of_Additive_Bases>
- AMS Joint Mathematics Meetings abstract, **Random Additive Bases and Mixed
  Sidon Sets**: <https://jointmathematicsmeetings.org/amsmtgs/2138_abstracts/1077-60-2208.pdf>

The author-uploaded extension uses the exact unequal-length terminology. For
unequal positive `h,k`, `A` is an `(h,k)`-Sidon set, or `B(h,k)`, when

```text
a_1+...+a_h = b_1+...+b_k
```

has no solution with all variables in `A`. For `h=k`, permutation-equal
multisets are the trivial solutions and the definition recovers an ordinary
`B_h` set.

Its Theorem 19 forms a binomial random subset of `[n]`, selecting each
integer with probability

```text
p = A_n / n^((h+k-1)/(h+k)),
```

and proves

```text
P(A is B(h,k)) -> 0 if A_n -> infinity,
P(A is B(h,k)) -> 1 if A_n -> 0.
```

Thus `B(3,1)` is exactly `E cap 3E=empty`. Here `np=A_n n^(1/4)`, so
the high-probability half of the random theorem has expected cardinality
`o(n^(1/4))`. Intersecting that property with ordinary `B_2` therefore does
not approach the required quadratic regime `|E| asymptotic sqrt(n)`.

Bibliographic caution is necessary. The mixed-Sidon section and numbering
above occur in the author-uploaded extended manuscript and are corroborated
by the primary AMS meeting abstract; the shorter arXiv/published *Integers*
text located in this audit does not contain that final section. Also, this
`B(h,k)` notation conflicts with the generalized `B(h,k)` notation of Dias da
Silva and Nathanson, where two *equal-length* `h`-sums must share at least
`k` terms. The latter is not P14:

J. A. Dias da Silva and M. B. Nathanson, **Maximal Sidon sets and matroids**,
*Discrete Mathematics* **309** (2009), 4489-4494,
<https://www.theoryofnumbers.com/melnathanson/pdfs/nath2009-132.pdf>, DOI
<https://doi.org/10.1016/j.disc.2009.02.009>.

A separate terminology trap is the phrase `3-sum-free`. In a substantial
primary literature it means absence of `x+y=3z`, not absence of
`x+y+z=w`; see A. Plagne and A. de Roton, **Maximal sets with no solution
to x+y=3z**, <https://arxiv.org/abs/1211.3341>. The unambiguous P14 phrases
are `(3,1)`-sum-free, mixed `B(3,1)`, or `E cap 3E=empty`.

## 3. Ruler terminology: verified false friends

### 3.1 Ordinary symmetric Golomb rulers

An ordinary normalized Golomb ruler cannot be centrally symmetric except in
the trivial two-mark case.  If marks include `0,L,x,L-x`, then the distance
`x` occurs both as `(0,x)` and `(L-x,L)`.  If `x=L/2`, the same distance occurs
as `(0,x)` and `(x,L)`.  Thus the reflected P14 construction is deliberately
not an ordinary symmetric Golomb ruler.

In computational ruler usage, a "mirror ruler" usually means that a ruler
`R` and its reflection `L-R` are equivalent solutions; it does not mean their
union is Golomb.

K. Drakakis, **A review of the available construction methods for Golomb
rulers**, *Advances in Mathematics of Communications* **3** (2009), 235-250.

- Primary article: <https://www.aimsciences.org/article/doi/10.3934/amc.2009.3.235>
- DOI: <https://doi.org/10.3934/amc.2009.3.235>

The review's "symmetric Golomb Costas arrays" are two-dimensional Costas
arrays whose diagonals yield ordinary Bose-Chowla rulers.  The symmetry is a
property of the array, not reflection closure of a one-dimensional mark set.

### 3.2 Golomb birulers and symmetric 2-configurations

H. Gropp, **On Golomb birulers and their applications**, *Mathematica
Slovaca* **42** (1992), 517-529.

- Primary PDF: <https://dml.cz/bitstream/handle/10338.dmlcz/136566/MathSlov_42-1992-5_1.pdf>
- EuDML: <https://eudml.org/doc/34348>
- DOI: none located in the primary records audited.

Definition 3.1 calls a list of `S` positive gaps summing to `L` a biruler when
no integer occurs more than twice as a sum of consecutive gaps.  A perfect
biruler attains the elementary counting lower bound; Theorem 3.2 proves that
no perfect biruler exists for `S>5`; Definition 3.3 calls a minimum-length
biruler a Golomb biruler.

This is essentially a difference-multiplicity-at-most-two condition.  It does
not say that the repeated differences all arise from one reflected sum, and
it does not impose `D(Z) cap (G+S(Z))=empty`.

Gropp's "symmetric 2-configuration" is a design with equally many points and
lines, regular incidence, and pair codegree at most two.  Here "symmetric"
means equal point and line counts, not geometric reflection.

### 3.3 General `g`-Golomb rulers

Y. Caicedo, C. Martos, and C. Trujillo, **`g`-Golomb Rulers**, *Revista
Integracion* **33** (2015), 161-172.

- Primary PDF: <https://dialnet.unirioja.es/descarga/articulo/5752612.pdf>
- DOI: <https://doi.org/10.18273/revint.v33n2-2015006>

A `g`-Golomb ruler permits every positive difference at most `g` times.  For
the minimum diameter `G(g,m)` of an `m`-mark ruler, the paper proves

```text
lim_{m->infinity} G(g,m)/m^2 = 1/g.
```

Thus generic `2`-Golomb rulers have coefficient `1/2`, far below `3`.  This is
not a counterexample to the P14 barrier: a generic `2`-Golomb ruler need not
have one exceptional sum, reflection pairing, same parity in the transformed
set, or disjointness between differences and shifted full sums (including
diagonal sums).

C. A. Martos Ojeda, D. F. Daza Urbano, and C. A. Trujillo Solarte,
**Near-Optimal `g`-Golomb Rulers**, *IEEE Access* **9** (2021), 65482-65489.

- DOI: <https://doi.org/10.1109/ACCESS.2021.3075877>

This paper supplies finite near-optimal constructions in the same broad
difference-multiplicity class.  It does not add the P14 cross-disjointness
condition.  Recent modular/high-multiplicity work, including
<https://arxiv.org/abs/2607.07931> and <https://arxiv.org/abs/2605.14229>, has
the same mismatch.

### 3.4 Perfect and near-perfect rulers

For an ordinary Golomb ruler, "perfect" means that the distinct positive
differences are exactly all integers from `1` through its length.  The
classical result is that perfect rulers have at most four marks.

S. W. Golomb, **How to Number a Graph**, in *Graph Theory and Computing*,
Academic Press, 1972, pp. 23-37.

- Accessible exposition/source: <https://www.cs.toronto.edu/~apostol/golomb/main.pdf>
- DOI: none located for the chapter.

"Near-perfect" is not a stable exact name for P14 in the primary ruler
sources audited.  "Near-optimal" normally means diameter close to the optimum
within the same ordinary or `g`-Golomb class.  Gropp's perfect biruler is a
different counting-equality notion.  None controls `D(Z)` against `G+S(Z)`.

### 3.5 Disjoint Golomb rulers and difference triangle sets

J. B. Shearer, **Some New Disjoint Golomb Rulers**, *IEEE Transactions on
Information Theory* **44** (1998), 3151-3153.

- Primary IBM record: <https://research.ibm.com/publications/some-new-disjoint-golomb-rulers>
- DOI: <https://doi.org/10.1109/18.737546>

Here "disjoint" means several ordinary rulers have pairwise disjoint mark
sets.  In difference triangle sets, internal differences across several
rulers are required to be mutually distinct.  Neither notion asks that one
ruler's difference set avoid a translate of its full two-sum set.  The phrase
"disjoint difference and shifted-sum sets" did not lead to a verified standard
named class beyond the exact P14 formulation.

## 4. Graceful labelings with reflection: verified false friends

H. J. Broersma and C. Hoede, **Another Equivalent of the Graceful Tree
Conjecture**, *Ars Combinatoria* **51** (1999), 183-192.

- Journal/archive record: <https://combinatorialpress.com/ars-articles/volume-051-ars-articles/another-equivalent-of-the-graceful-tree-conjecture/>
- DOI: none located in the primary records audited.

A tree with a perfect matching is strongly graceful if it has a graceful
labeling `f` satisfying

```text
f(u)+f(v)=n-1
```

on every matching edge.  The paper proves that every tree is graceful if and
only if every tree with a perfect matching is strongly graceful.  This is a
genuine reflection-pair condition, but uniqueness is required only for labels
of the tree's edges.  P14 needs uniqueness/collision control for all unordered
pairs, including diagonals, so the theorem does not construct the required
complete-ruler object.

J. Pereira, T. Singh, and S. Arumugam, **Additively graceful signed graphs**,
*AKCE International Journal of Graphs and Combinatorics* **20** (2023),
300-307.

- Primary PDF: <https://www.tandfonline.com/doi/pdf/10.1080/09728600.2023.2243619>
- DOI: <https://doi.org/10.1080/09728600.2023.2243619>

Positive edges receive difference labels and negative edges receive sum
labels, but the two sign classes have prescribed label ranges and collisions
are checked only on graph edges.  Simple graphs also omit the diagonal sums
`2a`.  This is not disjointness of the complete difference and shifted-sum
spectra.

## 5. "Signed Sidon" and linear-form Sidon terminology

M. B. Nathanson, **Sidon sets for linear forms**, arXiv:2101.01034.

- Primary preprint: <https://arxiv.org/abs/2101.01034>

For a linear form `phi`, a `phi`-Sidon set makes `phi` injective on all input
tuples.  Nathanson proves that infinite `phi`-Sidon sets exist precisely when
the coefficient set of `phi` has property N (distinct subset sums).

This framework is stronger than P14.  Encoding `3H-H` by the form with
coefficients `(1,1,1,-1)` repeats the coefficient `1`, so property N fails.
P14 only excludes the value zero for this form; it does not demand injectivity
of all four-variable outputs.  Consequently linear-form Sidon theorems do not
produce the desired family.

No stable primary-source use of "signed Sidon sequence" for the exact P14
object was verified in this audit.  "Signed sumset" is a standard but much
broader phrase for expressions such as `epsilon_1 A+...+epsilon_h A`; it does
not encode the Sidon and one-hole requirements.

## 6. The `3B-B` hole audit

The exact reflected criterion is

```text
B is Sidon,
M > 2 max(B),
M notin 3B-B.
```

The searched primary literature around maximal Sidon sets, Sidon sumsets, and
asymptotic Sidon bases frequently studies coverage by `B+B-B`, density of
`B+B`, or coverage by `hB`.  Those are not interchangeable with a controlled
hole in `3B-B` below a quadratic threshold.

Nearby primary examples include:

1. P. Erdos, A. Sarkozy, and V. T. Sos, **On Sum Sets of Sidon Sets I**,
   *Journal of Number Theory* **47** (1994), DOI
   <https://doi.org/10.1006/jnth.1994.1040>.
2. P. Erdos, A. Sarkozy, and V. T. Sos, **On Sum Sets of Sidon Sets II**,
   *Israel Journal of Mathematics* **90** (1995), DOI
   <https://doi.org/10.1007/BF02783214>.
3. S. Z. Kiss and C. Sandor, **Dense sumsets of Sidon sequences**,
   *European Journal of Combinatorics* **107** (2023), 103600, DOI
   <https://doi.org/10.1016/j.ejc.2022.103600>.

These results address sumset density/coverage, not the existence of a Sidon
set `B` with a prescribed-size center `M` outside `3B-B`.  No theorem in the
audited primary corpus yields, uniformly for arbitrarily large `p`,

```text
M/p^2 < 3-delta
```

under the exact reflected admissibility constraints.

## 7. False-friend classification

| Literature object | Verified condition | Why it does not settle P14 |
|---|---|---|
| Same-parity Sidon + `(3,1)`-sum-free | Exactly `H` Sidon and `H cap 3H=empty` | This is the exact object; no verified `<3` infinite family was located |
| Mixed `(3,1)`-Sidon / `B(3,1)` in Godbole et al. | No three-term sum equals a one-term sum | Exact second half of P14, but their random theorem has only `n^(1/4)` scale and omits the simultaneous sharp Sidon construction |
| 4-independent set in `Z_n` | Excludes every nontrivial relation of weight at most 4 | Modular and stronger; coefficient `3` is conjectural, not proved |
| Sum-free Sidon set | Sidon plus `H cap 2H=empty` | Misses `H cap 3H=empty` |
| Ordinary symmetric Golomb ruler | Reflection-closed ordinary Golomb marks | Nontrivial examples are impossible |
| `2`-Golomb ruler / biruler | Every positive difference occurs at most twice | Does not force one reflected collision class or cross-disjointness |
| Distinct difference set | All nonzero differences distinct, equivalently off-diagonal sums distinct | Does not compare differences with shifted sums and omits diagonals |
| Disjoint Golomb rulers | Several rulers have disjoint mark sets | "Disjoint" does not concern difference versus sum spectra |
| Difference triangle set | Internal differences across rulers are distinct | No shifted-sum avoidance |
| Strongly graceful labeling | Matched labels sum to one reflection center | Controls only graph edges, not every unordered pair |
| Additively graceful signed graph | Edge labels use differences or sums by sign | Separate edge classes; no complete cross-disjointness or diagonals |
| `phi`-Sidon set | A linear form is injective on all tuples | Much stronger; `(1,1,1,-1)` fails the coefficient criterion |
| `B_3` set / fifth-order carrier assignment | Every unordered triple sum is unique | Stronger than P14 and known constructions have cubic, not quadratic, span |
| Perfect / near-optimal ruler | Difference spectrum is complete or diameter is near class optimum | No `D(Z)` versus `G+S(Z)` constraint |

## 8. Additional verified distinct-sums source

M. D. Atkinson, N. Santoro, and J. Urrutia, **Integer Sets with Distinct Sums
and Differences and Carrier Frequency Assignments for Nonlinear Repeaters**,
*IEEE Transactions on Communications* **34** (1986), 614-617.

- Primary PDF: <https://people.scs.carleton.ca/~santoro/Reports/DistinctSums.pdf>
- DOI: <https://doi.org/10.1109/TCOM.1986.1096587>

The paper treats two different carrier-interference models and must not be
summarized as only a DDS paper.

For third-order intermodulation, its `k=2` problem asks for all two-term sums
to be distinct. The paper converts this to a distinct difference set (DDS),
because within-class sum uniqueness and within-class nonzero-difference
uniqueness are equivalent. It does **not** require the positive differences
to be disjoint from the two-sums, so this part is still an ordinary DDS false
friend for Proposition 2.

For fifth-order intermodulation, its `k=3` problem requires all unordered
triple sums to be distinct, i.e. a `B_3` set. The finite-field constructions
quoted from Bose-Chowla give respectively

```text
q+1 marks with triple sums distinct modulo q^3+q^2+q+1,
q marks with triple sums distinct modulo q^3-1.
```

The paper consequently obtains integer examples with maximum mark

```text
a_n < n^3+o(n^3),
```

while its Lemma 3 gives the lower bound

```text
a_n > (10/57)n^3
```

for `n+1` nonnegative marks with all triple sums distinct. If zero is one of
the marks, `B_3` certainly implies both Sidonicity and `E cap 3E=empty`, since
`a+b+c=d` would equal the triple sum `d+0+0`. It is therefore a valid but
vastly overconstrained sufficient construction, with cubic rather than
quadratic span. It cannot provide a coefficient below `3` in P14.

The physical terminology also explains the mismatch. Atkinson et al.'s
third-order equation is of the form `a_i+a_j-a_k=a_l`, while the fifth-order
condition is promoted to complete uniqueness of triple sums. The P14 cross
collision is the more specific all-positive relation
`a_i+a_j+a_k=a_l`; neither engineering reduction isolates it together with
only the ordinary Sidon constraints.

## 9. Search protocol and limitations

The audit used the exact phrases and citation chains around:

```text
"symmetric Golomb ruler"
"Golomb biruler"
"symmetric distinct difference"
"distinct sums and differences"
"strongly graceful" reflection matching
"disjoint Golomb ruler"
"difference triangle set"
"perfect ruler" and "near-perfect ruler"
"signed Sidon" and "Sidon sets for linear forms"
"mixed Sidon set", "B(3,1)", and unequal-length Sidon sums
"(3,1)-sum-free" and "no k of which sum to another"
"sum-free Sidon"
"3B-B" Sidon holes / coverage
"4-independent" subsets of cyclic groups
third- and fifth-order carrier-frequency intermodulation
jointly distinct two-sums and positive differences
```

Claims above were recorded only after opening a primary paper, author
manuscript, journal record, or archival full text and checking the operative
definition or theorem.  Search snippets were used only to locate candidates.
The following distinctions were enforced throughout:

1. unordered versus ordered two-sums;
2. inclusion of diagonal pairs `a+a`;
3. a single exceptional sum versus difference multiplicity at most two;
4. interval arithmetic versus modular arithmetic;
5. reflection of an entire mark set versus equivalence to its mirror image;
6. all-pairs Sidonicity versus uniqueness only on graph edges.

The literature is broad and terminology is not canonical.  Accordingly, the
negative conclusion is deliberately limited: **no primary source verified in
this audit establishes the exact P14 infinite family with coefficient below
3**.  The exact reformulation in Proposition 1 should be used for any further
forward/backward citation search; it is substantially less ambiguous than
"symmetric ruler."

## 10. Consequence for the P14 lane

The coefficient-`<3` target is not discharged by known generic ruler
asymptotics.  A valid import from prior art would need one of the following:

1. an integer Sidon set `H` of one parity with `H cap 3H=empty` and
   `max(H)<(3-delta)|H|^2` for infinitely many cardinalities;
2. equivalently, a Sidon set `B` with a center `M notin 3B-B`,
   `M>2 max(B)`, and the corresponding normalized span below
   `(3-delta)|B|^2`;
3. a theorem transferring a modular 4-independent construction to an
   interval without wraparound and without losing the strict coefficient.

None of these was found as a proved theorem.  P14 therefore remains a genuine
construction frontier rather than a renamed solved ruler problem.
