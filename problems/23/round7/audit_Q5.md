# audit_Q5.md — adversarial audit of round7/Q5.md

Auditor: independent re-implementation in `round7/audit_Q5_*.py|cpp` — own graph6
decoder, own exhaustive max-cut/`bip`, own simple-cycle enumerator, own exact
rational LP with two-sided certificates, own exact min-odd-cycle oracle
(double cover + Dijkstra over `Fraction`), and an odd-K5-minor decider written on a
**different algorithm** from the target's (switching-class first, not
branch-assignment first).  Every accepted number is a `Fraction` or an integer count;
floats only steer LP searches and are never accepted.

Cross-validation of the two independent minor deciders: they agree on all five cases
both computed (V8 NO, C5[2] NO, And(4) YES, And(5) YES, N14 YES).

---

## Verdicts, most consequential first

### 1. Thm C (triangle-free + no odd-K5 minor ⟹ ψ ≤ 1/25 for every x) — **CONFIRMED**

* Citation checked against the literature: a signed graph is *weakly bipartite* iff
  the clutter of its odd circuits is ideal; Seymour conjectured and **Guenin proved**
  (JCTB 83 (2001) 112–168) that this holds iff there is no odd-K5 minor.  The
  hypothesis matches the use: idealness gives `τ_w = τ*_w` for **all** `w ≥ 0`,
  product weights `w_uv = x_u x_v` (zeros allowed) included.
* `Λ ≤ ψ` is exact (`τ*_w ≤ τ_w = min_S w(mono S)`); Thm A bounds `Λ`.
* No circularity: nothing in the chain has strength ≥ the conjecture.
* **Gap in the statement, not in the proof.** "`= 1/25` **exactly when** `G` has an
  induced `C5`" is an iff; Q5.md proves only ⟸ (the plateau).  ⟹ is missing.  It is
  true and one line, supplied here: odd girth ≥ 7 ⟹ `z ≡ 1/7` feasible ⟹
  `Λ ≤ e/7 ≤ (1/4)/7 = 1/28 < 1/25` (using `e ≤ 1/4` on triangle-free graphs,
  Motzkin–Straus with ω = 2).

### 2. `max_x ψ(And(3)=V8) = 1/25` exactly; Wagner support induces V8 — **CONFIRMED** (scope caveat)

* Γ_14 restricted to `{0,1,2,5,6,7,10,11}` is cubic on 8 vertices, 12 edges, and my
  own brute-force isomorphism search returns the same map `(0,3,6,1,4,7,2,5)` onto
  `C8(1,4)`; `And(3) = Γ_8 ≅ C8(1,4)` likewise.  (`audit_Q5_cert.py`)
* V8 has **no K5 minor** — my own decider, exhaustive over all 88 connected subsets;
  the cubic counting argument in Q5.md is valid.  It has **no odd-K5 minor**
  (exhaustive over all 2^7 switchings).
* `ψ(V8,uniform) = Λ(V8,uniform) = 1/32`, matching the recorded W8 value.
* Independent grid sweep, own enumerator, pure integers, zero weights allowed:
  D = 10/12/15/20 → max ψ = **1/25, 1/36, 1/25, 1/25** with vector counts
  19448 / 50388 / 170544 / 888030 — identical to Q5.md.  Extended to
  D = 25,30,35,40,45,50,60: **1 371 049 759 further weight vectors, 0 violations.**
* **Not trivial**: V8 has **no homomorphism to C5** (exhaustive over all 5^8 maps),
  so the cheap pushforward argument `ψ(G,x) ≤ ψ(C5,φ_*x) ≤ 1/25` does *not* give it.
  The Guenin/Barahona input is doing real work.
* **Scope caveat.** By locality (`ψ(H,x) = ψ(H[supp x], x)`), this caps *every*
  weighting supported on the Wagner support — that is the recorded configuration's
  whole family.  It does **not** close `And(5) = Γ_14` itself; Q5.md says so in §4.3,
  but the headline "the recorded tightest open case is CLOSED" reads stronger than
  what is proved.

### 3. Thm A (`Λ(H,x) ≤ 1/25`) — **CONFIRMED, but not new**

Algebra verified symbolically: `4e²−e+1/25 = 4(e−1/20)(e−1/5)`, crossing at `e = 1/5`
where both branches equal `1/25`.  Step 2 (`ψ ≤ e−4e²`, cut `S = N(v)`, average with
weights `x_v`, Cauchy–Schwarz) is exactly **accepted base 5 in weighted form**; step 1
(`z ≡ 1/5`) is one line.  So Thm A is a correct repackaging of the accepted base, not
new mathematics.  **Exactly tight on `C5[n]`** as the protocol requires:
`e/5 = e−4e² = Λ = ψ = 1/25` exactly for n = 1,2,3.  Verified on all 10 round5
witnesses and on 12 further graphs; no violation.

### 4. Thm B (quantitative obstruction) — **CONFIRMED algebra, one stated consequence OVERSTATED**

`e−4e² = 1/25 + (3/5)s − 4s²` with `s = 1/5−e`; `(3/5)s−4s² ≥ η, s>0 ⟹ s ≥ 5η/3 ⟹
Λ ≤ 1/25 − η/3 ⟹ ψ−Λ ≥ 4η/3`.  All steps check.
**But** the bullet "no such dual can prove the conjecture either — the LP value
carries zero information about whether `ψ ≤ 1/25`" is contradicted by Q5.md's own
Thm C, which proves the conjecture on a class *by* LP duality (idealness).  The §6
blocking lemma states this correctly ("only through `ψ = Λ`"); the §3.5 bullet and
headline 2 ("the mechanism is dead in both directions") do not.

### 5. N=14 extremal `M?AE@bH{AYN_LgBs?` — **CONFIRMED exactly**

`bip = 7` (own exhaustive 2^13 cuts); odd-cycle spectrum `{5:92, 7:556, 9:1768,
11:4012, 13:3776}`; the 92 tight 5-cycles have **exact rank 32 = |E|** and every
`z_e = 1/5 > 0`, so `z ≡ 1/5` is a genuine vertex of `Q(G)`; `τ* = 32/5` with my own
two-sided certificate (cover `z ≡ 1/5`, packing of 27 odd cycles at denominator 10);
gap `3/5`.  The explicit odd-K5 certificate verifies **after** flipping one whole
branch set relative to the printed p-mask 628 — legitimate (flipping a branch set is
itself a switching, and the target's C++ correctly tests triangle parities, not
edge-by-edge negativity).  My decider independently finds an odd-K5 minor.

### 6. All minor decisions — **CONFIRMED** (two independent algorithms)

| graph | K5 minor | odd-K5 minor | agrees with Q5.md |
|---|---|---|---|
| V8 = And(3) | NO | NO | yes |
| C5[2] | YES | NO | yes |
| And(4) = Γ_11 | — | YES | yes |
| And(5) = Γ_14 | — | YES | yes |
| N=14 extremal | — | YES | yes |

### 7. Exact-value tables, 3-subdivision, Prop 6 — **CONFIRMED exactly**

Every `(e, Λ, ψ)` triple of §3.5 and every row of the §1 table reproduced:
see "EXACT VALUES" below.  `τ*(K5) = 10/3`, `bip(K5) = 4`; 3-subdivided K5 has
N = 25, |E| = 30, girth 9, triangle-free, `τ* = 10/3`; `bip = 4` follows exactly from
`τ* = 10/3` (integrality) plus a 4-edge transversal.  Subdivision invariance of `bip`
and `τ*` checked on C5, K4, K5.  Prop 6: every edge of `C5[n]` lies in exactly `n³`
transversal 5-cycles (n ≤ 4 checked), load exactly 1, value `n²`.

---

## UNSUPPORTED (true, but not established by what Q5.md reports)

* **"every `And(k)` with `k ≥ 4` has an odd-K5 minor."**  Q5.md verifies the induced
  embedding only for `k = 5,6,7,8` and then quantifies over all `k ≥ 4`.  I verified
  `k ≤ 60` and supply the general proof (`audit_Q5_theory.py`): place the arcs
  `{0..3}, {k..k+3}, {2k..2k+2}` and map the j-th element in cyclic order to `j`;
  writing `u = ak+p, v = bk+q` with `b−a ∈ {0,1,2}`, `|q−p| ≤ 3`, adjacency in
  `Γ_{3k−1}` and in `Γ_11` reduce to the *same* condition in each case
  (`b−a=0`: never; `b−a=1`: `q ≥ p`; `b−a=2`: `q < p`).  Statement true, evidence as
  printed insufficient.
* **Thm C's "exactly when"** — see verdict 1.
* Table row `C5[6]`: `bip` is printed `—` while the gap column asserts `0`.  Justified
  only through accepted base 1 (`bip(C5[n]) = n²`), which is not said there.

## DEFLATED (correct, but adds nothing)

* **Headline 5 / §4.2, "the extremal family is inside the class"** — `ψ(C5[2],x) ≤
  1/25 for every x` is **immediate** from accepted base 4: twin-collapsing gives
  `ψ(C5[2],x) = ψ(C5, y)` with `y_p = x_{2p}+x_{2p+1}`, and `ψ(C5,y) = min_i y_i y_{i+1}
  ≤ 1/25` by AM–GM.  Verified on 200 random exact weightings (`audit_Q5_deflate.py`).
  No minor theory is needed for `C5[n]`, and the undecided `C5[3]` search (6^15) is
  pointless for the same reason.
* **Thm A** is accepted base 5 in weighted form (verdict 3).

## UNDER-CLAIMED — Thm C closes three more objects than Q5.md says

My decider (exhaustive, complete switching enumeration) finds **no odd-K5 minor** in:

| graph | N | odd-K5 | induced C5 | consequence via Q5.md's own Thm C |
|---|---|---|---|---|
| Grötzsch | 11 | **NO** | `{0,2,3,6,9}` | `max_x ψ = 1/25` **exactly** |
| N=12 extremal `K?BD@g]Qvo^?` | 12 | **NO** | `{0,4,6,9,11}` | `max_x ψ = 1/25` **exactly** |
| N=13 extremal `L??ED@_~?~^_Fw` | 13 | **NO** | `{0,5,7,11,12}` | `max_x ψ = 1/25` **exactly** |
| Petersen | 10 | YES (`{0,1}{2,7}{3,4}{5,8}{6,9}`, P={1,2,3,6,8}) | — | not covered |
| N=12 extremal `K?ABBBwerwBw` | 12 | YES | — | not covered |

Each of the three has odd girth 5 and `ψ = 1/25` at the induced-C5 concentration
(exact).  Empirical control: 64 512 240 weight vectors on Grötzsch at D = 22, zero
violations; same count on And(4) (which is *not* covered) and 67 863 915 on And(5),
also zero violations.

## Process checks (protocol item 3)

* **Float on an acceptance path: NONE FOUND.**  `Q5_lib.py` is pure `Fraction`;
  floats in `Q5_*.py` appear only inside f-string display next to the exact value, or
  as `random.random()` choosing which weight to test.  `Q5_v8sweep.py` is pure integer
  and its only early exit is at `bm == 0`, which is sound (a true minimum).
* **Zero weights in integer enumerations: ALLOWED.**  Counts equal `C(D+7,7)` exactly
  (19448, 50388, 170544, 888030) — the enumerations do include zeros, as accepted
  base 2 demands.
* **A ψ below 1/25 reported as a maximum for an odd-girth-5 graph: NOT FOUND.**
  `ψ(V8,uniform) = 1/32` is explicitly labelled a *local* optimum, and the D=12 row
  (`1/36`) is explained by `12 ∤ 5`.
* **Claimed exhaustive ranges: COVERED.**  The target's decider loops over the full
  `6^N` assignment space with a canonical-order filter; "1432 configurations" is the
  post-filter count, not the loop bound.
* **Quoted theorem vs use: MATCHES** (Guenin, verdict 1).
* **Circularity: NONE.**
* Minor imprecision: §5's "flow-tractable **iff** no K5 minor" — Guenin's own theorem
  gives polynomial max-cut on the strictly larger no-odd-K5 class, so the "iff" is
  wrong as stated (harmless to every claim that depends on it).
* `Q5_checks.py C2` ("Theorem A stress test over geng") samples **3 graphs × 4
  weightings**; the report body does not lean on it, but the file-list description
  oversells it.

## EXACT VALUES reproduced independently (all rationals)

`bip`: C5[n] n=1..4 → 1,4,9,16 (exhaustive); N12a 5; N12b 5; N13 6; **N14 7**;
Petersen 3; Grötzsch 4; And(3) 2; And(4) 4; And(5) 6; And(6) 9; K5 4.
`τ*` (unit weights, two-sided exact): C5 1; C5[2] 4; C5[3] 9; N12a 5; N12b 5; N13 6;
**N14 32/5 (gap 3/5)**; Petersen 3; Grötzsch 4; And(3) 2; And(4) 4; And(5) 6;
And(6) 9; K5 10/3; 3-subdivided K5 10/3.
Uniform `x`, `(e, Λ, ψ)`: C5/C5[2]/C5[3] `(1/5, 1/25, 1/25)`; N12a/N12b
`(25/144, 5/144, 5/144)`; N13 `(30/169, 6/169, 6/169)`; N14 `(8/49, 8/245, 1/28)`;
Petersen `(3/20, 3/100, 3/100)`; Grötzsch `(20/121, 4/121, 4/121)`;
And(3) `(3/16, 1/32, 1/32)`; And(4) `(2/11, 4/121, 4/121)`; And(5) `(5/28, 3/98, 3/98)`;
And(6) `(3/17, 9/289, 9/289)`.  Grid maxima on V8: D=10 `1/25`, D=12 `1/36`,
D=15 `1/25`, D=20 `1/25`.

## Files (auditor)

```
audit_Q5.md          this report
audit_Q5_lib.py      independent library (graph6, bip, cycles, exact tau*)
audit_Q5_smoke.py    smoke tests of the library (all pass)
audit_Q5_vals.py     /.out   exact table of sec 3.5 + tau* + 3-subdivision
audit_Q5_lam.py      /.out   Lambda for C5[3], And(5), And(6) by exact certificates
audit_Q5_n14.py              every N=14 claim (bip, 92 tight 5-cycles, rank 32, tau*)
audit_Q5_cert.py     /.out   every explicit minor certificate of Q5.md
audit_Q5_theory.py   /.out   Thm A/B algebra, round5 witness regression, And(4) scope
audit_Q5_deflate.py          hom(V8,C5) = empty; twin-collapse deflation of C5[2]
audit_Q5_minor.cpp/.exe      independent odd-K5 decider (switching-first)
audit_Q5_v8.cpp/.exe /_sweep.out   independent integer sweep (violation search)
```
