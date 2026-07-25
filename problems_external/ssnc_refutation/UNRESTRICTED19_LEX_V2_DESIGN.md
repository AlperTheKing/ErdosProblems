# Unrestricted order-19 lexicographic C++ v2 design

Status: design only. The live v1 source, executable, and run are unchanged.

## Exact ranking bound

For a domain-valid order-19 row, d=8 has need=3 and each witness count at most8, so row smooth energy is at most24. For d=9 it is at most9; for d>=10 it is zero. Hence total smooth energy is at most 19*24=456.

Use stride457 and rank 457*objective+smooth_energy for global-best ordering. The maximum domain-valid rank is 57*457+456=26505, so int and atomic<int> are sufficient.

## Acceptance rule

Do not feed the stride-weighted rank into Metropolis acceptance. Define literal_delta=candidate.objective-current.objective. If nonzero, use literal_delta; otherwise use the smooth-energy delta. Thus literal improvements are deterministic, literal uphill moves remain possible during hot phases, and equal-literal motion uses the existing smooth landscape. The exact score_zero and independent raw replay remain the sole hit path.

## Source impact

In a separate future v2 source: add constants 456 and457; add best_rank and lex_acceptance_delta helpers; change the global-best atomic and mutex comparisons to best_rank; change the Metropolis delta to lex_acceptance_delta; record best_order=objective_then_smooth and bump schema metadata. Do not alter score_zero, verifier replay, or the live v1 source.

## Calibration

- current(13,14), candidate(11,16): ranks5955->5043; accept and checkpoint.
- current(9,0), candidate(8,456): ranks4113->4112; accept and checkpoint.
- current(9,456), candidate(10,0): ranks4569->4570; never checkpoint; acceptance delta+1.
- current(9,17), candidate(9,16): smooth tie-break accepts and checkpoints.
- identical pair: no checkpoint churn.
- a domain-valid synthetic smooth value457 must fail an assertion.

At the current schedule, literal +1 acceptance is exp(-1/3) in the hot phase and exp(-1/0.05) in the cold phase. Using the rank delta instead would make a +1 change approximately457 and destroy escape behavior.

## Seed caveat

The v1 source always calls initial_graph_for_q and has no objective-9 raw-seed loader. Its warmup also retains every valid proposal. A truthful future objective-9 mode must parse and re-evaluate the raw seed, require q=5 and objective9 plus both-oracle agreement, then skip warmup for that lane or use the same lexicographic acceptance during warmup. Comparator changes alone are not a search from the objective-9 seed.

No production launch is authorized by this design.

## Referee correction

The schedule never samples phase exactly1. Its coldest step has `T_min=0.05+2.95/50000=0.050059`, so literal +1 acceptance is approximately `2.11e-9`. The phrase `exp(-1/0.05)` above is only the limiting endpoint. All ranking bounds, rank examples, acceptance signs, seed caveat, and unchanged exact hit path were independently accepted.
