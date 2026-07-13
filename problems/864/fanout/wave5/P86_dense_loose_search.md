# P86: exact archived-ruler search for dense loose fold triangles

## Verdict

No infinite counterfamily was found.  In an exact scan of archived rulers and
two endpoint-preserving transformation lanes, the largest normalized loose
triangle count at order at least 20 is

\[
 {T_F\over p^3}={37\over17576}
\]

at `p=26`.  The largest raw count is `T_F=144` at `p=152`, giving only
`144/3511808`.  Thus this finite corpus contains no instance resembling
`T_F=Omega(p^3)`.

The scan does produce a stronger finite phase witness than P75.  Reflect the
P75 set by `x -> 990-x`:

```text
B = {3,13,37,59,75,107,127,215,275,301,351,359,471,
     485,489,581,587,617,661,739,767,779,821,921,985,987}.
```

Then, exactly,

\[
 p=26,\quad h=988,\quad b=1,\quad \delta=14,\quad
 C_S=51,\quad T_F=37.                                  \tag{1}
\]

Every mark is odd, so the literal hole follows from parity.  The original P75
orientation has the same `p,h,b,delta,C_S` but `T_F=25`.  Consequently `T_F`
is not reflection-invariant even when the unsigned fold count and all scalar
parameters are fixed.  This is an exact phase-sensitive obstruction to any
argument that tries to recover the loose count from `C_S` alone.

## Search domain

The driver extracted every integer array named `B`, `Z`, `ruler`, or `marks`
from 15 archived JSON artifacts, normalized it, rejected non-Sidon arrays,
added its reflection, and deduplicated.  The resulting domain has 2,526
oriented integer Sidon rulers.  SHA-256 hashes and byte sizes for every source
artifact are stored in `dense_loose_scan.json`.

For every normalized ruler `Z` of width `W`, the translation lane scans

\[
 B=Z+\gamma,\qquad h=W+\gamma+1,
\]

for every `gamma` with positive defect and possible nonzero folds, and for
both `b=1,2`.  It tested 1,613,120 `(Z,gamma,b)` candidates; 1,609,064 had a
nonzero fold count, and 313,863 also had the literal hole.

The insertion lane uses the P71/P75 transformation

\[
 C=Z+g,\qquad B=2C-1,\qquad h=2(W+g),
\]

and inserts every missing interior mark into `C`.  The resulting `B` is kept
only when the enlarged `C` is integer Sidon and the defect is positive.  All
marks of `B` are odd, so `b=1` gives the full literal hole.  On the primary
P46/P53 archives with base order at most 40, this exhaustively tested 312,094
insertions and found 242 Sidon insertions.  The order-26 record (1) is also the
best output of this lane.

All candidate acceptance, ranking, fold enumeration, and triangle counting
uses Python integers.  At most 16 worker processes are created.

## Exact triangle count

For each fold

\[
 a+c+h=u+v,\qquad a\le c<u\le v,
\]

the code stores the labelled hyperedge `(a,c,u)`.  It constructs the three
injective projections `(a,c)`, `(a,u)`, and `(c,u)`.  A shadow triangle is
counted when one edge from each projection meets at `(a,c,u)`; the canonical
case in which all three projection edges have the same fold ID is removed.
Linearity is asserted at runtime.  This reproduces P82's P75 convention
exactly:

\[
                       C_S=51,\qquad T_F=25.            \tag{2}
\]

The independent verifier rebuilt 144 retained global and per-order extrema
from their mark lists and obtained zero mismatches.

## Large-order data

Among retained per-order extrema, the largest raw row is

\[
 p=152,\quad h=29747,\quad b=1,\quad \delta=4834,
 \quad C_S=256,\quad T_F=144,                           \tag{3}
\]

with

\[
 {C_S\over p^2}={256\over23104},\qquad
 {T_F\over p^3}={144\over3511808}.
\]

At the largest scanned order, `p=168`, the best retained row has

\[
 C_S=253,\qquad T_F=114,qquad
 {C_S\over p^2}={253\over28224},\qquad
 {T_F\over p^3}={114\over4741632}.                     \tag{4}
\]

The complete exact best-by-order table is in the JSON artifact.  These rows
are finite observations only; they prove no uniform asymptotic upper bound.

## Transformation mechanism

The P75 one-insertion repair is a finite low-order effect, not an asymptotic
mechanism on the near-optimal archived families.  If a base ruler has order
`p`, width `W=(1+o(1))p^2`, and `r` same-parity marks are inserted before the
`q=2` lift, positive defect requires

\[
 2(W+g)<{3(p+r)^2-(p+r)+2\over2}.
\]

Hence necessarily

\[
 r\ge\left({2\over\sqrt3}-1-o(1)\right)p.             \tag{5}
\]

One insertion cannot meet (5).  In the P75 finite ruler, increasing the order
from 25 to 26 happens to move the exact defect from `-62` to `14`; the archive
search found no continuation of this repair into a growing family.

The remaining plausible counterfamily lane is still P82's direct
range-separated translation of near-optimal rulers.  The exact archived data
show roughly linear-sized `C_S` and `T_F`, not quadratic/cubic density, but do
not supply a theorem.  No asymptotic mechanism yielding `T_F=Omega(p^3)` is
identified here.

## Reproduction

Run the exact search and independent verification from the repository root:

```powershell
python problems/864/compute/p86/dense_loose_search.py search --workers 16 --top 25 --output problems/864/compute/p86/dense_loose_scan.json
python problems/864/compute/p86/dense_loose_search.py verify --input problems/864/compute/p86/dense_loose_scan.json --output problems/864/compute/p86/verification.json
```

The saved scan has SHA-256
`7dd733ba25ea062aea8f843324e148744ff6e0ece1c596679db87e1ba2a8dd80`.
The verifier reports `PASS` on 144 records.

## Claim boundary

This is an exact finite falsifier/construction search, not a proof that
`T_F=o(p^3)`.  It finds no infinite counterfamily and does not resolve the
reflected-center frontier.  Its new mathematical output is the reflected P75
phase pair with loose counts 25 and 37, plus the finite census and the scaling
obstruction (5) for the one-insertion parity-lift mechanism.
