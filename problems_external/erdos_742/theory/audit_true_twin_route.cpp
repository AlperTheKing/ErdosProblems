#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <vector>

using U64 = std::uint64_t;

struct Graph {
    int n = 0;
    std::vector<U64> adj;
};

static bool has_total_dominating_pair(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            if (((g.adj[x] >> y) & 1U) == 0) continue;
            if ((g.adj[x] | g.adj[y]) == all) return true;
        }
    }
    return false;
}

static bool has_total_dominating_triple(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            for (int z = y + 1; z < g.n; ++z) {
                if ((g.adj[x] | g.adj[y] | g.adj[z]) == all) return true;
            }
        }
    }
    return false;
}

static bool is_3t_critical(const Graph& g) {
    for (int v = 0; v < g.n; ++v) {
        if (g.adj[v] == 0) return false;
    }
    if (has_total_dominating_pair(g)) return false;
    if (!has_total_dominating_triple(g)) return false;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            if ((g.adj[x] >> y) & 1U) continue;
            Graph h = g;
            h.adj[x] |= U64{1} << y;
            h.adj[y] |= U64{1} << x;
            if (!has_total_dominating_pair(h)) return false;
        }
    }
    return true;
}

static Graph add_true_twin(const Graph& g, int v) {
    Graph h{g.n + 1, std::vector<U64>(g.n + 1)};
    for (int x = 0; x < g.n; ++x) h.adj[x] = g.adj[x];
    const int w = g.n;
    for (int x = 0; x < g.n; ++x) {
        if (x == v || ((g.adj[v] >> x) & 1U)) {
            h.adj[w] |= U64{1} << x;
            h.adj[x] |= U64{1} << w;
        }
    }
    return h;
}

static int degree(const Graph& g, int v) {
    return __builtin_popcountll(g.adj[v]);
}

static void print_graph(const Graph& g) {
    std::cout << "n=" << g.n << " edges=";
    int m = 0;
    for (int v = 0; v < g.n; ++v) m += degree(g, v);
    std::cout << m / 2 << " adjacency=";
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
    int max_n = 7;
    if (argc == 2) max_n = std::stoi(argv[1]);
    std::uint64_t total_3t = 0;
    std::uint64_t no_cloneable = 0;
    std::uint64_t no_cloneable_min_degree = 0;
    std::uint64_t no_cloneable_at_most_average = 0;
    bool printed_first = false;
    bool printed_first_average = false;

    for (int n = 3; n <= max_n; ++n) {
        const int pairs = n * (n - 1) / 2;
        if (pairs >= 63) return 2;
        const U64 count = U64{1} << pairs;
        std::uint64_t at_n = 0;
        for (U64 mask = 0; mask < count; ++mask) {
            Graph g{n, std::vector<U64>(n)};
            int bit = 0;
            for (int x = 0; x < n; ++x) {
                for (int y = x + 1; y < n; ++y, ++bit) {
                    if ((mask >> bit) & 1U) {
                        g.adj[x] |= U64{1} << y;
                        g.adj[y] |= U64{1} << x;
                    }
                }
            }
            if (!is_3t_critical(g)) continue;
            ++at_n;
            ++total_3t;
            int min_degree = std::numeric_limits<int>::max();
            int degree_sum = 0;
            for (int v = 0; v < n; ++v) {
                min_degree = std::min(min_degree, degree(g, v));
                degree_sum += degree(g, v);
            }
            bool any = false;
            bool any_min = false;
            bool any_at_most_average = false;
            for (int v = 0; v < n; ++v) {
                if (is_3t_critical(add_true_twin(g, v))) {
                    any = true;
                    if (degree(g, v) == min_degree) any_min = true;
                    if (degree(g, v) * n <= degree_sum) any_at_most_average = true;
                }
            }
            if (!any) ++no_cloneable;
            if (!any_min) {
                ++no_cloneable_min_degree;
                if (!printed_first) {
                    std::cout << "FIRST_NO_CLONEABLE_MIN_DEGREE ";
                    print_graph(g);
                    printed_first = true;
                }
            }
            if (!any_at_most_average) {
                ++no_cloneable_at_most_average;
                if (!printed_first_average) {
                    std::cout << "FIRST_NO_CLONEABLE_AT_MOST_AVERAGE ";
                    print_graph(g);
                    printed_first_average = true;
                }
            }
        }
        std::cout << "n=" << n << " labeled_3t_critical=" << at_n << "\n";
    }
    std::cout << "SUMMARY total_3t=" << total_3t
              << " no_cloneable=" << no_cloneable
              << " no_cloneable_min_degree=" << no_cloneable_min_degree
              << " no_cloneable_at_most_average=" << no_cloneable_at_most_average << "\n";
}
