# Magic Square of Distinct Positive Squares — Frozen 64-Lane Manifest

Frozen: 2026-07-21  
Execution window: one common eight-hour tranche; this file does not launch it.

## Audited direct bridge

Write (A=m^2).  The canonical certificate used by every lane is

```text
W = (m,b,c,
     r_b-,r_b+, r_c-,r_c+, r_sum-,r_sum+, r_diff-,r_diff+)
```

with (m,b,c>0), canonically (b>c), and

\[
 (r_d^-)^2=A-d,\qquad (r_d^+)^2=A+d
 \quad(d\in\{b,c,b+c,b-c\}).
\]

All roots must be positive and the nine squares consisting of (A) and the
eight displayed squares must be pairwise distinct.  A primitive certificate
is obtained by putting

\[
 g=\gcd(m,r_b^-,r_b^+,r_c^-,r_c^+,r_{sum}^-,r_{sum}^+,
             r_{diff}^-,r_{diff}^+)
\]

and dividing (m) and the eight roots by (g), and (b,c) by (g^2).
The final D4/transpose representative is the lexicographically least one.

Andrew Bremner's 1999 paper proves that every rational 3 by 3 magic square
has the normal form

\[
\begin{bmatrix}
A-b&A+b+c&A-c\\
A+b-c&A&A-b+c\\
A+c&A-b-c&A+b
\end{bmatrix}. \tag{B2}
\]

Consequently, `W` makes every entry in (B2) a positive integer square, and
direct addition gives common sum (3A).  Conversely, a distinct positive
integer square solution has form (B2).  Its corner deviations from (A), in
cyclic order, are (-b,-c,b,c).  Since distinctness gives (bc!=0), exactly one
corner in each antipodal pair has positive deviation.  Those two positive
corners are necessarily adjacent.  Rotate their common edge to the bottom;
then the new normal-form parameters are both positive.  A reflection in the
vertical axis swaps them, and distinctness lets us choose (b>c>0).  Its four
opposite pairs give exactly the four memberships in
(D_A).  Thus existence of `W` is equivalent to the target existence
statement, not merely a necessary condition.  Bremner's repeated-entry
criterion

\[
bc(b^2-c^2)(b^2-4c^2)(4b^2-c^2)=0
\]

is retained as a fast rejection, but the independent pairwise-distinctness
check remains authoritative.

For the elliptic bridge, Bremner uses

\[
E_\kappa:y^2=x(x^2-\kappa^2). \tag{B3}
\]

The paper states that (Q=(X,Y)\in E_\kappa(\mathbb Q)) belongs to
(2E_\kappa(\mathbb Q)) exactly when (X-\kappa,X,X+\kappa) are rational
squares.  Hence three doubled points with x-coordinates

\[
X_0=A-b,\qquad X_1=A,\qquad X_2=A+b
\]

in arithmetic progression give all nine rational squares in (B2), with
(c=\kappa); the converse is the same statement applied to Bremner's three
triples centered at (A-b), (A), and (A+b).  To reach the integer problem, a lane must output the
nine rational roots, choose their common denominator (L), multiply all
entries by (L^2), orient the result to (b>c>0), and emit `W`.  Algebraic
number-field examples in the paper do **not** cross this bridge.  Zero,
repeated, negative, merely near-magic, or non-rational specializations are
rejected.

Source audited directly: Andrew Bremner, *On squares of squares*, Acta
Arithmetica 88 (1999), equations (2)–(7),
<https://matwbn.icm.edu.pl/ksiazki/aa/aa88/aa8837.pdf>.

## Common execution and result rules

- Let `T0` be the common tranche start.  Every lane stops at the earlier of
  complete exhaustion of its stated finite domain or `T0 + 8 hours`.
- Complete exhaustion with no `W` is the lane's exact falsifier and is logged
  only as `NO_HIT` for that domain.  Reaching the wall clock first is
  `TIMEOUT_INCOMPLETE`, not a falsifier and not evidence of nonexistence.
- Every output is the exact integer certificate `W` plus the lane-specific
  reconstruction data.  It is a candidate only after both independent exact
  verifiers accept it.
- Candidate hashes use the primitive D4/transpose canonical form.  A
  rediscovery is verification evidence, not a new candidate.
- No interval, height, coefficient box, or denominator band is extended after
  the stop.  Modular exclusions, density data, and near misses are diagnostics
  only.

## G — 16 Gaussian-center lanes

For every center root (m) in the stated interval, factor (m) exactly and
enumerate all (u^2+v^2=2m^2) through \(\mathbb Z[i]\).  Completeness is
audited against

\[
r_2(2m^2)=4\prod_{p\equiv1\pmod4}(2v_p(m)+1).
\]

Each pair (0<u<v) gives (d=(v^2-u^2)/2\in D_{m^2}).  The exact hash join
tests (b,c,b+c,b-c\in D_{m^2}).  Bremner's 2001 sequel reports Buell's
search excluding the hourglass when the central entry is **strictly less
than** (25*10^24).  Thus it excludes (m<5,000,000,000,000), but does not
exclude equality.  G01 deliberately includes (m=5,000,000,000,000).
G02--G16 each contain exactly (2^{24}) centers; G01 contains one additional
boundary center.  The sixteen intervals remain disjoint.  Source for this
strict bound: Bremner, *On squares of squares II*, Acta Arithmetica 99
(2001), Section 1,
<https://www.impan.pl/shop/publication/transaction/download/product/82367>.
`G-W` means `{factorization,
representation-count audit, W}`.  `G_FAIL` means every center in the closed
interval has a complete representation audit and none emits `W`.

| ID | Explicit finite parameters | Candidate output type | Exact falsifier | 8-hour stop | Bridge |
|---|---|---|---|---|---|
| G01 | (m=5,000,000,000,000..5,000,016,777,216) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G02 | (m=5,000,016,777,217..5,000,033,554,432) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G03 | (m=5,000,033,554,433..5,000,050,331,648) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G04 | (m=5,000,050,331,649..5,000,067,108,864) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G05 | (m=5,000,067,108,865..5,000,083,886,080) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G06 | (m=5,000,083,886,081..5,000,100,663,296) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G07 | (m=5,000,100,663,297..5,000,117,440,512) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G08 | (m=5,000,117,440,513..5,000,134,217,728) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G09 | (m=5,000,134,217,729..5,000,150,994,944) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G10 | (m=5,000,150,994,945..5,000,167,772,160) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G11 | (m=5,000,167,772,161..5,000,184,549,376) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G12 | (m=5,000,184,549,377..5,000,201,326,592) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G13 | (m=5,000,201,326,593..5,000,218,103,808) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G14 | (m=5,000,218,103,809..5,000,234,881,024) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G15 | (m=5,000,234,881,025..5,000,251,658,240) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |
| G16 | (m=5,000,251,658,241..5,000,268,435,456) | `G-W` | `G_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D |

## E — 16 Bremner elliptic exact-reconstruction lanes

For every positive squarefree integer \(\kappa\) in the stated interval,
enumerate every integral precursor point

\[
P=(x,y)\in E_\kappa(\mathbb Q),\qquad |x|\le2^{20},\quad y>0,
\]

by exact integer-square testing, compute (Q=2P) exactly, and deduplicate
non-torsion outputs by (X=x(Q)).  Hash-join triples (X_0<X_1<X_2) with
(X_0+X_2=2X_1).  Require all nine values (X_i) and
(X_i\pm\kappa) used in (B2) to be positive, rational squares, and distinct.
`E-W` means `{kappa, P0,P1,P2, Q0,Q1,Q2, nine rational roots, clearing
denominator, W}`.  `E_FAIL` means complete enumeration of all stated
squarefree \(\kappa\), all integral (x) in the closed box, and all resulting
AP joins emits no `W`.  This finite domain contains **integral precursor
points only**.  Consequently, `E_FAIL`/`NO_HIT` means no certificate arose
from these doubled integral precursors in the stated x-box; it is not an
enumeration of all rational points, all denominator heights, or all of
(E_kappa(Q)).

| ID | Explicit finite parameters | Candidate output type | Exact falsifier | 8-hour stop | Bridge |
|---|---|---|---|---|---|
| E01 | squarefree kappa=1..64; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E02 | squarefree kappa=65..128; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E03 | squarefree kappa=129..192; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E04 | squarefree kappa=193..256; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E05 | squarefree kappa=257..320; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E06 | squarefree kappa=321..384; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E07 | squarefree kappa=385..448; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E08 | squarefree kappa=449..512; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E09 | squarefree kappa=513..576; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E10 | squarefree kappa=577..640; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E11 | squarefree kappa=641..704; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E12 | squarefree kappa=705..768; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E13 | squarefree kappa=769..832; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E14 | squarefree kappa=833..896; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E15 | squarefree kappa=897..960; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |
| E16 | squarefree kappa=961..1,024; -2^20 <= x <= 2^20 | `E-W` | `E_FAIL` on this curve/point box | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid via (B3), AP, clearing |

## N — 16 seven-entry near-miss completion lanes

These lanes use a second, disjoint center-root tranche.  For each (m), the
Gaussian representation engine constructs (D_{m^2}), but first hash-joins

\[
b>c>0,\qquad b,c,b+c\in D_{m^2},\qquad b+c<m^2.
\]

Those three memberships give a seven-square-entry near miss.  The lane then
tests the one theorem-closing condition (b-c\in D_{m^2}).  A near miss by
itself is never output.  `N-W` means `{three-membership near-miss audit,
missing-pair roots, W}`.  `N_FAIL` means complete representation enumeration,
complete additive-triple joining, and failure to complete every triple for
every center in the closed interval.  Each interval has (2^{24}) centers
and is disjoint from every other G or N interval.

| ID | Explicit finite parameters | Candidate output type | Exact falsifier | 8-hour stop | Bridge |
|---|---|---|---|---|---|
| N01 | (m=5,000,268,435,457..5,000,285,212,672) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N02 | (m=5,000,285,212,673..5,000,301,989,888) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N03 | (m=5,000,301,989,889..5,000,318,767,104) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N04 | (m=5,000,318,767,105..5,000,335,544,320) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N05 | (m=5,000,335,544,321..5,000,352,321,536) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N06 | (m=5,000,352,321,537..5,000,369,098,752) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N07 | (m=5,000,369,098,753..5,000,385,875,968) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N08 | (m=5,000,385,875,969..5,000,402,653,184) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N09 | (m=5,000,402,653,185..5,000,419,430,400) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N10 | (m=5,000,419,430,401..5,000,436,207,616) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N11 | (m=5,000,436,207,617..5,000,452,984,832) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N12 | (m=5,000,452,984,833..5,000,469,762,048) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N13 | (m=5,000,469,762,049..5,000,486,539,264) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N14 | (m=5,000,486,539,265..5,000,503,316,480) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N15 | (m=5,000,503,316,481..5,000,520,093,696) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |
| N16 | (m=5,000,520,093,697..5,000,536,870,912) | `N-W` | `N_FAIL` on this interval | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid only after missing pair emits MSQ-D |

## S — 16 structural rational-identity lanes

For a canonical reduced pair (p>q>0), \(\gcd(p,q)=1\), with (p-q) odd,
put

\[
H=p^2+q^2,\quad U=p^2-2pq-q^2,\quad V=p^2+2pq-q^2,
\]
\[
f(p,q)=\frac{4pq(p^2-q^2)}{H^2}.
\]

Then

\[
U^2=H^2-H^2f(p,q),\qquad
V^2=H^2+H^2f(p,q).
\]

Deduplicate each reduced rational value of (f) by its lexicographically
least pair.  Seek four canonical pairs satisfying the exact rational
identities

\[
f_3=f_1+f_2,\qquad f_4=f_1-f_2,qquad f_1>f_2>0,
\]

with all induced roots nonzero and all nine squares distinct.  Clear the
four rational root denominators to obtain (b=m^2f_1), (c=m^2f_2), and
`W`.  The lane key is (P=\max_i p_i); therefore the sixteen parameter
domains are disjoint even though lower-(p) pairs may be shared read-only
inputs.  `S-W` means `{four canonical pairs, exact two-identity audit,
denominator clearing, W}`.  `S_FAIL` means exhaustive canonical-pair
generation and exhaustive exact rational hash joining for the stated closed
(P)-band emits no `W`.

| ID | Explicit finite parameters | Candidate output type | Exact falsifier | 8-hour stop | Bridge |
|---|---|---|---|---|---|
| S01 | canonical quartet with (P=2..128) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S02 | canonical quartet with (P=129..256) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S03 | canonical quartet with (P=257..384) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S04 | canonical quartet with (P=385..512) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S05 | canonical quartet with (P=513..640) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S06 | canonical quartet with (P=641..768) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S07 | canonical quartet with (P=769..896) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S08 | canonical quartet with (P=897..1,024) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S09 | canonical quartet with (P=1,025..1,152) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S10 | canonical quartet with (P=1,153..1,280) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S11 | canonical quartet with (P=1,281..1,408) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S12 | canonical quartet with (P=1,409..1,536) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S13 | canonical quartet with (P=1,537..1,664) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S14 | canonical quartet with (P=1,665..1,792) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S15 | canonical quartet with (P=1,793..1,920) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |
| S16 | canonical quartet with (P=1,921..2,048) | `S-W` | `S_FAIL` on this (P)-band | exhaust or `T0+8h`; else `TIMEOUT_INCOMPLETE` | valid MSQ-D after exact clearing |

## Bridge disposition

All 64 listed lanes have a direct MSQ-D bridge because success is defined
only by emission of `W`.  No modular-only, density-only, algebraic-number-only,
repeated-entry, seven-line-sum, or bounded-obstruction lane was added to fill
the count.  In particular, a Bremner defect polynomial with no rational root
or a root only in a non-rational number field is a lane diagnostic, not an
accepted output.
