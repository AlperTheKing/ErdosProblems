#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr std::uint32_t kMaximumLimit = 1'000'000'000U;
constexpr std::uint64_t kFnvOffset = 14'695'981'039'346'656'037ULL;
constexpr std::uint64_t kFnvPrime = 1'099'511'628'211ULL;

enum class State : std::uint8_t {
    other = 0,
    generated = 1,
    splitless = 2,
    hard = 3,
};

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

void fnv_byte(std::uint64_t& digest, std::uint8_t value) {
    digest ^= value;
    digest *= kFnvPrime;
}

void fnv_u64(std::uint64_t& digest, std::uint64_t value) {
    for (unsigned shift = 0; shift < 64; shift += 8) {
        fnv_byte(digest, static_cast<std::uint8_t>(value >> shift));
    }
}

std::string hex_u64(std::uint64_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << value;
    return out.str();
}

struct MinimumRatio {
    bool found = false;
    std::uint64_t numerator = 0;
    std::uint64_t denominator = 1;
    std::uint32_t x = 0;

    void observe(std::uint32_t cutoff, std::uint64_t d, std::uint64_t a_h) {
        if (a_h == 0) return;
        if (!found || d * denominator < numerator * a_h) {
            found = true;
            numerator = d;
            denominator = a_h;
            x = cutoff;
        }
    }
};

struct Failure {
    bool found = false;
    std::uint32_t x = 0;
    std::uint64_t d = 0;
    std::uint64_t a_h = 0;
};

struct QuarterExtremum {
    bool found = false;
    std::int64_t value = 0;
    std::uint32_t x = 0;
    std::uint64_t a_h = 0;
    std::uint64_t d = 0;
    std::uint64_t quarter = 0;
};

struct QuarterAudit {
    QuarterExtremum minimum_additive;
    QuarterExtremum maximum_weighted;
    QuarterExtremum maximum_direct;
    QuarterExtremum maximum_actual_shell_excess;
    QuarterExtremum maximum_seed3_minus_quarter;
    std::uint64_t additive_below_minus_one = 0;
    std::uint64_t weighted_above_zero = 0;
    std::uint64_t direct_above_seven = 0;

    void observe(
        std::uint32_t x,
        std::uint64_t a_h,
        std::uint64_t d,
        std::uint64_t quarter,
        std::uint64_t healed_seed3
    ) {
        const auto additive = static_cast<std::int64_t>(d + quarter) -
                              static_cast<std::int64_t>(a_h);
        const auto weighted = static_cast<std::int64_t>(7 * quarter) -
                              static_cast<std::int64_t>(2 * d);
        const auto direct = static_cast<std::int64_t>(7 * a_h) -
                            static_cast<std::int64_t>(9 * d);
        const auto actual_shell = static_cast<std::int64_t>(a_h) -
                                  static_cast<std::int64_t>(d + healed_seed3);
        const auto seed3_quarter = static_cast<std::int64_t>(healed_seed3) -
                                   static_cast<std::int64_t>(quarter);
        const QuarterExtremum add_row = {
            true, additive, x, a_h, d, quarter
        };
        const QuarterExtremum weighted_row = {
            true, weighted, x, a_h, d, quarter
        };
        const QuarterExtremum direct_row = {
            true, direct, x, a_h, d, quarter
        };
        const QuarterExtremum actual_shell_row = {
            true, actual_shell, x, a_h, d, quarter
        };
        const QuarterExtremum seed3_quarter_row = {
            true, seed3_quarter, x, a_h, d, quarter
        };
        if (!minimum_additive.found || additive < minimum_additive.value) {
            minimum_additive = add_row;
        }
        if (!maximum_weighted.found || weighted > maximum_weighted.value) {
            maximum_weighted = weighted_row;
        }
        if (!maximum_direct.found || direct > maximum_direct.value) {
            maximum_direct = direct_row;
        }
        if (!maximum_actual_shell_excess.found ||
            actual_shell > maximum_actual_shell_excess.value) {
            maximum_actual_shell_excess = actual_shell_row;
        }
        if (!maximum_seed3_minus_quarter.found ||
            seed3_quarter > maximum_seed3_minus_quarter.value) {
            maximum_seed3_minus_quarter = seed3_quarter_row;
        }
        if (additive < -1) ++additive_below_minus_one;
        if (weighted > 0) ++weighted_above_zero;
        if (direct > 7) ++direct_above_seven;
    }
};

struct Audit {
    std::uint64_t event_count = 0;
    std::uint64_t positive_demand_events = 0;
    std::uint64_t below_five_sixths_count = 0;
    std::uint64_t at_most_three_quarters_count = 0;
    Failure first_below_five_sixths;
    Failure first_at_most_three_quarters;
    MinimumRatio minimum_ratio;

    void observe(std::uint32_t x, std::uint64_t d, std::uint64_t a_h) {
        ++event_count;
        if (a_h == 0) return;
        ++positive_demand_events;
        minimum_ratio.observe(x, d, a_h);
        if (6 * d < 5 * a_h) {
            ++below_five_sixths_count;
            if (!first_below_five_sixths.found) {
                first_below_five_sixths = {true, x, d, a_h};
            }
        }
        if (4 * d <= 3 * a_h) {
            ++at_most_three_quarters_count;
            if (!first_at_most_three_quarters.found) {
                first_at_most_three_quarters = {true, x, d, a_h};
            }
        }
    }
};

struct Checkpoint {
    std::uint32_t x = 0;
    std::uint64_t a_h = 0;
    std::uint64_t d = 0;
    std::uint64_t hard_roots = 0;
    std::uint64_t splitless_roots = 0;
};

std::vector<std::uint32_t> checkpoint_cutoffs(std::uint32_t limit) {
    std::vector<std::uint32_t> values = {
        2U, 54U, 74U, 186U, 362U, 1'000U, 2'000U, 5'000U,
        10'000U, 16'620U, 100'000U, 1'000'000U, 100'000'000U,
        1'000'000'000U, limit
    };
    std::erase_if(values, [limit](std::uint32_t x) { return x > limit; });
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

void build_odd_spf(std::uint32_t maximum, std::vector<std::uint16_t>& odd_spf) {
    for (std::uint32_t p = 3;
         static_cast<std::uint64_t>(p) * p <= maximum;
         p += 2) {
        if (odd_spf[p >> 1] != 0) continue;
        const std::uint64_t step = 2ULL * p;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= maximum;
             multiple += step) {
            auto& entry = odd_spf[static_cast<std::size_t>(multiple >> 1)];
            if (entry == 0) entry = static_cast<std::uint16_t>(p);
        }
    }
}

std::uint32_t prime_factor(
    std::uint32_t value,
    const std::vector<std::uint16_t>& odd_spf
) {
    if ((value & 1U) == 0) return 2;
    const auto factor = odd_spf[value >> 1];
    return factor == 0 ? value : factor;
}

void enumerate_divisors(
    std::uint32_t value,
    const std::vector<std::uint16_t>& odd_spf,
    std::vector<std::uint32_t>& divisors
) {
    divisors.clear();
    divisors.push_back(1);
    std::uint32_t remaining = value;
    while (remaining > 1) {
        const auto p = prime_factor(remaining, odd_spf);
        const auto old_size = divisors.size();
        std::uint32_t power = 1;
        do {
            remaining /= p;
            power *= p;
            for (std::size_t i = 0; i < old_size; ++i) {
                divisors.push_back(divisors[i] * power);
            }
        } while (remaining > 1 && remaining % p == 0);
    }
}

State classify(
    std::uint32_t n,
    const std::vector<std::uint16_t>& odd_spf,
    const std::vector<State>& state,
    std::vector<std::uint32_t>& divisors
) {
    const auto product = n + 1;
    enumerate_divisors(product, odd_spf, divisors);
    bool has_admissible_pair = false;
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left >= right) continue;
        if (!allowed(left) || !allowed(right)) continue;
        has_admissible_pair = true;
        if (state[left] == State::generated &&
            state[right] == State::generated) {
            return State::generated;
        }
    }
    if (!has_admissible_pair) return State::splitless;
    if ((n & 1U) == 0) {
        if (product % 3 != 0) return State::hard;
        const auto parent = product / 3;
        if (!allowed(parent) || parent == 3) return State::hard;
    }
    return State::other;
}

void write_failure(std::ostream& out, const Failure& failure) {
    if (!failure.found) {
        out << "null";
        return;
    }
    out << "{\"X\":" << failure.x
        << ",\"D\":" << failure.d
        << ",\"A_H\":" << failure.a_h << '}';
}

void write_ratio(std::ostream& out, const MinimumRatio& ratio) {
    require(ratio.found, "minimum ratio was never initialized");
    const auto divisor = std::gcd(ratio.numerator, ratio.denominator);
    out << "{\"D\":" << ratio.numerator
        << ",\"A_H\":" << ratio.denominator
        << ",\"X\":" << ratio.x
        << ",\"reduced_numerator\":" << ratio.numerator / divisor
        << ",\"reduced_denominator\":" << ratio.denominator / divisor
        << '}';
}

void write_quarter_extremum(
    std::ostream& out,
    const QuarterExtremum& row
) {
    require(row.found, "quarter extremum was never initialized");
    out << "{\"value\":" << row.value
        << ",\"X\":" << row.x
        << ",\"A_H\":" << row.a_h
        << ",\"D\":" << row.d
        << ",\"A_H_floor_X_over_4\":" << row.quarter << '}';
}

void verify_c87_checkpoint(const Checkpoint& row) {
    struct Expected {
        std::uint32_t x;
        std::uint64_t a_h;
        std::uint64_t d;
    };
    constexpr Expected expected[] = {
        {54U, 1U, 1U}, {74U, 2U, 2U}, {186U, 6U, 5U},
        {362U, 11U, 10U}, {1'000U, 34U, 34U},
        {2'000U, 83U, 72U}, {5'000U, 196U, 186U},
        {10'000U, 391U, 374U},
    };
    for (const auto& item : expected) {
        if (row.x == item.x && (row.a_h != item.a_h || row.d != item.d)) {
            throw std::runtime_error("C87 small-cutoff regression failed");
        }
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C95_quarter_event_census LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 54 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [54,1000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((limit + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> active_hard_history(
            static_cast<std::size_t>(limit / 4) + 1
        );
        std::vector<std::uint32_t> divisors;
        divisors.reserve(2048);

        const auto wanted_checkpoints = checkpoint_cutoffs(limit);
        std::size_t next_checkpoint = 0;
        std::vector<Checkpoint> checkpoints;
        checkpoints.reserve(wanted_checkpoints.size());

        std::uint64_t allowed_count = 0;
        std::uint64_t generated_count = 0;
        std::uint64_t hard_roots = 0;
        std::uint64_t active_hard = 0;
        std::uint64_t hard_deaths = 0;
        std::uint64_t splitless_values = 0;
        std::uint64_t splitless_roots = 0;
        std::uint64_t healed_splitless_roots = 0;
        std::uint64_t healed_seed3_roots = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t event_digest = kFnvOffset;
        Audit audit;
        QuarterAudit quarter_audit;

        for (std::uint32_t x = 2; x <= limit; ++x) {
            State current = State::other;
            if (x == 2 || x == 3) {
                current = State::generated;
            } else if (allowed(x)) {
                current = classify(x, odd_spf, state, divisors);
            }
            state[x] = current;

            bool event = false;
            if (allowed(x)) ++allowed_count;
            if (current == State::generated) ++generated_count;
            if (current == State::splitless) {
                ++splitless_values;
                if ((x & 1U) == 0) ++splitless_roots;
            }
            if (current == State::hard) {
                require((x & 1U) == 0, "hard value is not an even root");
                ++hard_roots;
                ++active_hard;
                event = true;
            }

            if ((x & 1U) != 0 && current != State::generated && allowed(x)) {
                const auto parent = (x + 1) / 2;
                if (!allowed(parent) || state[parent] == State::generated) {
                    throw std::runtime_error("odd hole has a nonhole parent");
                }
            }

            if ((x & 1U) != 0 && current == State::generated && x > 3) {
                const auto parent = (x + 1) / 2;
                if (allowed(parent) && state[parent] != State::generated) {
                    const auto shift = std::countr_zero(x - 1);
                    const auto root = ((x - 1) >> shift) + 1;
                    if ((root & 1U) != 0 || state[root] == State::generated) {
                        throw std::runtime_error("invalid seed-2 chain root");
                    }
                    if (state[root] == State::hard) {
                        require(active_hard > 0, "hard-chain death underflow");
                        --active_hard;
                        ++hard_deaths;
                        event = true;
                    } else if (state[root] == State::splitless) {
                        ++healed_splitless_roots;
                        event = true;
                    } else {
                        ++healed_seed3_roots;
                        event = true;
                    }
                }
            }

            if (event) {
                audit.observe(x, healed_splitless_roots, active_hard);
                fnv_u64(event_digest, x);
                fnv_u64(event_digest, active_hard);
                fnv_u64(event_digest, healed_splitless_roots);
            }
            if (x <= limit / 4) {
                active_hard_history[x] = static_cast<std::uint32_t>(active_hard);
            }
            quarter_audit.observe(
                x,
                active_hard,
                healed_splitless_roots,
                active_hard_history[x / 4],
                healed_seed3_roots
            );
            fnv_byte(classification_digest, static_cast<std::uint8_t>(current));

            if (next_checkpoint < wanted_checkpoints.size() &&
                x == wanted_checkpoints[next_checkpoint]) {
                const Checkpoint row = {
                    x, active_hard, healed_splitless_roots,
                    hard_roots, splitless_roots
                };
                verify_c87_checkpoint(row);
                checkpoints.push_back(row);
                ++next_checkpoint;
            }
        }

        require(hard_roots == active_hard + hard_deaths,
                "hard-chain accounting mismatch");
        require(splitless_roots >= healed_splitless_roots,
                "splitless-chain accounting underflow");
        require(checkpoints.size() == wanted_checkpoints.size(),
                "checkpoint capture mismatch");
        require(audit.minimum_ratio.found, "no positive-demand event");

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C95-quarter-event-census-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"definitions\":{"
            << "\"A_H\":\"hard even roots whose seed-2 top at X is not generated\","
            << "\"D\":\"structural splitless even roots whose seed-2 top at X is generated\","
            << "\"event\":\"a hard birth, hard-chain death, or splitless-chain healing\"},\n"
            << "  \"counts\":{"
            << "\"allowed\":" << allowed_count
            << ",\"generated\":" << generated_count
            << ",\"hard_roots\":" << hard_roots
            << ",\"A_H\":" << active_hard
            << ",\"hard_chain_deaths\":" << hard_deaths
            << ",\"splitless_values\":" << splitless_values
            << ",\"splitless_roots\":" << splitless_roots
            << ",\"D\":" << healed_splitless_roots
            << ",\"B_3\":" << healed_seed3_roots
            << ",\"unhealed_splitless_roots\":"
            << splitless_roots - healed_splitless_roots << "},\n"
            << "  \"event_audit\":{"
            << "\"event_count\":" << audit.event_count
            << ",\"positive_demand_events\":" << audit.positive_demand_events
            << ",\"six_D_lt_five_A_H_count\":"
            << audit.below_five_sixths_count
            << ",\"first_six_D_lt_five_A_H\":";
        write_failure(out, audit.first_below_five_sixths);
        out << ",\"four_D_le_three_A_H_count\":"
            << audit.at_most_three_quarters_count
            << ",\"first_four_D_le_three_A_H\":";
        write_failure(out, audit.first_at_most_three_quarters);
        out << ",\"minimum_D_over_A_H\":";
        write_ratio(out, audit.minimum_ratio);
        out << "},\n  \"quarter_audit\":{"
            << "\"additive_identity\":\"F=D+A_H(floor(X/4))-A_H(X)\"," 
            << "\"minimum_F\":";
        write_quarter_extremum(out, quarter_audit.minimum_additive);
        out << ",\"F_below_minus_one_count\":"
            << quarter_audit.additive_below_minus_one
            << ",\"weighted_identity\":\"G=7*A_H(floor(X/4))-2*D\"," 
            << "\"maximum_G\":";
        write_quarter_extremum(out, quarter_audit.maximum_weighted);
        out << ",\"G_above_zero_count\":"
            << quarter_audit.weighted_above_zero
            << ",\"direct_identity\":\"J=7*A_H(X)-9*D(X)\"," 
            << "\"maximum_J\":";
        write_quarter_extremum(out, quarter_audit.maximum_direct);
        out << ",\"J_above_seven_count\":"
            << quarter_audit.direct_above_seven
            << ",\"actual_shell_identity\":\"A_H-D-B_3\"," 
            << "\"maximum_actual_shell_excess\":";
        write_quarter_extremum(out, quarter_audit.maximum_actual_shell_excess);
        out << ",\"seed3_quarter_identity\":\"B_3-A_H(floor(X/4))\"," 
            << "\"maximum_seed3_minus_quarter\":";
        write_quarter_extremum(out, quarter_audit.maximum_seed3_minus_quarter);
        out
            << "},\n  \"c87_regression_checkpoints\":[\n";
        for (std::size_t index = 0; index < checkpoints.size(); ++index) {
            const auto& row = checkpoints[index];
            out << "    {\"X\":" << row.x
                << ",\"A_H\":" << row.a_h
                << ",\"D\":" << row.d
                << ",\"hard_roots\":" << row.hard_roots
                << ",\"splitless_roots\":" << row.splitless_roots << '}'
                << (index + 1 == checkpoints.size() ? "\n" : ",\n");
        }
        const auto allocated_bytes =
            static_cast<std::uint64_t>(odd_spf.size()) * sizeof(std::uint16_t) +
            static_cast<std::uint64_t>(state.size()) * sizeof(State) +
            static_cast<std::uint64_t>(active_hard_history.size()) *
                sizeof(std::uint32_t);
        out << "  ],\n"
            << "  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\","
            << "\"classification_2_through_limit\":\""
            << hex_u64(classification_digest) << "\","
            << "\"event_X_A_H_D\":\"" << hex_u64(event_digest) << "\"},\n"
            << "  \"resources\":{\"allocated_core_bytes\":"
            << allocated_bytes << ",\"odd_spf_bytes\":"
            << static_cast<std::uint64_t>(odd_spf.size()) * sizeof(std::uint16_t)
            << ",\"state_bytes\":"
            << static_cast<std::uint64_t>(state.size()) * sizeof(State) << "}\n"
            << "}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " events=" << audit.event_count
                  << " A_H=" << active_hard
                  << " D=" << healed_splitless_roots
                  << " min_F=" << quarter_audit.minimum_additive.value
                  << " max_G=" << quarter_audit.maximum_weighted.value
                  << " max_J=" << quarter_audit.maximum_direct.value
                  << " first_5_6="
                  << (audit.first_below_five_sixths.found
                          ? std::to_string(audit.first_below_five_sixths.x)
                          : std::string("none"))
                  << " first_3_4="
                  << (audit.first_at_most_three_quarters.found
                          ? std::to_string(audit.first_at_most_three_quarters.x)
                          : std::string("none"))
                  << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
