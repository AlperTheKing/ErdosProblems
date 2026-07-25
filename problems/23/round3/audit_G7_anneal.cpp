// audit_G7_anneal.cpp -- stronger LOWER-bound search for
//     Psi(H,c) = sup { psi(H,x) : x in simplex, (A x)_v > c }        (c = 1/3)
// and for the unrestricted max_x psi(H,x).
// Simulated annealing over integer weightings at a large fixed q (mesh 1/q),
// exact int64 objective bip(H[a]) = min over ALL cuts of Q_S(a).
// Used to test G7.md's claim that Psi(Gamma_3,1/3) has ~9% slack below 1/25.
//
// usage: audit_G7_anneal <n> <edges> <q> <deg|free> <iters> <restarts> [seed]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>

static int N, NE;
static int EU[512], EV[512];
static std::vector<int> ADJ[40];
static int NCUT;
static std::vector<std::vector<std::pair<int,int> > > MONO;
static long long Q;
static int DEG;

static long long bip(const int *a) {
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

static bool feas(const int *a) {
    if (!DEG) return true;
    for (int v = 0; v < N; v++) {
        long long d = 0;
        for (size_t j = 0; j < ADJ[v].size(); j++) d += a[ADJ[v][j]];
        if (3 * d <= Q) return false;
    }
    return true;
}

static unsigned long long rs = 88172645463325252ULL;
static unsigned long long rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static double rnd01() { return (double)(rnd() >> 11) / 9007199254740992.0; }

int main(int argc, char **argv) {
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
    Q = atoll(argv[3]);
    DEG = (strstr(argv[4], "deg") != NULL);
    long long iters = atoll(argv[5]);
    int restarts = atoi(argv[6]);
    if (argc > 7) rs = (unsigned long long)atoll(argv[7]) * 2654435761ULL + 12345;

    NCUT = 1 << (N - 1);
    MONO.assign(NCUT, std::vector<std::pair<int,int> >());
    for (int s = 0; s < NCUT; s++)
        for (int e = 0; e < NE; e++)
            if ((((s >> EU[e]) ^ (s >> EV[e])) & 1) == 0)
                MONO[s].push_back(std::make_pair(EU[e], EV[e]));

    int a[40], besta[40], cand[40];
    long long gbest = -1;
    for (int r = 0; r < restarts; r++) {
        for (int v = 0; v < N; v++) a[v] = (int)(Q / N);
        { long long rem = Q - (Q / N) * N; for (long long t = 0; t < rem; t++) a[rnd() % N]++; }
        while (!feas(a)) {              // repair (should not happen for regular H)
            int i = rnd() % N, j = rnd() % N;
            if (i == j || a[i] == 0) continue;
            a[i]--; a[j]++;
        }
        long long cur = bip(a);
        long long loc = cur; memcpy(cand, a, sizeof(int) * N);
        double T0 = (double)Q * Q / 2000.0;
        for (long long it = 0; it < iters; it++) {
            double T = T0 * (1.0 - (double)it / (double)iters) + 1e-9;
            int i = rnd() % N, j = rnd() % N;
            if (i == j) continue;
            int mx = a[i];
            if (mx == 0) continue;
            int amt = 1 + (int)(rnd() % (unsigned)std::max(1, std::min(mx, (int)(Q / 40) + 1)));
            a[i] -= amt; a[j] += amt;
            if (!feas(a)) { a[i] += amt; a[j] -= amt; continue; }
            long long v = bip(a);
            if (v >= cur || rnd01() < exp((double)(v - cur) / T)) {
                cur = v;
                if (v > loc) { loc = v; memcpy(cand, a, sizeof(int) * N); }
            } else { a[i] += amt; a[j] -= amt; }
        }
        // greedy polish from the best point seen
        memcpy(a, cand, sizeof(int) * N); cur = loc;
        bool imp = true;
        while (imp) {
            imp = false;
            for (int i = 0; i < N && !imp; i++)
                for (int j = 0; j < N && !imp; j++) {
                    if (i == j) continue;
                    for (int amt = 1; amt <= 4 && !imp; amt++) {
                        if (a[i] < amt) break;
                        a[i] -= amt; a[j] += amt;
                        if (feas(a)) { long long v = bip(a);
                            if (v > cur) { cur = v; imp = true; break; } }
                        a[i] += amt; a[j] -= amt;
                    }
                }
        }
        if (cur > gbest) { gbest = cur; memcpy(besta, a, sizeof(int) * N); }
    }
    printf("%s n=%d q=%lld Mlower=%lld 25M=%lld q2=%lld ratio=%.9f arg=",
           DEG ? "ANNEALDEG" : "ANNEAL", N, Q, gbest, 25 * gbest, Q * Q,
           25.0 * gbest / ((double)Q * (double)Q));
    for (int v = 0; v < N; v++) printf("%d ", besta[v]);
    printf("\n");
    return 0;
}
