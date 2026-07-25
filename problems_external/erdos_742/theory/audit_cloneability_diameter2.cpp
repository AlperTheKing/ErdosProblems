#define main audit_enumeration_main
#include "audit_true_twin_route.cpp"
#undef main

static bool has_diameter_two(const Graph& g) {
    const U64 all = (U64{1} << g.n) - 1;
    bool has_nonedge = false;
    for (int v = 0; v < g.n; ++v) {
        U64 reached = g.adj[v] | (U64{1} << v);
        U64 first = g.adj[v];
        while (first) {
            const int u = __builtin_ctzll(first);
            first &= first - 1;
            reached |= g.adj[u];
        }
        if (reached != all) return false;
        has_nonedge |= (g.adj[v] | (U64{1} << v)) != all;
    }
    return has_nonedge;
}

int main(int argc, char** argv) {
    int max_n = 7;
    if (argc == 2) max_n = std::stoi(argv[1]);
    std::uint64_t total = 0;
    std::uint64_t no_cloneable = 0;
    std::uint64_t no_cloneable_min = 0;
    std::uint64_t no_cloneable_average = 0;
    bool printed_min = false;
    bool printed_average = false;
    for (int n = 3; n <= max_n; ++n) {
        const int pairs = n * (n - 1) / 2;
        const U64 count = U64{1} << pairs;
        std::uint64_t at_n = 0;
        for (U64 mask = 0; mask < count; ++mask) {
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
            if (!is_3t_critical(g) || !has_diameter_two(g)) continue;
            ++total;
            ++at_n;
            int minimum = g.n;
            int degree_sum = 0;
            for (int v = 0; v < n; ++v) {
                minimum = std::min(minimum, degree(g, v));
                degree_sum += degree(g, v);
            }
            bool any = false;
            bool any_min = false;
            bool any_average = false;
            for (int v = 0; v < n; ++v) {
                if (!is_3t_critical(add_true_twin(g, v))) continue;
                any = true;
                any_min |= degree(g, v) == minimum;
                any_average |= degree(g, v) * n <= degree_sum;
            }
            if (!any) ++no_cloneable;
            if (!any_min) {
                ++no_cloneable_min;
                if (!printed_min) {
                    std::cout << "FIRST_NO_CLONEABLE_MIN ";
                    print_graph(g);
                    printed_min = true;
                }
            }
            if (!any_average) {
                ++no_cloneable_average;
                if (!printed_average) {
                    std::cout << "FIRST_NO_CLONEABLE_AVERAGE ";
                    print_graph(g);
                    printed_average = true;
                }
            }
        }
        std::cout << "n=" << n << " labeled_diam2_3t=" << at_n << "\n";
    }
    std::cout << "SUMMARY total=" << total
              << " no_cloneable=" << no_cloneable
              << " no_cloneable_min=" << no_cloneable_min
              << " no_cloneable_average=" << no_cloneable_average << "\n";
}
