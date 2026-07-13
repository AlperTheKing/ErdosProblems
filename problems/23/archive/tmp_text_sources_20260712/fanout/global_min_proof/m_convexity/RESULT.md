# RESULT — m_convexity

## Outcome

The active-scoped obligation score is **not M-convex** on the partition-matroid row-choice bases. The same order-10 example falsifies the singleton case of the multiple-exchange axiom. Thus neither M-convexity nor multiple exchange can supply the global-minimum-to-Hall theorem without an additional restriction (for example, restriction to Hall-failing tuples plus a new graph theorem).

This does not falsify the target global-minimizer statement: all four tuples in the exchange witness that have score zero have empty demand and hence satisfy Hall. It falsifies the proposed discrete-convex proof route.

## Exact definitions used

For one selected length-five row per bad edge, `pairCount omega x y` is the number of selected rows containing both `x,y`. `ActiveOwner` means membership in an off-selected-support blue component containing both endpoints of some selected bad edge. Active collision halves are excess pair occurrences owned by active vertices. At active vertex `v`,

`activeDegree(v) = degree in the active off-support graph`,

`selectedLoad(v) = 5 * pairCount(v,v)`, and

`hitNeedUnits(v) = activeDegree(v) - (N - selectedLoad(v))` (natural-number truncated subtraction).

The tested integer valuation is exactly

`f(omega) = scopedObligationScore = card(ActiveCollisionHalf ⊕ ActiveHitNeed)`.

The domain is the direct product of row families, equivalently bases of a partition matroid with one chosen row in each block. For two bases `x,y` and a row `u` in block `i` selected by `x` but not `y`, feasibility forces the exchange partner to be the row of `y` in the same block. Hence M-convex exchange requires

`f(x)+f(y) >= f(x with i from y)+f(y with i from x)`.

For a singleton exchange set, the multiple-exchange axiom has the same unique feasible partner, so the same inequality is necessary.

## Smallest-order exact falsifier

Connected triangle-free graph6 string (shown in a fence because it contains a backtick), `N=10`:

```text
I?`fBO]]?
```

Edge set:

`04,06,15,16,17,19,25,26,27,29,38,39,47,48,49,58,68`.

Its three row-family sizes are `(4,6,6)`. Use coordinate tuples

`x=(0,0,0)`, `y=(3,0,1)` and exchange coordinate `i=0`.

Rows:

* `x`: `(0,4,9,1,6); (5,1,9,3,8); (6,1,9,3,8)`
* `y`: `(0,4,7,2,6); (5,1,9,3,8); (6,2,9,3,8)`
* `x'`: `(0,4,7,2,6); (5,1,9,3,8); (6,1,9,3,8)`
* `y'`: `(0,4,9,1,6); (5,1,9,3,8); (6,2,9,3,8)`

Exact scores are `f(x)=0`, `f(y)=0`, `f(x')=19`, `f(y')=0`. Therefore

`f(x)+f(y)=0 < 19=f(x')+f(y')`.

This is smallest by vertex order within the exact search: orders 5–9 exhausted 1,731 connected triangle-free graphs, 609 eligible nontrivial row databases, 2,951 tuples, and 21,995 exchange inequalities with no failure. At order 10 the script found the displayed first `geng`-order failure after 9,649 graphs, 4,965 eligible databases, 38,166 tuples, and 929,191 tested inequalities. “Smallest” here means minimum `N`, not minimum edge count or row-product size among all order-10 falsifiers.

## Persistent-component monotonicity and useful conditional inequality

The Lean file proves, for a one-coordinate replacement and an owner whose new active component touches neither changed row:

1. `activeDegree_new <= activeDegree_old`;
2. the selected load is unchanged;
3. consequently `hitNeedUnits_new <= hitNeedUnits_old`.

Together with a component-aware coordinate injection, the already-compiled cardinality argument proves the useful multi-row inequality

`sum_q (f(omega[i:=q]) - f(omega)) <= |Alt_i| * (|Source(A)|-|Demand(A)|)`

for every coordinate `i` and deficient owner shore `A`. Summing over coordinates gives strict negative total one-coordinate variation when at least one alternative exists. The only unproved graph-theoretic premise is existence of those component-aware injections. The supplied evidence that all 4,801,067 heavy-N12 tuples pass this premise and every failure has negative summed variation is therefore directly aligned with this conditional theorem, but is not a universal proof.

## Fixture commands and exact outcomes

`python tmp/fanout/global_min_proof/m_convexity/test_m_exchange.py --min-n 5 --max-n 9 --output tmp/fanout/global_min_proof/m_convexity/m_exchange_falsifier.json`

Outcome: exact integer PASS; no falsifier; counts as above.

`python tmp/fanout/global_min_proof/m_convexity/test_m_exchange.py --min-n 10 --max-n 10 --output tmp/fanout/global_min_proof/m_convexity/m_exchange_n10.json`

Outcome: exact integer FAIL; displayed axiom falsifier, `0 < 19` in the forbidden direction.

The 2,943-vertex constructor/data is absent from the repository; only its prose specification is present. No 2,943 gate or global-optimum claim is made here.

## Proof status

Proved/refuted exactly: unrestricted M-convexity fails; unrestricted multiple exchange fails; minimum vertex order of a failure is 10 within the exhaustive connected triangle-free census; the persistent-component `activeDegree` and `HitNeed` monotonicities and the injection-to-multi-row inequality are Lean-proved in the relied-on source.

Open gap: prove `RealHallFailureHasComponentAwareCoordinateTransport`, or another graph-structural premise implying negative summed variation, for every complete shortest-row database. No M-convex axiom can replace that gap.

## SHA-256

Created artifacts:

* `test_m_exchange.py` `fc3229692a7e02e87bf6b7026a083914dbd9e868ffc24d21ff5430a43d9930a2`
* `m_exchange_falsifier.json` `ee4a7df14f723dffc4fdce3c1db760bb0c4fa8bec1408fb9d0ab3ecadb2555d6`
* `m_exchange_n10.json` `f0e8b1d612d740a331f4e721e5f53eeca866db7e0775a7d333c8d22876ffd30b`

Relied-on inputs:

* `COMMON.md` `533cd8772b6f0cd8f667e3388b7baba9a0734f862e41cb01cd6958ac2c296003`
* `GOAL_CODEX_SHORT.txt` `e032a3a8877ad80cdd0e628ea3352208330520f5b8d79a5b55da7b7637518b09`
* `CODEX_ONBOARDING.md` `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`
* `CLAUDE_TO_CODEX.md` `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`
* `WALL_ATTACK_R29_GPTPRO56.md` `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
* `ActiveScopedMinimumExchange.lean` `8f39d8443ddc26d38bb76da10b9bed223f5f141546e6194c5177779f03174bc8`
* `ActiveScopedCoordinateTransport.lean` `6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272`
* `_codex_r19_global_base_census.py` `b49e9a2add265052605ac412449b9fb12b1b879cc67e254b68189db7b831a737`
* `_codex_r20_two_row_exchange_gate.py` `73697b12b1e22a30e320fb970415e79fa90d88d1a6db27f42022cf9ffd9c6d83`
* `_codex_r23_outside_attachment_full_obligation_gate.py` `26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1`
* `geng.exe` `b35c657aba143d59bff0a66b176559beaab4a34cf4314985cb7df1474c1df2cd`

`RESULT.md` cannot contain a stable SHA-256 hash of itself; its external hash at delivery is reported in the final response.
