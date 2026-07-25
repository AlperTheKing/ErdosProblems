# AUDIT of round6/P2.md — adversarial review

**Bottom line: P2's headline result survives a hostile audit intact.** The criterion of item 7 is
FALSE, `sup_mu CRIT = 1/18`, and every number in §§1–6 and §7(d) reproduces *exactly* under an
independently written implementation. The whole 673 525 748-leaf sweep replicates to the leaf,
including the count 1 790 and the maximum `3/64`. Nothing in the report touches the arc-cut
conjecture or Erdős 23, exactly as it claims.

**What does not survive: §9 (the "repair direction") and the §7(a) table.** Both of §9's diagnostic
claims about *which* cut the criterion misses are false, and one of them proposes a selection rule
that the mandatory 9-witness regression kills outright — a rule P2 never ran against the regression
set. §7(a)'s numbers are `k <= 10`-truncated floats, not `CRIT` values, and its `n = 4` entry
exceeds a supremum P2 itself proves two sections earlier.

Audit code (independent data structures, own max-cut, own weight enumerator, integer-only
acceptance paths): `audit_P2_core.py`, `audit_P2_witness.py`, `audit_P2_extra.py`,
`audit_P2_sweep.cpp`, `audit_P2_falsifiers.py`, `audit_P2_final.py`; logs `audit_*.log`,
`audit_sweep_full.log`, `audit_sweep_falsifiers.txt`.

---

## Verdicts, most consequential first

### 1. "The criterion of item 7 is FALSE" — **CONFIRMED** (independently, four ways)

Item 7 asks: `W in (0.12,0.2)`, `2T < W - 1/25`, `4W^2 + Var(g) < W - 1/25` ⟹ some `bound_k <= 1/25`.
My own code (positions/weights as integers over `(M,Q)`, adjacency `3d > M`, `mono` over unordered
adjacent pairs, `m(b)` recomputed **as the monochromatic mass of the vertex set `N(b)` from
scratch**, never from item 4's formula) reproduces every witness to the last digit:

| witness | `W` | `A` | every `bound_k` | all 3 hypotheses | ARCBOUND | psi |
|---|---|---|---|---|---|---|
| 4 atoms `{0,9,606,1203}/1800` uniform | `1/8` | `49/1200` | `1/16` | true | `0` | `0` |
| 4 atoms `(169,239,169,239)/816` | `42841/332928` | `2142007159/49939200000` | `>= 28561/665856` | true | `0` | `0` |
| Wagner `V8` on `Gamma_14` uniform | `3/16` | `9/224` | `3/64` | true | `1/32` | `1/32` |
| Wagner `V8` on `Gamma_29` uniform | `3/16` | `3/58` | `3/64` | true | `1/32` | `1/32` |
| `Gamma_11 (3,0,1,3,0,1,3,3,0,1,3)` | `31/162` | `4/99` | `>= 13/324` | true | `5/162` | `5/162` |
| `Gamma_17` uniform on 8 pts | `3/16` | `3/68` | `3/64` | true | `1/32` | `1/32` |

The logical step is sound: `bound_k` is a weighted average of the `m(b)`, `b in supp mu`, so
`min_b m(b) > 1/25` forces `bound_k > 1/25` **for every `k`, with no truncation** — I verified
`bound_k` out to `k = 200` on each witness, and the sweep test is the truncation-free
`25*mn_b > q^2` integer comparison. Calibration on `C5` returns exactly `1/25` for `A`, every
`bound_k`, `ARCBOUND` and `psi`.

The falsification does not depend on the continuum: the 4-atom and Wagner witnesses are finite
weightings of `Gamma_m`, i.e. precisely the objects of items 2–3. The Wagner witnesses are
non-bipartite of odd girth 5, so the failure is not a bipartite degeneracy.

### 2. §6 exhaustive sweep — **CONFIRMED, and strengthened**

I rewrote the sweep with deliberately different internals (per-vertex vectors `gn[j], tn[j]` carried
down the DFS and `W, T` rebuilt at every leaf, versus P2's two incremental scalars; exact rational
maxima by `__int128` cross-multiplication versus P2's double ranking). Same space, same `qmax`
schedule. Result (`audit_sweep_full.log`):

```
leaves      = 673525748      (P2: 673 525 748)      identical
candidates  = 4218273        (P2: 4 218 273)        identical
falsifiers  = 1790           (P2: 1 790)            identical
per-cell:  m=11 q=18:32  m=14 q=8:8,13:43,14:29  m=17 q=8:24,13:322,14:269
           m=20 q=8:56,12:3  m=23 q=8:136,11:37,12:39  m=26 q=8:256  m=28 q=8:8  m=29 q=8:528
                                                        — every cell identical to P2's log
max LO = max min(A, min_b m(b)) = 3/64      <= max CRIT
max HI = max min(A, bound_0, lim_k bound_k) = 3/64   >= max CRIT
```

P2's max was the maximum of a `k <= 8` *truncated* `CRIT` ranked in doubles, which is only an upper
bound on the true maximum. My `LO <= CRIT <= HI` sandwich closes exactly at `3/64`, so
**`max CRIT = 3/64` over the swept space is now pinned rigorously**, not merely ranked. The
canonicalisation `w_0 = max_i w_i` covers every rotation orbit and zero weights are enumerated
(`c` starts at 0 for `i >= 1`), so no family is excluded; the `W`-window pruning is safe because
`CRIT < W/3 <= 0.04` for `W <= 0.12` and `CRIT <= W - 4W^2 <= 1/25` for `W >= 0.2`.

*Two cosmetic corrections.* (a) The maximum `3/64` is **not** attained only on `Gamma_29`: my argmax
was `Gamma_20, q=8`, and `Gamma_20, 23, 26, 29` all reach `3/64`. (b) "`Gamma_11 (q >= 18)`" should
read `q = 18`: `q = 19, 20` produce no falsifiers.

### 3. Ceiling `CRIT < min(W/3, W - 4W^2) <= 1/18` and `sup = 1/18` — **CONFIRMED**

`T > W/3` because every adjacent pair has `d > 1/3`, giving `A < W/3`; Cauchy–Schwarz gives
`int g^2 >= 4W^2`, giving `bound_0 <= W - 4W^2`. The branches cross at `W = 1/6` with common value
`1/18`, and `W - 4W^2 <= 1/25` outside `[1/20, 1/5]`. No circularity, no floating point, and — the
protocol's own test — **the ceiling is tight at `C5`**: at `W = 1/5` it returns `W - 4W^2 = 1/25`,
which `C5` attains exactly. The supremum is approached, never attained (`A < W/3` is strict); P2's
phrase "attaining family" is loose but §1 says "approached", which is correct.

### 4. §2 the `1/3`-periodic family — **CONFIRMED**

Independently re-derived by hand and reproduced by discrete stand-ins (`audit_P2_witness.py` §F,
`audit_P2_extra.py` §1): for three uniform arcs of width `eta`, `g ≡ 1/3`, `W = 1/6`, `m ≡ 1/18`,
`A = (1-2eta)/18`, falsifier iff `eta < 7/50`. My three-cluster discrete measures give exactly the
values P2 lists in §7(d): `21868/421875` (45 atoms) and `33329/625000` (75 atoms), both **exact
matches**, with `min_b m(b)` and `A` converging to `1/18` from the two sides. The Fourier
cross-check is right: `psihat(3k) = 0` for even `k`, `= 1/(9 pi^2 k^2)` for odd `k`,
`1/36 + 2*(1/72) = 1/18`. The identified hole in item 6 ("a purely 3-fold measure has no adjacent
pairs") is real: that inference holds only for the 3-atom coset measure, where pairs sit at distance
exactly `1/3`.

*One overclaim:* "the criterion overshoots by a factor of **exactly** 2" needs `ARCBOUND = 1/36`
exactly; only `ARCBOUND <= 1/36` is proved (the exhibited arc). The factor is `>= 2`.

### 5. "No counterexample to the arc-cut conjecture, none to Erdős 23" — **CONFIRMED**

I computed `ARCBOUND` and `psi` exactly for **all 1 790** sweep falsifiers: max `ARCBOUND` =
max `psi` = `4/121 = 0.03306 < 1/25`, and `psi <= ARCBOUND` holds throughout. Not one exceeds
`1/25`.

*But the ranking sentence is wrong as written.* "Every witness has `ARCBOUND <= 1/32`" is true of the
witnesses displayed in the report and **false** for the falsifier population: `Gamma_23`, `q = 11`,
`w = (1,0,0,0,0,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1)` has `ARCBOUND = psi = 4/121 = 0.0330579 > 1/32`.
Harmless to the conclusion, wrong as a quantifier.

### 6. Mandatory 9-witness regression — **CONFIRMED**

My `ARCBOUND` on the nine witnesses of `round5/claude_witness_regression.py`:
`1/49, 1/49, 1/49, 1/25, 1/54, 3/100, 0, 1/49, 1/100` — nine exact agreements with round 5's own
function and with P2's quoted list. None of the nine is an item-7 falsifier (verified with all three
hypotheses), so the regression set is consistent with the record and simply misses the failure
family, as P2 says.

### 7. "This kills the Chebyshev term and the harmonic mean" — **CONFIRMED**; "any future functional
of `{m(b)}` and `A`" — **UNSUPPORTED**

`E - Var(m)/(max m - E) >= min_b m(b)` is Bhatia–Davis, and `H = 1/E[1/m] >= min_b m(b)`, so both
exceed `1/25` on every witness. Verified exactly (`audit_P2_final.py`): on `Gamma_11
(3,0,1,3,0,1,3,3,0,1,3)`, where `m` takes three values, Chebyshev `= 257/6156 = 0.041748` and
`H = 39/908 = 0.042952`, both above `1/25`; on the optimal 4-atom witness, `0.0428937` and
`0.0540975`. *Note* that on the far-regular witnesses (Wagner) the Chebyshev term is literally `0/0`
— P2 should quote a witness where the form is defined, as `Gamma_11` is.

The generalisation "**any** future functional whose only inputs are the neighbourhood-cut values and
`A`" is not established. The argument proves it only for functionals that dominate `min_b m(b)`
(averages, Chebyshev, harmonic mean). Ruling out every functional of `({m(b)}, A)` would require
exhibiting a second measure with the same inputs whose `ARCBOUND` is near `1/25`; that is not done.

### 8. §9 "the natural next reduction ... on `mu_eta` that family already gives `1/36`" — **REFUTED**

The one-parameter family of `1/3`-arcs with a free endpoint is exactly `{N(b) : b in R/Z}` (any arc
`(a, a+1/3)` is the far-arc of `a - 1/3`). On the `1/3`-periodic family every one of them has value
**exactly `1/18`**, not `1/36`. Analytically: for `b` at offset `s*eta` inside a cluster, the
complement carries `[s^2 + (1-s)^2 + 2s(1-s)]/18 = 1/18` for every `s`. Numerically
(`audit_P2_extra.py` §1), min over free-offset `1/3`-arcs `= 7/135 = 0.05185` (45 atoms) and
`4/75 = 0.05333` (75 atoms), rising to `1/18`, while `ARCBOUND` is `49/2025` and `16/625`, falling
to `1/36`. The proposed rule does not merely fail to give `1/36` — it gives twice it.

**Worse, the rule dies on the mandatory regression set, which P2 never ran it against**: on `W3`
(uniform `Gamma_18`) the free-offset `1/3`-arc minimum is `5/108 = 0.046296 > 1/25`, and on `W4`
(uniform `Gamma_20`) it is `21/400 = 0.0525`. This is exactly the working-rule violation the
regression file was written to prevent.

### 9. §9 "the half-arc family has length 1/2 ... both families are blind to the good cut by
construction" — **REFUTED**

The certifying cut of `mu_eta` **is** in the half-arc family. The arc `[s*eta, s*eta + 1/2)` has
length exactly `1/2`, contains the upper `(1-s)` of cluster 0 and all of cluster 1, and has
monochromatic mass `[s^2 + (1-s)^2]/18`, i.e. `1/36` at `s = 1/2` — the same value as P2's
"one whole cluster plus half of the next". Confirmed exactly on the discrete stand-ins: the minimum
over arcs of length exactly `1/2` equals `ARCBOUND` there (`49/2025`, `16/625`). What is blind is
the half-arc **average** `A = W - 2T`, not the half-arc family. P2's own sub-claim that the good
arc has "both of its endpoints in the interior of the clusters" is likewise wrong: its left endpoint
lies in a gap.

P2's *conclusion* (a repair needs free length **and** free offset) nevertheless stands — for a
different reason than the one given: I ran both one-parameter families against the regression set,
and both are dead. Half-arc minimum: refuted by `W1'` (`2/49 = 0.0408 > 1/25`). Free-offset
`1/3`-arc minimum: refuted by `W3`, `W4`. So §9's recommendation survives while its stated evidence
does not.

### 10. §7(a) "the localised search" table — **REFUTED as `CRIT` values**

`P2_search.crit_float` minimises over `k <= KLEV = 10` only, in floating point. A `k`-truncated
minimum is an **upper** bound on `CRIT`, so the table's entries are not `CRIT`. The internal
contradiction is exact: §4 proves the four-atom optimum is `(3-2sqrt2)/4 = 0.04289322`, yet §7(a)
reports "`4 atoms, best CRIT = 0.0429749`" — larger. I re-proved the four-atom ceiling
independently by classifying all realisable 4-atom circle graphs (`audit_P2_extra.py` §2): `K_{1,3}`,
`P_4`, `P_3+K_1`, `K_2+2K_1` all have some `m(b) = 0` (and `C_4` is not realisable on the circle), so
only `2K_2` survives, where `m = {ab, ab, cd, cd}` and `A < (ab+cd)/3` force
`CRIT < (3-2sqrt2)/4` for **every** 4-atom measure. And the mechanism is demonstrated explicitly:
`x = (7,10,7,10)/34` has truncated `CRIT(k<=10) = 0.0429642` but **true `CRIT = 0.0423875`**; the
same effect at `(12,17)` and `(41,58)`. The §7(a) conclusion ("the optimiser rediscovers the
falsifier") is still supported — the exact `(169,239,169,239)` point has true `CRIT = 0.0428931 >
1/25` — but the table's numbers and its `x 1/25` column must not be quoted.

### 11. §3 "every neighbourhood cut `N(b)` is above `1/25`" — **REFUTED as stated**

True only for `b in supp mu`. `N(b)` is an independent arc for **every** `b` on the circle, and on
the 4-atom witness `b = 4/1800` gives the cut `{606, 1203}` with monochromatic mass **0**. The
hierarchy `bound_k` only weights `b in supp mu`, so the falsification is unaffected — and, notably,
free `b` does *not* rescue the Wagner witness (still `3/64`), which is why the falsification is
robust. But the sentence needs the qualifier.

### 12. §6 methodological finding about round-5 sampling — **CONFIRMED in part, UNSUPPORTED in detail**

`Gamma_11, 14, 17, 20, 23` do all appear in `R5K9_MOMENT_CRITERION.md`'s list
(`Gamma_5,7,8,10,11,13,14,16,17,20,22,23`, 2400 measures, 0 violations), and my sweep confirms
falsifiers exist on all five. But the round-5 random sampler is **not preserved** in `round5/` (no
script matches), so its weight range is unknown and the stronger claim "the round-5 sample space
contained falsifiers" cannot be checked against the record. The falsifiers on those graphs need
`q >= 8` (and `q = 18` for `Gamma_11`); if the sampler drew from a smaller `q`, the space did not
contain them.

---

## Trap checklist required by the audit protocol

| trap | finding |
|---|---|
| float on an acceptance path | `P2_verify.py`, `P2_verify2.py`, `P2_small.py`, `P2_minimal.py`: floats appear only inside f-strings; every comparison is on `Fraction`s. `P2_exhaust.cpp`: all acceptance tests integer, doubles only for ranking (as documented) — **but the ranked maximum is therefore not certified by that program**; my sweep certifies it. `P2_search.py` is float throughout — see verdict 10. |
| `psi < 1/25` quoted as a maximum for an odd-girth-5 graph | **not committed.** P2 reports `psi = 1/32` for Wagner *at one weighting*, never as `max_x psi`. For the record I exhibited `max_x psi(V8) >= 1/25`: the induced `C5` at `Gamma_14` support `{0,3,7,8,12}` with uniform weights gives `psi = ARCBOUND = 1/25` exactly. |
| enumeration excluding zero weights | not committed: `P2_exhaust.cpp` runs `c` from 0 for `i >= 1`; the quoted `Gamma_11` witness itself has zeros. |
| claimed exhaustive range vs loop bounds | matches: `qmax = 20/15/12/10` for `m <= 12/18/24/30`, `q >= 2`, `m in [5,30]`, and the caps are disclosed in §6. `m <= 4` is vacuous (`Gamma_3` has no edges, `Gamma_4` has `A = 0`). |
| circularity | none. The ceiling uses only Cauchy–Schwarz and `d > 1/3`; the falsifiers are direct evaluations. |
| quoted theorem whose hypotheses do not match its use | item 6 is quoted **as the thing being corrected**, correctly. Bhatia–Davis is used correctly (verdict 7). No use of Chen–Jin–Koh/Brandt–Thomassé. |
| tightness at the `C5` extremal | the ceiling proof returns exactly `1/25` at `W = 1/5`, which `C5` attains; every route calibrates to `1/25` on `C5`. |
| minimality claim ("four atoms") | **confirmed** by independent classification: 3 atoms give `bound_0 = 0` (path) or `x_a x_b x_c <= 1/27 < 1/25` (edge + isolated). |
| §6 self-caution (`k <= 8` truncation reports 10 442) | **confirmed**: the earlier log's summary is 10 442 vs 1 790; the quoted example `Gamma_11, (3,0,1,2,2,0,1,2,1,0,2)` has `bound_12 = 16673742257/419891253936 = 0.0397097 <= 1/25` (first closing level `k = 11`), and is not a falsifier. |

## Net effect on the programme

Withdrawing R5-K9 §§8–10 is justified: the "final form" `CRIT <= 1/25`, the two-term harmonic form,
and the ad-hoc variance form are all refuted by exact witnesses, and the single remaining unproved
step of the round-5 reduction is false. The arc-cut conjecture and Erdős 23 are untouched (max
`ARCBOUND` over 1 790 falsifiers `= 4/121 < 1/25`).

The one thing the next round must **not** inherit from P2 is §9. Both one-parameter arc families it
discusses are already refuted by the round-5 regression set (half-arc minimum by `W1'`, free-offset
`1/3`-arc minimum by `W3`/`W4`), and its description of which cut is missing is wrong: the
certifying cut for the `1/3`-periodic family *is* a length-`1/2` arc. The honest statement of the
gap is that the *average* `A` and the *support-anchored* cuts `m(b)` are both blind, while the
*minimum* over arcs sees it — and no one-parameter sub-family of arcs can be enough.
