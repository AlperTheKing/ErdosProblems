# Gaussian summary atomic-replacement calibration

Build and run on Windows:

    C:\msys64\mingw64\bin\g++.exe -std=c++17 -O2 -DNDEBUG -Wall -Wextra \
      -pthread -o test_gaussian_atomic_stress.exe \
      test_gaussian_atomic_stress.cpp
    test_gaussian_atomic_stress.exe

The reader repeatedly opens `summary.json` without delete sharing while the
writer performs 2,000 same-directory atomic replacements. Every observed
payload must be complete. The test requires at least one bounded transient
retry and verifies that replacing a directory fails on the first attempt.

The production writer retries only `ERROR_SHARING_VIOLATION`,
`ERROR_LOCK_VIOLATION`, and `ERROR_ACCESS_DENIED` when the existing target
is a regular file. It makes at most 128 attempts with a 1--8 ms delay and
reports the final Windows error code and attempt count on terminal failure.
