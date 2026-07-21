# Exact Gaussian-center engine

The compiled engine is single-threaded. Parallel lane execution is obtained by
running disjoint closed ranges in separate processes.

Build:

    C:\msys64\mingw64\bin\g++.exe -std=c++17 -O3 -DNDEBUG -Wall -Wextra \
      -o gaussian_center.exe gaussian_center.cpp

Finite G or N search:

    gaussian_center.exe --mode G --start 5000000000000 \
      --end 5000016777216 --chunk-size 65536 --run-dir logs/G01 \
      --scalar-verifier verify_scalar.py \
      --independent-verifier verify_independent.exe \
      --python python --deadline-unix ABSOLUTE_UNIX_SECONDS

Add --resume to continue from an existing atomic summary. The deadline is
absolute, so restart does not reset a tranche clock. The engine commits only
whole processed centers; if stopped during chunk factorization, the chunk is
factored again without changing committed counters.

The atomic run-dir/summary.json statuses are:

- RUNNING
- TIMEOUT_INCOMPLETE
- G_FAIL
- N_FAIL
- CANDIDATE_VERIFIED
- FAILED

next_m is always the first unprocessed center. G_FAIL and N_FAIL apply only to
the declared closed input range. Candidate files are written under
run-dir/candidates only after verify_scalar.py and verify_independent.exe both
return zero. An internal candidate rejected by either verifier makes the run
FAILED and emits no candidate file.

Inspect exact center data without starting a search:

    gaussian_center.exe --inspect --start 1 --end 512 --chunk-size 73

Independent small-center calibration:

    python calibrate_gaussian_center.py --start 1 --end 4096

The reference performs a direct coordinate scan. It does not factor m and does
not use Gaussian integer arithmetic.
