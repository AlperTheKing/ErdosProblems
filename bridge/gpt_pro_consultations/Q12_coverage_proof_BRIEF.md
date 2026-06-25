# Q12 BRIEF — the flag-SDP "coverage" proof for the (5-)branch Clebsch-frustration dichotomy

**Status: READY TO SEND when a fresh GPT-Pro-Extended session is available** (GPT degenerate after
first answer per session this round). Self-contained. This is the genuine research-grade endgame of
Step 2 for Erdős #23. Audit any answer HARD; save Q12_ANSWER_AND_AUDIT.

---

## 0. One-paragraph context
Erdős #23: every triangle-free `G` on `N=5n` vertices has `β(G)=e−MaxCut(G) ≤ n²`, sharp at the
balanced blow-up `C5[n]`. Step 1 (Codex, in progress) proves the finite base `a(30)=36`. Step 2 (this
brief) must prove the general-`n` reduction. We have reduced Step 2's open core to a single inequality
**CF** below; everything upstream of CF is proved and audited.

## 1. The exact open inequality (CF)
Let `K` = Clebsch graph (16 even subsets of `[5]`, `A~B ⟺ |A△B|=4`). For a graph `G` define the
**Clebsch frustration**
```
  τ_K(G) = min_{φ:V(G)→V(K)}  Σ_{uv∈E(G)} (4 − |φ(u)△φ(v)|)/2 ,   summand ∈ {0,1,2}.
```
**CF (UNPROVEN):** for every triangle-free `G` on `N` vertices with `e` edges in the band
`x=e/N² ∈ [0.1243, 0.16]`,
```
        τ_K(G)  ≤  (N²/5 − e)/2   =: RHS.
```
**Why CF closes Step 2 (PROVED + audited, see Q9/ledger CLEBSCH):**
- 5 coordinate cuts of `K` give `β(G) ≤ (e + 2τ_K)/5`. With CF: `β ≤ (e + (N²/5−e))/5 = N²/25 = n²`. ✓
- Blow-up homogeneity `τ_K(F[k]) = k²·τ_K(F)` (multi-affine ⟹ extreme points; VERIFIED) ⟹ the
  asymptotic/band CF transfers to the EXACT inequality for all `N`. The C5-free regime
  (`x` small / no induced C5) is handled separately by the proved **A7 bound** `β ≤ N²/32 < n²`.
- Equality `β=n²` forces `τ_K=0` and `e=N²/5`, i.e. `G=C5[n]` (uniqueness, audited).

## 2. What is PROVED (load-bearing, all independently verified)
- **τ_K(G) ≤ e − 4e²/N²**, unconditional/density-only. (edge-root `τ_K ≤ e−(S_u+S_v)/2` with
  `S_v=Σ_{z∼v}d_z`, via triangle-free ⟹ `N(u),N(v)` disjoint independent ⟹ map to an edge `a~b` of
  `K`, then `P=N_K(a)∖b`, `Q=N_K(b)∖a` (each 4 vtx independent, **P–Q a perfect matching**); plus
  `M_2=Σ_{uv}d_ud_v ≥ 4e³/N²`.) **This density-only bound caps `β` at ≈`N²/17.9` — provably TOO WEAK
  to reach CF** (gap `3x/2−4x²−1/10 ≈ 0.025–0.038·N²` over the band). Density alone CANNOT close CF.
- **C5-root certificate:** `τ_K ≤ 2e − ½Σ_c S_c − (3/2)e_01(C) − ½e_12°(C)` for any induced C5 `C`;
  CF if some `C` has `Σ_c S_c + 3e_01 + e_12° ≥ 5e − N²/5`. Exact on C5-blowups; FAILS on Petersen-
  and Clebsch-blowups.
- **Petersen-root** and **Clebsch-root** certificates `τ_K ≤ (3/4)·e_inc(B)` (B = "bad" vertices),
  `=0` on Petersen-/Clebsch-blowups respectively — they repair the exact C5-root failure cases.
- **A7:** every `{C3,C5}`-free graph has `β ≤ N²/32` (so the C5-free regime is closed).
- Proved upstream: `τ_5 ≥ 7/800·N²` (robust C5 abundance), `τ_K ≤ (3/2)β`, the 5-cut bound, the
  blow-up transfer, the Λ₅ finite H2-test (0 violations exhaustively for blow-up bases `r ≤ 10`).

## 3. The reduction to a coverage statement (THE ASK)
Each certificate is an **explicit randomized labeling** `V(G)→V(K)` rooted at a small flag (orders:
edge 4 / C5 7 / Petersen 12 / Clebsch 18). Writing `cert_T(G) ≤ RHS` for "template T certifies CF on
G", we have proved every individual `cert_T`. **CF follows if the templates COVER the band:**
```
  (COVERAGE)  every triangle-free G in the band satisfies  cert_T(G) ≤ RHS  for at least one
              T ∈ { A7(C5-free), edge, C5, Petersen, Clebsch }.
```
This is a **∀G ∃T** statement. It is NOT a raw 16-colour Clebsch-homomorphism SDP (that would be the
wrong quantifier ∀coloring vs ∃coloring). It is a **flag-algebra / rounding-menu coverage** claim.

## 4. Computational evidence FOR coverage (this session; NOT a proof)
- `verify_4branch_coverage.py` (31 band graphs): CF direct (τ_K_ub ≤ RHS) **0 violations**; random
  band cheap-coverage (edge OR C5-root) **24/24** (C5-root alone covers all 24); Petersen[t]/Clebsch[t]
  **4/4** cheap-FAIL but τ_K=0 (extra roots needed) — matches the predicted failure modes.
- `adversarial_coverage_search.py` (hill-climb N=10..20 maximizing `min(edge,F_C)−RHS`): **0 CF
  counterexamples**; C5-containing band graphs always covered (g_cheap<0); the only "both-cheap-fail"
  graphs are C5-FREE (so A7 applies; τ_K=0). No NEW (6th) template indicated.

## 5. Falsified / excluded approaches (do not re-suggest)
- Density-only bounds (cap ≈1/17.9) — provably cannot close CF (§2).
- Frustration-stability "small τ_K ⟹ near-extremal" — REFUTED (`dist_K ≤ τ_K ≤ 2dist_K`; small τ_K
  only forces Clebsch-HOM class, which strictly contains non-extremal blow-ups; explicit refuter
  `C5[m]⊔K_{r,r}` has τ_K=0, density 0.128).
- δ₂-codegree dichotomy — REFUTED (low-δ₂ ≡ full problem via blow-up; `Δ_v ≤ e₂(v)` is the wrong sign).
- Single-vertex / averaging / per-ball peeling for the exact H2 — all shown a factor ≈2.5 too weak on
  `C5[n]` (greedy recovers only `Σ⌈d/2⌉=5n` of a C5-transversal's incident edges; need all but `2n−1`).
- C5-packing COUNT alone — the synchronization gadget `F=(non-Clebsch-hom core)+private P4 per edge`
  has Θ(N²) edge-disjoint induced C5's yet `τ_K(F[k])=k²τ_K(F)>0`; need cycle-space/overlap consistency.

## 6. Concrete questions
1. **Prove COVERAGE** (§3) — ideally as a finite flag-algebra SDP at flag order ≤18 over the rooted
   templates {edge, C5, Petersen, Clebsch} (+ A7 for the C5-free corner), or a discharging argument
   distributing `RHS−cert_T` over local structure. Is the menu of 4(+1) templates provably sufficient,
   or is a finite further family of Clebsch-hom root templates required (and which)?
2. If a finite SDP is the route: state the exact rooted flag types, the density/edge functionals to
   feed CSDP/flagmatic, and the certificate format that would constitute a rigorous proof (not numeric).
3. **Falsification route:** give the most plausible construction of a band triangle-free graph that
   defeats ALL templates simultaneously (a true CF counterexample or a coverage gap), so we can target
   the search. Our hill-climb found none with an induced C5.
4. If CF is the wrong granularity, identify a single clean finite/asymptotic statement that (a) is
   provable and (b) still yields the exact `β ≤ n²` via the blow-up transfer.

**Deliverable wanted:** a proof of COVERAGE (hence CF, hence Step 2), OR a precise reduction of
COVERAGE to one finite checkable certificate, OR a falsifying construction. Audit-grade rigor; no
numeric-only SDP claims accepted as proof.
