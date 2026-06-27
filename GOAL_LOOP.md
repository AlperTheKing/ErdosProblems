# GOAL_LOOP.md — STEP-1 AGENT standing task (READ FIRST on every compaction / new session)
#
# Resume flow: (1) read this file; (2) read the last ~30 lines of PROGRESS.md = where you left off;
# (3) read coordination/STEP2_TO_STEP1.md for any new messages from Step-2 (the DIRECT agent channel,
#     set up 2026-06-26; protocol in coordination/CHANNEL.md; you write coordination/STEP1_TO_STEP2.md,
#     you read coordination/STEP2_TO_STEP1.md; no more human relay -- check it EVERY loop iteration);
# (4) resume the GOAL + LOOP below.
#
# Prior tracks are superseded but recoverable: the #944 Dirac-k=4 work is PUBLISHED (arXiv:2606.18462)
# and archived in memory (erdos944-shore-machine-state); the earlier multi-problem "New Mathematics on
# Open Erdős Problems" mission + its all-or-nothing/Lean-only override (this file before 2026-06-26)
# applied to the formal-conjectures track and are preserved in git history. Active track = Erdős #23,
# Step-1. Current policy = publish SOUND computer-assisted results via arXiv (user decision, this
# session; #23 v1 = submit/7754052).

================================================================================
GOAL
================================================================================
PRIMARY (the real prize, all-or-nothing): prove #23 for ALL triangle-free G on ALL N:
  beta(G) = e(G) - maxcut(G) <= N^2/25.
  ** H2 PEELING IS RETIRED (GPT-Pro audited, 2026-06-26, thread c/6a3b8a74). ** The
  exact transfer identity d_mono(W_G) = 2 beta(G)/N^2 (blow-up multilinearity: the
  monochromatic integral is multilinear in x_i = N*mu(S cap I_i), so its infimum sits
  at an integer vertex x_i in {0,1} = beta(G); NO o(1)/O(1/N)/rounding) means Step-2's
  exact band bound delta=0 gives beta(G) <= N^2/25 DIRECTLY for every finite N, incl.
  non-multiples of 5 (the real inequality auto-implies the floor; no peeling, no
  induction, no separate finite argument). The integrality trick was only ever needed
  for delta>0. So the WHOLE conjecture reduces to:
   (i)  the exact band graphon bound d_mono(W) <= 2/25 on [0.2486,0.3197] (delta=0)
        -- the SOLE hard piece; co-develop the Gamma-lemma (Gamma=sum ell^2<=N^2)
        with Step-2 (do NOT duplicate their flag-SDP / live-run files);
   (ii) the BCL tails + blow-up integrality, already in the paper.
  STEP-1's residual job for the full proof = the clean all-N ASSEMBLY: partition by
  d = d_edge(W_G) = 2e(G)/N^2 into {d<0.2486, 0.2486<=d<=0.3197, d>0.3197}; the CLOSED
  band owns BOTH endpoints (avoids BCL's finite-density-normalization e/C(N,2) endpoint
  issue); strict tails discharged by blow-up (beta(G[t])=t^2 beta). SUCCESS = a gap-free
  proof of #23 for all N in ONE paper (gated on Step-2's delta=0).

NEAR-TERM DELIVERABLE (do this FIRST — it is a real, in-hand publishable win):
  Independently EXACT-verify Step-2's sound-atom certificate (delta = 4.756e-5)
  and, on pass, ship arXiv v2 extending a(5n)=n^2 from N<=55 (v1, delta=5.991e-4)
  to N<=200. You OWN the single arXiv paper and the verification gate.
  Arithmetic: (25/2) n^2 delta < 1  ==>  delta=4.756e-5 closes n<=40 (N<=200);
  n=40 threshold = 2/(25*1600)=5.0e-5, n=41 = 4.76e-5. N<=200 is the flag-LP
  finite ceiling (the order-9/10 self-tight wall plateaus eta above 0) — do NOT
  push Step-2 to squeeze delta further. Lock v2, then co-develop delta=0 (the
  Gamma-lemma) with Step-2.

METHOD (standing, user directive 2026-06-26): FINISH Step-1 in active collaboration
  with GPT-Pro. At every decision point or stuck point, DRIVE THE BROWSER TOOL
  (Chrome MCP) to SEND a self-contained question to GPT-Pro and READ BACK its answer
  (main.innerText after the last "thought"/"düşündüm" marker; chunk <=700 chars).
  Audit every GPT answer line-by-line + exact-Fraction-check before adopting; then
  proceed on the path GPT picks. This browser round-trip is PART of the loop, not
  optional, and not user-relayed unless the browser is unavailable.

VERIFIABLE SUCCESS CRITERIA
  v2  : Step-2's cert passes (a) regen_verify_u7.py exact-Fraction dual feasibility
        [per-type sum_c lambda_{sigma,c}=1; cut+band+moment per-state residual >= 0
        in Fractions], (b) the moment-PSD Gram check [Step-2's rationalized v
        reproduce the moment rows AND M^sigma = sum_c w_c q_c q_c^T >= 0 exactly],
        (c) BCL band tiling [<=0.2486, [0.2486,0.3197], >=0.3197 tile [0,0.5] with
        shared endpoints, no gap]; and delta_exact < 5.0e-5.  THEN publish v2.
  full: Step-2's delta=0 (the Gamma-lemma) proven + Step-1's clean all-N assembly
        closes ==> beta <= N^2/25 for all N. (H2 is RETIRED — not needed; see GOAL.)

================================================================================
STATE (2026-06-26, reconciled with Step-2)
================================================================================
- Published v1 = envelope_k7_cert.pkl (per-root-MaxCut U_7, delta=5.991e-4, N<=55,
  multiples of 5). arXiv submit/7754052 (in queue, "Section ??" cross-ref fixed).
- v2 PENDING: Step-2 is emitting the exact delta=4.756e-5 cert. Open item on their
  side = R1 (the 317 moment-row eigenvectors v were discarded by cp_cache and are
  trajectory-unrecoverable; Step-2 is re-deriving the moment block as a fresh
  rational PSD Gram cert, GPT-Pro consult in flight). You receive: exact delta
  (Fraction), full dual (per-type lambda sum=1, band mu_lo/mu_hi, k8-leg a8,
  moment nu_j — all Fractions), the rationalized v / Gram cert, and a one-command
  verifier. Run YOUR independent check before v2 ships.
- Deficit cert dual_cert_n9.pkl is REFUTED + REMOVED (fixed profile-cut can't be
  tight at C5; C11 counterexample; t_ind type-density factor; balanced LP gave
  delta'=7.04e-3). Do NOT reintroduce deficit atoms anywhere.
- The 387-instance enumeration route to a(30)<=36 (H1) is ~15-25% done and is
  BYPASSED by the integrality shortcut (a(30)=a(5*6)=6^2=36 is a mult-of-5, closed
  by any delta<1/450). Do NOT invest more there. KNOWN BUG if any of those certs
  ever feed the writeup: search23/state_count_6195_cpsat.py L401-412 anti-tightness
  cut is ">=17", should be ">=16" (over-cuts => masks witnesses, soundness-safe
  direction, but un-trustworthy until re-run --disable-anti-tightness).
- H2 (peeling) + non-multiples-of-5 belong to the FULL induction, NOT v1/v2.
- H2 LEDGER REALITY (bridge/CLAIM_LEDGER.md, read 2026-06-26): H2 is TRUE+TIGHT on
  C5[n] (min 5-set drop = 2n-1). ALL local-certificate routes to its CF reformulation
  are REFUTED with explicit in-band tau_K=0 witnesses (Grotzsch[t], Grotzsch[5]+iso,
  K_{16,64}); "CF is irreducibly GLOBAL <=> the band conjecture". Live frontier =
  the 2-colored max-cut SWITCHING flag-SDP (bridge/flagsdp, Step-2's machine) + the
  Lambda_5 LAMBDA-BOUND sub-conjecture (Lambda_5(F)<=2r/5, eq iff C5-blowup; verified
  all tri-free bases r<=10, 0 violations). So H2 and Step-2's delta=0 have effectively
  MERGED at the flag-SDP; there is no separate tractable local Step-1 grind.
- RESOLVED 2026-06-26 (GPT-Pro, "Erdos Problem 23 Closure" thread c/6a3b8a74, audited):
  Step-2's delta=0 RETIRES H2. d_mono(W_G)=2 beta(G)/N^2 is EXACT (multilinear cut min
  at an integer vertex; no o(1)/rounding); delta=0 => beta(G)<=N^2/25 for ALL finite N
  incl. non-mult-of-5; the integrality trick was only ever needed for delta>0. So do
  NOT invest in proving H2 (the CLAIM_LEDGER "open core" is off the critical path).
  Step-1's full-conjecture job = the all-N assembly (above) + co-developing delta=0
  (the Gamma-lemma) with Step-2. The conjecture's ENTIRE remaining difficulty = delta=0.

================================================================================
LOOP (run every iteration)
================================================================================
1. Read this file + the tail of PROGRESS.md.
2. PROGRESS ► line: "[ISO-8601] ► <PHASE> | NEXT: <one concrete action + objective>".
3. Pick the active sub-task:
     - if Step-2's v2 cert has arrived but is not yet exact-verified -> verify it
       (regen_verify_u7 + Gram check + BCL tiling); on pass, prep + ship arXiv v2;
     - if v2 is shipped (or the cert hasn't arrived) -> co-develop delta=0 (the
       Gamma-lemma) with Step-2 and/or draft the all-N assembly (H2 is RETIRED).
4. At ANY decision point or when stuck -> consult GPT Pro VIA THE BROWSER TOOL
   (drive Chrome: send the self-contained question, wait, read the answer via
   main.innerText), audit it line-by-line + exact-Fraction-check, then proceed on
   the path GPT picks (do not deliberate in prose; execute the chosen path).
5. Do the work. ANY closure/bound claim MUST pass an EXACT Fraction check BEFORE
   you assert it. Numeric "eta<0 / promising / almost" is NOT a result.
6. PROGRESS ✔ line: "[ISO-8601] ✔/✘ <PHASE> | DID: <executed> | RESULT: <file/lemma/
   number/error — independently verifiable> | Δ: <status change or 'none'>".
7. Loop.

================================================================================
GUARDRAILS (never violate — these have caught 3 false closures)
================================================================================
- SOUND ATOMS ONLY: moment rows (G1 Gram-PSD), per-root-MaxCut U7/U8 envelope
  (per-type min_c, tight at C5), rooted-Horn (tight=0 at every odd cycle). All
  audited sound (7-agent adversarial pass, worst >= -1e-17). DEFICIT / fixed-
  profile-cut atoms are FORBIDDEN.
- Evaluate at the GRAPHON level via i.i.d. blow-up / count-vector density. NEVER
  finite distinct-subset (O(1/n) artifact: -6.7e-3 where true density is +1e-16).
- The EXACT rational Fraction certificate is the ONLY acceptance gate. No native_decide.
- BCL Thm 1.3 (arXiv:2103.14179) is the ONE imported dependency (density tails);
  cite it, do not re-derive its flag-SDP. The asymptotic-at-finite-n worry is
  RESOLVED via the uniform t-blow-up transfer (beta(G[t])=t^2 beta, density->m/450),
  NOT a finite-n BCL inequality — keep it that way.
- Commit as the user ALONE — NO "Co-Authored-By: ... anthropic/claude" trailer
  (breaks the Google CLA). Compute <= 64-100 workers (never 128), native clang++
  MT, never WSL. Never edit Step-2's flagsdp/* live-run files mid-solve.

================================================================================
COORDINATION (with Step-2)
================================================================================
- You OWN the single arXiv paper + the independent exact verification. Step-2 owns
  the flag-LP cert (delta) and the Gamma-lemma (delta=0 / full conjecture).
- Do NOT publish a Step-2 number until YOUR independent exact Fraction check passes
  (regen_verify_u7 + Gram-PSD + BCL tiling). Three false closures here were caught
  ONLY by the exact check; the earlier N<=180 deficit-reweight was unsound.
- H2 / Gamma-lemma is shared frontier — co-develop, don't duplicate. Relay through
  the user, in English.
