# Reproducibility package

This directory accompanies the paper:

Shortest-geodesic supports in triangle-free maximum cuts:
an infinite Hall obstruction and the first minimal footprints.

## Requirements

- Python 3.11 or later.
- nauty/Traces 2.8.9 for the footprint enumeration.
- Set the environment variable GENG to the full geng executable path,
  or place geng on PATH.

All combinatorial checks use integer arithmetic.

## Commands

Family construction and independent cut-count checks:

    python -B family_verify.py --max-t 8 --exact-max-t 5

Independent implementation (full cuts for t=1,2; orbit counts for t=3,4):

    python -B family_verify_independent.py

Independent direct footprint enumeration:

    python -B local_obstruction_recheck.py 10

Primary branch-and-bound footprint enumeration:

    python -B local_obstruction_scan.py scan 6 10 16

Expected classification:

    m=6: 0 valid footprints, 0 atom subsets
    m=7: 0 valid footprints, 0 atom subsets
    m=8: 0 valid footprints, 0 atom subsets
    m=9: 1 valid footprint, 1 atom subset
    m=10: 3 valid footprints, 56 atom subsets

The m=10 atom-subset count is across canonical footprint representatives
and is not quotiented again by footprint automorphisms.


