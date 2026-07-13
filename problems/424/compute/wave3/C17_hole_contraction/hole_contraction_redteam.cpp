#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <boost/multiprecision/cpp_int.hpp>

namespace {

using boost::multiprecision::cpp_int;
using boost::multiprecision::uint128_t;

constexpr std::uint64_t kWeightScale = 1ULL << 30;
constexpr std::uint16_t kNoRank = 0xffffU;

struct Rational {
    cpp_int numerator;
    cpp_int denominator;
};

struct ShellRow {
    std::uint32_t upper;
    std::uint64_t all_max_num;
    std::uint32_t all_arg;
    std::uint64_t composite_max_num;
    std::uint32_t composite_arg;
    std::uint64_t composite_envelope_num;
    std::uint64_t all_envelope_num;
    std::uint32_t missing_count;
    std::uint32_t composite_missing_count;
};

struct Snapshot {
    std::uint32_t x;
    std::uint64_t generated;
    std::uint64_t missing;
    std::uint64_t splitless;
    std::uint64_t reducible;
    std::uint64_t odd_reducible;
    std::uint64_t seed3_even_reducible;
    std::uint64_t hard_reducible;
    std::uint64_t seed2_healed;
    std::uint64_t missing_half;
    std::uint64_t direct_num;
    std::uint64_t direct_den;
    Rational reciprocal_charge;
    std::uint64_t fixed_point_charge_num;
    std::uint64_t prime_charge_num;
    std::uint64_t composite_charge_num;
    std::uint64_t all_envelope_bound_num;
    std::uint64_t composite_envelope_bound_num;
    std::uint64_t exceptional_recurrence_slack_num;
    Rational all_theta;
    Rational composite_theta;
    std::uint32_t forced_seed_max;
    std::uint32_t forced_seed_arg;
    std::vector<std::uint64_t> rank_histogram;
    std::vector<std::uint64_t> healing_rank_histogram;
    std::vector<ShellRow> shells;
};

struct RankCapAudit {
    std::uint16_t cap;
    std::uint64_t healed;
    std::uint32_t first_failure_x;
    std::uint32_t last_failure_x;
    std::uint64_t maximum_excess;
    std::uint32_t maximum_excess_x;
};

bool is_allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

cpp_int gcd_big(cpp_int a, cpp_int b) {
    while (b != 0) {
        const cpp_int r = a % b;
        a = b;
        b = r;
    }
    return a;
}

Rational reduce(Rational value) {
    if (value.numerator == 0) return Rational{0, 1};
    const cpp_int divisor = gcd_big(value.numerator, value.denominator);
    value.numerator /= divisor;
    value.denominator /= divisor;
    return value;
}

Rational incidence_sum(const std::vector<std::uint64_t>& counts) {
    cpp_int denominator = 1;
    for (std::size_t d = 1; d < counts.size(); ++d) {
        if (counts[d] == 0) continue;
        const std::uint64_t remainder =
            (denominator % static_cast<std::uint64_t>(d)).convert_to<std::uint64_t>();
        const std::uint64_t divisor = std::gcd<std::uint64_t>(d, remainder);
        denominator *= static_cast<std::uint64_t>(d) / divisor;
    }

    cpp_int numerator = 0;
    for (std::size_t d = 1; d < counts.size(); ++d) {
        if (counts[d] == 0) continue;
        numerator += cpp_int(counts[d]) * (denominator / d);
    }
    return reduce(Rational{numerator, denominator});
}

Rational weighted_theta(const std::vector<std::uint64_t>& envelope) {
    if (envelope.empty()) return Rational{0, 1};
    const std::size_t depth = envelope.size();
    cpp_int numerator = 0;
    std::uint64_t previous = 0;
    for (std::size_t index = 0; index < depth; ++index) {
        const std::uint64_t increment = envelope[index] - previous;
        numerator += cpp_int(increment) << (depth - index - 1);
        previous = envelope[index];
    }
    const cpp_int denominator = cpp_int(kWeightScale) << depth;
    return reduce(Rational{numerator, denominator});
}

std::string to_string(const cpp_int& value) {
    return value.convert_to<std::string>();
}

void ensure_size(std::vector<std::uint64_t>& values, std::size_t index) {
    if (values.size() <= index) values.resize(index + 1, 0);
}

void observe_rank_cap(
    RankCapAudit& audit,
    std::uint32_t x,
    std::uint64_t hard_reducible
) {
    if (hard_reducible <= audit.healed) return;
    const std::uint64_t excess = hard_reducible - audit.healed;
    if (audit.first_failure_x == 0) audit.first_failure_x = x;
    audit.last_failure_x = x;
    if (excess > audit.maximum_excess) {
        audit.maximum_excess = excess;
        audit.maximum_excess_x = x;
    }
}

Snapshot make_snapshot(
    std::uint32_t x,
    std::uint64_t generated,
    std::uint64_t splitless,
    std::uint64_t odd_reducible,
    std::uint64_t seed3_even_reducible,
    std::uint64_t hard_reducible,
    std::uint64_t seed2_healed,
    const std::vector<std::uint8_t>& member,
    const std::vector<std::uint32_t>& spf,
    const std::vector<std::uint32_t>& missing_prefix,
    const std::vector<std::uint64_t>& load_num,
    const std::vector<std::uint8_t>& forced_seed_load,
    const std::vector<std::uint64_t>& reciprocal_incidences,
    const std::vector<std::uint64_t>& rank_histogram,
    const std::vector<std::uint64_t>& healing_rank_histogram
) {
    const std::uint64_t missing = missing_prefix[x];
    const std::uint64_t reducible = missing - splitless;
    const std::uint32_t half = (x + 1) / 2;
    if (reducible != odd_reducible + seed3_even_reducible + hard_reducible) {
        throw std::runtime_error("reducible partition failed");
    }
    if (missing_prefix[half] != odd_reducible + seed2_healed) {
        throw std::runtime_error("seed-2 healing identity failed");
    }

    std::vector<std::uint32_t> thresholds;
    std::uint64_t divisor = 2;
    while ((static_cast<std::uint64_t>(x) + 1) / divisor >= 2) {
        thresholds.push_back(static_cast<std::uint32_t>(
            (static_cast<std::uint64_t>(x) + 1) / divisor
        ));
        if (divisor > (static_cast<std::uint64_t>(x) + 1) / 2) break;
        divisor *= 2;
    }

    const std::size_t depth = thresholds.size();
    std::vector<std::uint64_t> all_max(depth, 0);
    std::vector<std::uint64_t> composite_max(depth, 0);
    std::vector<std::uint32_t> all_arg(depth, 0);
    std::vector<std::uint32_t> composite_arg(depth, 0);
    std::vector<std::uint32_t> missing_count(depth, 0);
    std::vector<std::uint32_t> composite_count(depth, 0);

    std::uint64_t prime_charge = 0;
    std::uint64_t composite_charge = 0;
    std::uint32_t forced_seed_max = 0;
    std::uint32_t forced_seed_arg = 0;

    std::size_t band = 0;
    for (std::uint32_t value = half; value >= 2; --value) {
        while (band + 1 < depth && value <= thresholds[band + 1]) ++band;
        if (member[value] || !is_allowed(value)) {
            if (value == 2) break;
            continue;
        }

        ++missing_count[band];
        const bool prime = spf[value] == value;
        if (prime) {
            prime_charge += load_num[value];
        } else {
            composite_charge += load_num[value];
            ++composite_count[band];
        }

        if (load_num[value] > all_max[band]) {
            all_max[band] = load_num[value];
            all_arg[band] = value;
        }
        if (!prime && load_num[value] > composite_max[band]) {
            composite_max[band] = load_num[value];
            composite_arg[band] = value;
        }
        if (forced_seed_load[value] > forced_seed_max) {
            forced_seed_max = forced_seed_load[value];
            forced_seed_arg = value;
        }
        if (value == 2) break;
    }

    std::vector<std::uint64_t> all_envelope(depth, 0);
    std::vector<std::uint64_t> composite_envelope(depth, 0);
    for (std::size_t index = 0; index < depth; ++index) {
        all_envelope[index] = std::max(
            index == 0 ? 0ULL : all_envelope[index - 1],
            all_max[index]
        );
        composite_envelope[index] = std::max(
            index == 0 ? 0ULL : composite_envelope[index - 1],
            composite_max[index]
        );
    }

    std::uint64_t all_bound = 0;
    std::uint64_t composite_bound = 0;
    std::vector<ShellRow> shells;
    shells.reserve(depth);
    for (std::size_t index = 0; index < depth; ++index) {
        all_bound += all_envelope[index] * missing_count[index];
        composite_bound += composite_envelope[index] * composite_count[index];
        shells.push_back(ShellRow{
            thresholds[index],
            all_max[index],
            all_arg[index],
            composite_max[index],
            composite_arg[index],
            composite_envelope[index],
            all_envelope[index],
            missing_count[index],
            composite_count[index],
        });
    }

    const std::uint64_t fixed_point_charge = prime_charge + composite_charge;
    if (fixed_point_charge < reducible * kWeightScale) {
        throw std::runtime_error("fixed-point all-pair charge failed to cover demand");
    }
    if (all_bound < fixed_point_charge || composite_bound < composite_charge) {
        throw std::runtime_error("shell envelope failed to cover factor loads");
    }
    const std::uint64_t exceptional_bound = prime_charge + composite_bound;
    if (exceptional_bound < reducible * kWeightScale) {
        throw std::runtime_error("prime-exception recurrence failed");
    }

    return Snapshot{
        x,
        generated,
        missing,
        splitless,
        reducible,
        odd_reducible,
        seed3_even_reducible,
        hard_reducible,
        seed2_healed,
        missing_prefix[half],
        reducible,
        missing_prefix[half],
        incidence_sum(reciprocal_incidences),
        fixed_point_charge,
        prime_charge,
        composite_charge,
        all_bound,
        composite_bound,
        exceptional_bound - reducible * kWeightScale,
        weighted_theta(all_envelope),
        weighted_theta(composite_envelope),
        forced_seed_max,
        forced_seed_arg,
        rank_histogram,
        healing_rank_histogram,
        std::move(shells),
    };
}

void write_rational(std::ostream& out, const Rational& value) {
    out << "{\"numerator\":\"" << to_string(value.numerator)
        << "\",\"denominator\":\"" << to_string(value.denominator) << "\"}";
}

void write_snapshot(std::ostream& out, const Snapshot& row) {
    out << "    {\n";
    out << "      \"X\":" << row.x << ",\n";
    out << "      \"generated\":" << row.generated << ",\n";
    out << "      \"missing\":" << row.missing << ",\n";
    out << "      \"splitless_missing\":" << row.splitless << ",\n";
    out << "      \"reducible_missing\":" << row.reducible << ",\n";
    out << "      \"odd_reducible\":" << row.odd_reducible << ",\n";
    out << "      \"seed3_even_reducible\":" << row.seed3_even_reducible
        << ",\n";
    out << "      \"hard_reducible\":" << row.hard_reducible << ",\n";
    out << "      \"seed2_healed\":" << row.seed2_healed << ",\n";
    out << "      \"healing_surplus\":"
        << static_cast<std::int64_t>(row.seed2_healed) -
               static_cast<std::int64_t>(row.hard_reducible)
        << ",\n";
    out << "      \"missing_at_half\":" << row.missing_half << ",\n";
    out << "      \"direct_coefficient\":{\"numerator\":" << row.direct_num
        << ",\"denominator\":" << row.direct_den << "},\n";
    out << "      \"reciprocal_all_pair_charge\":";
    write_rational(out, row.reciprocal_charge);
    out << ",\n";
    out << "      \"fixed_point_charge\":{\"numerator\":"
        << row.fixed_point_charge_num
        << ",\"denominator\":" << kWeightScale << "},\n";
    out << "      \"prime_charge\":{\"numerator\":" << row.prime_charge_num
        << ",\"denominator\":" << kWeightScale << "},\n";
    out << "      \"composite_charge\":{\"numerator\":"
        << row.composite_charge_num << ",\"denominator\":" << kWeightScale
        << "},\n";
    out << "      \"all_envelope_bound_num\":" << row.all_envelope_bound_num
        << ",\n";
    out << "      \"composite_envelope_bound_num\":"
        << row.composite_envelope_bound_num << ",\n";
    out << "      \"prime_exception_recurrence_slack_num\":"
        << row.exceptional_recurrence_slack_num << ",\n";
    out << "      \"all_asymptotic_theta\":";
    write_rational(out, row.all_theta);
    out << ",\n";
    out << "      \"composite_asymptotic_theta\":";
    write_rational(out, row.composite_theta);
    out << ",\n";
    out << "      \"forced_seed_max\":{\"load\":" << row.forced_seed_max
        << ",\"factor\":" << row.forced_seed_arg << "},\n";
    out << "      \"rank_histogram\":[";
    for (std::size_t rank = 0; rank < row.rank_histogram.size(); ++rank) {
        if (rank != 0) out << ',';
        out << row.rank_histogram[rank];
    }
    out << "],\n";
    out << "      \"healing_rank_histogram\":[";
    for (std::size_t rank = 0; rank < row.healing_rank_histogram.size(); ++rank) {
        if (rank != 0) out << ',';
        out << row.healing_rank_histogram[rank];
    }
    out << "],\n";
    out << "      \"shells\":[\n";
    for (std::size_t index = 0; index < row.shells.size(); ++index) {
        const ShellRow& shell = row.shells[index];
        out << "        {\"j\":" << index + 1
            << ",\"upper\":" << shell.upper
            << ",\"all_max_num\":" << shell.all_max_num
            << ",\"all_arg\":" << shell.all_arg
            << ",\"composite_max_num\":" << shell.composite_max_num
            << ",\"composite_arg\":" << shell.composite_arg
            << ",\"composite_envelope_num\":" << shell.composite_envelope_num
            << ",\"all_envelope_num\":" << shell.all_envelope_num
            << ",\"missing_count\":" << shell.missing_count
            << ",\"composite_missing_count\":"
            << shell.composite_missing_count << "}"
            << (index + 1 == row.shells.size() ? "\n" : ",\n");
    }
    out << "      ]\n";
    out << "    }";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: hole_contraction_redteam LIMIT OUTPUT_JSON\n";
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
    for (std::uint32_t prime = 2;
         static_cast<std::uint64_t>(prime) * prime <=
             static_cast<std::uint64_t>(limit) + 1;
         ++prime) {
        if (spf[prime] != prime) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(prime) * prime;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += prime) {
            if (spf[multiple] == multiple) spf[multiple] = prime;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint16_t> rank(
        static_cast<std::size_t>(limit) + 1,
        kNoRank
    );
    std::vector<std::uint32_t> missing_prefix(
        static_cast<std::size_t>(limit) + 1,
        0
    );
    std::vector<std::uint64_t> load_num(
        static_cast<std::size_t>(limit) + 1,
        0
    );
    std::vector<std::uint8_t> forced_seed_load(
        static_cast<std::size_t>(limit) + 1,
        0
    );
    std::vector<std::uint64_t> reciprocal_incidences(2, 0);
    std::vector<std::uint64_t> output_pair_counts(2, 0);
    std::vector<std::uint64_t> double_missing_pairs(2, 0);

    member[2] = 1;
    member[3] = 1;
    rank[2] = 0;
    rank[3] = 0;
    std::uint64_t generated = 2;
    std::uint64_t splitless = 0;
    std::uint64_t odd_reducible = 0;
    std::uint64_t seed3_even_reducible = 0;
    std::uint64_t hard_reducible = 0;
    std::uint64_t seed2_healed = 0;
    std::vector<std::uint64_t> rank_histogram{2};
    std::vector<std::uint64_t> healing_rank_histogram{0};
    std::vector<RankCapAudit> rank_cap_audits{
        RankCapAudit{8, 0, 0, 0, 0, 0},
        RankCapAudit{9, 0, 0, 0, 0, 0},
    };

    std::vector<std::uint32_t> checkpoints{32, 100, 362};
    for (std::uint64_t value = 1000; value <= limit; value *= 10) {
        checkpoints.push_back(static_cast<std::uint32_t>(value));
        if (value > limit / 10) break;
    }
    checkpoints.push_back(limit);
    std::sort(checkpoints.begin(), checkpoints.end());
    checkpoints.erase(std::unique(checkpoints.begin(), checkpoints.end()), checkpoints.end());
    checkpoints.erase(
        std::remove_if(
            checkpoints.begin(),
            checkpoints.end(),
            [limit](std::uint32_t value) { return value > limit; }
        ),
        checkpoints.end()
    );
    std::size_t next_checkpoint = 0;
    std::vector<Snapshot> snapshots;

    std::uint64_t maximum_direct_num = 0;
    std::uint64_t maximum_direct_den = 1;
    std::uint32_t maximum_direct_x = 0;
    std::uint32_t first_lambda_two_failure = 0;
    std::uint64_t fixed_point_charge_num = 0;
    std::uint64_t maximum_fixed_point_num = 0;
    std::uint64_t maximum_fixed_point_den = 1;
    std::uint32_t maximum_fixed_point_x = 0;
    std::uint32_t first_fixed_point_lambda_two_failure = 0;
    std::uint32_t maximum_pair_count = 0;

    std::vector<std::uint32_t> divisors;
    std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
    divisors.reserve(2048);
    pairs.reserve(1024);

    for (std::uint32_t n = 2; n <= limit; ++n) {
        pairs.clear();
        std::uint16_t best_rank = kNoRank;
        bool rank_cap_event = false;
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
                    for (std::size_t index = 0; index < old_size; ++index) {
                        divisors.push_back(divisors[index] * power);
                    }
                } while (remaining > 1 && spf[remaining] == prime);
            }

            for (const std::uint32_t left : divisors) {
                if (left < 2) continue;
                const std::uint32_t right = product / left;
                if (left >= right) continue;
                if (!is_allowed(left) || !is_allowed(right)) continue;
                pairs.emplace_back(left, right);
                if (member[left] && member[right]) {
                    if (rank[left] == kNoRank || rank[right] == kNoRank) {
                        throw std::runtime_error("generated factor has no rank");
                    }
                    const std::uint16_t candidate = static_cast<std::uint16_t>(
                        1 + std::max(rank[left], rank[right])
                    );
                    best_rank = std::min(best_rank, candidate);
                }
            }
        }

        if (best_rank != kNoRank) {
            member[n] = 1;
            rank[n] = best_rank;
            ++generated;
            ensure_size(rank_histogram, best_rank);
            ++rank_histogram[best_rank];

            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (is_allowed(parent) && !member[parent]) {
                    ++seed2_healed;
                    ensure_size(healing_rank_histogram, best_rank);
                    ++healing_rank_histogram[best_rank];
                    for (RankCapAudit& audit : rank_cap_audits) {
                        if (best_rank <= audit.cap) ++audit.healed;
                    }
                    rank_cap_event = true;
                }
            }
        }

        missing_prefix[n] = missing_prefix[n - 1];
        if (is_allowed(n) && !member[n]) {
            ++missing_prefix[n];
            if (pairs.empty()) {
                ++splitless;
            } else {
                if ((n & 1U) != 0) {
                    ++odd_reducible;
                } else {
                    const std::uint32_t parent3 = (n + 1) / 3;
                    if ((n + 1) % 3 == 0 && is_allowed(parent3) && parent3 != 3) {
                        ++seed3_even_reducible;
                    } else {
                        ++hard_reducible;
                        rank_cap_event = true;
                    }
                }
                const std::size_t pair_count = pairs.size();
                maximum_pair_count = std::max<std::uint32_t>(
                    maximum_pair_count,
                    static_cast<std::uint32_t>(pair_count)
                );
                if (pair_count > kWeightScale) {
                    throw std::runtime_error("increase kWeightScale");
                }
                ensure_size(reciprocal_incidences, pair_count);
                ensure_size(output_pair_counts, pair_count);
                ensure_size(double_missing_pairs, pair_count);
                ++output_pair_counts[pair_count];

                const std::uint64_t weight_num =
                    (kWeightScale + pair_count - 1) / pair_count;
                std::uint64_t missing_incidences = 0;
                for (const auto& [left, right] : pairs) {
                    const bool left_missing = !member[left];
                    const bool right_missing = !member[right];
                    if (!left_missing && !right_missing) {
                        throw std::runtime_error("missing output has generated split");
                    }
                    missing_incidences += left_missing + right_missing;
                    if (left_missing) load_num[left] += weight_num;
                    if (right_missing) load_num[right] += weight_num;
                    if (left_missing && right_missing) ++double_missing_pairs[pair_count];
                }
                reciprocal_incidences[pair_count] += missing_incidences;
                fixed_point_charge_num += missing_incidences * weight_num;

                if (pair_count == 1) {
                    const auto [left, right] = pairs.front();
                    if ((left == 2 || left == 3) && !member[right]) {
                        ++forced_seed_load[right];
                    }
                    if ((right == 2 || right == 3) && !member[left]) {
                        ++forced_seed_load[left];
                    }
                }
            }
        }

        if (rank_cap_event) {
            for (RankCapAudit& audit : rank_cap_audits) {
                observe_rank_cap(audit, n, hard_reducible);
            }
        }

        const std::uint64_t reducible = missing_prefix[n] - splitless;
        const std::uint64_t denominator = missing_prefix[(n + 1) / 2];
        if (denominator > 0 &&
            reducible * maximum_direct_den > maximum_direct_num * denominator) {
            maximum_direct_num = reducible;
            maximum_direct_den = denominator;
            maximum_direct_x = n;
        }
        if (first_lambda_two_failure == 0 && denominator > 0 &&
            reducible >= 2 * denominator) {
            first_lambda_two_failure = n;
        }
        const std::uint64_t fixed_denominator = kWeightScale * denominator;
        if (fixed_denominator > 0 &&
            uint128_t(fixed_point_charge_num) * maximum_fixed_point_den >
                uint128_t(maximum_fixed_point_num) * fixed_denominator) {
            maximum_fixed_point_num = fixed_point_charge_num;
            maximum_fixed_point_den = fixed_denominator;
            maximum_fixed_point_x = n;
        }
        if (first_fixed_point_lambda_two_failure == 0 &&
            fixed_denominator > 0 &&
            fixed_point_charge_num >= 2 * fixed_denominator) {
            first_fixed_point_lambda_two_failure = n;
        }

        if (next_checkpoint < checkpoints.size() && n == checkpoints[next_checkpoint]) {
            snapshots.push_back(make_snapshot(
                n,
                generated,
                splitless,
                odd_reducible,
                seed3_even_reducible,
                hard_reducible,
                seed2_healed,
                member,
                spf,
                missing_prefix,
                load_num,
                forced_seed_load,
                reciprocal_incidences,
                rank_histogram,
                healing_rank_histogram
            ));
            ++next_checkpoint;
        }
    }

    const std::uint64_t direct_gcd = std::gcd(maximum_direct_num, maximum_direct_den);
    if (std::accumulate(rank_histogram.begin(), rank_histogram.end(), 0ULL) !=
        generated) {
        throw std::runtime_error("rank histogram does not cover generated set");
    }
    if (std::accumulate(
            healing_rank_histogram.begin(),
            healing_rank_histogram.end(),
            0ULL
        ) != seed2_healed) {
        throw std::runtime_error("healing rank histogram mismatch");
    }
    maximum_direct_num /= direct_gcd;
    maximum_direct_den /= direct_gcd;
    const std::uint64_t fixed_gcd =
        std::gcd(maximum_fixed_point_num, maximum_fixed_point_den);
    maximum_fixed_point_num /= fixed_gcd;
    maximum_fixed_point_den /= fixed_gcd;

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n";
    out << "  \"schema_version\":1,\n";
    out << "  \"arithmetic\":\"integer gates; reciprocal sums reduced exactly\",\n";
    out << "  \"rank_definition\":\"seeds rank 0; minimum 1+max factor ranks over generated witness pairs\",\n";
    out << "  \"rank_cap_healing_audit\":[\n";
    for (std::size_t index = 0; index < rank_cap_audits.size(); ++index) {
        const RankCapAudit& audit = rank_cap_audits[index];
        out << "    {\"cap\":" << audit.cap
            << ",\"healed\":" << audit.healed
            << ",\"first_failure_X\":" << audit.first_failure_x
            << ",\"last_failure_X\":" << audit.last_failure_x
            << ",\"maximum_excess\":" << audit.maximum_excess
            << ",\"maximum_excess_X\":" << audit.maximum_excess_x << "}"
            << (index + 1 == rank_cap_audits.size() ? "\n" : ",\n");
    }
    out << "  ],\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"weight_scale\":" << kWeightScale << ",\n";
    out << "  \"maximum_admissible_pair_count_on_reducible_hole\":"
        << maximum_pair_count << ",\n";
    out << "  \"maximum_direct_coefficient\":{\"X\":" << maximum_direct_x
        << ",\"numerator\":" << maximum_direct_num
        << ",\"denominator\":" << maximum_direct_den << "},\n";
    out << "  \"first_lambda_two_failure_X\":" << first_lambda_two_failure
        << ",\n";
    out << "  \"maximum_fixed_point_coefficient\":{\"X\":"
        << maximum_fixed_point_x << ",\"numerator\":"
        << maximum_fixed_point_num << ",\"denominator\":"
        << maximum_fixed_point_den << "},\n";
    out << "  \"first_fixed_point_lambda_two_failure_X\":"
        << first_fixed_point_lambda_two_failure << ",\n";
    out << "  \"pair_count_histogram\":[\n";
    bool first_histogram = true;
    for (std::size_t count = 1; count < output_pair_counts.size(); ++count) {
        if (output_pair_counts[count] == 0) continue;
        if (!first_histogram) out << ",\n";
        first_histogram = false;
        out << "    {\"pair_count\":" << count
            << ",\"outputs\":" << output_pair_counts[count]
            << ",\"missing_endpoint_incidences\":"
            << reciprocal_incidences[count]
            << ",\"double_missing_pairs\":" << double_missing_pairs[count]
            << "}";
    }
    out << "\n  ],\n";
    out << "  \"snapshots\":[\n";
    for (std::size_t index = 0; index < snapshots.size(); ++index) {
        write_snapshot(out, snapshots[index]);
        out << (index + 1 == snapshots.size() ? "\n" : ",\n");
    }
    out << "  ],\n";
    out << "  \"elapsed_seconds\":" << elapsed.count() << "\n";
    out << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " generated=" << generated
              << " missing=" << missing_prefix[limit]
              << " splitless=" << splitless
              << " max_direct=" << maximum_direct_num << "/" << maximum_direct_den
              << " at=" << maximum_direct_x
              << " max_fixed=" << maximum_fixed_point_num << "/"
              << maximum_fixed_point_den << " at=" << maximum_fixed_point_x
              << " lambda2_failure=" << first_lambda_two_failure
              << " fixed_lambda2_failure=" << first_fixed_point_lambda_two_failure
              << " max_pairs=" << maximum_pair_count
              << " elapsed_seconds=" << elapsed.count() << "\n";
    return 0;
}
