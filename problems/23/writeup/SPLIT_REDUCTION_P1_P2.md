# SPLIT route: the clean (P1)/(P2) reduction of ROWSUM-O

Status: exact reduction (validated), with one open analytic core (P1) and one near-closed
combinatorial selection (P2). This is the honest map of what remains for δ=0 (the whole of Erdős #23).

## Chain
δ=0  ⟺  Γ = Σ_f ℓ(f)² ≤ N²  ⟸  SPEC ρ(K)=ρ(O) ≤ N  ⟸  ROWSUM-O: for every bad edge f,
        (O·1)_f = Σ_g ⟨p_f,p_g⟩ = Σ_v p_f(v) S(v) ≤ N,   where S(v)=Σ_g p_g(v).
(O=PᵀP entrywise ≥0 ⟹ ρ(O) ≤ max row-sum by Perron–Frobenius.)

## Layer/band reformulation of one ROWSUM-O row
Fix a γ-min connected-B max cut. For bad edge f, ℓ=ℓ(f) (odd ≥5), layer i = vertices at B-distance i
on a-b geodesics; A_i = Σ_{v∈layer i} p_f(v) S(v). Then
- layer 0 = {a}, layer ℓ-1 = {b}, with p_f(a)=p_f(b)=1  ⟹  **A_0 = S(a), A_{ℓ-1} = S(b)**.
- ROWSUM(f) = Σ_i A_i.  OUT_t = Σ_{i<t}A_i + Σ_{i≥ℓ-t}A_i (outer 2t layers); CEN_t = ROWSUM − OUT_t.
- B_t := OUT_t − 2tN/ℓ  (shell deviation).   R := ROWSUM − N.

## ⛔ UPDATE 2026-06-28: BOTH band forms are DEAD; ROWSUM-O survives. Pivot to direct ROWSUM-O.
- INTEGER single-t band (∃ one t with both bands) = REFUTED at N=8 by GDSKVG (user/GPT-Pro): cut 01110110,
  bad edge f=23, A=(1,2,1,2,3/2), ROWSUM=15/2<8, B_1=-7/10<R=-1/2, B_2=1/10>0 -> no single t in [R,0].
  [_gdskvg_verify.py, exact]. The fractional interpolated band (min_t B_t<=0 AND max_t B_t>=R, separate t)
  DOES hold on GDSKVG (B_1<=0 outer, B_2>=R center) -- GDSKVG cleanly separates integer-band from fractional.
- FRACTIONAL interpolated band = REFUTED at N=12 by K??CE@A{?]Fc: all 11 gamma-min cuts fail the fractional
  gate (NO-GOOD-CUT), yet max ROWSUM=56/5=11.2<12 [_nogood_witness_verify.py]. So the fractional fix dies too.
- Both witnesses keep ROWSUM-O intact => band decomposition is strictly stronger than ROWSUM-O and cannot be
  the target. LIVE LEAD (user + Codex KKT, convergent): use the N - sum_i|I_i| corridor-EXTERNAL slack;
  Codex corridor-energy form: sum_v (T(v)-N) y_v <= sum_f sum_{i<j}(sqrt(w_{f,i})-sqrt(w_{f,j}))^2, y>=0
  (CODEX_LPD_KKT_CORE.md). Direct-attack workflow + GPT-Pro re-aim in flight.

## (P1)  — the (now-refuted) band core, kept for the record
> **Band lemma.** For every bad edge f there is t∈[1,(ℓ-1)/2] with
>    OUT_t(f) ≤ 2tN/ℓ   AND   CEN_t(f) ≤ (ℓ-2t)N/ℓ.
Because the two budgets sum to N, **(P1) ⟹ ROWSUM(f) ≤ N** — i.e. (P1) PROVES ROWSUM-O; it does
not assume it. This is the genuine remaining mathematics.

Useful identity (assuming ROWSUM ≤ N, i.e. for VERIFICATION not proof): the band-pair for t holds
**iff R ≤ B_t ≤ 0**. [verified exact, census N≤11, _split_charact_verify.py]
So the integer SPLIT ⟺ the shell sequence (B_1,…,B_{(ℓ-1)/2}) enters the interval [R,0].

t=1 special case: OUT_1 = A_0+A_{ℓ-1} = **S(a)+S(b)**, so the t=1 band is the clean endpoint-load bound
   **S(a)+S(b) ≤ 2N/ℓ(f).**
Empirics (_t1fail_probe.py, _split_bestt.py): t=1 suffices in 99.5–100% of cases. It FAILS only when one
endpoint carries near-maximal load (A_0=n_b can approach N on a min-product blow-up); a larger t always
rescues it (no-winning-t = 0 over 10⁶ overloaded blow-ups C5–C13, AND 220k via _split_verify.py, AND the
hard gate Mycielskians/glued islands). So (P1) is empirically airtight but UNPROVEN. It is the same
flavor as the dead overloaded-vertex bounds (S(v)≤N/ℓ FAILS at large N — C7 N=1212), rescued here by
aggregating over the t-band rather than a single vertex.

## (P2) — cut selection (near-closed, Codex's leg)
The integer/fractional SPLIT is NOT tie-invariant: some γ-min cuts are SPLIT-bad. But every triangle-free
graph has ≥1 SPLIT-good γ-min cut [_frac_selected_gate.py: census N≤11 NO-GOOD-CUT=0], and the reduction
may pick any γ-min cut (β,Γ cut-independent). Selection = descent on V(C)=Σ_f max(0,R(f)−max_t B_t(f)):
a SPLIT-bad cut admits a γ-preserving switch of Hamming radius ≤2 to a lower-V cut. Confirmed exact:
- All 8 census-N≤11 SPLIT-bad rows are ℓ=5 central overloads; 7 repair by a balanced-endpoint single
  flip, 1 by a verified symmetric paired switch ({0,4}/{1,5} on J?b@b_wBuD?: cut=16, Γ=75, Bconn — exact).
  [_balanced_endpoint_check.py 0 violations, _pairswitch_verify.py]
- HARD GATE: Mycielskians N≤23 (incl. Grötzsch, M(Petersen), M(Grötzsch)) and glued islands have ZERO
  SPLIT-bad cuts — every γ-min cut all-edges-good, ℓ up to 9 handled. [_hardgate_Vdefect.py V-min=0]
Open: prove the local balanced-endpoint lemma in general (a length-5 central overload forces a balanced
endpoint or symmetric pair). Pending: extend the switch-repair scan to census N=12 (asked Codex).

## Bottom line
δ=0 reduces to **(P1) the band lemma** + **(P2) the cut-selection descent**. (P2) is finite-combinatorial
and nearly in hand. (P1) is the analytic heart — a corridor-aggregated anti-concentration bound on the
geodesic load S — true on everything tested, no proof. Next: GPT-Pro on (P1) (prove the band lemma, or a
structural reason the t-band aggregation always succeeds where single-vertex bounds fail).
