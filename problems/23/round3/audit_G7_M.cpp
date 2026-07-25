// audit_G7_M.cpp -- INDEPENDENT exact computation of
//     M(H,q)     = max over a >= 0, sum a = q, of  bip(H[a])
//     M_deg(H,q) = same but restricted to  3*(A a)_v > q  for every v
// with bip(H[a]) = min over ALL cuts S of sum_{uv monochromatic} a_u a_v.
//
// Deliberately different from G7_psi_search.cpp:
//   * ALL 2^(n-1) cuts are carried incrementally (no pool of 8, no passive set),
//   * bip at a leaf is the direct minimum over the precomputed monochromatic
//     edge lists (no  W - maxcut  identity, no Gray code),
//   * the branch-and-bound bound is the crude but obviously sound
//        Q_S(completion) <= FF_S + rem*max_v c_S[v] + rem^2/4     (Mantel:
//     the free monochromatic graph is triangle-free), applied to EVERY cut,
//   * no automorphism pruning at all.
// Exact int64 everywhere.
//
// usage: audit_G7_M <n> <"u-v,u-v,...">  <qlo> <qhi> <max|maxdeg> [threads]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <atomic>
#include <algorithm>

static int N, NE;
static int EU[512], EV[512];
static std::vector<int> ADJ[32];
static int NCUT;
static std::vector<std::vector<std::pair<int,int> > > MONO;   // per cut
static std::vector<std::vector<int> > MSTART;                 // per cut, per k
static int DEG = 0;
static int Q;

struct Ctx {
    std::vector<long long> FF;          // NCUT
    std::vector<long long> C;           // NCUT * N
    long long pd[32];
    int a[32];
    long long best;
    int besta[32];
};

static long long bip_leaf(const int *a) {
    long long mn = -1;
    for (int s = 0; s < NCUT; s++) {
        long long v = 0;
        const std::vector<std::pair<int,int> > &L = MONO[s];
        for (size_t j = 0; j < L.size(); j++) {
            v += (long long)a[L[j].first] * a[L[j].second];
            if (mn >= 0 && v >= mn) break;
        }
        if (mn < 0 || v < mn) mn = v;
    }
    return mn;
}

static void dfs(Ctx &X, int k, int rem, std::mutex &mtx, long long &gbest, int *gbesta) {
    if (k == N) {
        if (rem != 0) return;
        if (DEG) for (int v = 0; v < N; v++) if (3 * X.pd[v] <= Q) return;
        long long m = bip_leaf(X.a);
        if (m > X.best) {
            X.best = m;
            memcpy(X.besta, X.a, sizeof(int) * N);
            std::lock_guard<std::mutex> lk(mtx);
            if (m > gbest) { gbest = m; memcpy(gbesta, X.a, sizeof(int) * N); }
        }
        return;
    }
    // ---- prune: upper bound on bip over all completions
    if (k > 0) {
        long long mn = -1;
        for (int s = 0; s < NCUT; s++) {
            long long mx = 0;
            const long long *c = &X.C[(size_t)s * N];
            for (int v = k; v < N; v++) if (c[v] > mx) mx = c[v];
            long long ub = X.FF[s] + (long long)rem * mx;
            // free monochromatic edges (both ends >= k)?
            bool hasedge = (MSTART[s][k] < (int)MONO[s].size());
            if (hasedge) ub += (long long)rem * rem / 4;
            if (mn < 0 || ub < mn) mn = ub;
            if (mn <= X.best) break;
        }
        if (mn <= X.best) return;
    }
    if (DEG) {
        for (int v = 0; v < N; v++) if (3 * (X.pd[v] + rem) <= Q) return;
    }
    int tlo = (k == N - 1) ? rem : 0;          // last coordinate is forced
    for (int t = tlo; t <= rem; t++) {
        X.a[k] = t;
        if (t) {
            for (size_t j = 0; j < ADJ[k].size(); j++) X.pd[ADJ[k][j]] += t;
            for (int s = 0; s < NCUT; s++) {
                long long *c = &X.C[(size_t)s * N];
                X.FF[s] += (long long)t * c[k];
            }
            for (int s = 0; s < NCUT; s++) {
                long long *c = &X.C[(size_t)s * N];
                const std::vector<std::pair<int,int> > &L = MONO[s];
                for (size_t j = MSTART[s][k]; j < L.size(); j++) {
                    if (L[j].first != k) break;
                    c[L[j].second] += t;
                }
            }
        }
        dfs(X, k + 1, rem - t, mtx, gbest, gbesta);
        if (t) {
            for (size_t j = 0; j < ADJ[k].size(); j++) X.pd[ADJ[k][j]] -= t;
            for (int s = 0; s < NCUT; s++) {
                long long *c = &X.C[(size_t)s * N];
                const std::vector<std::pair<int,int> > &L = MONO[s];
                for (size_t j = MSTART[s][k]; j < L.size(); j++) {
                    if (L[j].first != k) break;
                    c[L[j].second] -= t;
                }
                X.FF[s] -= (long long)t * c[k];
            }
        }
    }
    X.a[k] = 0;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: n edges qlo qhi max|maxdeg [threads]\n"); return 1; }
    N = atoi(argv[1]);
    { std::string s = argv[2]; NE = 0; size_t i = 0;
      while (i < s.size()) {
          size_t j = s.find(',', i); if (j == std::string::npos) j = s.size();
          std::string tok = s.substr(i, j - i);
          size_t d = tok.find('-');
          int u = atoi(tok.substr(0, d).c_str()), v = atoi(tok.substr(d + 1).c_str());
          if (u > v) std::swap(u, v);
          EU[NE] = u; EV[NE] = v; NE++;
          ADJ[u].push_back(v); ADJ[v].push_back(u);
          i = j + 1;
      } }
    int qlo = atoi(argv[3]), qhi = atoi(argv[4]);
    DEG = (strstr(argv[5], "deg") != NULL);
    int nthr = (argc > 6) ? atoi(argv[6]) : 8;

    NCUT = 1 << (N - 1);
    MONO.assign(NCUT, std::vector<std::pair<int,int> >());
    MSTART.assign(NCUT, std::vector<int>(N + 2, 0));
    for (int s = 0; s < NCUT; s++) {
        for (int e = 0; e < NE; e++)
            if ((((s >> EU[e]) ^ (s >> EV[e])) & 1) == 0)
                MONO[s].push_back(std::make_pair(EU[e], EV[e]));
        std::sort(MONO[s].begin(), MONO[s].end());
        size_t j = 0;
        for (int k = 0; k <= N + 1; k++) {
            while (j < MONO[s].size() && MONO[s][j].first < k) j++;
            MSTART[s][k] = (int)j;
        }
    }

    for (int q = qlo; q <= qhi; q++) {
        Q = q;
        long long gbest = -1; int gbesta[32]; memset(gbesta, 0, sizeof gbesta);
        std::mutex mtx;
        std::atomic<int> nxt(0);
        std::vector<std::thread> th;
        for (int tid = 0; tid < nthr; tid++) th.push_back(std::thread([&]() {
            Ctx X;
            X.FF.assign(NCUT, 0);
            X.C.assign((size_t)NCUT * N, 0);
            for (;;) {
                int t0 = nxt.fetch_add(1);
                if (t0 > q) break;
                for (int s = 0; s < NCUT; s++) X.FF[s] = 0;
                for (size_t j = 0; j < X.C.size(); j++) X.C[j] = 0;
                for (int v = 0; v < N; v++) { X.pd[v] = 0; X.a[v] = 0; }
                X.best = -1;
                { std::lock_guard<std::mutex> lk(mtx); if (gbest > X.best) X.best = gbest; }
                // place a[0] = t0 then recurse from k=1
                X.a[0] = t0;
                if (t0) {
                    for (size_t j = 0; j < ADJ[0].size(); j++) X.pd[ADJ[0][j]] += t0;
                    for (int s = 0; s < NCUT; s++) {
                        long long *c = &X.C[(size_t)s * N];
                        const std::vector<std::pair<int,int> > &L = MONO[s];
                        for (size_t j = MSTART[s][0]; j < L.size(); j++) {
                            if (L[j].first != 0) break;
                            c[L[j].second] += t0;
                        }
                    }
                }
                dfs(X, 1, q - t0, mtx, gbest, gbesta);
            }
        }));
        for (size_t i = 0; i < th.size(); i++) th[i].join();
        if (gbest < 0) gbest = 0;
        printf("%s n=%d q=%d M=%lld 25M=%lld q2=%lld %s arg=",
               DEG ? "AUDITDEG" : "AUDIT", N, q, gbest, 25 * gbest, (long long)q * q,
               (25 * gbest <= (long long)q * q) ? "OK" : "***VIOLATOR***");
        for (int v = 0; v < N; v++) printf("%d ", gbesta[v]);
        printf("\n");
        fflush(stdout);
    }
    return 0;
}
