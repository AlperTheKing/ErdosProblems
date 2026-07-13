# R51 rooted t=5 catalogue audit

Date: 2026-07-12

## Scope and inputs

Audited as a proposed proof certificate, not as a falsifier search:

- `tmp/fanout/r42_graph_specific_exclusion/rooted_t5_support_cp_sat.py`
  - 1,267 lines, 51,256 bytes
  - SHA256 `DFD060BD1955E7FDA6982958F40FDB70A1504A49827A7DD1EFAA77E89DF03053`
- `problems/23/writeup/WALL_ATTACK_R51_GPTPRO56.md`
- `problems/23/writeup/WALL_ATTACK_R50_GPTPRO56.md`, only to recover the stated 56-split index set
- all 18 files matching
  `tmp/fanout/r42_graph_specific_exclusion/t5_solo_*.json`

All 18 embedded `canonicalSha256` values replay correctly using the driver's
canonical JSON algorithm. This checks payload integrity only. It does not bind
the payload to the driver, an encoded SAT/PB model, a solver build, or a proof
trace.

## Verdict

The current `t5_solo` outputs are **search telemetry, not a proof catalogue**.

- The mathematically reduced rooted split universe is **49**, not 56, provided
  two missing range/root lemmas are proved and connected.
- R50/R51's **56** is the unreduced range `n=15..21`, `left=6..n-5`.
- The driver accepts only `left>=7`, giving 49 executable splits. Its input
  check is not itself a proof that the seven `left=6` bins are empty.
- Of the 49 executable splits, 18 have `t5_solo` files: 15 report outer-support
  `INFEASIBLE`, three report `LIMIT_REACHED`, and 31 have no solo artifact.
- None of the 49 splits is theorem-grade closed yet: no split has a checked
  parent relation, a proof-producing exhaustion trace, and the R51 profile and
  production-extension bundle.
- `LIMIT_REACHED` plus no hit never certifies a split as emitted.

## 1. Exact split universe: raw 56, reduced 49

R50 declares

```text
n = 15,...,21,   left = 6,...,n-5,   right = n-left.
```

Its size is

```text
5 + 6 + 7 + 8 + 9 + 10 + 11 = 56.
```

The driver rejects `left<7` at lines 64-65 and requires `right>=5`. Thus its
actual executable domain is

```text
n = 15,...,21,   left = 7,...,n-5,   right = n-left,
```

of size

```text
4 + 5 + 6 + 7 + 8 + 9 + 10 = 49.
```

The seven removed bins are

```text
(left,right) = (6,9),(6,10),(6,11),(6,12),(6,13),(6,14),(6,15).
```

### Why `left>=7` is valid, but still needs a theorem

In the rooted object, `v` and `m` are distinct vertices on the owner shore and
share blue neighbours `x` and `y`. Hence their blue distance is two, so `vm`
cannot be one of the selected t=5 bad atoms, whose endpoints have blue distance
four. Since `v` has five distinct selected bad neighbours on its own shore and
none is `m`, that shore contains `v`, `m`, and at least five further vertices.
Therefore `left>=7`.

This argument should become a compiled lemma, for example

```text
RootedT5Circuit.ownerShore_card_ge_seven
```

and the catalogue index type should use 49 bins. Alternatively, retain all 56
raw bins and attach a checked empty-bin proof to each `left=6` entry. A Python
`ValueError` is not an empty-bin certificate.

### The order range is also external to the driver

The driver itself permits `left+right<=24`. The restriction `15<=n<=21` comes
from the R49 prose lemma `t5_localProfile_supportOrder_ge_fifteen` plus an upper
order argument. No implementation of that lemma, `RootedT5Circuit`,
`RootedT5Iso`, or `checkedRootedT5Catalogue_complete` exists in the current Lean
tree; exact-name search finds them only in R50/R51 prose and the mailbox.

Therefore **49 is the correct target only conditional on compiled proofs that
every production t=5 rotor roots into an object with `15<=n<=21` and
`left>=7`, `right>=5`**. Without those proofs the catalogue domain itself is
not certified.

## 2. What each solver status actually means

### Outer support loop

The outer loop is at lines 1179-1257.

1. CP-SAT solves the rooted support formula.
2. A feasible support is converted to a graph and sent to the circuit/profile
   solver.
3. The exact labelled support is blocked unconditionally at lines 1251-1255.
4. A subsequent outer `INFEASIBLE` means no unblocked support assignment remains.
5. Reaching the loop bound executes the `for ... else` branch and writes
   `LIMIT_REACHED`; there is no final exhaustion solve.

### Is `supportTerminalStatus=INFEASIBLE` exhaustive?

**Relative to the encoded outer CP-SAT formula, yes only under additional
conditions. As a theorem certificate, no.**

For the 15 current solo files with `INFEASIBLE`, `supportsSolved=0`. Thus the
first outer solve declared the support formula unsatisfiable; no unconditional
blockers were involved. Trusting OR-Tools and the current model semantics, each
of those is a complete no-support result for that labelled split.

For a future file with `supportsSolved>0`, the status alone is insufficient.
The driver blocks a support even when the circuit result is `UNKNOWN`,
`MODEL_INVALID`, `ACTIVE_SCOPE_UNKNOWN`, `CUT_UNKNOWN`, or another
non-conclusive status. Therefore outer exhaustion can hide an unresolved
support. Such a split closes only if every prior support has a checked terminal
certificate and the final support formula has a checked UNSAT certificate.

Even in the zero-support case, the current JSON records only the string
`INFEASIBLE`. OR-Tools CP-SAT emits no independently checked LRAT/PB proof here,
and the repository contains no negative-result verifier. This is solver-relative
evidence, not kernel evidence.

### Can `LIMIT_REACHED` no-hit certify a split?

**No.** The loop stops immediately after processing support number 3,000 and
never asks whether a 3,001st support exists. The three current files therefore
say only that their first 3,000 solver-order supports had no accepted hit.

An independent theorem that exactly 3,000 supports exist could separately make
those runs exhaustive, but no such theorem or count certificate is present. In
that situation the correct implementation should perform one final solve and
obtain checked `INFEASIBLE`; `LIMIT_REACHED` itself remains non-certifying.

### Circuit/profile statuses

The same distinction recurs inside `choose_minimal_circuit`:

- `INFEASIBLE` is conclusive only relative to that CP-SAT model.
- `INFEASIBLE_AFTER_k_SCOPE_REJECTIONS` additionally depends on `k` separate
  active-scope UNSAT results and a final circuit UNSAT result.
- any `UNKNOWN`, `MODEL_INVALID`, or time-limit result is unresolved.
- the current outer loop does not enforce an allow-list of certifying statuses.

R51 must therefore reject a split manifest containing any unproved status, not
merely inspect its final outer status.

## 3. Current `t5_solo` inventory

All 18 files use:

```text
localClassifier = v
requireActiveScope = true
requireSharedBadNeighbour = false
requireBadTriangleFree = true
requireDeletionSdr = true
selectedAtomCount = 25
ownerBadDegree = 5
supportMinMultiplicity = 2
workers = 8
supportLimit = 3000
```

`hash` below is the first 12 hex digits of the embedded canonical payload hash,
not the SHA256 of the formatted file bytes.

| n | left | right | supports | terminal | circuit summary | hash |
|---:|---:|---:|---:|---|---|---|
| 15 | 7 | 8 | 0 | INFEASIBLE | none | `14ac9d93df5b` |
| 15 | 8 | 7 | 0 | INFEASIBLE | none | `8d194613f110` |
| 15 | 9 | 6 | 0 | INFEASIBLE | none | `66e0813cffb8` |
| 15 | 10 | 5 | 0 | INFEASIBLE | none | `5721cbc543b4` |
| 16 | 7 | 9 | 0 | INFEASIBLE | none | `8dff49eae32a` |
| 16 | 8 | 8 | 0 | INFEASIBLE | none | `bd0c032079de` |
| 16 | 9 | 7 | 0 | INFEASIBLE | none | `cc5462d6c4b8` |
| 16 | 10 | 6 | 0 | INFEASIBLE | none | `b5037e11ada7` |
| 16 | 11 | 5 | 0 | INFEASIBLE | none | `9f9401d07b51` |
| 17 | 7 | 10 | 0 | INFEASIBLE | none | `4d450ca0f315` |
| 17 | 8 | 9 | 0 | INFEASIBLE | none | `f76b9d64758e` |
| 17 | 9 | 8 | 3000 | LIMIT_REACHED | 3000 circuit INFEASIBLE | `95dbc901f9f3` |
| 17 | 10 | 7 | 3000 | LIMIT_REACHED | 2996 INFEASIBLE; 4 after one scope rejection | `d612c59eb1cf` |
| 17 | 11 | 6 | 3000 | LIMIT_REACHED | 3000 circuit INFEASIBLE | `31d82c62689c` |
| 17 | 12 | 5 | 0 | INFEASIBLE | none | `325012ec5ba8` |
| 18 | 7 | 11 | 0 | INFEASIBLE | none | `daf2d151fb7d` |
| 18 | 8 | 10 | 0 | INFEASIBLE | none | `27263655e20b` |
| 18 | 13 | 5 | 0 | INFEASIBLE | none | `574b5cbc0511` |

Missing solo files in the 49-bin domain:

```text
n=18: (9,9),(10,8),(11,7),(12,6)                         4
n=19: (7,12)..(14,5)                                    8
n=20: (7,13)..(15,5)                                    9
n=21: (7,14)..(16,5)                                   10
total                                                   31
```

Current search-level accounting is therefore:

```text
49 reduced bins = 15 outer-UNSAT claims + 3 bounded no-hit runs + 31 absent.
```

There are additional `t5_codex_*` files in the directory, but they are not
members of the requested solo set and do not repair the certificate-layer gaps
described here.

## 4. Artifact integrity gaps

The current solo JSON files omit all of the following:

- driver/source SHA and generated model SHA;
- full command line;
- `support-time` and `circuit-time` values;
- Python, OR-Tools, and NetworkX versions;
- solver response statistics and numeric status code;
- the support models encountered;
- per-support circuit/profile result records;
- active-scope rejection records;
- UNSAT proof traces;
- a final parent-cover proof;
- a byte-level artifact SHA manifest.

The current environment is Python 3.12.4, OR-Tools 9.14.6206, and NetworkX
3.6.1, but the JSON files do not establish that these exact builds produced
them. Filesystem times show the current driver predates the solo files, but that
is not a cryptographic provenance relation.

The driver's `verify_hit` checks positive witnesses only: atom count,
triangle-freeness, support multiplicity, and deletion SDRs. There is no
corresponding checker for negative results. The embedded canonical hash detects
payload mutation but proves no mathematical assertion.

## 5. Per-split theorem-grade artifact contract

A split may be marked `CLOSED` only when all applicable items below pass.

### A. Global domain and parent relation

1. Compiled `15<=supportOrder<=21` theorem.
2. Compiled `ownerShore.card>=7` and opposite-shore `card>=5` theorems.
3. A finite 49-bin index type, or 56 raw bins with seven checked empty entries.
4. `RootedT5Circuit` and `RootedT5Iso` definitions matching the production
   graph semantics.
5. A checked rooting/canonicalization theorem mapping every production t=5
   rotor to one split and one catalogue parent while preserving support,
   complete shortest-row families, selected atoms, shores, owner, and active
   neighbour.
6. A proof that degree-order symmetry constraints at driver lines 268-276 lose
   no rooted isomorphism class.
7. A separate k=3 reduction to the same rooted catalogue, or a separate checked
   k=3 catalogue. The current driver is a two-owner k=2 model.

### B. Support-level closure for each split

Each split needs a versioned manifest containing the exact generator SHA,
model SHA, flags, tool versions, and byte hashes, plus one of:

- an exact CNF/OPB encoding and independently checked LRAT/VeriPB UNSAT proof
  that no support exists; or
- a complete canonical support list, a checked witness for every listed
  support, and a final checked UNSAT proof after blocking exactly that list.

The encoding-to-`RootedT5Circuit` semantics must be proved. CP-SAT's status
string is not an accepted replacement.

### C. Circuit-level closure for every listed support

For each support:

1. checked bipartiteness, connectivity, 24-edge count, rooted edges, and owner
   blue degrees;
2. a complete atom database: every same-shore pair at blue distance exactly
   four and **all** shortest length-four rows, with a completeness checker;
3. either a complete list of 25-atom circuits or a checked circuit UNSAT proof;
4. for every listed circuit, checked triangle-freeness, footprint union,
   multiplicity, owner bad degree, and all 25 deletion-SDR witnesses;
5. no unresolved solver status.

### D. Profile and active-scope closure

For each circuit:

1. complete `T5ProfileKey` list, not one solver-selected profile;
2. checked four-number classifier and matching witnesses;
3. for every rejected active-scope candidate, an explicit separator or checked
   CNF/PB UNSAT proof;
4. for `INFEASIBLE_AFTER_k_SCOPE_REJECTIONS`, all `k` rejection proofs plus the
   final blocked-model UNSAT proof;
5. a theorem that rooting one profile owner as `v` makes `localClassifier=v`
   exhaustive.

### E. Production-extension closure

Intrinsic scope-vacuity is preprocessing only. Every zero-vector profile must
also carry the R51 production bundle:

- `CheckedT5IntrinsicCert` where applicable;
- all canonical `T5AmbientSplit` cases;
- for each split, either `CheckedWeightedSwitchCapacity` or a checked LRAT/PB
  extension-UNSAT proof;
- `checkedT5ExtensionUnsat_sound` connecting those certificates to the real
  production extension.

### F. Aggregate and kernel consumer

The per-split manifest must define and list, rather than merely report, the
sets counted by:

```text
G = canonical rooted supports
C = checked minimal 25/24 circuits
P = complete profile keys
A = profiles surviving intrinsic and production-extension checks
```

`A=0` is accepted only after the lists and their completeness proofs check.
Finally, `CheckedT5CatalogueBundle` and
`no_t5_balancedDeficiencyRotor_of_catalogue` must compile from these artifacts
with no `sorry`, `admit`, `native_decide`, or axioms beyond `propext`,
`Classical.choice`, and `Quot.sound`.

## 6. Concrete corrections to the current workflow

1. Rename `NO_HIT_WITHIN_EXPLICIT_LIMIT` into status classes that cannot be
   mistaken for proof:
   - `PARTIAL_LIMIT_NO_HIT`
   - `UNRESOLVED_SOLVER_STATUS`
   - `EXHAUSTED_RELATIVE_TO_MODEL`
   - `CHECKED_CLOSED`
2. Never block a support after `UNKNOWN`, `MODEL_INVALID`, or another
   non-certifying circuit/scope result.
3. After processing the nominal support limit, perform one additional solve.
   Only a checked UNSAT result may convert the run from partial to exhaustive.
4. Emit one record per support and per scope rejection; aggregate status maps
   are insufficient for replay.
5. Bind every result to driver SHA, encoded-model SHA, exact flags, solver
   versions, proof-file SHA, and byte-level artifact SHA.
6. Replace CP-SAT-only negative claims with proof-producing CNF/PB encodings or
   a kernel-checked finite certificate.
7. Correct the headline from “56-split closure” to either:
   - “49 rooted splits, plus a compiled seven-bin `left=6` exclusion”; or
   - “56 raw splits, seven closed structurally.”
8. Do not count the three `LIMIT_REACHED` files as closed. Deepening 3,000 to
   30,000 remains search, not certification.

## Final acceptance state

```text
Raw R50 index bins:                         56
Structurally empty left=6 bins:              7  (prose proof only)
Reduced target bins:                        49
Solo artifacts present:                     18
Outer-support INFEASIBLE, zero supports:    15  (solver-relative only)
LIMIT_REACHED no-hit:                        3  (non-certifying)
Reduced bins with no solo artifact:         31
Bins closed by theorem-grade catalogue:      0
```

The current data is useful: it identifies 15 likely empty support strata and
three feasibility-frontier strata. It does not yet establish catalogue
completeness or the t=5 theorem.
