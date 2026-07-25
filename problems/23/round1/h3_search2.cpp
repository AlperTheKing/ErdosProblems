// H3 max-bip search v2 (Erdos #23 counterexample hunt) -- EXACT verification.
//
// Objective: maximise bip(G) = |E| - maxcut(G) over triangle-free G on N vertices.
// bip(G) = min over the 2^(n-1) bipartitions of the number of monochromatic edges, so the
// search maximises min over a bounded POOL of currently tightest bipartitions and re-certifies
// by FULL Gray-code enumeration of all 2^(n-1) cuts whenever the pool is satisfied.  Nothing is
// ever reported on the strength of the pool alone.
//
// Moves: (a) single-edge toggle (incremental pool update),
//        (b) vertex rewire: strip a vertex and reattach it to a random maximal independent set.
// Acceptance: Metropolis on the pooled deficiency  sum_{c in POOL} max(0, T - mono(c)).
//
// Build: clang++ -O3 -march=native -std=c++17 h3_search2.cpp -o h3_search2.exe
// Usage: h3_search2.exe N T SEED SECONDS POOL TEMP0 [seedg6]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <cmath>

static int N, T, POOL;
static uint64_t adj[32];
static int deg[32];
static int M;
static inline int pc(uint64_t x) { return __builtin_popcountll(x); }

static std::string g6enc(int n, const uint64_t* a) {
    std::string s(1, (char)(n + 63)); int cur = 0, nb = 0;
    for (int j = 1; j < n; ++j) for (int i = 0; i < j; ++i) {
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
static int abest;
static void mis(uint64_t P, int sz) {
    if (sz + pc(P) <= abest) return;
    if (!P) { if (sz > abest) abest = sz; return; }
    int bv = -1, bd = -1; uint64_t Q = P;
    while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; int d = pc(adj[v] & P); if (d > bd) { bd = d; bv = v; } }
    uint64_t vb = 1ull << bv;
    mis(P & ~(adj[bv] | vb), sz + 1); mis(P & ~vb, sz);
}
static int alpha_exact(int n) { abest = 0; mis((1ull << n) - 1, 0); return abest; }

struct FullResult { long long maxcut; std::vector<uint32_t> tight; };
static FullResult full_exact(int n, int K) {
    uint32_t S = 0; long long cut = 0, best = 0;
    const uint64_t total = 1ull << (n - 1);
    for (uint64_t i = 1; i < total; ++i) {
        int v = __builtin_ctzll(i) + 1; uint32_t bit = 1u << v;
        int inter = pc(adj[v] & (uint64_t)S);
        if (S & bit) { cut -= deg[v] - 2 * inter; S &= ~bit; }
        else         { cut += deg[v] - 2 * inter; S |= bit; }
        if (cut > best) best = cut;
    }
    std::vector<uint32_t> tight; tight.reserve(K);
    for (int slack = 0; slack <= 20; ++slack) {
        tight.clear(); S = 0; cut = 0;
        if (cut >= best - slack) tight.push_back(0);
        for (uint64_t i = 1; i < total; ++i) {
            int v = __builtin_ctzll(i) + 1; uint32_t bit = 1u << v;
            int inter = pc(adj[v] & (uint64_t)S);
            if (S & bit) { cut -= deg[v] - 2 * inter; S &= ~bit; }
            else         { cut += deg[v] - 2 * inter; S |= bit; }
            if (cut >= best - slack) { tight.push_back(S); if ((int)tight.size() >= K) break; }
        }
        if ((int)tight.size() >= K) break;
    }
    return { best, tight };
}
static inline int mono_of(uint32_t mask, int n) {
    uint64_t A = mask & ((1ull << n) - 1), B = (~(uint64_t)mask) & ((1ull << n) - 1);
    int s = 0; uint64_t Q = A;
    while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; s += pc(adj[v] & A); }
    Q = B; while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; s += pc(adj[v] & B); }
    return s / 2;
}

int main(int argc, char** argv) {
    if (argc < 7) { std::fprintf(stderr, "usage: %s N T SEED SECONDS POOL TEMP0 [seedg6]\n", argv[0]); return 2; }
    N = atoi(argv[1]); T = atoi(argv[2]);
    uint64_t seed = strtoull(argv[3], nullptr, 10);
    double secs = atof(argv[4]); POOL = atoi(argv[5]); double temp0 = atof(argv[6]);
    std::mt19937_64 rng(seed ^ 0x9E3779B97F4A7C15ull);
    const uint64_t FULL = (1ull << N) - 1;

    for (int i = 0; i < N; ++i) adj[i] = 0; M = 0;
    if (argc > 7) { int n2, m2; if (!decode_g6(argv[7], n2, adj, m2) || n2 != N) { std::fprintf(stderr, "bad seed g6\n"); return 3; } M = m2; }
    else {
        std::vector<std::pair<int,int>> pr;
        for (int i = 0; i < N; ++i) for (int j = i + 1; j < N; ++j) pr.push_back({i, j});
        std::shuffle(pr.begin(), pr.end(), rng);
        for (auto& e : pr) if (!(adj[e.first] & adj[e.second])) { adj[e.first] |= 1ull << e.second; adj[e.second] |= 1ull << e.first; ++M; }
    }
    for (int i = 0; i < N; ++i) deg[i] = pc(adj[i]);

    FullResult fr = full_exact(N, POOL);
    long long bestbip = (long long)M - fr.maxcut;
    std::string bestg6 = g6enc(N, adj);
    uint64_t bestadj[32]; memcpy(bestadj, adj, sizeof(adj)); int bestM = M;
    const int TGOAL = T;
    // adaptive bar: aiming more than one above the current best makes the pooled deficiency
    // unreachable, which would freeze the pool and blind the search.
    T = (int)std::min<long long>(TGOAL, bestbip + 1);

    std::vector<uint32_t> pool = fr.tight;
    std::vector<int> mono(pool.size());
    for (size_t i = 0; i < pool.size(); ++i) mono[i] = mono_of(pool[i], N);
    long long penalty = 0;
    for (size_t i = 0; i < pool.size(); ++i) penalty += std::max(0, T - mono[i]);

    auto t0 = std::chrono::steady_clock::now();
    double temp = temp0; long long iters = 0, fullchecks = 0;
    long long sinceimp = 0;

    // hard self-certification: no value is ever reported for a graph that is not triangle-free,
    // whose adjacency is asymmetric, or whose edge count disagrees with the adjacency matrix.
    auto certify = [&](const char* where) {
        int mm = 0;
        for (int a = 0; a < N; ++a) {
            mm += pc(adj[a]);
            if (adj[a] & (1ull << a)) { std::printf("FATAL selfloop %d at %s\n", a, where); std::exit(90); }
            for (int b = 0; b < N; ++b)
                if (((adj[a] >> b) & 1ull) != ((adj[b] >> a) & 1ull)) {
                    std::printf("FATAL asymmetry %d %d at %s\n", a, b, where); std::exit(91);
                }
        }
        if (mm / 2 != M) { std::printf("FATAL edgecount %d vs %d at %s\n", mm / 2, M, where); std::exit(92); }
        for (int a = 0; a < N; ++a)
            for (int b = a + 1; b < N; ++b)
                if (((adj[a] >> b) & 1ull) && (adj[a] & adj[b])) {
                    std::printf("FATAL triangle %d %d %d at %s\n", a, b,
                                (int)__builtin_ctzll(adj[a] & adj[b]), where);
                    std::exit(93);
                }
    };
    certify("seed");

    auto rebuild = [&]() {
        certify("rebuild");
        FullResult f2 = full_exact(N, POOL);
        long long bip = (long long)M - f2.maxcut;
        if (bip > bestbip) {
            bestbip = bip; bestg6 = g6enc(N, adj); memcpy(bestadj, adj, sizeof(adj)); bestM = M;
            int al = alpha_exact(N);
            std::printf("NEW n=%d m=%d maxcut=%lld bip=%lld alpha=%d 25bip=%lld n2=%d %s g6=%s\n",
                        N, M, f2.maxcut, bip, al, 25 * bip, N * N,
                        (25 * bip > (long long)N * N) ? "*** VIOLATION ***" : "ok", bestg6.c_str());
            std::fflush(stdout);
        }
        T = (int)std::min<long long>(TGOAL, bestbip + 1);
        pool = f2.tight; mono.assign(pool.size(), 0);
        for (size_t i = 0; i < pool.size(); ++i) mono[i] = mono_of(pool[i], N);
        penalty = 0; for (size_t i = 0; i < pool.size(); ++i) penalty += std::max(0, T - mono[i]);
        return bip;
    };

    while (true) {
        if ((iters & 0x3FF) == 0) {
            double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            if (el > secs) break;
            double frac = el / secs;
            temp = temp0 * std::pow(0.02, frac) * (0.5 + 1.5 * std::fabs(std::sin(6.283 * frac * 7)));
            if (temp < 1e-3) temp = 1e-3;
        }
        ++iters; ++sinceimp;

        if (sinceimp > 400000) {   // restart from best
            memcpy(adj, bestadj, sizeof(adj)); M = bestM;
            for (int i = 0; i < N; ++i) deg[i] = pc(adj[i]);
            rebuild(); sinceimp = 0; continue;
        }

        if ((rng() & 31) == 0) {
            // vertex rewire
            int v = (int)(rng() % N);
            uint64_t old = adj[v];
            uint64_t Q = adj[v];
            while (Q) { int u = __builtin_ctzll(Q); Q &= Q - 1; adj[u] &= ~(1ull << v); }
            M -= pc(adj[v]); adj[v] = 0;
            // reattach: random order, keep neighbourhood independent
            int perm[32]; for (int i = 0; i < N; ++i) perm[i] = i;
            for (int i = N - 1; i > 0; --i) { int j = (int)(rng() % (i + 1)); std::swap(perm[i], perm[j]); }
            uint64_t nb = 0;
            for (int i = 0; i < N; ++i) {
                int u = perm[i]; if (u == v) continue;
                if (adj[u] & nb) continue;       // would create a triangle
                if ((rng() & 3) == 0) continue;  // random thinning
                nb |= 1ull << u;
            }
            adj[v] = nb; Q = nb;
            while (Q) { int u = __builtin_ctzll(Q); Q &= Q - 1; adj[u] |= 1ull << v; }
            M += pc(nb);
            for (int i = 0; i < N; ++i) deg[i] = pc(adj[i]);
            long long np = 0;
            for (size_t i = 0; i < pool.size(); ++i) { mono[i] = mono_of(pool[i], N); np += std::max(0, T - mono[i]); }
            long long dpen = np - penalty;
            bool acc = (dpen <= 0) || (std::generate_canonical<double,24>(rng) < std::exp(-(double)dpen / temp));
            if (!acc) {   // undo
                Q = adj[v]; while (Q) { int u = __builtin_ctzll(Q); Q &= Q - 1; adj[u] &= ~(1ull << v); }
                M -= pc(adj[v]); adj[v] = old; Q = old;
                while (Q) { int u = __builtin_ctzll(Q); Q &= Q - 1; adj[u] |= 1ull << v; }
                M += pc(old);
                for (int i = 0; i < N; ++i) deg[i] = pc(adj[i]);
                for (size_t i = 0; i < pool.size(); ++i) mono[i] = mono_of(pool[i], N);
            } else penalty = np;
        } else {
            int u = (int)(rng() % N), v = (int)(rng() % N);
            if (u == v) continue; if (u > v) std::swap(u, v);
            bool present = (adj[u] >> v) & 1ull; int d;
            if (present) d = -1; else { if (adj[u] & adj[v]) continue; d = +1; }
            long long dpen = 0;
            for (size_t i = 0, sz = pool.size(); i < sz; ++i) {
                uint32_t msk = pool[i];
                if ((((msk >> u) ^ (msk >> v)) & 1u) == 0u)
                    dpen += std::max(0, T - (mono[i] + d)) - std::max(0, T - mono[i]);
            }
            bool acc = (dpen <= 0) || (std::generate_canonical<double,24>(rng) < std::exp(-(double)dpen / temp));
            if (!acc) continue;
            if (present) { adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); --deg[u]; --deg[v]; --M; }
            else         { adj[u] |= 1ull << v;  adj[v] |= 1ull << u;  ++deg[u]; ++deg[v]; ++M; }
            for (size_t i = 0, sz = pool.size(); i < sz; ++i) {
                uint32_t msk = pool[i];
                if ((((msk >> u) ^ (msk >> v)) & 1u) == 0u) mono[i] += d;
            }
            penalty += dpen;
        }

        // full exact re-certification: whenever the pooled bar is met, and periodically anyway
        if (penalty == 0 || (iters % 250000) == 0) {
            ++fullchecks;
            long long b = rebuild();
            if (b >= bestbip) sinceimp = 0;
        }
    }
    std::printf("DONE n=%d seed=%llu iters=%lld fullchecks=%lld bestbip=%lld 25bip=%lld n2=%d g6=%s\n",
                N, (unsigned long long)seed, iters, fullchecks, bestbip, 25 * bestbip, N * N, bestg6.c_str());
    (void)FULL;
    return 0;
}
