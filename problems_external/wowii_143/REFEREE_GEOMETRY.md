# Independent referee report — WOWII / Graffiti.pc Conjecture 143

## Decision: ACCEPT

The mathematical proof is correct. I found no counterexample or logical gap in the maximal-induced-tree argument, the degree split, the acyclic extension, or the equality construction. The required editorial repairs identified in the first review have now been completed. The separate final novelty check remains a project-level requirement, not a defect in this proof.

## Mathematical audit

- **PASS — maximality quantifier (`PROOF.md`, line 32).** The family of induced trees containing the two selected leaves is nonempty because a shortest leaf-to-leaf path is induced. Finiteness permits choosing a member of maximum order *within that family*. This is exactly the maximality needed later; global maximality is unnecessary.
- **PASS — properness and the boundary vertex (`PROOF.md`, lines 34–37).** If the chosen induced tree `G[S]` spanned, it would equal the cyclic graph `G`, a contradiction. Since `S` is nonempty and proper and `G` is connected, an edge crosses from `S` to its complement, so a vertex `z` outside `S` adjacent to `S` exists. It already has at least one neighbor in `S`; if it had exactly one, `G[S ∪ {z}]` would be a larger induced tree containing both leaves. Thus `|N(z) ∩ S| ≥ 2`.
- **PASS — extra `z`–`P` edges (`PROOF.md`, lines 39–46).** For distinct `a,b ∈ N(z) ∩ S`, the unique `a`–`b` path `P` in the tree, together with `za` and `zb`, is a simple cycle as a subgraph, of length `|V(P)|+1`. A cycle need not be induced. Extra edges from `z` to internal vertices of `P` create chords/shorter cycles but do not destroy this cycle, so `g(G) ≤ |V(P)|+1` remains valid.
- **PASS — exclusion of the two leaves from `P` (`PROOF.md`, line 48).** Internal vertices of `P` have two distinct path neighbors. Each endpoint has one path neighbor and the distinct outside neighbor `z`. Hence every vertex of `P` has degree at least two in `G`; graph-leaves `x,y` cannot occur on `P`. Therefore `|S| ≥ |V(P)|+2 ≥ g+1`.
- **PASS — triangle boundary (`PROOF.md`, lines 56–68).** At `g=3`, deleting a vertex of a shortest triangle gives a two-vertex induced path and `2(g-1)=g+1=4`; no strict inequality was silently assumed.
- **PASS — meaning of `delta' = 1` (`PROOF.md`, lines 70–74).** Degrees are sorted with multiplicity. In a connected cyclic graph all degrees are positive, so a second-smallest degree of one means that the first two entries are both one, i.e. there are at least two leaves. A graph with exactly one leaf lies in the `delta' ≥ 2` case.
- **PASS — exhaustion of cases.** For a connected cyclic finite simple graph, `delta'` is a positive integer; hence `delta'=1` or `delta'≥2`. The two proof branches cover the entire original domain.
- **PASS — tree case in the current formal statement (`PROOF.md`, lines 78–84).** The current Lean source assumes a nontrivial finite vertex type, connectedness, and positive second-smallest degree, but does not assume cyclicity. Mathlib defines the natural-valued girth of an acyclic graph as zero. For a connected tree, the whole graph is an induced tree, so `t=|V|≥2` and `t delta'≥2≥1=g+1`. This correctly covers the formal extension; the one-vertex graph is excluded by `[Nontrivial α]`.
- **PASS with a requested clarification — sharpness (`PROOF.md`, lines 86–88).** The construction is valid for every integer `g≥3`, whether the two pendants have the same or different supports. At most two cycle vertices are supports, so one can delete a cycle vertex supporting neither pendant; the remaining `g+1` vertices induce a connected acyclic graph. No induced tree can have `g+2` vertices because that would be the full cyclic graph. Thus `t=g+1`, `delta'=1`, and equality holds. Replace “a suitable cycle vertex” by this explicit support argument.

## Computational audit

- **PASS — complete record comparison.** I independently recomputed every connected cyclic graph in NetworkX's graph atlas. All 971 records in `atlas_results.json` agree exactly on atlas index, graph6 string, order, size, sorted degrees, second-smallest degree, girth, maximum induced-tree order, leaf count, and both slack fields. Every listed `tree_witness` is a tree of the claimed maximum order.
- **PASS — aggregate consistency.** The reported counts reconcile: 1253 atlas graphs, 996 connected, 971 connected cyclic, `129+842=971` degree cases, 129 two-leaf cases, 22 main equalities, 21 two-leaf equalities, and no negative slack. The equality lists are exactly the records having zero slack; all 971 atlas indices are unique.
- **PASS — stronger maximality check.** A separate exhaustive subset oracle checked all 199 unordered pairs of leaves occurring in the 129 two-leaf graphs. For every pair, the largest induced tree containing that specific pair had order at least `g+1`; minimum slack was zero and there were no violations. This tests the proof's constrained maximum, not merely the global value `t(G)`.
- **Certificate.** Current SHA-256 of `atlas_results.json` is `FC5F3E8D1AC49BC86C0A779E08A1E1FEAAEA280A294DC4C05699963C1B3BE01B`.
- **Scope note.** The atlas is a falsification test through seven vertices, not part of the proof. It omits trees by design; the acyclic formal extension is discharged directly above.

## Required revisions (original report)

- **Major presentation defect — `PROOF.md`.** All intended LaTeX backslashes are absent. In addition, line 20 contains form-feed `0x0C` from `\frac`, line 34 is split at the `\n` in `\notin`, and line 65 contains two backspaces `0x08` from `\bigl`/`\bigr`. Examples such as `[ ... ]`, `(square)`, `Scup{z}`, and `delta'` are consequently not valid mathematical markup. Rewrite the file with literal Markdown/LaTeX escapes and verify that it contains no control characters other than tab/newline/carriage return.
- **Stale registry — `APPROACH_REGISTRY.md`, lines 11–17.** It still labels the proof “pending” and says no computation has been credited, while `PROOF.md` and `atlas_results.json` now exist. Update the status without changing the direct route or its exit conditions.
- **Artifact links — `PROOF.md`, line 4.** “Independent computation, referee review, and Lean verification are recorded separately” should link the exact artifacts. At the reviewed snapshot there was no Lean file in `problems_external/wowii_143`; do not claim completed Lean verification until such an artifact and a successful build record exist.
- **Sharpness wording — `PROOF.md`, line 88.** State explicitly that the deleted cycle vertex is chosen outside the at-most-two pendant supports.

## Revision check

- **CLOSED — control characters and Markdown mathematics.** `PROOF.md` now has zero disallowed control characters; inline and display mathematics use valid `$...$` and `$$...$$` delimiters, and the formerly corrupted formula passages render as ordinary mathematics.
- **CLOSED — Lean status.** The status now says that the mathematical proof, computation, and referee review are complete while Lean verification is still in progress; it no longer claims completed Lean verification.
- **CLOSED — sharpness support vertex.** The construction now explicitly deletes a cycle vertex supporting neither of the two leaves and explains why one exists for every `g≥3`.
- **CLOSED — registry status.** `APPROACH_REGISTRY.md` now records the executed lemma proof, two exact atlas oracles, three logical reviews, and the remaining Lean/novelty work.

## Priority / novelty risk

- Douglas West's current Graffiti.pc page still states Conjecture 143 with the same definition of the second-smallest degree: <https://dwest.web.illinois.edu/regs/graffiti.html>.
- DeLaVina's current resolved-conjectures page lists nearby induced-tree entries but not Conjecture 143, and page searches for `143` and the formula return no match: <https://cms.dt.uh.edu/faculty/delavinae/research/wowII/resolvedT.htm>.
- The current Formal Conjectures source marks `conjecture143` as `@[category research open]`: <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean>.
- Exact-formula and induced-tree/girth/second-smallest-degree searches found no published proof. This is evidence of unresolved status, not proof of priority. Because the argument is very short, the remaining priority risk is **moderate**: it may be folklore, unpublished, or hidden as an easy consequence in older induced-tree literature. Before making a first-proof claim, search citing literature around Erdős–Saks–Sós, ask West/DeLaVina whether a solution was communicated, and phrase any interim release as a proof of the conjecture “as still listed in the cited sources,” not as an unconditional global priority claim.

## Verdict rationale

I accept the revised proof. No mathematical or editorial revision remains from this referee report; the project should still perform its independently required final novelty gate.
