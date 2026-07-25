// Counterexample hunt for Erdos #23: search triangle-free graphs on N vertices maximising
// bip(G) = |E| - maxcut(G), targeting the orders where the conjecture has the LEAST slack.
//
// Slack analysis: if a(N) = floor(N^2/25) (exactly true for every 4 <= N <= 14 except N = 9),
// the surviving slack is frac(N^2/25), which equals 0.04 exactly when N = +-1 (mod 25):
// N = 24, 26, 49, 51, 74, 76, 99, 101, ...  At those orders a single extra unit of bip refutes
// the conjecture.  Published verification covers only N = 5n, so these orders are unchecked.
//
// Method: simulated annealing over triangle-free graphs. Objective = exact bip, computed by
// Gray-code enumeration of all 2^(N-1) cuts (N <= 26 => at most 33.5M steps, ~30ms).
// Moves: add a random non-edge that keeps the graph triangle-free; delete a random edge;
// swap (delete one, add one). Any state with 25*bip > N^2 is printed immediately as a
// candidate counterexample and must then be re-verified independently.
//
// Usage: claude_hunt.exe N seed iters [target]

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <random>
#include <algorithm>

static inline int popcnt(uint64_t x) { return __builtin_popcountll(x); }

struct G {
    int n;
    std::vector<uint64_t> adj;
    int m = 0;
    explicit G(int n_) : n(n_), adj(n_, 0) {}
    bool has(int u, int v) const { return (adj[u] >> v) & 1; }
    // adding uv keeps triangle-free iff u,v have no common neighbour
    bool can_add(int u, int v) const { return u != v && !has(u, v) && (adj[u] & adj[v]) == 0; }
    void add(int u, int v) { adj[u] |= 1ull << v; adj[v] |= 1ull << u; ++m; }
    void del(int u, int v) { adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); --m; }
};

static int maxcut_exact(const G& g) {
    const int n = g.n;
    std::vector<int> deg(n);
    for (int i = 0; i < n; ++i) deg[i] = popcnt(g.adj[i]);
    uint64_t S = 1ull;
    int cut = deg[0], best = cut;
    const uint64_t steps = 1ull << (n - 1);
    for (uint64_t k = 1; k < steps; ++k) {
        int v = __builtin_ctzll(k) + 1;
        uint64_t bit = 1ull << v;
        int a = popcnt(g.adj[v] & S);
        if (S & bit) { cut += 2 * a - deg[v]; S &= ~bit; }
        else         { cut += deg[v] - 2 * a; S |= bit; }
        if (cut > best) best = cut;
    }
    return best;
}

static int bip(const G& g) { return g.m - maxcut_exact(g); }

static void print_g6(const G& g) {
    // graph6 for n <= 62
    std::string out;
    out += char(g.n + 63);
    int cur = 0, nb = 0;
    for (int j = 1; j < g.n; ++j)
        for (int i = 0; i < j; ++i) {
            cur = (cur << 1) | (g.has(i, j) ? 1 : 0);
            if (++nb == 6) { out += char(cur + 63); cur = 0; nb = 0; }
        }
    if (nb) { cur <<= (6 - nb); out += char(cur + 63); }
    std::printf("%s", out.c_str());
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s N seed iters [target]\n", argv[0]); return 2; }
    const int n = std::atoi(argv[1]);
    const uint64_t seed = std::strtoull(argv[2], nullptr, 10);
    const long long iters = std::atoll(argv[3]);
    const long long need = (argc > 4) ? std::atoll(argv[4]) : ((1LL * n * n) / 25 + 1);

    std::mt19937_64 rng(seed);
    std::uniform_int_distribution<int> V(0, n - 1);
    std::uniform_real_distribution<double> U(0.0, 1.0);

    // random maximal triangle-free start
    G g(n);
    {
        std::vector<std::pair<int,int>> pairs;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) pairs.push_back({i, j});
        std::shuffle(pairs.begin(), pairs.end(), rng);
        for (auto& p : pairs) if (g.can_add(p.first, p.second)) g.add(p.first, p.second);
    }

    int cur = bip(g);
    int best = cur;
    G bestg = g;

    double T0 = 1.5, T1 = 0.02;
    for (long long it = 0; it < iters; ++it) {
        double T = T0 * std::pow(T1 / T0, double(it) / double(iters));
        G cand = g;
        double r = U(rng);
        if (r < 0.40) {                      // try to add
            for (int t = 0; t < 60; ++t) {
                int u = V(rng), v = V(rng);
                if (cand.can_add(u, v)) { cand.add(u, v); break; }
            }
        } else if (r < 0.70) {               // delete a random edge
            std::vector<std::pair<int,int>> es;
            for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (cand.has(i, j)) es.push_back({i, j});
            if (es.empty()) continue;
            auto e = es[rng() % es.size()];
            cand.del(e.first, e.second);
        } else {                             // swap
            std::vector<std::pair<int,int>> es;
            for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (cand.has(i, j)) es.push_back({i, j});
            if (es.empty()) continue;
            auto e = es[rng() % es.size()];
            cand.del(e.first, e.second);
            for (int t = 0; t < 60; ++t) {
                int u = V(rng), v = V(rng);
                if (cand.can_add(u, v)) { cand.add(u, v); break; }
            }
        }
        if (cand.m == g.m && cand.adj == g.adj) continue;

        int cb = bip(cand);
        int d = cb - cur;
        if (d >= 0 || U(rng) < std::exp(d / T)) { g = cand; cur = cb; }

        if (cb > best) {
            best = cb;
            bestg = cand;
            std::printf("n=%d it=%lld bip=%d m=%d  25*bip=%d vs N^2=%d  g6=", n, it, cb, cand.m, 25 * cb, n * n);
            print_g6(cand);
            std::printf("\n");
            std::fflush(stdout);
            if (25LL * cb > 1LL * n * n) {
                std::printf("*** CANDIDATE COUNTEREXAMPLE *** n=%d bip=%d  25*bip=%lld > %d  g6=",
                            n, cb, 25LL * cb, n * n);
                print_g6(cand);
                std::printf("\n");
                std::fflush(stdout);
            }
        }
    }
    std::printf("FINAL n=%d best_bip=%d need=%lld bound=%.2f g6=", n, best, need, n * n / 25.0);
    print_g6(bestg);
    std::printf("\n");
    return 0;
}
