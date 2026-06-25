# Q9 — Clebsch-frustration reduction: GPT Pro ANSWER + Step-2 AUDIT (2026-06-20)

User-relayed GPT Pro Extended answer to Q9 (chat c/6a35f70f). Step-2 hand-checked all 6
sections' algebra AND computationally verified the load-bearing claims
(`verify_clebsch_frustration.py`). **VERDICT: SOUND. Does NOT prove the conjecture (GPT says
so honestly), but a genuine, correct, substantial REFRAMING of the open core + new proven
lemmas + a finite H2 test.**

## GPT's result (no full proof): replace "C5-stability" by a finite Clebsch-frustration inequality
Notation: x = e/N². C5[n] extremizer at x=1/5 (β=n²). Medium band ⟺ 0.1243 < x < 0.15985
(= density 0.2486–0.3197).

### §1 Clebsch five-cut certificate — PROVEN + VERIFIED
K = Clebsch graph = 16 even subsets of [5], A~B iff |A△B|=4 (triangle-free SRG(16,5,0,2)).
Coordinate cuts C_j = {A even : j∈A}. Each edge has |A△B|=4 ⟹ cut by 4, mono in exactly 1 of
the 5 cuts. So **G hom to K ⟹ β(G) ≤ e/5** (1). Independently, triangle-free ⟹ MaxCut ≥ Q/N ≥
4e²/N² (Q=Σd²; the cut (N(v)|rest) cuts S_v edges, ΣS_v=Q, Cauchy-Schwarz), so
**β ≤ e − 4e²/N²** (2). Combining: every Clebsch-hom triangle-free G has
**β ≤ min{e/5, e−4e²/N²} ≤ N²/25** (3) (case split x≤1/5 vs x≥1/5; 1/25−(x−4x²)=4(x−1/20)(x−1/5)≥0).
**Step-2 VERIFIED:** Clebsch β=8, MaxCut=32, Q/N=25, β=8≤10.24 ✓; coordinate-cut certificate
(every edge mono in exactly 1 cut) ✓; MaxCut≥Q/N: 0 violations / 1803 tri-free graphs (tight at C5[n]).
**Note:** Clebsch-hom ⊋ C5-hom (since C5→K), so (3) genuinely enlarges C5HOM. But NOT every
tri-free graph is Clebsch-hom (K is 4-chromatic; high-chromatic tri-free graphs e.g. Kneser
are not hom to K) — so this alone does NOT close the problem.

### §2 Equality in the Clebsch class ⟹ G = C5[n] — PROVEN (Step-2 re-derived, rigorous)
β=N²/25 + Clebsch-hom ⟹ e=N²/5, MaxCut=4N²/25, equality in Cauchy-Schwarz ⟹ d-regular d=2N/5;
shortest odd cycle has ℓ=5 (counting: Σ_{v∈C}d(v) ≤ 2ℓ+2(N−ℓ)=2N, with d=2N/5 forces ℓ≤5;
triangle-free kills gap-1, ≥2 neighbours give odd gap ≤ℓ−4 ⟹ shorter odd cycle unless ℓ=5);
fibres F_i (distance-2 neighbour-pairs) all size N/5 (circulant C5-adjacency system, A invertible);
edges only between consecutive F_i, each vertex adjacent to all 2N/5 ⟹ G=C5[N/5]. No new extremizer.

### §3 ★ Clebsch frustration τ_K and the reduction — SOUND (the key new asset)
For φ:V→V(K), edge cost c_φ(uv)=(4−|φ(u)△φ(v)|)/2 ∈ {0,1,2} for |△|∈{4,2,0}. τ_K(G)=min_φ Σc_φ.
Edge with |△|=4,2,0 is mono in 1,3,5 cuts = 1+2c_φ. So Σ_{5 cuts} mono = e+2τ_K(G), one cut gives
**β(G) ≤ (e + 2τ_K(G))/5** (5). Equivalent: e+2τ_K = min over 4 free shores A_1..A_4 (A_5=A_1△A_2△A_3△A_4)
of Σ_{i=1}^5 #mono(A_i) (6) — a 5-cut GLOBAL-realignment problem with one parity relation (NOT
radius-2/single-cut/spectral). From (5), **β ≤ N²/25 whenever τ_K(G) ≤ (N²/5 − e)/2** (7). So a
band counterexample needs τ_K(G)/N² > (1/5−x)/2 ∈ [0.0201, 0.0378] (8).

### §4 Robust C5-abundance — PROVEN via A7
τ_5(G)=min edges to delete to kill all C5. G−F is {C3,C5}-free ⟹ β(G−F)≤N²/32 (A7); β≤β(G−F)+|F|
⟹ a counterexample (β≥N²/25) has **τ_5(G) ≥ (1/25−1/32)N² = 7/800·N²** (9), hence ≥ 7/4000·N²
edge-disjoint induced C5's. The C5-structure is quadratically robust.

### §5 ★ The single clean missing statement (CF) — the new open core
**(CF):** ∀ε>0, all large tri-free G with 0.1243N²≤e≤0.16N² and τ_5(G)≥7/800 N² satisfy
**τ_K(G) ≤ (N²/5 − e)/2 + εN².** Then (5)+(CF) ⟹ β ≤ N²/25 + (2ε/5)N²; a finite counterexample
F (β/|F|²=1/25+δ) blows up to F[k] (density + normalized β preserved, satisfies (9)), and CF
with ε<5δ/2 contradicts δ. So **asymptotic CF (NO effective N0) ⟹ the EXACT finite conjecture**
by blow-up transfer. (Logic verified.) GPT: "I cannot presently prove CF — this is exactly where
the argument stalls." More concrete than "stability": 16-state target, explicit quadratic objective
τ_K, explicit constant (1/5−x)/2, both C5[n] and Clebsch-blowups have τ_K=0, equality classified.

### §6 ★ Finite H2-falsification test Λ₅(F) — SOUND (Step-2 checked on C5)
For tri-free F on r vtx, F[k] blow-up, 5-set S = multiplicity vector s (Σs_i=5):
β(F[k]−S)=min_σ[k²|E(B_σ)|−kL_σ(s)+R_σ(s)] (12, B_σ=bad-edge graph of cut σ, L_σ=Σs_i deg_Bσ(i),
R_σ=Σ_{ij∈Bσ}s_is_j). For large k: β(F[k])−β(F[k]−S)=max_{σ∈O(F)}[kL_σ(s)−R_σ(s)] (13).
Λ₅(F)=min_s max_{σ∈O(F)} L_σ(s) (14). **Λ₅(F)>2r/5 ⟹ large blow-ups FALSIFY H2; <2r/5 ⟹ H2 holds;
=2r/5 boundary ⟹ need s with R_σ(s)≥1 on every optimal cut attaining L=2r/5** (15). Fractional
s_i=5/r gives L=10β(F)/r ≤ 2r/5 iff β(F)≤r²/25. For F=C5: s=(1,1,1,1,1), L_σ=2=2r/5, R_σ=1 ⟹
drop=2k−1 exactly ✓ (Step-2 verified). A complete finite criterion for whether H2 is the right lemma.

## Step-2 AUDIT verdict: SOUND, no overclaim
Every inequality (1)–(13) hand-re-derived; load-bearing numerics verified
(`verify_clebsch_frustration.py`: Clebsch β=8/MaxCut=32/coordinate-cert; MaxCut≥Q/N 0/1803).
GPT explicitly does NOT claim a proof. **Net new assets:** (a) Clebsch-hom ⟹ β≤N²/25 + uniqueness
(proven, enlarges C5HOM); (b) the Clebsch-frustration REDUCTION (5)/(7) — concrete replacement for
"effective stability"; (c) τ_5≥7/800 N² robust-C5 bound; (d) the open core is now the explicit
statement CF (flag-algebra-amenable); (e) the Λ₅ finite H2-test. **The conjecture is NOT closed:
CF is unproven** — it is the new, sharper barrier. Do NOT mark complete.

## Next concrete steps
- Attack CF directly (it is a finite-target flag-algebra problem — feasible for a flag/SDP
  computation à la BCL, or a fresh GPT/workflow consult focused on bounding τ_K in the band).
- Run the Λ₅(F) finite test on small triangle-free bases F to either FIND an H2-counterexample
  blow-up or accumulate evidence H2 holds (compute O(F), Λ₅, and the boundary R-condition).
