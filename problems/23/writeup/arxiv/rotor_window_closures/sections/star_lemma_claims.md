# Claims manifest — section "A star lemma at cut-tight vertices" (star_lemma.tex)

Section file: `problems/23/writeup/arxiv/rotor_window_closures/sections/star_lemma.tex`

Sources read for this section (all claims trace to these files only):
- `problems/23/writeup/WALL_ATTACK_R41_GPTPRO56.md` (sections 1-3 and the gate header)
- `problems/23/lean/Erdos23Delta0/Gamma/SingletonPairSigma.lean`
- `problems/23/lean/Erdos23Delta0/Gamma/CutTightStarPigeonhole.lean`
- `problems/23/lean/Erdos23Delta0/CertGraph.lean` (definitions `sigma`, `dB`, `dM`, `IsMaxCut`, `TriangleFree`; theorem `sigmaNonneg_of_badCount_min`) — read to state the formalization remark honestly
- Style/notation source: `problems/23/writeup/arxiv/shortest_support_obstructions/main.tex`

No computer-assisted claims in this section (no verifier scripts, no SHAs needed).

## Numbered claims

### Lemma `lem:switchloss` (Switch identity)
- Statement: switching S changes |M| by exactly sigma(S) = |boundary_B(S)| - |boundary_M(S)|; hence sigma(S) >= 0 for all S at a maximum cut.
- Status: proved (full one-paragraph proof in section).
- Lean: general-set form `sigmaNonneg_of_badCount_min` (`Erdos23Delta0/CertGraph.lean`, from bad-count minimality over all side assignments); singleton corollary `singleton_sigma_nonneg_of_isMaxCut` (`Erdos23Delta0/Gamma/SingletonPairSigma.lean`).
- Archive source: WALL_ATTACK_R41 section 1 ("sigma(v) = dB(v) - dM(v) >= 0 (maxcut)").

### Lemma `lem:nonedgeadd` (Additivity on a nonedge)
- Statement: x != y nonadjacent => sigma({x,y}) = sigma(x) + sigma(y) (any cut).
- Status: proved (proof in section) AND Lean-verified: `sigma_pair_eq_add_singletons_of_nonadjacent`, with `dB_pair_eq_add_singletons_of_nonadjacent` and `dM_pair_eq_add_singletons_of_nonadjacent` (`Erdos23Delta0/Gamma/SingletonPairSigma.lean`).

### Lemma `lem:starineq` (Star inequality)
- Statement: triangle-free, S = {v} u N_B(v): sigma(S) = sigma(v) + sum_{a in N_B(v)} sigma(a) - 2*dB(v); at a maximum cut sum sigma(a) >= 2 dB(v) - sigma(v).
- Status: proved (full proof in section: N_B(v) independent by triangle-freeness, internal edges = the k crossing star edges, degree double count). NOT formalized in the named Lean modules — stated as such in the Formalization remark.
- Archive source: WALL_ATTACK_R41 sections 2-3 + gate header ("VERIFIED BY INSPECTION: ... loss(S) = sigma(v) + sum sigma(a) - 2k >= 0").

### Corollary `cor:badendpoint`
- Statement: cut-tight => dM(v) >= dB(v) - 1; cut-tight with dB(v) >= 2 => v is a monochromatic-edge endpoint.
- Status: proved (one-line proof in section).
- Archive source: WALL_ATTACK_R41 section 1 ("every cut-tight active owner is a bad-edge endpoint").

### Corollary `cor:losstwoneighbour`
- Statement: maximum cut, triangle-free, cut-tight v with dB(v) >= 2 => some a in N_B(v) has sigma(a) >= 2.
- Status: proved (immediate from `lem:starineq`; proof in section).
- Archive source: immediate consequence of WALL_ATTACK_R41 sections 2-3 star bound (sum >= 2k-1).

### Proposition `prop:pairthreshold` (Pair threshold)
- Statement: maximum cut, triangle-free; x,y distinct crossing neighbours of a common vertex, sigma(x) >= 2 => xy not an edge and sigma({x,y}) >= 2.
- Status: proved (proof in section) AND Lean-verified: `nonadjacent_of_common_blue`, `two_le_sigma_pair_of_two_le_left`, `common_blue_pair_two_le_of_left_loss` (`Erdos23Delta0/Gamma/SingletonPairSigma.lean`).

### Lemma `lem:starpigeon` (Star pigeonhole, abstract)
- Statement: |A| >= 2, loss ell : A -> Z_{>=0}, s in {0,1}, 2|A| <= s + sum ell => for every x in A there is y in A\{x} with ell(x)+ell(y) >= 2.
- Status: proved (proof in section) AND Lean-verified: `exists_other_with_two_le_loss_sum` (`Erdos23Delta0/Gamma/CutTightStarPigeonhole.lean`); the Lean form is slightly more general (the prescribed element need not lie in A; losses in Nat, tightness s <= 1).

### Theorem `thm:starlemma` (Star lemma at cut-tight vertices)
- Statement: triangle-free, maximum cut, cut-tight v with dB(v) >= 2: for every x in N_B(v) there is y in N_B(v)\{x} with xy not an edge and sigma({x,y}) = sigma(x)+sigma(y) >= 2.
- Status: proved (proof in section = lem:switchloss + lem:nonedgeadd + lem:starineq + lem:starpigeon). The combined graph-level statement is NOT a single Lean theorem; the Formalization remark says exactly which pieces are machine-checked (arithmetic core + pair manipulations) and that the star identity step is paper-only.
- Archive source: WALL_ATTACK_R41 sections 2-3 ("THE STAR THEOREM"), stripped of the Hall/detour branch (see exclusions).

## Excluded claims (present in the archive, deliberately NOT in the section)

1. `cutTightActiveStar_strongProbe_or_detour` / `CutTightStarProbeResult` (strong-probe-OR-two-edge-detour dichotomy, "covered pair" branch, n(x,y) machinery): the archive names these only as Lean SHAPES/targets; no compiled source for the packaged graph-level theorem was among my sources, and the detour branch depends on the Hall/row system. The section keeps only the clean unconditional pair statement (thm:starlemma), which implies the archive dichotomy by a case split external to this section.
2. `noPositiveDefectFullyCoveredCutTightStar` (WALL_ATTACK_R41 section 8): explicitly an OPEN invariant. Excluded.
3. P1 pincer identity D_v - P1_v = 10r(v) - 2N + deg_I(v) and its shore form (section 5): engine bookkeeping, outside this section's scope. Excluded.
4. Anchored mass bounds r(v) >= t, c(v) <= 1+4r(v), C_v >= t-1, P3 floor (section 4): depend on anchored-row machinery. Excluded.
5. The t=3 / N=15 / |M|=9 falsifier window and its realization constraints (sections 6-7): conjectural target, unverified. Excluded.
6. Probability estimates P(falsifier) ~ 10% (section 9): not a mathematical claim. Excluded.
