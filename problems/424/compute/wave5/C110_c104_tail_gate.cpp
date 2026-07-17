#define main C110_imported_c104_main
#include "C104_reducible_root_census.cpp"
#undef main

#include <array>

namespace {

constexpr unsigned kC110ThresholdMaximum = 64;
constexpr unsigned kC110BinMaximum = 31;
constexpr unsigned kC110ScaleBits = 32;
constexpr std::uint64_t kC110Scale = 1ULL << kC110ScaleBits;
__extension__ using C110UInt128 = unsigned __int128;

struct C110Threshold {
    std::uint64_t root_count = 0;
    std::uint64_t scaled_dyadic_load = 0;
    std::array<std::uint64_t, kC110BinMaximum + 1> bin_count{};
    unsigned occupied_bins = 0;
};

struct C110Failure {
    bool set = false;
    std::uint32_t source = 0;
    std::uint32_t root = 0;
    unsigned d = 0;
    unsigned bin = 0;
    std::uint64_t lhs = 0;
    std::uint64_t rhs = 0;
};

struct C110TargetEvent {
    std::uint32_t root = 0;
    std::uint32_t source = 0;
    std::uint32_t endpoint = 0;
    std::uint32_t pair_count = 0;
    std::uint32_t one_hole_pairs = 0;
    std::uint32_t two_hole_pairs = 0;
};

void c110_record_failure(
    C110Failure& failure,
    std::uint32_t source,
    std::uint32_t root,
    unsigned d,
    unsigned bin,
    std::uint64_t lhs,
    std::uint64_t rhs
) {
    if (!failure.set) failure = {true, source, root, d, bin, lhs, rhs};
}

void c110_write_failure(std::ostream& out, const C110Failure& failure) {
    if (!failure.set) {
        out << "null";
        return;
    }
    out << "{\"source_h\":" << failure.source
        << ",\"last_root\":" << failure.root
        << ",\"D\":" << failure.d
        << ",\"bin\":" << failure.bin
        << ",\"lhs\":" << failure.lhs
        << ",\"rhs\":" << failure.rhs << '}';
}

std::pair<std::uint32_t, std::uint32_t> c110_blocker_profile(
    const std::vector<std::pair<std::uint32_t, std::uint32_t>>& pairs,
    const std::vector<State>& state
) {
    std::uint32_t one_hole = 0;
    std::uint32_t two_hole = 0;
    for (const auto& [left, right] : pairs) {
        const auto holes =
            static_cast<unsigned>(state[left] != State::generated) +
            static_cast<unsigned>(state[right] != State::generated);
        if (holes == 0) throw std::runtime_error("hard pair has no blocker");
        if (holes == 1) ++one_hole;
        if (holes == 2) ++two_hole;
    }
    return {one_hole, two_hole};
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C110_c104_tail_gate LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 1'000 || parsed_limit >= (1ULL << 32)) {
            throw std::runtime_error("LIMIT must lie in [1000,2^32)");
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
        std::vector<std::pair<std::uint32_t, std::uint32_t>> witnessed;
        std::vector<C110Threshold> thresholds(kC110ThresholdMaximum + 1);
        std::array<std::uint64_t, kC110BinMaximum + 1> integrated_load{};
        std::vector<C110TargetEvent> target_events;
        divisors.reserve(2048);
        pairs.reserve(1024);
        witnessed.reserve(1024);

        std::uint64_t hard_sources = 0;
        std::uint32_t maximum_pair_count = 0;
        std::uint64_t classification_digest = kFnvOffset;
        C110Failure bin_failure;
        C110Failure occupied_carleson_failure;
        C110Failure full_carleson_failure;
        C110Failure integrated_failure;

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
            witnessed.clear();
            for (const auto [left, right] : pairs) {
                bool blocked = false;
                for (const auto endpoint : {left, right}) {
                    if (state[endpoint] == State::generated) continue;
                    blocked = true;
                    const auto root = seed_root_from_missing_odd(endpoint);
                    if (state[root] == State::generated) {
                        throw std::runtime_error("missing endpoint has generated root");
                    }
                    if (state[root] != State::splitless) {
                        witnessed.emplace_back(root, endpoint);
                    }
                }
                if (!blocked) throw std::runtime_error("hard source has unblocked pair");
            }
            std::sort(witnessed.begin(), witnessed.end());
            witnessed.erase(
                std::unique(
                    witnessed.begin(), witnessed.end(),
                    [](const auto& a, const auto& b) { return a.first == b.first; }
                ),
                witnessed.end()
            );

            const auto capped = std::min<unsigned>(
                classified.pair_count, kC110ThresholdMaximum
            );
            const auto [one_hole_pairs, two_hole_pairs] =
                c110_blocker_profile(pairs, state);

            for (const auto [root, endpoint] : witnessed) {
                const auto old_d = static_cast<unsigned>(maximum_d[root]);
                if (capped <= old_d) continue;
                const auto denominator = root - 1;
                const auto bin = static_cast<unsigned>(std::bit_width(denominator) - 1);
                if (bin > kC110BinMaximum || bin > kC110ScaleBits) {
                    throw std::runtime_error("dyadic bin exceeds exact scale");
                }

                const auto old_q = old_d == 0 ? 0U : old_d - 1;
                const auto new_q = capped - 1;
                integrated_load[bin] += new_q - old_q;
                if (integrated_load[bin] > (1ULL << bin)) {
                    c110_record_failure(
                        integrated_failure, n, root, 0, bin,
                        integrated_load[bin], 1ULL << bin
                    );
                }

                for (unsigned k = old_d + 1; k <= capped; ++k) {
                    if (k < 2) continue;
                    const auto d = k - 1;
                    auto& threshold = thresholds[k];
                    if (threshold.bin_count[bin]++ == 0) ++threshold.occupied_bins;
                    ++threshold.root_count;
                    threshold.scaled_dyadic_load += 1ULL << (kC110ScaleBits - bin);

                    const auto bin_lhs = d * threshold.bin_count[bin];
                    const auto bin_rhs = 1ULL << bin;
                    if (bin_lhs > bin_rhs) {
                        c110_record_failure(
                            bin_failure, n, root, d, bin, bin_lhs, bin_rhs
                        );
                    }

                    const auto occupied_lhs =
                        static_cast<C110UInt128>(d) * threshold.scaled_dyadic_load;
                    const auto occupied_rhs =
                        static_cast<C110UInt128>(threshold.occupied_bins) * kC110Scale;
                    if (occupied_lhs > occupied_rhs) {
                        c110_record_failure(
                            occupied_carleson_failure, n, root, d, bin,
                            static_cast<std::uint64_t>(occupied_lhs),
                            static_cast<std::uint64_t>(occupied_rhs)
                        );
                    }

                    const auto available_bins = std::bit_width(n);
                    const auto full_rhs =
                        static_cast<C110UInt128>(available_bins) * kC110Scale;
                    if (occupied_lhs > full_rhs) {
                        c110_record_failure(
                            full_carleson_failure, n, root, d, bin,
                            static_cast<std::uint64_t>(occupied_lhs),
                            static_cast<std::uint64_t>(full_rhs)
                        );
                    }
                }
                maximum_d[root] = static_cast<std::uint8_t>(capped);
                if (root == 54 || root == 62) {
                    target_events.push_back({
                        root, n, endpoint, classified.pair_count,
                        one_hole_pairs, two_hole_pairs
                    });
                }
            }
        }

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C110-c104-tail-gate-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"arithmetic\":\"exact integers only\",\n"
            << "  \"hard_sources\":" << hard_sources << ",\n"
            << "  \"maximum_pair_count\":" << maximum_pair_count << ",\n"
            << "  \"classification_fnv1a64\":\""
            << hex_u64(classification_digest) << "\",\n"
            << "  \"first_C104_BIN_failure\":";
        c110_write_failure(out, bin_failure);
        out << ",\n  \"first_integrated_load_failure\":";
        c110_write_failure(out, integrated_failure);
        out << ",\n  \"first_occupied_bin_Carleson_failure\":";
        c110_write_failure(out, occupied_carleson_failure);
        out << ",\n  \"first_full_Carleson_failure\":";
        c110_write_failure(out, full_carleson_failure);
        out << ",\n  \"thresholds\":[\n";
        bool first_threshold = true;
        for (unsigned k = 2; k <= kC110ThresholdMaximum; ++k) {
            const auto& threshold = thresholds[k];
            if (threshold.root_count == 0) continue;
            if (!first_threshold) out << ",\n";
            first_threshold = false;
            out << "    {\"D\":" << k - 1
                << ",\"root_count\":" << threshold.root_count
                << ",\"occupied_bins\":" << threshold.occupied_bins
                << ",\"scaled_dyadic_load\":" << threshold.scaled_dyadic_load
                << ",\"scale\":" << kC110Scale << '}';
        }
        out << "\n  ],\n  \"target_root_upgrade_events\":[\n";
        for (std::size_t i = 0; i < target_events.size(); ++i) {
            const auto& event = target_events[i];
            out << "    {\"root\":" << event.root
                << ",\"source_h\":" << event.source
                << ",\"endpoint\":" << event.endpoint
                << ",\"d\":" << event.pair_count
                << ",\"one_hole_pairs\":" << event.one_hole_pairs
                << ",\"two_hole_pairs\":" << event.two_hole_pairs << '}'
                << (i + 1 == target_events.size() ? "\n" : ",\n");
        }
        out << "  ]\n}\n";
        if (!out) throw std::runtime_error("could not write output JSON");

        std::cout << "limit=" << limit
                  << " hard=" << hard_sources
                  << " max_d=" << maximum_pair_count
                  << " digest=" << hex_u64(classification_digest)
                  << " bin_failure=" << (bin_failure.set ? "yes" : "no")
                  << " carleson_failure=" << (full_carleson_failure.set ? "yes" : "no")
                  << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
