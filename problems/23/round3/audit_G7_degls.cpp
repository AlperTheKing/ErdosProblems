// audit_G7_degls.cpp -- LOWER bounds on  Psi(H,1/3) = sup{psi(H,x): (Ax)_v > 1/3}
// by randomised local search over integer weightings a >= 0, sum a = q, with
// 3*(A a)_v > q, maximising bip(H[a]) = min over ALL cuts of Q_S(a).
// Exact int64.  A hit is only ever a LOWER bound on Psi -- which is exactly the
// point: G7.md claims Psi(Gamma_3,1/3) has ~9% slack below 1/25 on the strength
// of a finite-q search, and a finite-q search can only bound Psi from BELOW.
//
// usage: audit_G7_degls <n> <edges> <q> <restarts> [seed]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>

static int N, NE;
static int EU[512], EV[512];
static std::vector<int> ADJ[40];
static int NCUT;
static std::vector<std::vector<std::pair<int,int> > > MONO;
static int Q;

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
    for (int v = 0; v < N; v++) {
        long long d = 0;
        for (size_t j = 0; j < ADJ[v].size(); j++) d += a[ADJ[v][j]];
        if (3 * d <= Q) return false;
    }
    return true;
}

static unsigned long long rs = 88172645463325252ULL;
static unsigned long long rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

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
    Q = atoi(argv[3]);
    int restarts = atoi(argv[4]);
    if (argc > 5) rs = (unsigned long long)atoll(argv[5]) * 2654435761ULL + 1;

    NCUT = 1 << (N - 1);
    MONO.assign(NCUT, std::vector<std::pair<int,int> >());
    for (int s = 0; s < NCUT; s++)
        for (int e = 0; e < NE; e++)
            if ((((s >> EU[e]) ^ (s >> EV[e])) & 1) == 0)
                MONO[s].push_back(std::make_pair(EU[e], EV[e]));

    int a[40], besta[40];
    long long gbest = -1;
    for (int r = 0; r < restarts; r++) {
        // random feasible start: uniform + random perturbation, repaired
        for (int v = 0; v < N; v++) a[v] = Q / N;
        int rem = Q - (Q / N) * N;
        for (int t = 0; t < rem; t++) a[rnd() % N]++;
        for (int t = 0; t < 200; t++) {
            int i = rnd() % N, j = rnd() % N;
            if (i == j || a[i] == 0) continue;
            int amt = 1 + (int)(rnd() % 3);
            if (a[i] < amt) continue;
            a[i] -= amt; a[j] += amt;
            if (!feas(a)) { a[i] += amt; a[j] -= amt; }
        }
        if (!feas(a)) continue;
        long long cur = bip(a);
        bool improved = true;
        while (improved) {
            improved = false;
            for (int i = 0; i < N && !improved; i++)
                for (int j = 0; j < N && !improved; j++) {
                    if (i == j) continue;
                    for (int amt = 1; amt <= 3 && !improved; amt++) {
                        if (a[i] < amt) break;
                        a[i] -= amt; a[j] += amt;
                        if (feas(a)) {
                            long long v = bip(a);
                            if (v > cur) { cur = v; improved = true; break; }
                        }
                        a[i] += amt; a[j] -= amt;
                    }
                }
        }
        if (cur > gbest) {
            gbest = cur; memcpy(besta, a, sizeof(int) * N);
            printf("  q=%d new best M_deg>=%lld  25M/q^2=%.9f  a=", Q, gbest,
                   25.0 * gbest / ((double)Q * Q));
            for (int v = 0; v < N; v++) printf("%d ", besta[v]);
            printf("\n"); fflush(stdout);
        }
    }
    printf("RESULT q=%d Mdeg_lower=%lld 25M=%lld q2=%lld ratio=%.9f arg=",
           Q, gbest, 25 * gbest, (long long)Q * Q, 25.0 * gbest / ((double)Q * Q));
    for (int v = 0; v < N; v++) printf("%d ", besta[v]);
    printf("\n");
    return 0;
}
