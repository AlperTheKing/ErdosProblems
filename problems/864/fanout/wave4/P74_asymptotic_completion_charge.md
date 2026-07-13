# P74: asymptotic completion charge from a large Sidon subset

## Theorem

Use the P56 notation for an endpoint-normalized admissible set
`A subset [0,L]`, with `min A=0`, `max A=L`, and exceptional sum `sigma`:

`P=A intersect (sigma-A)`, `R=A\P`,

`|P|=c=2p+delta`, `|R|=u`, `delta in {0,1}`,

and let `beta` be the reflected-completion defect. Let `h_S` be the number
of missing sum labels in `[0,2L]`.

In fact, the referee audit gives the uniform finite statement: if
`|A|>=1726`, then

`2 beta <= h_S`

holds. In particular it holds eventually along every sequence with
`|A|` tending to infinity.

This is an eventual exact inequality, not merely an estimate with an error
term.

## 1. An elementary Sidon span bound

### Lemma 1

If `B={b_1<...<b_s} subset [0,L]` is Sidon, including diagonal sums, then

`L >= s^2-3s^(3/2)`

for `s>=4`.

### Proof

Put `m=floor(sqrt(s))`. The positive differences

`b_{i+d}-b_i`, `1<=d<=m`, `1<=i<=s-d`,

are all distinct. Their number is

`N_m=ms-m(m+1)/2`.

Therefore their sum is at least `N_m(N_m+1)/2`. On the other hand,

`sum_{i=1}^{s-d}(b_{i+d}-b_i)
 =sum_{j=s-d+1}^s b_j-sum_{j=1}^d b_j <=dL`.

Summing over `d<=m` gives

`N_m(N_m+1)<=Lm(m+1)`.

Hence

`L >= [m/(m+1)] [s-(m+1)/2]^2`.

Since `m/(m+1)>=1-s^(-1/2)` and `m+1<=sqrt(s)+1`, the last expression is
at least `s^2-3s^(3/2)` for `s>=9` by direct expansion. For `4<=s<=8`,
the claimed right side is nonpositive, so the bound follows from `L>=0`.

## 2. A large genuine Sidon subset of A

Choose one point from each of the `p` off-diagonal reflected pairs in `P`,
include every point of `R`, and include `sigma/2` when `delta=1`. Call the
resulting set `B`. Then

`|B|=s=p+u+delta`.

The set `B` is Sidon. Indeed, any repeated unordered sum in `B` would also
be repeated in `A`, so it would have to be `sigma`. But `B` contains no
complete off-diagonal reflected pair. A residual point cannot occur in a
pair summing to `sigma`, by the definition of `R`. If the midpoint is
present, its diagonal is therefore the sole representation of `sigma` in
`B`.

Lemma 1 now gives

`L >= s^2-3s^(3/2)`.                                    (1)

## 3. Difference holes

P56 gives the exact positive-difference support size

`|D^+(A)|=p(p+delta)+cu+binom(u,2)`.

Let `h_D=L-|D^+(A)|`. A direct expansion using `s=p+u+delta` and
`c=2p+delta` gives

`s^2-|D^+(A)|=binom(u+1,2)+delta*s`.

Together with (1),

`h_D >= binom(u+1,2)+delta*s-3s^(3/2)`.                 (2)

Also

`h_S=2h_D+|D_R|-u
     =2h_D+binom(u+1,2)+u(c-2)`.                        (3)

Finally `beta<=binom(u+1,2)`, because there is one virtual label for each
unordered residual pair. Equations (2)-(3) imply

`h_S-2beta
 >= binom(u+1,2)+u(c-2)+2delta*s-6s^(3/2)`.            (4)

## 4. Completion of the proof

P61.2 already proves `2beta<=h_S` exactly whenever

`u<=2c-5`.

In the complementary range `u>2c-5`, if `|A|=c+u` tends to infinity then
`u` tends to infinity and `s=p+u+delta=O(u)`. The quadratic term
`binom(u+1,2)` in (4) therefore dominates `6s^(3/2)`. The remaining terms
are nonnegative because every exceptional sum has at least two unordered
representations, so `c>=3`. Thus the right side of (4) is positive for all
sufficiently large members of the sequence.

This proves the theorem.

## Scope

P74 proves the exact P66 inequality eventually and removes that lemma as an
asymptotic obstruction. It does not by itself prove that the P61 completion
credit pays every remaining general-case error, nor does it prove the sharp
bound for fully reflected sets.
