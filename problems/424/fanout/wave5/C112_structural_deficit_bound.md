# C112: structural deficit bound

## DIRECT ROUTE

1. **Exact final deliverable.** Prove that every hard even hole `h` satisfies
   `s(h) >= d(h)-8`, give an exact counterexample, or prove a strictly weaker
   quantified structural-pair bound that still makes the C99 estimate close.
2. **Current frontier.** Bound by eight the admissible factor pairs of a hard
   even hole for which no missing endpoint has a structural splitless seed-2
   root.
3. **Bridge to C99.** If the frontier holds and `K=floor((log X)^c)` with
   `1/2<c<log 2`, every hard `h<=X` with `d(h)>=K+1` has at least `K-7`
   structural pairs.  Choosing one structural missing endpoint per such pair
   gives distinct divisor incidences.  The C85 incidence argument then gives
   `H(X) <= B_K(X) + (X+1) W_E(X)/(K-7) = o(X)` by C99.3 and C99.5.
4. **Next falsifiable action.** Run an exact sparse factor-shape search, using
   recursive closure queries rather than the C105 contiguous state sieve, for
   hard holes above `4*10^9` with `d(h)-s(h)>=9`.
5. **Exit condition.** Stop on an independently replayed deficit-nine
   counterexample, a complete proof covering both hard arithmetic shapes and
   all diagonal/residue/seed-root endpoint cases, or a weaker quantified bound
   inserted into the displayed C99 bridge.

## Verdict

The universal candidate

\[
                         s(h)\ge d(h)-8                         \tag{1}
\]

is neither proved nor refuted here.  A structurally different sparse search
does rule out the most direct multiplicative falsifier well beyond both C105
ranges.  It tests `39,229` prime lifts, with largest source

\[
                 h=2,067,095,547,081,902,
\]

and finds that every source is generated, hence none is a hard counterexample.
The ordinary and optimized searches and independent replays are byte-identical.

The analytic result is a strictly weaker quantified target that still closes
C99.  It is enough to prove

\[
                         s(h)\ge d(h)^{3/4}-8                    \tag{2}
\]

for every hard even hole.  More generally, any uniform estimate

\[
                  s(h)\ge A d(h)^\alpha-B,
 \qquad A>0,\quad \alpha>{1\over2\log2},                       \tag{3}
\]

with constant `B` closes C99.  Equations (2) and (3) are isolated theorem
targets, not claims proved by the finite search.

## 1. Structural-pair incidence theorem

Retain C105's literal definitions.  For a hard `h`, its admissible pairs are
`P(h)`, `d(h)=|P(h)|`, and `s(h)` counts the pairs having a missing endpoint
whose seed-2 root is structural splitless.  Put

\[
 W_E(X)=\sum_{\substack{r\le X\\r\text{ structural splitless}}}
                   {1\over r-1}.
\]

### Theorem C112.1 (structural incidence bound)

Fix integers `X>=2`, `K>=0`, and a real `L>0`.  If every hard `h<=X` with
`d(h)>=K+1` satisfies `s(h)>=L`, then

\[
 \#\{h\le X:h\text{ hard},\ d(h)\ge K+1\}
       \le {X+1\over L}W_E(X).                                  \tag{4}
\]

Consequently,

\[
 H(X)\le B_K(X)+{X+1\over L}W_E(X).                             \tag{5}
\]

#### Proof

For each of the at least `L` structural pairs of a counted `h`, choose one
missing endpoint `p` whose seed-2 root `r` is structural splitless.  The
quantity on the left is integral, so `s(h)>=L` means at least `ceil(L)`
choices; retaining the real `L` only weakens the resulting inequality.

All endpoints are odd because `h+1` is odd.  Distinct complementary factor
pairs have disjoint endpoints: each divisor of `h+1` lies in exactly one
unordered complementary pair.  The strict rule `a<b` removes the diagonal.
Thus the chosen endpoints for one source are distinct, even when both
endpoints of a pair are missing or both have structural roots.

For a fixed odd missing endpoint `p`, the divisibility `p|(h+1)` permits at
most `floor((X+1)/p)` sources.  If `r` is its even seed-2 root, then

\[
                         p=2^j(r-1)+1,\qquad j\ge1.
\]

Therefore the total number of chosen incidences is at most

\[
 \begin{aligned}
 \sum_r\sum_{j\ge1}\left\lfloor{X+1\over2^j(r-1)+1}\right\rfloor
 &\le (X+1)\sum_r\sum_{j\ge1}{1\over2^j(r-1)}\\
 &= (X+1)W_E(X).
 \end{aligned}                                                   \tag{6}
\]

Every visible root satisfies `r<p<=X+1`, and in fact `r<=X`, so the displayed
root sum is valid.  Comparing the lower incidence count `L` per source with
(6) proves (4), and separating the sources with `d(h)<=K` proves (5).

The proof treats both C96 hard residue shapes uniformly.  If `3` does not
divide `h+1`, both factors are `2 mod 3`; if `h+1=3R`, exactly one factor is
divisible by `3`.  In either case the factors are odd allowed divisors, and
the complementary-pair and seed-root arguments above are unchanged.  QED.

## 2. A weaker bound that closes C99

### Theorem C112.2 (power criterion)

Suppose constants `A>0`, `B`, and

\[
                         \alpha>{1\over2\log2}                  \tag{7}
\]

exist such that (3) holds for every hard even hole.  Then `H(X)=o(X)`.

#### Proof

Choose `c` with

\[
                         {1\over2\alpha}<c<\log2                 \tag{8}
\]

and set `K=floor((log X)^c)`.  C99 Theorem C99.3 gives

\[
                         B_K(X)=O_c(X/\log\log X)=o(X).           \tag{9}
\]

For `d(h)>=K+1`, equation (3) gives

\[
                         s(h)\ge A(K+1)^\alpha-B=:L_X.
\]

This is positive for large `X`.  Apply Theorem C112.1 and C99 Proposition
C99.5:

\[
 {H(X)\over X}
 \le {B_K(X)\over X}
   +O\!\left({(\log X)^{1/2}\over(\log X)^{c\alpha}}\right)
 =o(1),                                                            \tag{10}
\]

where (8) makes the last exponent negative.  QED.

Taking `A=1`, `B=8`, and `alpha=3/4` gives (2), with any

\[
                         {2\over3}<c<\log2.                       \tag{11}
\]

This is strictly weaker than (1): for every integer `d>=1`,
`d^(3/4)-8<=d-8`, while, for example, `(d,s)=(16,0)` satisfies the weaker
numeric inequality and violates (1).  If (1) were proved instead, (5) would
give the stronger denominator `L=K-7`, allowing every `1/2<c<log 2`.

Thus (2) is a direct replacement frontier for C99, not a reformulation
without a bridge.  Proving it removes the non-splitless basin term in C99:
every high-pair hard source is paid directly by its structural pair
incidences.

## 3. Sparse lifted-family falsification

Start from C105's exact zero-structural hard source

\[
 \begin{aligned}
 N_0&=h_0+1=3\cdot13\cdot43\cdot557\cdot2213
              =2,067,138,957,\\
 (h_0,d(h_0),s(h_0))&=(2,067,138,956,8,0).
 \end{aligned}                                                    \tag{12}
\]

Each base pair has exactly one generated endpoint `g` and one missing
nonstructurally rooted blocker `m`:

| `m` | `g` |
|---:|---:|
| 557 | 3,711,201 |
| 1,671 | 1,237,067 |
| 2,213 | 934,089 |
| 21,723 | 95,159 |
| 23,951 | 86,307 |
| 71,853 | 28,769 |
| 285,477 | 7,241 |
| 311,363 | 6,639 |

Let `ell` be a prime with `ell=1 mod 3` and `ell` not dividing `N_0`.
The product `ell*N_0` is odd and squarefree.  Multiplication by `ell`
preserves allowed residues, and each base pair `(m,g)` gives exactly the two
admissible distinct pairs

\[
                         (m,\ell g),\qquad(\ell m,g).              \tag{13}
\]

There are no further pairs: placing `ell` on either side partitions all
allowed divisors, and squarefreeness excludes a diagonal.  Hence a hole in
this family would have `d=16`.  Its cofactor after removing `3` remains
`1 mod 3` with the two minus primes `557,2213`, so it is hard-shaped in the
`3R` case.  Most importantly, if any `ell*m` is generated, then the second
pair in (13) has two generated endpoints and generates `ell*N_0-1`.

`C112_lifted_family_search.py` recursively evaluates the exact least closure,
without a contiguous state array, for every such prime `ell<=1,000,000`.
For every one of the `39,229` primes it finds a generated multiplied blocker.
Using blockers in increasing order, the first-witness counts are

```text
m=557:   37,649
m=1,671:  1,573
m=2,213:      7
other m:      0
```

They sum to `39,229`.  The largest tested prime is `999,979`, giving the
largest source stated in the verdict.  The streaming digest of all ordered
`(ell,first_generated_blocker)` pairs is

```text
f80dda8b46e7fe5968ebb85cd585f5114d1b96a99927d905537f5b453910eda0
```

This is a finite exclusion of a targeted deficit-16 construction.  It is not
evidence promoted to (1) or (2).

## 4. Independent replay and hashes

The search enumerates divisors from explicit prime powers.  The independent
replay instead obtains divisors with `sympy.divisors`, has a separately
written closure classifier and iterative seed-root map, reconstructs the
base blockers, and recomputes every prime label and the streaming digest.
It reports `PASS` for all eleven claim checks.  Ordinary and optimized runs
are byte-identical for both the search and replay.

```powershell
python problems/424/compute/wave5/C112_lifted_family_search.py `
  --prime-limit 1000000 `
  --output problems/424/compute/wave5/C112_lifted_family_search_1m.json

python problems/424/compute/wave5/C112_lifted_family_verify.py `
  --claim problems/424/compute/wave5/C112_lifted_family_search_1m.json `
  --output problems/424/compute/wave5/C112_lifted_family_verify_1m.json
```

SHA-256:

```text
FC766EE3C11A6D0FE473DC216910F073DE7E15E47F96D2186708243A308764C8
  C112_lifted_family_search.py
93821827C7D9EA92D7B2C8593BE7978F8D2435E0F7F409658450DDB35F7E421B
  C112_lifted_family_verify.py
E417343E3D304069DAA8599BA46419088E71B0CF2563AF37ADFFEB6805DD24F3
  C112_lifted_family_search_1m.json
7A864A144F6BDF7AF2A9BF07383360C99202809F1007CD9C74BA0A9BA2BBE1F1
  C112_lifted_family_verify_1m.json
```

The `_O.json` artifacts have the same respective hashes.  No floating-point
quantity participates in search acceptance or replay acceptance.

## 5. Precise status for C99

Equation (1) remains an open candidate, with no exact counterexample in the
new lifted family.  Equation (2) is the strictly weaker quantified frontier
returned by C112.  If (2) is proved, Theorem C112.2 and C99 immediately give

\[
                              H(X)=o(X),
\]

so the C99 hard-hole route closes.  The present report proves that implication
and the exact finite exclusion; it does not claim the antecedent.
