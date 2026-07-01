# GOAL_LOOP.md — Erdős #23 proof agent, standing task (READ FIRST on every compaction / new session)
#
# Resume flow: (1) read this file; (2) read the last ~30 lines of PROGRESS.md = where you left off;
# (3) read MEMORY.md (the ACTIVE #23 block); (4) read the newest CODEX -> CLAUDE blocks in
#     coordination/CODEX_TO_CLAUDE.md (you reply in coordination/CLAUDE_TO_CODEX.md); (5) resume GOAL+LOOP.
#
# WHO: you are the EXACT-verification + proof-driver for #23 δ=0. Codex is the parallel proof-driver
# (coordination/CODEX_TO_CLAUDE.md ↔ CLAUDE_TO_CODEX.md). GPT-Pro ("Kapsamlı Pro") is consulted at
# decision/stuck points via the Chrome MCP (your own chat); Codex consults its OWN separate GPT-Pro chat.
# Last updated 2026-07-01 (end of the two-lane-refutation / LOAD-PSC / GERSH session).

================================================================================
GOAL
================================================================================
PRIMARY (the whole remaining prize): prove #23 for ALL triangle-free G on ALL N:
  beta(G) = e(G) - maxcut(G) <= N^2/25   (extremal = balanced C5[N/5]).

DONE / PUBLISHED (do NOT reopen): the FINITE-N certificates. v1 (N<=55) and the EXACT order-10 v2
  cert (delta=4.757e-5 < 5e-5 => a(5n)=n^2 for N<=200) are verified + PUBLISHED (memory
  erdos23-v2-cert-valid-n200). N<=200 is the flag-LP finite ceiling. The blow-up integrality identity
  d_mono(W_G)=2 beta/N^2 is EXACT (no rounding), so the SOLE remaining piece is:

  ** delta=0 (the graphon band bound d_mono(W)<=2/25 on the medium density band) = the WHOLE remaining
     conjecture. ** Equivalently the Gamma-lemma:  Gamma(G) = sum_{f in M} ell(f)^2 <= N^2  on every
     B-connected gamma-minimal maximum cut (M = monochromatic/bad edges; ell(f) = length of the shortest
     odd cycle through f). Gamma = sum_v T(v), and Gamma<=N^2 => beta<=N^2/25.

CURRENT REDUCTION (this is the live map — verified exact unless marked OPEN):
  beta<=N^2/25  <==  Gamma<=N^2  <==  LRS: sum_v T(v)^2 <= L*Gamma   (L = N + N^2/25 - m, m=|M|)
                                <==  CV (component-local): for each geodesic K-component C,
                                         sum_{v in C} T^2 <= L * sum_{v in C} T
                                <==  GERSH:  ROWSUM(f) = sum_{g in M} <p_f,p_g> <= A = L = N+N^2/25-m,
  where p_f(v) = (#shortest geodesics of f through v)/|cyc[f]|, T(v)=sum_f ell(f) p_f(v).
  VALID reduction (Claude-verified linear algebra): rowsum_f(O_C)=ROWSUM(f) (cross-component overlaps
  vanish); Gershgorin => GERSH => rho(O_C)<=A => A*I-O_C PSD => CV (= ell_C^T(A*I-O_C)ell_C>=0 at ell_C=(ell(f))).

  ** THE SOLE OPEN LEMMA = GERSH = "corrected ROWSUM-O": ROWSUM(f) <= N + N^2/25 - m. **
  This is the OLD ROWSUM-O with the CORRECTED ceiling L instead of N. It is exact-verified 0-fail on the
  full battery (census N<=11, two-lane L<=100, Myc-Grotzsch N23, glued islands, C5 blow-ups), tight only
  at balanced C5[t] (where A=N). UNPROVEN. Cleanest sub-form = ROWWISE-GERSH (per geodesic corridor Q):
  sum_{v in Q}(sum_{g in M_C} p_g(v)) <= A, tight at EVERY C5[t] corridor. Attack = deficit-capacity
  CAGE/Hall transport: route ROWSUM mass onto N vertices + a budget of size N^2/25-m from the uncut deficit.

C5-COLORABLE subcase is PROVEN (cyclic-min-product 25*min_i n_i n_{i+1} <= N^2, 1/25=(1/5)^2, eq iff
  balanced C5[N/5]). The OPEN CORE = non-C5-colorable triangle-free graphs (Grotzsch/Mycielskian/odd-girth).
  RISK (unresolved, BREAKTHROUGH_VERDICT.md 2026-06-29): GERSH/CV may be hardness-equivalent to the conjecture.

METHOD (standing user directive): FINISH in active collaboration with Codex + GPT-Pro. At every decision
  or stuck point, consult GPT-Pro via the Chrome MCP (drive your Kapsamlı Pro chat: send a self-contained
  question, read the answer, chunk main.innerText). Audit every GPT-Pro / Codex claim line-by-line and
  EXACT-Fraction-check on the full battery BEFORE adopting. The browser round-trip is PART of the loop.

VERIFIABLE SUCCESS = a sorry-free proof of GERSH (=> Gamma<=N^2 => beta<=N^2/25 for all N), exact-gated,
  then formalized (all-or-nothing: nothing ships until sorry-free Lean -> ONE formal-conjectures PR).

================================================================================
STATE (2026-07-01)
================================================================================
- SPECTRAL / 2nd-moment program is DEAD. rho(O)<=N, rho(K)<=N, rho(K2)<=N (CSM-SPEC / cycle-Hardy (H)),
  ROWSUM-O<=N, and the K2T "descent lemma" (gamma-min => K2*T<=N*T) are ALL FALSE. Killer = the two-lane
  family build_two_lane(L) (_verify_two_lane.py): L=12, N=39, UNIQUE gamma-min global-max cut, yet
  rho(K2)=rho(K)=rho(O)=40.21 > 39, R[v]=-60 on 9 verts, no Gamma-descent, while Gamma=492<<N^2=1521.
  K=PP^T, O=P^T P => rho(K)=rho(O), so ANY rho(.)<=N or ||T||^2<=N*Gamma route is arbitrarily false.
  The old 18690-cut _hardy_gate / _csmspec battery MISSED two-lane (census-pass != proof).
  (Claude re-derived this dead spectral chain early in the 07-01 session and the two-lane gate caught it.)
- LIVE first-moment target = LOAD-PSC-5 capacitary TV inequality
    5*sum_v a_tau(L-a_tau) >= N*(TV_B(a_tau)-TV_M(a_tau)),  a_tau=min(T,tau), L=N+N^2/25-m, all tau.
  Proven pieces: coarea identity LOAD-PSC-5 <=> Phi(tau)=25 sum a(L-a) - 5N(TV_B-TV_M) >= 0;
  sigma_s = delta_B(H_s)-delta_M(H_s) >= 0 UNCONDITIONALLY (any set-flip lowers the max cut); LOW-HARD-P5
  (2b<=N & Gamma>Nh => sigma<=5h). Per-level route is DEAD (exact cex to sigma<=5|H|, LOW-D, theta-split,
  per-vertex charge) => proof is irreducibly global/transport => reduces to component-local CV = GERSH (above).
- GERSH / CV / component PRESSURE-SURPLUS / ROWWISE-GERSH: all 0-fail on the full battery incl two-lane +
  Myc N23; GERSH reduction to CV is VALID linear algebra (Gershgorin). Sole open lemma = prove GERSH.
- Files (problems/23/writeup/ + scratchpad): LOAD_PSC_COMPONENT_CRUX.md (consolidated writeup),
  _loadpsc_gate.py, _cv_component_gate.py, _component_spectral_check.py, _codex_gersh_rowwise_gate.py,
  _lowhardp5_gate.py, _lowhardexcess_gate.py, _rowwise_tightness.py, _verify_two_lane.py, _twolane_k2_check.py.
- STALE / do-not-pursue: CODEX_GOAL.md, ROWSUM_O_reduction.md (ROWSUM<=N version), all spectral GLOBAL
  routes, all per-level shortcuts, no-two-hole/AtMostOneMiss (false on hard-H3), RFC/NL, GPT-Pro C5-collapse
  slogan (PASS_VACUOUS — antecedent empty on finite instances).
- Chrome MCP dropped mid-session (07-01) then reconnected; when down, route GPT-Pro consults via Codex.

================================================================================
LOOP (run every iteration)
================================================================================
1. ORIENT: read this file + PROGRESS.md tail + MEMORY.md ACTIVE block + new CODEX -> CLAUDE blocks.
   PROGRESS ► line: "[ISO-8601] ► <PHASE> | NEXT: <one concrete action + objective>".
2. PROCESS CODEX: for each new ASK, exact-gate it (Python Fraction) on the FULL battery -- census N<=11,
   two-lane L>=12 (the mandatory spectral-killer control), Myc-Grotzsch N23, glued islands, C5 blow-ups,
   ALWAYS on gmins cuts (never the natural C5 cut). Reply RESULT in CLAUDE_TO_CODEX.md. Exact-verify any
   GPT-Pro answer Codex relays before trusting.
3. ADVANCE THE PROOF: prove GERSH = ROWSUM(f) <= N+N^2/25-m (deficit-capacity CAGE/Hall; or the
   per-corridor ROWWISE-GERSH). Test building blocks exactly; a battery pass is NOT a proof.
4. WHEN STUCK: consult GPT-Pro via the Chrome MCP (drive your Kapsamlı Pro chat: send ONE self-contained
   question, read the answer). Audit + exact-Fraction-check before adopting; then execute the path it picks.
   (If Chrome is down, ask Codex to relay to its GPT-Pro.)
5. EXACT gate everything. Numeric "eta<0 / promising / almost" is NOT a result. Update PROGRESS ✔, MEMORY,
   and the writeup. Loop.

================================================================================
GUARDRAILS (never violate — these have caught every false closure)
================================================================================
- EXACT rational Fraction is the ONLY acceptance gate. No floats for pass/fail. No native_decide.
- BEFORE trusting ANY load-matrix spectral / second-moment bound, gate the TWO-LANE family
  build_two_lane(L>=12) FIRST. It kills rho(O)/rho(K)/rho(K2)/||T||^2<=N*Gamma. Also read BREAKTHROUGH_VERDICT.md.
- gamma-min = B-connected MAX cut minimizing Gamma=sum ell^2 (use gmins). NEVER the natural C5 part-parity
  cut -- it is NOT the max cut on unbalanced blow-ups (=> false GERSH/ROWSUM failures; wrong-cut artifact).
- ALL-OR-NOTHING: nothing ships until a sorry-free Lean proof -> ONE formal-conjectures PR.
- Commit as the USER ALONE -- NO "Co-Authored-By: ...anthropic/claude" trailer (breaks the Google CLA).
- Compute <= 64-100 workers (never 128); native clang++ via MSYS2, never WSL.
- Surface to the user ONLY for: a VERIFIED proof/closure, a one-line verdict, or a real decision.

================================================================================
COORDINATION
================================================================================
- Codex + you jointly own the δ=0 / GERSH proof. Channel: coordination/CODEX_TO_CLAUDE.md (read) +
  CLAUDE_TO_CODEX.md (write). Codex proposes lemmas/sublemmas; you exact-gate + hunt counterexamples.
- The finite-N arXiv paper (v1+v2, N<=200) is PUBLISHED; the all-N assembly is gated on the δ=0 proof.
- A plausible-looking proof from Codex or GPT-Pro is NOT a proof until it passes your exact gate on the
  full battery INCLUDING the two-lane control.
