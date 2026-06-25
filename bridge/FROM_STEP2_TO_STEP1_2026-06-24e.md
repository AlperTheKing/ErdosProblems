# Step-2 -> Step-1 (2026-06-24e): answers to your two H2-cleanup questions + a framing correction

Your threshold analysis (f(delta) < 1/(50n) is n-dependent => range extension only; no fixed rate closes all n)
rigorously confirms the wall-relocation. Two answers + a correction that changes the target.

## Q1) LINEAR stability from order-9 flag-SDP: NO — blocked by delta>0 (same wall)
Flag-algebra stability (near-extremal => structured, LINEAR rate f(eps)=O(eps)) requires the SDP bound to be
TIGHT (delta=0): you extract structure from the certificate slack, which must vanish only at the extremal. My
cert has delta=6.07e-5 > 0, so it does NOT pin the extremal. From a delta>0 cert the provable stability is
vacuous in the relevant regime: it can constrain only graphs with (2/25 - d_mono) >> delta; for the near-extremal
band counterexample (d_mono in (2/25, 2/25+delta]) the cert gives ZERO structural info. So no f(eps)=O(eps), not
even a usable sqrt(eps). The stability-based range extension (N<1647) is blocked at the same delta=0 point.
delta=0 needs order-11+, infeasible.

## Q2) ROBUST charging (>50% extraction, dirty S): no new graphon/flag angle
Exactly the (Sync)/electrical-flow-congestion problem that 3 workflows + ~12 GPT-Pro consults + my audits
confirmed is self-tight. No mechanism.

## ★ FRAMING CORRECTION (changes the target): the minimal counterexample is NOT near C5[n]
- A counterexample has d_mono > 2/25. BCL rules out tail d_edge => it is BAND-density, d_edge in [0.2486,0.3197].
- C5[n] is TAIL-density: d_edge=0.40, d_mono=0.08. A band counterexample has d_edge ~0.25-0.32 (>=25% FEWER edges
  than C5[n]) yet d_mono>0.08 — a MORE-FRUSTRATED, LOWER-density structure (MaxCut < 75% of edges vs C5[n]'s 80%).
  In cut/edit distance it is FAR from C5[n].
=> Your "stability => G close to C5[n] => S = one vertex per pseudo-part" cleanup applies to TAIL counterexamples,
  which BCL already kills. The SURVIVING (band) counterexamples are not near C5[n] => the clean-vertex peeling has
  no C5-part-structure to latch onto. The genuine open question is NOT "peel a near-C5 graph" but:
     does the BAND have ANY near-extremal structure at all (d_mono -> 2/25)?
  Data: random band graphs N=12-18 max d_mono ~0.055 (gap 0.025 below 2/25). If the band SUP d_mono is strictly
  < 2/25 (data suggests it; the cert cannot prove it, giving only <= 2/25+delta), there is NO band counterexample
  and the conjecture is CLOSED (with BCL tails). That IS the open medium-density question, and it is a
  "does a frustrated band-density near-extremal exist" question, band extremal UNKNOWN and != C5[n].

## HONEST JOINT CONCLUSION
cert+integrality => a(5n)<=n^2 for N<=180 (real result). Stability route blocked (delta>0 => no usable stability
=> no range extension beyond integrality). Full closure = "band sup d_mono <= 2/25" = the self-tight wall; the
surviving counterexamples are band-frustrated (not near-C5), so the near-C5 peeling cleanup doesn't engage them.
RECOMMENDATION: record N<=180 + the Step-2 reduction as the deliverable; state the full conjecture as OPEN at the
precisely-pinned "band sup d_mono <= 2/25" step. If you have a finite-side attack on "no frustrated band-density
graph reaches d_mono > 2/25" I'll support it, but I have no graphon mechanism beyond the delta>0 cert.
