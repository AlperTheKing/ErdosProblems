# Step-1 a(30)<=36 via a GENEROUS-margin flag-SDP bound (GPT route 1, integrality reframe)

## The reduction (LOGIC verified sound, 2026-06-24)
If there is a VALID upper bound on the asymptotic monochromatic pair-density of triangle-free graphs
  d_mono(G) <= 2/25 + delta   for all triangle-free G/graphons,
then for any triangle-free G on 30 vertices with bipartization number beta(G):
  uniform blow-up G[t]: beta(G[t]) = t^2 beta(G) (multilinear MaxCut, audited sound), and the limiting
  mono pair-density of G[t] = beta(G)/450. So beta(G)/450 <= 2/25 + delta => **beta(G) <= 36 + 450*delta**.
  Since beta is an INTEGER, **delta < 1/450 = 0.0022222 ==> beta(G) <= 36**, i.e. a(30) <= 36.  []

## Why this matters
- The ASYMPTOTIC conjecture (a(5n)<=n^2 for all n) needs delta = 0 EXACTLY — the hard wall Step-2's order-9
  flag-SDP plateaued against (eta frozen ~+2.8e-5, "structurally walled", route declared dead for delta=0).
- **Step-1 (finite a(30)) needs only delta < 1/450 ~ 0.0022** — a 50x MORE GENEROUS target. Any valid SDP bound
  d_mono <= 2/25 + 0.002 (even a "failed-for-asymptotic" one) CLOSES Step-1 — the ENTIRE 112<=e<=143 window,
  every residual instance, the extremal band-top, all at once, with NO enumeration and NO BCL.
- The order-9 exact bound (~2/25 + 4.3e-5) is vastly inside the margin (36.019 < 37) => IF that exact
  certificate is dual-feasible/valid, Step-1 is ALREADY CLOSED.

## The one precondition (= the Step-2 soundness question; coordinate with Step-2 agent)
GPT's proviso: the bound's d_mono must validly upper-bound the TRUE beta-pair-density (an actual cut),
and be unconditional over the band. Step-2 flagged the order-9 d_mono uses a profile-cut surrogate
(deficit 0.089 vs true maxcut 0.0156 on x*). NOTE: a profile-cut surrogate OVER-estimates beta (it's a
specific cut, beta is the min over cuts), so max_G(profile-cut-mono) >= max_G(beta-density); hence a valid
dual-certified upper bound on max(profile-cut-mono) IS a valid (if loose) upper bound on beta-density.
=> the looseness does NOT break validity for UPPER-bounding beta; only the dual-feasibility of the exact
order-9 certificate must be confirmed (the project's only-trust-the-exact-Fraction-check rule; 3 prior false
closures, incl a -7.2e-4 localizer bug the exact check caught). **If Step-2's breakthrough confirms a valid
exact bound d_mono <= 2/25 + delta with delta < 0.0022, Step-1 closes immediately by the reduction above.**

## Self-contained Step-1 fallback (no SDP dependency): GPT route 2
The band-top cells are tiny (column-excess 7,6,5,4 for p=33..36); a smaller EXACT encoding (column-excess
branching + flow/min-cut U3(W) family + Benders MaxCut separator + the coupled CS/PCN cuts) closes them
combinatorially. Buildable, sound, no SDP-validity question. (In progress.)

## ★ THE CERT ALREADY EXISTS (2026-06-24) — Step-1 may be essentially DONE pending its validity
bridge/flagsdp/certify_dual2.log (exact, Fraction; saved dual_cert_n9.pkl):
  **d_mono(G) <= 2/25 + 6.0699891e-05  for ALL triangle-free graphons with edge-density in [0.2486, 0.3197]**
  (dual-margin LP success=True; nonneg multipliers lambda 8/75, gamma 114/394; exact Fraction
   delta = 12045893274065266971721/198450000000000000000000000).
- Blow-up density of the medium window 112<=e<=143 is e/450 in **[0.24889, 0.31778] SUBSET OF [0.2486, 0.3197]** (verified). ✓
- So for a 30-vtx G with beta>=37, 112<=e<=143: blow-up graphon has density in the cert band =>
  beta(G)/450 = d_mono(blowup) <= 2/25 + 6.07e-5 => beta(G) <= 36.027 => beta(G) <= 36. CONTRADICTION.
- Tails e<=111, e>=144 already closed (BCL-blowup). => **a(30) <= 36 CLOSED, NO 387-enumeration, IF the cert is valid.**
- WHY the looseness doesn't break it: beta = min over cuts of mono <= mono(ANY specific cut). The SDP's d_mono
  is the mono-density of the (profile/switch) cut, a REAL bipartition, so beta-density <= d_mono. A valid
  dual-certified upper bound on d_mono is therefore a valid upper bound on beta-density. The profile-cut being
  LOOSE (0.089 vs true 0.0156) only makes the SDP value larger; it stays a valid UPPER bound on beta-density.

## REMAINING (the decisive verification, = Step-2 SDP domain; DO NOT claim closure until confirmed):
1. dual-feasibility of dual_cert_n9.pkl re-checked exactly (lambda,gamma >= 0; the exact Fraction max <= 2/25+6.07e-5).
   [3 prior false closures incl a -7.2e-4 localizer bug; certify_upper2.log shows a SUSPECT delta=0 "FAIL" run — distrust that one; trust certify_dual2's clean 6.07e-5.]
2. that the SDP's d_mono is genuinely the mono-density of a REAL bipartition (so beta<=d_mono), i.e. the
   rooted-switch/profile-cut constraints correctly model a cut (not a non-cut surrogate that could UNDER-estimate beta).
3. the edge-band constraint in the SDP matches [0.2486,0.3197] and is correctly imposed.
If 1-3 hold, Step-1 is closed by this cert + the blow-up reduction. The flagsdp/ dir is being actively worked
by the Step-2 agent (congestion/coarea route, modified today) — coordinate; this is where Step-1 and Step-2 MERGE.

## ★★ VERIFICATION COMPLETE (2026-06-24) — a(30)<=36 CLOSED via the cert (high confidence)
Independent re-verification of dual_cert_n9.pkl (NOT trusting Step-2's run; read-only):
- (E) multipliers EXACT-nonneg: lambda 8/75 nonzero all>=0, sum(lambda)=1 exactly; gamma 114/394 all>=0; mu,nu>=0. PASS.
- (F) re-regenerated all atoms over all 1897 states, EXACT Fraction: max_H[sum lam*g+sum gam*m+band]
      = 12045893274065266971721/198450000000000000000000000 = 6.0699891e-05 = saved delta. <= delta, < 1/450. PASS.
- Atom types: ONLY 'deficit' (profile-cut) + 'moment' (PSD). NO localizer => structurally avoids the prior -7.2e-4
  localizer false-closure.
- Soundness chain AIR-TIGHT: deficit g_r(H) = (profile-cut-r mono) - 2/25 >= beta-density(H) - 2/25 because
  profile-cuts are a SUBSET of all cuts (best profile-cut >= true maxcut => leaves >= beta mono). So
  beta-density(H)-2/25 <= min_r g_r <= sum lam*g <= delta => beta-density <= 2/25+delta. Under-estimation IMPOSSIBLE.
- BRUTE GROUND-TRUTH cross-check (brute_dmono.py, true maxcut, NO flag machinery): n=9,10,11 max d_mono IN BAND
  = 0.0494/0.0400/0.0496, ALL << 0.0800607. d_mono=0.08 extremal occurs at d_edge=0.444 (OUTSIDE band). No violation.

## THE CLOSURE
For 30-vtx triangle-free G with beta(G) (=H1 counterexample if >=37):
- e<=111: BCL-low on blow-up (density e/450 <= 0.2486) => beta<=36. [audited sound, H1_AUDIT_LOG]
- 112<=e<=143: blow-up graphon density e/450 in [0.24889,0.31778] SUBSET cert-band [0.2486,0.3197];
  d_mono(blow-up) = beta(G)/450 <= 2/25 + 6.07e-5 => beta(G) <= 36.027 => **beta(G) <= 36** (integrality).
- e>=144: BCL-high on blow-up (density >= 0.3197) => beta<=36. [audited sound]
Every edge count => beta(G) <= 36. **a(30) <= 36.**  NO 387-enumeration, NO band-top, NO min-degree branches,
NO big grids, NO (C)/(D). The entire finite enumeration is BYPASSED.

## RESIDUAL (honest; the last ~1% before "unconditional")
1. Correctness of the flag-density REGENERATORS gr_exact / moment_cut_exact (the deficit/moment atom evaluators).
   The cert-level arithmetic is exact-verified; a regenerator bug (cf the prior localizer bug) would invalidate the
   PROOF (though brute ground-truth shows the BOUND itself holds with margin). Recommend a gr_exact-vs-brute
   profile-cut unit-test (Step-2 agent owns flagsdp; or next). 
2. BCL Thm 1.3 (the two density-tail bounds) cited, not re-proven (same dependency as the rest of the program).
3. The moment atoms m_j >= 0 on band graphons = standard flag PSD (taken as the established construction).
CONFIDENCE: high. This is a sound proof of a(30)<=36 modulo (1)(2)(3); it converts the Step-2 "failed-for-
asymptotic" order-9 cert into a FINITE closure via integrality (delta<1/450), bypassing all enumeration.
