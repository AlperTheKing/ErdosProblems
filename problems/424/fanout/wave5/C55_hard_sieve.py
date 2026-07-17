#!/usr/bin/env python3
"""Exact hard-hole witness and critical-fiber audit for task C55.

The checked-in artifact is Python-only.  For the 1e8 scan it compiles the
embedded C++ kernel in a temporary directory, runs it, and deletes the
temporary files.  The kernel reconstructs the least grounded set in
increasing order and admits only factor pairs a < b, preserving the
distinct-input rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


CPP_SOURCE = r"""
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace {

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

bool hard_shape(std::uint32_t n, bool has_pair) {
    if ((n & 1U) != 0 || !has_pair) return false;
    if ((n + 1) % 3 != 0) return true;
    const std::uint32_t q = (n + 1) / 3;
    return !(allowed(q) && q != 3);
}

std::size_t bucket_index(std::uint32_t value) {
    if (value == 0) throw std::runtime_error("zero witness count");
    std::size_t index = 0;
    --value;
    while (value != 0) {
        value >>= 1U;
        ++index;
    }
    return index;
}

void write_buckets(
    const std::array<std::uint64_t, 32>& buckets,
    std::uint64_t overflow
) {
    std::cout << "[";
    bool first = true;
    for (std::size_t i = 0; i < buckets.size(); ++i) {
        if (buckets[i] == 0) continue;
        const std::uint64_t lo = i == 0 ? 1ULL : (1ULL << (i - 1)) + 1;
        const std::uint64_t hi = 1ULL << i;
        if (!first) std::cout << ",";
        first = false;
        std::cout << "{\"lo\":" << lo
                  << ",\"hi\":" << hi
                  << ",\"count\":" << buckets[i] << "}";
    }
    if (overflow != 0) {
        if (!first) std::cout << ",";
        std::cout << "{\"lo\":2147483649,\"hi\":null,\"count\":"
                  << overflow << "}";
    }
    std::cout << "]";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: c55_kernel LIMIT\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 100 || parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100, 1000000000]");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);
    const auto started = std::chrono::steady_clock::now();

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <=
             static_cast<std::uint64_t>(limit) + 1;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += p) {
            if (spf[multiple] == multiple) {
                spf[multiple] = p;
            }
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    constexpr std::uint16_t kUnsetRank =
        std::numeric_limits<std::uint16_t>::max();
    std::vector<std::uint16_t> rank(
        static_cast<std::size_t>(limit) + 1, kUnsetRank
    );
    std::vector<std::uint8_t> shadow_contains_6(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint8_t> shadow_only_6(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = member[3] = 1;
    std::vector<std::uint32_t> minimum_missing_fiber(
        static_cast<std::size_t>((limit + 1) / 5) + 2, 0
    );
    std::vector<std::uint32_t> minimum_critical_fiber(
        static_cast<std::size_t>((limit + 1) / 5) + 2, 0
    );
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    std::vector<std::uint32_t> missing_endpoints;
    missing_endpoints.reserve(256);

    std::uint64_t generated = 2;
    std::uint64_t healed_targets = 0;
    std::uint64_t healed_targets_containing_6 = 0;
    std::uint64_t hard = 0;
    std::uint64_t hard_mixed = 0;
    std::uint64_t hard_all_hole = 0;
    std::uint64_t hard_unique_pair = 0;
    std::uint64_t unique_mixed_blocker_11 = 0;
    std::uint64_t unique_mixed_blocker_11_top_half = 0;
    std::uint64_t minimum_critical_11_top_half = 0;
    std::uint64_t hard_shadow_only_6 = 0;
    std::int64_t singleton_6_maximum_deficit = 0;
    std::uint32_t singleton_6_maximum_x = 0;
    std::uint64_t singleton_6_maximum_h = 0;
    std::uint64_t singleton_6_maximum_q = 0;
    std::uint32_t maximum_pair_count = 0;
    std::uint32_t maximum_missing_endpoint_count = 0;
    std::uint16_t maximum_rank = 0;
    std::array<std::uint64_t, 32> pair_buckets{};
    std::array<std::uint64_t, 32> missing_buckets{};
    std::uint64_t pair_overflow = 0;
    std::uint64_t missing_overflow = 0;

    for (std::uint32_t n = 4; n <= limit; ++n) {
        if (!allowed(n)) continue;
        const std::uint32_t product = n + 1;
        std::uint32_t remaining = product;
        divisors.clear();
        divisors.push_back(1);
        missing_endpoints.clear();
        while (remaining > 1) {
            const std::uint32_t p = spf[remaining];
            const std::size_t old_size = divisors.size();
            std::uint32_t power = 1;
            do {
                remaining /= p;
                power *= p;
                for (std::size_t i = 0; i < old_size; ++i) {
                    divisors.push_back(divisors[i] * power);
                }
            } while (remaining > 1 && spf[remaining] == p);
        }

        bool has_pair = false;
        bool is_generated = false;
        bool has_mixed_pair = false;
        std::uint32_t pair_count = 0;
        std::uint32_t missing_endpoint_count = 0;
        std::uint32_t minimum_missing = std::numeric_limits<std::uint32_t>::max();
        std::uint16_t blocking_rank = 0;
        std::uint32_t minimum_critical = std::numeric_limits<std::uint32_t>::max();
        std::uint32_t unique_a = 0;
        std::uint32_t unique_b = 0;

        for (const std::uint32_t a : divisors) {
            if (a < 2) continue;
            const std::uint32_t b = product / a;
            // This is the distinct-input rule: equal factors are excluded.
            if (a >= b || !allowed(a) || !allowed(b)) continue;
            has_pair = true;
            ++pair_count;
            unique_a = a;
            unique_b = b;
            const bool ma = member[a] != 0;
            const bool mb = member[b] != 0;
            if (ma && mb) {
                is_generated = true;
            } else {
                has_mixed_pair = has_mixed_pair || (ma != mb);
                std::uint16_t pair_block = kUnsetRank;
                if (!ma) {
                    ++missing_endpoint_count;
                    minimum_missing = std::min(minimum_missing, a);
                    pair_block = rank[a];
                    missing_endpoints.push_back(a);
                }
                if (!mb) {
                    ++missing_endpoint_count;
                    minimum_missing = std::min(minimum_missing, b);
                    pair_block = std::min(pair_block, rank[b]);
                    missing_endpoints.push_back(b);
                }
                if (pair_block == kUnsetRank) {
                    throw std::runtime_error("blocked pair has no ranked endpoint");
                }
                if (pair_block > blocking_rank) {
                    blocking_rank = pair_block;
                    minimum_critical = std::numeric_limits<std::uint32_t>::max();
                }
                if (pair_block == blocking_rank) {
                    if (!ma && rank[a] == pair_block) {
                        minimum_critical = std::min(minimum_critical, a);
                    }
                    if (!mb && rank[b] == pair_block) {
                        minimum_critical = std::min(minimum_critical, b);
                    }
                }
            }
        }

        if (is_generated) {
            member[n] = 1;
            ++generated;
            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (!member[parent]) {
                    ++healed_targets;
                    if (shadow_contains_6[parent]) {
                        ++healed_targets_containing_6;
                    }
                }
            }
            continue;
        }
        rank[n] = has_pair ? static_cast<std::uint16_t>(blocking_rank + 1) : 0;
        maximum_rank = std::max(maximum_rank, rank[n]);
        if (!has_pair) {
            if (n == 6) {
                shadow_contains_6[n] = 1;
                shadow_only_6[n] = 1;
            }
        } else {
            bool found_lower = false;
            bool contains_6 = false;
            bool only_6 = true;
            for (const std::uint32_t endpoint : missing_endpoints) {
                if (rank[endpoint] >= rank[n]) continue;
                found_lower = true;
                contains_6 = contains_6 || shadow_contains_6[endpoint];
                only_6 = only_6 && shadow_only_6[endpoint];
            }
            if (!found_lower) {
                throw std::runtime_error("hole has no lower-rank endpoint");
            }
            shadow_contains_6[n] = static_cast<std::uint8_t>(contains_6);
            shadow_only_6[n] = static_cast<std::uint8_t>(only_6);
        }
        if (!hard_shape(n, has_pair)) continue;

        ++hard;
        if (has_mixed_pair) ++hard_mixed;
        else ++hard_all_hole;
        if (pair_count == 1) ++hard_unique_pair;
        maximum_pair_count = std::max(maximum_pair_count, pair_count);
        maximum_missing_endpoint_count = std::max(
            maximum_missing_endpoint_count, missing_endpoint_count
        );

        const std::size_t pair_bucket = bucket_index(pair_count);
        if (pair_bucket < pair_buckets.size()) ++pair_buckets[pair_bucket];
        else ++pair_overflow;
        const std::size_t missing_bucket = bucket_index(missing_endpoint_count);
        if (missing_bucket < missing_buckets.size()) {
            ++missing_buckets[missing_bucket];
        } else {
            ++missing_overflow;
        }

        if (minimum_missing == std::numeric_limits<std::uint32_t>::max()) {
            throw std::runtime_error("hard hole has no missing endpoint");
        }
        if (minimum_missing >= minimum_missing_fiber.size()) {
            throw std::runtime_error("C44 scale bound failed");
        }
        ++minimum_missing_fiber[minimum_missing];
        if (minimum_critical == std::numeric_limits<std::uint32_t>::max()) {
            throw std::runtime_error("hard hole has no critical endpoint");
        }
        if (minimum_critical >= minimum_critical_fiber.size()) {
            throw std::runtime_error("C44 critical scale bound failed");
        }
        ++minimum_critical_fiber[minimum_critical];
        if (minimum_critical == 11 && n > limit / 2) {
            ++minimum_critical_11_top_half;
        }
        if (shadow_only_6[n]) {
            ++hard_shadow_only_6;
            const std::int64_t deficit =
                static_cast<std::int64_t>(hard_shadow_only_6) -
                static_cast<std::int64_t>(healed_targets_containing_6);
            if (deficit > singleton_6_maximum_deficit) {
                singleton_6_maximum_deficit = deficit;
                singleton_6_maximum_x = n;
                singleton_6_maximum_h = hard_shadow_only_6;
                singleton_6_maximum_q = healed_targets_containing_6;
            }
        }

        if (pair_count == 1 && (unique_a == 11 || unique_b == 11)) {
            const std::uint32_t other = unique_a == 11 ? unique_b : unique_a;
            if (member[other]) {
                ++unique_mixed_blocker_11;
                if (n > limit / 2) ++unique_mixed_blocker_11_top_half;
            }
        }
    }

    std::uint32_t maximum_fiber_factor = 0;
    std::uint32_t maximum_fiber_count = 0;
    std::uint32_t maximum_critical_fiber_factor = 0;
    std::uint32_t maximum_critical_fiber_count = 0;
    for (std::uint32_t factor = 0;
         factor < minimum_missing_fiber.size();
         ++factor) {
        if (minimum_missing_fiber[factor] > maximum_fiber_count) {
            maximum_fiber_count = minimum_missing_fiber[factor];
            maximum_fiber_factor = factor;
        }
        if (minimum_critical_fiber[factor] > maximum_critical_fiber_count) {
            maximum_critical_fiber_count = minimum_critical_fiber[factor];
            maximum_critical_fiber_factor = factor;
        }
    }

    std::uint64_t prime_star_all = 0;
    std::uint64_t prime_star_generated = 0;
    std::uint64_t prime_star_all_top_half = 0;
    std::uint64_t prime_star_generated_top_half = 0;
    const std::uint32_t prime_limit = (limit + 1) / 11;
    for (std::uint32_t p = 5; p <= prime_limit; ++p) {
        if (spf[p] != p || p % 3 != 2 || p == 11) continue;
        const std::uint64_t source = 11ULL * p - 1;
        if (source > limit) continue;
        if (member[source]) {
            throw std::runtime_error("11p-1 prime-star source was generated");
        }
        ++prime_star_all;
        if (source > limit / 2) ++prime_star_all_top_half;
        if (member[p]) {
            ++prime_star_generated;
            if (source > limit / 2) ++prime_star_generated_top_half;
        }
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::cout << "{"
              << "\"limit\":" << limit
              << ",\"generated\":" << generated
              << ",\"healed_targets\":" << healed_targets
              << ",\"hard\":" << hard
              << ",\"hard_mixed\":" << hard_mixed
              << ",\"hard_all_hole\":" << hard_all_hole
              << ",\"hard_unique_pair\":" << hard_unique_pair
              << ",\"maximum_admissible_pairs\":" << maximum_pair_count
              << ",\"maximum_missing_endpoints\":"
              << maximum_missing_endpoint_count
              << ",\"maximum_obstruction_rank\":" << maximum_rank
              << ",\"admissible_pair_buckets\":";
    write_buckets(pair_buckets, pair_overflow);
    std::cout << ",\"missing_endpoint_buckets\":";
    write_buckets(missing_buckets, missing_overflow);
    std::cout << ",\"minimum_missing_factor_fiber\":{"
              << "\"factor\":" << maximum_fiber_factor
              << ",\"predecessor\":" << (maximum_fiber_factor + 1) / 2
              << ",\"count\":" << maximum_fiber_count
              << ",\"factor_11_count\":" << minimum_missing_fiber[11]
              << "}"
              << ",\"minimum_critical_endpoint_fiber\":{"
              << "\"factor\":" << maximum_critical_fiber_factor
              << ",\"predecessor\":"
              << (maximum_critical_fiber_factor + 1) / 2
              << ",\"count\":" << maximum_critical_fiber_count
              << ",\"factor_11_count\":" << minimum_critical_fiber[11]
              << ",\"factor_11_top_half\":" << minimum_critical_11_top_half
              << "}"
              << ",\"unique_mixed_blocker_11\":{"
              << "\"count\":" << unique_mixed_blocker_11
              << ",\"top_half\":" << unique_mixed_blocker_11_top_half
              << "}"
              << ",\"singleton_shadow_6_gate\":{"
              << "\"hard_shadow_only_6\":" << hard_shadow_only_6
              << ",\"healed_shadow_contains_6\":"
              << healed_targets_containing_6
              << ",\"maximum_deficit\":" << singleton_6_maximum_deficit
              << ",\"maximum_X\":" << singleton_6_maximum_x
              << ",\"hard_at_maximum\":" << singleton_6_maximum_h
              << ",\"healed_at_maximum\":" << singleton_6_maximum_q
              << "}"
              << ",\"forced_11_prime_star\":{"
              << "\"all\":" << prime_star_all
              << ",\"generated_cofactor\":" << prime_star_generated
              << ",\"all_top_half\":" << prime_star_all_top_half
              << ",\"generated_cofactor_top_half\":"
              << prime_star_generated_top_half
              << "}"
              << ",\"elapsed_seconds\":" << elapsed.count()
              << "}\n";
    return 0;
}
"""


EXPECTED_1E8 = {
    "generated": 51_899_129,
    "hard": 3_368_726,
    "healed_targets": 5_948_614,
    "minimum_critical_11": 472_257,
    "unique_mixed_blocker_11": 308_779,
    "hard_shadow_only_6": 336_564,
    "healed_shadow_contains_6": 1_962_543,
    "singleton_6_maximum_deficit": 1,
    "prime_star_all": 304_162,
    "prime_star_generated": 278_968,
    "prime_star_all_top_half": 144_682,
    "prime_star_generated_top_half": 134_901,
}


def compile_and_run(limit: int, compiler: str) -> dict:
    compiler_path = shutil.which(compiler)
    if compiler_path is None:
        raise SystemExit(f"compiler not found: {compiler}")
    with tempfile.TemporaryDirectory(prefix="c55_hard_sieve_") as temp_name:
        temp = Path(temp_name)
        source = temp / "c55_kernel.cpp"
        executable = temp / "c55_kernel.exe"
        source.write_text(CPP_SOURCE, encoding="ascii")
        subprocess.run(
            [
                compiler_path,
                "-O3",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                str(source),
                "-o",
                str(executable),
            ],
            check=True,
        )
        completed = subprocess.run(
            [str(executable), str(limit)],
            check=True,
            capture_output=True,
            text=True,
        )
    return json.loads(completed.stdout)


def verify_1e8(result: dict) -> None:
    star = result["forced_11_prime_star"]
    critical = result["minimum_critical_endpoint_fiber"]
    unique_11 = result["unique_mixed_blocker_11"]
    singleton = result["singleton_shadow_6_gate"]
    observed = {
        "generated": result["generated"],
        "hard": result["hard"],
        "healed_targets": result["healed_targets"],
        "minimum_critical_11": critical["factor_11_count"],
        "unique_mixed_blocker_11": unique_11["count"],
        "hard_shadow_only_6": singleton["hard_shadow_only_6"],
        "healed_shadow_contains_6": singleton["healed_shadow_contains_6"],
        "singleton_6_maximum_deficit": singleton["maximum_deficit"],
        "prime_star_all": star["all"],
        "prime_star_generated": star["generated_cofactor"],
        "prime_star_all_top_half": star["all_top_half"],
        "prime_star_generated_top_half": star["generated_cofactor_top_half"],
    }
    if observed != EXPECTED_1E8:
        raise AssertionError({"expected": EXPECTED_1E8, "observed": observed})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100_000_000)
    parser.add_argument("--compiler", default="g++")
    args = parser.parse_args()
    result = compile_and_run(args.limit, args.compiler)
    if args.limit == 100_000_000:
        verify_1e8(result)
    envelope = {
        "schema_version": 1,
        "arithmetic": "exact ascending divisor recursion",
        "distinct_input_rule": "only 2 <= a < b is admitted",
        "kernel_sha256": hashlib.sha256(CPP_SOURCE.encode("ascii")).hexdigest(),
        "result": result,
    }
    print(json.dumps(envelope, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
