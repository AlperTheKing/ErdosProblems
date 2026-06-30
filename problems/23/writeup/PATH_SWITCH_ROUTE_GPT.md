# PATH-SWITCH route to PATH-LRS (GPT-Pro, 2026-06-29) — the corrected, surviving program

After the spectral per-component route was refuted (Block-SBC + Bundle-SBC false; see SBC_WORKFLOW_VERDICT.md),
GPT-Pro redirected to the per-path scalar form with the GLOBAL bank. This is the surviving program.

## Target — PATH-LRS  (validated: 1.16M paths 0 viol; survives H?AFBo], alternating C5, two-lane)
A := N + N²/25 − m,  m=|M|. For every bad edge f and every shortest blue f-geodesic P=(x_0,…,x_{L−1}):
    Σ_{i} T(x_i) ≤ L·A   ⟺   (1/L)Σ_{x∈P} T(x) ≤ N + N²/25 − m.
Implication (verified): average over P weighted by L_f ⟹ ΣT² ≤ AΓ; with Γ²/N ≤ ΣT² ⟹ Γ ≤ NA; Γ≥25m ⟹ m ≤ N²/25. ∎

## Why global bank, not per-component
The false block inequality allocated the quadratic budget locally (n_C²/25). The correct bank is GLOBAL (N+N²/25−m).
PATH-LRS uses it directly: a small dense K-component (H?AFBo]) may exceed its local budget, two-lane may have
ρ(O)>N, yet the path-average stays under the full global allowance. RULE: prove ONE path inequality with the full
(N,m) bank; do NOT prove a component theorem.

## PATH-SWITCH LEMMA (the crux — Γ-minimality)
Fix f, shortest blue geodesic P (length L), excess E(P) := Σ_{x∈P}T(x) − L·A. If E(P)>0 then ∃ switch W⊆V:
  (1) flipped cut still maximum (δ_B(W)=δ_M(W), neutral); (2) B still connected; (3) m unchanged; (4) Γ(s^W)<Γ(s).
⟹ no Γ-min max cut has E(P)>0. ATOMS (exact-verified SOUND, _switch_atoms.py): δ_B(U)−δ_M(U)≥0 (every U, max cut);
Γ(s^W)≥Γ(s) for neutral W (Γ-min). The open analytic step is the UNCROSSING: that E(P)>0 forces such a W.

## Mechanism — STRIP-SHORTENING (§7)
Σ_{x∈P}T(x) = Σ_g (L_g/|cyc(g)|) Σ_{Q∈cyc(g)} |P∩Q|. So E(P)>0 means P is co-travelled by too much weighted
shortest-cycle traffic. A co-travelling atom Q gives an alternating-strip switch W_{P,Q} with
    ΔΓ(W_{P,Q}) ≤ −4 L_g (r−1) + boundary compensation,   r = shared/strip projection length on P.
Boundary paid by a max-cut margin δ_B(U)−δ_M(U)≥0 OR the global bank N²/25−m. A strip of length r shortens ∝ (r−1)
while its endpoint tax is paid once — why pure support-Hall fails but the (N²/25−m) bank succeeds. At balanced
C5[t] every strip is tight (r=5, m=N²/25, E(P)=0); two-lane has tiny m so the bank is huge and no positive-excess
switch is forced.

## DUAL-PATH (finite Farkas form, §5) and PATH-BUNDLE (corrected terminal, §8)
DUAL-PATH: LA − Σ_{x∈P}T(x) = Σ_W α_W ΔΓ(W) + Σ_U β_U(δ_B(U)−δ_M(U)) + R_P, α,β,R≥0, over the canonical switch
family W(I,π) (alternating path intervals I + forced parity choices on off-path blue components). [As a SCALAR
identity with free R_P≥0 this is near-trivial; the content is that ONLY canonical alternating-strip switches +
Γ-min neutral switches are needed — i.e. the uncrossing.]
PATH-BUNDLE (replaces false Bundle-SBC, GLOBAL bank): for a coherent bundle, n_0+n_{ℓ−1}+m_*Σ_{i=1}^{ℓ−2} 1/n_i ≤
N+N²/25−m. Left = active bundle only; right = full graph (N,m); no per-component n_C²/25.

## HOT-PATH COMPRESSION LEMMA (corrected, anchored to ONE path — the remaining risk)
Γ-min connected-B max cut, shortest blue path P with EXCESS Σ_{x∈P}T(x) > L·A. Then ∃ another connected-B max cut
s' with m(s')=m, Γ(s')≤Γ(s) (strict unless active support already balanced C5-blowup), path-excess non-decreasing
under the compressed model, and after finitely many switches the active support is a coherent layered bundle
satisfying PATH-BUNDLE. Since PATH-BUNDLE forbids EXCESS, EXCESS is impossible. Anchoring to P (not a whole
K-component) is what keeps the global (N,m) bank alive.

## Status / division of labour
Codex (proof-driver, switch arguments) owns the PATH-SWITCH / uncrossing proof. Claude (gate) has verified: the
implication chain, PATH-LRS on 1.16M paths + killers, and the nonneg atoms (a)/(b). Open analytic core = the
STRIP-SHORTENING uncrossing (E(P)>0 ⟹ neutral Γ-decreasing alternating-strip switch). That is the entire remaining risk.
