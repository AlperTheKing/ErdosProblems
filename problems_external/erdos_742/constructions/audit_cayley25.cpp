#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

using U32 = std::uint32_t;

struct Graph {
    std::array<U32, 25> adj{};
};

static int edge_count(const Graph& g) {
    int twice = 0;
    for (U32 row : g.adj) twice += std::popcount(row);
    return twice / 2;
}

static bool diameter_two(const Graph& g) {
    constexpr U32 all = (U32{1} << 25) - 1;
    bool has_nonedge = false;
    for (int v = 0; v < 25; ++v) {
        U32 reached = g.adj[v] | (U32{1} << v);
        U32 first = g.adj[v];
        while (first) {
            const int u = std::countr_zero(first);
            first &= first - 1;
            reached |= g.adj[u];
        }
        if (reached != all) return false;
        has_nonedge |= reached != (g.adj[v] | (U32{1} << v));
    }
    // The equality above is tautological after reachability expansion; test
    // non-completeness separately.
    has_nonedge = false;
    for (int v = 0; v < 25; ++v) {
        if (std::popcount(g.adj[v]) < 24) has_nonedge = true;
    }
    return has_nonedge;
}

static bool d2c(const Graph& g) {
    if (!diameter_two(g)) return false;
    constexpr U32 all = (U32{1} << 25) - 1;
    for (int x = 0; x < 25; ++x) {
        U32 ys = g.adj[x] & ~((U32{1} << (x + 1)) - 1);
        while (ys) {
            const int y = std::countr_zero(ys);
            ys &= ys - 1;
            Graph h = g;
            h.adj[x] &= ~(U32{1} << y);
            h.adj[y] &= ~(U32{1} << x);
            bool witnessed = false;
            for (int v = 0; v < 25 && !witnessed; ++v) {
                U32 reached = h.adj[v] | (U32{1} << v);
                U32 first = h.adj[v];
                while (first) {
                    const int u = std::countr_zero(first);
                    first &= first - 1;
                    reached |= h.adj[u];
                }
                witnessed = reached != all;
            }
            if (!witnessed) return false;
        }
    }
    return true;
}

static Graph cayley_c25(std::uint16_t mask) {
    Graph g;
    for (int x = 0; x < 25; ++x) {
        for (int d = 1; d <= 12; ++d) {
            if (((mask >> (d - 1)) & 1U) == 0) continue;
            const int y = (x + d) % 25;
            const int z = (x + 25 - d) % 25;
            g.adj[x] |= U32{1} << y;
            g.adj[x] |= U32{1} << z;
        }
    }
    return g;
}

static int code(int a, int b) {
    return 5 * a + b;
}

static std::vector<std::pair<int, int>> inverse_pairs_c5x5() {
    std::vector<std::pair<int, int>> reps;
    std::array<bool, 25> used{};
    used[0] = true;
    for (int a = 0; a < 5; ++a) {
        for (int b = 0; b < 5; ++b) {
            const int u = code(a, b);
            if (used[u]) continue;
            const int v = code((5 - a) % 5, (5 - b) % 5);
            reps.push_back({u, v});
            used[u] = used[v] = true;
        }
    }
    return reps;
}

static Graph cayley_c5x5(std::uint16_t mask) {
    static const auto pairs = inverse_pairs_c5x5();
    Graph g;
    for (int a = 0; a < 5; ++a) {
        for (int b = 0; b < 5; ++b) {
            const int x = code(a, b);
            for (int i = 0; i < 12; ++i) {
                if (((mask >> i) & 1U) == 0) continue;
                for (int delta : {pairs[i].first, pairs[i].second}) {
                    const int da = delta / 5;
                    const int db = delta % 5;
                    const int y = code((a + da) % 5, (b + db) % 5);
                    g.adj[x] |= U32{1} << y;
                }
            }
        }
    }
    return g;
}

static void print_edges(const Graph& g) {
    const int m = edge_count(g);
    std::cout << "p edge 25 " << m << "\n";
    for (int x = 0; x < 25; ++x) {
        for (int y = x + 1; y < 25; ++y) {
            if ((g.adj[x] >> y) & 1U) std::cout << "e " << x << " " << y << "\n";
        }
    }
}

template<class Builder>
static void audit(const std::string& name, Builder build) {
    int d2c_count = 0;
    int best_edges = -1;
    std::uint16_t best_mask = 0;
    Graph best;
    for (std::uint16_t mask = 0; mask < 4096; ++mask) {
        const Graph g = build(mask);
        if (!d2c(g)) continue;
        ++d2c_count;
        const int m = edge_count(g);
        if (m > best_edges) {
            best_edges = m;
            best_mask = mask;
            best = g;
        }
    }
    std::cout << "FAMILY " << name << " total=4096 d2c=" << d2c_count
              << " maximum=" << best_edges << " mask=" << best_mask << "\n";
    if (best_edges >= 157) {
        std::cout << "RAW_CANDIDATE_BEGIN " << name << "\n";
        print_edges(best);
        std::cout << "RAW_CANDIDATE_END " << name << "\n";
    }
}

int main() {
    if (inverse_pairs_c5x5().size() != 12) return 2;
    audit("C25", cayley_c25);
    audit("C5xC5", cayley_c5x5);
}
