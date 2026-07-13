#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

bool is_allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

struct InequalityAudit {
    std::uint64_t failures = 0;
    std::uint32_t first_failure = 0;
    std::int64_t maximum_excess = std::numeric_limits<std::int64_t>::min();
    std::uint32_t maximum_excess_x = 0;

    void observe(std::uint32_t x, std::int64_t excess) {
        if (excess > 0) {
            ++failures;
            if (first_failure == 0) first_failure = x;
        }
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_excess_x = x;
        }
    }
};

struct HardExample {
    std::uint32_t n;
    std::uint32_t admissible_splits;
    std::uint32_t one_missing_splits;
    std::uint32_t two_missing_splits;
    std::uint32_t least_missing_factor;
};

struct Checkpoint {
    std::uint32_t x;
    std::uint32_t missing;
    std::uint64_t splitless;
    std::uint64_t reducible;
    std::uint64_t odd_reducible;
    std::uint64_t seed3_even_reducible;
    std::uint64_t hard_reducible;
    std::uint32_t missing_half;
    std::uint32_t missing_third;
};

void write_audit(std::ostream& out, const InequalityAudit& audit) {
    out << "{\"failures\":" << audit.failures
        << ",\"first_failure\":" << audit.first_failure
        << ",\"maximum_excess\":" << audit.maximum_excess
        << ",\"maximum_excess_X\":" << audit.maximum_excess_x << "}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: hole_contraction LIMIT OUTPUT_JSON\n";
        return 2;
    }

    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 32 || parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [32, 1000000000]");
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
        for (std::uint64_t m = static_cast<std::uint64_t>(p) * p;
             m <= static_cast<std::uint64_t>(limit) + 1;
             m += p) {
            if (spf[m] == m) spf[m] = p;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint32_t> missing_prefix(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = 1;
    member[3] = 1;

    std::uint64_t splitless = 0;
    std::uint64_t reducible = 0;
    std::uint64_t odd_reducible = 0;
    std::uint64_t seed3_even_reducible = 0;
    std::uint64_t hard_reducible = 0;
    std::uint64_t forced_hard_fiber_11 = 0;
    std::array<std::uint64_t, 90> hard_residues{};
    std::vector<HardExample> hard_examples;
    hard_examples.reserve(64);

    InequalityAudit injective;
    InequalityAudit half_plus_third;
    InequalityAudit seed_partition;
    std::array<InequalityAudit, 33> half_plus_scale;

    std::vector<std::uint32_t> checkpoint_values;
    for (std::uint64_t x = 100; x <= limit; x *= 10) {
        checkpoint_values.push_back(static_cast<std::uint32_t>(x));
        if (x > limit / 10) break;
    }
    if (checkpoint_values.empty() || checkpoint_values.back() != limit) {
        checkpoint_values.push_back(limit);
    }
    std::vector<Checkpoint> checkpoints;
    std::size_t next_checkpoint = 0;

    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);

    for (std::uint32_t n = 2; n <= limit; ++n) {
        bool has_admissible_split = false;
        std::uint32_t admissible_splits = 0;
        std::uint32_t one_missing_splits = 0;
        std::uint32_t two_missing_splits = 0;
        std::uint32_t least_missing_factor = 0;

        if (n >= 4) {
            const std::uint32_t product = n + 1;
            std::uint32_t remaining = product;
            divisors.clear();
            divisors.push_back(1);
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

            for (const std::uint32_t left : divisors) {
                if (left < 2) continue;
                const std::uint32_t right = product / left;
                if (left >= right) continue;
                if (!is_allowed(left) || !is_allowed(right)) continue;

                has_admissible_split = true;
                ++admissible_splits;
                if (member[left] && member[right]) member[n] = 1;
            }

            if (is_allowed(n) && !member[n] && has_admissible_split) {
                for (const std::uint32_t left : divisors) {
                    if (left < 2) continue;
                    const std::uint32_t right = product / left;
                    if (left >= right) continue;
                    if (!is_allowed(left) || !is_allowed(right)) continue;

                    const bool left_missing = !member[left];
                    const bool right_missing = !member[right];
                    if (left_missing && right_missing) {
                        ++two_missing_splits;
                    } else {
                        ++one_missing_splits;
                    }
                    if (left_missing &&
                        (least_missing_factor == 0 || left < least_missing_factor)) {
                        least_missing_factor = left;
                    }
                    if (right_missing &&
                        (least_missing_factor == 0 || right < least_missing_factor)) {
                        least_missing_factor = right;
                    }
                }
            }
        }

        missing_prefix[n] = missing_prefix[n - 1];
        if (is_allowed(n) && !member[n]) {
            ++missing_prefix[n];
            if (!has_admissible_split) {
                ++splitless;
            } else {
                ++reducible;
                if ((n & 1U) != 0) {
                    const std::uint32_t parent = (n + 1) / 2;
                    if (!is_allowed(parent) || member[parent]) {
                        throw std::runtime_error("seed-2 ancestry assertion failed");
                    }
                    ++odd_reducible;
                } else {
                    const std::uint32_t parent = (n + 1) / 3;
                    if ((n + 1) % 3 == 0 && is_allowed(parent) && parent != 3) {
                        if (member[parent]) {
                            throw std::runtime_error("seed-3 ancestry assertion failed");
                        }
                        ++seed3_even_reducible;
                    } else {
                        ++hard_reducible;
                        ++hard_residues[n % 90];
                        if ((n + 1) % 11 == 0) {
                            const std::uint32_t p = (n + 1) / 11;
                            if (p >= 5 && p != 11 && spf[p] == p && member[p]) {
                                if (admissible_splits != 1 ||
                                    one_missing_splits != 1 ||
                                    least_missing_factor != 11) {
                                    throw std::runtime_error(
                                        "forced hard-fiber assertion failed"
                                    );
                                }
                                ++forced_hard_fiber_11;
                            }
                        }
                        if (hard_examples.size() < 64) {
                            hard_examples.push_back(HardExample{
                                n,
                                admissible_splits,
                                one_missing_splits,
                                two_missing_splits,
                                least_missing_factor,
                            });
                        }
                    }
                }
            }
        }

        const std::uint32_t half = (n + 1) / 2;
        const std::uint32_t third = (n + 1) / 3;
        const auto m_half = static_cast<std::int64_t>(missing_prefix[half]);
        const auto m_third = static_cast<std::int64_t>(missing_prefix[third]);
        injective.observe(
            n, static_cast<std::int64_t>(reducible) - m_half
        );
        half_plus_third.observe(
            n, static_cast<std::int64_t>(reducible) - m_half - m_third
        );
        seed_partition.observe(
            n,
            static_cast<std::int64_t>(odd_reducible + hard_reducible) - m_half
        );
        for (std::uint32_t k = 3; k <= 32; ++k) {
            half_plus_scale[k].observe(
                n,
                static_cast<std::int64_t>(reducible) - m_half -
                    static_cast<std::int64_t>(missing_prefix[(n + 1) / k])
            );
        }

        if (next_checkpoint < checkpoint_values.size() &&
            n == checkpoint_values[next_checkpoint]) {
            checkpoints.push_back(Checkpoint{
                n,
                missing_prefix[n],
                splitless,
                reducible,
                odd_reducible,
                seed3_even_reducible,
                hard_reducible,
                missing_prefix[half],
                missing_prefix[third],
            });
            ++next_checkpoint;
        }
    }

    if (reducible != odd_reducible + seed3_even_reducible + hard_reducible) {
        throw std::runtime_error("partition assertion failed");
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");

    out << "{\n";
    out << "  \"schema_version\":1,\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"missing\":" << missing_prefix[limit] << ",\n";
    out << "  \"splitless\":" << splitless << ",\n";
    out << "  \"reducible\":" << reducible << ",\n";
    out << "  \"partition\":{\"odd_seed2\":" << odd_reducible
        << ",\"even_seed3\":" << seed3_even_reducible
        << ",\"hard\":" << hard_reducible
        << ",\"forced_hard_fiber_11\":" << forced_hard_fiber_11
        << ",\"healed_seed2_capacity\":"
        << missing_prefix[(limit + 1) / 2] - odd_reducible << "},\n";
    out << "  \"inequalities\":{\n";
    out << "    \"R_le_Mhalf\":";
    write_audit(out, injective);
    out << ",\n    \"R_le_Mhalf_plus_Mthird\":";
    write_audit(out, half_plus_third);
    out << ",\n    \"odd_plus_hard_le_Mhalf\":";
    write_audit(out, seed_partition);
    out << "\n  },\n";

    out << "  \"half_plus_scale\":[\n";
    for (std::uint32_t k = 3; k <= 32; ++k) {
        out << "    {\"k\":" << k << ",\"audit\":";
        write_audit(out, half_plus_scale[k]);
        out << "}" << (k == 32 ? "\n" : ",\n");
    }
    out << "  ],\n";

    out << "  \"hard_examples\":[\n";
    for (std::size_t i = 0; i < hard_examples.size(); ++i) {
        const auto& row = hard_examples[i];
        out << "    {\"n\":" << row.n
            << ",\"admissible_splits\":" << row.admissible_splits
            << ",\"one_missing_splits\":" << row.one_missing_splits
            << ",\"two_missing_splits\":" << row.two_missing_splits
            << ",\"least_missing_factor\":" << row.least_missing_factor
            << "}" << (i + 1 == hard_examples.size() ? "\n" : ",\n");
    }
    out << "  ],\n";

    out << "  \"hard_residues_mod_90\":[";
    for (std::size_t r = 0; r < hard_residues.size(); ++r) {
        if (r != 0) out << ',';
        out << hard_residues[r];
    }
    out << "],\n";

    out << "  \"checkpoints\":[\n";
    for (std::size_t i = 0; i < checkpoints.size(); ++i) {
        const auto& row = checkpoints[i];
        out << "    {\"X\":" << row.x
            << ",\"M\":" << row.missing
            << ",\"E\":" << row.splitless
            << ",\"R\":" << row.reducible
            << ",\"odd_seed2\":" << row.odd_reducible
            << ",\"even_seed3\":" << row.seed3_even_reducible
            << ",\"hard\":" << row.hard_reducible
            << ",\"Mhalf\":" << row.missing_half
            << ",\"Mthird\":" << row.missing_third
            << "}" << (i + 1 == checkpoints.size() ? "\n" : ",\n");
    }
    out << "  ],\n";
    out << "  \"elapsed_seconds\":" << elapsed.count() << "\n";
    out << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " missing=" << missing_prefix[limit]
              << " splitless=" << splitless
              << " reducible=" << reducible
              << " odd=" << odd_reducible
              << " seed3_even=" << seed3_even_reducible
              << " hard=" << hard_reducible
              << " two_scale_failures=" << half_plus_third.failures
              << " seed_partition_failures=" << seed_partition.failures
              << " elapsed_seconds=" << elapsed.count() << '\n';
    return 0;
}
