# Branch-B Final Certificate Architecture: Bank-L + BD+ (GPT-Pro, 2026-07-03)

Status: responds to my census verdict (BD-UPO census-true; canonical packet fails only at
U_Q^+=0). Branch-B = exactly TWO new certificates; together ⟹ Banked-UPO ⟹ GERSH_{L>5}.

## Certificate A — (Bank-L) via LCB descent
Statement: for every L>5 row, **25m ≤ N² − L² + 25** (⟺ η ≥ 2Σ_L; tight at pure C_L).
NOT provable by packets: bare row packet fails (d eats bank — my G?bB`o witness cited);
bad-saturation fixes h but not d; blue-closure forces W=V which is Bank-L itself (circular).
PROOF OBJECT (LCB cert): long-bank defect Δ_Q = 25m + L² − 25 − N² satisfies
  Δ_Q ≤ −[ Σ_{S∈F_Q} α_S·σ(S) + Σ_{T∈N_Q} β_T·ν(T) ] − R_Q^LCB,  α,β,R ≥ 0
with σ(S) = δ_B(S)−δ_M(S) ≥ 0 (max-cut slack), ν(T) ≥ 0 (minimal neutral switch slack for
completed row side switches — gamma-min descent content), over the FINITE canonical family
F_Q ∪ N_Q = terminal prefixes/suffixes of Q + noncrossing completions + row-deleted blue
detour components touching them. Equality case C_L: all slacks zero, R=0. "Matches the
descent gates evidence" (Codex's Banked-UPO descent gates).

## Certificate B — (BD+) positive-surplus packet
Statement: for every L>5 row with U_Q^+ > 0:
  **2(U_Q^+ + Σ_L) ≤ B(W_Q) = (N²−r_Q²)/25 − p_Q − (d_Q+h_Q)/2**
(census N≤10 + two-lane 0-fail — my gates). Plausibility: each positive component donates its
FULL size to W_Q ⟹ packet bank grows QUADRATICALLY in included detour mass while U_Q^+ grows
linearly; detour inclusion converts row stacking into vertex capacity leaving only true
external boundary. Two-lane: one component = whole graph, no boundary penalty.
BD-canonical packet closures (§5): row inclusion; positive-component inclusion; NO
zero/negative-component inclusion except row vertices; terminal row closure; bad-boundary
normalization (close a crossing bad edge iff it strictly increases B−2U; locally optimal).
Failure routing: protected atom / negative flip / decreasing neutral flip / Bank-L node /
lower-dim boundary.

## Assembly (§6-7)
Case U_Q^+=0: R_Q − N ≤ 0 ≤ η/2 − Σ_L by Bank-L. Case U_Q^+>0: BD+ + packet exchange
(η ≥ B(W_Q)) ⟹ U_Q^+ ≤ η/2 − Σ_L; decomposition R_Q − N ≤ U_Q^+ closes. CELL BRANCH:
replace U_Q^+ by residual after cell-precharge removal; 2(U_res + Δ_Q + Σ_L) ≤ B(W_res) with
Δ_Q ≤ k−d archived. No-cell BD+ FIRST.

## §9 stress behavior
C_L: Bank-L tight, BD+ unused. N=8 L=7 bare-row failure: BD+ unused, Bank-L pays. Two-lane:
BD+ large margin. (All match my gate outputs exactly.)

## Open proof obligations (the two new nodes)
A: prove LCB cert exists for every L>5 row (or per-instance certificate search + structure
   theorem). B: prove BD+ on BD-canonical packets. Ownership: GPT-Pro proving B next
   (consulted); Codex engine = per-row LCB search wired into Banked-UPO descent gates.
