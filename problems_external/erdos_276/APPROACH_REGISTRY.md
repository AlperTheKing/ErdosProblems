# Erdős Problem 276 — Approach Registry

Selected for route audit: 2026-07-23
Status: AUDIT

## DIRECT ROUTE

### 1. Exact final deliverable

For the explicit Ismailescu--Son sequence from Theorem 3 of *A New Kind of
Fibonacci-Like Sequence of Composite Numbers*, prove that no positive integer
has a nontrivial common factor with every term. Together with their proved
compositeness theorem, this resolves Erdős Problem 276.

### 2. Current frontier lemma

Write \(y_n=x_{2n+1}\). For a prime \(r\) which divides some \(y_n\), let
\(z(r)\) be the least positive \(d\) with \(r\mid F_d\), and put
\(h_r=z(r)/\gcd(z(r),2)\). Test the strictly stronger rank-density lemma
\(\sum_{r\in S}1/h_r<1\) for every finite set \(S\) of primes occurring in
the odd subsequence.

### 3. Explicit logical bridge

The recurrence addition formula and \(\gcd(x_n,x_{n+1})=1\) imply
\(\gcd(y_m,y_n)\mid F_{2|m-n|}\). Hence, for each such prime \(r\), its zero
indices in \(y_n\) form one residue class modulo \(h_r\). The rank-density
lemma and the union bound would leave an index outside the zero classes of
every finite \(S\). Thus no finite prime set covers the odd terms, and no
integer has a common factor with every term of the full sequence.

### 4. Next falsifiable action

Derive the gcd and zero-period identities exactly, then enumerate all primes
\(r\le 10^5\) occurring in \(y_n\bmod r\), compute \(h_r\), and test whether
the partial reciprocal sum reaches \(1\). Reaching \(1\) kills this density
route; it is not evidence for a finite cover.

### 5. Exit condition

Exit the rank-density route immediately if its finite-prime test fails. Exit
the whole #276 route if primitive-divisor theory only supplies new factors
without excluding an old finite cover and the exact zero classes yield no
strictly smaller non-cover lemma. Do not replace it by successively larger
bounded prime searches.

## Sources

- `../_sources/neelsomani_gpt_erdos/data/solutions/276/candidate_solution.md`
- Ismailescu and Son, Journal of Integer Sequences 17 (2014), Article 14.8.2.

## R1 DEAD (2026-07-23)

- Exact identity: gcd(y_i,y_j) divides F_(2|i-j|); each prime-zero set is one anchored residue class modulo z(r)/gcd(z(r),2).
- Falsifier: primes 2, 3, and 5 divide y_0 and have reduced ranks 3, 2, and 5, so the proposed reciprocal-rank sum is 31/30.
- DEAD: rank-density obstruction is false; primitive divisors do not exclude an old finite cover, and anchored non-cover is the unresolved residual.
