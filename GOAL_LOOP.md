# GOAL_LOOP.md — kalıcı görev tanımı (her compaction/yeni oturumda ÖNCE burayı oku, sonra devam et)

> Kullanıcı direktifi (2026-06-11): "goal ve loop u GOAL_LOOP.md de kaydet her compaction dan
> sonra ya da yeni session da önce buraya bak burdan goal ve loop u al tekrar ve devam et."
> Resume akışı: (1) bu dosyayı oku; (2) PROGRESS.md'nin son satırlarından + memory'deki
> erdos944-shore-machine-state'ten kaldığın yeri al; (3) GOAL'ü ve LOOP'u aynen sürdür.

---

## ⭐ OVERRIDE (2026-06-17, kullanıcı direktifi: "you switch to codex rule too. all-or-nothing.")

Bu blok aşağıdaki GOAL'ün ÇELİŞEN maddelerini (Mission'daki "strictly better bound / resolved
special case" ve Success'teki çift-kanal) GEÇERSİZ kılar. Artık `GOAL_CODEX.md` ile aynı
submission politikası geçerli:

- ALL-OR-NOTHING: Hiçbir kısmî şey ASLA yayınlanmaz — statement-only PR yok, lemma çekirdeği yok,
  witness yok, certificate yok, "yeni diye" özel durum yok. Yayınlanan TEK şey: resmî
  formal-conjectures ifadesinin (ya da olumsuzlamasının) TAM, `sorry`/`admit`/`native_decide`/
  gerekçesiz `axiom` içermeyen, `#print axioms` = {propext, Classical.choice, Quot.sound} olan,
  pinned Mathlib altında derlenen Lean 4 kanıtı. Hipotez zayıflatması / sonucu trivialize eden
  güçlendirme sayılmaz.
- TEK BAŞARI KANALI: google-deepmind/formal-conjectures'a TEK PR. Bu turda arXiv notu ve
  erdosproblems.com yorumu BAŞARI KOŞULUNUN PARÇASI DEĞİL (commit = yalnız user; Anthropic
  co-author trailer YOK — Google CLA'yı bozar).
- KORUNAN: yeni matematik şartı + novelty gate + dead-end protokolü + native_decide yasağı aynen.
- Finite/computational kazanım (UNSAT-over-templates vb.) tek başına formalize edilebilir DEĞİL;
  ya yapısal/insan-okunur Lean kanıtına ya da kernel-`decide` boyutuna damıtılmadıkça submission
  gate'ini geçmez.
- Kısmî iş yerelde kalır (`problems/<n>/`, `search<n>/`); o PR var olana dek hiçbir yerde
  hiçbir şey yayınlanmaz. (Geçmiş PR #4192 / #4237 banked-partial mantığı artık geçerli DEĞİL.)

---

## GOAL (verbatim, 2026-06-12 r3 — başarı kanalı değişti: teorth PR çıkarıldı,
## yerine formal-conjectures PR + arXiv yayını kondu; kullanıcı direktifi
## "goal deki teorth pr kısmını değiştir ... formal-conjectures a pr ve arxiv da
## yayın olarak değiştir")

GOAL: New Mathematics on Open Erdős Problems (multi-problem, fail-fast, no time limit)

Mission: Run an autonomous research program over OPEN problems from erdosproblems.com until you produce ONE genuinely NEW mathematical result — a proof, disproof, strictly better bound, or resolved special case verifiably ABSENT from the published literature. [2026-06-17 OVERRIDE: only a FULL proof or FULL disproof of the official conjecture can SHIP; a better bound / special case is valid local research but does NOT meet the all-or-nothing submission gate.] There is NO wall-clock or cycle budget: days of sustained work on one problem are acceptable while the line of attack is alive. The instant a track is judged dead (see Dead-end protocol), abandon and reselect immediately.

Roles:
- Claude (orchestrator): problem selection, prior-art research, decomposition, computation, verification (small cases, numerics, counterexample search, Lean 4 for key lemmas), adversarial refereeing, logs, PR. Single source of truth.
- GPT-5.5 Pro (prover, via browser tool): creative proof content. Consult at the smallest stuck point with a self-contained sub-goal; audit every answer line by line; never accept unverified output.

Coordination & compute: a Codex agent runs the same program in parallel on this machine. Shared append-only registry E:\Projects\ErdosProblems\CLAIMS.md: append "[time] CLAUDE CLAIM #n" before attacking a problem, "[time] CLAUDE RELEASE #n DEAD|SOLVED: <one-line reason>" on exit. Skip problems with an active CODEX claim. A problem released DEAD by either agent is dead for both unless a gate-passing new idea is named. CPU: use at most 50% (32 of 64 cores); cap all parallel work at 32 workers. GPU (RTX 5090) is shared: GPU CLAIM / GPU RELEASE lines in CLAIMS.md around any GPU job; never start one while CODEX holds an unreleased GPU claim.

Novelty gate (BEFORE any proof effort on a candidate): search the erdosproblems.com page + arXiv + Google Scholar + zbMATH for (a) the result itself, (b) general theorems implying it, (c) recent preprints. Found -> candidate is DEAD for this goal: log one line with citation, release the claim, move on. Re-run the gate before any PR.

Known statuses (do not re-evaluate): #203 dead; #835 parked; #617 counterevidence logged; #488 open-hard; #993 no reachable new mathematics (Kadrawi et al. arXiv:2305.01784; Li arXiv:2603.03025) — skip unless a gate-passing new idea exists. Also honor all DEAD releases in CLAIMS.md.

Dead-end protocol (replaces all budgets): a track is ALIVE only while it keeps producing verifiable new facts (a proved lemma, a falsified claim, a numeric finding, a sharpened obstruction). After 3 consecutive cycles with no verifiable new fact, hold a MANDATORY joint review: write an honest obstruction brief (what was tried, what blocks it) and send it to GPT-5.5 Pro. Joint verdict DEAD -> abandon immediately, release the claim, log the obstruction, reselect. Verdict ALIVE -> whoever argues for continuing must name ONE concrete next experiment or lemma; execute it; re-evaluate. Never linger to look busy; an obstruction brief is legitimate output.

Forbidden (zero value — never do): formalizing known results in Lean (formalization is NOT a contribution); re-deriving or re-proving anything published; presenting sketches as results; fake progress or "still working" narration; self-congratulation; native_decide in any Lean proof.

Rigor: a claim is "established" only via (a) a gap-free logged proof, (b) a cited literature result, or (c) a verified computation. Tag every component: conjecture / heuristic / sketch / rigorous-informal / Lean-verified.

Success (the ONLY stopping condition) [SUPERSEDED by the 2026-06-17 OVERRIDE block above — all-or-nothing, single channel = ONE formal-conjectures PR of a complete sorry-free proof; the BOTH-channels / arXiv / partial-core wording below is NO LONGER the success condition]: a complete, verified result passing the novelty gate, written up with a prior-art comparison, and published via BOTH (a) a PR to github.com/google-deepmind/formal-conjectures containing the Lean-verified statements/cores, and (b) an arXiv note (author: Alper Ferudun) — plus, optionally, a comment on the erdosproblems.com problem page. NO PRs to github.com/teorth/erdosproblems (maintainer declined partial-progress comments there, 2026-06-11). Until then, never terminate.

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
  2026-06-13 DURUM: Teorem A n<=15; **TEOREM C KANITLANDI** (6-regüler (4,1)-grafta
  hiçbir 6-kesit kıyısı iki-parçalı değil) — not v4'te (erdos944_note.tex, 8s) +
  Lean çekirdeği `cut_row_forcing` PR #4237'de (commit 12c702b, [propext], derlendi).
  PG(2,5) all-unfrozen ⟹ frozen-kernel genel rotası öldü. AÇIK CEPHE: 3+3 diagonal
  kıyıların sonlu-durum sistemi (PROOF_STATE 2026-06-13 ~05:05 S-A/B1/B2/K) + spread
  Kempe-rijitlik. GPT thread c/6a29bd3c (round 6'ya kadar denetlendi).
- Bu kutuda Monitor araçları KULLANILMAZ (harici silent killer ~5-24 dk'da öldürüyor);
  izleme = ScheduleWakeup tick'leri. Compute = native clang++ (asla WSL).
- CPU tavanı (2026-06-12 kullanıcı: "cpu kullanımı düşük — %50'sini kullanıyor musun?"):
  %50 pay = 64 mantıksal thread (128'in yarısı); runner PAR=55 (2026-06-11 arbitrasyon
  değeri). GOAL metnindeki "32 worker" ifadesi eski yorum — kullanıcı netleştirmesi geçerli.
- geng çıktısı her sınıfta `>Z` terminatörüyle doğrulanmalı (sessiz kesinti tuzağı).
- teorth/erdosproblems comments-field'a partial-progress PR'ı AÇMA (Tao kapattı, 2026-06-11);
  kanallar: erdosproblems.com sayfa yorumu / formal-conjectures / arXiv not.
- Loop'u sürdürme mekaniği: her turda çalış + turu `ScheduleWakeup(prompt="/loop <LOOP metni>")`
  ile bitir; /goal Stop hook'u başarı koşulu sağlanana dek durmayı engeller.
- KANAL KARARI (2026-06-11, kullanıcı): teorth comments-PR YOK ("Tao oraya yorum
  istemiyor"); kanallar = arXiv notu (yazar: Alper Ferudun) + erdosproblems.com
  sayfa yorumu + (Lean) formal-conjectures. 2026-06-12 r3: bu karar GOAL'ün
  Success maddesine resmen işlendi (kullanıcı: "teorth pr kısmını ...
  formal-conjectures a pr ve arxiv da yayın olarak değiştir").
- AKTİF /goal METNİ: oturum hook'undaki metin hâlâ r2 olabilir; kullanıcıya r3
  metni verildi — /goal'e yapıştırınca hook da senkronlanır. Tek doğru kaynak
  her zaman bu dosyadaki r3.
