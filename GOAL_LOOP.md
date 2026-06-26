# GOAL_LOOP.md — STEP-1 AGENT standing task (READ FIRST on every compaction / new session)
#
# Resume flow: (1) read this file; (2) read the last ~30 lines of PROGRESS.md = where you left off;
# (3) resume the GOAL + LOOP below.
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
PRIMARY (the real prize, all-or-nothing): the FINITE + INDUCTIVE half of the full
conjecture — turn the graphon bound d_mono(W) <= 2/25 (Step-2's delta=0) into
  beta(G) = e(G) - maxcut(G) <= N^2/25  for ALL triangle-free G on ALL N vertices.
  This needs the parts the flag-LP + integrality shortcut does NOT give:
   (i)  H2, the PEELING LEMMA ("the open core", CLAIM_LEDGER.md): reduce a putative
        all-N counterexample to the graphon/band regime. H2 and Step-2's delta=0
        almost certainly SHARE the cut-geometry ingredient (the Connected-B
        Gamma-lemma, Gamma = sum ell^2 <= N^2). Co-develop it with Step-2.
   (ii) the rigorous all-N / all-residue ASSEMBLY: BCL tails (<=0.2486, >=0.3197) +
        Step-2 band + blow-up integrality, with the non-multiple-of-5 residues and
        the small-N base cases handled exactly.
  SUCCESS = a gap-free proof of #23 for all N, assembled in ONE paper.

NEAR-TERM DELIVERABLE (do this FIRST — it is a real, in-hand publishable win):
  Independently EXACT-verify Step-2's sound-atom certificate (delta = 4.756e-5)
  and, on pass, ship arXiv v2 extending a(5n)=n^2 from N<=55 (v1, delta=5.991e-4)
  to N<=200. You OWN the single arXiv paper and the verification gate.
  Arithmetic: (25/2) n^2 delta < 1  ==>  delta=4.756e-5 closes n<=40 (N<=200);
  n=40 threshold = 2/(25*1600)=5.0e-5, n=41 = 4.76e-5. N<=200 is the flag-LP
  finite ceiling (the order-9/10 self-tight wall plateaus eta above 0) — do NOT
  push Step-2 to squeeze delta further. Lock v2, then co-develop H2 / Gamma.

VERIFIABLE SUCCESS CRITERIA
  v2  : Step-2's cert passes (a) regen_verify_u7.py exact-Fraction dual feasibility
        [per-type sum_c lambda_{sigma,c}=1; cut+band+moment per-state residual >= 0
        in Fractions], (b) the moment-PSD Gram check [Step-2's rationalized v
        reproduce the moment rows AND M^sigma = sum_c w_c q_c q_c^T >= 0 exactly],
        (c) BCL band tiling [<=0.2486, [0.2486,0.3197], >=0.3197 tile [0,0.5] with
        shared endpoints, no gap]; and delta_exact < 5.0e-5.  THEN publish v2.
  full: H2 proven gap-free; the all-N/all-residue assembly closes; with Step-2's
        delta=0 (Gamma-lemma) ==> beta <= N^2/25 for all N.

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
- OPEN STEP-1 STRATEGIC QUESTION (queued for GPT): does Step-2's delta=0 (graphon
  bound for ALL triangle-free graphons) ALREADY imply beta(G)<=N^2/25 for all N via
  the published blow-up-integrality machinery (beta(G[t])=t^2 beta(G), multilinear
  maxcut => d_mono(W_G)=2 beta(G)/N^2 exactly), thereby RETIRING H2 — or does the
  fractional->integer gap at non-multiples-of-5 still require H2 / a separate
  integrality argument? Resolve before investing in H2.

================================================================================
LOOP (run every iteration)
================================================================================
1. Read this file + the tail of PROGRESS.md.
2. PROGRESS ► line: "[ISO-8601] ► <PHASE> | NEXT: <one concrete action + objective>".
3. Pick the active sub-task:
     - if Step-2's v2 cert has arrived but is not yet exact-verified -> verify it
       (regen_verify_u7 + Gram check + BCL tiling); on pass, prep + ship arXiv v2;
     - if v2 is shipped (or the cert hasn't arrived) -> work H2 / the Gamma-lemma
       assembly, co-developing the cut-geometry ingredient with Step-2.
4. At ANY decision point or when stuck -> consult GPT Pro, then proceed on the
   path GPT picks (do not deliberate in prose; execute the chosen path).
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
