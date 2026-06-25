# Draft review — `erdos23_step1.tex` (arXiv math.CO, Erdős #23 Step-1)

**Review lead consolidation of 5 lens reviews, 2026-06-24.** Target file:
`problems/23/writeup/arxiv/erdos23_step1.tex`. Evidence cross-checked against
`bridge/flagsdp/G2_AUDIT_REPORT.md`, `problems/23/writeup/PUBLICATION_PLAN.md`,
and the ancillary directory `problems/23/writeup/arxiv/anc/`.

---

## OVERALL VERDICT

**(b) Needs the MUST-FIX list applied first.** The mathematical/arithmetic spine
is sound and reproduces exactly (δ, the n≤36/37 integrality cutoff, the band
fractions, the blow-up identity, the brute-force in-band maxima). There is **no
incorrect proof step**. But the draft repeatedly presents the one open soundness
gate (G1, exact graphon moment-PSD) as a completed "safeguard," which — given three
prior false closures, one a numerics-missed sign bug — is a material overclaim at
the single load-bearing step. Plus two factual/file-packaging errors that must be
fixed before submission. None require new mathematics; the must-fix items are
honesty wording + two number/file corrections. After they are applied (or G1 is
actually discharged exactly), the draft is submission-ready.

---

## (A) MUST-FIX — correctness, overclaim, wrong numbers/files

### A1. Moment-PSD (gate G1) presented as a completed "safeguard" when it is the SOLE OPEN gate
*(merged: Math#1, Claims#1, Honesty#1 + Honesty#2 + Honesty#3, Citation#5)*

- **Location.** §6 para (3), lines 326–328: *"the matrices $M^\sigma(W)$ were
  confirmed positive semidefinite on sampled band graphons, and an exact eigenvalue
  confirmation for each $\sigma$ in use is the final implementation safeguard."*
  Reiterated in the "What is checked vs. cited" para, lines 344–345: *"with the
  exact eigenvalue confirmation as the final safeguard."* Also propagates to the
  Abstract (lines 53–56, "verified in exact rational arithmetic") and §7 line 371
  ("proving the finite range **unconditionally** up to $N=180$").
- **Problem.** Both `G2_AUDIT_REPORT.md` (§1, §3 item 1, §4) and
  `PUBLICATION_PLAN.md` gate G1 (`[!]` "THE BINDING GATE (only residual)... In the
  Step-2 relay") state this exact check is **PENDING**, not done. Only Monte-Carlo
  evidence exists (worst min-eig −5.9e-17, worst atom +4.3e-7). The moment atoms are
  **negative per-flag** (down to −5.45e-3), so the entire bound's validity on
  graphons rests on this PSD statement. Phrasing a not-yet-run check as an existing
  "safeguard" is precisely the project's historical false-closure failure mode (the
  −7.2e-4 localizer sign bug caught only by an exact check).
- **Fix.** Do NOT call the exact eigenvalue check an existing safeguard. Either:
  - **(a)** run and report the passing exact rational PSD certificate over the band
    before submission, then cite its output; OR
  - **(b)** reword to state honestly that graphon moment-PSD holds **as a theorem by
    Razborov [Raz07]** (which covers it), that the implementation's $P^\sigma$ was
    matched to an independent enumeration at **exact-zero discrepancy**, and that the
    supporting numerics are **Monte-Carlo on sampled band graphons (worst min-eig
    −5.9e-17)** — with an exact per-$\sigma$ eigenvalue certificate **in progress /
    not yet discharged in exact arithmetic**.
  - Add a **third "pending" category** to the "What is checked vs. cited" paragraph
    so level (3) is not bucketed with the exact-arithmetic checks (1),(2),(4).
  - Reconcile the sentence *"No part of the argument uses native\_decide or
    floating-point thresholds in its decision step"* (line 346–347): it becomes
    false if PSD positivity ultimately rests on Monte-Carlo — either complete the
    exact check or explicitly exclude the pending PSD positivity from that claim.
  - Drop **"unconditionally"** in §7 line 371 unless G1 is closed; otherwise
    "...up to $N=180$ modulo the cited Razborov moment-PSD theorem."
  - In the Abstract, scope "verified in exact rational arithmetic" to dual
    feasibility + the value of δ (which ARE exact), and anchor the band bound to the
    cited Razborov PSD theorem, not to an unrun numerical check.

### A2. Wrong flag count qualifier: "1897 flags of order ≤9" should be "order 9"
*(merged: Claims#2; supported by Claims#3)*

- **Location.** §6 para (1), line 293: *"regenerating every atom on all $1897$ flags
  of order $\le 9$."*
- **Problem.** 1897 is the number of triangle-free graphs of order **exactly 9**;
  order ≤9 is 2480 (1+1+2+3+7+14+38+107+410+1897). The certificate's maximization
  domain is the 1897 order-9 states (confirmed in `G2_AUDIT_REPORT.md` D3: "1897
  order-9 flags"). The very next paragraph (line 342) correctly says "all $1897$
  order-$9$ flags," so this is an internal inconsistency.
- **Fix.** Change "all $1897$ flags of order $\le 9$" → "all $1897$ triangle-free
  flags of order $9$." Optionally add one clause distinguishing atom support
  (rooted flags on ≤9 vertices) from the evaluation domain (the 1897 order-9 flags).

### A3. Ancillary-files section names files that are NOT in `anc/`; README claim now stale
*(corrected from Exposition#3 — re-verified against disk)*

- **Location.** "Ancillary files" section, lines 376–381, names
  `dual_cert_n9.pkl`, `certify_dual.py`, `flag_exact.py`, `brute_dmono.py`, and a
  `README`.
- **Problem (re-checked on disk, supersedes Lens-5's "no README" claim).**
  `problems/23/writeup/arxiv/anc/` **does exist** and contains: `README.md`,
  `dual_cert_n9.pkl`, `brute_dmono.py`, and **`flag_engine.py`** — NOT
  `certify_dual.py` and NOT `flag_exact.py`. So the draft's file list does not match
  the packaged anc/ directory. The arXiv package must contain exactly the files the
  note lists (and vice-versa). PUBLICATION_PLAN G5 also flags SHA256SUMS + cache
  decision as still deferred.
- **Fix.** Reconcile the two. Either rename `flag_engine.py` references / add
  `certify_dual.py` + `flag_exact.py` to `anc/`, or update the draft's list to match
  what is actually shipped (`flag_engine.py` as the standalone verifier). Confirm the
  README in `anc/` states order=9, band [0.2486, 0.3197], and the exact rational δ
  (it currently exists — keep the sentence promising it), and add SHA256SUMS before
  packaging.

---

## (B) SHOULD-FIX — missing caveats, clarity, weak exposition

### B1. Exact identification $d_\mathrm{mono}(W_G)=2\beta(G)/N^2$ hand-waved at the finite-n/graphon junction
*(Math#2)*

- **Location.** §2 line 159 ("it equals the value of the limiting graphon $W_G$");
  §5 band proof line 270 ("$\dmono(W_G)=2\beta(G)/N^2$ by Lemma 2.1").
- **Problem.** Theorem 3.1 bounds $d_\mathrm{mono}(W)$ for a graphon; the proof needs
  this EXACTLY for $G$'s own step-graphon. This is the precise junction where prior
  false closures lived. Lemma 2.1 is about $\beta(G[t])$, not a graphon value.
- **Fix.** Add a short lemma in §2: $W_G$ = step-graphon of $G$ = step-graphon of
  every $G[t]$; $d_\mathrm{mono}(G[t])=2\beta(G)/N^2$ for all $t$ by Lemma 2.1; so the
  limit value is exactly $2\beta(G)/N^2$ (the $O(1/n)$ disjointness residual genuinely
  vanishes — constant sequence). Have §5 cite that lemma.

### B2. Disjointness-correction argument asserted, not connected to the t→∞ limit
*(Honesty#4; cf. G2 audit residual 2)*

- **Location.** §6 para (3), lines 320–324: *"$O(1/n)$ disjointness correction
  [Raz07]; this correction vanishes in the blow-up limit $t\to\infty$ ... so it does
  not affect the bound."*
- **Problem.** The bridge to the finite $G$ is in §2 but never connected here; a
  referee may ask why an $O(1/n)$ moment-matrix correction does not perturb the
  certified δ for the finite $G$.
- **Fix.** One-line cross-reference: the certified inequality is a graphon statement
  proved in the $t\to\infty$ limit (correction identically zero); $G$ enters only via
  $d_\mathrm{mono}(G)=d_\mathrm{mono}(W_G)$ (the B1 lemma), so no finite-n correction
  is applied to $G$.

### B3. Blow-up cut reduction omits the twin-interchangeability step
*(Math#3)*

- **Location.** §2 proof of Lemma 2.1, lines 143–153.
- **Problem.** "The cut value of $G[t]$ is a multilinear function of $x_v$" is
  asserted; it holds because the $t$ vertices of each class are twins (same
  neighborhood), so the cut value depends only on the count per side.
- **Fix.** Insert one sentence stating twin-interchangeability, so the multilinear
  reduction is derived rather than asserted.

### B4. Abstract under-credits BCL with the all-N tail bound (drops "for N large")
*(Citation#1)*

- **Location.** Abstract lines 36–38: BCL "proved it in the two density tails ... and
  proved the global bound $a(N)\le N^2/23.5$" — stated unconditionally.
- **Problem.** BCL Thm 1.3 is asymptotic ("for $N$ sufficiently large," correctly
  stated in the body, Thm 4.1 / lines 237–240). The all-$N$ tail version is the
  draft's OWN contribution (Cor 4.2 via blow-up), so the abstract over-credits BCL.
- **Fix.** In the abstract say BCL proved it "asymptotically / for large $N$" in the
  tails, OR note the all-$N$ version follows by the blow-up transfer (Cor `cor:tails`).

### B5. Abstract brute-force range "order ≤11" vs body "order 9,10,11,12"
*(merged: Claims#5, Citation#2, Honesty#7, Exposition#1)*

- **Location.** Abstract lines 55–56 ("order at most $11$") vs §6 para (4) lines
  330–333 ("order $9,10,11,12$," headline in-band max 0.0556 at order 12).
- **Problem.** The order-12 value 0.0556 is the largest of the four and underwrites
  the "margin ≥ 0.024" claim (`G2_AUDIT_REPORT.md` D5). The abstract under-reports
  the strongest checked case.
- **Fix.** Change abstract to "order at most $12$" to match §6 and the audit.

### B6. N/5 peeling recursion attributed to an OEIS/SeqFan comment; AES→increment chain compressed
*(Citation#3)*

- **Location.** §7 lines 361–364: AES gives min-degree ≤2N/5, "peeling it yields the
  unconditional but weaker recursion $a(N)\le a(N-1)+N/5$ \cite{A389646}."
- **Problem.** Citing an OEIS comment as the source of a math bound is weak; the
  AES→increment inference is compressed.
- **Fix.** State the N/5 recursion as elementary/folklore ("a standard peeling
  argument"), cite the SeqFan discussion only as where it was recorded, and spell the
  one-line derivation. (AES74 venue Discrete Math. 8 (1974) 205–218 is correct.)

### B7. Author/affiliation TODO placeholder still in source
*(Exposition#2)*

- **Location.** Line 20: *"% TODO(user): confirm author name / affiliation before
  submission."*
- **Problem.** Leftover placeholder; author block must be finalized for arXiv.
- **Fix.** Confirm author name/affiliation and delete the TODO comment.

---

## (C) NICE-TO-HAVE

- **C1. "Same edge density" normalization (Math#5, §4 Cor 4.2 line 251).** Exact only
  in the $d=2e/N^2$ normalization; in $\binom{n}{2}$ normalization it is only
  asymptotic. Argument still correct (t→∞). Fix: clarify the normalization.
- **C2. a(25) is the first NEW value (Math#6, §1 lines 104–106).** A389646 is exact
  only to n=23. Add: "a(25)=25 through a(180)=1296 lie beyond the exhaustively
  determined range (n≤23) and are new."
- **C3. BCL theorem number (Citation#4, Thm 4.1 line 237).** Re-confirm "[Theorem 1.3]"
  against the final BCL PDF / Eurocomb proceedings; numeric content is verified
  regardless.
- **C4. Regenerator soundness test is the single closed-form case (Honesty#9, §6 para
  (2) line 307).** Tie it to the stronger per-flag zero-violation comparison over all
  1897 order-9 flags (already reported line 343) rather than presenting the k=0 case
  as the validation.
- **C5. $g_r$ described as "flag density" (§3) vs "deficit functional" (§6)
  (Exposition#4).** Call it a "deficit atom (profile-cut density minus 2/25)"
  consistently.
- **C6. μ=ν=0 in the realized cert (Exposition#5, Thm 3.1 lines 211–219).** Optional
  half-sentence: the realized certificate has μ=ν=0 (band enforced via deficit/moment
  atoms), so comparison to the .pkl is not surprising.
- **C7. Dangling label `eq:conj5` (Exposition#6, line 79).** Never `\eqref`'d. Either
  reference it where a(5n)=n² is restated, or drop the `\label`.
- **C8. Non-monotone value list (Exposition#7, line 101).** "$a(30)=36$, $a(25)=25$,
  \dots" reads oddly; reorder ascending.
- **C9. Unsourced "$-5.45\times10^{-3}$" (Exposition#8, §6 para (3) line 316).**
  Confirmed in `G2_AUDIT_REPORT.md` D3 ("down to −5.45e-3"); cite the script/output
  or soften to "order $10^{-3}$."

---

## Verified-correct (no action)

δ = 12045893274065266971721/198450000000000000000000000 = 6.0699891e-05;
(25/2)·36²·δ = 0.9833 < 1; (25/2)·37²·δ = 1.0387 ≥ 1; δ < 1/450; band
LO=1243/5000=0.2486, HI=3197/10000=0.3197; blow-up identity, integrality rounding,
three-regime coverage (gap-free at band edges); 8 nonzero λ, 114 nonzero γ, μ=ν=0;
brute in-band maxima 0.0494/0.0400/0.0496/0.0556; OEIS a(5,10,15,20)=1,4,9,16. BCL
thresholds/bounds match arXiv:2103.14179. Attribution of Razborov, BCL, AES, EGS92,
A389646 is honest. No LaTeX construct breaks compilation.
