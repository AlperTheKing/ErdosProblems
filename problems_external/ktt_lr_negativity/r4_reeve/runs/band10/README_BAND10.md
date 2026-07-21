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
