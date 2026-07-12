# REFORM_SWEEP_ROUND1 — CDC-style formulation sweep on Erdős #23 (triangle-free β ≤ N²/25)

**Round-1 registry/synthesis, 2026-07-12.**
Inputs: 3 independent formulation agents (`flag-sdp-free`, `lp-tension`, `semidefinite-rounding`) + 3 adversarial audits (`tmp\agent_reform\audit_0/1/2`). Every quantitative claim below is an audit-confirmed exact-arithmetic fact: author code was rerun verbatim AND independently reimplemented in each lane; zero numeric discrepancies survived. This document is the round-1 verdict of record and the round-2 tasking order. Orthogonal to the main Γ/Hall transfer-matching lane and its DEAD list (audit_0 item 13); nothing here alters the statement of record there.

---

## 0. Meta-result (read first)

All three formulations, built independently, converged onto the SAME reduction skeleton and then renamed the same residual problem:

| Step | A (pentagons) | B (LP/F2) | C (GW energy) | Status |
|---|---|---|---|---|
| Peel: WLOG δ > (4N−2)/25 | step 1 | Reduction 1 | T4 | proved ×3, elementary |
| Dense branch: δ > 3N/8 ⟹ hom-C5 ⟹ β ≤ (N/5)² | step 2 | Reduction 2 | T3 (+AES) | Häggkvist 1982 + AM-GM, proved ×3 |
| Residual "one missing lemma" | APS(κ) | W′ | ML | = the window problem, renamed |

**WINDOW PROBLEM (reformulation of record for this sweep):** triangle-free G on N vertices, (4N−2)/25 < δ(G) ≤ 3N/8, G not homomorphic to C5 ⟹ β(G) ≤ N²/25.

Each route's missing lemma is at least as strong as the window problem (A: strictly stronger; B: strictly stronger AND verbatim identical to the bare conjecture on a large graph class; C: ε=0 form equivalent, ε>0 form strictly stronger). **Net logical strength removed by round 1: zero.** Net value: several new proved inequalities, one universal forcing point (C13(1,5)), six exact dead-end calibrations, one certificate-search tool, and a unified falsification program (§4.1).

**Cross-audit reconciliation (binding):** Jin 1995 (δ ≥ 10N/29) does NOT supply hom-C5 — And(4) = C11(1,4) has δ/N = 4/11 > 10/29 and admits 0 homomorphisms to C5 (exhaustive, audit_2); Jin buys only 3-chromaticity, which feeds no route (3-coloring gives β ≤ e/3 ≤ N²/12 ≫ N²/25). audit_0's endorsement of the Jin parenthetical is overridden by audit_2's exhaustive datum. Häggkvist's 3/8 is sharp at And(3) = V8 (δ = 3N/8 exactly, not hom-C5). Window ceiling stands at 3N/8 pending §5 R2-WINDOW.

---

## 1. Approach-family registry (grouped by mathematical idea)

### Family A — Pentagon supersaturation ("pivotal pentagons", agent flag-sdp-free)
- **Idea:** for a mono edge uv of a cut, count anchored pentagons through uv whose flanking edges are cross; triangle-freeness makes the count the clean trace formula R(cut) = ½·tr(M·C·A²·C) and the config→pentagon map injective.
- **Proved new:** Prop A: R(cut) ≤ #C5(G) for every cut of every triangle-free G (elementary double count; ~10¹⁰ cuts machine-checked, 0 violations). At-most-one-pivot parity lemma. Blow-up transfer β(G[t]) = t²β(G) and R_best(G[t]) ≥ t⁵·R_best(G) ⟹ **blow-ups can never force a larger κ than their base** (audit_0 small theorem — closes the "C13 orbit via blow-ups" threat; Z₂₆ Cayley closed exhaustively).
- **Cap (named):** #C5 ≤ (N/5)⁵ (Grzesik 2012; Hatami–Hladký–Kráľ–Norine–Razborov 2013; exact-for-all-N extremal value is Lidický–Pfender 2018). **The cap's only known proofs are flag-algebra/SDP — the route's "flag-algebra-free" label is FALSE for the pipeline** and a first-class Lean-debt item.
- **Missing lemma APS(κ):** in-window, R_best ≥ (N/5)⁵ + κ·(β − N²/25)·(N/5)³. Strictly implies the full conjecture (no partial credit). Forced κ ≥ 215043/41743 ≈ 5.1516 by C13(1,5) (N=13, β=6, #C5=52, R_best=50 over ALL 4096 cuts, x = 150/169, not hom-C5 — confirmed twice independently). κ=6 survives audit_0's extended scan (all in-window triangle-free circulants 15 ≤ N ≤ 26 with ALL difference sets + blow-ups + randoms; 1201 graphs) with ≈16% margin; the global worst point is exactly the C13(1,5) iso/blow-up orbit.
- **Structural weakness (audit_0 item 12):** APS must be tight at (1,1) where Prop A and the cap are simultaneously tight ⟹ stability-grade at C5[t]; the natural proof is circular (presupposes the extremal theorem); exact decomposition at C13(1,5): 1−y = 0.579 = 0.562 pentagon-count deficit + 0.017 anchoring deficit ⟹ **APS is ≈97% pentagon-count stability** (spin-out A′, §3).
- **Data desert:** the strip 150/169 < x < 1 contains exactly ONE census point in the entire combined evidence base (C5[4,4,4,4,5], slope 0.22). κ=6 is a linear extrapolation into unprobed territory.
- **Hygiene corrections of record (audit_0 item 8):** shipped all-cut exhaustion is N ≤ 14 (not 16); the N=18 circulant scan used |D| ≤ 2 (not 3); "hill-climb found nothing above 1.99" was n = 12–14 with restricted cut sets — NOT a near-x=1 statement.
- **Artifacts:** `tmp\agent_reform\density_flagfree\{battery.py,hunt.py,hunt_best.json}`; audit: `tmp\agent_reform\audit_0\{audit_verify.py,gen_graphs.py,scan.cpp,scan_out.txt,postprocess.py,battery_rerun.log}`.

### Family B — Polyhedral / F2-certificate cuts (agent lp-tension)
- **Idea:** upper bounds on β need inner certificates = explicit cut families; take F(G) = im_F2(A) ∪ im_F2(A+I) (XORs of open/closed neighborhoods; contains every N(u); contains the optimal cut of every C5-blow-up).
- **Proved new:** ν* ≤ min(e/5, β); the direction β ≤ ν* FALSIFIED exactly (C13(1,5): 6 > 26/5; C17(1,4): 8 > 34/5) ⟹ no multiplicative integrality-gap theorem β ≤ ρν* can reach the sharp constant (ρ = 1 forced at C5[t], ρ ≥ 30/26 at C13(1,5)); LP tight at the extremal (9 edge-disjoint C5s partition E(C5[3])); Petersen ν* = 3 = β with max integral packing 2; payoff table M(d) = (5,1,3,3,1) with uncut(T_j) = e(V_{j+3},V_{j+4}) verified on 300 non-complete hom-C5 graphs (audit_1 strengthening); exact β(HoffmanSingleton) = 50 via the sandwich (A−2I)(A+3I) = J (audit_1, new).
- **Missing lemma W′:** every triangle-free non-bipartite G has S ∈ F(G) with uncut_G(S) ≤ N²/25.
- **Fatal degeneracy (audit_1, decisive):** if A or A+I is F2-invertible then F(G) = 2^V and W′ is VERBATIM the bare conjecture — generic (≈50% of random TF non-bip graphs; ≈30% in-window; 29/48 battery rows; **100% of the n = 5,6 "exhaustive evidence" was degenerate**, n = 7 only 12,222/26,232 informative). W′ is also strictly STRONGER than the conjecture (fam > β occurs). The proposed SRG hunting grounds (Gewirtz 56 / M22 77 / Higman–Sims 100) are REFUTED as tests: k, μ both even ⟹ (A+I)² = I ⟹ degenerate a priori; they could only falsify Erdős itself at n ≤ 100, excluded by the project's exact certificates (valid N ≤ 200).
- **Salvage:** F(G) is a fast exact certificate/prefilter tool on singular graphs (`lib.py:min_uncut_union_family`, practical to rank ≈ 22); repair direction = bounded-XOR family (spin-out B′, §3); informative hunting grounds = both-singular graphs (μ-odd algebraic: HoSi ranks 22/29, Petersen 6/5, Grötzsch 10/6, GP(n,k), Mycielski towers).
- **Artifacts:** `tmp\agent_reform\lp_polyhedral\{lib.py,battery.py,exhaustive567.py,probe_petersen.py,probe_fam_vs_beta.py}`; audit: `tmp\agent_reform\audit_1\{a_core.py,b_hosi.py,c_hunt.py,out_*.log,rerun_*.log}`.

### Family C — Continuous embeddings / GW uncut energy (agent semidefinite-rounding)
- **Idea:** β(G) = min over circle embeddings of U_G(f) = Σ_E (1 − θ_e/π) (T1, exact in both directions; higher spheres give nothing more); odd-cycle deficit law Σ_{e∈C} d_e ≥ π (T2, winding parity); conjecture ⟺ existence of a sub-budget embedding.
- **Proved new:** T1/T2/T5 (β(H[t]) = t²β(H), twin-free brute-force confirmed); T3 equality characterization (balanced complete C5 blow-up); TWO airtight negative calibrations: (i) the maxcut-SDP-optimal embedding of Petersen has U ≈ 4.0158 > 4 = N²/25 while β = 3, with SDP-optimum UNIQUENESS certified over Q (audit_2 closure: optimal face forced into E₋₂, rank(X*∘X*) = 10, det ≠ 0) ⟹ **GW rounding of the SDP optimum cannot prove the conjecture even on Petersen**; (ii) exact ±1/25 overdraft ledger along the C5[t] insertion chain ⟹ no single embedding style survives per-step induction against the N²/25 potential (other potentials NOT excluded — audit_2 flagged the "must morph" inference as an overclaim).
- **Missing lemma ML:** windowed non-hom-C5 ⟹ β ≤ (1−ε)N²/25. The ε=0 form is EQUIVALENT to the window problem (by T1's own exactness the GW language cannot reduce its strength); the ε>0 form is strictly stronger (second-extremal-gap assertion, could be false with the conjecture true). The proposed median-antipode/majorization attack is dead-pattern unquantified-stability handwave (audit_2: the majorization claim is not even well-formed; at a true minimizer the deficit profile majorizes the flat pentagram profile, not the reverse).
- **Threat scan (exact, blow-up-transferable by T5, all asserted non-hom-C5):** max known window ratio 25β/N² = 100/121 ≈ 0.826 (And(4) and Grötzsch); And(3) 25/32; And(6) 225/289; And(5) 75/98; Petersen 3/4; μ₃(C5) 125/256. Coverage thin (7 base graphs); Vega graphs = correct next target.
- **Artifacts:** `tmp\agent_reform\gw_geometric\{verify_all.py,petersen_spectral_exact.py,insertion_chain_exact.py}`; audit: `tmp\agent_reform\audit_2\audit_independent.py` (68/68 PASS, exit 0).

### Shared skeleton S — window reduction (all three agents, independently)
Peel telescope ((N−1)² + 2N − 1 = N² exact; base cases machine-enumerated), Häggkvist dense branch, GM-dual/AM-GM chain, β(C5[a]) = min aᵢaᵢ₊₁ (only the ≤ direction load-bearing). Proved, classical-strength, triple-verified. This is the only unconditionally banked reduction of the sweep.

---

## 2. Status verdicts

| Family | Status | Named gap | Salvage |
|---|---|---|---|
| A — pentagon supersaturation | **BLOCKED — THEOREM-STRENGTH-GAP(APS(κ))** | APS strictly implies the conjecture; stability-grade at (1,1); data desert in (150/169, 1) | spin-out A′ ALIVE (§3); hunt program (§4.1); Prop A + κ-forcing point banked |
| B — F2-certificate cuts | **BLOCKED — THEOREM-STRENGTH-GAP(W′) + degeneracy** | W′ verbatim = bare conjecture on the F2-nonsingular class; strictly stronger overall | spin-out B′ ALIVE (§3); F(G) salvaged as exact prefilter tool |
| C — GW uncut energy | **BLOCKED — THEOREM-STRENGTH-GAP(ML)** | ML(ε=0) ≡ window problem; ML(ε>0) strictly stronger; attack paragraph dead-pattern | two negative calibrations banked; falsification folded into §4.1 |
| S — window reduction | **PROVED (classical strength)** | — | reformulation of record |

REFUTED sub-claims → DEAD list, §6. No family is REFUTED outright; **no family is ALIVE at full-route level** — the requested "two most promising ALIVE families" are therefore the two spin-outs below, the only round-1 objects with both content and a non-theorem-strength target.

---

## 3. The two most promising ALIVE spin-outs (exact next lemmas)

### A′ — Pentagon-count stability: LEMMA PC(C, d₀)   [from Family A; ≈97% of APS by the exact C13 decomposition]
> **PC:** There exist C < ∞ and d₀ > 0 such that every triangle-free G on N vertices with δ(G) > (4N−2)/25 and β(G) ≥ (1−d)·N²/25 for some 0 ≤ d ≤ d₀ satisfies #C5(G) ≥ (1−Cd)·(N/5)⁵.

- **Why this one:** strictly WEAKER than the conjecture — at d = 0 it asserts a near-cap pentagon count, which does not contradict the cap, so a proof of PC does not secretly contain the target and a refutation does not kill Erdős. It is the ONLY lemma produced in round 1 with that property; every other "missing lemma" is conjecture-strength or stronger.
- **Attack order:** (i) literature-first — stability forms of the pentagon-density theorem (HHKNR uniqueness of C5[t] maximizers, Lidický–Pfender exactness, adjacent C5-supersaturation results); (ii) direct proof with the audit's circularity guard (must not presuppose the β-extremal theorem); (iii) refutation = a windowed family with β near N²/25 and #C5 bounded away from the cap — the SAME hunt as §4.1.
- **Scope guard:** closing APS afterwards additionally requires quantifying the anchoring-efficiency term (the 0.017 component at C13(1,5)) — flagged now to prevent silent scope creep in round 2.

### B′ — Bounded-XOR certificate family: LEMMA W′-k   [from Family B; the degeneracy-proof repair]
> **W′-k:** There is a fixed k (target: k ≤ 3) such that every triangle-free non-bipartite G in the window has S = symmetric difference of at most k open-or-closed neighborhoods with uncut_G(S) ≤ N²/25.

- **Why this one:** non-degenerate by construction — |F_k(G)| ≤ (2N)^k ≪ 2^N for fixed k, so W′-k can never collapse to the bare conjecture; structural content survives on every graph, and certificate search is polynomial.
- **First computation decides viability cheaply:** the minimal-k curve across the 48-graph battery + the informative (both-singular) part of exhaustive n ≤ 8 + both-singular randoms. Per audit_1, the old exhaustive evidence does NOT transfer and must be redone under F_k. If min-k grows with N ⟹ kill; if k ≤ 3 uniformly ⟹ promote W′-k to a named finite-structure target.
- **Known anchors:** C5-blow-up optimum = a single open neighborhood (k = 1); all 5 optimal Petersen cuts lie in im(A+I) — the minimal closed-neighborhood XOR count realizing one of them is the first number to compute.

(The unified near-extremal hunt of §4.1 is the strongest ALIVE *program* of round 1, but it is a falsification battery, not a lemma; it is tasked separately.)

---

## 4. Cross-pollination now justified

### 4.1 UNIFIED NEAR-EXTREMAL HUNT (A × B × C — one compute program, four kill conditions)
The APS desert-strip probe (x ∈ (0.85, 1), non-blow-up), the ML ratio hunt (25β/N² → 1), and the PC refutation hunt are the SAME search. Compose with Family B's tool: **F(G)/F_k(G) enumeration is a fast exact PREFILTER** — any F2-image cut with uncut under threshold discards the graph as a non-threat before exact maxcut is ever attempted; exact β only on survivors; slope y = 3125·R_best/N⁵ where size allows (all-cut exact to N ≤ 14 with shipped code, N ≤ 26 with audit_0's C++; max-cut-restricted beyond).
Targets — none scanned by any round-1 agent or auditor: Brandt–Thomassé **Vega graphs**; **Z_{13k} Cayley, k ≥ 3, |D| ≥ 3** (k = 2 closed exhaustively by audit_0); scaling of the **C21(1,4,6) family** (slope 4.734, the only known non-C13 point above 4); dense non-hom-C5 constructions near δ ≈ N/3 (hom-threshold literature); local edge-perturbations of the C13(1,5) orbit; both-singular window graphs (feeds B′ simultaneously).
**Kill conditions wired as asserts:** slope > 6 kills κ = 6; slope unbounded as x → 1 kills APS-linear (fallback = curved form through (1,1)); 25β/N² → 1 on a windowed non-hom-C5 family kills ML(ε); windowed β > N²/25 = **counterexample to Erdős #23** (instant global priority, escalate immediately).

### 4.2 Window-shrink via Γ_d interval-cut minimax (B.Reduction-2 × C.T3 × hom-threshold literature)
The pentagonal interval-cut LP (payoff table (5,1,3,3,1) + GM dual) and C's T3 are the same object. Extending it from C5 to Andrásfai targets Γ_d is a FINITE weighted-blowup minimax per d: compute exactly max over weight vectors a of 25·β(Γ_d[a])/(Σa)² from Γ_d's cut structure. Every d with max ≤ 1 lowers the window ceiling below 3N/8 (via the matching hom theorem) for EVERY route simultaneously; a weighting exceeding 1 kills the shrink for that d — a clean finite verdict either way. Balanced anchors already exact: And(3) 25/32, And(4) 100/121, And(5) 75/98, And(6) 225/289 — all < 1; the unbalanced minimax is the open half.

### 4.3 C13(1,5) fixture export
C13(1,5) is round 1's universal forcing point: kills β ≤ ν*, forces κ ≥ 215043/41743, worst slope in every scan, F2-degenerate for W′, below both hom thresholds. Export as a standing fixture to the project battery (13 vertices — cheap on every checker; main-lane orthogonality confirmed, no DEAD-list collision).

### Hygiene mandate (binding for round 2, from audit_1)
Exact int/Fraction arithmetic only; **every claimed number must have a saved log or it does not exist**; the scope of every scan (N range, |D| cap, all-cut vs restricted-cut) must be stated in the report body. Round 1 had three scope overstatements caught only by audit.

---

## 5. Round-2 agent assignments

| Agent | Task | Deliverable | Kill / success criterion |
|---|---|---|---|
| **R2-HUNT** (compute, ≤64T) | §4.1 unified hunt: construct Vega graphs from Brandt–Thomassé definitions (literature-careful), Z_{13k} k ≥ 3, C21(1,4,6) scaling, δ ≈ N/3 dense constructions, C13-orbit perturbations; F_k prefilter; exact β on survivors; y where computable | table (graph6, N, δ, β, x, y, certificate) + saved logs | any §4.1 kill condition fires; else the desert strip gains a real census and κ = 6 / PC / ML(ε) get their first genuine near-x=1 evidence |
| **R2-PC** (math) | Lemma PC: literature sweep (pentagon-theorem stability, HHKNR/Lidický–Pfender, C5 supersaturation), then prove-or-refute under the circularity guard | proof sketch with named tools, or a refuting-family spec handed to R2-HUNT | PC proved ⟹ APS reduces to the anchoring term (0.017-scale); PC refuted ⟹ Family A dead at linear form |
| **R2-WK** (mixed) | Lemma W′-k: implement F_k enumeration; minimal-k curve over the 48-graph battery + informative exhaustive n ≤ 8 + both-singular randoms; Petersen closed-XOR count first | min-k table + formal W′-k statement if bounded | min-k grows with N ⟹ kill B′; k ≤ 3 uniform ⟹ named target promoted |
| **R2-WINDOW** (math/compute) | §4.2 Γ_d interval-cut minimax, exact, for d = 3 (V8) and d = 4 (C11(1,4)) | exact max-weighting value per d | ≤ 1 ⟹ ceiling drops with the matching hom theorem; > 1 ⟹ shrink dead for that d |
| **Registry** (this agent) | round-2 gate: same synthesis discipline; enforce the hygiene mandate | REFORM_SWEEP_ROUND2.md | — |

**Lean-debt ledger (ALL-OR-NOTHING rule — must accompany any "math success" claim):** Häggkvist 1982 (all routes; no Lean/Mathlib formalization exists), Andrásfai–Erdős–Sós (C), Grzesik/HHKNR/Lidický–Pfender flag-SDP certificates (A only — heaviest: rational-SDP flag-certificate verification from scratch). Any route through these named theorems inherits this debt before it can feed the FC PR.

---

## 6. DEAD list additions (do not re-derive)

1. **β ≤ ν*** (fractional odd-cycle cover as an upper bound) — exact CEs C13(1,5) (6 > 26/5) and C17(1,4) (8 > 34/5).
2. **Any multiplicative integrality-gap route β ≤ ρν*** for the sharp constant — ρ = 1 forced at C5[t] vs ρ ≥ 30/26 at C13(1,5).
3. **GW rounding of the maxcut-SDP optimum** — Petersen U ≈ 4.0158 > 4 with the SDP optimum unique (certified over Q).
4. **Single-embedding-style insertion induction** against the N²/25 potential — exact ±1/25 ledger (cut and pentagram styles both excluded; other potentials not excluded).
5. **im(A) alone as a certificate family** — Petersen min 6 > 4.
6. **Gewirtz / M22 / Higman–Sims as W′ falsification grounds** — parity-degenerate (k, μ even ⟹ (A+I)² = I ⟹ F(G) = 2^V).
7. **Jin 10/29 as a hom-C5 supplier** — And(4) exhaustive CE; Jin gives 3-chromaticity only.
8. **"Flag-algebra-free" labeling of the pentagon route** — the cap's only known proofs are flag-algebraic/SDP.
9. Standing project DEAD list (spectral two-lane, bare SSE, deficit/fixed-cut atoms, …) untouched and non-colliding.

---

## Appendix — banked assets of round 1

**Proved:** Prop A (R(cut) ≤ #C5, triangle-free); one-pivot parity; β(G[t]) = t²β(G) (T5) and R_best(G[t]) ≥ t⁵R_best(G) (blow-ups never worsen κ); ν* ≤ min(e/5, β); the 9-C5 edge-partition of C5[3] (LP tight at extremal); exact β(HoffmanSingleton) = 50; payoff table (5,1,3,3,1) + GM-dual chain; T1 exactness + T2 odd-cycle deficit law; Petersen SDP-uniqueness certification chain; SRG parity-degeneracy lemma; F2-degeneracy classification (A or A+I invertible ⟹ F(G) = 2^V).
**Forcing point:** C13(1,5): N = 13, δ = 4, β = 6, #C5 = 52, R_best = 50 (all cuts), x = 150/169, κ-forced = 215043/41743, not hom-C5, F2-degenerate, below both hom thresholds; deficit split 0.562 pentagon-count + 0.017 anchoring.
**Code (all exact, all audit-rerun):** `tmp\agent_reform\density_flagfree\`, `tmp\agent_reform\lp_polyhedral\`, `tmp\agent_reform\gw_geometric\`, audits `tmp\agent_reform\audit_0\`, `audit_1\`, `audit_2\` (all paths relative to `E:\Projects\ErdosProblems\`).
