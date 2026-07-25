#define main d2c_fixed_swap_entry
#include "d2c_search.cpp"
#undef main

namespace {

std::vector<std::pair<int, int>> noncritical_edge_list(const Graph& g) {
    const Metrics metrics = analyze_fast(g, true);
    std::vector<std::pair<int, int>> result;
    int edge_index = 0;
    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            if (!g.edge(u, v)) continue;
            if (metrics.witness[edge_index].first < 0) {
                result.push_back({u, v});
            }
            ++edge_index;
        }
    }
    return result;
}

Graph perturbed_bipartite(std::mt19937_64& rng) {
    Graph g = complete_bipartite(12, 13);
    std::vector<std::pair<int, int>> internal;
    for (int u = 0; u < 12; ++u) {
        for (int v = u + 1; v < 12; ++v) internal.push_back({u, v});
    }
    for (int u = 12; u < 25; ++u) {
        for (int v = u + 1; v < 25; ++v) internal.push_back({u, v});
    }
    std::shuffle(internal.begin(), internal.end(), rng);
    const int additions = 1 + static_cast<int>(rng() % 36);
    for (int i = 0; i < additions; ++i) {
        g.set_edge(internal[i].first, internal[i].second, true);
    }

    // A minority of restarts also exchange cross and internal edges.  Reject
    // later if this destroys diameter two.
    const int swaps = static_cast<int>(rng() % 9);
    for (int i = 0; i < swaps; ++i) {
        int a = static_cast<int>(rng() % 12);
        int b = 12 + static_cast<int>(rng() % 13);
        g.set_edge(a, b, false);
        for (int attempts = 0; attempts < 50; ++attempts) {
            const auto [u, v] = internal[rng() % internal.size()];
            if (!g.edge(u, v)) {
                g.set_edge(u, v, true);
                break;
            }
        }
    }
    return g;
}

Graph dense_random_graph(std::mt19937_64& rng) {
    Graph g(25);
    const int threshold = 430 + static_cast<int>(rng() % 371);
    for (int u = 0; u < 25; ++u) {
        for (int v = u + 1; v < 25; ++v) {
            if (static_cast<int>(rng() % 1000) < threshold) {
                g.set_edge(u, v, true);
            }
        }
    }
    return g;
}

Graph complete_minus_edge(std::mt19937_64& rng) {
    Graph g(25);
    for (int u = 0; u < 25; ++u) {
        for (int v = u + 1; v < 25; ++v) g.set_edge(u, v, true);
    }
    int u = static_cast<int>(rng() % 25);
    int v = static_cast<int>(rng() % 24);
    if (v >= u) ++v;
    g.set_edge(u, v, false);
    return g;
}

Graph make_restart(std::mt19937_64& rng, std::uint64_t restart) {
    if (restart % 10 < 7) return perturbed_bipartite(rng);
    if (restart % 10 < 9) return dense_random_graph(rng);
    return complete_minus_edge(rng);
}

struct PruneShared {
    std::mutex mutex;
    int best_edges = -1;
    Graph best_graph;
    Metrics best_metrics;
    std::atomic<bool> hit{false};
    std::atomic<std::uint64_t> restarts{0};
};

bool is_complete_bipartite_12_13(const Graph& g) {
    if (g.n != 25) return false;
    std::vector<int> color(g.n, -1);
    std::queue<int> pending;
    color[0] = 0;
    pending.push(0);
    while (!pending.empty()) {
        const int u = pending.front();
        pending.pop();
        for (int v = 0; v < g.n; ++v) {
            if (!g.edge(u, v)) continue;
            if (color[v] < 0) {
                color[v] = 1 - color[u];
                pending.push(v);
            } else if (color[v] == color[u]) {
                return false;
            }
        }
    }
    if (std::find(color.begin(), color.end(), -1) != color.end()) {
        return false;
    }
    const int part0 = std::count(color.begin(), color.end(), 0);
    if (part0 != 12 && part0 != 13) return false;
    for (int u = 0; u < g.n; ++u) {
        for (int v = u + 1; v < g.n; ++v) {
            if (g.edge(u, v) != (color[u] != color[v])) return false;
        }
    }
    return true;
}

void emit_prune_best(int lane, std::uint64_t restart, const Graph& g,
                     const Metrics& m) {
    std::cout << "{\"strategy\":\"minimalize\",\"lane\":" << lane
              << ",\"restart\":" << restart << ",\"edges\":" << m.edges
              << ",\"uncovered\":" << m.uncovered_nonedges
              << ",\"noncritical\":" << m.noncritical_edges
              << ",\"d2c\":" << (m.d2c ? "true" : "false")
              << ",\"is_K12_13\":"
              << (is_complete_bipartite_12_13(g) ? "true" : "false");
    if (m.edges >= 157 && m.d2c) {
        std::cout << ",\"adjacency\":" << edge_list_json(g);
    }
    std::cout << "}\n";
}

void prune_lane(int lane, int seconds, std::uint64_t seed,
                PruneShared& shared) {
    std::mt19937_64 rng(seed + 0xd1b54a32d192ed03ULL * (lane + 1));
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(seconds);
    std::uint64_t local_restarts = 0;

    while (std::chrono::steady_clock::now() < deadline &&
           !shared.hit.load(std::memory_order_relaxed)) {
        Graph g = make_restart(rng, local_restarts);
        Metrics metrics = analyze_fast(g, false);
        ++local_restarts;
        shared.restarts.fetch_add(1, std::memory_order_relaxed);
        if (!metrics.diameter_exactly_two) continue;

        while (!metrics.d2c) {
            std::vector<std::pair<int, int>> removable =
                noncritical_edge_list(g);
            if (removable.empty()) break;
            std::shuffle(removable.begin(), removable.end(), rng);

            struct Choice {
                int noncritical;
                int uncovered;
                std::uint64_t tie;
                std::pair<int, int> edge;
                Metrics metrics;
            };
            std::vector<Choice> choices;
            const int sample =
                std::min<int>(static_cast<int>(removable.size()), 72);
            choices.reserve(sample);
            for (int i = 0; i < sample; ++i) {
                const auto [u, v] = removable[i];
                g.set_edge(u, v, false);
                Metrics after = analyze_fast(g, false);
                g.set_edge(u, v, true);
                if (!after.diameter_exactly_two) continue;
                choices.push_back(
                    {after.noncritical_edges, after.uncovered_nonedges,
                     rng(), {u, v}, after});
            }
            if (choices.empty()) break;
            std::sort(choices.begin(), choices.end(),
                      [](const Choice& a, const Choice& b) {
                          if (a.uncovered != b.uncovered) {
                              return a.uncovered < b.uncovered;
                          }
                          if (a.noncritical != b.noncritical) {
                              return a.noncritical < b.noncritical;
                          }
                          return a.tie < b.tie;
                      });
            const int rcl = std::min<int>(5, choices.size());
            const Choice& chosen = choices[rng() % rcl];
            g.set_edge(chosen.edge.first, chosen.edge.second, false);
            metrics = chosen.metrics;
        }

        if (!metrics.d2c) continue;
        const Metrics slow = analyze_slow(g, false);
        if (!same_semantics(metrics, slow) || !slow.d2c) {
            std::cerr << "prune verifier disagreement lane=" << lane
                      << " restart=" << local_restarts << "\n";
            shared.hit.store(true);
            return;
        }
        {
            std::lock_guard<std::mutex> lock(shared.mutex);
            if (metrics.edges > shared.best_edges) {
                shared.best_edges = metrics.edges;
                shared.best_graph = g;
                shared.best_metrics = metrics;
                emit_prune_best(lane, local_restarts, g, metrics);
            }
        }
        if (metrics.edges >= 157) {
            shared.hit.store(true);
            return;
        }
    }
}

int run_prune_search(int threads, int seconds, std::uint64_t seed) {
    if (threads < 1 || threads > 64 || seconds < 1) {
        std::cerr << "invalid search parameters\n";
        return 2;
    }
    PruneShared shared;
    std::vector<std::thread> pool;
    for (int lane = 0; lane < threads; ++lane) {
        pool.emplace_back(prune_lane, lane, seconds, seed, std::ref(shared));
    }
    for (auto& thread : pool) thread.join();
    std::cout << "{\"prune_search_complete\":true,\"threads\":" << threads
              << ",\"seconds\":" << seconds << ",\"seed\":" << seed
              << ",\"restarts\":" << shared.restarts.load()
              << ",\"hit\":" << (shared.hit.load() ? "true" : "false")
              << ",\"best_edges\":" << shared.best_edges << "}\n";
    return shared.hit.load() ? 0 : 1;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--calibrate") {
        return run_calibration();
    }
    if (argc == 8 && std::string(argv[1]) == "--search" &&
        std::string(argv[2]) == "--threads" &&
        std::string(argv[4]) == "--seconds" &&
        std::string(argv[6]) == "--seed") {
        return run_prune_search(parse_int(argv[3]), parse_int(argv[5]),
                                parse_u64(argv[7]));
    }
    std::cerr << "usage:\n"
              << "  d2c_prune --calibrate\n"
              << "  d2c_prune --search --threads N --seconds S --seed X\n";
    return 2;
}
