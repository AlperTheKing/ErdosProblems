#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace {

enum class State : std::uint8_t {
    other = 0,
    generated = 1,
    splitless = 2,
    hard = 3,
};

constexpr std::uint64_t kFnvOffset = 14'695'981'039'346'656'037ULL;
constexpr std::uint64_t kFnvPrime = 1'099'511'628'211ULL;

struct Certificate {
    std::uint32_t source = 0;
    std::uint32_t endpoint = 0;
    std::uint32_t d = 0;
};

struct Bin {
    std::uint64_t positive_roots = 0;
    std::uint64_t token_sum = 0;
    std::uint64_t sqrt_token_sum = 0;
    std::uint64_t sqrt_token_sum_excluding_least = 0;
    std::uint64_t moving_sqrt_token_sum = 0;
    std::uint64_t moving_sqrt_token_sum_excluding_least = 0;
    std::uint32_t maximum_q = 0;
    std::array<std::uint64_t, 256> threshold_counts{};
};

struct Failure {
    bool set = false;
    std::uint32_t x = 0;
    std::uint32_t root = 0;
    unsigned j = 0;
    std::uint64_t lhs = 0;
    std::uint64_t rhs = 0;
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
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= maximum;
             multiple += 2ULL * p) {
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
        if (left >= right || !allowed(left) || !allowed(right)) continue;
        pairs.emplace_back(left, right);
        generated = generated ||
                    (state[left] == State::generated &&
                     state[right] == State::generated);
    }
    if (generated) return {State::generated, static_cast<std::uint32_t>(pairs.size())};
    if (pairs.empty()) return {State::splitless, 0};
    if ((n & 1U) == 0) {
        const bool seed_three_easy =
            product % 3 == 0 && product / 3 != 3 && allowed(product / 3);
        if (!seed_three_easy) {
            return {State::hard, static_cast<std::uint32_t>(pairs.size())};
        }
    }
    return {State::other, static_cast<std::uint32_t>(pairs.size())};
}

std::uint32_t seed_root(std::uint32_t endpoint) {
    const auto shifted = endpoint - 1;
    return 1 + (shifted >> std::countr_zero(shifted));
}

std::uint32_t ceil_sqrt(std::uint32_t n) {
    std::uint32_t result = 0;
    while (result * result < n) ++result;
    return result;
}

void write_failure(std::ostream& out, const Failure& failure) {
    if (!failure.set) {
        out << "null";
        return;
    }
    out << "{\"X\":" << failure.x
        << ",\"root\":" << failure.root
        << ",\"j\":" << failure.j
        << ",\"lhs\":" << failure.lhs
        << ",\"rhs\":" << failure.rhs << '}';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C113_vulnerable_prefix_scan LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 2 || parsed_limit >= std::numeric_limits<std::uint32_t>::max()) {
            throw std::runtime_error("LIMIT lies outside the uint32 range");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((limit + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint8_t> maximum_d(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
        std::unordered_map<std::uint32_t, Certificate> certificates;
        std::vector<Bin> bins(32);
        divisors.reserve(2048);
        pairs.reserve(1024);
        certificates.reserve(static_cast<std::size_t>(limit / 100));

        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t hard_sources = 0;
        std::uint64_t upgrade_events = 0;
        std::uint32_t maximum_pair_count = 0;
        Failure weighted_failure;
        Failure c104_bin_failure;

        for (std::uint32_t n = 2; n <= limit; ++n) {
            Classification classified;
            if (n == 2 || n == 3) {
                classified = {State::generated, 0};
            } else if (allowed(n)) {
                classified = classify(n, odd_spf, state, divisors, pairs);
            }
            state[n] = classified.state;
            fnv_byte(classification_digest, static_cast<std::uint8_t>(classified.state));
            if (classified.state != State::hard) continue;

            ++hard_sources;
            maximum_pair_count = std::max(maximum_pair_count, classified.pair_count);
            std::unordered_map<std::uint32_t, std::uint32_t> witnessed;
            witnessed.reserve(pairs.size());
            for (const auto [left, right] : pairs) {
                bool blocked = false;
                for (const auto endpoint : {left, right}) {
                    if (state[endpoint] == State::generated) continue;
                    blocked = true;
                    const auto root = seed_root(endpoint);
                    if (state[root] == State::generated) {
                        throw std::runtime_error("generated witness root");
                    }
                    if (state[root] != State::splitless) {
                        witnessed.emplace(root, endpoint);
                    }
                }
                if (!blocked) throw std::runtime_error("unblocked hard pair");
            }

            for (const auto [root, endpoint] : witnessed) {
                const auto old_d = static_cast<std::uint32_t>(maximum_d[root]);
                const auto new_d = classified.pair_count;
                if (new_d <= old_d) continue;
                if (new_d > std::numeric_limits<std::uint8_t>::max()) {
                    throw std::runtime_error("pair count exceeds uint8 storage");
                }
                const auto old_q = old_d == 0 ? 0 : old_d - 1;
                const auto new_q = new_d - 1;
                const auto denominator = root - 1;
                const auto j = static_cast<unsigned>(std::bit_width(denominator) - 1);
                auto& bin = bins[j];
                if (old_q == 0 && new_q > 0) ++bin.positive_roots;
                bin.token_sum += new_q - old_q;
                bin.maximum_q = std::max(bin.maximum_q, new_q);
                for (auto d = old_q + 1; d <= new_q; ++d) {
                    ++bin.threshold_counts[d];
                    const auto capacity = 1ULL << j;
                    const auto lhs = static_cast<std::uint64_t>(d) *
                                     bin.threshold_counts[d];
                    if (!c104_bin_failure.set && lhs > capacity) {
                        c104_bin_failure = {true, n, root, j, lhs, capacity};
                    }
                }
                maximum_d[root] = static_cast<std::uint8_t>(new_d);
                certificates[root] = {n, endpoint, new_d};
                ++upgrade_events;

                const auto capacity = 1ULL << j;
                if (!weighted_failure.set && bin.token_sum > capacity) {
                    weighted_failure = {
                        true, n, root, j, bin.token_sum, capacity
                    };
                }
            }
        }

        std::vector<std::pair<std::uint32_t, Certificate>> top;
        top.reserve(certificates.size());
        for (const auto& item : certificates) {
            if (item.second.d >= 2) top.push_back(item);
        }
        std::sort(top.begin(), top.end(), [](const auto& a, const auto& b) {
            if (a.second.d != b.second.d) return a.second.d > b.second.d;
            return a.first < b.first;
        });
        if (top.size() > 64) top.resize(64);

        std::vector<std::vector<std::pair<std::uint32_t, std::uint32_t>>> by_bin(32);
        for (const auto& [root, cert] : certificates) {
            if (cert.d < 2) continue;
            const auto j = static_cast<unsigned>(std::bit_width(root - 1) - 1);
            by_bin[j].emplace_back(root, cert.d - 1);
        }
        Failure lower_moving_sqrt_deadline_failure;
        Failure lower_moving_sqrt_deadline_excluding_least_failure;
        for (unsigned j = 0; j < by_bin.size(); ++j) {
            auto& roots = by_bin[j];
            std::sort(roots.begin(), roots.end());
            std::uint64_t prefix = 0;
            std::uint64_t prefix_excluding_least = 0;
            for (std::size_t i = 0; i < roots.size(); ++i) {
                const auto [root, q] = roots[i];
                const auto uncapped_weight = ceil_sqrt(q);
                const auto weight = std::min<std::uint32_t>(uncapped_weight, j);
                prefix += weight;
                bins[j].sqrt_token_sum += uncapped_weight;
                bins[j].moving_sqrt_token_sum += weight;
                if (i > 0) {
                    prefix_excluding_least += weight;
                    bins[j].sqrt_token_sum_excluding_least += uncapped_weight;
                    bins[j].moving_sqrt_token_sum_excluding_least += weight;
                }
                const auto rhs = static_cast<std::uint64_t>(root - (1U << j));
                if (!lower_moving_sqrt_deadline_failure.set && prefix > rhs) {
                    lower_moving_sqrt_deadline_failure = {
                        true, limit, root, j, prefix, rhs
                    };
                }
                if (i > 0 && !lower_moving_sqrt_deadline_excluding_least_failure.set &&
                    prefix_excluding_least > rhs) {
                    lower_moving_sqrt_deadline_excluding_least_failure = {
                        true, limit, root, j, prefix_excluding_least, rhs
                    };
                }
            }
        }

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output");
        out << "{\n"
            << "  \"schema\":\"C113-vulnerable-prefix-scan-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"arithmetic\":\"exact integers only\",\n"
            << "  \"hard_sources\":" << hard_sources << ",\n"
            << "  \"maximum_pair_count\":" << maximum_pair_count << ",\n"
            << "  \"root_upgrade_events\":" << upgrade_events << ",\n"
            << "  \"classification_fnv1a64\":\""
            << hex_u64(classification_digest) << "\",\n"
            << "  \"first_C104_BIN_failure\":";
        write_failure(out, c104_bin_failure);
        out << ",\n  \"first_weighted_token_budget_failure\":";
        write_failure(out, weighted_failure);
        out << ",\n  \"lower_moving_sqrt_deadline_failure_at_limit\":";
        write_failure(out, lower_moving_sqrt_deadline_failure);
        out << ",\n  \"lower_moving_sqrt_deadline_excluding_least_failure_at_limit\":";
        write_failure(out, lower_moving_sqrt_deadline_excluding_least_failure);
        out << ",\n  \"bins\":[\n";
        bool first = true;
        for (unsigned j = 0; j < bins.size(); ++j) {
            const auto& bin = bins[j];
            if (bin.token_sum == 0) continue;
            if (!first) out << ",\n";
            first = false;
            out << "    {\"j\":" << j
                << ",\"capacity\":" << (1ULL << j)
                << ",\"positive_root_count\":" << bin.positive_roots
                << ",\"threshold_token_sum\":" << bin.token_sum
                << ",\"sqrt_token_sum\":" << bin.sqrt_token_sum
                << ",\"sqrt_token_sum_excluding_least\":"
                << bin.sqrt_token_sum_excluding_least
                << ",\"moving_sqrt_token_sum\":" << bin.moving_sqrt_token_sum
                << ",\"moving_sqrt_token_sum_excluding_least\":"
                << bin.moving_sqrt_token_sum_excluding_least
                << ",\"maximum_q\":" << bin.maximum_q
                << ",\"threshold_counts\":[";
            for (unsigned d = 1; d <= bin.maximum_q; ++d) {
                if (d > 1) out << ',';
                out << bin.threshold_counts[d];
            }
            out << "]}";
        }
        out << "\n  ],\n  \"largest_q_certificates\":[\n";
        for (std::size_t i = 0; i < top.size(); ++i) {
            const auto& [root, cert] = top[i];
            out << "    {\"root\":" << root
                << ",\"j\":" << (std::bit_width(root - 1) - 1)
                << ",\"q\":" << cert.d - 1
                << ",\"source\":" << cert.source
                << ",\"endpoint\":" << cert.endpoint << '}'
                << (i + 1 == top.size() ? "\n" : ",\n");
        }
        out << "  ],\n  \"vulnerable_boundary_certificates\":[\n";
        std::vector<std::pair<std::uint32_t, Certificate>> small;
        for (const auto& item : certificates) {
            const auto j = static_cast<unsigned>(std::bit_width(item.first - 1) - 1);
            const auto boundary = 1U << j;
            if (item.second.d >= 2 && item.first - boundary <= 8U * j * j) {
                small.push_back(item);
            }
        }
        std::sort(small.begin(), small.end(), [](const auto& a, const auto& b) {
            return a.first < b.first;
        });
        for (std::size_t i = 0; i < small.size(); ++i) {
            const auto& [root, cert] = small[i];
            out << "    {\"root\":" << root
                << ",\"j\":" << (std::bit_width(root - 1) - 1)
                << ",\"q\":" << cert.d - 1
                << ",\"source\":" << cert.source
                << ",\"endpoint\":" << cert.endpoint << '}'
                << (i + 1 == small.size() ? "\n" : ",\n");
        }
        out << "  ]\n}\n";
        if (!out) throw std::runtime_error("could not write output");

        std::cout << "limit=" << limit
                  << " hard=" << hard_sources
                  << " max_d=" << maximum_pair_count
                  << " digest=" << hex_u64(classification_digest)
                  << " C104_BIN_failure=" << (c104_bin_failure.set ? "yes" : "no")
                  << " weighted_failure=" << (weighted_failure.set ? "yes" : "no")
                  << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
