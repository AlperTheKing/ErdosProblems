# Exact Lean surface audited

From `ActiveScopedCoordinateTransport.lean`: the bundle is `Sigma q, Demand(after q)`; the target is `(q x OutsideShoreDemand) + (q x ShoreSource)`. Ordinary replacement asks only for an injection. Component-aware replacement additionally requires every shore-source image to satisfy `ComponentTransportSourceEligible`; outside-demand images have no legality condition.

Eligibility is exactly: the new component touches either changed row, or some old demand owned in the shore is Available to the source and its old component intersects the new component. Proved persistence is one-way: a new component avoiding both rows embeds in its old component. It does not connect that old component to a shore demand. The cardinal theorem discards `legal` via `toReplacementInjection`.

From `ActiveScopedVariationReduction.lean`: coordinate collision variation is bounded by `|Q_i| (|S_A|-|D_A|)`; coordinate HitNeed variation is nonpositive; score variation is their sum. Deficiency is strict `|S_A|<|D_A|`. Inclusion-minimality is not assumed by the transport declarations.
