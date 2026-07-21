# Independent audit of the cycle-19 binary DRAT check

Date: 2026-07-21 (Europe/Istanbul)

Verdict: **VERIFIED**.  The unchanged canonical proof was accepted by an
independently built binary-safe checker with process exit code `0` and the
exact line `s VERIFIED` after all `380,880,296` proof bytes were read.

The earlier `s NOT VERIFIED` result was caused by Windows text-mode I/O
truncation at byte `0x1a`; it was not evidence that the proof was invalid.

## Frozen artifacts

```text
cycle19.cnf
  bytes:   447305
  SHA-256: A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38

proof.drat
  bytes:   380880296
  SHA-256: 2BF6C909551EABE4E40A22920EC592900AD20FD3B34B964AD5FC8A77500D48D0
```

The proof hash was recomputed after verification and was unchanged.  Neither
the CNF nor proof was edited.

## Diagnosis of the old checker failure

Pinned upstream source:

```text
third_party/cadical/test/cnf/drat-trim.c
SHA-256 3346DBAFA47541EDFD6C1680C46B545ADBB3FE189C39C5B3C99FE9606553F824
```

The source opens the DIMACS file with `fopen(argv[1], "r")` and opens the
proof twice with `fopen(argv[2], "r")`.  No `_setmode`, `O_BINARY`, or `"rb"`
operation occurs.  The deployed PE imports `msvcrt.dll`, whose text streams
treat `0x1a` as end-of-file.

The canonical proof has its first `0x1a` at zero-based offset `650`:

```text
offset 636: 92 33 18 03 00 64 CE 33 54 02 00 61 F2 36 1A 00
offset 652: 64 F2 36 1A 03 00 64 AE 37 56 02 00 61 D2 3A 1C
```

The old checker reported `651` reads, then `no conflict` and
`s NOT VERIFIED`.  The one-byte difference is its attempted EOF read.  This
exact alignment identifies text-mode Ctrl-Z truncation.

Old executable hashes were:

```text
third_party/cadical/build/drat-trim.exe
  5D2FBA5B49CF82D04411CD1A42BAD481AF8777A4F97DD53B22968ABD9D5F52BC
engine/tests/audit_drat_trim.exe
  1317EBF80DD38ADA168E0C30FCB2E02993826F44BA10C629026B50C7F087E7E2
```

## Binary-safe remediation

`engine/tests/drat_trim_binary_safe_wrapper.c` includes the pinned upstream
source without changing it.  A local `fopen` wrapper maps read mode `"r"` to
`"rb"` on Windows and leaves every write mode unchanged.

```text
wrapper source SHA-256:
  40A048A2117A8852CFA4312623B6CA8598FA9947F24B7AD98E8F02AD774EA396

GCC 16.1.0 build SHA-256:
  B8BCC01A2753DD658629B35F3654C558043903CD3B60D9A0901124D8178307C7

Clang 22.1.4 build SHA-256:
  1E4C07B45896C4E70A3217ED00639BF358D17A07475DE719EE6A335073D1F6D8
```

Both builds used `-O2 -Dgetc_unlocked=getc`.  The GCC build emitted only
warnings already originating in the pinned upstream file.  The wrapper itself
introduced no compiler diagnostic.

## Calibration matrix

### Positive proof containing a literal `0x1a`

The mapped two-variable contradiction uses variables `13` and `12`.  Its
eight-byte proof is

```text
61 1A 00 61 18 00 61 00
```

with hashes

```text
audit_ctrlz_unsat.cnf
  F16427E6F8E70D1A640872E54773978293AA7C18881ABC1CA269C83FE83FB1AF
audit_ctrlz_unsat.drat
  0B61725600B39838DB988EC4F376E898E3CD6AE92BDBA7803E84EC5CF3B13242
```

Both old checker executables stopped at the Ctrl-Z and exited `80` without
`s VERIFIED`.  Both binary-safe builds read eight bytes, exited `0`, and
printed exactly `s VERIFIED`.

### Ordinary positive and negative controls

```text
nontrivial UNSAT CNF:
  BDCFED14408FB3F368FE82437336D283A9DEDC953677460E9C7317724C5E1E58
valid eight-byte proof:
  6E8F3AA6E5CD1134AC162F6CCD0BE67A9459A4B2FFFE7E618A0A5BA50E0AE807
empty proof:
  E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
corrupted all-deletion proof:
  C7B377137B83B88064C3B8FA49369830485EA5E0D804E8C0DF55A3679F16AB75
```

For both GCC and Clang binary-safe builds:

```text
valid:     exit 0, s VERIFIED
empty:     exit 1, s NOT VERIFIED
corrupted: exit 1, s NOT VERIFIED
```

## Full canonical replay

The GCC binary-safe checker produced:

```text
c finished parsing, read 380880296 bytes from proof file
c detected empty clause; start verification via backward checking
c 29813 of 31275 clauses in core
c 1508656 of 4284781 lemmas in core using 54203683 resolution steps
c 991 RAT lemmas in core; 868188 redundant literals in core lemmas
s VERIFIED
c verification time: 697.877 seconds
```

Process exit code was `0`.  The machine-readable record is
`engine/logs/cycle19-fixed-v1-cadical-20260721T185048/proof_check_binary_safe.json`.

## Classification

The full proof meets both mandatory conditions: checker exit code zero and
the exact verified status line.  It therefore independently establishes
UNSAT of the frozen CNF with hash `A0303301...EA38`.  By the separately
audited encoding bridge, this closes only the fixed `K_19-C_19` equality
cell; it is not a proof of Seymour's conjecture.
