# S2 Application Audit Table

This table checks the five S2 reduced-theta hypotheses from
`S2_REDUCED_THETA_AUDIT.md` against the three live applications.

Legend:

```text
OK      = justified by definitions/gates/proven reduction.
S2      = this is exactly the common S2 lemma to prove.
OPEN    = still needs a prose/formal proof from the local setup.
```

## Application 1: Cap L=5 Forcing

Input object: minimal deficient cap component classified as a nested
`L/(L+2)` core plus baggage.

| S2 hypothesis | Status | Evidence / obligation |
|---|---:|---|
| terminal-prefix rows | OK | cap classification gives terminal Ferrers/laminar rows; Claude 21:35 calls this S1 |
| shortest-row property | OK | every row is in `cyc[f]` by construction |
| reducedness | OPEN | must prove arbitrary realization has no interior split-rejoin-split except by S2 contradiction |
| strictness source | OK | `L>=7` gives a middle corridor edge / annulus excess at least two |
| no intermediate terminal door | OPEN | if present, cap block was not minimal; needs explicit statement in cap classification |

Conclusion after audit:

```text
The only cap-specific prose gap is proving terminal-product normal form from
S1 plus the no-intermediate-door minimality condition.
```

## Application 2: Row TH-long / EHR

Input object: shortest residual co-witness corridor

```text
e0,g1,e1,...,gk,ek
```

with one endpoint `lambda>L0`.

| S2 hypothesis | Status | Evidence / obligation |
|---|---:|---|
| terminal-prefix rows | OK | terminal-shadow switch; `path_exit` gate rejects re-entry |
| shortest-row property | OK | all paths are selected from `cyc[h]` |
| reducedness | OPEN | must come from shortest `J` path minimality and innermost split/rejoin selection; do **not** use no-two-hole here |
| strictness source | OK | endpoint terminal slack is positive and `_slack_gate.py` proves nonzero slack >=2 |
| no intermediate terminal door | S2 | if present branch is already closed; otherwise shortcut follows |

Conclusion after audit:

```text
TH-long depends on proving that shortest J-corridor minimality supplies the
reducedness hypotheses needed for S2.
```

## Application 3: Row TH-rare / RM

Input object: minimum-lambda two-hole corridor with cost-flat alternating
closures.

| S2 hypothesis | Status | Evidence / obligation |
|---|---:|---|
| terminal-prefix rows | OK | terminal-shadow switch; REX theta gate supplies 5/7 terminal annuli |
| shortest-row property | OK | singleton miss rows are in `cyc[f]` and `cyc[g]` |
| reducedness | OPEN | must prove first shadow interaction gives a reduced split/rejoin pair; do **not** use no-two-hole here |
| strictness source | OPEN | broad RM persistence is false; the scoped first-interaction version must be proved by S2/minimality. Dangerous-direction diagnostic has empty real-data support |
| no intermediate terminal door | S2 | if present branch is already closed by the same contradiction |

Conclusion after audit:

```text
TH-rare is the most delicate application.  The proof must state RM precisely:
at the first interaction of two cost-flat shadows, either S2 gives a
shortcut/intermediate door or an F1 row is counted by c(farther) but not by
c(nearer), so c(farther)>c(nearer).
```

Sanity diagnostics:

```text
_codex_rm_directional_gate.py:
  tested=182
  status={'ok': 182}
  skip_nondangerous_cost=7484
```

This one-sided diagnostic shows that no dangerous `c(target)>c(root)`
comparison occurs in the finite battery.  It is not a proof of scoped RM,
because the actual first-interaction/two-hole object has empty real-data
support.  The broad unscoped predicate is false.

## Next Local Proof Targets

1. Cap terminal-product lemma:

```text
minimal nested L/(L+2) core + no intermediate terminal door
=> no interior split-rejoin-split
=> terminal-product normal form.
```

2. Row corridor reducedness lemma:

```text
shortest exit co-witness corridor
=> no hinge row witnesses nonconsecutive exits
=> first/last strict hinges form a reduced theta.
```

3. Rare monotonicity lemma:

```text
first interaction of cost-flat shadows
=> reduced theta or strict F1 witness-set inclusion.
```

The first two look like direct shortestness/minimality lemmas.  The third is
the main remaining prose audit item.

Circularity warning:

```text
The row-side H3 reducedness proof cannot cite the component-local no-two-hole
theorem, because S2 is used to prove that theorem.  Use only minimal
counterexample/corridor choices.
```
