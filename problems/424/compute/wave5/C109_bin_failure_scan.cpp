#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr std::uint32_t kMaximumLimit = 4'000'000'000U;
constexpr unsigned kMaximumThreshold = 32;
constexpr unsigned kMaximumBin = 31;
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
        const auto step = 2ULL * p;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= maximum;
             multiple += step) {
            auto& entry = odd_spf[static_cast<std::size_t>(multiple >> 1)];
            if (entry == 0) entry = static_cast<std::uint16_t>(p);
        }
    }
}

std::uint32_t prime_factor(
    std::uint32_t value, const std::vector<std::uint16_t>& odd_spf
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
    while (value > 1) {
        const auto p = prime_factor(value, odd_spf);
        const auto old_size = divisors.size();
        std::uint32_t power = 1;
        do {
            value /= p;
            power *= p;
            for (std::size_t i = 0; i < old_size; ++i) {
                divisors.push_back(divisors[i] * power);
            }
        } while (value > 1 && value % p == 0);
    }
}

struct Classification {
    State state = State::other;
    std::uint32_t pair_count = 0;
};

Classification classify(
    std::uint32_t n,
    const std::vector<std::uint16_t>& odd_spf,
    const std::vector<State>& state,
    std::vector<std::uint32_t>& divisors,
    std::vector<std::pair<std::uint32_t, std::uint32_t>>& pairs
) {
    const auto product = n + 1;
    enumerate_divisors(product, odd_spf, divisors);
    pairs.clear();
    bool generated = false;
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = product / left;
        if (left >= right) continue;
        if (!allowed(left) || !allowed(right)) continue;
        pairs.emplace_back(left, right);
        generated = generated ||
                    (state[left] == State::generated && state[right] == State::generated);
    }
    if (generated) return {State::generated, static_cast<std::uint32_t>(pairs.size())};
    if (pairs.empty()) return {State::splitless, 0};
    if ((n & 1U) == 0) {
        const bool easy_seed_three =
            product % 3 == 0 && product / 3 != 3 && allowed(product / 3);
        if (!easy_seed_three) {
            return {State::hard, static_cast<std::uint32_t>(pairs.size())};
        }
    }
    return {State::other, static_cast<std::uint32_t>(pairs.size())};
}

std::uint32_t seed_root(std::uint32_t endpoint) {
    const auto shifted = endpoint - 1;
    return 1 + (shifted >> std::countr_zero(shifted));
}

struct Failure {
    unsigned k = 0;
    unsigned d_parameter = 0;
    unsigned bin = 0;
    std::uint64_t count = 0;
    std::vector<std::uint32_t> roots;
};

void write_failure(std::ostream& out, const Failure& failure) {
    out << "{\"k\":" << failure.k
        << ",\"D\":" << failure.d_parameter
        << ",\"dyadic_bin\":" << failure.bin
        << ",\"count\":" << failure.count
        << ",\"lhs_D_times_count\":" << failure.d_parameter * failure.count
        << ",\"rhs_2_to_j\":" << (1ULL << failure.bin)
        << ",\"roots\":[";
    for (std::size_t i = 0; i < failure.roots.size(); ++i) {
        if (i != 0) out << ',';
        out << failure.roots[i];
    }
    out << "]}";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C109_bin_failure_scan LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 1'000 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [1000,4000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((static_cast<std::uint64_t>(limit) + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint8_t> maximum_d(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
        std::vector<std::uint32_t> roots;
        divisors.reserve(4096);
        pairs.reserve(2048);
        roots.reserve(2048);

        std::uint64_t bin_counts[kMaximumThreshold + 1][kMaximumBin + 1]{};
        std::uint64_t hard_count = 0;
        std::uint32_t maximum_pair_count = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint32_t failure_source = 0;
        std::vector<Failure> failures;

        for (std::uint32_t n = 2; n <= limit; ++n) {
            Classification current;
            if (n == 2 || n == 3) {
                current = {State::generated, 0};
            } else if (allowed(n)) {
                current = classify(n, odd_spf, state, divisors, pairs);
            }
            state[n] = current.state;
            fnv_byte(classification_digest, static_cast<std::uint8_t>(current.state));
            if (current.state == State::hard) {
                ++hard_count;
                maximum_pair_count = std::max(maximum_pair_count, current.pair_count);
                const auto capped = std::min<unsigned>(current.pair_count, kMaximumThreshold);
                roots.clear();
                for (const auto [left, right] : pairs) {
                    for (const auto endpoint : {left, right}) {
                        if (state[endpoint] == State::generated) continue;
                        const auto root = seed_root(endpoint);
                        if (state[root] != State::splitless) roots.push_back(root);
                    }
                }
                std::sort(roots.begin(), roots.end());
                roots.erase(std::unique(roots.begin(), roots.end()), roots.end());
                bool touched[kMaximumThreshold + 1]{};
                for (const auto root : roots) {
                    const auto old = static_cast<unsigned>(maximum_d[root]);
                    if (capped <= old) continue;
                    const auto bin = static_cast<unsigned>(std::bit_width(root - 1) - 1);
                    for (unsigned k = old + 1; k <= capped; ++k) {
                        ++bin_counts[k][bin];
                        touched[k] = true;
                    }
                    maximum_d[root] = static_cast<std::uint8_t>(capped);
                }
                for (unsigned k = 2; k <= capped; ++k) {
                    if (!touched[k]) continue;
                    const std::uint64_t d_parameter = k - 1;
                    for (unsigned bin = 0; bin <= kMaximumBin; ++bin) {
                        const auto count = bin_counts[k][bin];
                        if (d_parameter * count <= (1ULL << bin)) continue;
                        Failure failure;
                        failure.k = k;
                        failure.d_parameter = static_cast<unsigned>(d_parameter);
                        failure.bin = bin;
                        failure.count = count;
                        const auto lower = 1ULL << bin;
                        const auto upper = 1ULL << (bin + 1);
                        for (std::uint64_t root = lower + 1; root <= upper && root <= n; ++root) {
                            if (maximum_d[static_cast<std::size_t>(root)] >= k) {
                                failure.roots.push_back(static_cast<std::uint32_t>(root));
                            }
                        }
                        failures.push_back(std::move(failure));
                    }
                }
                if (!failures.empty()) {
                    failure_source = n;
                    break;
                }
            }
            if (n == limit) break;
        }

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n  \"schema\":\"C109-first-C104-BIN-failure-v1\",\n"
            << "  \"requested_limit\":" << limit << ",\n"
            << "  \"scanned_through\":" << (failure_source == 0 ? limit : failure_source) << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"hard_count_scanned\":" << hard_count << ",\n"
            << "  \"maximum_pair_count_scanned\":" << maximum_pair_count << ",\n"
            << "  \"first_failure_source_h\":";
        if (failure_source == 0) out << "null";
        else out << failure_source;
        out << ",\n  \"failures_at_first_source\":[";
        for (std::size_t i = 0; i < failures.size(); ++i) {
            if (i != 0) out << ',';
            write_failure(out, failures[i]);
        }
        out << "],\n  \"classification_digest\":\"" << hex_u64(classification_digest)
            << "\"\n}\n";
        std::cout << "scanned_through=" << (failure_source == 0 ? limit : failure_source)
                  << " hard=" << hard_count << " failures=" << failures.size();
        if (failure_source != 0) std::cout << " first_h=" << failure_source;
        std::cout << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
