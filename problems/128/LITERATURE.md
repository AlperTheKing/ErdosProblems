# Erdős Problem 128 — Literature Gate

## Statement and status

- Thomas Bloom, “Erdős Problem #128,” <https://www.erdosproblems.com/128>, accessed 2026-07-13. The page states the induced-subgraph formulation with `floor(n/2)`, lists no claimed solution, and lists no current worker.
- The discussion thread clarifies that “subgraph” means induced subgraph and records the correction from `n/2` to `floor(n/2)`: <https://www.erdosproblems.com/forum/thread/128>.
- The local formal statement is `formal-conjectures/FormalConjectures/ErdosProblems/128.lean`. Its condition `2 * |V'| + 1 >= n` is equivalent to `|V'| >= floor(n/2)`.

## Primary partial results

- Peter Keevash and Benny Sudakov, “Sparse halves in triangle-free graphs,” *Journal of Combinatorial Theory, Series B* 96 (2006), 614–620, DOI 10.1016/j.jctb.2005.11.003. They prove the conjecture when the total edge count is at most `n^2/12` or at least `n^2/5`.
- Sergey Norin and Liana Yepremyan, “Sparse halves in dense triangle-free graphs,” arXiv:1311.5818. They prove the conjecture for minimum degree at least `5n/14`, for average degree at least `(2/5-epsilon)n`, and for graphs close to the Petersen graph.
- Alexander Razborov, “More about sparse halves in triangle-free graphs,” arXiv:2104.09406. He proves the weaker universal bound `27n^2/1024` and proves the conjecture for several classes, including girth at least five, independence number at least `2n/5`, and strongly regular graphs.

## Local overlap

- `search128/search_128_blowup.cpp` exhausts only integer blow-ups of `C5` in its declared range.
- `search128/search_128_andrasfai.cpp` tests only the Andrásfai family, exactly for small orders and heuristically later.
- No local full-graph SAT certificate or complete `n = 20` search log was found.
- `handoff.md:79` marks #128 as crowded and advises against an open-ended attack. The present route is therefore restricted to one exact order and has a hard exit.

## Gate decision

A valid finite graph would be a novel direct counterexample to the stated problem. An UNSAT result for `n = 20` would be only a restricted computational fact, not a solution. The one-order attack passes the direct-route gate; any order cascade or asymptotic surrogate does not.

