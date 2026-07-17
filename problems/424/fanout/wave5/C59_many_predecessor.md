# C59: many-predecessor stratification versus dyadic contraction

## Verdict

The C55 predecessor witnesses give a rigorous dyadic incidence inequality,
but the resulting uncorrelated pair-threshold argument does not prove an
eventual C54 coefficient below `2`.

Let

\[
 I_j=\sum_{\substack{u\in\mathcal M\\
                     u\le(2^j+6)/10}}
 \left(
 \left\lfloor{2^j+1\over2u-1}\right\rfloor-
 \left\lfloor{2^{j-1}+1\over2u-1}\right\rfloor
 \right).
\]

If `B_(j,D)` is the number of hard holes `h in (2^(j-1),2^j]`
having at most `D` admissible divisor pairs, then the exact theorem is

\[
 \boxed{
 h_j\le B_{j,D}+{I_j\over D+1}.
 }                                                        \tag{C59.1}
\]

Consequently C54 gives

\[
 \boxed{
 r_j\le m_{j-1}+s_j-q_j+B_{j,D}+{I_j\over D+1}.
 }                                                        \tag{C59.2}
\]

This is the strongest bound obtained by counting each C55 predecessor
independently and using only its source capacity. It has two incompatible
threshold scales:

* the quantitative C55 sieve makes `B_(j,D)=o(2^j)` for
  `D=(log 2^j)^c` whenever `c<log(2)/2=0.34657...`;
* the ambient dyadic capacity is

  \[
  I_j^{\rm amb}=\left({1\over6}+o(1)\right)2^j\log 2^j,
  \]

  so an ambient-capacity proof needs `D` of order `log 2^j` merely to
  obtain an `O(2^j)` error, and needs `D/log 2^j -> infinity` for an
  `o(2^j)` error.

The exponent gap is therefore

\[
 1-\frac{\log2}{2}=0.65342\ldots .                      \tag{C59.3}
\]

It is not a defect of floor estimates. Actual structural splitless holes
already contribute

\[
 \left({1\over8}+o(1)\right)2^j\log\log 2^j
\]

to `I_j`. Thus every fixed-`D` capacity bound diverges after normalization
by `2^j`.

The conclusion is scoped: divisor-pair stratification plus independent
predecessor capacities cannot close C54. A correlated incidence theorem
which removes non-witness multiples, or which credits the same structure
to `q_j`, could still close the problem.

## 1. Exact dyadic incidence theorem

Put `X=2^j`. For a hard hole `h`, let `d(h)` be its number of admissible
unordered factorizations

\[
 h+1=ab,\qquad 2\le a<b,\qquad a,b\in\mathcal A.
\]

For every such pair, at least one endpoint is a hole. Choose one missing
endpoint `p`. Hardness excludes the seed-3 factor, so the other endpoint
is at least `5`. Since `h+1` is odd, `p` is odd. C55 then gives

\[
 u={p+1\over2}\in\mathcal M,qquad
 u\le{h+6\over10},qquad 2u-1\mid h+1.                 \tag{1}
\]

The chosen values `u` are distinct as the divisor pairs vary: two
different unordered factor pairs have disjoint endpoint occurrences, and
`p -> (p+1)/2` is injective.

For fixed `u`, the number of possible `h in (X/2,X]` satisfying
`2u-1 | h+1` is exactly

\[
 \Delta_j(u)=
 \left\lfloor{X+1\over2u-1}\right\rfloor-
 \left\lfloor{X/2+1\over2u-1}\right\rfloor.           \tag{2}
\]

Every hard source with `d(h)>D` supplies at least `D+1` distinct
incidences `(h,u)`. Summing source degrees and then applying (2) proves

\[
 (D+1)(h_j-B_{j,D})\le I_j,
\]

which is (C59.1). Substitution in the exact C54 identity

\[
 r_j=m_{j-1}+s_j+h_j-q_j
\]

proves (C59.2). No asymptotic estimate or matching assumption enters this
argument.

There is also the exact shell-profile bound

\[
 I_j\le
 \sum_{i\le j-3}m_i\left(2^{j-i-1}+1\right).           \tag{3}
\]

Indeed, `(X+6)/10 <= X/8` for `j>=5`, while `u in (2^(i-1),2^i]`
implies `2u-1>=2^i+1` and hence
`Delta_j(u)<=2^(j-i-1)+1`. With `a_i=m_i/2^i`, (3) becomes

\[
 {I_j\over2^j}\le {1\over2}\sum_{i\le j-3}a_i
                  +{M(2^{j-3})\over2^j}.              \tag{4}
\]

Equation (4) is the precise harmonic congestion: one normalized hole
density contribution is paid at every earlier dyadic scale.

## 2. Quantitative low-pair range

C55 proves that if `k` is the number of distinct prime divisors congruent
to `2 modulo 3` in the non-3 part of `h+1`, then

\[
 d(h)\ge2^{k-2}-1.                                    \tag{5}
\]

The Turan-Kubilius theorem gives

\[
 k=\left({1\over2}+o(1)\right)\log\log X
\]

outside `o(X)` integers through `X`. Therefore, if

\[
 D(X)=\lfloor(\log X)^c\rfloor,qquad c<\frac{\log2}{2},
\]

then `d(h)<=D(X)` forces

\[
 k\le {c\over\log2}\log\log X+O(1)
     <\left({1\over2}-\epsilon\right)\log\log X
\]

for some fixed positive `epsilon`. Hence

\[
 B_{j,D(2^j)}=o(2^j).                                  \tag{6}
\]

This is a genuine growing-threshold extension of the fixed-`D` C55
theorem. It is still far below the threshold required by (3): inserting
(6) and the ambient estimate below in (C59.1) gives only

\[
 h_j\le o(2^j)+O\left(2^j(\log 2^j)^{1-c}\right),
\]

which is weaker than the trivial linear bound.

## 3. Sharp harmonic calculations

### Ambient capacity

Let `A={u>=2:u not congruent to 1 modulo 3}` and replace the holes in
`I_j` by all allowed predecessors. Uniformly for `u<=X/10`,

\[
 \Delta_j(u)={X\over2(2u-1)}+O(1)
             ={X\over4u}+O\left({X\over u^2}+1\right).
\]

Also

\[
 \sum_{\substack{u\le X/10\\u\in A}}{1\over u}
 ={2\over3}\log X+O(1).
\]

Summation gives the sharp formula

\[
 \boxed{
 I_j^{\rm amb}=\left({1\over6}+o(1)\right)X\log X.
 }                                                        \tag{7}
\]

Thus an uncorrelated argument based on the ambient capacity needs
`D=Omega(log X)` to produce even `O(X)`.

### An actual-hole contribution

For every prime `q congruent to 1 modulo 3`, the value `u=q-1` is allowed
and splitless, since `u+1=q` has no factorization. Hence `u` is an actual
hole. The corresponding part of `I_j` is

\[
 \sum_{\substack{q\le X/10+1\\q\equiv1\ (3)}}
 \Delta_j(q-1).
\]

Mertens' theorem in arithmetic progressions gives

\[
 \sum_{\substack{q\le y\\q\equiv1\ (3)}}{1\over q}
 ={1\over2}\log\log y+O(1).
\]

Since `2u-1=2q-3`, the same floor calculation proves

\[
 \boxed{
 \sum_{\substack{q\le X/10+1\\q\equiv1\ (3)}}
 \Delta_j(q-1)
 =\left({1\over8}+o(1)\right)X\log\log X.
 }                                                        \tag{8}
\]

Equation (8) is an exact structural obstruction to combining the
fixed-threshold C55 theorem directly with C54: even a guaranteed subset of
the actual predecessor holes gives unbounded normalized raw capacity.

## 4. Exact hard-shaped control family

The threshold `D` cannot simply be raised to order `log X` and still be
declared sparse by divisor statistics. Consider

\[
 h=30k+24,\qquad h+1=5(6k+5).                           \tag{9}
\]

For `k>=1`, `(5,6k+5)` is a distinct admissible pair. Also `h` is even,
`h congruent to 0 modulo 3`, and `h+1` is not divisible by `3`. Therefore
every member of (9) is hard-shaped: if it is a hole, it belongs to the
hard class.

The number of members of (9) in `(X/2,X]` is `X/60+O(1)`. Moreover

\[
 d(h)\le {\tau(h+1)\over2}.
\]

The normal order

\[
 \log\tau(n)=(\log2+o(1))\log\log n
\]

implies that all but `o(X)` members of (9) satisfy

\[
 d(h)=(\log X)^{\log2+o(1)}=o(\log X).                 \tag{10}
\]

Thus the threshold scale needed to absorb (7) contains a positive-density
family of hard-shaped candidates. Divisor statistics alone cannot show
that its hole members are sparse; doing so would require new information
from grounded closure.

This does not assert that the progression (9) contains a positive density
of actual hard holes. It is a falsifier to the proposed divisor-only
low-pair estimate, not to the desired density theorem.

## 5. Exact census

The checked C++ audit reconstructed `G` by ascending divisor recursion
through `2^27=134,217,728`. It enforced `a<b`, checked (C59.1) for every
threshold at every dyadic shell `7<=j<=27`, and checked the C54 identity.
An independent Python trial-division implementation passed `880` checks
through `2^16`.

Here `D_s=floor(j^(1/3))`; this is a concrete sieve-safe exponent because
`1/3<log(2)/2`. The column `theta_s` is the right side of (C59.2), divided
by `m_(j-1)`, using `D_s`. The column `theta_j` uses the capacity-absorbing
choice `D=j`.

| `j` | true `r_j/m_(j-1)` | `I_j/m_(j-1)` | `D_s` | `theta_s` | `theta_j` | AP count with `d<=j` / total |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | `4591/4602` | `50701/4602` | 2 | `64174/13806` | `128748/78234` | `1092/1092` |
| 20 | `45629/54172` | `1013284/54172` | 2 | `1145530/162516` | `1971493/1137612` | `17476/17476` |
| 24 | `502102/687297` | `18599775/687297` | 2 | `20045442/2061891` | `31152325/17182425` | `279620/279620` |
| 27 | `3223210/4850573` | `160453536/4850573` | 3 | `172923924/19402292` | `250703416/135816044` | `2236896/2236962` |

The sieve-safe upper coefficient is below `2` only at `j=7,8` and fails
at every tested shell `9<=j<=27`; at `j=27` it is
`8.91255...`. The choice `D=j` is below `2` at every tested shell, but at
`j=27` it puts all `2,114,256` actual hard holes into `B_(j,D)`. It also
contains `2,236,896` of the `2,236,962` progression candidates in (9).
This is exactly the illegal step that a quantitative proof would need to
justify.

A simpler proposed capacity inequality is already exactly false:

\[
 I_j\le j m_{j-1}.                                      \tag{11}
\]

Its first failure in the audit is `j=22`, where

\[
 I_{22}=4,371,557
 >22(190,632)=4,193,904.
\]

At `j=27`, `I_j/(j m_(j-1))=1.225159...`. The structural-prime part in
(8) alone equals `36,991,222`; the full actual-hole capacity is
`160,453,536`.

## 6. Reproduction

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic `
  problems/424/fanout/wave5/C59_exact_stratification.cpp `
  -o $env:TEMP/C59_exact_stratification.exe

& $env:TEMP/C59_exact_stratification.exe 134217728 `
  problems/424/fanout/wave5/C59_stratification_2p27.json

python problems/424/fanout/wave5/C59_verify.py `
  problems/424/fanout/wave5/C59_stratification_2p27.json `
  --limit 65536

python problems/424/fanout/wave5/C59_summarize.py `
  problems/424/fanout/wave5/C59_stratification_2p27.json `
  --output problems/424/fanout/wave5/C59_summary_2p27.json
```

SHA-256:

```text
C59_exact_stratification.cpp  99F2D9ECED314E02A1C88DF0C4EB99076117D4F4C50E562ADDB3BF1672FEDCF5
C59_stratification_2p27.json   A615F4569BF08A108A68D9E6D282F14A56427168385E0C88D25D31556A65FAC2
C59_verify.py                  DB32E2DC1EFF6B21B814A1CDEF639936C6712E05194E2CBCA03EE6F04939B783
C59_verify_2p16.json           BF1A75E7F94FA9F557A4808016133F4B5A904B189531D7AA6E2F6DCF1A116C8D
C59_summarize.py               4B8CCB4990E3593C8276F06AD057E324171175B784EC78528B8E9291D5076CDE
C59_summary_2p27.json          AE09F0B162F96D70888EC9F6091D4A8F9D7C85CE5E6E0F71826E6F5F7A310528
```

No eventual `theta<2`, density bound, or estimate involving `Q` is claimed.
The precise missing input is a correlated incidence inequality that charges
only divisor multiples which are genuine hard-source witnesses and couples
their congestion to healed seed-2 exits.
