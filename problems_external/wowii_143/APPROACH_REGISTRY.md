# WOWII / Graffiti.pc Conjecture 143 — Approach Registry

## DIRECT ROUTE — W143-A

1. **Exact final deliverable.** A referee-grade proof that every finite connected non-tree graph G satisfies t(G)·δ′(G) ≥ g(G)+1, where t is maximum induced-tree order, g is girth, and δ′ is the second-smallest degree; include a current prior-art comparison and Lean 4 verification of key lemmas when feasible. Deadline: 2026-07-18T21:57:27+03:00.
2. **Current frontier lemma.** L: if a finite connected cyclic graph has girth g and at least two leaves, then it has an induced tree on at least g+1 vertices.
3. **Explicit bridge.** If δ′≥2, a shortest induced g-cycle minus one vertex gives t≥g−1 and tδ′≥2(g−1)≥g+1. If δ′=1, the degree ordering gives two leaves and L gives tδ′=t≥g+1. These exhaustive cases are exactly the target inequality.
4. **Next falsifiable action.** Exhaustively enumerate all connected unlabeled graphs of orders 1–7, exactly compute g, δ′, and t, and test the inequality; preserve any counterexample. If none exists, referee the maximal induced tree proof of L line by line.
5. **Exit condition.** Exit DEAD on a verified counterexample, a located prior full proof, or a flaw in L without a replacement lemma that still directly implies the theorem. Stop at the deadline if proof, prior-art audit, and verification are not all complete. Do not branch to asymptotic or restricted-family bounds.

## Executed proof of L

Choose two leaves x,y and a maximum-order induced tree T containing both (a shortest x–y path makes the class nonempty). Since G is not a tree, T is not spanning. Connectivity gives z outside T adjacent to T. Maximality forces z to have two neighbors a,b in T. The unique a–b path P in T together with z contains a cycle, so |V(P)|≥g−1. Neither leaf lies on P, hence |T|≥|V(P)|+2≥g+1.

## Status

W143-A DECIDE/HANDOFF. Proof: PROOF.md. Two exact atlas oracles found no violation. Three logical reviews found no mathematical gap. Two key Lean components compile without warnings. The final novelty gate passed with no prior proof located (not proof of absence). Direct GitHub posting was not performed because Formal Conjectures adopts Mathlib's rule against LLM-written GitHub messages; human review and an independently written submission remain.

## DIRECT ROUTE — W143-B FORMAL SUBMISSION

1. **Exact final deliverable.** A clean PR branch for `google-deepmind/formal-conjectures` containing a warning-free, no-`sorry`, no-`native_decide` Lean proof of Graph Conjecture 143, pushed to the user's fork. GitHub prose is excluded and remains human-authored under repository policy.
2. **Current frontier lemma.** Formalize the two-leaf bound: a finite simple connected cyclic graph with two distinct degree-one vertices has `largestInducedTreeSize G ≥ G.girth + 1`.
3. **Explicit bridge.** Split on `secondSmallestDegree G = 1`. The frontier lemma closes that case. Otherwise positivity gives `2 ≤ secondSmallestDegree G`; deleting one vertex of a shortest chordless cycle gives an induced tree of size `girth - 1`, and arithmetic closes the target. Connected trees use `girth = 0` and the spanning induced tree.
4. **Next falsifiable action.** Create a scratch theorem with the exact target signature, import the existing key extension lemma, and compile it; every remaining goal must name a missing graph API lemma or be closed directly.
5. **Exit condition.** Success when the exact theorem compiles in a clean worktree and the branch is pushed. Exit the PR route if a full proof cannot fit repository rules or if expert acceptance is required before the status change; preserve a compiled auxiliary-lemma branch instead.

## Status W143-B

SUCCESS. Exact theorem and helper API compile without warnings or prohibited shortcuts. Full `lake --wfail build` completed 8868 jobs. Proof commit `6aab64f`; required `formal_proof` metadata commit `eb64455`; branch `codex/wowii-143-proof` pushed to `AlperTheKing/formal-conjectures`.

