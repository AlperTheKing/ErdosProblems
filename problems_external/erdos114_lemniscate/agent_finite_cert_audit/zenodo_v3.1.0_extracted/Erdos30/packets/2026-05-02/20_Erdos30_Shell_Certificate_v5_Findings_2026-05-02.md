# Erdos #30 Shell Certificate v5 Findings

Date: 2026-05-02

## Bottom Line

The first finite shell-graph certificate is complete.

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: finite shell-geometry certificate only
```

Target shell:

```text
k = 10
D = 60
D* = 55
shell delta = 5
```

## New Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_shell_certificate.py

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_certificate_k10_D60_v5_RESULTS.json

report:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_certificate_k10_D60_v5_REPORT.md

result_sha256:
569d7c427214b3f5c25874fd5a3d590dfc92c67ce6775e170da10adbbf0f7809
```

## Certificate Result

The shell has:

```text
V = 14 vertices
E = 0 accepted one-mark edges
components = 14
Laplacian zero modes = 14
```

The script checked:

```text
candidate one-mark moves: 448
accepted moves: 0
order violations: 38
repeated-difference collision witnesses: 410
valid candidate missing from shell: 0
```

So this is no longer just a graph statistic. It is a complete finite rejection
certificate for every local one-mark move in the shell.

## The Finite Theorem Shape

For this shell:

```text
Every one-mark local move from every canonical Sidon ruler either violates
order or creates a repeated difference.
```

Therefore:

```text
the one-mark shell graph has no edges
```

and:

```text
components = zero modes = vertices = 14.
```

## Why This Matters

This is the first concrete SKTC certificate object for #30:

```text
state-space fragmentation is certified by local obstruction witnesses.
```

The certificate is finite and reusable in form:

```text
vertex list
+ candidate move list
+ order/collision rejection witnesses
+ graph consequence
```

It is not Erdős #30. It is not asymptotic evidence. It is a rigorous local
geometry-of-feasible-states artifact.

## Next Step

Repeat the same certificate shape on:

```text
k=9, D=49:  V=96,  E=1
k=8, D=39:  V=192, E=5
```

Those are harder because some accepted edges exist. They will test whether the
certificate can handle both:

```text
accepted sparse edges
+ rejected collision witnesses
```

After that, the Lean bridge should prove generic lemmas rather than hardcode
this one finite shell:

```text
1. repeated-difference witness => not Sidon
2. no accepted moves => edgeless graph
3. edgeless graph on V vertices => V components
4. graph Laplacian zero modes = component count
```
