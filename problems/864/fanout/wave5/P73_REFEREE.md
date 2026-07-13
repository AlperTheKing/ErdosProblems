# Referee report on P73

## Verdict

**Rejected as written, with a fully repairable certification defect.**

The mathematical claims audited here are correct: the three-layer identity,
Lemma P73.2, the set of 45 exceptional triples, the reduction to 35 nonempty
boxes after the span-55 census, and the terminal span 567 all survive
independent exact checks.  However, the displayed Python checker does not run
successfully: its `bad` list is generated in a different order from the list
on the right side of its final assertion.  It therefore raises
`AssertionError`.  It also prints nothing, contrary to the sentence preceding
it.

There are two further presentation gaps.  The cutoff proof for `p < 100` and
`u < 500` is asserted only through asymptotic notation and an undisplayed
"direct expansion", and the endpoint normalization needed for the definition
of `h_S` is not explicit.  Exact repairs for both are given below.  With those
repairs and the checker correction, I would accept the finite reduction.

## 1. Three-layer identity

Write `q=p+u`.  Since `F` is symmetric under `x -> sigma-x`, its sum and
positive-difference supports satisfy

`|F+F| = 1 + 2|D^+(F)| = 1 + 2q(q+delta) - 2 beta`.

The layers in P73 have the exact sizes

`|C| = 2p(p+delta)+1`,

`|T| = cu+binom(u+1,2)`,

`|J| = |T|`,

`|K| = u(u-1)`.

The last equality follows because every positive difference represented by a
pair touching `R` is unique; hence the ordered nonzero differences `r-r'` are
all distinct.  Direct expansion gives

`|C|+2|T|+|K| = 1+2q(q+delta)`.

The endpoint-type decomposition also gives exactly

`F+F = C union T union J union K`.

Subtracting the union size from the sum of the layer sizes proves (6).  Adding
`J` to `S=C disjoint_union T` and then adding `K` gives

`2 beta = |J intersect S| + |K intersect (S union J)|`.

I independently enumerated all 262,143 endpoint-normalized subsets through
span 18.  There were 3,204 sets with one repeated sum and 3,008 with nonempty
residual.  Rebuilding `C,T,J,K,F+F,D^+(F),beta` from the sets verified (4),
(5), (6), and `|K|=u(u-1)` on all 3,008 records.

**Finding:** Lemma P73.1 is accepted.

## 2. Weighted difference lemma

For a sorted multiset of `m` positive integers with multiplicity at most two
and total excess at most `e`, the vector `b(m,e)` is a coordinatewise lower
bound.  This remains true when `e` is truncated at `floor(m/2)`, the largest
possible excess under multiplicity two.  Consequently the selected
short-difference multiset has sum at least `Q(M_{n,h},e)`.

For the consecutive gaps, let `g_(1)<=...<=g_(n-1)` denote their sorted
values.  Rearrangement and the same coordinatewise bound give

`sum_t lambda_t g_t <= sum_j lambda_(j) g_(j)`

`<= W(n,h,e) + C_{n,h}(L-Q(n-1,e))`.

Thus (15) is valid; combining it with the lower bound and taking the ceiling
proves (12)-(13).  The proof does not assume that the duplicated gap labels
are the smallest labels: that possibility is used only to form a universal
coordinatewise baseline.

As a consistency check, I compared an independent closed-form evaluator of
all `lambda_t` with the submitted nested loops for every `2<=n<=24` and
`0<=e<20`; all values of `G(n,e)` agreed.  I also enumerated 10,958 normalized
integer sets of size at most seven and span at most 18 whose difference
multiplicities are at most two.  Every set satisfied
`span(B)>=G(n,e)` for its exact excess `e`.

The whole-set excess in (16) is correct:

`binom(2p+delta,2)-p(p+delta)=p(p+delta-1)`.

The Sidon witness in (18) also has the claimed size `u+p+1`: for `delta=0`
one exceptional pair is retained in full, while for `delta=1` only the
midpoint representation is retained.

**Finding:** Lemma P73.2 and its applications (17)-(19) are accepted.

## 3. Parameter calculation and its tail

From `beta<=binom(u+1,2)` and (3), the target follows whenever

`L >= R = p(p+delta)+cu/2+3u(u+1)/4`.

An independent exact evaluator of (7)-(12), using integer numerators for
`R`, found precisely the following 45 triples as a set:

`(1,1,u), 2<=u<=26`;

`(2,0,u), 4<=u<=17`;

`(2,1,u), 6<=u<=11`.

The hard cutoffs in the submitted loop can be certified as follows.  Put
`s=u+p+1`.  The ordinary short-difference choice
`h=floor(sqrt(s))` implies

`G(s,0) >= s^2-3s^(3/2)`

for the tail under discussion.  Indeed, for this `h`, one has
`C_{s,h}<=h(h+1)/2` and `W<=C_{s,h}Q(s-1,0)`, so (12) dominates the usual
bound `M(M+1)/(h(h+1))`; the stated estimate is its elementary
`h=floor(sqrt(s))` simplification.

In the complementary P61 range, `u>=2c-4`.  In either cutoff tail
`u>=500` or `p>=100`, this implies `s<=3u/2`.  Moreover

`s^2-R = (u^2+4pu+5u+8p+4)/4` when `delta=0`,

`s^2-R = (u^2+4pu+3u+4p+4)/4` when `delta=1`.

Hence `s^2-R>=u^2/4`.  For `u>=500`, the required comparison follows from

`(u^2/4)^2 >= 9(3u/2)^3`,

which is equivalent to `u>=486`.  If instead `p>=100` and `u<500`, then
`s^2-R>=u^2/4+100u`; after squaring, the sufficient comparison is

`(u+400)^2 >= 486u`,

whose difference is `u^2+314u+160000>0`.  Thus the exact loop domain
`p<100,u<500` really does cover every case not eliminated analytically.

**Gap in P73:** the displayed `n^2-O(n^(3/2))` statement alone does not
certify either numerical cutoff.  The preceding inequalities, or an
equivalent explicit tail proof, must be inserted.

## 4. The 35 boxes and span 567

I rebuilt and reran
`compute/p66/exhaustive_completion_charge.cpp` with `--max-span 55` and
`--threads 55`.  Exact integer enumeration returned 35,776,005 admissible
sets, 30,899,206 nonempty-residual records, 18,800,840 records outside the
P61 range, and zero failures of `2beta<=h_S`.  The output SHA-256 was
`E43CFDE622517C106265C47F01FF9486D4CA8817DDFAB910365401568A19F83A`.

The census removes the exceptional triples whose upper span bound is below
56:

`(1,1): u=2,...,7` (six triples),

`(2,0): u=4,...,6` (three triples),

`(2,1): u=6` (one triple).

The 35 remaining boxes are therefore exactly the ranges in (2): 19 boxes
for `(1,1)`, 11 for `(2,0)`, and 5 for `(2,1)`.  Their upper endpoints are
`ceil(R)-1`.  At the three terminal values they are respectively

`u=26: ceil(R)-1=568-1=567`,

`u=17: ceil(R)-1=268-1=267`,

`u=11: ceil(R)-1=133-1=132`.

Thus every possible falsifier has at most `2+1+26=29` points and span at
most 567.  Both advertised terminal bounds are correct.

## 5. Embedded checker defects

The final assertion is false as written.  The loops order `bad` by `delta`
first, so the actual list begins with the `(2,0,u)` block, followed by the
`(1,1,u)` block and then `(2,1,u)`.  The asserted right side puts `(1,1,u)`
first.  Replace the assertion by a comparison of sorted lists or reorder the
expected blocks.  Also replace "prints exactly" by "asserts exactly", or add
an actual `print` statement.

The checker should additionally contain or cite the explicit tail
certificate above.  Without it, its finite bounds do not prove the claimed
unbounded parameter statement.

## 6. Remaining gaps and disposition

1. Normalize explicitly to `min A=0,max A=L`, or define `h_S` in
   `[2 min A,2 max A]`.  Formula (3) and the span-55 census use this
   normalization.
2. Fix the order-sensitive assertion and the false claim that the checker
   prints output.
3. Add the exact cutoff proof from Section 3 and cite the span-55 census
   source/artifact explicitly.

No gap was found in the three-layer identity, the weighted-difference
lemma, the 35-box arithmetic, or the terminal span calculation.  The result
is mathematically acceptable after the three listed repairs, but the current
submission is not an executable exact certificate and is therefore rejected
as written.

## Repair disposition

The source note now explicitly normalizes the endpoints, contains the finite
tail inequalities from Section 3, compares sorted parameter lists, prints the
result, and cites the stored census hash. The standalone repaired checker is
`compute/p73/verify_parameter_reduction.py`; it returns exactly the 45 triples
in 1.3 seconds. With these repairs, the finite reduction is accepted.
