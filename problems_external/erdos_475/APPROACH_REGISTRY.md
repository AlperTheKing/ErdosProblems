# Erdős Problem 475 — Approach Registry

Live audit date: 2026-07-23.

## Exact statement

For every prime `p` and every subset `A` of `F_p \ {0}`, determine whether
there is an ordering `a_1,...,a_t` of `A` whose nonempty partial sums

`s_j = a_1 + ... + a_j (mod p)`

are pairwise distinct.

Known results cover `t <= 12` and `p-3 <= t <= p-1`. A second novelty audit
found the published 2017 computation covering every abelian group of order
at most `23`; the public 2026 proof-candidate repository itself exhausts only
primes through `p=13`.

## DIRECT ROUTE R1: first uncovered counterexample layer

### 1. Exact final deliverable

One explicit sorted subset `A` of `F_17 \ {0}` with `|A|=13` for which no
permutation has pairwise distinct nonempty partial sums. The certificate
must include the canonical subset, a proof-producing exhaustive search
record, and acceptance by two independently implemented exact verifiers.

### 2. Current frontier certificate

Decide all `C(16,13)=560` subsets at `(p,t)=(17,13)`. This is the first
parameter layer not covered by `t<=12`, by `t>=p-3`, or by the public
small-prime backtest through `p=13`.

### 3. Explicit logical bridge

The conjecture is universal over primes and subsets. A single subset at
`p=17` with no valid ordering is therefore a complete negative resolution.
For a proposed subset, exhaustive traversal of every possible ordering,
with a fail-closed check of the partial-sum condition, proves that it is a
counterexample. Two implementations must replay the claim from the raw
sorted subset.

### 4. Next falsifiable action

Implement a native C++ exhaustive engine for precisely the 560 subsets,
calibrate it against the public `p<=13` checker and positive/negative
fixtures, and run an independently written C++ verifier. If either engine
reports a candidate, replay all `13!` branches through a separately derived
dynamic certificate or a checked SAT/UNSAT proof before any claim.

### 5. Exit condition

A candidate accepted by both independent exact verifiers resolves the
conjecture negatively and triggers a new live novelty audit. If every one of
the 560 subsets has a valid ordering, mark R1 `DEAD`. Do not automatically
cascade to larger primes or other cardinalities. `NO_HIT` at this layer is
only a bounded result and is not a proof of the conjecture.

## Adversarial checks

- Nonempty partial sums need only be pairwise distinct; they are not
  required to avoid `0`.
- The ordering must use every element of `A` exactly once.
- Arithmetic is modulo `p`.
- A zero total sum is allowed.
- Scalar-multiplication symmetry may reduce enumeration only after its
  soundness is proved; the final count must still account for all 560 sets.
- Search failure, timeout, and unchecked solver `UNSAT` are not
  counterexample certificates.

## Route status

`R1 DEAD (2026-07-23)`: the proposed `p=17` layer is not novel. Costa,
Morini, Pasotti, and Pellegrini report exhaustive verification for every
abelian group of order at most `23` in arXiv:1706.00042. The native engines
were stopped before this already-published layer was searched. The first
genuinely uncovered size-13 prime layer is `p=29`, but exhausting that one
finite layer has no stated bridge to the full conjecture, so it is not opened
automatically.
