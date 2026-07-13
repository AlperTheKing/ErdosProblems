# Exact collision / HitNeed accounting report

## Notation
Fix coordinate `i`, old row `P`, an alternative row `Q`, and let `b(x,y)` be the ordered co-occurrence multiplicity contributed by all rows except `i`. Put `R_S(v)=2 sum_y max(0,m_S(v,y)-1)`. Let `A_S` be the active vertices, `k_S(v)` their active-component labels, and let `shore(v)` mean membership in the fixed deficient owner shore `A`.

## Exact identities
For every vertex `v` and replacement `P -> Q`, integer arithmetic gives

`R_Q(v)-R_P(v) = 2 T_Q(v) - 2 T_P(v)`,

where `T_S(v)=#{y : v in S, y in S, b(v,y)>=1}`. Thus the exact transport supply released by the old row is `2 T_P(v)` and the exact consumption of the new row is `2 T_Q(v)`. Common cells cancel automatically. This is the sharp term erased when the cardinal injection remembers only target cardinality/capacity and not whether an ordered cell is already occupied by another row.

Moving active scope is accounted for exactly by

`C_Q-C_P = sum_{v in A_P}(R_Q(v)-R_P(v)) + sum_{v in A_Q\A_P}R_Q(v) - sum_{v in A_P\A_Q}R_Q(v)`.

For state `S`, component `K`, and side `sigma` in `{shore,outside}`, define

`C[S,K,sigma]=sum {R_S(v): v in A_S, k_S(v)=K, side(v)=sigma}`,

`H[S,K,sigma]=sum {max(0,d_S(v)-max(0,n-5 r_S(v))): v in A_S, k_S(v)=K, side(v)=sigma}`.

If `a_i=# alternatives`, the requested one-coordinate identities are

`oneCoordinateCollisionVariation = sum_Q sum_{K,sigma} C[Q,K,sigma] - a_i sum_{K,sigma} C[P,K,sigma]`,

`oneCoordinateHitNeedVariation = sum_Q sum_{K,sigma} H[Q,K,sigma] - a_i sum_{K,sigma} H[P,K,sigma]`.

The desired sign is the separate inequality

`sum_Q sum_{K,sigma} H[Q,K,sigma] <= a_i sum_{K,sigma} H[P,K,sigma]`,

so the HitNeed contribution is nonpositive without being charged to transport supply.

## Exact tests and falsifiers
Fixture graph6 `I?`fBO]]?`, family sizes `[4,6,6]`: all 2 Hall-deficient row choices were tested, comprising 6 coordinate instances and 26 alternatives. The saturated-pair identity, moving-scope identity, and component/shore totals had no falsifier. Coordinate collision bound failures: `0/6`. Positive coordinate HitNeed variations: `0/6`. Aggregate collision variation was `-416`; aggregate HitNeed variation was `-78`. Machine record: `exact_tests.json`.

The detailed choice `[1,1,1]` record (`default.json`) has collision variation `-208` over 13 alternatives and supplies the per-alternative component/scope data. No fraction or floating-point arithmetic was used.

## Hashes (SHA-256)
`f5c3fa45c9e9ccd9743d00feb3e5b08345ee957bf3f788a4f4216358c9cee978  default.json`

`dac6db2fed41e1eee622ea3f90c5ad76ffefac95924eb59d098e2e2161aa5d5a  exact_tests.json`

`a2a10e6241cb7d5254db8530c44d510c3e36779876ba7b219bdce49e5fa3ed62  _codex_scoped_variation_anatomy.py`

`f3ffd8b22edd2de55d53664f20b77651df4b35033ba3e1ecb5d029aa11f8a921  ActiveScopedVariationReduction.lean`

`2821eb83265c85dc41f42edd2b31dae11fe60256b257e6c129bbb6e882ab5706  ActiveScopedCoordinateTransport.lean`

## Unresolved combinatorial lemma
For every deficient owner shore and coordinate, prove simultaneously that the component/shore-resolved saturated release, after the two exact activation corrections, pays `a_i*(ownerDemand-ownerSourceHalves)`, and that the component/shore HitNeed sum is nonpositive. Equivalently, construct a charge from every unmatched shore-demand unit to a distinct base-saturated ordered pair released by `P`, allowing only same-component inherited anchors, while pairing every positive new HitNeed increment with an old HitNeed decrement. The census verifies the resulting two inequalities but does not supply this injection/pairing.
