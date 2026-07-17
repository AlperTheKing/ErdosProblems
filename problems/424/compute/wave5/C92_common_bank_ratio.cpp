#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr std::uint32_t kMaximumLimit = 4'000'000'000U;
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

struct RatioMinimum {
    bool set = false;
    std::uint64_t numerator = 0;
    std::uint64_t denominator = 1;
    std::uint32_t x = 0;

    void observe(std::uint32_t cutoff, std::uint64_t d, std::uint64_t a_h) {
        if (a_h == 0) return;
        if (!set || d * denominator < numerator * a_h) {
            set = true;
            numerator = d;
            denominator = a_h;
            x = cutoff;
        }
    }
};

struct Checkpoint {
    std::uint32_t x = 0;
    std::uint64_t a_h = 0;
    std::uint64_t d = 0;
    std::int64_t margin = 0;
};

std::vector<std::uint32_t> checkpoint_cutoffs(std::uint32_t limit) {
    std::vector<std::uint32_t> values = {
        54U, 74U, 114U, 186U, 204U, 362U, 1'000U, 10'000U,
        100'000U, 1'000'000U, 10'000'000U, 100'000'000U,
        1'000'000'000U, limit
    };
    std::erase_if(values, [limit](std::uint32_t x) { return x > limit; });
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C92_common_bank_ratio LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 54 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [54,4000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        const auto started = std::chrono::steady_clock::now();

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((limit + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        // The scale gates only query A_H(floor(X/4)), so retaining the
        // first quarter of the trajectory is sufficient.
        std::vector<std::uint32_t> active_hard_prefix(
            static_cast<std::size_t>(limit / 4) + 1
        );
        std::vector<std::uint32_t> divisors;
        divisors.reserve(2048);

        const auto wanted = checkpoint_cutoffs(limit);
        std::size_t next_checkpoint = 0;
        std::vector<Checkpoint> checkpoints;
        std::uint64_t active_hard = 0;
        std::uint64_t hard_births = 0;
        std::uint64_t hard_deaths = 0;
        std::uint64_t splitless_births = 0;
        std::uint64_t healed_splitless = 0;
        std::uint64_t splitless_deaths = 0;
        std::uint64_t checked_positive = 0;
        std::uint64_t failures = 0;
        std::uint32_t first_failure_x = 0;
        std::int64_t minimum_margin = std::numeric_limits<std::int64_t>::max();
        std::uint32_t minimum_margin_x = 0;
        RatioMinimum minimum_ratio;
        std::int64_t scale_upper_minimum = std::numeric_limits<std::int64_t>::max();
        std::uint32_t scale_upper_minimum_x = 0;
        std::uint64_t scale_upper_failures = 0;
        std::int64_t scale_lower_minimum = std::numeric_limits<std::int64_t>::max();
        std::uint32_t scale_lower_minimum_x = 0;
        std::uint64_t scale_lower_failures = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t trajectory_digest = kFnvOffset;

        for (std::uint32_t x = 2; x <= limit; ++x) {
            State current = State::other;
            if (x == 2 || x == 3) {
                current = State::generated;
            } else if (allowed(x)) {
                current = classify(x, odd_spf, state, divisors);
            }
            state[x] = current;

            if (current == State::hard) {
                if ((x & 1U) != 0) {
                    throw std::runtime_error("hard value is not an even root");
                }
                ++hard_births;
                ++active_hard;
            }
            if (current == State::splitless) {
                if ((x & 1U) != 0) {
                    throw std::runtime_error("splitless hole is not an even root");
                }
                ++splitless_births;
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
                        if (active_hard == 0) {
                            throw std::runtime_error("hard-chain death underflow");
                        }
                        --active_hard;
                        ++hard_deaths;
                    } else if (state[root] == State::splitless) {
                        ++healed_splitless;
                        ++splitless_deaths;
                    }
                }
            }

            const auto margin = static_cast<std::int64_t>(6 * healed_splitless) -
                                static_cast<std::int64_t>(5 * active_hard);
            if (x <= limit / 4) {
                active_hard_prefix[x] = static_cast<std::uint32_t>(active_hard);
            }
            const auto quarter_hard = active_hard_prefix[x / 4];
            const auto scale_upper =
                static_cast<std::int64_t>(healed_splitless) +
                static_cast<std::int64_t>(quarter_hard) + 1 -
                static_cast<std::int64_t>(active_hard);
            const auto scale_lower =
                static_cast<std::int64_t>(2 * healed_splitless) -
                static_cast<std::int64_t>(7) * quarter_hard;
            if (scale_upper < scale_upper_minimum) {
                scale_upper_minimum = scale_upper;
                scale_upper_minimum_x = x;
            }
            if (scale_lower < scale_lower_minimum) {
                scale_lower_minimum = scale_lower;
                scale_lower_minimum_x = x;
            }
            if (scale_upper < 0) ++scale_upper_failures;
            if (scale_lower < 0) ++scale_lower_failures;
            if (active_hard > 0) {
                ++checked_positive;
                minimum_ratio.observe(x, healed_splitless, active_hard);
                if (margin < minimum_margin) {
                    minimum_margin = margin;
                    minimum_margin_x = x;
                }
                if (margin < 0) {
                    ++failures;
                    if (first_failure_x == 0) first_failure_x = x;
                }
            }

            fnv_byte(classification_digest, static_cast<std::uint8_t>(current));
            fnv_u64(trajectory_digest, x);
            fnv_u64(trajectory_digest, active_hard);
            fnv_u64(trajectory_digest, healed_splitless);

            if (next_checkpoint < wanted.size() && x == wanted[next_checkpoint]) {
                checkpoints.push_back({x, active_hard, healed_splitless, margin});
                ++next_checkpoint;
            }
        }

        if (hard_births != active_hard + hard_deaths) {
            throw std::runtime_error("hard interval accounting mismatch");
        }
        if (splitless_deaths != healed_splitless ||
            splitless_deaths > splitless_births) {
            throw std::runtime_error("splitless interval accounting mismatch");
        }
        if (!minimum_ratio.set || checkpoints.size() != wanted.size()) {
            throw std::runtime_error("incomplete ratio or checkpoint audit");
        }
        if (limit >= 10'000 &&
            (minimum_ratio.numerator != 5 || minimum_ratio.denominator != 6 ||
             minimum_ratio.x != 186)) {
            throw std::runtime_error("C91 prefix ratio regression");
        }

        const auto finished = std::chrono::steady_clock::now();
        const auto seconds = std::chrono::duration<double>(finished - started).count();
        const auto divisor = std::gcd(
            minimum_ratio.numerator, minimum_ratio.denominator
        );

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C92-common-bank-ratio-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"definitions\":{"
            << "\"A_H\":\"persistent hard roots at cutoff X\","
            << "\"D\":\"splitless roots whose seed-2 chain has reached a generated value by X\"},\n"
            << "  \"audit\":{"
            << "\"checked_cutoffs_with_positive_A_H\":" << checked_positive
            << ",\"failure_count_6D_lt_5A_H\":" << failures
            << ",\"first_failure_X\":";
        if (first_failure_x == 0) out << "null"; else out << first_failure_x;
        out << ",\"minimum_margin_6D_minus_5A_H\":" << minimum_margin
            << ",\"minimum_margin_X\":" << minimum_margin_x
            << ",\"scale_quarter_upper\":{"
            << "\"statement\":\"A_H(X)<=D(X)+A_H(floor(X/4))+1\","
            << "\"failure_count\":" << scale_upper_failures
            << ",\"minimum_margin\":" << scale_upper_minimum
            << ",\"minimum_margin_X\":" << scale_upper_minimum_x << "}"
            << ",\"scale_quarter_lower\":{"
            << "\"statement\":\"2D(X)>=7A_H(floor(X/4))\","
            << "\"failure_count\":" << scale_lower_failures
            << ",\"minimum_margin\":" << scale_lower_minimum
            << ",\"minimum_margin_X\":" << scale_lower_minimum_x << "}"
            << ",\"minimum_ratio\":{"
            << "\"D\":" << minimum_ratio.numerator
            << ",\"A_H\":" << minimum_ratio.denominator
            << ",\"reduced_numerator\":" << minimum_ratio.numerator / divisor
            << ",\"reduced_denominator\":" << minimum_ratio.denominator / divisor
            << ",\"X\":" << minimum_ratio.x << "}},\n"
            << "  \"endpoint\":{"
            << "\"A_H\":" << active_hard
            << ",\"D\":" << healed_splitless
            << ",\"hard_births\":" << hard_births
            << ",\"hard_deaths\":" << hard_deaths
            << ",\"splitless_births\":" << splitless_births
            << ",\"splitless_deaths\":" << splitless_deaths << "},\n"
            << "  \"checkpoints\":[\n";
        for (std::size_t i = 0; i < checkpoints.size(); ++i) {
            const auto& row = checkpoints[i];
            out << "    {\"X\":" << row.x
                << ",\"A_H\":" << row.a_h
                << ",\"D\":" << row.d
                << ",\"margin_6D_minus_5A_H\":" << row.margin << "}"
                << (i + 1 == checkpoints.size() ? "\n" : ",\n");
        }
        out << "  ],\n"
            << "  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\","
            << "\"classification_2_through_limit\":\""
            << hex_u64(classification_digest) << "\","
            << "\"trajectory_X_A_H_D\":\""
            << hex_u64(trajectory_digest) << "\"},\n"
            << std::fixed << std::setprecision(6)
            << "  \"timing_seconds\":" << seconds << "\n"
            << "}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " A_H=" << active_hard
                  << " D=" << healed_splitless
                  << " failures=" << failures
                  << " min_ratio=" << minimum_ratio.numerator << '/'
                  << minimum_ratio.denominator
                  << " at_X=" << minimum_ratio.x
                  << " seconds=" << std::fixed << std::setprecision(3)
                  << seconds << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
