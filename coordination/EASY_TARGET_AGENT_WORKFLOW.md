# Direct-Resolution Target Workflow

## Scope

Find an open Erdős problem that has a short path to a terminal object: an explicit counterexample, an explicit witness, or a direct proof with one load-bearing lemma. Problems 23, 424, and 864 are archived. Problem 273 is stopped unless a new direct bridge is supplied.

This workflow is subordinate to the root `AGENTS.md`, especially its DIRECT-PROOF GUARD and append-only reporting protocol.

## Round A — independent scouting

Run these roles independently. A scouting role must not start a proof search or edit a problem directory.

1. **Finite-certificate scout:** audit every current FALSIFIABLE, VERIFIABLE, and DECIDABLE entry against local search history.
2. **Literature-lag scout:** look for a primary-source theorem or construction newer than, or absent from, the official remarks.
3. **Elementary-route scout:** inspect open statements for a direct one-lemma proof, a small exact counterexample, or an exact finite reduction with an explicit bound.

Every nomination must contain: problem number, exact terminal object, exact current frontier, direct bridge, next falsifiable action, exit condition, primary citations, local-overlap check, and a ten-line-or-shorter rationale.

## Gate — no maze admission

A target survives only if all answers below are yes.

- Would the next successful computation or lemma materially settle the original statement?
- Is the bridge to the original quantifiers written explicitly?
- Can failure be interpreted without inventing a new reformulation?
- Is there a novelty gap after checking the official discussion, primary literature, and local history?
- Can an independent auditor verify the terminal object exactly?

Reject a target immediately if its route becomes an asymptotic surrogate, an equivalent-reformulation chain, an ineffective “sufficiently large” theorem, or an expanding sequence of bounded-family exclusions. Record the missing bridge as `DEAD: reformulation maze`.

## Selection rule

Rank survivors lexicographically by:

1. finite terminal certificate;
2. shortest direct lemma tree;
3. weakest external theorem dependency;
4. smallest exact verification cost;
5. least prior active competition.

Select exactly one target. Before attack, create its `APPROACH_REGISTRY.md` with the five mandatory DIRECT-PROOF GUARD fields and create or update `LITERATURE.md`, `COMPUTATION.md`, and `PROOF_STATE.md`.

## Round B — dynamic attack team

Use three roles per wave, then dissolve or retask them from the observed frontier.

1. **Constructor:** produce the witness, counterexample, or proof of the named frontier lemma.
2. **Falsifier:** attack the proposed bridge and search the smallest exact cases first.
3. **Auditor:** independently verify arithmetic, quantifiers, source hypotheses, and novelty.

Each role must return at least one concrete object: a certificate, reproducible exact computation, proved lemma, explicit counterexample to a step, or primary-source theorem with exact hypotheses. Generic status reports are rejected.

## Wave decision

After every wave, the root agent records one of four decisions:

- `SOLVED`: terminal object independently verified; run a fresh novelty gate and write the proof.
- `ALIVE`: one direct frontier remains; name the next exact experiment.
- `DEAD`: a falsifying fact kills the route; preserve artifacts and return to Round A.
- `DEAD: reformulation maze`: the direct bridge disappeared; stop without adding another surrogate.

GPT-Pro is used only after a target survives the gate: first to adversarially challenge the direct bridge, and later to audit a complete candidate. Its prompt and complete answer are archived under the selected problem.

## Acceptance

No target is called solved until the original statement, not a surrogate, has a complete proof or finite certificate; two independent checks agree; primary-source novelty is documented; and the user-facing claim matches the verified scope exactly.
