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
