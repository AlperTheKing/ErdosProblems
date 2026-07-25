# AUDIT of G12 — adversarial re-verification

Auditor label `audit_G12`. Nothing below imports or runs any `G12_*` file; every number
was produced by a from-scratch re-implementation (own graph6 decoder, own exhaustive
max-cut, own cycle enumerator, own exact rational simplex, own certificate checker) in
`audit_G12_core.py`, `audit_G12_named.py`, `audit_G12_n12gap.py`, `audit_G12_misc.py`,
`audit_G12_residue.py`, `audit_G12_scan.cpp`, `audit_G12_pack.cpp`.
All acceptance arithmetic is `Fraction` / integer.

---

## 0. Headline

The report's mathematics is, with two exceptions, **correct and independently reproduced**.
Its *only positive deliverable* — the "NEW COVERING THEOREM" P3 and the "DENSITY BAND
CLOSED" P4 — is **not new**: it is verbatim the second term of Theorem 1 of
Erdős–Faudree–Pach–Spencer 1988 and its published consequence, and the band it "closes"
is **strictly larger** (i.e. weaker) than the band already closed by Balogh–Clemen–Lidický,
the paper named in this campaign's own prompt. Net contribution to the open problem: **zero**.

The report's negative results (the packing/covering LP route is dead) are correct and were
already implied in one line by the campaign's own accepted fact 8.

I resolved the report's one declared open arithmetic (the N = 12 sweep) and it **contradicts
the report's minimality framing**: exact integrality-gap witnesses exist at N = 12. I also
enumerated *all* extremal graphs at N = 12 and N = 13, which **refutes the report's bolded
characterisation of the extremal objects** and supersedes its N = 14 "headline" falsifier by
a smaller, sharper one at N = 13.

---

## 1. Verdict table

| # | claim (report) | verdict |
|---|---|---|
| P3/P4 novelty | "genuinely new unconditional covering theorem", "DENSITY BAND CLOSED", "open band is now exactly 0.08N² < \|E\| < 0.2N²" | **REFUTED (novelty + band)** |
| P3 | `bip ≤ min_v e(G−N(v)) = m − max_v Σ_{u∈N(v)} d(u) ≤ m − (1/N)Σd² ≤ m − 4m²/N² ≤ N²/16` | CONFIRMED (mathematically) |
| P4 (A),(B) | `m ≥ N²/5 ⇒ bip ≤ N²/25`; `m ≤ 2N²/25 ⇒ bip ≤ N²/25` | CONFIRMED, **published 1988** |
| P4 (C) | `Δ ≥ 3N/5 ⇒ bip ≤ N²/25` | CONFIRMED, trivial, novelty UNSUPPORTED, and superseded by its own α-version |
| P1 | `nu*(C5[n]) = tau*(C5[n]) = n² = bip` with closed-form certificate pair | CONFIRMED |
| P2 | `nu* = tau* ≤ \|E\|/5 ≤ N²/20`, equality iff a 5-cycle packing saturates every edge | CONFIRMED |
| R1(ii) | N = 14, `M?AE@bH{AYN_LgBs?`: `bip = 7`, `nu* = 32/5`, gap `35/32`, deficit `3/5` | CONFIRMED |
| R1(i) | OK5: N = 13, \|E\| = 18, `bip = 4`, `nu* = 10/3`, gap `6/5` | CONFIRMED **except girth** |
| R1(i) | "OK5 … girth 5" | **REFUTED: girth(OK5) = 4** |
| P1 | "**The extremal objects up to N = 13 are exactly the graphs on which the trivial uniform cover `x ≡ 1/5` is LP-optimal and integral**"; "Same phenomenon on the extremal graphs at N = 12 (both of them) and N = 13: there `bip = nu* = \|E\|/5` exactly" | **REFUTED: 4 of the 8 extremal graphs at N = 13 have `bip = 6 > \|E\|/5 ≥ nu*`** |
| R1(ii) | the N = 14 graph as *the* first/headline extremal object where the LP fails | **REFUTED: superseded at N = 13** (gap `≥ 15/13 = 1.154 > 35/32`, deficit `≥ 4/5 > 3/5`) |
| R1 | "minimum witness size is 12, 13 or 14" | **REFUTED / RESOLVED: it is exactly 12** |
| R1 | "no gap witness on N ≤ 11" (evidence: float LP) | claim TRUE — I re-proved it exactly; the report's own evidence is UNSUPPORTED (float on the acceptance path) |
| R2 | mechanism breaking values (Petersen 6, Clebsch 15, And(3..6), N=14 extremal 9, M5 on C5) | CONFIRMED |
| R2 | "worst M1 ratio found 5/81 = 0.061728"; scan table "N = 8: max M1 = 3" | **REFUTED: sup M1/N² = 1/16 = 0.0625, attained; max M1 at N = 8 is 4 (C8)** |
| R2 | `sup M2/N² ∈ [15/256, 1/16]` | CONFIRMED but self-superseded (their own Higman–Sims number gives 616/10⁴ = 0.0616 as the lower end) |
| R3 | regular ⇒ `nu* ≤ N²/25`; the `π > N²/25` refutation test is blocked | CONFIRMED, but **understated**: the test can never fire on *any* triangle-free graph |
| P5 | `bip = nu* ⇒ bip ≤ N²/25`; Guenin ⇒ #23 on odd-K5-minor-free | CONFIRMED (planar half is vacuous: `\|E\| ≤ 2N−4`) |
| P6 | T-join / cographic-matroid and double-cover formulations | CONFIRMED (and it is a rename, not progress) |
| exact values | the report's table of `bip`, `nu*`, `\|E\|`, gaps | CONFIRMED except the two entries above |
| artifacts | "doubly certified", "full list printed by `G12_f_n14witness.py`" | **UNSUPPORTED: `G12_f_out.txt` is truncated before any nu* line; `G12_a_out.txt` has no N=14 enumeration line.** The claims are nevertheless true (I verified them by two routes) |

No circularity anywhere: nothing in the report assumes a statement of strength ≥ the
conjecture. No hidden `1/25 + ε`, no "N sufficiently large".

---

## 2. The decisive finding: P3/P4 is Erdős–Faudree–Pach–Spencer 1988

Balogh–Clemen–Lidický, *Max cuts in triangle-free graphs*, arXiv:2103.14179 §1
(the paper named in the campaign prompt), state the prior art verbatim:

> "For every triangle-free graph with n vertices and m edges:
> `D₂(G) ≤ min{ m/2 − 2m(2m² − n³)/n²(n² − 2m) , m − 4m²/n² } ≤ n²/18`."
> "This result confirmed Erdős' conjecture for graphs with roughly at most 0.086n² edges
> and graphs with **at least n²/5 edges**."

and the supporting lemma is EFPS Lemma 2.1 (as recorded verbatim by the sibling agent in
`round3/G11.md`, §a.2):

> **LEMMA 2.1.** *Every triangle-free graph G has a vertex x such that
> `|E(G[Γ̄(x)])| ≤ |E(G)| − 4|E(G)|²/|V(G)|²`.*

That lemma **is** the report's P3(1)–(3); the report's P3(4) is EFPS's `≤ n²/18` step in a
weaker form (`N²/16` instead of `n²/18`); and the report's P4 (A)+(B) is exactly the
sentence "confirmed Erdős' conjecture for … at most 0.086n² edges and … at least n²/5 edges".
The same range is what the UCSD Erdős-problems page records as already done
("Erdős, Győri and Simonovits proved this conjecture for graphs with at least 5n² edges …
the general conjecture is still open for graphs with e edges for 2n² < e ≤ 5n²").

Three consequences.

1. **The claimed theorem is 38 years old.** "NEW COVERING THEOREM (mechanism new to this
   campaign)" is false even *within* the campaign: `round3/G11.md` (same directory, same
   round) already contains the quote above plus the derived sentence *"So EFPS Theorem 1
   already proves the conjecture for `m ≤ n²/20` and for `m ≥ n²/5`, tightly at both ends."*
2. **The claimed band is wrong as a statement about the open problem.** BCL prove the
   conjecture for edge density `≤ 0.2486` and `≥ 0.3197`, i.e. (density = `m/C(n,2)`, so
   `m ≈ density·n²/2`) for `m ≤ 0.1243 N²` and `m ≥ 0.15985 N²`. The report's
   "Open band is now **exactly** `0.08 N² < |E| < 0.2 N²`" is therefore false: the truly
   open band is `0.1243 N² < |E| < 0.15985 N²`, strictly inside the report's. P4 re-closes
   an already-closed region and leaves open a region that is already closed.
   *Fairness caveat, stated explicitly:* the report's (A) and (B) are exact at every finite
   `N`, whereas the BCL flag-algebra ranges may carry an `o(N²)`/large-`N` qualifier that I
   did not verify from the source. Even under the most favourable reading of that caveat the
   report gains nothing: the dense half `m ≥ N²/5` is EFPS Theorem 1's second term, which is
   also exact at every `N`; and the sparse end is closed by EFPS Theorem 1's **first** term
   out to `m ≈ 0.086 N²`, beating the report's `0.08 N²` from `bip ≤ m/2`.
3. The campaign's own `problems/23/writeup/BREAKTHROUGH_VERDICT.md` already records both
   facts ("Erdős–Győri–Simonovits (1992): dense tail e ≥ N²/5"; "exact N²/25 proved ONLY
   for edge-density ≤0.2486 or ≥0.3197").

The mathematics itself is right — I verified the chain exactly and exhaustively:

* algebra: roots of `x − 4x² = 1/25` are exactly `1/20, 1/5`; max `1/16` at `x = 1/8`
  (sympy exact, `audit_G12_misc.py`);
* `bip ≤ M1 = min_v e(G−N(v))` and `bip ≤ M4 = m − (1/N)Σd²`: **0 violations over all
  20 671 518 connected triangle-free graphs on 5..13 vertices** (`audit_G12_scan.cpp`;
  the report checked 11 563 graphs on 5..10);
* `bip ≤ M2` likewise 0 violations on the same set;
* 0 counterexamples to `25·bip ≤ N²` on the same 20.7M graphs.

Clause (C) `Δ ≥ 3N/5 ⇒ bip ≤ N²/25` is correct (Mantel inside `G − N(v)`) and is not
subsumed by (A)/(B), but it is a two-line corollary of the same 1988 lemma, and the report
misses that its own R2 material (`Δ ≤ α` for triangle-free G) upgrades it for free to the
strictly stronger **`α(G) ≥ 3N/5 ⇒ bip ≤ N²/25`**.

---

## 3. Independent reproduction of the falsifiers (all exact)

`audit_G12_named.py`, own max-cut over all `2^(N−1)` cuts, own LP + certificate pair:

| graph | N | \|E\| | girth | bip | nu* proof | nu* | verdict |
|---|---|---|---|---|---|---|---|
| `K?ABBBwerwBw` | 12 | 25 | 4 | 5 | 5-cycle packing 5 = uniform-cover 5 | 5 | matches |
| `K?BD@g]Qvo^?` | 12 | 25 | 4 | 5 | idem | 5 | matches |
| `L??ED@_~?~^_Fw` | 13 | 30 | 4 | 6 | idem | 6 | matches |
| `M?AE@bH{AYN_LgBs?` | 14 | 32 | 4 | **7** | 5-cycle packing `32/5`, all 32 loads exactly 1; uniform `x≡1/5` cover feasible on all 10 204 odd cycles | **32/5** | matches |
| OK5 (rebuilt) | 13 | 18 | **4** | 4 | full LP over all 22 odd cycles, dual verified | 10/3 | matches except girth |
| S3(K5) (rebuilt) | 25 | 30 | 9 | 4 | full LP | 10/3 | matches |
| Petersen | 10 | 15 | 5 | 3 | 5-cycle packing 3 | 3 | matches |
| Clebsch | 16 | 40 | 4 | 8 | — | — | matches accepted fact 8 |

`nu*(N=14) = 32/5` is proved by an exact primal/dual pair: uniform `x ≡ 1/5` is feasible
because `G` is triangle-free (checked: every one of the 10 204 odd cycles has ≥ 5 edges),
giving `tau* ≤ 32/5`; and an exactly-verified 5-cycle packing of value `32/5` gives
`nu* ≥ 32/5`. Two routes, both mine. (The report's own artifact for this,
`G12_f_out.txt`, stops before printing any nu* line, and `G12_a_out.txt` is missing its
N = 14 full-enumeration line, so the report's "doubly certified"/"full list printed"
claims are not backed by the files on disk. My optimal packing has 28 positive 5-cycles
with weights in `{1/10,1/5,3/10,2/5,1/2}`, not the report's "23 … in `{1/10,1/5,3/10,2/5}`";
the support of an optimal LP vertex is solver-dependent, so that particular sentence is
not a reproducible claim. The invariants — value `32/5`, all loads exactly 1 — are.)

**girth(OK5) = 4, not 5**: the retained edges are the `K_{2,3}` on `{0,1}×{2,3,4}`, and
`0–2–1–3–0` is a 4-cycle. Nothing else in the report depends on it (the uniform-`1/5`
cover needs only odd girth ≥ 5), but the stated fact is false. Also, OK5 is *not*
"maximally relevant": `δ(OK5) = 2 ≤ (4·13−2)/25 = 2.0` so accepted fact 7 excludes it, its
`m = 18 ≤ 0.1243·169 = 21.0` puts it inside the range already closed by BCL, and
`bip/N² = 4/169 = 0.0237 ≪ 1/25`.

---

## 4. What I found that the report got wrong or left open

### 4a. Minimum integrality-gap witness is **N = 12**, not "12, 13 or 14"

The report: *"The minimum witness size is therefore 12, 13 or 14 … (The N = 12 sweep over
1 144 061 graphs was launched and is the only unresolved arithmetic in this report.)"*
(Also loose: they exhibit a witness at 13, so 14 was already impossible.)

I ran the sweep (`audit_G12_scan.cpp`, 1 144 061 connected triangle-free graphs, 8.9 s).
Exact witnesses exist at N = 12. Certified twice (`audit_G12_n12gap.py`):

```
K??E@_qi?]Ia   N=12  |E|=18  tri-free  girth 4  degs 2^4 3^4 4^4
    bip = 4          (exhaustive over all 2^11 cuts)
    5*bip = 20 > 18 = |E|   =>  bip > |E|/5 >= tau* = nu*      [certificate 1]
    exact LP over all 40 odd cycles:  nu* = tau* = 10/3        [certificate 2]
    gap 6/5, deficit 2/3
K?AAD?WNBHCs   N=12  |E|=18  bip = 4, nu* = 10/3, gap 6/5, deficit 2/3
K??EDbGIaYAe   N=12  |E|=19  bip = 4, nu* = 11/3, gap 12/11, deficit 1/3
```
(exactly 10 of the 1 144 061 graphs pass the cheap exact test `5·bip > |E|` at N = 12, and
155 of the 19 425 052 graphs pass it at N = 13; the total number of N = 12 gap witnesses may
be larger, since that test is sufficient but not necessary.)

Note that the whole class of witnesses is exhibited for free by the campaign's **accepted
fact 8** plus the report's own P2: `nu* ≤ |E|/5` and `bip(Hoffman–Singleton) = 50 > 175/5 = 35`,
`bip(Gewirtz) = 84 > 56`, `bip(Higman–Sims) = 350 > 220`. So R1 ("`bip = nu*` is FALSE")
was a one-line consequence of facts already accepted by the campaign, with far larger gaps
(`50/35 = 10/7` vs the report's headline `35/32`). The report's contribution here is the
*small* witnesses, and the smallest is N = 12, which the report did not have.

### 4a′. The N = 14 "headline" is superseded at N = 13, and the P1 characterisation is false

The report checked the *one* N = 13 graph it was handed. My exhaustive sweep of all
19 425 052 connected triangle-free graphs on 13 vertices returns **exactly 8** graphs with
`bip = 6 = a(13)`. Exact results (`audit_G12_n13extremal.py`; for the four gap cases the
certificate is the one-line exact argument `5·bip > |E| ⇒ bip > |E|/5 ≥ tau* = nu*`, valid
because triangle-freeness makes `x ≡ 1/5` a feasible cover; for the four tight cases the
certificate is an exactly verified 5-cycle packing of value `6 = bip`):

| graph6 (N = 13, bip = 6) | \|E\| | degrees | nu* | deficit | gap |
|---|---|---|---|---|---|
| `L?`DAboUdIF_Bo` | 26 | 4-regular | ≤ 26/5 | ≥ 4/5 | ≥ 15/13 = 1.1538 |
| `L?`DE`gl@YJODg` | 26 | 4-regular | ≤ 26/5 | ≥ 4/5 | ≥ 15/13 = 1.1538 |
| `L?`DAboUdIF_Bw` | 27 | 4^11 5^2 | ≤ 27/5 | ≥ 3/5 | ≥ 10/9 = 1.1111 |
| `L?`DAboU`w@{hS` | 28 | 4^9 5^4 | ≤ 28/5 | ≥ 2/5 | ≥ 15/14 = 1.0714 |
| `L??ED@_~?~^_Fw` (the report's) | 30 | 4^9 6^4 | = 6 | 0 | 1 |
| `L??EDB_~?~^_Fw` | 31 | — | = 6 | 0 | 1 |
| `L??EFB_~FwB{Fw` | 32 | — | = 6 | 0 | 1 |
| `L??FFB_~?~^_Fw` | 33 | — | = 6 | 0 | 1 |

So:

* the bolded P1 claim *"The extremal objects up to N = 13 are exactly the graphs on which
  the trivial uniform cover `x ≡ 1/5` is LP-optimal and integral"* is **false**: half of
  the N = 13 extremal objects have `bip > nu*`;
* the P1 sentence *"Same phenomenon on the extremal graphs at N = 12 (both of them) and
  N = 13: there `bip = nu* = |E|/5` exactly"* is **false** at N = 13 — and even among the
  four tight ones, `nu* = |E|/5` fails for `|E| = 31, 32, 33` (there `nu* = 6 < |E|/5`,
  i.e. `bip = nu*` holds while the uniform cover is *not* optimal);
* the "THE HEADLINE" framing of the N = 14 graph as the extremal object on which the
  packing LP first falls short is **wrong by one vertex and by a factor**: two 4-regular
  13-vertex extremal graphs give deficit ≥ 4/5 and gap ≥ 15/13 = 1.1538, against the
  report's 3/5 and 35/32 = 1.0938.

(The two N = 12 extremal graphs *are* exactly the report's two strings — my sweep of all
1 144 061 connected triangle-free graphs on 12 vertices finds exactly two with `bip = 5`,
`K?ABBBwerwBw` and `K?BD@g]Qvo^?`, both with `bip = nu* = |E|/5 = 5`. That half of P1 stands.)

### 4b. "no gap witness on N ≤ 11" — true, but the report's proof is floating point

`G12_e_scan.py` computes `nu` with `scipy.optimize.linprog(method="highs")` (float) and
accepts on `if b - nu > 1e-6`. Its docstring says "candidates re-checked exactly"; **there
is no exact recheck in the code**, and `res.status` is never inspected. That is float on an
acceptance path for a negative claim.

I re-established the claim exactly, in two stages (`audit_G12_pack.cpp` + `audit_G12_residue.py`):
* for each of the 102 405 connected triangle-free graphs on 5..11 vertices
  (6+19+59+267+1380+9832+90842), search exhaustively for `bip` pairwise **edge-disjoint**
  odd cycles; success is an integer certificate `nu_int = bip`, hence `bip = nu*` (since
  `nu_int ≤ nu* ≤ bip`). Bipartite graphs are trivial (`bip = nu* = 0`); all the rest pass
  except 1 459;
* the 1 459 residue graphs were each settled by an exactly-verified rational packing of
  value `bip` (float used only to propose a support; the value recomputed by exact simplex).
  **0 gap witnesses.**

So: minimum witness size **= 12 exactly**.

### 4c. The M1 ceiling is attained: `sup_G M1(G)/N² = 1/16`, and the scan table has a wrong entry

The report: *"worst ratio found 5/81 = 0.061728 (N = 9 …), i.e. within 1.2 % of the proved
ceiling 1/16"*, and its scan table gives `N = 8: max M1 = 3`.

Exact truth: **`C8` (N = 8, 2-regular, m = 8) has `M1 = 8 − 2·2 = 4 = N²/16` exactly.**
More generally every `d`-regular triangle-free graph on `N = 4d` vertices has
`M1 = 2d² − d² = d² = N²/16`, so the ceiling `1/16` proved in P3(4) is *attained*, infinitely
often, and `5/81` is not the worst ratio. My exhaustive maxima (all connected triangle-free
graphs, exact):

| N | max M1 (mine) | report | max M2 (mine) | report |
|---|---|---|---|---|
| 8 | **4** (`G?qa`_` = C8, bipartite) | 3 ✗ | 3 | 3 ✓ |
| 9 | 5 | 5 ✓ | 3 | 3 ✓ |
| 10 | 6 | 6 ✓ | 4 | 4 ✓ |
| 11 | 7 | 7 ✓ | 6 | 6 ✓ |
| 12 | 9 = `N²/16` (3-regular, bipartite) | — | 8 | — |
| 13 | 10 | — | 10 | — |

Cause: `G12_e_scan.py` does `if b == 0: continue`, i.e. it silently **excludes every
bipartite graph** from the maxima. `M2 = 0` on bipartite graphs so M2 is unaffected, but
`M1` is, and bipartite graphs are legitimate witnesses against the mechanism (the mechanism
must return `≤ N²/25` on *every* triangle-free graph to prove anything).

### 4d. R3's refutation engine is dead unconditionally, not just on regular graphs

The report proves `π(G) ≤ nu* ≤ bip`, notes `π > N²/25` would refute #23, and blocks the
test only for **regular** graphs (via Andrásfai–Erdős–Sós). But its own P4(A) kills it
everywhere: if `m < N²/5` then `π ≤ m/5 < N²/25`; if `m ≥ N²/5` then `bip ≤ N²/25` by
P4(A)/EFPS, so `π ≤ bip ≤ N²/25`. **`π(G) > N²/25` is impossible for every triangle-free
graph**, so the proposed poly-time refutation scan is provably wasted compute. This should
be recorded as DEAD, not "blocked at 1/25 by AES".

### 4e. Minor

* R2's parenthesis "`M1, M2, M3, M4 are all ≤ M2`" is false as written (it self-corrects to
  `M2 ≤ M1 ≤ M4`); and M3 (BFS-layer cut) is not in the independent-set family at all —
  BFS layers are not independent sets (Petersen's layer 2 has 6 vertices and 6 internal edges).
* The stated interval `sup M2/N² ∈ [15/256, 1/16]` is superseded three lines later by the
  report's own Higman–Sims value `616/10⁴ = 0.0616`; the correct statement of the lower end
  is `0.0616`, so the bolded sentence "no cut with one side independent can prove a constant
  better than 0.0586" is weaker than what the report itself established.
* P5's planar corollary is vacuous: planar triangle-free ⇒ `|E| ≤ 2N−4` ⇒ `bip ≤ (2N−4)/5`,
  linear, and the report says so itself in P6 — yet still lists the Guenin consequence as a
  result in the PROVED section.
* the P1 characterisation of the extremal objects: see §4a′ — refuted at N = 13.

---

## 5. Failure-mode checklist (required by the audit protocol)

| failure mode | finding |
|---|---|
| float on an acceptance path | **YES** — `G12_e_scan.py` (`nu_float` + `b - nu > 1e-6`, no exact recheck despite the docstring). Everything else (`G12_core.py`, `G12_a/b/c/d/f`) is `Fraction`/int and sound. |
| max cut confused with a greedy/local cut | NO — `bip_bruteforce_fast` enumerates all `2^(n−1)` bipartitions; I reproduced every `bip` value independently. |
| ψ < 1/25 reported as a maximum on odd girth 5 | N/A — this report never computes ψ. (It does report `nu*/N² < 1/25` values, which is legitimate: `nu*` is not ψ and is not required to be ≥ 1/25.) |
| integer-weight enumeration excluding zero weights | N/A; the C5-blow-up scan in `G12_d_theorem.py` uses `range(0, N+1)` and does include zero parts. |
| triangle-freeness assumed but not used / used where false | Used correctly and essentially in three places (N(v) independent; odd cycles ≥ 5 edges; Mantel). Verified `is_triangle_free` on every named graph. |
| N odd / not divisible by 5 / disconnected / isolated vertices / unbalanced blow-ups | Handled. Connectivity reduction is valid (`bip`, `nu*` both additive over components). Unbalanced C5 blow-ups are covered in `G12_d_theorem.py`. |
| constant weakened to 1/25 + ε or "N large" | NO. All constants are exactly `1/25`, `1/16`, `1/20`, `2/25` as rationals. |
| circularity (assumes something of strength ≥ the conjecture) | NO. |
| finite verification presented as a general argument | NO for P3/P4 (the proof is general; the 11 563-graph run is only validation). **YES** for the "extremal objects up to N = 13 are exactly …" sentence: it is a 3-graph observation phrased as a characterisation, and it is false — see §4a′. |
| quoted theorem whose hypotheses do not match the use | Guenin: correctly used (weak bipartiteness = integrality of the odd-cycle covering polyhedron ⇒ `tau = tau*`, and `tau* = nu*` by LP duality; K5-minor-free ⇒ no odd-K5 minor since the underlying graph of a signed minor is a minor). Andrásfai–Erdős–Sós: correctly used (`δ > 2n/5 ⇒ bipartite`, applied to regular graphs where `δ = d`). Mantel, Cauchy–Schwarz: correct. **The missing citation is the fatal one**: EFPS 1988 Theorem 1 / Lemma 2.1, which the report re-derives and calls new. |

---

## 6. Files

* `E:\Projects\ErdosProblems\problems\23\round3\audit_G12.md` (this file)
* `...\audit_G12_core.py` — independent graph6, exhaustive max-cut, girth, cycle
  enumeration, exact Fraction simplex, exact primal/dual certificate checker
* `...\audit_G12_named.py` + `audit_G12_named_out.txt` — the four extremal strings, OK5,
  S3(K5), C5[n] closed form, Petersen, Clebsch
* `...\audit_G12_n12gap.py` + `audit_G12_n12gap_out.txt` — the N = 12 gap witnesses, doubly
  certified; the exact M1 ceiling
* `...\audit_G12_misc.py` + `audit_G12_misc_out.txt` — band algebra, M1..M5 on 11 named
  graphs, P6 statements 1 and 2, Clebsch/Higman–Sims arithmetic
* `...\audit_G12_scan.cpp` / `.exe` — exhaustive exact sweep (bip, M1, M2, M4, gap test,
  counterexample test) over `geng -tc n`, n = 5..13 (20 671 518 graphs)
* `...\audit_G12_pack.cpp` / `.exe` + `audit_G12_residue.txt` — integral edge-disjoint
  odd-cycle certificates, residue extraction
* `...\audit_G12_residue.py` — exact settlement of the 1 459 residue graphs
* `...\audit_G12_n13extremal.py` + `audit_G12_n13extremal_out.txt` — all 8 extremal graphs
  at N = 13, each decided exactly (4 gaps, 4 tight)
* `...\audit_G12_scan_n13.txt`, `audit_G12_extremal_n13.txt`, `audit_G12_m1max.py`

## 7. Reusable exact facts produced by this audit

* `a(12) = 5`, attained by exactly 2 connected triangle-free graphs; `a(13) = 6`, attained
  by exactly 8; `a(N)` for N = 5..13 = 1,1,1,2,2,4,4,5,6 (independent exhaustive recount,
  20 671 518 graphs).
* Smallest triangle-free graph with `bip > nu*`: N = 12, `K??E@_qi?]Ia`, `bip = 4`,
  `nu* = 10/3`.
* Sharpest small extremal gap witness: N = 13, `L?`DAboUdIF_Bo` (4-regular, 26 edges),
  `bip = 6`, `nu* ≤ 26/5`.
* `sup_G M1(G)/N² = 1/16`, attained by every `d`-regular triangle-free graph on `N = 4d`
  vertices (smallest: `C8`).
* `π(G) > N²/25` (5-cycle packing LP) is impossible for every triangle-free `G`.
