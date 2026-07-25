// H5 general hunter: simulated annealing over triangle-free graphs on N <= 64 vertices,
// with an ADVERSARIAL POOL OF CUTS as the objective.
//
//   objective(G) = min over the pool of cuts of the number of monochromatic edges.
// This is an UPPER bound on bip(G) (the pool is a subset of all 2^(N-1) cuts), so a high
// objective is only a candidate; every reported graph is re-certified exactly by CP-SAT.
// The pool is refreshed adversarially: every REFRESH moves we run a multi-restart max-cut
// local search on the current graph and insert the best cut it finds, evicting the least
// binding pool member.  That keeps the estimator honest during the search.
//
// build: clang++ -O3 -march=native -std=c++17 h5_hunt.cpp -o h5_hunt.exe
// usage: h5_hunt.exe N seconds [seed] [--blowup a,b,c,d,e] [--out file.g6]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cmath>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>
#include <thread>
#include <mutex>

using namespace std;
typedef unsigned long long u64;

static const int POOL = 384;

struct Rng {
    mt19937_64 g;
    Rng(u64 s) : g(s) {}
    inline u64 u() { return g(); }
    inline double d() { return (double)(g() >> 11) * (1.0 / 9007199254740992.0); }
    inline int i(int n) { return (int)(g() % (u64)n); }
};

struct State {
    int N, m = 0;
    u64 adj[64];
    u64 pool[POOL];
    int mono[POOL];
    int npool = 0;

    void clear(int n) { N = n; m = 0; memset(adj, 0, sizeof(adj)); npool = 0; }
    inline bool has(int u, int v) const { return (adj[u] >> v) & 1ull; }
    inline bool canAdd(int u, int v) const { return (adj[u] & adj[v]) == 0ull; }

    void addEdge(int u, int v) { adj[u] |= 1ull << v; adj[v] |= 1ull << u; m++; }
    void delEdge(int u, int v) { adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); m--; }

    int monoOf(u64 S) const {
        int c = 0;
        for (int u = 0; u < N; u++) {
            u64 hi = adj[u] & ~((1ull << (u + 1)) - 1);
            u64 same = ((S >> u) & 1ull) ? S : ~S;
            c += __builtin_popcountll(hi & same);
        }
        return c;
    }
    void addCut(u64 S) {
        if (npool < POOL) { pool[npool] = S; mono[npool] = monoOf(S); npool++; return; }
        int worst = 0;
        for (int k = 1; k < npool; k++) if (mono[k] > mono[worst]) worst = k;
        pool[worst] = S; mono[worst] = monoOf(S);
    }
    inline int obj() const {
        int b = mono[0];
        for (int k = 1; k < npool; k++) if (mono[k] < b) b = mono[k];
        return b;
    }
    // objective after toggling (u,v); dir=+1 add, -1 remove
    inline int objAfter(int u, int v, int dir) const {
        int b = INT32_MAX;
        for (int k = 0; k < npool; k++) {
            u64 S = pool[k];
            int same = (int)(1ull ^ (((S >> u) ^ (S >> v)) & 1ull));
            int val = mono[k] + dir * same;
            if (val < b) b = val;
        }
        return b;
    }
    inline void applyToggle(int u, int v, int dir) {
        for (int k = 0; k < npool; k++) {
            u64 S = pool[k];
            int same = (int)(1ull ^ (((S >> u) ^ (S >> v)) & 1ull));
            mono[k] += dir * same;
        }
        if (dir > 0) addEdge(u, v); else delEdge(u, v);
    }
};

// multi-restart max-cut local search; returns the cut with the FEWEST monochromatic edges
static u64 adversary(const State &st, Rng &rng, int restarts) {
    int N = st.N;
    u64 best = 0; int bestMono = INT32_MAX;
    for (int r = 0; r < restarts; r++) {
        u64 S = rng.u() & ((N == 64) ? ~0ull : ((1ull << N) - 1));
        bool improved = true;
        while (improved) {
            improved = false;
            for (int v = 0; v < N; v++) {
                u64 sameSet = ((S >> v) & 1ull) ? S : ~S;
                int same = __builtin_popcountll(st.adj[v] & sameSet);
                int diff = __builtin_popcountll(st.adj[v]) - same;
                if (same > diff) { S ^= 1ull << v; improved = true; }
            }
        }
        int mo = st.monoOf(S);
        if (mo < bestMono) { bestMono = mo; best = S; }
    }
    return best;
}

static string g6(int n, const u64 *adj) {
    string out(1, (char)(n + 63));
    unsigned cur = 0; int nb = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        cur = (cur << 1) | (unsigned)((adj[i] >> j) & 1ull);
        if (++nb == 6) { out += (char)(cur + 63); cur = 0; nb = 0; }
    }
    if (nb) out += (char)((cur << (6 - nb)) + 63);
    return out;
}

struct Result { int bip = -1; string g6; int m = 0; };

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: h5_hunt N seconds [threads] [a,b,c,d,e]\n"); return 1; }
    int N = atoi(argv[1]);
    double secs = atof(argv[2]);
    int NT = argc > 3 ? atoi(argv[3]) : (int)thread::hardware_concurrency();
    vector<int> seedParts;
    if (argc > 4) { char *s = strdup(argv[4]); for (char *p = strtok(s, ","); p; p = strtok(NULL, ",")) seedParts.push_back(atoi(p)); }

    mutex mtx; Result best;
    auto t0 = chrono::steady_clock::now();

    auto worker = [&](int tid) {
        Rng rng(0x5eed1234ull + 9176ull * tid);
        State st; Result loc;
        for (int outer = 0; ; outer++) {
            if (chrono::duration<double>(chrono::steady_clock::now() - t0).count() > secs) break;
            st.clear(N);
            // ---- initial graph
            if (!seedParts.empty() && (tid + outer) % 2 == 0) {
                vector<int> part(N); int idx = 0;
                for (int i = 0; i < 5; i++) for (int k = 0; k < seedParts[i]; k++) part[idx++] = i;
                for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++)
                    if ((part[u] + 1) % 5 == part[v] || (part[v] + 1) % 5 == part[u])
                        if (st.canAdd(u, v)) st.addEdge(u, v);
            } else {
                for (int t = 0; t < 8 * N * N; t++) {
                    int u = rng.i(N), v = rng.i(N);
                    if (u == v || st.has(u, v)) continue;
                    if (st.canAdd(u, v)) st.addEdge(u, v);
                }
            }
            // ---- pool seed
            st.npool = 0;
            for (int k = 0; k < POOL / 2; k++)
                st.addCut(rng.u() & ((N == 64) ? ~0ull : ((1ull << N) - 1)));
            for (int k = 0; k < POOL / 2; k++) st.addCut(adversary(st, rng, 4));

            double T0 = 2.0, T1 = 0.02;
            long STEPS = 4000000;
            for (long s = 0; s < STEPS; s++) {
                if ((s & 0xFFFFF) == 0 &&
                    chrono::duration<double>(chrono::steady_clock::now() - t0).count() > secs) break;
                double T = T0 * pow(T1 / T0, (double)s / STEPS);
                int u = rng.i(N), v = rng.i(N);
                if (u == v) continue;
                if (u > v) swap(u, v);
                int cur = st.obj();
                if (st.has(u, v)) {
                    int nv = st.objAfter(u, v, -1);
                    if (nv >= cur || rng.d() < exp((nv - cur) / T)) st.applyToggle(u, v, -1);
                } else if (st.canAdd(u, v)) {
                    int nv = st.objAfter(u, v, +1);
                    if (nv >= cur || rng.d() < exp((nv - cur) / T)) st.applyToggle(u, v, +1);
                }
                if ((s & 8191) == 0) {
                    u64 S = adversary(st, rng, 24);
                    int mo = st.monoOf(S);
                    if (mo < st.obj()) st.addCut(S);
                    else if ((s & 65535) == 0) st.addCut(S);
                }
                if ((s & 65535) == 0) {
                    // honest-ish evaluation with a heavy adversary
                    u64 S = adversary(st, rng, 400);
                    int b = st.monoOf(S);
                    int po = st.obj();
                    int est = min(b, po);
                    if (est > loc.bip) { loc.bip = est; loc.g6 = g6(N, st.adj); loc.m = st.m; }
                }
            }
            u64 S = adversary(st, rng, 2000);
            int est = min(st.monoOf(S), st.obj());
            if (est > loc.bip) { loc.bip = est; loc.g6 = g6(N, st.adj); loc.m = st.m; }
        }
        lock_guard<mutex> lk(mtx);
        if (loc.bip > best.bip) best = loc;
    };

    vector<thread> pool;
    for (int t = 0; t < NT; t++) pool.emplace_back(worker, t);
    for (auto &t : pool) t.join();

    printf("N=%d  best_estimated_bip=%d  m=%d  25*bip=%d vs N^2=%d\n",
           N, best.bip, best.m, 25 * best.bip, N * N);
    printf("g6=%s\n", best.g6.c_str());
    return 0;
}
