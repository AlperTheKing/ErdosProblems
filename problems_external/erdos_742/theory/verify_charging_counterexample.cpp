#include <cstdint>
#include <iostream>
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

int main() {
    Graph g{8, std::vector<U64>(8)};
    const std::vector<Edge> edges = {
        {0,4},{0,7},{1,2},{1,4},{2,4},{2,5},
        {2,7},{3,4},{3,6},{3,7},{4,5},{4,6}
    };
    for (const auto& e : edges) {
        g.adj[e.a] |= U64{1} << e.b;
        g.adj[e.b] |= U64{1} << e.a;
    }

    if (!diameter_at_most_two(g)) return 2;
    for (const auto& e : edges) {
        Graph h = g;
        h.adj[e.a] &= ~(U64{1} << e.b);
        h.adj[e.b] &= ~(U64{1} << e.a);
        if (diameter_at_most_two(h)) return 3;
    }

    int maximum = -1;
    int max_cut_count = 0;
    for (U64 side = 1; side < (U64{1} << 7); ++side) {
        const int value = cut_size(g, side);
        if (value > maximum) {
            maximum = value;
            max_cut_count = 1;
        } else if (value == maximum) {
            ++max_cut_count;
        }
    }

    const U64 side = 28;  // X={2,3,4}; Y={0,1,5,6,7}
    if (cut_size(g, side) != maximum) return 4;

    std::cout << "VERIFIED D2C n=8 m=12 max_cut=" << maximum
              << " max_cut_count_up_to_complement=" << max_cut_count << "\n";
    std::cout << "partition X={2,3,4} Y={0,1,5,6,7}\n";
    bool found_failure = false;
    for (const auto& e : edges) {
        const bool internal =
            (((side >> e.a) ^ (side >> e.b)) & 1U) == 0;
        if (!internal) continue;
        std::cout << "internal_edge=" << e.a << "-" << e.b
                  << " critical_pairs=";
        bool cross_critical = false;
        bool first = true;
        for (int u = 0; u < g.n; ++u) {
            for (int v = u + 1; v < g.n; ++v) {
                if (!critical_for(g, e, u, v)) continue;
                if (!first) std::cout << ",";
                std::cout << u << "-" << v;
                first = false;
                const bool cross =
                    (((side >> u) ^ (side >> v)) & 1U) != 0;
                const bool missing = ((g.adj[u] >> v) & 1U) == 0;
                cross_critical |= cross && missing;
            }
        }
        std::cout << " cross_missing_critical=" << (cross_critical ? 1 : 0) << "\n";
        found_failure |= !cross_critical;
    }
    if (!found_failure) return 5;
    std::cout << "CHARGING_LEMMA_FALSE\n";
}
