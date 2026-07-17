# C99: all-prime hard sieve and the root-trapping obstruction

## Verdict

The proposed all-prime strengthening is true.  Write

\[
 h+1=3^\epsilon R,\qquad \epsilon\in\{0,1\},\qquad
 R\equiv1\pmod3,\qquad 3\nmid R
\]

as in C55.  If `h` is hard, then

\[
                         d(h)\ge 2^{\omega(R)-2}.       \tag{1}
\]

Here every distinct prime divisor of `R` is counted, not only the primes
`2 mod 3`.  Even exponents of minus primes do not give an exceptional
positive-density family: their partial prime-power divisors supply at least
as many residue-compatible choices as the missing parity split.  The sole
zero-pair edge case is `R=p^2` for a minus prime, and C96 shows that it is
structural splitless rather than hard.

Consequently, for every fixed real `c<log 2`,

\[
 \#\{h\le X:h\text{ hard},\ d(h)\le(\log X)^c\}
       =O_c\!\left({X\over\log\log X}\right)=o(X).    \tag{2}
\]

In particular, the original threshold

\[
                         D_0(X)=(\log\log X)^2
\]

also has `B_{D_0(X)}(X)=O(X/log log X)`.

This repairs the exponent gap recorded in C94, but it does **not** by itself
prove hard-hole sparsity.  The reciprocal mass of the full structural
splitless bank satisfies the sharp order

\[
 W_E(X)=\Theta(\sqrt{\log X}).                         \tag{3}
\]

Thus `D_0` is too small for C85.  On the other hand, any fixed

\[
                         {1\over2}<c<\log2             \tag{4}
\]

does absorb the structural mass.  If all high-pair hard holes were trapped
by structural splitless witness roots, C85 would then give `H(X)=o(X)`.
That trapping hypothesis is not a theorem and is false pointwise, including
above fixed positive pair thresholds.  At `X=10^6`, with `c=0.6`, exactly
`151` hard holes satisfying `d(h)>(log X)^c` have a C85 witness root that is
not structural splitless.

Replacing a witness root by a terminal C38 splitless shadow does not preserve
the C85 capacity estimate.  The capacity remains charged at the reciprocal
weight of the original root, and a second application of C85 loses one
logarithmic power under partial summation.  Even after deleting the
low-pair error entirely, the best exponent supplied by one such iteration is

\[
                         {3\over2}-\log2=0.8068\ldots,
\]

which is larger than the maximum available threshold exponent
`log 2=0.6931...`.  Therefore the proved C55/C85/C38 mechanisms do not yield
hard-hole sparsity.  The exact remaining requirement is a new bound on the
reciprocal mass of the non-splitless witness-root basins.

## 1. Exact all-prime divisor count

Call a prime plus when it is `1 mod 3` and minus when it is `2 mod 3`.
Factor

\[
 R=R_+R_-,\qquad
 R_+=\prod_{i=1}^s p_i^{\alpha_i},\qquad
 R_-=\prod_{j=1}^t q_j^{\beta_j},                     \tag{5}
\]

where the `p_i` are plus primes and the `q_j` are minus primes.  Put

\[
 A=\tau(R_+),\qquad T=\tau(R_-),\qquad
 \delta=\begin{cases}
 1,&\text{all }\beta_j\text{ are even},\\
 0,&\text{some }\beta_j\text{ is odd}.
 \end{cases}                                          \tag{6}
\]

Let `V_2(R)` denote the number of divisors of `R` congruent to `2 mod 3`.

### Lemma C99.1 (exact residue-compatible divisor count)

If `t>=1`, then

\[
 V_2(R)={A(T-\delta)\over2}.                           \tag{7}
\]

For a hard hole `h`,

\[
 d(h)=
 \begin{cases}
 \lfloor V_2(R)/2\rfloor,&\epsilon=0,\\
 V_2(R),&\epsilon=1.
 \end{cases}                                          \tag{8}
\]

#### Proof

A divisor of `R` is `2 mod 3` exactly when the sum of its selected
minus-prime exponents is odd.  For a fixed `q_j^{beta_j}`, the difference
between the numbers of even and odd exponent choices is

\[
 \sum_{a=0}^{\beta_j}(-1)^a=
 \begin{cases}1,&\beta_j\text{ even},\\0,&\beta_j\text{ odd}.
 \end{cases}
\]

Hence the difference between the total even- and odd-parity choices from
`R_-` is `delta`, while their sum is `T`.  The plus-prime exponents have `A`
free choices.  This proves (7).

If `epsilon=0`, an admissible pair consists of two complementary divisors
of `R`, both `2 mod 3`.  Complementation is an involution on the divisors
counted by (7).  Its two-cycles give the distinct unordered pairs; its only
possible fixed point is `sqrt(R)`, which is excluded by `a<b`.  The number
of pairs is therefore `floor(V_2(R)/2)`.

If `epsilon=1`, every admissible pair has a unique factor not divisible by
`3`.  That factor is a divisor `a|R` with `a=2 mod 3`, and its complement
`3R/a` is automatically allowed.  Equality of the factors is impossible
because `3` divides exactly one of them.  Thus these pairs are in bijection
with the divisors in (7).  This proves (8).  QED.

The notation in (7) will not be used below; write the count explicitly from
now on.

### Corollary C99.2 (all-prime lower bound)

Every hard hole satisfies (1).

#### Proof

C96 Corollary C96.2 shows that a hard shape has `t>=1`; in the
`epsilon=0` case it is not the isolated square `R=q^2` of one minus prime.
Also

\[
                         A\ge2^s.                     \tag{9}
\]

If `delta=0`, then `T>=2^t`.  If `delta=1`, every minus exponent is at
least two, so

\[
                         T-1\ge3^t-1\ge2^t.           \tag{10}
\]

In both cases (7) gives

\[
                         V_2(R)\ge2^{s+t-1}
                                  =2^{\omega(R)-1}.   \tag{11}
\]

For `epsilon=1`, (8) is stronger than (1).  For `epsilon=0` and
`omega(R)>=2`, equations (8) and (11) give (1).  If `omega(R)=1`, hardness
excludes `R=q^2`, so `d(h)>=1>=2^{-1}`.  QED.

This proof handles the squarefull part directly.  It does not discard it as
an exceptional set and does not assume that `R` is squarefree.

## 2. Quantitative Turan--Kubilius sieve

All logarithms in this sidecar are natural.  Let

\[
 B_c(X)=\#\{h\le X:h\text{ hard},\ d(h)\le(\log X)^c\}.
\]

### Theorem C99.3 (uniform all-prime threshold)

For each fixed `c<log 2`, equation (2) holds.

#### Proof

By (1), a member of `B_c(X)` has

\[
 \omega(R)\le {c\over\log2}\log\log X+2.             \tag{12}
\]

Put `a=c/log 2<1`.  For the additive function `omega`, with the harmless
prime `3` omitted, Turan--Kubilius gives

\[
 \sum_{n\le Y}\left|\omega(n)-A(Y)\right|^2
       \ll Y B(Y)^2,                                  \tag{13}
\]

where

\[
 A(Y)=\sum_{\substack{p\le Y\\p\ne3}}{1\over p}
      =\log\log Y+O(1),
 \qquad
 B(Y)^2=\sum_{\substack{p\le Y\\p\ne3}}
              {1\over p}\left(1-{1\over p}\right)
      =\log\log Y+O(1).                              \tag{14}
\]

For all sufficiently large `X`, the right side of (12) is at most
`(1-eta) log log X` for a constant `eta=eta(c)>0`.  Chebyshev applied to
(13)-(14), with `Y=X+1`, therefore gives

\[
 \#\{R\le X+1:\omega(R)\le a\log\log X+2\}
       \ll_c {X\over\log\log X}.                     \tag{15}
\]

For each `R`, the normalization `h+1=3^epsilon R` has at most the two
choices `epsilon=0,1`.  Equation (15) proves (2).  QED.

### Corollary C99.4 (the proposed threshold)

For

\[
 D_0(X)=(\log\log X)^2,
\]

one has

\[
 B_{D_0(X)}(X)=O\!\left({X\over\log\log X}\right).    \tag{16}
\]

#### Proof

Equation (1) gives

\[
 \omega(R)\le {2\over\log2}\log\log\log X+O(1)
              =o(\log\log X).
\]

The same Turan--Kubilius argument applies.  QED.

## 3. Reciprocal mass of the structural bank

Let

\[
 W_E(X)=\sum_{\substack{e\le X\\e\text{ structural splitless root}}}
              {1\over e-1}.
\]

### Proposition C99.5 (sharp reciprocal order)

Equation (3) holds.

#### Proof

C96 Lemma C96.1 partitions the structural splitless roots by `N=e+1` into
the following classes:

1. every prime divisor of `N` is plus;
2. `N=q^2` for one minus prime `q`;
3. `N=9`;
4. `N=3S`, where every prime divisor of `S` is plus.

For `N>=4`, `1/(N-2)<=2/N`.  Therefore the first class has reciprocal
mass at most

\[
 2\sum_{\substack{N\le X+1\\p\mid N\Rightarrow p=1\ (3)}}{1\over N}
 \le2\prod_{\substack{p\le X+1\\p=1\ (3)}}
              \left(1-{1\over p}\right)^{-1}
 \ll\sqrt{\log X}.                                   \tag{17}
\]

The last estimate is Mertens' theorem in the progression `1 mod 3`.  The
fourth class obeys the same bound because `1/(3S-2)<=1/S`.  The prime-square
sum converges, and `N=9` contributes one constant.  This proves the upper
bound in (3).

For the lower bound, put `z=X^(1/2)` and give each squarefree product `N`
of plus primes `p<=z` weight `1/N`.  The total weight is

\[
 Z_z=\prod_{\substack{p\le z\\p=1\ (3)}}(1+1/p)
       \asymp\sqrt{\log z}\asymp\sqrt{\log X}.        \tag{18}
\]

Under the normalized weights, the expected value of `log N` is

\[
 \sum_{\substack{p\le z\\p=1\ (3)}}{\log p\over p+1}
       ={1\over2}\log z+O(1)
       ={1\over4}\log X+O(1).                        \tag{19}
\]

Markov's inequality shows that products `N<=X` carry at least
`(3/4-o(1))Z_z` of the weight.  Apart from the unit product, each gives the
structural splitless root `e=N-1`, and

\[
                         {1\over e-1}={1\over N-2}
                                      \ge {1\over N}.
\]

This proves the lower bound.  QED.

For the original `D_0`, the normalized C85 structural-bank term has size

\[
 {W_E(X)\over D_0(X)}
       \asymp {\sqrt{\log X}\over(\log\log X)^2}
       \longrightarrow\infty.                        \tag{20}
\]

Thus the proposed iterated-log threshold cannot absorb even the structural
roots.  In contrast, (2)-(4) give

\[
 B_c(X)+{X+1\over(\log X)^c}W_E(X)=o(X).              \tag{21}
\]

Equation (21) is the repaired exponent overlap; it is not yet a bound for
all hard holes.

## 4. The exact C85 trapping gap

Let `W_X` be the C85 witness-root graph, and put

\[
 Y=\left\lfloor{X+6\over10}\right\rfloor.
\]

Every witness root of a hard source through `X` is at most `Y`.  Let

`E_Y` be the structural splitless roots through `Y`, and define

\[
 F_D(X)=\#\{h\le X:h\text{ hard},\ d(h)\ge D+1,
                    N_{W_X}(h)\not\subseteq E_Y\}.    \tag{22}
\]

C85 Corollary C85.2 applied to `E_Y` controls only the hard holes whose
complete root neighborhood is contained in `E_Y`.  Its incidence proof
gives the exact consequence

\[
 H(X)\le B_D(X)+F_D(X)+{X+1\over D+1}W_E(Y).           \tag{23}
\]

With `D=floor((log X)^c)` and (4), the first and third terms in (23) are
`o(X)`.  Therefore the additional estimate

\[
                         F_D(X)=o(X)                   \tag{24}
\]

is sufficient to close this route.  It is not supplied by the cited
lemmas.

Neither C55 nor C85 proves (24).

### Lemma C99.6 (direct structural trapping is false)

The first hard hole whose C85 neighborhood is not structural splitless is
`h=534`.  It has

\[
 535=5\cdot107,
 \qquad N_{W_{534}}(534)=\{54\},                      \tag{25}
\]

and `54` is a reducible hard root.

#### Proof

The only admissible pair for `54` is `(5,11)`.  The value `5` is generated,
while `11` is blocked by the splitless hole `6`; hence `54` is hard.  The
admissible pairs for `107` are

\[
 (2,54),\quad(3,36),\quad(6,18),\quad(9,12).
\]

The values `6,12,18,36` are structural splitless, and `54` is a hole, so
every pair is blocked and `107` is a hole.  Its seed-2 root is `54`.
Finally, `(5,107)` is the only admissible pair for `534`; it is blocked by
`107`.  Thus `534` is hard and (25) follows.  Exhaustion of smaller hard
holes by the independent verifier gives the minimality assertion.  QED.

The example in Lemma C99.6 has one pair and is absorbed by `B_D` for a
growing threshold.  It proves that trapping is not automatic, not that
(24) is false.  The failure also occurs above fixed positive thresholds.
The verifier finds

\[
 h=14024,\qquad d(h)=6,
\]

as the first failure with at least five pairs; its non-splitless witness
roots are `54,104,638`.  At `X=10^6` and `c=0.6`, the active threshold is
`(log X)^c=4.833...`, and `151` of the `d>=5` hard holes fail structural
trapping.  These are exact finite facts, not an asymptotic counterfamily.

There is a formulation which avoids guessing a trapping bank.  Put

\[
 \mathcal R_X=\bigcup_{h\in H_X}N_{W_X}(h),\qquad
 \Sigma(X)=\sum_{r\in\mathcal R_X}{1\over r-1}.        \tag{26}
\]

Then `T_{R_X}(X)=H(X)`, so C85 gives

\[
 H(X)\le B_D(X)+{X+1\over D+1}\Sigma(X).              \tag{27}
\]

The splitless contribution to `Sigma` is at most `W_E(Y)` and is absorbed
by (4).  The precise missing estimate is, for some `c` in (4),

\[
 \sum_{\substack{r\in\mathcal R_X\\r\text{ reducible}}}{1\over r-1}
                         =o((\log X)^c).               \tag{28}
\]

No estimate of the form (28) is present in C55, C85, or C94.  Bounding
`R_X` by all allowed even roots gives only `O(log X)`, which is too large
for every `c<log 2`.

## 5. Why shadow iteration does not supply (28)

For each reducible witness root `r`, C38 supplies a nonempty structural
splitless shadow `L(r)`.  Choose one leaf `sigma(r) in L(r)`.  If the C85
incidences rooted at `r` are relabelled by `sigma(r)`, the capacity at a leaf
becomes

\[
 \sum_{\substack{r:\sigma(r)=e}}
 \sum_{p\in C_X(r)}\left\lfloor{X+1\over p}\right\rfloor
 \le (X+1)\sum_{\substack{r:\sigma(r)=e}}{1\over r-1}. \tag{29}
\]

Summing (29) over the leaves recovers the original reciprocal root mass,
not `W_E(X)`.  Nonempty terminal shadows therefore prove set-theoretic
trapping but do not prove a capacity transfer.

A constant leafwise transfer is false for the natural least-critical
shadow.  For every prime `p>11`, `p=2 mod 3`, C55 Proposition 5 gives the
hard root

\[
                         r_p=11p-1
\]

with least-critical terminal leaf `6`.  Mertens' theorem in the progression
`2 mod 3` gives

\[
 \sum_{\substack{r_p\le X\\p=2\ (3)}}{1\over r_p-1}
 =\sum_{\substack{p\le(X+1)/11\\p=2\ (3)}}{1\over11p-2}
 ={1\over22}\log\log X+O(1).                         \tag{30}
\]

Thus a bound by a fixed multiple of `1/(6-1)` is impossible.  Equation
(30) does not rule out a polylogarithmic basin estimate, which would be
enough in view of (4); it quantifies the minimum loss for this canonical
compression.

There is also an exponent obstruction to obtaining the needed basin bound
by simply applying C85 a second time.  Suppose, optimistically, that a
one-layer hard-root family is trapped by the structural bank.  Using
`D(t)=(log t)^c`, C85, (2), and (3) give at best

\[
 A(t)\ll_c {t\over\log\log t}
              +t(\log t)^{1/2-c}.                    \tag{31}

Partial summation turns this count into reciprocal mass

\[
 \sum_{\substack{a\le Y\\a\in A}}{1\over a-1}
 \ll_c {\log Y\over\log\log Y}
              +(\log Y)^{3/2-c}.                     \tag{32}

The first term in (32), which comes from the quantitative low-pair
exceptions, is too large for every threshold exponent below one.  Even if
that term is deleted entirely, feeding the second term into another C85
step with exponent `c'<log 2` would require

\[
                         {3\over2}-c<c'.               \tag{33}

But `c+c'<2 log 2=1.3862...<3/2`, so (33) is impossible.  The residual
exponent gap is

\[
                         {3\over2}-2\log2
                         =0.1137\ldots.                \tag{34}

Equations (29)-(34) are an obstruction to this iteration of the proved
bounds.  They are not a lower bound on the true basin mass.  A new
healing-sensitive or arithmetic basin estimate could still establish
(28).

## 6. Independent finite verification

`C99_all_prime_sieve_verify.py` imports no earlier constructor.  It builds a
smallest-prime-factor table, reconstructs the least closure in ascending
order, enumerates every admissible distinct factor pair, and checks (7)-(8)
directly.

At `X=10^6` it reports:

| quantity | exact value |
|---|---:|
| hard holes | `45583` |
| all-even minus-exponent cases | `2645` |
| some-odd minus-exponent cases | `42938` |
| failures of (7)-(8) | `0` |
| failures of (1) | `0` |
| structural splitless roots | `108651` |
| `W_E(10^6)` | `2.0431655822471715` |
| witness-root union mass `Sigma(10^6)` | `1.5914452169097786` |
| nontrapped hard holes | `17023` |
| nontrapped holes above the `c=0.6` threshold | `151` |

The hard-hole and structural-root counts match C55 and C94.  Reproduction:

```powershell
python problems/424/fanout/wave5/C99_all_prime_sieve_verify.py `
  --limit 10000 --exponent 0.6

python problems/424/fanout/wave5/C99_all_prime_sieve_verify.py `
  --limit 1000000 --exponent 0.6
```

The first run checks the minimal trap failure at `534`; the second checks
every hard hole through one million.  The computation is finite
verification only.  The analytic conclusions are Lemma C99.1 through
Proposition C99.5 and equations (23), (27), and (32)-(34).

The ordinary and `python -O` outputs at `X=10^6` are byte-identical.  The
verifier SHA-256 is

```text
B4BE979F123CF2A00B57966F2D6E57D225D59F96269589E89889F773D2179BA6
```

## 7. Precise status

The all-prime count proves a new usable threshold range

\[
                         {1\over2}<c<\log2,
\]

and removes C94's structural-bank exponent obstruction.  It does not verify
the C85 trapping hypothesis for the relevant high-pair hard set.  Direct
trapping requires (24); unrestricted C85 requires (28); terminal shadows
require a basin-capacity theorem strong enough to imply (28).  None follows
from the current rank/shadow recurrence, and a naive second C85 application
fails by the explicit exponent calculation (34).  No hard-hole sparsity or
positive-density theorem is claimed.
