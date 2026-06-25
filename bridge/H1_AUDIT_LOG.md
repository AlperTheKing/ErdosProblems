# H1 (a(30)<=36) — Step-2 independent audit log

Owner: Step-2 lead. Records Step-2's INDEPENDENT verification of Codex's closed H1
components as they land, against the `NEEDED_FROM_STEP1.md` checklist. H1 is NOT
marked PROVED here; this only pre-validates pieces so the final global audit is fast.

Two distinct audit layers (keep separate):
- **(item 5) certificate consistency** — counts sum to the declared universe, every
  status INFEASIBLE, duplicates unioned by key, zero UNKNOWN/FEASIBLE/missing.
  Step-2 CAN verify this independently from the artifacts.
- **(item 1) search-space completeness** — that the declared task universe really is
  ALL subproblems (rooting/branching drops no case) and that each INFEASIBLE verdict
  is solver-correct. Step-2 CANNOT verify this without Codex's full derivation /
  re-running solvers (= redoing enumeration, disallowed). Remains Codex's global audit.

---

## 2026-06-20 — eR16 union (`6195, e_R=16`) — item-5 PASS

Artifact: `search23/state_count_6195_er16_clean_infeasible_union.tsv` (10.6 MB).
Independent Python re-count (NOT Codex's `verify_state_count_union.exe`):

| check | result |
|---|---|
| rows_read | **63867** (matches Codex) |
| unique `(mask,P,M)` | **59823** = `2601 * 23` (matches Codex's declared universe) |
| duplicate rows | **4044** (matches Codex) |
| status histogram | `{INFEASIBLE: 63867}` — **all INFEASIBLE** |
| non-INFEASIBLE rows | **0** (no FEASIBLE/UNKNOWN/NO_STATUS/missing) |
| distinct masks | 2601 (each mask carries exactly 23 `(P,M)` tasks → 2601*23) |

**Verdict (item 5): PASS** — the eR16 union artifact is internally consistent and
uniformly INFEASIBLE, matching every number in Codex's verifier output
(`expected=59823 rows_read=63867 unique_infeasible=59823 missing=0 noninf_keys=0
duplicate_inf_rows=4044 malformed=0`).

**NOT yet audited (item 1):** that `2601` masks × `23 (P,M)` is the COMPLETE eR16
subproblem set (depends on Codex's `6195` rooting/branching being exhaustive), and
that the per-task INFEASIBLE verdicts are solver-correct. These stay open pending
Codex's global Step-1 audit. eR16 is also only ONE frontier of `6195`; the other
edge windows (`99<=e<=108`, `109<=e<=139`, `e>=140`) are not covered by this file.

## 2026-06-20 — eR15 + q13_t3_r8_a5b7 profile — item-5 PASS

Independent Python re-count (flexible schema; eR15 uses lowercase `p` column):
| artifact | rows | unique key | dup | status | verdict |
|---|---|---|---|---|---|
| `state_count_6195_er15_defect24.tsv` | 23446 | 23446 `(mask,p,M)` | 0 | `{INFEASIBLE:23446}` | **PASS** (matches Codex "23446, all INFEASIBLE") |
| `q13_t3_r8_a5b7_profile_cpsat_0_256.tsv` | 257 | 257 `(profile_idx,cnt)` | 0 | `{INFEASIBLE:257}` | **PASS** (matches Codex "257/257 INFEASIBLE") |

Same scope caveat as eR16: item-5 consistency only. Completeness (item 1) and
solver-correctness remain pending Codex's global audit. Running item-5 tally of
independently-confirmed `6195`/q13 components: eR16 (59823), eR15 (23446), eR14
(135, per Codex—artifact not separately re-counted here), q13_t3_r8_a5b7 (257).

## 2026-06-20 — COMPREHENSIVE sweep of all 44 `state_count_*.tsv` (reusable verifier)

Tool: `experiments/audit_h1_statecount.py --all` (independent, reusable). Result:
**34/44 PASS item-5; the 10 "red flags" are ALL intermediate partials, not the H1
certificate:**
- the FINAL/trusted `6195` artifacts (`er16_clean_infeasible_union`,
  `er16_chunk{A..P}`, `er15_defect24`, `er14_open9_defect24`, the `*_clean`
  versions, `er16_defect24` 26275, etc.) are **uniformly INFEASIBLE**;
- every UNKNOWN/NO_STATUS appears ONLY in a superseded intermediate run that has a
  completed sibling — `*_30s`/`*_projcuts_*` → `*_unknown_*_300s`/`*_unknown6_300s`;
  `er14_open9_60s` → `er14_open9_defect24`; `remaining3/5_*` → `*_clean`; `chunkD`
  → Codex-abandoned, replaced by `chunkD2` and excluded from the union.

**★ KEY SAFETY FACT (independently checked): ZERO `FEASIBLE`/`SAT` in ANY
`state_count_*.tsv`.** A `FEASIBLE` there would be a `β>=37` witness = H1 FALSE.
None exists across all 44 files. Strong item-5 support that the `6195` enumeration
found no counterexample.

## 2026-06-20 (later) — H1 MEDIUM WINDOW (112≤e≤143) early signal — IN PROGRESS

Codex is actively computing the medium window via `k2_idx14_q8D_a7b11_p22..p34`
exact state-count bands (its remaining H1 gap). Step-2 scan of the 30 new
`k2_idx14_q8D_*_results.tsv` (mask/p/M/status format): **656 INFEASIBLE, 52 UNKNOWN,
ZERO FEASIBLE/SAT** (708 rows). **No `β>=37` witness** in any closed row — good signal
the medium window closes cleanly. NOT a certificate yet: 52 UNKNOWN are still being
re-run by Codex (its `_hard_` files). When the UNKNOWN resolve to INFEASIBLE the medium
window closes; Step-2 will then run the item-5 union audit + full NEEDED_FROM_STEP1
checklist. (Reminder: the H1 certificate is sound ONLY when these bands have zero
UNKNOWN and the task universe is complete — item-1 completeness still pending.)

## 2026-06-20T13:27 — a8b10 progress: p26 closed, p27 running, a9b9 (idx16) prepped — SAFE
Codex closed a8b10 p26 (PROOF_STATE V419, union 32/32 INFEASIBLE) and is on p27 (22
INFEASIBLE/9 UNKNOWN, hard-tail running); generated `k2_idx16_q8D_a9b9_state_tasks.tsv`
(next q8 side prepped). idx15 cumulative: 247 INFEASIBLE/116 UNKNOWN/**0 FEASIBLE-or-SAT**
(UNKNOWN confined to in-progress p27). a8b10 side (p20–27...) not yet fully closed; q8 has
further sides (a9b9) + the valid q13 T2 frontier still open. H1 IN PROGRESS, safe; no
item-5 milestone to audit until a full side/window closes.

## 2026-06-20T12:10 — q8 all-D `(8,10)` side (idx15) progress spot-check — SAFE, IN PROGRESS
Codex closed `a7b11` (idx14) fully and is now grinding the `a8b10` (idx15) side band by
band (PROGRESS_CODEX: p20–24 closed as PROOF_STATE V416/V417 via first+hard+hard2 reruns;
p25 hard-tail running). Step-2 clean status-token scan over ALL `search23/k2_idx15_q8D_*.tsv`:
**189 INFEASIBLE, 94 UNKNOWN, ZERO FEASIBLE/SAT/OPTIMAL.** No `β>=37` witness; closed bands
p20–24 uniformly INFEASIBLE (matches Codex union audits `closed=32/32 missing=0`); the 94
UNKNOWN sit in the still-running bands (p25+) being hard-tailed. Safe signal, NOT a
certificate (item-1 completeness + zero-UNKNOWN still pending). The medium window now needs
the rest of the q8 all-D sides + the valid q13 T2 frontier; H1 remains IN PROGRESS.

## 2026-06-20 — audit of PROOF_STATE.md foundational lemmas V1–V9

Read `problems/23/PROOF_STATE.md` lines 1–170 (Codex-owned, read-only).
- **V1** `β(G) <= β(G−v)+⌊d(v)/2⌋` — SOUND (standard; place v on the better side).
- **V4** `β <= e/2` (so `β>=T ⟹ e>=2T`) — SOUND; this is EXACTLY Step-2's L0
  (`MAXCUT_BOUNDS.md`). Independent cross-validation. ✓
- **V2** McKay: six 23-vtx `β=20` graphs, edge counts 100–105 — sound relative to
  the McKay `a(23)=20` catalogue completeness (a cited computational fact).
- **V7/V8/V9** honestly establish that PURE deletion arithmetic (5-delete to a(25),
  7-delete to a(23)) CANNOT close a(30) — escape profiles always remain. Hence the
  exact rooted enumeration (state_count certs) is the real proof. Consistent with
  the in-progress heavy enumeration; no overclaim by Codex here.
- **★ V5 — additional BCL dependency found:** branches `r=0,1,2,3` are killed via
  `β(G−v) <= ⌊29²/23.5⌋ = 35` (BCL GLOBAL at n=29) contradicting `β(G−v) >= 36`.
  This is the asymptotic BCL bound at a FINITE n=29 — a SEPARATE finite-n gap from
  the e-window one. Step-2's L0 only gives `β(29-vtx) <= ⌊e/2⌋ <= 105`, far from 35,
  so it does NOT discharge r≤3. **Flagged to Codex (NEEDED_FROM_STEP1):** does the
  exact enumeration cover r=0..3 directly, or is r≤3 still resting on BCL-global-at-29?
  (V5 also uses BCL-high for `e<=139`; same known gap.)

## 2026-06-20 — ★ BCL gap RESOLVED for density tails via uniform blow-up (audit: SOUND)

Codex (CODEX_STATUS) resolved the BCL-finiteness gap I flagged, for the density TAILS,
by a uniform blow-up transfer. **Step-2 independent audit — the argument is RIGOROUS:**
- A 30-vtx triangle-free `G` with `β(G)>=37`: the uniform blow-up `G[t]` (each vertex →
  independent set of size t) is triangle-free on `30t` vertices, and `β(G[t])=t²·β(G)`
  EXACTLY (MaxCut is multilinear in the per-class split, so `MaxCut(G[t])=t²MaxCut(G)`,
  same argument as BU1; `e(G[t])=t²e(G)`). So `β(G[t])=37t²`.
- `density(G[t]) = e(G[t])/C(30t,2) → e(G)/450` (from ABOVE). So `e(G)<=111 ⟹` for large
  `t`, density `< 0.2486` (BCL LOW range); `e(G)>=144 ⟹` density `> 0.3197` (BCL HIGH).
  Either way BCL (asymptotic, valid as `t→∞`) gives `β(G[t]) <= (30t)²/25 = 36t²`,
  contradicting `37t²`. Hence `β(G)<=36`.
- **Verdict: SOUND** (modulo citing BCL Thm 1.3's two density bounds, both `n²/25`). This
  converts BCL's ASYMPTOTIC tail bounds into FINITE `n=30` results — exactly the gap
  Step-2 flagged. Closes `e<=111` and `e>=144`.
- **Remaining H1 gap: the medium window `112<=e<=143`** (BCL's tails don't reach it).
  The direct rooted `109<=e<=139` campaign is `149/149 INCONCLUSIVE` (NOT a certificate);
  the valid `q13,k=3,t=2,r0=8` frontier still has ~500k–576k uncertified prefilter rows
  per `(na,nb)`. So H1 is STILL IN PROGRESS — only the medium window remains.
- **TRANSFERS TO a(25)** (n=5 base): same blow-up argument with `density(G[t])→2e(G)/625`
  closes `e<=77` (low) and `e>=100` (high) for a 25-vtx `β>=26` counterexample; remaining
  medium window `78<=e<=99`. So the a(25) BCL-finiteness gap is likewise resolved for the
  tails. (See ledger DEP-a25 update.)

### Open question raised to Codex (different search context)
A grep for `SAT`/`FEASIBLE` across ALL `search23/*.tsv` found three NON-state_count
files in the `p14_z8_*` line carrying `SAT`:
`p14_z8_0_23_zdeg1700_row2_89_row3_smoke200.tsv` (`SAT:14, INFEASIBLE:173,
UNKNOWN:13`), `..._smoke_survivors_full.tsv`, `p14_z8_touch2_projection_filter.tsv`
(`SAT:1`). These look like a FILTER/screening pass (`status OPTIMAL`→SAT = a partial
config "survives, keep branching", which then resolves INFEASIBLE deeper, e.g. idx0
SAT then idx4 INFEASIBLE). They are NOT in the `6195` H1 certificate. **Flagged to
Codex (HANDOFF) to confirm these SAT markers are intermediate filter-survivors that
resolve to INFEASIBLE downstream, NOT `β>=37` witnesses.**
