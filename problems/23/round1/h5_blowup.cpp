// H5: exact search over BLOW-UPS of small triangle-free graphs.
//
// For a blow-up H[w] the maximum cut never splits a part: with all other vertices fixed,
// the cut value is a LINEAR function of how many vertices of the (independent) part V_i sit
// on side A, so an optimum exists with every part unsplit.  Hence
//        bip(H[w]) = min over the 2^(h-1) unsplit 2-colourings S of  sum_{uv in E(H),
//                    u,v on the same side}  w_u w_v ,
// which is EXACT integer arithmetic and cheap.  We hill-climb over integer weight vectors
// w >= 0 with sum w = N, for every connected triangle-free H read from stdin (graph6).
//
// build: clang++ -O3 -march=native -std=c++17 -fopenmp h5_blowup.cpp -o h5_blowup.exe
// usage: geng -tc -q 11 | ./h5_blowup.exe 49 51 74 76

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <array>
#include <iostream>
#include <thread>
#include <atomic>
#include <mutex>

using namespace std;

struct Graph { int h; uint32_t adj[20]; string g6; };

static bool parse_g6(const string &s, Graph &G) {
    int n = (int)s[0] - 63;
    if (n < 1 || n > 17) return false;
    G.h = n;
    for (int i = 0; i < n; i++) G.adj[i] = 0;
    int p = 1, bit = 0; unsigned cur = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        if (bit == 0) { if (p >= (int)s.size()) return false; cur = (unsigned)s[p++] - 63; bit = 6; }
        bit--;
        if ((cur >> bit) & 1) { G.adj[i] |= 1u << j; G.adj[j] |= 1u << i; }
    }
    G.g6 = s;
    return true;
}

static bool is_bipartite(const Graph &G) {
    int col[20]; for (int i = 0; i < G.h; i++) col[i] = -1;
    for (int s = 0; s < G.h; s++) {
        if (col[s] != -1) continue;
        col[s] = 0; vector<int> st{s};
        while (!st.empty()) {
            int v = st.back(); st.pop_back();
            for (int u = 0; u < G.h; u++) if ((G.adj[v] >> u) & 1) {
                if (col[u] == -1) { col[u] = col[v] ^ 1; st.push_back(u); }
                else if (col[u] == col[v]) return false;
            }
        }
    }
    return true;
}

struct Work {
    int h, ncuts, ne;
    int eu[80], ev[80];
    vector<long long> mono;   // ncuts
    vector<long long> A;      // ncuts * h
    vector<int> w;
    const Graph *G;

    void setup(const Graph &g) {
        G = &g; h = g.h; ne = 0;
        for (int u = 0; u < h; u++) for (int v = u + 1; v < h; v++)
            if ((g.adj[u] >> v) & 1) { eu[ne] = u; ev[ne] = v; ne++; }
        ncuts = 1 << (h - 1);
        mono.assign(ncuts, 0);
        A.assign((size_t)ncuts * h, 0);
        w.assign(h, 0);
    }
    inline uint32_t maskof(int t) const { return ((uint32_t)t) << 1; }  // vertex 0 always side 0
    inline bool same(uint32_t S, int a, int b) const { return (((S >> a) ^ (S >> b)) & 1u) == 0; }

    void rebuild() {
        for (int t = 0; t < ncuts; t++) {
            uint32_t S = maskof(t);
            long long mo = 0;
            for (int e = 0; e < ne; e++) if (same(S, eu[e], ev[e]))
                mo += (long long)w[eu[e]] * w[ev[e]];
            mono[t] = mo;
            long long *Ap = &A[(size_t)t * h];
            for (int v = 0; v < h; v++) {
                long long a = 0;
                for (int b = 0; b < h; b++) if (((G->adj[v] >> b) & 1) && same(S, v, b)) a += w[b];
                Ap[v] = a;
            }
        }
    }
    long long bip() const {
        long long best = mono[0];
        for (int t = 1; t < ncuts; t++) best = min(best, mono[t]);
        return best;
    }
    // value of bip after transferring one unit from j to i, or -1 if it cannot beat `cur`
    inline long long trial(int i, int j, long long cur) const {
        bool ij = (G->adj[i] >> j) & 1;
        long long best = INT64_MAX;
        for (int t = 0; t < ncuts; t++) {
            const long long *Ap = &A[(size_t)t * h];
            long long v = mono[t] + Ap[i] - Ap[j];
            if (ij && same(maskof(t), i, j)) v -= 1;
            if (v <= cur) return -1;          // early exit: not an improvement
            if (v < best) best = v;
        }
        return best;
    }
    void apply(int i, int j) {
        for (int t = 0; t < ncuts; t++) {
            uint32_t S = maskof(t);
            long long *Ap = &A[(size_t)t * h];
            long long d = Ap[i] - Ap[j];
            if (((G->adj[i] >> j) & 1) && same(S, i, j)) d -= 1;
            mono[t] += d;
            for (int v = 0; v < h; v++) {
                if (((G->adj[i] >> v) & 1) && same(S, i, v)) Ap[v] += 1;
                if (((G->adj[j] >> v) & 1) && same(S, j, v)) Ap[v] -= 1;
            }
        }
        w[i]++; w[j]--;
    }
};

struct Best { long long bip = -1; string g6; vector<int> w; int N = 0; };

// B(N) = max over w1..w5 >= 0 summing to N of min_i w_i w_{i+1}, with an argmax.
static long long Bopt(int N, int arg[5]) {
    long long best = -1;
    for (int a = 0; a <= N; a++) for (int b = 0; a + b <= N; b++)
        for (int c = 0; a + b + c <= N; c++) for (int d = 0; a + b + c + d <= N; d++) {
            int e = N - a - b - c - d;
            long long v = min(min((long long)a * b, (long long)b * c),
                              min(min((long long)c * d, (long long)d * e), (long long)e * a));
            if (v > best) { best = v; arg[0]=a; arg[1]=b; arg[2]=c; arg[3]=d; arg[4]=e; }
        }
    return best;
}

// every induced 5-cycle of H, as a cyclic order
static void induced_c5s(const Graph &G, vector<array<int,5>> &out) {
    int h = G.h;
    int idx[5];
    for (idx[0] = 0; idx[0] < h; idx[0]++)
     for (idx[1] = idx[0]+1; idx[1] < h; idx[1]++)
      for (idx[2] = idx[1]+1; idx[2] < h; idx[2]++)
       for (idx[3] = idx[2]+1; idx[3] < h; idx[3]++)
        for (idx[4] = idx[3]+1; idx[4] < h; idx[4]++) {
            int deg[5] = {0,0,0,0,0}; int tot = 0;
            for (int i = 0; i < 5; i++) for (int j = i+1; j < 5; j++)
                if ((G.adj[idx[i]] >> idx[j]) & 1) { deg[i]++; deg[j]++; tot++; }
            if (tot != 5) continue;
            bool ok = true;
            for (int i = 0; i < 5; i++) if (deg[i] != 2) ok = false;
            if (!ok) continue;
            array<int,5> cyc; int order[5]; order[0] = 0; int prev = -1, cur = 0;
            for (int s = 1; s < 5; s++) {
                for (int k = 0; k < 5; k++)
                    if (k != prev && k != cur && ((G.adj[idx[cur]] >> idx[k]) & 1)) { order[s] = k; prev = cur; cur = k; break; }
            }
            for (int s = 0; s < 5; s++) cyc[s] = idx[order[s]];
            out.push_back(cyc);
            if (out.size() >= 60) return;
        }
}

int main(int argc, char **argv) {
    vector<int> Ns;
    for (int i = 1; i < argc; i++) Ns.push_back(atoi(argv[i]));
    if (Ns.empty()) { fprintf(stderr, "usage: ... | h5_blowup N [N...]\n"); return 1; }

    vector<Graph> graphs;
    { string line; Graph G;
      while (getline(cin, line)) {
          while (!line.empty() && (line.back()=='\n'||line.back()=='\r')) line.pop_back();
          if (line.empty()) continue;
          if (!parse_g6(line, G)) continue;
          if (is_bipartite(G)) continue;          // bipartite H  =>  bip = 0
          graphs.push_back(G);
      } }
    fprintf(stderr, "loaded %zu connected non-bipartite triangle-free graphs\n", graphs.size());

    int R = 6, MAXSTEP = 400;
    vector<Best> best(Ns.size());
    vector<array<int,5>> Barg(Ns.size());
    vector<long long> Bval(Ns.size());
    for (size_t k = 0; k < Ns.size(); k++) {
        int a[5]; Bval[k] = Bopt(Ns[k], a);
        for (int s = 0; s < 5; s++) Barg[k][s] = a[s];
        fprintf(stderr, "B(%d) = %lld  parts %d,%d,%d,%d,%d\n", Ns[k], Bval[k],
                a[0], a[1], a[2], a[3], a[4]);
    }
    const char *envT = getenv("H5_THREADS");
    int NT = envT ? atoi(envT) : (int)thread::hardware_concurrency();
    if (NT < 1) NT = 1;
    fprintf(stderr, "threads=%d\n", NT);
    atomic<long> cursor(0);
    mutex mtx;
    vector<thread> pool;

    auto worker = [&](int tid) {
        vector<Best> loc(Ns.size());
        Work W;
        mt19937_64 rng(12345 + 7777ull * tid);
        for (;;) {
            long gi = cursor.fetch_add(1);
            if (gi >= (long)graphs.size()) break;
            const Graph &G = graphs[gi];
            W.setup(G);
            vector<array<int,5>> c5s; induced_c5s(G, c5s);
            int nseed = (int)min(c5s.size(), (size_t)15);
            for (size_t k = 0; k < Ns.size(); k++) {
                int N = Ns[k];
                if (N < G.h) continue;
                for (int r = 0; r < R + nseed; r++) {
                    // ---- start point
                    if (r == 0) { for (int v = 0; v < G.h; v++) W.w[v] = N / G.h;
                                  for (int v = 0; v < N % G.h; v++) W.w[v]++; }
                    else if (r <= nseed) {
                        // seed on an induced C5 with the B(N)-optimal C5 weights
                        for (int v = 0; v < G.h; v++) W.w[v] = 0;
                        const array<int,5> &cy = c5s[r - 1];
                        int rot = (int)(rng() % 5);
                        for (int s = 0; s < 5; s++) W.w[cy[(s + rot) % 5]] = Barg[k][s];
                    }
                    else { for (int v = 0; v < G.h; v++) W.w[v] = 0;
                           for (int c = 0; c < N; c++) W.w[rng() % G.h]++; }
                    W.rebuild();
                    long long cur = W.bip();
                    // ---- steepest-ascent hill climb on unit transfers
                    for (int step = 0; step < MAXSTEP; step++) {
                        long long bv = cur; int bi = -1, bj = -1;
                        for (int i = 0; i < G.h; i++) for (int j = 0; j < G.h; j++) {
                            if (i == j || W.w[j] == 0) continue;
                            long long v = W.trial(i, j, bv);
                            if (v > bv) { bv = v; bi = i; bj = j; }
                        }
                        if (bi < 0) break;
                        W.apply(bi, bj);
                        cur = bv;
                    }
                    if (cur > loc[k].bip) { loc[k].bip = cur; loc[k].g6 = G.g6;
                                            loc[k].w = W.w; loc[k].N = N; }
                }
            }
        }
        lock_guard<mutex> lk(mtx);
        for (size_t k = 0; k < Ns.size(); k++)
            if (loc[k].bip > best[k].bip) best[k] = loc[k];
    };
    for (int t = 0; t < NT; t++) pool.emplace_back(worker, t);
    for (auto &t : pool) t.join();

    for (size_t k = 0; k < Ns.size(); k++) {
        printf("N=%d  best_blowup_bip=%lld  B(N)=%lld  gain=%+lld  25*bip=%lld vs N^2=%d  ratio=%.6f  H=%s  w=[",
               Ns[k], best[k].bip, Bval[k], best[k].bip - Bval[k], 25 * best[k].bip, Ns[k] * Ns[k],
               (double)best[k].bip / (Ns[k] * (double)Ns[k]), best[k].g6.c_str());
        for (size_t i = 0; i < best[k].w.size(); i++) printf("%d%s", best[k].w[i],
               i + 1 == best[k].w.size() ? "" : ",");
        printf("]\n");
    }
    return 0;
}
