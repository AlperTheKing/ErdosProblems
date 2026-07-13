# Result: exact circulation exists, but the compact transport LP is non-integral

## Verdict

There is no non-tautological global dual proof from the stated evidence alone.  An
exact min-cost circulation extended formulation exists by using the complete prefix
state of a row tuple, but it is exponential and its dual is exactly Bellman optimality.
The proposed compact component-transport formulation has a fixed-charge activation
variable and its LP relaxation is not integral.  Thus component transport plus
negative summed one-coordinate variation on the N12 census does not imply that every
global minimizer satisfies scoped Hall.

## Exact definitions used

For a row tuple `omega`, the repository defines

* `pairCount omega x y` as the number of selected rows containing both coordinates;
* `collisionUnits = sum_(x,y) (pairCount x y - 1)` (truncated Nat subtraction);
* `activeGraph` from blue edges internal to selected vertices and absent from selected
  row support;
* `ActiveOwner(omega,v)` by reachability in `activeGraph` from both endpoints of some
  selected bad atom;
* `activeDegree(omega,v)` as active-graph degree on an active component and zero off it;
* `hitNeedUnits(omega,v) = activeDegree(omega,v) - (N-selectedLoad(omega,v))`;
* `scopedObligationScore(omega) = card(ActiveCollisionHalf + ActiveHitNeed)`.

The target is: if `omega` globally minimizes `scopedObligationScore`, then
`Matching G c omega` is nonempty.

## Exact exponential min-cost circulation formulation

Order the bad atoms `0,...,m-1`.  Make one DAG layer per prefix length.  A state at
layer `i` is the complete sufficient statistic of the selected prefix: the selected
row references themselves (equivalently all pair counts, selected vertices, and
selected support).  For every legal row `q` of atom `i`, add a unit-capacity arc

`(i,state) -> (i+1,state extended by q)`.

Give all nonterminal arcs cost zero and the terminal arc from a complete state cost
the exactly recomputed integer `scopedObligationScore`.  Send one unit from the empty
state to the sink.  Unit-capacity DAG incidence matrices are totally unimodular, so an
optimal LP flow is an integral source-sink path and projects to an exact global row
tuple.  This is an exact extended formulation, but it has one state per distinguishable
prefix and can be as large as the row-choice product.

Its dual has a potential `pi_s` for each state and inequalities

`pi_t - pi_s <= cost(s,t)`.

Taking `pi_s` to be the optimal remaining cost gives equality on an optimal path.
Consequently, deriving Hall from this dual requires proving that every Hall-failing
terminal has a cheaper terminal path.  That is precisely the unbounded simultaneous
trade lemma; the formulation does not prove it.

## Exact compact-form integrality obstruction

Persistent-component accounting is linear only while a component remains active.
Charging/deactivating a component introduces a fixed-charge Boolean `a_C`.  The
smallest capacity formulation already has a fractional vertex:

`f = 1`, `0 <= f <= 2 a`, `0 <= a <= 1`, minimize `a`.

With integral activation `a in {0,1}`, the optimum is `a=1`, cost `1`.  In the LP
relaxation, `(f,a)=(1,1/2)` is feasible and optimal, cost `1/2`.  Hence the activation
capacity matrix contains the coefficient `2`, is not a network matrix/TU, and has
integrality gap `2`.  This is the exact obstruction to replacing the exponential
state DAG by the natural compact min-cost component circulation.  Larger component
capacity `k` gives gap `k` via `f=1,a=1/k`.

In the repository model, this fixed charge is not cosmetic: `ActiveOwner` is a
reachability predicate and `activeDegree` changes from a positive degree to zero when
a selected trade disconnects/deactivates the component.  The reported Lean-monotone
facts control surviving components; they do not linearize the Boolean event that a
component ceases to be active.  R29's strict Hamming-one cage demonstrates why that
event may require a coordinated multi-row trade.

## What is proved and what remains open

Proved here:

1. The full-state DAG is an exact integral min-cost circulation EF.
2. Its dual is equivalent to global dynamic-programming optimality and supplies no
   Hall inequality without an additional exchange theorem.
3. The natural compact activated-component relaxation is non-integral, with the exact
   witness above.
4. Negative summed one-coordinate variation implies a one-coordinate descent only for
   the tuple at which that sum is evaluated.  The N12 exhaustive fact therefore rules
   out failing local minima in that census, but it is not a universal dual certificate;
   R29 lies outside that gate and kills the universal Hamming-one premise.

Open proof gap (exactly one): prove a genuinely global simultaneous-trade theorem that
handles component deactivation, or prove an additional valid inequality cutting off
all fractional activation points such as `(1,1/2)`.  The latter inequalities describe
the convex hull of reachable active-component states and are equivalent in difficulty
to the former theorem.

## Fixture commands and exact outcomes

Command:

`python tmp/fanout/global_min_proof/mincost_flow_duality/verify_obstruction.py`

Exact output:

`integer_optimum=1; lp_optimum=1/2; fractional_witness=(flow=1,active=1/2); integrality_gap=2`.

The user-supplied N12 count (4,801,067 heavy tuples, zero component-transport failures,
negative summed variation at every scoped-Hall failure) is treated as supplied exact
evidence; no repository constructor for that aggregate was located in this worker's
search.  The 2943 constructor/data was also not located.  Therefore this worker does
not claim to have independently rerun either census or the 2943 gate.

## SHA-256 inputs and artifacts

Hashes below are filled from the files actually read or created.  `RESULT.md` cannot
contain its own SHA-256 without changing that hash; its final hash is reported in the
worker response.

<!-- HASHES -->

`533cd8772b6f0cd8f667e3388b7baba9a0734f862e41cb01cd6958ac2c296003  tmp/fanout/global_min_proof/COMMON.md`

`e032a3a8877ad80cdd0e628ea3352208330520f5b8d79a5b55da7b7637518b09  GOAL_CODEX_SHORT.txt`

`e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0  coordination/CODEX_ONBOARDING.md`

`b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126  coordination/CLAUDE_TO_CODEX.md`

`fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04  problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`

`d49a2653879bf808481b095c9f7d617ecffcb63c476426a74d3fb040eda4947e  problems/23/writeup/ROWSUM_O_reduction.md`

`e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean`

`8f39d8443ddc26d38bb76da10b9bed223f5f141546e6194c5177779f03174bc8  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean`

`6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedCoordinateTransport.lean`

`0051036592004a5050e2a015af456a5ceb9fddaf4438b2c006e9a9563374ffd1  tmp/fanout/global_min_proof/mincost_flow_duality/verify_obstruction.py`
