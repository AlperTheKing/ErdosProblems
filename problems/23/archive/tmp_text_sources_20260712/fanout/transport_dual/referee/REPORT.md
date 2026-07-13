# Adversarial referee report: transport duality

## Verdicts

ACCEPTED: the coordinate collision bound plus `HitNeed <= 0`, the score decomposition, and the cardinal identities imply the ordinary cardinal inequality and hence some `CoordinateReplacementInjection` by finite cardinality. No component information is needed for that conclusion.

REJECTED: locality + one-way persistent-component embedding + inclusion-minimal deficient shore imply `ComponentAwareCoordinateReplacementInjection`. They do not ensure that a new persistent component meets the old component of any shore demand available to a needed shore source.

REJECTED: checking only total capacity `|new bundle| <= |Q|(|outside|+|shore sources|)` establishes component-aware transport. It establishes only the unlabelled injection after erasing `legal`.

ACCEPTED (exact finite characterization): add Hall for the actual legal bipartite relation. For every subset `X` of `CoordinateNewDemandBundle`,

`|X| <= |N_L(X)|`,

where every `(q,outsideDemand)` target is adjacent to every bundle element and `(q,shoreSource)` is adjacent exactly when `ComponentTransportSourceEligible` holds. Equivalently,

`|X| <= |Q| * (|OutsideShoreDemand| + |EligibleSources(X)|)`.

This is necessary and sufficient for the component-aware injection. A graph-side theorem implying this inequality is the logically sharp missing axiom. Merely asserting that each new component has one eligible source is insufficient because capacities can collide; the subset inequalities are necessary.

## Smallest exact abstract falsifier

One coordinate, one alternative, singleton inclusion-minimal shore `A={a}`:

* old shore demands: 2, both owned by `a`;
* distinct shore sources: 1, available to the old shore demands;
* old outside demands: 0;
* new demands across the sole alternative: 1, owned in component `C_b`;
* old shore demands/source lie in disjoint component `C_a`;
* `C_b(new) subset C_b(old)` and `C_b` avoids both changed rows.

Exact checks: deficiency `1<2`; collision delta `1-2=-1`; required collision bound `1-2=-1`; HitNeed delta `0<=0`; ordinary target cardinality `0+1=1`; bundle cardinality 1. Thus the scalar facts and ordinary injection hold at equality. Eligibility is false: no row touch and no available shore demand has old component intersecting `C_b`. Therefore the sole bundle element has zero legal targets and no component-aware injection exists.

`enumerate.py` exhaustively checked aggregate values `0..4` for `(dA,sA,outside,new)`, found 35 falsifiers, and found none with total counted multiplicity below 4. This minimality is for the stated abstract aggregate signature, not for real graphs.

## Abstract versus graph-realizable

The witness is an ABSTRACT FALSIFIER only. It respects the listed consequences as logical predicates, including one-way locality/persistence and singleton minimality, but it was not reconstructed from `GraphData`, `CutData`, shortest rows, `ActiveOwner`, collision demands, and `Available`. Accordingly it does not refute the desired theorem restricted to triangle-free max-cut graph instances. It proves that a graph-specific component-capacity lemma is indispensable.

No graph-realizable falsifier was established in this lane. The separate 2943 reconstruction was deliberately not used or duplicated.

## Proof gaps

1. Prove the legal-relation Hall inequalities from graph structure, preferably component by component with shared-source capacity retained.
2. Show how inclusion-minimal deficiency forces enough eligible source components; current Lean minimality is not an input to the transport declaration.
3. Control touched-row components: eligibility makes every shore source legal there, a very strong rule whose graph-side injective capacity still needs proof.
4. For untouched persistent components, prove attachment to old components carrying enough available shore demands, not merely containment in some old component.
5. Establish or refute graph realizability of the four-entity abstract pattern under the full demand definitions.

## SHA256

* `enumerate.py`: `f5700d6531114171d147bbfea8c9dd91d362890d52203b3c051d5685b2b1786a`
* `smallest_falsifier.json`: `efd98f164ce433bf4000f26b4db7e50cce6c9c6d70853ec6225b0a08c7d01c66`
* `ASSUMPTIONS.md`: `6828c878d739e40ef83deead255bffd73ab7e4ea27f6546c4d671c2c7595ed2e`
* audited `ActiveScopedCoordinateTransport.lean`: `2821eb83265c85dc41f42edd2b31dae11fe60256b257e6c129bbb6e882ab5706`
* audited `ActiveScopedVariationReduction.lean`: `f3ffd8b22edd2de55d53664f20b77651df4b35033ba3e1ecb5d029aa11f8a921`
