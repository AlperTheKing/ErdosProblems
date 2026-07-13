# Exact double-star global-minimizer search

## Result

The global-minimizer scoped-Hall statement is already falsified by the geometric-row-unique double-star family. For `a=4,b=5,e=0`, the row database is singleton, hence its only RowChoice is a global minimizer of `obligationScore`; the hub owner shore has demand 528 and reach 526, an exact Hall deficit 2. This is the independently replayable 89-vertex R22 certificate, not the unreplayable R29 prose construction.

## Family and exact formulas

Core blue edges are `r-cL`, `r-cR`, `cL-L_i`, `cR-R_j`; all `a*b` leaf pairs are bad. Each bad edge has the unique row `(L_i,cL,r,cR,R_j)`. Private length-three lock arms run from core vertices to a common anchor. Canonical leaf lock counts are `b,...,b,b-1` on the left and `a,...,a,a-1` on the right; `e>=0` extra arms are placed at `r`.

`Q=2ab-2+e`, `N=4+a+b+2Q=4ab+a+b+2e`.

The exact quotient for any core switch is indexed by three hub bits, switched-leaf counts `p,q`, and membership bits for the two low-lock leaves. Its loss is
`p*b-lowL + q*a-lowR + e*hr + delta_B(core)-delta_M(core)`.
The script exhausts this quotient and asserts it is nonnegative.

Collision score:
`Score=2[4a(b-1)+4b(a-1)+3(5ab-a-b-3)]`.
There are no active edges.

For `W={r,cL,cR}`:
`D(W)=6(5ab-a-b-3)`;
`Reach(W)=2[3(N-(3+a+b))+a(a-1)+b(b-1)]`;
therefore
`gap=D-Reach=2(3ab-a^2-b^2-2a-2b-6e)`.
Positive gap is an explicit Hall falsifier.

## Global optimization and symmetry

With one geometric row per bad edge there is exactly one RowChoice, so global optimality is tautological, not local-descent based. Duplicate aliases `u` and presentation blocks `c` were varied from 1 through 4. They are deliberately symmetry-only: every alias denotes the identical Row5, so all `u^(ab)` syntactic tuples map to one selected-row multiset and have identical score and Hall data. This is an exact orbit reduction. It does **not** model R29's genuinely different selector routes; doing so requires the missing constructor/row database.

## Search

Command:
`python search.py --max-side 18 --max-extra 8 --max-alias 4 --max-coupling 4 --output search_results.json`

Ranges: `2<=a<=b<=18`, `0<=e<=8`, `1<=u,c<=4`. Exact integer cases: 22,032; positive-gap cases: 9,584. Smallest by `(N,ab,a,b,e)`: `(a,b,e)=(4,5,0)`, `N=89`, `Q=38`, score 776, demand 528, reach 526, gap 2. Minimum switch loss is 0.

Explicit non-Hall regimes are exactly those satisfying
`3ab>a^2+b^2+2a+2b+6e`.
Thus extra lock arms monotonically destroy the hub-shore obstruction by 12 reach halves per arm. Star imbalance is limited by the quadratic term `a^2+b^2`.

## Explicit falsifiers and corrections

- Falsifier to the GLOBAL-minimizer Hall theorem: `a=4,b=5,e=0`, singleton rows, hub gap 2.
- Falsifier to unlimited lock strengthening preserving failure: any `e` with `6e>=3ab-a^2-b^2-2a-2b`; for `(4,5)`, already `e=1` gives gap `-10`.
- During development, the provisional score formula returned 880 at `(4,5)`; comparison with the independent fixture's 776 falsified it. Cause: a leaf row shares four, not five, coordinates with another row at that leaf. The final formula returns 776.

## Proof gaps

The script proves the core-switch quotient and evaluates the closed-form hub shore, but does not independently rebuild the full graph, enumerate shortest paths, or run the full max-flow. Those graph-level checks are supplied by the hashed R22 fixture below. A formal Lean theorem for the parametric formulas was not written. Alias coupling is not genuine selector coupling. The R29 2943 construction remains ungated because no graph/row artifact exists.

## SHA-256

Created:
- `search.py`: `cb52baaad8395864c6efabac1e147c0d6f596359082a76663bba43070a393ee7`
- `search_results.json`: `304767bd4c2f06dfd0589eef204894c0d0de55ab2cb3cfdef776abdb9e657d37`

Inputs:
- `coordination/CODEX_ONBOARDING.md`: `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`
- `WALL_ATTACK_R29_GPTPRO56.md`: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- newest R29 handoff `tmp/fanout/r29_gate/d10/report.md`: `f9c74e30626bed51eb5f4e92ff51768a29a40773069ede5c36d35cc82085503d`
- exact 89-vertex fixture `_claude_r22_89_gate.py`: `80191648ac38b353df13cf3ca700cecb86b6f683e80584eea2296f841a7df5d4`
- `MinimumDemandRowSelection.lean`: `e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a`
- `ActiveScopedOwnerHallReduction.lean`: `6a4d47533d10e4b04eb19cda0d0554658abd434c94c04566a01916708a90e8f0`

## Final fixture replay

`python problems/23/writeup/_claude_r22_89_gate.py` exited 0: all checks passed, including 4096 exact core assignments, unique shortest rows, score 776, full max-flow 774 versus demand 776, and hub-shore 528 versus 526.
