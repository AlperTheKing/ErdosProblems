# Top-level assembly and the δ=0 theorem (GPT-Pro SIBLING, 2026-07-07)

TRANSCRIBED (head+mid+tail, symbol-decoded, faithful). The manuscript's main-theorem completeness
certificate — assembles Branch-A + Branch-B + the deduction to β ≤ N²/25 and the FC bridge. Companion to
BRANCH_A_COMPLETENESS_GPTPRO.md + BRANCH_B_BANKED_UPO_ASSEMBLY_GPTPRO.md.

## Setup
G finite triangle-free on N vertices; B = B-connected maximum cut chosen Γ-minimal among B-connected max
cuts; M = bad edges, m = |M|; η = (N²−25m)/25. For bad edge f: ℓ(f) = shortest-row length, cyc(f) =
certified shortest rows, ROWSUM(f) = max_{Q∈cyc(f)} I(Q). GERSH target: ROWSUM(f) ≤ N + η for every f.
Scalar bank input: Branch-A consumes η ≥ 0 (Bank0 pure-L5 / Bank-L longer positive row).

## GERSH aggregation lemma (exact token-charging)
Under the hypothesis ROWSUM(f) ≤ N + η for every bad edge f:
    Σ_{f∈M} (ℓ(f)² − 25) ≤ 25·η.
The row database supplies a finite token set per bad edge f of cardinality ℓ(f)²−25, and an EXACT charging
map from those excess-length tokens to the row-sum slack budget. Summing over all bad edges, the total
charged amount is bounded by the global bank 25η = N²−25m. All row-token identities are LCM-cleared finite
identities in the Row/Gamma layer. The ONLY analytic input to the aggregation is the GERSH inequality
ROWSUM(f) ≤ N+η. Hence Σ_{f∈M}(ℓ(f)²−25) ≤ 25η, i.e. Γ(B) = Σ_f ℓ(f)² ≤ N².

## Deduction chain to β ≤ N²/25
- row/Gamma aggregation: GERSH ⟹ Γ(B) ≤ N².
- Γ(B) ≤ N² ⟹ 25m ≤ N².
- m = β(G) for a maximum cut.
- componentwise summation for disconnected graphs.
- the formal-conjectures bipartization bridge (β ≤ N²/25 ⟹ official erdos_23 ∃-bipartite-subgraph shape;
  PROVEN unconditional in Lean: beta_bipartization + erdos23_fcForm_of_bipartization).

## Complete finite-certificate-family dependency list
BRANCH A: six A1 ConeCerts M0-M5; PMTS slack dictionary; Seed3 ODL route trees; ODL semantic core + internal
excess-monotonicity links; CONE/Bank/Lens/NoOverfull terminal leaf providers; O14 EQ chart cover (108 rows);
seed + quotient well-formedness certs.
BRANCH B: OP5 transfer; fan ledger; CACTUS LEDGER using the PROVEN SH' peel invariant (m_C ≤ r_C²/25 + d_C/2,
two-orientation exchange); SH-prime peel; cell ledger; CombinedHBD single-spend certificate; PacketExchange;
DOOR-OWNERSHIP WIRING for the cactus d_C/2 credits; Banked-UPO assembly.
TOP-LEVEL DEDUCTION: row/Gamma aggregation (GERSH⟹Γ≤N²); Γ≤N²⟹25m≤N²; m=β for max cut; componentwise
summation; the FC bipartization bridge.

## Decisive completeness statement (verbatim-faithful)
"No open extremal inequality remains. The remaining non-deductive inputs are finite certificate artifacts and
their checker soundness theorems. Validation and census runs are annotations only; they are not used as proof
steps. The mathematical proof reduces to the enumerated finite certificate families above plus the Lean formal
deduction skeleton."

## Status (Claude, 2026-07-07)
This is the anti-fake-progress-compliant framing: the WHOLE proof is reduced to finite certificate DATA
(Codex generates + I exact-verify) + the compiled Lean deductive skeleton (11 green increments this session:
a1Proper reduction + full odlFull provider framework + FC bridge + assembly stages + checker suite). The
remaining OBLIGATIONS are all finite certificate families: six A1 cones (Codex PMTS), 108 chart cover / O14
(Codex k6/F6 reproduction from 22-family pool), Branch-B door-ownership wiring (Codex), per-row odlFull
payloads (Codex), + the payload-checker Lean build (pending MAIN rowSum-binding confirmation). No open
extremal inequality; no falsifier.
