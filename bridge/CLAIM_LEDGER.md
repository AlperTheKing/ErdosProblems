# Step-2 CLAIM LEDGER — Erdős #23

Every claim with status, exact statement, dependency, and audit. Append-only in
spirit; edit only to update STATUS/AUDIT of an existing claim. No claim is
"DONE" without an independent audit line.

Statuses: PROVED (audited) | CONDITIONAL (proved given a dependency) |
CONJECTURED (believed, evidence) | OPEN | REFUTED | WEAK (rigorous but
non-competitive).

---

### C1 — Reduction theorem
**Statement:** `a(30) <= 36` and (H2 peeling, ∀ n>=7) ⟹ `a(5n) <= n^2` ∀ n>=1.
**Status:** PROVED (conditional on H1=Step1 and H2).
**Depends:** H1 (Codex), H2 (open).
**Audit:** `REDUCTION_THEOREM.md` §Proof + §Audit notes. Telescoping identity
`(n-1)^2+(2n-1)=n^2` checked; base table n=1..6 cross-checked vs OEIS A389646
entries 5/10/15/20 = 1/4/9/16, a(25)=25, a(30)=36. Independently re-derived via
summation `25 + sum_{6}^{n}(2k-1) = n^2`. ✓

### C2 — Tightness of the increment
**Statement:** For `G = C5[n]`, `S` = one vertex per part, `beta(G)-beta(G-S) =
2n-1` exactly; hence (H2)'s constant cannot be improved to `2n-2`.
**Status:** PROVED.
**Audit:** `beta(C5[m])=m^2`, `G-S=C5[n-1]`, `n^2-(n-1)^2=2n-1`. ✓

### C3 — Greedy half-cut is non-competitive
**Statement:** Greedy extension gives `beta(G) <= beta(G-S)+floor(m(S)/2)`;
on `C5[n]` every 5-set has `m(S) >= 10n-O(1)`, so this route only yields
`a(5n) <~ 3.1 n^2`, weaker than BCL's `~1.06 n^2`.
**Status:** WEAK (rigorous lower-quality bound).
**Audit:** `PEELING_LEMMA.md` §3. m(S)=10n-5 on extremal; floor->5n-3. ✓

### C4 — Sufficiency of weaker forms
**Statement:** (H2) ⟹ (H2') ⟹ (H2''); and (H2'') = `a(5n)<=a(5(n-1))+2n-1` is
all the induction needs.
**Status:** PROVED.
**Audit:** `PEELING_LEMMA.md` §1. Each implication immediate. ✓

### C5 — Hardness placement
**Statement:** (H2'') ∀ n>=7 (with equality on C5[n]) implies the exact constant
`1/25` for a(5n) in all regimes; BCL leave the medium-density exact constant
open. So (H2'') is >= as hard as an open asymptotic question.
**Status:** CONJECTURED (informal hardness argument; not a formal reduction).
**Audit:** consistency note only; do NOT cite as a theorem. `PEELING_LEMMA.md`§4.

### C6 — Closed form for blow-up beta  (Lemma BU1)
**Statement:** `beta(C5[m_0..m_4]) = min_i m_i m_{i+1}` (minimum consecutive
product), for all `m_i >= 0`.
**Status:** PROVED (fully — whole-part optimality now rigorous).
**Audit:** (1) monochromatic count is MULTILINEAR in the per-part split variables
`a_i`, so its box-minimum is at a vertex `a_i∈{0,m_i}` = whole-part colouring
(upgrades the old "brute-verified" step to a theorem); (2) cut-space of C5 (cuts
= even subsets ⟹ mono = odd subsets ⟹ min = single min edge). Brute force still
matches on 10/15/20-vertex blow-ups. `PEELING_LEMMA.md` §9 (BU1).

### C7 — Blow-up Peeling Lemma  (Lemma BU2)
**Statement:** for `Σ m_i = 5n`, `pc(C5[m]) <= 2n-1`, equality iff balanced.
**Status:** PROVED-in-tight-case + VERIFIED n<=10. Case A (all m_i>=n-1, the
tight regime) PROVED via balanced reduction `x_i=n-1`. Case B (a small part):
TRUE, verified exhaustively all compositions n<=10, but NO clean removal rule —
water-filling REFUTED (EXP-5, fails n=9). General Case-B proof OPEN.
**Audit:** `PEELING_LEMMA.md` §9; EXP-3 (n<=6 then n<=10) worst pc=2n-1 at
balanced; EXP-5 water-filling counterexample m=[7,12,9,10,12].

### C9 — Blow-up exact stability (Lemma BU3)
**Statement:** over `Σ m_i = 5n`, `min_i m_i m_{i+1} <= n^2` with equality iff
`m=(n,..,n)`; so `C5[n]` is the unique beta-maximiser among C5-blow-ups.
**Status:** PROVED (AM–GM; equality analysis). `PEELING_LEMMA.md` §9 (BU3).
**Use:** seed of the exact-stability route to (H2).

### C7b — BU2 Case B (blow-up peeling, small-part case)
**Statement:** for `Σ m_i=5n` with some `m_j<=n-2` and `P=min_i m_i m_{i+1}>=2n`,
some removal of 5 vertices keeps `min_i (m_i-r_i)(m_{i+1}-r_{i+1}) >= P-(2n-1)`.
**Status:** PARTIALLY CLOSED (TRUE: verified exhaustively n=2..13). Split (Case 2,
`P>=2n`): **(2-min1) some `m_i=1` — PROVED** (remove 5 from a `>=2n` neighbour ⟹
`pc<=5<=2n-1`; exhaustively confirmed n<=13, worst pc=5); **(2-min>=2) all
`m_i>=2` — VERIFIED n<=13** via all-ones `(1,1,1,1,1)`, but the simple proof
route is REFUTED: the bounds `pc <= s_b-1` (any argmin-reduced edge) and
`pc <= s_max-1` are both too LOOSE. The clean reduction "some argmin-reduced edge
has endpoint-sum `<=2n`" is **FALSE** (counterexample `m=[2,23,5,7,23]`, n=12:
both argmin-reduced edges have sum 25 > 2n=24 — yet all-ones still gives pc=13<=23
because the true `P=35`, not `2*23`). So all-ones works for `m_i>=2` empirically
but needs a tighter `P-Q` argument than `s_b`/`s_max` give. PROOF STILL OPEN; the
computational check (EXP) prevented adopting a false lemma. NOT critical path.
Both all-ones and water-filling REFUTED as UNIVERSAL rules. So BU2 Case B is down
to one clean lattice inequality. NOT on the critical path (blow-up sub-case).
**Audit:** `PEELING_LEMMA.md` §9; EXP-3 (n<=13), EXP-5 (water-filling counterex).
**UPDATE 2026-06-20 (`BU2_REGIME_REDUCTION.md`, `verify_BU2_blowup_peeling.py`):**
the case split is now COMPLETE and explicit:
 (R1, PROVED) `P<=2n-1 ⟹ Δ<=P<=2n-1` trivially (β can't rise under deletion); this
   discharges ALL unbalanced+low-P configs that were in neither C7 Case A nor the
   `P>=2n` hypothesis of C7b. So BU2 reduces EXACTLY to regime `P>=2n`.
 (R2, PROVED) regime `P>=2n` has AT MOST ONE size-1 class (a size-1 class forces
   both neighbours `>=2n`; two would need `>=6n+2>5n`).
 Verification EXTENDED to ALL compositions `n<=20` (was `n<=13`); `Δ_best<=2n-1`
   with 0 violations; worst case UNIQUELY balanced `C5[n]` (`Δ=2n-1`).
 **CORRECTION (2026-06-20):** the prior claim that all-ones settles (2-min>=2) is
   **REFUTED** — all-ones is NOT universal even for all `m_i>=2`. First failure
   `m=(2,31,7,9,31)`, n=16 (`Δ_allones=32>31`); a size-2 part flanked by two `~2n`
   parts behaves like the size-1 case. (All-ones happens to work for every config
   only while `n<=15`, which is why the `n<=13` check missed it.) So the heavy-pair
   inequality `(m_i-1)(m_{i+1}-1)>=P-2n+1` is FALSE in general.
 **Actual open piece:** an ADAPTIVE removal rule for regime `P>=2n` (the optimal `s`
   protects small parts and trims `~2n` neighbours). `Δ_best<=2n-1` holds (verified
   `n<=20`); no clean rule proven. **ALL FIVE natural routes now REFUTED** (all-ones,
   greedy-max, water-filling, L2-balance — explicit rules; + naive smoothing: the
   per-transfer monotonicity of `Δ_best` is FALSE, 6320 viol at n=7, confined to
   low-`Δ` configs). Positively, `max_m Δ_best=2n-1` uniquely at balanced (n=7..20),
   so the lemma is robustly TRUE; the proof is genuinely hard. OPEN, off critical
   path; question saved `gpt_pro_consultations/Q4_BU2_smoothing` for manual relay.
   **BU2 proof-route search EXHAUSTED by Step-2; parked pending GPT/new idea.**

### C16 — homomorphic-to-C5 ⟹ β<=n²  (Lemma C5HOM)
**Statement:** any triangle-free `G` on `5n` vertices with a homomorphism to `C5`
has `β(G) <= n^2`.
**Status:** PROVED (fibers `V_i=φ^{-1}(i)` ⟹ `G ⊆ C5`-blowup; near-proper C5 cut +
BU3). `MINIMAL_COUNTEREXAMPLE.md` C5HOM.
**Use:** the exact lever for a min-degree route; but AES gives bipartite (β=0,
trivial) and Jin gives only 3-colourability (insufficient — C5[n] is 3-colourable
with β=n²). The "3-colourable vs hom-to-C5" gap = the medium-density difficulty.

### MC6 — AES min-degree cap
**Statement:** a counterexample has `δ <= 2n` (AES: tri-free + δ>2N/5 ⟹ bipartite).
**Status:** PROVED (finite/exact). `MINIMAL_COUNTEREXAMPLE.md` MC6.

### C8 — Sharp Peeling Conjecture (SPC)
**Statement:** for every triangle-free G on 5n vertices, `pc(G) <= 2n-1`, with
equality iff `G ≅ C5[n]`.
**Status:** CONJECTURED. Evidence: exhaustive n=2 (all 12172 graphs; unique
saturator C5[2]); structured n=3,4 (unique saturators C5[3],C5[4]; Petersen[2],
dodecahedron strictly slack); blow-up subclass proved tight-case (C6,C7).
Implies (H2). Reframes at extremal graphs to extremal-uniqueness.

### C10 — Minimal-counterexample structure (Lemma MC1)
**Statement:** a minimal-edge counterexample `G` (min `n0>=7` with `a(5n0)>n0^2`,
fewest edges) satisfies: (a) `beta(G)=n0^2+1` exactly; (b) every edge is
beta-critical (`beta(G-e)=n0^2`); (c) `delta(G)>=2`. Hence (H2) need only be
proved for connected*, edge-beta-critical, triangle-free `G` on `5n` vertices
with `beta=n^2+1`, `delta>=2`. (*connectedness NOT proved — excess can split;
not used.)
**Status:** PROVED (a,b,c). `MINIMAL_COUNTEREXAMPLE.md` (MC1).
**Audit note:** an earlier connectedness sub-claim was INVALID (padding one
component need not be a counterexample when excess splits); removed on self-audit.
Edge-deletion-moves-beta-by-<=1 verified from `beta=e-maxcut`.

### C11 — Exact Peeling-Cost Identity (PCI)
**Statement:** `β(G)-β(G-S) = min_{ψ cut of G-S}[ surplus(ψ)+extcost(ψ,S) ]`
(surplus = suboptimality of ψ for G-S; extcost = min mono edges to attach S given
ψ). Hence (H2) ⟺ ∃ S,ψ with `surplus(ψ)+extcost(ψ,S) <= 2n-1`.
**Status:** PROVED (edge partition + min). `PEELING_LEMMA.md` §4c.
**Use:** strictly generalises the greedy extension bound (allows trading a
slightly suboptimal G-S cut for cheaper attachment of S); the exact target for
the open (H2). Matches the identity GPT-Pro Q1 is converging to (cross-check
pending).

### C12 — No-light-boundary (Lemma MC2)  [from GPT-Pro Q1, audited]
**Statement:** in the minimal-edge counterexample, every 5-set `S` has
`e(S,V∖S) >= 4n0-2` (`>=4n0` if `G[S]≇C5`); the 5 lowest-degree vertices have
degree-sum `>= 4n0-2`, so `<=4` vertices have degree `< (4n0-2)/5 ≈ 0.8n0`.
**Status:** PROVED (independently re-derived from `Δ(S)>=2n0` + greedy Lemma 4).
`MINIMAL_COUNTEREXAMPLE.md` MC2. Strengthens MC1's `δ>=2`.

### C13 — Two-dominating C5 / root defect (Lemma MC3)  [from Q1, audited]
**Statement:** a 2-dominating induced C5 forces `G ⊆ C5-blow-up` with `β<=n^2`;
so a minimal counterexample has none. Root defect `def(S)=Σ(2-d_S(v))` is a finite
stability parameter (route f).
**Status:** PROVED. `MINIMAL_COUNTEREXAMPLE.md` MC3.

### C14 — Frozen-pair reformulation (Lemma MC4)  [from Q1, audited]
**Statement:** `a(5n)<=n^2 ⟺` no triangle-free `H` on `5n` vertices with
`β(H)=n^2` has a nonedge `uv` whose ends are together in EVERY maximum cut.
**Status:** PROVED equivalent. `MINIMAL_COUNTEREXAMPLE.md` MC4. Rooted target;
handed to Codex.

### C15 — Counterexample density (Lemma MC5)
**Statement:** any triangle-free `G` has `e(G) >= 2 β(G)` (since `maxcut>=e/2`);
a counterexample (`β=n^2+1`, `5n` vtx) has `e >= 2n^2+2`, avg degree `>= 4n/5`,
density `>= 0.16`; combined with BCL (low `<=0.2486`, high `>=0.3197`) it lies in
the open medium window `(0.2486,0.3197)`.
**Status:** PROVED (the `e>=2β` part); the BCL-window placement DEPENDS ON BCL's
stated thresholds (verify vs arXiv:2103.14179). `MINIMAL_COUNTEREXAMPLE.md` MC5.
**Use:** cross-checks MC2 (avg degree ~0.8n); locates difficulty in medium density.

### REJECTED-1 — GPT Q1 Lemma 5 (edge degree-sum `d(u)+d(v)>=8n/5+2`)
**Status:** DISPROVED-PROOF (claim unproven). The argument bounds `Σ_T d(w)` with
the inequality reversed (the R(3,3) triple has degrees `>=4n/5` each, a LOWER
bound, used as an upper bound). Do not use. `Q1_ANSWER_AND_AUDIT`.

### H1 — a(30) <= 36  [Step 1, Codex — EXTERNAL]
**Status:** CONDITIONAL/IN-PROGRESS (Codex). As of 2026-06-20T01:52, Codex CLOSED
the `e_R=16` frontier of profile 6195: clean union `59823/59823 INFEASIBLE`,
`missing=0, malformed=0, noninf_keys=0` (verifier `verify_state_count_union.cpp`).
Step-2 spot-audit: the union methodology is SOUND (dedup by (mask,p,M), zero
UNKNOWN). BUT H1 is NOT complete — Codex itself keeps it "IN PROGRESS pending
global Step-1 audit" with "remaining open families", and the NEEDED_FROM_STEP1
checklist is "not yet satisfied". Crucially the BCL-finiteness gap (e>=140 range,
DEP-a25/HANDOFF) is NOT yet addressed by Codex (its next action is the global
audit). So H1 stays CONDITIONAL: one frontier closed, but search-space
completeness (all profiles + all edge ranges, esp. e>=140 and e<=108) unproven.

### DEP-a25 — a(25) = 25  [n=5 base case, PROJECT dependency]
**Statement:** no triangle-free graph on 25 vertices has `β >= 26`.
**Status:** ⚠️ **GAP CONFIRMED (2026-06-20)** — downgraded from AUDITED-SOUND.
Two independent WebFetches of the full BCL paper (ar5iv 2103.14179) confirm its
Theorem 1.3 reads **"Let G be a triangle-free graph on n vertices. Then, for n
large enough, (a) D2<=n^2/23.5; (b) D2<=n^2/25 if |E|>=0.3197 C(n,2); (c)
D2<=n^2/25 if |E|<=0.2486 C(n,2)"**, and §2.3 states **"Theorem 1.3 only holds
for n >= n0 for some n0 large enough"** with NO explicit n0. So all three are
ASYMPTOTIC, not exact finite inequalities at all n. The a(25) proof APPLIES BCL high-density AT
n=25 ("a triangle-free graph on 25 vertices with density >= 0.3197 has β <= 25")
to force `e <= 95`. If BCL's n0 > 25, this step is INVALID and `e <= 95` does not
follow, breaking the proof. **ACTION NEEDED:** (i) confirm the exact BCL theorem
statement / whether n0 <= 25 (the ar5iv extraction is second-hand — read the PDF
Thm 1.3 directly); OR (ii) supply a direct high-density argument for 25-vertex
triangle-free graphs (`109<=e` regime), OR a direct/enumerative proof of
a(25) <= 25. Until resolved, the n=5 base case is NOT solidly established.
Same caveat hits MC5's "(0.2486,0.3197) medium window" (asymptotic, not finite).

[Prior audit, still valid for the NON-BCL parts:] Step-2 read
`docs_newmath/erdos23_a25_proof.md` and reconstructed the proof:
- Lower bound: `C5[5]` gives `β=25`. ✓
- Upper bound (contradiction, `β>=26`): BCL high-density ⟹ density `<0.3197` ⟹
  `e(G) <= 95`; pick `v`,`u` of degree `<=7` (avg deg `<=7.6`,`<8`), apply
  `β(X) <= β(X-x)+⌊d/2⌋` twice ⟹ a triangle-free 23-vtx `F` with `β(F)>=20`;
  since `a(23)=20` (McKay), `β(F)=20`, so `F` ∈ McKay `minbip23_20x.g6` (complete
  catalogue); the project's local C++ check (SHA256-pinned) found all 6 such
  graphs have `>=100` edges; but `e(F) <= e(G) <= 95` — contradiction. ✓
- Every inequality direction checks; the two-deletion greedy bound is correct.
**Remaining caveat (one citation), now pinned (WebFetch arXiv:2103.14179
abstract):** BCL's GLOBAL bound is finite — `β <= n^2/23.5` ("removing at most
n^2/23.5 edges") for all n — but that gives only `a(25) <= 25^2/23.5 = 26.6`, i.e.
`<=26` (one above the truth), so it does NOT alone yield a(25)<=25. The a(25)
proof relies specifically on the HIGH-DENSITY result, stated as "prove the [Erdős]
conjecture for edge density `>= 0.3197`". If "prove the conjecture" = the exact
finite `a(N) <= N^2/25` valid at `N=25` (the natural reading — the conjecture is
exact/finite), the proof is SOUND. The EUROCOMB abstract does not literally
disambiguate finite-exact vs. "n large"; the full paper Thm statement should be
read to be 100% certain there is no large-n caveat at N=25. The McKay catalogue
(`a(23)=20`, all β=20 graphs `>=100` edges) is trusted + locally verified
(count=6). This residual is the SAME citation MC5 leans on.
**UPDATE 2026-06-20 (provenance + resolution path):**
- `a(25)=25` is **NOT in OEIS** — A389646 stops at N=23 (so `a(5,10,15,20)` AND
  `a(23)=20` ARE OEIS-trusted, but `a(25)` is not). 25 vertices is too large to
  brute-force with `geng`, so there is no cheap independent computed value to cite.
- Step-2's L0/L1 (`MAXCUT_BOUNDS.md`) do NOT help: they give a LOWER bound
  `β>=26 ⟹ e>=52+Δ`, whereas the McKay route needs an UPPER bound `e<=95`. The
  upper bound is exactly the BCL high-density content; Step-2 cannot derive it
  elementarily. So n=5 is NOT closable by Step-2 alone.
- **Resolution path filed:** `NEEDED_FROM_STEP1.md` asks Codex whether its exact
  rooted-enumeration machinery (used for `a(30)`) can certify `a(25)<=25` directly
  (smaller search than N=30). An exact certificate would retire this BCL gap
  unconditionally. Status stays GAP-CONFIRMED until BCL-n0<=25 is pinned OR an
  exact N=25 certificate lands.
- **UPDATE 2026-06-20 — BCL gap RESOLVED for the density TAILS (blow-up transfer,
  audited SOUND).** Codex's uniform-blow-up transfer (`H1_AUDIT_LOG`) applies to
  a(25): a 25-vtx `β>=26` counterexample `G` has `β(G[t])=t²β(G)` and
  `density(G[t])→2e(G)/625`, so `e(G)<=77` (BCL low) and `e(G)>=100` (BCL high) both
  contradict BCL for large `t`. So only the medium window `78<=e<=99` remains for
  a(25). This REPLACES the old McKay-route reliance on "BCL high-density AT n=25"
  (which needed n0<=25): the asymptotic transfer is rigorous. The n=5 base is now
  gap-free EXCEPT the finite medium window `78<=e<=99` (needs enumeration, like a(30)'s
  `112<=e<=143`). Materially upgraded from full GAP to a narrow finite window.
**Net:** the n=5 base case is on solid footing; only the BCL-exactness citation
remains to nail. `REDUCTION_THEOREM` DEPENDENCIES updated.

### L0 / L1 — exact triangle-free MaxCut bounds  (`MAXCUT_BOUNDS.md`)
**Status: PROVED + COMPUTATIONALLY VERIFIED (2026-06-20).**
- L0 (any graph): `β <= ⌊e/2⌋`. Corollary N=30: `e <= 73 ⟹ β <= 36` unconditionally.
- L1 (triangle-free): `MaxCut(G) >= e/2 + Δ/2`, i.e. `β(G) <= ⌊(e − Δ)/2⌋`.
  Proof: `v` of degree Δ, `N(v)` independent ⟹ pre-place `v|N(v)` (cuts all Δ),
  greedy on the rest (≥ half of remaining edges); no edges inside `N(v)`.
  Equality on stars. Verified EXHAUSTIVELY on all 2466 triangle-free graphs
  `n=5..9` (`experiments/verify_L1_maxcut_delta.py`), 0 violations.
**Use:** discharges the low-edge sub-band of base cases without enumeration
(handed to Codex). Does NOT touch high density (`e>=140` at N=30) — `C5[6]`
saturates `β=36` there, so that band still needs Codex's exact certificates.
Not a closer; honest scope in `MAXCUT_BOUNDS.md`.

### H2 — Peeling Lemma  [the open core]
**Status:** OPEN. No proof; greedy insufficient; pursuing cut-aligned + GPT.
**2026-06-20 (workflow wf_ff5f1a5a-420, 9-strategy adversarial attack):** still OPEN,
0 proofs. New assets recorded in `H2_ATTACK_FINDINGS.md`. Decisive method-class
DEAD-ENDS (prune future effort): SDP/convex (lower-bounds β, GW gives 3.973n²<4n² on
C5[n]); spectral (β not spectral — cospectral N=12 pair β 3 vs 4); local-count (β not
a fn of ≤C6 counts — odd-girth invisible); weighted (quotient β≥β). Refuted: uniform
5-set averaging (E→2n−4/5>2n−1) and induced-C5 averaging (N=15 counterexample
E_mu=5.32>5). Unifying obstruction: upper-bounding β = exhibiting a realignment cut;
C5[n] sits at every static certificate threshold.
**2026-06-20 (2nd workflow wbnn6tj9s + Step-2 EXACT verification):** still OPEN, 0
proofs. **★ Step-2 PINNED DOWN H2 at the extremal family** (`verify_h2_5set_c5n.py`,
brute MaxCut over all C(5n,5) 5-sets): `min_S[β(C5[n])−β(C5[n]−S)] = 2n−1 EXACTLY`
(n=1,2,3 → 1,3,5), achieved by exactly `n⁵` C5-TRANSVERSALS (one vtx/part; removal
gives C5[n−1], drop n²−(n−1)²=2n−1). So H2 is TRUE & TIGHT on C5[n] — the workflow
critic's "H2 fails at C5[2]" was a harness MaxCut bug (REFUTED). Corollaries: (a) the
right peeling object is a near-C5-transversal (ties H2 to C5HOM/WYZ, not single-vertex);
(b) **averaging/LP route DEAD** — mean drop 3.87,7.19 > 2n−1 strictly for n≥3, so no
lower-bound-on-mean yields the needed min. New sub-results: Deletion-saturation lemma
`β≤f(M−1)+⌊δ/2⌋` (= V1 iterated + f; OFF-BY-ONE, zero slack at C5[n], f(12)=5>blowup4
so f(5n−1)≤n²−n equally hard — TOOL not path); Σ_vS_v=Q (uniform aggregate = 1/16 dead
end); deficiency anti-correlates with gain (GPT Q8 deficiency frontier WRONG SIGN);
per-ball A7 circular (c=25 forced). Live frontier unchanged = WYZ-hom-peel + deviation
inequality on the non-hom exceptional set. `H2_ATTACK_FINDINGS.md`.
**2026-06-20 (3rd workflow wf_67b8bb6b-50e + Step-2 machine-check):** still OPEN, 0 proofs.
The one proof attempt (discharging) REFUTED (separable "deficiency" overcounts the joint
reinsertion gain; 8-vtx witness drop=1>0). Red teams found NO counterexample (14 explicit
graphs + agent-claimed exhaustive 286699 tri-free 15-vtx ≥42 edges). **★ Step-2 independently
machine-checked all 14 via `h2_check_edgelist.exe`: all tri-free, all β match, H2 holds for
every one — NEW n=4 data: Petersen[2] (β12,drop5<7), Cay(Z20,1,4,9) (β12,drop5), C5[4]−edge
(β15,drop6); and C5[4] itself β16, min 5-set drop=7=2n−1 EXACTLY (extends tight-at-C5[n] to
n=4).** Surviving honest reformulation (≈tautological, SUFFICIENT only): `β(G)≤β(G−T)+e(T,V)
−gain_T^joint` (no decomposition). Remaining route needs an EFFECTIVE stability theorem
near C5[n] (explicit ε,C) — not in literature. GPT brief Q9 queued. `H2_ATTACK_FINDINGS.md`.

### CLEBSCH — Clebsch-frustration reduction + Clebsch-hom bound  [GPT Q9, Step-2 AUDITED+VERIFIED]
**Source:** GPT Pro Q9 (user-relayed), `gpt_pro_consultations/Q9_ANSWER_AND_AUDIT_2026-06-20.md`,
`verify_clebsch_frustration.py`. Status of each piece:
- **CLEBSCH-HOM (PROVED + VERIFIED):** every triangle-free `G` homomorphic to the Clebsch graph
  `K`(=16 even subsets of [5], `A~B ⟺ |A△B|=4`) has `β(G) ≤ N²/25`. Proof: 5 coordinate cuts ⟹
  `β ≤ e/5` (each edge mono in exactly 1 of 5, verified); triangle-free ⟹ `MaxCut ≥ Q/N ≥ 4e²/N²`
  (verified 0/1803); combine. ENLARGES C5HOM (C5→K). **Uniqueness:** equality ⟹ `G=C5[N/5]`
  (rigorous, Step-2 re-derived). Caveat: NOT every tri-free graph is Clebsch-hom (K is 4-chromatic).
- **★ CLEBSCH-FRUSTRATION reduction (SOUND):** `τ_K(G)=min_φ Σ (4−|φ(u)△φ(v)|)/2` over maps
  `φ:V→V(K)` (a 16-state quadratic CSP = 5 cuts + one parity relation `A_5=A_1△A_2△A_3△A_4`).
  Then `β(G) ≤ (e+2τ_K(G))/5`, so **`β ≤ N²/25` whenever `τ_K(G) ≤ (N²/5 − e)/2`.** This REPLACES
  "effective stability near C5[n]" with a concrete, explicit-constant target. Both C5[n] and
  Clebsch-blowups have τ_K=0.
- **TAU5 (PROVED via A7):** a counterexample (`β≥N²/25`) has `τ_5(G) ≥ 7/800·N²` (min edges to kill
  all C5; via `β(G−F)≤N²/32` + `β≤β(G−F)+|F|`), hence ≥`7/4000 N²` edge-disjoint induced C5's.
- **CF (the new OPEN CORE, UNPROVEN):** ∀ε>0, large tri-free `G` in the band with `τ_5≥7/800 N²`
  satisfy `τ_K(G) ≤ (N²/5−e)/2 + εN²`. Asymptotic CF (no effective N0) ⟹ EXACT conjecture by
  blow-up transfer (logic verified). GPT: cannot prove CF — the new barrier. More concrete/flag-
  algebra-amenable than "stability". **Do NOT mark solved.**
  **COMPUTATIONAL SUPPORT (Step-2, `tau_K_cf_test.py`, τ_K via local-search UPPER bound):** CF
  (`τ_K ≤ (N²/5−e)/2`) holds on EVERY tested graph — C5[n] (τ_K=0=RHS, tight); 36 random band graphs
  N=15,20,25 (0 failures, usually large margin τ_K 0–7 vs RHS 6–25); structured hard cores. NOTABLE:
  Petersen[2] & Cay(Z20,1,4,9) have τ_K=0 ⟹ they are CLEBSCH-HOMOMORPHIC (covered by proven (3)!),
  so the Clebsch class is much larger than C5-hom; only Cay(Z20,2,5,9) is genuinely non-Clebsch-hom
  (τ_K=10, CF tight). Strong evidence CF is TRUE (not a proof — τ_K_ub is a heuristic upper bound, CF
  is asymptotic).
  **★ GPT Q10 (AUDITED+VERIFIED 2026-06-20, `Q10_ANSWER_AND_AUDIT`, `verify_q10_cf_audit.py`):
  CF still OPEN but PINNED.** (i) **τ_K ≤ (3/2)β PROVED** (induced-C4-in-Clebsch rounding;
  hand-verified + 0/22) ⟹ τ_K ≤ (3/47)N²≈0.064N² — ~2× too weak, caps β at ~1/17.4 (SAME wall
  as radius-2 scalar). (ii) **Frustration-stability sub-target REFUTED:** G=C5[m]⊔K_{r,r} has
  τ_K=0, density 0.128 (band), τ_5>7/800N², yet far from C5[n] (VERIFIED N=80). Right notion =
  saturation of `e+2τ_K`. (iii) **Synchronization obstruction PINNED:** Clebsch=Cayley(Γ,{[5]∖i});
  packed C5's give generator-perms that need NOT agree across cycles (cycle-space sync); explicit
  gap M_2(C5) (N=23,e=71,χ=5⟹τ_K≥1, 13 edge-disjoint induced C5's, packing-LP=0; VERIFIED). C5-
  packing/entropy alone CANNOT work. (iv) **Path forward = the RR flag target:** C5-rooted F_C (7-vtx,
  τ_K≤F_C PROVED) fails on Clebsch-blowups (twin-pairs); a 6th anticomplete root fixes it ⟹
  `min{min_C F_C, min_{C,z}F_{C,z}^(6)} ≤ (N²/5−e)/2+εN²` (8-vtx rooted CSP, exact on C5- AND
  Clebsch-blowups) — UNPROVEN, needs a flag/SDP certificate. (v) Exact MILP falsification
  (τ_K(F[k])=k²τ_K(F), ν_5* packing). **CF unproven; do NOT mark solved.**
  **★ GPT Q11 (fresh session, AUDITED+VERIFIED 2026-06-20, `Q11_ANSWER_AND_AUDIT`,
  `verify_q11_cf_audit.py`): advances Q10.** (i) **τ_K(G) ≤ e − 4e²/N² PROVED, UNCONDITIONAL**
  (density-only, no BCL): edge-root `τ_K ≤ e−(S_u+S_v)/2` (Clebsch P-Q perfect matching VERIFIED) +
  `M_2≥4e³/N²` (Cauchy-Schwarz, VERIFIED 0/200). Caps β ~1/17.9 (same wall) — density-only can't
  close CF. (ii) **Petersen-root + Clebsch-root certificates** (τ_K≤(3/4)·e_inc(bad)) repairing the
  C5-root failures on Petersen-/Clebsch-blowups (Petersen 15-family VERIFIED). (iii) **★ 4-BRANCH
  DICHOTOMY** = the sharp flag-SDP target: CF if every band graph satisfies ≥1 of {edge, C5, Petersen,
  Clebsch} certificate (flag orders 4/7/12/18, each an EXPLICIT randomized labeling). Open step =
  flag-SDP "coverage" proof that band+triangle-free forces one branch (research-grade). **CF/RR unproven.**
  **★ COVERAGE PROBE (`verify_4branch_coverage.py`, 2026-06-20T18:06, 31 band graphs):** CF direct
  (τ_K_ub≤RHS) 0 violations/31; random band cheap-coverage (edge-root OR C5-root F_C) 24/24 (C5-root
  F_C alone covers all 24); Petersen[t]/Clebsch[t] 4/4 cheap-FAIL with τ_K=0 (the 2 extra roots are
  genuinely needed — matches Q11 §7). EVIDENCE the 4 templates suffice; NOT the coverage proof. CF unproven.
  **★ ADVERSARIAL SEARCH (`adversarial_coverage_search.py`, 2026-06-20T18:13, hill-climb N=10..20):**
  0 CF counterexamples (τ_K_ub≤RHS every endpoint). C5-containing band graphs (N=15/18/20): g_cheap<0
  always (cheap covers; search can't defeat both). Only g_cheap>0 cases = C5-FREE graphs (F_C undefined,
  τ_K=0) ⟹ the A7 branch (β≤N²/32), not a real gap. Refined taxonomy = **5 branches** {A7 C5-free}∪{edge,
  C5,Petersen,Clebsch}; no NEW template indicated. Still EVIDENCE-only — CF/coverage UNPROVEN.
  **⚠ CORRECTION (2026-06-20T19:13, from GPT Q12 intermediate trace, INDEPENDENTLY CONFIRMED):** the
  random/adversarial search MISSED a structured family — the **Grötzsch graph (Mycielskian of C5) blow-up
  + a small isolated set**. Grötzsch[3]+1iso (N=34,e=180,x=0.1557,RHS=25.6) and Grötzsch[5]+1iso
  (N=56,e=500,x=0.1594,RHS=63.6) are IN-BAND, have **τ_K=0** (so CF HOLDS, 0≤RHS — NOT a counterexample),
  yet BOTH cheap templates FAIL (edge-root & C5-root F_C > RHS). Grötzsch CONTAINS induced C5s, so the
  prior "C5-root covers every C5-containing band graph / coverage saturated" claim is **FALSE/WITHDRAWN**.
  General regime: Grötzsch[t]+s·iso with s∈[0.18t,0.40t) ⟹ in-band ∧ both cheap fail (F_C=3t², edge=6t²,
  RHS=((11t+s)²/5−20t²)/2). ⟹ the cheap 2-template coverage is **INCOMPLETE**; the 4-template menu likely
  needs a 5th template OR must use Clebsch-HOM existence (τ_K=0) directly, not the explicit rooted menu.
  **CF/Step-2 truth UNAFFECTED** (τ_K=0). Awaiting GPT Q12 final answer for its proposed resolution. Test:
  `experiments` ad-hoc Grötzsch script (logged PROGRESS 19:13).
  **★★ COVERAGE-BY-4-TEMPLATES REFUTED — GPT Q12 ANSWER (31m22s) AUDITED+VERIFIED 2026-06-20T19:50,
  `Q12_ANSWER_AND_AUDIT` + `verify_q12_groetzsch_audit.py`.** GPT gave an explicit infinite family: weighted
  blow-up G_k of H=Grötzsch=M(C5) (classes 2k for u_i,v_i; k for w), N=21k, e=70k², **x=10/63≈0.1587 in-band**,
  **τ_K=0** (explicit Clebsch embedding of H, VERIFIED hom+induced), RHS=91/10·k². It DEFEATS edge-root
  (≥18k²>RHS), the degree-relaxed C5-root (≥10k²>RHS), Petersen+Clebsch (ABSENT: H is 11-vtx, no H−z is
  3-regular, classes are false twins), and A7 (has induced C5). **⟹ the 4-template COVERAGE / order-≤18
  flag-SDP route is DEAD** (GPT's 11-vtx graphon μ(u)=μ(v)=2/21,μ(w)=1/21 is an exact PRIMAL witness ⟹ no
  rational dual cert at any order). **Audit precision-correction:** the finer 10-map F_C covers GPT's G_k
  (F_C=6k²<9.1k²), but F_C-coverage is ALSO refuted by uniform Grötzsch[5]+1iso (F_C=75>RHS=63.6, τ_K=0,
  clean margin) — so coverage fails for BOTH certificate strengths; M(C5) is the obstruction either way.
  **My prior "coverage saturated, 0 gaps N=10..26" was a SAMPLING ARTIFACT (random search never built M(C5)).**
  **CF/Erdős#23 UNTHREATENED** (τ_K=0). **NEW OPEN PROBLEM (replaces order-18 SDP):** does the ENLARGED menu
  — canonical-profile roots of ALL false-twin-free induced subgraphs of Clebsch (rooted order ≤18, incl. the
  order-13 M(C5) root τ_K≤2·e_bad^H) — cover the band? GPT leaves OPEN. CF still UNPROVEN.
  **★ SHARP CF TEST (`cf_5chromatic_probe.py`, 2026-06-20T20:00):** first probe of in-band graphs with
  **τ_K>0** (χ(G)≥5 ⟹ not Clebsch-hom ⟹ τ_K>0; ratio τ_K/RHS is blow-up-INVARIANT, so any in-band tri-free
  graph with ratio>1 blows up to a CF COUNTEREXAMPLE). M(M(C5)) (23v, χ5, in-band x=0.1342): τ_K=7, RHS=17.4,
  **ratio=0.402**; M³(C5) (χ6): ratio=0.360. **0 counterexamples; CF holds with margin even on the hardest
  non-Clebsch-hom case.** Blow-up invariance confirmed (τ_K 7→28=4·7). Strong evidence CF TRUE. Natural next:
  adversarial hill-climb maximizing τ_K/RHS over in-band tri-free graphs (does ratio ever approach 1?).
  **★★ Q13 TOOLKIT (Rung 2, AUDITED+VERIFIED 2026-06-20T21:10, `Q13_ANSWER_AND_AUDIT` + `verify_q13_audit.py`)
  — step-by-step plan paying off.** All VERIFIED: (i) character structure c(A,B)=(3+Σσ_iσ_i)/4, σ_i(A)=(−1)^[i∈A];
  (ii) **Lemma 1 exact star-extension** min_A Σc(A,B_j)=(3d−Σ|s_i|+2εm)/4 (0 viol/20000); (iii) **Q(d)=
  3⌊d/4⌋+[d%4∈{2,3}]** sharp degree term; (iv) **per-vertex recursion τ_K(G)≤τ_K(G−v)+Q(d_v)**; (v) **★Lemma 3:
  every 2-centre ball N[x]∪N[y] of a tri-free graph is Clebsch-hom** (0 viol/11625; explicit map (13) 0 fail/6053)
  ⟹ **Cor 4 τ_K(G)≤τ_K(G−S_xy)+Q(m_xy)** ⟹ computable U(H)≥τ_K; (vi) local charging certificate; (vii) **Mycielski
  τ_K(M(G))≤3τ_K(G)+Q(n)** ⟹ τ_K(M^k(C5))≤8·3^{k−1}−9·2^{k−1}+1, R(M^k)→0 (iterated Mycielskians NOT extremal).
  **EXTREMAL (§6): edge-SATURATED, near UPPER density, K-deletion-distance Θ(N)** (eq 25: dist t ⟹ τ_K≤(3/4)tN).
  **NEXT Rung 4:** test U(H)≤RHS (or greedy 2-centre-ball peel ≤ RHS) on band ⟹ would give CF. CF still UNPROVEN.
  **★★ Q14 (Rung 5, AUDITED+VERIFIED 2026-06-20, `Q14_ANSWER_AND_AUDIT` + `verify_q14_audit.py`) — local
  charging route RULED OUT.** Reduced CF to the charging inequality (★) Σ_v F_v ≥ 10e−(4/5)N² at a 1-opt-stable
  φ (F_v=Σ_i|s_{v,i}|−2ε_v m_v). GPT gave (all VERIFIED): **21-vertex stable polytope** (4 types up to S_5);
  **sharp bound F_v≥(3/5)Q_v/d_v** (3/5 optimal, Q_v=Σ_i s_{v,i}²); **global identity Σ_v Q_v=10e−6W_0+2W_1+10W_2**
  (0/150); reduced subtarget **6H_1+12H_2≥17e−N²−6n_+** (eq 9). **★NEGATIVE (load-bearing, VERIFIED):**
  K_{16,64} (complete bipartite, IN-BAND x=0.16) with uniform 16-label distribution has s_{v,i}=0 ∀v,i ⟹ every
  vertex a tie ⟹ **1-opt-stable** with Σ F_v=0 (★ fails by 0.8N²), cost(φ)=¾e=0.12N², YET **τ_K=0** (2-color).
  ⟹ "1-opt stability + local types + triangle-freeness ALONE cannot yield (★)"; need φ GLOBAL minimizer.
  **★★★ META-FINDING: all THREE local-certificate routes to CF are now RULED OUT** with explicit in-band
  **τ_K=0** witnesses where the local bound overshoots: Q12 coverage (Grötzsch x=0.159), Rung-4 deletion
  (Grötzsch[5]+iso, const 3/4), Q14 1-opt charging (K_{16,64} x=0.16). **CF is irreducibly GLOBAL** (⟺ the
  conjecture in band); no purely-local certificate suffices. Rung-6 needs global-opt/nonlocal or a different
  decomposition (eq 9 at the GLOBAL minimizer). CF still UNPROVEN.
  **★★★ Q15 STRATEGY PIVOT (2026-06-20T23:05, `Q15_ANSWER_AND_AUDIT` + `verify_q15_audit.py`, GPT-recommended,
  AUDITED).** GPT: STOP using τ_K (16-state Clebsch surrogate = liability); work DIRECTLY with β + a fixed GLOBAL
  max-cut as a 2-coloring + MACROSCOPIC SWITCHING inequalities (bounded roots, Θ(N)-vtx switched set ⟹ retains
  quadratic info, unlike fixed k-opt). **Switching Lemma (VERIFIED):** A⊔B max cut ⟺ ∀S |M∩δ(S)|≤|C∩δ(S)| ⟺
  fractional SW ⟺ L1-form; flag-compatible (p_v=fn of max-cut color + adjacency to k roots ⟹ linear ineq in
  2-colored flags order k+2). Explicit **SW1** `|P|+e(P,R)+e(Q,T)≤e(R,T)` at every max-cut root: **0 viol all**.
  **C5-cleanup (proven):** β≤(e+4d_5)/5, d_5=C5-frustration; Step2 would follow if d_5≤(N²/5−e)/4 — but that is
  **FALSE** (`census_d5.py`: N=10 e=16 x=0.16 d_5=2>target=1, exact β=3≤4 so conjecture holds but cleanup gives
  4.8≰4; N=11 ratio 1.54). ⟹ **C5-cleanup INSUFFICIENT standalone** (lossy near band-top, same wall). **NET: the
  2-colored max-cut switching FLAG-SDP is the route** (materially stronger than the uncolored coverage SDP ruled
  out in Q12; K_4-free precedent arXiv:2605.05346) — needs flagmatic/CSDP, research-grade. Ranking: switching-
  flags > C5-stability-cleanup > peeling > fixed-2-opt. Step 2 still UNPROVEN.
  **★★★ FLAG-SDP MACHINE BUILT (2026-06-21, user-authorized multi-day; `bridge/flagsdp/`).** From scratch in
  Python+cvxpy (CLARABEL/SCS; no flagmatic). Engine VALIDATED: triangle-free counts=OEIS A006785; **reproduces
  Mantel edge-density=0.5000 exactly (N=3,4,5)**. 2-colored extension + primal SDP `max d_mono s.t. M^σ(x)⪰0,
  edge-band, switching` (β/N²→d_mono/2; target d_mono≤2/25=0.08). Switching = general rooted-switch limit
  functionals `Σχ(uv)(p_u+p_v−2p_up_v)≤0`, p∈{0,½,1} of (color,k-root-adjacency); SW1-limit verified ≤0 on max
  cuts. **Bound progression (max d_mono, N=5): band-only 0.320 → +0root 0.160 (d_mono≤d_cut) → +1root 0.118 →
  +2root 0.101** (β/N²≤0.0503). N=6 same at k≤1 (0.118) ⟹ switching is binding, not flag order. Need k=2-frac /
  k=3 separation-oracle / margin color-refinement to reach 0.08. Phase A,B DONE; C in progress (~0.10); D (exact
  rational certificate) pending. NOT a proof — Step 2 still UNPROVEN.
- **★ Λ₅ finite H2-test (SOUND + EXHAUSTIVELY RUN):** for tri-free base `F` on r vtx, `Λ₅(F)=
  min_{Σs_i=5} max_{σ∈O(F)} L_σ(s)`; `Λ₅>2r/5` ⟹ blow-ups FALSIFY H2, `<2r/5` ⟹ H2 holds, `=2r/5` ⟹
  need `R_σ(s)≥1` on every tight optimal cut. C5: s=(1,1,1,1,1), L=2=2r/5, R=1 ⟹ drop 2k−1 ✓.
  **Step-2 IMPLEMENTED + RAN (`lambda5_h2_test.py`) over ALL triangle-free bases r=5,6,7,8 (14/38/
  107/410 graphs): ZERO with Λ₅>2r/5, ZERO boundary R-fails.** So H2 holds on ALL blow-ups F[k] of
  every triangle-free F with r≤8, for ALL n (infinite family via finite test). Λ₅ histograms peak at
  0 (bipartite bases); max Λ₅ at r=8 is 3 (ratio 0.375 < 2/5).
  **EXTENDED r=9,10 (1897 + 12172 graphs): still 0 violations, 0 boundary R-fails.** Total ALL
  triangle-free bases r=5..10 (14565 graphs): ZERO Λ₅>2r/5. The ONLY boundary cases (Λ₅=2r/5) are
  C5 (r=5) and C5[2] (r=10) — i.e. C5-blow-up bases where H2 is tight — and they satisfy R≥1.
  **★ EMERGING SUB-TARGET (LAMBDA-BOUND):** conjecture `Λ₅(F) ≤ 2r/5 for every triangle-free F on r
  vtx, equality iff F is a C5-blow-up (+R≥1)`. If proven ⟹ H2 holds on ALL blow-ups F[k] ∀n. Cleaner
  than CF (finite-per-F, universal over F); candidate for GPT/workflow. (Still only covers blow-ups;
  H2 for non-blow-up tri-free graphs separate but n≤4 direct search found 0 violations.)
  Strong evidence H2 is the correct induction lemma.
**Use:** CF is the sharpest current target (attack via flag algebras / focused consult); Λ₅ test
is the decisive finite check of whether H2 is the right induction lemma.

### MERGE — β-preserving identification of a codeg-0 common-side pair
**Statement:** nonedge `uv`, `N(u)∩N(v)=∅`, with SOME max cut placing `u,v` same side ⟹
identifying `u,v` into `w` (`N(w)=N(u)⊔N(v)`) gives `β(H')=β(H)` exactly.
**Status: PROVED + INDEPENDENTLY VERIFIED (Step-2).** Proof: codeg-0 ⟹ `e` preserved
(bijection); (≤) push common-side max cut; (≥) pull any H'-cut back. Common-side
hypothesis necessary (else merge can raise β 0→1). Step-2 recomputed `merge` from
scratch: 0 violations / 15717 codeg-0+common-side pairs over all tri-free graphs N=7,8,9.
`H2_ATTACK_FINDINGS.md`. **Use:** the engine of the MC4 frozen-pair route; gap = merge
can create a triangle (open at extremality).

### STRICT-FLIP — frozen pair forces sub-half mono-degree
**Statement:** codeg-0 nonedge frozen same-side in every max cut of tri-free `H` ⟹
`2·m(u)<c(u)`, `2·m(v)<c(v)` in every max cut (m=mono-deg, c=deg).
**Status: PROVED** (single-flip would separate u,v else). Verified 0/26646 frozen pairs
N≤10. `H2_ATTACK_FINDINGS.md`.

### A7 — a_7 sub-bound (C5-free ⟹ small β)  [PROVED, exact, finite]
**Statement:** every `{C3,C5}`-free graph (odd-girth>=7) `G` on `N` vertices has
`β(G) <= N^2/32`; hence `a_7(5n) <= 25n^2/32 < n^2`. Consequence: any triangle-free
`G` on `5n` with `β>=n^2` contains an INDUCED `C5`.
**Status: PROVED + INDEPENDENTLY VERIFIED.** Engine lemma (PROVED): `{C3,C5}`-free ⟹
`MaxCut(G) >= e/2 + (1/2N)Σ_u d(u)^2` (radius-2 ball `H_v` is bipartite because C5-free
forces the dist-2 layer independent; `e(H_v)=Σ_{u∈N(v)}d(u)`; probabilistic extension;
average; Cauchy-Schwarz `Σd^2>=4e^2/N`). Source: GPT-Pro (user-relayed), Step-2
line-by-line audit + computation: all `{C3,C5}`-free graphs N=7..12 (301172 graphs),
0 violations of lemma AND bound; worst β/N^2=0.0204≈1/49. Full audit
`gpt_pro_consultations/Q5_a7_subbound_ANSWER_AND_AUDIT_2026-06-20.md`.
**Use:** EXACTLY closes the C5-free half of the stability dichotomy (no BCL) and proves
the C5-stability entry point (counterexample ⟹ induced C5 exists). Remaining gap to
the full conjecture: leverage the induced C5 (ideally a 2-dominating one ⟹ MC3).
**COLD-REVIEWED FROM DEFINITIONS 2026-06-20 (Step-2):** the optimization is sound —
`β ≤ e/2 − (1/2N)Σd² ≤ e/2 − 2e²/N²` (Cauchy-Schwarz `Σd²≥4e²/N`); `f(e)=e/2−2e²/N²`
maximized at `e=N²/8` (within Turán `e≤N²/4`) gives `f=N²/16−N²/32=N²/32`. Load-bearing
input = the `{C3,C5}`-free MaxCut lemma `MaxCut≥e/2+Σd²/2N` (cited + 301172-graph verified).
Consequence `a₇(5n)≤25n²/32<n²` ⟹ induced C5: sound.

### RAD2 — radius-2 exact reduction (GPT Q7, Step-2 verified)
**Statement (bound):** for every triangle-free `G`, `β(G) <= e/2 − (Q−T)/(2N) − D/N`
where `Q=Σd(x)²`, `T=Σ_v e2(v)`, `D=Σ_v(MaxCut(H_v)−S_v)` (H_v=radius-2 ball, S_v=Σ_{u∈N(v)}d(u)).
**Status: PROVED + INDEPENDENTLY VERIFIED.** 0 violations all tri-free N=8,9,10;
EXACTLY TIGHT at C5[2],C5[3] (D=0). Hence **`a(5n)<=n²` ⟸ `Q−T+2D >= Ne−2N³/25`**
(C5-free specialisation T=D=0 recovers A7's `β<=N²/32`).
**★ SHARPENING (Step-2, 2026-06-20): the reduction target is VERIFIED-TRUE and TIGHT.**
The full corrected `RHS2 = e/2 − (Q−T)/2N − D/N` satisfies **`RHS2 <= N²/25` for ALL
triangle-free graphs** (0 overshoots N=8,9,10; N=11,12 running), with EQUALITY ONLY at
`C5[n]` (N=10: unique tight graph = C5[2]). The D-correction EXACTLY removes the ~3%
overshoots of the `D=0` version. So `Q−T+2D >= Ne−2N³/25` is a TRUE, single-inequality,
C5[n]-tight reformulation of the WHOLE conjecture (β <= RHS2 <= n²) — a faithful provable
target, NOT a false one. Proving it = structurally lower-bounding `D` (the realignment
surplus). This is the cleanest open formulation; GPT's δ₂ question (low-codeg ⟹ large D)
attacks exactly this.
**Local-ball identity (Step-2, clean):** `Δ_v = MaxCut(H_v)−S_v = t_v − β(H_v)` (since
`e(H_v)=S_v+t_v`), so `D = T − Σ_v β(H_v)`. The target `Q−T+2D >= Ne−2N³/25` becomes
**`Σ_v β(H_v) <= (Q+T−Ne)/2 + N³/25`** — a sum of LOCAL radius-2-ball non-bipartiteness
values, tight at C5[n] (both sides `=5n³`; each `β(H_v)=n²`). So the whole conjecture
reduces to bounding the total local non-bipartiteness of the radius-2 balls.
**Outcome: does NOT prove the conjecture.** Tractable scalar relaxations cap at
`β<=N²/16` (support+deg²) and `β<=N²/17.2` (Bernoulli/Φ_v correction) — both WEAKER
than BCL 1/23.5. The essential term is `D`=local-MaxCut surplus = cut-REALIGNMENT;
circular on diameter-2/dense graphs (on C5[n], H_v=G so the local bound IS global), and
the noncircular `Φ_v` relaxation is Clebsch-obstructed (11/256>1/23.5). Same wall as all
routes. `gpt_pro_consultations/Q7_radius2_extension_ANSWER_AND_AUDIT_2026-06-20.md`.
**Do NOT pursue radius-2 scalar relaxations further; progress needs structural control of D.**

### WYZ-CODEG — low-codegree extraction (general-n lift of Codex V10)
**Statement:** tri-free `G` on `5n`, `β>=n²+1` ⟹ ∃ nonedge of codegree `<=⌊5n/8⌋`.
**Status: FINITE-VERIFIED (2026-06-20, workflow wf_ddf2cb3e-f25).** WYZ
arXiv:2408.05547 (Wang–Yang–Zhao, "Triangle-free Graphs with Large Minimum Common
Degree") CONFIRMED real + **FINITE/EXACT** (3 independent fetches): Thm 1.4(ii)
tri-free `G` on `N`, `δ₂(G)>⌊N/8⌋`, `N>=8` ⟹ hom-to-C5; `δ₂`=min codegree over
NON-EDGES = our frozen-pair codegree; NO asymptotic qualifier (unlike BCL /
Letzter–Snyder / Ebsen–Schacht, all confirmed asymptotic-only). With C5HOM gives a
finite chain `δ₂>⌊N/8⌋ ⟹ hom-C5 ⟹ β<=n²`. SHARP at the Möbius-ladder (Wagner) blow-up
(`δ₂=N/8`, not hom-C5, β=0.78n²<n² — does NOT violate the conjecture). So codegree
can't bridge `N/8→N/5` alone.
**★ δ₂-DICHOTOMY REFUTED (GPT Q8, Step-2 audited 2026-06-20).** The split
"`δ₂>⌊5n/8⌋` [WYZ] vs `δ₂<=⌊5n/8⌋`" gives NO traction: (i) `δ₂>=1` ⟹ diameter<=2 ⟹
`H_v=G` ∀v ⟹ the radius-2 criterion `Q−T+2D>=Ne−2N³/25` reduces IDENTICALLY to
`β<=N²/25` (circular); (ii) `δ₂<=⌊N/8⌋` is EQUIVALENT to the full problem — blowup
`β(F[k])=k²β(F)` + `5K₁` padding gives `δ₂=0` and `β=k²β(F)`, so a low-codegree theorem
⟹ `β<=n²` for ALL `F`. Also "low δ₂ ⟹ large D" is FALSE: `Δ_v<=e₂(v)` (sparse ball ⟹
small D). δ₂ alone is insufficient. `gpt_pro_consultations/Q8_*`. **Do NOT pursue the
δ₂ split.** Next direction: a robust AGGREGATE statement (`Θ(N²)` coherent deficient
pairs → `Θ(N³)` realignment gain) OR localise exceptional pairs to a removable set
leaving a C5-homomorphic core + a sharp extension inequality. `H2_ATTACK_FINDINGS.md`.

### CUT3 — three-cut bound from a nonedge  [PROVED + verified]
**Statement:** for any tri-free `G` and nonedge `uv`, with `C=N(u)∩N(v)`, `A=N(u)∖C`,
`B=N(v)∖C`, `R=V∖({u,v}∪C∪A∪B)`, `t=|C|`, `p=e(A,B)`, `q=e(R)`, `x=e(A,R)`, `y=e(B,R)`:
`β(G) <= min{ p+q, t+q+x, t+q+y }`.
**Status: PROVED (3 explicit shores: `A∪B∪C`, `{v}∪A∪R`, `{u}∪B∪R`) + INDEPENDENTLY
VERIFIED** (0 violations, all tri-free graphs N=6..9, 69940 nonedge-checks). GPT Q8.
**COLD-REVIEWED FROM DEFINITIONS 2026-06-20 (Step-2):** re-derived all 3 shores; load-
bearing fact = triangle-free ⟹ N(u),N(v) independent ⟹ e(A)=e(B)=e(C)=e(A,C)=e(B,C)=0.
Shore A∪B∪C: only e(A,B)=p + e(R)=q mono (u,v have no R-nbrs, uv nonedge). Shore {v,A,R}:
side1 mono x+q, side2 {u,C,B} mono = u–C = t (C∪B indep, u∉N(B)) ⟹ t+q+x; symmetric ⟹
t+q+y. SOUND, no overclaim.
**Use:** minimal-counterexample constraint (a `β>=n²+1` graph has all three `>n²`);
limitation: `q=e(R)` can absorb the whole hard core (isolated-pair ⟹ only `β<=e(R)`).
**Companion ONE-ROOT bound (GPT Q8 formula 7, Step-2 VERIFIED):** for each `v`,
`M_v=V∖({v}∪N(v))`, `R_v=max_{Y⊆M_v}[Σ_{y∈Y}(d(y)−2codeg(v,y))−2e(Y)]`; then
`β(G) <= e − max_v(S_v+R_v)` (shore `N(v)∪Y`). 0 violations all tri-free N=6..9 (3190
checks). Scalar averaging of it gives the `1/17.2` bound (the cap, per Q8).

### PAIR-FLIP-DECOUPLE / BU3-GAP / C5N-NO-CODEG0  (proved sub-lemmas)
**Status: PROVED (workflow wf_ddf2cb3e-f25; correct-direction, none close H2):**
- PAIR-FLIP DECOUPLING: for a codeg-0 nonedge `uv`, the pair-flip cut-change equals
  `(m(u)−x(u))+(m(v)−x(v))` (cross-edges N(u)→N(v) contribute NOTHING) — so STRICT-FLIP
  captures all flip info and the merge-triangle is invisible to MaxCut (explains the wall).
- BU3 EXACT-GAP (finite): within the blow-up family any imbalance costs gap `>=n`;
  cheapest perturbation `(n+1,n-1,n,n,n)` gives β=n²−n. Resolves the "balancing half".
- C5[n] has NO codeg-0 nonedge (every nonedge codeg `>=n`), so it is vacuously
  merge-terminal — the MERGE route is orthogonal to the extremal graph.
- UNIQUENESS at extremum (verified n=2,3 exhaustively): tri-free on 5n with `β=n²`
  is EXACTLY `C5[n]` (the unique maximiser). **CORRECTION:** the workflow's stronger
  phrasing "`β>=n²−(n-1)` ⟹ C5[n]" is FALSE (n=2: 25 tri-free 10-vtx graphs have
  β=3=n²−(n-1) but are NOT C5[2]); only the `β=n²` uniqueness holds. This uniqueness
  does NOT by itself give `a(5n)<=n²` (it presupposes β=n²; ruling out β>=n²+1 is the
  conjecture). The "near-extremal ⟹ O(edits)-from-C5[n]" stability (S1a) that WOULD
  help is regularity-walled (asymptotic-only). REFUTED this round: induced-C5-peel formula
  (`pc<=Σmin+e(S)−4` false; counterexample pc=23>19 at n=10); two-distribution averaging
  (provably saturated at 2n-1 with zero slack on C5[n]); merge-iteration (chains cap at
  length 4<5, needs circular a(5n-1)<n²).
