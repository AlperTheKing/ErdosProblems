# Peel Invariant (SH′) — boundary-field version (GPT-Pro, 2026-07-02) — Branch B

Status: Lemma 1 + Lemma 2 PROVEN (exchange argument; min-cex induction on the GRAPH only).
Supersedes the bare §H hypothesis m_out ≤ r²/25 of CACTUS_PACKING_LEMMA_GPTPRO.md, which is
NOT cut-carried unless d = 0. Branch-B assembly now rests on ONE obligation: peel form (3.1).

Notation: U = ∪ selected protected cells (k cells, |C|≥10, e_M=2, δ_M=0, pairwise ≤1 shared
vertex), R = V∖U, r = |R|, m_out = e_M(R) (bad edges inside R), d = |δ_B(U,R)| (blue boundary;
δ_M(U)=0 kills bad boundary). η = N²/25 − m. Σ_L = (L²−25)/50.

## Lemma 1 (SH′) — the cut-carried invariant
Under minimal-counterexample induction (β(H) ≤ |H|²/25 for all |H| < N):
  **m_out ≤ r²/25 + d/2.**
Proof (exchange, two orientations): G[R] triangle-free, r < N ⟹ ∃ coloring ψ of R with
≤ r²/25 bad edges inside R. Extend to G keeping U fixed. Every U↔R boundary edge is blue in
the current cut (δ_M(U)=0); under exactly one of ψ, ψ̄ (complement on R) a given boundary
edge becomes bad ⟹ b(ψ) + b(ψ̄) = d ⟹ min ≤ d/2; bad-inside-R invariant under complement.
Modified cut ≤ e_M(U) + r²/25 + d/2 bad edges; current = e_M(U) + m_out; maximality (max cut
minimizes bad) forbids improvement ⟹ m_out ≤ r²/25 + d/2. ∎

Hypothesis usage: triangle-freeness → G[R] tri-free only; induction → β(G[R]) ≤ r²/25 (NO
assumption on the inherited cut — Guardrail 1 avoided; no recursion on cut pairs /
B-connectivity / gamma-min — Guardrail 3 avoided); maximality → the exchange comparison;
δ_M(U)=0 → (i) no bad boundary now, (ii) each boundary edge flips under exactly one
orientation (Guardrail 2 repaired: loss ≤ d/2, paid by the d-credit in the ledger).
Gamma-minimality: NOT needed here (upstream cell selection only). Protector lengths: not used.

## Lemma 2 — half-bank replacement
With the archived cactus packing (N²−r²)/25 ≥ 4k:
  η = N²/25 − 2k − m_out ≥ (N²−r²)/25 − 2k − d/2 ≥ 2k − d/2,
  ⟹ η/2 ≥ k − d/4 ⟹ **k − d ≤ η/2** (since k−d ≤ k−d/4 for d ≥ 0).
d = 0 recovers the old half-bank k ≤ η/2 exactly.

## Final assembly — the ONE remaining Branch-B obligation
  (3.1)  **R_Q ≤ N − Σ_L + k − d**   [peel-side form, d = FULL external blue boundary of U]
  ( = R_Q ≤ N − Σ_L + |Π_cell| + |Π_fan| − |δ_B(U,R)| with |Π_cell|+|Π_fan| = k )
Then Lemma 2: k − d ≤ η/2 ⟹ **R_Q ≤ N + η/2 − Σ_L** = GERSH_{L>5} target. ∎
No double counting: the ledger uses only the single combined term k − d; the d-credit both
absorbs fan-exposed precharges AND pays the ≤d/2 recut boundary loss.
(3.1) REPLACES (6.1) of LEDGER_INTERFACE_GPTPRO.md (sharpened: door credit → full blue
boundary d of the peeled union). STATUS: Codex reported (18:37Z) NO existing gate computes the
(6.1)-type ledger; (3.1) needs a new extraction script or a written derivation from the
SLACK-CAGE row-bank algebra. THIS IS THE CRITICAL PATH.

## Claude gate obligations
1. Witness instances with m_out > 0 (nonempty R carrying bad edges) — REQUIRED since all 11
   cactus-gate instances have m_out = 0:
   atom+C5 disjoint (N=15, k=1, m_out=1, d=0: SH′ TIGHT 1 ≤ 1);
   atom+C5 blue-bridged (N=15, k=1, m_out=1, d=1: 1 ≤ 3/2).
2. Verify exchange mechanics exactly on witnesses: β(G[R]) exact, b(ψ)+b(ψ̄)=d, min ≤ d/2,
   maximality comparison.
