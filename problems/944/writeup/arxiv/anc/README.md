# Ancillary files for "Exact 6-cut rigidity and small-order superconnectivity for the 6-regular case of Dirac's k=4 problem"

All graph generation uses nauty 2.8.9 `geng` (B. D. McKay), built with
`-DMAXN=WORDSIZE -DWORDSIZE=32`. All graph6 strings follow the standard nauty
format. Colourings are proper maps to {1,2,3}, never counted modulo colour
permutation.

## Theorem A (no 6-regular 4-vertex-critical graph on n <= 15 except a unique one on n = 13)

A 6-regular graph requires n >= 7. Generator + classifier:

    geng -d6 -D6 <n> | check_g6 <n>          # counts: total / 3col / notVC / 4VCcrit / target
    geng -d6 -D6 <n> | check_g6_v2 <n>       # same, with the neighbourhood-bipartite prefilter

Exact per-n commands and resulting counts (total / 3-colourable / not-vertex-critical
/ 4-VC-with-critical-edge / target):

    n=7   geng -d6 -D6 7  | check_g6 7        -> 1 / 0 / 1 / 0 / 0   (K_7 only)
    n=8   geng -d6 -D6 8  | check_g6 8        -> 1 / 0 / 1 / 0 / 0
    n=9   geng -d6 -D6 9  | check_g6 9        -> 4 / 1 / 3 / 0 / 0
    n=10  geng -d6 -D6 10 | check_g6 10       -> 21 / 1 / 20 / 0 / 0
    n=11  geng -d6 -D6 11 | check_g6 11       -> 266 / 3 / 263 / 0 / 0
    n=12  geng -d6 -D6 12 | check_g6 12       -> 7849 / 50 / 7799 / 0 / 0
    n=13  geng -d6 -D6 13 | check_g6 13       -> 367860 / 849 / 367010 / 1 / 0
    n=14  geng -d6 -D6 14 | check_g6 14       -> 21609301 / 42667 / 21566634 / 0 / 0
    n=15  geng -d6 -D6 15 r/2750 | check_g6_v2 15   (per residue class 0..2749; sum below)

- `check_g6.cpp`, `check_g6_v2.cpp` — C++ classifiers (clang++ -O3). v2 adds the
  prefilter of Lemma 2.5 (neighbourhood bipartiteness, valid since the graphs are
  6-regular so Delta <= 6); both validated to produce identical classifications on
  n = 11, 12, 13. Totals match the known counts of 6-regular graphs (OEIS A165628).
- n = 14 was also run twice with different residue chunkings (`geng ... r/110` and
  `r/73`); aggregates agree.
- n = 15 was run with check_g6_v2 in residue classes (geng `r/2750`); every class
  validated by matching the geng `>Z` terminating count against the classifier
  count; aggregate: 1,470,293,676 graphs (= known count), 0 4-vertex-critical, 0 target.
- `unique_6reg_4vc_n13.txt` — the unique 6-regular 4-vertex-critical graph on 13
  vertices (edge list; graph6: `L?bFFbw~B{FwFw`).
- `verify_lemma21_n13.py` — audit of the singleton-lemma mechanism on that graph:
  78 vertex-deleted colourings, none with a 2+2+2 split; 156 singleton
  predictions; 13/13 critical edges covered, 0 false positives.
- `test_lemma21_random.py` — stress test of the vertex-form Kempe tether
  (19,389 implications on random 4-chromatic graphs, 0 failures).

## Theorem B (shore exclusion, sizes 9..14)

Candidate shores of size a (connected, 3a-3 edges, max degree 6):

    geng -c -D6 <a> <3a-3>:<3a-3> | enum_shore <a>          # filter battery
    geng -c -D6 <a> <3a-3>:<3a-3> | enum_shore <a> certs    # + per-graph certificates

- `enum_shore.cpp` — the four necessary filters: deficiency range [B];
  all-colourings boundary row-sum vector in {(6,0,0),(3,3,0),(4,1,1),(2,2,2)} [C];
  localized comparable-nonneighbours [T]; boundary-shortfall [K].
- `verify_shore_indep.py` — independent Python reimplementation; identical counts
  at a = 9, 10, 11.
- `shore{9,10,11}_certs.txt` — per-graph fate certificates for every [B]+[C]
  survivor (graph6 + failed filter + killing vertex for [K]).
- `verify_9shore_survivor.py`, `kill_9shore_survivor.py` — the a=9 near-miss
  H = K_{3,3,3} minus a rainbow 3-matching (graph6 `HEzftz{`): full recount,
  structure, and the boundary-shortfall kill (also brute-forced over 3^8
  assignments).
- Large runs (a = 12, 13, 14) were executed as residue classes with a completeness
  guard: every class must end with geng's `>Z` terminator line and the generated
  count must equal the classifier's count.

## Theorem C (no bipartite shore; PG(2,5) sharpness)

- `pg25_test.cpp` — builds the incidence graph of PG(2,5) (31 points + 31 lines,
  6-regular bipartite, girth 6, n=62) and verifies a deletion-(2,2,2) witness for a
  point and a line; point/line-transitivity then covers all 62 vertices, so the
  graph is "all-unfrozen". This is the sharpness example of Remark 6.x: it passes
  the one-sided boundary-shortfall test at every vertex yet Theorem C excludes its
  deficiency-6 modifications.
- `verify_pg25.py` — independent Python reconstruction of the same graph (built from
  scratch over GF(5)), finding and explicitly checking the (2,2,2) witnesses
  (properness + neighbourhood colour counts). Two independent implementations agree.
- `unfrozen_census.cpp` — exhaustive deletion-witness census over 6-regular
  3-colourable graphs; confirms the whole-graph "frozen vertex" property holds for
  all n <= 15 (so the failure first appears at n=62, the PG(2,5) case).

## Lean-verified lemmas

`erdos944_cores.lean` (Lean 4 / Mathlib, toolchain leanprover/lean4:v4.27.0):
compiles with no sorry and no native_decide; `#print axioms` gives at most
[propext, Classical.choice, Quot.sound]:

- `singleton_edge_critical` — recolouring core of the singleton lemma (axiom-free);
- `comps`, `mem_comps` — enumeration of weak compositions with a proved
  completeness lemma;
- `cut_matrix_classification` — exactly 21 sum-6 matrices with all six
  permutation-diagonal sums >= 2;
- `matrix_mem_classification` — bridge to the genuine matrix form
  (forall pi in S_3 diagonal bounds);
- `turan_count_shore` — floor(a^2/3) < 3a-3 for 2 <= a <= 7.

`erdos944_rowforcing.lean` (same toolchain; `#print axioms cut_row_forcing` = [propext]):

- `cut_row_forcing` — among the 21 valid cut matrices, every one with row-sum vector
  (3,3,0) has both nonzero rows (1,1,1), and every one with (6,0,0) has nonzero row
  (2,2,2). This is the matrix input to the anti-diagonal and diagonal cases of
  Theorem C. Verify with `lake env lean erdos944_rowforcing.lean` against a Mathlib
  build for the stated toolchain.
