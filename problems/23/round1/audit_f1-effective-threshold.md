# ADVERSARIAL AUDIT — Erdős #23, Family F1 ("EFFECTIVE THRESHOLD")

**Target of audit:** `E:/Projects/ErdosProblems/problems/23/round1/F1.md` and all `f1_*` scripts
alongside it.
**Auditor stance:** break the claims. Every computation re-run with independently written code
(`aud_bip.cpp`, `aud_bip2.cpp`, `aud_bounds.py`, `aud_phi.py`, `aud_wit.py`, `aud_chi.py`,
`aud_beta.py`, `aud_and.py`, in the audit scratchpad
`C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/461052bb-8cbc-4d9f-996c-62e0fcc0bfcb/scratchpad/`).
All arithmetic exact (C++ integers / Python `Fraction`).
Notation as in F1.md: `a(N) = max{bip(G) : G triangle-free, |V|=N}`, `bip = e − maxcut`,
`(E)` is `a(N) ≤ N²/25`.

---

## 0. Verdict headline

**FAMILY F1 → BLOCKED.**  The blocking lemma is F1.md's own Theorem 4, which I confirm.
But **three of the four items F1.md flags as "OBSTRUCTION" are themselves wrong or vacuous**, and
the one deliverable it proposes as a live follow-up target (§9 item 4) is provably already a
theorem. Those must not be propagated to other families.

---

## 1. MOST SERIOUS FINDING — two of the four "OBSTRUCTIONS" are refuted by F1.md's own Lemma 2

### 1.1 The statement being audited

F1.md summary row 10 (Theorem 10):

> "Consequently there is **no slack** at non-multiples of five. Any interpolation/deletion argument
> that loses even `Ω(1)` per removed vertex is dead."

F1.md summary row 13 (Theorem 13):

> "Hence any proof scheme whose unique sharp case is '`C5` blow-ups' cannot be sharp at
> `N ≢ 0 (mod 5)`; **it must also be tight on Grötzsch-type and Ramsey-type graphs.**"

### 1.2 Why they are false

Apply F1.md's own Corollary 2.1 `a(5M) ≥ 25·a(M)` with `t = 5`:

> **Lemma (auditor).** If `(E)` holds for every `N ≡ 0 (mod 5)` then `(E)` holds for every `N`.
> *Proof.* Let `M ≥ 1`. Then `25·a(M) ≤ a(5M) ≤ (5M)²/25 = M²`, so `a(M) ≤ M²/25`. ∎

This is one line, uses nothing beyond Lemma 2 / Corollary 2.1 of F1.md itself, and it says:
**a proof of (E) is never required at any `N` that is not a multiple of 5.**  Consequently

* Theorem 10's obstruction ("no slack at non-multiples of five ⟹ interpolation/deletion is dead")
  obstructs nothing: no argument is ever required to step through `N ≢ 0 (mod 5)`;
* Theorem 13's "**it must also be tight** on Grötzsch-type and Ramsey-type graphs" is **false**.
  A scheme that is sharp only on `C5` blow-ups and proves `(E)` only at `5 | N` is a complete proof.
  Indeed my exhaustive scans below show that at `N = 5, 10, 15` the extremal graph is the *unique*
  `C5` blow-up, so at multiples of five the sharp case really is only `C5[t]`.

The same argument generalises: `(E)` on any set `S` such that every `M` has a multiple in `S`
(multiples of 5, tails `N ≥ N0`, `{5m : m ≥ m0}`, …) implies `(E)` everywhere. F1.md proves the
tail case (Theorem 4) and then *fails to notice that it kills its own Theorems 10 and 13*.

### 1.3 A second, independent error inside Theorem 10

The quantitative clause "any interpolation/deletion argument that loses even `Ω(1)` per removed
vertex is dead" is false in the only regime that matters. The step size of the target is

```
   ⌊N²/25⌋ − ⌊(N−1)²/25⌋  ≈  (2N−1)/25  =  Θ(N),
```

so a deletion argument may afford to lose up to `≈ 0.08N` per removed vertex — F1.md's own
Theorem 14(i) is built on exactly that budget. The "no slack" phenomenon is a small-`N` artefact of
the floor function (steps of 0 or 1 for `N ≤ 15`), and by §1.2 small `N` never has to be proved.

**VERDICT: Theorem 10 obstruction — REFUTED. Theorem 13 obstruction — REFUTED.**
(The underlying *computations* behind both — the exact `a(N)` values and the extremal-graph lists —
are CONFIRMED; see §5. It is the inferences drawn from them that fail.)

---

## 2. SECOND FINDING — the "best new target coming out of this round" (§9 item 4) is vacuous

F1.md §9 item 4 and the round report both call this

> "the most promising genuinely-new target coming out of this round:
> *prove `min_{S ⊆ Z_{3d−1}} Σ_{ij ∈ E(And(d)), ij uncut by S} t_i t_j ≤ (Σ t)²/25`
> for every `d ≥ 2` and every non-negative `t`*",

motivated (F1.md §5, §9) by: "*a counterexample with `δ > 10N/29` would force `β(And(d)) > 1/25`
for some `d`*", via Jin (`δ > 10n/29 ⟹ χ ≤ 3`) + Chen–Jin–Koh (`δ > n/3`, `χ ≤ 3` ⟹ `G → And(d)`).

**That whole regime is already closed — by F1.md's own Corollary 5.1.**

Chen–Jin–Koh needs `δ(G) > N/3`. Any triangle-free `G` with `δ > N/3` has

```
   2e(G)/N²  ≥  δ(G)/N  >  1/3 = 0.3333…  >  0.3197 ,
```

and the class `{G : 2e/N² ≥ 0.3197}` **is** closed under balanced blow-up (`2e/N²` is exactly
blow-up invariant). So Theorem 5(b) applied to Balogh–Clemen–Lidický Theorem 2(b) gives
`bip(G) ≤ N²/25` for **every** such `G` at **every** `N`. Jin's `10/29 = 0.34483` is even deeper
inside the proved region.

Worse, the corrected density constraint (§3 below) gives `δ(G) < 0.3197 N < N/3` for any minimal
counterexample, so **Chen–Jin–Koh can never be applied to a counterexample at all** — its
hypothesis is incompatible with the constraint F1.md itself derives.

Numerically re-verified (`aud_and.py`): for `And(d)`, `n = 3d−1`, `deg = d`,
`δ/n = 2e/n² = d/(3d−1)`:

```
 And(2) n= 5 δ/n=0.40000   And(3) n= 8 0.37500   And(4) n=11 0.36364
 And(5) n=14 0.35714       And(6) n=17 0.35294   →  limit 1/3 = 0.33333  > 0.3197 for all d
```

**VERDICT: §9 item 4 — REFUTED as a new target.** Its only stated consequence is already a
theorem; the structure theory it relies on cannot reach any counterexample.

---

## 3. THIRD FINDING — Corollary 5.2 / Theorem 14(iii): the density window is stated in the wrong
normalisation and is FALSE as written

F1.md Corollary 5.2 (and Theorem 14(iii)) states:

> "If `G` is triangle-free with `bip(G) > |V(G)|²/25` then
> `0.2486 < e(G)/binom(N,2) < 0.3197`."

I fetched the source: Balogh–Clemen–Lidický, *Max Cuts in Triangle-free Graphs*, arXiv:2103.14179,
Theorem 2: "*Let `G` be a triangle-free graph on `n` vertices. Then, **for `n` large enough**,
(a) `D2(G) ≤ n²/23.5`, (b) `D2(G) ≤ n²/25` when `|E(G)| ≥ 0.3197 binom(n,2)`,
(c) `D2(G) ≤ n²/25` when `|E(G)| ≤ 0.2486 binom(n,2)`.*"
So the density is indeed `e/binom(n,2)` — and that is exactly the problem.

**`e/binom(n,2)` is NOT invariant under balanced blow-up.** For `G` on `N` vertices,

```
   e(G[t])/binom(tN,2)  =  (2e/N²) · tN/(tN−1)   ↓   2e/N²    (strictly decreasing in t).
```

Theorem 5(b) therefore does **not** apply to a window in `e/binom(n,2)`; F1.md's own parenthetical
in Theorem 5(b) — "(e.g. **an edge-density window**, …)" — names a class that is not blow-up-closed.
What the blow-up argument actually yields is the window in the invariant `ρ(G) := 2e(G)/N²`:

```
   ρ(G) < 0.2486  ⟹ (E) holds for G ;      ρ(G) ≥ 0.3197  ⟹ (E) holds for G ;
   so a counterexample has   0.2486 ≤ 2e(G)/N² < 0.3197,  i.e.  0.1243 N² ≤ e(G) < 0.15985 N².
```

(F1.md's *parenthetical* "`0.1243 N² ≲ e ≲ 0.1599 N²`" is the correct form; the displayed
`e/binom(N,2)` statement is not.) In `e/binom(N,2)` terms the correct window is
`0.2486·N/(N−1) < e/binom(N,2) < 0.3197·N/(N−1)`, which is *shifted upward*, not equal.

**Concrete failure.** At `N = 14`: the stated corollary excludes every graph with
`e ≥ 0.3197·binom(14,2) = 29.09`, i.e. `e ≥ 30`. The justified argument only excludes
`e ≥ 0.3197·14²/2 = 31.34`, i.e. `e ≥ 32`. My exhaustive `N = 14` scan finds **289 maximal
triangle-free graphs with `e ∈ {30, 31}`** (81 with `e = 30`, 208 with `e = 31`, e.g.
`M?`DAboUdIF_Bo?N_` with `e = 31`, `bip = 6`) which Corollary 5.2 as written declares
counterexample-free with no justification.

Downstream: Theorem 14(ii) `δ ≤ 3N/8 = 0.375N` is superseded by the corrected (iii), which gives
`δ(G) ≤ 2e/N < 0.3197 N`. So the true minimal-counterexample min-degree window is
`0.16N < δ < 0.3197N`, not `0.16N < δ ≤ 0.375N`.

**VERDICT: Corollary 5.2 and Theorem 14(iii) as stated — REFUTED (over-claim).**
Corrected version: CONFIRMED. Corollary 5.1 for `n²/23.5` (Theorem 5(a)): CONFIRMED.

---

## 4. FOURTH FINDING — the §6 β-scan is not evidence: the optimiser provably misses known global optima

F1.md §6 presents

```
 h :  5      6      7      8      9      10     11     12     13
 β : .040000 .039917 .039991 .039990 .039994 .040000 .039996 .039995 .039997
```

as "`β(H) ≤ 1/25` for all 670 maximal triangle-free `H` on `≤ 13` vertices … no counterexample."

**These numbers are not `β` values, and 7 of the 9 are provably strict undershoots.**
If a triangle-free `H` contains a 5-cycle, that cycle is automatically induced (a chord would make a
triangle), and putting `t = 1/5` on its five vertices and `0` elsewhere gives, in exact arithmetic,
`min_S q_S(t) = 1/25` — because only the `C5`-edges carry weight and a 2-colouring of `C5` leaves
at least one of them monochromatic. Hence `β(H) ≥ 1/25 = 0.040000` **exactly** for every such `H`.

Verified exactly (`aud_beta.py`, `Fraction` arithmetic, all `2^{h−1}` subsets enumerated):

```
 h= 5 #max-tf=  3 #containing C5= 1  exact β ≥ 1/25 = 0.040000  (DUW = C5)
 h= 6 #max-tf=  4 #containing C5= 1  exact β ≥ 1/25 = 0.040000  (ECxo)
 h= 7 #max-tf=  6 #containing C5= 3  exact β ≥ 1/25 = 0.040000
 h= 8 #max-tf= 10 #containing C5= 6  exact β ≥ 1/25 = 0.040000
 h= 9 #max-tf= 16 #containing C5=12  exact β ≥ 1/25 = 0.040000
 h=10 #max-tf= 31 #containing C5=26  exact β ≥ 1/25 = 0.040000
 h=11 #max-tf= 61 #containing C5=56  exact β ≥ 1/25 = 0.040000
```

I re-ran their own scanner (`python f1_beta_scan.py 5 7 60`) and reproduced
`h=6 → 0.039917`, `h=7 → 0.039991` exactly. So at `h = 6` the *reported maximum over all `H`* is
`8.3e-5` (0.21 % relative) **below** a value that is provably attained. Since the code only flags a
graph when the continuous ratio exceeds `0.04 + 1e-9`, any true counterexample with
`β ∈ (0.04, 0.04008]` would be silently missed. The scan is not a certificate in any direction and
its numbers should not be quoted as `β(H)`.

Same defect in `f1_andrasfai.py`: F1.md reports "`β ≈ 0.03996` in each case (the optimum
concentrates on an induced `C5`)". If the optimum concentrated on an induced `C5` the value would be
`0.040000`. Exactly (`aud_and.py`): `β(And(d)) ≥ 1/25` for `d = 2,…,6`, contradicting the reported
`0.03996`.

**VERDICT: §6 / summary row 15 — GAP (search carries no certification; the tabulated numbers are
mislabelled and demonstrably below the true optima). NOT-REPRODUCED for the Andrásfai `β` values.**
The exact-integer champion checks (`25·bip(H[t]) − (Σt)² = 0`) reproduce and are CONFIRMED.

---

## 5. Exact-computation claims: independently reproduced (and strengthened)

I rebuilt the whole pipeline from scratch (own graph6 decoder, own triangle-free test — I did *not*
trust `geng -t` — own Gray-code exact maxcut) and ran it over **all** triangle-free graphs (including
disconnected ones and ones with isolated vertices), not only the connected ones F1.md scanned.

| `N` | source | graphs read | maximal tri-free | `a(N)` | witness | `⌊N²/25⌋` |
|---|---|---|---|---|---|---|
| 5 | `geng -tq` ALL | 14 | 3 | **1** | `DUW` (`C5`) | 1 |
| 6 | ALL | 38 | 4 | **1** | | 1 |
| 7 | ALL | 107 | 6 | **1** | | 1 |
| 8 | ALL | 410 | 10 | **2** | | 2 |
| 9 | ALL | 1 897 | 16 | **2** | | **3** |
| 10 | ALL | 12 172 | 31 | **4** | `I?rFf_{N?` `=C5[2,2,2,2,2]` (unique) | 4 |
| 11 | ALL | 105 071 | 61 | **4** | 4 extremals | 4 |
| 12 | ALL | 1 262 180 | 147 | **5** | 2 extremals | 5 |
| 13 | ALL | 20 797 002 | 392 | **6** | 3 extremals | 6 |
| 14 | ALL | 467 871 369 | 1 274 | **7** | `M?AE@bH{AYN_LgBs?` (unique) | 7 |
| 15 | ALL | 14 232 552 452 | 5 036 | **9** | `N??FFB_~Fw^_FwFwB{?` `=C5[3,3,3,3,3]` (unique) | 9 |

* `a(N) = 1,1,1,2,2,4,4,5,6,7,9` for `N = 5..15` — **CONFIRMED**, matching F1.md exactly, including
  the exceptional `a(9) = 2 < 3 = ⌊81/25⌋`.
* Maximal-triangle-free counts `3,4,6,10,16,31,61,147,392,1274,5036` — **CONFIRMED** (A006855).
* `a(14) = 7` with a **unique** extremal graph — **CONFIRMED** (my `N = 14` shard run read exactly
  467 871 369 graphs = A006785(14), zero non-triangle-free, and found exactly one graph with
  `bip = 7`; `bip` distribution `0:7, 1:25, 2:79, 3:219, 4:417, 5:411, 6:115, 7:1`).
  F1.md's warning about a truncated early run is well taken — my own first `N = 15` attempt
  truncated the same way (14 090 791 935 of 14 232 552 452 graphs); I re-ran it with per-shard
  `geng` checksums.
* `N = 12` extremals `K?ABBBwerwBw` (25 edges, `χ = 3`) and `K?BD@g]Qvo^?` (25 edges, `χ = 4`),
  neither `C5`-colourable — **CONFIRMED**.
* `N = 13` extremals: `L??FFB_~?~^_Fw` (33 edges, `= C5[3,2,3,2,3]`, `C5`-colourable),
  `L?`DAboU`w@{hS` (28 edges), `L?`DE`gl@YJODg` (26 edges, 4-regular, `α = 4`, `= C13(1,5)`) —
  **CONFIRMED**.
* `N = 11` extremals: 4 of them, including the Grötzsch graph `J?BD@g]Qvo?` (20 edges, `χ = 4`) and
  `And(4) = C11(1,4)` `J?bFF`wN?{?` (22 edges, 4-regular) — **CONFIRMED**.
* All 5 036 graphs in `f1_maximal15_bip.txt` re-decoded, re-tested for triangle-freeness and
  maximality, and their `e` and `bip` recomputed by my own code: **0 mismatches** on all 5 036 rows.

### 5.1 Two numeric claims that do NOT reproduce

**(a) `χ = 3` for the `N = 14` unique extremal graph — WRONG, it is `χ = 4`.**
F1.md Theorem 12 table: "`M?AE@bH{AYN_LgBs?` (32 edges, `α = 5`, `χ = 3`)".
Brute-force over all `3^{13}` colourings with vertex 0 fixed (`aud_chi.py`) returns
**not 3-colourable**. Consistent with F1.md's own remark that this graph is the 13-vertex
28-edge graph `L?`DAboU`w@{hS` with one vertex doubled — that graph is also not 3-colourable
(verified), and vertex duplication preserves `χ`. (`e` and `α = 5` do reproduce; the twin-class
profile is `[2,1,1,1,1,1,1,1,1,1,1,1,1]`, confirming the "one vertex doubled" description.)
Note this error runs *against* F1.md's own narrative — the correct `χ = 4` strengthens its
Theorem 13 rhetoric — but it is a stated computed fact that is false.

**(b) "`C5[3,3,3,2,2]`" listed as an `N = 13` extremal — as written it has `bip = 4`, not 6.**
In cyclic order `(3,3,3,2,2)` the blow-up has `min_i t_i t_{i+1} = min(9,9,6,4,6) = 4`.
The extremal graph actually found is `C5[3,2,3,2,3]` (same multiset, different cyclic order),
`min(6,6,6,6,9) = 6`. Notation-level, but as literally printed the entry is false.

---

## 6. Claims that survive the audit intact

| F1.md item | verdict | note |
|---|---|---|
| Lemma 1 (edge monotonicity) + Cor 1.1 (attained on maximal tri-free) | **CONFIRMED** | Proof complete. Empirically corroborated: scanning *all* triangle-free graphs (`N ≤ 12`, incl. disconnected/isolated vertices) gives the same `a(N)` as scanning maximal ones. |
| Lemma 2 (weighted blow-up identity) | **CONFIRMED** | The multilinearity/box-vertex argument is complete and correct; the box optimum is a 0/1 vector, hence realisable, so `maxcut(H[t]) = max_S(…)` is an identity, not an inequality. Their 2 577-test check reproduces (0 mismatches). |
| Cor 2.1 / (B) `a(tN) ≥ t²a(N)` | **CONFIRMED** | |
| Theorem 3 `c = lim = sup` | **CONFIRMED** | `a` nondecreasing (add isolated vertex), `a ≤ N²/4`; `liminf ≥ a(N)/N²` ∀N. Airtight. |
| Theorem 4 (the collapse) | **CONFIRMED as mathematics; label "OBSTRUCTION" is a misnomer** | It is an *upgrade tool* (Theorem 5 uses it as such) and it *enlarges* the space of admissible routes (§1.2). Calling it an obstruction is rhetoric. |
| Theorem 5(a) | **CONFIRMED** | |
| Theorem 5(b) | **CONFIRMED for genuinely blow-up-closed classes; the parenthetical example list is partly wrong** | `δ/N`, `Δ/N`, `α/N`, `2e/N²`, homomorphism-closed: all invariant ✓. "An edge-density window" in `e/binom(N,2)`: **not** blow-up-closed ✗ (§3). |
| Cor 5.1, `n²/23.5` at `N0 = 1` | **CONFIRMED** | BCL Thm 2(a) holds "for `n` large enough" ⟹ `limsup ≤ 1/23.5` ⟹ `sup ≤ 1/23.5` (Thm 3) ⟹ all `n`. |
| Cor 5.1, the two density regimes at `N0 = 1` | **GAP** | Correct only after re-normalising to `2e/N²` (§3). |
| Theorem 6 ("finite computation can never contribute") | **GAP — over-claim** | Literally true only in the narrow sense "finitely many terms do not bound a supremum". It is contradicted by Theorem 7 *in the same document*, which uses a finite computation to prove 32 new instances of (E), and by the standard architecture (asymptotic argument + finite base cases). F1.md hedges this in the body but not in the summary row. |
| Theorem 7 (`a(N) ≤ N²/25` for all `N ≤ 40`) | **CONFIRMED, conditional on the citation** | One-line proof, correct, and correct at `N = 1..4` and at odd/non-multiple `N`. **External dependency I could not verify:** the input `a(5m) = m²` for `m ≤ 40` is cited as arXiv:2606.28041, outside my verification reach. Everything in §3 of F1.md rests on it. |
| Theorem 8 (`U(N)`, 128 unsettled, deficits) | **numbers CONFIRMED exactly; proof GAP (informal)** | Independent re-derivation in exact `Fraction`s (`aud_bounds.py`): 72 settled (`N ≤ 40` plus all multiples of 5 up to 200 — the 32 non-multiples `≤ 39` and 40 multiples), 128 unsettled, min deficit **1** at `N = 41, 46, 48, 53`, max deficit **64** at `N = 196`, `U(41) = 1089/16 = 68.0625`. All match F1.md. The *proof* that `U` is the exact closure of `{K,M,B}` is a hand-wave about a proof calculus, not a theorem. |
| Theorem 9 (exact `a(N)`, `N ≤ 15`) | **CONFIRMED** (§5) | |
| Theorem 11 (`φ(N)`, `G → C5`) | **CONFIRMED** | The bound `P⁵ ≤ (Πt_i)² ≤ (N/5)^{10}` is correct; the `C5` step (a 2-colouring of an odd cycle leaves 1, 3 or 5 monochromatic edges, and every single edge is realisable as the unique monochromatic one) is correct. The *closed form* is asserted with "follows in general from the same product inequality" but only checked to `N ≤ 29` — I extended the exhaustive check to `N ≤ 60`, 0 mismatches; the closed form is not needed for `φ ≤ N²/25`, which is fully proved. Minor GAP in the closed-form generality only. |
| Cor 11.1 (`δ > 3N/8 ⟹ (E)`) | **CONFIRMED but subsumed** | `3/8 = 0.375 > 0.3197`, so BCL(b) + Thm 5(b) already gives it. |
| Theorem 12 (extremal graph list) | **CONFIRMED except two entries** | See §5.1. |
| Lemma 13 (deletion) | **CONFIRMED** | Uses a specific cut to *upper*-bound `bip` — correct direction (no maxcut/local-optimum confusion). |
| Theorem 14(i) `δ > (4N−2)/25` | **CONFIRMED** | The floor bookkeeping `⌊N²/25⌋+1−⌊(N−1)²/25⌋ > (2N−1)/25` is valid. |
| Theorem 14(ii),(iv),(v) | **CONFIRMED** | (ii) superseded by the corrected (iii). |
| Theorem 14(iii) | **REFUTED as stated** (§3) | |
| §7 `K_{m,m}` 1-flip obstruction | **CONFIRMED** | Reproduced for `m = 4,6,8,10`: uncut `= N²/8`, no improving single flip, `bip(K_{m,m}) = 0`. Silently requires `m` even (so `N ≡ 0 mod 4`) — harmless for an infinite family. It is an obstruction only to schemes that certify via *an arbitrary* locally optimal cut; it says nothing about flag algebras per se. |
| §9 item 3 (`β(H) ≤ 1/25` ∀ tri-free `H`) | **CIRCULAR — correctly self-flagged** | F1.md states plainly that this *is* the conjecture. No progress is claimed from it; §6's framework `c = sup_H β(H)` is a restatement, not a reduction. |

### 6.1 Where triangle-freeness is (not) used

Lemma 1, Lemma 2, Theorems 3–8 use triangle-freeness **only** through two closure properties of
the class (closed under balanced blow-up; `a(N)` well-defined and monotone). They are valid verbatim
for *any* blow-up-closed monotone class and any constant in place of `1/25`. So §§1–3 of F1.md —
which is where all its "PROVED" mass sits — contains **zero triangle-free-specific content**.
Triangle-freeness is genuinely invoked only in Cor 1.1 (maximality), Theorem 11 (`C5`-hom /
Häggkvist), Theorem 14(v) (`α ≥ δ`), and the exhaustive computations. This is the structural reason
the family produces bookkeeping rather than progress.

### 6.2 Small-case / degeneracy stress tests (audit checklist item 4)

* `N` odd, `N` not divisible by 5: all covered — `a(N)` computed exhaustively at `N = 7,9,11,13`;
  Theorem 7 verified at `N = 1..4` (where `N²/25 < 1` forces `a(N) = 0`, and indeed every
  triangle-free graph on `≤ 4` vertices is bipartite).
* Disconnected `G`, isolated vertices: my `N ≤ 12` runs used `geng -tq` (**all** triangle-free
  graphs, disconnected included) and reproduce the same `a(N)`; `N = 13,14,15` runs also read the
  full disconnected-inclusive stream and filtered by maximality *afterwards*, so nothing was assumed
  connected. (Maximal triangle-free ⟹ diameter ≤ 2 ⟹ connected, so the reduction is safe.)
* `G` regular / large min degree / `C5` structure: not assumed anywhere in Lemmas 1–2 or
  Theorems 3–8. Theorem 11 assumes `G → C5` explicitly, correctly.
* Constant degradation: the constant `1/25` survives exactly everywhere (Theorem 4/5 lose nothing —
  that is their content). No hidden `o(N²)`.

---

## 7. Reproduction log (auditor's own code, exact arithmetic)

```
aud_bip2.cpp     own graph6 decoder + own triangle-free test + Gray-code exact maxcut
                 geng -tq N | aud_bip2 N {all|maximal} [thr]
  N=5..12  ALL triangle-free graphs scanned  -> a = 1,1,1,2,2,4,4,5
  N=13     20 797 002 read, 392 maximal      -> a(13)=6
  N=14     467 871 369 read (=A006785(14)), 1 274 maximal, 32-way res split -> a(14)=7, unique
  N=15     5 036 maximal (their file re-verified row-by-row) -> a(15)=9, unique = C5[3,3,3,3,3]
aud_bounds.py    exact Fraction re-derivation of U(N)  -> 72 settled / 128 unsettled,
                 min deficit 1 @ {41,46,48,53}, max 64 @ 196, U(41)=1089/16
aud_phi.py       phi(N) exhaustive, N<=60 -> closed form + phi<=N^2/25 confirmed;
                 C5[3,3,3,2,2] cyclic -> min product 4 (not 6)
aud_wit.py       independent decode/bip/alpha/chi/C5-hom of every quoted witness
aud_chi.py       brute-force 3-colourability -> N=14 extremal NOT 3-colourable
aud_beta.py      exact Fraction beta lower bounds -> beta(H) >= 1/25 for h=5..11
aud_and.py       And(d), d=2..6: exact beta >= 1/25 ; delta/n = 2e/n^2 = d/(3d-1) > 1/3
f1_beta_scan.py 5 7 60   (their code, re-run) -> h=6: 0.039917, h=7: 0.039991  [reproduced]
f1_check_lemmaA.py       (their code, re-run) -> 2577 tests, 0 mismatches      [reproduced]
f1_final_checks.py       (their code, re-run) -> 11/11 PASS                    [reproduced]
```

Note on `f1_final_checks.py`: it passes, but it does **not** test the `χ = 3` claim, the `β` table,
Corollary 5.2, the `C5[3,3,3,2,2]` entry, or any of the obstruction inferences — i.e. none of the
claims this audit breaks. "11/11 PASS" is not coverage of F1.md's assertions.

---

## 8. FINAL VERDICT

### Status: **BLOCKED**

Family F1 asked (i) settle the non-multiples of 5 below 200, (ii) are the general bounds effective
and what is `N0`, (iii) prove `(E)` for `N ≥ N0`. The audit confirms:

* (ii)/(iii) are dissolved, not answered: effectivity is free and no threshold statement is easier
  than the full conjecture;
* (i) is answerable only up to `N = 40` (Theorem 7, correct, but conditional on the cited
  `a(5m) = m²`, `m ≤ 40`), and the remaining 128 values require exactly the value `a(5N) = N²`,
  i.e. a computation ~5× beyond the published range — which by the blocking lemma would still not
  advance the conjecture.

**Blocking lemma, verbatim (F1.md Theorem 4 — audited and CONFIRMED):**

> For every `N0 ≥ 1`:
> `[ a(N) ≤ N²/25 for all N ≥ N0 ]  ⟺  [ a(N) ≤ N²/25 for all N ≥ 1 ]`.
> *Proof.* (⇐) trivial. (⇒) Let `M < N0` and pick `t` with `tM ≥ N0`. By `a(tM) ≥ t² a(M)`
> (balanced blow-up, Lemma 2), `a(M) ≤ a(tM)/t² ≤ (tM)²/(25 t²) = M²/25`. ∎

**Auditor's strengthening of the blocking lemma** (which also refutes F1.md's Theorems 10 and 13):

> For every set `S ⊆ ℕ` such that every `M ≥ 1` has a multiple in `S` — in particular
> `S = 5ℕ`, or `S = {N : N ≥ N0}`, or `S = {5m : m ≥ m0}` —
> `[ a(N) ≤ N²/25 for all N ∈ S ]  ⟺  [ a(N) ≤ N²/25 for all N ≥ 1 ]`.
> *Proof.* Given `M ≥ 1`, pick `t` with `tM ∈ S`. Balanced blow-up gives `a(tM) ≥ t² a(M)`, and the
> hypothesis at `tM ∈ S` gives `a(tM) ≤ (tM)²/25`. Hence `t² a(M) ≤ t² M²/25`, i.e.
> `a(M) ≤ M²/25`. ∎

### Carry-forward instructions for the campaign

1. **Do not propagate** F1.md's Theorems 10 and 13 as obstructions. Both are false. Routes that are
   sharp only on `C5` blow-ups, and routes that only ever work at `N ≡ 0 (mod 5)` or for large `N`,
   remain fully live.
2. **Do not use** Corollary 5.2 / Theorem 14(iii) in the `e/binom(N,2)` form. Use
   `0.2486 ≤ 2e(G)/N² < 0.3197` (equivalently `0.1243 N² ≤ e(G) < 0.15985 N²`), which also gives
   the sharper `0.16N < δ(G) < 0.3197N`.
3. **Do not open** the Andrásfai target (§9 item 4) as motivated. Its regime (`δ > N/3`) is inside
   BCL's proved high-density region; and the corrected min-degree window `δ < 0.3197N` is disjoint
   from Chen–Jin–Koh's hypothesis, so no counterexample can ever be routed through it.
4. The only genuinely open thing F1 leaves behind is what BCL already left behind: close the gap
   `1/23.5 → 1/25` inside `0.2486 ≤ 2e/N² < 0.3197`. That is a different family, not F1.
5. Reusable, audited assets: Lemma 1, Lemma 2 / Cor 2.1, Theorem 3, Theorem 4 (+ auditor's
   strengthening), Theorem 5(a), Theorem 7, Theorem 11, Lemma 13, Theorem 14(i), the exact table
   `a(5..15) = 1,1,1,2,2,4,4,5,6,7,9`, and the extremal-graph census for `N ≤ 15`.
