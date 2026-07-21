# Queen Domination on Q_26 - Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-19T22:20:00+03:00
Status: CANCELLED - user stopped the Q26 SAT route on 2026-07-19T08:48:37+03:00

## Exact target

Let Q_26 be the graph on the 676 squares `(r,c)` with `0 <= r,c < 26`, where
two distinct squares are adjacent when they share a row, column, or diagonal.
Determine its domination number exactly. The published status is
`13 <= gamma(Q_26) <= 14`.

## DIRECT ROUTE

### 1. Exact final deliverable

Close one of these exhaustive alternatives:

1. POSITIVE: give 13 distinct square coordinates dominating every square of
   Q_26, two independent exhaustive verifiers, and a Lean proof of the exact
   finite witness; together with Weakley's published lower bound this proves
   `gamma(Q_26) = 13`.
2. NEGATIVE: emit a full-board CNF for domination by at most 13 queens, a
   machine-checkable LRAT/DRAT UNSAT certificate, its independent checker log,
   and an explicit verified 14-queen construction; this proves
   `gamma(Q_26) = 14`.

A heuristic failure, a restricted-family exclusion, or a solver bound is not
a deliverable.

### 2. Current frontier lemma / finite certificate

`Q26-13`: find a set `D` of exactly 13 squares such that every one of the 676
squares either belongs to D or shares a row, column, sum diagonal, or
difference diagonal with a member of D. The certificate is only 13 ordered
coordinate pairs. If the instance is UNSAT, the replacement frontier is the
proof trace for the same unrestricted full-board formula, not a new ansatz.

### 3. Explicit logical bridge

Weakley's lower bound gives `gamma(Q_26) > (26-1)/2`, hence
`gamma(Q_26) >= 13`. Therefore a verified 13-square dominating set gives both
bounds and proves equality. Conversely, verified UNSAT for every set of size
at most 13 gives `gamma(Q_26) >= 14`; the published explicit independent
14-queen dominating set gives `gamma(Q_26) <= 14`, again proving equality.

The SAT/CP variables are exactly the 676 board squares. Each board square has
one domination clause over its closed queen-neighborhood, and the only global
constraint is cardinality at most 13. Any D4 symmetry breaking must be proved
equisatisfiable and independently tested; no orbit or parity assumption may
replace the full formula.

For the positive construction lane only, one published necessary condition is
certified pruning rather than a restricted ansatz. Weakley 2022, Proposition
11, proves that a bichromatic size-13 dominating set of Q_26 has a 6/7 parity
split. Theorem 18 says a monochromatic one would require odd `d,e <= 13` with
`d^2 + 12 e^2 = 741`; direct checking of all 49 pairs gives none. Therefore
every possible size-13 witness has a 6/7 split. A heuristic may enforce this
equivalent condition, but its failure remains no theorem. An UNSAT certificate
must still cover the unrestricted formula unless this published implication
is also supplied as a separately checked proof bridge.


### 4. Next falsifiable action

The 64-worker sampled construction run ended `NO_HIT` after 3,600 seconds with
six uncovered squares; this is no mathematical conclusion. The transferable
min-conflicts mechanism from the user's
[`spiesRevised.cpp`](https://github.com/AlperTheKing/hackerRank/blob/bb64de313df3a8ad3f7e07e9cf4c6f2f32685fdc/spiesRevised.cpp)
passed the Q4 state audit but failed the required Q25 construction calibration
(`NO_HIT`, two uncovered squares after 30 seconds). That implementation lane is
`DEAD`; preserve its binary, audit log, and calibration summaries.

The next direct action is the unrestricted Q26 at-most-13 SAT lane.
Recheck that the encoder contains exactly the 676 primary board variables,
one full closed-neighborhood clause per square, and only the at-most-13
cardinality constraint. Reuse the Q13 UNSAT calibration for this same
Hilbert/modular-totalizer encoding before launch. No parity or symmetry
assumption is permitted in the formula whose proof could close the problem.
A solver model is a positive certificate; only an independently checked
proof trace for this unrestricted formula is a negative certificate.
Launch exactly 64 independent one-thread solver lanes on the literal unrestricted
`Q26` at-most-13 formula: 48 CaDiCaL195 seeds and 16 Glucose42 seeds.
Use Hilbert literal ordering and the modular-totalizer cardinality encoding;
do not add exact-cardinality, parity, D4, nonattacking, or pattern constraints.
The audited formula has 4,630 variables and 29,272 clauses: 676 full-board
domination clauses plus 28,596 at-most-13 cardinality clauses. Lane 1 also
writes the canonical DIMACS and a DRUP trace; all other lanes seek models.

Any SAT model must pass both independent board verifiers. Together with
the published lower bound, such a witness proves `gamma(Q_26) = 13`.
Only lane 1 can support a negative conclusion, and only after its unrestricted
DRUP trace passes an independent checker against the canonical DIMACS.
Proofless UNSAT, `UNKNOWN`, timeout, or portfolio exhaustion proves nothing.
At the global deadline, preserve all artifacts and record `NO_HIT` if neither
a verified model nor an independently checked unrestricted proof exists.
This portfolio exits only on one of those two final finite certificates.

### 5. Exit condition

Kill an implementation lane immediately if it fails either calibration or if
two independent checkers disagree. Stop the positive search if no model is
found by the deadline. Continue an UNSAT lane only if it is producing a full
checkable proof for the unrestricted instance and is on pace to finish within
the deadline. Do not branch to monochromatic, bichromatic, symmetric,
nonattacking, fixed-pattern, or bounded-coordinate subfamilies: excluding any
such family does not determine gamma(Q_26). At the deadline preserve all
artifacts, record DEAD if neither final certificate exists, and select a new
problem.

## Novelty gate snapshot

- W. D. Weakley, EJC 29(2), 2022, Proposition 21 retains
  `gamma(Q_26) in {13,14}`: https://doi.org/10.37236/10617
- Ostergard and Weakley, EJC 8(1), 2001, gives the explicit 14-queen upper
  construction: https://doi.org/10.37236/1573
- Rostami and Bright's 2025 proof-producing SAT work covers experiments and
  certificates only through n=19: https://arxiv.org/abs/2508.11945
- A targeted July 2026 paper, code, GitHub issue, and Formal Conjectures scan
  found no Q_26 resolution or priority claim. Formal Conjectures currently has
  no queen-domination statement, but mathlib has finite graph domination
  definitions suitable for a new exact theorem.
