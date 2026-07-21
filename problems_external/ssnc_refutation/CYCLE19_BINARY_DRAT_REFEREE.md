# Independent binary-DRAT I/O referee

Date: 2026-07-21 (Europe/Istanbul)

Scope: diagnose the 651-byte rejection of the frozen cycle-19 binary proof, build a binary-safe checker from the same frozen `drat-trim.c`, and calibrate positive and negative behavior. Neither CNF nor proof was modified. This report records checker behavior; it does not itself make an UNSAT claim.

## Frozen inputs and original checker

- CNF: 447,305 bytes, SHA-256 `A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38`.
- proof: 380,880,296 bytes, SHA-256 `2BF6C909551EABE4E40A22920EC592900AD20FD3B34B964AD5FC8A77500D48D0`.
- frozen source: 67,265 bytes, SHA-256 `3346DBAFA47541EDFD6C1680C46B545ADBB3FE189C39C5B3C99FE9606553F824`.
- original executable: 518,812 bytes, SHA-256 `5D2FBA5B49CF82D04411CD1A42BAD481AF8777A4F97DD53B22968ABD9D5F52BC`.

The frozen source opens the proof twice with `fopen(argv[2], "r")`. The first byte `0x1A` in the production proof is at zero-based offset 650. On the Windows CRT, the original executable treats this byte as text-mode EOF. Its reported count of 651 consists of the 650 preceding bytes plus the `getc` attempt that returned EOF: `read_lit` increments `nReads` immediately after `getc`.

The original replay exited 1 after reporting:

```text
c finished parsing, read 651 bytes from proof file
c ERROR: no conflict
s NOT VERIFIED
```

## Binary-safe build

The audit copy differs from the frozen source in exactly two lines:

```diff
-        S.proofFile = fopen (argv[2], "r");
+        S.proofFile = fopen (argv[2], "rb");
...
-        S.proofFile = fopen (argv[2], "r");
+        S.proofFile = fopen (argv[2], "rb");
```

No parser, proof rule, clause representation, or verification routine was changed.

- audit source: `engine/tests/drat-trim-binary-safe.c`, 67,267 bytes, SHA-256 `0EDBC9094B10A411E9AAF92AEFAEBD0EE189476546290DF8C1C49D972C5E15A9`;
- compiler: MSYS2 MinGW clang 22.1.4, target `x86_64-w64-windows-gnu`;
- command: `clang -O2 -Dgetc_unlocked=getc -o drat-trim-binary-safe.exe drat-trim-binary-safe.c`;
- executable: 515,336 bytes, SHA-256 `A01C14553C62A772C540BD46EBF1C2C9B90FCFC76F32FA1CD1F72CC2B085F255`.

Compilation exited 0. The upstream source emitted its pre-existing `%li` versus `ptrdiff_t` format warning at line 1275; the binary-I/O patch did not touch that code.

## Binary calibration

The positive CNF is the four-clause inconsistent two-variable pattern on variables 13 and 2. The nine-byte proof is:

```text
61 02 03 00 61 1A 00 61 00
```

It first adds the tautology `(1,-1)`, then the load-bearing unit `(13)`, then the empty clause. The leading binary bytes activate binary parsing before the embedded `0x1A`.

- positive CNF: 43 bytes, SHA-256 `23FE324174768E1350A4B27E3999F9F94DB6329E559459FC97CB6064349C1877`;
- positive proof: 9 bytes, SHA-256 `163FD0A2A0D3A48ADD9B6D58593FFBCA462A8486261A3D67A3FC8FC56B570794`.

```text
original text-mode checker: exit 1, read 6 bytes, s NOT VERIFIED
binary-safe checker:        exit 0, read 9 bytes, s VERIFIED
```

For a semantic negative calibration, the same nine-byte proof was replayed against the corresponding four-clause pattern on variables 12 and 2. Unit 13 is then irrelevant and the proof does not derive the contradiction.

- negative CNF: 43 bytes, SHA-256 `B38B8885679308EC42BEEB7D4176C2E908C488DFF1C876B2AA7AFF44C8790588`.

The binary-safe checker exited 1, read all 9 bytes, and emitted `s NOT VERIFIED`.

## Frozen production replay

The binary-safe checker replayed the unmodified frozen files with:

```text
c finished parsing, read 380880296 bytes from proof file
c detected empty clause; start verification via backward checking
c 29813 of 31275 clauses in core
c 1508656 of 4284781 lemmas in core using 54203683 resolution steps
c 991 RAT lemmas in core; 868188 redundant literals in core lemmas
s VERIFIED
c verification time: 573.864 seconds
```

Process exit was 0. The proof hash after replay remained `2BF6C909551EABE4E40A22920EC592900AD20FD3B34B964AD5FC8A77500D48D0`.

## Diagnosis

**ACCEPT:** Windows text-mode handling of `0x1A` is the sole reproduced cause of the original 651-byte rejection. Changing only the two proof-file open modes from `r` to `rb` changes the production read count from 651 to the exact file length 380,880,296 and removes the rejection. Positive and semantic negative binary calibrations both behave as required.