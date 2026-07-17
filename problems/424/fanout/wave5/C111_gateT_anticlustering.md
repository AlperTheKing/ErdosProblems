# C111: fixed-L Gate T anti-clustering

## Direct route

1. **Exact final deliverable.** For the `(3,2,1)` ray, prove Gate T with
   explicit integers `L,K0` and rational `eta>0`; construct an explicit
   infinite family forcing the retained fraction to have liminf zero for
   every fixed `L`; or prove a quantified asymptotic upper bound on edge mass
   in growing-multiplicity fibres that is strictly stronger than R9.
2. **Frontier.** Control the labelled edge mass in the dispersed regime
   `L < r_K(z) <= exp(o(K))`; R9 already excludes concentration on fewer than
   `60^((1-delta)K)` products and gives only a pointwise divisor bound.
3. **Logical bridge.** A uniform estimate
   `sum_{r_K(z)>L} r_K(z) <= (1-eta)N_K` proves Gate T directly. An explicit
   scalable collision family covering `1-o(1)` of edges refutes it. A
   distributional tail estimate for a growing cutoff is a strictly stronger
   asymptotic lemma because it removes edge mass from part of R9's unresolved
   medium-fibre regime.
4. **Next falsifiable action.** Derive the exact suffix congruences for a
   collision and exhaust the smallest exact layers to test whether channel,
   color, and a bounded suffix signature leave only uniformly many coprime
   swaps per edge.
5. **Exit condition.** Exit this route upon an explicit Gate-T proof, an
   explicit infinite falsifier, or a proved quantified distributional tail
   lemma. If bounded suffix signatures admit collision degree growing with
   every tested depth and no mass estimate follows, record the missing bridge
   and stop that branch rather than adding another equivalent encoding.

## Action log

`2026-07-13T20:31:42.0583982+03:00 > ATTACK | NEXT: test bounded suffix signatures against exact labelled fibres and coprime swaps.`

`2026-07-13T20:41:02.7296481+03:00 > ATTACK | NEXT: extract all Q=360 K=4 fibres from 60,512,841 labelled edges with 32 workers.`

`2026-07-13T20:43:20.2825224+03:00 OK ATTACK | DID: exact Q=360 K=4 product sort | RESULT: 15,931 repeated fibres; max multiplicity 3; C111_collision_extract.json | D: none`

`2026-07-13T20:43:20.2825224+03:00 > VERIFY | NEXT: check suffix ambiguity and the divisor-moment tail gate for q=1..4 and K=2..4 using exact integers.`

`2026-07-13T20:48:31.8592167+03:00 OK VERIFY | DID: normal and -O exact verifier runs | RESULT: identical SHA-256 867B732D9460EB3A821860FE589FAF8E17D297BA6326ADAF5F2698E43C41FE7F | D: none`

`2026-07-13T20:48:31.8592167+03:00 FAIL ATTACK | DID: six-letter suffix decoder test | RESULT: 30 collision pairs retain common suffixes on both factors | D: DEAD: bounded-suffix uniqueness`

`2026-07-13T20:48:31.8592167+03:00 > PLAN | NEXT: prove the exact divisor-moment edge-tail inequality and its optimized subexponential corollary.`

## Verdict

The fixed-`L` Gate T is not proved, and no infinite falsifier is found.
There is, however, a genuinely stronger quantified anti-clustering lemma
than R9: apart from an exponentially small fraction of labelled edges, every
fibre has multiplicity at most

\[
 \exp\!\left(\bigl((\log 2)(\log 6)+\varepsilon\bigr)
                  {K\over\log K}\right).                         \tag{1}
\]

This is a distributional edge-mass statement, not another pointwise divisor
bound. It removes almost all edge mass from the upper part of R9's unresolved
subexponential regime. Its nonasymptotic form is an exact integer inequality
valid for every `K,q,T`.

The attempted bounded-suffix decoder fails before the theorem: in the exact
`Q=360,K=4` block, 30 collision pairs admit the same complete six-letter
suffix word on each of their two factors. Conditioning on one ray block
therefore does not make products injective.

## 1. Exact edge-tail theorem

Retain the notation in the prompt, put

\[
 \iota_K=|I_K|,\qquad
 M_K(T)=\sum_{z:r_K(z)>T}r_K(z),                       \tag{2}
\]

and define the integer

\[
 J_K=1+\left\lceil\log_2(36\cdot360^K)\right\rceil. \tag{3}
\]

### Theorem 1 (nonasymptotic divisor-moment tail gate)

For every `K>=2` and all positive integers `q,T`,

\[
 \boxed{\;
 T^q M_K(T)
 \le 972\,\iota_K\,360^K J_K^{\,2(2^q-1)} .
 \;}                                                        \tag{4}
\]

Using only the exact block-code lower bound from R9 gives

\[
 \boxed{\;
 {M_K(T)\over N_K}
 \le \min\left\{1,\,
 {3888\,6^K J_K^{\,2(2^q-1)}\over T^q}\right\}.
 \;}                                                        \tag{5}
\]

No positive-density hypothesis, Gate A, energy bound, or pointwise
injectivity is assumed.

### Corollary 2 (quantified subexponential anti-clustering)

Let

\[
 A=(\log2)(\log6).
\]

For `K` sufficiently large define

\[
 q_K=\left\lfloor\log_2 {K\over(\log K)^3}\right\rfloor,
 \qquad
 T_K(\varepsilon)=
 \left\lceil\exp\left((A+\varepsilon){K\over\log K}\right)
 \right\rceil.                                             \tag{6}
\]

For every real `epsilon>0`, there is `K_epsilon` such that, for every
`K>=K_epsilon`,

\[
 \boxed{\quad
 {1\over N_K}\sum_{z:r_K(z)>T_K(\varepsilon)}r_K(z)
 \le \exp\left(-{\varepsilon K\over2\log2}\right).
 \quad}                                                      \tag{7}
\]

Consequently the explicitly bounded fibres themselves have support

\[
 \left|\{z:1\le r_K(z)\le T_K(\varepsilon)\}\right|
 \ge
 {\left(1-e^{-\varepsilon K/(2\log2)}\right)N_K
  \over T_K(\varepsilon)}                                  \tag{8}
\]

for all sufficiently large `K`. In particular, using
`N_K>=iota_K 60^K/4`, (8) is an explicit
`60^K exp(-O(K/log K))` anti-clustering certificate.

R9's pointwise `exp(o(K))` bound alone is compatible with every edge lying
in a fibre of size `exp(cK/log K)`. For every `c>A`, (7) instead forces the
edge mass above that scale to zero exponentially. Thus (7) is strictly more
information about the unresolved fibres, while still stopping short of a
fixed cutoff.

## 2. Divisor moments

Write `tau(n)` for the divisor function and `d_m(n)` for the number of
ordered factorizations of `n` into `m` positive factors.

### Lemma 3 (exact moment majorant)

For every positive integer `q`, put `m=2^q`. For every integer `X>=1`,

\[
 \sum_{n\le X}\tau(n)^q
 \le X\left(1+\lceil\log_2X\rceil\right)^{m-1}.    \tag{9}
\]

#### Proof

For a prime power `p^e`, encode a `q`-tuple
`(a_1,...,a_q) in {0,...,e}^q` by the following weak composition of
`e` into `2^q` cells. For each level `1<=t<=e`, form the binary vector

\[
 b_t=({\bf1}_{a_1\ge t},\ldots,{\bf1}_{a_q\ge t})
       \in\{0,1\}^q
\]

and let the cell indexed by `b` count the levels with `b_t=b`. The
composition recovers every coordinate through

\[
 a_j=\sum_{b:b_j=1}c_b,
\]

so the encoding is injective. Therefore

\[
 (e+1)^q\le {e+2^q-1\choose2^q-1}=d_{2^q}(p^e).
\]

Multiplication over prime powers gives `tau(n)^q<=d_m(n)`.

Now

\[
 \sum_{n\le X}d_m(n)
 =\#\{(a_1,\ldots,a_m):a_1\cdots a_m\le X\}.
\]

Fixing the first `m-1` entries and extending the sum gives

\[
 \sum_{n\le X}d_m(n)
 \le X\left(\sum_{a\le X}{1\over a}\right)^{m-1}.
\]

Grouping the harmonic sum into dyadic intervals proves the exact bound

\[
 \sum_{a\le X}{1\over a}\le1+\lceil\log_2X\rceil.
\]

This proves (9). QED.

## 3. Proof of Theorem 1

For a product `z`, remove its powers of two and three:

\[
 z_*=z/(2^{v_2(z)}3^{v_3(z)}).
\]

R9's label-preserving injection gives

\[
 r_K(z)\le\tau(z_*).                                    \tag{10}
\]

For completeness, every `u` is odd and every `v` is prime to three.
Thus a representation maps to `u/3^{v_3(z)}`, a divisor of `z_*`.
Equality of these divisors gives equality of `u`; the disjoint scale
intervals then recover `i`, and `v=z/u`. Hence the map retains labels.

For an edge `z=uv`, put `e=v_3(u)` and `f=v_2(v)`. Then

\[
 z_*=(u/3^e)(v/2^f)
\]

and divisor submultiplicativity gives

\[
 r_K(uv)\le\tau(z_*)\le\tau(u)\tau(v).              \tag{11}
\]

If `r_K(uv)>T`, (11) implies

\[
 1\le {\tau(u)^q\tau(v)^q\over T^q}.
\]

Summing this inequality over precisely the labelled edges counted by
`M_K(T)` yields

\[
 T^qM_K(T)
 \le\sum_{i\in I_K}
 \left(\sum_{u\in U_i}\tau(u)^q\right)
 \left(\sum_{v\in V_{K-i}}\tau(v)^q\right).          \tag{12}
\]

The exact factor ranges are

\[
 U_i\subset[1,36\cdot360^i],\qquad
 V_{K-i}\subset[1,27\cdot360^{K-i}].
\]

Apply Lemma 3 to each sum and enlarge both dyadic factors to `J_K`.
Every channel in (12) is at most

\[
 (36\cdot360^i)(27\cdot360^{K-i})
 J_K^{2(2^q-1)}
 =972\cdot360^KJ_K^{2(2^q-1)}.
\]

Summing over `iota_K` channels proves (4).

The 60 distinct one-block offsets concatenate injectively in base 360, so
`|D_k|>=60^k` and the majority choice gives `s_k>=60^k/2`. Therefore

\[
 N_K=\sum_{i\in I_K}s_i s_{K-i}
 \ge {\iota_K\over4}60^K.                             \tag{13}
\]

Divide (4) by (13), use `360/60=6`, and cap by one. This proves (5).
QED.

## 4. Optimization

For `K>=1`,

\[
 J_K\le16K,                                             \tag{14}
\]

because `36<2^6`, `360<2^9`, and hence `J_K<=7+9K<=16K`. The choice in
(6) obeys

\[
 2^{q_K}\le {K\over(\log K)^3},
\]

and

\[
 q_K\ge {\log K-3\log\log K-\log2\over\log2}.      \tag{15}
\]

Define

\[
\begin{aligned}
 E_\varepsilon(K)={}&{\varepsilon\over\log2}
 -\left(\log6+{\varepsilon\over\log2}\right)
 {3\log\log K+\log2\over\log K}\\
 &-{2\log(16K)\over(\log K)^3}
 -{\log3888\over K}.
\end{aligned}                                           \tag{16}
\]

Substitution of (14)-(15) and `T=T_K(epsilon)` into the exact gate (5)
gives, whenever `q_K>=1`,

\[
 {M_K(T_K(\varepsilon))\over N_K}
 \le e^{-K E_\varepsilon(K)}.                          \tag{17}
\]

Every error term in (16) tends to zero, so
`E_epsilon(K)->epsilon/log 2`. It is therefore at least
`epsilon/(2 log 2)` for every sufficiently large `K`, proving (7).
Equation (8) follows because each retained product carries at most `T_K`
labelled edges.

The leading cutoff constant is exactly

\[
 \boxed{A=(\log2)(\log6)}.                             \tag{18}
\]

It comes from the exponential ratio `360^K/60^K=6^K` in the only
unconditional support lower bound; the divisor moments contribute
`exp(o(K))` after optimization.

## 5. Exact failure of bounded-suffix uniqueness

The full `Q=360,K=4` extraction contains

\[
 \boxed{
 2090355\cdot3288011
 =2144355\cdot3205211
 =6873110233905.}                                      \tag{19}
\]

The corresponding left offsets are `8377,35377`, and the right offsets are
`59203,31603`. Complete word witnesses, listed in application order, are

\[
\begin{array}{c|l}
8377 &(2,2,2,3,3,5,\;2,3,5,2,2,3)\\
35377&(2,3,5,2,3,2,\;2,3,5,2,2,3)\\
59203&(3,3,2,2,3,2,\;5,3,2,2,2,5)\\
31603&(2,3,3,3,2,2,\;5,3,2,2,2,5).
\end{array}                                             \tag{20}
\]

Direct evaluation of `d -> m d+(m-2)` from `d=0` gives the four displayed
offsets. Thus both left words share their last six multipliers and both
right words share their last six multipliers, while (19) remains a
nontrivial collision.

The exhaustive suffix audit gives:

| suffix depth | ambiguous collision pairs | ambiguous fibres |
|---:|---:|---:|
| 1 | 5,475 | 5,473 |
| 2 | 2,244 | 2,244 |
| 3 | 726 | 726 |
| 4 | 227 | 227 |
| 5 | 82 | 82 |
| 6 | 30 | 30 |

Here "ambiguous" means that the two representations admit one common exact
suffix word on the left and one on the right. Exact words are stronger data
than their induced congruence signatures, so a one-block suffix congruence
cannot prove injectivity. Recursing into independent predecessors recreates
the same multiplication problem and supplies no finite-degree bridge; that
branch was stopped.

## 6. Verification

`C111_collision_extract.cpp` generated the `13,068` exact layer-two
offsets, retained the `7,779` majority-color offsets, sorted all
`60,512,841` labelled `U_2 x V_2` products together with their edge
indices, and replayed every repeated edge. It independently obtained

\[
 \text{histogram }1:60480975,\quad2:15927,\quad3:4,
\]

`60,496,906` product values, `15,931` repeated fibres, and `31,866`
colliding edges.

`C111_gateT_verify.py` uses ordinary Python integers. It:

1. checks the prime-power injection in Lemma 3 for `1<=q<=8` and
   `0<=e<=256`;
2. independently forms every `K=2,3` product and checks (10);
3. checks (12) and (5) for `K=2,3,4`, `1<=q<=4`, and `1<=T<=3`;
4. verifies all complete words in (20) and exhausts suffix depths one
   through six.

Normal and `python -O` verifier outputs are byte-identical. Two C++
extractions are also byte-identical.

SHA-256:

```text
A1448D6D24C6080E675443B31642EB4C3ACAC2CACCDECAC5827E919F18E56751  C111_collision_extract.cpp
D3A443E80138C95DCB6618762307A4E5CD4B7875D945C8476AE0C89BDDAED0DC  C111_collision_extract.json
D3A443E80138C95DCB6618762307A4E5CD4B7875D945C8476AE0C89BDDAED0DC  C111_collision_extract_replay.json
349A868755A5223C3FB1CE9919D268B63BE3659BDCC049361CCA6FF06468BCFB  C111_gateT_verify.py
867B732D9460EB3A821860FE589FAF8E17D297BA6326ADAF5F2698E43C41FE7F  C111_gateT_verify.json
867B732D9460EB3A821860FE589FAF8E17D297BA6326ADAF5F2698E43C41FE7F  C111_gateT_verify_O.json
```

Reproduction:

```powershell
g++ -std=c++20 -O3 -march=native -fopenmp -Wall -Wextra -Wconversion -Wshadow `
  problems/424/compute/wave5/C111_collision_extract.cpp `
  -o problems/424/compute/wave5/C111_collision_extract.exe

problems/424/compute/wave5/C111_collision_extract.exe `
  problems/424/compute/wave5/C111_collision_extract.json 32

python problems/424/compute/wave5/C111_gateT_verify.py `
  --collisions problems/424/compute/wave5/C111_collision_extract.json `
  --output problems/424/compute/wave5/C111_gateT_verify.json
```

## 7. Exact boundary

The proved gates are (4), (5), and their optimized consequence (7). They
force `1-o(1)` of all labelled edges below the explicit growing cutoff
`T_K(epsilon)`, with exponentially small exceptional edge mass.

They do not imply a fixed `L`. The exact unproved Gate-T condition remains

\[
 \exists L,\eta,K_0\quad
 M_K(L)\le(1-\eta)N_K\qquad(K\ge K_0).               \tag{21}
\]

Thus C111 removes the upper subexponential tail but leaves the regime
`L<r_K(z)<=T_K(epsilon)`. No additional encoding is introduced for that
lower medium-fibre regime.

`2026-07-13T20:52:05.2204789+03:00 OK PLAN | DID: divisor-moment optimization | RESULT: Theorem 1 and Corollary 2, equations (4)-(7), in C111_gateT_anticlustering.md | D: tail lemma proved`

`2026-07-13T20:52:05.2204789+03:00 OK VERIFY | DID: final compile, exact witness replay, hash and scope checks | RESULT: all checks pass; only C111-owned paths are untracked | D: none`
