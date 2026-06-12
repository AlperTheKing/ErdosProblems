# Ancillary files for "Exact 6-cut rigidity and small-order superconnectivity for the 6-regular case of Dirac's k=4 problem"

All graph generation uses nauty 2.8.9 `geng` (B. D. McKay), built with
`-DMAXN=WORDSIZE -DWORDSIZE=32`. All graph6 strings follow the standard nauty
format. Colourings are proper maps to {1,2,3}, never counted modulo colour
permutation.

## Theorem A (no 6-regular 4-vertex-critical graph on n <= 12 or n = 14)

Generator + classifier:

    geng -d6 -D6 <n> | check_g6 <n>          # counts: total / 3col / notVC / 4VCcrit / target
    geng -d6 -D6 <n> | check_g6_v2 <n>       # same, with the neighbourhood-bipartite prefilter

- `check_g6.cpp`, `check_g6_v2.cpp` — C++ classifiers (clang++ -O3). v2 adds the
  prefilter of Lemma (neighbourhood bipartiteness); both validated to produce
  identical classifications on n = 11, 12, 13.
- n = 14 was run twice with different residue chunkings (`geng ... r/110` and
  `r/73`); aggregates agree: 21,609,301 / 42,667 / 21,566,634 / 0 / 0.
- `unique_6reg_4vc_n13.txt` — the unique 6-regular 4-vertex-critical graph on 13
  vertices (edge list; graph6: `L?bFFbw~B{FwFw`).
- `verify_lemma21_n13.py` — audit of the singleton-lemma mechanism on that graph:
  78 vertex-deleted colourings, none with a 2+2+2 split; 156 singleton
  predictions; 13/13 critical edges covered, 0 false positives.
- `test_lemma21_random.py` — stress test of the vertex-form Kempe tether
  (19,389 implications on random 4-chromatic graphs, 0 failures).

## Theorem B (shore exclusion, sizes 9..13)

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
- Large runs (a = 12, 13) were executed as residue classes with a completeness
  guard: every class must end with geng's `>Z` terminator line and the generated
  count must equal the classifier's count.

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
