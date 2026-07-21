#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

constexpr int kMaxN = 63;
constexpr int kTargetN = 18;
constexpr int kMinOutDegree = 8;

struct State {
    int n = kTargetN;
    std::array<std::uint64_t, kMaxN> out{};
    std::array<std::uint64_t, kMaxN> in{};
};

int degree(std::uint64_t mask) {
    return static_cast<int>(std::popcount(mask));
}

int relation(const State& state, int i, int j) {
    if (i > j) {
        const int rel = relation(state, j, i);
        return -rel;
    }
    if ((state.out[i] >> j) & 1ULL) return 1;
    if ((state.out[j] >> i) & 1ULL) return -1;
    return 0;
}

void set_pair(State& state, int i, int j, int rel) {
    if (i == j) throw std::logic_error("loop in set_pair");
    if (i > j) {
        std::swap(i, j);
        rel = -rel;
    }

    state.out[i] &= ~(1ULL << j);
    state.in[j] &= ~(1ULL << i);
    state.out[j] &= ~(1ULL << i);
    state.in[i] &= ~(1ULL << j);

    if (rel == 1) {
        state.out[i] |= 1ULL << j;
        state.in[j] |= 1ULL << i;
    } else if (rel == -1) {
        state.out[j] |= 1ULL << i;
        state.in[i] |= 1ULL << j;
    } else if (rel != 0) {
        throw std::logic_error("invalid relation");
    }
}

bool is_oriented_graph(const State& state) {
    for (int v = 0; v < state.n; ++v) {
        if ((state.out[v] >> v) & 1ULL) return false;
        for (int w = v + 1; w < state.n; ++w) {
            if (((state.out[v] >> w) & 1ULL) &&
                ((state.out[w] >> v) & 1ULL)) {
                return false;
            }
        }
    }
    return true;
}

std::uint64_t new_second_mask(const State& state, int v) {
    std::uint64_t reach = 0;
    std::uint64_t first = state.out[v];
    while (first != 0) {
        const int u = static_cast<int>(std::countr_zero(first));
        first &= first - 1;
        reach |= state.out[u];
    }
    const std::uint64_t universe = (1ULL << state.n) - 1;
    return reach & universe & ~state.out[v] & ~(1ULL << v);
}

bool is_counterexample(const State& state) {
    if (!is_oriented_graph(state)) return false;
    for (int v = 0; v < state.n; ++v) {
        if (degree(new_second_mask(state, v)) >= degree(state.out[v])) {
            return false;
        }
    }
    return true;
}

// For n=18 and minimum out-degree 8, vertices of degree at least 9 satisfy
// |N2+(v)| < |N+(v)| automatically.  A degree-8 vertex has nine possible
// new second neighbors and succeeds exactly when at least two have zero
// two-step witnesses.  This energy is zero exactly at a counterexample.
int energy_18(const State& state) {
    int total = 0;
    for (int v = 0; v < state.n; ++v) {
        const int d = degree(state.out[v]);
        if (d < kMinOutDegree) return 1000000 + (kMinOutDegree - d) * 10000;
        if (d > kMinOutDegree) continue;

        int smallest = std::numeric_limits<int>::max();
        int second = std::numeric_limits<int>::max();
        for (int w = 0; w < state.n; ++w) {
            if (w == v || ((state.out[v] >> w) & 1ULL)) continue;
            const int witnesses = degree(state.out[v] & state.in[w]);
            if (witnesses < smallest) {
                second = smallest;
                smallest = witnesses;
            } else if (witnesses < second) {
                second = witnesses;
            }
        }
        if (second == std::numeric_limits<int>::max()) return 1000000;
        total += smallest + second;
    }
    return total;
}

State near_regular_tournament() {
    State state;
    for (int i = 0; i < state.n; ++i) {
        for (int j = i + 1; j < state.n; ++j) {
            const int distance = j - i;
            if (distance < state.n / 2) {
                set_pair(state, i, j, 1);
            } else if (distance > state.n / 2) {
                set_pair(state, i, j, -1);
            } else {
                set_pair(state, i, j, 1);
            }
        }
    }
    return state;
}

bool min_degree_ok(const State& state) {
    for (int v = 0; v < state.n; ++v) {
        if (degree(state.out[v]) < kMinOutDegree) return false;
    }
    return true;
}

bool mutate_pair(State& state, int i, int j, int new_rel) {
    const int old_rel = relation(state, i, j);
    if (new_rel == old_rel) return false;
    set_pair(state, i, j, new_rel);
    if (!min_degree_ok(state)) {
        set_pair(state, i, j, old_rel);
        return false;
    }
    return true;
}

template <class Rng>
void randomize_valid(State& state, Rng& rng, int moves) {
    std::uniform_int_distribution<int> vertex(0, state.n - 1);
    for (int step = 0; step < moves; ++step) {
        int i = vertex(rng);
        int j = vertex(rng);
        if (i == j) continue;
        if (i > j) std::swap(i, j);
        const int old_rel = relation(state, i, j);
        int new_rel = old_rel;
        if ((rng() & 7ULL) == 0) {
            new_rel = 0;
        } else {
            new_rel = (rng() & 1ULL) ? 1 : -1;
        }
        mutate_pair(state, i, j, new_rel);
    }
}

struct TargetMove {
    int i = -1;
    int j = -1;
    int rel = 0;
};

template <class Rng>
TargetMove targeted_move(const State& state, Rng& rng) {
    std::array<int, kMaxN> bad_vertices{};
    int bad_count = 0;
    for (int v = 0; v < state.n; ++v) {
        if (degree(state.out[v]) != kMinOutDegree) continue;
        int zero_count = 0;
        for (int w = 0; w < state.n; ++w) {
            if (w == v || ((state.out[v] >> w) & 1ULL)) continue;
            if ((state.out[v] & state.in[w]) == 0) ++zero_count;
        }
        if (zero_count < 2) bad_vertices[bad_count++] = v;
    }
    if (bad_count == 0) return {};
    const int v = bad_vertices[rng() % static_cast<std::uint64_t>(bad_count)];

    std::array<int, kMaxN> candidates{};
    std::array<int, kMaxN> counts{};
    int candidate_count = 0;
    for (int w = 0; w < state.n; ++w) {
        if (w == v || ((state.out[v] >> w) & 1ULL)) continue;
        candidates[candidate_count] = w;
        counts[candidate_count] = degree(state.out[v] & state.in[w]);
        ++candidate_count;
    }
    int best = 0;
    for (int idx = 1; idx < candidate_count; ++idx) {
        if (counts[idx] < counts[best]) best = idx;
    }
    const int w = candidates[best];
    std::uint64_t witnesses = state.out[v] & state.in[w];
    if (witnesses == 0) {
        int second_best = -1;
        for (int idx = 0; idx < candidate_count; ++idx) {
            if (idx == best) continue;
            if (second_best < 0 || counts[idx] < counts[second_best]) {
                second_best = idx;
            }
        }
        if (second_best < 0) return {};
        witnesses = state.out[v] & state.in[candidates[second_best]];
        if (witnesses == 0) return {};
        candidates[best] = candidates[second_best];
    }
    const int target = candidates[best];
    witnesses = state.out[v] & state.in[target];
    if (witnesses == 0) return {};
    const int offset = static_cast<int>(rng() % std::popcount(witnesses));
    int chosen = -1;
    for (int k = 0; k <= offset; ++k) {
        chosen = static_cast<int>(std::countr_zero(witnesses));
        witnesses &= witnesses - 1;
    }

    const int i = std::min(chosen, target);
    const int j = std::max(chosen, target);
    const int reverse_rel = (chosen == i) ? -1 : 1;
    return {i, j, (rng() & 1ULL) ? 0 : reverse_rel};
}

void write_certificate(const State& state, const std::filesystem::path& path) {
    if (!path.parent_path().empty()) {
        std::filesystem::create_directories(path.parent_path());
    }
    const std::filesystem::path temp = path.string() + ".tmp";
    std::ofstream out(temp, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("cannot open candidate output");
    out << "{\n  \"n\": " << state.n << ",\n  \"out_neighbors\": [\n";
    for (int v = 0; v < state.n; ++v) {
        out << "    [";
        bool first = true;
        for (int w = 0; w < state.n; ++w) {
            if (!((state.out[v] >> w) & 1ULL)) continue;
            if (!first) out << ", ";
            out << w;
            first = false;
        }
        out << "]" << (v + 1 == state.n ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    out.close();
    if (!out) throw std::runtime_error("failed writing candidate output");
    std::error_code error;
    std::filesystem::remove(path, error);
    std::filesystem::rename(temp, path);
}

bool self_test() {
    State base = near_regular_tournament();
    if (!is_oriented_graph(base) || !min_degree_ok(base)) return false;
    int degree8 = 0;
    int degree9 = 0;
    for (int v = 0; v < base.n; ++v) {
        degree8 += degree(base.out[v]) == 8;
        degree9 += degree(base.out[v]) == 9;
    }
    if (degree8 != 9 || degree9 != 9) return false;

    std::mt19937_64 rng(0x5E1F5E1FULL);
    State state = base;
    for (int trial = 0; trial < 20000; ++trial) {
        int i = static_cast<int>(rng() % state.n);
        int j = static_cast<int>(rng() % state.n);
        if (i == j) continue;
        if (i > j) std::swap(i, j);
        const int new_rel = static_cast<int>(rng() % 3) - 1;
        mutate_pair(state, i, j, new_rel);
        if (!is_oriented_graph(state) || !min_degree_ok(state)) return false;
        const bool zero_energy = energy_18(state) == 0;
        if (zero_energy != is_counterexample(state)) return false;
    }

    State cycle;
    cycle.n = 3;
    set_pair(cycle, 0, 1, 1);
    set_pair(cycle, 1, 2, 1);
    set_pair(cycle, 0, 2, -1);
    if (is_counterexample(cycle)) return false;
    return true;
}

struct Options {
    int threads = 1;
    double seconds = 1.0;
    std::uint64_t seed = 1;
    std::filesystem::path output = "candidate.json";
    bool run_self_test = false;
};

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&]() -> std::string {
            if (++i >= argc) throw std::runtime_error("missing value for " + arg);
            return argv[i];
        };
        if (arg == "--threads") {
            options.threads = std::stoi(value());
        } else if (arg == "--seconds") {
            options.seconds = std::stod(value());
        } else if (arg == "--seed") {
            options.seed = std::stoull(value());
        } else if (arg == "--output") {
            options.output = value();
        } else if (arg == "--self-test") {
            options.run_self_test = true;
        } else {
            throw std::runtime_error("unknown argument: " + arg);
        }
    }
    if (options.threads < 1 || options.threads > 64) {
        throw std::runtime_error("threads must be in 1..64");
    }
    if (!(options.seconds > 0.0)) throw std::runtime_error("seconds must be positive");
    return options;
}

double random_unit(std::mt19937_64& rng) {
    return static_cast<double>(rng() >> 11) * (1.0 / 9007199254740992.0);
}

std::string json_escape(const std::string& value) {
    static constexpr char hex[] = "0123456789abcdef";
    std::string escaped;
    escaped.reserve(value.size());
    for (const unsigned char ch : value) {
        switch (ch) {
            case '"': escaped += "\\\""; break;
            case '\\': escaped += "\\\\"; break;
            case '\b': escaped += "\\b"; break;
            case '\f': escaped += "\\f"; break;
            case '\n': escaped += "\\n"; break;
            case '\r': escaped += "\\r"; break;
            case '\t': escaped += "\\t"; break;
            default:
                if (ch < 0x20) {
                    escaped += "\\u00";
                    escaped += hex[ch >> 4];
                    escaped += hex[ch & 0x0f];
                } else {
                    escaped += static_cast<char>(ch);
                }
        }
    }
    return escaped;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.run_self_test) {
            const bool ok = self_test();
            std::cout << "{\"status\":\"" << (ok ? "SELF_TEST_PASS" : "SELF_TEST_FAIL")
                      << "\",\"trials\":20000}\n";
            return ok ? 0 : 2;
        }

        const auto start = std::chrono::steady_clock::now();
        const auto deadline = start + std::chrono::duration<double>(options.seconds);
        std::atomic<bool> found{false};
        std::atomic<std::uint64_t> iterations{0};
        std::atomic<int> global_best{std::numeric_limits<int>::max()};
        std::mutex result_mutex;
        State result;

        std::vector<std::thread> workers;
        workers.reserve(options.threads);
        for (int worker = 0; worker < options.threads; ++worker) {
            workers.emplace_back([&, worker]() {
                std::mt19937_64 rng(options.seed +
                                    0x9E3779B97F4A7C15ULL * (worker + 1ULL));
                State state = near_regular_tournament();
                randomize_valid(state, rng, 5000 + 37 * worker);
                int current_energy = energy_18(state);
                int local_best = current_energy;
                std::uint64_t local_iterations = 0;
                std::uint64_t since_restart = 0;

                auto record_best = [&](int value) {
                    int observed = global_best.load(std::memory_order_relaxed);
                    while (value < observed &&
                           !global_best.compare_exchange_weak(observed, value,
                                                              std::memory_order_relaxed)) {}
                };
                auto publish_if_hit = [&]() {
                    if (current_energy != 0 || !is_counterexample(state)) return false;
                    bool expected = false;
                    if (found.compare_exchange_strong(expected, true)) {
                        std::lock_guard<std::mutex> lock(result_mutex);
                        result = state;
                    }
                    return true;
                };
                record_best(current_energy);
                if (publish_if_hit()) {
                    iterations.fetch_add(local_iterations, std::memory_order_relaxed);
                    return;
                }

                while (!found.load(std::memory_order_relaxed) &&
                       std::chrono::steady_clock::now() < deadline) {
                    ++local_iterations;
                    ++since_restart;
                    const int old_energy = current_energy;
                    int i = -1;
                    int j = -1;
                    int new_rel = 0;

                    if ((rng() % 10) < 6) {
                        const TargetMove move = targeted_move(state, rng);
                        i = move.i;
                        j = move.j;
                        new_rel = move.rel;
                    }
                    if (i < 0) {
                        i = static_cast<int>(rng() % state.n);
                        j = static_cast<int>(rng() % state.n);
                        if (i == j) continue;
                        if (i > j) std::swap(i, j);
                        const int old_rel = relation(state, i, j);
                        do {
                            new_rel = static_cast<int>(rng() % 3) - 1;
                        } while (new_rel == old_rel);
                    }

                    const int old_rel = relation(state, i, j);
                    if (!mutate_pair(state, i, j, new_rel)) continue;
                    const int candidate_energy = energy_18(state);
                    const double phase = static_cast<double>(since_restart % 200000) / 200000.0;
                    const double temperature = 1.5 * std::pow(0.03 / 1.5, phase);
                    const bool accept = candidate_energy <= old_energy ||
                        random_unit(rng) < std::exp((old_energy - candidate_energy) / temperature);
                    if (accept) {
                        current_energy = candidate_energy;
                    } else {
                        set_pair(state, i, j, old_rel);
                        current_energy = old_energy;
                    }

                    if (current_energy < local_best) {
                        local_best = current_energy;
                        record_best(local_best);
                    }
                    if (publish_if_hit()) break;
                    if (since_restart >= 600000) {
                        state = near_regular_tournament();
                        randomize_valid(state, rng, 5000);
                        current_energy = energy_18(state);
                        local_best = current_energy;
                        since_restart = 0;
                        record_best(current_energy);
                        if (publish_if_hit()) break;
                    }
                }
                iterations.fetch_add(local_iterations, std::memory_order_relaxed);
            });
        }
        for (auto& worker : workers) worker.join();

        const double elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        if (found.load()) {
            if (!is_counterexample(result)) throw std::runtime_error("internal hit replay failed");
            write_certificate(result, options.output);
            std::cout << "{\"status\":\"RAW_HIT\",\"n\":18,\"threads\":"
                      << options.threads << ",\"seed\":" << options.seed
                      << ",\"iterations\":" << iterations.load()
                      << ",\"elapsed_seconds\":" << elapsed
                      << ",\"candidate\":\"" << json_escape(options.output.string()) << "\"}\n";
            return 0;
        }

        std::cout << "{\"status\":\"NO_HIT\",\"n\":18,\"threads\":"
                  << options.threads << ",\"seed\":" << options.seed
                  << ",\"iterations\":" << iterations.load()
                  << ",\"best_energy\":" << global_best.load()
                  << ",\"elapsed_seconds\":" << elapsed << "}\n";
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "{\"status\":\"ERROR\",\"message\":\""
                  << json_escape(error.what()) << "\"}\n";
        return 2;
    }
}
