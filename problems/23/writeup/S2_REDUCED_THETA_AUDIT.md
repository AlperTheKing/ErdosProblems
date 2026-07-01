# S2 Reduced-Theta Audit

Purpose: isolate the single geometric lemma now used by the cap and row
closures, and list the hypotheses that must be checked before the delta=0
proof can be called proof-grade.

Detailed lemma target:

```text
problems/23/writeup/S2_REDUCED_THETA_LEMMA.md
```

## Common Lemma Target

Let `B` be the cut graph.  Let `P` and `Q` be terminal-prefix shortest rows
of bad edges in a completed terminal-shadow switch.  Suppose their relevant
subpaths form a reduced blue theta:

```text
two internally disjoint blue arms between the same split/rejoin vertices,
with the terminal-prefix orientation inherited from the switch.
```

The S2 reduced-theta lemma must prove:

```text
Either the theta contains an intermediate terminal door,
or it yields a blue path for one involved bad edge h
of length at most ell(h)-3,
or the length-2 degeneration forms a triangle in G.
```

The forbidden alternatives are:

```text
intermediate terminal door  -> violates the selected minimal terminal block,
shorter blue path           -> contradicts definition of ell(h),
triangle                    -> contradicts triangle-free.
```

## Hypotheses To Check

Every application must explicitly provide:

1. Terminal-prefix property.

```text
Each row meets the switch S in one initial segment and never re-enters S.
```

2. Shortest-row property.

```text
Each row is in cyc[h] for its bad edge h, so every internal segment is a
shortest blue path between its endpoints.
```

3. Reducedness.

```text
No row witnesses two nonconsecutive exits in the chosen corridor, and no
smaller split/rejoin pair was available.
```

4. Strictness source.

```text
At least one terminal slack or annulus excess is positive and even, so the
diagonal saves at least two blue edges.
```

5. No already-existing terminal door.

```text
If an intermediate terminal door exists, the application is already closed;
otherwise the theta splice must be a genuine shortcut.
```

## Applications

### Cap L=5 Forcing

Input:

```text
nested L/(L+2) deficient cap core.
```

S2 use:

```text
two interior splits in the core row bundles force an intermediate terminal
door or a shorter row.
```

Conclusion:

```text
terminal-product normal form.
For L>=7 the common middle corridor contains a universal blue edge.
Recutting that edge replaces two bad terminal edges by one shorter/equal
shared-corridor bad edge, contradicting gamma-minimality.
Therefore L=5.
```

Audit status:

```text
Finite gates verify canonical stretched cores and one-edge attachments.
Need prose check that arbitrary realizations satisfy terminal-product
hypotheses before recut.
```

### Row TH-long / Endpoint Hinge Rigidity

Input:

```text
a minimal two-hole residual corridor with a long-lambda endpoint.
```

S2 use:

```text
first f-improving hinge and last f-worsening hinge form a reduced theta.
Endpoint slack gives the strictness source.
```

Conclusion:

```text
triangle or blue path of length <= ell(h)-3 for some involved h.
```

Audit status:

```text
Claude/GPT-Pro classify as S2 mirror. Need check reducedness follows from
shortest exit co-witness path and internal f-tightness.
```

### Row TH-rare / Rare Monotonicity

Input:

```text
minimum-lambda two-hole residual corridor, with cost-flat alternating shadows.
```

S2 use:

```text
an F1 row witnessing the farther exit but not the nearer exit gives a
first-split/last-rejoin theta unless it contributes a new F1 witness on the
farther side.
```

Conclusion:

```text
rare cost increases inward, c(farther)>c(nearer).
At the first interaction of two flat shadows this gives a reachable matched
exit of larger rare cost, contradicting stage-0 min-cost.
If shadows are disjoint, mu(F0) separates them, so they are not in one
residual component.
```

Audit status:

```text
Claude/GPT-Pro classify Atom B as complete. Need state RM with exact
nearer/farther orientation and verify the corridor interaction always
satisfies the S2 reducedness and strictness hypotheses.
```

## Exact-Gated Consequences

Already gated:

```text
REX theta singleton misses: 86/86 mirrored, 72/72 Codex inherited gate.
TH-Corridor row no-two-hole: tested=182, ok=182.
All-min stage0 row-miss: H2 tested=119 ok=119; inherited enumerated ok=139,
too_many=43, row_miss_fail=0.
L=5 forcing canonical stretches and one-edge attachments: no L>=7 survivor
with preserved parent lengths.
```

The remaining proof work is therefore not a new search but a formal audit of
this S2 reduced-theta statement and its three applications.
