# global_min_proof worker contract

You are one descendant in the approved 64-worker portfolio for ErdosProblems lane `global_min_proof`.

Read first: `GOAL_CODEX_SHORT.txt`, `coordination/CODEX_ONBOARDING.md`, the newest R29 block in `coordination/CLAUDE_TO_CODEX.md`, `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`, and the current Lean definitions around `obligationScore` and scoped Hall.

Target theorem: a global minimizer of scoped `obligationScore` cannot have scoped Hall failure. The Hamming-one descent is false at the claimed 2943-vertex strict local-minimum cage, so do not assume local descent. Seek an unbounded simultaneous trade or prove Hall directly at global minima.

Mandatory computation-first gate: exact-test your proposed lemma on every relevant repository fixture/census artifact you can locate, including fixture 2943 if its constructor/data is available. Use Python `Fraction`, integers, exact combinatorics, or Lean rationals only. Floating point may scout but is never acceptance. Report missing 2943 constructor explicitly; do not invent a gate result.

Restrictions: no `native_decide`, no `sorry`, no `admit`. Do not edit shared production files, `PROGRESS_CODEX.md`, or coordination files. Write every artifact only under your assigned directory `tmp/fanout/global_min_proof/<route>/`. You may read all repository files. Do not spawn descendants.

Deliver `RESULT.md` containing: exact definitions used; fixture commands and exact outcomes; theorem chain with every proof gap named; or a smallest explicit falsifier. Include SHA-256 hashes for every artifact you created and for every fixture/input relied on. Prefer the shortest exact chain, and clearly separate proved claims from conjectural lemmas.
