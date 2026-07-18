# SN13 calibration engine

- `SorterHunter/`: public upstream source pinned at commit `392762f916688756242d90febced98ad157bc6d2`.
- `build.ps1`: reproducible optimized Windows build.
- `fixtures/`: maintained N12L40 and N13L46 sorting networks.
- `configs/`: deterministic one-comparator deletion calibration cohorts.
- `run_single.ps1`: one-process, wall-time-bounded measurement harness.
- `verify_scalar.py` and `verify_bitslice.cpp`: independent exhaustive zero-one verifiers.
- `results/`: verified calibration hits.

The local `calibration_log.cpp` only makes upstream stdout line-buffered so a bounded run can be stopped without losing its last reports.
