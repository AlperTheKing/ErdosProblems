# P67: triple-block cycle obstruction

## Verdict

Retaining the actual partition of each equal-three-sum fiber does not repair
the P59 pairwise-support route.  There is an explicit infinite family of
valid P37 overlap pairs with two type-111 columns, each partitioned into `q`
blocks, whose supports share `3q-1` marks.  In particular,

\[
 |B_x\cap B_y|=3q-1,
 \qquad q_x+q_y=2q.                                    \tag{1}
\]

Thus every proposed bound

\[
 |B_x\cap B_y|\le q_x+q_y+o(q_x+q_y)                  \tag{2}
\]

is false, even when both fibers contain only all-distinct triples.  The
intersection graph is simple, so the obstruction is not caused by two blocks
sharing two marks.  It is a growing cycle-space obstruction.

This does not rule out a genuinely aggregate inequality coupling three or
more columns at once.  It proves that pairwise ordinary-support coupling,
including any constant or sublinear repair of P59, cannot supply the needed
leading reduction.

## 1. The exact block-intersection graph

Fix distinct balanced columns `x` and `y`.  Let `P_x` and `P_y` be their
actual type-111/type-3 block partitions, let

\[
 q_x=|\mathcal P_x|,\qquad q_y=|\mathcal P_y|,
\]

and let `B_x,B_y` be their support unions.  Form a bipartite multigraph
`J_{x,y}` whose vertices are the blocks in the two columns and whose edges
are the common marks.  Thus a mark in `B_x intersect B_y` joins its unique
`x`-block to its unique `y`-block.

**Lemma P67.1 (one doubled block pair).**  At most one block pair in
`J_{x,y}` has multiplicity two, and no block pair has multiplicity three.

### Proof

Multiplicity three would make the two triples identical and hence give
`x=y`.  Suppose two different block pairs each have multiplicity two.
Orient so `x<y`.  Write the first pair as

\[
 T=P\cup\{c\},\qquad T'=P\cup\{d\},
\]

where `P` is their common two-mark set.  Then

\[
 d-c=y-x>0.                                             \tag{3}
\]

A second doubled pair similarly gives `d'-c'=y-x`.
Positive differences in a Sidon set are unique, so `(c,d)=(c',d')`.
Distinct blocks in one column have disjoint supports, hence the two block
pairs were the same.  QED.

Let `s` be the number of edges in the underlying simple graph, `v` its
number of nonisolated vertices, `c` its number of nonempty components,
`mu=s-v+c` its cycle rank, and `d in {0,1}` its doubled-edge count.  Then the
exact identity is

\[
 \boxed{|B_x\cap B_y|=v-c+\mu+d.}                      \tag{4}
\]

P59 has `mu=d=c=1`, giving `5=4-1+1+1`.  The family below
has `d=0`, `c=1`, and cycle rank growing linearly with `q`.

## 2. Infinite cyclic construction

**Theorem P67.2.**  For every integer `q>=3`, there are a nonnegative integer
Sidon set `Z_q`, an endpoint `W_q=max Z_q`, a positive gap `G_q`, and two
distinct targets `x_q,y_q<=K_q:=W_q-G_q` such that

1. `D^+(Z_q)` is disjoint from `G_q+S_2(Z_q)`;
2. the complete balanced fiber at `x_q` consists of exactly `q` disjoint
   type-111 triples;
3. the complete balanced fiber at `y_q` consists of exactly `q` disjoint
   type-111 triples;
4. both support unions have size `3q`, and their intersection has size
   `3q-1`.

The set has `3q+2` marks, including its final endpoint.

### Formal labels

Work first in the free rational vector space with basis

\[
 X,B,D,C_0,\ldots,C_{q-1},
 \qquad U=C_0+C_{q-1}.                                  \tag{5}
\]

Define

\[
 c_i=C_i\quad(0\le i<q),\qquad b_0=B,                  \tag{6}
\]

and, for `1<=i<q`,

\[
 b_i=B+U-C_{i-1}-C_i-iD,                               \tag{7}
\]

\[
 a_i=X-B-U+C_{i-1}+iD.                                 \tag{8}
\]

Finally put

\[
 \ell=X-B-C_0,
 \qquad \rho=\ell+qD.                                 \tag{9}
\]

There are `3q+1` formal labels.  Partition all labels except `rho` into

\[
 L_0=\{b_0,c_0,\ell\},
 \qquad L_i=\{a_i,b_i,c_i\}\quad(1\le i<q).            \tag{10}
\]

Every block in (10) has sum `X`.  Partition all labels except `ell` into

\[
 R_0=\{b_{q-1},c_{q-2},\rho\},                         \tag{11}
\]

\[
 R_j=\{a_j,b_{j-1},c_{j-2\pmod q}\}
 \quad(1\le j<q).                                      \tag{12}
\]

Every block in (11)--(12) has sum `X+D`.  The two support unions therefore
have `3q-1` common labels.  Their simple intersection graph is the cyclic
3-regular bipartite graph with edge shifts `0,1,2`, with one edge removed
and the two resulting degree-two blocks completed by `ell,rho`.

### Formal Sidonicity

Write `e_i` for the `C_i` coordinate vector and define

\[
 f_0=0,qquad
 f_i=e_0+e_{q-1}-e_{i-1}-e_i\quad(1\le i<q),            \tag{13}
\]

\[
 h_0=h_q=-e_0,qquad
 h_j=-e_0-e_{q-1}+e_{j-1}\quad(1\le j<q).              \tag{14}
\]

The three label families have coefficient profiles

\[
 c_i:(X,B,D,C)=(0,0,0,e_i),                            \tag{15}
\]

\[
 b_i:(X,B,D,C)=(0,1,-i,f_i),                           \tag{16}
\]

\[
 H_j:(X,B,D,C)=(1,-1,j,h_j),                           \tag{17}
\]

where `H_0=ell`, `H_j=a_j` for `1<=j<q`, and `H_q=rho`.

The `(X,B)` coordinates split all unordered pair sums into six disjoint
classes:

\[
 CC,CB,BB,CH,BH,HH.                                    \tag{18}
\]

Inside `CB` and `CH`, the `D` coordinate first recovers the `B` or `H`
index, and the `C` profile then recovers the remaining index.  The other
three checks reduce to

\[
 (i+j,f_i+f_j),qquad(i+j,h_i+h_j),qquad(j-i,f_i+h_j).\tag{19}
\]

Each map in (19) is injective on its natural unordered or ordered domain.
Here is a direct coefficient proof.  For positive `i`, `f_i` is `U` minus
the incidence vector of edge `(i-1,i)` in the path on
`0,...,q-1`.  Sums of two path-edge incidence vectors determine the two
edges, since the path incidence matrix has full column rank.  The only
possible comparison involving `f_0` would require

\[
 U=E_k+E_l-E_j.                                        \tag{20}
\]

For odd `q`, `U` is not in the path incidence span.  For even `q`, its
unique path-edge expansion is

\[
 U=E_1-E_2+E_3-\cdots+E_{q-1}.                         \tag{21}
\]

Equation (20) is therefore impossible for `q>=6`; for `q=4`, the additional
index-sum coordinate would require `2=1+3`.  The case `q=3` is excluded by
the alternating endpoint functional.

For two interior `h` profiles, equality is equality of two sums of unit
vectors and recovers the two indices.  With one endpoint index, the profile
is `-e_0-U+e_{i-1}`; it determines the interior index, and the index-sum
coordinate distinguishes `0` from `q`.  Two endpoint indices are likewise
distinguished by their index sum.

Finally, for `i>0` and `0<j<q`,

\[
 f_i+h_j=-e_{i-1}-e_i+e_{j-1}.                         \tag{22}
\]

Unless `j=i` or `j=i+1`, its two adjacent negative coordinates recover
`i` and its positive coordinate recovers `j`.  In the two cancellation
cases the remaining negative coordinate, together with `j-i`, recovers
both indices.  If `i=0` then `j-i=j` already recovers the pair.  If
`j` is `0` or `q`, the profile is
`e_{q-1}-e_{i-1}-e_i`; its boundary coordinate and `j-i` distinguish all
remaining cases.  This proves injectivity in (19), hence every
diagonal-inclusive formal pair sum is distinct.

### Integer projection

Set

\[
 R=4q+2
\]

and map a coefficient vector `(v_0,...,v_{q+2})` to

\[
 \phi(v)=\sum_{r=0}^{q+2}v_rR^r.                       \tag{23}
\]

Every coordinate in the difference of two formal pair sums has absolute
value at most `4q<R-1`.  Looking at the highest nonzero coordinate shows
that (23) cannot send such a difference to zero.  Thus (23) preserves all
pair-sum inequalities.  Add one common integer to all projected labels so
that their minimum is zero.  This preserves pair-sum uniqueness and shifts
every triple sum by the same amount.  We obtain an integer Sidon core `C_q`
with maximum `L` and the two block partitions above.

There are no additional representations at either target.  Any different
triple with the same sum must have support disjoint from every displayed
triple, by Sidonicity.  The left blocks cover all core labels except `rho`,
and the right blocks cover all except `ell`.  The only possible remaining
support would be a type-3 singleton.  The coefficient vectors
`3rho-X` and `3ell-(X+D)` are nonzero, and the same radix argument preserves
this, so neither singleton occurs.

### Valid endpoint extension

Adjoin

\[
 W=4L+2,qquad G=L+1,qquad K=W-G=3L+1.                \tag{24}
\]

Since `W>2L`, adjoining `W` preserves Sidonicity.  Core differences lie in
`[1,L]`, while differences using `W` lie in `[3L+2,4L+2]`.  On the other
hand,

\[
 G+S_2(C_q)\subseteq[L+1,3L+1],                       \tag{25}
\]

and shifted pair sums involving `W` exceed every positive difference.
Therefore

\[
 D^+(C_q\cup\{W\})\cap(G+S_2(C_q\cup\{W\}))
 =\varnothing.                                         \tag{26}
\]

All core triple sums are at most `3L<K`, while `W>K`, so the two exact
fibers survive unchanged.  This proves Theorem P67.2.

## 3. Exact finite gates

The first audit tested the tempting constant repair

\[
 |B_x\cap B_y|\le q_x+q_y+1.                           \tag{27}
\]

It had zero failures on the three requested test beds:

| data | valid pairs / column pairs | maximum excess over `q_x+q_y` |
|---|---:|---:|
| exhaustive width at most 18 | 6,783 / 1,623 | 0 |
| P59 witness | 1 / 120 | 1 |
| Bose q=128 | 1 / 19,503 | 0 |

The first exact counterexample found by the structural search is

\[
 Z=\{0,2,8,12,17,28,41,42,60,63,177\},
 \quad G=62,
\]

with targets `70,77`.  Each target has three type-111 blocks; their supports
share eight marks, so (27) fails by one.  A four-block witness is

\[
 Z=\{0,2,3,7,15,35,57,73,171,879,974,991,1000,1161\},
 \quad G=87,
\]

with targets `1009,1050`; its two supports share eleven marks, an excess of
three over the eight-block total.

The mixed-radix constructor was checked with integer arithmetic for
`3<=q<=20`; complete triple fibers were independently enumerated through
`q=12`.  The quotient pair-sum signatures were also checked over exact
rationals for `3<=q<=30`.  Every row has intersection excess `q-1` and zero
gap-condition intersection.

Reproduction:

```powershell
python -B problems/864/compute/p67/audit_triple_block_coupling.py --max-width 18
python -B problems/864/compute/p67/search_excess2_core.py --bound 250 --workers 32
python -B problems/864/compute/p67/complete_excess2_core.py --max-endpoint 5000
python -B problems/864/compute/p67/search_q4_excess_core.py --bound 1000 --workers 32
python -B problems/864/compute/p67/complete_q4_core.py --max-endpoint 30000
python -B problems/864/compute/p67/audit_generic_circulant.py --max-q 30
python -B problems/864/compute/p67/construct_circulant_family.py --max-q 20 --fiber-max-q 12
```

## 4. Consequence for the main route

The actual type-111 partition can have almost all of each column support in
common with another column:

\[
 { |B_x\cap B_y|\over |B_x|}
 ={3q-1\over3q}\longrightarrow1.                       \tag{28}
\]

The intersection graph is simple, so counting doubled block pairs or shared
ordered differences does not remove the obstruction.  A proof that reduces
the P51 aggregate by a leading constant must use information that is absent
from a single pair of partitioned fibers, for example simultaneous coupling
of many target sums, a quantitative carry/location constraint, or a global
energy inequality.  Ordinary two-column support intersection is closed.
