# Exact computation

Two independent generators are required before any census result is used:

1. `compute/generator_a/generate_heap.py`: direct closure by distinct pairs.
2. `compute/generator_b/generate_divisors.py`: ascending membership from
   factorizations of `n+1` into two distinct previously reached factors.

`compute/crosscheck.py` compares their complete outputs and records hashes.

