# Delta=0 Dependency DAG

This DAG separates exact-verified finite consequences, pure path lemmas, and
geometry/application lemmas.

Canonical scoped geometry / Lean target ledger:

```text
problems/23/writeup/SCOPED_GEOMETRY_LEAN_TARGETS.md
```

## Layer 0: Already Proven Reduction

```text
ROWSUM-O / SPEC / LPD equivalence
=> rho(O)<=N
=> Gamma<=N^2
=> beta(G)<=N^2/25.
```

Authority:

```text
problems/23/writeup/ROWSUM_O_reduction.md
coordination/CODEX_ONBOARDING.md
```

## Layer 1: Pure Formal Graph/Path Lemmas

These should be formalized first.

```text
P1. shortest-row subpath is shortest.
P2. two shortest rows with two common vertices have equal segment lengths,
    unless one row can be shortened.
P3. strict arm replacement with saving >=2 gives a row shorter by >=2.
P4. length-2 degeneration gives a triangle.
```

Depends on: only `SimpleGraph.Walk` / path length / triangle-free.

## Layer 2: Terminal-Shadow Definitions

```text
T1. terminal-prefix rows meet S in one initial segment.
T2. terminal slack formula:
    s_f(e)=0 iff f witnesses e; positive slack >=2.
T3. stage0 matching optimality:
    reachable matched u with c(u)>c(e) gives a cost-decreasing exchange.
```

Exact gates:

```text
_slack_gate.py: mismatch=0, positive slack parity violations=0.
stage0 gates: all-min row-miss H2 ok=119; inherited enumerated ok=139.
_codex_rm_persistence_gate.py: dangerous-direction sanity check ok=182;
  skipped harmless cost direction comparisons=7484; no real two-hole support.
_codex_rm_persistence_gate.py: broad RM persistence fails on H2-allmax;
  this is the guardrail that forces first-interaction scope.
```

Formal status:

```text
T3 is elementary matching algebra.
T1/T2 depend on terminal-shadow definitions and can be formalized after those
definitions are fixed.
```

## Layer 3: Common S2 Geometry

```text
S2. reduced terminal theta + strict source
    => intermediate terminal door OR shorter blue row OR triangle.
```

Depends on:

```text
P1-P4, T1, reducedness hypotheses, strict source.
```

This is the central prose/formal audit target.

## Layer 4: Application Lemmas

### Cap

```text
C1. deficient cap classification -> nested L/(L+2) core + baggage.
C2. S2 -> terminal-product normal form for arbitrary nested core.
C3. L>=7 -> universal shared corridor edge.
C4. core recut lowers bad count/gamma unless an attachment creates S2 shorter row.
C5. therefore L=5, and local sign 25/4 closes cap side.
```

### Row

```text
R1. two residual misses -> shortest TH-Corridor.
R2. long endpoint -> S2/EHR -> contradiction.
R3. minimum endpoint -> RM + shadow separation -> stage0 cost exchange.
R4. therefore component-local row_miss<=1.
```

## Layer 5: Delta=0 Closure

```text
cap side closed + row side closed
=> selected terminal-shadow switch contradiction
=> no counterexample to ROWSUM-O/SPEC/LPD
=> Erdős #23.
```

## Current Open Formal/Proof Nodes

```text
S2 reduced terminal theta statement and proof.
C2 arbitrary-realization terminal-product normal form.
R3 rare monotonicity / near-witness persistence:
  broad form is false; dangerous-direction finite diagnostic is vacuous;
  formal proof must derive scoped persistence from first-interaction S2.
H3 noncircular reducedness:
  row H3 from shortest J-corridor minimality, not from no-two-hole;
  cap H3 from minimal deficient core, not from cap conclusion;
  RM H3 from first shadow interaction.
```

All other nodes are either exact-gated, algebraic, or already classified as
S2 consequences.
