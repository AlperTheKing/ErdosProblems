# C16: hole contraction reduction and exact obstruction

## Verdict

No aggregate contraction with a fixed coefficient below `2` is proved here.
There is, however, an exact two-scale reduction with reciprocal scale sum
`1/2+1/3=5/6`. It isolates one concrete cross-parity inequality, (HC)
below, which would imply

\[
 M(X)=o(X).
\]

The reduction is rigorous. The inequality (HC) is not proved. It passed
every integer cutoff through `10^9`, with an independent replay through
`10^5`, but a factor-local proof of it is impossible: its first hard hole
already has no eligible local target, and the missing endpoint `11` has an
exact forced hard fiber of size `2,493,479` through `10^9`.

Thus the output of this lane is a proved reduction, an exact falsifier for
local charging, and a precise remaining obstruction. No density theorem is
claimed.

## 1. Exact partition

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},\qquad
 \mathcal M=\mathcal A\setminus G,
\]

and write `M(X)` for the number of members of `mathcal M` through `X`.
Let `E(X)` be the splitless count from C13, and put

\[
 R(X)=M(X)-E(X).
\]

Thus `R(X)` counts the reducible holes. Set

\[
 Y=\left\lfloor{X+1\over2}\right\rfloor,\qquad
 Z=\left\lfloor{X+1\over3}\right\rfloor.
\]

Partition the reducible holes through `X` into the following three sets.

* `O_X`: the odd holes.
* `S_X`: the even holes `n` for which `3 | n+1`,
  `q=(n+1)/3` is allowed, and `q != 3`.
* `H_X`: all remaining reducible holes.

Write `O(X),S(X),H(X)` for their cardinalities. The set `H_X` is the hard
even, seedless part of the partition. Finally define the seed-2 healing
capacity

\[
 Q(X)=\#\{m\in\mathcal M:m\le Y,\ 2m-1\in G\}.              \tag{1}
\]

### Lemma 1 (exact seed partition)

For every integer `X >= 2`,

\[
 O(X)+Q(X)=M(Y),                                             \tag{2}
\]

\[
 S(X)\le M(Z),                                               \tag{3}
\]

and

\[
 R(X)=M(Y)-Q(X)+S(X)+H(X).                                  \tag{4}
\]

Consequently,

\[
 R(X)-M(Y)-M(Z)
 =H(X)-Q(X)-\bigl(M(Z)-S(X)\bigr).                          \tag{5}
\]

**Proof.** If an odd allowed `n` is missing, then

\[
 n=2m-1,\qquad m=(n+1)/2\in\mathcal A.
\]

The inputs are distinct for every missing `n`. If `m` were in `G`, closure
with the seed `2` would put `n` in `G`; hence `m` is missing. Conversely,
for every missing `m <= Y`, the allowed child `2m-1 <= X` is either missing
or generated. These alternatives are exactly `O_X` and the set counted by
(1), proving (2).

For `n in S_X`, the pair `3,q` is admissible. If `q` were generated, closure
would generate `n=3q-1`. Hence `q` is missing. The map `n -> q` is injective
and has image in `mathcal M intersect [1,Z]`, proving (3).

The sets `O_X,S_X,H_X` partition the reducible holes, so
`R=O+S+H`. Substitute (2) to obtain (4), then subtract `M(Y)+M(Z)` to obtain
(5). QED.

### Corollary 2 (one exact sufficient frontier)

Either of the following eventual estimates implies `M(X)=o(X)`:

\[
 H(X)\le Q(X),                                               \tag{HC}
\]

or, more generally,

\[
 H(X)-Q(X)\le M(Z)-S(X)+o(X).                               \tag{HC'}
\]

**Proof.** Equation (5) gives

\[
 R(X)\le M(Y)+M(Z)+o(X).
\]

C13 proves `E(X)=o(X)`, so

\[
 M(X)\le M(Y)+M(Z)+o(X).                                   \tag{6}
\]

Let `delta=limsup M(X)/X`. Divide (6) by `X` and take limsups:

\[
 \delta\le\left({1\over2}+{1\over3}\right)\delta
 ={5\over6}\delta.
\]

Thus `delta=0`. QED.

This is materially different from a coefficient-`lambda` charge to one
half-scale copy: the two target scales have total normalized weight `5/6`.

## 2. Exact local obstruction

The natural attempt to prove (HC) is to send a hard hole to a missing factor
of `n+1` which is counted by `Q(X)`. It fails before any fiber issue arises.

### Proposition 3 (first isolated source)

At `X=54`,

\[
 H_X=\{54\},\qquad Q_X=\{21\},                              \tag{7}
\]

while

\[
 54+1=5\cdot11                                               \tag{8}
\]

is the unique admissible split. Its only missing endpoint is `11`, and
`11` is not counted by `Q_X` because `2*11-1=21` is also missing. Moreover,
`21` does not divide `55`.

Hence the bipartite relation

```text
hard n  --  healed missing divisor m of n+1
```

has an isolated source at `n=54`. No matching, canonical-factor choice, or
bounded-capacity charge using that relation can prove (HC).

**Proof.** The exact ascending recursion gives `5 in G`, `11 notin G`,
`21 notin G`, and `41=3*14-1 in G`. Since `55=5*11`, (8) is its only
nontrivial factor pair, so `54` is a reducible hard hole. Thus `21` is a
healed missing parent because `2*21-1=41 in G`. Exact enumeration below
checks that it is the only such parent through `Y=27`. The remaining claims
follow directly. QED.

There is also a rule-independent unbounded version of the obstruction.

### Proposition 4 (forced hard fiber at 11)

Let `p >= 5` be an ordinary prime in `G`. Then

\[
 h_p=11p-1
\]

is a hard hole, `h_p+1` has the unique admissible split `11*p`, and its only
missing endpoint is `11`.

**Proof.** The value `11` is missing. A generated prime `p >= 5` is `2`
modulo `3`, as is `11`; hence `h_p` is an allowed even multiple of `3`.
The two distinct ordinary primes `11,p` give the unique nontrivial factor
pair of `11p`. One endpoint is missing, so the exact membership recursion
makes `h_p` missing. It is reducible, is not odd, and cannot belong to the
seed-3 class because it is `0` modulo `3`. Thus it is hard. QED.

The exact censuses have `278,968` such hard holes through `10^8` and
`2,493,479` through `10^9`. These are the C13 forced fibers with the two
non-hard outputs from `p=2,3` removed. They are finite counts, not a claim
that `G` contains infinitely many primes.

## 3. Precise remaining inequality

Membership recursion rewrites (1) as

\[
 Q(X)=\#\{m\le Y:m\in\mathcal M,
       \ 2m=ab\text{ for some }2\le a<b,\ a,b\in G\}.       \tag{9}
\]

Thus (HC) does not compare two copies of the same local factor relation.
It compares

* blocked admissible factorizations of odd integers `n+1`, counted by `H`;
* represented even products `2m` whose half `m` is nevertheless missing,
  counted by `Q`.

Propositions 3 and 4 show that the first class cannot be assigned to the
second through missing endpoints with bounded fibers. Proving (HC) requires
a genuinely nonlocal cross-parity product-support estimate. None of the
closure implications used in Lemma 1 supplies such an estimate: they give
the exact identity (5), but leave the sign of `H-Q` uncontrolled.

This is the precise obstruction in this lane.

## 4. Exhaustive checks

The C++ audit reconstructs `G` by exact ascending divisor recursion and tests
every integer cutoff. The quantities relevant to (HC) are:

| `X` | `H(X)` | `Q(X)` | `S(X)` | `M(Y)` | `M(Z)` |
|---:|---:|---:|---:|---:|---:|
| 100 | 2 | 3 | 4 | 21 | 13 |
| 1,000 | 41 | 46 | 51 | 214 | 146 |
| 10,000 | 518 | 593 | 353 | 1,837 | 1,280 |
| 100,000 | 5,108 | 6,783 | 2,046 | 14,524 | 10,122 |
| 1,000,000 | 45,583 | 67,537 | 10,087 | 112,283 | 78,173 |
| 10,000,000 | 392,961 | 637,270 | 49,109 | 904,635 | 623,682 |
| 100,000,000 | 3,368,726 | 5,948,614 | 260,959 | 7,690,740 | 5,258,414 |
| 1,000,000,000 | 29,010,146 | 55,583,430 | 1,536,871 | 67,876,334 | 46,166,704 |

At every `2 <= X <= 10^9`, both

\[
 H(X)\le Q(X)                                                \tag{10}
\]

and

\[
 R(X)\le M(Y)+M(Z)                                          \tag{11}
\]

hold. This is finite verification only. By contrast, the one-scale
capacity-one inequality `R(X)<=M(Y)` first fails at `X=32`, as in C13.

An independent Python implementation using `generator_b` replayed every
cutoff through `10^5`; it obtained

```text
M=26823, E=11928, R=14895,
O=7741, S=2046, H=5108, Q=6783,
forced hard fiber at 11=350.
```

## 5. Reproduction

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave3/C16_hole_contraction/hole_contraction.cpp -o problems/424/compute/wave3/C16_hole_contraction/hole_contraction.exe
problems/424/compute/wave3/C16_hole_contraction/hole_contraction.exe 1000000000 problems/424/compute/wave3/C16_hole_contraction/result_1e9.json
python problems/424/compute/wave3/C16_hole_contraction/verify_small.py --limit 100000 --output problems/424/compute/wave3/C16_hole_contraction/result_small.json
```

SHA-256:

```text
hole_contraction.cpp  AA0430765F8AB4F82223A53F0FDA21D2BAC592727231F1942F47F7745BF7087A
verify_small.py       02D3028B3D36793F7251884388C2B10BC8870B3CDC73699A2D264FB92A9E7A6C
result_1e8.json       0E7690DE0ED0CB7906F14285450B9997D133A08D06A087028995C78A9E78766D
result_1e9.json       31CDBC1DCFAE60D1177F238E0013D6790659153CC3B170C7FADD4E0B287D3B47
result_small.json     6B01C73CD7423AC6D27B011C18258B5B7F6090C21FB98A832CC6E9A322FA8F07
```
