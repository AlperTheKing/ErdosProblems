# AUDIT of round7/Q1.md — adversarial, independent re-implementation (pass 2)

Everything below was recomputed from scratch in `round7/a2_*.py|cpp`: my own graph6 decoder
(explicit column-major double loop, round-trip tested), my own `bip` in **three** mutually
independent ways (per-edge scan over all `2^(n-1)` cuts; popcount max-cut over all `2^n`
subsets; subset-DP `e[S]` with `mono(S)=e[S]+e[~S]` in C++), my own neighbourhood-union
enumerator over **all** `2^n` index sets, my own induced-C5 and 5-cycle counters (5-subset
scan, cross-validated against `tr(A^5)/10`), my own composition enumerator (zero weights
allowed), my own `geng` census driver. Exact integers / `fractions.Fraction` on every
acceptance path; floats appear only in the entropy diagnostics.

An earlier audit pass of this file exists at `round7/audit_Q1_pass1_backup.md`. It was treated
as untrusted data: every verdict below was re-derived here, not copied.

## Verdicts, most consequential first

| # | claim in Q1.md | verdict |
|---|---|---|
| E3 | §7 / summary: Grotzsch blow-ups, `max 25 bip/W^2 = 1` "attained **only** at `(0,0,0,0,0,t,t,t,t,t,0)`" | **REFUTED** — 471 maximisers at `W=25`; contradicts accepted base 2 **and** base 4 |
| R1 | neighbourhood-union cut certificate refuted by the Grotzsch graph | **CONFIRMED** — values, uniqueness in the census, blow-up family, and **novelty** against all ten recorded witnesses |
| R1-scope | "…in particular every BFS-layer cut rooted at a vertex … and every strengthening of the dead `{m(b)}` family" | **REFUTED as an inclusion** and **redundant**: BFS-layer and single-`N(v)` families already exceed `1/25` on *recorded* witnesses, and the single-`N(v)` family dies on `C6` |
| — | "unique failure among all **1 236 380** connected triangle-free graphs on `n<=12`" | **REFUTED** (arithmetic) — the total is **1 246 466** |
| — | §6: "`(27/16)^{2/5} N^2/25 = N^2/22.56`" | **REFUTED** (arithmetic) — `(27/16)^{2/5}=1.232814` gives `N^2/20.2788`; the constant that follows from Petersen is `(27/16)^{1/5}=1.110322`, i.e. `N^2/22.5160` |
| Q1-C | `bip <= floor((N-Delta-1)^2/4)`, "not subsumed by the base-5 chain" | **CONFIRMED as true, UNSUPPORTED as new**: it is base 5 + Mantel, it is a *max*-degree statement, it is vacuous and non-tight on `C5[n]` |
| R2 | pentagon counting refuted by `C7` | **CONFIRMED**, but `C7` is recorded witness **W6**, `(P)` was invented in this report, and the ratio table silently assumes `c5>0` |
| Q1-B | counting dichotomy | **CONFIRMED** (exact/symbolic), **not material** |
| (a) | entropy budget `log(10(2^n-1))`, scoreboard row "**BLOCKED**" | **values CONFIRMED**; label **UNSUPPORTED** (the report itself concedes it blocks nothing); one verbal overstatement; `eps>0` rows 0.04–0.82 % high |
| (c) | pairwise pseudo-marginals give `0` | **CONFIRMED**; the illustrating triple `{0,1,3}` on `C5` is **wrong** |
| — | no floating point on an acceptance path; zero weights allowed; ranges covered; no circularity | **CONFIRMED** |

---

## 1. REFUTED — E3, the uniqueness of the blow-up maximiser (§7 and the summary)

Q1.md §7: *"`max 25 bip/W^2 = 1` exactly, attained **only** at `a = (0,0,0,0,0,t,t,t,t,t,0)` —
the induced-`C5` concentration"*.

Exhaustive exact recount, `a2_blowup.exe "J?BD@g]Qvo?" 1 25 8 25`, **600 805 295** weight
vectors, zero weights allowed, all `2^10` cuts, 64-bit integers, no early-exit on the
acceptance test (`a2_blowup_grotzsch.out`):

```
W       =  5   10   15   20   25
#{ a : 25*bip(H[a]) == W^2 } = 31,  96, 191, 316, 471
#{ a : 25*bip(H[a])  >  W^2 } =  0,   0,   0,   0,   0     (max = 1 exactly: CONFIRMED)
```

Three exact falsifiers of the word "only", each verified twice — by the base-1 blow-up
identity over the `2^10` cuts of `H` **and** by brute force over all cuts of the explicit
25-vertex blow-up (`a2_final.out` item 1):

```
a = (5,5,0,0,0,5,5,0,0,5,0)   W=25  bip=25  25*bip=625=W^2   support {0,1,5,6,9} = another induced C5
a = (0,0,0,0,1,5,4,5,5,5,0)   W=25  bip=25  25*bip=625=W^2   support of size 6
a = (0,0,0,1,3,4,2,5,5,5,0)   W=25  bip=25  25*bip=625=W^2   support of size 7
```

The claim contradicts **two** items of the accepted base, so Q1.md §0's sentence *"Nothing
here contradicts the accepted base"* is itself false:

* **base 2 (plateau).** The Grotzsch graph has **31** induced `C5`s (`a2_r1.out` §F). Putting
  weight 5 on each vertex of any one of them gives `H[a] = C5[5]`, hence `bip = 25`. All 31
  are maximisers — exactly the 31 counted at `W=5`.
* **base 4 (twin-collapsing).** On the support of `(0,0,0,1,3,4,2,5,5,5,0)` the pairs
  `{3,5}` and `{4,6}` have equal neighbourhoods, so the vector twin-collapses to
  `C5[5,5,5,5,5]`. Every split of a `C5` blob across such a pair is again a maximiser; this
  is why the count grows `31 -> 96 -> 191 -> 316 -> 471` instead of staying at 1.

Mechanism of the error, in the target's own code: `Q1_blowup_search.cpp` line 94
`if(tru*bestratio_den*25 > bestratio_num*W*W)` and line 169 keep only the *first strict*
improvement in DFS order. Ties are discarded and never counted, so the program can only ever
report one argmax.

## 2. CONFIRMED — R1, the Grotzsch obstruction (the one item that meets the bar)

`a2_r1.py`, `a2_census.cpp`, `a2_regression.py`:

* `J?BD@g]Qvo?` decodes to `n=11`, `|E|=20`, triangle-free, degrees `3^5 4^5 5^1`; my
  backtracking isomorphism finds an explicit isomorphism to `M(C5)`. In this labelling
  `10` is the apex, `0..4` the shadows, `5..9` the `C5` (cycle `5-7-9-6-8-5`) — as Q1.md says.
* `bip = 4` by all three implementations. `130` distinct neighbourhood-union sets; the family
  minimum is `5`; single `N(v)` also `5`; pairs `5`; symmetric differences `9`; closed
  neighbourhoods `10`. `25*fam = 125 > 121 = n^2`; `25*bip = 100 <= 121`.
  Exactly `bip/n^2 = 4/121 = 1/25 - 21/3025`, `fam/n^2 = 5/121 = 1/25 + 4/3025`.
* `a = (1,1,1,1,1,2,2,2,2,2,2)`, `W=17`: `bip = 10` by base 1 **and** `bip = 10` by brute force
  over all `2^16` cuts of the explicit 17-vertex blow-up (50 edges, triangle-free) — this
  also re-verifies accepted base 1 independently. `fam = 12`, overshoot `300/289`.
  `10/289 = 1/25 - 39/7225`, `12/289 = 1/25 + 11/7225`.
* Census with my own driver (`geng -t -c` piped into `a2_census.exe`):
  `6, 19, 59, 267, 1380, 9832, 90842, 1144061` for `n=5..12`;
  `#{fam>bip} = 0,0,0,0,0,0,4,257`; `#{25 fam > n^2} = 0,…,0,1,0`; `#{25 bip > n^2} = 0` throughout.
  The single `n=11` hit printed by my driver is `J?BD@g]Qvo?`. Identical to Q1.md's table.
* Robustness (my own exhaustive search): the family fails at exactly **three** weight vectors
  with `W <= 25` — `1^11` (`W=11`), `(1^5,2^6)` (`W=17`, worst, `300/289`), `2^11` (`W=22`).
  Q1.md's "exactly two for `W <= 20`" is exact; `2^11` is the scaling of `1^11`.
* **Novelty CONFIRMED (protocol step 2).** Running the union family against the ten witnesses
  of `round5/claude_witness_regression.py` with exact integer weights (`a2_regression.out`):

```
witness                 true min (all cuts)   R1 union family   single N(v)   odd-BFS layers
W1  Gamma_8                    1/49                1/49            1/49          1/49
W1' Gamma_11                   1/49                1/49            1/49          1/49
W1'' Gamma_16                  1/49                1/49            1/49          1/49
W2  five-atom extremal         1/25                1/25            1/25          1/25
W3  uniform Gamma_18           1/54                1/54            5/81  ***     1/54
W4  uniform Gamma_20          3/100               3/100          21/400  ***   21/400  ***
W5  three-atom near-path          0                   0               0             0
W6  seven-atom (= C7)          1/49                1/49            3/49  ***     1/49
W8  far-regular Wagner         1/32                1/32            3/64  ***     3/64  ***
W7  unequal five-atom         1/100               1/100           1/100         1/100
```

  The R1 family equals the true minimum on **all ten**, so no recorded witness kills it and
  Grotzsch is a genuinely new kill. (`***` = exceeds `1/25`.) It is also exactly tight on
  `C5`: `fam = bip` for **every** integer weighting with `sum <= 12` (6187 vectors), and
  `max 25 bip/W^2 = 1` at `W ≡ 0 mod 5`; and `fam = bip` on `C5,C7,C9,C11,C13` and on
  `M(C7) (5,5)`, `M(C9) (6,6)`, `M(C11) fam = 7`, `Petersen (3,3)`.
* The census is a legitimate weighted test up to `W = 12`: a blow-up of a triangle-free graph
  is a triangle-free graph, zero weights give induced subgraphs, and a disconnected failure
  forces a connected one (`25 sum fam_i > (sum n_i)^2` is impossible if `25 fam_i <= n_i^2` for
  each part). So no separate weighted sweep is needed for `n <= 12`.

## 3. REFUTED / redundant — the stated SCOPE of R1

Q1.md §3: *"this refutes every certificate whose output cut is a union of neighbourhoods — in
particular the hard-core-model cut `N(I)`, **every BFS-layer cut rooted at a vertex**, … and
every strengthening of the already-dead `{m(b)}` family in that direction."*

**(a) The BFS inclusion is false.** Over the connected triangle-free census, the number of
(graph, root) instances whose odd-layer set is *not* any union of neighbourhoods is
`0, 2, 19, 166, 1542, 17319, 237471, 4124306` for `n = 5..12` (19 048 of 113 433 instances for
`n <= 10`; 4 124 306 of 13 728 732 for `n = 12` alone). Smallest witness `g6 = ECpo`, `n=6`.

**(b) The BFS conclusion needed no new witness.** The odd-BFS-layer family already exceeds
`1/25` on two **recorded** witnesses: `W4` (uniform `Gamma_20`) gives `21/400` against the
truth `3/100`, and `W8` (far-regular Wagner) gives `3/64` against the truth `1/32`. It also
fails on `n=8` and `n=11,12` graphs in the census (`#{25 bfsmin > n^2} = 1, 1, 16, 63` at
`n = 8, 10, 11, 12`). Grotzsch is not what kills it.

**(c) The single-`N(v)` sub-family — the one Q1.md says "attains the failing value" — is dead
four times over in the recorded set and dies on the six-cycle.** New exact witness:

```
C6  (g6 = EEh_, edges 0-3-1-5-2-4-0):   bip = 0   but   min_v e(C6 - N(v)) = 2
                                        25*2 = 50 > 36 = N^2        (factor 25/18 = 1.389)
scale-invariant:  C6[t]  ->  min_v = 2t^2   vs   N^2/25 = 1.44 t^2   for every t
```

This is a six-vertex **bipartite** graph, i.e. `psi = 0`, and it beats the Grotzsch overshoot
(`300/289 = 1.038`) by a factor of 26. Consequently Q1.md's headline *"unique failure among
all … connected triangle-free graphs on `n <= 12`"* is a property of the **union closure
only**; the family it closes dies at `n = 6`. My census confirms the base family fails on
`1, 5, 12, 24, 101, 5183, 61784` graphs at `n = 6,7,8,9,10,11,12`. The surviving new content
of R1 is exactly one sentence: *the union closure does not repair the dead single-`N(v)`
family* — which is true, exact, and worth recording.

## 4. REFUTED (arithmetic) — two numbers

* Census total. `6+19+59+267+1380+9832+90842+1144061 = 1 246 466`, not `1 236 380` (off by
  10 086). Adding `n <= 4` (`1,1,1,3`) gives `1 246 472`. Q1.md's per-`n` table is correct.
* §6 parenthesis. `(27/16)^{2/5} = 1.232814`, so `(27/16)^{2/5} N^2/25 = N^2/20.2788`, not
  `N^2/22.56`. The constant that actually follows from the Petersen ratio
  `bip^{5/2}/c5 = sqrt(27/16)` is `((27/16)^{1/2})^{2/5} = (27/16)^{1/5} = 1.110322`, giving
  `N^2/22.5160`. Both the exponent and the decimal are wrong; the qualitative claim ("worse
  than the published `N^2/23.5`") survives under either reading.

## 5. CONFIRMED with caveats — R2, pentagon counting

`C7`: `|E| = 7`, `bip = 1` (two implementations), `#C5 = 0`, so `bip^{5/2} <= c5` is false —
exact, confirmed. Caveats:
(i) `C7 = Gamma_7` is **recorded witness W6**, so the falsifier is not new;
(ii) the ratio table is silently conditioned on `c5 > 0`. Graphs with `c5 = 0` and `bip > 0`
number `1, 2, 18, 111` at `n = 7,8,9,10`, so the unconditioned maximum is `+inf` from `n = 7`
— which *is* the falsifier. Restricted to `c5>0` I reproduce
`max bip^5/c5^2 = 1 (n<=7), 2 (n=8), 8 (n=9,10)`, i.e. `1, sqrt2, 2 sqrt2`, matching Q1.md;
Petersen `bip=3, c5=12, bip^5/c5^2 = 27/16`. `C5[t]`: `bip = t^2`, `#C5 = t^5` for `t=1,2,3`
(so equality in `(P)` on `C5[n]` is confirmed);
(iii) `(P)` was introduced in this report, so no live recorded mechanism dies here.

## 6. CONFIRMED as true, UNSUPPORTED as new — Q1-C

`bip <= floor((N-Delta-1)^2/4)`: **0 violations** over all 11 563 connected triangle-free
graphs `n = 5..10`; and `((N-Delta-1)^2)/4` at `Delta = 3N/5-1` is exactly `N^2/25` (sympy).
The proof is correct. But:

* Accepted base 5 already records `bip <= min_v e(G - N(v))`. Q1-C is that inequality at a
  maximum-degree vertex plus Mantel on `G - N(v)` (`N-Delta` vertices, one of them isolated).
  One line from a recorded item is not a new theorem.
* The prompt's bar is *"an unconditional theorem on an explicit **minimum**-degree range (it
  shrinks the band of base 5)"*. Q1-C constrains `Delta`, and leaves the base-5 band
  `(4N-2)/25 < delta <= 3N/8` untouched.
* The companion window claim `N/10 < Delta` is strictly weaker than what base 5 already
  gives: `Delta >= delta > (4N-2)/25 = 0.16N`.
* It is vacuous and non-tight on the extremal family: `C5[n]` has `Delta = 2N/5 < 3N/5-1` for
  `n >= 2`, and the bound reads `6, 16, 30, 49` against `bip = 4, 9, 16, 25` for `n = 2..5`.
  A max-degree bound can never be tight at `C5[n]`, so it cannot enter a proof covering the
  extremal object.

## 7. CONFIRMED but not material — Q1-B

Symbolically verified: `max_m (m - 4m^2/N^2) = N^2/16` so `eps <= 1/16-1/25 = 9/400`;
`(1+25e)(1-6e)^2 - 1 = 900e^3 - 264e^2 + 13e`; the roots of `900x^2-264x+13` are
`11/75 -+ sqrt(159)/150 = 0.06260…, 0.23073…`, both above `9/400 = 0.0225`, so the cubic is
positive on the whole admissible range; `|U_1||U_2| >= (6 eps N)^2/4 - O(N) = 9 eps^2 N^2 - O(N)`.
`bip` additive over components and `bip(G_0[t]) = t^2 bip(G_0)` are base items. The theorem
is correct. It kills no mechanism, produces no counterexample and shrinks no degree band; it
is blow-up-plus-padding.

## 8. Values CONFIRMED, label UNSUPPORTED — (a) the entropy budget

My own exact profile enumeration of the `C5[n]` cut spectrum (histogram totals verified equal
to `2^{5n}`, `n = 1..8`) reproduces Q1.md exactly:

```
n           1   2   3    4    5    6    7     8
min mono    1   4   9   16   25   36   49    64      ( = n^2 )
#minimisers 10  30  70  150  310  630  1270  2550    ( = 10(2^n - 1) )
```

`log 2550 = 7.8438` nats `= 0.2829 * 40 log 2`. CONFIRMED.

* Diagnostic discrepancy: the `eps > 0` rows of Q1.md are **0.04 %, 0.17 %, 0.60 %, 0.82 %**
  too high, because `Q1_c5spectrum.py` minimises `beta*M + log Z(beta)` over a fixed grid.
  A convex ternary search on the same exact spectrum gives `9.1544 / 11.9123 / 14.3857 /
  18.3217` against the reported `9.1580 / 11.9322 / 14.4715 / 18.4715`. The direction is
  conservative (the true budget is smaller), so the narrative survives.
* Overstatement: *"at least `4N/5 - 4` of the `N` bits must be decided **deterministically**"*.
  The bound is `sum_v h(p_v) <= (N/5) log 2 + log 10`, i.e. at most `N/5+4` **fair** coins.
  It does not force any `p_v` to `0` or `1`.
* Label. Theorem Q1-A says: a method that is tight at the extremal object must be supported on
  the minimisers of the extremal object. That is true of *every* tight method, not only entropy
  ones, and the report concedes two lines later that it "does not say a graph-reading
  distribution cannot work". Scoring row (a) as **BLOCKED** on the scoreboard is therefore not
  supported by its own content; it is an exact budget computation, not a blocking lemma.

## 9. CONFIRMED with a wrong illustration — (c)

The pseudo-marginals `mu_v = (1/2,1/2)`, `mu_{uv}` uniform on the two unequal pairs for
`uv in E`, product off `E`, are pairwise consistent and give `sum_{uv in E} x_u x_v Pr[X_u=X_v] = 0`
on every graph and every `x`. CONFIRMED (this is the standard fact that the local marginal
polytope relaxation of max-cut equals `|E|`).
But *"on `C5`, the triple `{0,1,3}` forces `X_0 != X_1`, `X_1 = X_3`, `X_0 = X_3`"* is false:
in `C5` neither `13` nor `03` is an edge, so nothing is forced. A correct level-3 chain needs
three overlapping triples: `{0,1,2}` forces `X_0 = X_2`; consistency with `{0,2,3}` then forces
`X_0 != X_3`; `{0,3,4}` forces `X_0 = X_3`.

## 10. Checklist items that came back clean

* **Floating point on an acceptance path**: none. Every acceptance test in Q1.md's code and in
  mine is an integer or `Fraction` comparison (`25*f > n*n`, `25*q <= W*W`).
* **`psi` below `1/25` reported as a maximum at odd girth 5**: not present. Grotzsch's `4/121`
  is explicitly quoted at the uniform `x`, and the exhaustive blow-up search returns
  `max 25 bip/W^2 = 1` exactly, consistent with base 2.
* **Zero weights**: allowed (`lo = 0` in both composition recursions; my `W=5` maximiser count
  of 31 is only reachable with zeros).
* **Claimed exhaustive ranges**: reproduced. `geng -t -c` for `n = 5..12` gives exactly the
  stated counts and exactly the stated hit counts, with my own decoder and my own DP.
* **Circularity**: none found. §4.3 uses triangle removal and 1-Lipschitzness of `bip` under
  edge deletion in the correct directions; Q1-B uses base 1/3/5 correctly.
* **Quoted theorems**: Mantel, Haggkvist, the pentagon theorem `c5 <= (N/5)^5` and triangle
  removal are all used within hypotheses. `bip^{5/2} = c5` on `C5[n]` is verified for `t=1,2,3`.
* **Asymptotic presented as exact**: Q1-B is correctly flagged as `(1-o(1))`; the `o(N^2)` slack
  in §2 and §4.3 is correctly justified through base 3.

## Files (this pass)

`a2_core.py` (library), `a2_r1.py` (+`a2_r1.out`), `a2_census.cpp/.exe` (+`a2_census_n12.out`),
`a2_blowup.cpp/.exe` (+`a2_blowup_grotzsch.out`), `a2_misc.py` (+`a2_misc.out`),
`a2_regression.py` (+`a2_regression.out`), `a2_final.py` (+`a2_final.out`),
`a2_tf3.g6 … a2_tf10.g6`, `audit_Q1_pass1_backup.md`.
Reproduce the two headline findings:
`a2_blowup.exe "J?BD@g]Qvo?" 5 25 8 25` (E3) and `python a2_regression.py` (R1 novelty).
