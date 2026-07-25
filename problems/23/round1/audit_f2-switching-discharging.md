# Adversarial audit of `f2_local_switching.md` (Erdős #23, family F2)

**Auditor:** independent adversarial pass, 2026-07-25.
**Target:** `E:/Projects/ErdosProblems/problems/23/round1/f2_local_switching.md` and the scripts
`switch_lib.py`, `p4_obstruction.py`, `c5_tight_sets.py`, `c5_tight_profiles.py`,
`witness_verify.py`, `witness_odd.py`, `lemma_check.py`, `edge_ratio_search.py`.
**Method:** every claim re-derived by hand; every computation re-run with **independently written
code** that never imports the author's libraries. σ is computed twice — once from the edge list,
once by literally recomputing the cut after switching — and the two are cross-checked. All
arithmetic is exact integer / `Fraction`; no floating point enters any verdict.

**My audit code (persisted):** `E:/Projects/ErdosProblems/problems/23/round1/audit_f2/`
(`aud_core.py`, `aud1_lemmaA.py`, `aud2_c5.py`, `aud3_wb.py`, `aud4_wprime.py`,
`aud5_edgeratio.py`, `aud6_classical_tight.py`, `aud7_sweep.py`, `aud_ratio.cpp`, `aud_ce.cpp`).

---

## 0. Summary of the audit

The **mathematics that is claimed PROVED is correct** — Lemmas 1–4, Lemma A, Corollaries A1/A2 and
Proposition 3.1 all survive a full adversarial re-derivation, and I reproduced (and in several places
extended) every number. The **obstruction witnesses `W_b` and `W'_{L,b}` are exactly correct**; I
verified them on the explicit graphs, not by trusting the profile abstraction.

What does **not** survive is the *interpretation* layer — precisely the layer that turns a correct
but narrow obstruction into the headline "the local-switching programme is **provably dead**", and
the layer that declares the residual gap unfillable. Three separate factual errors there, plus one
refuted side claim in §6:

1. §4.3/§5's premise "the tight sets of `C5[n]` are none of the classical shapes" is **false** — the
   edge neighbourhood `N[u]∪N[v]` *is* a non-trivially tight sweep-chain member.
2. §3's "the ball `B(v,2)` for `v ∈ V_1` equals `V∖V_4`" is **false** — `C5[n]` has diameter 2, so
   every radius-2 ball is `V` and the ball inequality is *vacuous* at the extremal graph.
3. §5's "exact missing statement" (the reported dead end) is **answered by a one-line family the
   report itself names but never tests**; that family kills *both* witnesses.
4. §6's "So no small counterexample exists" to `bip ≤ |E|/5` is **false**: I exhibit **10** connected
   triangle-free graphs on **N = 12** vertices with `5·bip > |E|` (the report's search excluded them
   by an unjustified min-degree-3 restriction).

Nothing here is circular, and no constant silently degrades.

---

## 1. Per-claim audit

### C1 — Lemma 1 (decomposition), Lemma 2 (additivity, complementation), Lemma 3 (mass identity) — **CONFIRMED**

Proofs are correct and complete. `σ(S) = Σ_{v∈S}σ(v) − 2e_B(S) + 2e_M(S)`; `σ(S) = σ(V∖S)`;
`4|M| = 2|E| − Σσ(v)` (from `d_M(v) = (d(v)−σ(v))/2`, which needs nothing but the definitions).

*Independent machine check* (`aud1_lemmaA.py`): geng `-c -t` for n = 3..8 → **355** connected
triangle-free graphs, **598** maximum cuts (vertex 0 pinned), all `2^n` subsets each. Lemma 1,
Lemma 3, `σ(v) ≥ 0`, `σ(S) ≥ 0`, and `σ` computed-from-edges == `σ` computed-by-re-cutting: **0
failures**. The author's own `lemma_check.py` re-run reproduces its stated totals exactly
(`TOTAL: 655 graphs, 1387 maximum cuts, 0 failures`) — the extra 300 graphs are random ones on 9–13
vertices, so my 598 and his 1387 are consistent.

No hidden assumption: nothing uses connectivity, regularity, parity of `N`, or `5 | N`. Isolated
vertices are harmless (`σ = 0`, `d = 0`).

### C2 — Lemma A (sharp star) — **CONFIRMED**, with one load-bearing hypothesis worth flagging

Proof audited line by line. Triangle-freeness is **genuinely used and is essential**: `A ⊆ N_B(v)`
forces `A` independent, hence `e_B({v}∪A) = |A|`, `e_M({v}∪A) = 0`; without it the identity
`σ(S) = σ(v) + Σ_{a∈A}σ(a) − 2|A|` fails. The equivalence with the `max(2−σ(a),0)` form is correct,
and Lemma A is indeed strictly stronger than the star inequality (the difference is
`Σ_{σ(a)≥2}(σ(a)−2) ≥ 0`).

**Flag (not an error — the report says "maximum cut"):** Lemma A is *not* a consequence of
vertex-local optimality. Searching all cuts of the 355 graphs with `σ(v) ≥ 0 ∀v`, I find **1436**
such cuts that violate Lemma A, the smallest on **4 vertices** (graph6 `CU`, side `[0,1,1,0]`,
`σ = [0,1,1,0]`). So Lemma A consumes switch-optimality against sets of size up to `1+deg(v)`; any
downstream route that only has a locally optimal cut may not invoke it.

### C3 — Corollary A1 (matching structure of `Z = {σ ≤ 1}`) — **CONFIRMED**

Immediate from Lemma A. Machine-checked (matching + both ends `σ = 1`) over all 598 maximum cuts,
0 failures.

### C4 — Corollary A2 (`4|M| ≤ 2|E| − Σ_{Z_0}d(a) − Σ_{Z_1}(d(a)+1)/2`) — **CONFIRMED**

Double-counting step `Σ_v Σ_{a∈N_B(v)}(2−σ(a))^+ = Σ_a (2−σ(a))^+ d_B(a)` is correct;
`d_B(a) = (d(a)+σ(a))/2` gives `d(a)/2` and `(d(a)+1)/2` in the two cases (parity `σ(a) ≡ d(a) mod 2`
makes both integral). Machine-checked in exact `Fraction` arithmetic over all 598 maximum cuts,
0 failures. Sanity-checked non-vacuous on `W_b`: A2 gives `|M| ≤ b² + b/2` while `|M| = b²` — i.e. the
proved bound does *not* refute the author's own obstruction witness (a real consistency test that
could have caught an error, and passes).

### C5 — Proposition 3.1 (tight sets of `C5[n]`, all `n`) — **CONFIRMED (and extended)**; the *machine check as described* is **NOT-REPRODUCED**

*Mathematics.* Formula (★) re-derived and matches. Regroupings (G1), (G2) expand correctly. The
non-negativity case split (`x_4 ≥ x_1` / `x_5 ≥ x_3` / complement) is exhaustive; the equality
analysis under `x_4 ≥ x_1` is complete as written. **CONFIRMED.**

*Independent enumeration* (`aud2_c5.py`): I re-derived the profile formula from scratch, checked it
against σ computed on the explicit graph over **all** `2^N` subsets for n = 1,2,3 (0 mismatches), and
then enumerated all profiles for **n = 1..14** (the report only claims n ≤ 7). For every `n` the set
of tight profiles equals the 10-family list of Proposition 3.1 **exactly** (`missing = 0`,
`extra = 0`), count `= 10n`, and no profile has `σ < 0`. Independent enumeration of every maximum cut
for n = 1,2,3 reproduces `bip = n²`, `#maxcuts = 5, 15, 35` and `#tight sets per cut = 10, 30, 70`.
So every *number* quoted in §3 reproduces.

*But the described verification is not what the scripts do.* The report says
"`c5_tight_profiles.py` … the list agrees with Proposition 3.1" and that `c5_tight_sets.py`'s check
matches. In fact:

* `c5_tight_profiles.py::predicted` implements only **4 of the 10** families
  (`(0,0,0,t,0)`, `(0,0,0,0,t)`, `(0,0,t,n,0)`, `(t,0,0,0,n)`). Running it prints
  `missed=5, 11, 17, 23, 29, 35, 41` for n = 1..7 and a `MISSED:` list every time.
* `c5_tight_sets.py::structure_check` uses an even weaker predicate ("`S` or its complement lies
  inside one part of the monochromatic pair") and prints
  `canonical cut of C5[2]: characterisation FAILS on 16 sets`,
  `canonical cut of C5[3]: characterisation FAILS on 40 sets`.

Both self-checks **fail**, and neither failure is mentioned in the write-up. The *claim* is right (I
proved it independently for n ≤ 14); the *evidence cited for it* is not. Reporting-integrity defect.

### C6 — §3 bullet "the ball `B(v,2)` for `v ∈ V_1` equals `V∖V_4` and is tight (profile `(n,n,n,0,n)`)" — **REFUTED**

`C5[n]` has diameter 2. For `v ∈ V_1`: `N(v) = V_2∪V_5`, `N(V_2) = V_1∪V_3`, `N(V_5) = V_1∪V_4`, so
`B(v,2) = V`. Verified on the explicit graph for n = 1,2,3 (`|B(v,2)| = N`, profile `(n,n,n,n,n)`).

Consequence (matters for §4.3/§5): the radius-2 ball inequality at the extremal graph is the
**trivial identity `σ(V) = 0`** and carries no information at all. The set with profile
`(n,n,n,0,n)` that the report is thinking of is the **edge neighbourhood** `N[u]∪N[v]`, `u ∈ V_1`,
`v ∈ V_2` — see C7.

### C7 — §4.3/§5 "the only tight linear-size sets at `C5[n]` are the two sweep chains … whose members are neither balls, nor stars, nor neighbourhoods, nor independent"; "the only [named family] that survives is the radius-2 ball" — **REFUTED**

`aud6_classical_tight.py` evaluates every classical shape on `C5[n]` for n = 1,2,3,4,6,8. For every
`n ≥ 1`:

| set | profile | σ |
|---|---|---|
| `N[u]∪N[v]`, `u∈V_1, v∈V_2` | `(n,n,n,0,n)` | **0 — TIGHT** |
| `N[u]∪N[v]`, `u∈V_2, v∈V_3` | `(n,n,n,n,0)` | **0 — TIGHT** |
| `N[u]∪N[v]`, other 3 edge types | — | `2n²` |
| `B(v,2)` | `(n,n,n,n,n)` | 0 (trivial, `= V`) |
| `N[v]`, `N(v)`, star `{v}∪N_B(v)` (n ≥ 2) | — | `> 0` |

Both tight edge neighbourhoods are genuine, **proper**, linear-size (`4n = 4N/5`) members of the
sweep chains — profiles `(n,n,t,0,n)|_{t=n}` and `(t,n,n,n,0)|_{t=n}` of Proposition 3.1. So a
classical shape *is* non-trivially tight at `C5[n]`, and the surviving named family is the **edge
neighbourhood**, not the ball. This is exactly the premise on which §4.3's "sharp form of the answer
to (i)" and §5's framing rest, and it is false.

### C8 — Lemma 4 (multilinearity / whole-part reduction) — **CONFIRMED**

`F(x) = Σ ε_ij(n_j x_i + n_i x_j − 2x_i x_j)` is multilinear; a multilinear function on a box attains
its min at a vertex, and box vertices are integer points, so `min_S σ(S) = min over unions of whole
parts`. Correct, no gap.

### C9 — THEOREM 4.1 (obstruction `W_b = P_4[b+1,b,b,b+1]`) — **CONFIRMED exactly** (4 cosmetic gaps inside the proof)

Verified independently (`aud3_wb.py`), on the explicit graph wherever feasible:

* triangle-free (bipartite) ✔; `N = 4b+2`, `|E| = 3b²+2b`, `|M| = b²` ✔ (b = 2..12).
  `25|M| > N² ⟺ b ≥ 3` ✔ (b = 2 gives exact equality `100 = 100`; the report's `b ≥ 3` is right).
  `b = 3`: `N = 14`, `|E| = 33`, `|M| = 9 > 7.84` ✔.
* Formula (†) reproduced from an independently derived blow-up formula, **0 mismatches** over all
  profiles for b = 2..12; and `σ(profile) == σ(edge list) == σ(re-cut)` over **all 2^14 subsets**
  at b = 3, **0 mismatches**.
* `κ(b)` (smallest improving switch): exhaustive profile minimum equals the report's formula
  `min_u(⌊bu/(2u−1)⌋+1+u)` for **every** `b = 3..40`, **0 mismatches**; and by an independent
  `O(b²)` exact method also for `b = 60, 100, 150, 200, 300, 500`. `κ(3)=5`, `κ(6)=7`, `κ(8)=8` —
  matches the report's quoted values. Explicit-graph brute force over all `2^N` subsets confirms
  `min|S| with σ<0 = 5` for b = 3 (N = 14) and b = 4 (N = 18).
* **All named families, computed on the explicit graph** for b = 3..8, min σ:
  `vertex = 1`, `N(v) = b`, `whole part = b`, and `star = sharp star = N[v] = B(v,2) = N[u]∪N[v] =
  independent set = 0`. **All ≥ 0** ✔.
* `bip(W_b) = 0` by exact max cut (b = 3,4) ✔ — the report states this honestly.

Therefore the *logical* content is sound: `W_b` is triangle-free, so every true theorem about
triangle-free graphs holds for it; hence any derivation of `|M| ≤ N²/25` whose only cut-hypotheses
are `σ(S) ≥ 0` over a family inside that union would be false at `W_b`. **The obstruction is real.**

Four defects inside the *proof text* (none changes the result):

* **(a) genuine proof gap.** "Proof of 2": *"By (†) the cross term `+2s_2s_3` is non-negative, so a
  profile with `σ < 0` and minimum `Σ s_i` has `s_2 = 0` or `s_3 = 0`"* — this is a non sequitur;
  non-negativity of one term says nothing about where the size-minimiser sits. The conclusion is
  true (my exhaustive scan finds the minimiser at `(0,0,s_3,s_4)` or its mirror for all `b ≤ 40`,
  and the `O(b²)` argument confirms `κ(b)` up to `b = 500`) but it is **not proved**.
* **(b)** `κ(b) = min_{1≤u≤b+1}(⌊bu/(2u−1)⌋+1+u)` includes the **infeasible** term `u = 1`, which
  needs `s_3 = b+1 > n_3 = b`. Harmless: `u = 1` is never the strict minimum for `b ≥ 3` (checked to
  `b = 500`), but the formula as stated is not the honest one.
* **(c)** "Calculus … value `(√b+1)²/2 = b/2 + √b + 1/2`" minimises `bu/(2u−1) + u`, not
  `bu/(2u−1) + u + 1`; the continuous minimum is `b/2 + √b + 3/2` and the integer truth is
  `≈ b/2 + √b + 1`. Immaterial to `κ = N/8 + Θ(√N)`, which is correct.
* **(d) citation defect.** §4.2 says `p4_obstruction.py` "brute-forces **all 2^N subsets** for
  b = 2,3,4". It does not: that script only builds the **uniform** `P_4[n,n,n,n]`; the
  `(b+1,b,b,b+1)` witness is only ever checked *by profile* (in `witness_verify.py`). I supplied the
  missing explicit-graph brute force (b = 3, 4) and it passes.

### C10 — THEOREM 4.2 (non-bipartite witness `W'_{L,b}`) — **CONFIRMED exactly**, with a caveat the report omits

`aud4_wprime.py`, on the explicit graph:

| `(L,b)` | `N` | `|M|` | `25|M|` vs `N²` | odd girth | `κ'` | violated families |
|---|---|---|---|---|---|---|
| (9,8) | 39 | 64 | 1600 > 1521 | 9 | **9** | `B(v,2) = −63`, `N[u]∪N[v] = −63` |
| (9,12) | 55 | 144 | 3600 > 3025 | 9 | **11** | both `= −143` |
| (11,10) | 49 | 100 | 2500 > 2401 | 11 | **10** | both `= −99` |

All of `vertex (1)`, `sharp star (1)`, `star (2)`, `N(v) (4)`, `N[v] (2)`, `independent set (0)`,
`whole part (2)` are `≥ 0`. Every number in §4.3 reproduces exactly. Triangle-freeness and odd girth
`L` confirmed by BFS.

**Caveat I add (absent from the report):** `bip(W'_{L,b}) = 1` — recolour `C_L` alternately so that
the unique monochromatic pair is a pair of **size-1** parts, giving one monochromatic edge. So the
exhibited cut, with `|M| = b²`, is off by a factor `b²` from the true optimum (`b² = 64, 144, 100`
above). Both witnesses are *very deep, very bad* local optima. That is exactly what an obstruction to
local certification needs, but the report frames `W'` only as "connected and non-bipartite" without
saying how far from maximum its cut is, which overstates how "genuine extremal-like" the
configuration is.

### C11 — "`W'_{9,15} ⊔ C5[1]` gives an odd-girth-5 witness (`N = 72`, `|M| = 226 > 207.4`)" — **CONFIRMED arithmetically, VACUOUS strategically**

`25·226 = 5650 > 5184 = 72²` ✔, `σ` is additive over components ✔, `C5[1]`'s cut is maximum ✔.
But `bip(G_1 ⊔ G_2) = bip(G_1)+bip(G_2)` while `(N_1+N_2)²/25 ≥ N_1²/25 + N_2²/25`, so the
conjecture for disconnected `G` **follows immediately** from the connected case; a proof is entitled
to assume `G` connected. The `C5` component carries no violated inequality. The "odd girth 5"
upgrade is therefore cosmetic — it does not defeat any scheme that first reduces to connected `G`.

### C12 — §4.4 level values (`N²/8`, dies at `|S| = 2`, `≥ N²/16`) — **CONFIRMED**

`K_{m,m}` with `V_0 =` half of each side: verified for m = 4,6,8 — all `σ(v) = 0`, `|M| = N²/8`
exactly, and `min σ` over pairs `= −2 < 0`. `|M|/N² = b²/(4b+2)² → 1/16` ✔. "Loses a factor
`≥ 25/16`" is a correct lower bound on the local relaxation.

### C13 — §3 slack accounting ("slack `Θ(N)` ⟹ weight 0", "slack `Θ(N²)` ⟹ weight 0") — **GAP (minor)**

The σ values are right (`C5`-shaped: `2(3n−3)`; `V_1∪V_3`: `4n²` — both re-derived). But "must carry
weight **0** in any asymptotically sharp scheme" does not follow from "total slack `o(N²)`": a set
with slack `Θ(N)` may carry **total** weight `o(N)`, and one with slack `Θ(N²)` total weight `o(1)`.
The correct statement is about total weight, not per-set weight. Morally right, formally wrong.

### C14 — §5 "off by exactly `3/2`, deficit `2n²` concentrated on `V_2`" — **CONFIRMED**

Per-vertex Lemma-A slack on `C5[n]` re-derived: `V_1: 0`, `V_2: 2n`, `V_3: 0`, `V_4: 0`, `V_5: 0`;
`Σσ(v) = 6n²` versus the A2 input `≥ 4n²`; `|M| ≤ 1.5n² = 1.5·N²/25`. Exactly as stated. The
structural statement "no tight set contains a vertex of `V_2` unless it contains all of `V_3∪V_4`
(or all of `V_1∪V_5`)" is also correct — it follows from the verified Proposition 3.1 list.

### C15 — §5 "exact missing statement" / §(4) "Where I got stuck" — **REFUTED as an obstacle**

The report asks for a family `𝓕`, graph-theoretically defined at a maximum cut, with
(α) `σ(S) = 0` on `C5[n]` for all `S ∈ 𝓕`, and (β) some `S ∈ 𝓕(W_b)` with `σ(S) < 0`;
and it even suggests the shape ("sets of the form `N_B(W) ∪ W ∪ A`") — **and then never tests it.**

Take literally the simplest such family:

> `𝓕 = { W ∪ N_B(W) : W a colour class of a connected component of the monochromatic graph M }`.

`aud7_sweep.py` (explicit graphs) gives:

| graph | `W` | `S = W ∪ N_B(W)` profile | `|S|` | `σ(S)` |
|---|---|---|---|---|
| `C5[n]`, n = 1,2,3,5,8 | `V_4` | `(0,0,n,n,0)` | `0.4N` | **0** (α ✔) |
| `C5[n]`, n = 1,2,3,5,8 | `V_5` | `(n,0,0,0,n)` | `0.4N` | **0** (α ✔) |
| `W_b`, b = 3,5,8 | `P_2` | `(b+1,b,0,0)` | `0.5N` | **`−b²`** (β ✔) |
| `W_b`, b = 3,5,8 | `P_3` | `(0,0,b,b+1)` | `0.5N` | **`−b²`** (β ✔) |
| `W'_{9,8} / W'_{9,12} / W'_{11,10}` | `P_0` or `P_{L−1}` | — | `≈0.44N` | **`−55 / −131 / −89`** ✔ |

Both C5[n] sets are members of the Proposition 3.1 sweep chains, so (α) holds **exactly, for all n**,
and (β) holds for `W_b` *and* for `W'`. The reported dead end is therefore not a dead end; the author
stopped one experiment short of his own suggestion. (No contradiction with Theorem 4.1: these sets
have size `≈ N/2 > N/8`, so they lie outside the blocked union. What is genuinely open — and is a
much bigger question — is whether such linear-size sweep inequalities *suffice* to reach `N²/25`.)

### C16 — §6 / table row 10: `bip ≤ |E|/5` exhaustive search — **CONFIRMED as scoped, but the conclusion drawn from it is REFUTED**

*Reproduction.* Independent counts via `geng -t -c -d<k> -u`:
`n=5..10, d≥2 → 2, 6, 17, 82, 436, 3485`; `n=11, d≥3 → 2052`; `n=12, d≥3 → 36223`.
**Total = 42 303**, exactly the report's figure. Independent exact max cut (C++, all `2^{n}`
colourings) gives `max bip/|E| = 1/5` in every class, attained at `n=5` (C5, `1/5`), `n=8` (`2/10`),
`n=10` (`3/15`, Petersen), `n=11` (`4/20`), `n=12` (`4/20`), and **0** graphs with `5·bip > |E|`.
Everything the report *claims to have run* reproduces exactly.

*Refutation of the conclusion.* Min degree `≥ 2` **is** WLOG (deleting a degree-≤1 vertex preserves
`bip` and decreases `|E|`, so it only raises the ratio) — but min degree `≥ 3`, used at n = 11,12,
**is not**, and the report offers no justification. Extending the search to `n = 12, d ≥ 2`
(529 336 graphs) I find:

> **`max bip/|E| = 4/18 = 2/9 > 1/5`, and exactly 10 connected triangle-free graphs on 12 vertices
> with `5·bip > |E|`.**

All 10 have `bip = 4` and `|E| ∈ {18, 19}`:
`K??E@_qi?]Ia` (18), `K?AAD?WNBHCs` (18), `K??EDbGIaYAe`, `K?AAD?WXHLN_`, `K?AA@bGNAY@w`,
`K?AA@agRPw@w`, `K?AA@b@ZDcPW`, `K?ABA`ocdQBo`, `K?ABAaIs?{TG`, `K?`D@POd@wAw` (all 19).

Hand-checkable smallest one, verified by a third independent brute force over all `2^12` colourings:
`E = {(0,6),(1,6),(2,7),(3,7),(2,8),(3,8),(6,8),(0,9),(2,9),(4,9),(4,10),(5,10),(6,10),(7,10),
(1,11),(3,11),(5,11),(9,11)}` — `n = 12`, `|E| = 18`, 0 triangles, degrees `[2,2,2,2,3,3,3,3,4,4,4,4]`,
`maxcut = 14`, `bip = 4`, `5·4 = 20 > 18`. (The conjecture itself is untouched: `N²/25 = 5.76 > 4`.)

Since `n ≤ 11, d ≥ 2` is clean (I ran it: `n=11, d≥2`, 36 540 graphs, `max = 3/15 = 1/5`, 0
counterexamples) and pendant deletion reduces any counterexample to a min-degree-2 one on no more
vertices, **`N = 12` is exactly the minimum order of a counterexample to `bip ≤ |E|/5`.**
The report's §6 sentence *"So no small counterexample exists"* and the framing "a sublemma that is
**not** refutable at small size (recorded to save future effort)" are therefore wrong, and would have
cost future effort rather than saved it. Table row 10 itself, being explicitly scoped to min degree
≥ 3 at n = 11,12, remains literally true.

### C17 — "the tight sets are the members of two maximal chains in the subset lattice" — imprecise (cosmetic)

They are two maximal chains of **profiles**. As *sets* there are 10 / 30 / 70 of them for n = 1,2,3,
whereas two maximal chains in the subset lattice of an `N`-set contain at most `2(N+1)−2` sets
(18 for n = 2). The displayed picture with "`V_4∪(part of V_3)`" makes the intent clear.

### C18 — Headline claim (3): "the local-switching programme is **provably dead as stated**" — **GAP / overstated**

The narrow statement is true and exactly verified (C9): for every family `𝓕` contained in
`{|S| < κ(b)} ∪ {`stars, sharp stars, `N(v)`, `N[v]`, `B(v,2)`, `N[u]∪N[v]`, independent sets,
`C5`-shaped, single parts`}`, the implication fails. What is **not** established is the upgrade to
"the programme is dead", because:

* the justification clause "*by the `C5[n]` census the only candidates are the sweep-chain sets,
  which are none of the classical shapes*" is **false** (C7: `N[u]∪N[v]` is both);
* a scheme is entitled to use non-bipartiteness (the report grants this in §4.3), and against
  non-bipartite `G` the only witness offered is `W'`, which does **not** defeat `B(v,2)` or
  `N[u]∪N[v]` — and `N[u]∪N[v]` is precisely a family that is non-trivially tight at `C5[n]`;
* the successor family the report declares unfound is immediate (C15).

So the correct scope is: **bounded-size (`< N/8`) and classical-shape switching is blocked; linear-size
sweep switching is untouched.**

---

## 2. Answers to the standing audit questions

**1. Completeness of proofs.** All PROVED items are complete except: the `s_2 = 0 ∨ s_3 = 0` step in
Theorem 4.1's proof of item 2 (C9a, verbatim quoted above), the `u = 1` feasibility slip (C9b), and
the "weight 0" slack accounting in §3 (C13). None affects a stated result.

**2. Is triangle-freeness genuinely used?** Yes, and essentially, in Lemma A (independence of
`A ⊆ N_B(v)`), hence in A1/A2. Everywhere else it appears only as a property the witnesses satisfy
(and they do — checked explicitly, not assumed).

**3. Maximum vs locally optimal cut.** Correctly attributed everywhere. Worth recording that Lemma A
is *strictly stronger* than vertex-local optimality: 1436 explicit vertex-locally-optimal cuts on
≤ 8-vertex triangle-free graphs violate it (smallest on 4 vertices).

**4. Hidden hypotheses (`N` even, `5 | N`, connected, regular, min degree, extremal shape).**
Lemmas 1–4, A, A1, A2 assume none of these; isolated vertices and disconnected `G` are safe.
`W_b` always has `N = 4b+2 ≡ 2 (mod 4)` — the bipartite obstruction is never exhibited at odd `N`,
but `W'_{9,b}` has `N = 4b+7` odd, so odd `N` is covered. The **one place a hidden hypothesis does
real damage is §6**, where min degree `≥ 3` at `n = 11,12` is neither WLOG nor justified, and
removing it produces counterexamples (C16).

**5. Does the constant survive?** Yes; nothing degrades silently. The report is explicit that its
proved bound is `1.5·N²/25`, and that the local relaxation is worth `≥ N²/16 = 1.5625·N²/25`. No
`o(N²)` is hidden anywhere.

**6. Circularity.** None. Lemma A and Corollary A2 are strictly weaker than the conjecture
(`|M| ≤ |E|/2 − …`), Proposition 3.1 concerns one graph family, and the obstruction results are
negative statements. **Not circular; not BLOCKED for that reason.**

**7. Reproduction of computations.** Every quoted number reproduces (355 graphs / 1387 cuts; `10n`
tight profiles; 5/15/35 maximum cuts; 10/30/70 tight sets; `κ(3)=5, κ(6)=7, κ(8)=8`;
`κ'(9,8)=9, κ'(9,12)=11, κ'(11,10)=10`; 42 303 graphs; `max bip/|E| = 1/5`). The **only**
non-reproductions are (i) the *description* of the two `C5` scripts' self-checks, which in fact fail
and print `MISSED`/`FAILS` (C5); (ii) the claim that `p4_obstruction.py` brute-forces the
`(b+1,b,b,b+1)` witness (C9d).

**8. False obstruction check.** The obstruction is **not** false: `W_b` and `W'_{L,b}` are exactly as
described, re-verified on explicit graphs with an independently written σ, cross-checked by
re-cutting. It kills the sub-route it names. The danger here is the opposite one — the obstruction is
*over-generalised* in prose to kill a route (linear-size sweep switching) that it does not reach and
that is in fact still open (C15).

---

## 3. Verdict

**Family F2 (local switching + discharging): BLOCKED, in the precise scope below; the successor route
it wrongly declares unreachable should be opened as a separate live family.**

### Blocking lemma (verbatim; independently verified by this audit)

> **For every integer `b ≥ 3` let `W_b = P_4[b+1, b, b, b+1]` be the blow-up of the path
> `p_1p_2p_3p_4` with part sizes `(b+1, b, b, b+1)`, and take the cut `V_0 = P_1 ∪ P_4`,
> `V_1 = P_2 ∪ P_3`. Then `W_b` is triangle-free, `N = 4b+2`, `|E| = 3b²+2b`, `|M| = b²` and
> `25|M| > N²`; and `σ(S) ≥ 0` holds for**
> * **every `S` with `|S| < κ(b) = min_{u ≥ 1}(⌊bu/(2u−1)⌋ + 1 + u) = N/8 + Θ(√N)`, and**
> * **every `S` that is a single vertex, a sharp star `{v} ∪ A` with `A ⊆ N_B(v)`, a star
>   `{v} ∪ N_B(v)`, an open neighbourhood `N(v)`, a closed neighbourhood `N[v]`, a radius-2 ball
>   `B(v,2)`, an edge neighbourhood `N[u] ∪ N[v]`, an independent set, a `C5`-shaped set, or a single
>   part.**
>
> **Consequently, for every family `𝓕` of switch sets contained in that union, the implication
> "`σ(S) ≥ 0` for all `S ∈ 𝓕(G)` `⟹` `|M| ≤ N²/25`" is FALSE, and no discharging scheme whose only
> cut-hypotheses are `σ(S) ≥ 0` over such an `𝓕` can prove Erdős #23.**
>
> **(Smallest instance `b = 3`: `N = 14`, `|E| = 33`, `|M| = 9 > 196/25 = 7.84`, every `S` with
> `|S| ≤ 4` has `σ(S) ≥ 0`. `W_b` is bipartite, so a scheme that uses non-bipartiteness escapes this
> witness; the non-bipartite variant `W'_{L,b} = C_L[b, b+1, 1, …, 1, b+1, b]` (`L = 9, 11`,
> odd girth `L`) blocks the same list except `B(v,2)` and `N[u] ∪ N[v]`.)**

### What must NOT be inferred from it (corrections to the report)

* The union above is blocked; **the radius-2 ball is not "the only survivor"** — the ball is
  *vacuous* at `C5[n]` (`B(v,2) = V`, diameter 2), whereas the **edge neighbourhood `N[u]∪N[v]` is
  non-trivially tight** at `C5[n]` (profiles `(n,n,n,0,n)` and `(n,n,n,n,0)`), so it, not the ball,
  is the classical family that survives against non-bipartite witnesses.
* **The sweep-chain sets are not "none of the classical shapes"** — two of the five edge-neighbourhood
  types are exactly sweep-chain members.
* **The stated "exact missing statement" is already satisfied** by
  `𝓕 = { W ∪ N_B(W) : W a colour class of a component of the monochromatic graph }`:
  `σ = 0` on `C5[n]` for all `n`, `σ = −b²` on `W_b`, `σ < 0` on `W'_{L,b}`.

### Successor family to open (ALIVE)

> **F2′ — linear-size sweep switching.** Study the inequalities `σ(W ∪ N_B(W)) ≥ 0` and their
> extensions `σ(W ∪ N_B(W) ∪ A) ≥ 0` (`A` in the next layer), for `W` a colour class of a component
> of the monochromatic graph at a maximum cut of a **connected non-bipartite** triangle-free `G`.
> These are tight at `C5[n]` for all `n`, are not implied by any inequality in the blocked union, and
> kill both of F2's obstruction witnesses. Open question: do they, together with Corollary A2, close
> the residual factor `3/2` (equivalently, do they charge `V_2`)?

### Independent side result produced by this audit (not in the report)

> **`bip(G) ≤ |E|/5` is false for triangle-free `G` already at `N = 12`.** There are exactly 10
> connected triangle-free graphs on 12 vertices with `5·bip > |E|` (all with `bip = 4`,
> `|E| ∈ {18,19}`; best ratio `4/18 = 2/9`); the smallest is
> `E = {(0,6),(1,6),(2,7),(3,7),(2,8),(3,8),(6,8),(0,9),(2,9),(4,9),(4,10),(5,10),(6,10),(7,10),(1,11),(3,11),(5,11),(9,11)}`
> (`maxcut = 14`). There is none on `≤ 11` vertices. Any future route through the edge-ratio sublemma
> should be closed on this basis, not kept open on the report's "no small counterexample exists".
