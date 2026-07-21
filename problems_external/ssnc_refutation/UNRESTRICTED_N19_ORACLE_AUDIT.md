# Independent black-box oracle for unrestricted order-19 search

Status: **PRELAUNCH ORACLE AND ADVERSARIAL TESTS PASS**.

This audit supports the registered `UNRESTRICTED ORDER-19 STOCHASTIC
REFUTATION` route.  It does not inspect, import, or share scoring code with a
future C++ local-search engine, and it launches no production search.

Artifacts:

- `unrestricted_n19_oracle.py`: scalar standard-library oracle and strict
  candidate parser;
- `test_unrestricted_n19_oracle.py`: exhaustive and adversarial tests.

## 1. Raw graph and literal neighbourhood contract

A candidate is a finite oriented graph represented by canonical adjacency
rows.  Missing unordered pairs are absent in both directions.  The parser
rejects loops, digons, duplicates, non-integer endpoints, unsorted rows,
out-of-range endpoints, wrong row counts, unknown keys, malformed JSON, and
non-UTF-8 input.

For each vertex `v`, the oracle independently recomputes

\[
 N^+(v)=\{w:v\to w\},
\]

\[
 R_2(v)=\{x:\text{there exists }u\text{ with }v\to u\to x\},
\]

and the new-only second out-neighbourhood

\[
 N^{++}(v)=R_2(v)\setminus(N^+(v)\cup\{v\}).         \tag{1}
\]

`R_2(v)` is retained verbatim in the ledger.  Direct vertices reached again
by a two-arc walk are recorded in `direct_raw2_overlap` and removed only when
forming (1).  This prevents the common error of counting direct-and-two-step
overlap as new second neighbours.

The remaining vertices form

\[
 W_v=V\setminus(\{v\}\cup N^+(v)\cup N^{++}(v)).    \tag{2}
\]

The four sets in (2) are checked as a disjoint partition on every row.

## 2. Exact objective and zero equivalence

For each row define

\[
 p_v=\max(0,|N^{++}(v)|-|N^+(v)|+1),                \tag{3}
\]

and for the registered order-19 domain define

\[
 d_v=\max(0,8-|N^+(v)|).                             \tag{4}
\]

The exact black-box objective is

\[
 \boxed{F(D)=\sum_v p_v+\sum_v d_v.}                \tag{5}

\]

All terms are nonnegative integers.  Therefore

\[
 F(D)=0
 \quad\Longleftrightarrow\quad
 \min_v d^+(v)\geq8
 \text{ and }
 |N^{++}(v)|<|N^+(v)|\text{ for every }v.            \tag{6}
\]

Structural invalidity never receives a score: it is rejected before (5).
The oracle also exposes `strict_objective=sum p_v` and
`domain_deficit=sum d_v` separately, so a future engine cannot hide a degree
violation inside a claimed strictness score.

The C++ engine may use any internal heuristic, but every externally reported
calibration score and every raw hit must agree with (5).  A different internal
score is acceptable only if it is not called the certificate objective and
zero is replayed against (5) before termination.

## 3. Canonical parser contract

The only accepted candidate shape is

```json
{
  "schema": "ssnc-oriented-graph-v1",
  "n": 19,
  "out_neighbors": [[1, 4], [], "..."]
}
```

The displayed ellipsis is explanatory only and is not valid input.  The
actual object must contain exactly the three named keys and exactly 19 sorted
integer rows.  `bool` values are rejected even though Python normally treats
them as integers.  Canonical serialization and SHA-256 fingerprinting are
provided for mutation/revert and raw-hit identity checks.

Command-line replay is

```text
python unrestricted_n19_oracle.py candidate.json --expected-n 19 --min-outdegree 8
```

Exit code 0 prints the complete JSON ledger.  Exit code 2 prints an `INVALID`
record and no objective.

## 4. Exhaustive and adversarial coverage

The command

```text
python -m unittest -v test_unrestricted_n19_oracle.py
```

completed all nine tests:

```text
Ran 9 tests in 0.743s
OK
exhaustive_small_graphs=760
pair_state_transitions=6/6 random_walk_steps=1000
mutation_revert_pairs=171
parser_byte_mutations=5
parser_object_mutations=15
```

The coverage is exact as follows.

1. **Every oriented/missing graph through order four.**  Each unordered pair
   independently takes the states missing, forward, or reverse.  All
   `1+3+27+729=760` graphs were replayed.  A separate triple-loop definition
   agreed on `N+`, raw length-two reach, new `N2+`, unreachable sets, each row
   penalty, the objective, and score-zero equivalence.
2. **Direct/two-step overlap.**  The explicit pattern
   `0->1`, `0->2`, `2->1` places vertex 1 in both `N+(0)` and raw length-two
   reach; the audit confirms it is absent from new `N2+(0)`.
3. **Degree boundaries.**  A cyclic 19-tournament has minimum outdegree nine.
   Removing its directed Hamilton cycle gives minimum eight.  Removing one
   further outgoing edge at vertex zero gives minimum seven and domain deficit
   exactly one.  The oracle accepts the first two domain states and rejects
   score-zero equivalence for the third.
4. **Every pair mutation and exact revert.**  Each of the 171 unordered pairs
   was mutated and restored.  Canonical bytes, SHA identity, ledger, and score
   returned exactly to the baseline.
5. **All pair-state transitions.**  A deterministic sequence plus a
   1,000-step walk with seed `20260721` covered all six ordered transitions
   among missing, forward, and reverse.  At every step a separate triple-loop
   calculation agreed with both objective components.
6. **Parser mutations.**  Wrong schema/key/count/type/order/range, duplicates,
   loops, digons, malformed/trailing JSON, BOM, and invalid UTF-8 were all
   rejected.
7. **Relabelling and reversal controls.**  A deterministic permutation
   preserved the objective and row-ledger multiset.  Reversing the graph with
   arcs `0->2,1->2` changed strict objective from one to two, proving that
   global arc reversal is not a score-preserving symmetry.

## 5. Why order 19 is the first registered feasible domain

Under the current registered degree gate, a counterexample has minimum
outdegree

\[
 \delta\geq8.                                       \tag{7}

\]

The proved fixed-target packing inequality gives

\[
 n\geq2\delta+3.                                    \tag{8}

\]

Combining (7)--(8) yields `n>=19`.  The order-18 degree-eight layer is also
independently closed, but (8) already identifies 19 as the first remaining
order compatible with the general packing theorem.

The domain is nonempty at the boundary: the cyclic regular tournament on 19
vertices has outdegree nine, and deleting its directed Hamilton cycle gives
an oriented graph with every outdegree eight.  These examples are calibration
states, not counterexamples.

For any oriented graph on 19 vertices, edge counting gives average outdegree
at most nine.  Hence minimum outdegree at least eight covers exactly the only
two possible minimum-degree layers, eight and nine.  The minimum-nine case is
a tournament and is already covered by the tournament theorem, but retaining
it in the oracle is harmless and makes the black-box domain definition
literal.

## 6. Safe and unsafe symmetry restrictions

Every vertex permutation preserves oriented validity, the objective, and the
ledger up to the same permutation.  Therefore full canonical relabelling is
safe.  Because every domain graph contains an arc, a single pin `0->1` is also
safe after relabelling the tail and head of any existing arc.

The following are **not** consequences of vertex relabelling and are unsafe
without a separately proved reduction or complete orbit branching:

- global arc reversal;
- fixing a missing pair, missing graph, number of missing pairs, or missing
  degree sequence;
- forcing every outdegree to equal eight;
- fixing root fibres, unreachable counts by target, or a regular-block
  incidence system;
- circulant, cyclic, dihedral, two-factor, parity, or other construction
  families;
- fixing additional arc directions merely because `0->1` was fixed;
- assuming strong connectivity inside this raw unrestricted domain without
  explicitly invoking and checking the relevant minimal-counterexample
  reduction.

The reversal control above is a concrete falsifier: reversal changes the
objective even on three vertices.  The degree-nine tournament and degree-eight
missing-cycle calibration states similarly show that a pinned degree or
missing pattern is not a relabelling symmetry of the declared domain.

## 7. Required black-box use before production

The future engine should emit canonical raw adjacency after every calibration
mutation and revert, together with its claimed certificate score.  The audit
must compare the unchanged candidate SHA, both objective components, and all
19 ledger rows against this oracle.  A candidate with claimed score zero is a
raw hit only if:

1. the parser accepts it at `n=19`;
2. the oracle returns `objective=0`;
3. mutation/revert identity remains exact; and
4. the separately compiled scalar and C++ bitset certificate verifiers both
   accept the same unchanged adjacency list.

Any discrepancy blocks launch under the registered exit condition.  Ordinary
search exhaustion remains `NO_HIT`, never UNSAT.

