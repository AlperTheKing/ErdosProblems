# S2 Circularity Audit

Claude's 2026-06-30T22:44Z audit says H1/H2/H4 are gate-verified and H5 is
a case split.  It originally suggested H3 reducedness follows from
no-two-hole plus selector minimality; Claude's 2026-06-30T22:52Z correction
agrees that the row-side use would be circular and must instead come from the
local minimal obstruction setup.

This needs care: for the row applications, S2 is used to prove no-two-hole.
Therefore H3 cannot rely on the already-proved no-two-hole theorem.  It must
come from the local minimal obstruction setup.

The positive scoped statements to prove are collected in
`SCOPED_ROW_GEOMETRY_LEMMAS.md`.  This file records the circularity and
false-broad-form guardrails.

## Invalid Shortcut

Do not use:

```text
row_miss<=1 in every residual component
=> no row witnesses two nonconsecutive exits in the corridor
=> reducedness for TH-long/TH-rare.
```

Reason:

```text
row_miss<=1 is the conclusion of the row-side no-two-hole theorem.
```

The exact gate verifies this conclusion on finite batteries, but it is not a
permitted assumption in the proof.

## Noncircular H3 Sources

### Row TH-Corridor

Reducedness must come from the choice of a minimal two-hole obstruction.

Setup:

```text
Assume a counterexample row f misses two exits in one residual component.
Choose missed exits e0,ek with minimum distance in the exit co-witness graph J.
Choose e0,e1,...,ek shortest in J.
```

Then:

1. Internal exits are f-tight.

```text
If some internal e_i is missed by f, then e0,e_i or e_i,ek is a closer missed
pair, contradicting minimality.
```

2. No chosen hinge row witnesses two nonconsecutive corridor exits.

```text
If g witnesses e_i and e_j with j>i+1, then replacing the subpath
e_i,...,e_j by the edge e_i--e_j gives a shorter J path.
```

3. No smaller split/rejoin theta inside the row-union disk.

```text
If one exists, select the first split and last rejoin inside the disk; this is
the actual S2 theta.  Thus the proof should use the innermost/outermost
split-rejoin pair, not assume none exists globally.
```

These three facts are noncircular and sufficient for TH-long/EHR reducedness.

### Cap L=5 Forcing

Reducedness must come from the minimal deficient cap core:

```text
Choose the nested L/(L+2) deficient core minimal by inclusion and then by
terminal interval size.
```

Then:

1. two interior split/rejoin events in the core row family define a smaller
   terminal block or an intermediate terminal door; or
2. they are the S2 theta itself.

This is noncircular because it uses cap-core minimality, not the cap
conclusion.

### Row TH-rare / RM

Reducedness must come from first interaction of cost-flat shadows:

```text
Take the first point where two cost-flat alternating shadows interact along a
residual co-witness corridor.
```

Then no earlier split/rejoin or smaller interaction can exist by definition.
If a near witness fails to persist before this first interaction, that failure
is itself an earlier interaction or an S2 theta.

This is the noncircular source for RM reducedness.

## Revised H3 Audit

Use:

```text
H3-row = shortest J-corridor minimality + innermost split/rejoin selection.
H3-cap = minimal deficient core selection.
H3-RM  = first cost-flat shadow interaction.
```

Do not use:

```text
H3 = no-two-hole theorem.
```

## Scope Guardrail

Every local certificate used in the row proof must be stated with its
minimal-counterexample scope as an explicit hypothesis.

Known broad-form failures:

```text
HT/contact false globally:
  H2-allmax, S=(0,1,11,12), f=(0,10), g=(11,16),
  p=(1,13), q=(0,13), lambda(p)=7>L0=5.
  Here f has only one missed high-tier exit, so it is not a two-hole endpoint.

RM/persistence false globally:
  H2-allmax, S=(0,1,2,3,4,5,6,10,11,12,13,14,15),
  r=(10,16), a=(7,14), b=(6,17), g=(10,17).
  The terminal disk has no ell(h)-3 shortcut for h in {r,g}.
```

Therefore the proof may use only:

```text
HT/EHR inside a genuine shortest residual two-hole corridor.
RM/persistence at the first cost-flat shadow interaction.
S2 reducedness supplied by shortest-corridor or first-interaction minimality.
```

These scoped row lemmas are not real-data gates on the current batteries:

```text
No actual two-hole residual corridor appears in the finite batteries.
The passing row_miss<=1 gates are evidence, not proof inputs.
The only finite falsification route is synthetic: build a candidate minimal
two-hole corridor or first-interaction shadow object and test whether S2
or the stage-0 exchange dissolves it.
```

Thus the honest row-side ledger is:

```text
Gate-verified: terminal-prefix rows, shortest rows, slack formula, parity
strictness, all-min-cost row_miss<=1 evidence.

Proof obligations: scoped H3 reducedness, scoped HT/EHR contact, scoped
RM near-witness persistence at first shadow interaction.
```

## Ask For Claude

The exact gates remain valuable as evidence:

```text
row_miss<=1 gates show no falsifier appears.
smaller_descent/minimalized switch gates support selector minimality.
```

But the proof must cite the noncircular local minimality arguments above.
