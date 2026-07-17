# GitHub handoff packet — WOWII / Graffiti.pc Conjecture 143

**⚠ 2026-07-17 UPDATE — competing PR #4442 verified VALID.** DomTheDeveloper's
PR (filed 2026-07-16, one day before our proof) links an off-repo 6-module Lean
bundle. Our adversarial audit COMPILED it against the pinned toolchain: exit 0,
axioms = [propext, Classical.choice, Quot.sound], final theorem term-identical
to the repo statement. Consequences for your prose:
- Do NOT claim first resolution. Frame ours as an independent proof.
- Our PR's differentiators (all true, verifiable): (1) proof lives IN the repo
  (removes the `sorry`; their PR keeps `sorry` + external link); (2) reusable
  `FormalConjecturesForMathlib` API (CONTRIBUTING explicitly wants proofs
  there); (3) short in-file assembly proof, within the repo's 25–50-line rule;
  (4) independently double-compiled + axiom-audited; (5) accompanied by a
  human-readable arXiv exposition (theirs has none).
- Courteous move: comment on / reference #4442 in your issue, acknowledging
  their earlier claim and noting your audit found it valid; let maintainers
  decide whether to merge theirs (tag+link), ours (in-repo proof), or both
  (their priority acknowledgment + our API/proof). Cross-linking both is the
  honest equilibrium.

**⚠ Policy note (why this file exists).** Formal Conjectures follows Mathlib's AI
policy: GitHub issue/PR text must be written by the human contributor in their own
words, and AI assistance in the Lean code must be disclosed. The drafts below are
therefore *content checklists / raw material for you to rewrite*, not text to paste
verbatim. The Lean code itself may be submitted with an AI-assistance disclosure.

---

## Step 1 — Issue (open BEFORE the PR, per CONTRIBUTING §"Contribution process" item 2)

Points the issue should make (rewrite in your own words):

- The file `FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean` marks
  `conjecture143` as `research open`.
- You have a short proof of the conjecture (two-leaf maximal-induced-tree argument
  + shortest-cycle case split) and a complete sorry-free Lean 4 formalization of the
  exact repository statement.
- Priority caveat: West's register and DeLaViña's resolved list still treat 143 as
  open; the closest published result is the DeLaViña–Waller 2004 induced-forest
  bound f(G) ≥ g(G)+f₁(G)−1, which does not imply the tree statement. You are not
  claiming the argument cannot be folklore.
- Ask: (a) is the mathematical proof accepted; (b) does anyone know a prior
  resolution; (c) if OK, you will open a PR flipping the category to
  `research solved` with the supporting API in `FormalConjecturesForMathlib` and a
  short proof in the problem file, plus `formal_proof using formal_conjectures at
  "<fork-branch-URL>"`.
- Attach/link: the arXiv note (once posted) and the fork branch.
- Disclose AI assistance (proof discovery, Lean formalization) per Mathlib policy.

## Step 2 — PR

- Branch: `wowii-143-proof` on `AlperTheKing/formal-conjectures` (pushed by this
  session once the build is green).
- Diff shape:
  - `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/LargestInducedTree.lean`:
    new fully-proved API lemmas (tree extension, geodesic induced trees, maximum
    induced tree containing a prescribed pair, boundary/two-neighbour maximality
    obstruction, cycle-closing girth bounds, the two-leaf bound, ℕ-form of the
    conjecture inequality).
  - `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Degrees.lean`: lemma
    extracting two degree-one vertices from `secondSmallestDegree = 1` in a
    preconnected nontrivial graph.
  - `FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean`: category →
    `research solved`, `formal_proof` attribute, short (≤ ~15 line) proof by cast
    from the ℕ-form lemma. No change to the statement itself.
- PR body content (rewrite in your own words): what is proved, one-paragraph proof
  sketch, note that the statement was NOT modified, axiom audit result
  (`#print axioms conjecture143` = propext, Classical.choice, Quot.sound), AI
  disclosure, link to the issue and to the arXiv note.
- CLA: already required — sign with alper@mercurycodelab.com GitHub identity.
  NO Anthropic/Claude co-author trailer on any commit.

## Step 3 — after merge

- Update the arXiv note's Section 5 URL placeholders if the maintainers want a
  different `formal_proof` URL (e.g., upstream commit instead of fork branch).
- Optionally email DeLaViña / West for the priority check (paper already phrases
  the claim defensively).
