# WOWII / Graffiti.pc Conjecture 142 — Approach Registry

## DIRECT ROUTE — W142-B

1. **Exact final deliverable.** A referee-grade proof of the exact Formal Conjectures statement
   `tree(G) >= (2/3) girth(G) + eccSet(G, boundaryVertices(G))` for every finite nontrivial
   connected simple graph, together with a warning-free Lean 4 proof containing no `sorry` or
   `native_decide`, a current prior-art comparison, and the arXiv/DeepMind submission artifacts.
2. **Current frontier lemma or finite certificate.** Certify the splice lemma L7 in
   `PROOF_142_B.md`: for two descents to a shortest cycle of girth at least five, disjoint
   noninteracting descents form admissible forest components, while interacting descents splice
   into one admissible induced tree of order at least `d(u,v)+1`. The paper proof exists; the
   remaining frontier is independent referee certification and an exact Lean statement compiling
   without `sorry`.
3. **Explicit logical bridge.** L7 gives L8 for an `f`-realizer and a diametral pair. L8 yields
   `M(K) >= q = f+1-floor(g/3)` in the main range. Lemma M then gives
   `tree(G) >= g-1+q = f+ceil(2g/3)`. Lemmas L9 and L10 close respectively `g=4` and the
   two leftover residue boxes; `g=3`, small `f`, acyclic graphs, and `f=0` close by the
   compiled elementary bounds. These cases exhaust the exact theorem.
4. **Next falsifiable action.** State L7 with the exact descent/attachment data in a scratch Lean
   file, compile it against the pinned Formal Conjectures toolchain, and stop at the first goal
   whose claimed induced-tree or one-edge attachment property is false; in parallel, rerun the
   constructive certificate validator on its fixed corpus and preserve any counterexample.
5. **Exit condition.** Success when L7, L8, all residue cases, and the exact theorem compile in a
   clean worktree without warnings or prohibited shortcuts and an independent referee finds no
   gap. Exit DEAD on a verified counterexample, a false L7 attachment/counting claim without a
   direct repair, or a located prior full proof. Do not branch to another surrogate inequality.

## Current evidence

`PROOF_142_B.md` contains the complete direct paper proof. Existing exact validators report no
counterexample, but computation is not the proof. Do not cite the unpreserved hardening-log claim
from `PROOF_142_A.md`.
