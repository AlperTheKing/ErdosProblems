# B05: exact-cover compositions for Erdos #424

## Verdict

**NOT SOLVED.** No exact-cover certificate was found, and the argument below
does not exclude every periodic domain. It does prove an unbounded necessary
condition that falsifies most proposed domains, including `R = Z`, and it
records two completed exact bounded searches.

The exact falsifier for a residue class `q Z + r` is:

\[
  \boxed{\text{some }d\in D\text{ must divide }\gcd(q,r+2).}
\]

If this condition fails, the class contains an explicit Dirichlet family of
points outside the image of every nonempty composition. Thus such a class
cannot occur in an invariant exact-cover domain.

## 1. Coordinates and words

Fix

\[
D=\{2,3,5,9,14,17,26,27,33,41,44,50,51,53,65,69,77,80,81,84\}.
\]

For `f_d(x)=dx-1`, conjugation by `u=x-1` gives

\[
g_d(u)=du+(d-2),\qquad g_d(\mathbb Z)=d\mathbb Z-2.
\]

For a nonempty word `w=(d_1,...,d_k)` in application order, put

\[
G_w=g_{d_k}\circ\cdots\circ g_{d_1}=a_wu+b_w,
\qquad a_w=\prod_{j=1}^k d_j.
\]

The recurrence used by the code is

\[
(a,b)\longmapsto (da,db+d-2).
\]

It gives `a_w>1` and `b_w>=0` exactly, with no floating-point arithmetic.

## 2. What would constitute a certificate

Let `R` be a nonempty finite union of residue classes modulo `q`. Suppose a
finite word family `W` has all three properties

1. `G_w(R) subset R` for every `w in W`;
2. the sets `G_w(R)` are pairwise disjoint;
3. `sum_{w in W} 1/a_w = 1` exactly.

Then

\[
R=\bigsqcup_{w\in W}G_w(R). \tag{2.1}
\]

Indeed, `R` has a positive rational density, while

\[
d(G_w(R))=\frac{d(R)}{a_w}.
\]

The union in (2.1) is a periodic subset of `R` with the same density as `R`.
A nonempty periodic complement has positive density, so the complement is
empty. This proves (2.1) without checking a large common period.

This periodic version is enough for the proof of Shamazov--Talambutsa,
[Theorem 7](https://arxiv.org/pdf/2507.06875). Their Theorem 2 at `sigma=1`
gives a linear lower bound for the orbit multiset because of property 3.
Every orbit point stays in `R`. A least repeated orbit value cannot have two
different final maps by property 2; if the final maps agree, injectivity gives
a smaller repeated predecessor. Hence the orbit multiset has multiplicity
one and the orbit set has `Omega(X)` elements.

A safe seed completes the transfer to Problem 424. For example,

\[
x_0=87=2\cdot44-1\in A,
\qquad u_0=86.
\]

Since `87>max D`, every elementary operation inside every word uses distinct
inputs and strictly increases the current value. Therefore a certificate
whose domain contains `86` would give a positive-density subset of `A`.

## 3. Unbounded outer-image obstruction

### Proposition 3.1

Let `R` be a finite union of residue classes modulo `q`. If

\[
R=\bigcup_{w\in W}G_w(R)
\]

for any finite family of nonempty `D`-words (disjointness is not needed), then
every residue `r` used by `R` satisfies

\[
\exists d\in D:\quad d\mid\gcd(q,r+2). \tag{3.1}
\]

Equivalently,

\[
R\subseteq
\bigcup_{\substack{d\in D\\d\mid q}}(-2\pmod d). \tag{3.2}
\]

### Proof

The last letter `d` of a word is its outer map, so

\[
G_w(\mathbb Z)\subseteq g_d(\mathbb Z)=d\mathbb Z-2.
\]

Consequently each full class `q Z+r` in `R` must be contained in
`union_{d in D}(d Z-2)`.

Put

\[
h=\gcd(q,r+2),\qquad q'=q/h,\qquad c=(r+2)/h.
\]

Then `gcd(q',c)=1`. By Dirichlet's theorem, choose a prime
`p congruent c (mod q')` with `p>84`. For some integer `n`,

\[
qn+r+2=hp.
\]

If `d in D` divides this number, then `p>max D` implies `gcd(d,p)=1`,
so `d|h`. Therefore, if no `d in D` divides `h`, the point `qn+r` lies in
the proposed domain class but outside every possible word image, a
contradiction. This proves (3.1). Conversely, `d|gcd(q,r+2)` makes the whole
class lie in `d Z-2`, proving the equivalence with (3.2). QED.

### Consequences and falsifier

- No composition family can cover `Z`: choose any prime `p>84`; then
  `u=p-2` is in no `g_d(Z)`, hence in no nonempty word image.
- A progression `q Z+r` is impossible unless some `d in D` divides `q` and
  `r congruent -2 (mod d)`.
- Every residue of a finite-union domain must separately pass the same test.
- The obstruction is not a solution: for example `2 Z` passes it because
  `g_2(Z)=2 Z`. Further invariance and disjointness constraints are needed.

This is stronger than the one-step overlap observation in
`A04_modern_literature.md`: compositions can have disjoint images, but their
outer letters still force Proposition 3.1.

## 4. Exact bounded searches

The code is in `problems/424/compute/wave2/B05/`.

- `search_exact_cover.py` generates distinct affine maps exactly and builds
  finite exact-cover models.
- `verify_certificate.py` independently recomputes words, invariance,
  reciprocal slopes, pairwise image intersections, the seed witness, and a
  finite-period replay when the period is at most 2,000,000.
- `test_exact_cover.py` checks composition order, deduplication, the
  obstruction filter, progression conjugation, and a synthetic exact cover.

For a progression `R=q Z+r`, an invariant map `G(u)=au+b` induces

\[
n\longmapsto an+\frac{(a-1)r+b}{q}.
\]

For a finite union, the model is expanded exactly modulo `qL`, where every
candidate slope divides the master period `L`. OR-Tools CP-SAT imposes one
selected image at every target residue. `INFEASIBLE` is therefore exact for
the stated finite model; `UNKNOWN` is reported separately.

Completed runs:

1. `L=2160`, word depth at most 7, progressions `q<=48`, and all residue
   unions `q<=10` containing a direct safe seed `xy-1>84` with distinct
   `x,y in D`: 1,019 progression cases and 2,024 union cases were
   `INFEASIBLE`; 0 were `UNKNOWN`.
2. `L=12960`, word depth at most 9, progressions `q<=120` with the same safe
   seed rule: 3,451 classes were eliminated by Proposition 3.1 and the
   remaining 2,272 models were `INFEASIBLE`; 0 were `UNKNOWN`.

No certificate file was produced. These computations do not exclude words
with slopes not dividing the selected `L`, deeper words, larger moduli, or a
domain whose first known safe seed is not a direct product of two elements of
`D`.

The enlarged finite-union run (`L=12960`, depth 9, `q<=12`) was interrupted
at the audit deadline. It yields no mathematical claim.

## 5. Next search

Resume the exact finite-union search at `L=12960`, depth 9, `q<=12`, with
per-modulus checkpoints, retaining only residues allowed by Proposition 3.1.
Then enlarge the safe-seed witness pool and use master periods containing the
prime factors from `14,17,26,33,41,44,51,53,65,69,77,84`; the completed
smooth masters primarily test words over `2,3,5,9,27,81` (plus divisors such
as `80` only when they divide the chosen master).
