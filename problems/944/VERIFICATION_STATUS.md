# Erdős #944 verification status

Updated: 2026-06-11 Europe/Istanbul.

## Target

Primary #944 target is the last open Dirac case `k=4,r=1`: a 4-vertex-critical
graph with no critical edge, or a proof none exists.

Current publishable-secondary candidate is narrower:

1. verified exhaustive lower bound for the Skottova-Steiner 2025 Problem 5.2
   subproblem: no 6-regular `(4,1)` graph on `n <= 14`;
2. structural rigidity lemmas for any hypothetical 6-regular target, including
   no nontrivial 6-edge-cut shore of size at most 14 in the 6-regular case.

This is not yet a full resolution of #944.

## Verified Artifacts

- `formal-conjectures/erdos944_cores.lean`
  - Compiles with `lake env lean erdos944_cores.lean`.
  - Clean log: `problems/944/lean_compile_clean.log`.
  - No `sorry`, `admit`, `axiom`, or `unsafe` tokens.
  - Covers:
    - singleton recolouring core of Lemma 1.1;
    - 6-cut matrix count/membership support;
    - numeric Turan shore inequality for `2 <= a <= 7`.

- `experiments/sixreg/check_stream2.cpp`
  - C++ verifier for SMS graph streams.
  - Checks 3-colourability, vertex-criticality, and existence of critical
    edges.
  - Recompiled with progress reporting every 10,000 graphs.

- GPT-5.5 Pro Property-B answer has been decomposed and independently
  re-derived into T1 lemmas in `PROOF_STATE.md`:
  - 6-regular triangle bound: every edge lies in at most four triangles;
  - exact conflict count for 6-edge cuts: every colour gluing has exactly
    two monochromatic cut edges;
  - corrected Kempe tether lemma in `G - {e,f}`;
  - no 6-edge-cut shore of size `2..8` in a 6-regular target.

- Cold GPT-5.5 Pro red-team completed:
  - digest: `problems/944/gpt_redteam_2026-06-10.md`;
  - verdict: claims 1-5 are sound after wording corrections;
  - riskiest step: never use the Kempe tether as shore-internal without an
    additional localization argument.

- Exhaustive enumerations rechecked with standalone C++ summary files:
  - `n=11`: 266 six-regular graphs.
    - `experiments/sixreg/check_n11_summary2.out`
    - SHA256 `9397F2F65C5422AACAAC6EE78F1BA8794A5B1EF643C7483ADA17EE54433E7D7F`
  - `n=12`: 7,849 six-regular graphs.
    - `experiments/sixreg/check_n12_summary2.out`
    - SHA256 `92465A738543C27BEE01A79B4294A2F2D1066FFE43E535F12E59DC183FE2F4C9`
  - `n=13`: 367,860 six-regular graphs.
    - `experiments/sixreg/check_n13_summary2.out`
    - SHA256 `13EC862D7E79951E8DFF5E4BA52173778C8EA8A79C209C922FBB184DD9C7F8EE`
  - Summary: no 6-regular `(4,1)` graph for `n<=13`; exactly one 6-regular
    4-vertex-critical graph at `n=13`, and it has critical edges.
  - `n=14`: 21,609,301 six-regular graphs, checked twice by different native
    chunk partitions.
    - `experiments/sixreg/n14_chunks`: 110 residue classes, aggregate
      `total=21609301 threecol=42667 notVC=21566634 vcWithCritEdge=0 TARGET=0 badline=0`.
    - `experiments/sixreg/n14_chunks_v2`: 73 residue classes, identical
      aggregate.
    - Conclusion: no 6-regular 4-vertex-critical graph on 14 vertices at all.

- `experiments/sixreg/enum_9shore.cpp`,
  `experiments/sixreg/verify_9shore_survivor.py`,
  `experiments/sixreg/kill_9shore_survivor.py`
  - Computer-assisted 9-shore exclusion for 6-regular targets.
  - nauty/C++ filter over 729 connected 9-vertex, 24-edge, max-degree-6
    candidates leaves one survivor (`HEzftz{`, `b=011101110`).
  - Independent Python recount reproduces the classification.
  - Local multiplicity kill: for each internal vertex `0,4,8`, all 6 proper
    3-colourings of the survivor with that vertex deleted leave a colour
    appearing at most once in its neighbourhood.
  - Conclusion: no nontrivial 6-edge-cut shore has size `9` in a 6-regular
    `(4,1)` target; combined with the T1 `2..8` argument, all such shores have
    size at least `10`.

- `experiments/sixreg/enum_10shore.cpp`,
  `experiments/sixreg/verify_10shore.py`
  - Computer-assisted 10-shore exclusion for 6-regular targets.
  - nauty/C++ filter over 18,655 connected 10-vertex, 27-edge,
    max-degree-6 candidates leaves no survivors:
    `total=18655 badDeficiency=0 not3col=18345 badBoundaryVec=197 comparableNonNbr=86 localMultiplicityKill=27 SURVIVORS=0`.
  - Independent Python recount reproduces the same classification:
    `{'badvec': 197, 'badcomp': 86, 'not3col': 18345, 'badlocal': 27}`.
  - Conclusion: no nontrivial 6-edge-cut shore has size `10` in a
    6-regular `(4,1)` target; combined with the previous exclusions, all such
    shores have size at least `11`.

- `experiments/sixreg/enum_shore.cpp`,
  `experiments/sixreg/verify_shore_indep.py`
  - Generalized shore filter for sizes `a=9..14`.
  - Full C++ chunk coverage:
    - `a=11`: `total=696208 not3col=687377 badBoundaryVec=6013 comparableNonNbr=1300 localKill=1518 SURVIVORS=0`;
      independent full Python recount matches.
    - `a=12`: 110/110 chunks, `total=32833744 not3col=32484081 badBoundaryVec=241863 comparableNonNbr=27322 localKill=80478 SURVIVORS=0`.
    - `a=13`: 110/110 chunks, `total=1839349287 not3col=1822133664 badBoundaryVec=11944366 comparableNonNbr=788481 localKill=4482776 SURVIVORS=0`.
    - `a=14`: 110/110 chunks, `total=154941621 not3col=115063872 badBoundaryVec=32712357 comparableNonNbr=1752943 localKill=5412449 SURVIVORS=0`.
  - Independent Python spot checks agree for an `a=13` residue sample and an
    `a=14` 5000-line graph6 sample.
  - Conclusion: no nontrivial 6-edge-cut shore has size `9..14` in a
    6-regular `(4,1)` target; all such shores have size at least `15`.

## Pending / Needs Stronger Evidence

- teorth PR #314 is open/ready for review with a one-line database comment.
  A public artifact branch is available, but the artifact link could not be
  inserted into the PR body/comment automatically because the GitHub connector
  lacks write permission on `teorth/erdosproblems` and browser text insertion
  hit the virtual clipboard limitation.
- Decide which parts should get additional Lean coverage beyond the current
  cores.

## Current Blocking Mathematical Question

The immediate blocker is no longer the Kempe package itself; it is packaging
and adversarial verification:

- write the rigidity lemmas cleanly with the red-team wording corrections;
- monitor/respond to teorth PR #314 review;
- manually add the artifact link to PR #314 if a reviewer asks or browser input
  becomes available;
- fold the `n=14` closure and 9..14-shore exclusions into the public artifact
  branch / PR wording after final review.

## Publication Status

- PR: https://github.com/teorth/erdosproblems/pull/314
- Branch: `AlperTheKing/erdosproblems-fork:erdos944-sixreg-progress`
- Commit: `bce7260`
- Scope: one `data/problems.yaml` comment, status remains `open`.
- Public artifacts:
  https://github.com/AlperTheKing/erdosproblems-fork/tree/erdos944-artifacts/artifacts/erdos944-sixreg
