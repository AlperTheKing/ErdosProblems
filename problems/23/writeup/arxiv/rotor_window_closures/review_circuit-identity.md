# Adversarial review — section "Support circuits" (support_circuits.tex)

Reviewer: referee pass, 2026-07-17.
Files reviewed:
- `problems/23/writeup/arxiv/rotor_window_closures/sections/support_circuits.tex`
- `problems/23/writeup/arxiv/rotor_window_closures/sections/support_circuits_claims.md`

Sources opened and compared:
- `problems/23/writeup/WALL_ATTACK_R44_GPTPRO56.md` (§1, §2, gate header)
- `problems/23/writeup/WALL_ATTACK_R50_GPTPRO56.md` (§1–2 exclusion check)
- `problems/23/writeup/arxiv/shortest_support_obstructions/main.tex` (preamble lines 1–14; §2 lines 76–155 incl. lem:minimal 120–155; m≥5 discussion lines 269–275)
- `problems/23/writeup/AGENT_HUNT_ROUND1_PARTIAL.md` (Part (ii) item 1, line 183)

Verifier reruns: the manifest cites no python/anc verifiers (all rows "n/a"/"none"). The one
re-runnable check is the Lean-absence grep: `minimalSupportDeficient_union_card` re-grepped fresh
over `problems/23/lean` on 2026-07-17 — **0 hits (PASS, matches AGENT_HUNT Part (ii) item 1)**.
LaTeX: no TeX engine exists on this machine (pdflatex/tectonic/latexmk absent), so a compile could
not be run; a static structural check was run instead (script in session scratchpad,
`tex_static_check.py` + `label_dup_check.py`): **PASS** — details under "LaTeX" below.

## Per-claim verdicts

### Definition def:circuit + minimality equivalence — CONFIRMED
Matches R44 §1 line 19 ("Inclusion-minimal support-deficient A with proper-Hall subsets").
The one-line equivalence in the text (support circuit ⟺ inclusion-minimal deficient) is exact:
S ⊊ A deficient ⟺ |F(S)| < |S| ⟺ violation of the displayed condition. No strengthening.

### Theorem thm:circuit (i) |F*| = m−1 — CONFIRMED
Proof complete: A∖{a} proper ⟹ Hall ⟹ m−1 ≤ |F(A∖{a})| ≤ |F*| ≤ m−1 (deficiency + integrality).
Matches R44 gate-header pillar (1) verbatim in substance. Correctly stated as paper-proved only;
no Lean status claimed anywhere (verified by fresh grep, see above).

### Theorem thm:circuit (ii) deletion-unions = F* — CONFIRMED
Same displayed equality; F(A∖{a}) ⊆ F* of full finite cardinality ⟹ equal. Complete.

### Theorem thm:circuit (iii) multiplicity ≥ 2 — CONFIRMED
From (ii): f ∈ F_a and f ∈ F(A∖{a}). Complete. (R44's phrasing "an edge in only F_a would make the
deletion-union m−2" is a different but equivalent argument; no mismatch of statement.)

### Theorem thm:circuit (iv) incidence connectivity — CONFIRMED
Complete: every component contains an atom (each f lies in some F_a; singletons proper ⟹ F_a ≠ ∅);
a 2-group split gives nonempty proper A_1, A_2 with disjoint unions covering F*, so
|F*| = |F(A_1)|+|F(A_2)| ≥ m, contradicting (i). Matches R44 "two components would sum Hall to ≥ m".
The m ≥ 2 hypothesis is used exactly where declared.

### Theorem thm:circuit (v) deletion-SDR bijections — CONFIRMED
Complete: every S ⊆ A∖{a} is proper in A ⟹ Hall's condition for the deleted family ⟹ SDR (Hall);
injection into F* with |A∖{a}| = m−1 = |F*| ⟹ bijection. Matches R44 §1 "deleting any atom leaves a
perfect SDR onto all support edges". Hall's theorem is used uncited — consistent with the companion's
house style (companion line 68 also uses "Hall's theorem" bare); acceptable, optionally add Hall 1935.

### Remark rem:intrinsic — CONFIRMED
Matches R44 §1 last line ("If the minimal family is proper ⊂ M: |F*| = |A|−1 (NOT |M|−1)").
Trivial consequence of (i); correctly framed.

### Unnumbered remark (m ≥ 2 degenerate case) — CONFIRMED
The unique m = 1 circuit is indeed A = {a}, F_a = ∅ (deficiency forces |F_a| = 0), and (i),(ii) hold
trivially for it. (In fact (iii)–(v) also hold vacuously/trivially; the remark claims less — safe.)

### Corollary cor:sdr — CONFIRMED
Both directions complete via Hall's theorem; the containment argument (subfamily of a proper
subfamily is proper) and the converse localization of the violation to S = A are airtight.

### Remark rem:matroid — CONFIRMED
The index-side transversal matroid (subfamilies with SDRs = independent sets) is the classical fact,
and Edmonds–Fulkerson, "Transversals and matroid partition", J. Res. Nat. Bur. Standards Sect. B 69B
(1965) 147–153 is the correct and standard citation. cor:sdr ⟹ support circuits = matroid circuits is
exactly the circuit definition (minimal dependent sets). Rank-of-deleted-circuit remark consistent
with (v). Matches R44 §1 "A = a transversal-matroid CIRCUIT".

### Corollary cor:graph (a)–(d) — CONFIRMED
Checked clause-by-clause against companion lem:minimal (main.tex lines 120–134):
(a) = companion (i) (count via thm(i); connectivity fully reproved via incidence connectivity —
a different, complete argument; bipartite from F ⊆ B);
(b) ⊇ companion (ii) — see note N1 below;
(c) = companion (iii), reproved in full: d_F ≤ 4 from a shortest B-path, evenness from same-shore
endpoints in F ⊆ B, d_F = 2 excluded by triangle-freeness with the atom edge, both inclusions of
supp = union of length-4 F-paths argued;
(d) = companion (iv), complete (atoms ⊆ E(G), endpoints in V(F) by (c)).
Hypotheses: B connected stated explicitly (the companion carries it as the §2 ambient assumption,
line 82 "Assume that B is connected") and 𝒜 restricted to distance-4 bad edges explicitly (implicit
in the companion) — no dropped hypotheses, no strengthening. The companion lemma is in the
combinatorial part of that paper (its abstract separates it from the computer-assisted
classification), matching the manifest's "not computer-assisted" note.

### Corollary cor:graph (e) — CONFIRMED
Direct instantiation of thm:circuit(v) with F* = E(F) (E(F) is literally the support union since F
is the spanned subgraph). Matches R44 §1.

### Corollary cor:sizes — CONFIRMED
m ≥ 5: 4 ≤ |supp_B(a)| ≤ |E(F)| = m−1 — matches companion main.tex lines 269–272 ("Every atom
support has at least four edges, so m ≥ 5"). Average multiplicity: Σ_a |supp_B(a)| = Σ_{f∈E(F)} μ(f)
≥ 4m over m−1 edges ⟹ ≥ 4m/(m−1) > 4; the R44 §2 instance (t=4: m=16 ⟹ 64/15) agrees exactly. Complete.

### Excluded claims 1–4 — CONFIRMED
1. R50 |S_ω| ≥ 3t−1 / |L_ω| ≤ t(t−3): verified present in R50 §1–2 with the intrinsic-F* scope
   qualifier (gate header item (2)) and verified ABSENT from the section — only the forward
   pointer sentence appears. See note N3 on its phrasing.
2. R44 §§3–5 (kt+t, 3t+2, crossover) and §8 window structure: absent from the section. Correct.
3. Lean status: no Lean/computer-assistance claim anywhere in the .tex; shell name absent from
   problems/23/lean (fresh grep PASS); AGENT_HUNT Part (ii) item 1 says exactly what the manifest
   says it says. Correct and honestly handled.
4. R44 §2 classification remarks (17/16 K4-subdivision, double-star t=3 uniqueness): absent. Correct.

### LaTeX — CONFIRMED (static; no engine available for a real compile)
- Environments balanced (definition/theorem/proof/remark×3/corollary×3/proof×4 all matched, stack-checked).
- Braces, \[ \], \( \) all balanced; no negative depth.
- Every control sequence used is standard LaTeX/amsmath/amsthm/enumitem or a companion-preamble
  macro (\supp, \bip); enumitem key syntax [label=\textup{(\roman*)}]/[(\alph*)] requires enumitem,
  which the companion preamble loads (main.tex line 3). \mc is named in the header comment but never
  used — harmless, could be dropped from the comment.
- All 10 \ref targets resolve in-file; labels exported match the manifest list exactly.
- No duplicate labels across the six section files of rotor_window_closures.
- \cite{Ferudun26supports}, \cite{EdmondsFulkerson65} pending at assembly, as declared.

## Notes (minor, none blocking)

- **N1 (most serious, cosmetic).** The closing remark says "Corollary cor:graph(a)–(d) is the
  Minimal footprint lemma of [companion]". Not exactly: the second half of (b) — the deletion-union
  clause supp_B(𝒜∖{a}) = E(F) — is NOT in the companion lemma's *statement* (companion (ii) is only
  multiplicity ≥ 2); it occurs only inside the companion's *proof* ("removing any atom leaves the
  whole support union"). So (a)–(d) slightly exceeds the cited lemma. Everything is independently
  proved here, so nothing is wrong mathematically; fix by either moving the deletion-union clause
  into the "additional structure" sentence of the remark or crediting it as statement-level new.
- **N2.** cor:graph invokes Theorem thm:circuit, which is stated with hypothesis m ≥ 2, without
  noting m ≥ 2 (trivial: every support is nonempty since d_B(x,y) = 4, so a deficient family has
  m ≥ 2 — indeed m ≥ 5 by cor:sizes, but that would be circular at this point). One clause,
  e.g. "(supports are nonempty, so m ≥ 2)", closes it.
- **N3.** The forward pointer "Sharper counts are available for selected supports…" mildly asserts
  availability of the R50 bound, whose proof carries the intrinsic-F*/no-extra-active-edge scope
  qualifier. Since no statement or bound is given, this passes as non-claiming, but "are derived in
  later sections" would be strictly safer than "are available".
- **N4.** Hall's theorem is used without a bibliography entry (twice). House-style consistent with
  the companion; optional Hall 1935 key at assembly.

## Summary

All 13 manifest rows CONFIRMED; all four exclusions CONFIRMED; no MISMATCH, no GAP. Every proof
marked "proved" in the manifest is complete (not a sketch). Statements match the archive sources
with no strengthening and no dropped hypotheses; the two additions over the companion ((e),
incidence connectivity, plus the statement-level deletion-union in (b) — see N1) are fully proved
in-text. The section makes no Lean or computer-assistance claim, correctly.
