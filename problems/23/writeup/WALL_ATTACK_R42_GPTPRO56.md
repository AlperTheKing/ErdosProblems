# WALL ATTACK — R42: RATCHET FAILS (minimal neutral ledger (B,U,L,A)=(2,1,0,1) rotates deficiency);
# EXACT TRANSPORT IDENTITY Δ(ω′)−Δ(ω) = B + L − U − A_reopt (compile-ready ledger); balanced-rotor
# constraints (18)-(22) = COMPLETE falsifier-gate spec; wall = noExactBalancedFullyCoveredDetourRotor;
# GPT P(falsifier) back UP to ~15%
# (GPT-5.6 Pro, 2026-07-12, "worked 8m21s"; harvested ~14.7k ch)

**[CLAUDE GATE HEADER — the transport identity (12) is verified by inspection (|Carry| = ν(ω) − D_M − L;
|O′| − |O| = B − D_M − U; ν(ω′) = |Carry| + A_reopt ⟹ substitution); my deactivation lever is CONFIRMED as
identity (6): deg_I(v)=1 + Q′ selects vx ⟹ v ∉ A′ ⟹ U ≥ 1 ALWAYS at the live star detour — the deficient
obligation dies; the failure is that a born two-half stem at m with one matched half restores the count
((2,1,0,1) ⟹ ΔΔ = 0). The (18)-(22) constraint set goes to Codex VERBATIM as the t=3/N=15 gate spec; the
CheckedDetourTransportLedger structure + defect_delta go to the compile queue. NOTE P moved 10%→15% because
the even-fibre neutral ledger is internally consistent and the window satisfies all scalars — the question
is now PURELY whether real geometry realizes the balance cyclically. Next: engine decides; my R43 = the
K3,3-skeleton synthesis question (the 9/8 circuit's six degree-3 hubs are the ONLY vertices that can carry
the (22) owner profile — construct or kill on that skeleton).]**

## 1-3. Exact local formulas (all integer identities)
Row swap Q = C∪{m} → Q′ = C∪{v} (live: vx unique active edge, y ∈ C support nbr):
- n′(a,z) − n(a,z) = 1[a,z ∈ C∪{v}] − 1[a,z ∈ C∪{m}].
- Leaving middle: c′(m) − c(m) = −ℓ_m, ℓ_m = 1[r(m)≥2] + #{z∈C : n(m,z)≥2} (disappearing cells).
- Entering owner: c′(v) − c(v) = g_v = 1 + #{z∈C : n(v,z)≥1} (leading 1 = new diagonal; the active pair
  (v,x) creates NO collision: n(v,x)=0 → 1).
- Retained z ∈ C: c′(z) − c(z) = 1[n(z,v)≥1] − 1[n(z,m)≥2].
- Scoped demand: (|O′| − |O|)/2 = Σ_{A∩A′}(c′−c) + Σ_{A′\A} c′ − Σ_{A\A′} c (transfer + activation −
  deactivation). **v ∉ A′ ALWAYS** (vx becomes support; removed edges mx,my not incident with v) ⟹ all v's
  obligations die, including the unmatched one.
- Support: |S′| − |S| = 1 − 1[p(mx)=1] − 1[p(my)=1] ∈ {−1,0,+1} (matches the 7.6M-detour census).
- Free cells: F′(m) − F(m) = 1[r(m)=1] + #{z∈C : n(m,z)=1}; F′(v) − F(v) = −#{z∈C : n(v,z)=0};
  F′(z) − F(z) = 1[n(z,m)=1] − 1[n(z,v)=0]. P1(a) = 2F(a) − deg_I[A](a). P4/P5 = set differences only.

## 4-6. THE EXACT TRANSPORT IDENTITY (compile-ready)
Persistence: canonical copy-order for collision cells; FreeHalf persists when pair+bit stays free+unreserved;
carry M-edge iff obligation+source persist ∧ eligibility holds ∧ base label unchanged. Define B (born),
U (dead unmatched), L (broken live matches), A_reopt = ν(ω′) − |Carry(M)|. **Δ(ω′) − Δ(ω) = B + L − U −
A_reopt.** Lean: CheckedDetourTransportLedger (persistObligation/persistSource/carry/born/deadUnmatched/
brokenLive + 4 checker fields + newOptimal) + CheckedDetourTransportLedger.defect_delta.
Channel dictionary: U ≥ 1 (killed deficiency at v + possible split kills); B = new copies at surviving
owners + ALL scoped mass of newly activated regions (m's background mass can be LARGE); L = P1-ceases /
reservation-appears / eligibility-disappears / P4-P5-disappears / label-conflict (priority order);
A_reopt = new Free cells at m + newly exposed keys + rematching + coherent relabeling (exact optimization).

## 7-8. Why the ratchet fails
Minimal neutral rotation: two-half stem dies at v (one matched + THE unmatched), two-half stem born at m,
one new half matched ⟹ (B,U,L,A) = (2,1,0,1) ⟹ ΔΔ = 0. Even-fibre consistent (= the 6-obligation/5-source
rotor). ±7/9 owner-balance transfers telescope to 0 around cycles; support deltas sum to 0; tuple rank cannot
orient orbit minima. NO strictly decreasing quantity among compiled invariants.

## 9-10. Balanced-rotor conditions + COMPLETE t=3/N=15 gate spec
Per transition: B_i + L_i = U_i + A_i (18); minimal case (2,1,0,1); NO transition may have U+A > B+L (would
lower the global minimum). Cycle: Σ support deltas = 0; Σ ±τ transfers = 0 componentwise; same positive
optimal defect at every state; no outside tuple with smaller defect. Graph/row: N=15, 9 bads, distances 4,
anchored complete nodup families, tri-free, genuine maxcut, one 9/8 circuit. Owner (22): dB=dM=3, deg_I=1,
r=3, P1 pressure 1, star fully covered. Detour: Q′ complete-DB row, support delta ∈ {−1,0,+1}, v_i ∉ A_{i+1},
next deficient region contains m_i, ledger (18), all newly Free keys matched/blocked, sink SCC of global
minimizers. **A hit = decisive counterexample to the collision-selection theorem.**

## 11-12. The one missing lemma + verdict
`cutTightFullyCoveredDetour_has_transportSlack : ∃ ledger, U + A_reopt > B + L` (⟺ Δ(ω′) < Δ(ω)) —
UNPROVABLE from current hypotheses (neutral ledger (14) kills all parity/scalar arguments). Honest global
alternative: **`noExactBalancedFullyCoveredDetourRotor (R : CheckedBalancedDeficiencyRotor) : False`**
(rotor checks (18)-(22) + zero source exposure per transition). Anti-falsifier evidence stays strong (N≤12
zero; 8-vtx scope-vacuous; N=78 huge margins; stars always expose) BUT the even-fibre ledger is internally
consistent + the window satisfies all scalars ⟹ **P(falsifier) ≈ 15% (UP from 10%)**. Next gate = the exact
balanced ledger, NOT another scalar potential.
