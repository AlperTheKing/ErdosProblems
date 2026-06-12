# GOAL_LOOP.md — kalıcı görev tanımı (her compaction/yeni oturumda ÖNCE burayı oku, sonra devam et)

> Kullanıcı direktifi (2026-06-11): "goal ve loop u GOAL_LOOP.md de kaydet her compaction dan
> sonra ya da yeni session da önce buraya bak burdan goal ve loop u al tekrar ve devam et."
> Resume akışı: (1) bu dosyayı oku; (2) PROGRESS.md'nin son satırlarından + memory'deki
> erdos944-shore-machine-state'ten kaldığın yeri al; (3) GOAL'ü ve LOOP'u aynen sürdür.

---

## GOAL (verbatim, /goal 2026-06-11 r2 — CLAIMS.md koordinasyonu eklendi)

GOAL: New Mathematics on Open Erdős Problems (multi-problem, fail-fast, no time limit)

Mission: Run an autonomous research program over OPEN problems from erdosproblems.com until you produce ONE genuinely NEW mathematical result — a proof, disproof, strictly better bound, or resolved special case verifiably ABSENT from the published literature. There is NO wall-clock or cycle budget: days of sustained work on one problem are acceptable while the line of attack is alive. The instant a track is judged dead (see Dead-end protocol), abandon and reselect immediately.

Roles:
- Claude (orchestrator): problem selection, prior-art research, decomposition, computation, verification (small cases, numerics, counterexample search, Lean 4 for key lemmas), adversarial refereeing, logs, PR. Single source of truth.
- GPT-5.5 Pro (prover, via browser tool): creative proof content. Consult at the smallest stuck point with a self-contained sub-goal; audit every answer line by line; never accept unverified output.

Coordination & compute: a Codex agent runs the same program in parallel on this machine. Shared append-only registry E:\Projects\ErdosProblems\CLAIMS.md: append "[time] CLAUDE CLAIM #n" before attacking a problem, "[time] CLAUDE RELEASE #n DEAD|SOLVED: <one-line reason>" on exit. Skip problems with an active CODEX claim. A problem released DEAD by either agent is dead for both unless a gate-passing new idea is named. CPU: use at most 50% (32 of 64 cores); cap all parallel work at 32 workers. GPU (RTX 5090) is shared: GPU CLAIM / GPU RELEASE lines in CLAIMS.md around any GPU job; never start one while CODEX holds an unreleased GPU claim.

Novelty gate (BEFORE any proof effort on a candidate): search the erdosproblems.com page + arXiv + Google Scholar + zbMATH for (a) the result itself, (b) general theorems implying it, (c) recent preprints. Found -> candidate is DEAD for this goal: log one line with citation, release the claim, move on. Re-run the gate before any PR.

Known statuses (do not re-evaluate): #203 dead; #835 parked; #617 counterevidence logged; #488 open-hard; #993 no reachable new mathematics (Kadrawi et al. arXiv:2305.01784; Li arXiv:2603.03025) — skip unless a gate-passing new idea exists. Also honor all DEAD releases in CLAIMS.md.

Dead-end protocol (replaces all budgets): a track is ALIVE only while it keeps producing verifiable new facts (a proved lemma, a falsified claim, a numeric finding, a sharpened obstruction). After 3 consecutive cycles with no verifiable new fact, hold a MANDATORY joint review: write an honest obstruction brief (what was tried, what blocks it) and send it to GPT-5.5 Pro. Joint verdict DEAD -> abandon immediately, release the claim, log the obstruction, reselect. Verdict ALIVE -> whoever argues for continuing must name ONE concrete next experiment or lemma; execute it; re-evaluate. Never linger to look busy; an obstruction brief is legitimate output.

Forbidden (zero value — never do): formalizing known results in Lean (formalization is NOT a contribution); re-deriving or re-proving anything published; presenting sketches as results; fake progress or "still working" narration; self-congratulation; native_decide in any Lean proof.

Rigor: a claim is "established" only via (a) a gap-free logged proof, (b) a cited literature result, or (c) a verified computation. Tag every component: conjecture / heuristic / sketch / rigorous-informal / Lean-verified.

Success (the ONLY stopping condition): a complete, verified result passing the novelty gate, written up with a prior-art comparison, submitted as a PR to github.com/teorth/erdosproblems (data/problems.yaml per CONTRIBUTING.md; Lean-verified results may also go to google-deepmind/formal-conjectures). Until then, never terminate.

Reporting: follow the Progress Reporting Protocol in CLAUDE.md.

---

## LOOP (verbatim, /loop 2026-06-11)

LOOP (repeat until the GOAL success condition is met; never idle, never simulate activity):

1. SELECT: From open erdosproblems.com problems (excluding known statuses in GOAL), pick the most tractable candidate with a concrete attack surface. One line: problem #, why tractable.
2. GATE: Run the GOAL novelty gate. Fail -> log "DEAD: <citation>", go to 1.
3. PLAN: Decompose into a minimal lemma tree; identify the single highest-leverage open lemma (the frontier).
4. ATTACK: Work the frontier lemma. Computation FIRST — counterexample search and small-case verification (<=32 CPU workers) before proof effort. At the smallest stuck point, send GPT-5.5 Pro a self-contained sub-goal; audit its proof line by line before accepting anything.
5. VERIFY: Every accepted step gets a referee pass + a numeric/computational check where applicable + Lean 4 for key lemmas when feasible (no native_decide).
6. CHECK: Verifiable new fact this cycle? Yes -> stall=0, go to 7. No -> stall+1. At stall=3 -> run the GOAL Dead-end protocol jointly with GPT-5.5 Pro: verdict DEAD -> log obstruction, go to 1; verdict ALIVE -> execute the named next experiment, continue at 4. There is no other exit and no time limit.
7. DECIDE: Result complete? Re-run the novelty gate. Still novel -> write up + prior-art comparison -> PR -> STOP. Otherwise -> go to 4.

Every step transition emits the before/after protocol lines per CLAUDE.md.

---

## Operasyonel notlar (resume için kritik)

- AKTİF TRACK: #944 (Dirac k=4, 6-regüler hat) — durum: memory `erdos944-shore-machine-state`
  + `problems/944/PROOF_STATE.md` + `RESEARCH_LOG.md` sonu + PROGRESS.md.
- Bu kutuda Monitor araçları KULLANILMAZ (harici silent killer ~5-24 dk'da öldürüyor);
  izleme = ScheduleWakeup tick'leri. Compute = native clang++ (asla WSL), worker tavanı 32.
- geng çıktısı her sınıfta `>Z` terminatörüyle doğrulanmalı (sessiz kesinti tuzağı).
- teorth/erdosproblems comments-field'a partial-progress PR'ı AÇMA (Tao kapattı, 2026-06-11);
  kanallar: erdosproblems.com sayfa yorumu / formal-conjectures / arXiv not.
- Loop'u sürdürme mekaniği: her turda çalış + turu `ScheduleWakeup(prompt="/loop <LOOP metni>")`
  ile bitir; /goal Stop hook'u başarı koşulu sağlanana dek durmayı engeller.
- KANAL KARARI (2026-06-11, kullanıcı): teorth comments-PR YOK ("Tao oraya yorum
  istemiyor"); sonuçların gideceği kanallar = arXiv notu (yazar: Alper Ferudun) +
  erdosproblems.com problem sayfası yorumu + (Lean) formal-conjectures. GOAL'deki
  "PR to teorth" başarı adımı bu kanal setiyle İKAME edildi (kullanıcı sözlü onayı).
