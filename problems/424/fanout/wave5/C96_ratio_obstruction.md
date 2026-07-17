# C96: arithmetic classes and the theorem-strength scale obstruction

## Verdict

Write `A_H(X)` for the persistent hard seed-2 roots and write `D_E(X)` for
the structural splitless roots whose literal seed-2 chain has reached the
actual least generated closure by cutoff `X`.  This is the healed
structural-splitless bank counted by C92--C94.  The subscript distinguishes
it from any larger, abstract C87 common-neighbor bank.

The suggested softened scale comparison

\[
  2D_E(X)\ge 7A_H(\lfloor X/4\rfloor)-o(X)                 \tag{1}
\]

is **equivalent to the full density theorem**, not an intermediate analytic
estimate.  More precisely, there is a nonnegative `R(X)=o(X)` making (1)
valid for all sufficiently large `X` if and only if `A_H(X)=o(X)`.  The
other finite C92 scale gate,

\[
 A_H(X)\le D_E(X)+A_H(\lfloor X/4\rfloor)+1,              \tag{2}
\]

has the same obstruction: even allowing an arbitrary `o(X)` error, it is
equivalent to `A_H=o(X)`.  By C72, either conclusion is equivalent to the
full `M(X)=o(X)` and density-`2/3` theorem for Problem 424.

The reason is elementary but decisive: C13 gives

\[
                   0\le D_E(X)\le E(X)=o(X).              \tag{3}
\]

Thus an `o(X)` error is larger than the entire proposed reservoir.  A
Selberg--Delange or sieve count of the ambient structural classes cannot
repair this, because healing is not an arithmetic-class predicate: it
depends on membership in the actual least closure.

The exact no-error inequalities (1) with no error and (2) remain alive.
Two independent censuses find no failure through `10^9`; C96 does not prove
or falsify them.  It does prove an exact obstruction to the canonical
class map: the hard root `54` has prime-square shadow `24`, but that
splitless chain is entirely ungenerated through `4*54=216` and first heals
only at `5889`.  Hence the C74 prime-square shadow cannot supply a
fourfold-scale injection into `D_E`.

## 1. Structural classification

Call a prime `p` a plus prime when `p=1 mod 3` and a minus prime when
`p=2 mod 3`.  Let `n>=4` be even and allowed, and put `N=n+1`.

### Lemma C96.1 (splitless classes)

The value `n` has no admissible distinct-factor pair if and only if exactly
one of the following holds.

1. `3` does not divide `N`, and either every prime divisor of `N` is a plus
   prime or `N=p^2` for a minus prime `p`.
2. `3` divides `N`, and either `N=9` or
   \[
      N=3R,
   \]
   where every prime divisor of `R` is a plus prime.

Every such `n` is a structural splitless hole.  The excluded value `n=2`
has `N=3` but is a seed.

#### Proof

If `3` does not divide `N`, then `N=1 mod 3`.  An admissible factorization
must split the minus-prime factors into two factors both congruent to `2`
modulo `3`.  If a minus prime `p` divides `N`, then

\[
                         N=p(N/p)
\]

is such a factorization, except when both factors equal `p`.  Equality is
possible precisely when `N=p^2`; plus-prime cofactors would make the two
factors distinct.  With no minus-prime divisor, every divisor is `1 mod 3`
and no admissible pair exists.

Now write `N=3^aR`, with `3` not dividing `R`.  If `a>=2`, the pair
`(3,N/3)` is admissible and distinct except for `N=9`.  If `a=1` and a
minus prime `p` divides `R`, the distinct pair `(p,3R/p)` is admissible.
If no minus prime divides `R`, every divisor not divisible by `3` is
forbidden (`1 mod 3`), so no admissible pair exists.  These alternatives
are exhaustive.  QED.

### Corollary C96.2 (hard arithmetic shapes)

An even allowed `n` is hard-shaped exactly in one of the following two
classes.

1. `N` is not divisible by `3`, contains a minus-prime divisor, and is not
   the square of a single minus prime.
2. `N=3R`, where `R=1 mod 3` contains a minus-prime divisor.

It is an actual hard root precisely when it is hard-shaped and is absent
from the least generated closure.

#### Proof

Lemma C96.1 characterizes reducibility in the first case.  No seed-3 pair
exists there.  In the second case the cofactor `R=1 mod 3` is forbidden, so
the seed-3 factorization is unusable; a minus prime supplies the distinct
admissible pair from the preceding proof.  If `R=2 mod 3`, `(3,R)` is a
usable seed-3 pair and the shape is not hard.  Higher powers of `3` likewise
give the usable pair `(3,N/3)`, apart from the splitless value `8`.  QED.

This classifies the *possible* roots, but the final generated/hole decision
is still closure-dependent.

## 2. Exact characterization of the healed bank

Put

\[
 U(n)=2n-1,
 \qquad U^j(e)=2^j(e-1)+1.
\]

### Lemma C96.3 (first-death events)

Let `e` be a structural splitless root.  It is counted by `D_E(X)` if and
only if there is a least `j>=1` such that

\[
 t=U^j(e)\le X
\]

belongs to the actual least generated closure.  At this first event, `t`
is odd, its parent `U^(j-1)(e)` is a hole, and every generating pair for
`t` that certifies first generation has smaller factor at least `3`.
Conversely, every odd generated `t>3` whose seed-2 parent is a hole belongs
to the unique root

\[
 e=1+{t-1\over 2^{v_2(t-1)}}.                          \tag{4}
\]

It increments `D_E` exactly when this root has one of the splitless forms
in Lemma C96.1.

#### Proof

Generation is upward closed on each seed-2 chain.  Therefore a splitless
root has either no generated visible iterate or a unique first one.  At the
first one the seed pair `(2,U^(j-1)(e))` cannot generate `t`, because its
second factor is a hole.  Hence a certifying generated pair uses a smaller
factor at least `3`.  Since `e-1` is odd,
`v_2(t-1)=j`, which proves (4) and uniqueness.  The converse follows by
reversing this calculation.  QED.

Formula (4) is an exact event characterization, not a multiplicative-class
classification.  Whether `t` is generated depends recursively on the
closure below `t`.

## 3. Scale-error collapse

The following statements use explicit quantifiers.  A function `R` is
`o(X)` when, for every `epsilon>0`, there is `X_0` such that
`0<=R(X)<=epsilon X` for every `X>=X_0`.

### Theorem C96.4 (weighted quarter-scale equivalence)

The following are equivalent.

1. There is a nonnegative `R(X)=o(X)` such that, for every sufficiently
   large integer `X`,
   \[
      2D_E(X)\ge7A_H(\lfloor X/4\rfloor)-R(X).         \tag{5}
   \]
2. `A_H(X)=o(X)`.

#### Proof

Assume (5) and put `X=4Y`.  Then

\[
 7A_H(Y)\le2D_E(4Y)+R(4Y).
\]

Both terms on the right are `o(Y)`: the first by (3), and the second by the
definition of `R`.  Hence `A_H(Y)=o(Y)`.

Conversely, if `A_H=o(X)`, take

\[
 R(X)=7A_H(\lfloor X/4\rfloor).
\]

Then `R=o(X)`, and (5) reduces to `2D_E(X)>=0`.  QED.

### Theorem C96.5 (additive quarter-scale equivalence)

The following are equivalent.

1. There is a nonnegative `R(X)=o(X)` such that, for every sufficiently
   large integer `X`,
   \[
    A_H(X)\le D_E(X)+A_H(\lfloor X/4\rfloor)+R(X).     \tag{6}
   \]
2. `A_H(X)=o(X)`.

#### Proof

Let `L=limsup A_H(X)/X`, which is finite.  Divide (6) by `X`, use (3), and
take a limsup.  Since

\[
 \limsup_{X\to\infty}{A_H(\lfloor X/4\rfloor)\over X}
 \le {L\over4},
\]

we obtain `L<=L/4`, hence `L=0`.  Conversely, if `A_H=o(X)`, choose
`R(X)=A_H(X)`; then (6) is immediate from nonnegativity.  QED.

C72 proves that `A_H=o(X)` is equivalent to hard-hole sparsity, total-hole
sparsity, and the density-`2/3` conclusion.  Thus neither softened scale
gate is a weaker analytic lemma.  In particular, invoking Selberg--Delange
for the classes in Lemma C96.1 does not discharge (5): it controls the
ambient splitless count `E`, whereas (5) needs a lower bound for the
closure-dependent healed subset `D_E`.

## 4. Exact mechanism obstructions

### 4.1 Prime-square shadow misses the fourfold bank

C74 maps a hard root `h` with least minus prime `p|h+1` to the splitless
prime-square shadow `p^2-1`.  At the first hard root

```text
h = 54,  h+1 = 5*11,  p = 5,
```

the shadow is `e=24`.  Its chain through `4h=216` is

```text
24, 47, 93, 185,
```

and all four values are holes.  The first generated chain member is instead

```text
5889 = U^8(24).
```

Therefore this canonical structural map does not send even the first hard
root into `D_E(4h)`.

### 4.2 Arithmetic class does not determine healing

At cutoff `10^6`:

* `6+1=7` and `2340+1=2341` are both in the plus-prime semigroup class.
  Root `6` heals at `41`, while the complete visible chain of `2340` is
  \[
  2340,4679,9357,18713,37425,74849,149697,299393,598785
  \]
  and consists entirely of holes.
* `20+1=3*7` and `16148+1=3*7*769` are both in the
  three-times-plus-semigroup class.  Root `20` heals at `77`, whereas the
  complete visible chain of `16148` through `10^6` consists entirely of
  holes.

These are finite exact witnesses, not an asymptotic counterexample.  They
show that a comparison based only on the Selberg--Delange class label cannot
lower-bound the actual bank `D_E`.

## 5. Exact gate and independent replay

`C96_ratio_obstruction.py` independently reconstructs the closure and checks
the structural classification at every even allowed value through `10^6`.
It reproduces

```text
A_H(10^6) = 27056
D_E(10^6) = 44271
E(10^6) = 108651
minimum D_E/A_H = 5/6 at X=186.
```

It finds zero failures through `10^6` of both exact C92 scale gates.  Normal
and `python -O` outputs are byte-identical.  The independent verifier does
not import the classifier; it recursively evaluates the exact factor
closure for the displayed obstruction chains and checks all five claims.

Reproduction:

```powershell
python problems/424/compute/wave5/C96_ratio_obstruction.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C96_ratio_obstruction_1e6.json

python -O problems/424/compute/wave5/C96_ratio_obstruction.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C96_ratio_obstruction_1e6_O.json

python problems/424/compute/wave5/C96_ratio_obstruction_verify.py `
  --claim problems/424/compute/wave5/C96_ratio_obstruction_1e6.json `
  --output problems/424/compute/wave5/C96_ratio_obstruction_verify_1e6.json
```

SHA-256:

```text
B97AE5EEDB5A9D46A3459F073972112B79E67E5FA0D56DCD29E0DDC292D04741  C96_ratio_obstruction.py
DF80B27FBBCCB6E0A191B5D493781EAD5AF3331A88FB8B6223DFC4C73FAD6858  C96_ratio_obstruction_verify.py
9DA3022CC7CD8A44A54A8E9510C03A9A608F57A77C30866184A5B098B074F629  C96_ratio_obstruction_1e6.json
5BDB89119EBFF0D52E3C675053A5A9E92B7A039DF5303085996B076809EE08B6  C96_ratio_obstruction_verify_1e6.json
```

## Scope

C96 returns the requested exact obstruction.  It neither proves nor
falsifies the no-error inequalities

\[
 2D_E(X)\ge7A_H(\lfloor X/4\rfloor),
 \qquad
 A_H(X)\le D_E(X)+A_H(\lfloor X/4\rfloor)+1.
\]

Those remain exact, theorem-strength frontiers with zero falsifiers through
`10^9`.  Any productive continuation must retain actual closure information
and either prove one of these no-error gates or use an error term small
relative to the sparse bank (for example `o(D_E)`), not merely `o(X)`.
