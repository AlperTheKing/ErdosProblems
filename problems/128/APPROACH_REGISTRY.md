# Erdős Problem 128 — Approach Registry

## Governing direct route

### Exact deliverable

An explicit simple graph on 20 labelled vertices, given by an adjacency list, such that:

1. the graph is triangle-free; and
2. every induced subgraph on 10 vertices has at least 9 edges.

The certificate must be checked by two independent exact verifiers.

### Current frontier

Does such a 20-vertex graph exist?

### Direct bridge

For `n = 20`, the threshold in Problem 128 is `n^2 / 50 = 8`, so “more than `n^2 / 50` edges” means at least 9 edges. It is enough to check 10-vertex sets: any larger vertex set contains a 10-vertex subset, and adding vertices cannot delete induced edges. Thus a certificate satisfying the two conditions above directly disproves the published and formalised universal statement.

### Next falsifiable action

Run one exact `n = 20` SAT/CP-SAT wave with Boolean edge variables, triangle-free clauses, and exact cardinality constraints requiring at least 9 selected edges in every 10-set. Use an independent cut-generation formulation to audit any candidate.

### Exit condition

- `SOLVED` if an explicit graph passes both independent exact verifiers and the novelty audit.
- `DEAD` for this route if `n = 20` is proved UNSAT with a checkable certificate.
- `DEAD` for this route if the declared one-wave formulations both exhaust their resource cap without a candidate; do not continue to `n = 21, 22, ...` and do not replace the target by an asymptotic relaxation.

## Rejected routes

- Asymptotic or graphon reformulations: they do not supply a direct bridge to a finite counterexample or the full theorem.
- Cascading searches over graph orders: bounded failures do not resolve the problem.
- Special-family enumeration beyond the already tested `C5` blow-ups and Andrásfai graphs: failure in another family is not evidence for the universal statement.


## 2026-07-13 wave outcome

Both declared one-wave formulations reached their resource caps with zero candidate graphs and no UNSAT certificate. The computational route is therefore `DEAD` under its precommitted no-cascade exit. Do not continue to another order or encoding. The already-running GPT-Pro audit may alter this only by returning an explicit graph that passes both exact local verifiers.

## Order-selection qualification

`ORDER_SELECTION_AUDIT.md` proves exact necessary bounds for every surviving order through 20. They do not rank one order uniformly: `n=20` was a defensible bounded experiment, not a proved optimal order. This does not reopen an order cascade.

## Final route decision — 2026-07-13

`DEAD`: both local one-wave formulations exhausted their caps without a candidate or UNSAT certificate, and GPT-Pro ended with `Thinking failed`. Preserve the artifacts. Do not reopen this route through another order, encoding, family, or asymptotic surrogate.

## DIRECT ROUTE — neighbourhood-completion inequality audit

### Exact final deliverable

Prove the full finite statement: every triangle-free graph `G` on `n` vertices has a set of `floor(n/2)` vertices spanning at most `n^2/50` edges.

### Current frontier lemma

For `h=floor(n/2)`, prove or refute this direct averaging lemma. Either some vertex has degree at least `h`, or some vertex `v` of degree `d<h`, with `B=V(G)\(N(v) union {v})`, `b=|B|`, `t=h-d`, `q=e(N(v),B)`, and `r=e(B)`, satisfies

`q*t/b + r*t*(t-1)/(b*(b-1)) <= n^2/50`.

### Explicit logical bridge

If `d(v)>=h`, any `h` neighbours form an independent set. Otherwise a uniformly random `t`-subset `T` of `B` has the displayed expected edge count, so the inequality supplies an `h`-set with at most `n^2/50` edges.

### Next falsifiable action

Evaluate the inequality exactly on the balanced blow-up `C5[4]`, including every possible `v`; do not launch an order search.

### Exit condition

If `C5[4]` violates the lemma, mark this route `DEAD` and retain the exact counterexample. If it survives, attempt a degree-sum proof. No weaker constant, asymptotic surrogate, or equivalent optimization model reopens the route.

### Route outcome — 2026-07-13

`DEAD`: `C5[4]` violates the frontier inequality at every vertex: the exact expectation is `576/55 > 8`, although a structured completion attains 8. See `DIRECT_INEQUALITY_ATTACK.md`. The missing bridge is a structure-sensitive correlated choice inside `B`; do not replace it by another first-moment model.

## Easy-target selection correction — 2026-07-13

`STOPPED`: Problem 128 is not literally a generalization of Problem 23. Problem 23 asks for an arbitrary bipartition with at most `n^2/25` total internal edges; Problem 128 asks for one induced half with at most `n^2/50` edges. Razborov explicitly treats them as distinct questions under the same theme.

Nevertheless, Problem 128 is not a tractable "easy remaining problem." Its best audited universal bound is `27n^2/1024`, and that method is sharp on the Clebsch graph. The only surviving full-theorem bridge found in this wave is a new low-degree deletion/lift lemma covering the entire unresolved range; no proof mechanism for that lemma was found. Continuing would therefore amount to relabelling the open core, contrary to the direct-proof guard. Preserve the exact audits and stop this selection.

## Delayed GPT-Pro audit — 2026-07-14

`NO REOPEN`: the delayed answer contains no explicit graph, UNSAT certificate, proof, or full-theorem mechanism. Its `n=20` advice predates the completed terminal wave. Its only new operational proposal is an exact scan of all 263,520 Ramsey `(3,6;14)` graphs. A hit would refute Problem 128, but a miss would exclude only order 14 and has no bridge to another order or the universal theorem. This is the forbidden post-hoc order cascade, so the scan is not launched. Archived answer SHA-256: `E0C01B128385824203F21C0147A64162EE8F350A09951377FAD30D7333D9CF3B`.
