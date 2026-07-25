#include <algorithm>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>

using Mask = std::uint64_t;

struct Graph {
    int n;
    std::vector<Mask> a;
};

static void add_edge(Graph& g, int x, int y) {
    g.a[x] |= Mask{1} << y;
    g.a[y] |= Mask{1} << x;
}

static bool total_dominates(const Graph& g, Mask s) {
    Mask dominated = 0;
    while (s) {
        const int v = std::countr_zero(s);
        s &= s - 1;
        dominated |= g.a[v];
    }
    return dominated == ((Mask{1} << g.n) - 1);
}

static int total_domination_number_at_most_three(const Graph& g) {
    for (int k = 1; k <= 3; ++k) {
        for (Mask s = 1; s < (Mask{1} << g.n); ++s) {
            if (std::popcount(s) == k && total_dominates(g, s)) return k;
        }
    }
    return 4;
}

static bool critical(const Graph& g) {
    if (total_domination_number_at_most_three(g) != 3) return false;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            if ((g.a[x] >> y) & 1U) continue;
            Graph h = g;
            add_edge(h, x, y);
            if (total_domination_number_at_most_three(h) != 2) return false;
        }
    }
    return true;
}

static bool diameter_two(const Graph& g) {
    const Mask all = (Mask{1} << g.n) - 1;
    for (int v = 0; v < g.n; ++v) {
        Mask seen = g.a[v] | (Mask{1} << v);
        for (int u = 0; u < g.n; ++u)
            if ((g.a[v] >> u) & 1U) seen |= g.a[u];
        if (seen != all) return false;
    }
    return true;
}

static Graph add_true_twin(const Graph& g, int v) {
    Graph h{g.n + 1, std::vector<Mask>(g.n + 1)};
    for (int x = 0; x < g.n; ++x) h.a[x] = g.a[x];
    for (int x = 0; x < g.n; ++x) {
        if (x == v || ((g.a[v] >> x) & 1U)) add_edge(h, g.n, x);
    }
    return h;
}

int main() {
    Graph g{12, std::vector<Mask>(12)};
    const std::vector<std::vector<int>> rows = {
        {2,3,4,6,9,11}, {4,5,7,10}, {0,6,7,10,11},
        {0,5,6,7,8,9,10,11}, {0,1,5,6,8,11},
        {1,3,4,7,8,9,10,11}, {0,2,3,4,8,9,10},
        {1,2,3,5,8,9}, {3,4,5,6,7,9,10,11},
        {0,3,5,6,7,8,10,11}, {1,2,3,5,6,8,9,11},
        {0,2,3,4,5,8,9,10}
    };
    for (int x = 0; x < g.n; ++x)
        for (int y : rows[x])
            if (x < y) add_edge(g, x, y);

    if (!critical(g) || !diameter_two(g)) return 2;

    int degree_sum = 0;
    int minimum = g.n;
    std::vector<int> cloneable;
    for (int v = 0; v < g.n; ++v) {
        const int d = std::popcount(g.a[v]);
        degree_sum += d;
        minimum = std::min(minimum, d);
        if (critical(add_true_twin(g, v))) cloneable.push_back(v);
    }

    std::cout << "VERIFIED n=12 m=" << degree_sum / 2
              << " diameter=2 gamma_t_edge_critical=3"
              << " min_degree=" << minimum
              << " average_degree=" << degree_sum << "/12\n";
    std::cout << "cloneable_vertices=";
    for (std::size_t i = 0; i < cloneable.size(); ++i) {
        if (i) std::cout << ",";
        const int v = cloneable[i];
        std::cout << v << "(d=" << std::popcount(g.a[v]) << ")";
    }
    std::cout << "\n";

    bool low = false;
    for (int v : cloneable)
        low |= 12 * std::popcount(g.a[v]) <= degree_sum + 12;
    if (low) return 3;
    if (10 * minimum < 3 * g.n) return 4;
    std::cout << "AVERAGE_PLUS_ONE_CLONEABILITY_FALSE\n";
}
