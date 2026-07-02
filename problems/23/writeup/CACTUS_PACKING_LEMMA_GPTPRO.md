# Cactus-Packing Discharge Lemma (GPT-Pro, 2026-07-02) — Branch B

Status: statement + proof COMPLETE modulo one scoped hypothesis (the peel invariant, §H below).
Arithmetic exact-verified by Claude. This is the Branch-B protected-cell discharge.

## Setting
Selected protected cells C_1..C_k in a B-connected gamma-minimal maximum cut:
|C_a| ≥ 10, e_M(C_a) = 2, δ_M(C_a) = 0, pairwise |C_a ∩ C_b| ≤ 1 (cactus).
U = ∪C_a, u = |U|, R = V∖U, r = |R|, m_out = #{bad edges ⊆ R}.

## §1 Bad-edge accounting (exact)
δ_M(C_a)=0 ⟹ no bad edge crosses U↔R (endpoint in C_a forces the other endpoint in C_a).
A bad edge in two cells would put BOTH endpoints in C_a∩C_b ⟹ |C_a∩C_b| ≥ 2, contradiction.
⟹ e_M(U) = 2k and  **m = 2k + m_out**  (identity 1).

## §2 Gross packet (pairwise cactus suffices)
Pairwise ≤1 sharing ⟹ vertex-PAIRS inside cells are disjoint subsets of C(U,2):
Σ_a C(|C_a|,2) ≤ C(u,2); |C_a|≥10 ⟹ 45k ≤ u(u−1)/2 ⟹ u² ≥ 90k.
(N²−r²)/25 = (u²+2ur)/25 ≥ u²/25 ≥ 90k/25 = 18k/5 > 3k.
With the outside allocation m_out ≤ r²/25 (§H):
  m_out + 3k ≤ r²/25 + (N²−r²)/25 = N²/25   ⟹  **k ≤ η**  (gross: 2 internal bad edges + 1
  UNIT-FLAT5 precharge = 3 per cell).

## §3 Half-bank packet (contact-forest)
Proper cactus order (cell/contact incidence graph a forest): each contact component with k_α
cells has union ≥ 10 + 9(k_α−1) = 9k_α+1; summing over c components: u ≥ 9k + c ≥ 9k+1.
(9k+1)² − 100k = 81k²−82k+1 = (k−1)(81k−1) ≥ 0 for k ≥ 1   [verified]
⟹ u²/25 ≥ (9k+1)²/25 ≥ 4k ⟹ m_out + 4k ≤ N²/25 ⟹  **k ≤ η/2**  (HB).
HB is exactly the form the L>5 long-surplus needs: R_Q ≤ N + η/2 − (L²−25)/50, with the
(L²−25)/50 length surplus untouched by the packing.

## §4 Why not Σ|C_i|²/25
Summing per-cell squares double-counts shared vertices. Correct accounting: reserve r²/25 for
m_out; pay cell packets from the remaining (N²−r²)/25, bounded below via the union u.

## §H THE SCOPED HYPOTHESIS (the remaining Branch-B work)
m_out ≤ r²/25 is the PEEL INDUCTIVE INVARIANT, and it is NOT the naive β-induction:
the restriction of the max cut to G[R] need not be a max cut of G[R], so β(G[R]) ≤ r²/25 gives
m_out ≥ β(G[R]) — the WRONG direction. The SLACK-CAGE recursion must carry the invariant on the
CUT (same cut, smaller instance): δ_M(C)=0 keeps the restricted cut's bad-edge set exactly
{bad edges ⊆ R}, and the peel must show the restricted instance (R, restricted cut) still
satisfies the hypotheses that drive the discharge (B-connectivity after peel, gamma-minimality
surrogate, or a direct surplus bookkeeping). Codex to scope; Claude to gate on generated
cactus families (k=1..8 gluings, n=19 single-vertex contact).

## Remaining Branch-B checklist
1. Peel invariant §H (recursion scoping) — Codex.
2. ~~Fan lemma~~ DONE 2026-07-02 (FAN_LEMMA_GPTPRO.md — boundary form on completed fan closure);
   successor obligation = LEDGER INTERFACE (§A there) — GPT-Pro consulted.
3. ~~Claude: exact gate of §1-§3~~ DONE 2026-07-02: _claude_cactus_family_gate.py PASS on 11
   instances (disjoint k=1..8, contact-pair n=19, triple-chain n=28, mixed n=29); all exact,
   true max cut certified per instance via per-copy decomposition bound + 2^10 atom enumeration;
   u≥9k+c TIGHT on every tree gluing; k≤η/2 tight at k=1 exactly as (k−1)(81k−1)=0 predicts.
