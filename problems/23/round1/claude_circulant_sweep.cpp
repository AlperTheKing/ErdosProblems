// Exhaustive exact check of bip(G) <= N^2/25 over ALL triangle-free circulant graphs on Z_n,
// for n up to a given bound.  This family is a natural target because it contains
//   * the extremal blow-ups  C5[k] = circulant on Z_{5k} with S = { d : d = +-1 mod 5 },
//   * the cyclic Ramsey graphs (e.g. the unique (3,5)-graph on 13 vertices, S = {1,5}),
// and it reaches orders well beyond the full census.
//
// For each n and each symmetric connection set S subset {1..n/2}: build the circulant,
// reject if it has a triangle, else compute maxcut EXACTLY by Gray-code enumeration of all
// 2^(n-1) bipartitions, and compare 25*bip against n^2.  Exact integers only.
//
// Usage: claude_circulant_sweep.exe NMIN NMAX

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>

static inline int popcnt(uint64_t x) { return __builtin_popcountll(x); }

int main(int argc, char** argv) {
    int nmin = (argc > 1) ? std::atoi(argv[1]) : 5;
    int nmax = (argc > 2) ? std::atoi(argv[2]) : 26;

    long long total_tf = 0;
    for (int n = nmin; n <= nmax; ++n) {
        const int half = n / 2;
        const uint64_t nsets = 1ull << half;   // subsets of {1..half}
        int best_bip = -1;
        uint64_t best_S = 0;
        long long tf_count = 0;
        int violations = 0;

        std::vector<uint64_t> adj(n);
        for (uint64_t mask = 1; mask < nsets; ++mask) {
            // build connection set
            for (int i = 0; i < n; ++i) adj[i] = 0;
            int m = 0;
            for (int d = 1; d <= half; ++d) {
                if (!((mask >> (d - 1)) & 1)) continue;
                for (int v = 0; v < n; ++v) {
                    int w = (v + d) % n;
                    if (w == v) continue;
                    if (!((adj[v] >> w) & 1)) { adj[v] |= 1ull << w; adj[w] |= 1ull << v; ++m; }
                }
            }
            if (m == 0) continue;
            // triangle test
            bool tri = false;
            for (int v = 0; v < n && !tri; ++v)
                for (int w = v + 1; w < n && !tri; ++w)
                    if ((adj[v] >> w) & 1 && (adj[v] & adj[w])) tri = true;
            if (tri) continue;
            ++tf_count;

            // exact maxcut, vertex 0 fixed
            int deg0 = popcnt(adj[0]);
            uint64_t S = 1ull;
            int cut = deg0, best_cut = cut;
            const uint64_t steps = 1ull << (n - 1);
            for (uint64_t k = 1; k < steps; ++k) {
                int v = __builtin_ctzll(k) + 1;
                uint64_t bit = 1ull << v;
                int a = popcnt(adj[v] & S);
                int dv = popcnt(adj[v]);
                if (S & bit) { cut += 2 * a - dv; S &= ~bit; }
                else         { cut += dv - 2 * a; S |= bit; }
                if (cut > best_cut) best_cut = cut;
            }
            int bip = m - best_cut;
            if (25LL * bip > 1LL * n * n) {
                ++violations;
                std::printf("*** VIOLATION n=%d S=0x%llx m=%d maxcut=%d bip=%d  25*bip=%lld > n^2=%d\n",
                            n, (unsigned long long)mask, m, best_cut, bip, 25LL * bip, n * n);
            }
            if (bip > best_bip) { best_bip = bip; best_S = mask; }
        }
        total_tf += tf_count;
        // print the best connection set in readable form
        std::printf("n=%2d  triangle-free circulants=%6lld  max bip=%3d  bound n^2/25=%7.2f  "
                    "floor=%3d  violations=%d   best S={",
                    n, tf_count, best_bip, n * n / 25.0, (n * n) / 25, violations);
        bool first = true;
        for (int d = 1; d <= half; ++d)
            if ((best_S >> (d - 1)) & 1) { std::printf("%s%d", first ? "" : ",", d); first = false; }
        std::printf("}\n");
        std::fflush(stdout);
    }
    std::printf("TOTAL triangle-free circulants scanned: %lld\n", total_tf);
    return 0;
}
