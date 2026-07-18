# Combined PR packet — WOWII 141 + 143 in a single PR (user directive 2026-07-18)

**⚠ Policy reminder:** FC follows Mathlib's AI policy — the PR/issue text must be
written by you in your own words; AI assistance in the Lean code is disclosed.
Everything below is raw material, not paste-ready prose.

## Branch plan

- Base: `codex/wowii-143-proof` (already on fork: commits `6aab64f` + `eb64455` —
  the 143 resolution + ForMathlib API, full-repo `--wfail` verified).
- New commits on top: 141 supporting lemmas (ForMathlib) + solved
  `GraphConjecture141.lean`.
- Rename/push as **`wowii-141-143-proofs`** for PR clarity (keep the old branch
  name too; both point into the same history).
- The `formal_proof` attributes: 143's already points at `6aab64f`; 141's will
  point at the new proof commit on the same branch.

## Why one PR is coherent (points for your PR body)

- 141's proof **consumes the same reusable API** the 143 work adds to
  `FormalConjecturesForMathlib` (maximum induced tree containing a prescribed
  set, two-neighbour maximality obstruction, tree-path cycle certificates,
  star/leaf-insertion lemmas). Splitting them would duplicate the API diff.
- Both flips are `research open → research solved` on WOWII tree-number
  conjectures with short in-file proofs (repo's preferred shape; CONTRIBUTING
  wants proofs in ForMathlib and ≤25–50-line problem-file proofs).
- Full-repo `lake build --wfail` green at each commit; axiom audits
  (`#print axioms`) = `[propext, Classical.choice, Quot.sound]` for both
  `conjecture143` and `conjecture141` (attach transcripts).

## Mathematical summary (for your own words)

- **143** (t·δ′ ≥ g+1): two-leaf maximal-induced-tree lemma + chordless
  shortest cycle case split. Sharp for every girth.
- **141** (t ≥ ⌊g/2⌋−1+max ℓ(v)): star lemma closes girth ≤5 and acyclic;
  girth ≥6 via the **stronger new theorem t ≥ Δ+g−3 for connected cyclic
  triangle-free G** (maximality argument: maximum induced tree ⊇ N[v] of a
  max-degree vertex; two-neighbour obstruction forces a tree path of length
  ≥ g−2 sharing ≤3 vertices with N[v]). Sharp on all C_g and all K_{a,b};
  conjecture equality cases are exactly girth-4 (atlas-verified).

## Mandatory disclosures in the PR/issue

1. AI assistance (proof search, formalization, verification) per Mathlib policy.
2. **PR #4442 acknowledgment (143):** DomTheDeveloper's earlier (2026-07-16)
   external-bundle claim for 143 — our audit compiled it: valid. Ours is an
   independent proof, in-repo, with the API; maintainers choose how to credit /
   which to merge. Link both; do not claim priority on 143.
3. 141 has no known competing claim (checked registers, FC issues/PRs, and the
   competitor's public fork/site on 2026-07-18: 141/142/144 untouched).
4. Computational falsification checks (995 graphs n≤7 exhaustive + families,
   two independent oracles for 143; FC-def-faithful oracle for 141) — evidence
   only, not used in proofs.

## Verification checklist before the PR (I run these at integration)

- [ ] `lake build --wfail` full repo on the combined branch — zero warnings.
- [ ] `#print axioms` both theorems — exactly the 3 standard axioms.
- [ ] grep sorry/native_decide/axiom in all touched files — zero.
- [ ] Statements byte-identical to upstream (tag+proof-only diffs on both
      problem files).
- [ ] Commits authored as AlperTheKing <alper@mercurycodelab.com>, NO
      Anthropic/Claude trailer.
- [ ] Push branch; record permalink hashes for both formal_proof attributes.

## Open coordination point

Codex is concurrently building a **standalone** 141 proof on clean upstream
(branch `codex/wowii-141-proof`, BFS-parent-graph/broom route). At integration
I take whichever 141 proof is (a) complete and (b) cleaner on the combined
branch — they are mathematically interchangeable; the combined branch keeps
the single-PR shape either way.
