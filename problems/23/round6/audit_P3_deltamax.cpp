// audit_P3_deltamax.cpp -- adversarial attack on P3.md claim (e):
//   "max psi over the delta>1/3 polytope P(H) is attained at the paper's regular weight function;
//    the maximum over the whole Vega family is 29/841; V1' has a uniform 13.8% margin."
//
// P3's own DELTA engine was run ONLY on the four i=2 graphs, at denominators 29/58/87/116 (and
// 32/64, 35/70), and produced no log file.  For i >= 3 only the single point omega_reg was ever
// evaluated.  This program searches P(H) at a MUCH finer denominator D by hill-climbing on the
// exact bip (Gray-code over all 2^(n-1) cuts, pre-filtered by a pool of good cuts), for every
// Vega graph with n <= NMAX, and reports the best psi found together with 29/841 and 1/25.
//
// usage: audit_P3_deltamax <input.txt> <name|ALL> <D> <restarts> [threads] [nmax]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;
static const int MAXN = 40;

struct Graph { string name; int i, n, m; vector<int> eu, ev; vector<string> role;
               vector<long long> weight; uint32_t adj[MAXN]; };
static vector<Graph> GS;

static void readInput(const char* path) {
    FILE* f = fopen(path, "r"); if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    static char buf[1 << 16]; Graph* g = 0;
    while (fgets(buf, sizeof(buf), f)) {
        if (!strncmp(buf, "NAME", 4)) { GS.push_back(Graph()); g = &GS.back();
            char nm[128]; int ii, nn, mm; sscanf(buf, "NAME %s %d %d %d", nm, &ii, &nn, &mm);
            g->name = nm; g->i = ii; g->n = nn; g->m = mm;
            for (int k = 0; k < MAXN; k++) g->adj[k] = 0;
        } else if (!strncmp(buf, "EDGES", 5)) { char* p = buf + 5;
            for (int k = 0; k < g->m; k++) { int a, b, c; sscanf(p, "%d %d%n", &a, &b, &c); p += c;
                g->eu.push_back(a); g->ev.push_back(b); g->adj[a] |= 1u << b; g->adj[b] |= 1u << a; }
        } else if (!strncmp(buf, "ROLE", 4)) { char* p = buf + 4;
            for (int k = 0; k < g->n; k++) { char t[32]; int c; sscanf(p, "%s%n", t, &c); p += c; g->role.push_back(t); }
        } else if (!strncmp(buf, "WEIGHT", 6)) { char* p = buf + 6;
            for (int k = 0; k < g->n; k++) { long long v; int c; sscanf(p, "%lld%n", &v, &c); p += c; g->weight.push_back(v); } }
    }
    fclose(f);
}

struct Ctx {
    const Graph* g; int n; long long D;
    vector<uint32_t> pool;
    long long monoOf(const vector<long long>& a, uint32_t mask) const {
        long long s = 0;
        for (int e = 0; e < g->m; e++) { int u = g->eu[e], v = g->ev[e];
            if (((mask >> u) & 1u) == ((mask >> v) & 1u)) s += a[u] * a[v]; }
        return s;
    }
    long long poolMin(const vector<long long>& a) const {
        long long b = -1;
        for (size_t k = 0; k < pool.size(); k++) { long long s = monoOf(a, pool[k]); if (b < 0 || s < b) b = s; }
        return b;
    }
    // exact bip over all 2^(n-1) cuts (Gray code, single thread)
    long long exactBip(const vector<long long>& a, uint32_t& argm) const {
        vector<long long> same(n, 0), tot(n, 0);
        uint32_t mask = 0;
        for (int v = 0; v < n; v++) { uint32_t s = g->adj[v];
            while (s) { int u = __builtin_ctz(s); s &= s - 1; tot[v] += a[u]; same[v] += a[u]; } }
        long long cur = 0;
        for (int e = 0; e < g->m; e++) cur += a[g->eu[e]] * a[g->ev[e]];
        long long b = cur; uint32_t bm = 0;
        long long lim = 1LL << (n - 1);
        for (long long k = 1; k < lim; k++) {
            int v = __builtin_ctzll((unsigned long long)k);
            cur += a[v] * (tot[v] - 2 * same[v]);
            mask ^= (1u << v);
            uint32_t s = g->adj[v];
            while (s) { int u = __builtin_ctz(s); s &= s - 1;
                if (((mask >> u) & 1u) == ((mask >> v) & 1u)) same[u] += a[v]; else same[u] -= a[v]; }
            same[v] = tot[v] - same[v];
            if (cur < b) { b = cur; bm = mask; }
        }
        argm = bm; return b;
    }
    bool feasible(const vector<long long>& a) const {
        for (int v = 0; v < n; v++) { long long s = 0; uint32_t t = g->adj[v];
            while (t) { int u = __builtin_ctz(t); t &= t - 1; s += a[u]; }
            if (3 * s <= D) return false; }
        return true;
    }
};

static long long gcdll(long long x, long long y) { while (y) { long long t = x % y; x = y; y = t; } return x < 0 ? -x : x; }

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s <input> <name|ALL> <D> <restarts> [threads] [nmax]\n", argv[0]); return 1; }
    readInput(argv[1]);
    string want = argv[2]; long long MULT = atoll(argv[3]); int restarts = atoi(argv[4]);
    int nthreads = argc > 5 ? atoi(argv[5]) : 8; int nmax = argc > 6 ? atoi(argv[6]) : 19;
    printf("target thresholds: 29/841 = %.9f   1/25 = %.9f   denominator = %lld x (paper total)\n",
           29.0 / 841.0, 0.04, MULT);
    for (size_t gi = 0; gi < GS.size(); gi++) {
        Graph& g = GS[gi];
        if (want != "ALL" && want != g.name) continue;
        if (g.n > nmax) continue;
        int n = g.n;
        long long wtot = 0; for (int v = 0; v < n; v++) wtot += g.weight[v];
        long long D = MULT * wtot;
        // scale the regular weight to denominator D (D should be a multiple of wtot)
        vector<long long> areg(n);
        for (int v = 0; v < n; v++) areg[v] = g.weight[v] * D / wtot;
        long long s0 = 0; for (int v = 0; v < n; v++) s0 += areg[v];
        areg[0] += D - s0;
        Ctx c0; c0.g = &g; c0.n = n; c0.D = D;
        bool regFeas = c0.feasible(areg);
        uint32_t am; long long bipreg = c0.exactBip(areg, am);
        atomic<long long> bestGlobal(bipreg);
        mutex mtx; vector<long long> bestA = areg;
        atomic<int> next(0);
        vector<thread> th;
        for (int t = 0; t < nthreads; t++) th.push_back(thread([&, t]() {
            Ctx c; c.g = &g; c.n = n; c.D = D;
            uint64_t rs = 0x9E3779B97F4A7C15ULL + 1000003ULL * (t + 1) + 7919ULL * gi;
            auto rnd = [&]() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; };
            vector<long long> a(n);
            uint32_t dummy;
            c.pool.push_back(am);
            for (;;) {
                int r = next.fetch_add(1); if (r >= restarts) break;
                a = areg;
                if (r > 0) {            // random feasible perturbation of the regular point
                    for (int tries = 0; tries < 4000; tries++) {
                        vector<long long> b = areg;
                        int nm2 = 1 + (int)(rnd() % 8);
                        for (int k = 0; k < nm2; k++) {
                            int i2 = (int)(rnd() % n), j2 = (int)(rnd() % n);
                            long long amt = 1 + (long long)(rnd() % (unsigned long long)max(1LL, D / 40));
                            if (b[i2] >= amt) { b[i2] -= amt; b[j2] += amt; }
                        }
                        if (c.feasible(b)) { a = b; break; }
                    }
                }
                long long cur = c.exactBip(a, dummy);
                { lock_guard<mutex> lk(mtx); if (cur > bestGlobal) { bestGlobal = cur; bestA = a; } }
                long long step = max(1LL, D / 40);
                for (int it = 0; it < 6000; it++) {
                    int i2 = (int)(rnd() % n), j2 = (int)(rnd() % n);
                    if (i2 == j2) continue;
                    long long amt = 1 + (long long)(rnd() % (unsigned long long)step);
                    if (a[i2] < amt) continue;
                    a[i2] -= amt; a[j2] += amt;
                    bool ok = c.feasible(a);
                    long long v = ok ? c.poolMin(a) : -1;
                    if (ok && v >= cur) {                 // pool says promising -> exact check
                        uint32_t bm; long long ex = c.exactBip(a, bm);
                        if (c.pool.size() < 200) c.pool.push_back(bm);
                        if (ex >= cur) { cur = ex;
                            if (ex > bestGlobal) { lock_guard<mutex> lk(mtx); if (ex > bestGlobal) { bestGlobal = ex; bestA = a; } }
                            continue; }
                    }
                    a[i2] += amt; a[j2] -= amt;           // revert
                    if (it % 800 == 799 && step > 1) step = max(1LL, step * 3 / 4);
                }
            }
        }));
        for (int t = 0; t < nthreads; t++) th[t].join();
        long long B = bestGlobal;
        long long gg = gcdll(B, D * D);
        printf("%-12s n=%2d | reg feasible=%s  psi(reg)=%lld/%lld=%.9f | BEST over P(H) at D=%lld: "
               "%lld/%lld = %.9f | > 29/841 ? %s | > 1/25 ? %s\n",
               g.name.c_str(), n, regFeas ? "yes" : "NO", bipreg, D * D, (double)bipreg / (double)(D * D),
               D, gg ? B / gg : B, gg ? D * D / gg : D * D, (double)B / (double)(D * D),
               (841.0 * B > 29.0 * D * D) ? "*** YES ***" : "no",
               (25 * B > D * D) ? "*** YES -- ERDOS 23 VIOLATION ***" : "no");
        if (841.0 * B > 29.0 * (double)D * D) {
            printf("   witness a ="); for (int v = 0; v < n; v++) printf(" %lld", bestA[v]);
            printf("   roles ="); for (int v = 0; v < n; v++) printf(" %s", g.role[v].c_str());
            printf("\n");
        }
        fflush(stdout);
    }
    return 0;
}
