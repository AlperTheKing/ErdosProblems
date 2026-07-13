# Referee report on P74

## Verdict

The mathematical argument is correct after one minor statement correction:
either assume explicitly that `min A = 0` and `max A = L`, or define `L` as
the span and count missing sums in `[2 min A, 2 max A]`.  Merely writing
`A subset [0,L]` does not make `h_S` the number of missing labels in
`[0,2L]` unless the endpoints have been normalized.

With endpoint normalization, P74 proves the eventual exact inequality

`2 beta <= h_S`.

In fact, the constants used in the note give the following uniform finite
version.

## Corrected theorem

Let `A` be an admissible finite set having exactly one repeated unordered
sum `sigma`, where diagonal pairs are included.  Translate `A` so that
`min A = 0` and put `L = max A`.  Define

`P = A intersect (sigma-A)`, `R = A\P`,

`|P| = c = 2p+delta`, `|R| = u`, `delta in {0,1}`,

and let `beta` be the P56 reflected-completion defect.  Let `h_S` be the
number of integers in `[0,2L]` which are not represented as a sum of two
elements of `A`.  If

`|A| >= 1726`,

then

`2 beta <= h_S`.

The numerical threshold is only a convenient consequence of the constants
in P74 and is not claimed to be optimal.

## 1. Audit of the Sidon span estimate

For a Sidon set `B = {b_1 < ... < b_s}`, equality

`b_{i+d}-b_i = b_{j+e}-b_j`

gives

`b_{i+d}+b_j = b_{j+e}+b_i`.

Uniqueness of unordered sums, including diagonals, forces the two positive
difference pairs to be identical.  Hence all differences used in P74 are
indeed distinct.

For `m = floor(sqrt(s))`, their number is

`N_m = sum_{d=1}^m (s-d) = m(s-(m+1)/2)`.

Their sum is at least `N_m(N_m+1)/2`.  For each fixed `d`, telescoping gives

`sum_{i=1}^{s-d}(b_{i+d}-b_i)
 = sum_{j=s-d+1}^s b_j - sum_{j=1}^d b_j <= dL`.

After summing over `d`,

`N_m(N_m+1) <= Lm(m+1)`.

Dropping the positive `N_m` term yields exactly

`L >= (m/(m+1))(s-(m+1)/2)^2`.

The final simplification is also valid.  Put `x = sqrt(s)`.  Since
`m+1 >= x` and `m+1 <= x+1`, the last display is at least

`(1-1/x)(x^2-(x+1)/2)^2`.

Subtracting `x^4-3x^3` gives

`x^3+x^2/4+5x/4-1/4-1/(4x)`,

which is positive for `x >= 3`.  Thus the claimed estimate holds for
`s >= 9`; for `4 <= s <= 8`, its right side is negative.  Lemma 1 is
therefore correct.

## 2. Audit of the extracted Sidon subset

Choose one element from each off-diagonal reflected pair in `P`, retain all
of `R`, and retain the midpoint when `delta=1`.  The resulting set has size

`s = p+u+delta`.

Any repeated sum in this subset is a repeated sum in `A`, hence must equal
`sigma`.  Such a representation cannot use two selected members of one
off-diagonal reflected pair, since only one was selected.  It cannot use a
residual point: if `r+x=sigma` with `r,x in A`, then `sigma-r=x in A`, so
`r in P`, contrary to `r in R`.  If the midpoint is present, its diagonal
is the only remaining representation of `sigma`.  The extracted set is
therefore genuinely Sidon under the diagonal-inclusive convention.

This proves

`L >= s^2-3s^(3/2)`.

No reflected-extremizer hypothesis is used here.

## 3. Audit of the exact identities

P56 gives the disjoint positive-difference support counts

`|D_P| = p(p+delta)`,

`|D_R| = cu+binom(u,2)`.

Therefore

`|D^+(A)| = p(p+delta)+cu+binom(u,2)`.

Using `s=p+u+delta`, `c=2p+delta`, and `delta^2=delta`, direct expansion
gives

`s^2-|D^+(A)| = binom(u+1,2)+delta*s`.

Thus, for `h_D=L-|D^+(A)|`, the Sidon span estimate gives

`h_D >= binom(u+1,2)+delta*s-3s^(3/2)`.

The occupied-sum count is

`2p(p+delta)+cu+binom(u+1,2)+1`.

There are `2L+1` possible sum labels after endpoint normalization, so

`h_S = 2L-[2p(p+delta)+cu+binom(u+1,2)]`.

Substitution of the difference count gives both exact forms

`h_S = 2h_D+|D_R|-u`

and

`h_S = 2h_D+binom(u+1,2)+u(c-2)`.

Finally, there are only `binom(u+1,2)` virtual residual pairs, and P56's
exact collision formula gives

`beta <= binom(u+1,2)`.

Combining the last three displays yields exactly

`h_S-2beta >= binom(u+1,2)+u(c-2)+2delta*s-6s^(3/2)`.

All algebraic identities in P74 are therefore correct.

## 4. Easy and hard ranges

If `u <= 2c-5`, Lemma P61.2 proves `2beta <= h_S` exactly.

Now suppose `u > 2c-5`.  Since the exceptional sum has at least two
unordered representations, `p+delta >= 2`, and hence `c=2p+delta >= 3`.
As `u,c` are integers,

`u >= 2c-4`, so `c <= (u+4)/2`.

Consequently

`s = u+(c+delta)/2 <= 5u/4+3/2 <= 2u`

for `u >= 2`.  The terms `u(c-2)` and `2delta*s` are nonnegative.  It is
therefore enough that

`binom(u+1,2) > 6(2u)^(3/2)`.

For positive `u`, squaring this inequality is equivalent to

`(u+1)^2 > 1152u`,

or

`u^2-1150u+1 > 0`.

This holds for every integer `u >= 1150` (at `u=1150` the last expression
equals `1`, and it is then increasing).  In the hard range, if `u <= 1149`
then

`|A|=c+u <= floor((u+4)/2)+u <= 1725`.

Hence `|A| >= 1726` forces `u >= 1150`, and the right side of the P74
inequality is strictly positive.  This proves the corrected theorem and
also shows that the original sequence formulation is uniform, not dependent
on the chosen sequence.

## 5. Exact finite audit

An independent integer enumeration checked all `262143` endpoint-normalized
sets through span `18`.  Among them, `3204` sets had exactly one repeated
sum.  For every such set the audit reconstructed `P`, `R`, `p`, `delta`,
`beta`, the extracted subset, all sum and difference supports, and verified:

* the extracted subset is Sidon;
* its size is `p+u+delta`;
* both formulas for `h_S`;
* the formula for `s^2-|D^+(A)|`;
* `beta <= binom(u+1,2)`.

There were no failures.  This is only a consistency audit; the proof above
does not rely on finite enumeration.

## 6. Exact scope relative to P61

P74 proves the asymptotic completion-charge statement itself:

`2beta <= h_S`

for every sufficiently large admissible set having a repeated exceptional
sum.  It does not prove the fully reflected sharp span theorem, and it does
not complete the general P61 assembly.

The reason is precise.  P61's first branch contains the nonlinear credit

`Xi(k,u,b)=u^2-2b(k+u)+2b^2`, where `b=min(u,beta)`,

together with the two reflected error terms.  The estimate
`beta <= h_S/2` bounds `beta` by a quantity which itself contains `L`; it
does not, without an additional optimization using the second P61 branch,
show that `Xi` is nonnegative or that it pays the reflected errors in every
regime.

Accordingly, the Scope paragraph of P74 is correct.  Any stronger statement
that P74 has already made the P61 completion credit sufficient in all
asymptotic regimes, or that the general reduction is closed, is not proved
by this note.  What is closed is the standalone asymptotic P66 charge; a
separate P61 assembly lemma and the fully reflected sharp-center theorem
remain load-bearing.

## Disposition

Accept P74 as a correct standalone lemma after fixing the endpoint
normalization in the theorem statement.  Retain its current scope warning.
