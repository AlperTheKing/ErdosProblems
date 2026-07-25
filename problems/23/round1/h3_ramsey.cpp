// Construct triangle-free graphs on n vertices with independence number <= A
// (i.e. Ramsey (3, A+1)-graphs / near-extremal Ramsey-critical graphs), then optionally
// maximise edge count subject to that constraint.  Output: graph6 lines.
//
// Method: repeatedly compute a maximum independent set I exactly (branch and bound); insert an
// edge inside I whenever some pair of I has no common neighbour (keeps triangle-freeness);
// if I is "saturated", delete a random edge and continue.  Classical Ramsey-graph local search.
//
// Build: clang++ -O3 -march=native -std=c++17 h3_ramsey.cpp -o h3_ramsey.exe
// Usage: h3_ramsey.exe N ALPHAMAX SEED TRIES MAXEDGE_ROUNDS

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <vector>
#include <random>
#include <algorithm>

static int N;
static uint64_t adj[64];
static inline int pc(uint64_t x) { return __builtin_popcountll(x); }

static int abest; static uint64_t awit, acur;
static void mis(uint64_t P, int sz, uint64_t cur) {
    if (sz + pc(P) <= abest) return;
    if (!P) { if (sz > abest) { abest = sz; awit = cur; } return; }
    int bv = -1, bd = -1; uint64_t Q = P;
    while (Q) { int v = __builtin_ctzll(Q); Q &= Q - 1; int d = pc(adj[v] & P); if (d > bd) { bd = d; bv = v; } }
    uint64_t vb = 1ull << bv;
    mis(P & ~(adj[bv] | vb), sz + 1, cur | vb);
    mis(P & ~vb, sz, cur);
}
static int alpha_exact(int n, uint64_t& wit) { abest = 0; awit = 0; mis((1ull << n) - 1, 0, 0); wit = awit; return abest; }

static std::string g6enc(int n) {
    std::string s(1, (char)(n + 63)); int cur = 0, nb = 0;
    for (int j = 1; j < n; ++j) for (int i = 0; i < j; ++i) {
        cur = (cur << 1) | (int)((adj[i] >> j) & 1ull);
        if (++nb == 6) { s += (char)(cur + 63); cur = 0; nb = 0; }
    }
    if (nb) { cur <<= (6 - nb); s += (char)(cur + 63); }
    return s;
}
static int edges(int n) { int m = 0; for (int i = 0; i < n; ++i) m += pc(adj[i]); return m / 2; }

int main(int argc, char** argv) {
    if (argc < 6) { std::fprintf(stderr, "usage: %s N ALPHAMAX SEED TRIES EDGEROUNDS\n", argv[0]); return 2; }
    N = atoi(argv[1]); int A = atoi(argv[2]);
    std::mt19937_64 rng(strtoull(argv[3], nullptr, 10));
    long long TRIES = atoll(argv[4]); long long ER = atoll(argv[5]);

    for (int i = 0; i < N; ++i) adj[i] = 0;
    uint64_t wit;
    for (long long it = 0; it < TRIES; ++it) {
        int a = alpha_exact(N, wit);
        if (a <= A) break;
        // try to add an edge inside the witness independent set
        std::vector<int> I;
        uint64_t Q = wit; while (Q) { I.push_back(__builtin_ctzll(Q)); Q &= Q - 1; }
        std::shuffle(I.begin(), I.end(), rng);
        bool added = false;
        for (size_t x = 0; x < I.size() && !added; ++x)
            for (size_t y = x + 1; y < I.size() && !added; ++y) {
                int u = I[x], v = I[y];
                if (adj[u] & adj[v]) continue;             // common neighbour -> triangle
                adj[u] |= 1ull << v; adj[v] |= 1ull << u; added = true;
            }
        if (!added) {   // saturated: delete a random edge to escape
            for (int t = 0; t < 50; ++t) {
                int u = (int)(rng() % N);
                if (!adj[u]) continue;
                uint64_t R = adj[u]; int k = (int)(rng() % pc(R));
                while (k--) R &= R - 1;
                int v = __builtin_ctzll(R);
                adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); break;
            }
        }
    }
    uint64_t w2; int a = alpha_exact(N, w2);
    if (a > A) { std::fprintf(stderr, "FAILED n=%d target alpha<=%d, got %d\n", N, A, a); return 1; }

    // now push edge count up while keeping alpha <= A and triangle-freeness
    for (long long r = 0; r < ER; ++r) {
        int u = (int)(rng() % N), v = (int)(rng() % N);
        if (u == v) continue;
        if ((adj[u] >> v) & 1ull) continue;
        if (adj[u] & adj[v]) continue;
        adj[u] |= 1ull << v; adj[v] |= 1ull << u;          // alpha can only decrease
    }
    uint64_t w3; int a2 = alpha_exact(N, w3);
    std::printf("%s\tn=%d\tm=%d\talpha=%d\n", g6enc(N).c_str(), N, edges(N), a2);
    return 0;
}
