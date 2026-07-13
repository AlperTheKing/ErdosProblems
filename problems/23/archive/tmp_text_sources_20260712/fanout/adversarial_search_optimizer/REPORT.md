# Final report — adversarial_search_optimizer

## Exact claims

1. `optimizer.py` exactly evaluates the declared `row-choice-system` semantics using Python integers only: selected unions, off-support graph, active components, and scoped local costs.
2. Literal duplicate rows are safely quotiented per atom. The certificate records the raw-to-orbit maps and SHA-256 of both source and quotient.
3. For every accepted instance (nonnegative integer cost tables), 0 is a valid branch-and-bound lower bound even under arbitrary future component deactivation.
4. `exact-scoped-opt-v1` is a replay certificate: it lists every quotient terminal, exact score, optimum, and optimum score decomposition; `verify` regenerates the entire canonical object.
5. Selector/cable toys `k=1..8` were exhaustively solved and replay-verified. Each atom has 3 raw rows and 2 semantic row orbits. Quotient terminal counts were exactly `2^k` (2 through 256). Every optimum is the all-bypass choice and has score 0 with no active vertices.

## Falsifiers and guards

- Any differing regenerated certificate falsifies the claimed optimum.
- A negative/non-integer cost-table entry is rejected; allowing negative costs falsifies the universal lower bound 0.
- Quotienting nonidentical rows would falsify orbit safety; this implementation merges only byte-canonical identical row semantics.
- A toy optimum below 0, or an active vertex in the certified all-bypass optimum, falsifies the toy claim.

## Tested range

Python 3 exact replay on `toy1.json` through `toy8.json`; quotient terminal counts 2,4,8,16,32,64,128,256. No float calculation or float acceptance path exists.

## SHA-256

- `optimizer.py`: `FCDCF308132FFC03D42562B931F9EFA368E53CF9FF399D01A6F010BF41D96C65`
- `run.py`: `3C1AFDF2EA88D57E0CAB83186CA9D505144A0C39ECE3775AC3CF685F3B4A35CD`
- `make_toys.py`: `6E2967136E713457B75A8C1B5961B295D0F03CEDB33B4BC963395575CDCF89D4`
- `toy8.json`: `B578435D204D96ECF312F299FA2222B6A4FD6920B0368DC982B2E1B4A5F654EF`
- `toy8.cert.json`: `621DCAAB1C527C0A67F6CF22EA5B103BE9933AE9F7A4F8A78883323B79F3BFD9`

## Proof gaps / nonclaims

- The R29 2943 instance was not reconstructed: required documents omit canonical vertex/edge/row data, especially the 676 selector atoms x 680 rows. Aggregate histograms are insufficient to determine score or deactivation.
- Current cut state is the full prefix; it is exact but does not merge boundary-equivalent prefixes. Cross-atom permutation-orbit compression and a nonzero deactivation-aware lower bound remain unproved optimizations.
- The schema captures the stated scoped mechanism but is not claimed byte-equivalent to the unpublished R29 generator.
- No Lean formalization is claimed.
