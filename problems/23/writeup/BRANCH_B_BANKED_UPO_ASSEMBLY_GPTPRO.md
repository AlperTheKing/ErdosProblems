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

## PEELINVARIANT RESOLUTION (SIBLING, 2026-07-07) — per-node certificate, NOT universal
DECISIVE status of the single remaining Branch-B obligation (transcribed, symbol-decoded, faithful):

NON-UNIVERSALITY (concrete obstruction, C5[t]): balanced blowup C5[t], classes V0..V4 cyclic, |Vi|=t,
max cut = {V0,V2,V4 | V1,V3}. Only bad class-edge is V4V0, so m=t^2 global, cut is maximum. Take outside
packet W_out = V4 ∪ V0: r_out=|W_out|=2t; the inherited restricted cut makes ALL t^2 edges between V4,V0
bad, so m_out=t^2. Then 25*m_out=25t^2 > 4t^2 = r_out^2. So  m_out <= r_out^2/25  is FALSE for arbitrary
outside packets under a restricted maximum cut. Cause: restriction-of-max-cut != max-cut-of-restriction
(inside W_out the inherited cut is NOT a max cut). => the cactus peel invariant CANNOT be a blanket
structural lemma; it is a certified LOCAL BANK FACT for the particular outside packet a cactus peel produces.

PER-NODE CERTIFICATE SCHEMA — PeelInvariantCert(C):
  Data: ambient cut state (G,B,M) with fixed side; cactus peel node C + its outside packet W_out(C)⊆V;
        declared r_out; declared M_out = {uv∈E(G): u,v∈W_out, uv∈M} (M=ambient bad-edge set, restricted
        count under inherited cut); declared m_out=|M_out|; integer inequality cert 25*m_out <= r_out^2.
  Verifier obligations (all EXACT finite checks): r_out=|W_out|; M_out={uv∈E: u,v∈W_out, uv∈M};
        m_out=|M_out|; 25*m_out <= r_out^2.
  Implication: verified => m_out(C) <= r_out(C)^2/25. Proof = divide by 25. Content is NOT a universal
  inequality; it is the exact per-node fact that THIS peel packet has enough size vs its inherited bad edges.
  Symbolic/quotient variant: local quotient model for W_out, polynomials R_out(w)=r_out, M_out(w)=m_out, +
  a ConeCert/Bernstein cert proving R_out(w)^2 - 25*M_out(w) >= 0 on the declared domain; verifier checks
  evaluated R_out,M_out equal the packet size + inherited bad-edge count. For finite artifacts the direct
  integer-count cert is preferred.
  LEDGER: P7 cactus ledger CERTIFIED conditional on PeelInvariantCert(C) for EVERY cactus peel node C;
  P9, P10 CERTIFIED conditional on all required PeelInvariantCerts. Once Codex emits a PeelInvariantCert for
  every cactus peel node and the verifier accepts, the condition disappears; P7/P9/P10 become fully certified.
  => PeelInvariant is PER-NODE CERTIFIED, not universal. Final finite certificate family for Conjunct 2,
  ANALOGOUS TO THE A1 SIX CONES.

⚠ CLAUDE CAVEAT (not overclaiming): the C5[t] W_out=V4∪V0 is an ILLUSTRATIVE ARBITRARY packet (proves
non-universality) — it is NOT shown to be an actual cactus-peel outside packet, so it is NOT a proof
falsifier. BUT validity of 25*m_out<=r_out^2 for the ACTUAL cactus-peel nodes is now an UNVERIFIED
certification obligation: if some actual peel node has 25*m_out > r_out^2, THAT is a falsifier. Whether the
cactus-peel construction STRUCTURALLY GUARANTEES valid packets (peel produces size-dominant W_out) or must
be checked empirically per node is the remaining question (retasked SIBLING). Conjunct-2 closes iff Codex
emits + I exact-verify a passing PeelInvariantCert for every cactus peel node in the Branch-B rows.

## PEELINVARIANT SAFETY (SIBLING structural-guarantee answer, 2026-07-07) — NO guarantee; per-node cert MANDATORY
DECISIVE (falsifier-first, transcribed faithfully):
"The current cactus-peel construction does NOT structurally guarantee the PeelInvariant. It must be treated
as a per-node certified obligation. A genuine cactus-peel node that fails 25*m_out <= r_out^2 would FALSIFY
the current Branch-B/Conjunct-2 proof chain. It would not automatically falsify the THEOREM, but it would
break this proof architecture unless the cactus ledger is replaced or the node is routed through a different
certified bank."
WHY no guarantee: the cactus interface proves only membership/ownership/peel-legality — NOT that the inherited
restricted cut on W_out is maximum, C5-balanced, or Bank0-valid. So 25*m_out<=r_out^2 is NOT a theorem of the
current interface. The C5[t] W_out=V4∪V0 obstruction (25t^2>4t^2) stands. "A genuine cactus-peel node CAN
violate the PeelInvariant unless its node-specific certificate rules it out. A failing node is a DECISIVE
obstruction to the current Conjunct-2 proof."
CONCRETE CLOSURE PATH (Codex): for every cactus peel node C referenced by P7, emit PeelInvariantCert(C) with
data {nodeId(C), (Q,cellId), W_out(C)⊆V, r_out(C), M_out(C)={uv∈E: u,v∈W_out(C), uv∈M}, m_out(C), integer
proof 25*m_out(C)<=r_out(C)^2}; verifier checks W_out(C)=ledger's outside packet, r_out=|W_out|, M_out=restricted
bad set, m_out=|M_out|, 25*m_out<=r_out^2 (all exact finite). PLUS a COVERAGE certificate proving every required
node has a matching verified cert. Q ranges over the finite Branch-B row list. Count: #RequiredCactusPeelNodes
<= #CactusCells × max-peel-nodes-per-cell (exact from artifact manifest).
FINAL STATUS: PeelInvariant NOT structurally guaranteed; MANDATORY per-node cert family; if ANY required
cactus peel node fails 25*m_out<=r_out^2, Conjunct-2 is NOT closed; once every required node passes the exact
check, P7/P9/P10 become fully certified. A future "five-sector size-dominance" theorem for all cactus outside
packets COULD replace the per-node certs but is NOT currently established.
=> Branch-B (Conjunct-2) = CERTIFIED modulo a FINITE PeelInvariantCert family (Codex enumerates+emits, I
exact-verify) + coverage cert. LIVE RISK: a failing node = falsifier of THIS architecture (not yet exhibited;
requires Codex enumeration to check the actual nodes). Routed to Codex 2026-07-07.

## ⚠ RECONCILIATION PENDING (Claude catch, 2026-07-07T02:05Z): bare form vs proven (SH')
The "live risk" above analyzes the BARE PeelInvariant m_out<=r_out^2/25. BUT the peel invariant §H was
ALREADY PROVEN on 2026-07-02 as (SH'): m_out <= r_out^2/25 + d/2, d=|delta_B(U,R)| (blue boundary door
count), via the SAME two-orientation exchange (PEEL_INVARIANT_SHPRIME_GPTPRO.md, gated 4 witnesses; memory
erdos23-branchB-fan-cactus-state item 4). CLAUDE-VERIFIED: the C5[t] W_out=V0∪V4 obstruction (which breaks
the BARE form) SATISFIES (SH'): m_out=t^2, r_out=2t, d=|delta_B(W_out,R)|=(V0-V1)+(V4-V3)=2t^2, so
r_out^2/25+d/2 = 4t^2/25+t^2 = 29t^2/25 >= t^2. TRUE. So the bare-form counterexample is NOT a counterexample
to (SH'). DECISIVE OPEN QUESTION (retasked SIBLING): does the cactus ledger P7 consume BARE or (SH')?
(A) P7 uses (SH') => PeelInvariant PROVEN structurally, NO per-node obligation, NO live Branch-B risk.
(B) P7 needs BARE because the d/2 door credit is ALREADY SPENT (PacketExchange -d/2 / CombinedHBD single-spend)
    => bare per-node obligation + live risk stands. This is a d/2 SINGLE-SPEND accounting question.
=> The Branch-B "live risk" is NOT confirmed; it is PENDING this reconciliation. Do NOT surface it as a
falsifier or a confirmed risk until resolved.

## ⭐ PEELINVARIANT RESOLVED = SH' (SIBLING reconciliation, 2026-07-07) — LIVE RISK DISSOLVED
CLAUDE CATCH CONFIRMED: P7 consumes (SH'), NOT the bare invariant. SIBLING decisive:
"The correct form for the cactus ledger is SH', not the bare invariant: m_out <= r_out^2/25 + d/2, d=|delta_B(U,R)|
(blue boundary door count of peeled outside packet U=W_out vs retained side R). The bare form m_out<=r_out^2/25
is FALSE and must NOT be used by P7. (SH') 50*m_out <= 2*r_out^2 + 25*d is the form PROVED by the two-orientation
exchange — the exact analogue of PacketExchange with a boundary-door term RETAINED instead of discarded. The
C5[t] W_out=V4∪V0 is NOT a counterexample: it violates the bare inequality but SATISFIES SH'."
d/2 SINGLE-SPEND CLEAN: "The d/2 term is not an extra copy of eta/2. PacketExchange has eta>=(N^2-r^2)/25-p-d/2-h/2,
so the packet bank available to CombinedHBD ALREADY contains the door penalty -d/2. A local cactus estimate may
use a +d/2 door credit exactly when that same door is charged once in the packet's global d-term. NOT
double-spending — the same door term on opposite sides of the combined inequality." Ownership condition: each
blue boundary door credited to a cactus node assigned to EXACTLY ONE ledger node, counted once in packet d; no
door doubly used (cactus d_C/2, fan boundary, another cactus, untracked p).
DECISIVE STATUS (SIBLING §5): (1) P7 consumes SH', not bare. (2) SH' structurally PROVED by two-orientation
exchange under cactus peel witness hypotheses. (3) d/2 credit available (PacketExchange pays it via -d/2). (4)
NO Branch-B falsifier from bare C5[t] (only refutes obsolete bare form). (5) Conjunct-2 SAFE provided P7/P9/P10
wired with SH' door-credit ownership check.
REMAINING (finite WIRING checks, NOT new inequalities, NOT a live extremal risk): every cactus peel node
satisfies SH' two-orientation-exchange hypotheses; emitted d_C = |delta_B(U_C,R_C)|; cactus ledger uses SH'
form; door-credit ownership map injective; every cactus-credited door in packet door count d; no cactus door
also spent by fan/another cell.
=> BRANCH-B LIVE RISK DISSOLVED. PeelInvariant = SH' (PROVEN, archived PEEL_INVARIANT_SHPRIME_GPTPRO.md).
Conjunct-2 = certified layers + SH' (proven) + finite door-ownership wiring. SUPERSEDES the bare per-node
PeelInvariantCert framing above. (Claude gate caught SIBLING's bare-form error via the archived SH' proof.)

## BRANCH-B COMPLETENESS STATEMENT (SIBLING, 2026-07-07) — consolidated, SH'-corrected
Final consolidated Branch-B completeness section (transcribed head+tail, faithful):
"The only correction from the earlier draft is that the cactus peel input is the STRENGTHENED peel invariant
m_C <= r_C^2/25 + d_C/2, NOT the bare m_C <= r_C^2/25. The strengthened form is the invariant proved by the
two-orientation exchange. The d_C/2 term is a door credit, paid exactly once by the -d/2 term in PacketExchange."
Final chain: R_Q <= N + eta/2 - Sigma_L; Bank-L gives 25m <= N^2-L^2+25, i.e. eta=(N^2-25m)/25 >= (L^2-25)/25 =
2*Sigma_L; so N+eta/2-Sigma_L <= N+eta; therefore R_Q <= N+eta; since Q in cyc(f) arbitrary, ROWSUM(f) <= N+eta.
DECISIVE: "The Branch-B theorem has NO remaining open extremal inequality. The corrected cactus input is SH',
proven by the two-orientation exchange. The only remaining finite task is the door-ownership wiring certificate
ensuring the cactus d_C/2 credits are counted exactly once in the packet door count d used by PacketExchange."
=> Branch-B (Conjunct-2) = PROVEN modulo the finite door-ownership wiring cert (Codex, routed). Consistent with
the SH' resolution above. No open extremal risk. This is the manuscript Branch-B completeness certificate.
