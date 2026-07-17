# C105: structural-pair fraction census and the recurrent `d=8` zero family

## Verdict

The proposed sharper C85 count has substantial structural mass at the
largest divisor-pair levels seen, but the requested asymptotic statement is
**not proved**.

The exact contiguous census through

\[
X=4,000,000,000
\]

finds

\[
\max_{h\le X}(d(h)-s(h))=8.                         \tag{1}
\]

In particular, the data are compatible with the stronger bound
`s(h) >= d(h)-8`.  This is only a finite observation.  It is not promoted to
a lemma.

There is also an exact affine `d=8` template with recurrent `s=0` instances.
The sparse exact scan finds nine such instances, the largest at

\[
h=918,066,571,382.
\]

This rules out a positive bound with no additive constant, even far beyond
the contiguous census.  It does not contradict

\[
s(h)\ge \alpha d(h)-O(1)
\]

for fixed `alpha>0`, because `d=8` stays bounded.  No proof of such an
inequality and no infinite family with unbounded `d` and `s=o(d)` was found.
Consequently C105 does not close the C99 trapping gap.

## 1. Literal statistic

The implementation uses the C85/C99 closure on the allowed integers

\[
\mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

with seeds `2,3` and the distinct-factor rule `ab-1`, `2<=a<b`.
Classification is performed in increasing order, so every dependency is
strictly smaller than the classified value.

For a hard hole `h`, let

\[
\mathcal P(h)=\{(a,b):2\le a<b,\ ab=h+1,\ a,b\in\mathcal A\},
\qquad d(h)=|\mathcal P(h)|.
\]

Every pair has a missing odd endpoint.  For a missing odd endpoint `p`, its
seed-2 root is obtained by repeatedly replacing `p` by `(p+1)/2` until the
first even value.  A pair contributes one to `s(h)` exactly when at least one
of its missing endpoints has a structural splitless seed-2 root.  A pair is
counted at most once.

All acceptance arithmetic is integer arithmetic.  Ratios are compared by
cross multiplication.

## 2. Contiguous exact census

The main C++ scan classifies every integer in `[2,X]`, enumerates every
admissible divisor pair, and records `(h,d(h),s(h))` for every hard hole.

| cutoff `X` | hard holes | max `d` | `s=0` hard holes | largest `d` with `s=0` | max `d-s` | seconds |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000,000 | 45,583 | 9 | 4,330 | 4 | 5 | 0.030 |
| 100,000,000 | 3,368,726 | 12 | 364,176 | 6 | 8 | 3.410 |
| 1,000,000,000 | 29,010,146 | 16 | 3,305,307 | 6 | 8 | 38.640 |
| 4,000,000,000 | 106,360,959 | 18 | 12,408,349 | 8 | 8 | 202.326 |

At `X=4,000,000,000`, the exact distribution by `d` is:

| `d` | hard count | `s=0` count | min `s` | max `d-s` | first min-`s` witness |
|---:|---:|---:|---:|---:|---:|
| 1 | 58,935,729 | 10,207,551 | 0 | 1 | 534 |
| 2 | 41,675,672 | 2,163,811 | 0 | 2 | 11,576 |
| 3 | 970,573 | 10,968 | 0 | 3 | 516,312 |
| 4 | 4,627,919 | 25,986 | 0 | 4 | 112,412 |
| 5 | 3,238 | 13 | 0 | 5 | 298,782,840 |
| 6 | 101,192 | 19 | 0 | 6 | 43,378,670 |
| 7 | 27 | 0 | 3 | 4 | 1,094,959,242 |
| 8 | 45,708 | 1 | 0 | 8 | 2,067,138,956 |
| 9 | 425 | 0 | 3 | 6 | 79,285,674 |
| 10 | 47 | 0 | 3 | 7 | 767,381,208 |
| 12 | 414 | 0 | 4 | 8 | 38,624,780 |
| 16 | 14 | 0 | 8 | 8 | 2,796,867,114 |
| 18 | 1 | 0 | 14 | 4 | 2,934,744,174 |

The requested suffix minima by divisor threshold `D` are:

| `D` | hard holes with `d>=D` | min `s/d` | witness `h` | max `d-s` |
|---:|---:|---:|---:|---:|
| 1 | 106,360,959 | 0/1 | 534 | 8 |
| 2 | 47,425,230 | 0/2 | 11,576 | 8 |
| 3 | 5,749,558 | 0/4 | 112,412 | 8 |
| 4 | 4,778,985 | 0/4 | 112,412 | 8 |
| 5 | 151,066 | 0/6 | 43,378,670 | 8 |
| 6 | 147,828 | 0/6 | 43,378,670 | 8 |
| 7 | 46,636 | 0/8 | 2,067,138,956 | 8 |
| 8 | 46,609 | 0/8 | 2,067,138,956 | 8 |
| 9 | 901 | 3/10 | 767,381,208 | 8 |
| 10 | 476 | 3/10 | 767,381,208 | 8 |
| 11 | 429 | 4/12 | 38,624,780 | 8 |
| 12 | 429 | 4/12 | 38,624,780 | 8 |
| 13 | 15 | 8/16 | 2,796,867,114 | 8 |
| 14 | 15 | 8/16 | 2,796,867,114 | 8 |
| 15 | 15 | 8/16 | 2,796,867,114 | 8 |
| 16 | 15 | 8/16 | 2,796,867,114 | 8 |
| 18 | 1 | 14/18 | 2,934,744,174 | 4 |

The first overall maximum-deficit witness is

\[
(h,d,s)=(38,624,780,12,4).
\]

The full JSON contains every extremal pair list and endpoint/root
classification.  Its two streaming FNV-1a-64 digests are

```text
classification states, n=2..4,000,000,000: 08eb5810482ec820
hard triples (h,d,s):                         025149b7afc4b812
```

## 3. Exact recurrent `d=8` template

Put

\[
C=3\cdot13\cdot43\cdot557=934,089
\]

and, for a prime `q` with `q=2 (mod 3)` and `q` not dividing `C`, put

\[
h_q=Cq-1.                                          \tag{2}
\]

### Lemma C105.1 (factor-pair template)

For every such `q`, `d(h_q)=8`, and its admissible factor pairs are the
following unordered pairs:

\[
\begin{array}{llll}
(557,1677q),&(1671,559q),&(7241,129q),&(21723,43q),\\
(23951,39q),&(q,934089),&(3q,311363),&(13q,71853).
\end{array}                                        \tag{3}
\]

#### Proof

Exactly one member of a factor pair contains the prime `3`, so that member
is allowed automatically.  The other member is a product of a subset of
`13,43,557,q`.  The factors `13,43` have residue `1` modulo `3`, while
`557,q` have residue `2`.  The member not containing `3` is allowed exactly
when it contains an odd number of the two residue-2 primes.  There are
`2*2^2=8` such subsets, and expanding them gives (3).  Since `Cq` is
squarefree, none is diagonal.  QED.

The fixed endpoints in (3) have the following exact closure states:

| value | state | seed-2 root | root state |
|---:|---|---:|---|
| 557 | other hole | 140 | other hole |
| 1,671 | other hole | 836 | other hole |
| 7,241 | generated | - | - |
| 21,723 | other hole | 10,862 | other hole |
| 23,951 | other hole | 11,976 | hard |
| 934,089 | generated | - | - |
| 311,363 | other hole | 155,682 | hard |
| 71,853 | other hole | 17,964 | hard |

These are finite recursive checks.  For the generated entries, explicit
generating pairs are `(3,2414)` for `7241`, and `(2,467045)` (also
`(5,186818)`) for `934089`.  Exhaustive admissible-pair lists for all fixed
entries are checked by the sparse verifier.

It follows directly from (3) and the table that

\[
h_q\text{ is hard}
\quad\Longleftrightarrow\quad
q\text{ and }129q\text{ are holes}.                 \tag{4}
\]

Indeed, the six other pairs are blocked by a fixed hole, while the only
pairs with a fixed generated endpoint are `(7241,129q)` and `(q,934089)`.
The shape condition in the hard classification is automatic because
`(h_q+1)/3=311363q` is not allowed.

Moreover, for a hard `h_q`, one has `s(h_q)=0` exactly when every missing
member of

\[
\{q,3q,13q,39q,43q,129q,559q,1677q\}               \tag{5}
\]

has a non-splitless seed-2 root.  Thus (2)-(5) reduce this family to eight
exact recursive state queries, without scanning the interval up to `h_q`.

The exact scan over primes `q<=1,000,000` finds 18 hard members and the
following nine with `s=0`:

| `q` | `h_q` |
|---:|---:|
| 2,213 | 2,067,138,956 |
| 5,087 | 4,751,710,742 |
| 10,667 | 9,963,927,362 |
| 11,927 | 11,140,879,502 |
| 38,747 | 36,193,146,482 |
| 227,387 | 212,399,695,442 |
| 632,747 | 591,042,012,482 |
| 842,987 | 787,424,883,842 |
| 982,847 | 918,066,571,382 |

This is exact recurrence evidence, not an infinitude theorem.  Proving that
infinitely many primes `q` satisfy the closure conditions in (4)-(5) is an
additional number-theoretic problem not discharged here.

## 4. Consequence for the proposed C85 escape

Within the complete range, structural pair mass appears at least linear in
`d` once `d>=9`, and the observed deficit never exceeds eight.  The data
therefore point to the sharper possible target

\[
s(h)\ge d(h)-8.                                      \tag{6}
\]

But neither the closure recursion nor the factor-pair geometry currently
proves (6).  The `d=8,s=0` template also shows that any proof of a positive
fraction must genuinely retain an additive exceptional term; direct
per-pair positivity is false.

The output of C105 is therefore:

1. a certified finite lower envelope through `4*10^9`;
2. an exact algebraic explanation for the first and recurrent `d=8,s=0`
   examples;
3. a narrowed proof target such as (6), but no asymptotic bridge for C99.

## 5. Reproduction and independent check

The contiguous implementation is C++20 and uses one worker.  Its peak range
uses a byte state array and a 16-bit odd-SPF array.

```powershell
g++ -std=c++20 -O3 -DNDEBUG `
  problems/424/compute/wave5/C105_structural_pair_census.cpp `
  -o problems/424/compute/wave5/C105_structural_pair_census.exe

problems/424/compute/wave5/C105_structural_pair_census.exe `
  4000000000 `
  problems/424/compute/wave5/C105_structural_pair_census_4e9.json
```

The independent Python checker does not import or invoke the C++ program.  It
uses a full SPF sieve, a separately written recursive divisor constructor,
and a separate ascending closure/classification loop.  At `X=1,000,000` it
agrees on the full summary, every exact-by-`d` row, the classification
digest, and the hard-triple digest:

```powershell
python problems/424/compute/wave5/C105_structural_pair_verify.py `
  --limit 1000000 `
  --claim problems/424/compute/wave5/C105_structural_pair_census_1e6.json `
  --output problems/424/compute/wave5/C105_structural_pair_verify_1e6.json
```

The result is

```text
claim_check.status = PASS
limit = summary = exact_by_d = digests = true
```

Running the checker under `python -O` produces a byte-identical JSON file, so
the acceptance result does not depend on assertions.  The sparse affine scan
is reproduced by

```powershell
python problems/424/compute/wave5/C105_parametric_extension.py `
  --prime-limit 1000000 `
  --output problems/424/compute/wave5/C105_parametric_extension_1e6.json
```

All artifact SHA-256 values are recorded in
`problems/424/compute/wave5/C105_SHA256.txt`.

