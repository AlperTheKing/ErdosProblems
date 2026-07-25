# Exact audit of the codegree-three `3 x 8` transportation `L(1)` gate

Date: 2026-07-22

## Scope

This audit executes only the finite gate authorized in
`APPROACH_REGISTRY_GENERAL_KTT_V4.md`.  Let

```text
r=(r1,r2,r3),  ri >= 3,  N=r1+r2+r3,
c=(N-7,1,1,1,1,1,1,1).
```

It asks whether the full transportation polytope `T(r,c)` can satisfy
`L_T(1)=255`, the base-count invariant of the negative order polytope
`O(P_(7,7))`.  Exact degree-14 Ehrhart reconstruction was authorized only for
survivors of this gate.

## Exact count at dilation one

Each of the seven labelled unit columns has exactly one nonzero entry, equal
to one.  Assign that column to its row.  If `ki` unit columns are assigned to
row `i`, the entry in the large column is forced to be `ri-ki`.  Consequently

```text
L_T(1) = sum_{k1+k2+k3=7, 0<=ki<=ri} 7!/(k1! k2! k3!).
```

The count depends only on `si=min(ri,7)`.  Up to row permutation there are
exactly

```text
C(5+3-1,3)=35
```

capped triples `3 <= s1 <= s2 <= s3 <= 7`.

The count is coordinatewise nondecreasing in `(s1,s2,s3)`, so its global
minimum occurs at `(3,3,3)`.  Direct inclusion-exclusion gives

```text
L_(3,3,3)(1)
 = 3^7 - 3 * sum_{j=4}^7 C(7,j) 2^(7-j)
 = 2187 - 3*(280+84+14+1)
 = 1050.
```

Two cap-violation events cannot overlap: two row counts exceeding three would
already total at least eight.  Thus the displayed subtraction is exact.

It follows immediately that

```text
L_T(1) >= 1050 > 255
```

for every row-margin triple in the registered family.

## Independent finite replay

`transport_codegree3_l1_gate.py` enumerates all 35 unordered capped triples in
two independent ways:

1. exact multinomial summation over the compositions of seven;
2. direct enumeration of all `3^7=2187` labelled column assignments.

The two values agree for every capped triple.  The 35 counts are distinct,
with minimum 1050 at `(3,3,3)` and maximum 2187 at `(7,7,7)`.  No count is
255.

Replay from the repository root:

```powershell
python problems_external\ktt_lr_negativity\transport_codegree3_l1_gate.py
```

Expected headline output:

```text
PASS
unordered_capped_triples=35
minimum={'caps': [3, 3, 3], 'L1': 1050}
maximum={'caps': [7, 7, 7], 'L1': 2187}
target=255
survivors=0
L1_payload_sha256=3907934da5f593179491c267b4fca629967dd442273afd520070040b10e6c0fb
```

Checker SHA-256:

```text
FD491BB929D7E0717335D2331AE91B08670DF4FAD9768862BBE36E74E2A7C494
```

## Exact degree-14 replay on all canonical capped representatives

Although the invariant-matching subfamily is empty, the checker also treats
the 35 capped triples themselves as canonical row-margin representatives

```text
3 <= r1 <= r2 <= r3 <= 7.
```

For each dilation `n`, a unit column is a weak composition `(x,y,z)` of `n`.
The checker raises the exact triangular generating kernel

```text
sum_{x+y+z=n} X^x Y^y Z^z
```

to the seventh power by integer dynamic programming.  Summing its coefficients
subject to the three row bounds gives the transportation count.  This raw
counting engine is independent of the two `n=1` enumerators above.

For each of the 35 representatives, values at `n=0,...,14` determine the
degree-14 polynomial by exact Newton interpolation.  Direct DP values at
`n=15,16` are held out and agree with the interpolated polynomial in all 70
checks.  The `h*`-vectors also satisfy `h*_12=1` and `h*_13=h*_14=0`, as
required by codegree three.

Exact finite result:

```text
canonical_polynomials=35
negative_polynomials=0
negative_coefficients=0
smallest_coefficient=128114573/29059430400 rows=(3,3,3) degree=14
largest_linear_cancellation=131174147/131215991 rows=(4,4,4)
linear_coefficient_at_cancellation_champion=317/35
full_payload_sha256=3799958aaee2183d00beb97b793fa1a1d41ea053395a5c7d970469367b41fc48
```

The cancellation ratio is the total negative contribution divided by the
total positive contribution in the `h*`-expansion of the ordinary linear
coefficient.  Its maximum here is approximately `0.9996811059`, still strictly
below the negativity threshold one.

In particular, every ordinary coefficient of every one of the 35 canonical
representative polynomials is strictly positive.  These representatives cover
all row margins in the registered family, not only the dilation-one gate.  To
see this, project a table at dilation `n` to its seven unit columns and let
`si` be their total in row `i`.  The large-column entry is forced to
`n*ri-si`.  Since `si<=7n`, the inequality for row `i` is automatic whenever
`ri>=7`; replacing such an `ri` by `7` therefore preserves the projected
lattice-point set at every dilation.  The changed large-column margin is
automatically the sum of the three changed forced entries.  This is a
dilation-compatible lattice bijection.

The known order-polytope target instead has linear coefficient `-3041/1430`,
so none of these polynomials can equal its Ehrhart polynomial.

## Verdict and exact scope

There are no invariant-matching survivors.  The stronger finite replay of all
35 canonical capped representatives also gives no negative coefficient.  Under
the registry's exit condition:

```text
DEAD: codegree-three 3x8 transfer family exhausted -- all 35 unordered capped
row-margin patterns have L_T(1) >= 1050, whereas O(P_(7,7)) has L(1)=255; all
35 canonical representative Ehrhart polynomials are strictly positive.
```

This kills the whole registered family: the cap bijection above identifies all
of its unbounded row margins with the 35 representatives.  It does not prove
Ehrhart positivity of arbitrary `3 x 8` transportation polytopes with other
column margins, and it does not resolve the general KTT conjecture.
