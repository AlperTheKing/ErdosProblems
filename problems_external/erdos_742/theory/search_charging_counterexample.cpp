#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

using U64 = std::uint64_t;

struct Graph {
    int n = 0;
    std::vector<U64> adj;
};

struct Edge {
    int a = 0;
    int b = 0;
};

static bool diameter_at_most_two(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    for (int v = 0; v < g.n; ++v) {
        U64 reached = g.adj[v] | (U64{1} << v);
        U64 first = g.adj[v];
        while (first) {
            const int u = __builtin_ctzll(first);
            first &= first - 1;
            reached |= g.adj[u];
        }
        if (reached != all) return false;
    }
    return true;
}

static bool is_complete(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    for (int v = 0; v < g.n; ++v) {
        if ((g.adj[v] | (U64{1} << v)) != all) return false;
    }
    return true;
}

static bool is_d2c(const Graph& g) {
    if (is_complete(g) || !diameter_at_most_two(g)) return false;
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            if (((g.adj[a] >> b) & 1U) == 0) continue;
            Graph h = g;
            h.adj[a] &= ~(U64{1} << b);
            h.adj[b] &= ~(U64{1} << a);
            if (diameter_at_most_two(h)) return false;
        }
    }
    return true;
}

static bool critical_for(const Graph& g, const Edge& e, int u, int v) {
    Graph h = g;
    h.adj[e.a] &= ~(U64{1} << e.b);
    h.adj[e.b] &= ~(U64{1} << e.a);
    return (((h.adj[u] >> v) & 1U) == 0) && ((h.adj[u] & h.adj[v]) == 0);
}

static int cut_size(const Graph& g, U64 side) {
    int result = 0;
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            if ((((side >> a) ^ (side >> b)) & 1U) &&
                ((g.adj[a] >> b) & 1U)) ++result;
        }
    }
    return result;
}

static bool charging_holds(const Graph& g, U64 side) {
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            if ((((side >> a) ^ (side >> b)) & 1U) != 0) continue;
            if (((g.adj[a] >> b) & 1U) == 0) continue;
            const Edge e{a, b};
            bool found = false;
            for (int u = 0; u < g.n && !found; ++u) {
                for (int v = u + 1; v < g.n; ++v) {
                    if ((((side >> u) ^ (side >> v)) & 1U) == 0) continue;
                    if ((g.adj[u] >> v) & 1U) continue;
                    if (critical_for(g, e, u, v)) {
                        found = true;
                        break;
                    }
                }
            }
            if (!found) return false;
        }
    }
    return true;
}

static bool every_max_cut_holds(const Graph& g, U64& bad_side) {
    const U64 limit = U64{1} << (g.n - 1);
    int maximum = -1;
    for (U64 side = 1; side < limit; ++side) {
        maximum = std::max(maximum, cut_size(g, side));
    }
    for (U64 side = 1; side < limit; ++side) {
        if (cut_size(g, side) == maximum && !charging_holds(g, side)) {
            bad_side = side;
            return false;
        }
    }
    return true;
}

static Graph greedy_minimal_diameter_two(int n, std::mt19937_64& rng) {
    Graph g{n, std::vector<U64>(n)};
    std::vector<Edge> pairs;
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) {
            g.adj[a] |= U64{1} << b;
            g.adj[b] |= U64{1} << a;
            pairs.push_back({a, b});
        }
    }
    std::shuffle(pairs.begin(), pairs.end(), rng);
    bool changed = true;
    while (changed) {
        changed = false;
        std::shuffle(pairs.begin(), pairs.end(), rng);
        for (const auto& e : pairs) {
            if (((g.adj[e.a] >> e.b) & 1U) == 0) continue;
            g.adj[e.a] &= ~(U64{1} << e.b);
            g.adj[e.b] &= ~(U64{1} << e.a);
            if (diameter_at_most_two(g)) {
                changed = true;
            } else {
                g.adj[e.a] |= U64{1} << e.b;
                g.adj[e.b] |= U64{1} << e.a;
            }
        }
    }
    return g;
}

static Graph greedy_maximal_triangle_free(int n, std::mt19937_64& rng) {
    Graph g{n, std::vector<U64>(n)};
    std::vector<Edge> pairs;
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
    }
    std::shuffle(pairs.begin(), pairs.end(), rng);
    for (const auto& e : pairs) {
        if ((g.adj[e.a] & g.adj[e.b]) != 0) continue;
        g.adj[e.a] |= U64{1} << e.b;
        g.adj[e.b] |= U64{1} << e.a;
    }
    return g;
}

static void print_graph(const Graph& g, U64 side) {
    int m2 = 0;
    for (int v = 0; v < g.n; ++v) m2 += __builtin_popcountll(g.adj[v]);
    std::cout << "n=" << g.n << " m=" << m2 / 2 << " side=" << side
              << " adjacency=";
    for (int v = 0; v < g.n; ++v) {
        std::cout << v << ":[";
        bool first = true;
        for (int u = 0; u < g.n; ++u) {
            if ((g.adj[v] >> u) & 1U) {
                if (!first) std::cout << ",";
                std::cout << u;
                first = false;
            }
        }
        std::cout << "] ";
    }
    std::cout << "\n";
}

int main(int argc, char** argv) {
    int samples = 200;
    if (argc == 2) samples = std::stoi(argv[1]);
    std::mt19937_64 rng(74220260723ULL);
    std::uint64_t tested = 0;
    for (int n = 8; n <= 16; ++n) {
        for (int sample = 0; sample < samples; ++sample) {
            for (int family = 0; family < 2; ++family) {
                Graph g = family == 0
                    ? greedy_minimal_diameter_two(n, rng)
                    : greedy_maximal_triangle_free(n, rng);
                if (!is_d2c(g)) continue;
                ++tested;
                U64 bad_side = 0;
                if (!every_max_cut_holds(g, bad_side)) {
                    std::cout << "COUNTEREXAMPLE family=" << family << " ";
                    print_graph(g, bad_side);
                    return 1;
                }
            }
        }
        std::cout << "n=" << n << " tested_so_far=" << tested << "\n";
    }
    std::cout << "NO_COUNTEREXAMPLE tested=" << tested << "\n";
}
