# Exact transport-dual falsification report

## Scope and reconstruction

Read-only model sources: `problems/23/writeup/_codex_scoped_variation_anatomy.py`, `_codex_r23_heavy_alltuple_descent_gate.py`, and `_codex_r23_outside_attachment_full_obligation_gate.py`. The reconstructed bipartite incidence has demand owners on the left, ordered free-half cells on the right, cell capacity 1 on demanded active edges and 2 otherwise, and owner-to-cell eligibility exactly as `owner_shore_source_count` defines it. Component-aware alternative groups use the inherited/touched-anchor rule in `component_transport_flow`.

All certification arithmetic is integer (hence exact rational with denominator 1). No floating-point result, `native_decide`, or `sorry` was used.

## Parameters and counts

- graph6 fixture: "I?`fBO]]?"; order 10.
- Shortest-row family sizes: 4, 6, 6; exhaustive row-choice tuples: 144.
- Active-scope Hall failures: 2, at tuple 43 / choice (1,1,1) and tuple 108 / choice (3,0,0).
- Owner-shore inequalities enumerated: 3 per failure, 6 total.
- Inclusion-minimal deficient shores: 1 per failure, 2 total.
- Coordinate component-aware systems: 6; all-coordinate systems: 2.
- Exact subset limit: 22 demand groups; skipped systems: 0. Every tested alternative system had zero positive-demand groups, so its survival is vacuous and is not evidence for a general inequality.

## Smallest exact witnesses and optima

For both failing tuples, the inclusion-minimal shore is owners {8,9}. Owner demands are 9 and 10. Singleton exact gaps `demand-capacity` are -2 and 0; the joint shore has demand 19, exact source/max-flow optimum 17, and exact gap 2. Thus the plain owner-shore Hall/Farkas inequality `d(S) <= cap(N(S))` is falsified by 2, while every proper nonempty subshore survives. The lexicographically first exported witness is tuple 43 in `smallest_witness.json`.

The second witness has the same exact optimum and gap but replaces cells (8,1),(9,1) by (8,2),(9,2). Full incidences and all exact subset values are in `base_shores.json`.

## Candidate-family outcomes

- Singleton-owner Hall: 4/4 survived; minimum exact slack 0.
- Full deficient-owner-shore Hall: 0/2 survived; exact maximum gap 2.
- Per-coordinate scaled component-aware Hall/Farkas: 6/6 survived, but all six had zero demand groups.
- All-coordinate scaled component-aware Hall/Farkas: 2/2 survived, but both had zero demand groups.
- Shared/unscaled component-aware variants: same counts and same zero-group qualification.

Machine-readable survivor qualifications are in `survivors.json`; exhaustive tuple records are in `results.json` and `results_unscaled.json`.

## SHA256

- `exact_probe.py`: `349abba9a347e186d5d690b743c4d443cf3160e04f6917c7e37eca5a4a51c0fc`
- `exact_probe_unscaled.py`: `bd769109715c0a166016571c17cf2a4a6639ffd7035c54529697f7466d22cf89`
- `base_shores.py`: `5ab926c836b12eb90b813157bbed672538103fea22cc8d9c21afc0e33694b1d1`
- `results.json`: `dddc04d17402d4afb2b01eade2413b97235f4ee2b904f6d94f807b166cace318`
- `results_unscaled.json`: `d5284104c95ffe68eadb2d69c7b280b58d97d13b091660925aed5f9df1a003a4`
- `base_shores.json`: `95b7d3e3bc6c978b194dd12211e5c4e046060aa2b982fa2cb1fa3ac32417e40f`
- `smallest_witness.json`: `a95b719e35c23bb4363a4c59893f0efb668a7af7bc6a3ac79dedca723637ba8d`
- `survivors.json`: `f154bb2190032ef25fafc6041cbbcbe1266163b50cf1e03ac88cd6780ff08fc9`

## Untested regimes

Other graph6 fixtures and orders; row systems not belonging to this 4x6x6 fixture; outside-scope obligations; positive-demand alternative/component groups; demand-group systems above 22 groups; fractional capacities or coefficients not reducible to this integer incidence; weighted Farkas multipliers beyond 0/1 shore indicators; simultaneous changes of two or more rows that are not represented by the enumerated Hamming-one coordinate families.

