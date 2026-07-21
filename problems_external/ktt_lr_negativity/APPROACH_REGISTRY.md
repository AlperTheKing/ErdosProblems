# KTT Stretched-LR Negativity Hunt — Approach Registry

Selected: 2026-07-21 (user-directed 64-agent / ~8-hour swarm campaign)
Status: ACTIVE

## Exact target

For partitions lam, mu, nu with |lam|+|mu|=|nu|, let c(nu; lam, mu) be the
Littlewood-Richardson coefficient (coefficient of s_nu in s_lam * s_mu), and
let P(n) = c(n*nu; n*lam, n*mu). Derksen-Weyman: P is a polynomial in n.
King-Tollu-Toumazet (2004) conjectured all coefficients of P (in the monomial
basis n^k) are nonnegative.

TARGET (= FrontierMath open-problem statement): exhibit one triple
(lam, mu, nu) such that P has at least one strictly negative coefficient.

## DIRECT ROUTE

### 1. Exact final deliverable

One triple + the exact interpolated polynomial P over Q + the full sample
table c(n*nu; n*lam, n*mu) for n = 0..D+2 computed EXACTLY by two independent
engines + verification at two extra points beyond the assumed degree bound.
This is a finite, machine-checkable certificate; FrontierMath has an external
verifier. A NO_HIT sweep proves nothing and is recorded as such.

### 2. Current frontier lemma / finite certificate

`KTT-CE`: a single negative coefficient in one exactly-interpolated stretched
LR polynomial. Degree bound: with r = len(nu), deg P <= (r-1)(r-2)/2 (hive
polytope dimension). Sample n = 0..D, interpolate exactly, then MANDATORY
check at n = D+1, D+2 (mismatch = DEGREE_ANOMALY, never a hit).

### 3. Explicit logical bridge

Knutson-Tao hive theorem: c(nu; lam, mu) = #integer hives with boundary given
by partial sums of lam, mu, nu (triangle side r). Stretching dilates the hive
polytope, so P is its Ehrhart polynomial (a genuine polynomial by
Derksen-Weyman), and any exact interpolation certified at D+2 points equals P.
A negative coefficient in P refutes the KTT positivity conjecture outright.
Known dead zones (engine validators, not hunt targets): c=1 => P==1 (KTW /
Fulton), c=2 => P=n+1 (Ikenmeyer; Sherman). Hunt bias: thin-but-high-
dimensional hive polytopes (small P(n) values, dimension >= 6), i.e. c in
[3,12], r in {5,6,7}, |nu| <= 60 — Ehrhart negativity lives in spiky
low-volume polytopes (Reeve-type phenomenon).

### 4. Next falsifiable action

Launch workflow `ktt-lr-negativity-hunt`: 2 independent exact engines
(C++ hive DFS counter with abort-cap; independent LR-rule tableau counter) +
cross-calibration gate (300 random triples r<=5 + c=1/c=2 stretched
validators; any disagreement aborts) + 4 waves x 14 family hunters
(adaptive: dead-family registry passed between waves) + adversarial
verification of every candidate hit by fresh agents recomputing all samples
with both engines and re-interpolating independently. ~64 agents, ~8h wall.
Artifacts under problems_external/ktt_lr_negativity/{engine,runs}/.

### 5. Exit condition

Stop on first CONFIRMED hit (then package HIT_CERTIFICATE.md + notify user;
submission decisions are the user's). Otherwise stop at wave-4 end or ~8h:
record NO_HIT with the dead-family registry and per-wave triple counts.
No restricted-family failure is evidence for the conjecture; no claim is made
from heuristic absence. Kill any engine lane on calibration disagreement.

## Novelty gate snapshot (2026-07-21)

- No published counterexample or claim found (web sweep 2026-07-21; FrontierMath
  lists the problem as open, "Major advance" tier, added Feb 2026).
- Polynomiality: Derksen-Weyman; short proof arXiv:2211.06810.
- c=2 theorem: Ikenmeyer (combinatorial), Sherman (arXiv:1505.06551 geometric).
- KTT source: King-Tollu-Toumazet, "Stretched Littlewood-Richardson and
  Kostka coefficients" (2004).
