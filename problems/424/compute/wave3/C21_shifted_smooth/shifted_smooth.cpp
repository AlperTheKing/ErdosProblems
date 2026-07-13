#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using u128 = unsigned __int128;

constexpr std::uint64_t kScale64 = 1000000000000000000ULL;
constexpr u128 kScale = static_cast<u128>(kScale64);
constexpr std::size_t kBins = 8;

std::string decimal(u128 value) {
    if (value == 0) return "0";
    std::string out;
    while (value != 0) {
        out.push_back(static_cast<char>('0' + value % 10));
        value /= 10;
    }
    std::reverse(out.begin(), out.end());
    return out;
}

struct Bounds {
    u128 lower = 0;
    u128 upper = 0;

    void add(std::uint64_t coefficient, std::uint32_t denominator) {
        const u128 numerator = kScale * static_cast<u128>(coefficient);
        lower += numerator / denominator;
        upper += (numerator + denominator - 1) / denominator;
    }

    void merge(const Bounds& other) {
        lower += other.lower;
        upper += other.upper;
    }
};

std::size_t multiplicity_bin(std::uint32_t value) {
    if (value <= 4) return value;
    if (value <= 7) return 5;
    if (value <= 15) return 6;
    return 7;
}

struct Observation {
    std::uint32_t arithmetic_pairs = 0;
    std::uint32_t witness_pairs = 0;
    std::uint32_t hole_endpoints = 0;
    bool shifted_prime = false;
    bool no_two_mod_three_prime = false;
    bool exceptional_square = false;
    bool fixed_11_prime_block = false;
};

struct Stats {
    std::uint64_t total = 0;
    std::uint64_t present = 0;
    std::uint64_t missing = 0;
    std::uint64_t splitless = 0;
    std::uint64_t blocked = 0;
    std::uint64_t shifted_prime = 0;
    std::uint64_t no_two_mod_three_prime = 0;
    std::uint64_t exceptional_square = 0;
    std::uint64_t unique_blocked = 0;
    std::uint64_t multi_blocked = 0;
    std::uint64_t fixed_11_prime_block = 0;

    Bounds harmonic;
    Bounds present_harmonic;
    Bounds missing_harmonic;
    Bounds splitless_harmonic;
    Bounds blocked_harmonic;
    Bounds shifted_prime_harmonic;
    Bounds unique_blocked_harmonic;
    Bounds multi_blocked_harmonic;
    Bounds fixed_11_prime_block_harmonic;
    Bounds witness_first_moment;
    Bounds witness_second_moment;
    Bounds missing_arithmetic_pair_mass;
    Bounds missing_hole_endpoint_mass;

    std::array<std::uint64_t, kBins> missing_k_counts{};
    std::array<std::uint64_t, kBins> witness_r_counts{};
    std::array<Bounds, kBins> missing_k_harmonic{};
    std::array<Bounds, kBins> witness_r_harmonic{};

    void add(std::uint32_t s, const Observation& row) {
        ++total;
        harmonic.add(1, s);
        witness_first_moment.add(row.witness_pairs, s);
        witness_second_moment.add(
            static_cast<std::uint64_t>(row.witness_pairs) * row.witness_pairs,
            s
        );
        const auto r_bin = multiplicity_bin(row.witness_pairs);
        ++witness_r_counts[r_bin];
        witness_r_harmonic[r_bin].add(1, s);

        if (row.witness_pairs != 0) {
            ++present;
            present_harmonic.add(1, s);
            return;
        }

        ++missing;
        missing_harmonic.add(1, s);
        missing_arithmetic_pair_mass.add(row.arithmetic_pairs, s);
        missing_hole_endpoint_mass.add(row.hole_endpoints, s);
        const auto k_bin = multiplicity_bin(row.arithmetic_pairs);
        ++missing_k_counts[k_bin];
        missing_k_harmonic[k_bin].add(1, s);

        if (row.arithmetic_pairs == 0) {
            ++splitless;
            splitless_harmonic.add(1, s);
        } else {
            ++blocked;
            blocked_harmonic.add(1, s);
            if (row.arithmetic_pairs == 1) {
                ++unique_blocked;
                unique_blocked_harmonic.add(1, s);
            } else {
                ++multi_blocked;
                multi_blocked_harmonic.add(1, s);
            }
        }
        if (row.shifted_prime) {
            ++shifted_prime;
            shifted_prime_harmonic.add(1, s);
        }
        if (row.no_two_mod_three_prime) ++no_two_mod_three_prime;
        if (row.exceptional_square) ++exceptional_square;
        if (row.fixed_11_prime_block) {
            ++fixed_11_prime_block;
            fixed_11_prime_block_harmonic.add(1, s);
        }
    }

    void merge(const Stats& other) {
        total += other.total;
        present += other.present;
        missing += other.missing;
        splitless += other.splitless;
        blocked += other.blocked;
        shifted_prime += other.shifted_prime;
        no_two_mod_three_prime += other.no_two_mod_three_prime;
        exceptional_square += other.exceptional_square;
        unique_blocked += other.unique_blocked;
        multi_blocked += other.multi_blocked;
        fixed_11_prime_block += other.fixed_11_prime_block;
        harmonic.merge(other.harmonic);
        present_harmonic.merge(other.present_harmonic);
        missing_harmonic.merge(other.missing_harmonic);
        splitless_harmonic.merge(other.splitless_harmonic);
        blocked_harmonic.merge(other.blocked_harmonic);
        shifted_prime_harmonic.merge(other.shifted_prime_harmonic);
        unique_blocked_harmonic.merge(other.unique_blocked_harmonic);
        multi_blocked_harmonic.merge(other.multi_blocked_harmonic);
        fixed_11_prime_block_harmonic.merge(other.fixed_11_prime_block_harmonic);
        witness_first_moment.merge(other.witness_first_moment);
        witness_second_moment.merge(other.witness_second_moment);
        missing_arithmetic_pair_mass.merge(other.missing_arithmetic_pair_mass);
        missing_hole_endpoint_mass.merge(other.missing_hole_endpoint_mass);
        for (std::size_t i = 0; i < kBins; ++i) {
            missing_k_counts[i] += other.missing_k_counts[i];
            witness_r_counts[i] += other.witness_r_counts[i];
            missing_k_harmonic[i].merge(other.missing_k_harmonic[i]);
            witness_r_harmonic[i].merge(other.witness_r_harmonic[i]);
        }
    }
};

struct PairRecord {
    std::uint32_t left;
    std::uint32_t right;
    bool left_in_g;
    bool right_in_g;
};

struct Example {
    std::uint32_t s;
    std::uint32_t largest_prime_factor;
    std::uint32_t shifted;
    Observation observation;
    std::vector<PairRecord> pairs;
};

void write_bounds(std::ostream& out, const Bounds& value) {
    out << "{\"lower_numerator\":\"" << decimal(value.lower)
        << "\",\"upper_numerator\":\"" << decimal(value.upper)
        << "\",\"denominator\":\"" << kScale64 << "\"}";
}

void write_bounds_array(
    std::ostream& out,
    const std::array<Bounds, kBins>& values
) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) out << ',';
        write_bounds(out, values[i]);
    }
    out << ']';
}

void write_count_array(
    std::ostream& out,
    const std::array<std::uint64_t, kBins>& values
) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) out << ',';
        out << values[i];
    }
    out << ']';
}

void write_stats(std::ostream& out, const Stats& row) {
    out << "\"counts\":{";
    out << "\"smooth\":" << row.total
        << ",\"T_present\":" << row.present
        << ",\"T_missing\":" << row.missing
        << ",\"splitless\":" << row.splitless
        << ",\"blocked\":" << row.blocked
        << ",\"shifted_prime\":" << row.shifted_prime
        << ",\"no_2mod3_prime\":" << row.no_two_mod_three_prime
        << ",\"exceptional_p2_square\":" << row.exceptional_square
        << ",\"unique_pair_blocked\":" << row.unique_blocked
        << ",\"multi_pair_blocked\":" << row.multi_blocked
        << ",\"fixed_11_times_G2_prime\":" << row.fixed_11_prime_block
        << "},\"harmonic_bounds\":{";
    out << "\"H\":"; write_bounds(out, row.harmonic);
    out << ",\"present\":"; write_bounds(out, row.present_harmonic);
    out << ",\"missing\":"; write_bounds(out, row.missing_harmonic);
    out << ",\"splitless\":"; write_bounds(out, row.splitless_harmonic);
    out << ",\"blocked\":"; write_bounds(out, row.blocked_harmonic);
    out << ",\"shifted_prime\":"; write_bounds(out, row.shifted_prime_harmonic);
    out << ",\"unique_pair_blocked\":"; write_bounds(out, row.unique_blocked_harmonic);
    out << ",\"multi_pair_blocked\":"; write_bounds(out, row.multi_blocked_harmonic);
    out << ",\"fixed_11_times_G2_prime\":";
    write_bounds(out, row.fixed_11_prime_block_harmonic);
    out << ",\"witness_first_moment\":";
    write_bounds(out, row.witness_first_moment);
    out << ",\"witness_second_moment\":";
    write_bounds(out, row.witness_second_moment);
    out << ",\"missing_arithmetic_pair_mass\":";
    write_bounds(out, row.missing_arithmetic_pair_mass);
    out << ",\"missing_hole_endpoint_mass\":";
    write_bounds(out, row.missing_hole_endpoint_mass);
    out << "},\"multiplicity_bins\":{";
    out << "\"labels\":[\"0\",\"1\",\"2\",\"3\",\"4\",\"5-7\",\"8-15\",\"16+\"],";
    out << "\"missing_arithmetic_pair_counts\":";
    write_count_array(out, row.missing_k_counts);
    out << ",\"missing_arithmetic_pair_harmonic\":";
    write_bounds_array(out, row.missing_k_harmonic);
    out << ",\"witness_pair_counts\":";
    write_count_array(out, row.witness_r_counts);
    out << ",\"witness_pair_harmonic\":";
    write_bounds_array(out, row.witness_r_harmonic);
    out << '}';
}

void write_examples(std::ostream& out, const std::vector<Example>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) out << ',';
        const auto& value = values[i];
        out << "{\"s\":" << value.s
            << ",\"largest_prime_factor\":" << value.largest_prime_factor
            << ",\"3s_plus_1\":" << value.shifted
            << ",\"arithmetic_pairs\":" << value.observation.arithmetic_pairs
            << ",\"witness_pairs\":" << value.observation.witness_pairs
            << ",\"hole_endpoints\":" << value.observation.hole_endpoints
            << ",\"pairs\":[";
        for (std::size_t j = 0; j < value.pairs.size(); ++j) {
            if (j != 0) out << ',';
            const auto& pair = value.pairs[j];
            out << "[" << pair.left << ',' << pair.right << ','
                << (pair.left_in_g ? "true" : "false") << ','
                << (pair.right_in_g ? "true" : "false") << ']';
        }
        out << "]}";
    }
    out << ']';
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: shifted_smooth SMOOTH_LIMIT G_BITMAP OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 100 || parsed_limit > 100000000ULL) {
        throw std::runtime_error("SMOOTH_LIMIT must lie in [100, 100000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed_limit);
    const std::uint64_t shifted_limit_64 = 3 * parsed_limit + 1;
    if (shifted_limit_64 > std::numeric_limits<std::uint32_t>::max()) {
        throw std::runtime_error("shifted limit exceeds uint32");
    }
    const auto shifted_limit = static_cast<std::uint32_t>(shifted_limit_64);
    const auto started = std::chrono::steady_clock::now();

    std::ifstream bitmap(argv[2], std::ios::binary | std::ios::ate);
    if (!bitmap) throw std::runtime_error("could not open G bitmap");
    const auto bitmap_size = bitmap.tellg();
    if (bitmap_size < static_cast<std::streamoff>(shifted_limit) + 1) {
        throw std::runtime_error("G bitmap is too short");
    }
    bitmap.seekg(0);
    std::vector<std::uint8_t> member(static_cast<std::size_t>(bitmap_size));
    bitmap.read(
        reinterpret_cast<char*>(member.data()),
        static_cast<std::streamsize>(member.size())
    );
    if (!bitmap) throw std::runtime_error("could not read G bitmap");
    if (!member[2] || !member[3] || member[11]) {
        throw std::runtime_error("seed/missing-11 assertions failed");
    }

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(shifted_limit) + 1);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <= shifted_limit;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= shifted_limit;
             multiple += p) {
            if (spf[multiple] == multiple) spf[multiple] = p;
        }
    }

    std::vector<std::uint32_t> largest_prime_factor(
        static_cast<std::size_t>(limit) + 1,
        1
    );
    for (std::uint32_t n = 2; n <= limit; ++n) {
        const auto p = spf[n];
        largest_prime_factor[n] = std::max(p, largest_prime_factor[n / p]);
    }

    std::vector<std::uint32_t> y_values;
    for (const std::uint32_t value :
         {1000U, 10000U, 100000U, 1000000U, 10000000U, 100000000U}) {
        if (value <= limit) y_values.push_back(value);
    }
    if (y_values.empty() || y_values.back() != limit) y_values.push_back(limit);
    const std::vector<std::uint32_t> z_values = {
        2, 3, 5, 7, 11, 17, 29, 47, 71, 97, 149, 251, 503, 997
    };

    std::vector<std::vector<Stats>> buckets(
        y_values.size(),
        std::vector<Stats>(z_values.size())
    );
    std::vector<Example> splitless_examples;
    std::vector<Example> unique_blocked_examples;
    std::vector<Example> multi_blocked_examples;
    std::vector<Example> fixed_11_examples;

    std::vector<std::uint32_t> divisors;
    divisors.reserve(4096);
    struct PrimePower { std::uint32_t prime; std::uint32_t exponent; };
    std::vector<PrimePower> factorization;
    factorization.reserve(16);

    for (std::uint32_t s = 2; s <= limit; ++s) {
        const auto iy = std::lower_bound(y_values.begin(), y_values.end(), s);
        const auto iz = std::lower_bound(
            z_values.begin(),
            z_values.end(),
            largest_prime_factor[s]
        );
        if (iy == y_values.end() || iz == z_values.end()) continue;

        const std::uint32_t shifted = 3 * s + 1;
        std::uint32_t remaining = shifted;
        divisors.clear();
        divisors.push_back(1);
        factorization.clear();
        while (remaining > 1) {
            const std::uint32_t prime = spf[remaining];
            const std::size_t old_size = divisors.size();
            std::uint32_t power = 1;
            std::uint32_t exponent = 0;
            do {
                remaining /= prime;
                power *= prime;
                ++exponent;
                for (std::size_t i = 0; i < old_size; ++i) {
                    divisors.push_back(divisors[i] * power);
                }
            } while (remaining > 1 && spf[remaining] == prime);
            factorization.push_back(PrimePower{prime, exponent});
        }

        Observation observation;
        observation.shifted_prime =
            factorization.size() == 1 && factorization[0].exponent == 1;
        observation.no_two_mod_three_prime = std::all_of(
            factorization.begin(), factorization.end(),
            [](const PrimePower& item) { return item.prime % 3 == 1; }
        );
        observation.exceptional_square =
            factorization.size() == 1 &&
            factorization[0].exponent == 2 &&
            factorization[0].prime % 3 == 2;

        std::uint32_t two_mod_three_divisors = 0;
        bool equal_two_mod_three_square = false;
        std::vector<PairRecord> pair_records;
        for (const auto left : divisors) {
            if (left % 3 == 2) ++two_mod_three_divisors;
            if (static_cast<std::uint64_t>(left) * left == shifted &&
                left % 3 == 2) {
                equal_two_mod_three_square = true;
            }
            if (left < 2) continue;
            const auto right = shifted / left;
            if (left >= right) continue;
            if (left % 3 != 2 || right % 3 != 2) continue;
            ++observation.arithmetic_pairs;
            const bool left_in_g = member[left] != 0;
            const bool right_in_g = member[right] != 0;
            if (left_in_g && right_in_g) ++observation.witness_pairs;
            if (!left_in_g) ++observation.hole_endpoints;
            if (!right_in_g) ++observation.hole_endpoints;
            if (largest_prime_factor[s] <= 97) {
                pair_records.push_back(PairRecord{
                    left, right, left_in_g, right_in_g
                });
            }
        }
        std::sort(
            pair_records.begin(), pair_records.end(),
            [](const PairRecord& a, const PairRecord& b) {
                return a.left < b.left;
            }
        );

        if (two_mod_three_divisors !=
            2 * observation.arithmetic_pairs +
                (equal_two_mod_three_square ? 1U : 0U)) {
            throw std::runtime_error("divisor involution identity failed");
        }
        const bool splitless_characterization =
            observation.no_two_mod_three_prime || observation.exceptional_square;
        if ((observation.arithmetic_pairs == 0) != splitless_characterization) {
            throw std::runtime_error("splitless characterization failed");
        }
        if (observation.hole_endpoints <
                observation.arithmetic_pairs - observation.witness_pairs ||
            observation.hole_endpoints >
                2 * (observation.arithmetic_pairs - observation.witness_pairs)) {
            throw std::runtime_error("blocker endpoint inequality failed");
        }
        const bool t_member = member[3 * s] != 0;
        if (t_member != (observation.witness_pairs != 0)) {
            throw std::runtime_error("T/witness equivalence failed");
        }

        if (shifted % 11 == 0) {
            const auto other = shifted / 11;
            observation.fixed_11_prime_block =
                other != 11 && spf[other] == other && member[other] &&
                observation.arithmetic_pairs == 1 &&
                observation.witness_pairs == 0;
        }

        buckets[
            static_cast<std::size_t>(iy - y_values.begin())
        ][
            static_cast<std::size_t>(iz - z_values.begin())
        ].add(s, observation);

        if (largest_prime_factor[s] <= 97) {
            const Example example{
                s, largest_prime_factor[s], shifted, observation, pair_records
            };
            if (observation.arithmetic_pairs == 0 &&
                splitless_examples.size() < 12) {
                splitless_examples.push_back(example);
            }
            if (observation.witness_pairs == 0 &&
                observation.arithmetic_pairs == 1 &&
                unique_blocked_examples.size() < 12) {
                unique_blocked_examples.push_back(example);
            }
            if (observation.witness_pairs == 0 &&
                observation.arithmetic_pairs >= 2 &&
                multi_blocked_examples.size() < 12) {
                multi_blocked_examples.push_back(example);
            }
            if (observation.fixed_11_prime_block && fixed_11_examples.size() < 12) {
                fixed_11_examples.push_back(example);
            }
        }
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::ofstream out(argv[3]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n";
    out << "\"schema_version\":1,";
    out << "\"smooth_limit\":" << limit << ',';
    out << "\"G_bitmap_bytes\":" << member.size() << ',';
    out << "\"fixed_point_denominator\":\"" << kScale64 << "\",";
    out << "\"bin_labels\":[\"0\",\"1\",\"2\",\"3\",\"4\",\"5-7\",\"8-15\",\"16+\"],";
    out << "\"assertions\":["
        << "\"T(s) iff witness_pairs(s)>0 for every analyzed s\","
        << "\"K(s)=0 iff 3s+1 has no 2mod3 prime divisor or equals p^2 with p=2mod3\","
        << "\"K-R <= hole_endpoints <= 2(K-R) pointwise\","
        << "\"#2mod3 divisors = 2K plus the excluded equal-square indicator\"],";
    out << "\"rows\":[";
    bool first_row = true;
    for (std::size_t i = 0; i < y_values.size(); ++i) {
        for (std::size_t j = 0; j < z_values.size(); ++j) {
            Stats aggregate;
            for (std::size_t a = 0; a <= i; ++a) {
                for (std::size_t b = 0; b <= j; ++b) {
                    aggregate.merge(buckets[a][b]);
                }
            }
            if (!first_row) out << ',';
            first_row = false;
            out << "{\"y\":" << y_values[i]
                << ",\"z\":" << z_values[j] << ',';
            write_stats(out, aggregate);
            out << '}';
        }
    }
    out << "],\"examples\":{";
    out << "\"splitless\":"; write_examples(out, splitless_examples);
    out << ",\"unique_pair_blocked\":"; write_examples(out, unique_blocked_examples);
    out << ",\"multi_pair_blocked\":"; write_examples(out, multi_blocked_examples);
    out << ",\"fixed_11_times_G2_prime\":"; write_examples(out, fixed_11_examples);
    out << "},\"elapsed_seconds\":" << elapsed.count() << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "smooth_limit=" << limit
              << " G_bitmap_bytes=" << member.size()
              << " rows=" << y_values.size() * z_values.size()
              << " elapsed_seconds=" << elapsed.count() << '\n';
    return 0;
}
