# P51: integer barycenters of equal-three-sum partitions

## Verdict

There is an exact integer restriction that is absent from the translate-block
degree bound.  At a fixed triple sum, remove the representations having
multiplicity pattern `21`.  The union of every remaining support has exact
barycenter one third of the common sum.  Its cardinality also lies in one
specified residue class modulo `3`.

This gives an exact subset-sum capacity for every translate-block column.  On
the stored Bose `q=128` witness it replaces the coarse capacity `36,068` by
`1,685`; the actual incidence is `791`.  On all valid overlap pairs through
width `18`, the new capacity is exact: both totals are `20,134`, versus
`41,719` for the coarse capacity.

The first conjecture suggested by the small census is false.  The smallest
falsifier in cardinality and then width is preserved in
`problems/864/compute/p51/smallest_all_distinct_falsifier.json`.

## 1. Equal-sum notation

Put

\[
 K=W-G>0
\]

and, for `0 <= x <= K`, let

\[
 \mathcal R_x=
 \{(a,b,c)\in Z^3:a\leq b\leq c,\ a+b+c=x\}.
\]

For a triple `T`, write `supp(T)` for its set of distinct entries.  If two
different members of `R_x` shared an entry, cancellation would give two
different unordered pair representations of the same sum.  Sidonicity
therefore gives

\[
 \operatorname{supp}(T)\cap\operatorname{supp}(T')=\varnothing
 \quad(T\ne T').                                      \tag{1}
\]

Split the representations into the three multiplicity types

\[
 111,\qquad 21,\qquad 3.
\]

Let `U_x` be the union of all supports and put `r_x=|U_x|`.  Let `B_x`
be the union of supports of types `111` and `3`, put `b_x=|B_x|`, and let
`d_x` be the number of type `21` representations.  In a type `21`
representation write `(a,a,b)` with `a` the repeated entry, irrespective of
the increasing display order, and define

\[
 \Delta_x=\sum_{(a,a,b)\in\mathcal R_x}(a-b).          \tag{2}
\]

## 2. Integer barycenter-defect lemma

**Lemma P51.1.**  With the notation above,

\[
 \boxed{r_x=b_x+2d_x,}                                \tag{3}
\]

\[
 \boxed{x r_x-3\sum_{u\in U_x}u=\Delta_x,}            \tag{4}
\]

and

\[
 \boxed{3\sum_{u\in B_x}u=x b_x.}                    \tag{5}
\]

Define

\[
 \epsilon_x=
 \begin{cases}
 1,&3\mid x\text{ and }x/3\in Z,\\
 0,&\text{otherwise}.
 \end{cases}
\]

Then

\[
 b_x\equiv\epsilon_x\pmod 3,                          \tag{6}
\]

and `epsilon_x=1` implies `x/3 in B_x`.

### Proof

Disjointness (1) permits addition representation by representation.  A type
`111` block contributes support size `3`, support sum `x`, and zero to (4).
A type `3` block is `(a,a,a)`, so `x=3a`; it contributes support size `1`,
support sum `x/3`, and again zero to (4).  A type `21` block `(a,a,b)`
contributes support size `2` and

\[
 2x-3(a+b)=2(2a+b)-3(a+b)=a-b.                        \tag{7}
\]

This proves (3)--(5).  Every type `111` block contributes three elements to
`B_x`.  There is exactly one type `3` block precisely when `epsilon_x=1`,
and its support is `{x/3}`.  This proves (6).  QED.

The integer content can also be displayed by the affine set

\[
 \widetilde B_x=\{3u-x:u\in B_x\}.                    \tag{8}
\]

It is Sidon, every member is congruent to `-x (mod 3)`, and

\[
 \sum_{v\in\widetilde B_x}v=0.                        \tag{9}
\]

Thus a high-degree column contains a large literal zero-sum Sidon subset; it
is not merely a large subset of an interval.

## 3. Exact column capacity

For every represented `x`, define the relaxed integer capacity

\[
 \beta_Z(x)=\max |B|,                                  \tag{10}
\]

where the maximum is over `B subseteq Z intersect [0,x]` satisfying

\[
 3\sum_{u\in B}u=x|B|,\qquad |B|\equiv\epsilon_x\pmod3, \tag{11}
\]

and, when `epsilon_x=1`, also `x/3 in B`.  An empty feasible family has
capacity zero.  Lemma P51.1 gives

\[
                         b_x\leq\beta_Z(x).             \tag{12}
\]

Let `T_K` be the represented triple sums at most `K`, and put

\[
 D_Z(K)=|\{(a,b)\in Z^2:a\ne b,\ 2a+b\leq K\}|.       \tag{13}
\]

Finally let `S_2(Z)` contain each unordered pair sum once and define the
translate incidence

\[
 I_Z(K)=|\{(z,s)\in Z\times S_2(Z):z+s\leq K\}|.      \tag{14}
\]

Each representation contributes one incidence for every distinct entry in
its support.  Also, every type `21` representation has a unique repeated
entry and singleton, so its total count over `x <= K` is exactly `D_Z(K)`.
Equations (3) and (12) therefore give the new exact inequality

\[
 \boxed{
 I_Z(K)=\sum_{x\in T_K}r_x
 \leq\sum_{x\in T_K}\beta_Z(x)+2D_Z(K).
 }                                                       \tag{15}
\]

This is a subset-sum and congruence constraint.  It does not follow by
assigning a real capacity to each endpoint interval.

## 4. Asymptotic structural consequence

The double exception in (15) is lower order:

\[
                         2D_Z(K)\leq2p(p-1).            \tag{16}
\]

Consequently, if `K=O(p^2)` and `I_Z(K) >= c p^3` for fixed `c>0`, then
(15) forces a linearly large set of the form (8) for at least one common
sum.  More quantitatively,

\[
 \max_{x\in T_K}\beta_Z(x)
 \geq {I_Z(K)-2p(p-1)\over K+1}.                       \tag{17}
\]

There is a clean specialization in the near-minimal ruler regime.  Suppose
`W=(1+o(1))p^2` and `K/W -> kappa` for fixed `0<kappa<=1`.  The dense-Sidon
interval equidistribution theorem already audited in `L04` makes the
normalized counting measure of `Z` uniform.  The simplex

\[
 \{(u,v,w)\in[0,1]^3:u+v+w\leq\kappa\}
\]

has volume `kappa^3/6`.  Removing repeated coordinates and unordered
overcounting gives

\[
 I_Z(K)=\left({\kappa^3\over12}+o(1)\right)p^3.        \tag{18}
\]

Hence (15) forces

\[
 \sum_{x\in T_K}\beta_Z(x)
 \geq\left({\kappa^3\over12}+o(1)\right)p^3,          \tag{19}
\]

and some `x` has

\[
 \beta_Z(x)\geq\left({\kappa^2\over12}+o(1)\right)p. \tag{20}
\]

In fact, thresholding (19) at `kappa^2 p/24` shows that
`Omega_kappa(p^2)` different sums have a linear-size feasible set in
(10).  Thus any fixed overlap in this regime requires not one accidental
six-term relation but quadratically many large exact barycentric subsets.

This is the advance supplied by the lemma.  The remaining load-bearing step
is to couple these zero-sum subsets across different values of `x`, or to
retain their actual partition into zero-sum triples.  A scalar bound on
`beta_Z(x)` alone is still a relaxation.

## 5. Exact tests

The verifier reads the stored P37 witnesses rather than copying them.  Its
integer-only results are:

1. The 13 stored witnesses for `2 <= p <= 14` and the degree-sharp witness
   all satisfy (3)--(15).  In every one, the capacity in (15) equals the
   actual incidence.
2. Exhaustion through width `18` finds `1,340` endpoint-normalized Sidon
   rulers and `6,783` valid overlap pairs.  Across `13,747` represented
   targets and `13,836` triple representations, all identities pass.  There
   are `89` collision targets.  The exact aggregate capacity is `20,134`,
   equal to the actual incidence; the old aggregate capacity is `41,719`.
3. The stored Bose `q=128` witness has `K=3,630`, `21` low marks, `284`
   represented targets, and `302` representations.  Exactly `18` targets
   collide, including three with two all-distinct representations.  Testing
   all `2^21-1=2,097,151` low-mark subsets gives balanced capacity `1,483`;
   the type `21` contribution is `202`, so (15) gives `1,685`.  The actual
   incidence is `791`, while the old column cap gives `36,068`.

The certificate is

```text
problems/864/compute/p51/audit_results.json
```

and is reproduced by

```text
python -B problems/864/compute/p51/audit_equal_three_sum_partition.py \
  --max-width 18 --falsifier-max-width 44
```

## 6. Smallest falsifier to the first conjecture

The width-18 census suggested:

> Every low equal-three-sum collision in a valid pair contains a repeated
> summand.

The stored `q=128` witness already refutes this, for example

\[
 2670=0+494+2176=684+872+1114.                         \tag{21}
\]

The smallest falsifier in cardinality and then width is

\[
 Z=\{0,1,5,11,13,20,44\},\qquad G=16,\qquad K=28.     \tag{22}
\]

It is Sidon, with `28` distinct unordered pair sums and `21` distinct
positive differences, and

\[
 D^+(Z)\cap(16+S_2(Z))=\varnothing.                    \tag{23}
\]

Nevertheless,

\[
                  25=0+5+20=1+11+13.                  \tag{24}
\]

Both triples are all-distinct and their six supports are disjoint.  In the
same-parity coordinates,

\[
 E=\{16,18,26,38,42,56,104\},
\]

and the corresponding collision is

\[
                  98=16+26+56=18+38+42,
\]

while the exact audit gives `E intersect 3E = empty`.

Two all-distinct representations require six support marks, and the endpoint
`W` cannot occur because `x<K<W`; hence `p>=7`.  The verifier exhausts all
`6,129,150` possible six-mark prefixes of seven-mark rulers through width
`44`, in increasing width and lexicographic order, and then every eligible
`G`.  This proves the stated `(p,W)` minimality and preserves the complete
certificate separately.
