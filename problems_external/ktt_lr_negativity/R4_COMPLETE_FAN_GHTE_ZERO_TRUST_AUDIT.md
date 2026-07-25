# Zero-trust audit of the side-four complete-fan GHTE contract

Date: 2026-07-22  
Verdict: **PASS for the stated single-fan contract.**  This is not a proof of
GHTE in arbitrary rank and is not a proof of the full KTT conjecture.

## Audited artifacts

- Target: `r4_complete_fan_ghte_contract.py`
- Independent checker: `r4_complete_fan_ghte_independent_audit.py`
- Reduction statement: `GHTE_REDUCTION_AND_ENDPOINTS.md`

The reduction statement now uses the face-volume vector of the lattice
polytope `mQ`, not the unscaled rational polytope, and it chooses the integral
translation point `p0` only after assuming a nonzero LR triple.  Those two
hypotheses are necessary and are present in the audited text.

## Independence contract

The independent checker does not import the target program or any project
hive, polytope, Ehrhart, normal-fan, or BV module.  Its only non-standard
dependency is SymPy for exact rational matrix arithmetic.

It independently:

1. derives all 18 inequalities from the three rhombus families and the
   partition boundary;
2. enumerates rational triple intersections, removes redundant supporting
   rows, and reconstructs all vertices, edges, facets, and incidences;
3. chooses quotient-lattice bases by a different unimodular-completion order
   and rebuilds `B_2` from primitive quotient images;
4. evaluates index-one q=2 BV constants from the Gram formula and index-two
   constants in the saturated basis `s=(u+v)/2`, `t=(u-v)/2`;
5. computes q=3 BV constants directly on the **feasible tangent cones** by an
   exact truncated local Euler--Maclaurin Laurent recursion; it does not use
   the target's normal-cone refinement routine;
6. evaluates every nonsimplicial tangent cone using both possible diagonals
   and requires the two inclusion--exclusion values to agree;
7. enumerates lattice points at dilations 0 through 5 and separately applies
   the Littlewood--Richardson tableau rule at dilation one; and
8. constructs an exact spanning-tree Farkas certificate for q=3.

The source import audit reports no target import.  Agreement therefore checks
the target values through a distinct executable path.  It validates the
target's normal-cone-refinement *outputs for this fan*; it does not assert that
an arbitrary future normal-cone refinement may be summed without a separate
valuation proof.

## Exact reconstruction

For

```text
lambda = mu = (12,8,4,0),
nu = (18,14,10,6),
```

the independent face lattice has

```text
(f_0,f_1,f_2) = (11,21,12),
complete-fan f-vector = (1,12,21,11),
11 - 21 + 12 = 2.
```

All 11 vertices are integral.  At `(26,32,38)` the primitive tangent rays are

```text
(0,1,1), (1,0,1), (1,1,0),
```

with absolute determinant `2`.

The two independent counting routes give

```text
L(0),...,L(5) = 1, 50, 279, 832, 1853, 3486,
LR tableau count at dilation one = 50,
L(n) = 1 + 7 n + 18 n^2 + 24 n^3.
```

## q=2 complete-fan data

The independently based quotient matrix has

```text
rank(B_2) = 20,
number of columns = 21,
dim ker(B_2) = 1,
B_2 w_2 = 0.
```

The 21 edge cones have saturation-index histogram

```text
index 1: 18,
index 2: 3.
```

Every index-two value is `5/18`.  In canonical edge order the independent BV
vector is

```text
(5/18,5/18,5/18,1/9,1/9,1/6,1/9,1/9,1/6,1/9,1/9,
 1/6,1/8,1/8,1/8,1/8,1/4,1/8,1/8,1/4,1/4).
```

It agrees entry by entry with the target.  Its minimum is `1/9`, so `y=0` is
already a strict q=2 GHTE certificate, and

```text
<a_2,w_2> = 7 = [n] L(n).
```

## q=3 complete-fan data

The independently oriented edge-incidence matrix has

```text
rank(B_3) = 10,
number of columns = 11,
dim ker(B_3) = 1,
B_3 (1,...,1)^T = 0.
```

Direct feasible-cone evaluation gives, in canonical vertex order,

```text
a_3 = (1/4,1/18,1/18,1/18,1/24,1/24,1/9,1/24,1/9,1/9,1/8).
```

This agrees entry by entry with the target.  In particular, the determinant-two
vertex has BV value `1/4`.  The exact identities are

```text
sum(a_3) = 1 = [n^0] L(n),
a_3 + B_3^T y = (1/11,...,1/11) > 0
```

for the rational spanning-tree flow `y` emitted in the independent canonical
payload.

## Replay and hashes

```text
python problems_external\ktt_lr_negativity\r4_complete_fan_ghte_contract.py
python problems_external\ktt_lr_negativity\r4_complete_fan_ghte_independent_audit.py
python -m py_compile problems_external\ktt_lr_negativity\r4_complete_fan_ghte_independent_audit.py
```

The recorded replay produced `PASS` for both programs.

```text
target canonical payload SHA256:
  3e4f0b26b4085232df70dea7d565dbc58afcf0d3732a97e1d7371e1b85c7c45a

independent canonical payload SHA256:
  9a01b8c34612b2561cd5e0c510a3c032b73c90e979c190ec35609750fc9732f3

independent checker file SHA256:
  100AC64A372D651B9562B332AC2829983CD9E852BFCD6A1C266EC84DCDB207A6
```

The payload hashes differ because the two programs choose different quotient
bases and emit different certificate coordinates; the basis-invariant face,
rank, kernel, balance, BV, pairing, and shifted-certificate data agree.

## Scope boundary

This audit establishes that one non-unimodular side-four complete fan obeys
the q=2 and q=3 GHTE identities with exact certificates.  It also confirms the
intrinsic-lattice and denominator-clearing conventions used by the reduction.
It supplies no rank-uniform deletion, no proof of GHTE for all hive fans, and
no new claim beyond the already proved length-at-most-four KTT case.
