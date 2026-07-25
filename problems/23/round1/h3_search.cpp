// H3 max-bip search with EXACT verification (Erdos #23 counterexample hunt).
//
// bip(G) = |E| - maxcut(G) = min over bipartitions of the number of monochromatic edges.
// The search maximises  min_{mask in POOL} mono(mask)  over triangle-free G, where POOL is a
// bounded set of the currently tightest bipartitions.  Whenever every pooled cut leaves >= t
// monochromatic edges, a FULL exact Gray-code enumeration of all 2^(n-1) bipartitions is run:
// either it confirms bip >= t (reported, and t is raised), or it returns the true maximum cut
// and the pool is rebuilt from the tightest cuts of that enumeration.  Every reported value is
// therefore certified by exhaustive enumeration, never by the pool.
//
// Build: clang++ -O3 -march=native -std=c++17 h3_search.cpp -o h3_search.exe
// Usage: h3_search.exe N T SEED SECONDS [POOL] [ALPHAMAX] [seedg6]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <iostream>

static int N, T, POOL = 4096, ALPHAMAX = 99;
static uint64_t adj[32];
static int deg[32];
static int M;

static inline int pc(uint64_t x) { return __builtin_popcountll(x); }

static std::string g6enc(int n, const uint64_t* a) {
    std::string s(1, (char)(n + 63));
    int cur = 0, nb = 0;
    for (int j = 1; j < n; ++j)
        for (int i = 0; i < j; ++i) {
            cur = (cur << 1) | (int)((a[i] >> j) & 1ull);
            if (++nb == 6) { s += (char)(cur + 63); cur = 0; nb = 0; }
        }
    if (nb) { cur <<= (6 - nb); s += (char)(cur + 63); }
    return s;
}

static bool decode_g6(const char* p, int& n, uint64_t* a, int& m) {
    n = (int)p[0] - 63; if (n < 1 || n > 62) return false; ++p;
    for (int i = 0; i < n; ++i) a[i] = 0;
    m = 0; int cur = 0, nbits = 0;
    for (int j = 1; j < n; ++j) for (int i = 0; i < j; ++i) {
        if (nbits == 0) { if (!*p) return false; cur = (int)(*p++) - 63; nbits = 6; }
        int bit = (cur >> (nbits - 1)) & 1; --nbits;
        if (bit) { a[i] |= 1ull << j; a[j] |= 1ull << i; ++m; }
    }
    return true;
}

// exact independence number
static int abest;
static void mis(uint64_t P, int sz, int cap) {
    if (abest >= cap) return;                 // early exit: only need to know alpha >= cap
    if (sz + pc(P) <= abest) return;
    if (!P) { if (sz > abest) abest = sz; return; }
    int bv = -1, bd = -1; uint64_t Q = P;
    while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; int d = pc(adj[v] & P); if (d > bd) { bd = d; bv = v; } }
    uint64_t vb = 1ull << bv;
    mis(P & ~(adj[bv] | vb), sz + 1, cap);
    mis(P & ~vb, sz, cap);
}
static int alpha_cap(int n, int cap) {           // returns alpha, or >=cap if it exceeds cap
    abest = 0; mis((1ull << n) - 1, 0, cap); return abest;
}

// full exact maxcut; also collects the K tightest cuts (largest cut values)
struct FullResult { long long maxcut; std::vector<uint32_t> tight; };
static FullResult full_exact(int n, int K) {
    uint32_t S = 0; long long cut = 0, best = 0;
    const uint64_t total = 1ull << (n - 1);
    // first pass: find maxcut
    for (uint64_t i = 1; i < total; ++i) {
        int v = __builtin_ctzll(i) + 1; uint32_t bit = 1u << v;
        int inter = pc(adj[v] & (uint64_t)S);
        if (S & bit) { cut -= deg[v] - 2 * inter; S &= ~bit; }
        else         { cut += deg[v] - 2 * inter; S |= bit; }
        if (cut > best) best = cut;
    }
    // second pass: collect masks with cut >= best - slack (i.e. mono <= M-best+slack)
    std::vector<uint32_t> tight; tight.reserve(K);
    int slack = 0;
    while ((int)tight.size() < K && slack <= 12) {
        tight.clear();
        S = 0; cut = 0;
        if (cut >= best - slack) tight.push_back(0);
        for (uint64_t i = 1; i < total && (int)tight.size() < K; ++i) {
            int v = __builtin_ctzll(i) + 1; uint32_t bit = 1u << v;
            int inter = pc(adj[v] & (uint64_t)S);
            if (S & bit) { cut -= deg[v] - 2 * inter; S &= ~bit; }
            else         { cut += deg[v] - 2 * inter; S |= bit; }
            if (cut >= best - slack) tight.push_back(S);
        }
        ++slack;
    }
    return { best, tight };
}

static inline int mono_of(uint32_t mask, int n) {
    uint64_t A = mask, B = (~(uint64_t)mask) & ((1ull << n) - 1);
    int s = 0;
    uint64_t Q = A; while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; s += pc(adj[v] & A); }
    Q = B;          while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; s += pc(adj[v] & B); }
    return s / 2;
}

int main(int argc, char** argv) {
    if (argc < 5) { std::fprintf(stderr, "usage: %s N T SEED SECONDS [POOL] [ALPHAMAX] [seedg6]\n", argv[0]); return 2; }
    N = atoi(argv[1]); T = atoi(argv[2]);
    uint64_t seed = strtoull(argv[3], nullptr, 10);
    double secs = atof(argv[4]);
    if (argc > 5) POOL = atoi(argv[5]);
    if (argc > 6) ALPHAMAX = atoi(argv[6]);

    std::mt19937_64 rng(seed);
    for (int i = 0; i < N; ++i) adj[i] = 0;
    M = 0;
    if (argc > 7) {
        int n2, m2; if (!decode_g6(argv[7], n2, adj, m2) || n2 != N) { std::fprintf(stderr, "bad seed g6\n"); return 3; }
        M = m2;
    } else {
        // random triangle-free start: random order of pairs, add when triangle-free
        std::vector<std::pair<int,int>> pr;
        for (int i = 0; i < N; ++i) for (int j = i + 1; j < N; ++j) pr.push_back({i, j});
        std::shuffle(pr.begin(), pr.end(), rng);
        for (auto& e : pr) if (!(adj[e.first] & adj[e.second])) { adj[e.first] |= 1ull << e.second; adj[e.second] |= 1ull << e.first; ++M; }
    }
    for (int i = 0; i < N; ++i) deg[i] = pc(adj[i]);

    FullResult fr = full_exact(N, POOL);
    long long bestbip = (long long)M - fr.maxcut;
    std::string bestg6 = g6enc(N, adj);
    int bestalpha = alpha_cap(N, 99);
    std::vector<uint32_t> pool = fr.tight;
    std::vector<int> mono(pool.size());
    for (size_t i = 0; i < pool.size(); ++i) mono[i] = mono_of(pool[i], N);

    long long penalty = 0;
    for (size_t i = 0; i < pool.size(); ++i) penalty += std::max(0, T - mono[i]);

    auto t0 = std::chrono::steady_clock::now();
    double temp = 2.0;
    long long iters = 0, fullchecks = 0;
    std::vector<int> tmpmono(pool.size());

    while (true) {
        if ((iters & 0xFFF) == 0) {
            double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            if (el > secs) break;
            temp = 2.0 * (1.0 - el / secs) + 0.05;
        }
        ++iters;
        int u = (int)(rng() % N), v = (int)(rng() % N);
        if (u == v) continue;
        if (u > v) std::swap(u, v);
        bool present = (adj[u] >> v) & 1ull;
        int d;
        if (present) d = -1;
        else { if (adj[u] & adj[v]) continue; d = +1; }

        // delta on pool penalty
        long long dpen = 0;
        const uint32_t* pm = pool.data();
        for (size_t i = 0, sz = pool.size(); i < sz; ++i) {
            uint32_t msk = pm[i];
            if ((((msk >> u) ^ (msk >> v)) & 1u) == 0u) {
                int nm = mono[i] + d;
                dpen += std::max(0, T - nm) - std::max(0, T - mono[i]);
            }
        }
        bool accept = (dpen <= 0);
        if (!accept) {
            double p = std::exp(-(double)dpen / temp);
            accept = (std::generate_canonical<double, 24>(rng) < p);
        }
        if (!accept) continue;

        // apply
        if (present) { adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); --deg[u]; --deg[v]; --M; }
        else         { adj[u] |= 1ull << v;  adj[v] |= 1ull << u;  ++deg[u]; ++deg[v]; ++M; }
        for (size_t i = 0, sz = pool.size(); i < sz; ++i) {
            uint32_t msk = pool[i];
            if ((((msk >> u) ^ (msk >> v)) & 1u) == 0u) mono[i] += d;
        }
        penalty += dpen;

        if (penalty == 0) {
            if (ALPHAMAX < 99) { int al = alpha_cap(N, ALPHAMAX + 1); if (al > ALPHAMAX) { continue; } }
            ++fullchecks;
            FullResult f2 = full_exact(N, POOL);
            long long bip = (long long)M - f2.maxcut;
            if (bip > bestbip) {
                bestbip = bip; bestg6 = g6enc(N, adj); bestalpha = alpha_cap(N, 99);
                std::printf("NEW n=%d m=%d maxcut=%lld bip=%lld alpha=%d 25bip=%lld n2=%d %s g6=%s\n",
                            N, M, f2.maxcut, bip, bestalpha, 25 * bip, N * N,
                            (25 * bip > (long long)N * N) ? "*** VIOLATION ***" : "ok", bestg6.c_str());
                std::fflush(stdout);
            }
            if (bip >= T) { T = (int)bip + 1; }
            pool = f2.tight;
            mono.assign(pool.size(), 0);
            for (size_t i = 0; i < pool.size(); ++i) mono[i] = mono_of(pool[i], N);
            penalty = 0;
            for (size_t i = 0; i < pool.size(); ++i) penalty += std::max(0, T - mono[i]);
        }
    }
    std::printf("DONE n=%d seed=%llu iters=%lld fullchecks=%lld bestbip=%lld alpha=%d 25bip=%lld n2=%d g6=%s\n",
                N, (unsigned long long)seed, iters, fullchecks, bestbip, bestalpha, 25 * bestbip, N * N, bestg6.c_str());
    return 0;
}
