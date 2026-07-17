#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
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

void build_odd_spf(std::uint32_t maximum, std::vector<std::uint16_t>& odd_spf) {
    for (std::uint32_t p = 3; static_cast<std::uint64_t>(p) * p <= maximum; p += 2) {
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
    auto remaining = value;
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
        if (state[left] == State::generated && state[right] == State::generated) {
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

std::uint32_t seed_root(std::uint32_t endpoint) {
    require(endpoint >= 3 && (endpoint & 1U) != 0, "seed root requires odd endpoint");
    return ((endpoint - 1) >> std::countr_zero(endpoint - 1)) + 1;
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

struct Counts {
    std::uint32_t d = 0;
    std::uint32_t s = 0;
    std::uint32_t t = 0;
    std::uint32_t e0 = 0;
    std::uint32_t e1 = 0;
    std::int32_t minimum_prefix_slack = std::numeric_limits<std::int32_t>::max();
};

Counts endpoint_counts(
    std::uint32_t n,
    const std::vector<std::uint32_t>& divisors,
    const std::vector<State>& state,
    std::vector<std::uint32_t>& pair_lefts
) {
    Counts counts;
    const auto product = n + 1;
    pair_lefts.clear();
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left >= right || !allowed(left) || !allowed(right)) continue;
        pair_lefts.push_back(left);
    }
    std::sort(pair_lefts.begin(), pair_lefts.end());
    std::uint32_t prefix_t = 0;
    for (const auto left : pair_lefts) {
        const auto right = product / left;
        ++counts.d;
        bool structural_pair = false;
        std::uint32_t missing = 0;
        for (const auto endpoint : {left, right}) {
            if (state[endpoint] == State::generated) continue;
            ++missing;
            const auto root = seed_root(endpoint);
            require(root < endpoint && allowed(root), "invalid seed root");
            require(state[root] != State::generated, "missing endpoint has generated root");
            if (state[root] == State::splitless) {
                ++counts.e0;
                structural_pair = true;
            } else {
                ++counts.e1;
            }
        }
        require(missing >= 1, "unblocked hard pair");
        counts.s += static_cast<std::uint32_t>(structural_pair);
        const auto canonical = state[left] != State::generated ? left : right;
        const auto canonical_structural = static_cast<std::uint32_t>(
            state[seed_root(canonical)] == State::splitless
        );
        counts.t += canonical_structural;
        prefix_t += canonical_structural;
        const auto prefix_slack = static_cast<std::int32_t>(2 * prefix_t)
            - static_cast<std::int32_t>(counts.d) + 8;
        counts.minimum_prefix_slack = std::min(
            counts.minimum_prefix_slack,
            prefix_slack
        );
    }
    return counts;
}

std::string describe_hard(
    std::uint32_t n,
    const std::vector<std::uint32_t>& divisors,
    const std::vector<State>& state,
    Counts counts
) {
    std::ostringstream out;
    const auto product = n + 1;
    out << "{\"h\":" << n << ",\"product\":" << product
        << ",\"d\":" << counts.d << ",\"s\":" << counts.s
        << ",\"t\":" << counts.t
        << ",\"E0_count\":" << counts.e0 << ",\"E1_count\":" << counts.e1
        << ",\"endpoint_imbalance_slack\":"
        << static_cast<std::int64_t>(counts.e0) + 8 - counts.e1
        << ",\"power_bridge_slack\":"
        << 3 * static_cast<std::int64_t>(counts.s) - counts.d + 8
        << ",\"canonical_power_slack\":"
        << 2 * static_cast<std::int64_t>(counts.t) - counts.d + 8
        << ",\"minimum_canonical_prefix_slack\":"
        << counts.minimum_prefix_slack
        << ",\"pairs\":[";
    std::vector<std::uint32_t> pair_lefts;
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left < right && allowed(left) && allowed(right)) pair_lefts.push_back(left);
    }
    std::sort(pair_lefts.begin(), pair_lefts.end());
    bool first_pair = true;
    std::uint32_t prefix_index = 0;
    std::uint32_t prefix_t = 0;
    for (const auto left : pair_lefts) {
        const auto right = product / left;
        if (!first_pair) out << ',';
        first_pair = false;
        ++prefix_index;
        bool structural_pair = false;
        out << "{\"prefix_index\":" << prefix_index
            << ",\"pair\":[" << left << ',' << right << "],\"endpoints\":[";
        for (unsigned i = 0; i < 2; ++i) {
            if (i != 0) out << ',';
            const auto endpoint = i == 0 ? left : right;
            out << "{\"value\":" << endpoint << ",\"state\":\""
                << state_name(state[endpoint]) << "\",\"root\":";
            if (state[endpoint] == State::generated) {
                out << "null,\"root_state\":null}";
            } else {
                const auto root = seed_root(endpoint);
                structural_pair = structural_pair || state[root] == State::splitless;
                out << root << ",\"root_state\":\"" << state_name(state[root]) << "\"}";
            }
        }
        const auto canonical = state[left] != State::generated ? left : right;
        const auto canonical_root = seed_root(canonical);
        prefix_t += static_cast<std::uint32_t>(
            state[canonical_root] == State::splitless
        );
        out << "],\"counted_in_s\":" << (structural_pair ? "true" : "false")
            << ",\"canonical_blocker\":" << canonical
            << ",\"canonical_root\":" << canonical_root
            << ",\"counted_in_t\":"
            << (state[canonical_root] == State::splitless ? "true" : "false")
            << ",\"prefix_t\":" << prefix_t
            << ",\"prefix_slack\":"
            << 2 * static_cast<std::int64_t>(prefix_t) - prefix_index + 8 << '}';
    }
    out << "]}";
    return out.str();
}

void write_optional(std::ostream& out, const std::string& value) {
    if (value.empty()) out << "null"; else out << value;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C116_endpoint_invariant LIMIT OUTPUT_JSON\n";
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
        std::vector<std::uint32_t> pair_lefts;
        pair_lefts.reserve(256);

        std::uint64_t hard_count = 0;
        std::uint32_t maximum_d = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t metric_digest = kFnvOffset;
        std::int64_t minimum_endpoint_slack = std::numeric_limits<std::int64_t>::max();
        std::int64_t minimum_power_slack = std::numeric_limits<std::int64_t>::max();
        std::int64_t minimum_canonical_slack = std::numeric_limits<std::int64_t>::max();
        std::int64_t minimum_canonical_prefix_slack =
            std::numeric_limits<std::int64_t>::max();
        std::string minimum_endpoint_detail;
        std::string minimum_power_detail;
        std::string minimum_canonical_detail;
        std::string minimum_canonical_prefix_detail;
        std::string endpoint_failure;
        std::string power_failure;
        std::string canonical_failure;
        std::string canonical_prefix_failure;

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

            ++hard_count;
            const auto counts = endpoint_counts(n, divisors, state, pair_lefts);
            require(counts.d > 0 && counts.s <= counts.d, "invalid hard counts");
            require(counts.d - counts.s <= counts.e1, "first counting bridge failed");
            require(counts.e0 <= 2 * counts.s, "second counting bridge failed");
            require(counts.t <= counts.s, "canonical count exceeds structural pairs");
            maximum_d = std::max(maximum_d, counts.d);
            fnv_u64(metric_digest, n);
            fnv_u64(metric_digest, counts.d);
            fnv_u64(metric_digest, counts.s);

            const auto endpoint_slack =
                static_cast<std::int64_t>(counts.e0) + 8 - counts.e1;
            const auto power_slack =
                3 * static_cast<std::int64_t>(counts.s) - counts.d + 8;
            const auto canonical_slack =
                2 * static_cast<std::int64_t>(counts.t) - counts.d + 8;
            if (endpoint_slack < minimum_endpoint_slack) {
                minimum_endpoint_slack = endpoint_slack;
                minimum_endpoint_detail = describe_hard(n, divisors, state, counts);
            }
            if (power_slack < minimum_power_slack) {
                minimum_power_slack = power_slack;
                minimum_power_detail = describe_hard(n, divisors, state, counts);
            }
            if (canonical_slack < minimum_canonical_slack) {
                minimum_canonical_slack = canonical_slack;
                minimum_canonical_detail = describe_hard(n, divisors, state, counts);
            }
            if (counts.minimum_prefix_slack < minimum_canonical_prefix_slack) {
                minimum_canonical_prefix_slack = counts.minimum_prefix_slack;
                minimum_canonical_prefix_detail = describe_hard(n, divisors, state, counts);
            }
            if (endpoint_slack < 0 && endpoint_failure.empty()) {
                endpoint_failure = describe_hard(n, divisors, state, counts);
            }
            if (power_slack < 0 && power_failure.empty()) {
                power_failure = describe_hard(n, divisors, state, counts);
            }
            if (canonical_slack < 0 && canonical_failure.empty()) {
                canonical_failure = describe_hard(n, divisors, state, counts);
            }
            if (counts.minimum_prefix_slack < 0 && canonical_prefix_failure.empty()) {
                canonical_prefix_failure = describe_hard(n, divisors, state, counts);
            }
        }

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C116-endpoint-invariant-cpp-v2\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"hard_holes\":" << hard_count << ",\n"
            << "  \"maximum_d\":" << maximum_d << ",\n"
            << "  \"minimum_endpoint_imbalance_slack\":" << minimum_endpoint_slack << ",\n"
            << "  \"minimum_power_bridge_slack\":" << minimum_power_slack << ",\n"
            << "  \"minimum_canonical_power_slack\":" << minimum_canonical_slack << ",\n"
            << "  \"minimum_canonical_prefix_slack\":"
            << minimum_canonical_prefix_slack << ",\n"
            << "  \"first_endpoint_imbalance_failure\":";
        write_optional(out, endpoint_failure);
        out << ",\n  \"first_power_bridge_failure\":";
        write_optional(out, power_failure);
        out << ",\n  \"first_canonical_power_failure\":";
        write_optional(out, canonical_failure);
        out << ",\n  \"first_canonical_prefix_failure\":";
        write_optional(out, canonical_prefix_failure);
        out << ",\n  \"minimum_endpoint_detail\":" << minimum_endpoint_detail
            << ",\n  \"minimum_power_detail\":" << minimum_power_detail
            << ",\n  \"minimum_canonical_detail\":" << minimum_canonical_detail
            << ",\n  \"minimum_canonical_prefix_detail\":"
            << minimum_canonical_prefix_detail
            << ",\n  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\"," 
            << "\"classification_2_through_limit\":\"" << hex_u64(classification_digest)
            << "\",\"hard_h_d_s\":\"" << hex_u64(metric_digest) << "\"}\n}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        const auto seconds = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started
        ).count();
        std::cout << "limit=" << limit << " hard=" << hard_count
                  << " max_d=" << maximum_d
                  << " min_endpoint_slack=" << minimum_endpoint_slack
                  << " min_power_slack=" << minimum_power_slack
                  << " min_canonical_slack=" << minimum_canonical_slack
                  << " min_prefix_slack=" << minimum_canonical_prefix_slack
                  << " seconds=" << std::fixed << std::setprecision(3) << seconds << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
