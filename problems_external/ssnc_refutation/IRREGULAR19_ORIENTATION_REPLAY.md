# Strict replay of the frozen irregular orientation

Date: 2026-07-21 (Europe/Istanbul)

Status: **VALID ORIENTED GRAPH; REJECTED AS AN SSNC COUNTEREXAMPLE BY BOTH INDEPENDENT VERIFIERS**.

## Canonical certificate

`IRREGULAR19_ORIENTATION_CERTIFICATE.json` contains exactly the two permitted top-level keys `{n,out_neighbors}`. It was extracted without changing any adjacency row from `IRREGULAR19_INCIDENCE_SEED.json`.

- certificate: 1,716 bytes, SHA-256 `0292CF5A7757F0009627E43DC4B302AE39CE5B196C6CE42C760D325F56D6D826`;
- vertices: 19;
- arcs: 152;
- outdegree: 8 at all 19 vertices;
- loops: 0;
- digons: 0.

## Scalar-set replay

Verifier: `engine/verify_scalar.py`, 9,193 bytes, SHA-256 `71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443`.

Result:

```text
exit = 1
status = VALID_GRAPH_NOT_COUNTEREXAMPLE
failing_vertices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
errors = []
```

Exact stdout ledger: `IRREGULAR19_ORIENTATION_SCALAR_LEDGER.json`, 2,332 bytes, SHA-256 `7D98C4C33BCFFE23FFD8E31396724A6DC3065F8D89DCDBA5CC778E693A2BF9DB`.

Stderr is empty, SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

## C++ bitset replay

Verifier executable: `engine/verify_bitset.exe`, 190,590 bytes, SHA-256 `E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC`.

Its independent source is `engine/verify_bitset.cpp`, 16,190 bytes, SHA-256 `A015E32A360A57C5652B01FBCC06775A19A50A11271CF1D72C8B201A103ED672`.

Result:

```text
exit = 1
status = VALID_GRAPH_NOT_COUNTEREXAMPLE
failing_vertices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
errors = []
```

Exact stdout ledger: `IRREGULAR19_ORIENTATION_BITSET_LEDGER.json`, 2,332 bytes, SHA-256 `9691C3AC03E04F46DA493AD3FE13E2C615B045AA3D5DDB9D782417FEE887B2FC`.

Stderr is empty, SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

## Ledger agreement and rejection

The two ledger files have different byte hashes because the independent implementations serialize object keys in different orders. Parsing them as JSON gives exactly equal objects, including all 19 per-vertex neighbour sets.

Both verifiers independently return, for every vertex,

```text
d1 = 8
d2 = 10
strict_d2_lt_d1 = false
```

Thus all 19 vertices fail the strict counterexample predicate. The complete `n1` and `n2_new` sets are preserved in both exact ledger files. The orientation is accepted as a valid oriented graph but is not an SSNC counterexample.

No search, reorientation, or incidence change was performed in this replay.