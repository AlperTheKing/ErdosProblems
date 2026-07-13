# Independent rooted t=5 support audit

## Verdict

**PASS for the nine completed support-level claims at orders 15 and 16.**

The original artifacts contain only a CP-SAT terminal status.  They do not
contain a support object, a circuit object, or a solver proof.  This audit
reconstructs the support constraints independently as CNF and proves a
strict relaxation UNSAT for every split:

| order | split | vars | clauses | core clauses | DRAT bytes | LRAT bytes |
|---:|:---:|---:|---:|---:|---:|---:|
| 15 | 7+8  | 3046 | 7236 | 11   | 31176   | 13031   |
| 15 | 8+7  | 3036 | 7214 | 17   | 31772   | 13517   |
| 15 | 9+6  | 3000 | 7202 | 770  | 228029  | 242171  |
| 15 | 10+5 | 2968 | 7240 | 49   | 223762  | 241003  |
| 16 | 7+9  | 3794 | 9025 | 11   | 39038   | 14627   |
| 16 | 8+8  | 3791 | 8989 | 17   | 38796   | 15193   |
| 16 | 9+7  | 3774 | 8981 | 2641 | 1021320 | 2787360 |
| 16 | 10+6 | 3733 | 8991 | 2439 | 436742  | 783696  |
| 16 | 11+5 | 3698 | 9059 | 103  | 279878  | 310843  |

All three independent PySAT backends (`cadical195`, `glucose4`, and
`lingeling`) return `UNSAT` on all nine CNFs.  CaDiCaL emits textual DRAT and
native LRAT proofs.  `drat-trim` and `lrat-trim` independently print
`s VERIFIED` for every split.

Canonical manifest SHA-256:

```text
5555438712085653259b65b98c25da17647e41602b1df23494abe4cb6bbbe33a
```

## Independent formulation

The encoder in `independent_t5_cnf.py` does not import the production
generator.  Its primary variables are the bipartite support edges.  Tseitin
definitions express:

1. common-neighbour distance-two relations on each shore;
2. exact distance four as a two-step walk in the shore square with no
   distance-two shortcut;
3. exactly 24 support edges;
4. the six prescribed edges of the two rooted rows;
5. degree five for both rotating owners and no isolated support vertex;
6. the rooted bad pair at distance four;
7. at least five distance-four atoms at each owner;
8. at least 25 same-shore distance-four atoms globally.

The CNF deliberately omits two source-model constraints:

- support connectivity;
- safe degree-order label symmetries.

It also omits every downstream circuit, classifier, and active-scope
condition.  Those conditions are reached only after a support is found, while
all nine source artifacts report `supportsSolved = 0`.

Therefore every source CP-SAT support assignment would satisfy this CNF, but
not conversely.  UNSAT of the CNF proves UNSAT of the source support model
without trusting its flow formulation or symmetry breaking.

## Positive control

The same independent encoder, now with its own bounded-reachability
connectivity encoding, is SAT at split `9+8` (order 17) in all three solvers.
`semantic_check.py` verifies the returned graph directly:

```text
edge count                 24
connected                  true
root degrees               5, 5
root distance-four counts  5, 5
total distance-four atoms  26
```

This rules out a globally contradictory encoder and matches the reported
order-17 feasibility frontier.

## Source artifact audit

The following canonical source hashes recompute exactly:

```text
n15 7+8   14ac9d93df5b975282318107c2db9b41276662a8cf9031757e1bd4a00c9dee56
n15 8+7   8d194613f11069adde25a7f01b6f60b781196ab3842866219c034dc300608ed1
n15 9+6   66e0813cffb89df44b06cfbbd090fec6a4d8f27fca2180ea0c236eba38dd52c0
n15 10+5  5721cbc543b4338fa95281fbddd579621bd82452d6332989ad8563f41794ec68
n16 7+9   8dff49eae32a418a07390cdcc9db0395098c1ae28e2e65064cff9e34927e1683
n16 8+8   bd0c032079def49ca9d71583e03a9ad87a0d486b30b4d82f453daa3b922cfa8e
n16 9+7   cc5462d6c4b82a52634511780c3b5b1a8d3f6e9928b67222eb75c21dad16070c
n16 10+6  b5037e11ada7075f2704625eb249536ea499616f4b82d59b3a1ad6544e3c99a2
n16 11+5  9f9401d07b5190a359c3917d505314b58361a3844039dc55a160cc78cb6a4921
```

Every source artifact has `supportTerminalStatus = INFEASIBLE`,
`supportsSolved = 0`, `hit = null`, and an empty `circuitStatuses` map.
Consequently there are **zero emitted support certificates and zero emitted
circuit certificates** to inspect.  The only original evidence was the
uncheckable solver-status string.

## Exactness boundary

What is now exact and independently replayable:

- byte and canonical hashes of all nine source artifacts;
- CNF reconstruction of a strict support-model relaxation;
- three-solver UNSAT agreement;
- DRAT verification;
- native LRAT verification;
- direct graph-semantic verification of a connected order-17 SAT control.

What is not kernel-closed:

- the implication from the prose/source support specification to the CNF is
  reviewed and tested, not yet a Lean theorem;
- `drat-trim` and `lrat-trim` are native C checkers, not Lean-kernel checkers;
- the original CP-SAT JSON files still carry no solver proof of their own;
- this audit does not close any feasible order-17-or-higher split and does not
  certify downstream circuit/classifier no-hit searches.

Thus the honest coverage verdict is: **the completed order-15 and order-16
support infeasibility claims are independently exact-verified, but not yet
imported into the final Lean kernel.**

