#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using u32 = std::uint32_t;
using u64 = std::uint64_t;

namespace {

constexpr u32 kCheckpoint = 10'000'000;
const std::vector<u32> kThresholds{1, 2, 4, 8, 16, 32, 64, 128, 256};

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

struct Factorization {
    std::vector<std::pair<u32, u32>> prime_powers;
    std::vector<u32> divisors;
    u32 omega = 0;
    u32 tau = 1;
};

Factorization factorize(u32 value, const std::vector<u32>& spf) {
    Factorization result;
    result.divisors.push_back(1);
    u32 remaining = value;
    while (remaining > 1) {
        const u32 prime = spf[remaining];
        u32 exponent = 0;
        u32 power = 1;
        const std::size_t old_size = result.divisors.size();
        do {
            remaining /= prime;
            ++exponent;
            ++result.omega;
            power *= prime;
            for (std::size_t i = 0; i < old_size; ++i) {
                result.divisors.push_back(result.divisors[i] * power);
            }
        } while (remaining > 1 && spf[remaining] == prime);
        result.prime_powers.emplace_back(prime, exponent);
        result.tau *= exponent + 1;
    }
    require(result.divisors.size() == result.tau, "divisor count disagrees with tau");
    return result;
}

std::vector<u32> smallest_prime_factors(u32 limit) {
    std::vector<u32> spf(static_cast<std::size_t>(limit) + 1);
    std::iota(spf.begin(), spf.end(), 0U);
    for (u32 prime = 2; static_cast<u64>(prime) * prime <= limit; ++prime) {
        if (spf[prime] != prime) continue;
        for (u64 multiple = static_cast<u64>(prime) * prime; multiple <= limit;
             multiple += prime) {
            if (spf[multiple] == multiple) spf[multiple] = prime;
        }
    }
    return spf;
}

struct MembershipResult {
    std::vector<std::uint8_t> reached;
    u64 count = 0;
    u64 checkpoint_count = 0;
};

MembershipResult build_membership(u32 limit, const std::vector<u32>& spf) {
    MembershipResult result;
    result.reached.assign(static_cast<std::size_t>(limit) + 1, 0);
    if (limit >= 2) {
        result.reached[2] = 1;
        ++result.count;
    }
    if (limit >= 3) {
        result.reached[3] = 1;
        ++result.count;
    }

    for (u32 n = 4; n <= limit; ++n) {
        const auto factors = factorize(n + 1, spf);
        for (const u32 left : factors.divisors) {
            if (left < 2) continue;
            const u32 right = (n + 1) / left;
            if (left >= right) continue;
            if (result.reached[left] && result.reached[right]) {
                result.reached[n] = 1;
                ++result.count;
                break;
            }
        }
        if (n == kCheckpoint) result.checkpoint_count = result.count;
    }
    return result;
}

u32 primorial_up_to(u32 z, const std::vector<u32>& spf) {
    u32 product = 1;
    for (u32 value = 2; value <= z; ++value) {
        if (spf[value] == value) product *= value;
    }
    return product;
}

struct PairInfo {
    u32 left;
    u32 right;
    bool left_in_g;
    bool right_in_g;
};

struct PairAnalysis {
    u32 omega = 0;
    u32 tau = 0;
    u32 residue_two_divisors = 0;
    u32 generated_residue_two_divisors = 0;
    u32 admissible_pairs = 0;
    u32 witness_pairs = 0;
    u32 covered_pairs = 0;
    u32 both_missing_pairs = 0;
    bool equal_residue_two_divisor = false;
};

PairAnalysis analyze_pairs(
    u32 product,
    const Factorization& factors,
    const std::vector<std::uint8_t>& reached
) {
    PairAnalysis analysis;
    analysis.omega = factors.omega;
    analysis.tau = factors.tau;
    for (const u32 left : factors.divisors) {
        if (left % 3 != 2) continue;
        ++analysis.residue_two_divisors;
        if (reached[left]) ++analysis.generated_residue_two_divisors;
        const u32 right = product / left;
        if (left == right) {
            analysis.equal_residue_two_divisor = true;
            continue;
        }
        if (left > right) continue;
        require(right % 3 == 2, "residue-two divisor has wrong complementary residue");
        ++analysis.admissible_pairs;
        const bool left_in_g = reached[left] != 0;
        const bool right_in_g = reached[right] != 0;
        if (left_in_g && right_in_g) ++analysis.witness_pairs;
        if (left_in_g || right_in_g) ++analysis.covered_pairs;
        if (!left_in_g && !right_in_g) ++analysis.both_missing_pairs;
    }

    require(
        2 * analysis.admissible_pairs
                + static_cast<u32>(analysis.equal_residue_two_divisor)
            == analysis.residue_two_divisors,
        "residue-two divisors do not pair exactly"
    );
    require(
        3 * analysis.residue_two_divisors >= analysis.tau,
        "divisor-character bound D_2 >= tau/3 failed"
    );
    require(
        6 * analysis.admissible_pairs + 3 >= analysis.tau,
        "admissible-pair bound A >= tau/6 - 1/2 failed"
    );
    require(
        6 * analysis.admissible_pairs + 2 >= analysis.omega,
        "admissible-pair bound A >= (Omega-2)/6 failed"
    );
    require(
        analysis.covered_pairs + analysis.both_missing_pairs
            == analysis.admissible_pairs,
        "covered and both-missing pairs do not partition admissible pairs"
    );
    return analysis;
}

struct Record {
    u32 r = 0;
    u32 product = 0;
    u32 omega = 0;
    u32 tau = 0;
    u32 residue_two_divisors = 0;
    u32 generated_residue_two_divisors = 0;
    u32 admissible_pairs = 0;
    u32 covered_pairs = 0;
    u32 both_missing_pairs = 0;
    std::vector<std::pair<u32, u32>> prime_powers;
    std::vector<PairInfo> blocked_pairs;
};

Record make_record(
    u32 r,
    const Factorization& factors,
    const PairAnalysis& analysis,
    const std::vector<std::uint8_t>& reached,
    bool include_pairs
) {
    Record record;
    record.r = r;
    record.product = 3 * r + 1;
    record.omega = analysis.omega;
    record.tau = analysis.tau;
    record.residue_two_divisors = analysis.residue_two_divisors;
    record.generated_residue_two_divisors =
        analysis.generated_residue_two_divisors;
    record.admissible_pairs = analysis.admissible_pairs;
    record.covered_pairs = analysis.covered_pairs;
    record.both_missing_pairs = analysis.both_missing_pairs;
    record.prime_powers = factors.prime_powers;
    if (include_pairs) {
        for (const u32 left : factors.divisors) {
            const u32 right = record.product / left;
            if (left >= right || left % 3 != 2) continue;
            require(right % 3 == 2, "recorded pair has wrong residue");
            record.blocked_pairs.push_back(
                {left, right, reached[left] != 0, reached[right] != 0}
            );
        }
        std::sort(
            record.blocked_pairs.begin(),
            record.blocked_pairs.end(),
            [](const PairInfo& first, const PairInfo& second) {
                return first.left < second.left;
            }
        );
        require(
            record.blocked_pairs.size() == record.admissible_pairs,
            "recorded pair list has wrong size"
        );
    }
    return record;
}

struct Row {
    u32 cutoff;
    u32 z;
    u32 primorial;
    u64 rough_count = 0;
    u64 member_count = 0;
    u64 miss_count = 0;
    u64 strict_divisor_majority_certificates = 0;
    u32 maximum_pairs_all = 0;
    std::map<u32, u64> all_below;
    std::map<u32, u64> misses_below;
    std::map<u32, std::optional<Record>> first_miss_at_least;
    std::optional<Record> maximum_miss;
    u64 misses_with_every_pair_covered = 0;
    std::optional<Record> maximum_fully_covered_miss;

    Row(u32 cutoff_value, u32 z_value, u32 primorial_value)
        : cutoff(cutoff_value), z(z_value), primorial(primorial_value) {
        for (const u32 threshold : kThresholds) {
            all_below.emplace(threshold, 0);
            misses_below.emplace(threshold, 0);
            first_miss_at_least.emplace(threshold, std::nullopt);
        }
    }
};

void update_row(
    Row& row,
    u32 r,
    const Factorization& factors,
    const PairAnalysis& analysis,
    const std::vector<std::uint8_t>& reached
) {
    ++row.rough_count;
    row.maximum_pairs_all = std::max(row.maximum_pairs_all, analysis.admissible_pairs);
    for (const u32 threshold : kThresholds) {
        if (analysis.admissible_pairs < threshold) ++row.all_below[threshold];
    }

    const bool member = analysis.witness_pairs > 0;
    const u32 no_witness_generated_divisor_capacity =
        analysis.admissible_pairs
        + static_cast<u32>(analysis.equal_residue_two_divisor);
    if (analysis.generated_residue_two_divisors
        > no_witness_generated_divisor_capacity) {
        require(member, "strict divisor-majority certificate is not a T-member");
        ++row.strict_divisor_majority_certificates;
    }
    require(
        member == (reached[3 * r] != 0),
        "T membership disagrees with all-G2-factor-pair recursion"
    );
    if (member) {
        ++row.member_count;
        return;
    }

    ++row.miss_count;
    const u32 missing_residue_two_divisors =
        analysis.residue_two_divisors - analysis.generated_residue_two_divisors;
    require(
        missing_residue_two_divisors >= analysis.admissible_pairs,
        "a T-miss has fewer than one missing endpoint per pair"
    );
    if (analysis.covered_pairs == analysis.admissible_pairs) {
        ++row.misses_with_every_pair_covered;
        if (!row.maximum_fully_covered_miss.has_value()
            || analysis.admissible_pairs
                > row.maximum_fully_covered_miss->admissible_pairs) {
            row.maximum_fully_covered_miss =
                make_record(r, factors, analysis, reached, true);
        }
    }
    for (const u32 threshold : kThresholds) {
        if (analysis.admissible_pairs < threshold) ++row.misses_below[threshold];
        auto& first = row.first_miss_at_least[threshold];
        if (analysis.admissible_pairs >= threshold && !first.has_value()) {
            first = make_record(r, factors, analysis, reached, false);
        }
    }
    if (!row.maximum_miss.has_value()
        || analysis.admissible_pairs > row.maximum_miss->admissible_pairs) {
        row.maximum_miss = make_record(r, factors, analysis, reached, true);
    }
}

void write_factorization(
    std::ostream& output, const std::vector<std::pair<u32, u32>>& factors
) {
    output << "[";
    for (std::size_t i = 0; i < factors.size(); ++i) {
        if (i) output << ",";
        output << "{\"prime\":" << factors[i].first
               << ",\"exponent\":" << factors[i].second << "}";
    }
    output << "]";
}

void write_record(std::ostream& output, const Record& record, bool include_pairs) {
    output << "{\"r\":" << record.r
           << ",\"3r_plus_1\":" << record.product
           << ",\"Omega\":" << record.omega
           << ",\"tau\":" << record.tau
           << ",\"residue_two_divisors\":" << record.residue_two_divisors
           << ",\"generated_residue_two_divisors\":"
           << record.generated_residue_two_divisors
           << ",\"admissible_pairs\":" << record.admissible_pairs
           << ",\"pairs_with_at_least_one_G_endpoint\":" << record.covered_pairs
           << ",\"pairs_with_both_endpoints_missing\":" << record.both_missing_pairs
           << ",\"factorization\":";
    write_factorization(output, record.prime_powers);
    if (include_pairs) {
        output << ",\"blocked_pairs\":[";
        for (std::size_t i = 0; i < record.blocked_pairs.size(); ++i) {
            if (i) output << ",";
            const auto& pair = record.blocked_pairs[i];
            output << "{\"a\":" << pair.left << ",\"b\":" << pair.right
                   << ",\"a_in_G\":" << (pair.left_in_g ? "true" : "false")
                   << ",\"b_in_G\":" << (pair.right_in_g ? "true" : "false")
                   << "}";
        }
        output << "]";
    }
    output << "}";
}

void write_row(std::ostream& output, const Row& row) {
    require(row.member_count + row.miss_count == row.rough_count, "row partition failed");
    require(row.maximum_miss.has_value(), "row has no missing rough candidate");
    output << "{\n"
           << "      \"R\":" << row.cutoff << ",\n"
           << "      \"z\":" << row.z << ",\n"
           << "      \"P_z\":" << row.primorial << ",\n"
           << "      \"rough_count\":" << row.rough_count << ",\n"
           << "      \"T_member_count\":" << row.member_count << ",\n"
           << "      \"T_miss_count\":" << row.miss_count << ",\n"
           << "      \"strict_divisor_majority_certificates\":"
           << row.strict_divisor_majority_certificates << ",\n"
           << "      \"maximum_admissible_pairs_all\":" << row.maximum_pairs_all
           << ",\n"
           << "      \"counts_with_admissible_pairs_below\":{";
    bool first_entry = true;
    for (const u32 threshold : kThresholds) {
        if (!first_entry) output << ",";
        first_entry = false;
        output << "\"" << threshold << "\":" << row.all_below.at(threshold);
    }
    output << "},\n      \"miss_counts_with_admissible_pairs_below\":{";
    first_entry = true;
    for (const u32 threshold : kThresholds) {
        if (!first_entry) output << ",";
        first_entry = false;
        output << "\"" << threshold << "\":" << row.misses_below.at(threshold);
    }
    output << "},\n      \"first_miss_with_at_least\":{";
    first_entry = true;
    for (const u32 threshold : kThresholds) {
        const auto& record = row.first_miss_at_least.at(threshold);
        if (!record.has_value()) continue;
        if (!first_entry) output << ",";
        first_entry = false;
        output << "\"" << threshold << "\":";
        write_record(output, *record, false);
    }
    output << "},\n      \"maximum_pair_miss\":";
    write_record(output, *row.maximum_miss, true);
    output << ",\n      \"misses_with_every_pair_covered\":"
           << row.misses_with_every_pair_covered
           << ",\n      \"maximum_fully_covered_miss\":";
    require(
        row.maximum_fully_covered_miss.has_value(),
        "row has no fully covered missing candidate"
    );
    write_record(output, *row.maximum_fully_covered_miss, true);
    output << "\n    }";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: shifted_sifted_audit OUTPUT_JSON\n";
        return 2;
    }

    const std::vector<std::pair<u32, u32>> specs{
        {200'000, 9}, {2'000'000, 11}, {6'666'666, 11}
    };
    const u32 maximum_r = specs.back().first;
    const u32 membership_limit = 3 * maximum_r;
    const auto spf = smallest_prime_factors(membership_limit + 1);
    const auto membership = build_membership(membership_limit, spf);

    require(membership.checkpoint_count == 4'952'270, "G count through 1e7 changed");
    require(membership.reached[2] && membership.reached[3], "seeds missing");
    require(!membership.reached[4] && !membership.reached[8]
            && !membership.reached[24], "distinct-input sentinels changed");
    require(membership.reached[51] && !membership.reached[57]
            && membership.reached[69] && !membership.reached[35],
            "C11 low-factor-pair sentinels changed");

    std::vector<Row> rows;
    rows.reserve(specs.size());
    for (const auto [cutoff, z] : specs) {
        rows.emplace_back(cutoff, z, primorial_up_to(z, spf));
    }

    u64 analyzed_candidates = 0;
    for (u32 r = 2; r <= maximum_r; ++r) {
        bool needed = false;
        for (const auto& row : rows) {
            if (r <= row.cutoff && std::gcd(r, row.primorial) == 1) {
                needed = true;
                break;
            }
        }
        if (!needed) continue;

        const u32 product = 3 * r + 1;
        const auto factors = factorize(product, spf);
        const auto analysis = analyze_pairs(product, factors, membership.reached);
        ++analyzed_candidates;
        for (auto& row : rows) {
            if (r <= row.cutoff && std::gcd(r, row.primorial) == 1) {
                update_row(row, r, factors, analysis, membership.reached);
            }
        }
    }

    std::ofstream output(argv[1]);
    if (!output) throw std::runtime_error("could not open output JSON");
    output << "{\n"
           << "  \"schema_version\":1,\n"
           << "  \"definitions\":\"A(r)=# distinct pairs 2<=a<b, ab=3r+1, a congruent b congruent 2 (mod 3); witness requires a,b in G2\",\n"
           << "  \"membership_limit\":" << membership_limit << ",\n"
           << "  \"G_count_through_membership_limit\":" << membership.count << ",\n"
           << "  \"G_count_through_10000000\":" << membership.checkpoint_count
           << ",\n"
           << "  \"analyzed_distinct_candidates\":" << analyzed_candidates << ",\n"
           << "  \"exact_checks\":{\n"
           << "    \"D2_at_least_tau_over_3_every_candidate\":true,\n"
           << "    \"A_at_least_tau_over_6_minus_half_every_candidate\":true,\n"
           << "    \"A_at_least_Omega_minus_2_over_6_every_candidate\":true,\n"
           << "    \"every_T_miss_has_at_least_one_missing_endpoint_per_pair\":true,\n"
           << "    \"strict_divisor_majority_implies_T_every_candidate\":true,\n"
           << "    \"T_iff_nonempty_G2_witness_every_candidate\":true,\n"
           << "    \"reference_G_count_through_10000000_matched\":true,\n"
           << "    \"distinct_input_sentinels_4_8_24_absent\":true\n"
           << "  },\n"
           << "  \"rows\":[\n";
    for (std::size_t i = 0; i < rows.size(); ++i) {
        if (i) output << ",\n";
        write_row(output, rows[i]);
    }
    output << "\n  ]\n}\n";
    require(static_cast<bool>(output), "failed while writing output JSON");

    std::cout << "membership_limit=" << membership_limit
              << " G_count=" << membership.count
              << " analyzed=" << analyzed_candidates << "\n";
    for (const auto& row : rows) {
        std::cout << "R=" << row.cutoff << " z=" << row.z
                  << " rough=" << row.rough_count << " miss=" << row.miss_count
                  << " max_miss_pairs=" << row.maximum_miss->admissible_pairs
                  << " at_r=" << row.maximum_miss->r << "\n";
    }
    return 0;
}
