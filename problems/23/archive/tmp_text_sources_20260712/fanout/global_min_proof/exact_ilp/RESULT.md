# RESULT — route exact_ilp

## Outcome

I obtained an exact finite 0-1 reduction theorem, not a resolution of the uniform graph theorem and not a counterexample. `FORMULATION.md` gives a MILP/SAT model whose integral optimum is exactly Lean `obligationScore`, and whose augmented feasible points at that optimum are exactly Hall-failing global minimizers.

I also found a concrete defect in the repository's existing C5 CP-SAT prototype: `solve_failing_optimum` treats every row companion as eligible but Lean `RowCompanion` additionally requires the exact cut predicate `0 <= sigma G c [a,b]`. Thus SAT from that symbolic model needs independent replay; UNSAT remains sound because it is UNSAT for a relaxation.

## Exact definitions used

From `MinimumDemandRowSelection.lean`: one literal row per bad edge; `pairCount`; `collisionUnits=sum_(x,y)(pairCount x y - 1)` with Nat truncation; selected vertex and path-edge unions; `activeEdges` are blue edges with both endpoints selected but absent from selected support; `obligationScore=2*collisionUnits+2*|activeEdges|`.

From `MinimumDemandCollisionHall.lean`: two collision halves for every excess ordered-pair occurrence; free directed distinct source halves have pairCount zero; half zero on an active edge is reserved; eligibility is SameOwner OR RowCompanion, where RowCompanion includes both positive co-occurrences and `sigma([a,b])>=0`; scoped Hall fails when some nonempty owner shore has demand strictly greater than its available-source neighborhood.

## Proved finite theorem chain

1. Exactly-one row variables biject with `RowChoice`.
2. The count, threshold, excess, OR, and AND constraints force the literal `pairCount`, collision excess, selected vertices, selected support, and active edges.
3. Therefore the integer objective equals `obligationScore` term by term.
4. Shore/source variables with the mandatory sigma filter force the literal available neighborhood.
5. The strict integer inequality `D >= |N(W)|+1` is equivalent to scoped Hall failure.
6. Hence augmented UNSAT at a proved optimum implies every global minimizer satisfies scoped Hall; SAT plus literal replay yields a counterexample.

Proof gap: this is instance-wise. No graph-structural argument proves augmented UNSAT for every complete triangle-free maximum-cut row database.

## Fixture commands and exact outcomes

Full records are in `GATES.jsonl`.

* C5 sizes `1,1,1,1,1`: n=5, optimum 0, independent matcher PASS, failing-minimizer relaxation UNSAT.
* sizes `1,1,2,1,1`: n=6, 2 rows for the bad edge, optimum 0, replay PASS, relaxation UNSAT.
* sizes `2,1,1,1,2` (canonical rotation): n=7, 4 rows, optimum 0, replay PASS, relaxation UNSAT.
* preserving that noncanonical ordering was rejected exactly because its displayed cut was not maximum (`len(blue) != maximum`).

These are exact integer/CP-SAT outcomes. They are small smoke gates, not evidence for the uniform theorem.

## Mandatory fixture 2943

FAIL / unavailable. Repository-wide search found only the prose specification in `WALL_ATTACK_R29_GPTPRO56.md` and the newest R29 mailbox block. There is no executable constructor, graph/row database, or claimed SHA artifact `00186166...` in the workspace. Therefore I did not claim a 2943 gate, global optimum, or Hall verdict. The decisive 2943 joint-selector landscape remains open until its constructor/data is supplied.

## SHA-256

Relied inputs:

* `COMMON.md` 533cd8772b6f0cd8f667e3388b7baba9a0734f862e41cb01cd6958ac2c296003
* `GOAL_CODEX_SHORT.txt` e032a3a8877ad80cdd0e628ea3352208330520f5b8d79a5b55da7b7637518b09
* `CODEX_ONBOARDING.md` e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0
* `CLAUDE_TO_CODEX.md` b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126
* `WALL_ATTACK_R29_GPTPRO56.md` fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04
* `MinimumDemandRowSelection.lean` e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a
* `MinimumDemandCollisionHall.lean` ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7
* `_codex_r20_c5_nonuniform_global_cpsat.py` 25707f776cfca057ef17aab5f54303f1c9d5a1ee796583fdddb03bfffc63cf68
* `_codex_r20_two_row_exchange_gate.py` 73697b12b1e22a30e320fb970415e79fa90d88d1a6db27f42022cf9ffd9c6d83

Created artifacts before this report:

* `FORMULATION.md` e29f21aaef89561b79b3369e666e0a839df181ae732f7847888fdbd1f6bde6d1
* `GATES.jsonl` 668bb025a7e79435cb8b518c4edf6ad896f980a52486131868674d5f21ae75e9
