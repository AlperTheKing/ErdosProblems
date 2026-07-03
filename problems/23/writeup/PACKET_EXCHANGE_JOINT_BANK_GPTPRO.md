# Packet Exchange Inequality + Corrected Branch-B Chain (GPT-Pro, 2026-07-02)

Status: resolves the (3.1) normalization failure (Codex C7 audit). Σ_L is a BANK RESERVATION,
not a local subtraction. New general tool: the packet exchange inequality (1.4). Branch-B's
single remaining machine obligation = Banked-UPO (Mode A below).

## §1 PACKET EXCHANGE INEQUALITY (SH′ generalized — h > 0 allowed)
Any packet W ⊆ V on a gamma-min max cut, R = V∖W, r=|R|: p = e_M(W), h = |δ_M(W)|,
d = |δ_B(W)|, m_R = e_M(R); m = p + h + m_R (1.1). Min-cex induction (β(G[R]) ≤ r²/25) +
two-orientation exchange over the d+h boundary edges (exactly one orientation makes each bad;
better one ≤ (d+h)/2) + maximality:
  (1.3)  m_R + h/2 ≤ r²/25 + d/2
  (1.4)  **η ≥ (N²−r²)/25 − p − d/2 − h/2**
SH′ cell lemma = h=0 special case. This converts induction+maximality into quadratic-capacity
statements for ANY packet with controlled boundary.

## §2 Joint bank (JB) — corrected form of my η ≥ 2Σ_L + 2(k−d) candidate
W = joint packet (row packet ∪ k selected cells). s_W = (N²−r²)/25 − (L²/25 + 4k) [joint
packing surplus]; q_W = p − (1+2k) [extra internal bad burden]. Using L²/25 − 1 = 2Σ_L:
  (2.3)  η ≥ 2Σ_L + 2(k−d) + (s_W + 3d/2 − q_W − h/2)
  (JB)   η ≥ 2Σ_L + 2(k−d)  VALID WHENEVER  (J res): s_W + 3d/2 ≥ q_W + h/2.
Clean sufficient package: h=0 (bad-saturated W), q_W=0 (only internal bad = row edge + 2k),
s_W ≥ 0 (joint packing (N²−r²)/25 ≥ L²/25 + 4k). C7: equality throughout (η=24/25=2Σ_7).

## §3 Bare row cycle UNSAFE (my flagged caution confirmed)
δ_M(V(Q))=0 is NOT automatic — outside bad edges may touch row vertices; the h/2 penalty in
(1.4) is the price. Correct row packet: bad-saturated (h=0) or certify (J res) explicitly.

## §4 Corrected residual ledger
Row excess E_Q = R_Q − N = U_Q + Δ_Q:
  U_Q = pure-cycle/unprotected surplus (present even with no cells) — paid by the fractional
        baseline bank η/2 − Σ_L. NOT paid by cells/doors. (Why old (3.1) failed.)
  Δ_Q = cell-door residual ≤ k − d (via Π_cell ≤ k, Π_fan ≤ |D_u| fan union).
Per-row target (= the existing gate): **(Banked-UPO) R_Q ≤ N + η/2 − Σ_L.**

## §5–6 Integration modes + corrected final chain
MODE A (direct, CLEANEST): Codex proves peel-side Banked-UPO directly ⟹ Branch B closes
immediately; fan/cactus/SH′/packet are internal machinery. ONE machine gate.
MODE B (split): needs BOTH (5.1) Pure-UPO U_Q ≤ η/2 − Σ_L − (k−d) AND (5.2)=(JB). Even with
(JB), the per-row Pure-UPO statement is still required — no escape from a per-row argument.
Corrected chain: peel decomposition + fan union + Δ_Q ≤ k−d + (JB under J res) + Pure-UPO
⟹ Banked-UPO ⟹ R_Q ≤ N + η/2 − (L²−25)/50 = GERSH_{L>5}. ∎

## Stress compatibility (asserted; my gates to verify)
C7: U_Q=0, Δ_Q=0, bank=0 — equality. k=0 attachment rows: U_Q>0 paid by bank. W1-W4: packet
formula with h=0 for cell-only packets. Two-lane L=12 + glued cactus: fan/cactus controls
ONLY Δ_Q; the final gate must be residual-normalized Banked-UPO, never N − Σ_L + k − d.

## Bottom line / ownership
- (1.4) packet inequality: PROVEN (gate it — my job, _claude_packet_exchange_gate.py).
- (JB): proven UNDER (J res) — per-instance certification needed where used.
- **THE remaining Branch-B machine obligation: Banked-UPO per-row (Mode A)** — the peel-side
  proof that R_Q ≤ N + η/2 − Σ_L; equivalently Pure-UPO for the U_Q part. Codex owns the peel
  algebra; GPT-Pro next consult = Pure-UPO design (k=0 core: what bounds attachment surplus).
- Battery status: Banked-UPO HOLDS on 196 rows (min margin 0 at C7[1]) + descent 21+1135
  sides 0 fail (Codex, reproduced by me digit-exact). Battery ≠ proof.
