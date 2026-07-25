# Erdős Problem 617 — Approach Registry

Live audit date: 2026-07-23.

## Exact statement

For every integer `r >= 3`, every `r`-edge-colouring of
`K_(r^2+1)` is conjectured to have a set of `r+1` vertices whose induced
complete graph omits at least one colour.

The cases `r=3` and `r=4` were proved by Erdős and Gyárfás. Their affine-plane
construction shows that the analogous assertion on `r^2` vertices fails.
The first open case is therefore `r=5`, on `K_26`.

## DIRECT ROUTE R1: refute at r=5

### 1. Exact final deliverable

A canonical colouring of all 325 edges of `K_26` by colours `0,...,4` such
that every one of the `C(26,6)=230230` six-vertex sets contains at least one
edge of every colour. The certificate must be accepted from the raw edge list
by two independently implemented exhaustive verifiers.

### 2. Current frontier certificate

Construct one five-colouring of `K_26` for which every colour graph has
independence number at most five. This is equivalent to the required
six-set condition.

### 3. Explicit logical bridge

At `r=5`, the conjecture asserts that every five-colouring of `K_26` has a
six-set omitting a colour. A colouring in which every six-set contains all
five colours is its direct negation, hence a single verified certificate
refutes the full universal conjecture.

### 4. Next falsifiable action

Calibrate two independent certificate verifiers on the published affine-plane
colouring of `K_25` and corrupted fixtures. In parallel, attack `K_26` through:

1. algebraic and construction-based extensions or perturbations of the
   affine-plane colouring;
2. exact SAT with bidirectional edge-colour semantics and audited
   symmetry breaking;
3. native C++ incremental local search whose candidates are always replayed
   by both exact verifiers; and
4. structural analysis of five graphs on 26 vertices with independence
   number at most five.

Only engines passing calibration and adversarial audit may use multiple CPU
workers.

### 5. Exit condition

A raw colouring accepted by both independent exhaustive verifiers resolves
the conjecture negatively and triggers a repeated live novelty search. A
timeout or `NO_HIT` is only bounded search failure. A proof-checked `UNSAT`
result closes only `r=5`; without a theorem covering all `r`, mark this route
`DEAD` and do not cascade automatically to `r=6`.

## Adversarial checks

- Each unordered edge receives exactly one colour.
- “Balanced” here does not mean equal colour-class sizes.
- Every six-set must contain every colour; merely avoiding monochromatic
  six-sets is insufficient.
- All 230230 six-sets are replayed directly from the raw edge list.
- Vertex and colour symmetry breaking must be proved satisfiability-preserving.
- Solver objectives, approximate scores, and unchecked assignments are not
  certificates.
- A negative computational result does not prove the general conjecture.

## DIRECT ROUTE R2: Ramsey--Turán edge lemma

### 1. Exact final deliverable

A proof, for every integer `r >= 3`, that every graph on `r^2+1` vertices
with both clique number and independence number at most `r` has strictly
more than `r(r^2+1)/2` edges.

### 2. Current frontier lemma

Prove the stated strict edge lower bound. The equality analogue is false for
`r=2`, where `C_5` has five edges, clique number two, and independence number
two; the route must use `r >= 3`.

### 3. Explicit logical bridge

In a counterexample colouring, every colour graph has independence number at
most `r`. It also has clique number at most `r`, since a monochromatic
`K_(r+1)` omits every other colour. The `r` colour graphs partition
`C(r^2+1,2)` edges, so one has at most `r(r^2+1)/2` edges, contradicting the
frontier lemma. Thus the lemma proves the full conjecture for every `r >= 3`.

### 4. Next falsifiable action

Test the bound exactly for the proved cases `r=3,4`, search for graph-level
counterexamples at `r=5`, and attempt a proof using critical subgraphs,
Brooks-type colouring, and Ramsey--Turán stability. Every proposed inequality
must be checked against `C_5`, joins, blow-ups, and small Ramsey graphs.

### 5. Exit condition

Exit R2 immediately if an explicit graph violates the frontier lemma, or if
the proof reduces to an open Ramsey--Turán statement of comparable strength
without an additional closing argument. A finite check for fixed `r` alone
does not complete R2.

### Route status

`R2 DEAD (2026-07-23)`: the frontier inequality is false at `r=5`.
Let `F=M(C_5)` be the 11-vertex Grötzsch graph, with 20 edges,
`alpha(F)=5`, and clique number two. Its complement `H` has 35 edges,
`alpha(H)=2`, and clique number five. Then `H disjoint_union 3K_5` has
26 vertices, 65 edges, and both independence and clique numbers five.

## DIRECT ROUTE R3: decompose K26 into five equality graphs

### 1. Exact final deliverable

A canonical decomposition of all 325 edges of `K_26` into five copies of the
65-edge graph `H disjoint_union 3K_5`, specified by five vertex permutations.
The five colour classes must be pairwise disjoint, cover every edge, and pass
both exhaustive `K_26` colour verifiers.

### 2. Current frontier certificate

Find five permutations of the equality graph whose edge sets are pairwise
disjoint. Since their total size is 325, disjointness implies exact coverage.

### 3. Explicit logical bridge

Each copy has independence number five. Therefore all five resulting colour
graphs have independence number at most five, equivalently every six-set
contains every colour. The decomposition is thus a complete `r=5`
counterexample and refutes the universal conjecture.

### 4. Next falsifiable action

Encode the exact graph-decomposition problem independently as permutation
search and exact-cover/SAT, calibrate on smaller decompositions, and replay
any output as a raw 325-edge colouring through both unrestricted verifiers.

### 5. Exit condition

A verified decomposition resolves the conjecture negatively. A checked
`UNSAT` or exhaustive `NO_HIT` kills only this equality-graph decomposition
route; unrestricted R1 remains the only direct refutation lane.

### Route status

`R3 DEAD (2026-07-23)`: the five-copy decomposition is impossible.
The degree-role and block-intersection proof is in
`structure/R3_DECOMPOSITION_OBSTRUCTION.md`; its independent arithmetic and
graph audit is `structure/audit_r3_decomposition_obstruction.cpp`.

## DIRECT ROUTE R4: pack five 61-edge Ramsey graphs

### 1. Exact final deliverable

Five vertex permutations of a fixed 61-edge spanning graph `G_61` whose
images in `K_26` are pairwise edge-disjoint. The remaining 20 edges are then
assigned arbitrary colours, and the resulting canonical 325-edge colouring
must pass both unrestricted exhaustive verifiers.

Here `G_61 = complement(F) disjoint_union 3K_5`, where `F` is the complete
`C_5` blow-up with cyclic part sizes `(3,2,2,2,2)`.

### 2. Current frontier certificate

Construct five pairwise edge-disjoint labelled copies of `G_61` in `K_26`.
This is a finite permutation-packing certificate with no auxiliary
asymptotic parameter.

### 3. Explicit logical bridge

The blow-up `F` is triangle-free and has independence number five, hence
`complement(F)` has independence number two and clique number five.
Consequently `G_61` has independence number five. Give the five packed
copies distinct colours and colour each of the 20 uncovered edges
arbitrarily. Every colour graph contains its spanning `G_61`; adding edges
cannot increase independence number. Thus each colour has independence
number at most five, every six-set contains all five colours, and the
resulting colouring refutes Problem 617.

### 4. Next falsifiable action

Generate and independently verify the canonical `G_61`. Build two
independent permutation-packing encodings, calibrate their edge-overlap
objectives adversarially, and search for overlap zero. Replay any raw packing
as a full colouring through both unrestricted verifiers.

### 5. Exit condition

A packing accepted by both full verifiers resolves the conjecture
negatively. A checked `UNSAT` for the complete permutation formulation kills
R4; a bounded `NO_HIT` kills only the specific search schedule. Do not open
another restricted family without a new direct bridge.

### Route status

`R4 DEAD (2026-07-23)`: five arbitrary copies of `G_61` cannot be
pairwise edge-disjoint. The general proof in
`structure/R4_GENERAL_PACKING_OBSTRUCTION.md` forces at least 59 distinct
edges inside a fixed 11-vertex set of capacity 55. The independent auditor
is `structure/audit_r4_general_packing_obstruction.cpp`.

## Target status

`HALTED INCONCLUSIVE (2026-07-23)`. R1 unrestricted native search was
cancelled after 219602944 reported moves with best score 842; unrestricted
exact SAT was cancelled without SAT or checked UNSAT. R2, R3, and R4 were
killed by exact counterexamples or proofs. None of these outcomes proves or
disproves Problem 617, and no computation is left running.
