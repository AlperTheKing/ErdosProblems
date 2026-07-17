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

struct Ratio {
    std::uint64_t numerator = 0;
    std::uint64_t denominator = 1;
    std::uint32_t x = 0;

    void observe(std::uint32_t cutoff, std::uint64_t left, std::uint64_t right) {
        if (right == 0) return;
        // LIMIT <= 1e9, so both products are at most 1e18 and fit uint64_t.
        if (left * denominator > numerator * right) {
            numerator = left;
            denominator = right;
            x = cutoff;
        }
    }
};

struct Failure {
    bool found = false;
    std::uint32_t x = 0;
    std::uint64_t left = 0;
    std::uint64_t right = 0;
};

struct Audit {
    std::uint64_t checked_cutoffs = 0;
    std::uint64_t failure_count = 0;
    Failure first_failure;
    Ratio maximum_ratio;
    std::int64_t maximum_excess = std::numeric_limits<std::int64_t>::min();
    std::uint32_t maximum_excess_x = 0;
    std::uint64_t maximum_excess_left = 0;
    std::uint64_t maximum_excess_right = 0;
    std::uint64_t endpoint_left = 0;
    std::uint64_t endpoint_right = 0;

    void observe(std::uint32_t x, std::uint64_t left, std::uint64_t right) {
        ++checked_cutoffs;
        if (left > right) {
            ++failure_count;
            if (!first_failure.found) {
                first_failure = {true, x, left, right};
            }
        }
        maximum_ratio.observe(x, left, right);
        const auto excess = static_cast<std::int64_t>(left) -
                            static_cast<std::int64_t>(right);
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_excess_x = x;
            maximum_excess_left = left;
            maximum_excess_right = right;
        }
        endpoint_left = left;
        endpoint_right = right;
    }
};

struct Checkpoint {
    std::uint32_t x = 0;
    std::uint64_t generated = 0;
    std::uint64_t splitless = 0;
    std::uint64_t hard = 0;
    std::uint64_t active_hard = 0;
    std::uint64_t e_plus = 0;
    std::uint64_t deaths = 0;
};

std::vector<std::uint32_t> checkpoint_cutoffs(std::uint32_t limit) {
    std::vector<std::uint32_t> values = {
        2U, 6U, 54U, 74U, 16'620U, 175'956U, 1'000'000U
    };
    for (std::uint64_t x = 10; x <= limit; x *= 10) {
        values.push_back(static_cast<std::uint32_t>(x));
        if (x > limit / 10) break;
    }
    values.push_back(limit);
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

void write_ratio(std::ostream& out, const Ratio& ratio) {
    const auto divisor = std::gcd(ratio.numerator, ratio.denominator);
    out << "{\"numerator\":" << ratio.numerator
        << ",\"denominator\":" << ratio.denominator
        << ",\"X\":" << ratio.x
        << ",\"reduced_numerator\":" << ratio.numerator / divisor
        << ",\"reduced_denominator\":" << ratio.denominator / divisor
        << '}';
}

void write_failure(std::ostream& out, const Failure& failure) {
    if (!failure.found) {
        out << "null";
        return;
    }
    out << "{\"X\":" << failure.x
        << ",\"left\":" << failure.left
        << ",\"right\":" << failure.right
        << ",\"excess\":" << failure.left - failure.right << '}';
}

void write_audit(
    std::ostream& out,
    const Audit& audit,
    std::uint32_t limit,
    const char* left_name
) {
    out << "{\"checked_cutoffs\":" << audit.checked_cutoffs
        << ",\"failure_count\":" << audit.failure_count
        << ",\"first_failure\":";
    write_failure(out, audit.first_failure);
    out << ",\"max_ratio\":";
    write_ratio(out, audit.maximum_ratio);
    out << ",\"maximum_excess\":{\"value\":" << audit.maximum_excess
        << ",\"X\":" << audit.maximum_excess_x
        << ",\"left\":" << audit.maximum_excess_left
        << ",\"right\":" << audit.maximum_excess_right << "}"
        << ",\"endpoint\":{\"X\":" << limit
        << ",\"" << left_name << "\":" << audit.endpoint_left
        << ",\"e_plus\":" << audit.endpoint_right << "}"
        << ",\"verdict\":\""
        << (audit.first_failure.found ? "fails" : "no_failure_through_limit")
        << "\"}";
}

void verify_c67_prefix(const Audit& terminal, const Audit& all_hard) {
    const auto& a = terminal.maximum_ratio;
    const auto& k = all_hard.maximum_ratio;
    if (terminal.first_failure.found || all_hard.first_failure.found ||
        a.numerator != 656 || a.denominator != 1033 || a.x != 16'620 ||
        k.numerator != 8846 || k.denominator != 9907 || k.x != 175'956) {
        throw std::runtime_error("C67 scalar prefix regression failed");
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C71_tail_bank_cpp LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 2 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [2,1000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        const auto total_started = std::chrono::steady_clock::now();

        const auto maximum_product = limit + 1;
        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>(maximum_product / 2) + 1
        );
        const auto spf_started = std::chrono::steady_clock::now();
        build_odd_spf(maximum_product, odd_spf);
        const auto spf_finished = std::chrono::steady_clock::now();

        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        divisors.reserve(2048);
        const auto wanted_checkpoints = checkpoint_cutoffs(limit);
        std::size_t next_checkpoint = 0;
        std::vector<Checkpoint> checkpoints;
        checkpoints.reserve(wanted_checkpoints.size());

        std::uint64_t generated_count = 0;
        std::uint64_t allowed_count = 0;
        std::uint64_t splitless_count = 0;
        std::uint64_t splitless_half = 0;
        std::uint64_t hard_count = 0;
        std::uint64_t active_hard = 0;
        std::uint64_t deaths = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t trajectory_digest = kFnvOffset;
        Audit terminal_audit;
        Audit all_hard_audit;
        Audit c67_terminal_prefix;
        Audit c67_all_hard_prefix;
        bool captured_c67_prefix = false;

        const auto scan_started = std::chrono::steady_clock::now();
        for (std::uint32_t x = 2; x <= limit; ++x) {
            State current = State::other;
            if (x == 2 || x == 3) {
                current = State::generated;
            } else if (allowed(x)) {
                current = classify(x, odd_spf, state, divisors);
            }
            state[x] = current;

            if (allowed(x)) ++allowed_count;
            if (current == State::generated) ++generated_count;
            if (current == State::splitless) ++splitless_count;
            if (current == State::hard) {
                if ((x & 1U) != 0) {
                    throw std::runtime_error("hard value is not an even root");
                }
                ++hard_count;
                ++active_hard;
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
                        ++deaths;
                    }
                }
            }

            if ((x & 1U) == 0 && state[x / 2] == State::splitless) {
                ++splitless_half;
            }
            const auto e_plus = splitless_count - splitless_half;
            terminal_audit.observe(x, active_hard, e_plus);
            all_hard_audit.observe(x, hard_count, e_plus);

            fnv_byte(classification_digest, static_cast<std::uint8_t>(current));
            fnv_u64(trajectory_digest, x);
            fnv_u64(trajectory_digest, active_hard);
            fnv_u64(trajectory_digest, e_plus);
            fnv_u64(trajectory_digest, hard_count);

            if (x == 1'000'000U) {
                c67_terminal_prefix = terminal_audit;
                c67_all_hard_prefix = all_hard_audit;
                captured_c67_prefix = true;
                verify_c67_prefix(c67_terminal_prefix, c67_all_hard_prefix);
            }

            if (next_checkpoint < wanted_checkpoints.size() &&
                x == wanted_checkpoints[next_checkpoint]) {
                checkpoints.push_back({
                    x,
                    generated_count,
                    splitless_count,
                    hard_count,
                    active_hard,
                    e_plus,
                    deaths,
                });
                ++next_checkpoint;
            }
        }
        const auto scan_finished = std::chrono::steady_clock::now();

        if (hard_count != active_hard + deaths) {
            throw std::runtime_error("hard interval accounting mismatch");
        }
        if (generated_count + (allowed_count - generated_count) != allowed_count) {
            throw std::runtime_error("allowed partition mismatch");
        }
        if (checkpoints.size() != wanted_checkpoints.size()) {
            throw std::runtime_error("checkpoint capture mismatch");
        }

        const auto seconds = [](auto start, auto finish) {
            return std::chrono::duration<double>(finish - start).count();
        };
        const auto spf_seconds = seconds(spf_started, spf_finished);
        const auto scan_seconds = seconds(scan_started, scan_finished);
        const auto total_seconds = seconds(total_started, scan_finished);

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema_version\":1,\n"
            << "  \"lane\":\"Erdos 424 C71\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"definitions\":{"
            << "\"allowed\":\"n>=2 and n mod 3 != 1\","
            << "\"admissible_pair\":\"2<=a<b, a*b=n+1, a and b allowed\","
            << "\"generated\":\"ascending closure from seeds 2 and 3\","
            << "\"A_H\":\"hard roots whose literal seed-2 chain through top_X is all holes\","
            << "\"e_plus\":\"E(X)-E(floor(X/2))\","
            << "\"K\":\"C67 hard holes through X\"},\n"
            << "  \"counts\":{"
            << "\"allowed\":" << allowed_count
            << ",\"generated\":" << generated_count
            << ",\"holes\":" << allowed_count - generated_count
            << ",\"E\":" << splitless_count
            << ",\"K\":" << hard_count
            << ",\"A_H\":" << active_hard
            << ",\"e_plus\":" << terminal_audit.endpoint_right
            << ",\"hard_chain_deaths\":" << deaths << "},\n"
            << "  \"inequalities\":{\n"
            << "    \"A_H_le_e_plus\":";
        write_audit(out, terminal_audit, limit, "A_H");
        out << ",\n    \"K_le_e_plus\":";
        write_audit(out, all_hard_audit, limit, "K");
        out << "\n  },\n"
            << "  \"c67_prefix_check\":";
        if (!captured_c67_prefix) {
            out << "null";
        } else {
            out << "{\"through\":1000000,\"matched\":true,"
                << "\"A_H_max_ratio\":";
            write_ratio(out, c67_terminal_prefix.maximum_ratio);
            out << ",\"K_max_ratio\":";
            write_ratio(out, c67_all_hard_prefix.maximum_ratio);
            out << '}';
        }
        out << ",\n  \"checkpoints\":[\n";
        for (std::size_t i = 0; i < checkpoints.size(); ++i) {
            const auto& row = checkpoints[i];
            out << "    {\"X\":" << row.x
                << ",\"generated\":" << row.generated
                << ",\"E\":" << row.splitless
                << ",\"K\":" << row.hard
                << ",\"A_H\":" << row.active_hard
                << ",\"e_plus\":" << row.e_plus
                << ",\"hard_chain_deaths\":" << row.deaths << '}'
                << (i + 1 == checkpoints.size() ? "\n" : ",\n");
        }
        const auto allocated_bytes =
            static_cast<std::uint64_t>(odd_spf.size()) * sizeof(std::uint16_t) +
            static_cast<std::uint64_t>(state.size()) * sizeof(State);
        out << "  ],\n"
            << "  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\","
            << "\"classification_2_through_limit\":\""
            << hex_u64(classification_digest) << "\","
            << "\"trajectory_X_A_H_e_plus_K\":\""
            << hex_u64(trajectory_digest) << "\"},\n"
            << "  \"resources\":{\"allocated_core_bytes\":"
            << allocated_bytes << ",\"odd_spf_bytes\":"
            << static_cast<std::uint64_t>(odd_spf.size()) * sizeof(std::uint16_t)
            << ",\"state_bytes\":"
            << static_cast<std::uint64_t>(state.size()) * sizeof(State) << "},\n"
            << std::fixed << std::setprecision(6)
            << "  \"timing_seconds\":{\"spf\":" << spf_seconds
            << ",\"scan\":" << scan_seconds
            << ",\"total\":" << total_seconds << "},\n"
            << "  \"compiler\":\"" << __VERSION__ << "\"\n"
            << "}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " generated=" << generated_count
                  << " E=" << splitless_count
                  << " K=" << hard_count
                  << " A_H=" << active_hard
                  << " e_plus=" << terminal_audit.endpoint_right
                  << " A_failures=" << terminal_audit.failure_count
                  << " K_failures=" << all_hard_audit.failure_count
                  << " seconds=" << std::fixed << std::setprecision(3)
                  << total_seconds << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
