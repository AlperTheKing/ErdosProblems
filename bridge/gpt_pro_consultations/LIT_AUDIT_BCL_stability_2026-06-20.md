# Literature audit — BCL stability & the medium-density open core (2026-06-20)

Step-2 web search + ar5iv fetch of Balogh–Clemen–Lavrov–Lidický–Pfender, "Max Cuts in
Triangle-free Graphs" (arXiv:2103.14179), to test the H2 blocker's premise (an effective
stability theorem near C5[n]).

## Verified theorem statements (ar5iv 2103.14179)
- **Thm 1.3 (the density-restricted n²/25 bounds):** "Let G be triangle-free on n vertices.
  Then, FOR n LARGE ENOUGH, (a) D₂(G) ≤ n²/23.5; (b) D₂ ≤ n²/25 if |E| ≥ 0.3197·C(n,2);
  (c) D₂ ≤ n²/25 if |E| ≤ 0.2486·C(n,2)." ⇒ ASYMPTOTIC, **no explicit n₀** (only ε=10⁻⁸
  appears internally). Confirms the DEP-a25 / H1 finite-n caveat against the primary source.
- **Thm 1.4:** "Let G be K₃-free on n vertices with ≥ n²/5 edges. Then ∃ an UNBALANCED C₅
  blow-up H with D₂(G) ≤ D₂(H)." ⇒ a reduction-to-blowups for density ≥ 0.4, NOT an
  edit-distance stability theorem; does not quantify closeness to the extremal C5[n].
- **No uniqueness theorem, NO effective/finite stability, no computable n₀.** (The web
  snippet "balanced C5 blow-up is the unique extremal for all n except n=8" is NOT a BCL
  theorem with explicit constants — over-read by the search summarizer.)

## ★ Sharpened density geometry of the open core
- `density(C5[n]) = 5n² / C(5n,2) → 2/5 = 0.4`. So the EXTREMIZER lives at density 0.4,
  i.e. in BCL's HIGH tail (≥ 0.3197), where the n²/25 bound IS proven — asymptotically.
- Blow-up is density-PRESERVING (`density(G[t]) → density(G)`), so Codex's blow-up transfer
  only moves TAIL graphs into BCL range; a MEDIUM-band graph stays medium. Hence the genuine
  open core = triangle-free graphs with density in **(0.2486, 0.3197)** at finite N.
- **Consequence (new framing):** a counterexample (β > n²) in the open band would have
  density < 0.3197 < 0.4 = extremizer density, yet β > n² = the believed MAX β. I.e. it must
  be **strictly sparser than the extremizer C5[n] yet strictly beat its β.** This is highly
  implausible (sparser triangle-free graphs are closer to bipartite / have lower β) and is
  why the conjecture is believed — but ruling it out IS the open medium-density problem.
  Empirically consistent: Step-2 found 0 counterexamples over n≤4 (incl. non-hom hard cores),
  and OEIS A389646 obeys a(N) ≤ N²/25 for all N ≤ 23.

## Bearing on H2 / completion
- The H2 proof's only surviving route (effective stability near C5[n]) is CONFIRMED absent
  from the literature — not merely assumed. So H2 is genuinely research-grade open.
- a(25)/a(30) finite medium windows are the density band (0.2486,0.3197) at N=25,30, closed
  only by EXACT enumeration (Codex's machinery), since BCL is asymptotic there. Matches the
  current Codex H1 campaign + the a(25) DEP.
- Update GPT brief Q9: BCL has no effective stability (verified); the target is exactly the
  band (0.2486,0.3197), where a counterexample would be sparser-than-extremal yet higher-β.
  A finite/effective stability theorem there, or an exact argument that no sub-0.32-density
  triangle-free graph beats β=n², would close it.

## β-vs-density profile (Step-2 compute, `beta_vs_edges.cpp`, N=15)
Random triangle-free 15-vtx graphs by exact edge count (LOWER bounds on max β per e):
max β rises with density, PEAKS at e=45 / density 0.43 with β=9=n² (= C5[3], the extremizer),
then COLLAPSES for denser graphs (e=50 → β=1, since dense triangle-free → near-bipartite).
In the OPEN band (e=26–34, density 0.2486–0.3197) sampled max β only reaches ~6–7 < 9=n².
**So the conjecture's boundary β=n² is attained ONLY at the extremal density ≈0.43, NOT in
the open medium band — the band sits strictly below n².** Concrete support for "a counterexample
must be sparser than the extremizer yet beat its β" being implausible. (Sampled, not exhaustive;
the TRUE max over ALL 15-vtx tri-free graphs is a(15)=9, OEIS-confirmed, attained at C5[3].)
N=20 (n=4, n²=16): open band e∈[47,61], sampled max β ~10–12 < 16. CAVEAT: random sampling at
N=20 does NOT reach the structured extremizer C5[4] (β=16) — it tops out at β≈13 even at the
extremal density — so the N=20 profile maps the TYPICAL landscape, not a bound on the true
max-β-in-band. (Net: both N=15,20 show the band's β well below n²; N=15 also hits the true
extremizer, N=20 does not.)

Sources: arXiv:2103.14179 (ar5iv); OEIS A389646; related: arXiv:2104.09406 (sparse halves),
"Making K_{r+1}-free graphs r-partite" (exact only in the DENSE m ≥ t_r(n)−δ_r n² regime,
density ~1/2, NOT the C5[n] band).
