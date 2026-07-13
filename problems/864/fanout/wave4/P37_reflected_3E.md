# P37: reflected three-sum hole and modular carry obstruction

## Verdict

This lane does not prove

\[
 \max E\geq(3-o(1))|E|^2
\]

and does not construct an infinite family with coefficient below `3`.
It gives two complete exact lemmas and one exact obstruction.

1. The difficult P21 relation has a low reflected form.  If
   `E=G+2Z`, `F=W-Z`, and `K=W-G`, then

   \[
   E\cap3E=\varnothing
   \quad\Longleftrightarrow\quad
   G+2W\notin3F-F
   \quad\Longleftrightarrow\quad
   K\notin F+3Z.                                      \tag{1}
   \]

   Every summand may repeat.  This converts the top-layer `3F-F` hole
   into a literal nonnegative four-sum hole at `K`.

2. A strong modular Sidon lift cannot certify this hole by congruence.
   If a `p`-point lift lies in `Z/nZ`, then every target residue has at
   least

   \[
                        (p^2-n)_+                       \tag{2}
   \]

   representations as an unordered pair sum plus a *positive literal
   difference*, modulo `n`.  Diagonal pair sums are included.  For a
   Bose-Chowla set, `n=p^2-1`, so every target has such a modular
   representation.  A literal hole can exist only because every modular
   representation has nonzero integer carry.

3. A deterministic `q=128` Bose-Chowla sample gives a literal valid set
   with

   \[
     |E|=128,\qquad \max E=42705<3\cdot128^2=49152.     \tag{3}
   \]

   This is finite and is not an asymptotic disproof.  At its center there
   are exactly `4156` positive-difference modular representations: `2015`
   lie at integer layer `M-2n`, `2141` at `M-n`, and none at the literal
   layer `M`.  Thus replacing literal equality by modular equality gives
   the wrong answer on an exact 128-point certificate.

The surviving issue is therefore a uniform carry theorem.  Neither (1) nor
(2) forces one modular representation onto the literal layer.

## 1. Conventions

All sets below are sets of integers.  Sidon means that

\[
 a+b=c+d\quad\Longrightarrow\quad\{a,b\}=\{c,d\}
\]

as multisets.  In particular, `a+a` is an allowed pair sum.  The notation
`3E` permits all repeated triples, including `a+a+a` and `a+a+b`.

Write the P21 data as

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\},\qquad G\geq1,
 \qquad E=G+2Z,\qquad M=G+2W.                           \tag{4}
\]

Define the reflected ruler and the overlap length by

\[
 F=W-Z,\qquad K=W-G=3W-M.                               \tag{5}
\]

Then

\[
 E=M-2F.                                                 \tag{6}
\]

The difficult overlap regime is exactly

\[
 0<K<W\quad\Longleftrightarrow\quad G<W
 \quad\Longleftrightarrow\quad 2W<M<3W.                \tag{7}
\]

Reflection and the affine map in (6) preserve diagonal-inclusive
Sidonicity.  They also make every element of `E` congruent to `M` modulo
`2`, and positivity is exactly `M-2W=G>0`.

## 2. Reflected low-hole lemma

### Lemma R3E

For the data (4)-(5), the following are equivalent.

1. `E` is disjoint from `3E` as a literal integer set.
2. `M` is not in `3F-F` as a literal integer.
3. `K` is not in `F+3Z` as a literal integer.
4. `Z` is disjoint from `G+3Z`.

All four statements allow repeated summands.

### Proof

Take `f_t,f_a,f_b,f_c` in `F`.  Using (6),

\[
 M-2f_t=(M-2f_a)+(M-2f_b)+(M-2f_c)
\]

is equivalent to

\[
 f_a+f_b+f_c-f_t=M.                                    \tag{8}
\]

This proves the equivalence of 1 and 2 without deleting any diagonal or
repeated variable.

Write `f_i=W-z_i`.  Equation (8) becomes

\[
 M=2W-z_a-z_b-z_c+z_t.
\]

Subtracting from `3W` gives

\[
 K=3W-M=(W-z_t)+z_a+z_b+z_c=f_t+z_a+z_b+z_c.           \tag{9}
\]

Thus 2 and 3 are equivalent.  Finally, (9) can be rearranged as

\[
 z_t=G+z_a+z_b+z_c,
\]

which proves the equivalence with 4.  Every step is an equality in the
integers, not in a quotient group.  QED.

### Exact top-strip consequence

Let

\[
 S(F)=\{a+b:a,b\in F,\ a\leq b\},\qquad
 D^+(F)=\{b-a:a,b\in F,\ a<b\}.
\]

If the equivalent conditions of Lemma R3E hold in the overlap regime,
then

\[
\boxed{
 |S(F)\cap[M-W,2W]|
 +|D^+(F)\cap[M-2W,W]|
 \leq 3W-M+1=K+1.}                                    \tag{10}
\]

Indeed, both

\[
 S(F)\cap[M-W,2W]
\]

and

\[
 M-\bigl(D^+(F)\cap[M-2W,W]\bigr)
\]

lie in the integer interval `[M-W,2W]`.  They are disjoint because an
intersection is exactly `M=s+d` with `s` an unordered pair sum and `d` a
positive difference, hence a representation of `M` in `3F-F`.  The interval
has `3W-M+1` integer points.  The sum `2W=W+W` is present, so the diagonal
endpoint is included in (10).

Equation (10) is a reflected form of the existing endpoint/cutoff packing
and is not claimed as a new coefficient-three estimate.  The exact `p=5`
example has equality, while the stored `p=9` example has six units of slack.
Thus the unweighted top strip does not close the asymptotic problem.

## 3. Quantitative modular carry obstruction

### Lemma MC1

Let

\[
 B=\{b_1<\cdots<b_p\}\subseteq[0,n-1]
\]

be strong Sidon modulo `n`, with diagonal sums included.  Let

\[
 \overline S=\{b_i+b_j\pmod n:i\leq j\},
\]

and let

\[
 \overline D_+
 =\{b_j-b_i\pmod n:i<j\},                               \tag{11}
\]

where the sign in (11) is the orientation of the chosen literal
representatives.  For every target `t` modulo `n`,

\[
\boxed{
 \#\{(s,d)\in\overline S\times\overline D_+:s+d=t\}
 \geq (p^2-n)_+.}                                      \tag{12}
\]

If `D=B-B` denotes the full modular difference support, including zero,
then also

\[
\boxed{
 \#\{(s,d)\in\overline S\times D:s+d=t\}
 \geq
 \left({3p^2-p+2\over2}-n\right)_+.}                  \tag{13}
\]

These counts are support-label counts.  They do not multiply the zero
difference by its `p` diagonal representations.

### Proof

Strong modular Sidonicity gives

\[
 |\overline S|={p(p+1)\over2}.                          \tag{14}
\]

It also makes the positive differences in (11) distinct.  If

\[
 b_j-b_i=b_l-b_k\pmod n,
\]

then

\[
 b_j+b_k=b_l+b_i\pmod n.
\]

Strong Sidonicity identifies the two unordered pairs.  The swapped
identification would force `b_j=b_i`, impossible for `i<j`; hence the two
oriented endpoint pairs are equal.  Therefore

\[
 |\overline D_+|={p(p-1)\over2}.                        \tag{15}
\]

For a fixed target `t`, the number in (12) is exactly

\[
 |\overline S\cap(t-\overline D_+)|.
\]

Inclusion-exclusion in the `n` residue classes, followed by (14)-(15),
gives

\[
 |\overline S\cap(t-\overline D_+)|
 \geq {p(p+1)\over2}+{p(p-1)\over2}-n=p^2-n.
\]

Taking the positive part proves (12).

Every nonzero ordered difference is also unique, while all zero differences
give one support residue.  Hence

\[
 |D|=p(p-1)+1.                                         \tag{16}
\]

Applying the same intersection argument to `t-D` proves (13).  QED.

### Bose-Chowla consequence

For the Bose-Chowla relative difference set, `n=p^2-1`.  Lemma MC1 gives

\[
 |\overline S\cap(t-\overline D_+)|\geq1               \tag{17}
\]

for every target residue, and

\[
 |\overline S\cap(t-D)|\geq{p^2-p+4\over2}.            \tag{18}
\]

Thus no target is an oriented modular hole.  If an integer lift has a
literal center `M` outside `S(B)+D^+(B)`, every intersection in (17) must
satisfy

\[
                         s+d=M+kn                       \tag{19}
\]

with a nonzero integer `k`.  This is the exact obstruction: modular
saturation supplies representations but does not choose their carry layer.

## 4. Exact 128-point literal obstruction

The stored record is

```text
problems/864/compute/p37/bose_q128_sample.jsonl
```

It is a deterministic scan of eight affine multiplier classes out of the
`5292` classes at Bose-Chowla parameter `q=128`.  It is not an exhaustive
best-center claim.  Its selected reflected ruler `F` has

\[
 n=16383,\quad p=128,\quad W=15445,\quad M=42705.       \tag{20}
\]

Set

\[
 E=M-2F.
\]

The independent verifier proves, by literal enumeration,

\[
 \min E=11815>0,\qquad \max E=42705,
\]

all elements of `E` are odd, all

\[
 {128\cdot129\over2}=8256
\]

unordered pair sums including diagonals are distinct, and

\[
 E\cap3E=\varnothing
\]

with repeated summands allowed.  Equivalently, the complete reflected set
`F union (M-F)` has exactly one repeated unordered sum:

\[
                         (M,128).                        \tag{21}
\]

The low reflected parameters are

\[
 G=M-2W=11815,qquad K=3W-M=3630,                       \tag{22}
\]

and the verifier independently finds no representation of `K` in
`F+3(W-F)`.

On the other hand, modulo `n` the center has `4156` oriented
sum-plus-positive-difference representations.  Their exact integer totals
are distributed as

\[
\begin{array}{c|c|c}
\text{layer}&\text{integer total}&\text{count}\\ \hline
-2&M-2n=9939&2015\\
-1&M-n=26322&2141\\
 0&M=42705&0.
\end{array}                                             \tag{23}
\]

This proves an exact falsifier to the bridge

> a modular representation of the reflected center supplies a literal
> collision.

It also falsifies any version of that bridge which merely asks for many
modular representations: this example has `4156`, not just the one forced by
(17), and every one has the wrong carry.

Equation (3) is a finite sub-`3` example only.  It is compatible with
`M/p^2` tending to `3` along every infinite Bose-Chowla sequence.

## 5. Exact computation

All arithmetic in the P37 checkers is integer, residue, or finite-field
arithmetic.  No floating-point gate is used.

### Small reflected census

```text
python -B problems/864/compute/p37/reflected_hole_audit.py \
  --max-width 18 --max-examples 8
```

This enumerates every endpoint-normalized Sidon ruler through width `18`.
It checked `1340` rulers and `6783` top-layer holes.  Every reconstructed
`E=M-2F` passed positivity, same parity, diagonal-inclusive Sidonicity, and
literal `E cap 3E=empty` with repeated triples.

### Modular lemma census

```text
python -B problems/864/compute/p37/modular_carry_bound_audit.py \
  --max-modulus 16
```

The exact output is

```text
nonempty subsets: 131053
strong modular Sidon sets: 2731
targets checked in each of (12) and (13): 37119
equalities in (12): 12809
equalities in (13): 11807
```

The finite audit is not used to prove Lemma MC1; the inclusion-exclusion
argument is the proof.

### Bose-Chowla sample and independent verification

```text
python -B problems/864/compute/p12/algebraic_scan.py \
  --family bose --parameters 128 --unit-limit 8 \
  --output problems/864/compute/p37/bose_q128_sample.jsonl

python -B problems/864/compute/p37/verify_bose_sample.py
```

The second program reads only the stored JSON record.  It reconstructs all
pair sums, positive differences, repeated-summand triples, the full reflected
sum census, the low reflected hole, and the modular carry histogram (23).

## 6. Scope and remaining frontier

Lemma R3E isolates the exact low target:

\[
 K=3W-M\notin(W-Z)+3Z.                                  \tag{24}
\]

Under a hypothetical fixed-epsilon counterexample

\[
 M\leq(3-\varepsilon)p^2
\]

and the classical `W\geq(1-o(1))p^2`, (24) has

\[
 K\geq(\varepsilon-o(1))p^2.                            \tag{25}
\]

So a proof of the proposed constant must rule out a macroscopic low
four-sum hole generated by one ruler and its exact reflection.

For modular algebraic constructions, Lemma MC1 proves that the corresponding
residue is already occupied.  What remains is not modular coverage but the
integer layer question in (19).  A complete continuation needs one of:

1. a uniform theorem forcing one of the modular intersections onto layer
   `k=0` whenever (25) holds; or
2. an explicit infinite sequence for which all intersections stay on
   nonzero layers and `M\leq(3-\varepsilon)p^2`.

The `q=128` certificate proves that neither modular saturation nor a large
finite representation count supplies item 1.  No theorem in this lane
supplies item 2.

Relative to the local dossier, P21 gives the `E cap 3E` reformulation, P24
gives the endpoint-shadow packing, P34 gives a full-difference modular
coverage threshold, and P26/P30 analyze family-specific carry layers.  The
new exact point recorded here is the oriented bound (12), together with the
low reflected identity (1) and the explicit 128-point audit showing thousands
of modular representations but no literal one.  No global literature-first
claim is made.
