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

struct PairStats {
    std::uint64_t count = 0;
    std::uint64_t zero_s_count = 0;
    std::uint32_t first_zero_s_h = 0;
    std::uint32_t last_zero_s_h = 0;
    std::uint32_t min_s = std::numeric_limits<std::uint32_t>::max();
    std::uint32_t min_s_h = 0;
    std::uint32_t max_deficit = 0;
    std::uint32_t max_deficit_h = 0;
    std::string min_s_detail;
    std::string max_deficit_detail;
};

struct RatioWitness {
    bool set = false;
    std::uint32_t s = 0;
    std::uint32_t d = 1;
    std::uint32_t h = 0;

    void observe(std::uint32_t structural, std::uint32_t pairs, std::uint32_t hole) {
        if (!set || static_cast<std::uint64_t>(structural) * d <
                        static_cast<std::uint64_t>(s) * pairs ||
            (static_cast<std::uint64_t>(structural) * d ==
                 static_cast<std::uint64_t>(s) * pairs &&
             hole < h)) {
            set = true;
            s = structural;
            d = pairs;
            h = hole;
        }
    }
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
    const std::vector<std::uint32_t>& divisors,
    const std::vector<State>& state
) {
    const auto product = n + 1;
    bool has_pair = false;
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left >= right || !allowed(left) || !allowed(right)) continue;
        has_pair = true;
        if (state[left] == State::generated &&
            state[right] == State::generated) {
            return State::generated;
        }
    }
    if (!has_pair) return State::splitless;
    if ((n & 1U) == 0) {
        if (product % 3 != 0) return State::hard;
        const auto parent = product / 3;
        if (!allowed(parent) || parent == 3) return State::hard;
    }
    return State::other;
}

std::uint32_t seed_root(std::uint32_t odd_hole) {
    if ((odd_hole & 1U) == 0 || odd_hole < 3) {
        throw std::runtime_error("seed_root requires an odd hole");
    }
    const auto shift = std::countr_zero(odd_hole - 1);
    return ((odd_hole - 1) >> shift) + 1;
}

const char* state_name(State state) {
    switch (state) {
        case State::other: return "other_hole";
        case State::generated: return "generated";
        case State::splitless: return "structural_splitless";
        case State::hard: return "hard";
    }
    throw std::runtime_error("unknown state");
}

std::string describe_hard(
    std::uint32_t n,
    const std::vector<std::uint32_t>& divisors,
    const std::vector<State>& state
) {
    std::ostringstream out;
    const auto product = n + 1;
    out << "{\"h\":" << n << ",\"pairs\":[";
    bool first_pair = true;
    std::uint32_t d = 0;
    std::uint32_t s = 0;
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left >= right || !allowed(left) || !allowed(right)) continue;
        if (!first_pair) out << ',';
        first_pair = false;
        ++d;
        bool structural = false;
        out << "{\"a\":" << left << ",\"b\":" << right << ",\"endpoints\":[";
        for (unsigned i = 0; i < 2; ++i) {
            if (i != 0) out << ',';
            const auto endpoint = i == 0 ? left : right;
            out << "{\"value\":" << endpoint << ",\"state\":\""
                << state_name(state[endpoint]) << "\",\"root\":";
            if (state[endpoint] == State::generated) {
                out << "null,\"root_state\":null}";
            } else {
                const auto root = seed_root(endpoint);
                structural = structural || state[root] == State::splitless;
                out << root << ",\"root_state\":\"" << state_name(state[root]) << "\"}";
            }
        }
        s += static_cast<std::uint32_t>(structural);
        out << "],\"counted_in_s\":" << (structural ? "true" : "false") << '}';
    }
    out << "],\"d\":" << d << ",\"s\":" << s << '}';
    return out.str();
}

std::vector<std::uint32_t> selected_thresholds(std::uint32_t maximum_d) {
    std::vector<std::uint32_t> values;
    for (std::uint32_t d = 1; d <= std::min<std::uint32_t>(maximum_d, 16); ++d) {
        values.push_back(d);
    }
    for (const auto d : {24U, 32U, 48U, 64U, 96U, 128U, 192U, 256U,
                         384U, 512U, 768U, 1024U, 1536U, 2048U, 3072U,
                         4096U, 6144U, 8192U, 12288U, 16384U}) {
        if (d <= maximum_d) values.push_back(d);
    }
    if (maximum_d > 0) values.push_back(maximum_d);
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C105_structural_pair_census LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 534 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [534,4000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        const auto started = std::chrono::steady_clock::now();

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((limit + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        divisors.reserve(4096);
        std::vector<PairStats> exact_by_d(1);

        std::uint64_t hard_count = 0;
        std::uint64_t zero_s_count = 0;
        std::uint32_t largest_d = 0;
        std::uint32_t largest_zero_s_d = 0;
        std::uint32_t largest_zero_s_h = 0;
        std::uint32_t largest_deficit = 0;
        std::uint32_t largest_deficit_h = 0;
        std::uint32_t largest_deficit_d = 0;
        std::uint32_t largest_deficit_s = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t hard_metric_digest = kFnvOffset;
        std::vector<RatioWitness> first_witness_for_d;

        for (std::uint32_t n = 2; n <= limit; ++n) {
            State current = State::other;
            if (n == 2 || n == 3) {
                current = State::generated;
            } else if (allowed(n)) {
                enumerate_divisors(n + 1, odd_spf, divisors);
                current = classify(n, divisors, state);
            }
            state[n] = current;
            fnv_byte(classification_digest, static_cast<std::uint8_t>(current));
            if (current != State::hard) continue;

            std::uint32_t d = 0;
            std::uint32_t s = 0;
            const auto product = n + 1;
            for (const auto left : divisors) {
                if (left < 2) continue;
                const auto right = product / left;
                if (left >= right || !allowed(left) || !allowed(right)) continue;
                ++d;
                bool structural = false;
                for (const auto endpoint : {left, right}) {
                    if (state[endpoint] == State::generated) continue;
                    if ((endpoint & 1U) == 0) {
                        throw std::runtime_error("hard successor had even endpoint");
                    }
                    const auto root = seed_root(endpoint);
                    if (state[root] == State::generated) {
                        throw std::runtime_error("missing endpoint had generated root");
                    }
                    structural = structural || state[root] == State::splitless;
                }
                s += static_cast<std::uint32_t>(structural);
            }
            if (d == 0 || s > d) {
                throw std::runtime_error("invalid hard pair statistics");
            }

            ++hard_count;
            largest_d = std::max(largest_d, d);
            if (exact_by_d.size() <= d) exact_by_d.resize(d + 1);
            auto& row = exact_by_d[d];
            ++row.count;
            if (s < row.min_s) {
                row.min_s = s;
                row.min_s_h = n;
                row.min_s_detail = describe_hard(n, divisors, state);
            }
            const auto deficit = d - s;
            if (deficit > row.max_deficit) {
                row.max_deficit = deficit;
                row.max_deficit_h = n;
                row.max_deficit_detail = describe_hard(n, divisors, state);
            }
            if (s == 0) {
                ++zero_s_count;
                ++row.zero_s_count;
                if (row.first_zero_s_h == 0) row.first_zero_s_h = n;
                row.last_zero_s_h = n;
                if (d > largest_zero_s_d ||
                    (d == largest_zero_s_d && n < largest_zero_s_h)) {
                    largest_zero_s_d = d;
                    largest_zero_s_h = n;
                }
            }
            if (deficit > largest_deficit) {
                largest_deficit = deficit;
                largest_deficit_h = n;
                largest_deficit_d = d;
                largest_deficit_s = s;
            }
            fnv_u64(hard_metric_digest, n);
            fnv_u64(hard_metric_digest, d);
            fnv_u64(hard_metric_digest, s);
        }

        std::vector<std::uint64_t> suffix_count(largest_d + 2);
        std::vector<RatioWitness> suffix_ratio(largest_d + 2);
        std::vector<std::uint32_t> suffix_max_deficit(largest_d + 2);
        std::vector<std::uint32_t> suffix_max_deficit_h(largest_d + 2);
        for (std::uint32_t d = largest_d; d >= 1; --d) {
            suffix_count[d] = suffix_count[d + 1] + exact_by_d[d].count;
            suffix_ratio[d] = suffix_ratio[d + 1];
            if (exact_by_d[d].count != 0) {
                suffix_ratio[d].observe(exact_by_d[d].min_s, d, exact_by_d[d].min_s_h);
            }
            suffix_max_deficit[d] = suffix_max_deficit[d + 1];
            suffix_max_deficit_h[d] = suffix_max_deficit_h[d + 1];
            if (exact_by_d[d].max_deficit > suffix_max_deficit[d]) {
                suffix_max_deficit[d] = exact_by_d[d].max_deficit;
                suffix_max_deficit_h[d] = exact_by_d[d].max_deficit_h;
            }
            if (d == 1) break;
        }

        const auto finished = std::chrono::steady_clock::now();
        const auto seconds = std::chrono::duration<double>(finished - started).count();
        const auto thresholds = selected_thresholds(largest_d);

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C105-structural-pair-census-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"definitions\":{"
            << "\"d(h)\":\"admissible distinct factor pairs of h+1\","
            << "\"s(h)\":\"pairs with a missing endpoint whose seed-2 root is structural splitless\"},\n"
            << "  \"summary\":{"
            << "\"hard_holes\":" << hard_count
            << ",\"maximum_d\":" << largest_d
            << ",\"zero_s_count\":" << zero_s_count
            << ",\"largest_d_with_s_zero\":" << largest_zero_s_d
            << ",\"largest_d_with_s_zero_h\":" << largest_zero_s_h
            << ",\"largest_deficit_d_minus_s\":" << largest_deficit
            << ",\"largest_deficit_h\":" << largest_deficit_h
            << ",\"largest_deficit_h_d\":" << largest_deficit_d
            << ",\"largest_deficit_h_s\":" << largest_deficit_s << "},\n"
            << "  \"thresholds\":[\n";
        for (std::size_t i = 0; i < thresholds.size(); ++i) {
            const auto d = thresholds[i];
            const auto& ratio = suffix_ratio[d];
            if (!ratio.set) throw std::runtime_error("unset suffix ratio");
            const auto gcd = std::gcd(ratio.s, ratio.d);
            out << "    {\"minimum_d\":" << d
                << ",\"hard_count\":" << suffix_count[d]
                << ",\"minimum_ratio_s\":" << ratio.s
                << ",\"minimum_ratio_d\":" << ratio.d
                << ",\"minimum_ratio_reduced_s\":" << ratio.s / gcd
                << ",\"minimum_ratio_reduced_d\":" << ratio.d / gcd
                << ",\"minimum_ratio_h\":" << ratio.h
                << ",\"maximum_deficit\":" << suffix_max_deficit[d]
                << ",\"maximum_deficit_h\":" << suffix_max_deficit_h[d]
                << "}" << (i + 1 == thresholds.size() ? "\n" : ",\n");
        }
        out << "  ],\n"
            << "  \"exact_by_d\":[\n";
        bool first = true;
        for (std::uint32_t d = 1; d <= largest_d; ++d) {
            const auto& row = exact_by_d[d];
            if (row.count == 0) continue;
            if (!first) out << ",\n";
            first = false;
            out << "    {\"d\":" << d
                << ",\"count\":" << row.count
                << ",\"zero_s_count\":" << row.zero_s_count
                << ",\"first_zero_s_h\":";
            if (row.first_zero_s_h == 0) out << "null"; else out << row.first_zero_s_h;
            out << ",\"last_zero_s_h\":";
            if (row.last_zero_s_h == 0) out << "null"; else out << row.last_zero_s_h;
            out
                << ",\"minimum_s\":" << row.min_s
                << ",\"minimum_s_h\":" << row.min_s_h
                << ",\"maximum_deficit\":" << row.max_deficit
                << ",\"maximum_deficit_h\":" << row.max_deficit_h
                << ",\"minimum_s_detail\":" << row.min_s_detail
                << ",\"maximum_deficit_detail\":" << row.max_deficit_detail
                << "}";
        }
        out << "\n  ],\n"
            << "  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\","
            << "\"classification_2_through_limit\":\""
            << hex_u64(classification_digest) << "\","
            << "\"hard_h_d_s\":\"" << hex_u64(hard_metric_digest) << "\"},\n"
            << std::fixed << std::setprecision(6)
            << "  \"timing_seconds\":" << seconds << "\n"
            << "}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " hard=" << hard_count
                  << " max_d=" << largest_d
                  << " zero_s=" << zero_s_count
                  << " max_zero_d=" << largest_zero_s_d
                  << " max_deficit=" << largest_deficit
                  << " seconds=" << std::fixed << std::setprecision(3)
                  << seconds << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
