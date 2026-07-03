# Pure-UPO via Fractional Hall Transport (GPT-Pro, 2026-07-03) — Branch B final core

## ⛔ STATUS: (BSH) REFUTED 2026-07-03 by Claude gate (_claude_nocell_pu_gate.py) on the
## two-lane p198 instance (n=27, m=4, unique max cut): at Y = V(Q) = the x-path {0..8},
## ALL FOUR bad edges' shortest paths lie inside Y ⟹ D_Q(Y) = R_Q = 28, |Y| = 9, defect 19;
## BSH needs defect ≤ η/2 − Σ_L = 573/50 ≈ 11.46 — FALSE by 2(19+28/25) = 1006/25 vs
## η = 629/25. 590 violating packets found (structured + LCG). Banked-UPO itself HOLDS there
## (margin 523/50) — the Hall reduction (Lemma A) is sufficient-NOT-necessary and overshoots:
## routing all row-atom mass into supply-set-local capacity is infeasible when nested bad
## edges stack mass 28 onto 9 row vertices, yet R_Q ≤ N + bank is still true. The transport
## model needs off-supply capacity (the 18 slab vertices) or a different mechanism entirely.
## TENTH TRAP: row-local Hall transport (BSH) — two-lane kills it. C7/C9/C11 + W1/W2/W4 were
## clean (0 positive-defect failures); the killer = multiple nested bad edges on one row.
## SURVIVES: packet exchange (1.4) (exhaustively gated), Banked-UPO as target, the E_Q =
## U_Q + Δ_Q ledger split, canonical-packet machinery (reusable). DEAD: (BSH)/(PU-packet)/
## (NoCell-PU) as stated. Redesign consult sent to GPT-Pro.

Status (original claim, now refuted as stated): proof ARCHITECTURE complete; THE one genuinely
new machine obligation = (NoCell-PU). Non-spectral, non-pointwise — "survives two-lane by
design (no ρ ≤ N anywhere)" — WRONG: two-lane kills the transport quantifier instead.

## Row atom measure
For the L>5 row Q of bad edge f: atoms α=(g,P,i), g∈M_C, P∈cyc[g], q_i∈V(P); weight
w(α)=|cyc g|⁻¹; supply set V(P). Total row mass = R_Q = Σ_{v∈Q} Tw_C(v) (Claude checked:
D_Q(V) = Σ_g Σ_{v∈Q} p_g(v) = R_Q ✓; and ROWSUM(f) = |cyc f|⁻¹ Σ_{Q∈cyc f} R_Q ≤ max R_Q, so
the per-row bound suffices for GERSH).

## §1 Fractional Hall reduction (Lemma A — pure LP duality)
D_Q(Y) = Σ_g |cyc g|⁻¹ Σ_{P: V(P)⊆Y} |V(P)∩V(Q)| (atom mass with supply entirely inside Y).
R_Q ≤ N + max_Y (D_Q(Y) − |Y|)_+. Hence Banked-UPO follows from
  (BSH)  D_Q(Y) ≤ |Y| + η/2 − Σ_L   for every Y ⊆ V.

## §2 Local packet certificate
B(Y) = (N²−r_Y²)/25 − e_M(Y) − (|δ_B(Y)|+|δ_M(Y)|)/2  [= packet-exchange lower bound: η ≥ B(Y)].
  (PU-packet)  2(D_Q(Y) − |Y| + Σ_L) ≤ B(Y)  ⟹ BSH [via η ≥ B(Y)].
Pure C_L, Y=V: D_Q=L=|Y|, e_M=1, r=d=h=0: B(V) = L²/25−1 = 2Σ_L — TIGHT (matches C7/C9).
Y=V in general: (PU-packet) ⟺ Banked-UPO itself (B(V)=η).

## §3 k=0 interpretation
Attachment surplus is paid by the GROWTH of the packet-exchange bank (N²−r_Y²)/25 as packets
absorb attachments — not by doors, not by cells.

## §4 Canonical packet reduction (Lemma B — machine-checkable closures)
Minimal violating packet may be assumed: (1) row-closed (whole rows only — built into D_Q);
(2) row-CONVEX (missing subpath insertion only improves boundary terms); (3) terminal-shadow
closed (a row entering/leaving/re-entering Y: closing the gap either keeps D_Q−|Y| or creates
a negative flip, contradicting maximality); (4) noncrossing (uncross terminal intervals;
triangle-freeness + shortestness); (5) UNIT-FLAT5 extraction (positive atoms → protected
cells → fan/cactus ledger; residual has no unprotected UNIT-FLAT5 obstruction).

## §5 Lemma skeleton
A: Hall reduction (LP duality). B: canonical reduction. C: RESIDUAL PACKET INEQUALITY — for
canonical Y with NO selected cells: 2(D_Q(Y) − |Y| + Σ_L) ≤ B(Y) [the pure k=0 UPO atom].
D: selected precharge insertion — with cells, demand = residual + 2·precharge; precharge paid
by fan-union + cactus/SH′ (k−d ≤ η/2) or (JB) under (J res). E: packet exchange η ≥ B(Y).
C+D+E ⟹ BSH ⟹ Banked-UPO ⟹ GERSH_{L>5}.

## §6 Two-lane
Route needs no ρ≤N; two-lane margin M(Q) = N + η/2 − Σ_12 − R_Q must be computed exactly
(Claude gate). Lane packets must have enough outside capacity or bank — testable.

## §7-9 THE intermediate target = (NoCell-PU)
  (NoCell-PU)  2(D_Q(Y) − |Y| + Σ_L) ≤ B(Y) for every NO-CELL canonical packet Y.
Certificate computation (§8, Codex): enumerate row-convex terminal-shadow canonical packets;
compute (D_Q, |Y|, e_M(Y), δ_B, δ_M, r_Y); check the rational inequality; classify failures
(protected cell / fan-cactus residual / gamma-descent / negative flip); ONLY allowed
survivors = selected protected UNIT-FLAT5 atoms (paid by Branch-B ledger).

## ⚠ CLAUDE REFINEMENT (2026-07-03, from the C7 empty-packet failure)
(PU-packet) is FALSE at defect-free packets: Y=∅ on C7 gives LHS=2Σ_L=24/25 > B(∅)=0. The
correct quantifier split: (i) POSITIVE-DEFECT packets (D_Q(Y) > |Y|): (PU-packet) with Y's own
bank B(Y); (ii) defect ≤ 0 packets: BSH(Y) reduces to BANK NONNEGATIVITY η ≥ 2Σ_L — which is
exactly the (JB) k=0 statement, needing the JOINT row-packet argument ((J res) with the
bad-saturated row closure W: h=0, q_W=0, s_W≥0), NOT the local bank. So the machine
obligations are TWO: (NoCell-PU restricted to positive-defect canonical packets) AND
(η ≥ 2Σ_L via the joint row packet). At C7 both are tight/equalities.

## ⚠ Claude gate notes (traps)
- DW-Hall trap check: this is a DIFFERENT Hall statement (bank = quadratic packet-exchange
  capacity, not recip-slack widths). Still: exhaustive-subset gates BEFORE trusting;
  two-lane + p198 n=27 instance (R_Q=28>N=27 row!) mandatory.
- (PU-packet) at Y=V IS Banked-UPO — so the packet form is a strict strengthening; if it
  fails at some sub-packet while Y=V holds, only the LOCAL certificate route dies, not
  Banked-UPO itself. Classify which.
