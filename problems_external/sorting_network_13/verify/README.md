# Sorting-network calibration fixtures

This directory contains the maintained 12-channel/40-comparator/depth-8 and
13-channel/46-comparator/depth-9 fixtures copied from:

<https://bertdobbelaere.github.io/sorting_networks.html>

The JSON files preserve the source layers and declare their expected channel,
comparator, and depth counts. No search code is present here.

## Independent exhaustive verifiers

- verify_scalar.py uses Python's JSON parser. It simulates one binary input
  at a time as a mutable list, checks the final list against the unique sorted
  list with the same Hamming weight, and visits all 2^n inputs.
- verify_bitsliced.cpp has its own fixture parser. It represents each wire as
  a bit vector containing all 2^n inputs at once, implements each comparator
  by bitwise AND/OR, and counts every adjacent 1,0 output inversion.

These implementations do not share simulation or output-checking code.

## Reproduction

From the repository root:

    python problems_external\sorting_network_13\verify\verify_scalar.py
    g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic problems_external\sorting_network_13\verify\verify_bitsliced.cpp -o problems_external\sorting_network_13\verify\verify_bitsliced.exe
    problems_external\sorting_network_13\verify\verify_bitsliced.exe problems_external\sorting_network_13\verify\fixtures\sn12_40_depth8.json problems_external\sorting_network_13\verify\fixtures\sn13_46_depth9.json

Both verifiers returned zero failures on 4,096 inputs for SN12/40 and 8,192
inputs for SN13/46. The exact machine-readable reports and SHA-256 fixture
identities are recorded in verification_results.json.
