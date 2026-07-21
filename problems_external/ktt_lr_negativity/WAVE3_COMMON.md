# WAVE-3 COMMON PROTOCOL (RUN-TOKEN R3) — read before executing any wave-3 family

Applies to all 14 wave-3 hunters. Family specs give only what is family-specific.

## 0. Non-negotiables

- ALL mathematical decisions in exact integers / `fractions.Fraction`. Floats may
  be used ONLY inside the LP triage oracle (see §3) to choose which basis to
  solve exactly; every keep is re-derived exactly. No float ever decides a verdict.
- Engine A `engine/lr_hive.exe`, engine B `engine/engineB_lrrule.py`,
  interpolation `engine/interp.py` (has `--selftest`). Before hunting, run the
  sanity gate: c=1 triple must stretch to P≡1 (KTW), c=2 to P(n)=n+1
  (Ikenmeyer/Sherman), engines A and B must agree. Abort on disagreement.
- Degree bound D = (r-1)(r-2)/2 with r = #parts(nu). Nodes n = 0..D (P(0)=1),
  exact Newton interpolation, then MANDATORY held-out check at n = D+1 and D+2.
  Mismatch = DEGREE_ANOMALY: log it, never promote it.
- A HIT is one strictly negative monomial coefficient. On a hit: stop the family,
  recompute the entire sample table with BOTH engines, re-interpolate
  independently, write the certificate, notify. No hit is claimed from the LP
  oracle or from an h*-flag alone.

## 1. Caps — the wave-2 cap story was wrong, fix it

Wave-3 value cap is **4000000** (was 200000). But measured on this machine:
the binding limit is NOT the value cap, it is engine A's DFS **node** cap
(`LR_HIVE_NODE_CAP`, default 2e8 ≈ 2.0 s). Thin (= interesting) polytopes burn
~1e8 nodes/s and hit it long before the value cap.

**Every wave-3 hunter must export `LR_HIVE_NODE_CAP=20000000000` (2e10)** and
add its own wall-clock timeout per sample (suggest 240 s). Measured example:
lam=mu=(6,5,4,3,2,1), nu=(11,9,8,7,5,2) (c=12, deg 6) returned CAP_EXCEEDED at
n=10,11,12 under the default node cap and returns 71214 / 116480 / 183547 in
4.4 / 9.8 / 20.9 s under the raised one. Wave-2's "fat skips" in the c=11..12
band were mostly this artifact, not fat triples.

Distinguishing the two skip reasons: re-run the same sample with cap `10**18`.
Still CAP_EXCEEDED ⇒ node/time limit (THINSKIP, interesting); a number ⇒ it was
the value cap (FATSKIP, discard).

Cost model to plan with: ~1e8 DFS nodes/s; a genuine r=6 dim-10 profile
(n = 0..12, P(12) ≈ 6·10^5) costs roughly 3–6 min single-threaded. With 6
threads and 60–75 min, **budget 60–120 deep profiles per hunter**. Deep and few
beats wide and shallow this wave.

## 2. The two mathematically distinct routes (why wave 1–2 found nothing)

For a d-dimensional LATTICE polytope, P(n) = Σ_j h*_j C(n+d-j, d) with
h*_0 = 1 and all h*_j ≥ 0 integers (Stanley), and its d+1 affinely independent
vertices are lattice points, so

        c = P(1) = (d+1) + h*_1  ≥  d+1 = deg P + 1.

Waves 1–2 verified `deg ≤ c-1` on 118,639 polynomials with zero exceptions and
never saw a negative h*_j. Consequences you must design around:

- **Route A (lattice, heavy late h*).** With h* ≥ 0 a negative monomial
  coefficient needs large mass at middle/late j. Exactly:
  a_1 = H_d + Σ_{j≥1} h*_j (-1)^{j-1} (d-j)!(j-1)!/d!, and the j and d+1-j
  weights have equal magnitude and opposite sign, so h*_1 and h*_d cancel.
  At d = 6 with h*-support ⊆ {0,..,3} this needs Σh* ≥ 37 (wave-2 result);
  wave-2's observed ceiling was Σh* ≈ 20 at c = 12. Route A therefore needs
  **larger c than wave 1–2 allowed** — the c ≤ 12 bias was a wave-1 heuristic,
  not a theorem. Wave-3 families may go to c ≤ 24 (at d = 10 the value cap
  4e6 permits h*_1 ≤ 9, i.e. c ≤ 20, at n = 12).
- **Route B (non-lattice).** If Q has a fractional vertex, Stanley gives zero
  protection: hive polytopes always have a genuine POLYNOMIAL Ehrhart counting
  function (Derksen–Weyman), so a non-integral hive polytope is automatically a
  period-collapse polytope à la Haase–McAllister, where h*_j < 0 is allowed.
  **`c ≤ deg P` (⇔ h*_1 < 0) is a proof of non-integrality** and is the single
  cheapest jackpot flag in the campaign. It has never been observed. Get it.

## 3. The wave-3 triage oracle: `engine/hive_poly.py` (new, self-tested)

`python engine/hive_poly.py --selftest` must print `SELFTEST PASS` (exit 0)
before use. It was validated against engine A on four triples including
lam=mu=(6,5,4,3,2,1), nu=(11,9,8,7,5,2) where it returns dim 6, matching the
exactly interpolated deg P = 6.

- `analyze(lam, mu, nu, K, seed)` → `{d, dim_lo, dim_hi, maxden, nverts}`.
  It builds the exact rhombus system (same convention as `BUILD_A.md`), samples
  K vertices by random linear objectives (float LP picks the basis; the vertex
  is then solved and verified EXACTLY over Fractions), and returns
  * `dim_lo` = affine rank of certified vertices — a rigorous LOWER bound on
    dim Q = deg P,
  * `dim_hi` = heuristic upper bound (constraints tight at all sampled vertices),
  * `maxden` = largest denominator seen in a certified vertex. `maxden ≥ 2` is a
    rigorous certificate that Q is **not** a lattice polytope.
  Cost ≈ 0.4 s (r=5) / 1.2 s (r=6) / 3–5 s (r=7) per triple at K = 18–25.
  Treat `dim_lo == dim_hi` as "dim known" for triage.
- `hstar_prefix(d, [P(0),...,P(m)])` → exact h*_0..h*_m via
  h*_j = Σ_{i≤j} (-1)^i C(d+1,i) P(j-i). **This is the wave-3 force multiplier:**
  with d supplied by the oracle, h*_0..h*_4 come from the CHEAP samples n ≤ 4,
  so a full negativity screen costs ~2 s instead of ~5 min. Validated:
  d=6, P = 1,12,74,304 → h* = 1,5,11,3 (matches exact interpolation).

Standing rule: the LP oracle and the h*-prefix are TRIAGE ONLY. Any flag
(`maxden ≥ 3`, `c ≤ dim_lo`, `h*_j < 0`, `dim_lo ≥ 9`) must be escalated to the
full exact protocol of §0 before it means anything.

## 3b. Measured wave-3 calibration (run 2026-07-21 on this machine, seed 31)

20,000 random r=6 triples (lam, mu distinct 6-part, |lam|,|mu| in [21,30], nu a
random 6-part partition of the sum):

- engine-A batch screen at n=1 **with value cap 25** : 0.24 s for all 20,000.
  Screen with a SMALL cap (25–30), never with 4e6 — a fat triple costs ~2 s at a
  big cap and nothing at a small one. The big cap belongs in the profile stage.
- 1,912 / 20,000 had 0 < c <= 25; 885 had c in [8,25].
- `hive_poly.analyze` at K=18: **0.49 s per r=6 triple**.
- dim_lo histogram over 308 analysed c-in-[8,25] triples:
  3:1, 4:6, 5:79, 6:105, 7:45, 8:44, **9:24, 10:4** — i.e. ~9% of the c-band
  reaches the mandated dim>=9 stratum, ~0.4% of raw draws. Finding dim-9/10
  triples is NOT the bottleneck any more; deep profiling is.
- maxden histogram: 1:255, **2:53** (17% already non-integral vertices), 3+: none
  seen in 308.
- best `c - dim_lo` seen in this unbiased sample: **+1**
  (c=8, dim 7, lam=(8,5,4,3,2,1), mu=(12,6,4,3,2,1), nu=(14,13,7,7,7,3)).
  Zero or negative is the jackpot; the unbiased base rate is already one step away.

## 4. Universal flags to log per triple (one JSONL record each)

`c`, `d` (ambient), `dim_lo`, `dim_hi`, `maxden`, `c - dim_lo`, the h*-prefix,
and for profiled triples the exact coefficient vector, the full h*, Σh*
(= normalized volume), ρ = Σh*/c, and `minhstar = min_j h*_j`.

Ranked promotion ladder (report anything at level ≥ 3 immediately):
1. `dim_lo ≥ 9` at r=6 (the mandated virgin stratum) — profile it.
2. `maxden ≥ 3`, or Σh*/c ≥ 3 — orbit-mine it.
3. `min_j h*_j < 0`, or `c ≤ dim_lo` — **stop the family, verify exhaustively**.
4. a strictly negative monomial coefficient — HIT: §0 hit protocol.

## 5. Staged verification (throughput amendment, R3)

For r=6 the two held-out points n = 11, 12 dominate cost. Permitted staging:
take nodes n = 0..10 always; take n = 11, 12 for (a) every triple whose
coefficient vector has any non-positive entry, (b) every triple with
observed degree ≥ 9, (c) every triple with any h*_j < 0, and (d) a random 10%
audit sample. Everything promoted or reported as a hit gets the full n = 0..12
plus the §0 dual-engine recomputation, without exception.

## 6. Artifacts

Run dir `problems_external/ktt_lr_negativity/runs/wave3_<family>/` with
`manifest.json` (spec text, seeds, engine sha256s, caps, counts),
append-only `results.jsonl`, `near_miss.jsonl`, and the driver script.
Report NO_HIT honestly with exact counts; absence of a hit is never evidence
for the conjecture.
