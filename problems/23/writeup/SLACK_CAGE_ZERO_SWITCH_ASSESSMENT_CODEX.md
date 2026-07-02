# SLACK-CAGE Zero-Switch Assessment

Date: 2026-07-01

## Target

GPT-Pro's latest lemma is a contradiction statement for a hypothetical minimal
positive-debt pair:

```text
epsilon_Q(U) = D_Q(U) - |U| - sigma(U) - eta > 0.
```

It asserts that such a pair forces a connected zero-slack cage switch `S` with

```text
sigma(S) = 0
DeltaGamma(S) < 0,
```

contradicting Gamma-minimality.

## Current Exact Gate Status

The existing gate

```text
problems/23/writeup/_codex_slack_cage_switch_gate.py
```

already implements the minimal positive-debt search followed by a cage-switch
search.  On the small exact census run:

```text
python problems/23/writeup/_codex_slack_cage_switch_gate.py \
  --min-n 7 --max-n 9 --cut-mode gmins --max-cuts 16 \
  --skip-two-lane --skip-named
```

the result is:

```text
cuts: 2240
no_debt: 2240
positive: 0
switch: 0
fails: 0
VERDICT: VACUOUS_NO_POSITIVE_DEBT
```

So this finite gate does not expose the switch structure: the tested graphs
already satisfy SLACK-CAGE directly.

## Consequence

The zero-switch lemma should be treated as a proof-by-minimal-counterexample
skeleton, not as a pattern mined from existing positive-debt examples.

The next proof obligations are:

1. Debt-cage decomposition:
   From a lexicographically minimal positive-debt pair `(Q,U)`, extract
   inclusion-minimal terminal row-cages whose first exits account for every
   unpaid atom.

2. Neutral cage forcing:
   Show that if all extracted cages have positive cut slack, then the summed
   first-exit inequalities imply

   ```text
   D_Q(U) <= |U| + sigma(U) + eta,
   ```

   contradicting positive debt.  Hence some cage has `sigma(S)=0`.

3. Flat-cell separation:
   For a zero-slack cage, either the terminal replacement has strict square
   gain and gives `DeltaGamma(S)<0`, or the cage is a balanced Flat5 cell with
   zero local debt.  The balanced case must be paid by the eta bank and cannot
   be the source of a positive-debt minimal pair.

4. Connectivity preservation:
   The cage extraction must either build `B^S` connected by construction or
   include the blue-closed/moat closure needed to make the switch connected.

This leaves the proof attack focused on the abstract decomposition and
Flat5-bank exclusion, rather than on further small-census counterexample
search.
