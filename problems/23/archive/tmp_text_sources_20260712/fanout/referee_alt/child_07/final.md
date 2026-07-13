Blocked before file access: the execution host is missing.

Exact failing command:

```powershell
Get-Location
```

Error:

```text
failed to spawn code-mode host E:\Projects\ErdosProblems\tmp\fanout\referee_alt\bin\codex-code-mode-host.exe:
The system cannot find the file specified. (os error 2)
```

The same failure occurred when attempting to read the four mandated context files. Therefore:

- No required files were read.
- No computations or exact-rational tests were run.
- No artifacts were created or modified.
- No SHA256 hashes can be truthfully reported.
- Proof gap: the entire potential-compression question remains unexamined because the evidence and execution environment were inaccessible.