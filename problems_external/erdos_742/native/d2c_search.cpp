#include <algorithm>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <queue>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace {

struct Graph {
    int n = 0;
    std::vector<std::uint32_t> adj;

    explicit Graph(int order = 0) : n(order), adj(order, 0) {}

    bool edge(int u, int v) const {
        return ((adj[u] >> v) & 1U) != 0;
    }

    void set_edge(int u, int v, bool value) {
        if (u == v) std::abort();
        const std::uint32_t bu = 1U << u;
        const std::uint32_t bv = 1U << v;
        if (value) {
            adj[u] |= bv;
            adj[v] |= bu;
        } else {
            adj[u] &= ~bv;
            adj[v] &= ~bu;
        }
    }

    void flip(int u, int v) {
        set_edge(u, v, !edge(u, v));
    }
};

struct Metrics {
    int edges = 0;
    int uncovered_nonedges = 0;
    int noncritical_edges = 0;
    bool diameter_exactly_two = false;
    bool d2c = false;
    std::vector<std::pair<int, int>> witness;
};

std::uint32_t order_mask(int n) {
    return n == 32 ? 0xffffffffU : ((1U << n) - 1U);
}

int take_low_bit(std::uint32_t& bits) {
    const int v = std::countr_zero(bits);
    bits &= bits - 1U;
    return v;
}

// Exact local semantics.  If deleting uv can make a distance exceed two, a
// shortest path destroyed by the deletion has length one or two.  Therefore
// one endpoint of the affected pair is u or v.  This gives the three cases
// tested below: uv has no common neighbor, or uv is part of the unique
// two-path from u (respectively v) to another vertex.
Metrics analyze_fast(const Graph& g, bool keep_witnesses) {
    Metrics out;
    const int total_pairs = g.n * (g.n - 1) / 2;
    const std::uint32_t mask = order_mask(g.n);
    if (keep_witnesses) out.witness.assign(total_pairs, {-1, -1});
    int edge_index = 0;

    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            const std::uint32_t common = g.adj[u] & g.adj[v];
            if (!g.edge(u, v)) {
                if (common == 0) ++out.uncovered_nonedges;
                continue;
            }

            ++out.edges;
            std::pair<int, int> witness{-1, -1};
            if (common == 0) {
                witness = {u, v};
            } else {
                std::uint32_t candidates =
                    g.adj[v] & ~g.adj[u] & mask & ~(1U << u);
                while (candidates != 0 && witness.first < 0) {
                    const int w = take_low_bit(candidates);
                    if ((g.adj[u] & g.adj[w]) == (1U << v)) {
                        witness = {u, w};
                    }
                }

                candidates = g.adj[u] & ~g.adj[v] & mask & ~(1U << v);
                while (candidates != 0 && witness.first < 0) {
                    const int w = take_low_bit(candidates);
                    if ((g.adj[v] & g.adj[w]) == (1U << u)) {
                        witness = {v, w};
                    }
                }
            }

            if (witness.first < 0) ++out.noncritical_edges;
            if (keep_witnesses) out.witness[edge_index] = witness;
            ++edge_index;
        }
    }

    out.diameter_exactly_two =
        out.uncovered_nonedges == 0 && out.edges < total_pairs;
    out.d2c = out.diameter_exactly_two && out.noncritical_edges == 0;
    return out;
}

int distance_ignoring_edge(const Graph& g, int source, int target,
                           int skip_u, int skip_v) {
    std::vector<int> dist(g.n, -1);
    std::queue<int> q;
    dist[source] = 0;
    q.push(source);
    while (!q.empty()) {
        const int u = q.front();
        q.pop();
        std::uint32_t next = g.adj[u];
        while (next != 0) {
            const int v = take_low_bit(next);
            if ((u == skip_u && v == skip_v) ||
                (u == skip_v && v == skip_u)) {
                continue;
            }
            if (dist[v] >= 0) continue;
            dist[v] = dist[u] + 1;
            if (v == target) return dist[v];
            q.push(v);
        }
    }
    return -1;
}

// Deliberately independent exhaustive definition-level implementation.
Metrics analyze_slow(const Graph& g, bool keep_witnesses) {
    Metrics out;
    const int total_pairs = g.n * (g.n - 1) / 2;
    if (keep_witnesses) out.witness.assign(total_pairs, {-1, -1});
    int edge_index = 0;
    std::vector<std::vector<int>> base_distance(
        g.n, std::vector<int>(g.n, -1));

    int diameter = 0;
    bool connected = true;
    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            const int d = distance_ignoring_edge(g, u, v, -1, -1);
            base_distance[u][v] = base_distance[v][u] = d;
            if (d < 0) {
                connected = false;
            } else {
                diameter = std::max(diameter, d);
            }
            if (!g.edge(u, v) && (d < 0 || d > 2)) {
                ++out.uncovered_nonedges;
            }
        }
    }

    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            if (!g.edge(u, v)) continue;
            ++out.edges;
            std::pair<int, int> witness{-1, -1};
            for (int a = 0; a < g.n && witness.first < 0; ++a) {
                for (int b = a + 1; b < g.n; ++b) {
                    if (base_distance[a][b] < 0 ||
                        base_distance[a][b] > 2) {
                        continue;
                    }
                    const int d =
                        distance_ignoring_edge(g, a, b, u, v);
                    if (d < 0 || d > 2) {
                        witness = {a, b};
                        break;
                    }
                }
            }
            if (witness.first < 0) ++out.noncritical_edges;
            if (keep_witnesses) out.witness[edge_index] = witness;
            ++edge_index;
        }
    }

    out.diameter_exactly_two =
        connected && diameter == 2 && out.edges < total_pairs;
    out.d2c = out.diameter_exactly_two && out.noncritical_edges == 0;
    return out;
}

bool same_semantics(const Metrics& a, const Metrics& b) {
    return a.edges == b.edges &&
           a.uncovered_nonedges == b.uncovered_nonedges &&
           a.noncritical_edges == b.noncritical_edges &&
           a.diameter_exactly_two == b.diameter_exactly_two &&
           a.d2c == b.d2c;
}

Graph complete_bipartite(int a, int b) {
    Graph g(a + b);
    for (int u = 0; u < a; ++u) {
        for (int v = a; v < a + b; ++v) g.set_edge(u, v, true);
    }
    return g;
}

Graph cycle_graph(int n) {
    Graph g(n);
    for (int u = 0; u < n; ++u) g.set_edge(u, (u + 1) % n, true);
    return g;
}

Graph star_graph(int n) {
    Graph g(n);
    for (int v = 1; v < n; ++v) g.set_edge(0, v, true);
    return g;
}

bool check_named(const std::string& name, const Graph& g,
                 bool expected_d2c, int expected_edges) {
    const Metrics fast = analyze_fast(g, true);
    const Metrics slow = analyze_slow(g, true);
    const bool ok = same_semantics(fast, slow) &&
                    fast.d2c == expected_d2c &&
                    fast.edges == expected_edges;
    std::cout << "{\"calibration\":\"" << name << "\",\"ok\":"
              << (ok ? "true" : "false") << ",\"edges\":" << fast.edges
              << ",\"uncovered\":" << fast.uncovered_nonedges
              << ",\"noncritical\":" << fast.noncritical_edges
              << ",\"d2c\":" << (fast.d2c ? "true" : "false") << "}\n";
    return ok;
}

bool exhaustive_semantics_audit(int n) {
    const int pairs = n * (n - 1) / 2;
    const std::uint64_t graph_count = 1ULL << pairs;
    std::vector<std::pair<int, int>> pair;
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) pair.push_back({u, v});
    }
    for (std::uint64_t code = 0; code < graph_count; ++code) {
        Graph g(n);
        for (int i = 0; i < pairs; ++i) {
            if ((code >> i) & 1ULL) {
                g.set_edge(pair[i].first, pair[i].second, true);
            }
        }
        const Metrics fast = analyze_fast(g, false);
        const Metrics slow = analyze_slow(g, false);
        if (!same_semantics(fast, slow)) {
            std::cerr << "semantic mismatch n=" << n << " code=" << code
                      << "\n";
            return false;
        }
    }
    std::cout << "{\"exhaustive_audit\":true,\"n\":" << n
              << ",\"graphs\":" << graph_count << "}\n";
    return true;
}

bool random_flip_audit(std::uint64_t seed, int flips) {
    std::mt19937_64 rng(seed);
    Graph g(25);
    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            if ((rng() % 1000) < 520) g.set_edge(u, v, true);
        }
    }
    for (int step = 0; step < flips; ++step) {
        int u = static_cast<int>(rng() % g.n);
        int v = static_cast<int>(rng() % (g.n - 1));
        if (v >= u) ++v;
        if (u > v) std::swap(u, v);
        const Metrics before = analyze_fast(g, false);
        g.flip(u, v);
        const Metrics after = analyze_fast(g, false);
        const Metrics slow = analyze_slow(g, false);
        if (!same_semantics(after, slow)) {
            std::cerr << "flip audit mismatch step=" << step << " edge=" << u
                      << "," << v << "\n";
            return false;
        }
        g.flip(u, v);
        const Metrics restored = analyze_fast(g, false);
        if (!same_semantics(before, restored)) {
            std::cerr << "flip rollback mismatch step=" << step << "\n";
            return false;
        }
        g.flip(u, v);
    }
    std::cout << "{\"flip_audit\":true,\"seed\":" << seed
              << ",\"flips\":" << flips << "}\n";
    return true;
}

int run_calibration() {
    bool ok = true;
    ok &= check_named("K12,13", complete_bipartite(12, 13), true, 156);
    ok &= check_named("C5", cycle_graph(5), true, 5);
    ok &= check_named("star25", star_graph(25), true, 24);

    Graph added = complete_bipartite(12, 13);
    added.set_edge(0, 1, true);
    ok &= check_named("K12,13_plus_internal", added, false, 157);

    Graph removed = complete_bipartite(12, 13);
    removed.set_edge(0, 12, false);
    ok &= check_named("K12,13_minus_cross", removed, false, 155);

    Graph complete(25);
    for (int u = 0; u < 25; ++u) {
        for (int v = u + 1; v < 25; ++v) complete.set_edge(u, v, true);
    }
    ok &= check_named("K25", complete, false, 300);
    ok &= exhaustive_semantics_audit(6);
    ok &= random_flip_audit(74220260723ULL, 200);
    std::cout << "{\"calibration_complete\":" << (ok ? "true" : "false")
              << "}\n";
    return ok ? 0 : 2;
}

long long objective(const Metrics& m, int target_edges) {
    const long long edge_distance = std::llabs(m.edges - target_edges);
    return 100000LL * m.uncovered_nonedges +
           1000LL * m.noncritical_edges + edge_distance;
}

std::string edge_list_json(const Graph& g) {
    std::ostringstream out;
    out << "[";
    bool first = true;
    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            if (!g.edge(u, v)) continue;
            if (!first) out << ",";
            first = false;
            out << "[" << u << "," << v << "]";
        }
    }
    out << "]";
    return out.str();
}

struct SharedBest {
    std::mutex mutex;
    long long value = std::numeric_limits<long long>::max();
    Graph graph;
    Metrics metrics;
    std::atomic<bool> hit{false};
};

Graph initial_target_graph(std::mt19937_64& rng, int target_edges) {
    Graph g = complete_bipartite(12, 13);
    std::vector<std::pair<int, int>> absent;
    std::vector<std::pair<int, int>> present;
    for (int u = 0; u < 25; ++u) {
        for (int v = u + 1; v < 25; ++v) {
            (g.edge(u, v) ? present : absent).push_back({u, v});
        }
    }
    std::shuffle(absent.begin(), absent.end(), rng);
    std::shuffle(present.begin(), present.end(), rng);
    int edges = 156;
    int ai = 0;
    int pi = 0;
    while (edges < target_edges) {
        const auto [u, v] = absent[ai++];
        g.set_edge(u, v, true);
        ++edges;
    }
    while (edges > target_edges) {
        const auto [u, v] = present[pi++];
        g.set_edge(u, v, false);
        --edges;
    }
    return g;
}

void report_best(int lane, std::uint64_t moves, long long value,
                 const Graph& g, const Metrics& m) {
    std::cout << "{\"lane\":" << lane << ",\"moves\":" << moves
              << ",\"objective\":" << value << ",\"edges\":" << m.edges
              << ",\"uncovered\":" << m.uncovered_nonedges
              << ",\"noncritical\":" << m.noncritical_edges
              << ",\"d2c\":" << (m.d2c ? "true" : "false");
    if (m.d2c) std::cout << ",\"adjacency\":" << edge_list_json(g);
    std::cout << "}\n";
}

void search_lane(int lane, int seconds, int target_edges, std::uint64_t seed,
                 SharedBest& shared) {
    std::mt19937_64 rng(seed + 0x9e3779b97f4a7c15ULL * (lane + 1));
    Graph current = initial_target_graph(rng, target_edges);
    Metrics current_m = analyze_fast(current, false);
    long long current_value = objective(current_m, target_edges);
    Graph lane_best = current;
    Metrics lane_best_m = current_m;
    long long lane_best_value = current_value;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(seconds);
    std::uint64_t moves = 0;

    while (std::chrono::steady_clock::now() < deadline &&
           !shared.hit.load(std::memory_order_relaxed)) {
        std::vector<std::pair<int, int>> present;
        std::vector<std::pair<int, int>> absent;
        present.reserve(target_edges);
        absent.reserve(300 - target_edges);
        for (int u = 0; u < 25; ++u) {
            for (int v = u + 1; v < 25; ++v) {
                (current.edge(u, v) ? present : absent).push_back({u, v});
            }
        }

        Graph proposal = current;
        const auto remove = present[rng() % present.size()];
        const auto add = absent[rng() % absent.size()];
        proposal.set_edge(remove.first, remove.second, false);
        proposal.set_edge(add.first, add.second, true);
        Metrics proposal_m = analyze_fast(proposal, false);
        const long long proposal_value = objective(proposal_m, target_edges);

        const double phase = static_cast<double>(moves % 20000) / 20000.0;
        const double temperature = 5000.0 * std::pow(0.002, phase);
        const long long delta = proposal_value - current_value;
        const double draw =
            std::generate_canonical<double, 53>(rng);
        if (delta <= 0 ||
            draw < std::exp(-static_cast<double>(delta) / temperature)) {
            current = std::move(proposal);
            current_m = proposal_m;
            current_value = proposal_value;
        }
        ++moves;

        if (current_value < lane_best_value) {
            lane_best = current;
            lane_best_m = current_m;
            lane_best_value = current_value;
        }
        if ((moves % 10000) == 0) {
            const Metrics audit = analyze_slow(current, false);
            if (!same_semantics(current_m, audit)) {
                std::cerr << "runtime audit mismatch lane=" << lane
                          << " moves=" << moves << "\n";
                shared.hit.store(true);
                return;
            }
        }

        if (current_m.d2c && current_m.edges >= 157) {
            const Metrics audit = analyze_slow(current, true);
            if (!same_semantics(current_m, audit) || !audit.d2c) {
                std::cerr << "candidate verifier disagreement lane=" << lane
                          << " moves=" << moves << "\n";
                shared.hit.store(true);
                return;
            }
            {
                std::lock_guard<std::mutex> lock(shared.mutex);
                shared.graph = current;
                shared.metrics = audit;
                shared.value = current_value;
                report_best(lane, moves, current_value, current, audit);
            }
            shared.hit.store(true);
            return;
        }
    }

    {
        std::lock_guard<std::mutex> lock(shared.mutex);
        if (lane_best_value < shared.value) {
            shared.value = lane_best_value;
            shared.graph = lane_best;
            shared.metrics = lane_best_m;
            report_best(lane, moves, lane_best_value, lane_best, lane_best_m);
        }
    }
}

int run_search(int threads, int seconds, int target_edges,
               std::uint64_t seed) {
    if (threads < 1 || threads > 64 || seconds < 1 ||
        target_edges < 157 || target_edges > 300) {
        std::cerr << "invalid search parameters\n";
        return 2;
    }
    SharedBest shared;
    std::vector<std::thread> pool;
    for (int lane = 0; lane < threads; ++lane) {
        pool.emplace_back(search_lane, lane, seconds, target_edges, seed,
                          std::ref(shared));
    }
    for (auto& thread : pool) thread.join();
    std::cout << "{\"search_complete\":true,\"threads\":" << threads
              << ",\"seconds\":" << seconds << ",\"target_edges\":"
              << target_edges << ",\"seed\":" << seed << ",\"hit\":"
              << (shared.hit.load() ? "true" : "false")
              << ",\"best_objective\":" << shared.value << "}\n";
    return shared.hit.load() ? 0 : 1;
}

int parse_int(const char* text) {
    return static_cast<int>(std::strtol(text, nullptr, 10));
}

std::uint64_t parse_u64(const char* text) {
    return static_cast<std::uint64_t>(std::strtoull(text, nullptr, 10));
}

}  // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--calibrate") {
        return run_calibration();
    }
    if (argc == 10 && std::string(argv[1]) == "--search" &&
        std::string(argv[2]) == "--threads" &&
        std::string(argv[4]) == "--seconds" &&
        std::string(argv[6]) == "--target-edges" &&
        std::string(argv[8]) == "--seed") {
        return run_search(parse_int(argv[3]), parse_int(argv[5]),
                          parse_int(argv[7]), parse_u64(argv[9]));
    }
    std::cerr
        << "usage:\n"
        << "  d2c_search --calibrate\n"
        << "  d2c_search --search --threads N --seconds S "
           "--target-edges M --seed X\n";
    return 2;
}
