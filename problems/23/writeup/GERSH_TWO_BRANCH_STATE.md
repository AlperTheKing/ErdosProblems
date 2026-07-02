# GERSH — Two-Branch Proof State (canonical, 2026-07-02)

Status: this is the CURRENT goal decomposition. GERSH itself is battery-verified
(0-fail); the two branch-lemmas below are the ONLY open mathematics. A battery
pass is NOT a proof.

## Frame (verified, not in question)

G triangle-free, N vertices, B-connected gamma-minimal maximum cut; M = bad
edges, m=|M|; ℓ(f) = shortest odd cycle through bad f (≥5); cyc[f] = its
shortest geodesic rows; p_f(v) = row-fraction through v; K-components by
geodesic vertex-sharing; s(v)=Tw_C(v)=Σ_{g∈M_C} p_g(v).

GERSH: ROWSUM(f)=Σ_{g∈M}⟨p_f,p_g⟩ ≤ A = N + N²/25 − m for every bad edge f.

Chain (exact-verified end-to-end to N=47): GERSH ⟹ ρ(O_C)≤A ⟹ A·I−O_C PSD ⟹
component-CV ⟹ LRS ⟹ Γ=Σℓ²≤N² ⟹ β≤N²/25.

Battery verification of GERSH: DONE 2026-07-01 (census N≤11 ALL gmins cuts =
304131 bad edges + two-lane L≤60 + Myc-Grötzsch N23 + glued islands + chains +
C5 blow-ups; GERSH_fail=0, PSD_fail=0, min margin 0 tight at C5[t]).

## Branch (A) — equal-length L=5 (PMS-5 / C5-RS)

Sufficient two-mask split (τ=5m/N, η=N²/25−m, per shortest row Q, s_i=s(q_i)):

  (a) PROPER-MASK LIFT: for every nonempty proper A ⊂ {0..4}:
        Σ_{i∈A}(s_i − τ) ≤ (25/N + 2/3)·η
  (b) FULL-MASK row bound: I(P) = Σ_i s_i ≤ N + η        [all overload lives here]

(a)+(b) ⟹ C5-RS: Σ(s_i−τ)_+ ≤ (1+25/N)η ⟹ net-DW′ with UNIFORM width w_i=N/5
⟹ GERSH restricted to L=5 rows. Identity 5τ = N − 25η/N is exact.

Exact evidence (gates: _gate_propermask.py, _gate_c5rs.py, scratchpad):
  - (a)+(b) 0-fail on 814629 rows: census N≤11 all gmins + both N=10 seeds +
    C5 blow-ups + glued chains + Grötzsch N11 + MycGrotzsch N23 on its TRUE
    unique gamma-min cut (slacks +1.748 / +5.53).
  - Tightness ONLY at the N=10 seeds (η=1): eq I?BD@g]Qo (min_lift 0),
    sib I?`FAo]]? (gap 1/3). Overload exists nowhere else in census
    (0/0/36/36 rows at N=8/9/10/11; no growth at N=11).
  - All overloaded rows are C5-hom (verified); Grötzsch-type non-C5-hom rows
    are non-overloaded. Overload fingerprints, all m_C=3: (4,3,(1,1,2,2)),
    (5,3,(1,1,1,1,2)), (6,3,(1,1,1,1,1,1)) — 2 seed graphs only.
  - C5-hom sharp sub-branch (Codex seven-cut algebra on the eq-seed weighted
    quotient): masks 127 (both branches), 125/126, 47-a=1 boundary CLOSED via
    shifted-coefficient/Bernstein positivity (independently reproduced).
    Open pillars: face completeness; atom ⟹ GERSH structure map; sib closure.

Full-mask branch now has an exact two-bank reformulation.  The eta-only
half-degree shortcut

```text
I(Q) <= (1/2)sum_{v in Q}deg_G(v) + eta
```

is false (`G?`DA_wJ?`, `N=10`, `m=2`, `eta=2`, row
`[2,6,0,4,8]`, `I=9`, `halfdeg=13/2`, excess `5/2>eta`).  However,
Claude exact-gated the identity

```text
I(Q) - (1/2)sum_{v in Q}deg_G(v)
  = sum_e a_Q(e)(F(e)-1)
```

and the triangle-free half-degree bound

```text
sum_{v in Q}deg_G(v) <= 2N.
```

Thus (b) is exactly equivalent to the two-bank flow inequality

```text
sum_e a_Q(e)(F(e)-1)
  <= eta + (1/2)sum_{x notin Q}(2-|N(x) cap Q|).
```

Codex diagnostic `_codex_c5_fullmask_twobank_probe.py` reproduces this on
`N=8..10`: `identity_fails=0`, `hdx_fails=4`, `twobank_fails=0`.

Sharper sufficient refinement: `HDX` may only be needed on overloaded rows.
The same diagnostic gives `over_rows=36` and `hdx_over_fails=0` on `N=8..10`.
With active-specific output, those overloaded rows split as
`over_active_counts={4:2,5:34}`.  The active-5 worst row has
`hdx_margin=1/3`, `halfdeg=N`, `row_sum=32/3` at seed `I?BD@g]Qo`; the
active-4 worst row has `hdx_margin=11/30`, `halfdeg=N-1/2`,
`row_sum=152/15` at seed ``I?`FAo]]?``.
On the full `N=11` local census it gives `rows=1045374`, `over_rows=0`,
`hdx_fails=9`, `hdx_over_fails=0`.
Thus a cleaner full-mask lemma is:

```text
I(Q)>N  =>  I(Q) <= (1/2)sum_{v in Q}deg_G(v) + eta.   (OHDX)
```

Non-overloaded rows are trivial; `(OHDX)` plus the half-degree bound proves
the full row-sum branch.  This is now the preferred exact-test target for (b).

Even smaller final C5-RS split: if the active set
`A(Q)={i:s_i>tau}` is proper, the proper-mask lift already gives

```text
sum_i max(0,s_i-tau)
  <= (25/N+2/3)eta
  <= (25/N+1)eta.
```

So the final GERSH burden is `proper-mask lift` plus only the active-5
full-mask stability `I(Q)<=N+eta` (or sharper `I(Q)<=N+(2/3)eta`).  OHDX is
diagnostic/useful, but active-4 is not needed as a separate final row-sum
branch.

Active-5 quotient stress update: the sharper seed stability
`I(Q)<=N+(2/3)eta` has now passed exact weighted quotient scans with weight
orbits and weights in `{1,2,3,4}` for both N=10 seeds:

```text
equality seed: weights=1048576, qmax_cuts=213213, rows_checked=207739,
fails=0, worst_margin=0 at the all-ones equality atom.

sibling seed: weights=1048576, qmax_cuts=926894, rows_checked=754765,
fails=0, worst_margin=1/3 at the all-ones sibling atom.
```

This is only the active-all-five branch.  The separate fixed-mask /
active-size coefficient split with small proper-mask coefficients is still
dead by the Myc(Grotzsch) guardrail.

## Branch (B) — L>5 (LONG-SURPLUS / SLACK-CAGE)

Route: Codex protected UNIT-FLAT5 peel + fan-component lemma.

  Fan lemma target: for blue-closed selected fan components C built from
  protected UNIT-FLAT5 atoms: b(C) ≥ k(C) (blue side-door boundary ≥ selected
  bad leaves); else σ(C) < 0 contradicts max-cut.
  Peel target: selected protected cells admit a peel ordering with singleton
  intersection components (or fan-collapse with ≥3 leaves exposing a negative
  switch).

Exact evidence: census N=10 (15497 cuts, hist {0:15491,1:6}) and N=11 (164986
cuts, hist {0:164966,1:20}) — PASS, all singleton cells, 0 missing/bad/overlap
(Codex + independent reproduction, digits match). Glued chains: no atoms arise
(3900 cuts). Extension battery (blow-ups, islands, N23, two-lane) in progress.

Multi-cell correction: protected cells are **not** necessarily vertex-disjoint.
Artificial two-copy tests show:

  - positive-length blue path overlaps (edge/path lengths 1..4) either destroy
    the protected atom, create bad cell boundary, or expose a negative-sigma
    switch (`min_sigma=-1` or `-2`);
  - single-vertex contacts survive maxcut and Gamma-minimality.  Six
    side-compatible vertex-sharing overlaps have `n=19`, `bad=max_bad=4`,
    intended cut connected max, `Gamma=100=min Gamma`, and
    `atom_count_hist={2:1}`.

So the live Branch (B) packing target is cactus packing, not disjoint packing:
distinct protected UNIT cells may meet in at most one vertex; positive-length
overlap is forbidden by maxcut/bad-cell failure.  The remaining scalar task is
to pay one bank atom per protected cell in such cactus contact families.

## Trap list (SIX — every future candidate must be checked against these)

Root cause of all: LOAD CONCENTRATION — Σ_{v∈V_i}s(v)=m_C is constant per
class, so a lone vertex in a size-1 class carries the whole m_C; loads track
class TOTALS, not SIZES; I(P) can exceed |V(C)| and N.

  1. DW-Hall (min Σmax(0,s_i−m/w_i) ≤ η): too strong; N=8 G?bF`w.
  2. (HL) threshold shift Σ(s_i−N/5)_+ ≤ η: FALSE; G?`F`w N=8 m=2 row
     (1,1,2,1,2), 4/5 > 14/25. The reciprocal slack 25η/N cannot be moved
     into the threshold.
  3. Row-Majorization (s)≺_w(class sizes): FALSE; H?AFBo] N=9,
     s=(1,2,2,1,2) sum 8 > n=(2,1,1,2,1) sum 7 = |V(C)|.
  4. (RW) pointwise majorant w≥s, Σw≤N: dies at EVERY overloaded row
     (Σw ≥ I(P) > N; atom 32/3 > 10).
  5. CRS5 real-width 5-var lemma (w_i w_{i+1}≥m, Σw≤N ⟹ Σ(w−τ)_+≤(1+25/N)η):
     FALSE over reals; N=9 m=3 w=(2,3/2,2,2,3/2), 1 > 68/75 (gap 7/75).
     The INTEGER class-size version (CSL) is battery-true — do not port
     integer arguments to real widths.
  6. C5-hom assumption: all-ℓ=5 does NOT imply C5-hom (Grötzsch). Only
     overload ⟹ C5-hom is verified.

⚠ Heuristic-cut contamination: NEVER claim a scale failure from a heuristic
cut. MycGrotzsch N23 maxcut_ls gives 54 but true max is 55; gmins(N23) is
feasible (unique gamma-min cut). Earlier "sharp 2/3 fails non-C5-hom at scale"
claims were contaminated and are RETRACTED.

## Dead routes (do not revive)

Spectral/2nd-moment (ρ(O)/ρ(K2)/ROWSUM≤N/K2T-descent; two-lane L=12 kills all),
per-level LOAD-PSC shortcuts, no-two-hole/AtMostOneMiss, RFC/NL, C5-collapse
slogan, DW-Hall, (HL), Row-Majorization, (RW), CRS5-real, sibling monotone
domination.

## Success = (A) proven + (B) proven + every lemma battery-verified + sorry-free
Lean → ONE formal-conjectures PR. Nothing ships partially.
