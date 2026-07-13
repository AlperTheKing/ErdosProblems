Blocked before any command executed: the lane’s code-mode host is missing.

Exact error:

```text
failed to spawn code-mode host E:\Projects\ErdosProblems\tmp\fanout\referee_alt\bin\codex-code-mode-host.exe:
The system cannot find the file specified. (os error 2)
```

Both explicit-workdir and workspace-default invocations failed identically. Consequently:

- No source files were readable.
- No artifacts were written or shared files edited.
- No LP search ran.
- No witnesses, certificates, or SHA256 hashes can honestly be supplied.

Proof gap: the abstract hypotheses and compiled global-min wrapper could not be inspected, so no finite rational encoding or Farkas conclusion was established.