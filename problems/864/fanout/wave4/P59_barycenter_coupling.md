# P59: smallest falsifier to block-count barycenter coupling

## Verdict

The natural intersection coupling strong enough to remove a leading third of
the P51 capacity is false, even for maximum-capacity witnesses.  Its smallest
falsifier in cardinality and then width is

\[
 Z=\{0,7,9,12,20,26,30,58\},\qquad G=15,\qquad K=43.       \tag{1}
\]

At the two represented targets `37` and `39`, maximum P51 witnesses are

\[
 A_{37}=\{0,7,9,12,20,26\},
 \qquad
 A_{39}=\{0,7,9,12,20,30\}.                              \tag{2}
\]

Both capacities are six, but the witnesses intersect in five marks.  The
proposed bound is four.  The same ruler also falsifies the partition-aware
version using actual supports at targets `39` and `42`.

## 1. The proposed leading-order coupling

For a P51-feasible barycentric set `A_x`, put

\[
 q_x={|A_x|+2\epsilon_x\over3}.                           \tag{3}
\]

For the actual support `B_x`, this is exactly the number of its type `111`
blocks plus its possible type `3` block.  The concrete proposal was

\[
 \boxed{|A_x\cap A_y|\le q_x+q_y\quad(x\ne y).}           \tag{C}
\]

This would have reduced total capacity by a leading term.  Indeed, choose one
maximizer `A_x` for every nonzero P51 capacity, let

\[
 t=|\{x:\beta_Z(x)>0\}|,
 \quad B=\sum_x\beta_Z(x),
 \quad E=\sum_x\epsilon_x,
\]

and let `d_z` count the chosen sets containing `z`.  Cauchy and (C) would give

\[
 {B^2/p-B\over2}
 \leq\sum_{z\in Z}{d_z\choose2}
 =\sum_{x<y}|A_x\cap A_y|
 \leq{(t-1)(B+2E)\over3}.                                \tag{4}
\]

Consequently

\[
 3B^2-p(2t+1)B-4p(t-1)E\leq0,                            \tag{5}
\]

and hence

\[
 B\leq {p(2t+1)+
 \sqrt{p^2(2t+1)^2+48p(t-1)E}\over6}
 \leq{p(2t+1)\over3}+2E.                                \tag{6}
\]

For `t,E=O(p^2)`, this is `B <= (2/3)pt+O(p^2)`, a leading
one-third reduction from the uncoupled `pt` capacity.  Thus (C) meets the
required strength; (1)--(2) show that it is not true.

## 2. Exact capacity falsifier

Both targets in (2) are represented:

\[
 \mathcal R_{37}=\{(0,7,30)\},
 \qquad
 \mathcal R_{39}=\{(0,9,30),(7,12,20)\}.                 \tag{7}
\]

The two sets in (2) satisfy the P51 constraints with
`epsilon_37=epsilon_39=0`:

\[
 3\sum A_{37}=222=37|A_{37}|,
 \qquad
 3\sum A_{39}=234=39|A_{39}|.                            \tag{8}
\]

Their sizes must be multiples of three.  Since the low ground has seven
marks, the exhibited size six is maximal; hence

\[
 \beta_Z(37)=\beta_Z(39)=6,
 \qquad q_{37}=q_{39}=2.                                 \tag{9}
\]

Nevertheless,

\[
 A_{37}\cap A_{39}=\{0,7,9,12,20\},
 \qquad 5>2+2.                                           \tag{10}
\]

Partition information does not repair the proposal on this ruler.  Exact
triple enumeration also gives

\[
 B_{39}=\{0,7,9,12,20,30\},
 \qquad
 B_{42}=\{0,7,9,12,26,30\},                              \tag{11}
\]

from

\[
 39=0+9+30=7+12+20,
 \qquad
 42=0+12+30=7+9+26.
\]

Thus the actual supports also share five marks while their two block counts
sum to four.

The set in (1) has `36` distinct diagonal-inclusive unordered pair sums and
`28` distinct positive differences.  Direct computation also gives

\[
 D^+(Z)\cap\bigl(15+S_2(Z)\bigr)=\varnothing,             \tag{12}
\]

so `(Z,G)` is a valid overlap pair and both targets lie below `K=43`.

## 3. Minimality

The order is `(p,W,Z lexicographic,G,x,y)`.  First, every feasible `A_x` omits
the endpoint `W`, so when `p<=7` all columns live on at most six marks.  Their
possible positive sizes are `1,3,4,6`, with block counts `1,1,2,2`.

Two size-three sets at distinct barycenters intersect in at most two; a
size-three set meets a size-four or size-six set in at most three; two
size-four sets at distinct barycenters meet in at most three; and a size-four
set meets a size-six set in at most four.  Two size-six sets on at most six
marks are equal, which forces the same barycenter.  Thus (C) cannot fail for
`p<=7`.

For `p=8`, the width-first verifier generates every endpoint-normalized ruler
by adjoining marks only when all new internal and endpoint differences are
unused.  At every represented target below `W`, it enumerates all `127`
nonempty subsets of the seven low marks and retains exactly those satisfying
P51's barycenter, residue, range, and central-singleton conditions.  It tests
every retained cross-column pair against (C), then every eligible gap by
(12).  It examined `2,005,269` endpoint Sidon rulers before reaching (1); no
admissible failure has smaller width, and the recursive order makes (1) the
first ruler at width `58` having one.

## 4. Requested computations

The exhaustive width-18 census contains `1,340` endpoint Sidon rulers,
`6,783` valid pairs, and `15,049` actual cross-column pairs.  Its maximum
ordinary intersection is two, and (C) has no failure among the selected
maximum witnesses.  The stored Bose `q=128` case has `284` represented
columns and `40,186` actual column pairs; its maximum ordinary intersection
is three, and (C) has no actual-support failure.

The unpartitioned P51 relaxation fails earlier inside the same `q=128` data.
The selected maximum witnesses for `x=2187` and `y=2609` are

\[
 \{0,422,494,684,893,1881\},
 \quad
 \{0,422,494,684,1737,1881\}.                            \tag{13}
\]

They are maximum feasible size-six barycentric sets, share five marks, and
violate (C) by one.  Among the `28,203` pairs of selected nonzero-capacity
witnesses, there are `1,294` violations.

For comparison, both shifted restrictions

\[
 |(x-A_x)\cap(y-A_y)|\leq1,
 \qquad
 |(3A_x-x)\cap(3A_y-y)|\leq1                             \tag{14}
\]

hold in the requested data.  They also hold for arbitrary subsets of the
Sidon set by uniqueness of a nonzero ordered difference, so independently
chosen P51 maximizers already satisfy them.  They therefore do not reduce
`sum beta_Z(x)`.

## 5. Reproduction

The standalone certificate is generated by

```powershell
python -B problems/864/compute/p59/verify_smallest_falsifier.py
```

The width-first minimality search is reproduced by

```powershell
g++ -std=c++20 -O3 -DNDEBUG `
  problems/864/compute/p59/search_intersection_falsifier.cpp `
  -o problems/864/compute/p59/search_intersection_falsifier.exe
problems/864/compute/p59/search_intersection_falsifier.exe --max-width 58
```

The requested width-18 and `q=128` audit is reproduced by

```powershell
python -B problems/864/compute/p59/probe_barycenter_coupling.py `
  --max-width 18
```
