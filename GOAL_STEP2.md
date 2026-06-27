# STEP-2 AGENT — GOAL + LOOP   (Erdős #23, the n^2/25 max-cut conjecture)
# READ THIS FIRST ON EVERY RESUME. Then read the last ~30 lines of
# E:\Projects\ErdosProblems\PROGRESS.md to find exactly where you left off.

================================================================================
GOAL
================================================================================
PRIMARY (the real prize, all-or-nothing): prove the FULL conjecture —
  every triangle-free graph G on N vertices has beta(G) = e(G) - maxcut(G) <= N^2/25,
  for ALL N  (equivalently d_mono(W) <= 2/25 for every triangle-free graphon W,
  i.e. eta <= 0 / delta = 0).
  LIVE ROUTE = the Connected-B Gamma-lemma: bad edges M are odd chords of the
  bipartite frame B, ell = d_B + 1 >= 5; invariant Gamma = sum ell^2 <= N^2  ==>  beta <= N^2/25.
  Reduced to ONE open lemma: SYNC (block -> general). The block case (P5 lemma,
  sharp 25 = 5^2) is PROVED; Sync needs an electrical-flow / congestion argument,
  NOT scalar coarea (the scalar version has an audited counterexample).
  SUCCESS = a rigorous, gap-free proof of Sync ==> Gamma <= N^2 ==> full conjecture.

NEAR-TERM DELIVERABLE (do this FIRST — it is ~done and is a real publishable win):
  Emit your exact sound-atom certificate (delta = eta = 4.756e-5 < 5.0e-5) for
  Step-1's INDEPENDENT exact-Fraction verification. If it passes, Step-1 issues an
  arXiv v2 that extends a(5n)=n^2 from N<=55 (v1, delta=5.991e-4) to N<=200.
  Arithmetic: (25/2) n^2 delta < 1  ==>  delta=4.756e-5 closes n<=40 (N<=200).
  N<=200 is the flag-LP finite ceiling (self-tight wall plateaus eta above 0) — do
  NOT over-invest squeezing delta lower. Lock v2, then pivot fully to Gamma-lemma.

================================================================================
★ GPT PRO COLLABORATION (2026-06-26 user directive: "collab with gpt pro to finish
  step-2; use your browser tool to send and receive questions and answers")
================================================================================
- This is a STANDING collaboration: at every decision point / stuck point, consult
  GPT Pro and proceed on the path it picks ([[gpt-pro-decides-path]]).
- MECHANISM: use the Chrome MCP browser tools (mcp__Claude_in_Chrome__*) to SEND
  questions and READ answers DIRECTLY yourself — do not require the user to relay
  unless the browser is unavailable or the user explicitly takes it over.
    * ALWAYS OPEN A FRESH CHATGPT CONVERSATION per consult — navigate to
      https://chatgpt.com/  (NOT the old chat 6a3b5aba; that thread is overloaded
      with history and is slow/heavy). One new tab + new chat each time.
    * tabs_context_mcp{createIfEmpty:true} -> navigate to https://chatgpt.com/.
    * Type the question into the ProseMirror contenteditable (#prompt-textarea),
      submit, wait for streaming to finish (no stop-button). Use GPT Pro / the
      reasoning model if the picker is available.
    * READ the reply via javascript_tool on the last [data-message-author-role=
      "assistant"] innerText, sliced in <=1400-char chunks WITH char-substitution
      (= -> EQ, & -> AMP, ? -> QQ, http*:// -> URL, : -> COL) to dodge the harness
      cookie/query-string block. (See [[reading-gpt-replies-chrome-mcp]].)
- SAVE every GPT answer to bridge/gpt_pro_consultations/ before acting on it.
- If the user says they are relaying manually, let them; otherwise drive it yourself.

VERIFIABLE SUCCESS CRITERIA
  v2  : exact cert passes (a) regen_verify_u7.py exact-Fraction dual feasibility
        [per-type sum_c lambda_{sigma,c}=1; cut+band+moment per-state residual >= 0],
        (b) the moment-PSD Gram check [your rationalized v reproduce the rows AND
        M^sigma = sum_c w_c q_c q_c^T >= 0], (c) BCL band tiling; and
        delta_exact < 5.0e-5.  THEN Step-1 publishes v2.
  full: Sync proven sound (no gaps), Gamma = sum ell^2 <= N^2 established
        ==> beta <= N^2/25 for all N.

================================================================================
STATE (2026-06-26, reconciled with Step-1)
================================================================================
- Published v1 = envelope_k7_cert.pkl (per-root-MaxCut U_7, delta=5.991e-4, N<=55,
  multiples of 5). arXiv submit/7754052 (in queue).
- Deficit cert dual_cert_n9.pkl REFUTED + REMOVED (fixed profile-cut not tight at
  C5; C11 counterexample). Do NOT reintroduce deficit atoms.
- EXACT CERT IN FLIGHT: order-10 Horn LP, it16, delta=4.756e-5 EXACT (Fraction),
  full dual residual >= 0 at float (min +3.5e-12), dual extracted (horn_dual.pkl,
  horn_cert_state_it16.pkl). Cut atoms (k7=int/1814400, k8/Horn=int/90, dedge=
  int/45) recover exactly.
- R1 OPEN: the 317 moment rows m_j = v_j^T P^sigma v_j; cp_cache discarded the v_j;
  re-running cutting_plane gives DIFFERENT rows (trajectory-dependent eigenvectors,
  worst L2 2.24e-2). So the v_j are UNRECOVERABLE. R1 needs a FRESH rational PSD
  moment cert (re-derive Q>=0), NOT v-recovery. GPT Pro consult sent (option a:
  feasibility SDP for rational Q>=0 with sum_t D[t,s]<Q,P^sigma_t> <= R_cbh[s]).
- H2 (peeling) + non-multiples-of-5 belong to the full induction (Step-1 + shared
  Gamma-lemma), NOT v1/v2.

================================================================================
LOOP (run every iteration)
================================================================================
1. Read this file + the tail of PROGRESS.md.
2. PROGRESS ► line: "[ISO-8601] ► <PHASE> | NEXT: <one concrete action + objective>".
3. Pick the active sub-task:
     - if the v2 cert is not yet emitted + verified by Step-1  -> finish & hand it off
       (R1: emit the fresh exact moment-PSD cert + the full rational dual + verifier);
     - else  -> work the Gamma-lemma / Sync.
4. At ANY decision point or when stuck -> consult GPT Pro VIA THE BROWSER (send +
   read directly; see the GPT PRO COLLABORATION block), then proceed on the path
   GPT picks (do not deliberate in prose; execute the chosen path).
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
- BCL Thm 1.3 (arXiv:2103.14179) is the ONE imported dependency (density tails).
- Commit as the user ALONE — NO "Co-Authored-By: ... anthropic/claude" trailer
  (breaks the Google CLA). Compute <= 64-100 workers (never 128), native clang++
  MT, never WSL.

================================================================================
COORDINATION (with Step-1)
================================================================================
- Step-1 owns the single arXiv paper + the independent exact verification. Do NOT
  publish independently. Hand Step-1: exact delta (Fraction), full dual
  (per-type lambda sum=1, band mu_lo/mu_hi, moment nu_j — all Fractions), the
  rationalized v / Gram cert, and a one-command verifier. Step-1 runs
  regen_verify_u7 + the Gram check + BCL band tiling; only on pass does v2 ship.
- Relay through the user, in English, when not driving the browser yourself.
