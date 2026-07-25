# Erdős #114 finite-certificate audit

Audit date: 2026-07-23

## Verdict

**REJECT the claimed certificates for \(3\le n\le14\).** The deposited
files and their checksums are reproducible as files, but the executable does
not produce mathematical enclosures of lemniscate length or certified upper
bounds over coefficient boxes. It also automatically exempts a positive-volume
part of the search domain from branch-and-bound. Consequently none of the
JSON verdicts `EHP_N{n}_PROVEN` proves the EHP conjecture for all monic
polynomials of that degree.

Recommended route status:

`DEAD: finite-certificate bridge fails -- the evaluator and box bound do not enclose the true objective, and positive-volume "extremizer boxes" are never bounded.`

## Exact artifacts and integrity replay

- Zenodo record: <https://doi.org/10.5281/zenodo.20087919>, version `v3.1.0`,
  concept DOI `10.5281/zenodo.19184467`.
- Downloaded metadata:
  `zenodo_20087919_metadata.json`.
- Downloaded archive:
  `erdos-experiments-v3.1.0.zip`, 55,306,035 bytes,
  MD5 `d8c60284dd3a51f90c03140583a9c61a`, exactly matching the Zenodo API.
- Downloaded paper:
  `Mendoza_EHP_n3-14_April2026.pdf`, MD5
  `55818f7a310e1adc4aeefd2a136301d3`, exactly matching the Zenodo API.
- GitHub release:
  <https://github.com/MendozaLab/erdos-experiments/releases/tag/v3.1.0>.
  The exact tag is commit
  `f89597e2eaadbaa520eb7f9e36ac95c9822e81ca`.
- The four critical files checked (root README, proof engine, Cargo lock,
  and TeX paper) are text-identical between the Zenodo ZIP and the Git tag
  after normalizing Git's CRLF checkout to LF.
- All twelve canonical result sidecars for \(n=3,\ldots,14\) equal the
  independently recomputed SHA-256 of their JSON files. This establishes file
  integrity only, not correctness of the mathematical predicates encoded in
  those JSON files.
- The canonical \(n=13\) JSON SHA-256 is
  `c06c633b4053cdf2c4c6003327f30ee2ce683e6a9da70e047d5c5d43e685fd17`.
  Zenodo also deposits the archived earlier `EHP_N13_PROVEN` result with zero
  evaluations; its SHA-256 is
  `a4e72a9be2811e9d2290c6cdd0f6a9f1dd17fa85790e380bd5af8b09179e02ac`.

The archive's root `README.md:58` now explicitly says that the reported
searches are not certified global gaps over all monic polynomials. That
disclaimer agrees with the source audit below and contradicts the global
claim in the deposited paper.

## Fatal completeness failures

### 1. The "interval" length evaluator is only a floating-point polygonal approximation

Critical source:
`zenodo_v3.1.0_extracted/scripts/erdos-114/src/bin/ehp_general_ieee1788.rs`.

- `eval_poly_interval` at lines 237-251 is never called.
- At lines 303-402, corner signs and crossing parameters are computed first
  in ordinary `f64` (`321-347`). Each already-rounded crossing is then wrapped
  as a degenerate interval `interval!(t,t)`.
- Linear interpolation of endpoint values does not enclose the true
  intersection of an algebraic level curve with a cell edge. Summing the
  lengths of polygonal chords does not enclose the true arc length (a chord
  normally underestimates its arc).
- Lines 337-339 discard cases with four equal corner signs. Equal corner signs
  do not exclude a level-set component or a pair of crossings wholly inside
  the cell. There is no interval root-exclusion or topology certificate.
- The paper says a conservative 5% grid-error envelope is absorbed into the
  intervals, but no 5% term, curvature bound, or grid-error term occurs in this
  executable.

Thus `lemniscate_length_interval` is not an interval enclosure of \(L(p)\).
IEEE-1788 rounding of the final chord arithmetic cannot repair non-enclosed
inputs or discretization error.

### 2. The branch-and-bound upper bound is empirical, not certified

- `BoxND::sample_points` (lines 519-549) samples only the center, face
  centers, and (only when \(d\le10\)) corners. It never interval-evaluates
  the coefficient box.
- `upper_bound_box` (lines 557-599) estimates a Lipschitz constant from the
  observed sample variation, clamps it below by 8, and multiplies by the
  empirical factor `0.29`. No analytic bound on the derivative of \(L\), no
  interval derivative, and no proved interpolation remainder is present.
- The source itself calls `0.29` empirical at lines 563-567. Hence
  `max_upper + interp_margin` is not proved to dominate every polynomial in
  the box.

This is the central missing theorem: a valid uniform upper bound
\(\sup_{p\in B}L(p)\le U(B)\). Without it, every elimination is heuristic.

### 3. A positive-volume region is automatically skipped

- `contains_extremizer` (lines 481-493) labels any box whose closed coordinate
  intervals contain `(1,0,...,0)` as an "extremizer box".
- Such a box is assigned infinity and never evaluated (lines 752-760).
- The computation declares completion as soon as no *other* boxes survive
  (lines 821-824), even though every exempt box has nonzero volume.

For the default `grid_per_axis=2` used at \(n\ge6\), the domain is
\([0,3]\times[-3,3]^{d-1}\). The first-coordinate cell \([0,1.5]\) contains
1, and both cells `[-3,0]` and `[0,3]` contain 0 because the test is inclusive.
Therefore exactly \(2^{d-1}\) boxes -- the entire half-domain
\([0,1.5]\times[-3,3]^{d-1}\) -- are automatically exempted.

The deposited JSONs confirm this:

| \(n\) | \(d\) | initial boxes | auto-exempt "ext" boxes | fraction |
|---:|---:|---:|---:|---:|
| 6 | 9 | 512 | 256 | 1/2 |
| 10 | 17 | 131,072 | 65,536 | 1/2 |
| 13 | 23 | 8,388,608 | 4,194,304 | 1/2 |
| 14 | 25 | 33,554,432 | 16,777,216 | 1/2 |

For \(n=13\), the independent count replay is exact:
when \(d=23>10\), each evaluated box has `1+2d=47` sample points, and
\[
4,194,304\cdot47=197,132,288,
\]
exactly `bb_total_evals`. Hence every reported evaluation is accounted for by
the eliminated half; the surviving half was not evaluated. The progress log
also records zero evaluations through almost the first 50% of enumerated
boxes, then finishes with 4,194,304 exempt survivors
(`...n13...PROGRESS.log:3-171,339`).

The pointwise Hessian calculation cannot bound this positive-volume region.

### 4. The outer-domain test is finite random sampling

Lines 843-895 sample at most 10,000 pseudorandom points on each face and set
`outer_safe = max_face < l_lower`. There is:

- no interval covering of a face;
- no proof that length is radially monotone in coefficients;
- no quantitative growth theorem controlling every point outside the box.

Sampling a boundary does not prove an inequality everywhere on that boundary,
and an inequality on a boundary does not by itself control the unbounded
exterior. Thus the finite box is not bridged to all monic polynomials.

### 5. The Hessian predicate proves neither a Hessian bound nor negative definiteness

Lines 897-983 use only coordinatewise finite differences at one point.

- A finite-\(h\) second difference is not an upper bound on the second
  derivative without a certified Taylor remainder or another regularity
  theorem.
- Mixed partials are never computed.
- Negative diagonal entries do not imply that a symmetric Hessian is negative
  definite.
- Even a negative-definite Hessian at the single extremizer would establish
  only local behavior, not strict dominance throughout the automatically
  exempt boxes.

The paper claims verified Hessian eigenvalues; the deposited executable
computes no eigenvalues.

## Paper/source/result inconsistencies

- The paper claims a reduction to \(2n-5\) dimensions and reports dimensions
  1 at \(n=3\), 15 at \(n=10\), and 21 at \(n=13\). The executable and canonical
  JSONs use \(2n-3\): respectively 3, 17, and 23. The code's centered and
  phase-normalized parameterization has the latter dimension.
- The paper reports the obsolete \(n=13\) zero-evaluation, 18-second
  "specialized optimization" as proven. Zenodo separately includes that broken
  JSON and the later 197,132,288-evaluation rerun.
- The TeX source included in the ZIP claims only \(n=3,\ldots,12\), whereas
  the separately deposited PDF claims \(n=3,\ldots,14\); the PDF is not
  reproducible from that TeX source without unprovided edits.
- Evaluation counts in the PDF disagree with the canonical JSONs for most
  degrees (for example \(n=3\): 8 versus 7,560; \(n=10\): 32,768 versus
  2,293,760).

The deposit is therefore not one coherent source-to-certificate chain.

## Does it prove all monic polynomials for a fixed \(n\)?

No. The \(2n-3\)-parameter code nominally represents every centered monic
polynomial after a length-preserving rotation, but nominal parameter coverage
is not a proof:

1. half of the bounded domain is automatically exempt at \(n\ge6\);
2. evaluated boxes receive only an empirical sample bound;
3. the length samples are not enclosures; and
4. the unbounded complement receives only random boundary samples.

The only rigorously replayed facts are integrity/statistics facts about the
files and program execution, not the asserted universal inequalities.

## Can this machinery cover \(15,\ldots,N_0-1\)?

No, not in its present form, regardless of the eventual value of \(N_0\).
It first needs new certified mathematics for curve length, boxwise objective
bounds, the extremizer neighborhood, and the outer domain.

Even ignoring correctness, the first-level cost grows exponentially. With
the default \(d=2n-3\) and two cells per axis:

| \(n\) | \(d\) | initial boxes \(2^d\) | point evaluations under the same flawed skip |
|---:|---:|---:|---:|
| 15 | 27 | 134,217,728 | 3,690,987,520 |
| 16 | 29 | 536,870,912 | 15,837,691,904 |
| 18 | 33 | 8,589,934,592 | 287,762,808,832 |
| 20 | 37 | 137,438,953,472 | 5,153,960,755,200 |

The executable also hard-codes reference intervals only through \(n=16\)
(lines 424-446). A sound implementation would do more work, since it cannot
skip half the domain. Therefore this machinery could at most be considered
for a few additional degrees after a fundamental rewrite; it cannot bridge a
large finite interval up to Tao's threshold.

## Audit conclusion

Artifact hashes replay successfully. Mathematical certificate replay fails at
the semantics layer before any expensive rerun is useful. Running the binary
again would reproduce JSON predicates whose definitions are insufficient for
the theorem. Erdős #114 must not be selected on the premise that \(n\le14\)
is already certified.
