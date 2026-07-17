# Adversarial referee review — section "A star lemma at cut-tight vertices"

Reviewed: `sections/star_lemma.tex` + `sections/star_lemma_claims.md` (manifest)
Date: 2026-07-17. Reviewer: independent referee pass (Claude, adversarial).

Method: every numbered claim checked against (a) the cited Lean sources on disk,
(b) the archive `problems/23/writeup/WALL_ATTACK_R41_GPTPRO56.md`, (c) the companion
preamble `problems/23/writeup/arxiv/shortest_support_obstructions/main.tex`;
every proof in the .tex re-derived line by line; LaTeX checked statically
(no TeX engine is installed on this machine — see Issue 1).

Source-integrity anchor: SHA-256 prefixes of the two cited Gamma modules were
recomputed and match the gate-accepted builds exactly:
- `SingletonPairSigma.lean` = `E4060BCC` (accepted 2026-07-11T21:11Z, rebuild rc=0,
  axiom probes on `sigma_pair_eq_add_singletons_of_nonadjacent` and
  `common_blue_pair_two_le_of_left_loss` = exactly `[propext, Quot.sound]`;
  PROGRESS.md:2972, coordination/CLAUDE_TO_CODEX.md:14542).
- `CutTightStarPigeonhole.lean` = `DD6DA23C` (accepted 2026-07-11T20:44Z, rebuild
  rc=0, `exists_other_with_two_le_loss_sum` axioms
  `[propext, Classical.choice, Quot.sound]`; PROGRESS.md:2967,
  coordination/CLAUDE_TO_CODEX.md:14492).
No `sorry`/`admit`/`axiom` in either module; both end in `#print axioms` probes.
The manifest cites no verifier scripts ("No computer-assisted claims") — confirmed:
the section contains no computational claim, so there was nothing to rerun.

## Per-claim verdicts

### 1. Lemma `lem:switchloss` (Switch identity) — CONFIRMED
- Proof in section is complete: new monochromatic set `(M \ ∂_M S) ∪ ∂_B S`,
  disjoint union, size `|M| + σ(S)`; minimality gives σ(S) ≥ 0. No gap.
- Lean citations exact: `sigmaNonneg_of_badCount_min` (CertGraph.lean:1615)
  proves `∀ S : List Nat, 0 ≤ sigma G c S` from `checkGraph`, `checkCut`, and
  bad-count minimality over all valid cuts — exactly the general-set inequality.
  `singleton_sigma_nonneg_of_isMaxCut` (SingletonPairSigma.lean:159) is the
  vertex case, from `IsMaxCut` (CertGraph.lean:2393 = validity + min_bad over all
  valid side assignments, matching the paper's definition of maximum cut).
- Archive §1 matches ("σ(v) = dB(v) − dM(v) ≥ 0 (maxcut)").
- Note (under-claim, harmless): the exact identity itself also exists in Lean as
  `badCount_flip_eq` (CertGraph.lean:408); the remark cites only nonnegativity.

### 2. Lemma `lem:nonedgeadd` (Additivity on a nonedge) — CONFIRMED
- Proof complete (boundary sets split as disjoint unions; subtract).
- Lean exact match: `sigma_pair_eq_add_singletons_of_nonadjacent`
  (SingletonPairSigma.lean:103), with `dB_pair_eq_add_singletons_of_nonadjacent`
  (:68) and `dM_pair_eq_add_singletons_of_nonadjacent` (:85), for arbitrary
  `CutData` (paper: "any cut" — matches; Lean adds the formalization-level
  `checkGraph = true` well-formedness hypothesis, not a mathematical hypothesis).

### 3. Lemma `lem:starineq` (Star inequality) — CONFIRMED
- Proof complete: N_B(v) independent by triangle-freeness; internal edges of
  S = {v} ∪ N_B(v) are exactly the k crossing star edges (simplicity used and
  stated); degree double count gives |∂_B S| = Σ d_B − 2k, |∂_M S| = Σ d_M;
  identity σ(S) = σ(v) + Σ σ(a) − 2k follows; inequality via lem:switchloss at
  a maximum cut. Re-derived — correct.
- Archive match verbatim (gate header: "loss(S) = σ(v) + Σσ(a) − 2k ≥ 0 ⟹
  Σ σ(a) ≥ 2k − σ(v)"; §§2-3 same).
- Honesty flag verified: grep over all of `problems/23/lean/Erdos23Delta0` finds
  NO Lean formalization of the star identity (only the abstract pigeonhole's
  `2 * neighbours.card` hypothesis) — the "paper-proved only" statement in
  Remark rem:leanstar is accurate in both directions.

### 4. Corollary `cor:badendpoint` — CONFIRMED
- One-line proof valid (σ(v) = dB − dM ≤ 1). Archive §1 matches ("every
  cut-tight active owner is a bad-edge endpoint"; archive's "active" ⟹ k ≥ 2 is
  replaced by the explicit dB(v) ≥ 2 — no strengthening).
- Nit (not a defect): the "at a maximum cut" hypothesis is not needed for
  dM ≥ dB − 1 (it is the definition of cut-tight); harmless extra hypothesis.

### 5. Corollary `cor:losstwoneighbour` — CONFIRMED
- Proof complete: all σ(a) ≤ 1 gives Σ ≤ k ≤ 2k−2 < 2k−1 ≤ Σ for k ≥ 2,
  contradiction. Uses only eq:starineq + σ(v) ≤ 1. Correct.

### 6. Proposition `prop:pairthreshold` (Pair threshold) — CONFIRMED
- Proof complete (triangle-freeness ⟹ nonadjacency; additivity; σ(y) ≥ 0).
- Lean exact match: `nonadjacent_of_common_blue` (:138, TriangleFree, two
  distinct blue neighbours of one owner ⟹ `adjb = false`),
  `two_le_sigma_pair_of_two_le_left` (:114), and the graph-complete combination
  `common_blue_pair_two_le_of_left_loss` (:167, checkGraph + TriangleFree +
  IsMaxCut + distinct blue neighbours + 2 ≤ σ(left) ⟹ 2 ≤ σ(pair)).
  The equality clause of the Proposition is covered by claim 2's Lean theorem.
  No dropped hypotheses, no strengthening.

### 7. Lemma `lem:starpigeon` (Star pigeonhole) — CONFIRMED
- Proof complete and correct: negation gives ℓ ≤ 1 on all of A (via ℓ ≥ 0 and a
  witness y0, which exists since |A| ≥ 2), hence Σ ≤ |A| and 2|A| ≤ 1 + |A|,
  contradiction. (Checked independently; the statement is TRUE as stated,
  including for every x ∈ A.)
- Lean exact match: `exists_other_with_two_le_loss_sum`
  (CutTightStarPigeonhole.lean:18). Manifest's generality caveat verified
  literally: `activeNeighbour : Vertex` is NOT required to be in `neighbours`;
  `loss : Vertex → Nat`; `ownerLoss ≤ 1` (Nat, ≡ s ∈ {0,1});
  `2 ≤ neighbours.card`; conclusion `∃ y ∈ neighbours, y ≠ x ∧ 2 ≤ ℓx + ℓy`.
  The paper statement is the weaker specialization — correctly described.

### 8. Theorem `thm:starlemma` (Star lemma) — CONFIRMED
- Assembly proof complete: pigeonhole with A = N_B(v) (|A| = dB(v) ≥ 2),
  ℓ = σ|_A ≥ 0 (cited), s = σ(v) ∈ {0,1}, hypothesis = eq:starineq;
  nonadjacency by triangle-freeness; equality by lem:nonedgeadd.
- Nano-remark (cosmetic, not a gap): "s = σ(v) ∈ {0,1}" uses σ(v) ≥ 0 from
  Lemma lem:switchloss; the parenthetical citation in that sentence formally
  attaches only to ℓ. The fact is stated in lem:switchloss ("in particular
  σ(v) ≥ 0 for every vertex") three lines up, so no reader can be misled.
- The manifest's status line is exact: the combined graph-level statement is
  NOT a single Lean theorem, and the section says so explicitly.
- Archive relation verified: the paper's unconditional pair statement implies
  the archive's strongProbe-or-detour dichotomy by a case split on n(x,y) for
  the produced y — external to this section, as the manifest says.

### 9. Remark `rem:leanstar` (Formalization) — CONFIRMED
- All five cited Lean names exist, in the named modules, with statements
  matching the described content (details under claims 1, 2, 6, 7).
- The Lean-encoding description (literal edge lists, executable adjacency,
  side-assignment cuts, max cut = monochromatic-count minimizer over all side
  assignments) matches CertGraph.lean definitions (GraphData :15, adjb :33,
  CutData :53, sigma :86, IsMaxCut :2393, TriangleFree :2399).
- Build status: relied on the pinned 2026-07-11 gate evidence (rc=0 rebuilds +
  axiom probes, SHAs matching today's files, see anchor above); a fresh Mathlib
  build was not rerun for this review.

### 10. No-bound remark — CONFIRMED
- Accurate: nothing in the section bounds bip(G); the modesty statement about
  the N²/25 conjecture is correct and matches the companion paper's framing.

### 11. Exclusions list (manifest) — CONFIRMED
- `cutTightActiveStar_strongProbe_or_detour`, `CutTightStarProbeResult`,
  `noPositiveDefectFullyCoveredCutTightStar`: ZERO hits in
  `problems/23/lean` — they are indeed only named shapes in the archive text,
  exactly as the manifest states. Correctly excluded.
- P1 pincer identity, anchored-mass bounds, t=3/N=15/|M|=9 window,
  P(falsifier) ≈ 10%: none appear anywhere in the .tex. Correctly excluded.

### 12. LaTeX / compilability — CONFIRMED (static), with one environment note
- Balanced: 22 \begin/\end pairs match exactly (definition x1, lemma x4,
  corollary x2, proposition x1, theorem x1, remark x2, proof x8, equation x1,
  enumerate x1); \( \) 121/121; \[ \] 8/8.
- All \ref/\eqref targets defined in-file; all \texttt underscores escaped;
  math macros (\mathbb, \eqref, \mathbin{\dot\cup}, \H) covered by
  amsmath/amssymb + standard LaTeX; \bip, the six theorem environments, and the
  enumitem label syntax are all provided by the style-source preamble
  (shortest_support_obstructions/main.tex:3-12).
- NOT verified by an actual compile: no TeX engine (pdflatex/xelatex/lualatex/
  tectonic/miktex/texlive) is installed on this machine. See Issue 1.

## Issues (most serious first)

1. **Compile not executed + missing target preamble** (tooling/packaging, not
   mathematical). No TeX engine exists on this machine, so compilation was
   verified only by static balance/macro analysis. Moreover
   `rotor_window_closures/` has no `main.tex` yet: the section free-rides on a
   preamble (theorem environments, `\bip`, `enumitem`) that exists only in the
   OTHER paper's directory. When the rotor_window_closures wrapper is created,
   it must replicate those definitions or the section will not compile in situ.
2. Nano-remark on thm:starlemma (claim 8): the σ(v) ≥ 0 half of
   "s = σ(v) ∈ {0,1}" could carry its own citation of Lemma lem:switchloss.
   Cosmetic.
3. Nit on cor:badendpoint (claim 4): the maximum-cut hypothesis is unnecessary
   for the first assertion. Harmless as stated.

## Summary
12/12 claims CONFIRMED; 0 MISMATCH; 0 GAP. All proofs marked "proved" in the
manifest are complete (not sketches). Lean citations are exact, hypotheses
intact, no strengthening; the honesty flags (star identity paper-only, no
single Lean theorem for the assembled star lemma) are accurate both ways.
