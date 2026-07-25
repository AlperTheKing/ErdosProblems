# Reproducible results

All programs were compiled with MSYS2 `g++ -std=c++20 -O2 -Wall -Wextra
-pedantic` and run single-process.

## Raw verifier calibration

`verify_a.exe fixtures/affine_k25.col`:

```
AUDIT n=25 colors=5 edges=300 sets=177100 failing_sets=0 missing_c0=0 missing_c1=0 missing_c2=0 missing_c3=0 missing_c4=0
VERIFIED
```

The property-corrupted fixture has 73 failing six-sets, first
`0 1 2 3 4 5`, all missing colour 4. The duplicate-edge and loop fixtures
are rejected as format errors.

SHA-256:

```
verify_a.cpp             A7292247DE5FE735CF0022283EFA93A178A295DCA5D33E69A14A1866A8EB47E4
fixtures/affine_k25.col  5FAB4678926AEFB1159A6F46D8A31A5B019DEF2503F96D705256FD7C04C8D51D
```

## Fixed K25 plus one new vertex

The encoder reports:

```
ENCODED vars=125 clauses=12895 exactly_one_atleast=25 exactly_one_atmost=250 five_sets=53130 extension_clauses=12620 symmetry_breakers=0 absent_c0=3125 absent_c1=3125 absent_c2=3125 absent_c3=3125 absent_c4=120
```

The independent clause-multiset auditor reports:

```
CNF_AUDIT_OK vars=125 clauses=12895 exactly_one_atleast=25 exactly_one_atmost=250 extension_clauses=12620 symmetry_breakers=0
```

CaDiCaL 3.0.0 reports `s UNSATISFIABLE`. A first default-binary proof was not
accepted by this build of `drat-trim` and is not used. CaDiCaL was rerun with
`--binary=false --check=1`; independent checking then reports:

```
c 539 of 12895 clauses in core
c 792 of 3783 lemmas in core using 13945 resolution steps
s VERIFIED
```

SHA-256:

```
affine_one_extension.cnf       500D92F8F9544F21BD14F7C0D2E06FDD5FA64617B454825BFE4E529FA1705EE9
affine_one_extension_text.drat 1623674180576B1C1D378C02B5B6A2427B1732925B24FEFD0D01A123DFB5819B
```

This proves only that this fixed merged-direction K25 fixture has no valid
one-vertex extension.

## Seventy-five-free-edge affine family

The encoder and independent transversal-based auditor report:

```
AFFINE_ENCODED vars=375 clauses=16450 exactly_one_atleast=75 exactly_one_atmost=750 five_sets=53130 requirements=15625 symmetry_breakers=0 need_c0=3125 need_c1=3125 need_c2=3125 need_c3=3125 need_c4=3125
AFFINE_CNF_AUDIT_OK vars=375 clauses=16450 exactly_one_atleast=75 exactly_one_atmost=750 requirements=15625 symmetry_breakers=0
```

CaDiCaL 3.0.0 reports `s UNSATISFIABLE`; `drat-trim` reports:

```
c 893 of 16450 clauses in core
c 839 of 4174 lemmas in core using 19364 resolution steps
s VERIFIED
```

SHA-256:

```
affine_family.cnf       498C525D24856E64476828E1D6FDFEA938DC222A48683612713F808D414C9933
affine_family_text.drat B5778FEC15F5FBA4FBD03A8FA07E5E3F30BECF625DD9CF760782AF05EE2583DE
```

`AFFINE_FAMILY_UNSAT.md` gives a non-computational proof of the same
restricted-family obstruction. Neither result excludes arbitrary
five-colourings of `K_26`.
