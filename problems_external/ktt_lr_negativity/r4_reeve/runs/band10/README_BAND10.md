# BAND 10 — r = 4 (Reeve dimension), targeted hunt for c = 4 (h*_1 = 0) with V >= 2

Assignment: unbounded weight; search directly for r = 4 hive polytopes with
`c = L(1) = 4` (equivalently `h*_1 = 0` in dimension 3) and normalized volume
`V >= 2`, push `V` as high as possible, and report the record `(c, V)` pair.
This is exactly the Reeve mechanism: `T_q` is an empty lattice 3-simplex with
`c = 4`, `h* = (1,0,q-1,0)`, `V = q`, and `a_1 = 2 - q/6 < 0` iff `q >= 13`.

## Moduli framing (why "unbounded weight" is covered)

`Q(lam,mu,nu) = {h in R^3 : A h <= b}` with a FIXED 18x3 matrix `A` (15 distinct
primitive directions); only `b` moves, linearly in the 9 gaps
`a = (l1-l2,l2-l3,l3-l4)`, `b = (m1-m2,...)`, `c = (n1-n2,...)`.
Two triples with the same gap vector differ by `(lam,mu,nu) -> (lam+s, mu+t, nu+s+t)`
(componentwise on all four parts), which TRANSLATES `Q`. Verified on 386 random
pairs (`dim, c, L(0..5), h*, V, P` all identical) — see the session log.

Consequently the gap vector determines the entire Ehrhart data, and one gap
class contains triples of arbitrarily large weight. A census over gaps in
`[0,G]^9` is therefore a census over ALL WEIGHTS for every triple whose
consecutive part-gaps are `<= G`.

## Files

| file | what |
|---|---|
| `../../band10.cpp`, `band10.exe`/`band10b.exe` | exact integer structural scanner (`--exh G`, `--rand K N SEED`, `--one g1..g9`) |
| `subset_atlas.py` / `subset_atlas.json` | the weight-independent bound: which 4-subsets of the 15 normal directions can bound a simplex, and their vertex-cone multiplicities |
| `lattice_certificate.py` / `.json` | attempted proof that every vertex is integral — REPORTED AS FAILED (510 congruence violations; non-integral *candidate* Cramer solutions exist, they are simply never feasible in any scan) |
| `xvalidate_band10.py` | cross-validation of `band10.exe` against `hive4.py` (exact) |
| `verify_record.py` | record verification: `hive4.py` + engine A (`lr_hive.exe`) + engine B (`engineB_lrrule.py`) |
| `scan_G12_perc.log` | exhaustive Ehrhart census over gaps in `[0,12]^9` (`gapscan4.exe`), incl. max V at each fixed `c` |
| `b10_exh12.log`, `b10_exh6.log` | exhaustive structural census (denominators, multiplicities, simplex volumes) |
| `b10_rand_bigK.log`, `b10_rand_K1e9_deep.log` | unbounded-weight random census, gaps up to `10^9` |
| `unbounded_weight_c4.json` | one c=4 class exhibited at weights up to `4*10^12` |
| `verify_g12_minA1.json` | the global `a_1`-minimiser, verified by all three engines |
| `manifest.json` | machine-readable summary |

## Result

No negative coefficient. `min a_1 = 11/6`, attained exactly on the `c = 4, V = 1`
(unimodular-simplex) stratum. `max V at h*_1 = 0` is **1**, and this is not a
box artifact: it is forced, at every weight, by the finite normal-fan atlas
(subject to the vertex-integrality hypothesis, which is verified but not proved).

Absence of a counterexample here is NOT evidence for the King–Tollu–Toumazet
conjecture. What it is: an exhaustive negative census of the r = 4 cell, plus a
structural reason why the Reeve mechanism cannot fire there.

---

# WAVE 2 — second independent pass (hunter 10 of 12)

Wave 1 (above) was re-run from scratch, not taken on trust, and then extended.

## What was re-verified independently

| check | scale | result |
|---|---|---|
| `hive4.py --selftest` | Reeve `T_q` q=1..20, `c=1 => P==1`, `c=2 => P=n+1` | PASS |
| `gapscan4.exe --one` vs `hive4.py` (exact Fractions) | 250 random gap vectors, gaps ≤ 12 | 250/250 identical `L1,L2,L3,6a1,V` |
| same, in the **slab regime** (int64 overflow check) | 60 vectors, weights to 128046, `V` to 702 | 60/60 identical |
| `hive4.py` vs LR engine **A** and engine **B** | 120 stretched counts `c(n·nu; n·lam, n·mu)`, n=1,2,3 | all three engines agree |
| normal-fan atlas (the load-bearing lemma) | re-derived from scratch in `b10w2_atlas.py` | 36 positively-spanning simple 4-subsets; profiles `(1,1,1,1)`×18, `(1,1,2,2)`×6, `(1,1,1,4)`×12 — reproduces wave 1 exactly |

## New structural facts

**Homogeneity.** `b` is linear-homogeneous in the 9-gap vector `g`, so
`Q(t·g) = t·Q(g)` up to a lattice translation and therefore
`a_k(t·g) = t^k · a_k(g)`. Verified exactly on 224 `(g,t)` pairs, `t = 2,3`.
Consequence: **`{g : a_1(g) < 0}` is a cone**, so an exhaustive census of a box
or of a value ladder settles every *ray* through it — i.e. it covers unbounded
weight along each direction it meets, not just the small triples in the box.

**Only `a_1` can be negative.** `a_0 = 1`; `a_3 = V/6 > 0` in dim 3; `a_2` is
half the lattice-normalized surface area of a lattice 3-polytope, hence `> 0`.
So the entire r=4 cell reduces to the sign of
`6a_1 = 11 + 2h*_1 - h*_2 + 2h*_3 = 3(c + i) - V`, i.e. to
`h*_2 > 2h*_1 + 2h*_3 + 11`. Empirically confirmed: over 800 random dim-3
triples the *minima* are `a_1 = 11/6`, `a_2 = 1`, `a_3 = 1/6` — exactly the
values of the standard unimodular 3-simplex.

**Where the one open gap lives.** Of the 15 fixed rhombus directions, the 12
A3 ("alcoved / polytrope") ones are **unimodular in triples**: 0 of their
triples have `|det| > 1`. Every one of the 49 bad triples (48 with `|det|=2`,
one with `|det|=4`) contains at least one of the three **odd** rows
`R_A, R_B, R_C` (rhombi `A(1,1), B(1,1), C(1,1)`). So a non-integral vertex
requires an odd row to be tight. *Refuted en route*: the stronger claim
"`|det|>1` implies ≥ 2 odd rows" — 18 bad triples have exactly one.

## New censuses (all exact integer, all negative)

| census | gap vectors | min `6a1` | max `V` at `c=4` |
|---|---|---|---|
| exhaustive box `[0,14]^9` (`scan_G14.log`) | 38 443 359 375 | see log | see log |
| ladder `0,1,2,3,5,8,13,21,34` | 387 420 489 | 11 | 1 |
| ladder `0,1,2,4,8,16,32,64,128` | 387 420 489 | 11 | 1 |
| ladder `0,1,3,10,32,100,316` | 40 353 607 | 11 | 1 |
| slab `MAXUV=4`, ladder to `10^5` | 573 308 928 | 11 | 1 |
| slab `MAXUV=4`, ladder to `10^9` | 1 003 976 272 | 11 | 1 |
| slab `MAXUV=6`, ladder to `10^6` | 360 000 000 | 11 | 1 |
| structural random, gaps ≤ `10^9`, seed 777002 | 200 000 000 | — | no `c=4` with `V≥2` |
| `--climb` (scale-invariant descent) K=40, 128 restarts | — | 11 | 1 |
| `--rand` K=200, N=500 000 | — | 11 | 1 |

The **slab** mode is new: `g[1] = lam2-lam3` and `g[7] = nu2-nu3` are exactly
the widths of the `(u,v)` fibre grid, so holding them at `1..4` is both the
cheap regime *and* the only regime where a polytope can have few lattice points
while being long — the only place a Reeve-type `(c=4, V≫1)` could hide. Holding
them small lets the other **seven** gaps run to `10^9`.

One run is **reported but excluded**: `b10w2_rand_K1e11.log` (gaps to `10^11`).
Its non-emptiness rate (0.23%) contradicts the scale-invariance of
non-emptiness (65% at `K=10^9`), so it is outside the validated integer range of
`band10.exe` and is used for nothing.

## Records

* `c = 4` (`h*_1 = 0`) record: **`V = 1`**, e.g.
  `lam=(358,326,10,0)`, `mu=(120,110,10,0)`, `nu=(394,391,75,74)`,
  `L = (1,4,10,20,35,56)`, `P = 1 + (11/6)n + n² + (1/6)n³`, confirmed by
  `hive4.py`, engine A and engine B; exhibited at weights up to `4·10^12` by the
  translation family.
* max normalized volume verified exactly this pass:
  **`V = 103 813 825 188 771 821 384 673 875`** at weight `7 704 665 172`
  (4 vertices, all integral) — lattice-point count not enumerated at that size,
  and no float substitute was used.

## Verdict (wave 2)

No negative coefficient. `min a_1 = 11/6` everywhere: the r=4 hive polytopes
never beat the standard unimodular 3-simplex, and the distance to negativity,
`3(c+i) - V ≥ 11`, never shrinks. This is an exhaustive negative census plus a
structural obstruction to one mechanism in one cell. **It is not evidence for
the King–Tollu–Toumazet conjecture.**
