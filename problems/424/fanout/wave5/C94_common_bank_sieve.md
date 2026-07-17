# C94: the healed splitless bank collapses to the full theorem

## Verdict

Let `A_H(X)` count persistent hard roots as in C67/C72, and let `D(X)`
count structural splitless roots whose literal seed-2 chain has reached a
generated value by cutoff `X`.  Thus, for the actual least closure, `D(X)`
is exactly the `B_E` term in the C67 root identity.

The proposed comparison

\[
 D(X)\ge \alpha A_H(X)-o(X),\qquad \alpha>\frac34,
 \tag{1}
\]

is not an intermediate contraction lemma.  C13 gives `E(X)=o(X)`, and
`D(X)<=E(X)`.  Consequently, for **every fixed alpha>0**, (1) is equivalent
to

\[
                         A_H(X)=o(X).                 \tag{2}
\]

C72 proves that (2) is equivalent to hard-hole sparsity, hole sparsity, and
the full density-`2/3` conclusion.  The coefficient `3/4` therefore has no
separate asymptotic significance in this lane.

The suggested combination of C55 and the C85 weighted root pool also has a
precise exponent obstruction.  The reciprocal weight of the full structural
splitless bank is `Omega(sqrt(log X))`, so C85 needs a pair threshold larger
than `(log X)^(1/2)`.  The factor-count mechanism proved in C55 can be made
uniform up to `(log X)^c` for every `c<(log 2)/2`, but `(log 2)/2<1/2`.
Thus those two proved mechanisms have no overlapping exponent range.

Exact computation is consistent with the desired inequality but proves no
asymptotic statement.  At every cutoff through `10^6`,

\[
                         D(X)\ge\frac56 A_H(X),       \tag{3}
\]

and the exact minimum positive ratio is `5/6` at `X=186`.  At `10^6`,

\[
 (A_H,D,E)=(27056,44271,108651).
\]

An independent implementation reproduces every endpoint count and every
cutoff comparison.  A bounded-depth healing substitute is already false:
at `X=10^6`, the structural splitless root `2340` and all eight visible
successors are holes.

Two quarter-scale inequalities survive exact testing through `10^9`, but
neither has a local descent proof.  At the equality cutoff `X=186`, the
persistent hard source `74` has complete splitless obstruction shadow `{8}`;
root `8` is unhealed and `A_H(46)=0`.  Hence even the first source has no
local resource on the proposed right side.  An infinite `11p-1` fiber rules
out every fixed-capacity canonical-predecessor repair.

No positive-density theorem is claimed.  C94 closes the proposed
analytic-count shortcut and records the exact finite gate.

## 1. Definitions and the C67 identity

Put

\[
 U(n)=2n-1.
\]

A hard root `r` is **persistent through X** when every literal iterate
`U^j(r)<=X` is a hole.  Their number is `A_H(X)`.

A structural splitless root `e` is **healed through X** when some literal
iterate `U^j(e)<=X` is generated.  Since generation is upward closed on a
seed-2 chain, there is then a unique first generated iterate.  Let `D(X)` be
the number of such roots.

For the actual source side consisting of all holes, C67 Lemma C67.1 becomes

\[
 H(X)-Q(X)=A_H(X)-D(X)-B_3(X),                         \tag{4}
\]

where `B_3(X)` counts healed seed-3-root chains.  Indeed, unhealed hard
chains are exactly the persistent hard roots, while healed splitless chains
are exactly the roots counted by `D`.

## 2. Collapse theorem

### Theorem C94.1

Fix any real `alpha>0`.  The following are equivalent:

1. there is a function `R(X)=o(X)` such that, for all sufficiently large
   `X`,
   \[
   D(X)\ge\alpha A_H(X)-R(X);                          \tag{5}
   \]
2. `A_H(X)=o(X)`.

Consequently either statement is equivalent to

\[
 H(X)=o(X),\qquad M(X)=o(X),\qquad
 |G\cap[1,X]|=\frac{2X}{3}+o(X).                       \tag{6}
\]

### Proof

C13 proves that the structural splitless count satisfies `E(X)=o(X)`.
Every root counted by `D` is structural splitless, so

\[
                         0\le D(X)\le E(X)=o(X).       \tag{7}
\]

If (5) holds, then

\[
 \alpha A_H(X)\le D(X)+R(X)=o(X),
\]

and `alpha>0` gives `A_H(X)=o(X)`.

Conversely, if `A_H(X)=o(X)`, choose `R(X)=alpha A_H(X)`.  Then `R=o(X)`
and (5) reduces to `D(X)>=0`.

C72 Theorem 1 and Corollary 2 prove the equivalences in (6), using C13 and
the exact C16 recurrence.  QED.

The proof shows that replacing `alpha>3/4` by any positive constant, however
small, does not weaken the target.  In particular, (4) does not turn the
healed splitless bank into a positive-density reservoir: the whole bank is
already `o(X)`.

## 3. Quantifier audit of C55, C67, and C71

### C55

C55 Theorem 4 states

\[
 \text{for every fixed integer }d,\qquad B_d(X)=o(X), \tag{8}
\]

where `B_d` counts hard holes having at most `d` admissible divisor pairs.
The quantifier `d fixed before X tends to infinity` is essential.  A
diagonal argument permits some unspecified, arbitrarily slowly increasing
threshold `d(X)`, but supplies no prescribed growth rate.

### C67 and C71

C67 isolates the finite terminal budget

\[
 A_H(X)\le e^+(X),\qquad
 e^+(X)=E(X)-E(\lfloor X/2\rfloor).                    \tag{9}
\]

C71 verifies (9) exactly at every cutoff through `10^9`; it does not prove
(9) for unbounded `X`.  Moreover `e^+` counts upper-shell splitless roots
that are automatically unhealed at their birth cutoff.  It is not the
healed bank `D`, and no substitution of `e^+` by `D` follows from C71.

### Reciprocal-mass obstruction to the direct C55+C85 combination

For every prime `p=1 mod 3`, the even allowed value

\[
                         e=p-1
\]

is structural splitless: `e+1=p` has no nontrivial factor pair.  Hence

\[
 \sum_{\substack{e\le X\\e\text{ splitless}}}{1\over e-1}
 \ge
 \sum_{\substack{p\le X+1\\p\equiv1\ (3)}}{1\over p-2}
 =\frac12\log\log X+O(1),                              \tag{10}
\]

where the final equality is Mertens' theorem in the progression `1 mod 3`;
replacing `1/(p-2)` by `1/p` changes the sum by a convergent series.

C85 Corollary C85.2 pays a root set `R` by

\[
 B_d(X)+{X+1\over d+1}\sum_{r\in R}{1\over r-1}.       \tag{11}
\]

The prime-root lower bound in (10) is not sharp for the full structural
bank.  Put

\[
 W_E(X)=\sum_{\substack{e\le X\\e\text{ structural splitless}}}
             {1\over e-1}.
\]

### Lemma C94.2 (reciprocal mass of the structural bank)

There is an absolute constant `c_0>0` such that, for all sufficiently large
`X`,

\[
                         W_E(X)\ge c_0\sqrt{\log X}.   \tag{12}
\]

### Proof

Let `z=X^(1/2)` and let `P_z` be the primes `p<=z`, `p=1 mod 3`.  Every
squarefree product `n` of members of `P_z` satisfies `n=1 mod 3`; when
`n<=X+1`, the value `e=n-1` is structural splitless because every divisor
of `n` is `1 mod 3` and hence forbidden as a factor input.

Give a subset of `P_z` weight `1/n`, where `n` is its product.  Its total
weight is

\[
 Z_z=\prod_{p\in P_z}(1+1/p)\asymp\sqrt{\log z}
     \asymp\sqrt{\log X}.                              \tag{13}
\]

Moreover,

\[
 {1\over Z_z}\sum_n{\log n\over n}
 =\sum_{p\in P_z}{\log p\over p+1}
 ={1\over2}\log z+O(1)
 ={1\over4}\log X+O(1),                              \tag{14}
\]

by Mertens' and the prime number theorem in the progression `1 mod 3`.
Markov's inequality applied to `log n` shows that the products `n<=X`
carry at least `(3/4-o(1))Z_z` of the weight.  Since
`1/(e-1)=1/(n-2)>=1/n`, (12) follows.  QED.

### Lemma C94.3 (the uniform range supplied by C55)

Let `d(h)` be the number of admissible factor pairs of a hard hole.  For
every fixed real

\[
                         0<c<{\log 2\over2},
\]

one has

\[
 \#\{h\le X:h\text{ hard},\ d(h)\le(\log X)^c\}=o(X). \tag{15}
\]

### Proof

C55 Lemma 2 writes `h+1=3^epsilon R` and, with
`k=omega_2(R)`, gives

\[
                         d(h)\ge2^{k-2}-1.
\]

Thus `d(h)<=(log X)^c` implies

\[
 k\le {c\over\log 2}\log\log X+O(1)
   \le (1/2-\eta)\log\log X                           \tag{16}
\]

for some `eta>0`.  The Turan--Kubilius inequality for the additive function
`omega_2`, together with

\[
 \sum_{\substack{p\le X\\p=2\ (3)}}{1\over p}
 ={1\over2}\log\log X+O(1),
\]

shows that the integers satisfying (16) are `O(X/log log X)`, hence `o(X)`.
The map from `h` to `R` has multiplicity at most two, which proves (15).
QED.

For the direct C85 application with `R` containing the full structural
bank, Lemma C94.2 forces its pair threshold `T(X)` to satisfy

\[
                         T(X)/\sqrt{\log X}\longrightarrow\infty. \tag{17}
\]

Lemma C94.3 supplies `B_d(X)=o(X)` only in the range
`d=(log X)^c`, `c<(log 2)/2=0.3465...`, whereas (17) requires an exponent
strictly larger than `1/2`.  There is no overlap.  This does not prove that
a stronger estimate for `B_d` is false; it proves that C55's factor-count
lower bound plus C85's full-bank capacity cannot close the argument.  A new
divisor theorem or a healing-sensitive reduction of the reciprocal root
mass is required.

## 4. Exact finite census

`C94_common_bank_sieve.py` uses the accepted C67 arithmetic constructor but
computes the two chain statistics independently of C67's optimization code.
It records every hard birth, hard-chain death, and splitless-chain death.

| `X` | hard roots | `A_H(X)` | splitless roots `E(X)` | healed `D(X)` | `D/A_H` |
|---:|---:|---:|---:|---:|---:|
| `100000` | `5108` | `3386` | `11928` | `4279` | `4279/3386` |
| `1000000` | `45583` | `27056` | `108651` | `44271` | `44271/27056` |

The all-cutoff scan through `10^6` finds no failure of `4D>=3A_H`.  More
strongly, among every cutoff with `A_H>0`, the exact minimum of `D/A_H` is

\[
                         {5\over6}\quad\text{at }X=186. \tag{25}
\]

At that cutoff the persistent hard roots are

```text
54, 74, 114, 144, 174, 186
```

and the five healed splitless roots are

```text
6, 18, 20, 38, 66.
```

This is the same global-bank bottleneck seen by C65.  Equation (25) is
finite evidence only.

## 5. The quarter-scale map audit

Let `B_H(X)` count hard-root births through `X`, and let `R_H(X)` count hard
roots whose chains have healed through `X`.  Then

\[
                         A_H(X)=B_H(X)-R_H(X).          \tag{18}
\]

### Lemma C94.4 (exact quarter-shell accounting)

For `Y=floor(X/4)`, subtraction gives the exact shell identity

\[
\begin{aligned}
A_H(X)-D(X)-A_H(Y)
={}&B_H(X)-B_H(Y)\\
 &-\bigl(R_H(X)-R_H(Y)\bigr)-D(X).                    \tag{19}
\end{aligned}
\]

Consequently a proof of

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+C             \tag{20}
\]

must pay every hard birth in `(X/4,X]` by a splitless-chain death through
`X`, a hard-chain death in the same shell, or one of `C` exceptions.  Also

\[
 2D(X)-7A_H(Y)=2D(X)-7B_H(Y)+7R_H(Y).                 \tag{21}
\]

Thus the proposed second inequality is a weighted ballot between two units
per splitless death and seven units per still-active hard birth at the
quarter cutoff.

The C92 independent integer sweep checked, at every cutoff through `10^9`,

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+1,            \tag{22}
\]

\[
                         2D(X)\ge7A_H(\lfloor X/4\rfloor). \tag{23}
\]

There were no failures.  C94's independent implementations reproduce every
cutoff through `10^6`; the minimum margin in (22) is zero at `X=186`, and
the minimum margin in (23) is zero only before positive events begin.  This
is exact finite evidence, not an all-`X` lemma.

If (20) held with fixed `C`, iteration on the quarter scale and `D=o(X)`
would give `A_H=o(X)`, hence the full density theorem by C72.  Likewise,
(23) with an `o(X)` error is asymptotically equivalent to `A_H=o(X)`, since
`D=o(X)`.  If both estimates held, then directly

\[
 A_H(X)\le {9\over7}D(X)+o(X),
 \qquad
 D(X)\ge {7\over9}A_H(X)-o(X),                       \tag{24}
\]

and `7/9>3/4`.

### Exact obstruction to a descent-local injection

### Lemma C94.5 (the natural target graph has an isolated source)

Let `D_X` be the set of structural splitless roots healed through `X`, and
let `A_Y` be the set of persistent hard roots through `Y`.  Give a persistent
hard source `h<=X` the natural target neighborhood

\[
       N_X(h)=\bigl(L(h)\cap D_X\bigr)\ \dot\cup\ A_{\lfloor X/4\rfloor},
                                                               \tag{26}
\]

where `L(h)` is its complete C38 splitless obstruction shadow.  Then

\[
                         N_{186}(74)=\varnothing.        \tag{27}
\]

Hence there is no no-exception matching, or even a pointwise map, from all
persistent hard sources into the resources in (20) whose splitless images
must lie in the source's complete descent shadow.  The `+1` in (22) is
necessary for this natural target graph at `X=186`.

### Proof

At `X=186`, the source `h=74` is persistent: its visible chain is

```text
74, 147.
```

The only admissible factorization is `75=5*15`, with `5` generated and
`15` a hole.  The only admissible factorization of `16` is `2*8`, with `2`
generated and `8` structural splitless.  Hence the complete C38 obstruction
shadow is

\[
                         L(74)=L(15)=\{8\}.
\]

But the visible chain

```text
8, 15, 29, 57, 113
```

consists entirely of holes at `186` (root `8` first heals only at `449`),
and `A_H(46)=0`.  Thus `74` has no image in either local resource class on
the right of (22).  The equality in (22) is paid by unrelated healed roots,
so a proof must be genuinely global.  This proves (27).  QED.

There is also an analytic infinite-fiber obstruction to selecting one
canonical predecessor.

### Lemma C94.6 (forced-star counting obstruction)

Let

\[
 \mathcal S_X=\{11p-1:X/2<11p-1\le X,
          \ p>11\text{ prime},\ p\equiv2\pmod3\}.
\]

Then every member of `mathcal S_X` is a persistent hard root at cutoff `X`,

\[
             |\mathcal S_X|\sim {X\over44\log X},       \tag{28}
\]

and every member has the same forced minimum-critical descent

\[
                         11p-1\longrightarrow11\longrightarrow6. \tag{29}
\]

Consequently, any assignment which sends a source to its least critical
factor (`11`) or to the corresponding C44 predecessor (`6`) has an unbounded
top-shell fiber.  In particular, neither assignment can be a bounded-capacity
injection into the resources on the right of (20).

### Proof

C55 Proposition 5 proves that, for every prime `p>11`, `p=2 mod 3`,

\[
 h_p=11p-1
\]

is a hard hole and has the forced minimum-critical descent

\[
                         h_p\longrightarrow11\longrightarrow6.
\]

The prime number theorem in arithmetic progressions gives (28).  Each root
lies above `X/2`, so its first seed-2 child exceeds `X`; since the root itself
is a hole, it is persistent at cutoff `X`.  The common images in (29) prove
the fiber assertion.  QED.

This family is `o(X)`, so it may be discarded in an asymptotic argument; it
nevertheless rules out the two canonical exact local injections suggested by
(22).  A successful map must aggregate genuinely global transition state.

Finally, the C94 factorization type does not determine healing.  Roots `12`
and `18` both have `e+1` prime and `1 mod 3`; at cutoff `186`, root `18` has
healed at `69`, while root `12` remains unhealed (its first death is `5633`).
Any type-only assignment therefore loses the transition state that (19)--
(23) require.

## 6. C94 classification and depth data

The type decomposition at `10^6` is:

| splitless type | all roots | healed roots |
|---|---:|---:|
| factors of `e+1` all `1 mod 3` | `80586` | `33214` |
| `e+1=3s`, factors of `s` all `1 mod 3` | `27978` | `10995` |
| `e+1=p^2`, `p=2 mod 3` | `86` | `61` |
| exceptional `e+1=9` | `1` | `1` |

The first generated member of a healed splitless chain occurs at depths
`1,2,3` for respectively `34760,6909,2159` roots; another `443` roots die
at depths `4` through `9`.  This concentration at short depth is not a
theorem.

### Bounded-depth falsifier

At `X=10^6`, root `2340` is structural splitless and the complete visible
chain is

```text
2340, 4679, 9357, 18713, 37425,
74849, 149697, 299393, 598785.
```

Every displayed value is a hole.  Thus a claim that every splitless root
heals within its first eight seed-2 transitions is false.  The independent
verifier reconstructs this chain directly.

## 7. Independent verification

`C94_common_bank_verify.py` imports neither C67 nor the main C94 script.  It
builds its own smallest-prime-factor table, enumerates every distinct
admissible pair, reconstructs the least closure in ascending order, and
updates chain deaths online.  At both `10^5` and `10^6` it matches the main
counts, the complete all-cutoff `3/4` audit, both quarter-scale gates, and
the local-shadow probe exactly.

Reproduction:

```powershell
python problems/424/compute/wave5/C94_common_bank_sieve.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C94_common_bank_1e6.json

python problems/424/compute/wave5/C94_common_bank_verify.py `
  --limit 1000000 `
  --expected problems/424/compute/wave5/C94_common_bank_1e6.json `
  --output problems/424/compute/wave5/C94_common_bank_verify_1e6.json
```

Both commands were rerun under `python -O`; their corresponding JSON files
are byte-identical.

```text
924B2304FA423D604885055643CDF7BE14CBE4DF4AFEFCFF77410293054C6A1E  C94_common_bank_sieve.py
3425DFF5CB25F073A054B28DEBED717CB6F1E4A583D25BE18025897164BD6E73  C94_common_bank_verify.py
187EE01E2B36FF1DEB28F16A04FCE5B9677367C215710F645CA9B2CDD2A7F0C2  C94_common_bank_1e6.json
9AE4A7E171F7E6A8F7CBE67B94717638D5CE055BAD47C03E4FE6A87DD2A08301  C94_common_bank_verify_1e6.json
```

## 8. Scope

C94 proves a lane obstruction, not Problem 424.  A proof of (1) would solve
the full asymptotic problem because its proposed bank is itself sparse.  A
genuinely weaker analytic target must retain a reservoir not already known
to be `o(X)`, or prove a direct cancellation in (4) without comparing two
sublinear quantities.
