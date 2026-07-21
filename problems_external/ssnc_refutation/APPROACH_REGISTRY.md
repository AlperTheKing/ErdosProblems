# Seymour Second-Neighborhood Conjecture - Counterexample Registry

Status checked: 2026-07-21.

## CURRENT-STATUS GATE

- The conjecture states that every finite oriented graph has a vertex `v` with
  `|N2+(v)| >= |N+(v)|`.
- Wang and Lu, *Graphs and Combinatorics* 42 (2026), Article 19, still state
  the general conjecture and prove special near-tournament cases.
- Sadhukhan, Sandeep, and Sen, arXiv:2606.30588v1 (2026), claim the case of
  minimum out-degree at most 7, with reproducible CP-SAT checks. This recent
  preprint is useful pruning but is not needed for the soundness of a hit.
- Seacrest, arXiv:1808.06293v3, proves that if a counterexample of minimum
  out-degree `delta` exists, one exists on at most `binom(delta+1,2)` vertices.
- A current search on 2026-07-21 found no accepted proof or counterexample to
  the general conjecture. This is a current-status gate, not a publication
  claim.

## DIRECT ROUTE - REFUTATION BY ONE ORIENTED GRAPH

### 1. Exact final deliverable

An explicit finite oriented graph `D`, supplied as a canonical adjacency list,
such that every vertex `v` satisfies

`|N2+(v)| < |N+(v)|`,

together with two independent exhaustive verifiers and a per-vertex
`(out_degree, second_out_degree)` ledger. This is the only success condition.

### 2. Current frontier finite certificate

Search for a counterexample with minimum out-degree 8. The first possible
order after the degree-7 result and the tournament theorem is `n=18`.
Seacrest's finite reduction bounds the minimum-order search for this degree
layer by `18 <= n <= 36`. The first attack is frozen at `n=18`; larger orders
are not automatic continuations.

For a proposed adjacency matrix `A`, define

- `N+(v) = {w : A[v,w] = 1}`;
- `N2+(v) = {w != v : A[v,w] = 0 and there exists u with A[v,u]=A[u,w]=1}`.

The graph must have no loops and no digons: `A[v,v]=0` and
`A[v,w] + A[w,v] <= 1`.

### 3. Explicit logical bridge

The conjecture asserts the existence of at least one vertex with
`|N2+(v)| >= |N+(v)|` in every oriented graph. A graph for which the strict
reverse inequality holds at every vertex is its literal negation. Therefore
one double-verified adjacency list refutes the full conjecture, with no
asymptotic, reduction, or unproved auxiliary lemma.

### 4. Next falsifiable action

Before production search:

1. implement independent scalar-set and bitset/matrix verifiers;
2. calibrate them on tournaments, directed cycles, deliberately invalid
   loop/digon inputs, and randomly generated oriented graphs;
3. implement an exact `n=18`, minimum-out-degree-8 CP-SAT/SAT model with
   bidirectional definitions for every two-step reachability variable;
4. implement an independent incremental-bitset local-search engine whose
   success predicate is exactly the verifier predicate;
5. run independent agent audits for encoding soundness and certificate replay.

Only after all five checks pass may a bounded multi-worker search start.

### 5. Exit condition

- **Success:** the same explicit graph passes both independent verifiers;
  stop all search and rerun the live novelty/status gate.
- **Exact finite result:** a proof-producing solver plus an independent proof
  checker may establish UNSAT for `n=18`; report only that finite theorem, not
  the conjecture, and stop this lane unless a separately registered direct
  counterexample mechanism justifies another order.
- **Resource exit:** after the fixed eight-hour refutation tranche, a timeout,
  `UNKNOWN`, ordinary `UNSAT` without a checked proof, or no hit is only
  `NO_HIT`. Stop. Do not cascade through orders 19-36, minimum degrees 9+, or
  restricted graph classes.

## REFERENCES

- H. Wang and M. Lu, *Seymour's second neighborhood conjecture for some
  oriented graphs*, Graphs and Combinatorics 42 (2026), Article 19,
  https://doi.org/10.1007/s00373-026-03014-y
- A. Sadhukhan, R. B. Sandeep, and S. Sen, *A proof of Seymour's second
  neighborhood conjecture for oriented graphs with minimum out-degree equal
  to 7*, arXiv:2606.30588v1 (2026).
- T. Seacrest, *Seymour's Second Neighborhood Conjecture for Subsets of
  Vertices*, arXiv:1808.06293v3 (2019).
- D. C. Fisher, *Squaring a tournament: a proof of Dean's conjecture*,
  Journal of Graph Theory 23 (1996), 43-48.

## DIRECT ROUTE - FIXED CONNECTED MISSING CYCLE AT ORDER 19

### 1. Exact final deliverable

One canonical adjacency list for an orientation of `K_19-C_19` with
outdegree 8 at every vertex and exactly three unreachable targets at every
vertex, accepted by both independent exhaustive SSNC verifiers and accompanied
by the complete 19-row neighborhood ledger.

### 2. Current frontier finite certificate

The exact fixed-cycle Boolean instance described in `N19_MECHANISM.md`: every
present edge has exactly one orientation; all outdegrees are 8; every
two-step and unreachable variable is defined biconditionally; and every row
and column of the unreachable relation sums to 3.

### 3. Explicit logical bridge

For every source, the 18 other vertices split into eight direct
out-neighbors, seven new second out-neighbors, and three unreachable targets.
Thus a satisfying assignment has `|N2+(v)|=7<8=|N+(v)|` for all 19 vertices
and, after independent replay, is a counterexample to the full conjecture.
An independently checked UNSAT certificate excludes only the fixed
`K_19-C_19` family.

### 4. Next falsifiable action

After the generator, frozen independent CNF specification, pinned-orientation
calibrations, parser audit, and proof-tool calibration all agree, run one
bounded proof-producing CaDiCaL instance for this exact fixed formula. Replay
SAT from raw adjacency data in both verifiers; check UNSAT with an independent
DRAT checker.

### 5. Exit condition

- Verified SAT: stop every search and repeat the live status/novelty gate.
- Independently checked UNSAT: close only this connected missing-cycle lane.
- Timeout, `UNKNOWN`, unchecked UNSAT, or no hit: mark this mechanism
  `BLOCKED` and stop; do not cascade to another 2-factor, value of `q`, order,
  or degree without a separately audited direct mechanism.

## STATUS UPDATE - 2026-07-21 17:40 +03:00

The registered `n=18`, minimum-outdegree-8 certificate class is closed by
the elementary double-counting theorem in `CONSTRUCTION_N18.md`. Two independent
referee passes accepted the proof; `REFEREE_COUNTING_OBSTRUCTION.md` records the
adversarial audit. No production search was launched at this layer.

This exact finite theorem is not a resolution of SSNC. The `n=18` attack is
exited. A larger order may not be opened automatically. The next active PLAN
must provide either a theorem-closing global proof bridge or a separately
justified construction mechanism whose explicit graph would refute SSNC.

## STATUS UPDATE - 2026-07-21 19:39 +03:00

The frozen `K_19-C_19` CNF (`A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38`)
is UNSAT. Two separately compiled binary-safe checkers replayed the unchanged
380,880,296-byte DRAT proof (`2BF6C909551EABE4E40A22920EC592900AD20FD3B34B964AD5FC8A77500D48D0`)
to exact `s VERIFIED`; positive and negative proof-tool controls also passed.

Independently, `CYCLE19_OVERLAP_OBSTRUCTION.md` gives a short two-block
digon contradiction. Referee review and exhaustive replay of all 59,049
relaxed local five-vertex states accepted it. `CYCLE19_OVERLAP_SCOPE.md`
shows that the argument excludes every sharp regular case
`n=2*delta+3`, `d+(v)=delta`, and missing degree 2, including every missing
2-factor at order 19; it does not depend on the connected-cycle choice.

This restricted theorem is not a resolution of SSNC. The irregular incidence
model in `GENERAL_GOOD_BLOCK_COUNTING_BARRIER.md` satisfies all current coarse
counting constraints, so those constraints do not bridge to the full
conjecture. No separately audited direct mechanism remains. This route is
exited, and no order/degree/family cascade is opened.

## DIRECT ROUTE - IRREGULAR ORDER-19 INCIDENCE LIFT

### 1. Exact final deliverable

One canonical 19-vertex oriented graph whose raw adjacency list satisfies
`|N2+(v)| < |N+(v)|` at all 19 vertices, with a complete ledger and acceptance
by the independent scalar-set and C++ bitset verifiers.

### 2. Current frontier finite certificate

The explicit irregular sharp-order parameter model in
`GENERAL_GOOD_BLOCK_COUNTING_BARRIER.md`: missing degrees
`{4,3^8,1^10}`, 19 specified target fibres, three unreachable targets per
source, and saturated target capacities `{7,5^8,1^10}`. An independent
construction report additionally claims a missing-edge-compatible orientation
realizing every listed block as a regular tournament; that raw seed must be
frozen and replayed before it is trusted.

### 3. Explicit logical bridge

A completion of that one finite seed satisfying the biconditional condition
`u in W_v` iff `u` is neither `v`, nor a direct out-neighbour of `v`, nor
reachable by a directed path of length two, has eight out-neighbours and at
most seven new second out-neighbours at every source. Its independently
verified adjacency list therefore refutes SSNC directly. A checked UNSAT
certificate excludes only this fixed irregular mechanism.

### 4. Next falsifiable action

Freeze the claimed missing graph, root incidence, and partial orientation.
Independently replay all degrees, missing-edge avoidance, root fibres, and
block tournaments. Only if they agree, construct two independent exact lift
encodings with bidirectional length-two reachability and test pinned SAT and
contradictory fixtures before one bounded proof-producing solve.

### 5. Exit condition

- Verified SAT: stop every search, produce the ledger, and rerun the live
  status/novelty gate.
- Independently checked UNSAT: close only this exact irregular lift.
- Seed disagreement, parser disagreement, timeout, `UNKNOWN`, or unchecked
  UNSAT: close this mechanism. Do not vary the missing graph, order, degree,
  or incidence hierarchy without a separately audited direct bridge.

## STATUS UPDATE - IRREGULAR SEED IDENTITY CORRECTION

The fibres printed in `GENERAL_GOOD_BLOCK_COUNTING_BARRIER.md` and the fibres
in `IRREGULAR19_INCIDENCE_SEED.json` are different finite objects. They must
not be conflated. `IRREGULAR19_LIFT_OBSTRUCTION.md` proves that the former
fibres are contradictory: `R_6={2,3,4,5,14}` and
`R_7={2,3,4,5,11}` cannot both satisfy saturated external-row equality.
That registered fixed-fibre mechanism is closed.

The JSON seed has different root blocks. Its stored orientation is a valid
8-outregular orientation realizing the coarse regular-block constraints, but
literal replay gives `|N2+(v)|=10` and no unreachable target at every vertex.
It is not a counterexample. Reorienting its fixed missing graph and different
linear root system remains a separate finite question.

## DIRECT ROUTE - IRREGULAR ORDER-19 LINEAR-SEED LIFT

### 1. Exact final deliverable

One canonical 19-vertex adjacency list satisfying the strict SSNC negation at
all vertices, with a complete ledger and acceptance by the independent scalar
and bitset exhaustive verifiers.

### 2. Current frontier finite certificate

`IRREGULAR19_INCIDENCE_SEED.json`, SHA-256
`B4BFB3000D9F14E7C763764DDF474FECD166DE12CC7F96B9D593F8801DF5EF69`,
fixes one missing graph with degree multiset `{4,3^8,1^10}` and a different
19-block root system of sizes `{7,5^8,1^10}` with three declared targets per
source. The stored orientation proves only coarse block-orientation
compatibility and is not pinned in the lift problem.

### 3. Explicit logical bridge

Any reorientation of the fixed present pairs for which the declared fibres
are exactly the literal unreachable relation has outdegree eight, three
unreachable targets, and seven new second out-neighbours at every vertex.
After two independent raw-adjacency replays, it is a counterexample to SSNC.
Checked UNSAT excludes only this exact missing-graph/root-system lift.

### 4. Next falsifiable action

Independently reconstruct the JSON missing graph and fibres, then build two
non-inherited exact models that leave all present orientations free while
pinning outdegree eight and the full biconditional unreachable relation.
Calibrate reachability, strictness, parser direction, and one-clause mutations
on pinned fixtures before any bounded production solve.

### 5. Exit condition

- Verified SAT: stop all searches, emit the full ledger, and repeat the live
  status/novelty gate.
- Independently checked UNSAT: close only this exact linear seed.
- Model disagreement, seed disagreement, timeout, `UNKNOWN`, or unchecked
  UNSAT: stop this seed; do not vary its incidence system automatically.

## STATUS UPDATE - TWO DISTINCT IRREGULAR SEEDS CLOSED

The fibres in `GENERAL_GOOD_BLOCK_COUNTING_BARRIER.md` are impossible by the
independently refereed 5-block overlap contradiction in
`IRREGULAR19_LIFT_OBSTRUCTION.md`. The different JSON root system is impossible
by the repeated-singleton and singleton-cycle contradictions in
`IRREGULAR19_LINEAR_SEED_OBSTRUCTION.md`. Its title is historical: the JSON
blocks are not linear (maximum pairwise intersection four). The stored JSON
orientation was separately rejected by both exhaustive verifiers with
`d+=8`, `|N2+|=10` on all 19 rows. Neither finite closure resolves SSNC.

## DIRECT ROUTE - UNRESTRICTED ORDER-19 STOCHASTIC REFUTATION

### 1. Exact final deliverable

One canonical adjacency list for any 19-vertex oriented graph satisfying
`|N2+(v)|<|N+(v)|` at every vertex, accompanied by the full per-vertex ledger
and acceptance by the independent scalar-set and C++ bitset verifiers.

### 2. Current frontier finite certificate

The search domain is the complete unrestricted set of oriented graphs on 19
vertices with minimum outdegree at least eight. No missing graph, degree
sequence, root incidence, symmetry class, or construction family is pinned.
The proved bounds `delta>=8` and `n>=2*delta+3` make order 19 the first direct
finite layer for minimum degree eight; the order-18 layer is already closed.

### 3. Explicit logical bridge

The engine objective is zero exactly when the raw graph satisfies the literal
strict inequality at all vertices. The two exhaustive verifiers then recompute
all direct and new second out-neighbourhoods from the raw adjacency list. One
accepted witness is therefore a counterexample to the full conjecture.

### 4. Next falsifiable action

Implement an order-19 local/stochastic engine whose score is computed from raw
bitset reachability, plus a separately implemented scalar oracle. Calibrate
score, mutation/revert, loop/digon rejection, strictness, parser, and candidate
replay on exhaustive small graphs and adversarial random walks. Only after an
independent audit may one self-terminating run use up to 64 CPU workers.

### 5. Exit condition

- Raw hit: stop all workers immediately and replay the unchanged certificate
  through both independent verifiers before any claim.
- Eight-hour bounded run with no verified hit: record only `NO_HIT`, preserve
  the best states, and stop this order. It is not UNSAT and does not authorize
  an order or degree cascade.
- Calibration disagreement, invariant failure, or parser disagreement: do not
  launch; close the engine as invalid.

## LIVE STATUS GATE - 2026-07-21 20:03 +03:00

A primary-source search immediately before the unrestricted order-19 route
found no complete proof or explicit counterexample. Bai, Li, and Park,
`arXiv:2607.18047` (submitted 2026-07-20), explicitly state that the general
conjecture remains open. Sadhukhan, Sandeep, and Sen, `arXiv:2606.30588`,
cover minimum outdegree at most seven, not the general case. This gate supports
starting the direct search; it is not evidence that a future result is novel.

- https://arxiv.org/abs/2607.18047
- https://arxiv.org/abs/2606.30588
