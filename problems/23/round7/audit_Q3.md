# audit_Q3.md — ADVERSARIAL AUDIT of `round7/Q3.md` (pass 1 + pass 2)

Auditor: independent re-implementation, exact integers / `Fraction` / `sympy.Rational` on every
acceptance path. Own graph6 decoder, own `bip = |E| − maxcut` (full `2^{N−1}` cut enumeration), own
`dist` (branch and bound over `φ : V → ℤ₅`, cross-checked by exhaustive `5^{N−1}` enumeration for
`N ≤ 13`). Nothing below reuses the target's code or data-processing.

**Headline.** The *data* of pass 2 is impeccable: my engine reproduces **all 126 097 rows byte for
byte** (`diff` = 0 on every one of the ten `p2_*.tsv` files). The *inferences* are not: five claims
are refuted with exact witnesses, three more are unsupported, and the one "exactly known" value that
the report's blocking question rests on (`D(n=3) = 19`) was asserted from a corpus that cannot decide
it — I closed that gap by hand, and the value survives.

---

## VERDICTS, most consequential first

### 1. REFUTED — "the open BCL band contains nothing near-extremal"

Claimed (pass 1 b.7, re-asserted pass 2 P2.4/P2.5 and in the summary):
`max{bip/N² : density in the open band} = 7/225 = 0.03111 = 0.778·(1/25)`, hence
*"The open range contains no near-extremal configuration; what is missing there is a better bound,
not a structure theorem."*

The number `7/225` is right **for the corpus** (I reproduce it: 69 840 points, same witness
`N??E@_Ki?]ESoWTC^_?`). The conclusion is false: it is an artefact of stopping at `N ≤ 15`, where the
`|E|/C(N,2)` normalisation inflates the density of the good graphs above the `0.3197` threshold.
Blow-ups — which preserve `ψ` **exactly** by the accepted blow-up identity (base 1),
`bip(G[t]) = t²·bip(G)` — move the same graphs inside the band:

| exact witness | `N` | `|E|` | density `|E|/C(N,2)` | inside open band? | `bip` | `ψ = bip/N²` | `ψ·25` |
|---|---|---|---|---|---|---|---|
| `N?ABAaQT?]N_}?iSDM?[3]` | 45 | 315 | `7/22 = 0.318182` | **yes** (`< 0.3197`) | 72 | **`8/225 = 0.035556`** | **0.8889** |
| `C₁₃(1,5)[3]` | 39 | 234 | `6/19 = 0.315789` | **yes** | 54 | `6/169 = 0.035503` | 0.8876 |

and the whole tails `t ≥ 3` stay inside (densities `→ 14/45` and `→ 4/13`, both `< 0.3197`).
The blow-up identity is not taken on trust here: `bip(C₁₃(1,5)[2]) = 24 = 4·6` and
`bip(N?ABAaQT?]N_}?iSDM?[2]) = 32 = 4·8` are re-verified **directly**, by enumerating all `2^25`
resp. `2^29` cuts of the 26- and 30-vertex blow-ups.
So the open band contains an infinite family at `0.889·(1/25)`, not `0.778·(1/25)`, and the report's
strategic conclusion ("stability is not the missing ingredient / nothing near-extremal lives there")
does not follow from its own data. (Under the other common normalisation, `|E|/(N²/2)`, both
witnesses are inside the band already at `t = 1`, so the refutation is normalisation-robust.)

**Corollary — the same fact kills pass 2's "second, independent reason".** P2.4 argues:
*"`C₁₃(1,5)` has density exactly `1/3 > 0.3197`, i.e. it sits in the range BCL have already settled …
the objects that break the stability constant and the objects that break the flag bound live in
different density ranges."* But P2.3 also asserts *"`R` is blow-up invariant, so `425/19` recurs at
every `N = 13t`"*. The two are inconsistent: `C₁₃(1,5)[3]` has `R = 425/19` (given their invariance
claim) at density `6/19 < 0.3197`, i.e. **inside** the open band. One of the two claims must go.
Applying an asymptotic density theorem to a single 13-vertex graph is in any case the
"asymptotic-presented-as-exact" failure mode.

### 2. REFUTED — the BLOCKED box's equivalence `D < ∞ ⟺ perfect stability`

Verbatim (P2.6): *"`R = dist` exactly on this class, so `D < ∞ ⟺ perfect stability`."*
Falsified by the report's own P2.3, verbatim: *"(`D` is a necessary condition, not a sufficient one;
`D = ∞` refutes perfect stability outright.)"* Perfect stability quantifies over **all** orders and
**all** deficits; `D` only sees `N = 5n` at deficit exactly `1/N²`. Only `⟹` is proved.
Second defect in the same box: both directions silently need `a(5n) = n²` (otherwise the deficit at
`bip = n²−1` is not `1/N²`), i.e. the conjecture at those sizes — established only for `n ≤ 40`.
The final-message version ("`D = ∞` refutes perfect stability outright") is the correct direction and
survives, with that proviso.

### 3. REFUTED — "max `R` per band is monotone increasing in `d`"

Their own row sequence (which I reproduce exactly) is
`25/21, 50/21, 25/7, 125/19, 50/7, 13/2, 125/7, 19, 425/19`
= `1.190, 2.381, 3.571, 6.579, 7.143, 6.500, 17.857, 19.000, 22.368`.
`50/7 = 7.143` (band `1/25 < d ≤ 1/20`) → `13/2 = 6.500` (band `1/20 < d ≤ 3/50`) is a **decrease**.
The claim appears both in P2.3 ("max `R` increases monotonically with the distance band") and in the
final summary ("monotone increasing in `d`"). Exact falsifier: the pair `(50/7, 13/2)`.

### 4. REFUTED — "worst direction … `bip = k²−j`, `dist = 5j`, `R = 5` exactly (verified `k=2,3,4`, all `j`)"

`k = 2, j = 2` fails, for **every** possible choice of the two matchings (there are only two
isomorphism types of the result, and I checked both), and the distance is verified by **exhaustive
`5⁹` enumeration**, not by branch and bound:

| graph | g6 | `bip` | `dist` (exhaustive `5⁹`) | claimed | `R` |
|---|---|---|---|---|---|
| `C₅[2]` − 5 "aligned" perfect matchings (`= C₅ ⊔ C₅`) | `IQGOOIAOO` | 2 | **8** | 10 | **4**, not 5 |
| `C₅[2]` − 5 "crossed" perfect matchings (`= C₁₀`) | `IKC_GP@__` | 0 | **8** | 10 | 2, not 5 |

The table row inside P2.2 hedges with "all `k ≥ 3`", but the sentence under it and the final summary
both claim `k = 2` was verified; it cannot have been. `k = 3` (`j = 1,2,3`) and `k = 4` (`j = 1..4`)
**do** give `bip = k²−j`, `dist = 5j`, `R = 5` exactly (I confirm all seven), so the *conclusion*
`c ≤ 1/5` in `ψ ≤ 1/25 − c·d` survives; only the verification claim is false.

### 5a. REFUTED — "the best possible constant in `ψ ≤ 1/25 − c·d` is `c = 1/5` locally"

Exact falsifiers, at ever smaller `d`, all inside the report's own data:

| witness | `ψ` | `d` | `R = d/(1/25−ψ)` |
|---|---|---|---|
| `K?ABBBwerwBw` (`N=12`, `bip=5`) | `5/144` | `5/144 = 0.0347` | `125/19 = 6.58 > 5` |
| Wagner `Γ₈` uniform (= regression witness **W8**, and pass 1's own table b.6) | `1/32` | `3/64 = 0.0469` | `75/14 = 5.357 > 5` |
| `Γ₁₁ = And(4)` uniform | `4/121` | `6/121 = 0.0496` | `50/7 = 7.14 > 5` |

So `ψ ≤ 1/25 − (1/5)d` already fails at `d = 5/144`; the constant `1/5` is valid only on a
neighbourhood `η ≤ 5/144` that the report never specifies and never proves. (`c = 1/5` *is* correct
as a **ceiling** — no constant above `1/5` can hold — and that part is confirmed by the `k = 3,4`
families.) Protocol step 2 executed: all ten round-5 regression witnesses satisfy `ψ ≤ 1/25` and the
pass-1 envelope `ψ ≤ 1/25 − (19/425)d`; exactly one (W8) violates the `1/5` version; and both
envelopes are **exactly tight at `C5[n]`** for `n = 1..6` (`ψ = 1/25`, `d = 0`), as required.

### 5b. UNSUPPORTED — "the deficit is `Θ(d)`, never `Θ(d²)` … perfect stability cannot fail for a local reason"

Evidence offered: one theorem (the prism, which I confirm and strengthen, item 9) plus three sampled
one-parameter families. That is four directions out of a `dim`-many-dimensional cone of directions at
the extremal point, and the statement quantifies over all of them (and, for a *uniform* conclusion,
over all triangle-free hosts). Nothing in the report bounds `R` uniformly on a neighbourhood — and by
item 5a the constant already breaks at `d = 5/144`. Missing: a uniform lower bound on the directional
derivative, or a compactness argument. The weaker true statement is: *along the four exhibited
families the deficit is linear with `R ∈ {5/2, 5}`*.

### 6. UNSUPPORTED (overstated) — "the class-level cut family cannot perform the local step (S2), at any scale"

The arithmetic is **correct** and I confirm it exactly: on the weighted prism with the *natural*
template `φ(o_j) = φ(i_j) = j`, `E_w = 5αδ`, `F = 0`, `g_j = 2αδ`, the best of the sixteen
class-level cuts is `α² + δ² + 5αδ = 1/25 + 3αδ` (excesses `57/10000, 27/2500, 9/400, 3/100` at
`t = 1/100, 1/50, 1/20, 1/10` — all four reproduce), while `ψ = 1/25 − 2αδ`.
But the report's own next paragraph says the family **is** a valid certificate at the `d`-minimising
template (`1/25 − αδ ≤ 1/25`), and a local step is free to choose the template — it is *given* that
`d` is small, so it takes a near-optimal `φ`. What the prism exhibits is that a *badly chosen*
template is useless, plus a factor-2 loss at the good one. Verdict: the computation is CONFIRMED, the
headline inference ("at any scale", "invalid as a certificate at every scale") is not supported.

### 7. UNSUPPORTED as argued, VALUE CONFIRMED by me — `D(n=3) = 19`

P2.3 says *"Known exactly, by complete enumeration: `D(n=2) = 10` (Petersen), `D(n=3) = 19`."*
For `n = 3` the corpus is **maximal** triangle-free graphs on 15 vertices. Edge-monotonicity of `bip`
lets an MTF corpus decide `max bip`; it does **not** decide `sup dist at a fixed value of bip`,
because `dist` is not monotone under edge deletion (exhibited: `L?`DAboU`w@{hS`, 13 vertices,
28 edges, `bip = 6`, `dist = 14`; its 2-edge-deleted subgraph `L?`DAboU`w@whO`, 26 edges, still has
`bip = 6` but `dist = 15`).
I closed the gap exactly. Every triangle-free `G` on 15 vertices with `bip(G) = 8` is a spanning
subgraph of an MTF graph with `bip ≥ 8`, i.e. of `C₅[3]` or of the two `bip = 8` graphs; and
`{H ⊆ G' : bip(H) = 8}` is connected under single-edge deletion (monotonicity). Complete exploration:

| parent | states with `bip = 8` | max `dist` |
|---|---|---|
| `N?AAD@O{AiN_N_B{TT?` (36 edges) | 1 (no edge may be removed) | 19 |
| `N?ABAaQT?]N_}?iSDM?` (35 edges) | 1 | 19 |
| `C₅[3]` | 3664 | 5 |

Hence `D(n=3) = 19` **exactly** — the value stands, the stated justification did not.
`D(n=2) = 10` is genuinely settled by the complete `N = 10` corpus (I re-derive the histogram
`0:5479, 1:5270, 2:1397, 3:25, 4:1` and `max dist = 10` over the 25 graphs with `bip = 3`).

*Audit-side proposition (proved, explains the `N = 20` non-finding).* For every `n`, every spanning
subgraph `H ⊆ C₅[n]` with `bip(H) = n²−1` has `dist(H) ≤ 5`. Proof: the five cuts
`φ⁻¹({i,i+1,i+3})` have monochromatic count exactly `n²` in `C₅[n]` (only the `(i,i+1)` edges are
monochromatic), so at most one edge may be deleted from each of the five class-pair groups; `≤ 5`
deletions from a blow-up give `dist ≤ 5`. ∎ (Verified at `n = 3`: max is exactly 5.) So `D` is decided
entirely by non-blow-up graphs, and the annealer's failure at `N = 20, dist ≥ 6` is expected on the
near-blow-up side.

### 8. CONFIRMED and STRENGTHENED — `sup R = 425/19`, attained by `C₁₃(1,5)`

`labelg` confirms `L?`DE`gl@YJODg ≅ C₁₃(1,5) ≅ C₁₃(2,3)` (common canonical form
`Ls`?XGRQR@B`Kc`), and I re-derive 4-regular, `α = 4`, 52 pentagons, `bip = 6`, `dist = 17`
(`dist` also by exhaustive `5^12`, no branch and bound), `R = 425/19`. The corpus max is `425/19`.
The corpus is MTF-only for `N ≥ 12`, so the claim as stated does not cover all graphs of those
orders; I closed that too. Using `dist ≤ |E| ≤ ⌊N²/4⌋` and `R > 425/19 ⟺ dist > 17(N²−25·bip)/19`:

| `N` | branches to kill | how killed |
|---|---|---|
| 9,10,11 | — | complete TF corpora |
| 12 | `bip = 5, dist ≥ 18` | complete subgraph exploration of both MTF parents → max `dist = 9` |
| 13 | `bip = 6, dist ≥ 18` / `bip = 5, dist ≥ 40` | exploration of all 3 parents → max `dist = 17` / all 6 TF graphs with `|E| ≥ 40` → max `R = 0.148` |
| 14 | `bip = 7, dist ≥ 19` / `bip = 6, dist ≥ 42` | unique parent → max `dist = 15` / all 382 TF graphs with `|E| ≥ 42` → max `R = 0.765` |
| 15 | `bip = 9` / `bip = 8, dist ≥ 23` / `bip = 7, dist ≥ 45` | only `C₅[3]`, `dist = 0` / item 7 → 19 / all 17 949 TF graphs with `|E| ≥ 45` → max `R = 1` |

**Result (mine): `max{R(G) : G triangle-free, |V(G)| ≤ 15} = 425/19`, attained by `C₁₃(1,5)`** — now
over *all* triangle-free graphs, not just maximal ones.
Caveat that the report does not state: all 126 097 points are the **uniform** weighting only, while
`(S1′)` quantifies over pairs `(H,x)`; the empirical `sup R` is a supremum over a slice.

### 9. CONFIRMED and STRENGTHENED — Theorem P2-A (prism trade-off curve)

Independently re-derived: all `2⁹` cuts give 34 distinct coefficient triples (same count as their
proof file), the candidate `1/25 − 2t(1/5−t)` is realised by a cut, and **no** cut dips below it
anywhere on `[0,1/10]` (each difference minimised at exact rational critical points).
For the distance I did better than the report: instead of confirming `d = 5t(1/5−t)` at six rational
`t`, I enumerated **all `5⁹` templates** (814 distinct coefficient triples) and showed exactly one
realises `5t(1/5−t)` and none goes below it on the whole interval. So `ψ = 1/25 − 2t(1/5−t)` and
`d = 5t(1/5−t)` hold identically, and `R = 5/2` for all `t ∈ (0,1/10]` (at `t = 0`, `R = 0/0`).

### 10. CONFIRMED — the entire empirical dataset and the remaining exact values

* **Row-by-row diff of my scan against `p2_{tf9,tf10,tf11,mtf9..mtf15}.tsv`: 0 differing lines in all
  ten files** (126 097 rows). Corpora independently validated: every graph triangle-free; every
  `mtfN.g6` graph maximal; `tf11` contains exactly 61 maximal ones (= `|mtf11|`); all files pairwise
  non-isomorphic under `labelg` (5036 and 105 071 distinct canonical forms); counts agree with
  A006785 / A024607.
* Band table: all ten rows (`#points`, `max ψ`, deficit, `max R`, witnesses) reproduce exactly.
* `ψ ≥ 1/25`: exactly 3 points, all with `d = 0` (`C₅[2]` twice, `C₅[3]`); all 45 single-edge
  deletions of `C₅[3]` give `bip = 8`.
* `a(9..15) = 2,4,4,5,6,7,9`; MTF15 histogram `0:7,1:31,2:109,3:388,4:971,5:1665,6:1558,7:304,8:2,9:1`;
  both `bip = 8` graphs at `dist = 19`.
* Table b.6 (Andrásfai/circle graphs, Petersen, Grötzsch, Clebsch): all 15 rows reproduce
  (`Γ₈:(2,3), Γ₁₀:(2,5), Γ₁₁:(4,6), Γ₁₂:(2,11), Γ₁₃:(4,10), Γ₁₄:(6,10), Γ₁₅:(4,15), Γ₁₆:(6,15),
  Γ₁₇:(9,15)`, Petersen `(3,10)`, Grötzsch `(4,9)`, Clebsch `(8,31)`).
* `N = 20`, the 99 structured graphs: `bip` histogram `0:30, 2:4, 4:7, 6:9, 8:16, 10:9, 12:21, 16:3`
  — the only `bip = 16` are the three `C₅[4]` copies, next value 12, exactly as claimed.
* Integrality: `R = 25·dist/(N²−25·bip)`; `= dist` at `N = 5n, bip = n²−1`; minimal deficit
  `1/(25N²)` iff `N² ≡ 1 (25)` iff `N ≡ ±1 (25)` (the square roots of 1 in the cyclic group
  `(ℤ/25)*` are `±1`) — correct.
* **Theorem Q3-1** (pass 1 d.1): re-derived line by line — the five cuts do have monochromatic mass
  `p_i − g_i` under `H ⊆ B_φ`; `Σt_i ≥ 4·MISS` from `p_i ≤ 1/4`; `Πp_i ≤ 5^{−10}`; `e^{−y} ≤ 1−0.9y`
  on `[0,1/5]` (chord slope `−0.906344…`); degenerate branch fine. **Valid.**
* **Proposition P2-B**: both inequalities correct (`N(w) ∩ class j` independent by triangle-freeness;
  `e_j ≤ (m_j−α_j)m_j`), and the AM–GM chain to `(1 − Σe_j/m_j)/25` is correct, as is the corollary
  `1/25 + (4/5)E_w + F` at balanced classes.
* **Claim P and pass 2's correction to pass 1**: 0 violations at `K = 25, 30, 45, 60`; at `K = 30`
  there are **76** equality points including `k = (0,14,15,1,0)` (`Σp = 225 = K²/4`, `min p = 0`,
  LHS `= 900 = K²`), so pass 1's "equality exactly at two orbits" is indeed false and pass 2's
  correction is right. (Refinement: at `K = 25, 45` the uniform point *is* the unique equality point —
  the degenerate family needs `K` even — but in the continuous formulation, where Claim P is used, the
  locus is genuinely one-parameter.)
* The conditional consequence of Claim P (`ψ ≤ 1/25 − (4/25)MISS`) re-derived: `4S+5μ ≤ 1`,
  `S ≥ 5ψ + MISS`, `μ ≥ ψ` ⟹ `25ψ + 4·MISS ≤ 1`. Correct.

### 11. UNSUPPORTED — "`R` is blow-up invariant"

Asserted as a general fact ("so `425/19` recurs at every `N = 13t`"), verified in the report on one
example. `ψ` is blow-up invariant (accepted base 1), but `dist(G[t]) = t²·dist(G)` is only clear as
`≤`: the minimising template of a blow-up may split a part, which is a strictly larger search space
(a fractional relaxation of the template problem). Not refuted either: my local search found nothing
below `t²·17` for `C₁₃(1,5)` at `t = 2` (20 000 restarts, best 68) or `t = 3` (4000 restarts, best
153), and `Petersen[2]` is exactly `40 = 4·10` by my B&B. Status: plausible, unproved, and load-
bearing for the density argument of item 1.

### 12. Process checks (all clean)

* **No floating point on any acceptance path.** `Q3_pass2_core.py` uses `numpy` int64 / `Fraction`;
  `Q3_pass2_scan.cpp` is pure `int`; the `double`s in `Q3_pass2_n20.cpp` are the annealer's
  temperature/Metropolis only (search, allowed), and its `bip`/`dist` are integer. The one `float` in
  `Q3_pass2_curve.py` is inside a display string.
* **No `ψ < 1/25` reported as a maximum for an odd-girth-5 graph.** Pass 2's `ψ` is explicitly
  `bip/N²` (the *uniform* weighting), never `max_x ψ`; no conflict with PLATEAU.
* **Zero weights**: pass 2 runs no integer-weight enumeration, so the "must allow zero weights" trap
  is not triggered (pass 1's Wagner optimum at `w = (7,8,0,8,8,0,8,1)` does include zeros).
* **No circularity of strength ≥ the conjecture**, with one exception already logged in item 2: the
  identification "deficit at `bip = n²−1` is exactly `1/N²`" uses `a(5n) = n²`.
* **Quoted theorem hypotheses**: PST's framework requirements (bounded-order density functional;
  certificate value equal to the conjectured optimum) are used correctly against `bip`; the BCL
  density thresholds are used *incorrectly* on a 13-vertex graph (item 1).
* Not verifiable offline: the literature statements (BCL thresholds `0.2486 / 0.3197`, PST Thm 7.1,
  arXiv:2606.28041). Item 1's refutation is robust to either density normalisation, so it does not
  depend on that.

---

## FILES (mine, all in `E:\Projects\ErdosProblems\problems\23\round7\`)

| file | what |
|---|---|
| `audit_Q3.md` | this report |
| `audit_Q3_engine.cpp/.exe` | independent engine: own graph6 codec, `bip` over all `2^{N−1}` cuts, `dist` by own B&B; modes `scan`, `bipscan`, `check`, `sub` (complete subgraph exploration at fixed `bip`) |
| `audit_Q3_blowup.cpp/.exe` | exhaustive `5^{N−1}` `dist` for `N ≤ 13` + exact-integer local search for blow-ups `G[t]` |
| `audit_Q3_prism.py` | exact symbolic audit of Theorem P2-A (all `2⁹` cuts, all `5⁹` templates, sympy rationals) |
| `audit_Q3_named.py`, `audit_named.tsv/.g6` | independent constructions of `C₅[k]`, prism, Petersen, Grötzsch, Clebsch, `C₁₃(1,5)`, `Γ₈…Γ₁₇` |
| `audit_Q3_family.py`, `audit_family.tsv/.g6` | the `C₅[k]` − `j`-matching family (item 4) |
| `audit_Q3_invariants.py` | `α`, pentagon count, degree sequence of `C₁₃(1,5)`; both `k=2,j=2` variants |
| `audit_Q3_table.py` | band table + BCL band + `a(N)` rebuilt from my scans in exact `Fraction`s |
| `audit_Q3_band.py` | item 1: blow-up families inside the open BCL band |
| `audit_Q3_regression.py` | protocol step 2: the ten round-5 witnesses vs `ψ ≤ 1/25`, the `19/425` envelope, the `1/5` ceiling, plus `C₅[n]` tightness |
| `audit_{tf9,tf10,tf11,mtf9..mtf15}_scan.tsv` | my 126 097 rows (diff 0 against `p2_*.tsv`) |
| `audit_tf13_dense.g6`, `audit_tf14_dense.g6`, `audit_tf15_dense.g6` | `geng`-generated dense branches used in item 8 |
| `audit_c13_t3.log`, `audit_n20_bip.tsv`, `audit_iso.g6`, `audit_can{11,15}.g6` | supporting runs |
