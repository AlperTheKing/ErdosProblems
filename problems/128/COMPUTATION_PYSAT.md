# Erdős Problem 128 — Independent PySAT wave

## Scope

This is the single permitted PySAT/PB wave for the direct n=20 certificate
route. It did not search any other graph order and it used no labelling
symmetry breaking.

A witness would be a triangle-free graph on 20 labelled vertices for which
every one of the C(20,10)=184756 induced ten-vertex subgraphs has at least 9
edges.

## Exact formulation

The 190 possible edges are Boolean variables.

- Every one of the C(20,3)=1140 triples has the exact triangle clause
  (not e_ij) OR (not e_ik) OR (not e_jk).
- Every vertex has degree at most 9. This is necessary because a 10-vertex
  neighbourhood is independent in a triangle-free graph.
- For every vertex v, e(G-v) >= 35, as proved in SEARCH_LEMMAS.md; also
  e(G) >= 39.
- Five workers used incremental exact CEGIS. Each SAT model was audited by
  enumerating all 184756 ten-sets, and every generated cut was the exact
  constraint sum_{ij in C(S,2)} e_ij >= 9 for a genuinely violating ten-set.
- One MiniCard worker loaded all 184756 ten-set constraints before its first
  solve.
- Five workers required maximal triangle-freeness via exact common-neighbour
  auxiliary variables. This is lossless by SEARCH_LEMMAS.md, Lemma 3.
  One CaDiCaL worker omitted this restriction. No other restriction was used.

For MiniCard, at-least-b was encoded natively as at-most-(r-b) on the negated
literals. For CaDiCaL 1.9.5 and Glucose 4.2 backends, PySAT sequential counter
CNF encodings were used.

## Software and command

- Python: 3.12.4
- python-sat: 1.8.dev24
- backends: MiniCard, CaDiCaL 1.9.5, Glucose 4.2
- workers: 6
- declared cap: 6 CPU workers, 8 GB aggregate RAM, 590 seconds wall time
- observed runner wall time: 590.094 seconds

Command:

    python problems/128/search/pysat_wave_128.py --wall-limit 590 --worker-limit 570 --output-dir problems/128/search/pysat_wave_20260713

## Exact outcome

| worker | formulation | models audited | exact cuts loaded | best ten-set minimum | fewest violations | terminal state |
|---|---|---:|---:|---:|---:|---|
| w0 MiniCard seed 11 | all 184756 constraints | 0 | 184756 | — | — | UNKNOWN |
| w1 MiniCard seed 23 | CEGIS, maximal | 55 | 195 | 5 | 77 | killed at outer wall cap |
| w2 MiniCard seed 37 | CEGIS, maximal | 86 | 23434 | 5 | 33 | UNKNOWN |
| w3 CaDiCaL seed 53 | CEGIS, maximal | 755 | 1830 | 6 | 33 | UNKNOWN |
| w4 CaDiCaL seed 71 | CEGIS, nonmaximal allowed | 79 | 13708 | 5 | 33 | UNKNOWN |
| w5 Glucose seed 89 | CEGIS, maximal | 363 | 1742 | 6 | 183 | UNKNOWN |

No candidate file was produced. The w1 return code 1 in the runner summary is
the result of outer-process termination after it stopped emitting models; its
log contains no UNSAT record. It is not an UNSAT result. CaDiCaL reported that
its in-process limited-solve interrupt is unsupported; the outer 590-second
runner supplied the hard wall stop.

Thus this wave gives neither a counterexample nor an infeasibility
certificate. It does not settle the n=20 instance or Problem 128, and no
negative claim follows.

## Artifacts and SHA-256

- pysat_wave_summary.json:
  EAA197E10B48574C4B870270BBF93348F23C0CC691B60173D3FD0681AC6FFC54
- pysat_cegis_128.py:
  7C2146A6625B7EAECE71D7A8988A007AB8C62918E8A763ACEB706E1BB8DEF403
- pysat_verify_128.py:
  B50B87D3AB6E5CD7E692847457E6546FDDBA52AF681815EF477D886EC9D0C034
- pysat_wave_128.py:
  C8F783E6DDF6CA214E9758DDD3E39CB4AFBB0A6388275CBEFD4670B9761ACEEA
- w0 log:
  D00875F7DF33102C9A401536DC5CE186BA59A7F113F915DAB250A5496E561902
- w1 log:
  0CDFC0C6033F84AD8943517B04C6EC3A72805784FBE201B8906CE8346579DDF8
- w2 log:
  6A12841AB3B937EF05B95B1CADD5E21FE134C9383F3AB454F93E0F7C2A4111C7
- w3 log:
  6E9F7171017E920826030403A91D9886B548D910C7518DE4B59F18C5670856D1
- w4 log:
  175FC73D20D41132A13BE55624F04096547B687492A4BE10FE27CAB96238E3EF
- w5 log:
  F794DEB297DD6A8C31C0228D29CDB12B737F1C059B163C1694958915B1604657

The standalone verifier was syntax-checked but was not run on a certificate,
because no candidate exists.

