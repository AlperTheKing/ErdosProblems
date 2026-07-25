# Erdős 742: SAT Modulo Symmetries route audit

Date: 2026-07-23

## Verdict

- **Toolchain and encoding: GO.** The current official SMS source builds locally,
  the public `--diam2-critical` encoding is present, and both SAT and UNSAT
  small calibrations behaved correctly.
- **Order-25 production now: NO-GO.** The route is mathematically sound, but the
  published computation already required 50,054 degree-sequence cases and 23.7
  accumulated CPU-days at order 19. There is no evidence that the unrestricted
  order-25 instance is an hours-scale search. No order-25 solver was launched.
- **Unchecked first-pass UNSAT is not a certificate.** The current solver's
  direct LRAT output does not include a dynamically learned symmetry clause as
  an independently checkable premise. Certification requires the documented
  two-pass workflow below.

## Frozen source and build

- SMS repository: <https://github.com/markirch/sat-modulo-symmetries>
- SMS commit: `464f12f1fd36b496e7ba9dcbb622b079de02dce4`
- bundled `cadical_sms` commit:
  `b023aaf059babf867a7fdfc5fb342d52ffbccb25`
- `smsg.exe` SHA-256:
  `5347C3DCD5A154A652543A53E104AF49E8DE728FFC5D1C59284DB455B2DC2B37`
- The source was not changed. On MinGW, compilation required the build-only
  definition `-Drandom=rand`; the official documentation supports Linux only.

The public builder implements `--diam2-critical` in
`pysms/graph_builder.py::diameter2critical`.

## Small calibration

The encoding and solver were calibrated at order 5.

1. `n=5`, exactly 6 edges: SAT (exit 10), returning
   `[(0,3),(0,4),(1,3),(1,4),(2,3),(2,4)]`, i.e. `K_{3,2}`.
2. `n=5`, at least 7 edges: UNSAT (exit 20).
3. A two-pass LRAT certificate for case 2 was accepted by the independent
   `lrat-check` implementation from
   <https://github.com/marijnheule/drat-trim>, commit
   `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, exit 0 (`c VERIFIED`).

Calibration artifacts:

- `d2c_n5_e6.cnf`
- `d2c_n5_ge7.cnf`
- `d2c_n5_ge7_sym.json`
- `d2c_n5_ge7_augmented.cnf`
- `d2c_n5_ge7_static.lrat`
- `check_and_augment_sms.py`

The verified LRAT has SHA-256
`3B07E128F64E63413246954FB18E6BDCD2672C800E66FE6D57888E3CAEBEA923`.

## Exact order-25 instance

Generate the direct counterexample instance:

```powershell
$repo = (Resolve-Path .\sat-modulo-symmetries).Path
$env:PYTHONPATH = $repo
python -m pysms.graph_builder `
  --vertices 25 `
  --diam2-critical `
  --num-edges-low 157 `
  --no-solve `
  --cnf-file .\d2c_n25_ge157.cnf `
  --DEBUG 0
```

The generated formula is:

```text
p cnf 68400 547030
```

File size: 9,419,626 bytes.

SHA-256:
`A15E1616E221496C91CFC8BCAC1FD9AA68ACA465A073227481D4D4FD1E7DDFFB`.

The exact first-pass SMS search command corresponding to the paper's D2C
settings (frequency `1/20`, cutoff `20000`) is:

```powershell
.\sat-modulo-symmetries\build-mingw\src\smsg.exe `
  -v 25 `
  --frequency 20 `
  --cutoff 20000 `
  --sym-break-clauses .\d2c_n25_ge157_sym.json `
  --dimacs .\d2c_n25_ge157.cnf
```

This command stops at the first SAT graph by default. Any printed graph must
still be replayed by the two independent D2C adjacency verifiers specified in
the main registry.

## Certificate limitation and sound UNSAT procedure

The thesis specifies this proof workflow:

1. run SMS and record every dynamic symmetry-breaking clause together with its
   witnessing permutation;
2. independently validate those permutation witnesses;
3. add the validated clauses to the original CNF;
4. run a proof-producing SAT solver without dynamic SMS; and
5. independently check the resulting DRAT/LRAT proof.

The current checkout has two interface problems:

- `--sym-break-clauses` writes JSON, but the bundled
  `pysms/sym_clause_checker.py` still parses the former semicolon text format
  and exits with `IndexError` on current output.
- A direct first-pass `--lrat-output` trace failed independent checking in the
  calibration because hint clause 715, the dynamic symmetry clause, was absent
  from the proof premises.

`check_and_augment_sms.py` is a local compatibility adapter. It validates the
current JSON witnesses against the row-major lexicographic edge ordering and
creates a static augmented DIMACS. The calibrated second pass was:

```powershell
python .\check_and_augment_sms.py `
  --vertices 5 `
  --cnf .\d2c_n5_ge7.cnf `
  --sym-json .\d2c_n5_ge7_sym.json `
  --output .\d2c_n5_ge7_augmented.cnf

.\sat-modulo-symmetries\build-mingw\src\smsg.exe `
  -v 5 `
  --no-SMS `
  --cadical-config binary=false `
  --lrat-output .\d2c_n5_ge7_static.lrat `
  --dimacs .\d2c_n5_ge7_augmented.cnf

.\drat-trim\lrat-check.exe `
  .\d2c_n5_ge7_augmented.cnf `
  .\d2c_n5_ge7_static.lrat
```

This ended with `c VERIFIED` and checker exit 0.

## Scaling evidence

The 2023 thesis reports that the strongest D2C computation did not use a
single unrestricted instance. It split the search by degree combinations,
using Fan's square-degree inequality and the maximum-degree theorem. At
`n=19`, it used 50,054 combinations, 23.7 accumulated CPU-days, and a maximum
of 312 seconds for one combination.

A local exact C++ count using only the stated necessary numeric restrictions
for a strict `n=25` counterexample found 3,836,501 nondecreasing graphical
degree sequences. This is only a scale diagnostic, not a lower bound on
runtime and not a mathematical result about existence.

The current public PySMS CLI does not provide a turnkey exact degree-sequence
driver matching the published split. Its `--static-partition
--degree-partition` path attempts to forward the unsupported option
`--combine-static-dynamic` to the current `smsg`. Reproducing the published
high-order strategy therefore requires an audited custom degree-sequence
encoder/launcher before any production allocation.

## Sources

- Official documentation:
  <https://sat-modulo-symmetries.readthedocs.io/en/latest/>
- Markus Kirchweger, *Dynamic Symmetry Breaking for SAT-Encodings of
  Combinatorial Problems* (2023):
  <https://repositum.tuwien.at/handle/20.500.12708/177268>
- Markus Kirchweger and Stefan Szeider, *SAT Modulo Symmetries for Graph
  Generation and Enumeration* (2024):
  <https://doi.org/10.1145/3670405>
