# AUDIT of round6/P3.md (Vega graphs) — ADVERSARIAL

STATUS: IN PROGRESS (stub filed 2026-07-25). Verdicts below are provisional until marked FINAL.

Auditor protocol: independent re-implementation in `round6/audit_P3_*.py`, exact rational/integer
arithmetic on every acceptance path, mandatory regression against
`round5/claude_witness_regression.py`.

## Claims under audit (from P3.md)
- (a) Vega family definition: infinite, one parameter i>=2, four members per i.
- (b) `P3_vega.g6` = 28 graphs i=2..8, all triangle-free / maximal / chi=4 / odd girth 5 / delta>N/3.
- (c) 2.6255e11 weightings, zero violations; max psi = 1/25 attained exactly at 5|q.
- (d) ARCPLUS cut family is EXACT (ARCBOUND = psi); m(b)/bound_k hierarchy FAILS on Vega
      (claimed witness Upsilon_2, q=15).
- (e) delta-constrained maximum 29/841 = 0.0344828 (Grotzsch) — "Vega not the hard case".

(verdicts to follow)
