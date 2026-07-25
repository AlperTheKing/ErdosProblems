# Codimension-three checker supersession

The publication-grade local checker is
`uniform_codim3_local_certificate.py`, with the boundary-preserving capture
bound **21** proved in its module documentation and in
`UNIFORM_CODIM3_BV_REPORT.md`.

The files `uniform_codim3_local_classify.py` and
`uniform_codim3_local_classify_v2.py` are preliminary development probes. Their
earlier bound 18 removed every empty strip all the way to the boundary and did
not explicitly preserve the interior/boundary status of the nearest stencil
vertices. They are retained only because the canonical checker imports their
low-level enumeration helpers. Do not cite their stated capture bound or their
standalone `status` field.

The corrected canonical run keeps one strip next to every previously untouched
side, giving the rigorous bound `3*(6+1)=21`. It returns:

```text
connected_rank3_triples_checked = 761329
index_histogram = {1: 760527, 2: 801, 4: 1}
violations = []
sha256_canonical_types = 27b0da1c9889576779c4e7d1939243b748f16062bc16c227f104adea343cf92d
status = PASS
```
