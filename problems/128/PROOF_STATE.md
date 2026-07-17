# Erdős Problem 128 — Proof State

## Original claim

Every finite graph `G` on `n` vertices for which every induced subgraph on at least `floor(n/2)` vertices has more than `n^2/50` edges contains a triangle.

## Selected disproof instance

Set `n = 20`. A triangle-free graph in which every 10-vertex induced subgraph has at least 9 edges is a counterexample.

## Lemma tree

1. **Finite witness:** construct the 20-vertex adjacency list.
2. **Triangle audit:** enumerate all `C(20,3) = 1140` triples and show none induces three edges.
3. **Half-set audit:** enumerate all `C(20,10) = 184756` ten-sets and show each induces at least 9 edges.
4. **Monotonicity bridge:** every larger induced set contains a ten-set and hence has at least 9 edges.
5. **Threshold bridge:** `9 > 20^2/50 = 8`.
6. **Novelty gate:** compare the witness with the primary literature and official discussion.

## Status

Open frontier: Lemma 1. No witness exists yet.


## Status update — 2026-07-13

No 20-vertex witness was found, and no nonexistence theorem or checkable UNSAT certificate was obtained. The one-shot search route has reached its declared hard exit. Problem #128 is not solved. The independent GPT-Pro response remains pending; absent a verifier-passing adjacency list, this route stays closed.

## Final status — 2026-07-13

Problem #128 remains unsolved. No finite witness and no impossibility proof were obtained. GPT-Pro returned no mathematical content. The selected `n=20` route is closed under the mandatory no-cascade rule.
