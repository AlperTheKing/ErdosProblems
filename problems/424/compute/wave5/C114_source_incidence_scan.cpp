#define main C114_imported_c104_main
#include "C104_reducible_root_census.cpp"
#undef main

#include <set>

namespace {

struct C114Failure {
    bool set = false;
    std::uint32_t source = 0;
    std::uint32_t d = 0;
    std::uint32_t all_roots = 0;
    std::uint32_t reducible_roots = 0;
    std::uint64_t lhs = 0;
    std::uint64_t rhs = 0;
};

void c114_record(
    C114Failure& failure,
    std::uint32_t source,
    std::uint32_t d,
    std::uint32_t all_roots,
    std::uint32_t reducible_roots,
    std::uint64_t lhs,
    std::uint64_t rhs
) {
    if (!failure.set && lhs < rhs) {
        failure = {true, source, d, all_roots, reducible_roots, lhs, rhs};
    }
}

void c114_write_failure(
    std::ostream& out,
    const C114Failure& failure,
    const std::vector<std::uint16_t>& odd_spf,
    const std::vector<State>& state
) {
    if (!failure.set) {
        out << "null";
        return;
    }
    std::vector<std::uint32_t> divisors;
    std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
    enumerate_divisors(failure.source + 1, odd_spf, divisors);
    for (const auto left : divisors) {
        if (left < 2) continue;
        const auto right = (failure.source + 1) / left;
        if (left < right && allowed(left) && allowed(right)) {
            pairs.emplace_back(left, right);
        }
    }
    std::sort(pairs.begin(), pairs.end());
    out << "{\"source_h\":" << failure.source
        << ",\"d\":" << failure.d
        << ",\"all_root_count\":" << failure.all_roots
        << ",\"reducible_root_count\":" << failure.reducible_roots
        << ",\"lhs\":" << failure.lhs
        << ",\"rhs\":" << failure.rhs
        << ",\"pairs\":[";
    for (std::size_t i = 0; i < pairs.size(); ++i) {
        if (i) out << ',';
        const auto [left, right] = pairs[i];
        out << "{\"pair\":[" << left << ',' << right << "],\"missing\":[";
        bool first = true;
        for (const auto endpoint : {left, right}) {
            if (state[endpoint] == State::generated) continue;
            if (!first) out << ',';
            first = false;
            const auto root = seed_root_from_missing_odd(endpoint);
            out << "{\"endpoint\":" << endpoint
                << ",\"root\":" << root
                << ",\"root_state\":" << static_cast<unsigned>(state[root]) << '}';
        }
        out << "]}";
    }
    out << "]}";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C114_source_incidence_scan LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 2 || parsed_limit >= (1ULL << 32)) {
            throw std::runtime_error("LIMIT must lie in [2,2^32)");
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
        std::vector<std::uint32_t> all_roots;
        std::vector<std::uint32_t> reducible_roots;
        divisors.reserve(2048);
        pairs.reserve(1024);
        all_roots.reserve(2048);
        reducible_roots.reserve(1024);

        std::uint64_t hard_sources = 0;
        std::uint64_t upgrade_sources = 0;
        std::uint64_t root_upgrade_events = 0;
        std::uint32_t maximum_pair_count = 0;
        std::uint64_t classification_digest = kFnvOffset;
        std::int64_t minimum_a_minus_q = std::numeric_limits<std::int64_t>::max();
        std::uint32_t minimum_a_minus_q_source = 0;
        C114Failure a_ge_q_failure;
        C114Failure mixed_failure;
        C114Failure upgrade_source_a_ge_q_failure;
        C114Failure a_ge_each_increment_failure;
        C114Failure aggregate_increment_failure;

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
            const auto d = classified.pair_count;
            if (d > std::numeric_limits<std::uint8_t>::max()) {
                throw std::runtime_error("pair count exceeds byte storage");
            }
            maximum_pair_count = std::max(maximum_pair_count, d);
            all_roots.clear();
            reducible_roots.clear();
            for (const auto [left, right] : pairs) {
                bool blocked = false;
                for (const auto endpoint : {left, right}) {
                    if (state[endpoint] == State::generated) continue;
                    blocked = true;
                    const auto root = seed_root_from_missing_odd(endpoint);
                    if (state[root] == State::generated) {
                        throw std::runtime_error("missing endpoint has generated root");
                    }
                    all_roots.push_back(root);
                    if (state[root] != State::splitless) {
                        reducible_roots.push_back(root);
                    }
                }
                if (!blocked) throw std::runtime_error("hard pair has no blocker");
            }
            std::sort(all_roots.begin(), all_roots.end());
            all_roots.erase(std::unique(all_roots.begin(), all_roots.end()), all_roots.end());
            std::sort(reducible_roots.begin(), reducible_roots.end());
            reducible_roots.erase(
                std::unique(reducible_roots.begin(), reducible_roots.end()),
                reducible_roots.end()
            );
            if (reducible_roots.empty()) continue;

            const auto a = static_cast<std::uint32_t>(all_roots.size());
            const auto m = static_cast<std::uint32_t>(reducible_roots.size());
            const auto q = d - 1;
            const auto a_minus_q = static_cast<std::int64_t>(a) - q;
            if (a_minus_q < minimum_a_minus_q) {
                minimum_a_minus_q = a_minus_q;
                minimum_a_minus_q_source = n;
            }
            c114_record(a_ge_q_failure, n, d, a, m, a, q);
            c114_record(
                mixed_failure, n, d, a, m,
                static_cast<std::uint64_t>(a) * m, q
            );

            std::uint64_t total_increment = 0;
            std::uint32_t maximum_increment = 0;
            bool upgraded = false;
            for (const auto root : reducible_roots) {
                const auto old_d = static_cast<std::uint32_t>(maximum_d[root]);
                if (d <= old_d) continue;
                const auto old_q = old_d == 0 ? 0U : old_d - 1;
                const auto increment = q - old_q;
                total_increment += increment;
                maximum_increment = std::max(maximum_increment, increment);
                maximum_d[root] = static_cast<std::uint8_t>(d);
                ++root_upgrade_events;
                upgraded = true;
            }
            if (!upgraded) continue;
            ++upgrade_sources;
            c114_record(upgrade_source_a_ge_q_failure, n, d, a, m, a, q);
            c114_record(
                a_ge_each_increment_failure, n, d, a, m, a, maximum_increment
            );
            c114_record(
                aggregate_increment_failure, n, d, a, m,
                static_cast<std::uint64_t>(a) * m, total_increment
            );
        }

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n"
            << "  \"schema\":\"C114-source-incidence-scan-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"arithmetic\":\"exact integers only\",\n"
            << "  \"hard_sources\":" << hard_sources << ",\n"
            << "  \"upgrade_sources\":" << upgrade_sources << ",\n"
            << "  \"root_upgrade_events\":" << root_upgrade_events << ",\n"
            << "  \"maximum_pair_count\":" << maximum_pair_count << ",\n"
            << "  \"classification_fnv1a64\":\"" << hex_u64(classification_digest) << "\",\n"
            << "  \"minimum_A_minus_q\":" << minimum_a_minus_q << ",\n"
            << "  \"minimum_A_minus_q_source\":" << minimum_a_minus_q_source << ",\n"
            << "  \"first_A_ge_q_failure\":";
        c114_write_failure(out, a_ge_q_failure, odd_spf, state);
        out << ",\n  \"first_A_times_M_ge_q_failure\":";
        c114_write_failure(out, mixed_failure, odd_spf, state);
        out << ",\n  \"first_upgrade_source_A_ge_q_failure\":";
        c114_write_failure(out, upgrade_source_a_ge_q_failure, odd_spf, state);
        out << ",\n  \"first_A_ge_each_increment_failure\":";
        c114_write_failure(out, a_ge_each_increment_failure, odd_spf, state);
        out << ",\n  \"first_A_times_M_ge_total_increment_failure\":";
        c114_write_failure(out, aggregate_increment_failure, odd_spf, state);
        out << "\n}\n";
        std::cerr << "limit=" << limit
                  << " hard=" << hard_sources
                  << " max_d=" << maximum_pair_count
                  << " min_A-q=" << minimum_a_minus_q << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
