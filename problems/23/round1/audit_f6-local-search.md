# ADVERSARIAL AUDIT — Erdős #23, family F6 (`f6_local_search.md`)

Auditor: independent re-derivation + independently written code, exact integer/rational
arithmetic throughout. Nothing below reuses the F6 scripts except where explicitly labelled
"their own script".

Audit artifacts (all written from scratch by the auditor):

```
<scratch>/audit_f6/aud1_named.py        independent bip / alpha / w / m-Dmax for the §4 table
<scratch>/audit_f6/aud2_higmansims.py   Higman-Sims from the QR Golay code + exact bip resolution
<scratch>/audit_f6/aud3_family_blowup.py  own G(p,t), Delta by RECOUNT, blow-up lemma, iso checks
<scratch>/audit_f6/aud4_sharpness.py    adversarial sweep against OBSTRUCTION #9
<scratch>/audit_f6/aud5_c32.py          exact audit of the 1/16 witness
<scratch>/audit_f6/aud_census.cpp/.exe  own census (e[mask] DP, no Gray code), N = 3..13
<scratch>/audit_f6/aud_moves.cpp/.exe   own F_C(N), Delta by recount, classes evaluated STANDALONE
<scratch>/audit_f6/aud_moves12.cpp/.exe lean N = 12 sweep for Theorem B'
<scratch>/audit_f6/aud_thmA.cpp/.exe    falsification sweep for Theorem A over the whole census
```
(`<scratch>` = `C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\461052bb-8cbc-4d9f-996c-62e0fcc0bfcb\scratchpad`)

Generator: `E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe -tq N`.

---

## 1. MOST SERIOUS — OBSTRUCTION #9 IS **REFUTED AS SHARP**. The true worst case of `min(⌊m/2⌋, m−w)` is **exactly `N²/16`**, not `≥ 10/169`.

The report states (§4, "Obstruction (sharp)", repeated in §7 row 9 and in the cover note
"F6 cannot get below `0.0592N²`, period"):

> Its worst case over triangle-free graphs is pinned to `[10/169, 1/16] = [0.05917, 0.0625]`
> … no argument using only random/locally-optimal cuts and independent-set cuts can prove
> `bip ≤ cN²` for any `c < 10/169 ≈ 0.0592`, i.e. for any constant within a factor `1.48`
> of the conjecture.
> Exhaustive confirmation that `10/169` is the true optimum for `N ≤ 13` …

The `N ≤ 13` census is correct (I reproduced it, §6 below) but the extrapolation is false.
**Counter-witness, verified exactly and twice independently:**

| graph | `N` | `m` | reg | `α` | `w` | `⌊m/2⌋` | `m−w` | `min` | `min/N²` | true `bip` |
|---|---|---|---|---|---|---|---|---|---|---|
| `C32(1,4,6,15)` | 32 | 128 | 8 | **8** | 64 | 64 | 64 | **64** | **`1/16` = .0625** | **32** |

* Triangle-freeness: proved twice — by the exact difference-set test on
  `±S = {1,4,6,15,17,26,28,31} (mod 32)` (no two elements sum into `±S`) and by explicit
  enumeration of all `C(32,3) = 4960` triples (0 triangles).
* `α = 8`: OR-Tools CP-SAT, status **OPTIMAL**, proved bound 8 (and my own branch&bound agrees).
  8-regular ⟹ `w = 8α = 64`; CP-SAT max-weight-IS independently returns `w = 64`.
* `⌊m/2⌋ = m − w = 64 = N²/16` — the Theorem-A ceiling is **attained**, not approached.
* `bip = 32`: CP-SAT maxcut `= 96`, status **OPTIMAL**, proved bound 96 ⟹ `bip = 128−96 = 32`.
  `32 < 40.96 = N²/25`, so this is **not** a counterexample to Erdős #23 (ratio `1/32`).

By the report's own Lemma 4.1 (which I re-verified, §5), the balanced blow-ups
`C32(1,4,6,15)[r]` give an **infinite family** with `N = 32r`, `m = 128r²`, `w = 64r²`,
`min(⌊m/2⌋, m−w) = 64r² = N²/16` exactly, while `bip = 32r² = N²/32`.

Consequences:

* The correct statement is: **the worst case of `min(⌊m/2⌋, m−w)` over triangle-free graphs
  is exactly `1/16`**; Theorem A is *tight*, and the interval `[10/169, 1/16]` collapses to
  its upper endpoint.
* The advertised factor `1.48` is wrong; the correct factor is `25/16 = 1.5625`.
* The cover claim "F6 cannot get below `0.0592N²`, period" must read "**F6 cannot get below
  `0.0625 N²`**".
* `10/169` was a small-`N` artifact. My per-`n` sweep of triangle-free circulants
  `C_n(S), |S| ≤ 4` already beats `10/169` from `n = 20` on:
  `n=20: 3/50`, `21: 3/49`, `24: 35/576`, `26: 21/338`, `28: 3/49`, `30: 14/225`,
  `31: 60/961`, **`32: 1/16`**. 121 circulants in the sweep exceed `10/169`.

This is an obstruction that got *stronger*, so it does not resurrect a killed route — but the
number quoted throughout the deliverable is wrong, and the report explicitly labels it
"(sharp)" and "exhaustively confirmed".

---

## 2. CIRCULAR — the §9 "Missing Lemma" is logically **equivalent to Erdős #23 itself**

Verbatim from §9:

> **`bip(G) ≤ m − w(G) − γ(G)` with `γ(G) ≥ m − w(G) − N²/25`**

Substituting the second inequality into the first gives, immediately and with no further
hypothesis, `bip(G) ≤ m − w − (m − w − N²/25) = N²/25`. Conversely `bip ≤ N²/25` supplies
`γ := m − w − N²/25` (which is `≥ 0` exactly when the lemma is non-vacuous, and when it is
negative the conclusion is already implied by `bip ≤ m−w`). So the Missing Lemma, restricted
to the stated window `2N²/25 < m < N²/5`, is **exactly** the conjecture on that window; and
the report's own §3 disposes of `m ≤ 2N²/25` and `m ≥ N²/5`. Therefore

> **Missing Lemma ⟺ Erdős #23.**

Under the campaign rules this makes the family's stated forward path vacuous: the "one missing
statement" has strength equal to the target. There is no reduction here, only a restatement.
(The report is honest that it is stuck; the point is that what it is stuck *on* is the whole
problem, not a lemma.)

---

## 3. GAP / NOT-REPRODUCED — the `N(v)`, `N[v]` and cut-star rows of the §5 table are **not** the classes they are labelled with

`moves.cpp` only evaluates `okNB()`, `okNC()`, `okCS()` inside `if(gk>=1){…}`, i.e. only at
cuts that are already **single-vertex** locally optimal. So the printed
`F_{N(v)}`, `F_{N[v]}`, `F_{cut-star}` are `F_{𝓒 ∧ |S|≤1}`, not `F_𝓒`. My `aud_moves.exe`
evaluates each class standalone (and computes `Δ` by recounting monochromatic edges rather
than from identity (0.1)):

| class | `N=8` | `N=9` | `N=10` | `N=11` | report says |
|---|---|---|---|---|---|
| `F_{N(v)}` standalone | 8 | **10** | 12 | **15** | 8 / 8 / 12 / 12 |
| `F_{N[v]}` standalone | 8 | **9** | 12 | **14** | 8 / 8 / 12 / 12 |
| `F_{cut-star}` standalone | **3** | 4 | 5 | 6 | 2 / 4 / 5 / 6 |

Hence §1.3's

> Confirmed computationally: `F_{N(v)}(N) = F_{|S|≤1}(N)` for every `N ≤ 12`

is **not** a confirmation of anything: the code can only ever return that answer, because
Prop. 1.3 says exactly that `Δ(N(v)) ≥ 0` is automatic once `s ≥ 0`, and `s ≥ 0` is the gate
the code applies before testing. The claim as literally written (about the standalone class)
is **false** at `N = 9` and `N = 11`.

Impact: **none on the obstructions.** The headline classes (`|S| ≤ k`, full star class,
combined) all contain the singletons, so they are unaffected; I reproduced every one of them
exactly (§6).

---

## 4. GAP — Theorem B is false at its own boundary `t = p`; Corollary B2 is proved only for `N ≡ 0 (mod 4)`

**(a) `t = p`.** The family is declared for `0 ≤ t ≤ p` and Theorem B asserts, for every
`t ≥ 1`, "there is an `S` with `|S| = 2t+1` and `Δ(S) < 0`". The proof takes `t` vertices of
`X₁` and `t+1` of `Y₂` — which needs `t+1 ≤ p`, i.e. `t < p`. At `t = p` the statement is
false, and I verified this exhaustively with my own recount-based `Δ`:

```
G(2,2): N=8  |M|=0  minDelta by size: k=1:2 k=2:2 k=3:2 k=4:0 k=5:+2   (no improving set)
G(3,3): N=12 |M|=0  minDelta ... k=6:0 k=7:+3                          (no improving set)
```
(Harmless: at `t = p`, `|M| = 0 = bip`, so the cut is globally optimal. Their own
`f6_family_Gpt.py` only tests `t < p`, so the error is in the statement, not the code.)

**(b) `N ≢ 0 (mod 4)`.** `G(p,t)` exists only for `N = 4p`. Corollary B1 states its
`N ≡ 0 (mod 4)` hypothesis; **Corollary B2 does not**, yet its proof invokes `G(N/4, t)`.
Padding with `N mod 4` isolated vertices is legitimate (isolated vertices contribute 0 to
every `Δ`, so local optimality is preserved and `|M|` is unchanged), but the padded family
falls 1–2 short of the stated threshold `k < 0.34N − 1` at, e.g.,
`N = 13,14,15,18,19,23,25,26,27,30,31,35,37,38,39,62,63,101,102,103`
(exact table in `aud3_family_blowup.py` output). Example: `N = 101`, padded family covers
`k ≤ 32`, statement claims all `k < 33.34`.
The **asymptotic** content ("moves of size `≥ 0.34N − O(1)` are necessary") is confirmed;
the literal inequality is proved only for `4 | N`.

For `4 | N` the constant is exactly right — I recomputed it: at `N = 100` the largest `k`
still defeated is `32` (statement: `k < 33`); at `N = 1000` it is `338` (statement: `k < 339`).

---

## 5. CONFIRMED — everything else, reproduced exactly

### 5.1 Move calculus (§0–§1.4) — CONFIRMED
Identity `(0.1) Δ(S) = Σ_{v∈S}s(v) − 2(cut_S − mono_S)` cross-checked against a from-scratch
recount of monochromatic edges: **6 932 780 580 + 333 535 290 + 20 976 120 + 1 776 924 checks,
0 failures** over the complete triangle-free censuses `N = 8,9,10,11` and all their cuts.
`(0.2)` follows algebraically. The pair classification, `Δ(N[v]) = Σ_{u∈N(v)}s(u) − s(v)`, and
the star collapse `s(v) ≥ Σ_{u∈N_C(v)}(2−s(u))⁺` are all correct; triangle-freeness is
**genuinely used** (independence of `N(v)`) in §1.3, §1.4 and in `w ≥ max_v D_v`. My
`aud_moves.exe` brute-forces the **entire** `2^{d(v)}` star class rather than using the
collapsed inequality and gets the same `F_{STAR}` values (2, 3, 4, 6, 8 for `N = 8..12`),
so the collapse is validated, not assumed.

### 5.2 Theorem A + density window (§3) — CONFIRMED
Proof re-derived line by line; no divisibility, connectivity, regularity or minimum-degree
assumption is used or needed. `f(x) = x − 4x²` peaks at `x = 1/8` with `f = 1/16`;
`4x² − x + 1/25 ≥ 0 ⟺ x ≤ 1/20 or x ≥ 1/5`; union with `x ≤ 2/25` is `x ≤ 2/25 or x ≥ 1/5`.
Exact.

Falsification sweep (`aud_thmA.exe`) over the **complete** censuses `N = 5..12`
(1 381 889 graphs, includes disconnected graphs, isolated vertices, odd `N`, `N ∤ 5`):

```
bip > ⌊m/2⌋ : 0    bip > m−Dmax : 0    bip > m−w : 0    16·bip > N² : 0
window violations : 0    conjecture violations : 0
```

Exact equality of the whole chain on `C5[n]` re-verified: `m − Dmax = m − w = m − Σd²/N =
m − 4m²/N² = 4n²`, `bip = n² = N²/25`.

*Caveat (not an error):* `bip ≤ N²/16` is far weaker than the published record
(`0.0409N²`, Balogh–Clemen–Lidický, cited by the report itself), so §3 contributes no new
mathematics; only the density-window corollary is not literally subsumed, and by §1 above it
can never be improved past `1/16` inside this family.

### 5.3 Blow-up lemma (§4.1) — CONFIRMED
Exchange argument is correct (all neighbours of a class lie outside it; the cost function
`c` is the same for all vertices of the class; moving the whole class to `argmin c` cannot
increase the count; iterate). No triangle-freeness needed, correctly stated for arbitrary `H`.
Full brute force over all `2^{N−1}` cuts, my own code, including a **new** case not in their
script: `Petersen[2]`, `N = 20`, `bip = 12 = 4·3`. All MATCH.

### 5.4 §4 refutation table — CONFIRMED EXACTLY (and one open cell closed)
My independent constructions (Clebsch as the folded 5-cube, `C13(1,5)` as a circulant,
Chvátal from the 1970 edge list, Wagner as `C8(1,4)`) and my own MWIS branch&bound + full
`2^{N−1}` cut enumeration:

| graph | `N` | `m` | `α` | `w` | `m−w` | `(m−w)/N²` | true `bip` | report |
|---|---|---|---|---|---|---|---|---|
| Wagner `C8(1,4)` | 8 | 12 | 3 | 9 | 3 | 3/64 | 2 | ✓ |
| Chvátal | 12 | 24 | 4 | 16 | 8 | 1/18 | 4 | ✓ |
| `C13(1,5)` | 13 | 26 | 4 | 16 | 10 | 10/169 | 6 | ✓ |
| Clebsch | 16 | 40 | 5 | 25 | 15 | 15/256 | 8 | ✓ |
| Higman–Sims | 100 | 1100 | 22 | 484 | 616 | 77/1250 | **350** | report: "≤ 550" |

Higman–Sims built **independently** from the quadratic-residue `[23,12,7]` Golay code (a
different generator from the report's `[I|B]` matrix), extended, weight enumerator
`1,759,2576,759,1` verified, parameters `srg(100,22,0,6)` verified exactly (`k=22, λ=0, μ=6`),
which identifies the graph by Gewirtz uniqueness. `α = 22` by my own branch&bound.

**The report left `bip(HiS)` undetermined ("≤ 550 (Thm A)").** That interval contains
`N²/25 = 400`, i.e. as written the report does not rule out that Higman–Sims is a
counterexample to Erdős #23. I closed it: the eigenvalue bound with `λ_min = −8` gives
`maxcut ≤ N(k−λ_min)/4 = 750 ⟹ bip ≥ 350`, and local search finds a cut with exactly 350
monochromatic edges (a 50/50 split into two 7-regular halves — the Hoffman–Singleton
decomposition). Hence **`bip(HiS) = 350 = 0.035 N² < 0.04 N²`. No counterexample.**

### 5.5 Theorem B / B′ and `F_combined(12) = 6` — CONFIRMED
My own `G(p,t)` builder + `Δ` by full recount, exhaustive over all `S` up to size `2t+1`:
`(p,t) ∈ {(2,1),(3,1),(3,2),(4,1),(4,2),(4,3),(5,1),(5,2),(6,2)}` all give `|M| = N²/8 − tN/2`,
`s ≡ t`, `Δ ≥ 0` for `|S| ≤ 2t`, first negative at `|S| = 2t+1`. Proof of Theorem B is
correct: `cut_S = a₁b₂ + a₂b₁ ≤ (a₁+a₂)(b₁+b₂) ≤ |S|²/4`, giving `Δ ≥ t|S| − |S|²/2 ≥ 0`
for `|S| ≤ 2t`.

Independent exhaustive `N = 12` sweep over all **1 262 180** triangle-free graphs and all
`2^{11}` cuts (`aud_moves12.exe`, 8m39s):

```
F_{|S|<=1}(12) = 18 = N^2/8        F_{|S|<=2}(12) = 12        F_{|S|<=3}(12) = 9
F_{|S|<=4}(12) =  6 = N^2/8 - N    F_{STAR}(12)   =  8        F_{COMBINED}(12) = 6
```
`6 > 5.76 = N²/25` ✓, and `N = 12` is indeed the smallest `N` at which the combined class
fails (`F_comb = 2, 2, 4, 4, 6` for `N = 8..12` vs `N²/25 = 2.56, 3.24, 4.00, 4.84, 5.76`).

**But:** the report's identification of the extremal witness is wrong. §5 says
"`F_{|S|≤4}(12) = 6` … **exactly `G(3,2)`** of Theorem B'". The witness graph is
`K??FFB_vDwN_`, and their own `f6_final_checks.py` prints

```
  witness: N=12 m=24 bipartite=True
  G(3,2):  N=12 m=24 bipartite=True
  isomorphic? False
```
My `networkx` check agrees: **not isomorphic**. `G(3,2)` does attain 6 (verified), and 6 is
the maximum (verified), so the *value* stands; the *identification* is refuted by the report's
own script.

### 5.6 Census `N ≤ 13` (§5) — CONFIRMED (with two corrections)
My own census (`e[mask]` edge-count DP + `mono(B) = e[B] + e[~B]`, no Gray code; MWIS DP
branching on the highest bit) over `geng -tq N`:

| `N` | #graphs | max `bip` | #extremisers | max `min(⌊m/2⌋,m−w)/N²` |
|---|---|---|---|---|
| 5 | 14 | 1 | **1** (`DUW` ≅ `C5`) | .040000 |
| 6 | 38 | 1 | 3 | .027778 |
| 7 | 107 | 1 | 19 | .020408 |
| 8 | 410 | 2 | 7 | .046875 |
| 9 | 1 897 | **2** (`< 3 = ⌊81/25⌋`) | 86 | .037037 |
| 10 | 12 172 | 4 | **1** (`I?rFf_{N?` ≅ `C5[2]`, iso-verified) | .040000 |
| 11 | 105 071 | 4 | 14 | .049587 |
| 12 | 1 262 180 | 5 | 2 | .055556 (Chvátal) |
| 13 | 20 797 002 | 6 | **8** | .059172 (`C13(1,5)`, iso-verified) |

Every number in the report's §5 table reproduces. Two corrections:

* **Total graph count.** `Σ_{N=3..13} = 22 178 901`, not the reported **22 178 977**
  (off by 76). The per-`N` counts in the table are individually correct (= OEIS A006785).
* **C5-homomorphism claim.** §5 says the `N = 13` extremisers are "eight graphs, `bip = 6` …
  **neither homomorphic to `C5` or `C7`**". Four of the eight **are** `C5`-homomorphic —
  and this is confirmed by *their own* `decode.py`:
  ```
  L??ED@_~?~^_Fw  N=13 m=30 bip=6  hom to C5? True   hom to C7? False
  L??FFB_~?~^_Fw  N=13 m=33 bip=6  hom to C5? True   hom to C7? False
  ```
  (also `L??EDB_~?~^_Fw`, `L??EFB_~FwB{Fw`). The other four, including `C13(1,5)`, are not.
  The separate claim "ratio `1/25` attained only at `N = 5, 10`, uniquely by `C5` and `C5[2]`"
  is CONFIRMED, so "no non-blow-up graph ties the `C5[n]` ratio for `N ≤ 13`" survives.
* Their `census_N13b.txt` prints only 6 of the 8 extremisers; the two missing are
  `L?`DAboUdIF_Bw` and `L?`DE`gl@YJODg` (`= C13(1,5)`).

### 5.7 Minor errors
* §5 "Readings": "`F_{|S|≤1}(N) = ⌊N²/8⌋` exactly at `N ≡ 0 (mod 4)`" — false at `N = 10`,
  where `F_{|S|≤1}(10) = 12 = ⌊100/8⌋` (verified in two independent programs).
* §6 "Stall 1": the configuration `K_{N/4,N/4} ⊔ K_{N/4,N/4}` does **not** stall algorithm
  NC-LS as specified. Its step 2 is "the best independent-set cut", and there `w = m`
  (take one side of each component), so `m − w = 0` and the certificate equals the truth `0`.
  Verified for `N = 8,12,16,20`. `N²/16` is only the value of the *degree-averaged surrogate*
  `m − max_v D_v`. Stall 1 is a stall of a weakened bound, not of the stated algorithm.
* §0's "no argument that uses only the inequalities `{Δ(S) ≥ 0}` plus triangle-freeness can
  prove anything smaller [than `F_𝓒(N)`]" is correct as literally stated, but note the
  scope: it rules out bounds valid at *every* `𝓒`-locally-optimal cut. It does **not** rule
  out arguments that select a particular locally optimal cut — on `G(p,2)` itself the optimal
  cut (`|M| = 0`) is `𝓒`-locally optimal for every class considered. Any future F6-style
  work must respect this distinction; the report's §6 conclusion about *algorithms* is fine.

---

## 6. Answers to the standing audit questions

1. **Completeness / gaps.** §1–§4 proofs are complete apart from the two boundary gaps in
   §4 above (`t = p` in Theorem B; `4 ∤ N` in Corollary B2). §9's "missing statement" is not
   a gap but a restatement of the target.
2. **Triangle-freeness.** Genuinely invoked, never merely assumed: §1.1 (Mantel),
   §1.3/§1.4 (`N(v)` independent), Theorem A (`w ≥ max_v D_v`). Lemma 4.1 correctly does
   *not* use it. The `G(p,t)` family is bipartite, so triangle-freeness is automatic.
3. **Max-cut vs locally optimal cut.** No confusion found. `bip = m − maxcut` is used only
   where an *upper* bound on `bip` is asserted from an *exhibited* cut (random `⟹ m/2`,
   independent-set cut `⟹ m − w`), which is sound. `F_𝓒(N)` is correctly defined over
   locally optimal cuts. The only scoping subtlety is §5.7 bullet 3.
4. **Hidden hypotheses.** `N ≡ 0 (mod 4)` is genuinely needed for `G(p,t)`, declared in
   Cor. B1, **omitted** in Cor. B2 (§4b). `N` odd, `N ∤ 5`, disconnected `G` and isolated
   vertices are all covered by the census (`geng -t` emits disconnected graphs; counts match
   A006785) and by Theorem A, which is parity-free — 0 violations in 1 381 889 graphs.
   No regularity or min-degree assumption is smuggled in.
5. **Constant survival.** No `1/25 + ε` and no hidden `o(N²)`: everything is exact rational.
   `1/25` appears only as the *target*; F6's own output is `1/16` exactly (§1).
6. **Circularity.** §9's Missing Lemma has strength `=` the conjecture (§2). Everything else
   is strictly weaker than the conjecture and non-circular.
7. **Reproduction.** All four F6 python scripts run and pass their own assertions on this
   machine. My independent census/moves/graph computations agree with theirs on every value
   except the three listed above (standalone `N(v)`/`N[v]`/cut-star, the 22 178 977 total,
   the `C5`-homomorphism claim), plus the wrong witness identification and the refuted
   sharpness of `10/169`.
8. **Obstruction verification.** Cor. B2 (bounded moves) — verified exactly, obstruction is
   REAL. Theorem B' / `F_combined(12) = 6` — verified exactly over all 1 262 180 graphs,
   obstruction is REAL. Obstruction #9 — REFUTED as sharp, and the corrected version is
   *stronger* (§1). No false obstruction kills a live route here.

---

## 7. VERDICT

**BLOCKED.**

Reason: F6's entire proof engine is the single certificate `C(G) = min(⌊m/2⌋, m − w(G))`
(plus local moves, which §2 shows are capped at `N²/8` for bounded size). Its worst case is
**exactly** the conjecture-irrelevant constant `1/16`, and the only route the report proposes
out of that is a lemma equivalent to the conjecture.

**Blocking lemma (verbatim, as it should be recorded in the registry):**

> **F6 blocking lemma.** For a graph `G` with `m` edges let
> `w(G) = max{ Σ_{u∈I} d(u) : I ⊆ V(G) independent }` and
> `C(G) = min( ⌊m/2⌋ , m − w(G) )`. Then
> (i) `bip(G) ≤ C(G)` for every graph `G`, and `C(G) ≤ N²/16` for every triangle-free `G`
> on `N` vertices; and
> (ii) `C(G) = N²/16` **exactly** on the infinite family of triangle-free graphs
> `G_r := C_{32}(1,4,6,15)[r]` (`N = 32r`, `m = 128r²`, `α(G_r) = 8r`, `w(G_r) = 64r²`,
> `⌊m/2⌋ = m − w = 64r² = N²/16`), while `bip(G_r) = 32r² = N²/32`.
> Consequently no bound derived solely from random cuts, single-vertex-locally-optimal cuts
> and independent-set cuts can prove `bip(G) ≤ cN²` for any `c < 1/16 = 0.0625`, a factor
> `25/16 = 1.5625` above the conjectured `1/25`.
> Moreover (Corollary B2, `N ≡ 0 mod 4`) no move class all of whose members have size
> `≤ k < 0.34N − 1` can certify `bip ≤ N²/25`, since `G(N/4, ⌈k/2⌉)` has a locally optimal
> cut with `|M| = N²/8 − ⌈k/2⌉N/2 > N²/25` and `bip = 0`.

Salvageable by-products worth keeping in the registry (all verified):
`bip(HiS) = 350`; `bip(C32(1,4,6,15)) = 32`; the census table `N ≤ 13`; Lemma 4.1;
Theorem A with its exact tightness; the `G(p,t)` stalling family.
