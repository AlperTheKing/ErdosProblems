# Step-1 publication plan — Erdős #23 (computer-assisted)

> ✅ **DECISION LOCKED 2026-06-25: publish the SOUND per-root-MaxCut envelope result, N≤55.**
> The order-9 fixed-cut DEFICIT cert was proven unsound (G4 + Step-2; balanced δ'=7.04e-3). The
> sound replacement is the **order-9 U₇ per-root-MaxCut envelope** (k=7 roots, 107-type complete
> cover): `d_mono(W) ≤ U₇(W) = 2/25 + Σ_σ min_c g_{σ,c}(W)` [k-uniform genuine-coloring argument,
> validated], certified `U₇ ≤ 2/25 + δ` on the band with `η=δ≈6.06e-4` (Step-2 converging to maxit
> 120; exact rational pending). Integrality ⟹ a(5n)=n² for n with δ<2/(25n²): **n≤11 ⟹ N≤55**
> (margin ~8%; if exact δ exceeds 6.61e-4 it's n≤10 / N≤50). N≤180/all-n is NOT reachable by flags
> (order-9 AND order-10 plateau ≫ 6.17e-5) — it needs the cut-geometry Connected-B Gamma Lemma
> (self-tight research barrier, ~15-20%, OPEN). Full conjecture stays the open frontier.
>
> **NEW GATE SEQUENCE (on the envelope cert):**
> - [ ] G0. Receive `envelope_k7_cert.pkl` + `regen_verify_u7.py` from Step-2 (~30 min) + the EXACT rational δ + final n.
> - [ ] G1env. **Re-audit the U₇ cert** (G2-style multi-agent EXACT audit): cut rows exact-rational
>        (g = integer-count/(n)_k), per-type envelope u_σ ≤ min_c g_{σ,c}·x, moment-PSD = G1 Gram-cert,
>        η=δ exact, Σx=1. PLUS confirm `d_mono ≤ U₇` (k=7) validation (Step-2 validated U₈/8-anchor;
>        the k=7 version holds by the same argument — get the U₇-specific n=6,7 exact + zoo).
> - [ ] G2env. Rewrite §3 (envelope, drafted: SECTION3_envelope_draft.tex) + §6 (verification) + abstract
>        + §5 closure (rescope n≤11/N≤55) + §7 obstruction (flag cap + cut-geometry frontier). §2 blow-up/
>        integrality, BCL tails, G1 moment Gram-cert all CARRY OVER (with the GPT-review fixes already applied).
> - [ ] G3env. Fresh GPT-Pro adversarial read on the rewritten proof.
> - [ ] G4env. Compile + finalize anc/ (envelope scripts + cert + SHA256SUMS), then USER submits arXiv + OEIS.
> Upgrade: if Step-2's order-10 "conditional-profile Gram PSD" closes (EXACT-verified, ~15-25%), swap to N≤180/all-n.
> See memory [[erdos23-deficit-fix-and-u8-envelope]], [[erdos23-step1-a30-state]].

## (historical, pre-reversal) Step-1 publication plan — a(5n)=n² for n≤36 (computer-assisted)

Decision (user, 2026-06-24): publish the computer-assisted Step-1 result, PR-less.
arXiv note + OEIS contribution, linked. NO formal-conjectures PR (proof not in Lean).
Full #23 PR deferred until/unless a full proof exists.

## Artifacts
- arXiv note: `problems/23/writeup/arxiv/erdos23_step1.tex` (DRAFT — modeled on the 944 note).
- Ancillary files (to package into `arxiv/anc/`): `bridge/flagsdp/dual_cert_n9.pkl`,
  `certify_dual.py`, `flag_exact.py`, `brute_dmono.py`, + a README + SHA256SUMS.

## Result restated (sanity-checked against OEIS A389646)
a(5n)=n² for 1≤n≤36 (N=5,10,...,180). A389646 known terms (exhaustive, n≤23):
  n  : 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
  a  : 0 0 0 0 1 1 1 2 2  4  4  5  6  7  9  9 10 12 13 16 16 17 20
Multiples of 5 in known range: a(5)=1, a(10)=4, a(15)=9, a(20)=16 = 1²,2²,3²,4² — MATCH.
We ADD: a(25)=25, a(30)=36, a(35)=49, ..., a(180)=1296.

## OEIS contribution (A389646) — COMMENT + reference (NOT a b-file extension)
A389646 is defined for ALL n; our result determines only the MULTIPLES OF 5 (n≤36),
so we cannot extend the main data line term-by-term (a(24),a(26),... undetermined).
Submit instead a COMMENT + a reference. Draft comment text:

  "It is now proven that a(5k) = k^2 for all 1 <= k <= 36, i.e. Erdős's conjecture
   a(n) <= n^2/25 holds with equality on the multiples of five up to n=180. In
   particular a(25)=25, a(30)=36, ..., a(180)=1296. The proof is computer-assisted:
   an order-9 flag-algebra certificate bounds the monochromatic-pair density by
   2/25 + 6.07e-5 in the medium edge-density band, and a blow-up identity together
   with integrality of the bipartization number closes the small gap for n <= 36;
   the two density tails use Balogh–Clemen–Lidický. See [arXiv link]. — [author], 2026"

  Reference line (%H): "[author], <a href='[arXiv url]'>The Erdős n^2/25 max-cut
   conjecture for the first 36 multiples of five</a>, arXiv:[id] (2026)."

NOTE: OEIS submission goes through oeis.org (login + editorial review). USER submits.

## Venues (USER decision 2026-06-24: arXiv + OEIS only; Tao's repo + wiki DROPPED)
1. arXiv — math.CO. Submit erdos23_step1.tex + anc/. (compile first; see gates.) THE ANCHOR.
2. OEIS A389646 — the comment + reference above, after the arXiv id exists. "OEIS entry is
   enough" (user). The sequence link on Tao's DB already exists; nothing to do there.
   (OPTIONAL, user's call, NOT required: a short SeqFan post or an erdosproblems.com/#23
    math-context comment linking the arXiv note. User did not ask for these.)
3. teorth/erdosproblems (Tao's DB) + its AI-contributions wiki — DROPPED (user, 2026-06-24:
   "#23 is already OEIS-linked there, so no need; the OEIS entry is enough; forget the wiki").
   FYI for context: problems.yaml #23 already has oeis:["A389646"], status:"falsifiable",
   formalized:"yes" — and being a partial result it would not change any of those anyway.

## PRE-SUBMISSION GATES (correctness, must pass before ANY external post)
[x] G1. flag-PSD — CLOSED 2026-06-25 by Step-2 (exact, not numerical). EXACT rational Gram
        certificate M^σ(W)=Σ_c w_c q_c q_cᵀ (w_c≥0, manifestly PSD) for all 4 σ-types (sizes
        7,35,34,57); 20/20 band graphons sym + independent-double-sum diff 0 + ⟨Q_σ,M⟩≥0 exact.
        SOUNDNESS (subtle): moment term = ORDER-9 AVERAGE m_avg=Σ_σ ρ_σ⟨Q_σ,M^σ⟩≥0, ρ_σ=
        C(n-k-s,s)/C(n-k,s)=5/126,1/70,4/35,4/35; NOT per-flag m_j≥0 (negative); routed through
        BLOW-UP graphon W_G (finite distinct-subset densities carry O(1/n) defect, e.g. C7[2]
        -4.4e-5; graphon C7 +2.19e-5, C5 +5.03e-5). REQUIRED §6 WRITEUP FIX (4 pts) APPLIED to
        the draft 2026-06-25 (§3 + §6(3) rewrite + abstract + checked-vs-cited). Scripts in anc/:
        g1_exact_psd.py, g1_graphon_density.py, g1_soundness_check.py. ALL CORRECTNESS GATES NOW
        CLOSED (G1+G2). Remaining = mechanical: G3 should-fix polish, G4 GPT-Pro read, compile,
        author, anc finalize.
[x] G2. regenerator + cert audit — DONE 2026-06-24, workflow wf_e5bbaee5-419, 13 agents.
        VERDICT: G2 PASS-WITH-RESIDUALS. All 6 dims PASS + independently CONFIRMED_PASS:
        D1 gr_exact two independent reimpls match at EXACT-0 discrepancy, soundness 0 violations
        (min gap exactly 0, 4366 states); D2 P^σ+quadform match first-principles at diff 0, all
        114 γ≥0; D3 dual-feasibility byte-identical, sum(lam)=1 exact, 0 neg multipliers, μ=ν=0;
        D4 soundness chain 0 violations on 1897 flags; D5 brute n≤12 in-band max 0.0556 (margin
        ≥0.024); D6 first-failing-n exactly 37, δ<1/450, band edges gap-free. Report:
        bridge/flagsdp/G2_AUDIT_REPORT.md. Cert byte-identical to backup (sha256 verified).
        Sole residual handed to G1.
[~] G3. compile the .tex (no local LaTeX here — user/Overleaf), proofread, author DONE.
        INTERNAL review DONE (wf_5680fc7e-b37, 5 lenses): math spine SOUND, no incorrect step.
        3 MUST-FIX APPLIED (A1 superseded by G1 EXACT closure — no longer pending; A2 flag-count;
        A3 anc reconciled). SHOULD-FIX B1-B7 APPLIED 2026-06-25: B1 (W_G step-graphon lemma,
        d_mono(W_G)=2β/N² exact, no O(1/t) residual — the finite/graphon junction), B3 (twin-
        interchangeability in Lemma 2.1), B4 (abstract: BCL tails "for large N"), B5 (order 12),
        B6 (peeling derivation spelled + citation reframed), B7 (author TODO removed). B2 covered
        by B1. Remaining nice-to-have C1/C3/C4/C5/C6/C9 = minor, fold into the G4 GPT-Pro pass.
        Compile still needs user/Overleaf. Punch-list: problems/23/writeup/DRAFT_REVIEW_2026-06-24.md.
[ ] G4. GPT Pro adversarial read of the whole note (per the false-closure history;
        3 prior false closures — the public claim must survive a skeptical expert read).
        Do AFTER G1 closes + the G3 punch-list is applied (review the FINAL draft).
[~] G5. package anc/ — STARTED: problems/23/writeup/arxiv/anc/ has dual_cert_n9.pkl +
        brute_dmono.py + flag_engine.py (standalone independent verifier) + README.md.
        DEFERRED to submission: the 278MB cache decision (cache-rebuild script or cache-free
        re-verifier), the full 7-module set for the exact pipeline, Step-2's PSD-check script,
        and SHA256SUMS. Mirror the 944 anc layout at the end.

## Honest scope line for all venues
"a(5n)=n² for n≤36 (N≤180), computer-assisted; the full conjecture (all n) reduces to
a single robust per-step peeling estimate (open)." Do not overstate as resolving #23.
