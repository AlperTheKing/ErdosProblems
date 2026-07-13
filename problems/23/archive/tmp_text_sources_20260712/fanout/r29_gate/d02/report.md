# R29 graph-integrity audit (lane d02)

## Verdict

The archived material does not contain a complete 2,943-vertex graph input or a deterministic constructor sufficient to recover every edge. Therefore triangle-freeness and connectivity of the claimed R29 graph are **not verified** in this lane. No triangle or disconnected witness for R29 is asserted, because there is no exact incidence object to test.

## Exact claims checked

`audit_graph.py` independently checks a supplied canonical JSON graph using only integer indices, exact set membership, adjacency intersections, and BFS. It rejects duplicate vertices, loops, unknown endpoints, malformed edges, and duplicate undirected edges. For a valid graph it returns an explicit triangle `(u,v,w)` if one exists and vertices in distinct BFS components if disconnected.

Adversarial self-tests passed exactly:

- input `V={0,1,2}, E={{0,1},{1,2},{0,2}}` returned triangle witness `[0,1,2]`;
- input `V={0,1,2}, E={{0,1}}` returned disconnected witness `[0,2]`.

No floats, `sorry`, `native_decide`, graph libraries, max-cut, Gamma, Hall, Hamming, or optimization code are used.

## Missing input / proof gap

The R29 archive states `N=2943`, `|E|=8422`, aggregate edge-class counts, a six-edge cable, and prose descriptions of traffic, selector, private-C5, and 28/27-circuit pieces. It does **not** specify the full vertex labels and edge incidence, nor enough indexed rules to reconstruct the lock/selector incidences and the 168-vertex circuit exactly. The sibling `d03/gate_maxcut.py` contains only aggregate counts/formulas, not a graph.

Thus the exact unproved claims are:

1. the intended 2,943-vertex incidence object is triangle-free;
2. that incidence object is connected (or whatever connectivity scope was intended).

## Falsifiers

- Triangle-free claim falsifier: any returned `triangle_witness=[u,v,w]`, certifying all three edges `uv`, `vw`, `uw` occur in the hashed input.
- Connectivity claim falsifier: `component_count > 1` and returned `disconnected_witness=[u,v]`, with `u,v` in distinct exact BFS components.
- Audit completeness falsifier: provide a canonical R29 JSON edge list or a fully indexed deterministic constructor. Running `python audit_graph.py INPUT.json` then produces a hashed, witness-bearing verdict; until then, any unconditional R29 verdict exceeds the available evidence.

## SHA-256

- `audit_graph.py`: `ced8237a399ff88ea24c03b9f66b0e29da22f8799686f639eddc8fb64bc65391`
- `hash_evidence.py`: `5dec32036a2813602dc67eb687c6ac7902683d31222776128d1171eb9a197ef1`
- `self_test_output.json`: `cea0861b7acfaa2db92cb56b0ea652f11188fcc41720e20780908eb549c3429e`
- `evidence_hashes.json`: `571a67c47bedd2fd69576ab4de4ce8d2a6cf2d9405642fa6d3ac37c38b0fea63`

Source-input hashes and byte counts are recorded in `evidence_hashes.json`. There is no R29 graph-input hash and no R29 audit-output hash because no graph incidence input exists locally in the searched lane/archive material.
