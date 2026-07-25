// Collect EVERY connected triangle-free graph on N vertices with bip(G) >= T.
// Usage:  geng -t -c -q N [res/mod] | claude_collect_extremal.exe N T
// Prints one "HIT" line per graph; exact integers throughout.

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <iostream>

static inline int popcnt(uint32_t x) { return __builtin_popcount(x); }

int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: %s N T\n", argv[0]); return 2; }
    const int n = std::atoi(argv[1]);
    const int T = std::atoi(argv[2]);

    uint32_t adj[32];
    int deg[32];
    long long count = 0, hits = 0;
    std::string line;
    std::ios::sync_with_stdio(false);

    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        const char* p = line.c_str();
        if ((int)p[0] - 63 != n) { std::fprintf(stderr, "order mismatch\n"); return 3; }
        ++p;
        for (int i = 0; i < n; ++i) { adj[i] = 0; deg[i] = 0; }
        int m = 0, cur = 0, nbits = 0;
        for (int j = 1; j < n; ++j)
            for (int i = 0; i < j; ++i) {
                if (nbits == 0) { cur = (int)(*p++) - 63; nbits = 6; }
                int bit = (cur >> (nbits - 1)) & 1; --nbits;
                if (bit) { adj[i] |= 1u << j; adj[j] |= 1u << i; ++deg[i]; ++deg[j]; ++m; }
            }
        uint32_t S = 1u;
        int cut = deg[0], best_cut = cut;
        const uint64_t steps = 1ull << (n - 1);
        for (uint64_t k = 1; k < steps; ++k) {
            int v = __builtin_ctzll(k) + 1;
            uint32_t bit = 1u << v;
            int a = popcnt(adj[v] & S);
            if (S & bit) { cut += 2 * a - deg[v]; S &= ~bit; }
            else         { cut += deg[v] - 2 * a; S |= bit; }
            if (cut > best_cut) best_cut = cut;
        }
        ++count;
        int bip = m - best_cut;
        if (bip >= T) {
            ++hits;
            std::printf("HIT bip=%d m=%d maxcut=%d g6=%s\n", bip, m, best_cut, line.c_str());
        }
    }
    std::fprintf(stderr, "scanned=%lld hits=%lld\n", count, hits);
    return 0;
}
