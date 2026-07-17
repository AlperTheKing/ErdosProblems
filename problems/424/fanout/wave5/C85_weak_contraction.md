# C85: weighted seed-chain pooling and the unit-capacity obstruction

## Verdict

The bounded-divisor-pair sieve does combine with seed-chain pooling, but the
unconditional result is a **capacitated** Hall theorem rather than the
unit-capacity matching needed for

\[
H(X)\le cQ(X)+o(X),\qquad c<\frac43.
\]

For every pair threshold `D`, all hard holes with more than `D` admissible
factor pairs can be matched to seed-chain roots if root `r` is given capacity

\[
c_{X,D}(r)=
\left\lceil {1\over D+1}
\sum_{\substack{p\le X+1\\p\text{ is a missing odd node}\\
                 \text{on the chain rooted at }r}}
\left\lfloor {X+1\over p}\right\rfloor
\right\rceil .                                      \tag{1}
\]

This has two unconditional consequences.

1. Every **fixed finite** collection of seed-chain roots traps only `o(X)`
   hard holes.
2. A root set whose reciprocal weight is small compared with the available
   pair threshold also traps only `o(X)` hard holes.

The hoped-for capacity-one strengthening is false.  The first local collapse
is the hard hole `6140`: its two admissible pairs have missing endpoints `23`
and `89`, both on the chain rooted at `12`.  More decisively, after discarding
all hard holes with at most five admissible pairs, capacity-one Hall first
fails at the exact cutoff

\[
X=4,361,928.
\]

There are `48` high-pair hard holes whose complete witness-root neighborhood
has size `47`.  This graph uses **all** witness roots, not merely healed roots,
so restricting the right side to the `Q` reservoir cannot repair it.

Thus C85 proves a genuine global-pooling lemma and removes finite seed-chain
stars as asymptotic obstructions, but it does not prove WRC or any coefficient
`c<4/3`.  The remaining issue is to reduce the capacities in (1) by exploiting
healing or cancellation across a root set whose size grows with `X`.

## 1. Setup

Use the C16/C55 notation.  For a hard hole `h`, let

\[
\mathcal P(h)=
\{(a,b):2\le a<b,\ ab=h+1,\ a,b\in\mathcal A\},
\qquad d(h)=|\mathcal P(h)|.
\]

Every pair in `P(h)` has a missing endpoint.  Since `h+1` is odd, such an
endpoint `p` is odd.  Its seed-2 parent

\[
u={p+1\over2}
\]

is a hole: otherwise the generated pair `(2,u)` would generate `p`.  Repeatedly
applying the parent map to `u` ends at a unique even hole, denoted `root(p)`.

Define a bipartite graph `W_X` as follows.

* The left side is the hard holes `h<=X`.
* The right side is the even hole roots.
* Put `h~r` when some pair in `P(h)` has a missing endpoint `p` with
  `root(p)=r`.

For an even root `r`, its odd seed-chain nodes have the form

\[
U^j(r)=2^j(r-1)+1,\qquad j\ge1.                    \tag{2}
\]

Only the initial missing segment of this sequence can occur as missing
endpoints.  Let `C_X(r)` denote those missing odd nodes not exceeding `X+1`,
and put

\[
b_X(r)=\sum_{p\in C_X(r)}
\left\lfloor{X+1\over p}\right\rfloor .             \tag{3}
\]

Then (1) is `c_{X,D}(r)=ceil(b_X(r)/(D+1))`.

## 2. Weighted root-pool Hall theorem

### Theorem C85.1

Fix integers `X>=2` and `D>=0`, and let

\[
L_D(X)=\{h\le X:h\text{ is hard and }d(h)\ge D+1\}.
\]

There is a matching of `L_D(X)` into copies of its neighboring roots in
`W_X` such that root `r` is used at most `c_{X,D}(r)` times.  Moreover,

\[
c_{X,D}(r)
\le
\left\lceil{X+1\over(D+1)(r-1)}\right\rceil .        \tag{4}
\]

### Proof

Let `A` be any subset of `L_D(X)` and put `R=N(A)`.  For each `h in A` and
each pair in `P(h)`, choose one missing endpoint `p`.  Endpoints chosen from
different complementary factor pairs are distinct, because a divisor of
`h+1` belongs to exactly one complementary pair.  Every chosen `p` lies on
a chain rooted in `R`.  Hence there are at least `(D+1)|A|` incidences
`(h,p)`.

For fixed `p`, an incidence requires `p | h+1`.  There are at most

\[
\left\lfloor{X+1\over p}\right\rfloor
\]

such values of `h`.  Therefore

\[
(D+1)|A|
\le \sum_{r\in R} b_X(r),
\]

and consequently

\[
|A|\le\sum_{r\in R}c_{X,D}(r).
\]

This is Hall's condition with integral vertex capacities, so the asserted
matching exists.

Finally, (2) gives

\[
\sum_{p\in C_X(r)}{1\over p}
\le\sum_{j\ge1}{1\over2^j(r-1)}={1\over r-1}.
\]

Using this in (3) proves (4).  QED.

This theorem is not a restatement of C23/C56: it is unconditional, it gives
an explicit finite capacity at every root, and its proof uses only divisor
incidence plus the lacunarity of a seed chain.

## 3. Finite root traps are sparse

For a root set `R`, let `T_R(X)` count hard holes `h<=X` whose entire
neighborhood in `W_X` is contained in `R`.  Let

\[
B_D(X)=\#\{h\le X:h\text{ is hard and }d(h)\le D\}.
\]

### Corollary C85.2

For every `X,D,R`,

\[
T_R(X)
\le B_D(X)+{X+1\over D+1}
\sum_{r\in R}{1\over r-1}.                            \tag{5}
\]

In particular, for every fixed finite root set `R`,

\[
T_R(X)=o(X).                                          \tag{6}
\]

### Proof

Apply the incidence argument in Theorem C85.1 to the members of `T_R(X)`
having at least `D+1` pairs.  Their neighbor set is contained in `R`, so (4)
without ceilings gives the second term in (5).  The remaining members are
counted by `B_D(X)`.

For fixed `D`, C55 Theorem 4 gives `B_D(X)=o(X)`.  Divide (5) by `X`, take
the limsup, and then let `D` tend to infinity.  The reciprocal sum is finite
when `R` is fixed, proving (6).  QED.

More generally, (5) proves sparsity for varying `R=R_X` whenever one has a
threshold `D=D(X)` with

\[
B_D(X)=o(X),\qquad
{1\over D}\sum_{r\in R_X}{1\over r-1}=o(1).          \tag{7}
\]

Condition (7) is a usable quantitative criterion, but it is not currently
known for the growing deficient root sets relevant to WRC.

## 4. Smallest local collapse

The tempting claim

\[
\#N_{W_X}(h)\ge d(h)                                  \tag{8}
\]

is false.  Exhaustion in increasing order gives the first failure at
`h=6140`.  Indeed,

\[
6141=3\cdot23\cdot89,
\]

and the only admissible factor pairs are

\[
(23,267),\qquad(69,89).                               \tag{9}
\]

Here `69` and `267` are generated:

\[
69=5\cdot14-1,
\quad 267=2\cdot134-1,
\quad 134=5\cdot27-1,
\quad 27=2\cdot14-1.
\]

The other endpoints `23` and `89` are holes.  They lie on the same missing
seed chain

\[
12\longrightarrow23\longrightarrow45\longrightarrow89,
\]

so both pairs in (9) give the single witness root `12`.  The value `6140`
is even and its seed-3 cofactor `2047` is forbidden modulo `3`, hence it is
hard.  The exact scan checks every smaller hard hole, so this is the smallest
failure of (8).

## 5. First global capacity-one failure at pair threshold six

Even after discarding every hard hole with at most five admissible pairs,
the graph `W_X` need not have a unit-capacity matching.  The first failure is
at

\[
X=4,361,928.
\]

The exact Hall witness has the following `48` left vertices:

```text
65414, 138620, 187914, 197714, 200360, 251516, 329328,
392402, 407630, 536402, 614900, 688596, 739262, 771896,
827930, 915606, 928010, 967700, 985830, 1049190, 1268952,
1540902, 1568342, 1621262, 1766400, 1777610, 1858520,
1884882, 1968770, 2061282, 2134560, 2333036, 2402910,
2485218, 2581662, 2969840, 2987750, 3219930, 3444300,
3570482, 3894372, 3941118, 4054830, 4091658, 4147758,
4212186, 4256930, 4361928
```

Their complete neighborhood consists of the following `47` roots:

```text
6, 8, 12, 18, 24, 30, 36, 42, 54, 62, 68, 72, 86, 102,
104, 114, 144, 150, 188, 216, 224, 252, 270, 276, 312,
398, 462, 540, 564, 846, 942, 1070, 1152, 1392, 1446,
2844, 3570, 5562, 5946, 6000, 6402, 6542, 12240, 13500,
18792, 19772, 26934
```

Thus `|N(L)|=47<48=|L|`.  Every listed source has at least six admissible
pairs.  The incremental exact matching has size equal to the number of
sources at every preceding source cutoff; insertion of `4361928` is the
first failure.  Since every witness root of `h` is smaller than `h`, no later
right vertex can alter this prefix claim.

At this same witness, the capacities (1) provide `469099` root slots, with
maximum individual capacity `100709`.  The corrected theorem therefore has
ample capacity, but that capacity is far too large to imply contraction.

## 6. Why this does not close density

Summing the simple capacities (4) over a growing root set gives the harmonic
term

\[
{X+1\over D+1}\sum_r{1\over r-1}.                    \tag{10}
\]

C55 proves `B_D(X)=o(X)` for every **fixed** `D`, but supplies no threshold
large enough to absorb (10) uniformly over all roots.  The unit-capacity
substitute is already false by Section 5.  Therefore the new theorem removes
fixed stars such as the root-`6` obstruction, but a density proof still needs
one additional arithmetic input: healing must reduce the aggregate capacity
of every growing deficient root set to less than `4/3` per `Q` boundary (or
establish WRC directly).

No such estimate is claimed here.

## 7. Exact reproduction

From the repository root:

```powershell
python problems/424/compute/wave5/C85_witness_pool.py `
  --limit 6140 `
  --output problems/424/compute/wave5/C85_witness_pool_6140.json

python problems/424/compute/wave5/C85_global_pool.py `
  --limit 4361928 --min-pairs 6 `
  --output problems/424/compute/wave5/C85_global_pool_4361928.json
```

Both commands were rerun under `python -O`; each replay JSON is byte-identical
to its ordinary run.  SHA-256:

```text
F632D7DABEB331035D508FE81C4695CF482E051441E4B94B9FE1AD53C149B912  C85_witness_pool.py
0854516C3996493927AD0FF8DC522D5E8E3B8793BB0FF030BAC0D19241FF6D88  C85_witness_pool_6140.json
35BBB52F9DDFB50074151809B8FBBEE92B934DEC0A63A5662E3978FE9BCB5CA7  C85_global_pool.py
C612FF06D7B032F2D98CDCFB4287BAB8839F9A922B8B5C4321D89F5C2AA478F4  C85_global_pool_4361928.json
```

No floating-point arithmetic, `native_decide`, or solver tolerance is used.
The matching is an integer augmenting-path computation, and each emitted Hall
neighborhood is recomputed from the arithmetic data before acceptance.
