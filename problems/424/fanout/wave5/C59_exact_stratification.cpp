#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

std::uint32_t shell_of(std::uint32_t n) {
    if (n < 2) return 0;
    return std::bit_width(n - 1U);
}

struct Shell {
    std::uint64_t holes = 0;
    std::uint64_t splitless = 0;
    std::uint64_t reducible = 0;
    std::uint64_t odd = 0;
    std::uint64_t seed3 = 0;
    std::uint64_t hard = 0;
    std::uint64_t hard_pair_mass = 0;
    std::vector<std::uint64_t> hard_by_pairs = std::vector<std::uint64_t>(1, 0);
    std::uint64_t ap_hard_shape = 0;
    std::uint64_t ap_pairs_le_shell_index = 0;
    std::uint32_t ap_max_pairs = 0;
};

std::uint64_t interval_capacity(std::uint64_t x, std::uint64_t p) {
    return (x + 1) / p - (x / 2 + 1) / p;
}

void write_fraction(
    std::ostream& out,
    std::uint64_t numerator,
    std::uint64_t denominator
) {
    out << "{\"numerator\":" << numerator
        << ",\"denominator\":" << denominator;
    if (denominator != 0) {
        out << ",\"decimal\":"
            << static_cast<long double>(numerator) /
                   static_cast<long double>(denominator);
    }
    out << "}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: C59_exact_stratification LIMIT OUTPUT.json\n";
        return 2;
    }
    const std::uint64_t parsed = std::stoull(argv[1]);
    if (parsed < 128 || parsed > (1ULL << 30)) {
        throw std::runtime_error("LIMIT must lie in [128,2^30]");
    }
    if ((parsed & (parsed - 1)) != 0) {
        throw std::runtime_error("LIMIT must be a power of two");
    }
    const auto limit = static_cast<std::uint32_t>(parsed);
    const std::uint32_t max_shell = std::bit_width(limit) - 1U;

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <=
             static_cast<std::uint64_t>(limit) + 1;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t k = static_cast<std::uint64_t>(p) * p;
             k <= static_cast<std::uint64_t>(limit) + 1;
             k += p) {
            if (spf[k] == k) spf[k] = p;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint8_t> hole(static_cast<std::size_t>(limit) + 1, 0);
    member[2] = member[3] = 1;
    std::vector<Shell> shells(static_cast<std::size_t>(max_shell) + 1);
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);

    for (std::uint32_t n = 4; n <= limit; ++n) {
        if (!allowed(n)) continue;
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

        bool has_pair = false;
        bool generated = false;
        std::uint32_t pair_count = 0;
        for (const std::uint32_t a : divisors) {
            if (a < 2) continue;
            const std::uint32_t b = product / a;
            if (a >= b || !allowed(a) || !allowed(b)) continue;
            has_pair = true;
            ++pair_count;
            if (member[a] && member[b]) generated = true;
        }
        if (n % 30 == 24 && has_pair) {
            Shell& ap_shell = shells[shell_of(n)];
            ++ap_shell.ap_hard_shape;
            if (pair_count <= shell_of(n)) {
                ++ap_shell.ap_pairs_le_shell_index;
            }
            ap_shell.ap_max_pairs = std::max(ap_shell.ap_max_pairs, pair_count);
        }
        if (generated) {
            member[n] = 1;
            continue;
        }

        hole[n] = 1;
        Shell& shell = shells[shell_of(n)];
        ++shell.holes;
        if (!has_pair) {
            ++shell.splitless;
            continue;
        }

        ++shell.reducible;
        if ((n & 1U) != 0) {
            ++shell.odd;
        } else if (
            (n + 1) % 3 == 0 &&
            allowed((n + 1) / 3) &&
            (n + 1) / 3 != 3
        ) {
            ++shell.seed3;
        } else {
            ++shell.hard;
            shell.hard_pair_mass += pair_count;
            if (shell.hard_by_pairs.size() <= pair_count) {
                shell.hard_by_pairs.resize(
                    static_cast<std::size_t>(pair_count) + 1,
                    0
                );
            }
            ++shell.hard_by_pairs[pair_count];
        }
    }

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output");
    out << "{\n  \"schema_version\":1,\n"
        << "  \"limit\":" << limit << ",\n"
        << "  \"arithmetic\":\"exact integer recursion; a<b enforced\",\n"
        << "  \"shells\":[\n";

    bool first_shell = true;
    for (std::uint32_t j = 7; j <= max_shell; ++j) {
        const std::uint64_t x = 1ULL << j;
        const Shell& row = shells[j];
        const Shell& parent = shells[j - 1];
        const std::uint64_t q = parent.holes - row.odd;

        std::uint64_t actual_capacity = 0;
        std::uint64_t ambient_capacity = 0;
        std::uint64_t structural_prime_capacity = 0;
        const std::uint64_t umax = (x + 6) / 10;
        for (std::uint64_t u = 2; u <= umax; ++u) {
            if (!allowed(static_cast<std::uint32_t>(u))) continue;
            const std::uint64_t cap = interval_capacity(x, 2 * u - 1);
            ambient_capacity += cap;
            if (hole[u]) actual_capacity += cap;
            if (spf[u + 1] == u + 1 && (u + 1) % 3 == 1) {
                structural_prime_capacity += cap;
            }
        }
        if (row.hard_pair_mass > actual_capacity) {
            throw std::runtime_error("C55 incidence inequality failed");
        }

        std::uint32_t max_pairs =
            static_cast<std::uint32_t>(row.hard_by_pairs.size() - 1);
        while (max_pairs > 0 && row.hard_by_pairs[max_pairs] == 0) {
            --max_pairs;
        }

        if (!first_shell) out << ",\n";
        first_shell = false;
        out << "    {\"j\":" << j
            << ",\"X\":" << x
            << ",\"m_parent\":" << parent.holes
            << ",\"m\":" << row.holes
            << ",\"e\":" << row.splitless
            << ",\"r\":" << row.reducible
            << ",\"s\":" << row.seed3
            << ",\"h\":" << row.hard
            << ",\"q\":" << q
            << ",\"hard_pair_mass\":" << row.hard_pair_mass
            << ",\"actual_hole_capacity\":" << actual_capacity
            << ",\"ambient_allowed_capacity\":" << ambient_capacity
            << ",\"structural_prime_capacity\":"
            << structural_prime_capacity
            << ",\"max_pairs\":" << max_pairs
            << ",\"ap_hard_shape\":" << row.ap_hard_shape
            << ",\"ap_pairs_le_shell_index\":"
            << row.ap_pairs_le_shell_index
            << ",\"ap_max_pairs\":" << row.ap_max_pairs
            << ",\"theta\":";
        write_fraction(out, row.reducible, parent.holes);
        out << ",\"pair_histogram\":[";
        bool first_hist = true;
        for (std::uint32_t d = 1; d <= max_pairs; ++d) {
            if (row.hard_by_pairs[d] == 0) continue;
            if (!first_hist) out << ',';
            first_hist = false;
            out << "{\"pairs\":" << d
                << ",\"count\":" << row.hard_by_pairs[d] << "}";
        }
        out << "],\"thresholds\":[";
        std::uint64_t low = 0;
        bool first_threshold = true;
        const std::uint32_t threshold_limit = std::max(max_pairs, 2U * j);
        for (std::uint32_t d = 0; d <= threshold_limit; ++d) {
            if (d > 0 && d < row.hard_by_pairs.size()) {
                low += row.hard_by_pairs[d];
            }
            const std::uint64_t high = row.hard - low;
            const std::uint64_t divisor = static_cast<std::uint64_t>(d) + 1;
            if (divisor * high > actual_capacity) {
                throw std::runtime_error("threshold incidence inequality failed");
            }
            const std::uint64_t upper_numerator =
                divisor * (parent.holes + row.seed3 + low - q) +
                actual_capacity;
            const std::uint64_t upper_denominator = divisor * parent.holes;
            if (!first_threshold) out << ',';
            first_threshold = false;
            out << "{\"D\":" << d
                << ",\"low_pair_hard\":" << low
                << ",\"high_pair_hard\":" << high
                << ",\"high_bound_numerator\":" << actual_capacity
                << ",\"high_bound_denominator\":" << divisor
                << ",\"finite_theta_upper\":";
            write_fraction(out, upper_numerator, upper_denominator);
            out << "}";
        }
        out << "]}";
    }
    out << "\n  ]\n}\n";
    return 0;
}
