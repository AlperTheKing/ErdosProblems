# Zero-trust audit of the side-five intrinsic-3 GHTE gate

Date: 2026-07-22

Verdict: **CONFIRMS the finite claims in
`R5_LOWERDIM_GHTE_COMPLETE_FAN_AUDIT.md`; no discrepancy found.**  This does
not prove GHTE or KTT.

## Independent implementation boundary

The independent reconstruction is

```text
r5_lowerdim_complete_fan_ghte_zero_trust_audit.py
```

It does not import `r5_lowerdim_complete_fan_ghte_contract.py` or the r4
checker/helpers.  Its only geometric inputs are the authoritative local
side-five hive builder and exact ambient vertex/lattice-coordinate engine:

```text
r5_certificate/hive5.py
r5_certificate/polytope5.py
```

The independent paths differ as follows.

1. All thirty hive inequalities are restricted to the recovered saturated
   intrinsic tangent lattice.  Actual facets are selected from this exact
   intrinsic H-description.  The audited checker instead discovers supporting
   planes from vertex triples.
2. At q=2, a primitive quotient incidence modulo a facet normal `u` is
   represented by the primitive cross-product image of the adjacent normal.
   This gives three displayed rows per facet with rank two, rather than the
   audited checker's chosen two-coordinate quotient completion.
3. At q=3, the balance matrix is an independently oriented edge/vertex graph
   incidence matrix.  It is not copied from normal-cone sign calculations.
4. The index-two q=2 BV value is computed both by an independent primitive-ray
   subdivision and by the closed index-two formula; the two results must agree.
5. Each q=3 normal cone is evaluated using every cyclic fan triangulation.  A
   separate recursive fundamental-parallelepiped refinement, with a different
   tie-break, reduces every simplicial cell to determinant one.  Every
   triangulation must return the same exact BV value.
6. The Gram matrix of each unimodular q=3 cell is constructed directly from
   the primal basis dual to the normal rows and checked against the inverse
   normal Gram matrix.
7. Ehrhart values are obtained by direct enumeration in the intrinsic
   three-dimensional lattice, not by `hive5.lattice_count`.

The canonical independent payload has digest

```text
cba5ad66090bf6c8ee68dd21e0917c37eb19d7a14e4212efde7bd8c4a3e5cd0d
```

The audited checker independently replays with its recorded digest

```text
d5fcb31c2bcfc891aef39cf47d45f206036cbc3dd35191168f43f59f26a2b249
```

## Hard selected hive

For

```text
lambda = (27,6)
mu     = (20,8,4,1)
nu     = (40,14,5,4,3),
```

the independent saturated tangent basis is

```text
(1,0,0,0,0,0), (0,0,0,1,0,0), (0,0,0,0,0,1),
```

with saturation index one and identity Gram matrix.  Restricting the original
hive inequalities gives the following six facets:

```text
normal       rhs   tight vertices
(-1,-1, 0)   0     0,1,2,3
( 0,-1,-1)   2     1,3,4
( 0,-1, 1)   1     2,3,5
( 0, 0, 1)   0     0,2,5,6
( 0, 1,-1)   0     0,1,4,6
( 1,-1, 0)   3     3,4,5,6
```

They give the complete normal-fan f-vector `(1,6,11,7)`.  Direct intrinsic
lattice counts are

```text
L(0),...,L(5) = 1,8,27,64,125,216,
L(n)           = 1 + 3n + 3n^2 + n^3.
```

### q=2

The independently represented balance matrix has 18 rows and 11 columns.
Its row rank is 9, its kernel dimension is 2, and its exact edge-length vector
is in its kernel.  The stacked row space of this matrix and the audited
12-by-11 quotient-coordinate matrix still has rank 9, proving that the two
representations impose the same balance relations.

The eleven BV entries in edge order are

```text
1/3, 1/4, 3/8, 1/6, 1/4, 1/6, 1/8, 1/6, 1/6, 1/3, 1/4.
```

Their pairing with normalized edge lengths is exactly `3`, the coefficient of
`n`.  The only nonsaturated pair is

```text
(0,-1,-1), (0,1,-1), index 2,
```

and the independent refinement ray is `(0,0,-1)`.  Both unimodular cells sum
to `1/4`, also equal to the direct index-two closed formula.  Since every raw
entry is positive, `y=0` is an exact GHTE certificate for q=2.

### q=3

The independent 11-by-7 graph-incidence matrix has rank 6 and kernel dimension
1; the all-ones vertex-volume vector balances.  Its row space agrees with the
audited q=3 row space because their stacked rank is still 6.

All cyclic triangulations give the same seven BV values:

```text
5/16, 1/9, 7/144, 1/18, 1/9, 7/144, 5/16.
```

They sum to `1`.  An exact independently solved incidence-flow certificate
shifts this vector to `(1/7,...,1/7)`, so q=3 also passes GHTE on this fan.

## Horn-gap cross-check

The independent reconstruction also confirms the second fixture:

```text
fan f-vector:        (1,4,6,4)
Ehrhart polynomial:  1 + 11/6 n + n^2 + 1/6 n^3
q=2:                 rank 5, kernel 1, pairing 11/6, min raw 1/4
q=3:                 rank 3, kernel 1, pairing 1, min raw 1/8
q=3 shifted vector:  (1/4,1/4,1/4,1/4).
```

## Full 87-record corpus audit

Every record marked `status=OK,d=3` in `_sym5b.jsonl` was rebuilt from its
partition triple.  This was a complete replay of the 87-record subset, not a
sample.  The independent totals are

```text
records in source                         1500
reported dim-3 records rebuilt              87
q=2 cones rebuilt                          866
negative q=2 BV entries                       0
minimum q=2 BV entry                       1/10
maximum vertex count                         10
maximum q=2 saturation index                  2
records with >4 vertices and index >1         6
first qualifying record                       line 2, the hard hive
q=2 balance failures                           0
pairing mismatches with recorded exact a1      0
```

Thus the independent audit confirms not only the raw BV statistics but also
`Bv=0` and the exact q=2 Euler--Maclaurin pairing for all 87 reconstructed
fans.

## Replay

Run the independent reconstruction:

```text
python r5_lowerdim_complete_fan_ghte_zero_trust_audit.py
```

Print its complete canonical payload if desired:

```text
python r5_lowerdim_complete_fan_ghte_zero_trust_audit.py --full
```

After the independent run, compare exact face data, BV vectors, volumes, and
balance-matrix row spaces against the audited checker:

```text
python r5_lowerdim_complete_fan_ghte_cross_compare.py
```

The cross-comparison returns

```text
horn_gap: FULL_MATCH q2_rowspace_rank=5 q3_rowspace_rank=3
hard: FULL_MATCH q2_rowspace_rank=9 q3_rowspace_rank=6
PASS
```

## Scope

This audit removes the identified implementation-risk channels for the two
fixtures and confirms every stated q=2 corpus statistic.  It remains a finite
definition/falsification gate.  It supplies no rank-uniform wall-crossing lift
and therefore does not establish GHTE or the general KTT conjecture.
