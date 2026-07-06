# Branch-B final assembly: cell ledger + CombinedHBD + PacketExchange + Banked-UPO (GPT-Pro SIBLING, 2026-07-06)

TRANSCRIBED from the SIBLING thread (6a45e152), symbol-transform-decoded (@EQ@→=, @PL@→+,
@LT@→<, @GT@→>, @AM@→&). Structural/formula-faithful; base-draft re-emission section for repo
archiving. Companion to BRANCH_B_WRITEUP_GPTPRO.md / PACKET_EXCHANGE_JOINT_BANK_GPTPRO.md.

## Setup
G triangle-free; B = B-connected maximum cut chosen Γ-minimal among B-connected max cuts;
Q ∈ cyc(f) a certified shortest row of a bad edge f with ℓ(f)=L>5. Row contribution R_Q.
η = (N²−25m)/25.  Length reserve Σ_L = (L²−25)/50.  Bank-L later gives η ≥ 2·Σ_L.

## Cell ledger — the E_Q = U_Q + Δ_Q accounting
BlueDetour + PeelSplit + cell ledger give the row inequality
    R_Q ≤ N + E_Q = N + U_{Q,res} + Σ_fan + Σ_cell,   equivalently   R_Q ≤ N + U_Q + Δ_Q.
[CERT: P2 PEELSPLIT; P6 FAN LEDGER; P7 CACTUS LEDGER; P8 SH-PRIME PEEL; P9 CELL LEDGER; P5 OP5 TRANSFER]
This is ONLY an accounting decomposition — no bank has been spent yet.

## CombinedHBD as a single-spend ledger
CombinedHBD pays the ENTIRE quantity E_Q + Σ_L = U_{Q,res} + Σ_fan + Σ_cell + Σ_L from a
SINGLE residual packet W_Q^res. The CombinedHBD certificate proves
    2·( U_{Q,res} + Σ_fan + Σ_cell + Σ_L ) ≤ B(W_Q^res).
(Single-spend: the η/2 is spent exactly once, no double-count across fan/cell/L terms.)

## PacketExchange (P11) — separately certified lemma
For ANY packet W with size r=|W| and params p (already-accounted packet bad-edge contribution),
d (door count), h (hole count):
    η ≥ (N²−r²)/25 − p − d/2 − h/2,   equivalently   B(W) ≤ η.
PROOF (two-orientation exchange): for each orientation o∈{+,−} the cert supplies a switch set X_o,
oriented hole/door sets H_o,D_o, and an injection
    25·(M_R ∪ H_o ∪ ∂_B X_o) ↪ (W×W) ∪ 25·(D_o ∪ ∂_M X_o),
counting which gives  25·m_R + 25·h_o + 25·δ_B(X_o) ≤ r² + 25·d_o + 25·δ_M(X_o).  [CERT: P11 PACKETEXCHANGE]

## Banked-UPO conclusion
Combining: R_Q ≤ N + η/2 − Σ_L (via CombinedHBD 2(…)≤B ≤ η), then Bank-L (η ≥ 2Σ_L) gives
    R_Q ≤ N + η.
Since Q ∈ cyc(f) was arbitrary,  ROWSUM(f) ≤ N + η  for every bad edge f with ℓ(f)=L>5.

## ⭐ HARD-CORE PURE-UPO STATUS (decisive — answers the standing open-crux question)
"The final proof does NOT use an unconditional hard-core Pure-UPO theorem at k=0. The statement
U_Q ≤ η/2 − Σ_L for a pure residual k=0 core, WITHOUT a CombinedHBD certificate, is NOT a
standalone theorem in this architecture. Instead the k=0 case is ROUTED THROUGH THE SAME
CombinedHBD mechanism with Σ_fan=0 and Σ_cell=0 (no fan/protected-cell terms). In that
specialization CombinedHBD certifies 2(U_Q + Σ_L) ≤ B(W_Q^res), and PacketExchange gives
B(W_Q^res) ≤ η, thus U_Q ≤ η/2 − Σ_L."

**IMPLICATION**: Branch-B has NO separate open Pure-UPO k=0 obligation. The k=0 core is a
SPECIALIZATION of the certified CombinedHBD + PacketExchange layers. Conjunct-2 therefore reduces
to certifying the named layers (CombinedHBD single-spend, PacketExchange P11, cell/fan/cactus
ledgers P5–P9, CD telescope + 24-signature dictionary) — each already stated as a [CERT: Pxx]
node — NOT to proving a standalone hard-core theorem. (Corrects the earlier "Pure-UPO k=0 = open
hard core" framing in [[erdos23-branchB-fan-cactus-state]].)

## ⭐ CERTIFIED-LAYER INVENTORY (SIBLING msg 15, 2026-07-07) — Conjunct-2 status pinned to ONE obligation
SIBLING's per-node inventory gives the exact PROVEN/CERTIFIED/OBLIGATION status of every Branch-B layer:
```
P5 OP5 transfer   : CERTIFIED (finite injection/counting artifact)
P6 fan ledger     : CERTIFIED (finite injection/counting artifact)
P7 cactus ledger  : CERTIFIED conditional — requires PeelInvariant certificates
PeelInvariant     : OBLIGATION — unless emitted for every cactus peel node    ← THE remaining open item
P8 SH-prime peel  : CERTIFIED (finite peel artifact)
P9 cell ledger    : CERTIFIED conditional — depends on P5, P7, P8 and PeelInvariant
P10 CombinedHBD   : CERTIFIED conditional — single residual packet bank artifact
P11 PacketExchange: PROVEN (two-orientation injection theorem, B(W)≤η)
P12 Banked-UPO    : PROVEN conditional — arithmetic assembly from P10, P11, Bank-L
```
**THE PEELINVARIANT** is the single genuine remaining Branch-B obligation:
    m_out ≤ r_out²/25,
where r_out = size of the peeled OUTSIDE packet and m_out = its bad-edge count under the RESTRICTED
cut. "This is the only nonlocal input to the cactus half-bank inequality." It is an OBLIGATION unless
emitted (certified) for every cactus peel node. Subtlety (memory §H): restriction-of-max-cut ≠
max-cut-of-restriction, so it is NOT a β-induction — the genuine Branch-B open core.
So Conjunct-2 = {P5,P6,P8 CERTIFIED} + {P11 PROVEN} + {P7,P9,P10,P12 PROVEN/CERTIFIED conditional on
PeelInvariant} + {PeelInvariant OBLIGATION}. Everything reduces to certifying/proving the PeelInvariant.
