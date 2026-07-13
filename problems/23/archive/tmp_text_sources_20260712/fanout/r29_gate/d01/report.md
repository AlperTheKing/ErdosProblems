# R29 deterministic reconstruction gate (d01)

## Verdict

`UNDERDETERMINED`. The local sources do not determine a 2943-vertex graph or its selected row tuple. I reconstructed, serialized, and checked the uniquely recoverable 2927-vertex subgraph: the complete 2760-vertex traffic/lock block and the independently archived 167-vertex 28/27 circuit. The remaining prose specifies only aggregate counts, not incidences.

Run `python reconstruct.py` in this directory. It uses integers only and deterministically rewrites `known_subgraph.json` and `certificate.json`.

## Exact reconstructed claims

- Traffic class: 54 core edges + 676 leaf-pair edges + 1352 length-three lock arms (4056 edges) = 4786 edges on 2760 vertices.
- Selected double-star rows: all 676 tuples `(L_i,cL,r,cR,R_j)` in lexicographic `(i,j)` order.
- Circuit: 167 vertices, 207 blue edges, 28 atom edges, 235 total edges, and 28 canonical lexicographic-BFS selected length-four paths. Its displayed cut has 207 edges; the 28 edge-disjoint private 7-cycles give the matching upper bound 207.
- Canonical known serialization: UTF-8 compact JSON, sorted keys, sorted vertex labels, sorted endpoints, lexicographically sorted edges/rows, one LF terminator.
- Combined known object: 2927 vertices, 5021 edges, 704 selected rows.

## Exact aggregate identities accepted (not graph facts)

`4786+3380+15+235+6=8422`; `4110+2704+12+207+6=7039`; `676+28+3=707`; `676*679=459004`.

## Missing data / falsifier

The claimed completion needs 16 vertices, 3401 edges, and 679 selected rows beyond the recovered object: 3380 selector-C5 edges, 15 private cable-seed-C5 edges, and 6 cable edges. R29 does not give their endpoint lists. It also does not specify the left/right selector partition, how the 1352 lock vertices are paired into 676 C5s, the three private C5 layouts, or the cable's exact circuit endpoint labels.

This is a constructive falsifier of unique reconstruction: endpoint permutations inside either lock region preserve every aggregate sentence in R29 but change the labeled edge list and canonical SHA256. Hence no canonical serialization can be derived from those sources. The claimed prefix `00186166...` has no target filename, full digest, or bytes locally.

## Proof gaps

No certificate here proves the full graph's 2943 vertex count, 8422 edge count, triangle-freeness, 7039 maximum cut, 34575 Gamma minimum, 1383-atom row histogram, selected tuple, Hall gap, score 30811, or the 459004 replacement bound. Those require the omitted completion.

## SHA256

- `reconstruct.py`: `6e2fcf3080a0abcc1d2fa40ddf88973faa238f6b2b1fc1a8ae027e87aa5a16bb`
- `known_subgraph.json`: `48aae3f663c342ccd7b72304cb1ce2fbc1243da7ea93dea9403130196ee4cd4a`
- `certificate.json`: `673c6a1c80e5f38cff1136df627291378a1535dc9f5b81beb1116fb937be9c1a`
- R28 source: `819d6a3bb2da534beb7ac86f8b50e9ab936942893671bca12c61e027069e42b9`
- R29 source: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- newest-read `CLAUDE_TO_CODEX.md`: `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`
- circuit helper: `b91da1341cbeb9df28c0c2b270b8be8bc2112c14311cdb61da33fb512a5232bc`
