# Lean build/probe report

## Repository toolchain and project root

- Lake project root: `E:\Projects\ErdosProblems\formal-conjectures`
- Toolchain file: `E:\Projects\ErdosProblems\formal-conjectures\lean-toolchain`
- Toolchain file contents: `leanprover/lean4:v4.27.0`
- Lake manifest/config: `E:\Projects\ErdosProblems\formal-conjectures\lakefile.toml`
- Erdős 23 module root added through `LEAN_PATH`: `E:\Projects\ErdosProblems\problems\23\lean`
- Existing compatible `.olean` cache used for the successful read-only probes: `E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1`

Exact version command, run from `E:\Projects\ErdosProblems\formal-conjectures`:

```powershell
lake env lean --version; "EXIT=$LASTEXITCODE"
```

Exact result (exit code 0, 19.6 s):

```text
Lean (version 4.27.0, x86_64-w64-windows-gnu, commit db93fe1608548721853390a10cd40580fe7d22ae, Release)
EXIT=0
```

## Minimal imports and namespaced probes

### `FullBankRelaxedCoverCert`

Minimal direct import:

```lean
import Erdos23Delta0.Ell5FullBankInterface
```

Fully qualified name:

```lean
Erdos23Delta0.Ell5FullBankInterface.FullBankRelaxedCoverCert
```

Exact successful read-only stdin build/probe, run from `E:\Projects\ErdosProblems\formal-conjectures`:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1;E:\Projects\ErdosProblems\problems\23\lean'; @'
import Erdos23Delta0.Ell5FullBankInterface
#check Erdos23Delta0.Ell5FullBankInterface.FullBankRelaxedCoverCert
'@ | lake env lean --stdin; "EXIT=$LASTEXITCODE"
```

Exact result (exit code 0, 50.9 s):

```text
Erdos23Delta0.Ell5FullBankInterface.FullBankRelaxedCoverCert.{u_1, u_2, u_3, u_4} {R : Type u_1} {E : Type u_2}
  {JT : Type u_3} {ι : Type u_4} [DecidableEq R] [DecidableEq E] (S : Finset R) (F O : Finset E) (J : Finset JT)
  (K : Finset ι) (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ) :
  Type (max (max u_2 u_3) u_4)
EXIT=0
```

### `FullBankGlobalPackage.Checked`

Minimal direct import:

```lean
import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge
```

Fully qualified name:

```lean
Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked
```

Exact successful read-only stdin build/probe, run from `E:\Projects\ErdosProblems\formal-conjectures`:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1;E:\Projects\ErdosProblems\problems\23\lean'; @'
import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge
#check Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked
'@ | lake env lean --stdin; "EXIT=$LASTEXITCODE"
```

Exact result (exit code 0, 52.6 s):

```text
Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked {G : Erdos23Delta0.CertGraph.GraphData}
  {c : Erdos23Delta0.CertGraph.CutData} {rows : Erdos23Delta0.CertGraph.RowDB}
  (P : Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows) : Prop
EXIT=0
```

## Source-file build form

For a probe saved as `<probe.lean>`, the corresponding repo build command is:

```powershell
Set-Location E:\Projects\ErdosProblems\formal-conjectures
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1;E:\Projects\ErdosProblems\problems\23\lean'
lake env lean <probe.lean>
```

The stdin form above is the tested no-probe-file equivalent.

## Timed-out checks

Two earlier combined stdin attempts were terminated by the command runner after approximately 124 s (exit code 124): one with `LEAN_PATH` set only to `E:\Projects\ErdosProblems\problems\23\lean`, and one with the cache-prepended `LEAN_PATH`. Because each command contained both probes sequentially and emitted no output before termination, neither timeout establishes which probe was active or whether elaboration had failed. The separate cache-backed commands above are the definitive checks and both exited 0.
