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
#include <utility>
#include <vector>

namespace {

constexpr std::uint32_t kMaximumLimit = 100'000'000U;
constexpr unsigned kFixedBits = 56;
constexpr std::uint64_t kFixedScale = 1ULL << kFixedBits;
constexpr unsigned kThresholdMaximum = 16;
constexpr unsigned kBinMaximum = 31;
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

std::uint32_t seed_root_from_missing_odd(std::uint32_t endpoint) {
    if ((endpoint & 1U) == 0 || endpoint <= 1) {
        throw std::runtime_error("witness endpoint is not an odd value >1");
    }
    const auto shifted = endpoint - 1;
    const auto root = (shifted >> std::countr_zero(shifted)) + 1;
    if ((root & 1U) != 0) throw std::runtime_error("seed root is not even");
    return root;
}

std::vector<std::uint32_t> checkpoint_cutoffs(std::uint32_t limit) {
    std::vector<std::uint32_t> values = {
        1'000U, 3'000U, 10'000U, 30'000U, 100'000U, 300'000U,
        1'000'000U, 3'000'000U, 10'000'000U, 30'000'000U,
        100'000'000U, limit
    };
    std::erase_if(values, [limit](std::uint32_t x) { return x > limit; });
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

struct ThresholdStats {
    std::uint64_t hard_sources = 0;
    std::uint64_t root_count = 0;
    std::uint64_t fixed_lower_numerator = 0;
    std::uint64_t bin_count[kBinMaximum + 1]{};
    std::uint64_t bin_fixed_lower[kBinMaximum + 1]{};
};

struct Failure {
    bool set = false;
    std::uint32_t x = 0;
    std::uint32_t source = 0;
    std::uint32_t root = 0;
    unsigned d = 0;
    unsigned bin = 0;
    std::uint64_t lhs = 0;
    std::uint64_t rhs = 0;
};

struct CandidateFailures {
    Failure bin_linear[kThresholdMaximum + 1];
    Failure bin_quadratic[kThresholdMaximum + 1];
    Failure prefix_linear[kThresholdMaximum + 1];
    Failure sigma_le_one[kThresholdMaximum + 1];
    Failure d_sigma_le_one[kThresholdMaximum + 1];
    Failure sigma_le_d[kThresholdMaximum + 1];
};

struct Checkpoint {
    std::uint32_t x = 0;
    std::vector<ThresholdStats> stats;
};

void record_failure(
    Failure& failure,
    std::uint32_t x,
    std::uint32_t source,
    std::uint32_t root,
    unsigned d,
    unsigned bin,
    std::uint64_t lhs,
    std::uint64_t rhs
) {
    if (!failure.set) failure = {true, x, source, root, d, bin, lhs, rhs};
}

void write_fraction(
    std::ostream& out,
    std::uint64_t numerator,
    std::uint64_t denominator
) {
    const auto divisor = std::gcd(numerator, denominator);
    out << "{\"numerator\":" << numerator / divisor
        << ",\"denominator\":" << denominator / divisor << '}';
}

void write_failure(std::ostream& out, const Failure& failure) {
    if (!failure.set) {
        out << "null";
        return;
    }
    out << "{\"X\":" << failure.x
        << ",\"source_h\":" << failure.source
        << ",\"last_inserted_root\":" << failure.root
        << ",\"D\":" << failure.d
        << ",\"dyadic_bin\":" << failure.bin
        << ",\"lhs\":" << failure.lhs
        << ",\"rhs\":" << failure.rhs << '}';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C104_reducible_root_census LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 1'000 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [1000,100000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        const auto started = std::chrono::steady_clock::now();

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((limit + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        const auto spf_finished = std::chrono::steady_clock::now();

        std::vector<State> state(static_cast<std::size_t>(limit) + 1);
        // max_threshold[r] is min(16, max d(h)) over processed hard h
        // whose non-splitless witness-root set contains r.
        std::vector<std::uint8_t> max_threshold(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
        std::vector<std::uint32_t> roots;
        divisors.reserve(2048);
        pairs.reserve(1024);
        roots.reserve(1024);

        std::vector<ThresholdStats> stats(kThresholdMaximum + 1);
        CandidateFailures failures;
        const auto wanted = checkpoint_cutoffs(limit);
        std::size_t next_checkpoint = 0;
        std::vector<Checkpoint> checkpoints;

        std::uint64_t generated_count = 0;
        std::uint64_t splitless_count = 0;
        std::uint64_t hard_count = 0;
        std::uint64_t hard_with_reducible_root = 0;
        std::uint32_t maximum_pair_count = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::uint64_t root_event_digest = kFnvOffset;

        for (std::uint32_t x = 2; x <= limit; ++x) {
            Classification classified;
            if (x == 2 || x == 3) {
                classified = {State::generated, 0};
            } else if (allowed(x)) {
                classified = classify(x, odd_spf, state, divisors, pairs);
            }
            state[x] = classified.state;
            fnv_byte(classification_digest, static_cast<std::uint8_t>(classified.state));

            if (classified.state == State::generated) ++generated_count;
            if (classified.state == State::splitless) ++splitless_count;
            if (classified.state == State::hard) {
                ++hard_count;
                maximum_pair_count = std::max(maximum_pair_count, classified.pair_count);
                const auto capped = std::min<unsigned>(
                    classified.pair_count, kThresholdMaximum
                );
                for (unsigned k = 1; k <= capped; ++k) ++stats[k].hard_sources;

                roots.clear();
                for (const auto [left, right] : pairs) {
                    bool pair_blocked = false;
                    for (const auto endpoint : {left, right}) {
                        if (state[endpoint] == State::generated) continue;
                        pair_blocked = true;
                        const auto root = seed_root_from_missing_odd(endpoint);
                        if (state[root] == State::generated) {
                            throw std::runtime_error("missing endpoint has generated root");
                        }
                        if (state[root] != State::splitless) roots.push_back(root);
                    }
                    if (!pair_blocked) {
                        throw std::runtime_error("hard source has an unblocked pair");
                    }
                }
                std::sort(roots.begin(), roots.end());
                roots.erase(std::unique(roots.begin(), roots.end()), roots.end());
                if (!roots.empty()) ++hard_with_reducible_root;

                std::uint32_t last_inserted_root[kThresholdMaximum + 1]{};
                bool touched[kThresholdMaximum + 1]{};
                unsigned minimum_touched_bin[kThresholdMaximum + 1];
                std::fill(
                    std::begin(minimum_touched_bin),
                    std::end(minimum_touched_bin),
                    kBinMaximum + 1
                );

                for (const auto root : roots) {
                    const auto old = static_cast<unsigned>(max_threshold[root]);
                    if (capped <= old) continue;
                    const auto denominator = root - 1;
                    const auto bin = static_cast<unsigned>(std::bit_width(denominator) - 1);
                    if (bin > kBinMaximum) throw std::runtime_error("dyadic bin overflow");
                    const auto fixed_term = kFixedScale / denominator;
                    for (unsigned k = old + 1; k <= capped; ++k) {
                        ++stats[k].root_count;
                        stats[k].fixed_lower_numerator += fixed_term;
                        ++stats[k].bin_count[bin];
                        stats[k].bin_fixed_lower[bin] += fixed_term;
                        touched[k] = true;
                        last_inserted_root[k] = root;
                        minimum_touched_bin[k] = std::min(minimum_touched_bin[k], bin);
                    }
                    max_threshold[root] = static_cast<std::uint8_t>(capped);
                    fnv_u64(root_event_digest, x);
                    fnv_u64(root_event_digest, root);
                    fnv_u64(root_event_digest, old);
                    fnv_u64(root_event_digest, capped);
                }

                for (unsigned k = 2; k <= kThresholdMaximum; ++k) {
                    if (!touched[k]) continue;
                    const std::uint64_t d = k - 1;
                    for (unsigned bin = minimum_touched_bin[k]; bin <= kBinMaximum; ++bin) {
                        const auto count = stats[k].bin_count[bin];
                        const auto capacity = 1ULL << bin;
                        if (d * count > capacity) {
                            record_failure(
                                failures.bin_linear[k], x, x, last_inserted_root[k],
                                static_cast<unsigned>(d), bin, d * count, capacity
                            );
                        }
                        if (d * d * count > capacity) {
                            record_failure(
                                failures.bin_quadratic[k], x, x, last_inserted_root[k],
                                static_cast<unsigned>(d), bin, d * d * count, capacity
                            );
                        }
                    }
                    std::uint64_t prefix = 0;
                    for (unsigned bin = 0; bin <= kBinMaximum; ++bin) {
                        prefix += stats[k].bin_count[bin];
                        const auto capacity = 1ULL << (bin + 1);
                        if (d * prefix > capacity) {
                            record_failure(
                                failures.prefix_linear[k], x, x, last_inserted_root[k],
                                static_cast<unsigned>(d), bin, d * prefix, capacity
                            );
                        }
                    }
                    const auto lower = stats[k].fixed_lower_numerator;
                    if (lower > kFixedScale) {
                        record_failure(
                            failures.sigma_le_one[k], x, x, last_inserted_root[k],
                            static_cast<unsigned>(d), 0, lower, kFixedScale
                        );
                    }
                    if (d * lower > kFixedScale) {
                        record_failure(
                            failures.d_sigma_le_one[k], x, x, last_inserted_root[k],
                            static_cast<unsigned>(d), 0, d * lower, kFixedScale
                        );
                    }
                    if (lower > d * kFixedScale) {
                        record_failure(
                            failures.sigma_le_d[k], x, x, last_inserted_root[k],
                            static_cast<unsigned>(d), 0, lower, d * kFixedScale
                        );
                    }
                }
            }

            if ((x & 1U) != 0 && classified.state != State::generated && allowed(x)) {
                const auto parent = (x + 1) / 2;
                if (!allowed(parent) || state[parent] == State::generated) {
                    throw std::runtime_error("odd hole has a nonhole parent");
                }
            }

            if (next_checkpoint < wanted.size() && x == wanted[next_checkpoint]) {
                checkpoints.push_back({x, stats});
                ++next_checkpoint;
            }
        }
        if (checkpoints.size() != wanted.size()) {
            throw std::runtime_error("not all checkpoints were emitted");
        }
        const auto finished = std::chrono::steady_clock::now();

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C104-reducible-root-census-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"fixed_point\":{\"bits\":" << kFixedBits
            << ",\"scale\":" << kFixedScale
            << ",\"lower_rule\":\"sum floor(scale/(r-1))\""
            << ",\"upper_rule\":\"lower_numerator+root_count\"},\n"
            << "  \"definitions\":{"
            << "\"hard_source\":\"C55/C85 hard even hole h\","
            << "\"witness_root\":\"1+(p-1)/2^v2(p-1) for a missing odd endpoint p\","
            << "\"reducible\":\"witness root whose state is not structural splitless\","
            << "\"threshold_k\":\"sources satisfy d(h)>=k; D=k-1\","
            << "\"dyadic_bin_j\":\"2^j<=r-1<2^(j+1)\"},\n"
            << "  \"totals\":{\"generated\":" << generated_count
            << ",\"structural_splitless\":" << splitless_count
            << ",\"hard\":" << hard_count
            << ",\"hard_with_reducible_root\":" << hard_with_reducible_root
            << ",\"maximum_pair_count\":" << maximum_pair_count << "},\n"
            << "  \"checkpoints\":[\n";

        for (std::size_t ci = 0; ci < checkpoints.size(); ++ci) {
            const auto& checkpoint = checkpoints[ci];
            out << "    {\"X\":" << checkpoint.x << ",\"thresholds\":[\n";
            for (unsigned k = 1; k <= kThresholdMaximum; ++k) {
                const auto& row = checkpoint.stats[k];
                out << "      {\"k\":" << k << ",\"D\":" << k - 1
                    << ",\"hard_sources\":" << row.hard_sources
                    << ",\"root_count\":" << row.root_count
                    << ",\"reciprocal_interval\":{\"lower\":";
                write_fraction(out, row.fixed_lower_numerator, kFixedScale);
                out << ",\"upper\":";
                write_fraction(
                    out, row.fixed_lower_numerator + row.root_count, kFixedScale
                );
                out << ",\"floor_numerator\":" << row.fixed_lower_numerator
                    << ",\"error_numerator_lt\":" << row.root_count << "}"
                    << ",\"dyadic_bins\":[";
                bool first_bin = true;
                for (unsigned bin = 0; bin <= kBinMaximum; ++bin) {
                    if (row.bin_count[bin] == 0) continue;
                    if (!first_bin) out << ',';
                    first_bin = false;
                    out << "{\"j\":" << bin
                        << ",\"lower\":" << (1ULL << bin)
                        << ",\"upper_exclusive\":" << (1ULL << (bin + 1))
                        << ",\"count\":" << row.bin_count[bin]
                        << ",\"fixed_floor_numerator\":"
                        << row.bin_fixed_lower[bin] << '}';
                }
                out << "]}" << (k == kThresholdMaximum ? "\n" : ",\n");
            }
            out << "    ]}" << (ci + 1 == checkpoints.size() ? "\n" : ",\n");
        }
        out << "  ],\n  \"candidate_inequality_failures\":[\n";
        for (unsigned k = 2; k <= kThresholdMaximum; ++k) {
            out << "    {\"k\":" << k << ",\"D\":" << k - 1
                << ",\"D_times_bin_count_le_2j\":";
            write_failure(out, failures.bin_linear[k]);
            out << ",\"D2_times_bin_count_le_2j\":";
            write_failure(out, failures.bin_quadratic[k]);
            out << ",\"D_times_prefix_count_le_2j1\":";
            write_failure(out, failures.prefix_linear[k]);
            out << ",\"Sigma_le_1\":";
            write_failure(out, failures.sigma_le_one[k]);
            out << ",\"D_times_Sigma_le_1\":";
            write_failure(out, failures.d_sigma_le_one[k]);
            out << ",\"Sigma_le_D\":";
            write_failure(out, failures.sigma_le_d[k]);
            out << '}' << (k == kThresholdMaximum ? "\n" : ",\n");
        }
        const auto spf_seconds = std::chrono::duration<double>(spf_finished - started).count();
        const auto scan_seconds = std::chrono::duration<double>(finished - spf_finished).count();
        const auto allocated_bytes =
            static_cast<std::uint64_t>(odd_spf.size()) * sizeof(std::uint16_t) +
            static_cast<std::uint64_t>(state.size()) * sizeof(State) +
            static_cast<std::uint64_t>(max_threshold.size()) * sizeof(std::uint8_t);
        out << "  ],\n"
            << "  \"digests\":{\"algorithm\":\"FNV-1a-64 little-endian\""
            << ",\"classification_2_through_limit\":\""
            << hex_u64(classification_digest) << "\""
            << ",\"reducible_root_upgrade_events\":\""
            << hex_u64(root_event_digest) << "\"},\n"
            << "  \"memory_bytes\":" << allocated_bytes << ",\n"
            << std::fixed << std::setprecision(6)
            << "  \"timing_seconds\":{\"spf\":" << spf_seconds
            << ",\"scan\":" << scan_seconds << "}\n"
            << "}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " hard=" << hard_count
                  << " reducible_union=" << stats[1].root_count
                  << " fixed_lower=" << stats[1].fixed_lower_numerator
                  << '/' << kFixedScale
                  << " seconds=" << std::fixed << std::setprecision(3)
                  << std::chrono::duration<double>(finished - started).count()
                  << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
