#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
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

struct Result {
    int seed = 0;
    int k = 0;
    int required = std::numeric_limits<int>::min();
    int required_at = 0;
    int first_failure = 0;
    int first_failure_margin = 0;
    int endpoint_ah = 0;
    int endpoint_d = 0;
    int minimum_margin_delta = std::numeric_limits<int>::max();
    int minimum_margin_delta_at = 0;
};

std::vector<std::vector<std::pair<int, int>>> build_pairs(int limit) {
    std::vector<std::vector<std::pair<int, int>>> pairs(
        static_cast<std::size_t>(limit + 1));
    std::vector<int> values;
    for (int n = 2; n <= limit; ++n) {
        if (allowed(n)) values.push_back(n);
    }
    for (std::size_t i = 0; i < values.size(); ++i) {
        const int a = values[i];
        for (std::size_t j = i + 1; j < values.size(); ++j) {
            const std::int64_t out = static_cast<std::int64_t>(a) * values[j] - 1;
            if (out > limit) break;
            pairs[static_cast<std::size_t>(out)].push_back({a, values[j]});
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
            state[static_cast<std::size_t>(b)] == GENERATED) {
            return GENERATED;
        }
    }
    if (row.empty()) return SPLITLESS;
    if (n % 2 == 0) {
        const int product = n + 1;
        if (product % 3 != 0) return HARD;
        const int parent = product / 3;
        if (!allowed(parent) || parent == 3) return HARD;
    }
    return OTHER;
}

Result scan_one(
    int seed,
    int limit,
    const std::vector<std::vector<std::pair<int, int>>>& pairs,
    const std::vector<int>* base_margin,
    std::vector<int>* margin_output) {
    std::vector<std::uint8_t> state(static_cast<std::size_t>(limit + 1), OTHER);
    std::vector<int> active_prefix(static_cast<std::size_t>(limit + 1), 0);
    int active_hard = 0;
    int healed_splitless = 0;
    Result result;
    result.seed = seed;
    result.k = (chain_root(seed) == 2 ? 1 : 2);

    for (int n = 2; n <= limit; ++n) {
        std::uint8_t current = OTHER;
        if (n == 2 || n == 3 || n == seed) {
            current = GENERATED;
        } else if (allowed(n)) {
            current = classify(n, state, pairs);
        }
        state[static_cast<std::size_t>(n)] = current;
        if (current == HARD) ++active_hard;

        if (n > 3 && n % 2 == 1 && current == GENERATED) {
            const int parent = (n + 1) / 2;
            if (allowed(parent) &&
                state[static_cast<std::size_t>(parent)] != GENERATED) {
                const int root = chain_root(n);
                if (state[static_cast<std::size_t>(root)] == HARD) {
                    --active_hard;
                } else if (state[static_cast<std::size_t>(root)] == SPLITLESS) {
                    ++healed_splitless;
                }
            }
        }

        active_prefix[static_cast<std::size_t>(n)] = active_hard;
        const int quarter = active_prefix[static_cast<std::size_t>(n / 4)];
        const int required = active_hard - healed_splitless - quarter;
        const int quarter_margin = -required;
        if (margin_output != nullptr) {
            (*margin_output)[static_cast<std::size_t>(n)] = quarter_margin;
        }
        if (base_margin != nullptr) {
            const int delta = quarter_margin - (*base_margin)[static_cast<std::size_t>(n)];
            if (delta < result.minimum_margin_delta) {
                result.minimum_margin_delta = delta;
                result.minimum_margin_delta_at = n;
            }
        }
        if (required > result.required) {
            result.required = required;
            result.required_at = n;
        }
        const int margin = result.k - required;
        if (margin < 0 && result.first_failure == 0) {
            result.first_failure = n;
            result.first_failure_margin = margin;
        }
    }
    result.endpoint_ah = active_hard;
    result.endpoint_d = healed_splitless;
    return result;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: C107_single_seed_sweep LIMIT THREADS OUTPUT\n";
        return 2;
    }
    const int limit = std::stoi(argv[1]);
    const int threads = std::stoi(argv[2]);
    const std::string output = argv[3];
    if (limit < 186 || threads < 1 || threads > 64) return 2;
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif

    const auto pairs = build_pairs(limit);
    std::vector<int> seeds;
    seeds.push_back(3);  // This duplicates the base system without a new chain.
    for (int seed = 5; seed <= limit; ++seed) {
        if (allowed(seed)) seeds.push_back(seed);
    }
    std::vector<Result> results(seeds.size());
    std::vector<int> base_margin(static_cast<std::size_t>(limit + 1), 0);
    results[0] = scan_one(seeds[0], limit, pairs, nullptr, &base_margin);

#pragma omp parallel for schedule(dynamic, 1)
    for (std::int64_t i = 1; i < static_cast<std::int64_t>(seeds.size()); ++i) {
        results[static_cast<std::size_t>(i)] = scan_one(
            seeds[static_cast<std::size_t>(i)], limit, pairs, &base_margin, nullptr);
    }

    int failures = 0;
    int tight = 0;
    int minimum_slack = std::numeric_limits<int>::max();
    Result worst;
    bool have_worst = false;
    int minimum_perturbation = 0;
    Result worst_perturbation;
    bool have_perturbation = false;
    for (const Result& result : results) {
        failures += (result.first_failure != 0);
        tight += (result.k == result.required);
        const int slack = result.k - result.required;
        if (!have_worst || slack < minimum_slack ||
            (slack == minimum_slack && result.seed < worst.seed)) {
            have_worst = true;
            minimum_slack = slack;
            worst = result;
        }
        if (result.seed != 3 &&
            (!have_perturbation || result.minimum_margin_delta < minimum_perturbation)) {
            have_perturbation = true;
            minimum_perturbation = result.minimum_margin_delta;
            worst_perturbation = result;
        }
    }

    std::ofstream out(output, std::ios::binary);
    if (!out) return 3;
    out << "{\n";
    out << "  \"schema\": \"C107-single-seed-sweep-v1\",\n";
    out << "  \"acceptance\": \"exact integer\",\n";
    out << "  \"limit\": " << limit << ",\n";
    out << "  \"threads\": " << threads << ",\n";
    out << "  \"seed_systems\": " << results.size() << ",\n";
    out << "  \"failures\": " << failures << ",\n";
    out << "  \"tight_systems\": " << tight << ",\n";
    out << "  \"minimum_slack\": " << minimum_slack << ",\n";
    out << "  \"minimum_one_chain_margin_delta\": " << minimum_perturbation << ",\n";
    out << "  \"worst_perturbation\": {\"seed\": " << worst_perturbation.seed
        << ", \"root\": " << chain_root(worst_perturbation.seed)
        << ", \"delta\": " << worst_perturbation.minimum_margin_delta
        << ", \"at\": " << worst_perturbation.minimum_margin_delta_at << "},\n";
    out << "  \"worst\": {\"seed\": " << worst.seed
        << ", \"root\": " << chain_root(worst.seed)
        << ", \"k\": " << worst.k
        << ", \"required\": " << worst.required
        << ", \"required_at\": " << worst.required_at << "},\n";
    bool first = true;
    std::vector<Result> perturbation_rows;
    for (const Result& result : results) {
        if (result.seed != 3 && result.minimum_margin_delta < 0) {
            perturbation_rows.push_back(result);
        }
    }
    std::sort(perturbation_rows.begin(), perturbation_rows.end(),
              [](const Result& lhs, const Result& rhs) {
                  if (lhs.minimum_margin_delta != rhs.minimum_margin_delta) {
                      return lhs.minimum_margin_delta < rhs.minimum_margin_delta;
                  }
                  if (lhs.minimum_margin_delta_at != rhs.minimum_margin_delta_at) {
                      return lhs.minimum_margin_delta_at < rhs.minimum_margin_delta_at;
                  }
                  return lhs.seed < rhs.seed;
              });
    out << "  \"negative_perturbation_count\": " << perturbation_rows.size() << ",\n";
    out << "  \"negative_perturbations\": [\n";
    first = true;
    for (std::size_t i = 0; i < std::min<std::size_t>(200, perturbation_rows.size()); ++i) {
        const Result& result = perturbation_rows[i];
        if (!first) out << ",\n";
        first = false;
        out << "    {\"seed\": " << result.seed
            << ", \"root\": " << chain_root(result.seed)
            << ", \"delta\": " << result.minimum_margin_delta
            << ", \"at\": " << result.minimum_margin_delta_at << "}";
    }
    out << "\n  ],\n";
    std::vector<Result> candidate_rows;
    for (const Result& result : results) {
        if (result.seed != 3 && chain_root(result.seed) != 2) {
            candidate_rows.push_back(result);
        }
    }
    std::sort(candidate_rows.begin(), candidate_rows.end(),
              [](const Result& lhs, const Result& rhs) {
                  const int lhs_slack = lhs.k - lhs.required;
                  const int rhs_slack = rhs.k - rhs.required;
                  if (lhs_slack != rhs_slack) return lhs_slack < rhs_slack;
                  if (lhs.minimum_margin_delta != rhs.minimum_margin_delta) {
                      return lhs.minimum_margin_delta < rhs.minimum_margin_delta;
                  }
                  return lhs.seed < rhs.seed;
              });
    out << "  \"combination_candidates\": [\n";
    first = true;
    for (std::size_t i = 0; i < std::min<std::size_t>(200, candidate_rows.size()); ++i) {
        const Result& result = candidate_rows[i];
        if (!first) out << ",\n";
        first = false;
        out << "    {\"seed\": " << result.seed
            << ", \"root\": " << chain_root(result.seed)
            << ", \"slack\": " << result.k - result.required
            << ", \"required\": " << result.required
            << ", \"required_at\": " << result.required_at
            << ", \"min_delta\": " << result.minimum_margin_delta
            << ", \"min_delta_at\": " << result.minimum_margin_delta_at << "}";
    }
    out << "\n  ],\n";
    out << "  \"tight\": [\n";
    first = true;
    for (const Result& result : results) {
        if (result.k != result.required) continue;
        if (!first) out << ",\n";
        first = false;
        out << "    {\"seed\": " << result.seed
            << ", \"root\": " << chain_root(result.seed)
            << ", \"k\": " << result.k
            << ", \"required\": " << result.required
            << ", \"required_at\": " << result.required_at << "}";
    }
    out << "\n  ],\n";
    out << "  \"failure_rows\": [\n";
    first = true;
    for (const Result& result : results) {
        if (result.first_failure == 0) continue;
        if (!first) out << ",\n";
        first = false;
        out << "    {\"seed\": " << result.seed
            << ", \"root\": " << chain_root(result.seed)
            << ", \"k\": " << result.k
            << ", \"first_failure\": " << result.first_failure
            << ", \"margin\": " << result.first_failure_margin << "}";
    }
    out << "\n  ]\n}\n";

    std::cout << "seed_systems=" << results.size()
              << " failures=" << failures
              << " tight=" << tight
              << " minimum_slack=" << minimum_slack
              << " worst_seed=" << worst.seed
              << " required=" << worst.required
              << " k=" << worst.k
              << " min_perturbation=" << minimum_perturbation
              << " perturbation_seed=" << worst_perturbation.seed << "\n";
    return failures == 0 ? 0 : 1;
}
