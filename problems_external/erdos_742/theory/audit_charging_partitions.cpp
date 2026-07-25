#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
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

static int popcount(U64 x) {
    return __builtin_popcountll(x);
}

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
    if (u == v) return false;
    Graph h = g;
    h.adj[e.a] &= ~(U64{1} << e.b);
    h.adj[e.b] &= ~(U64{1} << e.a);
    if (((h.adj[u] >> v) & 1U) != 0) return false;
    return (h.adj[u] & h.adj[v]) == 0;
}

static bool augment(int left, const std::vector<std::vector<int>>& options,
                    std::vector<int>& right_match, std::vector<char>& seen) {
    for (int r : options[left]) {
        if (seen[r]) continue;
        seen[r] = 1;
        if (right_match[r] == -1 ||
            augment(right_match[r], options, right_match, seen)) {
            right_match[r] = left;
            return true;
        }
    }
    return false;
}

static bool has_critical_charging(const Graph& g, U64 side) {
    std::vector<Edge> inside;
    std::vector<Edge> missing_cross;
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            const bool cross = ((side >> a) & 1U) != ((side >> b) & 1U);
            const bool edge = ((g.adj[a] >> b) & 1U) != 0;
            if (!cross && edge) inside.push_back({a, b});
            if (cross && !edge) missing_cross.push_back({a, b});
        }
    }
    if (inside.size() > missing_cross.size()) return false;
    std::vector<std::vector<int>> options(inside.size());
    for (int i = 0; i < static_cast<int>(inside.size()); ++i) {
        for (int j = 0; j < static_cast<int>(missing_cross.size()); ++j) {
            const auto& p = missing_cross[j];
            if (critical_for(g, inside[i], p.a, p.b)) options[i].push_back(j);
        }
        if (options[i].empty()) return false;
    }
    std::vector<int> right_match(missing_cross.size(), -1);
    for (int i = 0; i < static_cast<int>(inside.size()); ++i) {
        std::vector<char> seen(missing_cross.size(), 0);
        if (!augment(i, options, right_match, seen)) return false;
    }
    return true;
}

static int cut_size(const Graph& g, U64 side) {
    int result = 0;
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            if ((((side >> a) ^ (side >> b)) & 1U) &&
                ((g.adj[a] >> b) & 1U)) {
                ++result;
            }
        }
    }
    return result;
}

static void print_graph(const Graph& g) {
    int m = 0;
    for (int v = 0; v < g.n; ++v) m += popcount(g.adj[v]);
    std::cout << "n=" << g.n << " m=" << m / 2 << " adjacency=";
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
    std::uint64_t total = 0;
    std::uint64_t no_good_partition = 0;
    std::uint64_t some_bad_max_cut = 0;
    std::uint64_t no_good_max_cut = 0;
    bool printed_any = false;
    bool printed_max = false;

    for (int n = 3; n <= max_n; ++n) {
        const int pairs = n * (n - 1) / 2;
        const U64 graph_count = U64{1} << pairs;
        std::uint64_t at_n = 0;
        for (U64 mask = 0; mask < graph_count; ++mask) {
            Graph g{n, std::vector<U64>(n)};
            int bit = 0;
            for (int a = 0; a < n; ++a) {
                for (int b = a + 1; b < n; ++b, ++bit) {
                    if ((mask >> bit) & 1U) {
                        g.adj[a] |= U64{1} << b;
                        g.adj[b] |= U64{1} << a;
                    }
                }
            }
            if (!is_d2c(g)) continue;
            ++total;
            ++at_n;
            int maximum = -1;
            for (U64 side = 1; side < (U64{1} << (n - 1)); ++side) {
                maximum = std::max(maximum, cut_size(g, side));
            }
            bool any_good = false;
            bool any_good_max = false;
            bool any_bad_max = false;
            for (U64 side = 1; side < (U64{1} << (n - 1)); ++side) {
                const bool good = has_critical_charging(g, side);
                any_good |= good;
                if (cut_size(g, side) == maximum) {
                    any_good_max |= good;
                    any_bad_max |= !good;
                }
            }
            if (!any_good) {
                ++no_good_partition;
                if (!printed_any) {
                    std::cout << "FIRST_NO_GOOD_PARTITION ";
                    print_graph(g);
                    printed_any = true;
                }
            }
            if (!any_good_max) {
                ++no_good_max_cut;
                if (!printed_max) {
                    std::cout << "FIRST_NO_GOOD_MAX_CUT ";
                    print_graph(g);
                    printed_max = true;
                }
            }
            if (any_bad_max) ++some_bad_max_cut;
        }
        std::cout << "n=" << n << " labeled_d2c=" << at_n << "\n";
    }
    std::cout << "SUMMARY total=" << total
              << " no_good_partition=" << no_good_partition
              << " no_good_max_cut=" << no_good_max_cut
              << " some_bad_max_cut=" << some_bad_max_cut << "\n";
}
