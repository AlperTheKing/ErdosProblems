# SBC proof architecture (GPT-Pro, 2026-06-29) — exact-testable skeleton

**Target (corrected from the false ρ(O)≤N):**  ρ(O) + m ≤ N + N²/25,  m=|M|.  Equivalently ρ(O) ≤ A := N + N²/25 − m.
Implies #23: O PSD ⟹ ρ(O) ≥ ℓᵀOℓ/ℓᵀℓ = ΣT²/Γ ≥ Γ/N ≥ 25m/N (Γ=Σℓ_f²≥25m); with SBC ⟹ m ≤ N²/25 = β.

## 1. Corrected local split (Hardy-SBC)
Local circulant (PROVEN): p_f p_fᵀ + ā_f L_{τ_f} ⪯ L_f diag(p_f), ā_f = L_f³/(4(L_f²−2)). Sum ⟹ K + L_ω ⪯ diag(T),
L_ω = Σ_f ā_f L_{τ_f}. Hence with A = N + N²/25 − m:
    A·I − K = [diag(T) − K − L_ω]  +  [L_ω + diag(A − T)]
            =  R_cyc (⪰0, proven)   +  H_A (Hardy-SBC target).
**Hardy-SBC:**  H_A = L_ω + diag(N + N²/25 − m − T) ⪰ 0.  The bad-count slack is the uniform potential (N²/25 − m)I:
vanishes at the C5[t] extremal (m=N²/25, recovers the old sharp N−T form), huge on two-lane (m=4).

## 2. Component reduction — the whole proof reduces to BLOCK-SBC  (algebra VERIFIED valid)
O is **block-diagonal over the positive K-components** C_1..C_r (cross-component ⟨p_f,p_g⟩=0 since geodesic supports
are disjoint). Let n_i=|C_i|, m_i=|M_i|, λ_i=ρ(O_i). It SUFFICES to prove per component:
    **BLOCK-SBC:**  λ_i + m_i ≤ n_i + n_i²/25.
Summation (pick block c with λ_c=ρ(O)): BLOCK-SBC for c gives λ_c+m_c ≤ n_c+n_c²/25; for i≠c, BLOCK-SBC + Rayleigh
λ_i ≥ 25m_i/n_i ⟹ m_i ≤ n_i²/25. Then ρ(O)+m = λ_c + Σm_i ≤ n_c+n_c²/25 + Σ_{i≠c} n_i²/25 = n_c + (1/25)Σn_i²
≤ N + N²/25  (since Σn_i ≤ N, Σn_i² ≤ (Σn_i)² ≤ N²).  ∎ reduction.

## 3. Hot-core compression (the HARD structural lemma — uses Γ-minimality; NOT gate-provable)
A Γ-minimal connected-B max cut with a K-component C violating BLOCK-SBC: its Perron support compresses, without
decreasing ρ(O_C)+m_C, to a **coherent odd-cycle bundle**. Non-parallel overlaps / private tails / crossed corridors
in a Perron-HOT component yield either (1) a cold-geodesic uncrossing that doesn't lower the Rayleigh quotient, or
(2) a neutral max-cut switch that strictly decreases Γ — contradicting Γ-minimality. Two-lane is already coherent
(small m) ⟹ NOT excluded; consistent with ρ(O)>N there.

## 4. Coherent bundle model + terminal BUNDLE-SBC (1D — pure numeric, gate-provable)
Bundle: odd ℓ≥5, layers A_0..A_{ℓ-1}, bad-edge graph H ⊆ A_0×A_{ℓ-1}, m=|E(H)|, n_i=|A_i|, n=Σn_i. Model vector
q_e: q_e(a)=q_e(b)=1 (endpoints in A_0,A_{ℓ-1}), q_e(v)=1/n_i for v∈A_i (1≤i≤ℓ-2). Then **O_bun = B_Hᵀ B_H + c J_m**,
c=Σ_{i=1}^{ℓ-2} 1/n_i, B_H = 0/1 endpoint incidence. So ρ(O_bun) ≤ ρ(B_Hᵀ B_H) + c m ≤ (n_0+n_{ℓ-1}) + c m.
**BUNDLE-SBC (1D):**  for odd ℓ≥5, n_i>0, m ≤ n_i n_{i+1} (cyclic):
    n_0 + n_{ℓ-1} + m(1 + Σ_{i=1}^{ℓ-2} 1/n_i)  ≤  n + n²/25.
Sharp iff ℓ=5, all n_i=√m, H=K_{√m,√m} (the balanced C5 blow-up). Smoothing proof: reduce to a_i a_{i+1}≥1,
A=Σa_i≥ℓ≥5; worst case √m=1; tighten adjacent products to equality ⟹ all a_i=1 ⟹ A=ℓ ⟹ ℓ+1 ≤ ℓ+ℓ²/25 (true ℓ≥5).

## Exact-testable claims (gated by Claude)
- BLOCK-SBC per K-component (the reduction's core) — full battery + two-lane + blown-up two-lane.
- BUNDLE-SBC (1D) over (ℓ, n_i, m) ranges.
- block-diagonality of O over K-components; O_bun = B_Hᵀ B_H + cJ identity.
- adversarial counterexample hunt for BLOCK-SBC.
**NOT gate-provable:** the hot-core compression lemma (§3) — the remaining open analytic step.

## Relation to Codex PATH-LRS-2/3
Codex's per-path lemma (1/ℓ_f)Σ_{v∈P}T[v] ≤ N + (2/3)(N²/25−m) is theorem-sufficient by the same Cauchy argument
(ΣT²/Γ ≤ N+(2/3)D; D<0 ⟹ contradiction). Likely the per-path twin of BLOCK-SBC (both = load-average + bad-count slack).
