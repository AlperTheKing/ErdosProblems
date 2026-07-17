#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace {

constexpr std::uint8_t OTHER = 0;
constexpr std::uint8_t GENERATED = 1;
constexpr std::uint8_t SPLITLESS = 2;
constexpr std::uint8_t HARD = 3;

bool allowed(int n) { return n >= 2 && n % 3 != 1; }

int chain_root(int n) {
    int value = n - 1;
    while (value % 2 == 0) value /= 2;
    return value + 1;
}

std::vector<std::vector<std::pair<int, int>>> build_pairs(int limit) {
    std::vector<std::vector<std::pair<int, int>>> pairs(
        static_cast<std::size_t>(limit + 1));
    std::vector<int> values;
    for (int n = 2; n <= limit; ++n) if (allowed(n)) values.push_back(n);
    for (std::size_t i = 0; i < values.size(); ++i) {
        for (std::size_t j = i + 1; j < values.size(); ++j) {
            const std::int64_t out =
                static_cast<std::int64_t>(values[i]) * values[j] - 1;
            if (out > limit) break;
            pairs[static_cast<std::size_t>(out)].push_back({values[i], values[j]});
        }
    }
    return pairs;
}

std::uint8_t classify(
    int n,
    const std::vector<std::uint8_t>& state,
    const std::vector<std::vector<std::pair<int, int>>>& pairs) {
    const auto& row = pairs[static_cast<std::size_t>(n)];
    for (const auto& [a, b] : row) {
        if (state[static_cast<std::size_t>(a)] == GENERATED &&
            state[static_cast<std::size_t>(b)] == GENERATED) return GENERATED;
    }
    if (row.empty()) return SPLITLESS;
    if (n % 2 == 0) {
        if ((n + 1) % 3 != 0) return HARD;
        const int cofactor = (n + 1) / 3;
        if (!allowed(cofactor) || cofactor == 3) return HARD;
    }
    return OTHER;
}

struct Eval {
    std::vector<int> indices;
    int required = std::numeric_limits<int>::min();
    int required_at = 0;
    int slack = std::numeric_limits<int>::max();
};

Eval evaluate(
    const std::vector<int>& indices,
    const std::vector<int>& candidates,
    int limit,
    const std::vector<std::vector<std::pair<int, int>>>& pairs) {
    std::vector<int> seeds;
    seeds.reserve(indices.size());
    for (int index : indices) seeds.push_back(candidates[static_cast<std::size_t>(index)]);
    std::sort(seeds.begin(), seeds.end());
    std::vector<std::uint8_t> state(static_cast<std::size_t>(limit + 1), OTHER);
    std::vector<int> active_prefix(static_cast<std::size_t>(limit + 1), 0);
    int active = 0;
    int healed = 0;
    int required = std::numeric_limits<int>::min();
    int required_at = 0;
    std::size_t next_seed = 0;

    for (int n = 2; n <= limit; ++n) {
        const bool is_extra = next_seed < seeds.size() && seeds[next_seed] == n;
        if (is_extra) ++next_seed;
        std::uint8_t current = OTHER;
        if (n == 2 || n == 3 || is_extra) {
            current = GENERATED;
        } else if (allowed(n)) {
            current = classify(n, state, pairs);
        }
        state[static_cast<std::size_t>(n)] = current;
        if (current == HARD) ++active;
        if (n > 3 && n % 2 == 1 && current == GENERATED) {
            const int parent = (n + 1) / 2;
            if (allowed(parent) && state[static_cast<std::size_t>(parent)] != GENERATED) {
                const int root = chain_root(n);
                if (state[static_cast<std::size_t>(root)] == HARD) {
                    --active;
                } else if (state[static_cast<std::size_t>(root)] == SPLITLESS) {
                    ++healed;
                }
            }
        }
        active_prefix[static_cast<std::size_t>(n)] = active;
        const int need = active - healed - active_prefix[static_cast<std::size_t>(n / 4)];
        if (need > required) {
            required = need;
            required_at = n;
        }
    }
    Eval result;
    result.indices = indices;
    result.required = required;
    result.required_at = required_at;
    result.slack = static_cast<int>(indices.size()) + 1 - required;
    return result;
}

bool better(const Eval& lhs, const Eval& rhs) {
    if (lhs.slack != rhs.slack) return lhs.slack < rhs.slack;
    if (lhs.required != rhs.required) return lhs.required > rhs.required;
    if (lhs.required_at != rhs.required_at) return lhs.required_at < rhs.required_at;
    return lhs.indices < rhs.indices;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "usage: C107_combo_search LIMIT THREADS DEPTH BEAM OUTPUT\n";
        return 2;
    }
    const int limit = std::stoi(argv[1]);
    const int threads = std::stoi(argv[2]);
    const int max_depth = std::stoi(argv[3]);
    const int beam_width = std::stoi(argv[4]);
    const std::string output = argv[5];
    if (limit < 1000 || threads < 1 || threads > 64 || max_depth < 2 ||
        beam_width < 1) return 2;
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    const auto pairs = build_pairs(limit);

    // The exact one-seed sweep identified these as the complete -2 class
    // through 100000, plus 66 (the unique non-base tight chain) and the first
    // exact -1 perturbation roots.  Every entry is an even, distinct U-root.
    std::vector<int> candidates = {
        66, 668, 606, 1116, 1010, 930, 1928, 2126, 2468, 2792,
        858, 3116, 2648, 2160, 3600, 3692, 3728, 2268, 3972, 2400,
        4718, 4788, 2916, 1656, 5096, 3132, 5348, 5420, 5448, 5742,
        3468, 3480, 3570, 6312, 6348, 6608, 6788, 786, 7068, 4430,
        7472, 7806, 7868, 4818, 8030, 8088, 8156, 2474, 8246,
        18, 38, 56, 78, 90, 110, 116, 120, 126, 138, 146, 182,
        198, 200, 210, 218, 222, 228, 236, 246, 258, 290, 294, 306,
        308, 318, 326
    };
    candidates.erase(
        std::remove_if(candidates.begin(), candidates.end(),
                       [limit](int seed) { return seed > limit; }),
        candidates.end());
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(std::unique(candidates.begin(), candidates.end()), candidates.end());
    if (candidates.size() < 2) return 2;

    std::vector<std::vector<Eval>> best_by_depth;
    std::vector<Eval> beam;
    beam.reserve(candidates.size());
    for (int i = 0; i < static_cast<int>(candidates.size()); ++i) {
        beam.push_back(evaluate({i}, candidates, limit, pairs));
    }
    std::sort(beam.begin(), beam.end(), better);
    if (beam.size() > static_cast<std::size_t>(beam_width)) beam.resize(beam_width);
    best_by_depth.push_back(beam);
    bool found_failure = !beam.empty() && beam.front().slack < 0;

    for (int depth = 2; depth <= max_depth && !found_failure; ++depth) {
        std::vector<std::vector<int>> tasks;
        for (const Eval& parent : beam) {
            const int last = parent.indices.back();
            for (int next = last + 1; next < static_cast<int>(candidates.size()); ++next) {
                std::vector<int> indices = parent.indices;
                indices.push_back(next);
                tasks.push_back(std::move(indices));
            }
        }
        std::sort(tasks.begin(), tasks.end());
        tasks.erase(std::unique(tasks.begin(), tasks.end()), tasks.end());
        std::vector<Eval> evaluated(tasks.size());
#pragma omp parallel for schedule(dynamic, 1)
        for (std::int64_t i = 0; i < static_cast<std::int64_t>(tasks.size()); ++i) {
            evaluated[static_cast<std::size_t>(i)] = evaluate(
                tasks[static_cast<std::size_t>(i)], candidates, limit, pairs);
        }
        std::sort(evaluated.begin(), evaluated.end(), better);
        if (evaluated.size() > static_cast<std::size_t>(beam_width)) {
            evaluated.resize(beam_width);
        }
        beam = evaluated;
        best_by_depth.push_back(beam);
        found_failure = !beam.empty() && beam.front().slack < 0;
    }

    std::ofstream out(output, std::ios::binary);
    if (!out) return 3;
    out << "{\n  \"schema\": \"C107-combination-beam-v1\",\n";
    out << "  \"acceptance\": \"exact integer\",\n";
    out << "  \"limit\": " << limit << ",\n";
    out << "  \"threads\": " << threads << ",\n";
    out << "  \"beam_width\": " << beam_width << ",\n";
    out << "  \"candidate_seeds\": [";
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        if (i) out << ", ";
        out << candidates[i];
    }
    out << "],\n  \"failure_found\": " << (found_failure ? "true" : "false") << ",\n";
    out << "  \"best_by_depth\": [\n";
    for (std::size_t depth = 0; depth < best_by_depth.size(); ++depth) {
        if (depth) out << ",\n";
        out << "    {\"extra_seed_count\": " << depth + 1 << ", \"rows\": [";
        const auto& rows = best_by_depth[depth];
        const std::size_t keep = std::min<std::size_t>(20, rows.size());
        for (std::size_t j = 0; j < keep; ++j) {
            if (j) out << ", ";
            out << "{\"seeds\": [2, 3";
            for (int index : rows[j].indices) {
                out << ", " << candidates[static_cast<std::size_t>(index)];
            }
            out << "], \"k\": " << rows[j].indices.size() + 1
                << ", \"required\": " << rows[j].required
                << ", \"slack\": " << rows[j].slack
                << ", \"required_at\": " << rows[j].required_at << "}";
        }
        out << "]}";
    }
    out << "\n  ]\n}\n";

    const Eval& best = best_by_depth.back().front();
    std::cout << "candidate_count=" << candidates.size()
              << " depths=" << best_by_depth.size()
              << " failure=" << found_failure
              << " best_slack=" << best.slack
              << " required=" << best.required
              << " k=" << best.indices.size() + 1
              << " at=" << best.required_at << "\n";
    return found_failure ? 1 : 0;
}
