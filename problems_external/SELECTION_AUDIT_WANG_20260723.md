# Selection audit based on the Wang six-problem run

## Source set

- Public repository: `https://github.com/ShouqiaoW/erdos`
- Problems reported there: 390, 486, 536, 788, 1002, and 1038.
- The repository contains a problem-specific prompt and a mathematical
  manuscript for each of the six problems.

This audit concerns the shape of the successful routes. It does not treat the
repository manuscripts as externally refereed results.

## Common structure of the six successful routes

The decisive feature is not the topic or the availability of large-scale
computation. Each route starts from a mature reduction that leaves a finite
number of load-bearing gaps.

1. **390:** a pre-existing valuation lower-bound framework reduces the problem
   to exact cofactor allocation and smooth-number estimates.
2. **486:** the negative direction admits a finite-block colouring
   construction together with an exact interface argument.
3. **536:** the target is reduced through squarefree capacity and a balanced
   cube/cap-set estimate.
4. **788:** a graph min-max reduction is coupled to a finite-field extractor
   and an audited carry-lifting step.
5. **1002:** a Kesten-style fixed-start gap is closed by a Fourier/Ramanujan
   analysis and a continued-fraction rare-event estimate.
6. **1038:** a one-cut structural reduction is already available; the remaining
   cases are closed by analytic estimates and certified interval arithmetic.

The common selection signal is therefore:

> an established theorem has already reduced the original problem to one or
> several explicit lemmas whose truth would immediately close the original
> statement.

## Mandatory selection score

A candidate is admitted only if all five items below are concrete before an
attack begins.

1. The exact full-resolution statement.
2. A named current theorem or construction that supplies the scaffold.
3. One explicit frontier lemma or finite certificate.
4. A written implication from that frontier to the full statement.
5. A falsifiable exit test that can kill the route without starting a new
   equivalent formulation.

Additional priority is given to a direct negative construction, a finite
analytic case split, an exact constant gap, or a theorem with a visibly missing
endpoint case. Fame, prize value, and raw computability are not positive
selection signals by themselves.

## Rejections recorded in the current pass

- **1132:** the fixed-defect recurrence, clustered construction, and
  point-dependent interpretations fail; no theorem-closing fixed-point lemma
  remains.
- **1192:** the proposed tensor bridge fails because the relevant energy
  multiplies; the route does not preserve the required inequality.
- **156, probabilistic route:** the exact Ruzsa bad events have full support;
  ordinary LLL, the audited lopsided matching, and standard Moser--Tardos retain
  the logarithm.
- **734:** the available reduction is conditional on a new flat
  shifted-correlation code and therefore does not yet expose a smaller
  load-bearing lemma.
- **864:** the elementary sum/difference counts give only the known
  `sqrt(2)`-type upper constant; no bridge to `2/sqrt(3)` is currently stated.
- **1181:** the elementary primorial bound gives the coefficient `1`; a
  constant saving requires a new theorem controlling large prime divisors in
  a logarithmic-length interval.

## Current decision rule

Problem 156 remains active only while its deterministic Singer-lift and
batched-alteration routes are being audited. If both return only an equivalent
all-residue covering statement, Problem 156 is rejected and no larger finite
search is authorised.
