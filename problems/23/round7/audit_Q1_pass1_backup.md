# AUDIT of round7/Q1.md — adversarial, independent re-implementation

All checks re-implemented from scratch in `round7/audit_Q1_*.py|cpp`: own graph6 decoder,
own max-cut (subset-DP `e[S]`, **not** a Gray code), own neighbourhood-union family over **all**
index sets (Q1_indcut.cpp only searches independent sets), own induced-C5 counter (5-subsets
inducing a 2-regular connected graph, **not** `tr(A^5)/10`), own composition enumerator.
Exact integers / `Fraction` on every acceptance path.

## Verdicts, most consequential first

| # | claim in Q1.md | verdict |
|---|---|---|
| E3 | §7: Grotzsch blow-ups, `max 25 bip/W^2 = 1` "attained **only** at `(0,0,0,0,0,t,t,t,t,t,0)`" | **REFUTED** — 471 maximisers at `W=25`, 31 at `W=5` |
| R1 | neighbourhood-union cut certificate refuted by Grotzsch | **CONFIRMED** (values, uniqueness in the census, blow-up family, novelty) |
| R1-scope | "…in particular every BFS-layer cut rooted at a vertex" | **REFUTED as stated** (conclusion survives for another reason) |
| R2 | pentagon counting refuted by `C7` | **CONFIRMED**, but the witness is the recorded W6 and the ratio table needs `c5>0` |
| Q1-C | `bip <= floor((N-Delta-1)^2/4)` | **CONFIRMED**, but it is base-5 + Mantel, and it is a *max*-degree statement |
| Q1-B | counting dichotomy | **CONFIRMED** (arithmetic exact), **not material** |
| (a) | entropy budget `log(10(2^n-1))` | **CONFIRMED** exactly; one verbal overstatement; `eps>0` rows 0.2–0.6 % high |
| (c) | pairwise pseudo-marginals give `0` | **CONFIRMED**; the illustrating triple `{0,1,3}` on `C5` is wrong |
| — | summary line "1 236 380 connected triangle-free graphs on `n<=12`" | **REFUTED** — the correct total is 1 246 466 |
| — | no floating point on an acceptance path / zero weights allowed | **CONFIRMED** |

## 1. REFUTED — the uniqueness of the blow-up maximiser (§7)

Q1.md §7: *"`max 25 bip/W^2 = 1` exactly, attained **only** at `a = (0,0,0,0,0,t,t,t,t,t,0)` —
the induced-`C5` concentration"*.

Exhaustive exact recount (`audit_Q1_blowup.exe "J?BD@g]Qvo?" 1 25 8`, 600 805 295 vectors,
zero weights allowed, all `2^10` cuts, integer arithmetic):

```
W = 5 10 15 20 25   ->   #{a : 25 bip(H[a]) = W^2} = 31, 96, 191, 316, 471
```

Exact falsifier at `W=25`: `a = (5,5,0,0,0,5,5,0,0,5,0)` has `bip = 25`, `25 bip = 625 = W^2`.
There are **31** induced `C5` in the Grotzsch graph and every one of them gives a maximiser
(`audit_Q1_falsifier.py` §D); by accepted base 2 this is forced, so the "only" claim
*contradicts the accepted base*, which the report elsewhere says it does not do.
Mechanism of the error: `Q1_blowup_search.cpp` line 94 (`if(tru*bestratio_den*25 > bestratio_num*W*W)`)
and line 169 keep the **first** argmax in DFS order only; ties are discarded and never counted.
The numeric part of the claim (`max = 1`, no counterexample for `W <= 25`) is CONFIRMED.

## 2. CONFIRMED — R1, the Grotzsch obstruction

Independent values (`audit_Q1_falsifier.py`, `audit_Q1_census.exe`, plus a third DP-free
per-edge loop):

* `J?BD@g]Qvo?`: `n=11`, `|E|=20`, triangle-free, degrees `3^5 4^5 5`, isomorphic to `M(C5)`;
  in that labelling `5..9` is the `C5`, `0..4` the shadows, `10` the apex — as Q1.md states.
* `bip = 4` (three implementations), `min` over **all 130** unions of neighbourhoods `= 5`.
  `4/121 < 1/25 < 5/121`; `25*fam - n^2 = +4`.
* Widened: single `5`, pairs `5`, triples `5`, all unions `5`, symmetric differences `9`,
  set differences `N(u)\N(v)` `5`, closed neighbourhoods `10`, unions of closed neighbourhoods `9`.
* Blow-up `a = (1,1,1,1,1,2,2,2,2,2,2)`, `W=17`: `bip = 10`, `fam = 12`,
  `10/289 < 1/25 < 12/289`, overshoot `300/289`. Cross-checked against the **explicit
  17-vertex blow-up** by brute force over all `2^17` cuts: `bip = 10` (this also re-verifies base 1).
* Census (my own geng driver): `6, 19, 59, 267, 1380, 9832, 90842, 1144061`;
  `#{fam>bip} = 0,0,0,0,0,0,4,257`; `#{25 fam > n^2} = 0,…,0,1,0` — identical for the
  independent-set family **and** for the full union family. Unique failure = the Grotzsch graph.
* Robustness: over all `a >= 0` with `sum a = W <= 25` the certificate fails at exactly
  three vectors: `1^11` (`W=11`, `125/121`), `(1^5,2^6)` (`W=17`, `300/289`), `2^11` (`W=22`,
  `500/484 = 125/121`). Q1.md's "exactly two for `W <= 20`" is exact; the `W=22` vector is the
  scaling of the first, confirming scale-invariance.
* **Novelty CONFIRMED**: the R1 family run against the ten recorded witnesses of
  `round5/claude_witness_regression.py` returns `1/49, 1/49, 1/49, 1/25, 1/54, 3/100, 0, 1/49,
  1/32, 1/100` — **exactly equal to the truth on all ten**, in particular `1/32` on the
  far-regular Wagner configuration. So no recorded witness kills this family; Grotzsch is a new kill.
  It is exactly tight on `C5[n]` (`n<=4` by brute force over all `2^{5n}` cuts, `n<=6` by base 1)
  and `fam = bip` for all 6187 integer weightings of `C5` with `sum <= 12`.

### 2a. REFUTED sub-claim — the scope sentence

Q1.md §3: *"this refutes every certificate whose output cut is a union of neighbourhoods — in
particular … **every BFS-layer cut rooted at a vertex** …"*.
Odd-BFS-layer sets are **not** in the neighbourhood-union family: over the 113 433 rooted
instances in the connected triangle-free census `n <= 10`, **19 048** have an odd-layer set that
is not any union of neighbourhoods. Smallest witness: `g6 = ECpo` (`n=6`), root `0`,
odd-layer set `{2,3,4}`. (The conclusion is nevertheless true for BFS-layer certificates, but by
a separate computation, not by inclusion: on the Grotzsch graph the eleven odd-layer cuts have
monochromatic values `7,7,7,7,7,6,6,6,6,6,5`, minimum `5 > 121/25`.)

## 3. CONFIRMED, with caveats — R2, pentagon counting

`C7`: `|E| = 7`, `bip = 1`, `#C5 = 0` — exact, so `bip^{5/2} <= c5` is false. Confirmed.
Caveats: (i) `C7` is **witness W6** (`Gamma_7` uniform) of the recorded regression set, so the
falsifier is not new; (ii) the table "max `bip^{5/2}/c5` = `1, sqrt2, 2sqrt2, 4sqrt2`" is
implicitly restricted to `c5 > 0` — with `C7` included the maximum is `+inf` at `n = 7`, which is
the falsifier itself; the report does not state the restriction. Exact values reproduced:
`max bip^5/c5^2 = 1/1 (n<=7), 32/16 (n=8), 32/4 (n=9,10), 32/1 (n=11,12)`; Petersen `27/16`.
(iii) `(P)` was introduced in this report, so no recorded mechanism dies here.

## 4. CONFIRMED but not new — Q1-C

`bip <= floor((N-Delta-1)^2/4)` holds for all 11 563 connected triangle-free graphs `n=5..10`
(0 violations), and `((N-D-1)^2)/4` at `D = 3N/5-1` is exactly `N^2/25` (sympy).
But accepted base 5 already records `bip <= min_v e(G-N(v))`; Q1-C is that inequality plus
Mantel on `G-N(v)` (which has `N-Delta` vertices, one of them isolated). It is a **max**-degree
statement, so it does not shrink the minimum-degree band that base 5 leaves open. Also the
reported window `N/10 < Delta` is weaker than the base already gives
(`Delta >= delta > (4N-2)/25 = 0.16N`).

## 5. CONFIRMED but not material — Q1-B

Arithmetic verified symbolically: `bip <= N^2/16` is the maximum of `|E| - 4|E|^2/N^2`,
`1/16 - 1/25 = 9/400`, `(1+25e)(1-6e)^2 - 1 = 900e^3 - 264e^2 + 13e`, and the smallest positive
root of `900x^2 - 264x + 13` is `11/75 - sqrt(159)/150 = 0.0626… > 9/400 = 0.0225`, so the
polynomial is positive on the whole admissible range. `bip` additivity over components and
`bip(G_0[t]) = t^2 bip(G_0)` are base items, re-verified. The theorem is correct; it is a
blow-up-plus-padding argument, it kills no mechanism, produces no counterexample, and shrinks
no degree band.

## 6. CONFIRMED — the exact values of (a)

Cut spectrum of `C5[n]`, computed twice (brute force over all `2^{5n}` subsets for `n <= 4`;
exact multinomial profile enumeration for `n <= 8`, histogram totals `= 2^{5n}`):
`min = n^2` and `#minimisers = 10(2^n - 1)` for `n = 1..8` (10, 30, 70, 150, 310, 630, 1270, 2550).
`log 2550 = 7.8438` nats `= 0.2829 * 40 log 2`.
Discrepancy (diagnostic only): the `eps > 0` rows are 0.2–0.6 % too high because
`Q1_c5spectrum.py` minimises over the fixed grid `beta in {b/8}`; a convex ternary search gives
`9.1544 / 11.9123 / 14.3857 / 18.3217` against the reported `9.1580 / 11.9322 / 14.4715 / 18.4715`.
Direction is conservative, so the conclusion stands.
Overstatement: "at least `4N/5 - 4` of the `N` bits must be decided **deterministically**". What
the entropy bound gives is `sum_v h(p_v) <= (N/5) log 2 + log 10`, i.e. at most `N/5+4` **fair**
coins; a coin with `p = 0.499` is not deterministic and is not excluded.

## 7. CONFIRMED — (c), with a wrong illustration

The pseudo-marginals are pairwise consistent and give `0` on every graph (this is the standard
fact that the local marginal polytope relaxation of max-cut equals `|E|`). But the sentence
*"on `C5`, the triple `{0,1,3}` forces `X_0 != X_1`, `X_1 = X_3`, `X_0 = X_3`"* is false: in `C5`
neither `13` nor `03` is an edge, so nothing is forced. The correct level-3 infeasibility chains
three triples (`{0,1,2}` forces `X_0=X_2`, `{0,2,3}` then forces `X_0 != X_3`, `{0,3,4}` forces
`X_0 = X_3`).

## 8. Arithmetic slip in the summary

"unique failure among all **1 236 380** connected triangle-free graphs on `n <= 12`":
`6+19+59+267+1380+9832+90842+1144061 = 1 246 466` (`1 246 472` including `n <= 4`).
The per-`n` table inside Q1.md is correct; only the total is wrong.

## 9. Checklist items that came back clean

* No floating point on any acceptance path (`25*f > n*n`, `25*q <= W*W`, `Fraction`).
* Integer enumerations allow zero weights (`lo = 0` in the composition recursion).
* Claimed exhaustive ranges are covered: geng `-t -c` for `n = 5..12` reproduced exactly.
  (The saved log `Q1_grotzsch_W25.out` only contains `W = 23,24,25`; I re-ran `W = 1..25`.)
* No circularity: nothing in Q1.md assumes a statement of strength `>=` the conjecture.
  §4.3 uses triangle removal correctly and `bip` 1-Lipschitz under edge deletion correctly.
* The pruning in `Q1_blowup_search.cpp` (`25*mn*10 > 9*W*W`) is sound for the maximum, since the
  early-exit value `mn` is a genuine upper bound on `bip`.

## Files (audit)

`audit_Q1.md`, `audit_Q1_core.py`, `audit_Q1_falsifier.py` (+`.out`), `audit_Q1_misc.py` (+`.out`),
`audit_Q1_regression.py` (+`.out`), `audit_Q1_scope.py`, `audit_Q1_scope2.py` (+`.out`),
`audit_Q1_census.cpp/.exe`, `audit_Q1_n12.out`, `audit_Q1_blowup.cpp/.exe`,
`audit_Q1_grotzsch_W25.out`.
