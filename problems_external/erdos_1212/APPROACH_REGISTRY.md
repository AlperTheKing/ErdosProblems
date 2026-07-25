# Erdős Problem 1212 — Approach Registry

## DIRECT ROUTE R1: periodic monotone path

### 1. Exact final deliverable

Give integers `M >= 1`, a starting vertex `(a,b)`, and a finite word
`W` in the unit steps `E=(1,0)` and `N=(0,1)` such that:

1. `W` contains exactly `M` copies of each step;
2. every vertex on `W`, and on every translate
   `W + k(M,M)` for `k >= 0`, has coprime coordinates;
3. both coordinates exceed `1`;
4. at least one coordinate is composite; and
5. concatenating the translates yields a simple path going to infinity.

The final certificate is the explicit word and the finite residue/gcd ledger
which proves all five properties for every translate.

### 2. Current frontier certificate

Find one finite monotone path from `(a,b)` to `(a+M,b+M)` with no vertex on
the diagonal. For a vertex `(x,y)` with `d=y-x`, require:

- every prime factor of `d` divides `M`;
- `gcd(x,d)=1`; and
- one coordinate is divisible by a fixed prime divisor of `M` and is larger
  than that prime.

These are finite, exact checks on the period.

### 3. Logical bridge

For the translate `(x+kM,y+kM)`,

`gcd(x+kM,y+kM)=gcd(x+kM,d)`.

If every prime factor of `d` divides `M`, then this gcd equals `gcd(x,d)=1`
for every `k`. Divisibility of a coordinate by a fixed prime divisor of `M`
is likewise translation-invariant, so that coordinate remains composite.
The endpoint translation makes consecutive copies share exactly one vertex;
monotonicity makes every other vertex distinct and both coordinates tend to
infinity. Thus one finite certificate proves the full existential statement.

### 4. Next falsifiable action

Use an exact dynamic program to search all monotone `E/N` paths for
`2 <= M <= 120` and starting residues `0 <= a,b < M`, enforcing the finite
conditions above. Replay a candidate with a separately implemented verifier
over at least 10,000 translated periods and then replace that finite replay
by the symbolic gcd/divisibility proof.

### 5. Exit condition

If the declared `M <= 120` search has no candidate, mark R1 `DEAD` and do
not increase the bound. If a candidate is found but any symbolic condition
or independent replay fails, mark R1 `DEAD`. A valid candidate moves
immediately to proof audit and a fresh live novelty search.

## Status

R1 is `CALIBRATION_PENDING`. No large computation is authorized.

## DIRECT ROUTE R2: unbalanced periodic monotone path

### 1. Exact final deliverable

Give positive integers `A != B`, a starting vertex `(x,y)`, and a finite
word containing exactly `A` east steps and `B` north steps. Repeating the
word by translation through `(A,B)` must give a simple unbounded path whose
vertices are all visible, exceed `1` in both coordinates, and have at least
one composite coordinate.

### 2. Current frontier certificate

For every phase vertex `(u,v)`, require `C = A*v - B*u != 0`, every prime
factor of `C` to divide `gcd(A,B)`, and no prime dividing `gcd(A,B)` to
divide both `u` and `v`. Also require `gcd(u,A)>1` or `gcd(v,B)>1`.

### 3. Logical bridge

Any common prime divisor of `u+kA` and `v+kB` divides `C`. If it does not
divide both `A` and `B`, the two linear congruences have a simultaneous
solution for infinitely many `k`; the stated factor condition excludes this.
If it divides both steps, the residues are constant and the second condition
excludes simultaneous divisibility. Hence every translate is visible.
The last condition supplies a fixed prime divisor of one coordinate in every
translate, so that coordinate is composite after a common finite lift.

### 4. Next falsifiable action

Exhaust all `2 <= A,B <= 80`, `A != B`, all start residues, and all monotone
paths in the `A` by `B` period rectangle by exact dynamic programming.
Independently replay any candidate over 10,000 periods and check the symbolic
determinant ledger.

### 5. Exit condition

If the declared rectangle family has no candidate, mark R2 `DEAD` and do not
increase the bound. If a hit fails either independent replay or symbolic
audit, mark R2 `DEAD`. A verified hit closes the original existential
problem and triggers the novelty gate.

## Status update

R1 is `DEAD`: two exact implementations found no candidate for `M<=120`,
and the fixed-divisor balanced period meets an unprotected prime-pair phase.
R2 is `CALIBRATION_PENDING`.

## DIRECT ROUTE R3: fixed composite strip

### 1. Exact final deliverable

Give one finite path from `(a,25)` to `(a+390,25)` contained in the three
rows `y=25,26,27`, using unit horizontal or vertical edges, such that every
vertex `(x,y)` has `gcd(x,y)=1`. Its translates by `(390,0)` must concatenate
to a simple path.

### 2. Current frontier certificate

Find the finite path in the declared `390 by 3` strip. Horizontal moves are
allowed only when both endpoints are coprime to the row value. A switch
between rows 25 and 27 uses both vertical edges through row 26 and is allowed
only at a column coprime to all three row values.

### 3. Logical bridge

The three row values are composite and exceed `1`, so every path vertex has
a composite coordinate and both coordinates exceed `1` once `a>1`.
Moreover

`rad(25*26*27) = 2*3*5*13 = 390`.

Thus, if `gcd(x,y)=1` for a phase vertex, then
`gcd(x+390k,y)=1` for every `k>=0`. Repeating the finite path therefore
preserves every required property; a path whose internal x-coordinates lie
strictly between its endpoints repeats without overlap and goes to infinity.

### 4. Next falsifiable action

Run exact breadth-first search on precisely this `390 by 3` strip, require
the endpoint and no boundary overlap, and independently replay any word for
at least 10,000 periods before replacing replay by the radical argument.

### 5. Exit condition

If this single declared strip has no path, mark R3 `DEAD`; do not try other
row triples or larger moduli. If a path is found but either independent
replay or the symbolic radical proof fails, mark R3 `DEAD`. A verified path
is a complete affirmative resolution of #1212 and triggers a fresh novelty
gate.

## Status update

R3 is `DEAD`: every finite horizontal strip has an impenetrable column.

## Final route audit

R2 is `DEAD`: the root and an independent C++ implementation each exhausted
all 6,162 ordered pairs `2 <= A,B <= 80`, `A != B`, with every start residue
and every monotone `A by B` path represented by exact dynamic programming.
Both returned `NO_HIT`. This closes only the registered bounded R2 family.

The horizontal-strip obstruction used for R3 is general within its mechanism:
horizontal edges cannot lie on an even row, while for any finite collection
of odd rows a column divisible by every prime occurring in those row values
contains no visible vertex. Hence no path confined to finitely many fixed
rows can cross that column.

No registered direct route remains. Erdős #1212 is unresolved; bounded
`NO_HIT` results are not a proof or disproof.
