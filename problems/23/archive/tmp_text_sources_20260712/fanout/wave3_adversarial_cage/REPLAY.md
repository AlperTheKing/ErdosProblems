# Replay

From `E:\Projects\ErdosProblems`:

```powershell
pwsh -File tmp/fanout/wave3_adversarial_cage/replay.ps1
```

The script deterministically regenerates the three supports, exhausts all
rooted degree-five atom selections, rebuilds the small CNFs, emits native LRAT
proofs with CaDiCaL, and runs the independent semantic/LRAT verifier.

The terminal verifier verdict must be:

```text
PASS_ALL_THREE_SUPPORTS_EXCLUDED_BY_STRICT_RELAXATION
```

Direct LRAT replay for one split is:

```powershell
tmp/fanout/r51_independent_t5_verifier/lrat-trim.exe `
  tmp/fanout/wave3_adversarial_cage/small_obstruction_l9_r8.cnf `
  tmp/fanout/wave3_adversarial_cage/small_obstruction_l9_r8.lrat
```

It must print `s VERIFIED`. Replace `l9_r8` by `l10_r7` or `l11_r6` for the
other two supports.

