#!/usr/bin/env python3
"""Exact, unthinned dyadic energy extension for Erdos problem 424.

This is a Python build/run driver for an embedded C++20 kernel.  Keeping the
kernel here makes the experiment a single owned, reproducible source file.

The kernel computes G through B by the exact ascending divisor recurrence and
then computes

    E(U,V) = sum_p r_{U,V}(p)^2,  r_{U,V}(p) = #{(u,v): uv=p},

and |U*V|.  Its bounded-memory algorithm partitions the integer product axis
into disjoint half-open buckets.  In one bucket it stores the exact product
offsets as uint32 values, radix-sorts them, and counts equal runs.  Thus every
pair is processed, no reservoir is thinned, and products in different buckets
cannot collide.  A legacy full-product std::sort implementation is retained as
an independent small-instance oracle.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


CPP_SOURCE = r'''
#define NOMINMAX
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <tuple>
#include <utility>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#else
#include <sys/resource.h>
#include <unistd.h>
#endif

#ifdef _OPENMP
#include <omp.h>
#endif

using u32 = std::uint32_t;
using u64 = std::uint64_t;
using u128 = unsigned __int128;
using Clock = std::chrono::steady_clock;

static std::string u128_string(u128 value) {
    if (value == 0) return "0";
    std::string out;
    while (value > 0) {
        out.push_back(char('0' + value % 10));
        value /= 10;
    }
    std::reverse(out.begin(), out.end());
    return out;
}

static long double u128_long_double(u128 value) {
    const u64 low = static_cast<u64>(value);
    const u64 high = static_cast<u64>(value >> 64);
    return static_cast<long double>(high) * 18446744073709551616.0L
         + static_cast<long double>(low);
}

static u64 current_rss_bytes() {
#ifdef _WIN32
    PROCESS_MEMORY_COUNTERS_EX counters{};
    counters.cb = sizeof(counters);
    if (GetProcessMemoryInfo(
            GetCurrentProcess(),
            reinterpret_cast<PROCESS_MEMORY_COUNTERS*>(&counters),
            sizeof(counters))) {
        return static_cast<u64>(counters.WorkingSetSize);
    }
    return 0;
#else
    struct rusage usage{};
    if (getrusage(RUSAGE_SELF, &usage) != 0) return 0;
#ifdef __APPLE__
    return static_cast<u64>(usage.ru_maxrss);
#else
    return static_cast<u64>(usage.ru_maxrss) * 1024ULL;
#endif
#endif
}

class RssSampler {
public:
    void start() {
        stop_flag_.store(false, std::memory_order_relaxed);
        peak_.store(current_rss_bytes(), std::memory_order_relaxed);
        thread_ = std::thread([this]() {
            while (!stop_flag_.load(std::memory_order_relaxed)) {
                const u64 value = current_rss_bytes();
                u64 old = peak_.load(std::memory_order_relaxed);
                while (value > old && !peak_.compare_exchange_weak(
                           old, value, std::memory_order_relaxed)) {}
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        });
    }

    u64 stop() {
        stop_flag_.store(true, std::memory_order_relaxed);
        if (thread_.joinable()) thread_.join();
        const u64 final_value = current_rss_bytes();
        return std::max(final_value, peak_.load(std::memory_order_relaxed));
    }

    ~RssSampler() {
        if (thread_.joinable()) {
            stop_flag_.store(true, std::memory_order_relaxed);
            thread_.join();
        }
    }

private:
    std::atomic<bool> stop_flag_{true};
    std::atomic<u64> peak_{0};
    std::thread thread_;
};

static double elapsed_seconds(Clock::time_point start) {
    return std::chrono::duration<double>(Clock::now() - start).count();
}

struct Config {
    u32 limit = 10'000'000;
    std::vector<u32> ys{1'000, 10'000, 100'000};
    std::vector<u32> zs{1'000, 10'000, 100'000, 1'000'000, 10'000'000};
    std::vector<std::pair<u32, u32>> explicit_cases;
    u64 bucket_products = 100'000'000;
    int workers = 24;
    bool triangular = true;
    bool validate = true;
    bool validation_only = false;
};

static std::vector<u32> parse_u32_list(const std::string& text) {
    std::vector<u32> values;
    std::stringstream in(text);
    std::string item;
    while (std::getline(in, item, ',')) {
        if (item.empty()) continue;
        const unsigned long long value = std::stoull(item);
        if (value > std::numeric_limits<u32>::max()) {
            throw std::runtime_error("list value exceeds uint32: " + item);
        }
        values.push_back(static_cast<u32>(value));
    }
    if (values.empty()) throw std::runtime_error("empty integer list");
    return values;
}

static std::vector<std::pair<u32, u32>> parse_cases(const std::string& text) {
    std::vector<std::pair<u32, u32>> cases;
    std::stringstream in(text);
    std::string item;
    while (std::getline(in, item, ',')) {
        const auto colon = item.find(':');
        if (colon == std::string::npos) {
            throw std::runtime_error("case must be Y:Z: " + item);
        }
        const auto y = std::stoull(item.substr(0, colon));
        const auto z = std::stoull(item.substr(colon + 1));
        if (y > std::numeric_limits<u32>::max() ||
            z > std::numeric_limits<u32>::max()) {
            throw std::runtime_error("case endpoint exceeds uint32: " + item);
        }
        cases.emplace_back(static_cast<u32>(y), static_cast<u32>(z));
    }
    if (cases.empty()) throw std::runtime_error("empty case list");
    return cases;
}

static void usage(const char* program) {
    std::cout
        << "usage: " << program << " [options]\n"
        << "  --limit N                 exact closure cutoff (default 10000000)\n"
        << "  --ys A,B,C                Y endpoints\n"
        << "  --zs A,B,C                Z endpoints\n"
        << "  --cases Y:Z,Y:Z           run exactly these cases\n"
        << "  --workers N               OpenMP workers, hard-capped at 24\n"
        << "  --bucket-products N       maximum representations in one bucket\n"
        << "  --full-grid               include Z < Y cases\n"
        << "  --no-validate             skip legacy product-sort cross-checks\n"
        << "  --validation-only         stop after cross-checks\n";
}

static Config parse_args(int argc, char** argv) {
    Config config;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto need_value = [&]() -> std::string {
            if (++i >= argc) throw std::runtime_error("missing value after " + arg);
            return argv[i];
        };
        if (arg == "--limit") {
            config.limit = static_cast<u32>(std::stoull(need_value()));
        } else if (arg == "--ys") {
            config.ys = parse_u32_list(need_value());
        } else if (arg == "--zs") {
            config.zs = parse_u32_list(need_value());
        } else if (arg == "--cases") {
            config.explicit_cases = parse_cases(need_value());
        } else if (arg == "--workers") {
            config.workers = std::stoi(need_value());
        } else if (arg == "--bucket-products") {
            config.bucket_products = std::stoull(need_value());
        } else if (arg == "--full-grid") {
            config.triangular = false;
        } else if (arg == "--no-validate") {
            config.validate = false;
        } else if (arg == "--validation-only") {
            config.validation_only = true;
        } else if (arg == "--help" || arg == "-h") {
            usage(argv[0]);
            std::exit(0);
        } else {
            throw std::runtime_error("unknown argument: " + arg);
        }
    }
    if (config.limit < 3) throw std::runtime_error("--limit must be at least 3");
    if (config.workers < 1 || config.workers > 24) {
        throw std::runtime_error("--workers must lie in [1,24]");
    }
    if (config.bucket_products < 1) {
        throw std::runtime_error("--bucket-products must be positive");
    }
    return config;
}

struct GeneratedSet {
    std::vector<std::uint8_t> member;
    std::vector<u32> g0;
    std::vector<u32> g2;
    u64 count = 0;
};

static std::vector<u32> smallest_prime_factors(u32 limit) {
    std::vector<u32> spf(static_cast<std::size_t>(limit) + 1, 0);
    for (u32 p = 2; static_cast<u64>(p) * p <= limit; ++p) {
        if (spf[p] != 0) continue;
        for (u64 multiple = static_cast<u64>(p) * p;
             multiple <= limit; multiple += p) {
            if (spf[static_cast<std::size_t>(multiple)] == 0) {
                spf[static_cast<std::size_t>(multiple)] = p;
            }
        }
    }
    return spf;
}

static GeneratedSet generate_set(u32 limit) {
    // The checkpoint values come from the independent census.cpp recurrence.
    const std::map<u32, u64> checkpoints{
        {10, 4}, {100, 23}, {1'000, 250}, {10'000, 3'207},
        {100'000, 39'843}, {1'000'000, 457'599},
        {10'000'000, 4'952'270},
    };

    auto spf = smallest_prime_factors(limit + 1);
    GeneratedSet result;
    result.member.assign(static_cast<std::size_t>(limit) + 1, 0);
    result.member[2] = 1;
    result.member[3] = 1;
    result.count = 2;

    // tau(n) <= 448 for n <= 10^7; the larger fixed buffer leaves room for
    // exploratory cutoffs while avoiding one heap allocation per integer.
    std::array<u32, 4096> divisors{};
    for (u32 n = 4; n <= limit; ++n) {
        if (n % 3 != 1) {
            u32 remaining = n + 1;
            std::size_t divisor_count = 1;
            divisors[0] = 1;
            while (remaining > 1) {
                const u32 prime = spf[remaining] == 0 ? remaining : spf[remaining];
                const std::size_t old_count = divisor_count;
                u32 power = 1;
                do {
                    remaining /= prime;
                    power *= prime;
                    if (divisor_count + old_count > divisors.size()) {
                        throw std::runtime_error("divisor buffer exhausted");
                    }
                    for (std::size_t j = 0; j < old_count; ++j) {
                        divisors[divisor_count++] = divisors[j] * power;
                    }
                } while (remaining % prime == 0);
            }
            const u64 product = static_cast<u64>(n) + 1;
            for (std::size_t j = 0; j < divisor_count; ++j) {
                const u32 left = divisors[j];
                if (left < 2 || static_cast<u64>(left) * left >= product) continue;
                const u32 right = static_cast<u32>(product / left);
                if (result.member[left] && result.member[right]) {
                    result.member[n] = 1;
                    ++result.count;
                    break;
                }
            }
        }

        const auto expected = checkpoints.find(n);
        if (expected != checkpoints.end() && result.count != expected->second) {
            throw std::runtime_error(
                "membership checkpoint mismatch at " + std::to_string(n) +
                ": got " + std::to_string(result.count) +
                ", expected " + std::to_string(expected->second));
        }
    }

    result.g0.reserve(result.count / 2);
    result.g2.reserve(result.count / 2);
    for (u32 n = 2; n <= limit; ++n) {
        if (!result.member[n]) continue;
        if (n % 3 == 0) result.g0.push_back(n);
        else if (n % 3 == 2) result.g2.push_back(n);
        else throw std::runtime_error("mod-3 invariant failure");
    }
    if (result.g0.size() + result.g2.size() != result.count) {
        throw std::runtime_error("colour counts do not sum to |G|");
    }
    return result;
}

static std::vector<u32> window(const std::vector<u32>& values, u32 high) {
    const auto first = std::upper_bound(values.begin(), values.end(), high / 2);
    const auto last = std::upper_bound(values.begin(), values.end(), high);
    return std::vector<u32>(first, last);
}

struct Stats {
    u128 energy = 0;
    u64 distinct = 0;
    u64 representations = 0;
};

template <typename Integer>
static Stats sorted_stats(const std::vector<Integer>& sorted) {
    Stats stats;
    stats.representations = static_cast<u64>(sorted.size());
    if (sorted.empty()) return stats;
    u64 run = 1;
    for (std::size_t i = 1; i < sorted.size(); ++i) {
        if (sorted[i] == sorted[i - 1]) {
            ++run;
        } else {
            stats.energy += static_cast<u128>(run) * run;
            ++stats.distinct;
            run = 1;
        }
    }
    stats.energy += static_cast<u128>(run) * run;
    ++stats.distinct;
    return stats;
}

static Stats full_product_sort(
    const std::vector<u32>& left,
    const std::vector<u32>& right
) {
    const u128 count128 = static_cast<u128>(left.size()) * right.size();
    if (count128 > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("full product vector exceeds size_t");
    }
    std::vector<u64> products;
    products.reserve(static_cast<std::size_t>(count128));
    for (u32 x : left) {
        for (u32 y : right) products.push_back(static_cast<u64>(x) * y);
    }
    std::sort(products.begin(), products.end());
    return sorted_stats(products);
}

static int radix_threads(std::size_t size, int requested) {
    if (size < 500'000) return 1;
    const u64 useful = std::max<u64>(1, size / 500'000);
    return std::min<int>(requested, static_cast<int>(useful));
}

static void radix_sort_u32(std::vector<u32>& values, int requested_workers) {
    if (values.size() < 2) return;
    constexpr unsigned bits = 11;
    constexpr std::size_t radix = 1U << bits;
    constexpr u32 mask = static_cast<u32>(radix - 1);

    const u32 maximum = *std::max_element(values.begin(), values.end());
    int passes = 1;
    while (passes * static_cast<int>(bits) < 32 &&
           (maximum >> (passes * bits)) != 0) {
        ++passes;
    }

    const int workers = radix_threads(values.size(), requested_workers);
    std::vector<u32> temporary(values.size());
    std::vector<u64> counts(static_cast<std::size_t>(workers) * radix);
    std::vector<u64> offsets(static_cast<std::size_t>(workers) * radix);
    u32* source = values.data();
    u32* target = temporary.data();
    const std::size_t size = values.size();

    for (int pass = 0; pass < passes; ++pass) {
        const unsigned shift = pass * bits;
        std::fill(counts.begin(), counts.end(), 0);

#ifdef _OPENMP
#pragma omp parallel num_threads(workers)
#endif
        {
#ifdef _OPENMP
            const int thread = omp_get_thread_num();
            const int team = omp_get_num_threads();
#else
            const int thread = 0;
            const int team = 1;
#endif
            const std::size_t begin = size * thread / team;
            const std::size_t end = size * (thread + 1) / team;
            u64* local = counts.data() + static_cast<std::size_t>(thread) * radix;
            for (std::size_t i = begin; i < end; ++i) {
                ++local[(source[i] >> shift) & mask];
            }
        }

        u64 position = 0;
        for (std::size_t digit = 0; digit < radix; ++digit) {
            for (int thread = 0; thread < workers; ++thread) {
                const std::size_t index = static_cast<std::size_t>(thread) * radix + digit;
                offsets[index] = position;
                position += counts[index];
            }
        }
        if (position != size) throw std::runtime_error("radix count mismatch");

#ifdef _OPENMP
#pragma omp parallel num_threads(workers)
#endif
        {
#ifdef _OPENMP
            const int thread = omp_get_thread_num();
            const int team = omp_get_num_threads();
#else
            const int thread = 0;
            const int team = 1;
#endif
            const std::size_t begin = size * thread / team;
            const std::size_t end = size * (thread + 1) / team;
            u64* local = offsets.data() + static_cast<std::size_t>(thread) * radix;
            for (std::size_t i = begin; i < end; ++i) {
                const u32 value = source[i];
                target[local[(value >> shift) & mask]++] = value;
            }
        }
        std::swap(source, target);
    }

    if (source != values.data()) values.swap(temporary);
}

static u64 ceil_div(u64 numerator, u64 denominator) {
    return numerator / denominator + (numerator % denominator != 0);
}

static u64 products_in_range(
    const std::vector<u32>& left,
    const std::vector<u32>& right,
    u64 low,
    u64 high
) {
    u64 count = 0;
    for (u32 x : left) {
        const u64 first_value = ceil_div(low, x);
        const u64 past_value = ceil_div(high, x);
        const auto first = std::lower_bound(right.begin(), right.end(), first_value);
        const auto past = std::lower_bound(right.begin(), right.end(), past_value);
        count += static_cast<u64>(past - first);
    }
    return count;
}

struct ProductBucket {
    u64 low = 0;
    u64 high = 0;
    u64 count = 0;
};

static void split_bucket(
    const std::vector<u32>& left,
    const std::vector<u32>& right,
    u64 low,
    u64 high,
    u64 count,
    u64 target_products,
    std::vector<ProductBucket>& output
) {
    constexpr u64 max_width = static_cast<u64>(std::numeric_limits<u32>::max()) + 1;
    if (count == 0) return;
    if ((count <= target_products && high - low <= max_width) || high - low <= 1) {
        output.push_back({low, high, count});
        return;
    }
    const u64 middle = low + (high - low) / 2;
    if (middle == low || middle == high) {
        throw std::runtime_error("unable to split nonterminal product bucket");
    }
    const u64 left_count = products_in_range(left, right, low, middle);
    if (left_count > count) throw std::runtime_error("bucket count underflow");
    split_bucket(left, right, low, middle, left_count, target_products, output);
    split_bucket(left, right, middle, high, count - left_count, target_products, output);
}

static std::vector<ProductBucket> make_buckets(
    const std::vector<u32>& left,
    const std::vector<u32>& right,
    u64 target_products
) {
    if (left.empty() || right.empty()) return {};
    const u64 total = static_cast<u64>(left.size()) * right.size();
    const u64 minimum = static_cast<u64>(left.front()) * right.front();
    const u64 maximum = static_cast<u64>(left.back()) * right.back();
    if (maximum == std::numeric_limits<u64>::max()) {
        throw std::runtime_error("product-axis endpoint overflow");
    }
    std::vector<ProductBucket> buckets;
    split_bucket(left, right, minimum, maximum + 1, total, target_products, buckets);
    u64 sum = 0;
    u64 previous_high = minimum;
    for (const auto& bucket : buckets) {
        if (bucket.low < previous_high || bucket.high <= bucket.low) {
            throw std::runtime_error("invalid bucket partition");
        }
        previous_high = bucket.high;
        sum += bucket.count;
    }
    if (sum != total) throw std::runtime_error("bucket partition loses products");
    return buckets;
}

static std::vector<u32> materialize_bucket(
    const std::vector<u32>& left,
    const std::vector<u32>& right,
    const ProductBucket& bucket,
    int workers
) {
    if (bucket.count > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("bucket exceeds size_t");
    }
    std::vector<std::size_t> first(left.size());
    std::vector<std::size_t> past(left.size());
    std::vector<u64> offsets(left.size() + 1, 0);
    for (std::size_t i = 0; i < left.size(); ++i) {
        const u64 low_value = ceil_div(bucket.low, left[i]);
        const u64 high_value = ceil_div(bucket.high, left[i]);
        first[i] = static_cast<std::size_t>(
            std::lower_bound(right.begin(), right.end(), low_value) - right.begin());
        past[i] = static_cast<std::size_t>(
            std::lower_bound(right.begin(), right.end(), high_value) - right.begin());
        offsets[i + 1] = offsets[i] + (past[i] - first[i]);
    }
    if (offsets.back() != bucket.count) {
        throw std::runtime_error("bucket materialization count mismatch");
    }

    std::vector<u32> products(static_cast<std::size_t>(bucket.count));
#ifdef _OPENMP
#pragma omp parallel for schedule(dynamic, 1) num_threads(workers)
#endif
    for (std::int64_t i = 0; i < static_cast<std::int64_t>(left.size()); ++i) {
        u64 output = offsets[static_cast<std::size_t>(i)];
        const u64 x = left[static_cast<std::size_t>(i)];
        for (std::size_t j = first[static_cast<std::size_t>(i)];
             j < past[static_cast<std::size_t>(i)]; ++j) {
            const u64 product = x * right[j];
            if (product < bucket.low || product >= bucket.high) {
                throw std::runtime_error("materialized product outside bucket");
            }
            const u64 relative = product - bucket.low;
            if (relative > std::numeric_limits<u32>::max()) {
                throw std::runtime_error("bucket offset exceeds uint32");
            }
            products[static_cast<std::size_t>(output++)] = static_cast<u32>(relative);
        }
        if (output != offsets[static_cast<std::size_t>(i) + 1]) {
            throw std::runtime_error("parallel materialization offset mismatch");
        }
    }
    return products;
}

struct BucketRun {
    Stats stats;
    std::size_t buckets = 0;
    u64 largest_bucket = 0;
};

static BucketRun bucketed_energy(
    const std::vector<u32>& left,
    const std::vector<u32>& right,
    u64 target_products,
    int workers,
    bool show_progress
) {
    BucketRun run;
    const auto buckets = make_buckets(left, right, target_products);
    run.buckets = buckets.size();
    const u64 expected = static_cast<u64>(left.size()) * right.size();
    const auto start = Clock::now();
    std::size_t next_progress = 10;
    for (std::size_t i = 0; i < buckets.size(); ++i) {
        run.largest_bucket = std::max(run.largest_bucket, buckets[i].count);
        auto products = materialize_bucket(left, right, buckets[i], workers);
        radix_sort_u32(products, workers);
        const Stats local = sorted_stats(products);
        if (local.representations != buckets[i].count) {
            throw std::runtime_error("bucket representation count mismatch");
        }
        run.stats.energy += local.energy;
        run.stats.distinct += local.distinct;
        run.stats.representations += local.representations;

        const std::size_t percent = buckets.empty() ? 100 : (100 * (i + 1)) / buckets.size();
        if (show_progress && (percent >= next_progress || i + 1 == buckets.size())) {
            std::cout << "BUCKET_PROGRESS\tdone=" << (i + 1)
                      << "\ttotal=" << buckets.size()
                      << "\tpercent=" << percent
                      << "\twall_s=" << std::fixed << std::setprecision(3)
                      << elapsed_seconds(start) << "\n" << std::flush;
            while (next_progress <= percent) next_progress += 10;
        }
    }
    if (run.stats.representations != expected) {
        throw std::runtime_error("total representation count mismatch");
    }
    return run;
}

static void validate_algorithms(
    const GeneratedSet& generated,
    const Config& config
) {
    std::vector<std::pair<u32, u32>> cases;
    if (config.limit >= 1'000) cases.emplace_back(1'000, 1'000);
    if (config.limit >= 10'000) {
        cases.emplace_back(1'000, 10'000);
        cases.emplace_back(10'000, 10'000);
    }
    for (const auto [y, z] : cases) {
        const auto left = window(generated.g0, y);
        const auto right = window(generated.g2, z);
        const Stats oracle = full_product_sort(left, right);
        const BucketRun candidate = bucketed_energy(
            left, right, std::min<u64>(config.bucket_products, 10'000),
            config.workers, false);
        const bool equal = oracle.energy == candidate.stats.energy &&
                           oracle.distinct == candidate.stats.distinct &&
                           oracle.representations == candidate.stats.representations;
        std::cout << "VALIDATE\tY=" << y << "\tZ=" << z
                  << "\tU=" << left.size() << "\tV=" << right.size()
                  << "\tproducts=" << oracle.representations
                  << "\tE=" << u128_string(oracle.energy)
                  << "\tdistinct=" << oracle.distinct
                  << "\tbuckets=" << candidate.buckets
                  << "\tequal=" << (equal ? "true" : "false") << "\n";
        if (!equal) throw std::runtime_error("legacy/bucket validation mismatch");
    }
}

static std::vector<std::pair<u32, u32>> requested_cases(const Config& config) {
    if (!config.explicit_cases.empty()) return config.explicit_cases;
    std::vector<std::pair<u32, u32>> cases;
    for (u32 y : config.ys) {
        for (u32 z : config.zs) {
            if (!config.triangular || y <= z) cases.emplace_back(y, z);
        }
    }
    return cases;
}

int main(int argc, char** argv) {
    try {
        const Config config = parse_args(argc, argv);
#ifdef _OPENMP
        omp_set_dynamic(0);
        omp_set_num_threads(config.workers);
#endif
        std::cout << "META\talgorithm=adaptive_u32_product_buckets_radix11"
                  << "\tlimit=" << config.limit
                  << "\tworkers=" << config.workers
                  << "\tbucket_products=" << config.bucket_products
#ifdef _OPENMP
                  << "\topenmp=true"
#else
                  << "\topenmp=false"
#endif
                  << "\n" << std::flush;

        RssSampler generator_memory;
        generator_memory.start();
        const auto generation_start = Clock::now();
        const GeneratedSet generated = generate_set(config.limit);
        const double generation_wall = elapsed_seconds(generation_start);
        const u64 generation_peak = generator_memory.stop();
        std::cout << "GEN\tB=" << config.limit
                  << "\tG=" << generated.count
                  << "\tG0=" << generated.g0.size()
                  << "\tG2=" << generated.g2.size()
                  << "\twall_s=" << std::fixed << std::setprecision(3)
                  << generation_wall
                  << "\tpeak_rss_gib=" << std::setprecision(3)
                  << generation_peak / 1073741824.0 << "\n" << std::flush;

        if (config.validate) validate_algorithms(generated, config);
        if (config.validation_only) return 0;

        std::cout << "TABLE\tY\tZ\tU\tV\tproducts\tE\tdistinct"
                  << "\tE_over_UV\tkappa\tbuckets\tmax_bucket"
                  << "\twall_s\tpeak_rss_gib\n";
        for (const auto [y, z] : requested_cases(config)) {
            if (y > config.limit || z > config.limit) {
                throw std::runtime_error("case endpoint exceeds --limit");
            }
            const auto left = window(generated.g0, y);
            const auto right = window(generated.g2, z);
            if (left.empty() || right.empty()) {
                throw std::runtime_error("empty dyadic reservoir");
            }
            const u64 products = static_cast<u64>(left.size()) * right.size();
            std::cout << "CASE_BEGIN\tY=" << y << "\tZ=" << z
                      << "\tU=" << left.size() << "\tV=" << right.size()
                      << "\tproducts=" << products << "\n" << std::flush;

            RssSampler case_memory;
            case_memory.start();
            const auto case_start = Clock::now();
            const BucketRun run = bucketed_energy(
                left, right, config.bucket_products, config.workers, true);
            const double wall = elapsed_seconds(case_start);
            const u64 peak = case_memory.stop();

            const long double energy = u128_long_double(run.stats.energy);
            const long double denominator =
                static_cast<long double>(left.size()) * right.size();
            const long double ratio = energy / denominator;
            const long double kappa = energy * y * static_cast<long double>(z) /
                (static_cast<long double>(left.size()) * left.size() *
                 static_cast<long double>(right.size()) * right.size());

            std::cout << "ROW\t" << y << "\t" << z
                      << "\t" << left.size() << "\t" << right.size()
                      << "\t" << run.stats.representations
                      << "\t" << u128_string(run.stats.energy)
                      << "\t" << run.stats.distinct
                      << "\t" << std::fixed << std::setprecision(9) << ratio
                      << "\t" << std::setprecision(9) << kappa
                      << "\t" << run.buckets
                      << "\t" << run.largest_bucket
                      << "\t" << std::setprecision(3) << wall
                      << "\t" << std::setprecision(3)
                      << peak / 1073741824.0 << "\n" << std::flush;
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << "\n";
        return 1;
    }
}
'''


def main() -> int:
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    if compiler is None:
        raise SystemExit("g++ is required (or set CXX to a C++20 compiler)")

    flags = [
        "-O3",
        "-std=c++20",
        "-march=native",
        "-fopenmp",
        "-DNDEBUG",
    ]
    if os.name == "nt":
        flags.append("-lpsapi")
    cache_key = hashlib.sha256(
        (CPP_SOURCE + "\0" + compiler + "\0" + " ".join(flags)).encode("utf-8")
    ).hexdigest()[:20]
    build_dir = Path(tempfile.gettempdir()) / "erdos424_c01_energy_ext"
    build_dir.mkdir(parents=True, exist_ok=True)
    source_path = build_dir / f"kernel_{cache_key}.cpp"
    executable_path = build_dir / f"kernel_{cache_key}.exe"

    if not executable_path.exists():
        source_path.write_text(CPP_SOURCE, encoding="utf-8", newline="\n")
        command = [compiler, *flags, str(source_path), "-o", str(executable_path)]
        print("BUILD\t" + subprocess.list2cmdline(command), flush=True)
        subprocess.run(command, check=True)
    else:
        print(f"BUILD\tcache={executable_path}", flush=True)

    command = [str(executable_path), *sys.argv[1:]]
    print("RUN\t" + subprocess.list2cmdline(command), flush=True)
    completed = subprocess.run(command)
    script_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(f"SCRIPT_SHA256\t{script_digest}", flush=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
