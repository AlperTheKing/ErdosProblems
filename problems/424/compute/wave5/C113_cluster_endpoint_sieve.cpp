#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

namespace {

struct Scenario {
    std::uint32_t endpoint0;
    std::uint32_t endpoint1;
};

struct Factor {
    std::uint32_t prime;
    std::uint32_t exponent;
};

struct Candidate {
    std::uint32_t scenario;
    std::uint32_t multiplier;
    std::uint32_t d;
    std::uint64_t product;
};

std::vector<Factor> factor_small(
    std::uint32_t value,
    const std::vector<std::uint32_t>& spf
) {
    std::vector<Factor> result;
    while (value > 1) {
        const auto prime = spf[value] == 0 ? value : spf[value];
        std::uint32_t exponent = 0;
        do {
            value /= prime;
            ++exponent;
        } while (value % prime == 0);
        result.push_back({prime, exponent});
    }
    return result;
}

void merge_factor(std::vector<Factor>& factors, Factor added) {
    for (auto& factor : factors) {
        if (factor.prime == added.prime) {
            factor.exponent += added.exponent;
            return;
        }
    }
    factors.push_back(added);
}

std::uint32_t base_exponent(
    const std::vector<Factor>& factors,
    std::uint32_t prime
) {
    for (const auto factor : factors) {
        if (factor.prime == prime) return factor.exponent;
    }
    return 0;
}

struct DivisorProfile {
    std::uint64_t plus_tau = 1;
    std::uint64_t minus_tau = 1;
    std::uint32_t odd_minus_exponents = 0;
    std::uint32_t odd_total_exponents = 0;
    std::uint32_t v3 = 0;
    bool sqrt_minus_parity = false;
};

void add_prime_power(
    DivisorProfile& profile,
    std::uint32_t prime,
    std::uint32_t old_exponent,
    std::uint32_t added_exponent
) {
    const auto new_exponent = old_exponent + added_exponent;
    profile.odd_total_exponents -= old_exponent & 1U;
    profile.odd_total_exponents += new_exponent & 1U;
    if (prime == 3) {
        profile.v3 = new_exponent;
        return;
    }
    auto& tau = prime % 3 == 1 ? profile.plus_tau : profile.minus_tau;
    tau = tau / (old_exponent + 1) * (new_exponent + 1);
    if (prime % 3 == 2) {
        profile.odd_minus_exponents -= old_exponent & 1U;
        profile.odd_minus_exponents += new_exponent & 1U;
        profile.sqrt_minus_parity ^= static_cast<bool>((old_exponent / 2) & 1U);
        profile.sqrt_minus_parity ^= static_cast<bool>((new_exponent / 2) & 1U);
    }
}

DivisorProfile fixed_profile(const std::vector<Factor>& factors) {
    DivisorProfile profile;
    for (const auto factor : factors) {
        add_prime_power(profile, factor.prime, 0, factor.exponent);
    }
    return profile;
}

std::uint64_t admissible_pair_count(const DivisorProfile& profile) {
    if (profile.v3 > 1 || (profile.odd_minus_exponents & 1U) != 0) return 0;
    const auto parity_difference = profile.odd_minus_exponents == 0 ? 1ULL : 0ULL;
    const auto residue_two_divisors =
        profile.plus_tau * (profile.minus_tau - parity_difference) / 2;
    if (profile.v3 == 1) return residue_two_divisors;
    if (profile.v3 != 0) return 0;
    const bool diagonal =
        profile.odd_total_exponents == 0 && profile.sqrt_minus_parity;
    return (residue_two_divisors - static_cast<std::uint64_t>(diagonal)) / 2;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) {
            std::cerr << "usage: C113_cluster_endpoint_sieve OUTPUT_JSON\n";
            return 2;
        }
        constexpr Scenario scenarios[] = {
            {1'048'685U, 524'351U},
            {1'048'685U, 1'048'701U},
        };
        std::uint32_t maximum_limit = 0;
        for (const auto scenario : scenarios) {
            const auto base =
                static_cast<std::uint64_t>(scenario.endpoint0) * scenario.endpoint1;
            maximum_limit = std::max(
                maximum_limit,
                static_cast<std::uint32_t>(
                    std::numeric_limits<std::uint64_t>::max() / base
                )
            );
        }
        std::vector<std::uint32_t> spf(static_cast<std::size_t>(maximum_limit) + 1);
        for (std::uint32_t prime = 2;
             static_cast<std::uint64_t>(prime) * prime <= maximum_limit;
             ++prime) {
            if (spf[prime] != 0) continue;
            for (std::uint64_t multiple = static_cast<std::uint64_t>(prime) * prime;
                 multiple <= maximum_limit;
                 multiple += prime) {
                auto& entry = spf[static_cast<std::size_t>(multiple)];
                if (entry == 0) entry = prime;
            }
        }

        std::vector<Candidate> candidates;
        std::vector<std::uint64_t> eligible(std::size(scenarios));
        std::vector<std::uint64_t> threshold_count(std::size(scenarios));
        std::vector<std::uint64_t> maximum_d(std::size(scenarios));
        std::vector<std::uint32_t> maximum_multiplier(std::size(scenarios));

        for (std::uint32_t scenario_index = 0;
             scenario_index < std::size(scenarios);
             ++scenario_index) {
            const auto scenario = scenarios[scenario_index];
            const auto base =
                static_cast<std::uint64_t>(scenario.endpoint0) * scenario.endpoint1;
            const auto limit = static_cast<std::uint32_t>(
                std::numeric_limits<std::uint64_t>::max() / base
            );
            auto fixed = factor_small(scenario.endpoint0, spf);
            for (const auto factor : factor_small(scenario.endpoint1, spf)) {
                merge_factor(fixed, factor);
            }
            const auto initial = fixed_profile(fixed);
            for (std::uint32_t multiplier = 1; multiplier <= limit; ++multiplier) {
                auto profile = initial;
                auto remaining = multiplier;
                while (remaining > 1) {
                    const auto prime = spf[remaining] == 0 ? remaining : spf[remaining];
                    std::uint32_t exponent = 0;
                    do {
                        remaining /= prime;
                        ++exponent;
                    } while (remaining % prime == 0);
                    add_prime_power(
                        profile,
                        prime,
                        base_exponent(fixed, prime),
                        exponent
                    );
                }
                const auto d = admissible_pair_count(profile);
                if (d == 0) continue;
                ++eligible[scenario_index];
                if (d > maximum_d[scenario_index]) {
                    maximum_d[scenario_index] = d;
                    maximum_multiplier[scenario_index] = multiplier;
                }
                if (d >= 258) {
                    ++threshold_count[scenario_index];
                    candidates.push_back({
                        scenario_index,
                        multiplier,
                        static_cast<std::uint32_t>(d),
                        base * multiplier,
                    });
                }
            }
        }

        std::ofstream out(argv[1], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output");
        out << "{\n"
            << "  \"schema\":\"C113-cluster-all-endpoints-sieve-v1\",\n"
            << "  \"arithmetic\":\"exact unsigned integers only\",\n"
            << "  \"scenarios\":[\n";
        for (std::size_t index = 0; index < std::size(scenarios); ++index) {
            const auto scenario = scenarios[index];
            const auto base =
                static_cast<std::uint64_t>(scenario.endpoint0) * scenario.endpoint1;
            out << "    {\"index\":" << index
                << ",\"endpoints\":[" << scenario.endpoint0 << ',' << scenario.endpoint1 << ']'
                << ",\"base\":" << base
                << ",\"maximum_multiplier\":"
                << std::numeric_limits<std::uint64_t>::max() / base
                << ",\"eligible_multipliers\":" << eligible[index]
                << ",\"threshold_candidates\":" << threshold_count[index]
                << ",\"maximum_d\":" << maximum_d[index]
                << ",\"maximum_d_multiplier\":" << maximum_multiplier[index] << '}'
                << (index + 1 == std::size(scenarios) ? "\n" : ",\n");
        }
        out << "  ],\n  \"threshold_candidates\":[\n";
        for (std::size_t index = 0; index < candidates.size(); ++index) {
            const auto& row = candidates[index];
            out << "    {\"scenario\":" << row.scenario
                << ",\"multiplier\":" << row.multiplier
                << ",\"d\":" << row.d
                << ",\"product\":" << row.product << '}'
                << (index + 1 == candidates.size() ? "\n" : ",\n");
        }
        out << "  ]\n}\n";
        if (!out) throw std::runtime_error("could not write output");
        std::cout << "maximum_limit=" << maximum_limit
                  << " threshold_candidates=" << candidates.size() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
