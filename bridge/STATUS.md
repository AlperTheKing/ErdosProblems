# Step-2 STATUS — Erdős #23 induction (a(5n) <= n^2)

Owner: Step-2 lead. Codex owns Step 1 (a(30)=36) + `bridge/CODEX_STATUS.md`.
Last updated: 2026-06-21T01:20+03:00.

## ★★★ CURRENT STATE (2026-06-21) — READ FIRST (supersedes everything below)

**Active route = a 2-COLORED MAX-CUT SWITCHING FLAG-SDP for β directly** (GPT Q15 pivot). The whole
τ_K/Clebsch-frustration (CF) line below is EXHAUSTED as a *proof* route (every local + 2nd-moment variant
provably too lossy: Q12 coverage refuted by Grötzsch; Rung-4 deletion, Q14 1-opt charging, eq9-at-global-min
all too lossy; see ledger CF + Q12/Q14/Q15 audits). CF itself tests TRUE (worst R=τ_K/RHS≈0.40; (★) holds at
global min) but is irreducibly global.

**GPT Q15 strategy (AUDITED):** drop τ_K (16-state surrogate = liability); work directly with β, fix a GLOBAL
max-cut as a 2-coloring (A/B), impose MACROSCOPIC switching inequalities. Switching Lemma SW1 verified ≤0 on
max cuts. C5-cleanup β≤(e+4d₅)/5 proven but insufficient standalone (d₅≤(N²/5−e)/4 FALSE near band-top).

**Flag-SDP machine BUILT + VALIDATED** (`bridge/flagsdp/`, Python+cvxpy, from scratch; reproduces Mantel
edge-density=1/2 EXACTLY). Primal: max d_mono (=mono-edge density; β/N²→d_mono/2) s.t. moment matrices
M^σ(x)⪰0 + edge-band + rooted-switch constraints; TARGET d_mono≤2/25=0.08 (β/N²≤1/25). Separation oracle +
vectorized build.
**RESULT — robust PLATEAU at β/N² ≈ 1/20** (d_mono≈0.10): band-only 0.32→+0root 0.16→+1root 0.118→+2,3root
0.10, then converges. Flag order does NOT help (k≤1 = 0.118 identical at N=5,6,7). Pseudo-graphon = diffuse
band-top mix ~30% mono-frac (vs C5's 20%). This is the best certified bound of the session (beats all prior
~1/17 routes) but is a BOUND, not a proof, and is short of 1/25.
**GPT Q16** (chat "Beta Bound Plateau Analysis" c/6a370bb0...): asked if 1/20 is the wall / how to break it —
appears DEGENERATE (reasoning preview frozen ~30+ min, matches earlier failed-run signature).
**★ FLAG-SDP plateau diagnosed (2026-06-21):** the 1/20 plateau = the balanced CLEBSCH blow-up at a
1-switch-stable NON-global cut (Clebsch: global max cut 8 mono/40 = frac 0.20; worst 1-switch-stable cut
12 mono = frac 0.30 → β/N²≈1/21≈plateau). GPT Q16 (relayed fresh session, AUDITED `verify_q16_badcut.py` —
bad-cut A₀ fingerprint fully verified: e40/cut28/mono12, margins (3,2,1)×12+(5,0,5)×4, switch {13,23,45,1245}
gains 4, identity ΣH+2e_M−2e_C=−4) gives the BREAK and **corrects the earlier "fundamental wall" claim**:
1/20 is only the SHALLOW UNMARKED hierarchy's wall (3/64), NOT fundamental. FIX = (i) EXACT switch separation
(coord-ascent was inexact — DONE, but insufficient alone); (ii) MARGIN COLORS A_L/A_H/B_L/B_H by H(x)=cut-deg−
mono-deg, split at t=1/8, with consistency localizers; (iii) the margin-conditioned 2-root switch (destroys the
bad cut). Diagnostic confirmed: unmarked switch detects the bad cut at order-16 (k2=68,k3=228) but not at
order-5/6 without margin marks. **Phase F (margin-color lift) IN PROGRESS** — k-color engine built+validated
(flag_engine_kcol.py); next = margin SDP + localizers + margin switch, target d_mono below 3/32 toward 0.08.
**Bottom line:** flag-SDP gives the session's best certified bound (1/20, beats all prior ~1/17) but is NOT a
proof and is at a characterized limit. All three Step-2 routes (peeling H2 / τ_K-CF / flag-SDP) now hit
well-understood walls; the problem is genuinely research-grade open. Step 2 / β≤n² UNPROVEN. No fabrication.

**Base cases / H1:** Codex grinding the a(30) medium window (q8 all-D a9b9, ~p26); 0 FEASIBLE (no β≥37
witness) — safe but NOT complete/audited. **Completion NOT reached:** Step 2 / β≤n² UNPROVEN (flag-SDP at
1/20, not 1/25, no exact certificate). H2 peeling unproven. No fabrication.

---
## (historical, pre-2026-06-21 — τ_K/CF + H2 era, superseded by the block above)

## ★ CURRENT STATE (2026-06-20, comprehensive) — read this first

**Reduction PROVED** (Step1 `a(30)<=36` + Peeling Lemma H2, n>=7 ⟹ `a(5n)<=n²` ∀n;
exact telescoping; bases n=1..6). The full conjecture is the OPEN medium-density case
of Erdős #23. Session's VERIFIED results (each independently checked):
- **A7 (PROVED, exact):** `{C3,C5}`-free ⟹ `β<=N²/32`, so `a_7(5n)<n²`; hence a tri-free
  `β>=n²` graph has an induced C5 (`MAXCUT_BOUNDS`/A7; via the radius-2 ball MaxCut
  lemma; verified 301172 graphs N<=12). C5-stability entry point.
- **RAD2 (PROVED + verified):** `β <= e/2 − (Q−T)/2N − D/N` (D=Σ(MaxCut(H_v)−S_v)),
  TIGHT at C5[n]; and the corrected RHS `<= N²/25` for ALL tri-free graphs (verified
  N<=11, eq only at C5[n]). So the WHOLE conjecture ⟺ `Q−T+2D >= Ne−2N³/25`
  ⟺ `Σ_v β(H_v) <= (Q+T−Ne)/2 + N³/25`. **The open core = lower-bounding D
  (the cut-realignment surplus).** Scalar relaxations cap at 1/16–1/17.2 (GPT Q7,
  Clebsch-obstructed). GPT δ₂/D-bound consult in progress.
- **MERGE + STRICT-FLIP (PROVED):** codeg-0 common-side pair merges preserving β; frozen
  pair forces `2m(u)<c(u)`. WYZ arXiv:2408.05547 confirmed FINITE (`δ₂>⌊N/8⌋⟹hom-C5`):
  δ₂ dichotomy (high-codeg closed). BU2 blow-up case verified n<=20 (all explicit rules
  refuted; smoothing also). Dead-ends pruned: SDP/spectral/local-count/weighted.
- **BASE CASES / H1:** BCL finiteness gap (flagged by Step-2) RESOLVED for density TAILS
  via Codex's uniform blow-up transfer (audited SOUND): a(30) `e<=111`&`e>=144` closed,
  a(25) `e<=77`&`e>=100` closed. Remaining = finite MEDIUM windows (a(30): `112<=e<=143`;
  a(25): `78<=e<=99`) — Codex enumeration IN PROGRESS.
- **H2 PEELING OBJECT PINNED + VERIFIED n≤4 (2026-06-20):** `verify_h2_5set_c5n.py` +
  native C++ `h2_check_edgelist.exe` ⟹ `min_S[β(C5[n])−β(C5[n]−S)]=2n−1` EXACTLY for
  n=1,2,3,4 (C5[4]: β=16, min drop=7), minimizers = `n⁵` C5-TRANSVERSALS (removal →
  C5[n−1]). H2 TRUE & TIGHT at the extremizer (2nd-workflow critic's "H2 fails at C5[2]"
  = harness bug, REFUTED). Right peeling object = near-C5-transversal ⟹ couples to
  C5HOM/WYZ. Averaging/LP DEAD (mean drop > 2n−1). Crux = GLOBAL cut-realignment.
  **NO H2 counterexample found:** n=2 exhaustive; n=3 794500 random + agent-claimed
  exhaustive 286699 (≥42 edges); n=4 all structured hard cores incl. Petersen[2] (β12,
  drop5<7), Cay(Z20,{1,4,9}) (β12,drop5), C5[4]−edge (β15,drop6). 3 multi-agent workflows
  = 0 proofs (discharging "proof" REFUTED: separable deficiency overcounts joint gain).
  Remaining route needs an EFFECTIVE stability theorem near C5[n] (research-grade). GPT
  brief Q9 ready. `H2_ATTACK_FINDINGS.md`.
- **★ CLEBSCH-FRUSTRATION reduction (2026-06-20, GPT Q9 — AUDITED+VERIFIED):** the open core
  is REFRAMED. PROVEN: Clebsch-hom ⟹ β≤N²/25 (enlarges C5HOM) + uniqueness=C5[n]; τ_5≥7/800 N²
  (robust C5-abundance). NEW REDUCTION: β≤(e+2τ_K)/5, so conjecture-in-band ⟸ `τ_K(G)≤(N²/5−e)/2`
  where τ_K = Clebsch frustration (16-state quadratic CSP). Open core now = the explicit asymptotic
  statement **CF** (asymptotic ⟹ exact via blow-up; flag-algebra-amenable) — sharper than "stability".
  Plus a finite H2-falsification test Λ₅(F). `gpt_pro_consultations/Q9_ANSWER_AND_AUDIT_2026-06-20.md`,
  ledger CLEBSCH, `verify_clebsch_frustration.py`. **NOT solved — CF unproven.**
**Completion NOT reached:** open core = D-bound / H2 realignment (medium-density); H1
medium window in progress. No fabrication. See ledger A7/RAD2/MERGE/WYZ-CODEG/H2/DEP-a25,
`H1_AUDIT_LOG`, `H2_ATTACK_FINDINGS`.

## One-line state (earlier, superseded by the block above)

Reduction **PROVED** (Step1 a(30)<=36 + Peeling Lemma (H2) ⟹ a(5n)<=n^2 ∀n, all
base cases n=1..6 verified). Open core = (H2). Progress: exact closed form
`beta(C5[m]) = min_i m_i m_{i+1}` PROVED; **blow-up case of (H2) proved in the
tight regime** (Case A) + verified n<=6; per-graph (H2) verified EXHAUSTIVELY at
n=2 (unique saturator C5[2]) and on strong structured candidates at n=3,4 — no
counterexample, C5[n] uniquely tight (Sharp Peeling Conjecture). General (H2)
remains open (needs cut-aligned/stability ideas); GPT Pro brief prepared.
**2026-06-20:** blow-up case (BU2) case-split now COMPLETE+explicit — R1 (P<=2n-1
trivial) + R2 (regime P>=2n has <=1 size-1 class), both PROVED; exhaustive
Δ_best<=2n-1 verified n<=15, worst UNIQUELY balanced C5[n]; sole open piece = one
heavy-pair inequality (all m_i>=2, P>=2n). See `BU2_REGIME_REDUCTION.md`. Also
proved exact MaxCut bounds L0/L1 (`MAXCUT_BOUNDS.md`): `β<=⌊(e-Δ)/2⌋` triangle-free,
giving unconditional `e<=73⟹β<=36` (handed to Codex for the low-edge band).

## Done (audited)

- `REDUCTION_THEOREM.md`: `(H1) a(30)<=36` and `(H2) peeling, n>=7` ⟹
  `a(5n)<=n^2 ∀n>=1`. Telescoping exact, base cases n=1..6 from
  OEIS A389646 / project a(25)=25 / Codex a(30)=36. **Fully proved & audited.**
- `PEELING_LEMMA.md`: exact tightness of `2n-1` on `C5[n]`; greedy half-cut is
  ~2.5x too weak; hardness placement vs BCL; weaker sufficient forms; min-
  counterexample framing; **§9 blow-up case: closed form BU1 (PROVED) + BU2
  Case A (PROVED tight regime) + n<=6 exhaustive.**
- `experiments/`: EXP-1 exhaustive n=2 (12172 graphs, pc<=3, unique saturator
  C5[2]); EXP-2 structured n=3,4 (no counterexample, C5[n] unique tight); EXP-3
  exhaustive blow-up peeling n=2..6 (worst pc=2n-1 at balanced).
- GPT Pro consultation #1 brief: `gpt_pro_consultations/Q1_*` (+ signal
  `GPT_PRO_QUESTION.md`).

## In progress / next

- **GPT Pro Q1 SENT** (chat c/6a35992e, "Erdős Problem 23 Lemma", Pro Extended);
  awaiting reply, will audit. Prioritised (A) cut-extension>50% + (C) min-ctrex.
- General (H2): cut-aligned extension (>50% extraction) + exact stability cleanup.
- BU2 Case B: TRUE + verified n<=10, but water-filling REFUTED (EXP-5); the
  optimal removal "preserve binding/pivot part, balance the rest" lacks a clean
  proof yet (likely a discrete-derivative/concavity argument). NOT critical path.
- Minimal-counterexample (MC1 done): leverage edge-criticality + stability.

## Loop state (2026-06-19 ~23:30) — GPT-Pro Q1 DONE, audited, integrated

GPT-Pro Q1 (chat c/6a35992e, ~70 min) completed. Independently AUDITED
(`gpt_pro_consultations/Q1_ANSWER_AND_AUDIT`): 2 errors caught (its Lemma 5
proof reversed an inequality = REJECTED; an arithmetic slip in eq 7, harmless).
ADOPTED (re-derived) results:
- **MC2 (no-light-boundary):** every 5-set has boundary `>= 4n-2`; `<=4` vertices
  have degree `< ~0.8n` — strong strengthening of MC1.
- **MC3 (two-dominating C5 / root defect):** a 2-dominating induced C5 forces
  `β<=n^2`; gives a finite stability parameter `def(S)` (route f).
- **MC4 (Frozen-pair reformulation):** `a(5n)<=n^2 ⟺` no triangle-free `β=n^2`
  graph has a codegree-0 nonedge frozen-together in all max cuts. ROOTED, handed
  to Codex.
- Confirmed: GPT's drop identity = my PCI; per-graph H2 may exceed what's needed.

Next live target: the Frozen-pair saturation statement (MC4), attacked via MC2 +
MC3 (bounded-defect C5) + finite cleanup; plus GPT's suggested low-load-unlocking
census (sec 4). Codex Step-1 healthy.

## Loop state (2026-06-20 ~03:00) — GPT UNAVAILABLE this session (degenerate after Q1)

GPT-Pro-Extended produced a real answer ONLY for the first query Q1 (18.9k chars,
audited → MC2/MC3/MC4). EVERY subsequent consult is degenerate: Q2="A"+stall,
Q2b=empty, Q3="Radius"/"B" (even in a fresh chat, after ~70 min reasoning). This
is a persistent quota/glitch (NOT a rate-limit; the "sınır" reads were false
matches on "sınırlıyor"). The pending sub-bound question is saved in
`GPT_PRO_QUESTION.md` for the USER to relay manually.
**Remaining resumption trigger: Codex H1 (closing its certificate / addressing
the BCL flag).** Core H2/MC4 open; BU2 min>=2 verified-not-proved; BCL base-case
gap needs Codex enumeration. Structural small-n investigations largely exhausted.

## Loop state (2026-06-20 ~00:37)

- GPT Q1: DONE, audited, integrated (MC2 no-light-boundary, MC3 two-dominating-C5
  + root defect, MC4 frozen-pair). 2 GPT errors caught/rejected.
- GPT Q2 (bounded-defect-C5 crux): STALLED (literature-search froze, no output).
  Re-sent as Q2b (math-only, no web search) — generating; will audit on landing.
- Base cases: n=1..4 OEIS (n=2 also Step-2-exhaustive-confirmed); n=5 a(25)=25
  AUDITED-SOUND modulo BCL high-density finite-exactness at N=25 (global BCL bound
  n^2/23.5 only gives a(25)<=26; high-density n^2/25 is the precise dependency);
  n=6 a(30)<=36 Codex IN PROGRESS (eR16 INFEASIBLE), audit checklist pending.
- The THREE inputs to close the bridge: (i) H2/MC4 [OPEN, the research core];
  (ii) a(25)=25 [audited-sound, 1 citation to fully nail]; (iii) a(30)<=36
  [Codex, in progress].
- Computational: no peeling-lemma counterexample anywhere (exhaustive n=2,
  structured n=3/4, blow-ups n<=13, random dense n=4, annealing); C5-free graphs
  have small beta (supports MC3 route); sub-bound a_7(5n)<n^2 is the live target
  (Q2b + C7-blowup gives 0.51n^2).

## ⚠️ BCL-FINITENESS GAP (2026-06-20) — affects BOTH base cases

Verbatim audit of Balogh–Clemen–Lidický (arXiv:2103.14179, two WebFetches):
Theorem 1.3 (global `n^2/23.5`; high-density `>=0.3197C(n,2)`; low-density
`<=0.2486C(n,2)` ⟹ `D2<=n^2/25`) holds only **"for n large enough"**; §2.3:
"only holds for n>=n0 for some n0 large enough", NO explicit n0.
- **a(25)=25** (n=5 base, project): its proof applies BCL high-density AT n=25 to
  force `e<=95` — UNJUSTIFIED unless n0<=25. n=5 base case now has a GAP.
- **a(30)<=36** (n=6 base, Codex/H1): its edge-range reduction `109<=e<=139`
  uses BCL at n=30 — same gap. FLAGGED to Codex (HANDOFF_TO_CODEX URGENT).
- MC5's medium-density window placement is asymptotic-only (corrected).
The unconditional finite fact `e>=2*beta` (so counterexample density `>=0.16`)
stands. Resolution needs a finite-n density bound / direct argument / extended
enumeration for both n=25 and n=30.

**UPDATE 2026-06-20 (later) — ★ BCL FINITENESS GAP RESOLVED for the density TAILS
(Codex uniform blow-up transfer; Step-2 audited SOUND, `H1_AUDIT_LOG`).** A 30-vtx
`β>=37` counterexample `G` has uniform blow-up `G[t]` triangle-free with
`β(G[t])=t²β(G)` and `density(G[t])→e(G)/450`; so `e<=111` (BCL low) and `e>=144`
(BCL high) each contradict BCL `β(G[t])<=(30t)²/25` for large `t`. RIGOROUS (modulo
citing BCL Thm 1.3). This converts BCL's ASYMPTOTIC tail bounds to FINITE n=30 —
exactly the gap Step-2 flagged. **Remaining for a(30): only the medium window
`112<=e<=143`** (finite enumeration; rooted `109-139` campaign was `149/149
INCONCLUSIVE`, ~500k T2 rows uncertified). **The SAME transfer resolves a(25)'s gap
tails** (`e<=77`, `e>=100`); remaining a(25) window `78<=e<=99`. So BOTH base cases'
BCL gaps are reduced from "asymptotic-unjustified" to "narrow finite medium window,"
which is exactly the kind of thing Codex's exact enumeration closes.
[Earlier note, superseded: Codex's finite 7-deletion-to-McKay closed `74<=e<=98`;
Step-2's L0 gives `e<=73⟹β<=36` unconditional. Both remain valid independent checks.]

## Honest bottom line (unchanged)

Reduction + base cases + blow-up tight case + MC1 are PROVED. The general Peeling
Lemma (H2) is the open core, equivalent to the exact constant 1/25 in the
medium-density regime (BCL-open). No fabrication: a complete Step1⟹#23 theorem
is NOT yet in hand and is not reachable by elementary means found so far.

## Blocked / open

- (H2) itself — the whole problem. No elementary route found; greedy is
  non-competitive. Pursuing cut-aligned peeling + stability cleanup + GPT.

## Key facts ledger (numbers I rely on)

- a(5n) known: a(5)=1, a(10)=4, a(15)=9, a(20)=16, a(25)=25, a(30)=36(Codex).
- derivative a(5n)-a(5(n-1)) = 2n-1 with EQUALITY for all n=2..6 (data) — strong
  evidence (H2'') holds tightly.
- beta(C5[n]) = n^2, e(C5[n]) = 5n^2, 2n-regular.

## Next actions (priority order)

1. Build beta/peeling tester (C++ or Python) and run on `geng -t 10`.
2. Hand-verify peeling-set rule on C5[n], unbalanced blow-ups.
3. Write GPT_PRO consultation #1; if no live access, drop GPT_PRO_QUESTION.md.
4. Formalize the minimal-counterexample structure lemmas (high min degree).
