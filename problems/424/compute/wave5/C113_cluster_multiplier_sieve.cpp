#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace {

struct Row {
    std::uint32_t d = 0;
    std::uint32_t multiplier = 0;
};

bool better(const Row& left, const Row& right) {
    return std::tie(left.d, right.multiplier) > std::tie(right.d, left.multiplier);
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) {
            std::cerr << "usage: C113_cluster_multiplier_sieve OUTPUT_JSON\n";
            return 2;
        }
        constexpr std::uint64_t p0 = 524'343ULL;
        constexpr std::uint64_t p1 = 524'351ULL;
        constexpr std::uint64_t base = p0 * p1;
        constexpr std::uint64_t maximum =
            std::numeric_limits<std::uint64_t>::max() / base;
        static_assert(maximum < std::numeric_limits<std::uint32_t>::max());
        const auto limit = static_cast<std::uint32_t>(maximum);

        std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 1);
        for (std::uint32_t p = 2; static_cast<std::uint64_t>(p) * p <= limit; ++p) {
            if (spf[p] != 0) continue;
            for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
                 multiple <= limit;
                 multiple += p) {
                auto& value = spf[static_cast<std::size_t>(multiple)];
                if (value == 0) value = p;
            }
        }

        std::uint64_t eligible = 0;
        std::uint64_t at_least_198 = 0;
        std::uint64_t at_least_258 = 0;
        Row maximum_row;
        std::vector<Row> top;
        top.reserve(256);
        std::vector<Row> threshold_candidates;
        threshold_candidates.reserve(250'000);

        for (std::uint32_t multiplier = 2; multiplier <= limit; ++multiplier) {
            if (multiplier % 3 != 2) continue;
            ++eligible;
            std::uint32_t remaining = multiplier;
            std::uint64_t plus_tau = 4;   // 19 and 9199 in p0/3.
            std::uint64_t minus_tau = 2;  // prime p1.
            bool p1_exponent_even = false;  // p1 initially has exponent one.
            bool other_minus_exponents_even = true;
            while (remaining > 1) {
                const auto prime = spf[remaining] == 0 ? remaining : spf[remaining];
                std::uint32_t exponent = 0;
                do {
                    remaining /= prime;
                    ++exponent;
                } while (remaining % prime == 0);
                if (prime == 19 || prime == 9'199) {
                    plus_tau = plus_tau / 2 * (exponent + 2);
                } else if (prime == p1) {
                    minus_tau = minus_tau / 2 * (exponent + 2);
                    p1_exponent_even = ((exponent + 1) % 2 == 0);
                } else if (prime % 3 == 1) {
                    plus_tau *= exponent + 1;
                } else if (prime % 3 == 2) {
                    minus_tau *= exponent + 1;
                    if (exponent % 2 == 1) other_minus_exponents_even = false;
                } else {
                    throw std::runtime_error("multiplier divisible by three");
                }
            }
            const auto odd_minus_divisors =
                (minus_tau - (p1_exponent_even && other_minus_exponents_even ? 1ULL : 0ULL)) / 2;
            const auto d64 = plus_tau * odd_minus_divisors;
            if (d64 > std::numeric_limits<std::uint32_t>::max()) {
                throw std::runtime_error("pair count overflow");
            }
            const Row row{static_cast<std::uint32_t>(d64), multiplier};
            if (better(row, maximum_row)) maximum_row = row;
            if (row.d >= 198) ++at_least_198;
            if (row.d >= 258) {
                ++at_least_258;
                threshold_candidates.push_back(row);
            }
            if (top.size() < 256) {
                top.push_back(row);
                std::push_heap(top.begin(), top.end(), better);
            } else if (better(row, top.front())) {
                std::pop_heap(top.begin(), top.end(), better);
                top.back() = row;
                std::push_heap(top.begin(), top.end(), better);
            }
        }
        std::sort(top.begin(), top.end(), better);

        std::ofstream out(argv[1], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output");
        out << "{\n"
            << "  \"schema\":\"C113-cluster-multiplier-sieve-v1\",\n"
            << "  \"arithmetic\":\"exact unsigned integers only\",\n"
            << "  \"endpoint_product\":" << base << ",\n"
            << "  \"maximum_multiplier\":" << limit << ",\n"
            << "  \"eligible_multipliers\":" << eligible << ",\n"
            << "  \"count_d_at_least_198\":" << at_least_198 << ",\n"
            << "  \"count_d_at_least_258\":" << at_least_258 << ",\n"
            << "  \"maximum\":{\"d\":" << maximum_row.d
            << ",\"multiplier\":" << maximum_row.multiplier
            << ",\"product\":" << base * maximum_row.multiplier << "},\n"
            << "  \"top\":[\n";
        for (std::size_t index = 0; index < top.size(); ++index) {
            const auto& row = top[index];
            out << "    {\"d\":" << row.d
                << ",\"multiplier\":" << row.multiplier
                << ",\"product\":" << base * row.multiplier << '}'
                << (index + 1 == top.size() ? "\n" : ",\n");
        }
        out << "  ],\n  \"threshold_candidates\":[\n";
        for (std::size_t index = 0; index < threshold_candidates.size(); ++index) {
            const auto& row = threshold_candidates[index];
            out << "    {\"d\":" << row.d
                << ",\"multiplier\":" << row.multiplier
                << ",\"product\":" << base * row.multiplier << '}'
                << (index + 1 == threshold_candidates.size() ? "\n" : ",\n");
        }
        out << "  ]\n}\n";
        if (!out) throw std::runtime_error("could not write output");
        std::cout << "limit=" << limit
                  << " max_d=" << maximum_row.d
                  << " d258=" << at_least_258 << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
