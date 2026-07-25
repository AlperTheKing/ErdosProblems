# ADVERSARIAL AUDIT — family F5 ("exact LP/SDP duality and certificates"), Erdős #23

Target of the audit: `E:/Projects/ErdosProblems/problems/23/round1/f5.md` and every script it
names (`f5lib.py`, `c5n_cert.py`, `exhaust.py`, `scan.cpp`/`scan.exe`, `srg.py`,
`subdiv_and_srgscan.py`, `srg_tail_and_sdp.py`, `verify_lemmas.py`, `blowup_search.py`,
`gaps12.txt`, `srg_cuts.json`, `exhaust_n10.log`, `exhaust_n11.log`, `scan13.log`).

Everything below marked "independently reproduced" was recomputed with **code written from
scratch for this audit**, using different algorithms where possible (edge-subset cycle
enumeration instead of DFS; a different simplex implementation and pivot rule; pure-Python
integer matrix products instead of numpy; a different graph6 decoder; an integral
edge-disjoint-odd-cycle certificate instead of an LP). Audit scripts:
`C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/461052bb-8cbc-4d9f-996c-62e0fcc0bfcb/scratchpad/`
(`aud_lib.py`, `aud1_n12.py`, `aud2_srg.py`, `aud3_m22.py`, `aud4_lemmas.py`,
`aud5_missing.cpp`, `aud6_lp.py`, `aud7_misc.py`, `aud_scan.cpp`, `aud_pack.cpp`).

---

## 0. Headline

**The single live target the write-up leaves behind (§11, the "missing statement") is
logically EQUIVALENT to the conjecture, not "strictly stronger".** The write-up asserts the
opposite in bold ("The statement is *not* a reformulation in the forbidden sense — it is
**strictly stronger** than the conjecture"). It is a reformulation. Under campaign rules
that makes the residual route **BLOCKED**, and it is refuted by a two-line argument plus an
exhaustive machine check.

Separately, the write-up's *reason* for declaring F5 blocked (§0 + §4: "convex relaxations
bound `bip` from below, so they help only if exact, and exactness is NP-hard") is **not a
valid obstruction argument** — it silently ignores rounding, which is the standard and only
way a convex relaxation ever produces an upper bound on `bip`. So the family is blocked, but
not for the reason given, and the write-up's stated "most valuable thing established" does
not hold up.

The computational content of the write-up, by contrast, is **almost entirely correct**: every
census number, every LP value, every graph6 witness, every srg number and the GW value at
`C₅` reproduced exactly under independent recomputation.

---

## 1. MOST SERIOUS FINDING — §11 "missing statement" is CIRCULAR (a reformulation)

### The claim being audited (f5.md §11, verbatim)

> **Missing statement.** *There is an absolute constant `c > 0` such that every
> triangle-free graph `G` on `N` vertices admits a map `φ : V(G) → ℤ₅` with*
> `min_{i∈ℤ₅} ( n_{i−1}(φ) n_i(φ)  +  |B_i(φ)| )  ≤  N²/25 ,`
> *where `B_i(φ)` is the set of edges that are monochromatic in the rotation cut
> `S_i = φ^{−1}({i,i+2})` but do not join `φ^{−1}(i−1)` to `φ^{−1}(i)`.*
>
> For a homomorphism, `B_i = ∅` and this is Lemma 3. The statement is *not* a reformulation
> in the forbidden sense — it is **strictly stronger** than the conjecture …

### AUDIT LEMMA (proved here, and machine-checked)

> For **every** graph `G` on `N` vertices,
> ```
> min_{φ : V(G) → ℤ₅}  min_{i∈ℤ₅} ( n_{i−1}(φ)·n_i(φ) + |B_i(φ)| )  =  bip(G)   exactly.
> ```
> Hence the §11 missing statement holds for `G` **iff** `bip(G) ≤ N²/25`. It is the
> conjecture, restated.

*Proof.*
**(≥)** Fix `φ` and `i`. Since `i ∈ S_i` and `i−1 ∉ S_i = {i, i+2}`, **no** edge joining
`φ^{−1}(i−1)` to `φ^{−1}(i)` is monochromatic in the cut `(S_i, V∖S_i)`. Therefore the
exclusion clause in the definition of `B_i` removes nothing, `|B_i| = mono(S_i)`, and
`bip(G) ≤ mono(S_i) = |B_i| ≤ n_{i−1}n_i + |B_i|`.
**(≤)** Let `(A, V∖A)` be a maximum cut and put `φ(v) = 0` for `v ∈ A`, `φ(v) = 1` otherwise;
then `n₂ = n₃ = n₄ = 0`. Take `i = 3`: the first term is `n₂n₃ = 0`, and
`S₃ = φ^{−1}({3,0}) = A`, so `|B₃| = mono(A) = bip(G)`. ∎

The same argument applies verbatim to the **index-corrected** reading (see §1b): with
`n_{i+3}n_{i+4}` in place of `n_{i−1}n_i` and `B′_i = mono(S_i) ∖ e(φ^{−1}(i+3), φ^{−1}(i+4))`,
take `i = 4` in the same degenerate `φ`.

### Machine confirmation (`aud5_missing.cpp`)

Exhaustive over **all** `5^{N−1}` maps `φ` (fixing `φ(v₀)=0`, legitimate by the rotation
symmetry of the whole expression):

| family | graphs | `min_φ Q(φ) ≠ bip` | `min_φ Q′(φ) ≠ bip` |
|---|---|---|---|
| connected triangle-free `N=5` | 6 | 0 | 0 |
| `N=6` | 19 | 0 | 0 |
| `N=7` | 59 | 0 | 0 |
| `N=8` | 267 | 0 | 0 |
| `C₅[2]` (`I?rFf_{N?`) | 1 | 0 | 0 |
| the `N=12` LP-gap witness `K??E@_qi?]Ia` | 1 | 0 | 0 |

`min_φ` of the §11 quantity equals `bip(G)` in **all 353** cases, for both readings.

### 1b. The §11 statement is additionally mis-indexed, and its own justification is false

"For a homomorphism, `B_i = ∅`" is **false as written**. Under a homomorphism `G → C₅` the
monochromatic edges of `S_i = φ^{−1}({i,i+2})` are exactly those joining classes `i+3` and
`i+4` (the only `C₅`-edge inside the complement `{i+1,i+3,i+4}`), **not** those joining `i−1`
to `i`. Measured (`aud7_misc.py`), at `C₅[n]` with the natural homomorphism:

```
n=1 : mono(S_0)=1 , |B_0| (literal) = 1 , |B'_0| (corrected) = 0 ; min_i literal = 2 , corrected = 1 , bip = 1
n=2 : mono(S_0)=4 , |B_0| = 4 , |B'_0| = 0                       ; min_i literal = 8 , corrected = 4 , bip = 4
n=3 : mono(S_0)=9 , |B_0| = 9 , |B'_0| = 0                       ; min_i literal = 18, corrected = 9 , bip = 9
```

So for the *intended* `φ` the literal §11 quantity is `2n² = 2·N²/25` — **twice** the target —
at the extremal example itself. The statement is only rescued by the existential quantifier
over `φ`, and that quantifier is exactly what collapses it to `bip`.

### 1c. The write-up already refutes itself in §8

f5.md §8 states, verbatim:

> "Any scheme that keeps the *exact* monochromatic counts and takes the minimum is trivially
> complete (it recomputes `bip`); so all the content of the pentagon template lives in the
> step where the monochromatic count `e(V_{i−1},V_i)` is replaced by the size bound
> `n_{i−1}n_i` …"

§11 then adds the exact monochromatic residue `|B_i|` back into the minimum — i.e. it does
precisely the thing §8 identifies as "trivially complete". The document is internally
inconsistent, and §8 has it right.

**Verdict: CIRCULAR.** The route's only remaining forward step is the conjecture itself.

---

## 2. SECOND FINDING — §0/§4 "the F5 duality direction is provably the wrong way round" is a GAP

f5.md §0:

> "no *outer* relaxation `R` … can certify `bip ≤ N²/25` **unless it is exact**, i.e. unless
> `bip(G) = |E| − R(G)` for every triangle-free `G`."

and §4:

> "**This is the decisive obstruction for family F5.** … exactness on triangle-free graphs is
> NP-hard. … Combined with Lemma 4, the whole F5(iii) programme is blocked."

This is invalid as an obstruction, for three independent reasons.

1. **It ignores rounding.** Convex relaxations do not produce upper bounds on `bip` by being
   equal to it; they produce them by *rounding*. `maxcut ≥ g(SDP)` (Goemans–Williamson
   hyperplane rounding, and every refinement of it) gives `bip = |E| − maxcut ≤ |E| − g(SDP)`
   — an **upper** bound on `bip` obtained from an outer relaxation that is nowhere exact.
   Any argument of the form "exhibit a feasible SDP/LP solution of value ≥ V, then round"
   yields exactly the kind of upper bound the conjecture needs. §0 does not address this at
   all, so it does not establish that the direction is wrong.
2. **Corollary 4a bounds the wrong object.** NP-hardness of computing `bip` on girth-≥9
   graphs rules out a *poly-time-computable* `R` with `bip = |E| − R` on all triangle-free
   `G`. It says nothing about a relaxation used with an approximation/rounding guarantee, and
   nothing about a non-uniform per-family analysis (the conjecture is a single inequality,
   not an algorithm).
3. **It answers a question task (iii) did not ask.** Task (iii) as quoted in §7 asks for
   "a semidefinite relaxation whose value on `C₅[n]` is exactly the truth" — exactness **at
   `C₅[n]`**, not globally. §7 itself concedes that SDP + odd-cycle inequalities is exact at
   both `C₅[n]` and Higman–Sims. Declaring the task blocked by a *global* exactness
   obstruction is a non-sequitur.

Lemma 4 and Corollary 4a are themselves **correct theorems** (verified, §3 below). It is the
inference drawn from them about the family that fails.

Consequence: the write-up's stated "(3) Most valuable thing established: the F5 duality
direction is provably the wrong way round" is **not established**. The genuinely valuable
outputs are the census, the `N=12` witnesses, and `bip(Higman–Sims) = 350`.

---

## 3. Per-claim audit (all recomputed independently)

### 3.1 Theorem 1 — `ν* = τ* = bip(C₅[n]) = n²` — **CONFIRMED**

Reproduced from scratch (`aud4_lemmas.py`): for `n = 1,2,3` the transversal-pentagon count is
`n⁵` (1, 32, 243), every edge lies in exactly `n³` of them (edge-load sets `{1}`, `{8}`,
`{27}` — recomputed, not assumed), the uniform cover `y ≡ 1/5` is feasible against **all**
odd cycles (1 / 352 / 895131 cycles, matching the write-up's counts exactly, enumerated by a
second, independent DFS), cover value = packing value = `n²`, and brute-force
`bip(C₅[n]) = n²`.

Triangle-freeness is **genuinely used** (odd girth ≥ 5 ⇒ `Σ_{e∈C} y_e = |C|/5 ≥ 1`). No
hidden parity/divisibility assumption: `N = 5n` by construction. The theorem is correct but
elementary; `bip(C₅[n]) = n²` is the standard extremal computation.

### 3.2 Proposition 1a — optimal cover face has dimension `5n−1 = N−1` — **CONFIRMED**

Independent exact rank over ℚ (my own Fraction Gaussian elimination), extended one step
beyond the write-up:

```
n=1: m=5   #pent=1     rank=1   dim=4   = 5·1−1  OK
n=2: m=20  #pent=32    rank=11  dim=9   = 5·2−1  OK
n=3: m=45  #pent=243   rank=31  dim=14  = 5·3−1  OK
n=4: m=80  #pent=1024  rank=61  dim=19  = 5·4−1  OK   (NEW — not in the write-up)
```

The identification of the optimal face with the pentagon-tight affine space is sound
(`y ≡ 1/5` is in the relative interior; every other odd-cycle constraint has slack
`|C|/5 − 1 ≥ 2/5 > 0`; summing the pentagon equalities forces objective `n²`, so the face is
exactly the optimum set). The parametrisation for **general** `n` is a *proof sketch* only —
adequate but not a proof; the dimension formula is verified only for `n ≤ 4`. Minor GAP.

**Unsupported rider (flagged):** "everything a proof can extract from `C₅[n]` is the single
scalar identity `|E| = 5·bip`". This does not follow from an `(N−1)`-dimensional optimal
face; it is rhetoric. Lemma 3 itself extracts the *part sizes* `n_i` from the extremal
structure and never touches the dual.

### 3.3 Lemma 2 — blow-up formula — **CONFIRMED (with a repairable hole)**

`bip(H[n₁..n_h]) = min_X Σ_{uv mono} n_u n_v` reproduced on **23 862** independently generated
(template, multiplicity) pairs, deliberately including **zero multiplicities** and a
**disconnected** template: 0 mismatches. The author's own run reproduces its 12 324 pairs.

**Hole:** the proof sets `x_u = a_u/n_u`, which is undefined when `n_u = 0`. Repair: delete
empty blobs first (the formula's right-hand side is unchanged since `n_u n_v = 0`). Verified
empirically that the identity survives at `n_u = 0`.

Triangle-freeness is **not** used here, correctly (the lemma is general; looplessness is what
matters, and it is used).

### 3.4 Lemma 3 — odd-cycle template — **CONFIRMED**

The cut construction, the AM–GM chain and the equality analysis all check out by hand
(`Y_i = {i+1,…,i+2k−1}` independent; the unique `Z_i`-internal edge is `{i+2k, i}`;
`min ≤ geometric mean`; `2k+1 ≥ 5`). Reproduced on all **10 548** `C₅`-multiplicity vectors
with `N ≤ 16` (including `N` odd and `N ≢ 0 mod 5`, and vectors with zero entries) plus 300
random **non-complete** subgraphs of `C₅`-blow-ups: `bip ≤ min_i n_{i−1}n_i ≤ N²/25` always;
equality vectors exactly `(1,1,1,1,1), (2,2,2,2,2), (3,3,3,3,3)`.

Not circular: it proves the conjecture on the strict subclass `χ_c ≤ 5/2`. Note (as the
write-up says) `G → C_{2k+1}` for any `k ≥ 2` implies `G → C₅`, so the "`k ≥ 2`" generality is
cosmetic. Not new mathematics.

### 3.5 Lemma 4 / Corollary 4a — 3-subdivision, NP-hardness — **CONFIRMED**

Both directions of the proof are correct (parity of colour changes along a length-3 path).
Reproduced on 6 hand-picked cases including a **disconnected** `G`, a `G` with **isolated
vertices**, `K₄`, and `C₅`+chords: 0 mismatches; the author's own 88-graph sweep reproduces.
The reduction is genuinely polynomial and `bip`-preserving, so `bip` is NP-hard on graphs of
girth ≥ 9. The *theorem* is fine; the *use made of it* is the over-claim in §2 above.

### 3.6 Census `N ≤ 11` — **CONFIRMED (independently, by a different method)**

My rescan (`aud_scan.cpp`, independent graph6 decoder, edge-list parity `bip`, triangle-check
re-run on every graph):

```
n=5  graphs=6      nonbip=1     maxbip=1 (DUW)          tight=1
n=6  graphs=19     nonbip=2     maxbip=1 (ECpo)         tight=0
n=7  graphs=59     nonbip=15    maxbip=1 (F?bBo)        tight=0
n=8  graphs=267    nonbip=85    maxbip=2 (G?`F`w)       tight=0
n=9  graphs=1380   nonbip=650   maxbip=2 (H?AAF_})      tight=0
n=10 graphs=9832   nonbip=5800  maxbip=4 (I?rFf_{N?)    tight=1
n=11 graphs=90842  nonbip=65244 maxbip=4 (J?BEFboL`{?)  tight=0
```

Identical to f5.md §5a in every entry (Σ = 102 405), same record graph6 strings, and the only
two graphs with `25·bip ≥ N²` are `C₅` and `C₅[2]`.

`τ*(G) = bip(G)` for all of them — **re-established without solving the same LP**: for
70 338 of the 71 797 non-bipartite graphs I exhibited `bip(G)` **edge-disjoint odd cycles**
(an integral packing ⇒ `bip ≥ τ* = ν* ≥ ν ≥ bip`), and for the remaining 1 459 graphs where
that certificate does not exist I ran my own exact rational LP: **0 graphs with `τ* < bip`**
(`lp_check.out`). Claim fully independent-confirmed.

### 3.7 `N = 12` and `N = 13` scans — **CONFIRMED**

```
N=12 : graphs=1144061 nonbip=931281 maxbip=5 (K?ABBBwerwBw)  5·bip>|E| : 10   25·bip≥N² : 0
N=13 : graphs=19425052 nonbip=17183322 maxbip=6 (L??ED@_~?~^_Fw …)  5·bip>|E| : 155  25·bip≥N² : 0
```

(N=13 run split by edge count across 31 parallel jobs.) Exactly the write-up's numbers,
including `max bip/N² = 5/144` at `N=12` and `6/169` at `N=13`. The 155 `N=13` gap graphs match
`scan13.log` graph-for-graph in their `(m, bip)` profile multiset
(97×`m=24,bip=5`, 33×`m=19,bip=4`, 18×`m=23,bip=5`, 3×`m=18,bip=4`, 2×`m=26,bip=6`,
1×`m=27,bip=6`, 1×`m=28,bip=6`).

*Scope note the write-up does not make:* the census is over **connected** graphs only. This is
harmless (`bip` is additive over components and `Σ N_i² ≤ (Σ N_i)²`), but the reduction is
never stated. Isolated vertices only inflate `N`, likewise harmless.

### 3.8 Theorem 5 — smallest LP failure at `N = 12` — **CONFIRMED**

All ten `N=12` witnesses re-decoded, re-checked triangle-free, `bip` recomputed by brute
force, all odd cycles re-enumerated by **exhaustive edge-subset enumeration** (a completely
different algorithm; it agrees set-for-set with a second DFS enumerator), and `τ*` recomputed
with my own simplex:

```
K??E@_qi?]Ia  m=18 bip=4 tau*=10/3  ratio 6/5
K?AAD?WNBHCs  m=18 bip=4 tau*=10/3  ratio 6/5
K??EDbGIaYAe / K?AAD?WXHLN_ / K?AA@bGNAY@w / K?AA@agRPw@w / K?AA@b@ZDcPW /
K?ABA`ocdQBo / K?ABAaIs?{TG / K?`D@POd@wAw   m=19 bip=4 tau*=11/3  ratio 12/11
```

The explicitly published edge list of `K??E@_qi?]Ia` decodes correctly, and the published
cover (`y = 1/3` on the ten named edges) is feasible against **all 40** odd cycles with value
`10/3 < 4 = bip`. The write-up's caveat that `5·bip > |E|` is sufficient-not-necessary is
correctly stated; the "exactly `N=12`" claim is safe because `N ≤ 11` was settled by the full
LP census (which I re-confirmed).

### 3.9 §5c / §6 — the strongly regular graphs — **CONFIRMED**, two reproducibility defects

Re-verified in **pure-Python integer arithmetic** (no numpy) directly from `srg_cuts.json`:
regularity, the exact identity `A² = dI + λA + μ(J−I−A)`, `λ = 0`, the integer root
`s = λ_min`, the spectral bound `bip ≥ m/2 + N·λ_min/4`, and the stored cut recounted:

```
Higman–Sims      n=100 m=1100 d=22 λ=0 μ=6 λ_min=−8  bip ≥ 350  cut = 350  ⇒ bip = 350 = 7/200·N²
Hoffman–Singleton n=50 m=175  d=7  λ=0 μ=1 λ_min=−3  bip ≥ 50   cut = 50   ⇒ bip = 50
Gewirtz          n=56  m=280  d=10 λ=0 μ=2 λ_min=−4  bip ≥ 84   cut = 84   ⇒ bip = 84
Clebsch          n=16  m=40   d=5  λ=0 μ=2 λ_min=−3  bip ≥ 8    cut = 8    ⇒ bip = 8
```

The spectral argument is sound: `(A − rI)(A − sI) = μJ` vanishes on `1⊥`, so `λ_min|_{1⊥} ≥ s`,
and `min_{x∈{±1}^N} xᵀAx ≥ N·s`. The cut is used only as an **upper** bound and the spectral
bound only as a **lower** bound — no misuse of "maximum cut where only a local optimum is
justified" anywhere in this family.

`M22`: I rebuilt it **independently** as the second subconstituent of the stored
Higman–Sims graph (non-neighbours of a vertex), obtained `srg(77,16,0,4)` exactly, spectral
bound `385/2 ⇒ bip ≥ 193`, and my own 4 000-restart local search also found a cut of exactly
**196**. `bip(M22) ∈ [193,196]` — CONFIRMED.

Defects:
* **`srg_cuts.json` is not produced by any delivered script** — `grep "srg_cuts" *.py *.cpp`
  returns nothing, and `srg.py` (which the §10 reproduction list points at) does not write it.
  The M22 cut is not in the file at all. The `bip(M22) ≤ 196` claim therefore has **no stored
  certificate** in the delivered artefact set (I re-derived it, so the claim stands).
* **`τ*` is only bounded, not computed.** The write-up presents `τ*(HS) = 220`
  ("it gives 220/10000 = 0.022") and "LP gap `35/22`", "`10/7`", "`3/2`", but the only argument
  given is `τ* ≤ |E|/5`. Repair (not in the write-up): these graphs are edge-transitive, so
  the uniform pentagon packing has constant edge load and value exactly `|E|/5`; hence
  `τ* = |E|/5` and the ratios are exact. The direction actually needed for the gap
  (`τ* ≤ |E|/5 < bip`) is proved, so no conclusion changes.

### 3.10 §7 — Goemans–Williamson — **CONFIRMED**

Independently, symbolically: `SDP(C₅) = 5(1−cos 4π/5)/2 = (25+5√5)/8 = 4.5225424859373685603…`,
`|E| − SDP = (15−5√5)/8 = 0.47745751406263143974…`, minimal polynomial `16x² − 60x + 25`
(re-derived by sympy and re-substituted to 0), and the `d`-regular bound
`N(d−λ_min)/4` equals the same value, so the configuration is optimal. `< 1 = bip(C₅)`, and
irrational, so plain GW is not exact at `C₅`. At Higman–Sims `N(d−λ_min)/4 = 750 = maxcut`, so
`SDP = 750` and `|E| − SDP = 350 = bip`. All correct.

### 3.11 §8 Obstruction 8 — **CONFIRMED**

Rotation weights recomputed from the definition: distance 0 → 5, distance 1 → 1, distance 2 → 3
(exactly as claimed), so `Σ_i mono(S_i) = 5e₀ + e₁ + 3e₂ ≥ |E|` and the *average* bound is
always `≥ |E|/5`. `G_a = C₅[a,a,1,1,1]`: `N = 2a+3`, `|E| = a²+2a+2`, `bip = 1`,
`5|E| − N² = (a−1)²` — all reproduced for `a = 1..7`. The obstruction is correctly scoped to
the *averaging* step only.

### 3.12 §9b — srg parameter scan — **value CONFIRMED, completeness argument has a GAP**

`sup ρ = 7/200`, attained uniquely at `srg(100,22,0,6)` — reproduced by my own scan, and the
top-10 table agrees entry for entry with `subdiv_and_srgscan.py`. `24` admissible sets with
`r ≤ 5` — reproduced exactly.

**GAP in the stated argument.** f5.md claims "The scan is complete, not just a finite range",
justified by `ρ < μ/(4(d−1))` ⇒ `r ≥ 6` impossible, "and `r ≤ 5` was scanned exhaustively for
`t ≤ 30000`". Nothing in the write-up bounds `t` for `r ≤ 5`: the very bound it uses gives
`ρ → 1/(4(r+1))`, i.e. `1/8, 1/12, 1/16, 1/20, 1/24` for `r = 1..5` — **all above `1/25`** — so
the `t ≤ 30000` cut-off is unjustified by anything stated, and "complete" is not earned.

**Repair (supplied by this audit, verified symbolically).** The second Krein condition, which
the *code* applies but the *text* never analyses, simplifies for `λ = 0`, `s = −t` to
```
(s+1)(d+s+2rs) − (d+s)(r+1)²  =  −r(t−1)(r² + 2r − t)  ≤ 0   ⟺   t ≤ r² + 2r ,
```
(sympy factorisation, `aud2_srg.py`). So `r ≤ 5 ⇒ t ≤ 35`; `t ≤ 30000` is 850× more than
needed, and the scan really is complete. I re-ran with the exact range `r ≤ 199`,
`t ≤ r²+2r` (3 444 admissible sets): `sup ρ = 7/200`. Conclusion stands.

**Minor omission.** The parametrisation by integer `(r,t)` silently excludes strongly regular
graphs with irrational eigenvalues (conference graphs). For `λ = 0` the conference case forces
`N = 4μ+1` and `λ = (N−5)/4 = 0`, i.e. `N = 5`, `G = C₅`, with `ρ = (2−(√5−1)/2)/20 ≈ 0.0191
< 7/200` — harmless, but note that `srg.py`'s comment "among the SEVEN known triangle-free
srgs" prints only six: `C₅ = srg(5,2,0,1)` never appears anywhere in the scan.

**Scope caveat that should be louder.** `ρ` is a *lower* bound on `bip/N²`. The scan shows no
parameter set makes the *spectral bound* exceed `1/25`; it does **not** show no srg has
`bip > N²/25`. The write-up's own wording ("via the eigenvalue bound") is honest, but the
one-line summary in the hand-off ("No srg counterexample exists via the eigenvalue bound")
is doing a lot of work with that qualifier.

### 3.13 §9a — blow-up template search — **numerically reproduced, but VACUOUS**

`python blowup_search.py 5 9` reproduces the reported certified bounds exactly
(`h=5: 1/25`, `h=8: 31097/793800`, `h=9: 17/441`). But its own header column shows what was
actually scanned:

```
h   #maximal-tf-twinfree
5        1
6        0        <-- nothing scanned
7        0        <-- nothing scanned
8        1
9        1
```

Independently confirmed (counting maximal triangle-free graphs before and after the twin
filter): `h=5..10` give `3/4/6/10/16/31` maximal triangle-free graphs of which
`1/0/0/1/1/2` are twin-free. **The entire "template search over `5 ≤ h ≤ 9`" examined three
graphs.** Moreover the method produces only certified *lower* bounds on `f(H)`, so it can
never exclude a template; and for `h = 8, 9` the returned values are *below* the trivial
`f(H) ≥ 1/25` that holds for every triangle-free `H` containing a `C₅`, i.e. the optimiser
did not even find the known optimum. f5.md does say "its strength should not be overstated",
but the hand-off line "Blow-up template search (`h ≤ 9`) … found no counterexample" carries
no information at all.

---

## 4. Answers to the standing audit questions

**(2) Is triangle-freeness genuinely used?** Yes, where it matters and only there:
Theorem 1's cover feasibility (odd girth ≥ 5) and the global bound `τ* ≤ |E|/5` (★) both use
it essentially. Lemma 2 does not use it and does not claim to. Lemma 3's hypothesis
(`G → C_{2k+1}`, `k ≥ 2`) *implies* triangle-freeness, so it is not an extra assumption.
Lemma 4 does not need it. The srg work uses `λ = 0` throughout. No place where
triangle-freeness is assumed and never invoked.

**(3) Maximum vs. locally optimal cut.** Clean everywhere. `bip()` in `f5lib.py` and
`scan.cpp` is an exhaustive minimum over all `2^{N−1}` bipartitions (verified by
reimplementation). `srg.py::local_search_cut` returns a merely locally optimal cut, but it is
used **only** as an upper bound on `bip` and the count is recomputed exactly; the matching
lower bound is the spectral one. `bip = 350`, `= 84`, `= 50`, `= 8` are therefore genuine.

**(4) Hidden structural assumptions.** Tested `N` odd, `N ≢ 0 mod 5`, disconnected `G`,
isolated vertices, zero blow-up multiplicities, non-regular `G`, small minimum degree. Two
findings, both benign: (i) Lemma 2's proof divides by `n_u` (undefined at `n_u = 0`);
(ii) the censuses cover connected graphs only, and the (easy) reduction from disconnected `G`
is never stated. `bip(C₅[n]) = n²` is of course specific to `5 | N`, but the write-up never
uses it outside that family. No hidden regularity or minimum-degree assumption anywhere.

**(5) Does the constant survive exactly?** Yes — every bound in the file is exact rational or
exact integer; nothing degrades to `1/25 + ε` and nothing hides an `o(N²)`. The floats appear
only in heuristics (`local_search_cut`, `blowup_search.maximin`, the `%.6f` printing in
`scan.cpp`) and every proposed object is re-counted exactly.

**(6) Circularity.** One instance, and it is the decisive one: §11 (see §1 above). Lemma 3 is
strictly weaker than the conjecture (it covers `χ_c ≤ 5/2` only) and is not circular.

**(7) Reproduction.** Every reported number reproduced. Zero numeric mismatches found in the
entire document: 102 405 / 1 144 061 / 19 425 052 graph counts; `max bip` 1,1,1,2,2,4,4,5,6;
`10` and `155` cheap-gap counts with identical witnesses; `τ* = 10/3` and `11/3`;
`bip(HS)=350`, `bip(HoS)=50`, `bip(Gewirtz)=84`, `bip(Clebsch)=8`, `bip(M22)∈[193,196]`;
`sup ρ = 7/200`; `24` admissible `r ≤ 5` sets; ranks `1, 11, 31` (+ `61` at `n=4`);
`895131` odd cycles in `C₅[3]`; `(25+5√5)/8`; `31097/793800`; `17/441`; `12324` and `10548`
verification counts.

**(8) Are the claimed obstructions real?** Obstruction 8 (uniform averaging): **real**, and
correctly scoped. The srg exclusion: **real** after the Krein repair, but only against the
*eigenvalue bound*. The `N=12` and Higman–Sims LP failures: **real**, verified exactly and
independently — these genuinely kill "prove `τ* ≤ N²/25`, then use integrality". The §0/§4
"direction" obstruction: **not real as stated** (see §2) — and a false obstruction that
declares a route dead is exactly the failure mode the audit is meant to catch, so this one is
flagged as damaging even though the family is blocked anyway.

---

## 5. Verdict

**BLOCKED.**

Not for the reason the write-up gives. The family is blocked because its own stated residual
target is the conjecture in disguise, so the write-up contains **no reduction of the problem
at all** beyond the classical special case `χ_c(G) ≤ 5/2` (Lemma 3, which is folklore). What
survives as usable output is data, not a route: the exact `N ≤ 13` census, the ten `N = 12`
odd-cycle-LP counterexamples, `bip(Higman–Sims) = 350 = 0.035·N²` as the sharpest known
non-`C₅` test object, and the (correct, previously-known-flavoured) fact that the odd-cycle LP
is not exact.

### Blocking lemma, stated verbatim

> **Blocking lemma.** For every graph `G` on `N` vertices,
> ```
> min_{φ : V(G) → ℤ₅}  min_{i ∈ ℤ₅} ( n_{i−1}(φ)·n_i(φ) + |B_i(φ)| )  =  bip(G),
> ```
> where `n_j(φ) = |φ^{−1}(j)|` and `B_i(φ)` is the set of edges monochromatic in the rotation
> cut `S_i = φ^{−1}({i, i+2})` that do not join `φ^{−1}(i−1)` to `φ^{−1}(i)`.
> The identity holds verbatim for the index-corrected variant in which `n_{i−1}n_i` is
> replaced by `n_{i+3}n_{i+4}` and `B_i` by `B′_i = B_i ∖ e(φ^{−1}(i+3), φ^{−1}(i+4))`.
> Consequently the f5.md §11 "missing statement" is logically **equivalent** to
> `bip(G) ≤ N²/25` for every triangle-free `G`, and is therefore a reformulation of the
> conjecture, not a strictly stronger statement.

*Proof.* (≥) `i ∈ S_i` and `i−1 ∉ S_i`, so no `φ^{−1}(i−1)`–`φ^{−1}(i)` edge is monochromatic
in `S_i`; hence `|B_i| = mono(S_i) ≥ bip(G)`. (≤) Take a maximum cut `(A, V∖A)`, set `φ ≡ 0`
on `A` and `φ ≡ 1` off `A`; at `i = 3`, `n₂n₃ = 0` and `S₃ = A`, so the bracket equals
`mono(A) = bip(G)`. ∎

### If the family is to be reopened

Any revival must (a) drop §11 entirely, (b) replace the §0 "direction" argument with a real
analysis of **rounding** (`maxcut ≥ g(R)`), which is the only mechanism by which a convex
relaxation can ever bound `bip` from above, and (c) state a target that is provably *weaker*
than the conjecture. Nothing in the current document does any of these.
