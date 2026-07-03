# Bank-L via LCB Switch Cone (GPT-Pro, 2026-07-03) — the last Branch-B node

Status: GPT-Pro states honestly NO hand proof of Bank-L from archived ingredients alone
(bare-row packet insufficient (1.1): 39<50 at G?bB`o; bad-closure loses d; blue-closure
circular at W=V). The proof object = LCB SWITCH CONE certificate; per-row existence /
generation = the remaining obligation (= Codex descent-gate territory).

## Objects
Row Q of f, L>5. S_Q = finite family of completed row side switches: for every proper
interval I ⊆ Q, two terminal sides, completed under: terminal prefix/suffix closure for every
shortest row meeting the side; noncrossing-safe closure; true-twin closure in positive-flow
support; UNIT-FLAT5 extraction on atom creation. Discard ∅/V.
- σ(S) = δ_B(S) − δ_M(S) ≥ 0 (max-cut slack).
- ν(S) = Σ_{e∈δ_B(S)} ℓ_S(e)² − Σ_{g∈δ_M(S)} ℓ(g)²  [switch slack: flipping S makes crossing
  blue e bad with NEW length ℓ_S(e) (shortest odd cycle in the switched cut), removes
  crossing bad g of length ℓ(g)]. Gamma-minimality: σ(S)=0 ⟹ ν(S) ≥ 0 (2.2).
- **ν_K(S) = ν(S) + K_S·σ(S), K_S = Σ_{g∈δ_M(S)} ℓ(g)² ⟹ ν_K(S) ≥ 0 UNIVERSALLY**
  (σ=0: minimality; σ≥1: ν ≥ −K_S). The key normalization — descent info without falsely
  applying minimality to non-neutral switches.

## (LCB) Certificate Theorem
Δ_Q = 25m + L² − 25 − N². If there exist α_S, β_S ≥ 0 and visibly-nonnegative residual
R_Q^lcb ≥ 0 with   **−Δ_Q = Σ α_S σ(S) + Σ β_S ν_K(S) + R_Q^lcb**   then Bank-L holds for Q.
Δ_Q > 0 would force: an improving flip (σ<0, impossible) / a Γ-decreasing neutral switch
(ν<0 at σ=0, impossible by gamma-min) / violation of a nonnegative residual fact. ∎
Residual R allowed pieces (§4): size terms c(N−L), c(N−L)², c|A|; triangle-free consecutive-
attachment counts (x cannot attach to q_i AND q_{i+1}); protector extraction slack (→ cell
ledger); detour terms |K|−T_Q(K) ≥ 0 (negative components!). Compatible with fan/cactus/BD+.

## Tightness (§6) + power (§9)
Pure C_L: interval switches merely move the bad edge, ℓ_new = L ⟹ ν=0, σ=0, R=0 — TIGHT.
Stronger than packet exchange: the cone SEES the L² contribution through ν(S) — at G?bB`o the
interval switches shorten/move the long bad edge and their slacks certify the missing 11/25.

## Row-level certificate format (§8, exact rational, machine-checkable)
Per switch: sides, δ_B, δ_M, σ, ℓ_S(e) per new bad edge, ν, K_S, ν_K = ν + K_S·σ.
Certificate: {α_S ≥ 0}, {β_S ≥ 0}, residual terms ≥ 0, and the EXACT identity
−Δ_Q = Σασ + Σβν_K + R. LP feasibility per row.

## Obligations
1. Codex: extend _codex_bankl_lcb_skeleton.py — emit σ(S), ν(S), K_S, ν_K(S) over S_Q, then
   LP-solve (α,β,R≥0) for the identity per census L>5 row; ANY UNSAT row → immediate relay
   (counterexample to LCB form). [Answers Codex 22:08Z ν(T) question: ν(T) is NOT the neutral
   Γ-drop (zero on gamma-min); it is the switch slack ν(S) above, used as ν_K.]
2. GPT-Pro next: the EXISTENCE theorem (every L>5 row admits an LCB certificate) — after
   census LP evidence.
3. Claude: exact-audit the emitted certificates (identity check is pure arithmetic).

## ADDENDUM 2026-07-03: QUANTITATIVE TRICHOTOMY + EQUALITY FACE (GPT-Pro reply 2)
Certificate forms finalized: TIGHT (Delta_Q=0) / (D-cert) -Delta_Q = c_K*(|K|-T_Q(K)) + R_K /
(S-cert) -Delta_Q = c_S*nu_K(S) + R_S — all coefficients rational >= 0, residuals visibly >= 0.
CAUTION: qualitative deficit existence is NOT enough (no universal scalar c with -Delta_Q <=
c(N-R_Q)); the LP finds row-local quantitative identities. Completed switch family = interval
seed + fixed-point closure (B-connected row-subpath, terminal prefix, noncrossing, twin,
FLAT5 extraction), discard empty/V, keep connected.
EQUALITY FACE THEOREM (sketch, provable): Delta_Q = 0 ⟹ N=L, m=1, G[V(Q)] = C_L exactly —
via: N>L gives an outside component (positive deficit ⟹ D-cert ⟹ Delta<0 contra; nonneg
surplus ⟹ BD+ ⟹ eta > 2Sigma_L contra); m>1 on N=L gives a chord (blue chord contradicts
shortestness; bad chord gives shorter odd row ⟹ positive nu_K switch contra); triangle-
freeness excludes local triangular chords. USES: shortestness + tri-free + gamma-min.
STATUS: GPT-Pro declines to assert naked per-row existence pre-LP-evidence; the sound closure
is the LCB certificate cone theorem + per-row LP generation (Codex). SCOPE NOTE (Claude):
overfull rows (like two-lane-L8, the 130 size2 rows' suspected class) get Bank-L FREE from
H_BD + packet exchange (eta >= B(W_Q) >= 2(U+Sigma_L) >= 2Sigma_L) — LCB cone only needs
UNDERFULL rows, where the detour deficit = underfullness margin exists by identity (1.1).

## ADDENDUM 2 (2026-07-03): QUADRICHOTOMY THEOREM (GPT-Pro reply 3) + scope cross-tab
FORMALIZED: Bank-L quadrichotomy — (T) tight / (SP) sparse identity -Delta_Q =
((N-L)^2-25(m-1)) + 2L(N-L) with (N-L)^2 >= 25(m-1) [pure algebra, proven] / (D-cert) /
(S-cert with nu_K >= 0 universal). All certificates are exact IDENTITIES (not inequalities —
correction: c_K*deficit >= -Delta_Q with Delta_Q<0 would be trivially satisfiable; identity
form required). EQUALITY FACE PROVEN (section 5): N=L, m=1 ⟹ G = pure C_L exactly (blue
chord contradicts shortestness; bad chord creates shorter odd cycle; triangle-freeness kills
length-3 chords); conversely C_L gives Delta_Q = 0. REMAINING STRUCTURAL NODE (section 6):
**Dense LCB Switch Deficit Lemma** — if not tight, SP fails ((N-L)^2 < 25(m-1)), and no
detour certificate exists, then a completed connected row side switch certificate exists.
CODEX SCOPE CROSS-TAB (full battery 14247 rows, bad_lcb_scope_fallback_rows=0):
{equal:tight 34, overfull:sparse 130, underfull:detour 1344, underfull:nuK 12739} — EXACT
scope split: all sparse rows OVERFULL (min R_Q-N=1 at two-lane-L8; logically routed to
BD+/H_BD in assembly), all underfull rows use only {nuK, detour}. ASSEMBLY: overfull → H_BD;
equal → tight face; underfull → trichotomy {nuK, detour} whose existence = Dense lemma scope.

## ADDENDUM 3 (2026-07-03): NORMALIZATION CORRECTION + COAREA REFRAME (GPT-Pro reply 4)
CATCH: unrestricted c_K makes the quadrichotomy ILL-POSED — any underfull row trivially
detour-certifies (pick c_K = -Delta_Q/deficit; Sigma deltas = N-R_Q > 0 guarantees a positive
component); unrestricted c_S likewise. The battery split is meaningful only via chooser
preferences. CORRECT OBJECT: the NORMALIZED LCB COAREA IDENTITY
  -Delta_Q = SP_Q + Sigma_K a_K(Q)*delta_Q(K) + Sigma_S b_S(Q)*nu_K(S) + R_Q^lcb
with CANONICAL coefficients a_K, b_S >= 0 determined by the construction (not post hoc),
SP_Q = ((N-L)^2-25(m-1))_+ + 2L(N-L) (dense branch: positive part omitted, negative part
absorbed into switch side). GIVEN the identity: dense switch lemma = 3 lines (if detour+
sparse+residual insufficient, the switch sum is > 0, so some nu_K(S) > 0 with b_S > 0).
THE remaining theorem = EXISTENCE of the coarea identity per row = the LP/Farkas certificate
theorem (Codex's emitter instantiates it per battery row; the general proof should go
Farkas: if the LP were infeasible, the dual separator violates maximality/gamma-min via a
flip or descent). Proof organization: LCB coarea identity ⟹ quadrichotomy ⟹ Bank-L —
NOT a direct scalar counting argument. NOTE (Claude): the sparse identity is itself a
2-term coarea identity — the general identity generalizes it; for Bank-L-as-inequality the
identity is the proof vehicle (terms nonneg ⟹ Delta_Q <= 0).
NEXT: (1) Codex full N<=11 JSONL artifact (emitter live, bankl_lcb_cert_v1); (2) GPT-Pro
consult: PROVE coarea existence via Farkas/flip-descent duality; (3) my audit of emitted
identities (pure arithmetic).

## ADDENDUM 4 (2026-07-03): ROW BOUNDARY PRESSURE COVER (PC) — final sharpening (reply 5)
EXACT IDENTITY (1.2): -Delta_Q = [2Lr - 25(p-1) - 25(d+h)/2] + rho_Q, r=N-L, (p,h,d) of the
bare row packet W=V(Q); rho_Q = 25*(eta - [(N^2-r^2)/25 - p - (d+h)/2]) >= 0 BY PACKET
EXCHANGE (1.3). Define PRESSURE P_Q = 25(p-1) + 25(d+h)/2 - 2Lr. Then (1.6):
**Bank-L ⟺ rho_Q >= P_Q.** Branch split: P_Q <= 0 ⟹ Bank-L by packet exchange ALONE (no
switches needed); P_Q > 0 ⟹ need
  **(PC)  rho_Q >= P_Q^+ = Sigma a_K delta_Q(K) + Sigma b_S nu_K(S) + R**  [canonical coeffs]
G?bBo check: P_Q = 25*0 + 25 - 14 = 11 = exactly the missing bank units ✓. One-switch
certificates on the battery are extreme simplifications of (PC). Sparse-vs-dense refines to
P_Q-sign (sharper than (N-L)^2 vs 25(m-1)). Detour normalization + nu_K as before.
REMAINING NODE: prove (PC) for P_Q > 0 rows. NEXT MACHINE STEP (Codex): cross-tab the
battery by sign of P_Q — count P_Q<=0 rows (free) vs P_Q>0 (true hard set), emit exact
(p,h,d,r,P_Q,rho_Q) per row; the hard set is expected SMALL and structured (boundary-heavy
rows). Then (PC) proof consult targets exactly those.
