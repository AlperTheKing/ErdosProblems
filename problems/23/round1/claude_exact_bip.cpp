// Exact a(N) = max bip(G) over connected triangle-free graphs on N vertices.
// Reads graph6 lines on stdin (from nauty geng -t -c N [res/mod]).
// bip(G) = |E| - maxcut(G); maxcut by exhaustive Gray-code enumeration of all
// 2^(N-1) cuts (vertex 0 fixed on one side). Exact integers only.
//
// Restricting to CONNECTED graphs is sound for the conjecture: for a graph with
// components of orders N_i, bip = sum bip_i and sum N_i^2 <= (sum N_i)^2, so the
// bound for all components implies it for the graph.
//
// Usage:  geng -t -c 12 0/16 | claude_exact_bip.exe 12
// Output: one line per record-setting graph, then a final summary line.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <iostream>

static inline int popcnt(uint32_t x) { return __builtin_popcount(x); }

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s N\n", argv[0]); return 2; }
    const int n = std::atoi(argv[1]);
    if (n < 1 || n > 30) { std::fprintf(stderr, "N out of range\n"); return 2; }

    uint32_t adj[32];
    int deg[32];

    long long best_bip = -1;
    std::string best_g6;
    long long count = 0;
    long long best_count = 0;   // how many graphs attain best_bip

    std::string line;
    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        const char* p = line.c_str();
        // graph6 header: n <= 62 encoded as single byte n+63
        int gn = (int)p[0] - 63;
        if (gn != n) { std::fprintf(stderr, "order mismatch %d != %d\n", gn, n); return 3; }
        ++p;
        for (int i = 0; i < n; ++i) { adj[i] = 0; deg[i] = 0; }
        int m = 0;
        int bitpos = 0;
        int cur = 0, nbits = 0;
        for (int j = 1; j < n; ++j) {
            for (int i = 0; i < j; ++i) {
                if (nbits == 0) { cur = (int)(*p++) - 63; nbits = 6; }
                int bit = (cur >> (nbits - 1)) & 1;
                --nbits;
                if (bit) {
                    adj[i] |= (1u << j);
                    adj[j] |= (1u << i);
                    ++deg[i]; ++deg[j];
                    ++m;
                }
                ++bitpos;
            }
        }
        (void)bitpos;

        // exhaustive maxcut: vertex 0 fixed in S
        uint32_t S = 1u;                 // {0}
        int cut = deg[0];
        int best_cut = cut;
        const uint64_t steps = 1ull << (n - 1);
        for (uint64_t k = 1; k < steps; ++k) {
            int v = __builtin_ctzll(k) + 1;         // vertex to flip, in 1..n-1
            uint32_t bit = 1u << v;
            int a = popcnt(adj[v] & S);
            if (S & bit) { cut += 2 * a - deg[v]; S &= ~bit; }
            else         { cut += deg[v] - 2 * a; S |= bit; }
            if (cut > best_cut) best_cut = cut;
        }

        long long bip = (long long)m - best_cut;
        ++count;
        if (bip > best_bip) {
            best_bip = bip;
            best_g6 = line;
            best_count = 1;
            std::printf("NEW n=%d bip=%lld m=%d maxcut=%d g6=%s\n", n, bip, m, best_cut, line.c_str());
            std::fflush(stdout);
        } else if (bip == best_bip) {
            ++best_count;
        }
    }
    std::printf("SUMMARY n=%d graphs=%lld a_N=%lld attained_by=%lld example=%s\n",
                n, count, best_bip, best_count, best_g6.c_str());
    return 0;
}
