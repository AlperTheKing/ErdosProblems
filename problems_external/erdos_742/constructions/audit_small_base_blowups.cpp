#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <string>
#include <vector>

using U32 = std::uint32_t;
using U64 = std::uint64_t;

struct Graph {
    int n = 0;
    std::vector<U32> adj;
};

static Graph graph_from_mask(int n, U64 mask) {
    Graph g{n, std::vector<U32>(n)};
    int bit = 0;
    for (int x = 0; x < n; ++x) {
        for (int y = x + 1; y < n; ++y, ++bit) {
            if (((mask >> bit) & 1U) == 0) continue;
            g.adj[x] |= U32{1} << y;
            g.adj[y] |= U32{1} << x;
        }
    }
    return g;
}

static int edge_count(const Graph& g) {
    int twice = 0;
    for (U32 row : g.adj) twice += std::popcount(row);
    return twice / 2;
}

static bool diameter_two(const Graph& g) {
    const U32 all = (U32{1} << g.n) - 1;
    bool noncomplete = false;
    for (int v = 0; v < g.n; ++v) {
        U32 reached = g.adj[v] | (U32{1} << v);
        U32 first = g.adj[v];
        while (first) {
            const int u = std::countr_zero(first);
            first &= first - 1;
            reached |= g.adj[u];
        }
        if (reached != all) return false;
        if (std::popcount(g.adj[v]) < g.n - 1) noncomplete = true;
    }
    return noncomplete;
}

static bool d2c(const Graph& g) {
    if (!diameter_two(g)) return false;
    const U32 all = (U32{1} << g.n) - 1;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            if (((g.adj[x] >> y) & 1U) == 0) continue;
            std::vector<U32> h = g.adj;
            h[x] &= ~(U32{1} << y);
            h[y] &= ~(U32{1} << x);
            bool witnessed = false;
            for (int v = 0; v < g.n && !witnessed; ++v) {
                U32 reached = h[v] | (U32{1} << v);
                U32 first = h[v];
                while (first) {
                    const int u = std::countr_zero(first);
                    first &= first - 1;
                    reached |= h[u];
                }
                witnessed = reached != all;
            }
            if (!witnessed) return false;
        }
    }
    return true;
}

static U64 permuted_mask(const Graph& g, const std::vector<int>& p) {
    U64 mask = 0;
    int bit = 0;
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y, ++bit) {
            if ((g.adj[p[x]] >> p[y]) & 1U) mask |= U64{1} << bit;
        }
    }
    return mask;
}

static U64 canonical_mask(const Graph& g) {
    std::vector<int> p(g.n);
    std::iota(p.begin(), p.end(), 0);
    U64 best = ~U64{0};
    do {
        best = std::min(best, permuted_mask(g, p));
    } while (std::next_permutation(p.begin(), p.end()));
    return best;
}

static std::vector<U64> unlabeled_d2c_bases(int n) {
    const int pairs = n * (n - 1) / 2;
    const U64 total = U64{1} << pairs;
    std::set<U64> canonical;
    for (U64 mask = 0; mask < total; ++mask) {
        const Graph g = graph_from_mask(n, mask);
        if (d2c(g)) canonical.insert(canonical_mask(g));
    }
    return {canonical.begin(), canonical.end()};
}

static Graph substitute(
    const Graph& base,
    const std::vector<int>& sizes,
    unsigned clique_mask
) {
    const int k = base.n;
    std::vector<int> start(k + 1);
    for (int i = 0; i < k; ++i) start[i + 1] = start[i] + sizes[i];
    Graph g{start[k], std::vector<U32>(start[k])};
    for (int i = 0; i < k; ++i) {
        if ((clique_mask >> i) & 1U) {
            for (int x = start[i]; x < start[i + 1]; ++x) {
                for (int y = x + 1; y < start[i + 1]; ++y) {
                    g.adj[x] |= U32{1} << y;
                    g.adj[y] |= U32{1} << x;
                }
            }
        }
        for (int j = i + 1; j < k; ++j) {
            if (((base.adj[i] >> j) & 1U) == 0) continue;
            for (int x = start[i]; x < start[i + 1]; ++x) {
                for (int y = start[j]; y < start[j + 1]; ++y) {
                    g.adj[x] |= U32{1} << y;
                    g.adj[y] |= U32{1} << x;
                }
            }
        }
    }
    return g;
}

struct Audit {
    U64 compositions = 0;
    U64 substitutions = 0;
    U64 threshold_tests = 0;
    int best = 156; // P3 -> K_12,13 is in the audited family.
    int best_n = 3;
    U64 best_base = 3; // P3 under the local bit convention.
    unsigned best_types = 0;
    std::vector<int> best_sizes{12, 1, 12};
    Graph target;
};

static int substitution_edges(
    const Graph& base,
    const std::vector<int>& a,
    unsigned types
) {
    int m = 0;
    for (int i = 0; i < base.n; ++i) {
        if ((types >> i) & 1U) m += a[i] * (a[i] - 1) / 2;
        for (int j = i + 1; j < base.n; ++j) {
            if ((base.adj[i] >> j) & 1U) m += a[i] * a[j];
        }
    }
    return m;
}

static void audit_composition(
    const Graph& base,
    U64 base_mask,
    const std::vector<int>& a,
    Audit& audit
) {
    ++audit.compositions;
    const unsigned type_count = 1U << base.n;
    for (unsigned types = 0; types < type_count; ++types) {
        ++audit.substitutions;
        const int m = substitution_edges(base, a, types);
        if (m <= audit.best) continue;
        ++audit.threshold_tests;
        const Graph g = substitute(base, a, types);
        if (!d2c(g)) continue;
        audit.best = m;
        audit.best_n = base.n;
        audit.best_base = base_mask;
        audit.best_types = types;
        audit.best_sizes = a;
        if (m >= 157) audit.target = g;
    }
}

static void compositions(
    int at,
    int left,
    std::vector<int>& a,
    const Graph& base,
    U64 base_mask,
    Audit& audit
) {
    const int k = base.n;
    if (at + 1 == k) {
        a[at] = left;
        audit_composition(base, base_mask, a, audit);
        return;
    }
    for (int value = 1; value <= left - (k - at - 1); ++value) {
        a[at] = value;
        compositions(at + 1, left - value, a, base, base_mask, audit);
    }
}

static void print_edges(const Graph& g) {
    std::cout << "p edge " << g.n << " " << edge_count(g) << "\n";
    for (int x = 0; x < g.n; ++x) {
        for (int y = x + 1; y < g.n; ++y) {
            if ((g.adj[x] >> y) & 1U) std::cout << "e " << x << " " << y << "\n";
        }
    }
}

int main(int argc, char** argv) {
    int max_base_n = 6;
    if (argc == 2) max_base_n = std::stoi(argv[1]);
    if (max_base_n < 3 || max_base_n > 6) return 2;

    Audit audit;
    for (int n = 3; n <= max_base_n; ++n) {
        const auto bases = unlabeled_d2c_bases(n);
        std::cout << "BASES n=" << n << " unlabeled_d2c=" << bases.size() << "\n";
        for (U64 mask : bases) {
            const Graph base = graph_from_mask(n, mask);
            std::vector<int> a(n);
            compositions(0, 25, a, base, mask, audit);
        }
    }

    std::cout << "SUMMARY max_base_n=" << max_base_n
              << " compositions=" << audit.compositions
              << " substitutions=" << audit.substitutions
              << " above_current_best_tested=" << audit.threshold_tests
              << " maximum=" << audit.best
              << " best_base_n=" << audit.best_n
              << " best_base_mask=" << audit.best_base
              << " best_types=" << audit.best_types
              << " best_sizes=";
    for (std::size_t i = 0; i < audit.best_sizes.size(); ++i) {
        if (i) std::cout << ",";
        std::cout << audit.best_sizes[i];
    }
    std::cout << "\n";
    if (audit.target.n == 25) {
        std::cout << "RAW_CANDIDATE_BEGIN\n";
        print_edges(audit.target);
        std::cout << "RAW_CANDIDATE_END\n";
        return 1;
    }
    return audit.best == 156 ? 0 : 3;
}
