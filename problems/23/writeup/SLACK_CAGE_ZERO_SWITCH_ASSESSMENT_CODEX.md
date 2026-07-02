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

3. Flat-cell / Xi2 separation:
   The informal implication

   ```text
   zero-slack non-balanced cage => DeltaGamma(S)<0
   ```

   is false.  `C7` with an alternating maximum cut has zero-slack terminal
   prefix rotations with `DeltaGamma(S)=0`; they just move the unique bad edge
   around the odd cycle.  The strict condition must instead be residual and
   square-surplus based:

   ```text
   zero-slack + rho_Q(S)>0 + not banked Flat5 => Xi2(S)>0.
   ```

   Then a witness SDR from blue exits to crossing bad edges gives
   `DeltaGamma(S)<0`.  Flat5 cages with `Xi2(S)=0` are bank cases, and odd-cycle
   rotations with `Xi2(S)=0` have no residual positive debt.

4. Connectivity preservation:
   The cage extraction must either build `B^S` connected by construction or
   include the blue-closed/moat closure needed to make the switch connected.

This leaves the proof attack focused on the abstract decomposition,
positive-part Flat5 bank packing, and the `STRICT-RESIDUAL` implication
`rho_Q(S)>0 => Xi2(S)>0` for zero-slack non-bank cages, rather than on the
false non-balanced shortcut.
