# Q11 — Attack on CF (fresh GPT session): ANSWER + Step-2 AUDIT (2026-06-20)

User-relayed GPT Pro answer to the self-contained CF question (fresh session, chat c/6a368eab).
**Verdict: SOUND, load-bearing facts VERIFIED (`verify_q11_cf_audit.py`). CF still UNPROVED, but
Q11 genuinely ADVANCES Q10** — an unconditional density bound + edge/Petersen/Clebsch root
certificates + a sharper 4-branch flag dichotomy.

## New results (audited)
1. **τ_K(F[k]) = k²τ_K(F)** (blow-up homogeneity, multi-affine ⟹ extreme points) — same as Q10.
   So CF ⟺ exact finite `τ_K(F) ≤ (N²/5−e)/2` for band F.
2. **★ EDGE-ROOT certificate (PROVED):** for every edge uv, `τ_K(G) ≤ e − (S_u+S_v)/2`
   (S_v=Σ_{z∈N(v)}d_z). Proof: triangle-free ⟹ N(u),N(v) disjoint independent; map them to an
   edge a~b of K (cost 0); for the rest pick P=N_K(a)∖{b} or Q=N_K(b)∖{a} (each 4 vtx, independent,
   **P-Q a perfect matching** — Step-2 VERIFIED) at random ⟹ R-edges expected cost 1, mixed 1/2;
   total e−(S_u+S_v)/2. Stronger non-averaged partition form also given.
3. **★ τ_K(G) ≤ e − 4e²/N² — PROVED, UNCONDITIONAL/density-only.** From edge-root: some edge has
   S_u+S_v ≥ 2M_2/e (M_2=Σ_{uv}d_ud_v); and `M_2 ≥ 4e³/N²` (two Cauchy-Schwarz steps:
   Σ1/√(d_ud_v) ≤ N/2 ⟹ Σ√(d_ud_v) ≥ 2e²/N ⟹ M_2 ≥ 4e³/N²; Step-2 VERIFIED 0/200). So
   `τ_K/N² ≤ x−4x²` (x=e/N²). CLEANER than Q10's 3β/2 (no BCL needed), and tighter at x=0.16
   (0.0576 vs 0.0638). Still ~2× too weak for CF: gap to (1/5−x)/2 is 3x/2−4x²−1/10 ≈ 0.025–0.038N²
   over the band — caps β at ~1/17.9 (the SAME wall). Density-only CANNOT close CF (consistent
   with all prior routes).
4. **★ C5-root (sharpened):** `τ_K ≤ 2e − ½Σ_c S_c − (3/2)e_01(C) − ½ e_12°(C)`; CF if some induced
   C5 has `Σ_c S_c + 3e_01 + e_12° ≥ 5e − N²/5`. Exact on C5-blowups. FAILS on Petersen-blowups
   (Σ_c S_c=0.45N² < 0.55N² needed, yet τ_K=0) and Clebsch-blowups — these are the two repairs:
5. **★ PETERSEN-ROOT certificate (NEW):** for an induced Petersen P (=10 two-subsets of [5],
   adjacency=disjointness), the 15 maximal intersecting families (5 stars size4 + 10 triangles
   size3 — Step-2 VERIFIED) ↔ 15 Clebsch vertices; good vertices map cost-0, bad vertices random ⟹
   `τ_K ≤ (3/4)·e_inc(B_P)`. =0 on a complete Petersen-blowup (repairs the C5-root Petersen failure).
6. **★ CLEBSCH-ROOT certificate (NEW):** induced Clebsch Q; good z (N_G(z)∩Q = N_K(a)) ↦ a (cost 0
   on good-good, disjoint signatures ⟹ adjacent in K); ⟹ `τ_K ≤ (3/4)·e_inc(B_K)`. =0 on Clebsch-blowup.
7. **★ THE 4-BRANCH DICHOTOMY (the sharp flag-SDP target):** CF follows if EVERY band graph has ≥1 of:
   Edge `S_u+S_v ≥ 3e−N²/5`; C5 `Σ_c S_c+3e_01+e_12° ≥ 5e−N²/5`; Petersen `e_inc(B_P) ≤ (4/3)(N²/10−e/2)`;
   Clebsch `e_inc(B_K) ≤ (4/3)(N²/10−e/2)`. Each with an EXPLICIT randomized labeling (flag orders
   4/7/12/18). Remaining open step: a flag-algebra/SDP "local-template coverage" proof that band +
   triangle-free FORCES one certificate (or add more Clebsch-hom root templates). NOT a raw 16-color
   SDP (wrong quantifier: ∀coloring vs ∃coloring) — must certify an explicit randomized rounding menu.
8. **Synchronization obstruction (sharper, Section 7):** gadget F = (non-Clebsch-hom H, e.g. M_2(C5))
   + private u−a−b−c−v path per edge ⟹ F triangle-free, edge-disjoint induced C5 per edge, F↛K,
   τ_K(F[k])=k²τ_K(F)>0 with Θ(N²) edge-disjoint C5's. So C5-packing COUNT alone cannot force o(N²)
   frustration — need cycle-space/overlap consistency. (Consistent with Q10's M_2(C5).)
9. **Frustration-stability:** `dist_K(G) ≤ τ_K ≤ 2 dist_K`; small τ_K ⟹ close to Clebsch-HOM class
   (⊋ C5/Clebsch blowups) ⟹ stability false as stated (same as Q10; need e+2τ_K near-saturation).

## Step-2 AUDIT verdict: SOUND, real advance
Edge-root P-Q matching VERIFIED; Petersen 15-family VERIFIED; M_2≥4e³/N² VERIFIED 0/200; M_2 chain
+ edge-root rounding re-derived by hand. GPT states CF unproved. **Net advance over Q10:** (a) an
UNCONDITIONAL density bound τ_K≤e−4e²/N² (no BCL); (b) the edge-root certificate; (c) Petersen-root
+ Clebsch-root certificates repairing the exact C5-root failures; (d) the explicit 4-branch flag
dichotomy — the sharpest, most concrete CF-sufficient target so far, each branch a constructive
randomized labeling. **The single open step is the flag-SDP "coverage" proof that band+triangle-free
forces one branch.** CF/Step-2 still UNPROVEN — do NOT mark solved.

## Next steps
- Implement the 4-branch coverage check computationally: for band graphs, verify at least one of the
  4 certificate inequalities holds (extends verify_FC_c5root; would test whether the 4 templates
  suffice or more are needed). If a band graph fails ALL 4 ⟹ need more root templates; report.
- The flag-SDP coverage proof (orders 4/7/12/18 rooted flags) is the research-grade endgame
  (flagmatic/CSDP) — beyond current tooling; candidate for a specialist or further consult.

## DONE 2026-06-20T18:06 — 4-branch coverage probe (`experiments/verify_4branch_coverage.py`)
Tested 31 band triangle-free graphs (C5[2..4], Petersen[1,2], Clebsch[1,2], + 24 random N=15..22 in
x=e/N²∈[0.12,0.16]). Results (single-thread Python, all VERIFIED, no fabrication):
- **CF direct (τ_K_ub ≤ RHS=(N²/5−e)/2): 0 violations / 31.** Direct numeric evidence CF holds.
- **Random band: cheap (edge-root OR C5-root F_C) coverage = 24/24.** The C5-root F_C alone covers
  ALL 24 random graphs (F_C ≤ RHS every time); edge-root additionally covers the low-density tail.
  So the two CHEAP templates already suffice on every generic band graph sampled.
- **Petersen[t]/Clebsch[t]: 4/4 motivating cases** — edge-root AND C5-root both FAIL (bound > RHS)
  yet τ_K_ub = 0, exactly matching Q11 §7's claim that the Petersen-root and Clebsch-root templates
  are genuinely needed for those two structured blow-ups (their (3/4)e_inc(B)=0 is witnessed by
  τ_K_ub=0; induced 10/16-vtx detection not reimplemented — that's part of the flag-SDP endgame).
- **NET:** the 4-branch menu covers every sampled band graph; failure modes are precisely the two
  predicted blow-ups. This is strong EVIDENCE the 4 templates suffice — NOT the coverage proof.
  CF / the flag-SDP "coverage" proof remain UNPROVEN. Step-2 still incomplete; gate genuinely unmet.

## DONE 2026-06-20T18:13 — adversarial coverage search (`experiments/adversarial_coverage_search.py`)
Hill-climbed band triangle-free graphs (N=10..20, x∈[0.1243,0.16]) to MAXIMIZE the cheap gap
`g_cheap = min(edge_root, F_C) − RHS` (>0 ⟺ both cheap certs fail) and tracked `g_CF = τ_K_ub − RHS`
(>0 ⟺ candidate CF counterexample). Single-thread Python, well under caps. Findings (no fabrication):
- **0 CF counterexamples** — τ_K_ub ≤ RHS at every search endpoint across all N.
- **C5-containing band graphs (N=15,18,20): g_cheap < 0 always** — edge-root OR C5-root F_C always
  covered; the adversarial search could NOT push a C5-bearing band graph past both cheap certs.
- The ONLY g_cheap>0 cases (N=10,12) are **C5-FREE** (induced-C5 count = 0, so F_C is undefined and
  the flag is an artifact of min() defaulting to edge-root). VERIFIED the N=12 maximiser: triangle-free,
  x=0.1597 (in band), 0 induced C5, τ_K_ub=0. These are exactly the **{C3,C5}-free** regime already
  covered by the proven **A7 bound β≤N²/32** — NOT a genuine coverage gap, and CF holds trivially (τ_K=0).
- **Refined taxonomy: 5 branches** = {A7 for C5-free} ∪ {edge, C5, Petersen, Clebsch}. No 5th *new*
  template indicated; the apparent gap maps onto an already-proven bound.
- **NET:** strengthens the coverage picture (no counterexample, no genuine new gap), but CF and the
  flag-SDP coverage proof remain UNPROVEN. Step-2 incomplete; gate genuinely unmet.
