# SLACK-CAGE Zero-Switch Audit

Date: 2026-07-02

## Latest GPT-Pro Statement

The latest proposed atom is:

```text
minimal positive-debt pair (Q,U)
=> exists a (Q,U)-cage switch S with sigma(S)=0 and DeltaGamma(S)<0.
```

This is the same contradiction skeleton already implemented in:

```text
problems/23/writeup/_codex_slack_cage_switch_gate.py
```

The exact small-census gate remains vacuous because all tested true gmins cuts
already satisfy SLACK-CAGE directly:

```text
cuts = 2240
no_debt = 2240
positive = 0
switch = 0
fails = 0
VERDICT = VACUOUS_NO_POSITIVE_DEBT
```

So this atom is not currently mined from positive examples. It must be proved as
a minimal-counterexample theorem.

## Load-Bearing Gap 1: Flat5 Is Bankable, Not Zero-Debt

The proof text says:

```text
balanced C5-cell case has zero debt
```

That is not the form supported by the exact guardrail. The local UNIT-FLAT5
atom has positive local prebank:

```text
n = 15
m = 3
eta = 6
prebank = 1
counted_rows = 2
pair_inter = 4
has_flat5_bank_1 = True
```

Thus the corrected statement must be:

```text
Flat5 cells do not force DeltaGamma<0; each selected UNIT-FLAT5 atom consumes
one unit of the global eta bank.
```

The zero-switch proof can only close the non-Flat5 branch. The Flat5 branch
needs the selected-family / UNIT-PACK argument.

## Load-Bearing Gap 2: Counted-Row Safety Is Not Global Safety

The cage definition controls only counted rows:

```text
(g,P) in R_Q(U)
```

The Gamma comparison, however, is global over all bad edges in `M^S`.
Therefore the proof needs one of the following:

1. a safety lemma showing that every uncounted noncrossing bad edge keeps an
   old shortest B-geodesic after the switch; or
2. an error term charging any uncounted length increase to the same debt bank.

The gate computes actual `DeltaGamma(S)`, so the script is safe. The written
proof mechanism is not safe unless this missing safety statement is supplied.

## Load-Bearing Gap 3: Cage Decomposition Must Be Measure-Disjoint

The argument:

```text
if every cage has sigma(S)>0, summing first-exit inequalities gives
D_Q(U) <= |U| + sigma(U) + eta
```

requires a canonical decomposition of unpaid row atoms into cages with no
double-counting of:

```text
row-overlap mass,
blue first exits,
bad boundary exits,
Flat5 bank units.
```

The exact census showed symmetric duplicate UNIT-FLAT5 atoms. Therefore the
decomposition must choose a canonical selected family, not all possible local
Flat5 witnesses.

## Corrected Proof Split

A viable version of the lemma should be split into two statements.

### Non-Flat5 Zero-Slack Cage

For a minimal positive-debt pair, if an extracted cage is zero-slack and not a
UNIT-FLAT5 bank atom, then:

```text
sigma(S)=0
B^S connected
global safety holds
DeltaGamma(S)<0
```

This contradicts Gamma-minimality.

### Flat5 Bank Branch

Every extracted zero-slack cage that does not decrease Gamma is a selected
UNIT-FLAT5 atom, and selected atoms satisfy:

```text
number of selected atoms <= eta.
```

This prevents the Flat5 branch from producing positive total SLACK-CAGE debt.

## Current Exact Evidence

Pair-row-union census through `N<=11`:

```text
positive = 40
eta_paid = 40
unit_eta_paid = 40
nonunit_eta_paid = 0
fails = 0
```

Generated two-lane / long-row stress through `L<=24`:

```text
positive = 30
eta_paid = 30
unit_eta_paid = 2
nonunit_eta_paid = 28
fails = 0
```

UNIT-PACK proxy through `N<=11`:

```text
max_per_q = 1
max_disjoint_all = 1
max_disjoint_by_q = 1
violations = 0
```

## Next Formal Target

Define a canonical selected-family extraction:

```text
minimal positive-debt pair (Q,U)
=> disjoint sequence of cages S_i
```

such that every selected `S_i` is either:

```text
1. non-Flat5 and Gamma-decreasing at zero slack; or
2. UNIT-FLAT5 and consumes one eta bank unit.
```

Then prove:

```text
unpaid debt <= sum selected Flat5 bank units <= eta,
```

contradicting positive debt.

