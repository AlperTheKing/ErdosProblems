// H3 (Ramsey-critical family) exact engine for Erdos #23.
//
// bip(G) = |E(G)| - maxcut(G).  maxcut is computed EXACTLY by Gray-code
// enumeration of all 2^(n-1) bipartitions (vertex 0 fixed).  alpha(G) is the
// exact independence number by branch and bound on bitmasks.  Triangle-freeness
// is re-checked explicitly on every graph.  Integer arithmetic only.
//
// Modes:
//   census   : stdin graph6 lines -> table  alpha -> (max bip, argmax g6, count)
//   eval     : stdin graph6 lines -> per-line "g6 n m maxcut bip alpha tf"
//
// Build: clang++ -O3 -march=native -std=c++17 h3_engine.cpp -o h3_engine.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <iostream>
#include <vector>
#include <algorithm>

static int N;
static uint64_t adj[64];
static int deg[64];

static inline int pc(uint64_t x) { return __builtin_popcountll(x); }

// ---------- graph6 decode ----------
static bool decode_g6(const char* p, int& n, uint64_t* a, int& m) {
    n = (int)p[0] - 63;
    if (n < 1 || n > 62) return false;
    ++p;
    for (int i = 0; i < n; ++i) a[i] = 0;
    m = 0;
    int cur = 0, nbits = 0;
    for (int j = 1; j < n; ++j) {
        for (int i = 0; i < j; ++i) {
            if (nbits == 0) { if (!*p) return false; cur = (int)(*p++) - 63; nbits = 6; }
            int bit = (cur >> (nbits - 1)) & 1;
            --nbits;
            if (bit) { a[i] |= (1ull << j); a[j] |= (1ull << i); ++m; }
        }
    }
    return true;
}

// ---------- exact maxcut, Gray code over 2^(n-1) ----------
static long long maxcut_exact(int n, const uint64_t* a, const int* d) {
    if (n <= 1) return 0;
    uint64_t S = 0;              // side-1 set; vertex 0 always outside S
    long long cut = 0, best = 0;
    const uint64_t total = 1ull << (n - 1);
    for (uint64_t i = 1; i < total; ++i) {
        int v = __builtin_ctzll(i) + 1;      // vertex to flip (1..n-1)
        uint64_t bit = 1ull << v;
        int inter = pc(a[v] & S);
        if (S & bit) { cut -= d[v] - 2 * (inter - 0); S &= ~bit; }
        else        { cut += d[v] - 2 * inter;      S |= bit; }
        if (cut > best) best = cut;
    }
    return best;
}

// ---------- exact independence number ----------
static int alpha_best;
static void mis(uint64_t P, int sz) {
    if (sz + pc(P) <= alpha_best) return;
    if (!P) { if (sz > alpha_best) alpha_best = sz; return; }
    // pivot: vertex of maximum degree inside P
    int bestv = -1, bestd = -1;
    uint64_t Q = P;
    while (Q) {
        int v = __builtin_ctzll(Q); Q &= Q - 1;
        int dv = pc(adj[v] & P);
        if (dv > bestd) { bestd = dv; bestv = v; }
    }
    uint64_t vb = 1ull << bestv;
    mis(P & ~(adj[bestv] | vb), sz + 1);   // include pivot
    mis(P & ~vb, sz);                      // exclude pivot
}
static int alpha_exact(int n) {
    alpha_best = 0;
    uint64_t all = (n == 64) ? ~0ull : ((1ull << n) - 1);
    mis(all, 0);
    return alpha_best;
}

static bool triangle_free(int n, const uint64_t* a) {
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if (a[i] & (1ull << j))
                if (a[i] & a[j]) return false;
    return true;
}

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s census|eval\n", argv[0]); return 2; }
    const bool census = (std::strcmp(argv[1], "census") == 0);
    std::ios::sync_with_stdio(false);

    long long maxbip[64]; std::string arg[64]; long long cnt[64];
    for (int i = 0; i < 64; ++i) { maxbip[i] = -1; cnt[i] = 0; }
    long long total = 0;

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        int n, m;
        if (!decode_g6(line.c_str(), n, adj, m)) { std::fprintf(stderr, "bad g6: %s\n", line.c_str()); return 3; }
        N = n;
        for (int i = 0; i < n; ++i) deg[i] = pc(adj[i]);
        bool tf = triangle_free(n, adj);
        long long mc = maxcut_exact(n, adj, deg);
        long long bip = (long long)m - mc;
        int al = alpha_exact(n);
        ++total;
        if (census) {
            if (!tf) continue;
            if (bip > maxbip[al]) { maxbip[al] = bip; arg[al] = line; cnt[al] = 1; }
            else if (bip == maxbip[al]) ++cnt[al];
        } else {
            std::printf("%s n=%d m=%d maxcut=%lld bip=%lld alpha=%d tf=%d 25bip=%lld n2=%d %s\n",
                        line.c_str(), n, m, mc, bip, al, (int)tf, 25 * bip, n * n,
                        (25 * bip > (long long)n * n) ? "VIOLATION" : "ok");
            std::fflush(stdout);
        }
    }
    if (census) {
        std::printf("# total graphs read: %lld\n", total);
        std::printf("# alpha  maxbip  count  argmax_g6\n");
        for (int a = 0; a < 64; ++a)
            if (maxbip[a] >= 0)
                std::printf("%d %lld %lld %s\n", a, maxbip[a], cnt[a], arg[a].c_str());
    }
    return 0;
}
