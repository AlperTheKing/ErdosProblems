#define main audit_enumeration_main
#include "audit_true_twin_route.cpp"
#undef main

#include <algorithm>
#include <random>

struct E2 {
    int a;
    int b;
};

static bool diam2_or_less(const Graph& g) {
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

static Graph minimal_diam2(int n, std::mt19937_64& rng) {
    Graph g{n, std::vector<U64>(n)};
    std::vector<E2> pairs;
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) {
            g.adj[a] |= U64{1} << b;
            g.adj[b] |= U64{1} << a;
            pairs.push_back({a,b});
        }
    }
    bool changed = true;
    while (changed) {
        changed = false;
        std::shuffle(pairs.begin(), pairs.end(), rng);
        for (const auto& e : pairs) {
            if (((g.adj[e.a] >> e.b) & 1U) == 0) continue;
            g.adj[e.a] &= ~(U64{1} << e.b);
            g.adj[e.b] &= ~(U64{1} << e.a);
            if (diam2_or_less(g)) {
                changed = true;
            } else {
                g.adj[e.a] |= U64{1} << e.b;
                g.adj[e.b] |= U64{1} << e.a;
            }
        }
    }
    return g;
}

static Graph complement_graph(const Graph& g) {
    Graph h{g.n, std::vector<U64>(g.n)};
    for (int a = 0; a < g.n; ++a) {
        for (int b = a + 1; b < g.n; ++b) {
            if (((g.adj[a] >> b) & 1U) == 0) {
                h.adj[a] |= U64{1} << b;
                h.adj[b] |= U64{1} << a;
            }
        }
    }
    return h;
}

int main(int argc, char** argv) {
    int samples = 5000;
    if (argc == 2) samples = std::stoi(argv[1]);
    std::mt19937_64 rng(742260723ULL);
    std::uint64_t tested = 0;
    std::uint64_t no_cloneable_low_ceiling_average = 0;
    bool printed_average = false;
    for (int n = 8; n <= 20; ++n) {
        for (int s = 0; s < samples; ++s) {
            Graph h = complement_graph(minimal_diam2(n, rng));
            if (!is_3t_critical(h)) continue;
            if (!diam2_or_less(h)) continue;  // excludes the solved dominating-edge class
            int minimum_degree = n;
            for (int v = 0; v < n; ++v) {
                minimum_degree = std::min(minimum_degree, degree(h, v));
            }
            if (10 * minimum_degree < 3 * n) {
                continue;  // Fan already handles delta <= 0.3n
            }
            ++tested;
            int degree_sum = 0;
            for (int v = 0; v < n; ++v) degree_sum += degree(h, v);
            bool any = false;
            bool any_at_most_ceiling_average = false;
            for (int v = 0; v < n; ++v) {
                if (!is_3t_critical(add_true_twin(h, v))) continue;
                any = true;
                any_at_most_ceiling_average |= degree(h, v) * n <= degree_sum + n;
            }
            if (!any) {
                std::cout << "NO_CLONEABLE ";
                print_graph(h);
                return 1;
            }
            if (!any_at_most_ceiling_average) {
                ++no_cloneable_low_ceiling_average;
                if (!printed_average) {
                    std::cout << "NO_CLONEABLE_AT_MOST_AVERAGE_PLUS_ONE ";
                    print_graph(h);
                    printed_average = true;
                }
            }
        }
        std::cout << "n=" << n << " tested_so_far=" << tested << "\n";
    }
    std::cout << "NO_NO_CLONEABLE tested=" << tested
              << " no_cloneable_at_most_ceiling_average=" << no_cloneable_low_ceiling_average << "\n";
}
