# Exact computation

Two independent generators are required before any census result is used:

1. `compute/generator_a/generate_heap.py`: direct closure by distinct pairs.
2. `compute/generator_b/generate_divisors.py`: ascending membership from
   factorizations of `n+1` into two distinct previously reached factors.

`compute/crosscheck.py` compares their complete outputs and records hashes.


## Accepted exact outputs

- `crosscheck_100000.json`: both generators give `39,843` members.
- Independent wave-1 generators agree bit-for-bit through `10^7`, with `A(10^7)=4,952,270`.
- `census_100000000.json`: `A(10^8)=51,899,129`, maximum observed gap `21`.
- B02 frozen `{2,3,5}` subsystem: `18,222,202,754` members through `10^11`;
  exact modular orbit size `6,011,481,468` modulo `30^7`.

These finite counts are discovery and falsification data only.
