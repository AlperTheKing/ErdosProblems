# C12: prime-frontier injectivity, abundance obstruction

## Verdict

No nontrivial unconditional lower bound for `|F(X,Y(X))|` with
`Y(X) -> infinity` is proved. In particular, the finite counts below are not
an all-large-`X` statement.

The obstruction alternative is proved in two exact forms.

1. The target-specific block construction that gives the accepted exponent
   `log(6)/log(30)` has a composite-only subfamily with the same exponent.
   Thus the full known unconditional cardinality lower bound can be matched,
   up to a constant, without producing any ordinary primes.
2. More generally, for every `epsilon>0` there is a least distinct-input
   closure under `xy-1`, seeded by two ordinary primes and using every newly
   generated value as a multiplier, whose entire counting function is
   `O(X^epsilon)`. Its prime-frontier count is therefore `O(X^epsilon)` for
   every choice of `Y`. Closure combinatorics and prime seeds do not force
   any uniform power of generated-prime or prime-frontier abundance.

These are not counterexamples for the actual seeds `2,3`. They prove that a
successful lower bound for the actual `F` must use arithmetic special to
those seeds, beyond the exact closure identity and the accepted block-growth
lemma.

There is a second, independent bottleneck after a generated prime is found.
The natural one-step cofactor `q=dp-1` can satisfy `p<=ell(q)` only if
`6 | d`; even the first possible multiplier `d=84` fails at the generated
prime `p=149`. Generated-prime abundance alone would not establish the
rough-cofactor abundance required by `F`.

## 1. Exact definitions and quantifier audit

For `n>=4`, the well-founded closure recurrence is

```text
n in G  iff  n+1=ab for some a,b in G with 2<=a<b.              (1)
```

For `q in G`, put

```text
ell(q)=min {d in G : d divides q}.                              (2)
```

The set investigated here is exactly the C06 set

```text
F(X,Y)={(p,q):
  p is an ordinary prime in G,
  Y<p<q, q in G, p<=ell(q), and p*q<=X+1}.                      (3)
```

The C06 proof that `(p,q) -> pq-1` is injective is correct. If
`pq=p'q'` and `p<p'`, ordinary primality gives `gcd(p,p')=1`, hence
`p | q'`; then `ell(q')<=p<p'`, a contradiction. The same argument is
not valid for a composite multiplier.

The interval quantifiers impose the exact necessary condition

```text
Y < p < sqrt(X+1).                                               (4)
```

Consequently, if `Y(X)->infinity` and `|F(X,Y(X))|>=1` for every
sufficiently large `X`, then `G` contains infinitely many ordinary primes.
Indeed, if its generated primes had maximum `P`, then `Y(X)>P` eventually
and (3) would be empty. A bound tending to infinity needs correspondingly
stronger uniform control of generated primes in every moving interval (4).
No accepted closure lemma supplies even the infinitude conclusion.

This is not repaired by taking an ordinary prime divisor of a generated
number: membership is not inherited by divisors. Section 5 gives an exact
mixed example in which one prime divisor is generated and the other is not.

## 2. Exact obstruction to one-step cofactors

**Lemma.** Let `p>3` be an ordinary prime in `G`, let `d in G`, `d!=p`,
and put `q=dp-1`. If `p<=ell(q)`, then `6 | d`.

**Proof.** Every member of `G` is `0` or `2 mod 3`. Since `p>3` is prime,
`p` is odd and `p=2 mod 3`.

- If `d` is odd, then `q` is even, so `ell(q)<=2<p`.
- If `d=2 mod 3`, then `q=0 mod 3`, so `ell(q)<=3<p`.

The only remaining possibility is that `d` is even and `d=0 mod 3`, which
is exactly `6 | d`. QED.

The least generated multiple of `6` is `84=5*17-1`; exact recurrence (1)
finds no earlier one. Necessity is not sufficiency:

```text
149 in G,
84*149-1 = 12515 = 5*2503,
```

so `ell(12515)<=5<149`. A second example after covering `2,3,5` is

```text
900=17*53-1 in G,
101 in G,
900*101-1 = 90899 = 17*5347,
```

so this cofactor also fails.

The general obstruction is exact: if `r in G`, `r<p`, and
`dp=1 mod r`, then `r | (dp-1)` and `ell(dp-1)<=r<p`. A one-step
construction must avoid a growing family of inverse residue classes, not
merely produce many generated primes. In particular, the ubiquitous
multipliers `2,3,5` produce no frontier cofactors for any generated prime
`p>5`.

## 3. Target-specific composite family

Let `T_d(x)=dx-1`. Applying each permutation of `(2,3,5)` gives the six
valid three-step blocks

```text
x -> 30x-b,        b in D={9,10,13,16,19,21}.                   (5)
```

All intermediate inputs are distinct when `x>=9`. Composing `n` blocks
from `x=9` gives

```text
30^n*9 - sum_{j=0}^{n-1} b_j 30^j,      b_j in D.              (6)
```

The `6^n` values are distinct by uniqueness of the base-30 digit string.
If the last applied block has

```text
b in D_comp={9,10,16,21},                                      (7)
```

then the final value is composite: it is divisible by `3,10,2,3`,
respectively, and is larger than the displayed divisor. The preceding
`n-1` blocks remain arbitrary. Hence (6) contains exactly
`4*6^(n-1)` certified distinct composite members of `G` for each `n>=1`.

Put `alpha=log(6)/log(30)`. For every `X>=270`, take
`n=floor(log_30(X/9))>=1`. All values (6) are below `9*30^n<=X`, and

```text
#{m<=X : m in G and m composite}
  >= 4*6^(n-1)
  >= (1/9)*(X/9)^alpha.                                        (8)
```

This has the same exponent as the accepted lower bound
`|G intersect [1,X]| >= (1/6)*(X/9)^alpha`. Thus that entire known
power-law scale is compatible with an explicitly composite certificate.
The remaining terminal digits `13,19` are only candidates for ordinary
primality; closure gives no lower-bound sieve for them.

## 4. Full-closure countermodel with prime seeds

The preceding result is internal to the actual `G`, but it is a pruned
subsystem. The following is a full least-closure countermodel to any generic
forcing principle.

**Theorem.** Let `a<b` be distinct ordinary primes with `a>=11`, and let
`C` be the least set containing `a,b` and closed under `xy-1` for distinct
inputs. Define

```text
lambda=(a^2-1)/a=a-1/a,
theta=log(8)/log(lambda)<1.                                    (9)
```

Then, for `X>=a`,

```text
|C intersect [1,X]| <= (16/7)*(X/a)^theta = o(X).              (10)
```

For the analogue `F_C` of (3), using the least `C`-divisor,

```text
|F_C(X,Y)| <= (16/7)*(X/a)^theta                               (11)
```

for every `X,Y`.

**Proof.** Every element of `C` has a full binary derivation tree with
leaves labelled `a` or `b`. If a tree has `n` leaves, its value is at least

```text
a*lambda^(n-1).                                                 (12)
```

This is immediate for a leaf. If child values are `u,v>=a`, then

```text
uv-1 >= (1-1/a^2)uv,
```

and induction turns the right side into
`(a^2-1)lambda^(n-2)=a lambda^(n-1)`.

There are `Cat_(n-1)` ordered full binary tree shapes and `2^n` leaf
labellings. Counting all trees, including invalid equal-child trees, only
enlarges the set, and

```text
Cat_(n-1)*2^n <= 2*8^(n-1).                                    (13)
```

A value at most `X` has
`n-1<=log(X/a)/log(lambda)`. Summing (13) gives (10). The
prime-frontier map for `C` is injective by the same ordinary-prime proof as
in C06, and its image lies in `C intersect [1,X]`, proving (11). QED.

For `a=11`, `theta=0.8702061489...`. More sharply, `a` can be chosen as
an arbitrarily large prime, making `theta` smaller than any prescribed
positive `epsilon`. Therefore no fixed power lower bound for a prime
frontier follows uniformly from the least-closure axiom, distinct inputs,
two prime seeds, and dynamic availability of all generated multipliers.

This theorem does not share the target seeds `2,3`. Its exact role is to
separate generic closure logic from the seed-specific arithmetic that a
positive result for (3) would have to exploit.

## 5. Prime-divisor opacity inside the actual closure

Starting from `u_0=3` and applying `u -> 2u-1` gives

```text
u_n=2^n+1 in G.                                                 (14)
```

Thus the Fermat number

```text
F_5=2^32+1=4294967297=641*6700417                              (15)
```

belongs to `G`. Both displayed factors are ordinary primes. Their generated
statuses differ:

```text
161 in G,
321=2*161-1 in G,
641=2*321-1 in G,
6700417 notin G.                                                (16)
```

The last exclusion is exact from recurrence (1) through `6,700,417`; values
above it cannot change membership. The C12 program also trial-divides both
factors to audit ordinary primality. Hence closure has neither upward nor
downward inheritance between a generated composite and all of its ordinary
prime factors.

Together with the C06 primitive composite `77=7*11`, this blocks the two
obvious replacements for an abundance theorem: taking ordinary prime
divisors of generated elements, or treating every least generated divisor
as an ordinary prime.

## 6. Exact census through 100,000,000

The finite computation is diagnostic only. It used recurrence (1) in
ascending order. Ordinary primality was marked by a smallest-prime-factor
sieve; every generated prime that could occur in `F(10^8,Y)`, hence every
one at most `sqrt(10^8+1)=10000`, was independently trial-divided.

The least generated divisors were built by marking multiples of generated
`d` in ascending `d` order through `14,285,714`. For every cofactor that
appeared in any reported frontier row, `ell(q)` was recomputed independently
by factoring `q`, enumerating all divisors, and taking the least divisor in
`G`. This audited `275,536` distinct cofactors. At the final cube-root row,
all `715,317` outputs were marked directly and no collision occurred; every
output was independently checked to be in `G`.

Reference membership counts through `10^8` and the distinctness sentinels
`8,24 notin G` all matched.

### Generated ordinary primes

Here "eligible" means `2`, `3`, or an ordinary prime `2 mod 3`, the only
ordinary-prime residue classes compatible with `G`.

| `X` | all ordinary primes | eligible | ordinary primes in `G` | generated / eligible | largest observed generated-prime gap |
|---:|---:|---:|---:|---:|---:|
| `10^4` | 1,229 | 618 | 385 | 0.622977 | 162 |
| `10^6` | 78,498 | 39,267 | 33,944 | 0.864441 | 246 |
| `10^7` | 664,579 | 332,385 | 305,394 | 0.918796 | 324 |
| `10^8` | 5,761,455 | 2,880,938 | 2,730,169 | 0.947667 | 510 |

These ratios do not prove that there are infinitely many generated ordinary
primes. The growing finite maximum gap also supplies no asymptotic upper or
lower conclusion.

### Moving prime frontier

For each upper endpoint `U`, the interval count below uses the single fixed
frontier `Y=floor(cuberoot(U))` and counts outputs in `(L,U]`. It is not the
difference of two prefix rows having different values of `Y`.

| output interval `(L,U]` | `Y` | `|F(U,Y)|` prefix | outputs in `(L,U]` |
|---:|---:|---:|---:|
| `(1,000,10,000]` | 21 | 21 | 21 |
| `(10,000,100,000]` | 46 | 357 | 349 |
| `(100,000,1,000,000]` | 100 | 5,872 | 5,632 |
| `(1,000,000,2,000,000]` | 125 | 12,796 | 7,638 |
| `(1,000,000,10,000,000]` | 215 | 61,605 | 59,018 |
| `(10,000,000,100,000,000]` | 464 | 715,317 | 680,006 |

The first four interval counts reproduce C06 exactly. The final interval
fraction is `680006/90000000=0.0075556222...`; the final prefix fraction is
`0.00715317`.

As a separate quantifier check, the genuinely moving choice
`Y=floor(log X)` (natural logarithm) gives

```text
|F(10^8,18)|=1,980,167.                                        (17)
```

This is still one finite value. Neither (17) nor any table row establishes a
lower bound for every sufficiently large `X`.

## 7. Literature boundary

The official problem page, checked 2026-07-13, still marks #424 open and
lists no claimed partial solution:

<https://www.erdosproblems.com/424>

The block family (6) is a six-symbol base-30 digit-restricted family after
the elementary borrow conversion. Maynard's Theorem 1.3 on multiple
restricted digits requires, in its most permissive consecutive-exclusion
case, an allowed alphabet of size at least `q^(4/5+epsilon)` for sufficiently
large `q`. The present size is `6`, with dimension
`log(6)/log(30)=0.52680255...`, so that theorem does not apply. The arbitrary
excluded-digit case is still farther from this alphabet.

Primary source:

J. Maynard, *Primes and polynomials with restricted digits*, Theorem 1.3,
<https://arxiv.org/abs/1510.07711>.

No cited restricted-digit theorem found in this gate supplies primes in the
specific six-digit family (6).

## 8. Exact remaining frontier

A lower bound for (3) needs both of the following target-specific inputs.

1. A uniform all-large-`X` theorem producing ordinary primes of `G` in the
   moving interval `(Y(X),sqrt(X+1))`.
2. For enough such primes, a uniform supply of generated cofactors
   `p<q<=(X+1)/p` avoiding every generated divisor below `p`.

Equivalently, one must lower-bound

```text
sum over generated ordinary primes Y(X)<p<=sqrt(X+1)
  #{q in G : p<q<=(X+1)/p and ell(q)>=p}.                       (18)
```

The composite family (8) shows why the accepted growth theorem does not
provide input 1. The one-step lemma and its examples show why input 1 alone
would not provide input 2. The full-closure theorem shows that neither input
is a consequence of generic dynamic closure.

## 9. Reproduction

Artifacts:

- `problems/424/compute/wave3/C12_prime_frontier/prime_frontier.cpp`
- `problems/424/compute/wave3/C12_prime_frontier/result_1e8.json`

Run with assertions enabled; do not compile with `-DNDEBUG`:

```powershell
g++.EXE -O3 -std=c++20 -Wall -Wextra -Wpedantic `
  problems/424/compute/wave3/C12_prime_frontier/prime_frontier.cpp `
  -o problems/424/compute/wave3/C12_prime_frontier/prime_frontier.exe

problems/424/compute/wave3/C12_prime_frontier/prime_frontier.exe `
  100000000 `
  problems/424/compute/wave3/C12_prime_frontier/result_1e8.json
```

The recorded run used one CPU thread; its principal arrays total less than
700 MB, and it completed in `38.9251` wall seconds. SHA-256:

```text
prime_frontier.cpp  31854b8af1a0609d93cd21c1cc9ef8868419c894950b44955be90c7544ba5d6b
result_1e8.json     caffaa46c0b5477ecd1f56a1fb7e33e0b21d46c3dab7db9ffcfe074e7c7d35b9
```
