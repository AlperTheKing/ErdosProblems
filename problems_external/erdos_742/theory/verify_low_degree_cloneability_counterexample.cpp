#define main audit_enumeration_main
#include "audit_true_twin_route.cpp"
#undef main

static bool diameter_two(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    bool noncomplete = false;
    for (int v = 0; v < g.n; ++v) {
        U64 reached = g.adj[v] | (U64{1} << v);
        U64 first = g.adj[v];
        while (first) {
            int u = __builtin_ctzll(first);
            first &= first - 1;
            reached |= g.adj[u];
        }
        if (reached != all) return false;
        noncomplete |= (g.adj[v] | (U64{1} << v)) != all;
    }
    return noncomplete;
}

int main() {
    Graph h{11, std::vector<U64>(11)};
    const std::vector<std::vector<int>> adjacency = {
        {2,3,5,6,7,10},
        {2,4,5,6,7,8,10},
        {0,1,5,6,7,8,10},
        {0,4,10},
        {1,3,6,8,9,10},
        {0,1,2,8,9},
        {0,1,2,4,7,9},
        {0,1,2,6,8,9,10},
        {1,2,4,5,7,9,10},
        {4,5,6,7,8},
        {0,1,2,3,4,7,8}
    };
    for (int v = 0; v < h.n; ++v) {
        for (int u : adjacency[v]) h.adj[v] |= U64{1} << u;
    }
    if (!is_3t_critical(h) || !diameter_two(h)) return 2;
    int degree_sum = 0;
    int min_degree = h.n;
    for (int v = 0; v < h.n; ++v) {
        degree_sum += degree(h, v);
        min_degree = std::min(min_degree, degree(h, v));
    }
    std::cout << "VERIFIED n=11 m=" << degree_sum / 2
              << " diameter=2 gamma_t_edge_critical=3"
              << " min_degree=" << min_degree
              << " average_degree=" << degree_sum << "/11"
              << " ceil_average=" << (degree_sum + 10) / 11 << "\n";
    std::cout << "cloneable_vertices=";
    bool first = true;
    int min_cloneable = h.n;
    for (int v = 0; v < h.n; ++v) {
        if (!is_3t_critical(add_true_twin(h, v))) continue;
        if (!first) std::cout << ",";
        std::cout << v << "(d=" << degree(h, v) << ")";
        first = false;
        min_cloneable = std::min(min_cloneable, degree(h, v));
    }
    std::cout << " min_cloneable_degree=" << min_cloneable << "\n";
    if (min_cloneable <= (degree_sum + 10) / 11) return 3;
    std::cout << "LOW_DEGREE_CLONEABILITY_FALSE\n";
}
