# AUDIT of round3/G11.md (adversarial)

Auditor scripts (all independent re-implementations; nothing imported from `G11_verify_*.py`):

- `E:\Projects\ErdosProblems\problems\23\round3\audit_G11_core.py` (+ `audit_G11_core_out.txt`)
- `E:\Projects\ErdosProblems\problems\23\round3\audit_G11_lit.py`
- `E:\Projects\ErdosProblems\problems\23\round3\audit_G11_ladder.py` (+ `audit_G11_ladder_out.txt`)
- `E:\Projects\ErdosProblems\problems\23\round3\audit_G11_wlfalsifier.py` (+ `audit_G11_wl_out.txt`)

My max-cut is a different algorithm from the target's (adjacency bitmasks, crossing-edge count
`sum_{v in S} popcount(adj[v] & ~S)` over the 2^(n-1) bipartitions) — exact integers throughout.
My Vega construction was retyped from the Brandt–Thomassé source text, my Andrásfai isomorphism
is an explicit multiplier map, my graph6 decoder is my own. `audit_G11_core.py`: 0 failures.
`audit_G11_lit.py`: 0 failures. `audit_G11_ladder.py`: 0 failures.

Sources actually read in full during this audit (not just abstracts): Heinig arXiv:0907.3928v3
(7 pp.), Norin–Sun arXiv:1602.04370v1 (pp. 1–3), Balogh–Clemen–Lidický arXiv:2103.14179v1
(all 6 pp.), Wang–Yang–Zhao arXiv:2408.05547v1 (pp. 1–3), Brandt–Thomassé `vega11.pdf`
(pp. 1–6), Łuczak–Polcyn–Reiher arXiv:2002.01498v2 (pp. 1–8, 13, 22),
Balogh–Clemen–Lidický arXiv:2203.15764, Razborov arXiv:2104.09406v2.

---

## 1. REFUTED — the report's own "corrected record" understates the record at every n

Report §0.1: *"the best published unconditional bound is bip(G) ≤ n²/23.5 = 2n²/47 for all
sufficiently large n (BCL 2021); for all n the best fully explicit bound remains
bip(G) ≤ n²/18 + n/2"*; the summary table repeats "n large — CURRENT RECORD".

**This is false.** BCL themselves remove the `n₀` in their §2.3 by the blow-up argument, and
that argument is campaign fact 4, which the report cites in its own §a.3. Explicitly: if
`bip(G) ≤ c·n²` for all `n ≥ n₀` and some `G` on `n < n₀` had `bip(G) > c·n²`, take the balanced
blow-up `G'` with parts of size `t = ⌈n₀/n⌉`; then `bip(G') = t²·bip(G)` (fact 1) and
`|V(G')| = tn ≥ n₀`, so `c ≥ bip(G')/(tn)² = bip(G)/n² > c`. Contradiction.

Hence **`bip(G) ≤ 2n²/47` holds for every `n ≥ 1`**, and `n²/18 + n/2` is strictly worse at
every `n ≥ 1` (`1/23.5 < 1/18`). The row "n large" in the report's table is wrong for BCL 2(a),
2(b) and 2(c) alike (2(b),(c) are density-conditional but their `n₀` is removable the same way
only if one also tracks the density under blow-up — which is preserved up to `2m/n²` vs
`2m/(n(n−1))`, so state that one with care).

Consequence for the campaign: the *unconditional* gap to close is `2/47 → 1/25`, i.e.
`0.0425532 → 0.04`, at **every** `n`, with no threshold escape hatch.

---

## 2. REFUTED — "δ₂ > ⌊n/8⌋ is a region strictly containing δ > ⌊3n/8⌋"

Report §b.2 and summary item 2 assert that the settled region `{δ₂(G) > ⌊n/8⌋}` *contains*
`{δ(G) > ⌊3n/8⌋}`.

**Exact falsifier (verified in `audit_G11_core.py` part G):**

> `G = K_{8,8}` minus a perfect matching. `n = 16`, `|E| = 56`, triangle-free (bipartite),
> `δ(G) = 7 > ⌊3·16/8⌋ = 6`, but `δ₂(G) = 0 ≤ ⌊16/8⌋ = 2`.

`δ₂ = 0` because for `u ∈ X` and its unmatched partner `v ∈ Y` the pair `uv` is a non-edge with
`N(u) ⊆ Y`, `N(v) ⊆ X`, so `N(u) ∩ N(v) = ∅`. The same construction works for every even
`n ≥ 16` (`K_{n/2,n/2}` minus a perfect matching: `δ = n/2 − 1 > 3n/8` for `n ≥ 9`).

**What survives.** WYZ derive Häggkvist from their Thm 1.4(ii) via their Lemma 1.5, whose
hypothesis is *maximal* triangle-free (I read this on p. 3 of arXiv:2408.05547: they apply
Lemma 1.5 with `α = 1/15` and `α = 1/24`). Completing `G` to a maximal triangle-free `G'`
preserves triangle-freeness, does not lower `δ`, and `G ⊆ G' → C₅` implies `G → C₅`. So the
*implication* is valid, the union of settled classes does strictly grow (their `G₂` witness,
which I reproduced exactly as `C5[7,14,7,7,14]`, `n = 49`, `δ = 14 ≤ ⌊3n/8⌋ = 18`,
`δ₂ = 7 > ⌊n/8⌋ = 6`, maximal triangle-free), and the campaign may indeed assume
`1 ≤ δ₂ ≤ ⌊n/8⌋` for a minimal counterexample (fact 6 gives `δ₂ ≥ 1`). But the containment
claim as written is false.

**Additional deflation.** WYZ **does not shrink the min-degree band at all**: Lemma 1.5 with
`α = 1/24` converts `δ > 3n/8` into `δ₂ > n/8` and back, so the settled min-degree threshold is
still exactly `3n/8`. Under the campaign's rules of evidence ("an unconditional theorem valid on
an explicit minimum-degree range IS valuable (it shrinks the open band)"), exploitable item 2
delivers a `δ₂` side condition, not a band reduction.

---

## 3. REFUTED — misattribution of the quantitative Andrásfai threshold

Report §b.3(i): *"The quantitative form used by Łuczak–Polcyn–Reiher (arXiv:2002.01498, Thm 1.3)
… is: triangle-free, χ(G) ≤ 3 and δ(G) > ((k+1)/(3k+2))·n ⇒ G → And_k."*

LPR Theorem 1.3 (read on p. 3 of arXiv:2002.01498v2) says something else entirely: for `k ≥ 2`
and `n ≥ s ≥ 1`, if `H` is triangle-free on `n` vertices **with independence number
`α(H) ≤ s`** and `δ(H) > ((k+1)/(3k+2))n`, then **`e(H) ≤ g_k(n,s)`** — a Ramsey–Turán edge
count. There is no `χ ≤ 3` hypothesis and no homomorphism conclusion. This is exactly the audit
failure mode "a quoted theorem whose hypotheses do not match the use made of it".

The threshold `((k+1)/(3k+2))` *is* the right one, but its correct provenance is LPR **Fact
2.1(b)** + LPR **Theorem 5.1** (their statement of Brandt–Thomassé), or the published
Jin + Chen–Jin–Koh pair. See §4.

---

## 4. MISSED — the sharp form the report's own sources give (highest-value finding)

Report exploitable #1 reduces `δ > n/3` to the **infinite** family `{And_i} ∪ {Vega}` and then
flags "a uniform-in-i argument is needed" as the risk. Its own quoted Brandt–Thomassé
Corollary 4.3(3)/(4) and LPR Fact 2.1(b) give a **one-graph-per-threshold ladder** instead.

**LADDER (assembled and machine-checked in `audit_G11_ladder.py`, 0 failures).**
For every integer `1 ≤ k ≤ 9`: every triangle-free `G` on `n` vertices with
`δ(G) > ((k+1)/(3k+2))·n` is homomorphic to the **single** Andrásfai graph `And_k` on `3k−1`
vertices. Hence, by campaign fact 2,

  `bip(G) ≤ n² · max_x ψ(And_k, x)`,

so the conjecture holds on that entire min-degree range as soon as
`max_x ψ(And_k, x) ≤ 1/25`.

*Proof.* Complete `G` to a maximal triangle-free `G'` (fact 6; `δ` does not drop). Since
`(k+1)/(3k+2) > 1/3`, LPR Theorem 5.1 (= Brandt–Thomassé) makes `G'` a proper blow-up of some
`Γ_ℓ` or Vega graph `J`. Every such `J` has an `ℓ`-regular proper blow-up on `3ℓ−1` vertices,
with `ℓ(Γ_ℓ) = ℓ` and `ℓ(Υ^{μν}_i) = 9i − (6+μ+ν)`. LPR Fact 2.1(b) then gives
`δ(G') ≤ ℓn/(3ℓ−1)`. The map `t ↦ t/(3t−1)` is strictly decreasing, so
`ℓ/(3ℓ−1) > (k+1)/(3(k+1)−1)` forces `ℓ ≤ k`. The smallest Vega `ℓ`-value is `9·2 − 8 = 10`
(attained by `Υ_2 − {y,4}` = Grötzsch), so for `k ≤ 9` the target is an Andrásfai graph `Γ_ℓ`,
`ℓ ≤ k`, and `Γ_ℓ` is an **induced** subgraph of `Γ_k` (Heinig Lemma 2; verified for
`k = 3..10` by exact isomorphism in `audit_G11_ladder.py` part 3). Hence `G → And_k`. ∎

For `k ≤ 9` the unpublished Brandt–Thomassé manuscript is **not needed**: the threshold satisfies
`(k+1)/(3k+2) ≥ 10/29` exactly for `k ≤ 9` (equality at `k = 9`), so Jin 1995 gives `χ(G) ≤ 3`
and Chen–Jin–Koh 1997 gives `G → And_i` for some `i`; the same degree count (`δ(G) ≤ in/(3i−1)`
for a proper blow-up) forces `i ≤ k`.

Exact ladder (all rationals verified):

| k | threshold `(k+1)/(3k+2)` | decimal | target | `|V|` | status |
|---|---|---|---|---|---|
| 1 | 2/5 | 0.400000 | `And_1 = K_2` | 2 | trivial (AES) |
| 2 | 3/8 | 0.375000 | `And_2 = C_5` | 5 | **done** (`max ψ = 1/25`, Häggkvist) |
| 3 | **4/11** | **0.363636** | `And_3 = Wagner V8` | **8** | **first open; shrinks the band** |
| 4 | 5/14 | 0.357143 | `And_4` | 11 | open |
| 5 | 6/17 | 0.352941 | `And_5` | 14 | open |
| 6 | 7/20 | 0.350000 | `And_6` | 17 | open |
| 7 | 8/23 | 0.347826 | `And_7` | 20 | open |
| 8 | 9/26 | 0.346154 | `And_8` | 23 | open |
| 9 | 10/29 | 0.344828 | `And_9` | 26 | open (Jin's exact value) |
| ≥10 | < 10/29 | | Vega graphs enter (`ℓ ≥ 10`) | | |

Two consequences the report does not state:

- **`max_x ψ(V8, x) ≤ 1/25` — one 8-vertex graph — unconditionally shrinks the campaign's open
  min-degree band from `(0.16, 0.375]` to `(0.16, 4/11] = (0.16, 0.363636…]`.** By fact 3 the
  target is equality (`V8` has odd girth 5), and `ψ(V8, uniform) = 1/32` is *not* the maximum.
- **Heinig's Conjecture 6 is far more than the `δ > 10n/29` case needs.** The `10n/29` band
  requires only `max_x ψ(And_9, x) ≤ 1/25`, a single 26-vertex graph — and since
  `And_k ⊆ And_9` induced for `k ≤ 9`, that single statement implies all of `k ≤ 9` by fact 3.
  The report's BLOCKED entry ("Prove the conjecture for graphs homomorphic to an Andrásfai
  graph … blocked by Heinig Conjecture 6") therefore over-blocks: the finite sub-statements
  `k = 3, 4, …, 9` each *shrink the band* and are not equivalent to the full conjecture.

Ladder sharpness is exact: the balanced blow-up of `And_{k+1}` has `δ/n = (k+1)/(3k+2)` exactly
(so it is excluded by the strict inequality), while the balanced blow-up of `And_k` has
`δ/n = k/(3k−1) > (k+1)/(3k+2)` (verified for `k = 2..7`).

---

## 5. UNSOUND METHOD (true conclusion) — `Γ_i ≅ And_i` via a WL-1 certificate

`G11_verify_andrasfai.py` part (D) certifies `Γ_i ≅ And_i` for `i = 2..7` by comparing
`canonical_certificate`, a degree/WL-1 colour refinement. On **vertex-transitive regular** graphs
that refinement is constant, so the certificate degenerates to `(n, |E|, const, const)` and
distinguishes nothing.

**Exact falsifier of the method (`audit_G11_wlfalsifier.py`):** the Wagner graph `V8` and the
3-cube `Q3` are both 3-regular on 8 vertices with 12 edges; the target's certificate declares
them equal, yet `Q3` is bipartite and `V8` is not, so they are non-isomorphic.

**The conclusion is nevertheless TRUE**, and I proved it exactly rather than heuristically:
multiplication by 3 is a group automorphism of `Z_{3i−1}` sending the Brandt–Thomassé connection
set `{i, …, 2i−1}` onto `{1, 4, …, 3i−2}` = Heinig's set of differences `≡ 1 (mod 3)`, because
`3(i+t) ≡ 1 + 3t (mod 3i−1)` for `0 ≤ t ≤ i−1`. Verified as an edge-set bijection for
`i = 2..11` in `audit_G11_core.py` part D.

---

## 6. OVERSTATED — "exact reduction ⟺" for the `δ > n/3` band

Report exploitable #1: *"`bip(G) ≤ n²/25` for all triangle-free `G` with `δ(G) > n/3`
**⟺** `max_x ψ(H, x) ≤ 1/25` for `H ∈ {And_i} ∪ {Vega}`"*.

Only `⟸` is established. `max_x ψ(H,x)` ranges over the **whole** simplex, including weight
vectors whose weighted minimum degree is `≤ 1/3`; the corresponding blow-ups of `H` are
triangle-free graphs with `δ ≤ n/3` and are *not* covered by the left-hand side. Brandt–Thomassé
Corollary 4.1 has `δ > 1/3` as a hypothesis on the weighted graph, so it cannot deliver the
`⟹` direction. The correct statement is `⟸` (which is all the campaign needs) plus
`⟹` restricted to `x` with weighted min degree `> 1/3`. Calling it an "exact reduction, not a
reformulation" is not supported by the quoted corollary.

Related risk the report notes but does not weight: **Brandt–Thomassé is an unpublished
manuscript** (Heinig 2009 already cites it as "to appear in JCTB"; LPR 2021 still cite it as
[8] and say it "plays a decisive rôle" in their proof). Any deliverable resting on it inherits
that status. §4 above shows the `k ≤ 9` rungs do not.

---

## 7. OVERSTATED — "EGS 1992 Theorem 7 is the source of campaign facts 1 and 4"

Report §a.3. What BCL actually cite EGS Theorem 7 for is the blow-up **monotonicity** inequality
`D₂(G′)/(⌈n₀/n⌉ n)² ≥ D₂(G)/n²` (their eq. (8), read on p. 5 of arXiv:2103.14179v1) — i.e.
campaign fact 4. The exact blow-up **identity** of campaign fact 1
(`bip(H[a]) = min over cuts of Σ a_u a_v`) is a different and stronger statement and is not
established by that citation. In BCL's "10 problems" the EGS Theorem 7 quote is about `D₃`, not
`D₂`. Recommendation: keep fact 1 as the campaign's own proved statement; cite EGS Thm 7 only
for fact 4.

---

## 8. Minor inaccuracies inside "verbatim" quotes

- Report §0.1 quotes Balogh–Chen–Lidický arXiv:2606.20397 as crediting "Balogh, Clemen, and
  Lidický **[3]**". The paper's own reference number in that sentence is **[4]**. Everything else
  in that sentence matches character-for-character.
- Report §(f) attributes `|E| + bip ≤ n²/4` for triangle-free `G` to Norin–Sun. Norin–Sun's own
  introduction (which the report quotes elsewhere) records that **Puleo** already proved the
  inequality for triangle-free graphs; Norin–Sun's new content is the general case and the
  equality characterisation. Attribution should be Puleo (inequality) + Norin–Sun (equality).

---

## 9. UNVERIFIED (not refuted): EFPS 1988 beyond Theorem 1

JCTB 45 (1988) 86–98 is paywalled and I could not read it. I independently confirmed
**Theorem 1** because BCL restate it verbatim (p. 2 of arXiv:2103.14179v1) in exactly the form
the report gives, including the `≤ n²/18` tail. The report's quotations of EFPS **Theorem 2,
Theorem 3, Theorem 4, Corollary 2.6, Lemma 2.1, Lemma 2.4, Proposition 2.5** rest on a source I
could not open; treat them as unverified transcription.

I did verify EFPS Theorem 1 **empirically** as a mathematical statement: over all
`14 + 38 + 107 + 410 + 1897 + 12172` triangle-free graphs on `n = 5..10` from `geng -t`
(`audit_G11_lit.py`), `bip ≤ m − 4m²/n²` never fails, and the first term never fails either
(guarding `n² ≠ 2m`).

---

## 10. CONFIRMED claims (independent exact reproduction)

| claim | verdict | my value |
|---|---|---|
| arXiv:2103.14179 has one version, comments = EuroComb 2021 abstract, no journal-ref | CONFIRMED | fetched arXiv abs page |
| No Combinatorica version; only publication is EuroComb 2021 Trends in Math. 14, 509–514 | CONFIRMED | Illinois Experts + Springer listing; Balogh's own page notes "journal version still in preparation" |
| Best published constant is `n²/23.5 = 2n²/47`, not `0.0409 n²`; `0.0409 < 2/47` | CONFIRMED | `2/47 = 0.0425531…`, exact Fraction check |
| Balogh–Chen–Lidický arXiv:2606.20397 (18 Jun 2026) still records `n²/23.5` as the record | CONFIRMED | quote located in the HTML full text (ref. number is [4], not [3]) |
| BCL Theorem 2(a)(b)(c), Theorem 3 (EGS), Theorem 4, Lemma 1, cut counts 10/108/953/125, the Clebsch-cut root, the `K₂∪K₂∪K₂` extension, §2.3 "marginal improvements" | CONFIRMED verbatim | read arXiv:2103.14179v1 pp. 2–6 |
| Heinig Theorem 3 formulas for `U_k^{(1)}, U_k^{(2)}`, Conjecture 5, Conjecture 6, the (1)/(2) dichotomy | CONFIRMED verbatim | read arXiv:0907.3928v3, all 7 pp.; the target's `heinig_F(k)` reproduces (1),(2) index-for-index |
| `F_k ⊆ E(And_k)`, `And_k − F_k` bipartite, `\|F_k\| = ⌊k²/4⌋ = ⌊(n+1)²/36⌋` | CONFIRMED, extended to `k = 2..11` | `audit_G11_core.py` part B |
| `bip(And_k) = ⌊k²/4⌋`, i.e. Heinig Conjecture 5, for `k ≤ 6` | CONFIRMED, **extended to `k = 7`** | exhaustive max-cut: `1, 2, 4, 6, 9, 12` for `k = 2..7`; ratios `1/25, 1/32, 4/121, 3/98, 9/289, 3/100` |
| `⌊(n+1)²/36⌋ ≤ n²/25` for `n = 3k−1`, equality only at `k = 2` | CONFIRMED and **upgraded from a finite check to a proof**: `k²/4 ≤ (3k−1)²/25 ⟺ 11k² − 24k + 4 ≥ 0`, roots `2` and `2/11`, so it holds for every integer `k ≥ 2` with equality exactly at `k = 2` | `audit_G11_core.py` part C |
| `Γ_3 = And_3 = Möbius ladder M₈ = Wagner V8`, `bip = 2`, ratio `1/32` | CONFIRMED | exhaustive `8!` isomorphism + exact max-cut |
| all four Vega families `i = 2..6`: triangle-free, maximal triangle-free, twin-free, BT weights regular with degree `9i−6 / 9i−7 / 9i−7 / 9i−8` and totals `27i−19 / 27i−22 / 27i−22 / 27i−25` | CONFIRMED | independent construction, `audit_G11_core.py` part E; cross-checked against LPR's `ℓ = 9i−(6+μ+ν)` and `3ℓ−1` |
| `Υ_2 − {y,4}` is the Grötzsch graph, 11 vertices, 20 edges, `χ = 4` | CONFIRMED **and strengthened**: exact isomorphism to the Mycielskian of `C₅`, not just `χ`/`n`/`m` | `audit_G11_core.py` part F |
| largest `bip/n²` over the Vega graphs is `Υ_3 − {2i}` = `8/225` | CONFIRMED exactly | `8/225 < 9/225 = 1/25` |
| `ψ` at the BT weights ranges `0.0345 … 0.0314`, decreasing in `i` per family | CONFIRMED exactly | max `1/29 = 0.0344827…` (`Υ_2−{y,4}`), min `19/605 = 0.0314049…` (`Υ_5−{y,2i}`) |
| §0.2's own caveat that every ψ table entry is a LOWER bound only | CONFIRMED and **verified structurally**: every Vega graph I built has odd girth exactly 5 and an explicit induced `C₅`, so `max_x ψ ≥ 1/25` for all 20 of them by fact 3 | `audit_G11_lit.py` part 4 |
| EFPS Thm 1 second term: `c − 4c² ≤ 1/25 ⟺ c ≤ 1/20 or c ≥ 1/5`, equality at both | CONFIRMED | `100c² − 25c + 1 = (5c−1)(20c−1)` |
| BCL's density thresholds `0.172` / `0.4` come from the two terms of EFPS Thm 1 | CONFIRMED | BCL p. 2 says "roughly at most `0.086n²` … at least `n²/5`", and `0.086·2 = 0.172`, `0.2·2 = 0.4` |
| Norin–Sun Theorem 4 statement and equality characterisation | CONFIRMED verbatim | read arXiv:1602.04370v1 p. 2 |
| `α₁ = |E|` for triangle-free ⇒ `|E| + bip ≤ n²/4`, equality only at `K_{n/2,n/2}` | CONFIRMED **exhaustively**: over all triangle-free graphs on `n ≤ 10`, no violation; equality occurs exactly `5` times, at `K_{1,1}, K_{2,2}, K_{3,3}, K_{4,4}, K_{5,5}` | `audit_G11_lit.py` part 1 |
| combining with `m/2` and EFPS maxes at `n²/16` at `c = 1/8`; NS alone gives the conjecture for `m ≥ 0.21n²` | CONFIRMED | `1/4 − 21/100 = 1/25` exactly |
| SRG ratios `1/32, 1/50, 3/112, 7/200`, all `< 1/25` | CONFIRMED | exact Fractions |
| §(f) observation `ν_odd(C5[n]) = bip(C5[n])` | CONFIRMED at `n = 2` by an explicit decomposition of `C5[2]` into 4 edge-disjoint pentagons using all 20 edges, matching `bip = 4` | `audit_G11_lit.py` part 5 |
| BCL "10 problems" quotes (Brandt/Higman–Sims `α < 0.474`, Question 2.2, EGS canonical edge deletion for `D₃`, the equality sentence) | CONFIRMED verbatim | read arXiv:2203.15764 |
| Razborov quotes (abstract; "the number 27/1024 … is not arbitrary … Clebsch … extremal example") | CONFIRMED verbatim | read arXiv:2104.09406v2 |
| Brandt–Thomassé Theorem 1, Theorem 3, Theorem 4, Corollaries 4.1/4.2/4.3(3), the `Γ_i` definition, the Vega construction, the four weightings | CONFIRMED verbatim | read `vega11.pdf` pp. 3–5 |
| WYZ Theorem 1.2/1.3/1.4/Lemma 1.5 and the `G₂` witness | CONFIRMED verbatim | read arXiv:2408.05547v1 pp. 1–3 |

**Failure-mode checklist (all explicitly checked):** no floating point on any acceptance path in
either target script or in mine (floats appear only in print formatting); the target's max-cut is
a genuine exhaustive minimum over all `2^(n−1)` bipartitions, not a greedy or local optimum
(re-derived by a different formula here); no ψ value below `1/25` is reported as a maximum — the
report's §0.2 states the plateau caveat correctly and I verified the structural precondition
(odd girth 5 + induced `C₅`) for all 20 Vega graphs; no integer-weight enumeration is involved;
triangle-freeness is asserted and verified everywhere it is used; the report's `n = 3k−1`
Andrásfai sizes are odd/even and non-multiples of 5 without incident, and the Vega graphs are
connected with no isolated vertices; the constant is never weakened to `1/25 + ε` (but see §1 for
a hidden and *removable* "`n` sufficiently large"); no finite verification is presented as a
general argument except the `⌊(n+1)²/36⌋ ≤ n²/25` check, which I upgraded to a proof; and the
circularity check is where the report is strongest — its BLOCKED section is correct in each case,
except that the Andrásfai entry over-blocks (see §4).

---

## 11. UNSUPPORTED (may be true; not established by the report)

- **"a small new fact"** / "(new)" for `bip(And_k) = ⌊k²/4⌋`, `k ≤ 6`. Heinig's §3.1 offers no
  computation and says only that he thinks it likely, so nothing contradicts novelty — but the
  report supplies no evidence that the small cases were not checked elsewhere in 17 years.
  Mathematically the statement is CONFIRMED and I extended it to `k = 7`.
- **"I could find no source"** for `δ > 10n/29 ⇒ conjecture`. A negative literature claim cannot
  be verified. It is consistent with everything I read: by §4 that band is exactly
  `max_x ψ(And_9, x) ≤ 1/25`, which is open.
- **Report §a.5**: "Any counterexample therefore lives at density strictly between 0.2486 and
  0.3197 of `binom(n,2)`". True only for large `n`, and the blow-up upgrade preserves
  `2m/n²` but not `2m/(n(n−1))` exactly; the safe statement is in terms of `m/n²`.
- Pikhurko–Sliačan–Tyros: the report's reason for inapplicability (their `λ` must be linear in
  order-`κ` subgraph statistics, `D₂` is a min over `2^{n−1}` cuts) is a correct reading of the
  method's shape, but I did not read JCTB 135 (2019) 129–178 and cannot certify the hypothesis
  text.

---

## 12. Material omission

BCL's "10 problems" records that **Krivelevich observed that the sparse-half conjecture
(Erdős, $250) implies the `n²/25` conjecture for regular graphs**. The report cites Razborov's
`27/1024` bound on exactly that sparse-half problem (as a BLOCKED item) without noting the
implication. That link makes Razborov's `27/1024 = 0.0263671875` relevant to the regular case;
`27/1024 > 1/50 = 0.02`, so the sparse-half conjecture itself is still open and the link is not
a route — but it belongs in a literature reference file.

---

## Verdict summary

The report is unusually careful about its own limits (the `ψ`-plateau caveat in §0.2 is correct
and I verified the structural precondition for it), its verbatim quotations are accurate to the
character in every source I could open, and its exact computations all reproduce. Three claims
are wrong (§1, §2, §3), two are overstated (§6, §7), one verification method is unsound though
its conclusion is true (§5), and the single most valuable item in the report's own sources — the
one-graph-per-threshold ladder culminating in an 8-vertex target that would shrink the open band
— was not extracted (§4).
