# audit_P1 — adversarial audit of `round6/P1.md`

Auditor, round 6, 2026-07-25.  Independent re-implementation in `round6/audit_P1_*.py`
(own data structures: integer positions `k/q` so the far-test is the pure-integer
`3*min(dk,q-dk) > q`; cuts as bitmasks; monochromatic mass recomputed from the edge list every
time — no incremental update; `psi` = brute force over all `2^(n-1)` bitmasks; `ARCBOUND` by two
independent arc enumerations; pentagonality enumerated over 5-tuples of cut points **with
repetition**, i.e. empty blocks allowed; plus an independent hom-to-`C5` backtracking test).
All acceptance paths exact (`Fraction` / `int`).

Files: `audit_P1_engine.py`, `audit_P1_item7.py`, `audit_P1_claims.py` (+`.log`),
`audit_P1_extra.py` (+`.log`), `audit_P1_atilde_fix.py` (+`.log`),
`audit_rerun_frontier.log`, `audit_rerun_atilde.log`.

---

## Verdicts, most consequential first

### 1. "ITEM 7 IS FALSE" — **CONFIRMED** (and strengthened)

Reproduced from scratch for `mu = 1/8` on `{0,1,6,7,12,13,14,19}/20`:

| quantity | exact | hypothesis of item 7 |
|---|---|---|
| `W` | `3/16 = 0.1875` | in `(0.12,0.2)` ✔ |
| `2T` | `9/64 = 0.140625` | `< W-1/25 = 59/400 = 0.1475` ✔ |
| `Var(g)` | `0` (far-graph 3-regular, `g ≡ 3/8`) | — |
| `4W^2+Var(g)` | `9/64` | `< 59/400` ✔ |
| `bound_k`, `k = 0..300` | `3/64 = 0.046875` | must be `<= 1/25` ✘ |
| `min_b m(b)`, `1/E[1/m]`, `A`, `B` | `3/64` | all ✘ |
| `ARCBOUND`, `psi` | `1/32 = 0.03125` | conjecture safe ✔ |

* far-graph verified isomorphic to the Wagner graph `V8 = C8(1,4)` by explicit permutation search.
* `B` recomputed over **both** endpoint families of closed `1/3`-arcs (P1's own code only slides
  the left endpoint over atoms — see defect D3): still `3/64`.
* `ARCBOUND` agrees under two enumerations; optimal arc = atoms `{0,1,6,7}`, span `7/20`.
* no pairwise distance equals `1/3` (positions live on the `1/20` grid), so no
  strict/non-strict convention issue; the three hypotheses are strict with slack `>= 0.0069`,
  so this is an open region, as claimed.

**Strengthening (my own exhaustive search, `audit_P1_item7.py`):** over all uniform-weight
measures on subsets `S ⊂ Z_q`, `q <= 22`, `|S| <= 10`, rotation fixed, with integer-exact
filters (flat far-graph, `25|E| > 3n^2`, `5|E| < n^2`, `50*sum k_e < 25q|E| - qn^2`):
**88 counterexamples to item 7**, none of which threatens Erdős 23 (`psi <= 1/25` in all 88).
The smallest circle is `q = 14`, `S = {0,1,2,5,6,7,10,11}` (again `V8`, `W = 3/16`,
`bound_k = 3/64`, `2T = 33/224` with slack only `1/5600`).  P1's `q = 20` representative is the
better-conditioned member of the family.

Consequence beyond P1's own framing: the same witness also refutes the **root agent's R5-K18
two-term form** `min(W-2T, H) <= 1/25` (`H` = harmonic mean of `m`), recorded in `PROGRESS.md`
with "0 violations in 3606 exact tests" — both terms equal `3/64` here.

### 2. `psi` of the witness / "the conjecture is untouched" — **CONFIRMED, with a caveat P1 omits**

`psi = 1/32` at that weighting (full `2^7` enumeration).  But `V8` contains the **induced** `C5`
`{0,1,7,12,14}`, so `max_x psi(V8) = 1/25` exactly, attained only at the degenerate corner
(exhaustive integer weightings with all weights positive: max `13/400 = 0.0325` at denominator
20 and `8/225 = 0.03556` at denominator 30).  So the graph carrying the item-7 witness is an
equality case of Erdős 23 in the limit; P1's §6 `eps`-family is exactly that corner being
approached.  No error, but the report's "psi = 1/32" should not be read as a maximum.

### 3. §9 row "non-pentagonal ⟹ `Atilde <= 1/25` is refuted" — **witness REFUTED, claim survives via a different witness**

P1's quoted falsifier (`q = 26`, support `{0,1,11,12,13,14,15,16,24,25}`, `Atilde = 0.0814`)
**is pentagonal**: my enumeration finds a 5-block decomposition with two empty blocks,
`q = (9097/33333, 0, 6324/11111, 0, 5264/33333)`, and the support is hom-to-`C5`
(`ARCBOUND = psi = 0`).  It therefore does not satisfy the hypothesis, and P1's stated
refutation of its own candidate (Q) is invalid.

Cause = defect **D1** below.  Because P1 states that (P)+(Q) *would close the arc-cut
conjecture*, this bug retired a live route on false evidence.  I re-ran the search with the
corrected pentagonality test (`audit_P1_atilde_fix.py`, 172 genuinely non-pentagonal supports
hill-climbed, exact acceptance): (Q) **is** false, but the honest witness is
`q = 20`, support `{1,2,4,8,9,11,12,14,15,16}`, `Atilde = 0.073911 > 1/25` (with
`ARCBOUND = 3.2e-4`).  Also checked: on the `eps`-degeneration family (genuinely
non-pentagonal) `Atilde` stays below `1/25` (`0.03999992` at `eps = 1e-6`), so that family is
not a falsifier of (Q).

### 4. §6(ii) "robustly non-pentagonal … empirically bounded by 0.0372 < 1/25, i.e. with real slack" — **REFUTED**

The weight floor P1 uses, `x_i >= 1/(3n)`, is `n`-dependent, so it cannot bound the class away
from `1/25`; the reported `0.037150` is an artefact of the search range (`n <= 10`, `q <= 24`).

Explicit falsifier family (`audit_P1_claims.py` §(f), exact): blow the five `C5`-atoms of `V8`
into clusters of `c` consecutive atoms on `Gamma_{20M}` and keep the three
pentagonality-breaking atoms as singletons of weight exactly the floor `1/(3n)`.  Every weight
is `>= 1/(3n)`; the support contains `V8` as an induced subgraph, and `V8` has no homomorphism
to `C5`, hence the support is non-pentagonal.

| `q` | `c` | `n` | floor | `ARCBOUND` |
|---|---|---|---|---|
| 200 | 2 | 13 | 1/39 | 0.034740 |
| 200 | 3 | 18 | 1/54 | 0.036022 |
| 600 | 6 | 33 | 1/99 | **0.037715** |
| 600 | 10 | 53 | 1/159 | **0.038544** |

and the family tends to `1/25`.  So P1's proposed split of the residual problem into
"(i) degenerating-to-pentagonal + (ii) robust case with genuine slack" is wrong: **there is no
slack half**; case (ii) as defined is again a degeneration problem.

### 5. §5 statement about the "recorded hard cases" — **two FALSE claims**

* "R1 and R2 — the two cases … the ones where `A`, `bound_0` and even `bound_1` fail — are
  pentagonal, hence now proved."  **False for R2.**  Exact: `bound_0(R2) = 781/19683 =
  0.0396787…  <= 1/25` and `bound_1(R2) = 0.039227 <= 1/25`.  (The chain text supplied to the
  agent says the same: "bound_0 gives 0.039679".)  Only R1 is in the failure region
  (`A = 0.041522`, `b0 = 0.041980`, `b1 = 0.040751`, `b2 = 0.039664`, closed at `k = 2`).
* "it settles cases with `W > 1/5` (W7 has `W = 0.21`), which the `bound_0` argument cannot
  touch."  **False.**  `bound_0(W7) = 3/100 = 0.03 <= 1/25`; even the crude Cauchy–Schwarz form
  `W - 4W^2 = 0.0336 <= 1/25`; chain item 7 explicitly says `bound_0` settles `W >= 1/5`.

### 6. Theorem 3 (PENTAGON LEMMA) — mathematics **CONFIRMED**, novelty **REFUTED**

Proof re-derived and checked; it is tight where it must be: `C5` and its balanced `2x`, `3x`
blow-ups give pentagon bound `= ARCBOUND = 1/25` exactly.  The equality analysis is correct.
On the 9 pentagonal test measures the bound equals `ARCBOUND` exactly, as claimed.

But the claim that this "settles the conjecture … for the whole pentagonal class" is void as a
contribution to Erdős 23, and the presentation as a new theorem is wrong:

* **The class is exactly the trivially-settled one.**  Over 36 609 circle supports (`q <= 16`,
  `|S| <= 8`) "pentagonal" and "admits a homomorphism to `C5`" agree with **zero** mismatches
  (`audit_P1_extra.py`).  For any `H -> C5` one pulls a cut back along the homomorphism and gets
  `psi(H,x) <= psi(C5, f_*x) <= 1/25` for every `x` — the classical blow-up argument.  The only
  content beyond that is that the certifying cut can be taken to be an **arc**.
* **It duplicates round 5.**  `round5/R5K19_PENTAGRAM_LEMMA.md` (root agent, same session)
  already proves the same statement by the same "AM–GM twice" mechanism for pentagram-position
  supports, and says explicitly that it is the classical `C5`-colourable argument.  P1's version
  generalises it (incomplete joins, empty blocks) but never cites it, and the two measures P1
  says are "now proved" (R1, R2) are exact pentagram configurations — their pentagon bound equals
  `min_i q_{i+2} q_{i+4}` — hence were already covered there.
* **It covers nothing in the family the chain reduces to.**  For `And(k) = Gamma_{3k-1}`,
  `k = 3..7`, the uniform measure is non-pentagonal and not hom-to-`C5` (verified); only
  `And(2) = C5` is pentagonal.  The residual class therefore still contains every Andrasfai
  graph — i.e. exactly what chain item 2 reduces the conjecture to.

### 7. Theorem 1 (`sigma`-family) — **CONFIRMED**

The probability computation is right (`t` and `t+1/2` land in an interval of length `D <= 1/2`
disjointly; the symmetric difference of two half-circles offset by `D` has measure `2D`), and
the atomic case `sigma = mu` is a legitimate limit of non-atomic `sigma` under **symmetric**
smearing, which is exactly P1's gap vector `s_i = (x_i+x_{i+1})/2`.  Stress test: 5 200 random
exact rational `sigma` on 13 measures, **0** values below `ARCBOUND`.

### 8. Theorem 2 (`inf_sigma A_sigma = ARCBOUND`) — **CONFIRMED**

The spike construction is correct and I reproduced it exactly: putting `sigma`-mass `1/2` at
each of the two boundary gaps of a chosen arc returns that arc's cut value exactly (3/3 arcs
tested on the witness).  P1's own conclusion — "reformulation, not a reduction, do not spend a
round on it" — is right and is the responsible call.

### 9. §3 "the arc length cannot be fixed" (`V(l)` monotone) — **CONFIRMED**

Independently re-derived: for `l <= 1/2` the separation probability of an edge of length `d` is
`2l - 2(l-d)_+`, so `V(l) = W(1-2l) + 2 sum_e w_e (l-d_e)_+` and
`V'(l) = -2W + 2 mu_pair([1/3,l)) <= 0`; `V(1/2) = W - 2T = A`.  P1's script also checks the
closed form against a direct exact integration at 7 lengths on 4 measures.

### 10. §2.3 "why more levels cannot help" — **UNSUPPORTED as stated** (harmless)

`sd(m) <= (1+2W) sd(g)` and `|bound_1 - bound_0| <= (1+2W)Var(g)/(2W)` are correct, but at
`W = 3/16` this permits a move of `3.67*Var(g) <= 0.0253` while the gap to close is only
`bound_0 - 1/25 <= 0.0069 - Var(g)`; the estimate therefore does **not** rule level 1 out
(it fails to for any `Var(g) >= 0.0015`).  The heading overclaims; the refutation itself rests
on the explicit `Var(g) = 0` witness and stands.

### 11. Mandatory regression (`round5/claude_witness_regression.py`) — **RUN, results below**

P1's own scripts do re-run the nine witnesses (its `WITNESSES` list matches round 5 verbatim)
with asserts that no bound drops below `ARCBOUND`.  Independently, through the round-5 harness:

| rule | result on the nine |
|---|---|
| pentagon lemma (Thm 3) | valid and `<= 1/25` on the 7 it applies to; **no bound at all** on W3 (`Gamma_18` uniform) and W4 (`Gamma_20` uniform) — non-pentagonal |
| `A_mu` (`sigma = mu`) | fails W7 (`23/500 = 0.046`) — matches P1's §9 |
| `A_Leb` (`= A = W-2T`) | fails W1, W1', W1'', W7 — the known half-arc failure |
| `min(A,B)` | passes all nine; refuted only by P1's new `V8` witness |

So the one rule P1 offers as *proved* (Theorem 3) is silent on 2 of the 9 regression witnesses,
and `min(A,B)` shows P1 correctly went beyond the regression set to kill its own conjecture.

### 12. Other checks demanded by the protocol

* floating point on an acceptance path: **none found**.  The LP in `P1_sigma.best_sigma` and the
  SLSQP/hill-climbs in `P1_frontier.py`, `P1_atilde.py` are search only; every quoted value is
  re-evaluated exactly at a rationalised point, and the asserts are exact.
* `psi < 1/25` reported as a maximum for an odd-girth-5 graph: **not done** (see verdict 2).
* integer enumeration excluding zero weights: P1's floor searches exclude them by design and say
  so; the inference drawn from that exclusion is nevertheless wrong (verdict 4).
* claimed exhaustive range not covered by the loop bounds: **yes** — defect D1 below.
* circularity: none found; `ARCBOUND` is always the brute-force ground truth and every proposed
  bound is asserted `>= ARCBOUND`.
* quoted theorem whose hypotheses do not match its use: **yes** — §9's `Atilde` row (verdict 3);
  and the two §5 claims (verdict 5).
* tight at the `C5` extremal: Theorem 3 is (`= 1/25` exactly on `C5` and its balanced blow-ups).

---

## Code defects found

* **D1 (consequential).** `P1_pentagon.pentagon_bound` enumerates `combinations(range(n), 5)` —
  five **distinct** cut points — so it never sees a 5-block decomposition with an **empty**
  block, although the lemma explicitly allows them.  Measured against my enumeration over
  6 666 uniform circle supports (`q <= 13`, `|S| <= 8`): **2 370 false "not pentagonal"**
  verdicts, at every support size (`n=4`: 450, `n=5`: 800, `n=6`: 681, `n=7`: 343, `n=8`: 96).
  First example `q = 7`, `S = {0,1,2,3,4}`.  Consequences: the §9 `Atilde` row is invalid
  (verdict 3); the "robustly non-pentagonal" search filters are wrong in principle (its four top
  supports happen to be genuinely non-pentagonal — I re-checked all four).  The verdicts on the
  13 headline measures are unaffected (my independent test and the hom-to-`C5` test agree with
  P1 on all 13).
* **D2.** `P1_engine.best_window` / `P1_refutation`'s `B` maximise `nu` only over closed
  `1/3`-arcs whose **left** endpoint is an atom.  The sliding-window mass is a sum of indicators
  of closed intervals in the start coordinate, so the maximum can also be attained at a window
  whose **right** endpoint is an atom.  `B` can therefore be over-reported (making "B fails"
  claims too easy).  On the item-7 witness both families give `3/64`, so nothing in the report
  changes.
* **D3 (cosmetic).** `P1_pentagon.py`'s last test row is labelled "C5 blow-up 5x2 (G10 pairs)"
  but that measure's far-graph is a 5-edge path (`ARCBOUND = 0`), not a `C5` blow-up.  It does
  not enter `P1.md`.

---

## Net assessment

The headline is right and is the important result of the round: **item 7 is false**, by an exact,
perturbation-stable, independently reproduced witness — in fact by an 88-member family of them —
and it takes the root agent's R5-K18 two-term form down with it.  Everything the report proves
(Theorems 1, 2, the `V(l)` monotonicity, the flat-collapse proposition, the pentagon lemma with
its equality case) is correct as mathematics.

What does not survive audit is the *value* assigned to the replacement: the pentagon lemma is
the classical `C5`-homomorphism case in circle language (already recorded in round 5 as R5-K19),
it covers no Andrasfai graph, and the two "hard cases" it is said to newly settle were already
closed — R2 by `bound_0` outright.  The residual frontier is therefore not "sharply smaller":
it is the whole target family, and the report's claim that half of it has "real slack" is
refuted by an explicit floor-respecting family reaching `0.038544` and tending to `1/25`.
