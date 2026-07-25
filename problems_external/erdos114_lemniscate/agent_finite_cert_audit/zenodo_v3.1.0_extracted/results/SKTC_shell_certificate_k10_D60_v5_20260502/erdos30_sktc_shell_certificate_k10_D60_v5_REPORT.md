# Erdos #30 SKTC Shell Certificate v5 Report

Date: 2026-05-02

## Verdict

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: finite shell-geometry certificate only
```

This is the first finite shell-graph certificate object for the #30 SKTC
program.

It certifies the local one-mark graph for:

```text
k = 10
D = 60
optimal diameter D* = 55
shell delta = 5
```

## Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_shell_certificate.py

input:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_compression_shell_v3_RESULTS.json

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_certificate_k10_D60_v5_RESULTS.json

result_sha256:
569d7c427214b3f5c25874fd5a3d590dfc92c67ce6775e170da10adbbf0f7809
```

## Certificate Content

The shell contains:

```text
vertices V: 14
accepted edges E: 0
candidate one-mark moves checked: 448
```

The 448 candidates come from:

```text
14 vertices
* 2 orientations per non-symmetric canonical ruler
* 8 movable interior marks
* 2 directions (+/-1)
```

Every candidate move was accounted for:

```text
order violations: 38
repeated-difference collision witnesses: 410
valid candidate missing from shell: 0
accepted moves: 0
```

All 14 vertices are Sidon/Golomb rulers.

## Example Collision Witness

One rejected candidate changes:

```text
[0, 1, 3, 11, 17, 29, 36, 51, 56, 60]
```

to:

```text
[0, 2, 3, 11, 17, 29, 36, 51, 56, 60]
```

The repeated-difference witness is:

```text
36 - 2 = 51 - 17 = 34
```

So the candidate is not Sidon.

## Graph Consequence

For any finite graph:

```text
components(G) >= V - E
```

Here:

```text
V = 14
E = 0
components = 14
Laplacian zero modes = 14
```

The bound is tight:

```text
components = V - E = 14
```

## Meaning

This proves a finite local statement:

```text
The k=10, D=60 Sidon shell has completely fragmented one-mark local transition
geometry under the chosen graph definition.
```

It does not prove Erdős #30 or move the A-axis. It is a reusable certificate
shape:

```text
vertex list
+ candidate move enumeration
+ collision witnesses for rejected moves
+ graph consequence
```

## Next Lean Bridge

The Lean bridge should not encode the 448-line certificate manually first.
The better route is:

1. Prove a generic repeated-difference rejection lemma.
2. Prove `components(G) >= V - E` for finite graphs, or specialize to `E=0`.
3. Add a checker/generator path for importing finite certificates.
4. Only then consider registering this as a C3 candidate.

Safe claim:

```text
We have produced a complete finite certificate that the k=10, D=60 near-optimal
Sidon shell has no valid one-mark transitions; all 448 candidate moves are
rejected by order or explicit difference-collision witnesses.
```
