# Blue-Detour UPO (GPT-Pro redesign after BSH refutation, 2026-07-03) — Branch B core

Status: replaces the REFUTED row-local Hall transport (BSH). Supply enlargement is CANONICAL:
the blue component of each row vertex after deleting the row's own blue edges. Both
calibrations exact (pure C_L tight; two-lane easy). New machine target = (BD-Packet).

## Construction
Row Q (L≥5 shortest row of bad edge f), E_Q^B = blue edges of Q. H_Q = G_B − E_Q^B;
B_Q = components of H_Q (isolated vertices included ⟹ Σ_K |K| = N).
T_Q(K) = Σ_{q_i ∈ K∩Q} Tw_C(q_i) (row load content); surplus σ_Q(K) = T_Q(K) − |K|;
U_Q^+ = Σ_K (T_Q(K) − |K|)_+.

## (1) Algebraic decomposition (Lemma 1 — no spectral/width/class-size)
R_Q = Σ_K T_Q(K), N = Σ_K |K| ⟹ **R_Q − N ≤ U_Q^+**. Purely algebraic.

## (BD-UPO) U_Q^+ ≤ η/2 − Σ_L ⟹ Banked-UPO.
Each load unit at q_i may route to the WHOLE blue-detour component of q_i, not merely its own
shortest path — the smallest natural enlargement that: (i) is tight on pure C_L (row-edge
deletion isolates row vertices, U_Q^+=0=bank); (ii) sees arbitrary-length protectors/lanes
(no fixed-length trap); (iii) is max-cut compatible (boundary of component unions = row blue
edges + exposed bad edges — exactly the packet-exchange terms).

## Two-lane p198 verification (the BSH killer, now easy)
Deleting the x-path row edges leaves G_B connected THROUGH THE LANES ⟹ one component K=V:
T_Q(V) = R_Q = 28, |K| = 27 ⟹ U_Q^+ = 1 ≤ η/2 − Σ_9 = 573/50 ✓. The lanes absorb stacking.

## (BD-Packet) — the finite certificate (Lemma 2)
Canonical packet W_Q = V(Q) ∪ ∪{K : σ_Q(K) > 0} (row included even with no positive
components — needed for pure-cycle equality). With p, h, d, r of W_Q and
B(W) = (N²−r²)/25 − p − (d+h)/2:
  **(BD-Packet)  2(U_Q^+ + Σ_L) ≤ B(W_Q)**
Packet exchange (Lemma 3, accepted): η ≥ B(W) ⟹ (BD-UPO) ⟹ Banked-UPO (Lemma 4, k=0 branch).
Calibrations: pure C_L: W_Q=V, B = L²/25 − 1 = 2Σ_L, LHS = 2Σ_L — TIGHT. Two-lane: W_Q=V,
B = η = 629/25, LHS = 2(1+28/25) = 106/25, margin 523/25 = 2× the row margin ✓.

## Cell versions (§ Cell)
First machine target: **(NoCell-BD-Packet)** — k=0 rows (isolates exactly the obstruction
that killed BSH; must pass two-lane). Full assembly: (Cell-BD-Packet)
2(U_Q^res + Δ_Q + Σ_L) ≤ B(W_Q^res) with Δ_Q ≤ k−d from the archived fan/cactus ledger,
W_Q^res = row ∪ positive residual components ∪ selected cell closures.

## Certificate computation recipe (§ Cert — Claude gate + Codex engine)
Per row: delete row blue edges → components → T_Q, σ_Q, U_Q^+, W_Q → p,h,d,r → check the
rational inequality; classify failures (protected cell / fan-cactus residual / negative flip).

## ✔/✘ CLAUDE GATE VERDICT (2026-07-03, _claude_blue_detour_gate.py + _claude_bd_split_count.py)
census N≤10 all gamma-min B-conn cuts × all rows + C7/C9/C11 + two-lane + W1/W2/W4:
- **(BD-UPO) U_Q^+ ≤ η/2 − Σ_L: 0 FAILURES on ALL L>5 rows** (N=7:7, N=8:17, N=9:175,
  N=10:1210 rows; two-lane 3 L>5 rows incl. R_Q=28; cycles tight). THE STATEMENT IS
  CENSUS-TRUE on Branch-B scope. (L=5 upo-failures exist only at protected-cell graphs —
  incl. the base atom I?AAD@wF_ U_Q^+=2>η/2=1 — k≥1, out of NoCell scope, Branch-A territory.)
- **(BD-Packet) canonical-W_Q: REFUTED as stated** — L>5 failures N=8:10, N=9:122, N=10:1018,
  BUT the split is PERFECT: **every failure has U_Q^+ = 0** (zero failures with positive
  surplus). At U=0 the inequality reads 2Σ_L ≤ B(V(Q)) which is false when the bare row's
  boundary eats the bank (e.g. G?bB`o L=7: B=13/25 < 24/25); yet W=V gives B(V)=η and
  η ≥ 2Σ_L held on every census row. The canonical packet is simply the wrong witness at U=0.

## CORRECTED MACHINE OBLIGATIONS (census-clean target set)
1. **(Bank-L)**  η ≥ 2Σ_L  ⟺  m ≤ (N²−L²+25)/25  for every L>5 row on a gamma-min max cut
   [tight at pure C_L; = the joint-bank k=0 case; candidate proof = (J res) clean package on
   the bad-saturated closure of the row cycle].
2. **(Surplus-Packet)**  2(U_Q^+ + Σ_L) ≤ B(W_Q)  for rows with U_Q^+ > 0
   [census 0-fail N≤10 + two-lane 0-fail — the canonical packet works exactly where needed].
3. Cell insertion (k>0): archived fan/cactus ledger (Δ_Q ≤ k−d).
