// Round-2 / G1 core: the Andrasfai family And(k) against the 1/25 ceiling.
//
// And(k) = circulant on Z_{3k-1} with connection set {k,...,2k-1}: k-regular, triangle-free,
// vertex-transitive, n = 3k-1.  And(2) = C5 (the extremal graph); And(3) is the Wagner graph
// C_8(1,4) (multiply the connection set by 3 mod 8).
//
// By the blow-up identity, if G -> H then bip(G)/N^2 <= max_x psi(H,x) where
// psi(H,x) = min over cuts S of sum_{uv monochromatic} x_u x_v on the simplex.  Chen-Jin-Koh put
// every triangle-free graph with delta > N/3 either into a finite Andrasfai-type family or
// containing a Grotzsch graph, so this computation is the core of that route.
//
// Reports, per k: exact bip by exhaustive maximum cut (so the uniform value bip/n^2 is exact), and
// a multi-start hill-climb maximum of psi over the simplex, which is a LOWER bound only.

#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <random>
#include <algorithm>

static inline int popc(uint64_t x) { return __builtin_popcountll(x); }

int main(int argc, char** argv) {
    int kmin = (argc > 1) ? atoi(argv[1]) : 2;
    int kmax = (argc > 2) ? atoi(argv[2]) : 8;

    std::printf("%2s %3s %4s %9s %12s %22s %22s %8s\n",
                "k", "n", "|E|", "tri-free", "bip(exact)", "uniform bip/n^2", "max_x psi (lower)", "vs 1/25");
    for (int k = kmin; k <= kmax; ++k) {
        int n = 3 * k - 1;
        if (n > 26) break;
        std::vector<uint64_t> adj(n, 0);
        for (int v = 0; v < n; ++v)
            for (int d = k; d < 2 * k; ++d) {
                int w = ((v + d) % n + n) % n;
                if (w != v) { adj[v] |= 1ull << w; adj[w] |= 1ull << v; }
            }
        std::vector<std::pair<int,int>> E;
        for (int u = 0; u < n; ++u)
            for (int v = u + 1; v < n; ++v)
                if ((adj[u] >> v) & 1) E.push_back({u, v});
        bool tf = true;
        for (auto& e : E) if (adj[e.first] & adj[e.second]) tf = false;

        // exhaustive maximum cut
        std::vector<int> deg(n);
        for (int i = 0; i < n; ++i) deg[i] = popc(adj[i]);
        uint64_t S = 1ull; int cut = deg[0], best = cut;
        const uint64_t steps = 1ull << (n - 1);
        for (uint64_t m = 1; m < steps; ++m) {
            int v = __builtin_ctzll(m) + 1;
            uint64_t bit = 1ull << v;
            int a = popc(adj[v] & S);
            if (S & bit) { cut += 2 * a - deg[v]; S &= ~bit; }
            else         { cut += deg[v] - 2 * a; S |= bit; }
            if (cut > best) best = cut;
        }
        int bip = (int)E.size() - best;

        // hill-climb max of psi over the simplex
        std::mt19937_64 rng(4242 + k);
        std::uniform_real_distribution<double> U(0.0, 1.0);
        std::uniform_int_distribution<int> V(0, n - 1);
        auto psi = [&](const std::vector<double>& x) {
            double bestv = 1e18;
            for (uint64_t m = 0; m < steps; ++m) {
                uint64_t Sm = (m << 1) | 1;
                double t = 0;
                for (auto& e : E)
                    if (((Sm >> e.first) & 1) == ((Sm >> e.second) & 1)) t += x[e.first] * x[e.second];
                if (t < bestv) bestv = t;
                if (bestv == 0) break;
            }
            return bestv;
        };
        double bv = -1;
        int restarts = (n <= 14) ? 20 : 6;
        int iters    = (n <= 14) ? 2500 : 700;
        for (int r = 0; r < restarts; ++r) {
            std::vector<double> x(n);
            double s = 0;
            for (int i = 0; i < n; ++i) { x[i] = U(rng) + 1e-3; s += x[i]; }
            for (int i = 0; i < n; ++i) x[i] /= s;
            double cur = psi(x), step = 0.10;
            for (int it = 0; it < iters; ++it) {
                int i = V(rng), j = V(rng);
                if (i == j) continue;
                double d = step * U(rng) * x[i];
                if (x[i] - d <= 0) continue;
                std::vector<double> y = x;
                y[i] -= d; y[j] += d;
                double v2 = psi(y);
                if (v2 > cur) { x = y; cur = v2; }
                if (it % 500 == 499) step *= 0.7;
            }
            if (cur > bv) bv = cur;
        }
        double unif = (double)bip / ((double)n * n);
        const char* verdict = (bv > 0.04 + 1e-9) ? "ABOVE" : ((bv > 0.04 - 1e-9) ? "EQUAL" : "below");
        std::printf("%2d %3d %4zu %9s %12d %22.6f %22.6f %8s\n",
                    k, n, E.size(), tf ? "true" : "FALSE", bip, unif, bv, verdict);
        std::fflush(stdout);
    }
    return 0;
}
