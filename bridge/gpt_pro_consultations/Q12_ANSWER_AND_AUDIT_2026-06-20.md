# Q12 — flag-SDP COVERAGE proof: GPT-Pro ANSWER + Step-2 AUDIT (2026-06-20)

Chat "Erdos Problem #23 Proof" `c/6a36b525-d8fc-83eb-b29f-b41052441eb2`, Kapsamlı Pro (Pro-Extended),
reasoned **31m 22s**. Question = the self-contained Q12 brief (prove COVERAGE of the 4+1-template menu
⟹ CF ⟹ Step 2; or reduce to a finite cert; or falsify). **Verdict: SOUND. GPT delivered a rigorous
NEGATIVE result — COVERAGE (as posed) is FALSE — with an explicit infinite family. All load-bearing
facts INDEPENDENTLY VERIFIED (`verify_q12_groetzsch_audit.py`, `groetzsch_coverage_gap.py`). One audit
precision-correction below. CF and Erdős #23 remain UNTHREATENED.**

## GPT's result (audited)
**COVERAGE is FALSE for the stated menu {A7, edge, C5, Petersen, Clebsch}.** Explicit infinite family:
- **Base graph H = the 11-vertex Grötzsch graph = M(C5)** (Mycielskian of C5): vertices {v_i,u_i:i∈Z5}∪{w},
  edges v_i v_{i+1}, u_i v_{i-1}, u_i v_{i+1}, w u_i. GPT gave an **explicit embedding H ↪ Clebsch**
  (even subsets of [5]): u=(∅,{1,4},{1,3},{1,2},{1,5}), v=({2,3},{1,2,4,5},{3,5},{2,4},{1,3,4,5}),
  w={2,3,4,5}. ✅ VERIFIED: all 20 H-edges map to |symdiff|=4 (Clebsch edges), embedding is INDUCED ⟹ τ_K(H)=0.
- **Weighted blow-up G_k**: classes of size 2k for each u_i,v_i and size k for w; complete bipartite per
  H-edge. ✅ VERIFIED: N=21k, e=70k², **x=10/63≈0.158730 ∈ [0.1243,0.16]** (in band), RHS=(N²/5−e)/2=**91/10·k²**,
  **τ_K(G_k)=0** (map each class to its Clebsch vertex; cross-checked by local search). For the exact N=5n
  setting take k=5m ⟹ N=105m=5·(21m). Contains induced C5 ⟹ A7 inapplicable. ✅
- **No Petersen/Clebsch root**: blow-up classes are false twins; C5/Petersen/Clebsch are false-twin-free ⟹
  any induced copy injects into the 11-vtx H. No induced Clebsch (needs 16). No induced Petersen (every
  H−z fails 3-regularity: w keeps degree 5 or 4, or some u_i drops to 2). ✅ VERIFIED.
- **Edge-root fails**: degrees d_U=5k,d_V=8k,d_W=10k; S_U=42k²,S_V=52k²,S_W=50k²; edge-root e−(S_a+S_b)/2 ∈
  {18,23,24}k² > RHS=9.1k² on all edge classes VV/UV/WU. ✅ VERIFIED (min edge-root 18k² > 9.1k²).
- **C5-root fails**: GPT case-split 31 induced C5's into 5 stat-classes, all with certificate ≥10k² > 9.1k²
  (margin ≥0.9k²). (See precision note.) ✅ the algebraic/degree-relaxed C5-root indeed ≥10k².
- **SDP consequence**: the 11-vtx graphon (μ(u_i)=μ(v_i)=2/21, μ(w)=1/21) is an exact PRIMAL witness ⟹ **no
  rational dual certificate proving COVERAGE exists at flag order ≤18 (or any order)** over the 4 templates.
  A flag-SDP solver reporting infeasibility there has encoded a stronger, INCORRECT condition. ⟹ the
  "prove COVERAGE by an order-18 flag-SDP over {edge,C5,Petersen,Clebsch}" plan is **DEAD**.
- **Repair (GPT §7)**: add the order-13 **M(C5)=Grötzsch root** σ_H with the canonical-type certificate
  τ_K ≤ 2·e_bad^H(G,ρ) (=0 on every complete blow-up of H). Principled finite closure = add canonical-profile
  roots for ALL false-twin-free induced subgraphs of Clebsch (≤16 vtx ⟹ rooted order ≤18). **Whether that
  enlarged finite menu covers all non-Clebsch-hom band graphs is the NEXT open coverage problem.**
- GPT explicitly notes: this falsifies only the proposed COVERAGE reduction, **NOT CF nor Erdős #23**.

## Step-2 AUDIT — independent verification
`verify_q12_groetzsch_audit.py` (clean) confirmed: embedding hom+induced; H triangle-free, degrees
[3×5,4×5,5]; no H−z 3-regular; G_k (k=1,2) N/e/x/RHS/τ_K exactly as claimed; edge-root min 18k²>RHS; has
induced C5. **All GPT's arithmetic checks out.**

### ★ PRECISION CORRECTION (audit-grade, important)
GPT's C5-root failure uses the **degree-relaxed (W_C-type) algebraic bound** (its row-min 10k²). The
**finer 10-map F_C C5-certificate** (what `verify_4branch_coverage.py` actually computes; τ_K≤F_C≤W_C)
is STRICTLY tighter and **COVERS GPT's specific G_k**: F_C(G_k)=6k² ≤ 9.1k²=RHS. So G_k refutes coverage
only for the *degree-relaxed* C5-root, not for F_C. **However the F_C-coverage is ALSO genuinely false**,
witnessed (clean margin) by the *uniform* blow-up: Grötzsch[5]+1·iso (N=56,e=500,x=0.1594, RHS=63.6,
τ_K=0) has F_C=75 > 63.6; Grötzsch[4]+1·iso (N=45,x=0.1580,RHS=42.5) has F_C=48 > 42.5. So:
- **COVERAGE is FALSE for BOTH the degree-relaxed C5-root (GPT's G_k) AND the finer 10-map F_C
  (uniform Grötzsch+iso).** The Grötzsch graph M(C5) is the obstruction in both. GPT's high-level
  conclusion and repair direction stand; the only correction is *which Grötzsch witness* kills *which*
  certificate strength.

## Implications for Step 2 (honest)
1. **The 4-template COVERAGE / order-18 flag-SDP route is REFUTED** (was the open endgame in Q11/ledger CF).
   My earlier "coverage evidence saturated, 0 gaps N=10..26" was a SAMPLING ARTIFACT — random/adversarial
   search never generated the Grötzsch=M(C5) structure. GPT's structural insight found it.
2. **CF and Step 2 are NOT refuted** — τ_K=0 on every Grötzsch witness (CF holds, 0≤RHS). This is a gap in
   the PROOF METHOD only.
3. **New open problem (replaces the old one in ledger CF):** does the ENLARGED menu — all canonical-profile
   roots of false-twin-free induced subgraphs of Clebsch (rooted order ≤18, incl. the M(C5) root) — cover
   the band? GPT leaves this open. This is the new research-grade target. (Equivalent in spirit to: every
   non-Clebsch-hom band graph has SOME false-twin-free Clebsch-subgraph whose canonical root certifies CF.)
4. Caveat to even that: M(C5) is itself Clebsch-hom (τ_K(H)=0); the obstruction is that the EXPLICIT
   small-flag rounding menus are too coarse to realize the homomorphism. A direct **Clebsch-homomorphism
   existence** argument (prove every band graph is Clebsch-hom, or close enough) would sidestep templates
   entirely — but that is exactly CF-strength and currently has no proof route.

## Next steps
- Do NOT pursue the order-18 flag-SDP over the 4 templates (GPT's primal witness proves it cannot certify).
- Candidate next consult (FRESH chat — this one is spent): does the enlarged false-twin-free-root menu cover
  the band, or is there a band graph evading even M(C5)/all-Clebsch-subgraph roots with τ_K>0 (a real CF
  counterexample)? Our searches found none with τ_K>0.
- Keep monitoring Codex Step-1 (independent of this).
- CF / Step 2 remain UNPROVEN; gate genuinely unmet. Do NOT mark solved.
