# AUDIT of round7/Q2.md — adversarial re-verification (COMPLETE)

Auditor's own re-implementation: `audit_Q2_v2_core.py` (own graph6 decoder, own
max-cut, own switching algebra — `Delta(S)` is obtained by RECOMPUTING the cut
value `mono(Y) - mono(Y xor S)`, never from the claimed formula), plus
`audit_Q2_v2_a/b/c/e/f.py` and `audit_Q2_v2_d.cpp` (own ceiling search, own
composition enumerator).  All arithmetic is Python `int`/`Fraction` or C++
`long long`/`__int128`.  No floating point on any acceptance path.

**Bottom line.**  The load-bearing object of the report — the obstruction
`W*(u,r)` and its stability threshold — is CONFIRMED exactly and extended.
Three recorded values/claims are wrong, one of them a claimed exhaustive
value (`STAR = 0` at `N=45`).  The headline "Blocking Lemma" is UNSUPPORTED
**as written** (its stated derivation is a non-sequitur and it misuses Lemma 1);
its operative corollary is CONFIRMED.

| # | claim | verdict |
|---|---|---|
| 1 | R3 Blocking Lemma as stated | **UNSUPPORTED** (corollary CONFIRMED) |
| 2 | §4/EXACT VALUES `STAR = 0 at N = 45` | **REFUTED** — exact falsifier `28/27` |
| 3 | R1 table entry `b = 10 -> min|S| = 10` | **REFUTED** — truth `9` (its own script says 9) |
| 4 | Fact 2.2 example `v in c4, T = c4` | **REFUTED** — `Delta = -2n^2`, and `c4` has `sigma = 0` |
| 5 | R2 `W*(u,r)` (all exact values + stability) | **CONFIRMED**, extended to `u <= 12` |
| 6 | L1, L2, L3, C5[n] ledger, charge identity | **CONFIRMED** |
| 7 | Part (c) exhaustive `N <= 12` | **CONFIRMED** (counts, 587, 0 failures, the 15) |
| 8 | §4 ceiling table at `h <= 6` (N=24,30,36,48,60) | **CONFIRMED** exactly |
| 9 | R4 6-part LOC champion `EEj_` | **CONFIRMED** |
| 10 | "LOC caps at `89/900`" read as an upper bound | **UNSUPPORTED** (h=7 gives `42/576`) |
| 11 | round5 ten-witness regression + C5[n] tightness | **PASSED** |

---

## 1. R3 / BLOCKED — UNSUPPORTED as stated; the corollary is CONFIRMED

Verbatim from Q2.md:

> Let `Phi` be any functional of the graph `G` alone. ... Hence no discharging
> scheme whose global term is a functional of `G` alone can separate them, and
> since the conclusion `25|M| <= N^2` is true at the maximum cut and false at the
> `W*` cut, no such scheme exists.  Consequently the global term must be a
> functional of the cut, and by Lemma 1 the only such functionals are the
> `Delta(S)`; every `Delta(S)` with `|S| < (7/24)N` is satisfied by `W*(u,u)`.

Two defects.

**(a) The `Phi`-invariance clause does no work; the inference is a non-sequitur.**
What blocks a scheme is that `W*(u,u)` satisfies every *cut* hypothesis the
scheme uses while violating the conclusion.  Whether the global term is a
functional of `G` is irrelevant to that.  Read literally the lemma proves too
much: the same two sentences applied to a scheme that uses the *full* maximality
hypothesis would "show" no such scheme exists, which is false — the conclusion
*is* true at the maximum cut of the very same graph (`bip(C5[2u,2u,3u,2u,3u]) =
4u^2 = N^2/36 < N^2/25`, verified exactly, `audit_Q2_v2_b_out.txt` B1).  The
honest statement is about the *local family*, not about `Phi`.

**(b) "by Lemma 1 the only such functionals are the `Delta(S)`" is a category
error.**  Lemma 1 says the *maximality hypothesis* is equivalent to
`{Delta(S) <= 0}`.  It does not say every functional of the cut is a `Delta(S)`.
Counterexamples: `|M|`, the multiset `{sigma(v)}`, `e_M(N(v))`, `#{v : d_M(v)>0}`
are all functionals of the cut and none is a `Delta(S)`.

**Corrected statement, which my run CONFIRMS.**  Any scheme whose cut hypotheses
are contained in `{Delta(S) <= 0 : |S| < (7/24)N}` — together with arbitrary
facts about `G` — cannot prove better than `bip(G) <= N^2/24`, because
`W*(u,u)` satisfies all of them and has `25|M|/N^2 = 25/24` exactly.

**Two scope caveats the report does not state.**

* *Necessary is very far from sufficient.*  `SUP` (supersets of a neighbourhood)
  invokes sets of size `|S|/N = 5/6 = 0.8333` and still has `max Delta = 0` on
  `W*(u,u)` for every `u = 1..7` (`audit_Q2_v2_b_out.txt` B4, argmax
  `(2u,2u,3u,0,0,3u)`).  "The global term must invoke a switching set of measure
  `>= 7/24`" is a valid necessary condition and is not a recipe.
* The obstruction says nothing about schemes with a minimality/induction
  hypothesis (`bip(G) <= bip(G-v) + floor(d(v)/2)`, minimal counterexample,
  Haggkvist), since `W*` is a *cut* inside a graph that obeys the conjecture, not
  a minimal counterexample.

No circularity: nothing in the chain assumes a statement of strength `>=` the
conjecture; `25|M| <= N^2` is only ever tested.

---

## 2. REFUTED — `STAR = 0 at N = 45` (exact falsifier)

Q2.md §4 and EXACT VALUES:

> **STAR `600/576, 1350/1296, 2400/2304, 3750/3600` — all exactly `25/24`**
> (`0` at `N = 30, 45` since the witness needs `12 | N`).

**Exact falsifier** (`audit_Q2_v2_d_out.txt`, dissected at the vertex level in
`audit_Q2_v2_e_out.txt` E1):

```
H = ECxo (= C5 with the c3 class doubled), col = 010110,
a = (7,2,5,7,12,12)   i.e.  G = C5[7,7,12,7,12],
X = c0 u c2 u (c3 \ R), Y = c1 u c4 u R, |R| = 2
N = 45   |E| = 385   |M| = 84
25|M|/N^2 = 2100/2025 = 28/27 > 1
sigma per part = (19, 0, 0, 19, 10, 4)  >= 0
switch-star slacks = (19, 0, 0, 19, 0, 0)  >= 0
family (*) : max Delta = 0    (SATISFIED)
min improving switch |S| = 13 = (13/45)N = 0.2889 N
```

So `STAR(N = 45, h <= 6) = 2100/2025 = 28/27`, not `0`.  `STAR(N = 30) = 0` is
confirmed.  The stated *reason* is also wrong: the family is
`C5[a,a,b,a,b]` with `|M| = ab`, `N = 3a+2b`; `25ab > (3a+2b)^2` has integer
solutions at many `N` not divisible by 12 (`a=7, b=12` at `N=45`).  Only the
*exact* value `25/24` needs `12 | N` (it forces `b/a = 3/2`).

Cause: the `N = 45` row was run at `h <= 5` only.  The table row discloses
`(h<=5)`; the EXACT VALUES summary drops the caveat and states `0` as a value.
My `h <= 5` re-run reproduces the report's `2750/2025` (witness `H=CU`,
`a=(10,11,13,11)`, `M=110`) and `STAR = 0` exactly — the engine is right, the
scope statement is not.

Impact on the headline: none.  `28/27 < 25/24`, so the `N^2/24` cap stands.

---

## 3. REFUTED — R1 table, `b = 10`

Q2.md §3 table: `b = 10 -> min|S| = 10, |S|/N = 10/42 = .238`.

**Exact falsifier** (independent count enumeration and full `2^N` cross-check at
small `b`, `audit_Q2_v2_a_out.txt` A4):

```
b = 10, N = 42:  S = (7 vertices of A3) u (2 vertices of A4)
Delta = 2*2*7 - 2*10 - 7 = 28 - 27 = 1 > 0,   |S| = 9
min |S| = 9,  |S|/N = 9/42 = 3/14 = 0.2143   (report: 10, 10/42 = .238)
```

The report contradicts its own script: `Q2_ledger_out.txt` line 235 reads
`MIN IMPROVING SWITCH: |S|=9 s=(0, 0, 7, 2) Delta=1 ratio |S|/N = 3/14 = 0.2143`.
The table copied `b = 11`'s value `10` into the `b = 10` column and re-derived
`10/42` from it — a number that appears nowhere in the computation.
All other entries (`b = 3,4,5,6,8,12`) reproduce exactly, and the direction of
the error weakens `W_b` further, so **R1's verdict is unaffected**.
The asymptotic `|S|/N -> 1/8` is CONFIRMED (`b=50`: `33/202 = 0.1634`; the exact
optimum of `p + q` under `q(2p-1) > pb` is `(1+sqrt b)^2/2 + O(1)`).

---

## 4. REFUTED — Fact 2.2's worked example

> for each of the three `sigma = 2n` classes there is an independent `T` with
> `Delta(N(v) u T) = 0` (e.g. `v in c2, T = c2`; `v in c4, T = c4`)

`c4` has `sigma = 0`, not `2n` (the report's own §2 ledger says so), and
exactly:

```
v in c4, T = c4 :  Delta = -2n^2   ( -2, -8, -18, -32 at n = 1,2,3,4 )
```

The *claim* is CONFIRMED — per-class maxima of `Delta` over the family `(*)` are
`c0: 0, c1: 0, c2: 0, c3: -2n^2, c4: -2n^2` — only the second example is wrong.

---

## 5. CONFIRMED — everything else, reproduced independently and exactly

**L1** (`audit_Q2_v2_a_out.txt`): 1,620,864 `(graph, cut, S)` triples over all
connected triangle-free graphs on 5..8 vertices, `Delta` recomputed vs formula,
**0 mismatches**; `max cut <=> all Delta(S) <= 0` checked over all `2^n` subsets
for every cut, **0 mismatches**.

**L2** (corner certificate): 33,312 part-respecting cuts of `C5`/`P4`/`C4`
blow-ups, **0 mismatches**.  This is what licenses every part-level computation
in the report and in this audit.

**C5[n] ledger**: `25|M| - N^2 = 0` exactly for `n = 1..8`;
`sum mu = N^2 - 25|M|` exactly; `mu = +N` on `c0,c1,c2` and `-(3/2)N` on
`c3,c4`; family `(*)` tight (`max Delta = 0`).  Fact 2.1's radius-2 conclusion
is sound as an argument about rules that ship charge along edges (`c3`'s only
non-deficit neighbour is `c2`, whose own supply `5n^2 < 7.5n^2`); "unique" is an
over-claim — only the class-to-class totals are forced, the per-edge split
`(5/2, 15/2)` additionally assumes rules uniform within classes.

**R2 / `W*(u,r)`** — the load-bearing witness, re-derived from an
independently-built graph (interleaved vertex numbering, `Delta` by
recomputation):

```
u=1..9:  N = 12u, |E| = 28u^2, |M| = 6u^2 (independent of r),
         25|M|/N^2 = 25/24 exactly,  sigma = (5u,5u,2r,0,0,4u-2r),
         bip(G) = 4u^2 = N^2/36 < N^2/25   [G obeys the conjecture]
min improving switch = ceil((7u+3)/2) for u = 1..12   (report: u <= 9)
   5,9,12,16,19,23,26,30,33,37,40,44   witness (0,1,floor(5u/2)+1,0,u,0)
min |S|/N over u <= 9 = 11/36 = 0.30556 ;  every improving S has |S| > (7/24)N
(*) / SUP / NBRU / PAIRNBR : max Delta = 0 exactly, u = 1..7
vertex-level (*) by FULL independent-set enumeration: u=1 (760 instances),
   u=2 (72,768 instances) -> max Delta = 0
r-ranges for u = 1..7 match the report exactly
```

**Part (c)** (`audit_Q2_v2_c_out.txt`, own geng + own maximality filter):
counts `1,2,3,4,6,10,16,31,61,147` (n=3..12), **278** for `5<=n<=12`;
**587** maximum cuts; **0** failures of the bound, **0** of the charge identity,
**0** of `(*)` at maximum cuts; exactly **15** PART-B witnesses on the same 6
graphs (my masks are the complements of the report's — the same cuts under the
opposite pinning); best ratio `25/24`; the champion `K??FF?^Fvw^_` has twin
quotient a 5-cycle with class sizes `(3,2,2,3,2)`, i.e. it **is**
`C5[2,2,3,2,3] = W*(1,1)`.  Extra: there are **no** disconnected maximal
triangle-free graphs on 3..9 vertices, so `geng -c` lost nothing.

**§4 ceilings at `h <= 6`** (`audit_Q2_v2_d.cpp`, own engine) — every reported
number reproduced exactly, witnesses included:

| N | LOC | STAR | ALL |
|---|---|---|---|
| 24 | 850/576 | 600/576 = 25/24 | 0 |
| 30 | 1950/900 | 0 | 0 |
| 36 | 2900/1296 | 1350/1296 = 25/24 | 0 |
| 45 | 4600/2025 (report: 2750/2025 at h<=5) | **2100/2025** (report: 0) | 0 |
| 48 | 5450/2304 `a=11,4,9,4,9,11` | 2400/2304 = 25/24 | 0 |
| 60 | 8900/3600 `a=14,4,12,4,12,14` | 3750/3600 = 25/24 | 0 |

**R4** (`audit_Q2_v2_e_out.txt` E3): `EEj_` decodes to edges
`03,04,05,13,15,24,25`, `bip = 0` (bipartite) ✓; at `a=(14,4,12,4,12,14)`,
`N=60`: `|M| = 356`, `|M|/N^2 = 89/900 ~ 1/10.112`, `sigma = (2,10,2,10,2,2)`,
switch-star slacks `(2,10,2,10,2,2)` all `>= 2` ✓, and family `(*)` catches it
(`max Delta = 284 > 0`) ✓.  Its minimum improving switch is only **5 vertices**
`(0,0,2,0,0,3)`, `Delta = 2` — a vivid demonstration that LOC misses `O(1)`-size
improvements that are not stars.

**§3 uniqueness**: `X = A1 u A4` is indeed the *unique* non-optimal part-cut of
`W_b` passing `sigma >= 0` + switch-star, for `b = 3,4,5,6` ✓.
`(*)` refutes `W_b`: `Delta(N(v) u A1) = b^2` exactly, `b = 2..5` ✓.

---

## 6. Auditor's extension: the `h = 7` probe the report never ran

`audit_Q2_v2_d_h7.txt`, all 59 connected triangle-free 7-vertex patterns, all
colourings, all integer weight vectors **including zeros**:

```
N=24, h=7:  LOC 1050/576  (h<=6 value was 850/576)   STAR 600/576 = 25/24   ALL 0
N=30, h=7:  LOC 1950/900                              STAR 0                 ALL 0
```

Consequences.

* **The `25/24` STAR ceiling survives 7 parts** — the `N^2/24` figure in the
  headline is not an artefact of the 6-part restriction.  (Strengthens Q2.md.)
* **`89/900` is not a cap.**  The LOC ceiling grows with the number of parts
  (`34/576 -> 42/576` at `N=24` going from `h=6` to `h=7`) and with `N`
  (`.0590, .0867, .0895, .0946, .0989` at `N=24..60`).  Q2.md's wording
  "cap no better than `89N^2/900`" is the correct direction (a lower bound on the
  cap) but §7's summary invites the opposite reading.  R4's actual conclusion —
  purely local is weaker than the record's `1/16` — stands a fortiori.
* **No ALL-feasible configuration violates the bound anywhere**, `h <= 7`,
  `N <= 60`: the conjecture holds on everything searched.

---

## 7. Protocol checks (item 3 of the brief)

* **Float on an acceptance path**: none.  `Q2_finite.cpp` compares `25M/N^2` by
  `__int128` cross-multiplication; the Python scripts use `int`/`Fraction`.  The
  single float script `Q2_family.py` is quarantined by the report itself and
  carries no claim.  My re-implementations are exact throughout.
* **A `psi` value below `1/25` reported as a maximum at odd girth 5**: N/A —
  Q2 works with `25|M| <= N^2` at a fixed cut.  The one blow-up minimum used,
  `bip(C5[w]) = min_i w_i w_{i+1}`, is exhaustive over the `2^5` corners and I
  cross-checked it by full `2^(N-1)` brute force at `N = 12`.
* **Zero weights**: allowed everywhere (`Q2_finite.cpp` composition loop starts
  at 0 and guards `sigma >= 0` by `a_i > 0`); my own `h=7` STAR champion at
  `N=24` actually uses a zero weight.
* **A claimed exhaustive range the loop bounds do not cover**: FOUND — item 2
  (`N = 45` is an `h <= 5` run reported as a value of the `h <= 6` row).
* **Circularity**: none found.
* **Quoted theorem with mismatched hypotheses**: none quoted.
* **Asymptotics as exact**: two mild cases, both labelled as limits in the text —
  `|S|/N -> 1/8` for `W_b` (finite values are all above `1/8`, `0.1634` at
  `b=50`) and "`h<=5` LOC ceiling `1/16`" (exact finite values `1/19.2, 1/18,
  1/18.4` at `N=24,36,45`, approaching `1/16` from below).

## 8. Mandated round5 regression (item 2 of the brief)

`audit_Q2_v2_f_out.txt`, all ten witnesses of
`round5/claude_witness_regression.py`, exact, every part-respecting cut:

```
witness                  m   N   25*bip/N^2   LOC     STAR    ALL
W1 half-arc killer       8   7   25/49        25/49   25/49   25/49
W1' Gamma_11            11   7   25/49        25/49   25/49   25/49
W1'' Gamma_16           16   7   25/49        25/49   25/49   25/49
W2 five-atom extremal    5   5   1            1       1       1
W3 uniform Gamma_18     18  18   25/54        25/54   25/54   25/54
W4 uniform Gamma_20     20  20   3/4          3/4     3/4     3/4
W5 three-atom near-path 12   9   0            0       0       0
W6 seven-atom            7   7   25/49        25/49   25/49   25/49
W8 far-regular Wagner   14   8   25/32        25/32   25/32   25/32
W7 unequal five-atom    20  10   1/4          1/4     1/4     1/4
```

No witness exceeds `1`; on every one of them the LOC/STAR ceilings coincide with
the true value, so nothing in Q2's machinery misfires there.
**Exact tightness on `C5[n]`**: `25*bip/N^2 = 1` exactly for `n = 1..8`, and both
the LOC and STAR ceilings are exactly `1` there — the required tightness holds.

---

## 9. Files (all under `E:\Projects\ErdosProblems\problems\23\round7\`)

| file | what |
|---|---|
| `audit_Q2.md` | this report |
| `audit_Q2_v2_core.py` | auditor's primitives (graph6, max-cut, switching algebra) |
| `audit_Q2_v2_a.py` / `_a_out.txt` | L1, L2, C5[n] ledger, `W_b` table (finds the `b=10` falsifier) |
| `audit_Q2_v2_b.py` / `_b_out.txt` | `W*(u,r)` closed forms, min switch `u<=12`, `(*)`/SUP/NBRU/PAIRNBR |
| `audit_Q2_v2_c.py` / `_c_out.txt` | exhaustive maximal triangle-free `N<=12` |
| `audit_Q2_v2_d.cpp` / `.exe`, `_d_out.txt`, `_d_big.txt`, `_d_h7.txt` | auditor's ceiling search, `h<=6` and `h=7` |
| `audit_Q2_v2_e.py` / `_e_out.txt` | vertex-level dissection of the `N=45` falsifier, `EEj_`, `ECxo` |
| `audit_Q2_v2_f.py` / `_f_out.txt` | round5 ten-witness regression, Facts 2.1/2.2, `W_b` uniqueness |
| `audit_v2_h.g6`, `audit_v2_h35.g6`, `audit_v2_h7.g6` | pattern lists (own geng runs) |

An earlier partial audit pass left `audit_Q2_a_lemmas.py`, `audit_Q2_b_wstar.py`,
`audit_Q2_c_switch.py`, `audit_Q2_d_exhaust.py` and their `_out.txt` in this
directory; this report does not rely on them.  Where they overlap (L1, L2,
`W_b` `b=10`, `W*` min switch, the 278/587/15 census) my independent
implementation agrees with them.
