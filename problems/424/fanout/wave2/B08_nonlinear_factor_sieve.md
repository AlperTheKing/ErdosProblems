# B08: nonlinear factor sieve

## Verdict

**Problem 424 is not solved.**  The argument below neither proves positive
lower density for `A` nor proves that the allowed complement has density zero.
It gives an exact descent inequality using the whole growing multiplier set,
and identifies a sharp infinite family that this descent cannot see.

Let

\[
U=\{n\geq1:n\equiv0,2\pmod3\},\qquad C=U\setminus A,
\]

and, for `z >= 2`, let

\[
D_z=\{d\in A:d\leq z,\ d\equiv2\pmod3\}.
\]

## Exact growing-multiplier descent

**Lemma 1.**  If `n in C`, `d in A`, `d = 2 (mod 3)`, `d | n+1`, and
`d^2 != n+1`, then

\[
q=\frac{n+1}{d}\in C\quad\hbox{and}\quad q<n.
\tag{1}
\]

Consequently, writing `C(Y)=|C intersect [1,Y]|`,

\[
\sum_{\substack{n\leq X\\n\in C}}
 \#\{d\in D_z:d\mid n+1,\ d^2\ne n+1\}
\leq
\sum_{d\in D_z} C\!\left(\left\lfloor\frac{X+1}{d}\right\rfloor\right).
\tag{2}
\]

**Proof.**  The mod-3 invariant gives `A subset U`.  If `n = 0 (mod 3)`,
then `n+1 = 1 (mod 3)` and division by `d = 2 (mod 3)` gives
`q = 2 (mod 3)`.  If `n = 2 (mod 3)`, it gives `q = 0 (mod 3)`.
Thus `q in U`.  If `q in A`, the hypotheses `d,q in A` and `d != q`
would give `n=dq-1 in A`, contrary to `n in C`.  Hence `q in C`.
Also `d>=2`, so `q< n` for `n>1`.  For each fixed `d`, the map
`n -> q=(n+1)/d` is injective and has the range used on the right of (2).
Summing over `d` proves (2).  QED.

This is not a fixed-alphabet affine subsystem: `D_z` consists of every
generated multiplier congruent to 2 modulo 3 and grows with `z`.

## A factor-sieve blind family

Let

\[
\mathcal S=\{s\geq1:p\mid s\Longrightarrow p\equiv1\pmod3\}.
\]

**Lemma 2.**  For every `s in S` with `s>1`,

\[
s-1\in C,\qquad 3s-1\in C. \tag{3}
\]

Moreover, neither `s` nor `3s` has a divisor congruent to 2 modulo 3.
Therefore every term in (3) has zero weight on the left of (2), even if
`D_z` is replaced by the entire growing set
`D=A intersect {2 (mod 3)}`.

**Proof.**  Every divisor of `s` is 1 modulo 3.  Hence a factorization
`s=xy` cannot have both `x,y in A subset U`.  In a factorization
`3s=xy`, exactly one factor is divisible by 3; the other divides `s` and is
1 modulo 3, so again both factors cannot lie in `A`.  The exact ascending
factor criterion for `A` now excludes `s-1` and `3s-1`.  Their residues are
0 and 2 modulo 3, respectively, so they lie in `C`.  The divisor assertion
is immediate.  QED.

The condition `s>1` is necessary.  The value `s=1` in the second family
would give `3s-1=2`, which is a seed in `A`; this is the boundary falsifier
found by the first exact replay.

## Size of the obstruction

Let `S(X)=|S intersect [1,X]|`.  Its Dirichlet series is

\[
F(w)=\prod_{p\equiv1\ (3)}(1-p^{-w})^{-1}.
\]

For the nonprincipal character `chi` modulo 3,

\[
F(w)^2=\zeta(w)L(w,\chi)(1-3^{-w})
        \prod_{p\equiv2\ (3)}(1-p^{-2w}).
\]

Selberg--Delange therefore gives

\[
S(X)\sim \kappa\frac{X}{\sqrt{\log X}},\qquad
\kappa=\frac1{\sqrt\pi}
\left(\frac23L(1,\chi)
\prod_{p\equiv2\ (3)}(1-p^{-2})\right)^{1/2}>0.
\tag{4}
\]

The two families in (3) are disjoint.  For `X>=20` their exact count is

\[
S(X+1)+S\!\left(\left\lfloor\frac{X+1}{3}\right\rfloor\right)-2,
\]

and hence is asymptotic to

\[
\frac{4\kappa}{3}\frac{X}{\sqrt{\log X}}. \tag{5}
\]

Thus unconditionally

\[
|C\cap[1,X]|\geq
\left(\frac{4\kappa}{3}+o(1)\right)\frac{X}{\sqrt{\log X}}.
\tag{6}
\]

In particular, `C=o(X/sqrt(log X))` is false, and a proof based only on
the `A intersect {2 mod 3}` descent (2) must separately handle a family of
the order shown in (5).  This does not obstruct the desired conclusion
`C(X)=o(X)`, because the family in (5) itself has density zero.

## Exact replay

An SPF enumeration through `X=2,000,000`, using the exact divisor-recursion
generator in `problems/424/compute/wave1/A06/divisor_generator.py`, asserted
membership exclusion and zero `A intersect {2 mod 3}` divisors term by term.
It returned:

| `X` | `s-1` family | `3s-1` family | total |
|---:|---:|---:|---:|
| 10,000 | 984 | 347 | 1,331 |
| 100,000 | 8,813 | 3,081 | 11,894 |
| 1,000,000 | 80,586 | 27,978 | 108,564 |
| 2,000,000 | 157,337 | 54,513 | 211,850 |

At the final cutoff, `|C intersect [1,X]|=391,539`; 240,770 of these
exceptions had no divisor in the full computed
`A intersect {2 mod 3}`, and the proved family above accounts for 211,850
of them.  These finite counts verify the lemma at the stated cutoff but are
not used in the asymptotic proof.
