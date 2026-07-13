# R29 production vertexSlack referee audit

## Verdict

Production vertexSlack cannot pay any of the 28 missing hub-shore units. Total available capacity at owners {0,1,2} is exactly zero, before and after factor-25 normalization.

## Independent all-anchor reconstruction

I read no forbidden R29 fanout/gate/global-min artifact or semantic-audit script. The archival specification gives N=2943 and 26*26=676 rigid double-star atoms. Every selected length-five rigid double-star row contains all three hubs. The tuple additionally selects 676 anchor, 28 circuit, and 3 cable-seed rows, unnecessary below. Comparison values: demand 19953, reach 19925, defect 28.

Production traffic is T(v)=5*r(v). For each hub, rigid rows alone give r(v)>=676, T(v)>=3380, and T(v)-N>=437. Hence max(0,N-T(v)) is exactly zero at hubs 0, 1, and 2. Extra rows only increase T.

## Separate audit layers

Available cap: raw hub cap is 0. In 25|S|<=25|F|+B this is B/25=0 Hall units, so payable defect is min(28,0)=0.

Legal incidence: PositiveSinkSemantics.vertexSlack_owner restricts legal ports for vertexSlack(v) to inside endpoint v. The singleton mixed constructor sends only non-Door off-support edges, at 1/2 to incident endpoints; Door edges consume no vertex cap. Active-scoped triples are not FullBank incidence certificates. Regardless of incidence, legal hub arcs reach zero-cap sinks.

Reserved/spent cap: componentReserveSlackQ and superadditivitySlackQ are non-spendable reserves, not vertexSlack tokens. Nonnegative spend plus no_double_spend forces spend from zero-cap tokens to zero. No checked R29 FullBank ledger is instantiated, so no positive unspent allocation is inferable: available, spent, and remaining hub vertexSlack are zero.

Component ownership: the cable keeps hubs in one active component. Covers and tokens are component-owned, typed vertexSlack is vertex-keyed, and no_cross_component_spend prevents pooling. Ownership does not remove endpoint locality or enlarge zero cap.

## Production trace

- Ell5SingletonVertexSlack.lean: endpoint load, half-incidence consumption, mixed Door/vertex routing.
- TypedPositiveCapacityMixedPath.lean: inside-endpoint ownership.
- Gamma/FullBankToLengthSurplusCharge.lean: spendable kinds, spend, ownership, no-double-spend, and reserves.
- Gamma/TypedFullBankSources.lean: vertex-keyed sources do not manufacture legal incidence.

## Replay

python tmp/fanout/r29_fullbank_referee/child_07/audit_vertex_slack.py


## Exact replay result and input hashes

Command: python tmp/fanout/r29_fullbank_referee/child_07/audit_vertex_slack.py

Result: N=2943; rigidDoubleStarRows=676; T_hub_lower=3380; excess=437; raw cap=0; scaled cap=0; defect=28; payable=0.

- WALL_ATTACK_R29_GPTPRO56.md: fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04
- R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md: 5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42
- Ell5SingletonVertexSlack.lean: 2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048
- FullBankToLengthSurplusCharge.lean: f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd
- TypedPositiveCapacityMixedPath.lean: 673fdf970934f9f6f3ddfefc5ad755c84123dada359719c8de0949e076319e7f
