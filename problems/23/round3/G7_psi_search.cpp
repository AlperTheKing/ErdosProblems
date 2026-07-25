// G7_psi_search.cpp -- exhaustive EXACT integer-weighting search for
//   M(H,q) = max_{a in Z_{>=0}^n, sum a = q}  bip(H[a])
// where bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v
//                 = W(a) - maxcut_a(H)      (accepted fact 1).
//
// Erdos-Faudree-Pach-Spencer restricted to blow-ups of H is exactly
//        25 * M(H,q) <= q^2      for every q >= 0.
//
// ZEROS ARE ALLOWED in a (essential: an engine restricted to strictly
// positive parts returns wrong values).  All arithmetic is exact int64.
//
// modes:
//   cert : fixed threshold T = floor(q^2/25); prove every a admits a cut S
//          with Q_S(a) <= T.  Any a failing this is printed as a VIOLATOR.
//   max  : compute M(H,q) exactly (branch and bound with moving best).
//
// build: clang++ -O3 -march=native -std=c++17 G7_psi_search.cpp -o G7_psi_search.exe
// usage: G7_psi_search <n> <"u-v,u-v,..."> <q> <cert|max> [threads]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>

static int N, Q, M_EDGES;
static int EU[1024], EV[1024];
static uint32_t ADJ[32];
static int MODE_CERT;
static long long g_T;               // shared lower bound (mode max) / threshold

static const int APOOL = 8;         // active (incremental) cut pool

// per active cut: its monochromatic edges (u<v) sorted by u, and, for each k,
// the index of the first such edge with u >= k.
static std::vector<std::pair<int, int> > MONO[APOOL];
static int MSTART[APOOL][34];

// --- automorphism orbit pruning (optional) -----------------------------
static int NAUT = 0;
static int AUT[4096][32];
static std::vector<int> ALEV[34];       // ALEV[k] = sigma with sigma({0..k})={0..k}

static void build_aut_levels() {
    for (int k = 0; k < N; k++) {
        ALEV[k].clear();
        for (int s = 0; s < NAUT; s++) {
            bool ok = true, id = true;
            for (int j = 0; j <= k; j++) {
                if (AUT[s][j] > k) { ok = false; break; }
                if (AUT[s][j] != j) id = false;
            }
            if (ok && !id) ALEV[k].push_back(s);
        }
    }
}

static inline bool orbit_prune(const int *a, int k) {
    for (size_t t = 0; t < ALEV[k].size(); t++) {
        const int *s = AUT[ALEV[k][t]];
        for (int j = 0; j <= k; j++) {
            int x = a[s[j]], y = a[j];
            if (x < y) return true;
            if (x > y) break;
        }
    }
    return false;
}

static void build_mono(int p, uint32_t S) {
    MONO[p].clear();
    for (int e = 0; e < M_EDGES; e++) {
        int u = EU[e], v = EV[e];
        if (u > v) std::swap(u, v);
        if ((((S >> u) ^ (S >> v)) & 1) == 0) MONO[p].push_back(std::make_pair(u, v));
    }
    std::sort(MONO[p].begin(), MONO[p].end());
    size_t j = 0;
    for (int k = 0; k <= N + 1; k++) {
        while (j < MONO[p].size() && MONO[p][j].first < k) j++;
        MSTART[p][k] = (int)j;
    }
}

// ---------------------------------------------------------------- exact bip
// bip = W - maxcut, maxcut by Gray code over 2^(n-1) cuts (vertex n-1 fixed out)
static long long exact_bip(const int *a, uint32_t &argcut) {
    long long W = 0;
    for (int e = 0; e < M_EDGES; e++) W += (long long)a[EU[e]] * a[EV[e]];
    long long s[32], D[32];
    for (int v = 0; v < N; v++) {
        s[v] = 0; D[v] = 0;
        uint32_t nb = ADJ[v];
        while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; D[v] += a[u]; }
    }
    long long cut = 0, bestcut = 0;
    uint32_t S = 0, bestS = 0;
    uint32_t total = 1u << (N - 1), prev = 0;
    for (uint32_t i = 1; i < total; i++) {
        uint32_t g = i ^ (i >> 1);
        int v = __builtin_ctz(g ^ prev);
        prev = g;
        if (!((S >> v) & 1)) {
            cut += (long long)a[v] * (D[v] - 2 * s[v]);
            S |= 1u << v;
            uint32_t m = ADJ[v];
            while (m) { int u = __builtin_ctz(m); m &= m - 1; s[u] += a[v]; }
        } else {
            cut += (long long)a[v] * (2 * s[v] - D[v]);
            S &= ~(1u << v);
            uint32_t m = ADJ[v];
            while (m) { int u = __builtin_ctz(m); m &= m - 1; s[u] -= a[v]; }
        }
        if (cut > bestcut) { bestcut = cut; bestS = S; }
    }
    argcut = bestS;
    return W - bestcut;
}

static inline long long Qcut(const int *a, uint32_t S) {
    long long r = 0;
    for (int e = 0; e < M_EDGES; e++)
        if ((((S >> EU[e]) ^ (S >> EV[e])) & 1) == 0) r += (long long)a[EU[e]] * a[EV[e]];
    return r;
}

// ------------------------------------------------------- per-thread context
struct Ctx {
    uint32_t cut[APOOL];
    long long FF[APOOL];
    long long c[APOOL][32];
    std::vector<uint32_t> passive;
    int a[32];
    long long T;
    long long bestval; int besta[32];
    long long violators; int vio[32];
    unsigned rng;
};

static void dfs(Ctx &X, int k, int r, std::mutex &mtx) {
    if (k == N - 1) {
        X.a[k] = r;
        if (NAUT && orbit_prune(X.a, k)) return;
        long long mn = -1;
        for (int p = 0; p < APOOL; p++) {
            long long q = X.FF[p] + (long long)r * X.c[p][k];
            if (mn < 0 || q < mn) mn = q;
        }
        if (mn <= X.T) return;
        for (size_t j = 0; j < X.passive.size(); j++)
            if (Qcut(X.a, X.passive[j]) <= X.T) return;
        uint32_t ac;
        long long m = exact_bip(X.a, ac);
        if (m > X.T) {
            if (MODE_CERT) { X.violators++; memcpy(X.vio, X.a, sizeof(int) * N); }
            else {
                X.bestval = m; memcpy(X.besta, X.a, sizeof(int) * N); X.T = m;
                { std::lock_guard<std::mutex> lk(mtx); if (m > g_T) g_T = m; }
            }
        } else {
            bool have = false;
            for (int p = 0; p < APOOL; p++) if (X.cut[p] == ac) have = true;
            for (size_t j = 0; j < X.passive.size(); j++) if (X.passive[j] == ac) have = true;
            if (!have) {
                if (X.passive.size() < 64) X.passive.push_back(ac);
                else { X.rng = X.rng * 1103515245u + 12345u; X.passive[(X.rng >> 16) % 64] = ac; }
            }
        }
        return;
    }
    for (int t = 0; t <= r; t++) {
        X.a[k] = t;
        if (NAUT && orbit_prune(X.a, k)) continue;
        long long saveFF[APOOL];
        for (int p = 0; p < APOOL; p++) {
            saveFF[p] = X.FF[p];
            X.FF[p] += (long long)t * X.c[p][k];
            if (t) {
                uint32_t nb = ADJ[k];
                while (nb) {
                    int u = __builtin_ctz(nb); nb &= nb - 1;
                    if (u > k && ((((X.cut[p] >> u) ^ (X.cut[p] >> k)) & 1) == 0)) X.c[p][u] += t;
                }
            }
        }
        int rem = r - t;
        // TIGHT bound: for each active cut S, max over REAL completions of Q_S.
        // By the Motzkin-Straus shifting argument the maximiser of
        //   sum_v c_v a_v + sum_{uv mono, both free} a_u a_v   on {a>=0, sum=rem}
        // is supported on a clique of the free monochromatic graph, i.e. on one
        // vertex or one edge (that graph is triangle-free).  Everything is
        // computed times 4 to stay in integers.
        bool prune = false;
        long long T4 = 4 * X.T;
        for (int p = 0; p < APOOL && !prune; p++) {
            long long bestc = 0;                     // 4 * (best completion)
            for (int v = k + 1; v < N; v++) {
                long long z = 4LL * rem * X.c[p][v];
                if (z > bestc) bestc = z;
            }
            const std::vector<std::pair<int,int> > &ME = MONO[p];
            for (size_t j = MSTART[p][k + 1]; j < ME.size(); j++) {
                int u = ME[j].first, v = ME[j].second;   // u < v, u >= k+1
                long long cu = X.c[p][u], cv = X.c[p][v];
                long long d = cu - cv + rem;             // 2*s*
                long long z;
                if (d <= 0) z = 4LL * rem * cv;
                else if (d >= 2LL * rem) z = 4LL * rem * cu;
                else z = d * d + 4LL * rem * cv;
                if (z > bestc) bestc = z;
            }
            if (4 * X.FF[p] + bestc <= T4) prune = true;
        }
        if (!prune) dfs(X, k + 1, rem, mtx);
        for (int p = 0; p < APOOL; p++) {
            X.FF[p] = saveFF[p];
            if (t) {
                uint32_t nb = ADJ[k];
                while (nb) {
                    int u = __builtin_ctz(nb); nb &= nb - 1;
                    if (u > k && ((((X.cut[p] >> u) ^ (X.cut[p] >> k)) & 1) == 0)) X.c[p][u] -= t;
                }
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: n edges q mode [threads]\n"); return 1; }
    N = atoi(argv[1]);
    { std::string s = argv[2]; M_EDGES = 0; size_t i = 0;
      while (i < s.size()) {
          size_t j = s.find(',', i); if (j == std::string::npos) j = s.size();
          std::string tok = s.substr(i, j - i);
          size_t d = tok.find('-');
          int u = atoi(tok.substr(0, d).c_str()), v = atoi(tok.substr(d + 1).c_str());
          EU[M_EDGES] = u; EV[M_EDGES] = v; M_EDGES++;
          ADJ[u] |= 1u << v; ADJ[v] |= 1u << u;
          i = j + 1;
      } }
    Q = atoi(argv[3]);
    MODE_CERT = (strcmp(argv[4], "cert") == 0);
    int nthr = (argc > 5) ? atoi(argv[5]) : 8;
    if (argc > 6) {
        FILE *f = fopen(argv[6], "r");
        if (f) {
            while (NAUT < 4096) {
                int ok = 1;
                for (int v = 0; v < N; v++) if (fscanf(f, "%d", &AUT[NAUT][v]) != 1) { ok = 0; break; }
                if (!ok) break;
                NAUT++;
            }
            fclose(f);
        }
        build_aut_levels();
        fprintf(stderr, "loaded %d automorphisms ", NAUT);
    }

    long long T0 = MODE_CERT ? ((long long)Q * Q) / 25 : 0;
    g_T = T0;

    std::vector<uint32_t> seed;
    { int a1[32]; for (int v = 0; v < N; v++) a1[v] = 1;
      std::vector<std::pair<long long, uint32_t> > all;
      for (uint32_t S = 0; S < (1u << (N - 1)); S++) all.push_back(std::make_pair(Qcut(a1, S), S));
      std::sort(all.begin(), all.end());
      for (size_t j = 0; j < all.size() && (int)seed.size() < APOOL; j++) seed.push_back(all[j].second);
    }
    while ((int)seed.size() < APOOL) seed.push_back(0);
    for (int p = 0; p < APOOL; p++) build_mono(p, seed[p]);

    long long gbest = -1; int gbesta[32]; memset(gbesta, 0, sizeof gbesta);
    long long gvio = 0; int gvioa[32]; memset(gvioa, 0, sizeof gvioa);

    std::mutex mtx;
    std::atomic<int> next_t0(0);
    std::vector<std::thread> th;
    for (int tid = 0; tid < nthr; tid++) th.push_back(std::thread([&, tid]() {
        Ctx *Xp = new Ctx();
        Ctx &X = *Xp;
        for (int p = 0; p < APOOL; p++) X.cut[p] = seed[p];
        X.bestval = -1; X.violators = 0; X.T = T0; X.rng = 12345u + 7919u * tid;
        for (;;) {
            int t0 = next_t0.fetch_add(1);
            if (t0 > Q) break;
            if (!MODE_CERT) { std::lock_guard<std::mutex> lk(mtx); if (g_T > X.T) X.T = g_T; }
            for (int p = 0; p < APOOL; p++) {
                X.FF[p] = 0;
                for (int v = 0; v < N; v++) X.c[p][v] = 0;
            }
            X.a[0] = t0;
            if (NAUT && orbit_prune(X.a, 0)) continue;
            if (t0) for (int p = 0; p < APOOL; p++) {
                uint32_t nb = ADJ[0];
                while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
                    if (u > 0 && ((((X.cut[p] >> u) ^ (X.cut[p] >> 0)) & 1) == 0)) X.c[p][u] += t0; }
            }
            if (N == 1) continue;
            dfs(X, 1, Q - t0, mtx);
        }
        {
            std::lock_guard<std::mutex> lk(mtx);
            if (X.bestval > gbest) { gbest = X.bestval; memcpy(gbesta, X.besta, sizeof(int) * N); }
            if (X.violators) { gvio += X.violators; memcpy(gvioa, X.vio, sizeof(int) * N); }
        }
        delete Xp;
    }));
    for (auto &t : th) t.join();

    if (MODE_CERT) {
        printf("CERT n=%d q=%d T=floor(q^2/25)=%lld violators=%lld\n", N, Q, T0, gvio);
        if (gvio) { printf("VIOLATOR a ="); for (int v = 0; v < N; v++) printf(" %d", gvioa[v]); printf("\n"); }
    } else {
        if (gbest < 0) gbest = 0;
        printf("MAX n=%d q=%d M=%lld 25M=%lld q2=%d %s\n", N, Q, gbest, 25 * gbest, Q * Q,
               (25 * gbest <= (long long)Q * Q) ? "OK" : "***REFUTATION***");
        printf("ARGMAX a ="); for (int v = 0; v < N; v++) printf(" %d", gbesta[v]); printf("\n");
    }
    return 0;
}
