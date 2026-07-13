#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

struct Checkpoint {
    std::uint32_t x;
    std::uint64_t generated;
    std::uint64_t missing;
    std::uint64_t splitless_missing;
    std::uint64_t missing_at_half;
    std::int64_t injective_excess;
    std::uint64_t forced_fiber_11;
};

bool is_allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

void write_checkpoint(std::ostream& out, const Checkpoint& row) {
    out << "    {\"X\":" << row.x
        << ",\"generated\":" << row.generated
        << ",\"missing\":" << row.missing
        << ",\"splitless_missing\":" << row.splitless_missing
        << ",\"missing_at_floor_Xplus1_over_2\":" << row.missing_at_half
        << ",\"injective_excess\":" << row.injective_excess
        << ",\"forced_fiber_11\":" << row.forced_fiber_11 << "}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: missing_charge LIMIT OUTPUT_JSON\n";
        return 2;
    }

    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 32 || parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [32, 1000000000]");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);
    const std::string output_path = argv[2];
    const auto started = std::chrono::steady_clock::now();

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t prime = 2;
         static_cast<std::uint64_t>(prime) * prime <=
             static_cast<std::uint64_t>(limit) + 1;
         ++prime) {
        if (spf[prime] != prime) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(prime) * prime;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += prime) {
            if (spf[multiple] == multiple) {
                spf[multiple] = prime;
            }
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint32_t> missing_prefix(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = 1;
    member[3] = 1;
    std::uint64_t generated_count = 2;
    std::uint64_t splitless_missing_count = 0;

    std::uint32_t first_failure_x = 0;
    std::uint64_t first_failure_missing = 0;
    std::uint64_t first_failure_splitless = 0;
    std::uint64_t first_failure_missing_half = 0;
    std::uint64_t failure_cutoff_count = 0;
    std::uint32_t last_failure_x = 0;
    std::int64_t maximum_excess = 0;
    std::uint32_t maximum_excess_x = 0;
    std::uint64_t maximum_excess_missing = 0;
    std::uint64_t maximum_excess_splitless = 0;
    std::uint64_t maximum_excess_missing_half = 0;

    std::uint64_t maximum_ratio_numerator = 0;
    std::uint64_t maximum_ratio_denominator = 1;
    std::uint32_t maximum_ratio_x = 0;

    std::vector<std::uint32_t> checkpoint_values;
    for (std::uint64_t value = 10; value <= limit; value *= 10) {
        if (value >= 100) checkpoint_values.push_back(static_cast<std::uint32_t>(value));
        if (value > limit / 10) break;
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
        if (n >= 4) {
            const std::uint32_t product = n + 1;
            std::uint32_t remaining = product;
            divisors.clear();
            divisors.push_back(1);

            while (remaining > 1) {
                const std::uint32_t prime = spf[remaining];
                const std::size_t old_size = divisors.size();
                std::uint32_t power = 1;
                do {
                    remaining /= prime;
                    power *= prime;
                    for (std::size_t i = 0; i < old_size; ++i) {
                        divisors.push_back(divisors[i] * power);
                    }
                } while (remaining > 1 && spf[remaining] == prime);
            }

            for (const std::uint32_t left : divisors) {
                if (left < 2) continue;
                const std::uint32_t right = product / left;
                if (left >= right) continue;
                if (is_allowed(left) && is_allowed(right)) {
                    has_admissible_split = true;
                }
                if (!member[n] && member[left] && member[right]) {
                    member[n] = 1;
                    ++generated_count;
                }
            }
        }

        missing_prefix[n] = missing_prefix[n - 1];
        if (is_allowed(n) && !member[n]) {
            ++missing_prefix[n];
            if (!has_admissible_split) ++splitless_missing_count;
        }

        const std::uint32_t half = (n + 1) / 2;
        const std::int64_t excess =
            static_cast<std::int64_t>(missing_prefix[n]) -
            static_cast<std::int64_t>(splitless_missing_count) -
            static_cast<std::int64_t>(missing_prefix[half]);
        if (excess > 0) {
            ++failure_cutoff_count;
            last_failure_x = n;
            if (first_failure_x == 0) {
                first_failure_x = n;
                first_failure_missing = missing_prefix[n];
                first_failure_splitless = splitless_missing_count;
                first_failure_missing_half = missing_prefix[half];
            }
        }
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_excess_x = n;
            maximum_excess_missing = missing_prefix[n];
            maximum_excess_splitless = splitless_missing_count;
            maximum_excess_missing_half = missing_prefix[half];
        }

        const std::uint64_t reducible_missing =
            static_cast<std::uint64_t>(missing_prefix[n]) - splitless_missing_count;
        const std::uint64_t denominator = missing_prefix[half];
        if (denominator > 0 &&
            reducible_missing * maximum_ratio_denominator >
                maximum_ratio_numerator * denominator) {
            maximum_ratio_numerator = reducible_missing;
            maximum_ratio_denominator = denominator;
            maximum_ratio_x = n;
        }

        if (next_checkpoint < checkpoint_values.size() &&
            n == checkpoint_values[next_checkpoint]) {
            checkpoints.push_back(Checkpoint{
                n,
                generated_count,
                missing_prefix[n],
                splitless_missing_count,
                missing_prefix[half],
                excess,
                0,
            });
            ++next_checkpoint;
        }
    }

    std::uint64_t forced_fiber_count = 0;
    std::uint32_t first_forced_prime = 0;
    std::uint32_t last_forced_prime = 0;
    std::size_t forced_checkpoint = 0;
    const std::uint32_t prime_limit = (limit + 1) / 11;
    for (std::uint32_t prime = 2; prime <= prime_limit; ++prime) {
        while (forced_checkpoint < checkpoints.size() &&
               prime > (checkpoints[forced_checkpoint].x + 1) / 11) {
            checkpoints[forced_checkpoint].forced_fiber_11 = forced_fiber_count;
            ++forced_checkpoint;
        }
        if (spf[prime] != prime || !member[prime]) continue;
        if (prime == 11) continue;

        const std::uint64_t output = 11ULL * prime - 1;
        if (output > limit) break;
        if (member[output] || !is_allowed(static_cast<std::uint32_t>(output))) {
            throw std::runtime_error("forced-fiber assertion failed");
        }
        if (first_forced_prime == 0) first_forced_prime = prime;
        last_forced_prime = prime;
        ++forced_fiber_count;
    }
    while (forced_checkpoint < checkpoints.size()) {
        checkpoints[forced_checkpoint].forced_fiber_11 = forced_fiber_count;
        ++forced_checkpoint;
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;

    std::ofstream out(output_path);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n";
    out << "  \"schema_version\":1,\n";
    out << "  \"arithmetic\":\"exact ascending divisor recursion\",\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"generated_count\":" << generated_count << ",\n";
    out << "  \"missing_allowed_count\":" << missing_prefix[limit] << ",\n";
    out << "  \"splitless_missing_count\":" << splitless_missing_count << ",\n";
    out << "  \"injective_contraction\":{\n";
    out << "    \"formula\":\"M(X) <= E(X) + M(floor((X+1)/2))\",\n";
    out << "    \"tested_every_integer_cutoff_through\":" << limit << ",\n";
    out << "    \"first_failure\":{\"X\":" << first_failure_x
        << ",\"M\":" << first_failure_missing
        << ",\"E\":" << first_failure_splitless
        << ",\"half_argument\":" << (first_failure_x + 1) / 2
        << ",\"M_half\":" << first_failure_missing_half
        << ",\"excess\":"
        << static_cast<std::int64_t>(first_failure_missing) -
               static_cast<std::int64_t>(first_failure_splitless) -
               static_cast<std::int64_t>(first_failure_missing_half)
        << "},\n";
    out << "    \"failure_cutoff_count\":" << failure_cutoff_count << ",\n";
    out << "    \"last_failure_X\":" << last_failure_x << ",\n";
    out << "    \"maximum_excess\":{\"X\":" << maximum_excess_x
        << ",\"M\":" << maximum_excess_missing
        << ",\"E\":" << maximum_excess_splitless
        << ",\"M_half\":" << maximum_excess_missing_half
        << ",\"excess\":" << maximum_excess << "},\n";
    out << "    \"maximum_required_coefficient\":{\"X\":" << maximum_ratio_x
        << ",\"numerator\":" << maximum_ratio_numerator
        << ",\"denominator\":" << maximum_ratio_denominator << "}\n";
    out << "  },\n";
    out << "  \"forced_fiber_11\":{\n";
    out << "    \"description\":\"p in G prime gives unique split 11*p and missing output 11*p-1\",\n";
    out << "    \"count\":" << forced_fiber_count << ",\n";
    out << "    \"first_generated_prime\":" << first_forced_prime << ",\n";
    out << "    \"last_generated_prime\":" << last_forced_prime << ",\n";
    out << "    \"last_output\":" << 11ULL * last_forced_prime - 1 << "\n";
    out << "  },\n";
    out << "  \"checkpoints\":[\n";
    for (std::size_t i = 0; i < checkpoints.size(); ++i) {
        write_checkpoint(out, checkpoints[i]);
        out << (i + 1 == checkpoints.size() ? "\n" : ",\n");
    }
    out << "  ],\n";
    out << "  \"elapsed_seconds\":" << elapsed.count() << "\n";
    out << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " generated=" << generated_count
              << " missing=" << missing_prefix[limit]
              << " splitless=" << splitless_missing_count
              << " first_failure=" << first_failure_x
              << " forced_fiber_11=" << forced_fiber_count
              << " elapsed_seconds=" << elapsed.count() << "\n";
    return 0;
}
