# r=4 edge-local positivity certificate

## Scope

This note proves the following conditional statement:

> Every three-dimensional **lattice** polytope whose facet normals belong to
> the fixed 15-element `r=4` hive normal set has nonnegative linear Ehrhart
> coefficient.

Thus this certificate closes the positivity step for `r=4`; a separate exact
certificate that every `r=4` hive polytope has integral vertices is still
needed before applying it to all hives.

## Edge coordinates and the universal balance space

Write the fixed primitive outward normals as `n_0,...,n_14`.  Six of their
105 unordered pairs are parallel, leaving 99 possible edge types.  For a
lattice 3-polytope `P`, let

```
Lambda(P)_{ij} = total lattice length of edges incident to facets i and j.
```

For every facet `i`, its oriented lattice polygon boundary closes.  If
`u_ij = primitive(n_i x n_j)`, this gives

```
sum_j Lambda(P)_{ij} u_ij = 0.
```

Using opposite signs in the `i` and `j` facet blocks defines an integer
matrix `B` of size `45 x 99`, and every realizable edge vector satisfies
`B Lambda(P) = 0`.  Exact elimination gives

```
rank(B) = 27,   dim ker(B) = 99 - 27 = 72.
```

The witness certificate contains 72 actual integral 3-polytopes with these
facet normals.  Independent reconstruction gives 72 linearly independent
edge vectors, each in `ker(B)`.  Consequently their edge vectors form a basis
of the entire universal balance space `ker(B)`; there is no unsampled linear
direction left.

## Local Ehrhart functional

The Berline-Vergne/McMullen local Ehrhart formula in dimension three says

```
a_1(P) = sum_edges(e) lattice_length(e) * alpha(transverse_cone(e)).
```

For this fixed normal set, the transverse cone of an edge depends only on its
unordered incident-normal pair.  Hence `a_1` is a fixed linear functional of
`Lambda(P)` on `ker(B)`.

The certificate embeds a rational vector `mu` with 99 entries.  The exact
checker proves

```
mu >= 0 componentwise,
Lambda(P_k) . mu = a_1(P_k)   for all 72 basis witnesses P_k.
```

Since the witness edge vectors span `ker(B)`, this equality holds for every
edge vector in `ker(B)`, in particular for every lattice 3-polytope with the
fixed normal set.  Its edge lengths are nonnegative, so

```
a_1(P) = Lambda(P) . mu >= 0.
```

For a 3-dimensional lattice polytope, `a_0=1`, `a_3=V/6>0`, and `a_2` is half
the lattice-normalized boundary area and is positive.  Dimensions zero, one,
and two have nonnegative Ehrhart coefficients by the point, segment, and
lattice-polygon formulas.  Therefore vertex integrality plus this certificate
implies coefficientwise nonnegativity for the whole `r=4` cell.

Finally, with `c=L(1)`, `i=#(int(P) cap Z^3)`, Ehrhart reciprocity gives

```
3(c+i)-V = 6 a_1 >= 0,
```

which is the claimed bound `V <= 3(c+i)`.

## Exact artifacts and replay

Run from the repository root:

```powershell
python problems_external\ktt_lr_negativity\r4_reeve\q2_verify_r4_certificate.py
```

Expected terminal summary:

```
PASS
certificate_sha256=c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148
witnesses=72 witness_rank=72 balance_rank=27 kernel_dimension=72 min_mu=0
r4_normal_set=PASS
```

Files:

- `q2_make_basis_certificate.py`: deterministic generator; seed `31337`, 190
  candidates tested.
- `q2_basis_witness_certificate.json`: all exact inequalities, vertices,
  edge vectors, `L(0..5)`, Ehrhart coefficients, and `mu`.
- `q2_verify_basis_certificate.py`: independent exact vertex enumeration,
  brute-force lattice counting, edge extraction, interpolation, and rank replay.
- `q2_verify_r4_certificate.py`: binds the certificate to the canonical 15
  `r=4` hive normals before running the replay.

The generator was rerun to a separate path and reproduced the certificate
SHA-256 byte for byte.
