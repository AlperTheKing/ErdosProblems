#define main audit_enumeration_main
#include "audit_true_twin_route.cpp"
#undef main

int main() {
    const int n = 8;
    Graph d2c{n, std::vector<U64>(n)};
    const std::vector<std::pair<int,int>> d2c_edges = {
        {0,4},{0,7},{1,2},{1,4},{2,4},{2,5},
        {2,7},{3,4},{3,6},{3,7},{4,5},{4,6}
    };
    for (const auto& [a,b] : d2c_edges) {
        d2c.adj[a] |= U64{1} << b;
        d2c.adj[b] |= U64{1} << a;
    }
    Graph h{n, std::vector<U64>(n)};
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) {
            if (((d2c.adj[a] >> b) & 1U) == 0) {
                h.adj[a] |= U64{1} << b;
                h.adj[b] |= U64{1} << a;
            }
        }
    }
    std::cout << "H_IS_3T_CRITICAL=" << (is_3t_critical(h) ? 1 : 0) << "\n";
    print_graph(h);
    std::cout << "cloneable=";
    bool first = true;
    for (int v = 0; v < n; ++v) {
        if (!is_3t_critical(add_true_twin(h, v))) continue;
        if (!first) std::cout << ",";
        std::cout << v << "(d=" << degree(h, v) << ")";
        first = false;
    }
    std::cout << "\n";
}
