# Claims manifest — section "Support circuits" (support_circuits.tex)

Paper: rotor_window_closures. Every numbered claim in the section, with verification status and exact sources.

| # | Claim (summary) | Status | Source file(s) | Verifier / SHA |
|---|---|---|---|---|
| Definition (def:circuit) | Support circuit = deficient family with all proper subfamilies Hall; = inclusion-minimal deficient family | definitional (equivalence proved in text, one line) | WALL_ATTACK_R44_GPTPRO56.md §1 ("Inclusion-minimal support-deficient A with proper-Hall subsets") | n/a |
| Theorem (thm:circuit) (i) | \|F*\| = \|A\|−1 for a support circuit | **proved** (full proof in text: proper Hall on A∖{a} gives m−1 ≤ \|F(A∖{a})\| ≤ \|F*\| ≤ m−1) | WALL_ATTACK_R44_GPTPRO56.md §1 + gate header pillar (1) | none — NOT Lean-verified. R44 names the shell `minimalSupportDeficient_union_card` as "Lean-ready"; AGENT_HUNT_ROUND1_PARTIAL.md (Part ii, item 1) grep-verifies it ABSENT from problems/23/lean. Stated as paper-proved only. |
| Theorem (thm:circuit) (ii) | every deletion-union equals F* | **proved** (in text, same displayed equality) | WALL_ATTACK_R44_GPTPRO56.md §1 | none (see above) |
| Theorem (thm:circuit) (iii) | every support element lies in ≥ 2 atom sets | **proved** (in text, from (ii)) | WALL_ATTACK_R44_GPTPRO56.md §1 + gate header ("an edge in only F_a would make the deletion-union m−2") | none |
| Theorem (thm:circuit) (iv) | atom–edge incidence graph connected | **proved** (in text: two components sum Hall to ≥ m, contradicting (i)) | WALL_ATTACK_R44_GPTPRO56.md §1 + gate header ("two components would sum Hall to ≥ m") | none |
| Theorem (thm:circuit) (v) | deletion-SDRs: for every atom a, a bijection A∖{a} → F* with φ(b) ∈ F_b (Hall + cardinality) | **proved** (in text) | WALL_ATTACK_R44_GPTPRO56.md §1 ("deleting any atom leaves a perfect SDR onto all support edges") | none |
| Remark (rem:intrinsic) | identity is \|A\|−1, not ambient \|M\|−1 | **proved** (trivial consequence of (i)) | WALL_ATTACK_R44_GPTPRO56.md §1 last line | n/a |
| Corollary (cor:sdr) | support circuits ⟺ no SDR but every proper subfamily has one | **proved** (full proof in text via Hall's theorem, both directions) | WALL_ATTACK_R44_GPTPRO56.md §1 (transversal-circuit framing) | none |
| Remark (rem:matroid) | = circuits of the transversal matroid induced by the supports; deletion matchings perfect onto F* | **proved** in text modulo the classical fact that SDR-subfamilies form a matroid, cited to Edmonds–Fulkerson 1965 (bib key EdmondsFulkerson65, to add at assembly) | WALL_ATTACK_R44_GPTPRO56.md §1 ("A = a transversal-matroid CIRCUIT") | n/a (classical citation) |
| Corollary (cor:graph) (a)–(d) | graph form: \|E(F)\| = m−1, F connected bipartite; multiplicity ≥ 2 + deletion-unions; d_F = 4 and support = union of length-4 F-geodesics; (V(F), A) triangle-free | **proved** (full proofs in text; (a),(b) instantiate the Theorem, (c),(d) reproved following the companion) | companion paper main.tex, Lemma "Minimal footprint" (lem:minimal), problems/23/writeup/arxiv/shortest_support_obstructions/main.tex lines 120–155; Theorem thm:circuit | n/a — companion lemma is combinatorial (not computer-assisted) |
| Corollary (cor:graph) (e) | graph deletion-SDR onto E(F) | **proved** (instantiates Theorem (v)) | WALL_ATTACK_R44_GPTPRO56.md §1 | none |
| Corollary (cor:sizes) | m ≥ 5; average edge multiplicity ≥ 4m/(m−1) > 4 | **proved** (one-line proof in text) | companion main.tex ("Every atom support has at least four edges, so m ≥ 5", lines 270–272); WALL_ATTACK_R44_GPTPRO56.md §2 (the t=4 instance "avg edge multiplicity ≥ 64/15") | n/a |

## Excluded claims (and why)

1. **R50 selected-support lower bound \|S_ω\| ≥ 3t−1 and latent budget \|L_ω\| ≤ t(t−3)** (WALL_ATTACK_R50_GPTPRO56.md §1–2): depends on the owner-profile definitions (owners, rows v−y−p−q−b, selections ω) — deferred to the owner-profile section per the drafting instruction ("put it in the later section if cleaner"). Also carries R50's explicit intrinsic-F*/production scope qualifier, so it must be stated with the no-extra-active-edge hypothesis wherever it lands. Only a non-claiming forward pointer ("treated in later sections") appears in this section.
2. **R44 §§3–5 shape-independent bounds (kt+t, 3t+2, crossover table) and §8 (t,k)=(4,2) window structure**: owner/profile-dependent; belong to the window sections, not to the abstract circuit section.
3. **Any Lean-verified status**: R44 marks §1 "Lean-ready" and names `minimalSupportDeficient_union_card`, but AGENT_HUNT_ROUND1_PARTIAL.md (grep audit of problems/23/lean) lists it as MISSING compile debt. No Lean claim is made anywhere in the section; all statuses are paper-proved with complete elementary proofs included.
4. **R44 §2 classification remarks at general t** (17/16 bipartite K4-subdivision circuit, double-star uniqueness to t=3): not needed for the identity; the double-star computation belongs with the window analysis.

## Notes for assembly

- Bib keys needed: `Ferudun26supports` (companion paper), `EdmondsFulkerson65` (Transversals and matroid partition, J. Res. NBS 69B (1965) 147–153).
- Environments/macros assumed from companion preamble: theorem/corollary/definition/remark numbered by section; `\supp`, `\bip`; `enumitem`.
- Labels exported: sec:support-circuits, def:circuit, thm:circuit, rem:intrinsic, cor:sdr, rem:matroid, cor:graph, cor:sizes. Later sections should cite thm:circuit(v) for deletion-SDRs and cor:graph for the graph form.
