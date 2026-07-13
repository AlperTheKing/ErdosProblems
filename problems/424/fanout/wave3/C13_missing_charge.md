# C13: canonical-factor missing-set charging

## Verdict

The natural injective missing-factor charge is false.  Let `M(X)` count
allowed missing values through `X`, and let `E(X)` count those missing values
whose successor has no distinct factorization into two allowed factors.  An
injective charge would give

\[
 M(X)\le E(X)+M\!\left(\left\lfloor{X+1\over2}\right\rfloor\right). \tag{IC}
\]

The first exact failure is `X=32`:

\[
 M(32)=13,\qquad E(32)=7,\qquad M(16)=5,\qquad 13>7+5.
\]

This is not an artifact of choosing the least or the most balanced divisor.
Both `21+1=2*11` and `32+1=3*11` have a unique admissible split, and both
are forced to charge to the missing input `11`.

There is a much larger rule-independent finite obstruction.  Every ordinary
prime `p` in `G` gives a unique-split missing output `11p-1`; any one-split
rule must charge it to `11`.  The exact census through `10^8` contains
`278,970` such generated primes, hence a forced fiber of at least `278,970`
over one missing input.

The splitless error does have density zero, proved below.  Consequently, an
aggregate inequality

\[
 M(X)-E(X)\le\lambda
 M\!\left(\left\lfloor{X+1\over2}\right\rfloor\right),
 \qquad \lambda<2,                                           \tag{AC}
\]

for all sufficiently large `X` would prove that `G` has density `2/3`.
The all-cutoff census does not falsify such an aggregate estimate: the largest
coefficient required through `10^8` is exactly `101/80`, at `X=362`.  This is
finite data only.  No proof of (AC), and hence no density theorem, is claimed.

## 1. Exact setup

Put

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
 \qquad \mathcal M=\mathcal A\setminus G,
\]

and let `M(X)` be the cardinality of `M` through `X`.  Induction under the
closure rule shows `G` is contained in `A`: products of residues `0,2`
modulo 3 have residue `0,1`, so subtracting one again gives residue `2,0`.

Call a factor pair for an allowed `n` admissible if

\[
 n+1=ab,\qquad 2\le a<b,\qquad a,b\in\mathcal A.            \tag{1}
\]

The exact ascending recursion says

\[
 n\in G\quad\Longleftrightarrow\quad n\in\{2,3\}
 \quad\hbox{or (1) holds with }a,b\in G.                     \tag{2}
\]

Let `E(X)` count the `n` in `M` through `X` for which (1) has no solution.
If `n` is in `M` but is not counted by `E`, every admissible split has at
least one endpoint in `M`; otherwise (2) would put `n` in `G`.

Choose one admissible split and then one missing endpoint `c(n)`.  Since both
factors in (1) are at most `(n+1)/2`,

\[
 c(n)\le \left\lfloor{n+1\over2}\right\rfloor.              \tag{3}
\]

If `c` were injective on the reducible missing values through `X`, equations
(3) and the definition of `M` would prove (IC).  Thus (IC) is the exact
counting consequence of a capacity-one canonical charge.

## 2. First exact falsifier

The missing and splitless sets needed at `X=32` are

```text
M through 32 = {6,8,11,12,15,18,20,21,23,24,29,30,32}
E through 32 = {6,8,12,18,20,24,30}
M through 16 = {6,8,11,12,15}.
```

Hence `(IC)` reads `13 <= 7+5`, which is false.

There is also a local Hall obstruction.  The value `11` is missing: the two
factor pairs of `12` are `2*6` and `3*4`; `6` is missing because `7` is
prime, while `4` is forbidden modulo 3.  Now

\[
 21+1=2\cdot11,\qquad 32+1=3\cdot11.                        \tag{4}
\]

Each product in (4) has only the displayed nontrivial factor pair.  The other
endpoint is a seed in `G`, so both outputs are missing and their only possible
missing charge is `11`.  No alternative ordering of divisors, balanced split,
or endpoint preference can make this charge injective.

## 3. Forced-fiber obstruction

**Proposition 1.**  Let `p != 11` be an ordinary prime belonging to `G`.
Then

\[
 n_p=11p-1\in\mathcal M,                                    \tag{5}
\]

`n_p+1` has exactly one admissible split, and every missing-endpoint charge
for `n_p` equals `11`.

**Proof.**  Since `G` is contained in `A`, the prime `p` is either `3` or is
`2` modulo 3.  Thus `11p-1` is allowed.  The two distinct primes `11,p`
give the unique nontrivial factorization of `11p`, and both factors are
allowed.  We proved above that `11` is missing, while `p` is in `G`.
Equation (2) therefore makes `11p-1` missing, and the unique split has only
one missing endpoint.  QED.

At `X=100,000,000`, exact enumeration gives

\[
 \#\{p\le\lfloor(10^8+1)/11\rfloor:p\text{ prime},\ p\in G\}
 =278970.                                                     \tag{6}
\]

The last such prime is `9,090,857`, giving the missing output `99,999,426`.
Thus any local theorem assigning capacity at most `278,969` to each missing
input is already false on the supplied census.  Equation (6) is a finite
obstruction; it does not assert that `G` contains infinitely many primes.

## 4. The splitless error has density zero

Let `S` be the positive integers having no ordinary prime divisor congruent
to `2` modulo 3, and write `S(Y)=|S intersect [1,Y]|`.

**Lemma 2.**  The splitless count satisfies

\[
 E(X)=o(X).                                                   \tag{7}
\]

**Proof.**  Write `N=n+1`.

If `N` is `1` modulo 3, an admissible split must have both factors `2`
modulo 3.  Such a split exists as soon as some prime `p = 2 (mod 3)` divides
`N`: use `p*(N/p)`.  The two factors have the required residues and are
distinct unless `N=p^2`.  Conversely, if no such prime divides `N`, every
divisor of `N` is `1` modulo 3.  Therefore the splitless `N = 1 (mod 3)`
are contained in `S`, together with the squares `p^2` for primes
`p = 2 (mod 3)`.

If `3` divides `N` at least twice, `3*(N/3)` is admissible and distinct,
except when `N=9`.  If `N=3R` with `3` not dividing `R`, an admissible split
exists exactly when `R` has a prime divisor `2` modulo 3: that prime can be
paired with its complementary factor, which is divisible by 3.  Hence the
remaining splitless values have `R` in `S`.

It follows, with harmless endpoint constants, that

\[
 E(X)\le S(X+1)+S((X+1)/3)+O(\sqrt X).                       \tag{8}
\]

For a fixed `y`, every member of `S` avoids each prime
`p <= y`, `p = 2 (mod 3)`.  Inclusion-exclusion, or the Chinese remainder
theorem, therefore gives

\[
 \limsup_{Y\to\infty}{S(Y)\over Y}
 \le \prod_{\substack{p\le y\\p\equiv2\ (3)}}\left(1-{1\over p}\right).
\]

The Euler-Dirichlet divergence of the reciprocal sum over primes
`p = 2 (mod 3)` makes this product tend to zero as `y` tends to infinity.
Thus `S(Y)=o(Y)`, and (8) proves (7).  QED.

**Corollary 3 (sharp normalized frontier).**  If (AC) holds for some fixed
`lambda < 2` and all sufficiently large `X`, then

\[
 M(X)=o(X),\qquad |G\cap[1,X]|={2X\over3}+o(X).               \tag{9}
\]

**Proof.**  Put `delta=limsup M(X)/X`.  Divide (AC) by `X`, use (7), and
note that `floor((X+1)/2)/X` tends to `1/2`.  Taking limsups gives

\[
 \delta\le {\lambda\over2}\delta.
\]

Since `lambda/2 < 1`, this forces `delta=0`.  The allowed set has counting
function `2X/3+O(1)`, and
\(G=\mathcal A\setminus\mathcal M\), proving (9).  QED.

This criterion is deterministic and uses no multiplicative-energy estimate.
Proposition 1 explains why proving it requires a genuinely aggregate charge;
a pointwise bounded-fiber argument cannot simply choose better factors.

## 5. Exhaustive census test

The C++ audit reconstructs `G` by (2), computes `M` and `E`, and tests (IC)
at every integer cutoff, not only at powers of ten.  It reproduces the
accepted count `51,899,129` at `10^8`.

| `X` | `M(X)` | `E(X)` | `M(floor((X+1)/2))` | IC excess | forced fiber at 11 |
|---:|---:|---:|---:|---:|---:|
| 100 | 43 | 19 | 21 | 3 | 3 |
| 1,000 | 416 | 156 | 214 | 46 | 6 |
| 10,000 | 3,459 | 1,344 | 1,837 | 278 | 40 |
| 100,000 | 26,823 | 11,928 | 14,524 | 371 | 352 |
| 1,000,000 | 209,067 | 108,651 | 112,283 | -11,867 | 3,353 |
| 10,000,000 | 1,714,396 | 1,004,961 | 904,635 | -195,200 | 31,030 |
| 100,000,000 | 14,767,537 | 9,395,726 | 7,690,740 | -2,318,929 | 278,970 |

Here `IC excess = M(X)-E(X)-M(floor((X+1)/2))`.  Among all cutoffs through
`10^8`, (IC) fails at `160,641` cutoffs; the first is `32`, the last is
`163,150`, and the largest excess is `564` at `X=57,302`, where

\[
 (M(X),E(X),M(\lfloor(X+1)/2\rfloor))=(16404,7010,8830).
\]

For the diagnostic coefficient

\[
 C_X={M(X)-E(X)\over M(\lfloor(X+1)/2\rfloor)},              \tag{10}
\]

the exact maximum over the census is

\[
 \max_{X\le10^8}C_X={101\over80}=1.2625,
 \quad X=362,\quad (M(362),E(362),M(181))=(163,62,80).       \tag{11}
\]

Equation (11) only says that `lambda=101/80` fits this finite prefix.  It is
not evidence sufficient to assert (AC) beyond `10^8`.

## 6. Reproduction

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave3/C13_missing_charge/missing_charge.cpp -o problems/424/compute/wave3/C13_missing_charge/missing_charge.exe
problems/424/compute/wave3/C13_missing_charge/missing_charge.exe 100000000 problems/424/compute/wave3/C13_missing_charge/result_1e8.json
```

The audited run took `9.38` seconds on this machine.  SHA-256:

```text
missing_charge.cpp  4BBF4CF5A18356A6DAC1F098C7EA03E7429958A805A163DC558D457CC3572D81
result_1e8.json     40EF05B6C141E558E895D1D961E44C2E6CC3AFD579DB90F1E7ACFA1FCE8FB8CD
```

The JSON commits the all-cutoff extremizers, every decimal checkpoint, and
the forced-prime fiber count.  No registry, mailbox, or progress file was
edited in this lane.
