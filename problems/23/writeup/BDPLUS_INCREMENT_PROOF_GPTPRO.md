# Cert B (BD+) — Increment-Lemma Proof (GPT-Pro, 2026-07-03)

Status: (BD+) reduced RIGOROUSLY to H_BD (clean local hypothesis) with H_BD-exact as fallback
finite certificate. The increment lemma is PROVEN (maximality). Naked-stack case routed.

## Increment Lemma (Inc) — PROVEN
W ⊇ V(Q) a packet; A = K∖V(Q) the off-row part of a positive component not yet included,
s=|A|, r=|V∖W|. KEY (2.1): K is a component of G_B−E_Q^B and W ⊇ all row vertices ⟹ NO blue
edges from A to V∖(W∪A) ⟹ blue boundary increment is only b_in = e_B(A,W). With π_A=e_M(A),
π_in=e_M(A,W), π_out=e_M(A,V∖(W∪A)):
  B(W∪A) − B(W) = (2rs−s²)/25 − π_A − π_in/2 − π_out/2 − b_in/2 + (h-terms)   (Inc)
Max-cut slack of A: σ(A) = b_in − π_in − π_out ≥ 0 ⟹ the boundary group ≥ −e_M(A)-adjusted:
  **(Inc-LB)  B(W∪A) ≥ B(W) + (2rs−s²)/25 − e_M(A).**
"Adding a full positive blue-detour component contributes its full quadratic capacity; the
possible bad-boundary loss is paid by the max-cut slack of A."

## H_BD ⟹ BD+ — PROVEN (telescoping, order-irrelevant)
  (H_BD)  B(V(Q)) + [(N−L)² − r_Q²]/25 − Σ_{K∈P_Q} e_M(A_K) ≥ 2Σ_L + 2U_Q^+
Summing (Inc-LB) over any ordering: B(W_Q) ≥ B(V(Q)) + [(N−L)²−r_Q²]/25 − Σ e_M(A_K) ⟹ BD+.
Terms: bare-row bank + donated quadratic capacity − off-row internal bad cost ≥ reserve+demand.

## H_BD-exact (fallback finite certificate, §5)
B(V(Q)) + Σ_j Δ_j ≥ 2Σ_L + 2U_Q^+ with explicit per-component increments Δ_j (max-cut slack
term (b_in−π_in−π_out)/2 visible). Hierarchy: H_BD ⟹ H_BD-exact ⟺ BD+.

## NoNaked (§6)
A positive component K ⊆ V(Q) (no off-row vertices) is a "naked stacked row segment" —
donates no capacity. For NoCell-BD: assume (NoNaked) σ_Q(K)>0 ⟹ K∖V(Q) ≠ ∅; if it fails,
route to max-cut-improving flip / decreasing neutral switch / protected-cell descent ledger.

## Hypothesis usage (§7)
Triangle-freeness: Q induced shortest odd cycle; components can't shortcut (else Q not
shortest); induction for packet exchange. Shortestness: positive components are legitimate
detours. Maximality: EXACTLY in (Inc-LB)'s σ(A) ≥ 0. [Gamma-min: descent routing.]

## ⚠ SCOPE AMENDMENT (Claude, from N=11 census)
N=11 has 71 L>5 rows where (BD-UPO full-U) fails but ALL are UNDERFULL (R_Q−N=−4/3 samples,
Banked-UPO holds on all 71, no other bad edge in positive components) — pure decomposition
lossiness: negative components' deficits discarded by U^+. CORRECT SCOPING: (BD+)/H_BD needed
only on OVERFULL rows (R_Q>N); underfull rows reduce to Bank-L. Overfull-restricted census
N=7..11 verdict pending (_claude_bd_overfull_scope.py).

## Machine obligations after this
1. (Bank-L) via LCB descent (Codex wiring). 2. H_BD on overfull rows (or H_BD-exact per-row
certificates). 3. NoNaked routing. My gates: overfull scope + H_BD census check next.
