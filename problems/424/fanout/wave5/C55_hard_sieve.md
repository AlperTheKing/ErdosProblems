# C55: analytic hard-hole sieve

## Verdict

No bound

\[
H(X)\le Q(X)+C E(X)+o(X)
\]

is proved here. The C44 scale drop does yield an unconditional analytic
sieve theorem:

> For every fixed `D`, the number of hard holes through `X` having at most
> `D` admissible divisor pairs is `o(X)`. Every other hard hole has more
> than `D` distinct predecessor-hole witnesses below `(h+6)/10`.

This theorem does not use local rank descent. Its missing next step is a
global expansion estimate from the many predecessor witnesses into
distinct healed targets or splitless shadows. Direct incidence summation
has one `O(X)` contribution per dyadic predecessor scale and therefore
does not give a contraction.

There is also an exact obstruction to bounded predecessor multiplicity.
For primes `p = 2 (mod 3)`, `p != 11`, the hard holes

\[
h_p=11p-1
\]

have one admissible pair and minimum critical blocker `11`, hence C44
predecessor `6`. This fiber is unbounded even inside top dyadic shells. At
`X=10^8` the exact minimum-critical fiber over `11` has size `472257`, of
which `223508` lie in `(X/2,X]`.

The stronger global singleton-shadow ballot survives the exact scan:

\[
H_{\{6\}}(x)\le Q_{\ni6}(x)+1\qquad(1\le x\le10^8),
\]

where the source shadow is exactly `{6}` and the target-parent shadow
contains `6`. Its maximum defect is `1` at `x=362`. This is finite
verification, not a theorem.

## 1. Setup

Let

\[
\mathcal A=\{n\ge2:n\not\equiv1\pmod3\},\qquad
\mathcal M=\mathcal A\setminus G.
\]

For an allowed hole `h`, put

\[
\mathcal P(h)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=h+1\}
\]

and write `d(h)=|P(h)|`. A hard hole is a reducible even hole outside the
usable seed-3 class. The obstruction rank and lower-rank splitless shadow
`L(n)` are the C44/C38 definitions.

For each pair in `P(h)`, at least one endpoint is missing. Choose one such
endpoint `p` and put

\[
u={p+1\over2}.                                           \tag{1}
\]

The choices for distinct divisor pairs are automatically distinct because
complementary factor pairs partition the divisors of `h+1`.

## 2. The scale lemma without ranks

### Lemma 1 (disjoint predecessor witnesses)

Every hard hole `h` has at least `d(h)` distinct holes `u` satisfying

\[
2u-1\mid h+1,
\qquad
u\le {h+6\over10}.                                      \tag{2}
\]

### Proof

Put `N=h+1`. Since `h` is even, `N` and every factor in `P(h)` are odd.
An admissible factor cannot equal `3`: its complementary factor would be
allowed and distinct from `3`, making `h` seed-3 easy. Thus both factors
in every admissible pair are at least `5`.

Choose a missing endpoint `p` from each pair. Its cofactor is at least `5`,
so

\[
p\le {N\over5}.
\]

The value `u=(p+1)/2` is allowed. If `u` were generated, the distinct pair
`(2,u)` would generate `p=2u-1`, contradicting that `p` is missing. Hence
`u` is a hole, and

\[
u\le {N/5+1\over2}={h+6\over10}.
\]

No divisor belongs to two complementary pairs, and `p -> (p+1)/2` is
injective. The witnesses are therefore distinct. QED.

C44 additionally permits one endpoint to be chosen critical, in which
case its predecessor drops at least two ranks. Lemma 1 deliberately uses
no rank statement and retains one witness from every divisor pair.

## 3. Bounded-witness hard holes are sparse

For an integer `R`, let `omega_2(R)` be the number of distinct prime
divisors congruent to `2 modulo 3`.

### Lemma 2 (many residue-compatible pairs)

If `h` is hard, then

\[
h+1=3^\epsilon R,qquad \epsilon\in\{0,1\},qquad
R\equiv1\pmod3,qquad 3\nmid R.                         \tag{3}
\]

If `k=omega_2(R)>=2`, then

\[
d(h)\ge 2^{k-2}-1.                                     \tag{4}
\]

### Proof

If `3` does not divide `h+1`, (3) is immediate. If it does, hardness rules
out the admissible seed-3 pair. Apart from the splitless value `h=8`, this
forces `v_3(h+1)=1` and `(h+1)/3 = 1 (mod 3)`, proving (3).

The total multiplicity of prime factors `2 modulo 3` in `R` is even. For
every odd subset `S` of its `k` distinct such primes, let `a_S` be their
squarefree product. Then `a_S = 2 (mod 3)`. Its complement in `h+1` is
also `2 (mod 3)` when `epsilon=0`, and is divisible by `3` when
`epsilon=1`. Hence it is allowed in either case.

There are `2^(k-1)` odd subsets. Passing from ordered divisors to unordered
factor pairs loses a factor of at most two, and excluding a possible equal
pair loses at most one further value. The weaker integral bound (4)
follows. QED.

### Lemma 3 (few `2 modulo 3` prime divisors)

For every fixed `K`,

\[
\#\{n\le X:\omega_2(n)\le K\}=o(X).                    \tag{5}
\]

### Proof

Fix `y` and let `P_y` be the primes `p<=y`, `p=2 (mod 3)`. The density of
integers divisible by at most `K` primes from `P_y` is

\[
\delta_{y,K}=
\prod_{p\in P_y}\left(1-{1\over p}\right)
\sum_{j=0}^K\ \sum_{\substack{S\subseteq P_y\\|S|=j}}
\prod_{p\in S}{1\over p-1}.                            \tag{6}
\]

Put `A_y=sum_(p in P_y) 1/(p-1)`. The inner elementary symmetric sum is at
most `A_y^j/j!`. Also

\[
\prod_{p\in P_y}(1-1/p)\le C e^{-A_y},                 \tag{7}
\]

because `sum_p(1/(p-1)-1/p)` converges. The reciprocal sum over primes
`2 modulo 3` diverges, so `A_y` tends to infinity. Equations (6)-(7) give

\[
\delta_{y,K}\le C e^{-A_y}\sum_{j=0}^K{A_y^j\over j!}
\longrightarrow0.
\]

For each fixed `y`, (6) follows by the Chinese remainder theorem. Taking
first `X -> infinity` and then `y -> infinity` proves (5). QED.

### Theorem 4 (bounded-witness hard-hole sieve)

For every fixed `D`,

\[
\#\{h\le X:h\text{ hard and }d(h)\le D\}=o(X).         \tag{8}
\]

Consequently, outside `o(X)` exceptions, every hard hole has more than
`D` distinct predecessor-hole witnesses satisfying (2).

### Proof

By (4), `d(h)<=D` bounds `omega_2(R)` by a constant depending only on
`D`. Lemma 3 bounds the possible shifted values `R`, and hence `h`, by
`o(X)`. Lemma 1 supplies the final assertion. QED.

## 4. Why the dyadic double count stops

Let `W_X` be the bipartite incidence graph from hard holes `h<=X` to all
predecessor witnesses `u` in Lemma 1, and put

\[
Y=\left\lfloor{X+6\over10}\right\rfloor.
\]

For fixed `u`, every adjacent source satisfies

\[
h+1=(2u-1)m,
\]

so

\[
\deg_{W_X}(u)\le\left\lfloor{X+1\over2u-1}\right\rfloor. \tag{9}
\]

If `B_D(X)` denotes the left side of (8), double counting gives the valid
global sieve inequality

\[
H(X)\le B_D(X)+{1\over D}
\sum_{\substack{u\le Y\\u\in\mathcal M}}
\left\lfloor{X+1\over2u-1}\right\rfloor.               \tag{10}
\]

The first term is `o(X)` for each fixed `D`. The second term is the exact
obstruction. With no harmonic estimate for the hole set, its elementary
bound is `O(X log X/D)`. Equivalently, each dyadic interval `U<u<=2U`
has at most `O(X)` right incidence, and there are `O(log X)` intervals.

Theorem 4 permits `D` to be any fixed constant before taking the limit; it
does not provide a uniform estimate with `D` growing fast enough to remove
the logarithm. More importantly, (10) has no `Q` term and does not control
how the predecessor holes share splitless shadows. Thus disjoint divisor
witnesses alone do not prove a contraction.

## 5. Exact forced-star obstruction

### Proposition 5 (the `11p-1` star)

Let `p=5` or let `p>11` be prime with `p=2 (mod 3)`. Then

\[
h_p=11p-1
\]

is a rank-two hard hole with the unique admissible pair `(11,p)`. Its
minimum critical endpoint is `11`, its C44 predecessor is `6`, and its
minimum-critical descent is

\[
h_p\longrightarrow11\longrightarrow6.                 \tag{11}
\]

### Proof

The value `6` is splitless because `7` is prime. The only admissible pair
for `11` is `(2,6)`, so `11` is a rank-one hole. Unique factorization gives
`P(h_p)={(11,p)}`; the inputs are distinct because `p!=11`. Both factors
are allowed, while `11` blocks generation. Also `h_p` is even and divisible
by `3`, so it is hard.

If `p` is generated, `11` is the only missing endpoint. If `p` is a hole,
its seed-2 predecessor is missing, so `rho(p)>=1`. In both cases the pair
blocker score is one, `rho(h_p)=2`, and the least critical endpoint is
`11`. Equation (11) follows. QED.

The prime number theorem in arithmetic progressions gives

\[
\#\{h_p\le X\}\sim {X\over22\log X},
\]

and the count in `(X/2,X]` is asymptotic to `X/(44 log X)`. Hence the
minimum-critical predecessor fiber over `6` is unbounded in every top
dyadic shell. Bounded capacity per critical predecessor, per selected
descent leaf, or per direct seed-2 exit is therefore false.

The direct seed-2 chain is shared:

\[
6\to11\to21\to41,
\]

where `41` is generated via `(3,14)`. It supplies one local `Q` exit, not
one exit per source.

This star is sparse by Theorem 4, so it does not disprove a scalar
`Q+o(X)` estimate. It proves that a successful estimate must either absorb
low-divisor cofactors analytically or use genuinely global `Q` targets.

## 6. Exact computation through `10^8`

`C55_hard_sieve.py` embeds a C++ kernel, compiles it in a temporary
directory, and writes JSON only to stdout. It reconstructs `G` in ascending
order, computes obstruction ranks and shadows, and enforces `a<b` whenever
a factor pair is admitted.

| `X` | hard `H` | `d(h)=1` | all-hole | min-critical fiber `11` | fiber in `(X/2,X]` | prime star | generated-prime star |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^5` | `5108` | `3011` | `1004` | `911` | `418` | `566` | `350` |
| `10^6` | `45583` | `25427` | `7083` | `7043` | `3246` | `4411` | `3351` |
| `10^7` | `392961` | `214713` | `43447` | `56725` | `26584` | `35998` | `31028` |
| `10^8` | `3368726` | `1838052` | `251139` | `472257` | `223508` | `304162` | `278968` |

At `10^8`, the exact admissible-pair histogram for hard holes is

| pairs | `1` | `2` | `3-4` | `5-8` | `9-16` |
|---:|---:|---:|---:|---:|---:|
| count | `1838052` | `1315004` | `207196` | `8339` | `135` |

The maximum is `12`. The corresponding number of distinct missing
endpoints has histogram

| endpoints | `1` | `2` | `3-4` | `5-8` | `9-16` | `17` |
|---:|---:|---:|---:|---:|---:|---:|
| count | `1609629` | `1237864` | `445355` | `74319` | `1558` | `1` |

Thus the asymptotic theorem (8) has very slow finite onset: more than half
the hard holes at `10^8` still have one admissible pair.

The minimum missing-factor fiber over `11` has size `728173`. The subset
with a unique pair and a generated cofactor has size `308779`, including
`149192` in the top half. For these sources `11` is the only missing
divisor witness, so alternative blocker selection cannot split the fiber.

The prime star has `304162` sources, including `144682` in the top half.
Exactly `278968` cofactors are generated, including `134901` in the top
half. C13's related count `278970` includes primes `2` and `3`; their
outputs are not hard, so C55 excludes both.

## 7. The global singleton-shadow gate

Let

\[
H_{\{6\}}(X)=\#\{h\le X:h\text{ hard},\ L(h)=\{6\}\},
\]

and let `Q_{ni6}(X)` count healed target parents `q` whose splitless shadow
contains `6`, with the usual child cutoff `2q-1<=X`.

The exact sweep checks every hard event and finds

\[
H_{\{6\}}(x)-Q_{\ni6}(x)\le1
\quad\text{for every }x\le10^8.                         \tag{12}

The maximum is first attained at `x=362`, with `(H_6,Q_6)=(4,3)`. At the
endpoint,

\[
H_{\{6\}}(10^8)=336564,
\qquad
Q_{\ni6}(10^8)=1962543.                                \tag{13}

The `10^7` values `(39603,238937,1)` reproduce C38 exactly. Equations
(12)-(13) show why the raw fiber falsifier is not a scalar counterexample:
global targets from outside the direct chain can pay the singleton shadow.
They do not prove that the same expansion holds simultaneously for unions
of splitless shadows. C38 already gives finite Hall cuts where such unions
defeat every tested capacity through `40`.

## 8. Reproduction and precise obstruction

From the repository root:

```powershell
python problems/424/fanout/wave5/C55_hard_sieve.py --limit 1000000
python problems/424/fanout/wave5/C55_hard_sieve.py --limit 100000000
```

The `10^6` run independently matches C49 on `H`, mixed/all-hole counts,
unique pairs, maximum rank, and the critical `11` fiber `7043`. The
`10^7` singleton-shadow fields match C38. At `10^8`, `|G|=51899129` and
`H=3368726` match the accepted census and C25.

Embedded-kernel SHA-256:

```text
A88D15117037B053E974F96A317BDC5C986DA04505181D078040EC8DA5B2A547
```

Checked-in script SHA-256:

```text
B295E5CFF1CF391B8314C84F1ED21497E4572F9C4AC353F46A73A5E5EA628F2B
```

The exact remaining obstruction is a uniform shadow-expansion inequality.
For every collection `U` of splitless leaves, one would need to bound all
hard sources whose predecessor shadows are trapped in `U` by the healed
targets whose shadows meet `U`, plus `C|U|` (and an analytically sparse
error). Theorem 4 controls hard sources with few divisor witnesses, but it
does not control concentration of many witnesses into the same `U`.
Equation (10) records this failure quantitatively. No local rank descent,
pointwise predecessor capacity, or dyadic divisor count supplies the
missing global `Q` expansion.
