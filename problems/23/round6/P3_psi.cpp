// P3_psi.cpp -- exhaustive EXACT-INTEGER lower bound on max_x psi for the Vega graphs.
//
// psi(H,a/q) = min over cuts S of sum_{uv monochromatic} a_u a_v / q^2.
// Erdos 23 (blow-up form) says psi <= 1/25 for every triangle-free H and every x.
// For an integer weighting a with sum q this is the exact integer inequality
//        DEN * mono_S(a) <= NUM * q * q          with (NUM,DEN) = (1,25)
// for SOME cut S.  This program enumerates EVERY integer weighting a >= 0 with sum a = q
// (zeros allowed), reduced by Aut(H), and for each one exhibits such a cut, or reports a
// violation.  All arithmetic is exact 64-bit integer; no floating point on any acceptance path.
//
// Certification pipeline per weighting:
//   1. try the cuts already in the per-thread cache (cheap: cost = #monochromatic edges)
//   2. local-search max-cut (a few restarts) -> new cut, cached on success
//   3. EXACT: enumerate all 2^(s-1) cuts of the support (s = |support| <= min(n,q)),
//      compute the true min monochromatic mass = bip(a).  This is the definitive answer.
//
// Usage: P3_psi <input.txt> <graphname|ALL> <q> [threads] [mode] [NUM] [DEN] [maxn]
//   mode = LT  (default) certify only when DEN*mono <  NUM*q*q  -> the exact path is taken by
//                        every weighting with psi >= 1/25, so equality cases are censused
//   mode = LE            certify when DEN*mono <= NUM*q*q       -> faster, only violations
//                        reach the exact path
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

struct Graph {
    string name;
    int i, n, m;
    vector<int> eu, ev;
    vector<string> role;
    vector<vector<int> > auts;
    vector<long long> weight;
    uint32_t adj[MAXN];
};

static vector<Graph> GS;

static void readInput(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    char buf[1 << 16];
    Graph* g = 0;
    while (fgets(buf, sizeof(buf), f)) {
        if (!strncmp(buf, "NAME", 4)) {
            GS.push_back(Graph());
            g = &GS.back();
            char nm[128]; int ii, nn, mm;
            sscanf(buf, "NAME %s %d %d %d", nm, &ii, &nn, &mm);
            g->name = nm; g->i = ii; g->n = nn; g->m = mm;
            for (int k = 0; k < MAXN; k++) g->adj[k] = 0;
        } else if (!strncmp(buf, "EDGES", 5)) {
            char* p = buf + 5;
            for (int k = 0; k < g->m; k++) {
                int a, b; int c;
                sscanf(p, "%d %d%n", &a, &b, &c); p += c;
                g->eu.push_back(a); g->ev.push_back(b);
                g->adj[a] |= 1u << b; g->adj[b] |= 1u << a;
            }
        } else if (!strncmp(buf, "ROLE", 4)) {
            char* p = buf + 4;
            for (int k = 0; k < g->n; k++) {
                char t[32]; int c;
                sscanf(p, "%s%n", t, &c); p += c;
                g->role.push_back(t);
            }
        } else if (!strncmp(buf, "AUT", 3)) {
            int k; sscanf(buf, "AUT %d", &k);
            for (int j = 0; j < k; j++) {
                if (!fgets(buf, sizeof(buf), f)) break;
                vector<int> p(g->n); char* q = buf;
                for (int t = 0; t < g->n; t++) { int c; sscanf(q, "%d%n", &p[t], &c); q += c; }
                g->auts.push_back(p);
            }
        } else if (!strncmp(buf, "WEIGHT", 6)) {
            char* p = buf + 6;
            for (int k = 0; k < g->n; k++) { long long v; int c; sscanf(p, "%lld%n", &v, &c); p += c; g->weight.push_back(v); }
        }
    }
    fclose(f);
}

struct Cut {
    uint32_t mask;
    vector<uint8_t> eu, ev;   // monochromatic edges of this cut
    long long hits;
};

struct Result {
    long long leaves, processed, certCache, certLS, exact, eq, gt, ltCount;
    long long maxExactBip;
    vector<vector<int> > violations, equalities;
    vector<int> maxWit;
    Result() : leaves(0), processed(0), certCache(0), certLS(0), exact(0), eq(0), gt(0),
               ltCount(0), maxExactBip(-1) {}
};

struct Worker {
    const Graph* g;
    int q, n;
    long long NUM, DEN;
    bool strictMode;      // true = LT
    vector<Cut> cache;
    Result R;
    int a[MAXN];
    // scratch for exact
    int sup[MAXN], supIdx[MAXN];
    int seu[512], sev[512];
    long long sw[512];

    inline bool certify(long long mono) const {
        long long lhs = DEN * mono, rhs = NUM * (long long)q * (long long)q;
        return strictMode ? (lhs < rhs) : (lhs <= rhs);
    }

    inline long long monoOf(const Cut& C) const {
        long long s = 0;
        int k = (int)C.eu.size();
        for (int t = 0; t < k; t++) s += (long long)a[C.eu[t]] * a[C.ev[t]];
        return s;
    }

    long long monoOfMask(uint32_t mask) const {
        long long s = 0;
        for (int t = 0; t < g->m; t++) {
            int u = g->eu[t], v = g->ev[t];
            if (((mask >> u) & 1u) == ((mask >> v) & 1u)) s += (long long)a[u] * a[v];
        }
        return s;
    }

    void addCut(uint32_t mask) {
        Cut C; C.mask = mask; C.hits = 0;
        for (int t = 0; t < g->m; t++) {
            int u = g->eu[t], v = g->ev[t];
            if (((mask >> u) & 1u) == ((mask >> v) & 1u)) { C.eu.push_back((uint8_t)u); C.ev.push_back((uint8_t)v); }
        }
        for (size_t k = 0; k < cache.size(); k++) if (cache[k].mask == mask) return;
        if (cache.size() >= 40) {
            // drop the least used
            size_t worst = 0; for (size_t k = 1; k < cache.size(); k++) if (cache[k].hits < cache[worst].hits) worst = k;
            cache[worst] = C;
        } else cache.push_back(C);
    }

    // local-search max-cut; returns best (smallest) monochromatic mass found and its mask
    long long localSearch(uint32_t& bestMask, uint64_t& rng) {
        long long best = -1; bestMask = 0;
        long long nbr[MAXN];
        for (int rep = 0; rep < 4; rep++) {
            uint32_t mask;
            if (rep == 0 && !cache.empty()) mask = cache[0].mask;
            else { rng = rng * 6364136223846793005ULL + 1442695040888963407ULL; mask = (uint32_t)(rng >> 20) & ((1u << n) - 1); }
            // nbr[v] = mass of neighbours of v on v's own side
            for (int v = 0; v < n; v++) {
                long long s = 0; uint32_t A = g->adj[v];
                uint32_t same = (((mask >> v) & 1u) ? mask : ~mask) & ((1u << n) - 1);
                uint32_t t = A & same;
                while (t) { int u = __builtin_ctz(t); t &= t - 1; s += a[u]; }
                nbr[v] = s;
            }
            bool improved = true;
            while (improved) {
                improved = false;
                for (int v = 0; v < n; v++) {
                    if (a[v] == 0) continue;
                    // flipping v changes mono by a_v*(otherSideMass - sameSideMass)
                    long long tot = 0; uint32_t t = g->adj[v];
                    while (t) { int u = __builtin_ctz(t); t &= t - 1; tot += a[u]; }
                    long long delta = (long long)a[v] * (tot - 2 * nbr[v]);
                    if (delta < 0) {
                        mask ^= (1u << v);
                        uint32_t s2 = g->adj[v];
                        while (s2) { int u = __builtin_ctz(s2); s2 &= s2 - 1;
                            if (((mask >> u) & 1u) == ((mask >> v) & 1u)) nbr[u] += a[v]; else nbr[u] -= a[v]; }
                        nbr[v] = tot - nbr[v];
                        improved = true;
                    }
                }
            }
            long long mm = monoOfMask(mask);
            if (best < 0 || mm < best) { best = mm; bestMask = mask; }
            if (certify(best)) break;
        }
        return best;
    }

    // exact min over all cuts, restricted to the support
    long long exactBip(uint32_t& bestMask) {
        int s = 0;
        for (int v = 0; v < n; v++) if (a[v] > 0) { supIdx[v] = s; sup[s++] = v; } else supIdx[v] = -1;
        int me = 0;
        for (int t = 0; t < g->m; t++) {
            int u = g->eu[t], v = g->ev[t];
            if (a[u] > 0 && a[v] > 0) { seu[me] = supIdx[u]; sev[me] = supIdx[v]; sw[me] = (long long)a[u] * a[v]; me++; }
        }
        long long best = -1; uint32_t bm = 0;
        uint32_t lim = (s <= 1) ? 1u : (1u << (s - 1));
        for (uint32_t mask = 0; mask < lim; mask++) {
            long long tot = 0;
            for (int t = 0; t < me; t++) if (((mask >> seu[t]) & 1u) == ((mask >> sev[t]) & 1u)) tot += sw[t];
            if (best < 0 || tot < best) { best = tot; bm = mask; }
        }
        uint32_t full = 0;
        for (int k = 0; k < s; k++) if ((bm >> k) & 1u) full |= 1u << sup[k];
        bestMask = full;
        return best < 0 ? 0 : best;
    }

    bool lexMin() const {
        for (size_t k = 0; k < g->auts.size(); k++) {
            const vector<int>& p = g->auts[k];
            for (int t = 0; t < n; t++) {
                int x = a[p[t]], y = a[t];
                if (x < y) return false;
                if (x > y) break;
            }
        }
        return true;
    }

    uint64_t rng;

    void leaf() {
        R.leaves++;
        if (!lexMin()) return;
        R.processed++;
        // 1. cache
        for (size_t k = 0; k < cache.size(); k++) {
            long long mm = monoOf(cache[k]);
            if (certify(mm)) {
                cache[k].hits++;
                if (k > 0 && cache[k].hits > cache[k - 1].hits) swap(cache[k], cache[k - 1]);
                R.certCache++; return;
            }
        }
        // 2. local search
        uint32_t mask;
        long long ls = localSearch(mask, rng);
        if (certify(ls)) { addCut(mask); R.certLS++; return; }
        // 3. exact
        R.exact++;
        uint32_t bm;
        long long bip = exactBip(bm);
        addCut(bm);
        long long lhs = DEN * bip, rhs = NUM * (long long)q * (long long)q;
        if (bip > R.maxExactBip) { R.maxExactBip = bip; R.maxWit.assign(a, a + n); }
        if (lhs > rhs) { R.gt++; if (R.violations.size() < 50) R.violations.push_back(vector<int>(a, a + n)); }
        else if (lhs == rhs) { R.eq++; if (R.equalities.size() < 50) R.equalities.push_back(vector<int>(a, a + n)); }
        else R.ltCount++;
    }

    void rec(int d, int rem) {
        if (d == n - 1) { a[d] = rem; leaf(); return; }
        for (int t = rem; t >= 0; t--) { a[d] = t; rec(d + 1, rem - t); }
    }
};

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s <input> <name|ALL> <q> [threads] [LT|LE] [NUM] [DEN] [maxn]\n", argv[0]); return 1; }
    readInput(argv[1]);
    string want = argv[2];
    int q = atoi(argv[3]);
    int nthreads = argc > 4 ? atoi(argv[4]) : 8;
    bool strictMode = (argc > 5) ? (string(argv[5]) == "LT") : true;
    long long NUM = argc > 6 ? atoll(argv[6]) : 1;
    long long DEN = argc > 7 ? atoll(argv[7]) : 25;
    int maxn = argc > 8 ? atoi(argv[8]) : 64;

    for (size_t gi = 0; gi < GS.size(); gi++) {
        Graph& g = GS[gi];
        if (want != "ALL" && want != g.name) continue;
        if (g.n > maxn) continue;
        int n = g.n;
        // task list = prefixes of length P
        int P = 1;
        while (P < n - 1) {
            double cnt = 1; for (int k = 1; k <= P; k++) cnt = cnt * (q + k) / k;
            if (cnt >= 512) break;
            P++;
        }
        vector<vector<int> > tasks;
        {
            vector<int> cur(P, 0);
            // enumerate prefixes with sum <= q
            vector<int> stack;
            struct Gen {
                static void go(int d, int P, int rem, vector<int>& cur, vector<vector<int> >& out) {
                    if (d == P) { out.push_back(cur); return; }
                    for (int t = rem; t >= 0; t--) { cur[d] = t; go(d + 1, P, rem - t, cur, out); }
                }
            };
            Gen::go(0, P, q, cur, tasks);
        }
        atomic<size_t> next(0);
        vector<Result> res(nthreads);
        vector<thread> th;
        double t0 = (double)clock() / CLOCKS_PER_SEC;
        for (int t = 0; t < nthreads; t++) {
            th.push_back(thread([&, t]() {
                Worker W; W.g = &g; W.q = q; W.n = n; W.NUM = NUM; W.DEN = DEN;
                W.strictMode = strictMode; W.rng = 88172645463325252ULL + 1000003ULL * (t + 1);
                for (;;) {
                    size_t k = next.fetch_add(1);
                    if (k >= tasks.size()) break;
                    int s = 0;
                    for (int d = 0; d < P; d++) { W.a[d] = tasks[k][d]; s += tasks[k][d]; }
                    if (P == n - 1) { W.a[n - 1] = q - s; W.leaf(); }
                    else W.rec(P, q - s);
                }
                res[t] = W.R;
            }));
        }
        for (int t = 0; t < nthreads; t++) th[t].join();
        Result T;
        for (int t = 0; t < nthreads; t++) {
            T.leaves += res[t].leaves; T.processed += res[t].processed;
            T.certCache += res[t].certCache; T.certLS += res[t].certLS; T.exact += res[t].exact;
            T.eq += res[t].eq; T.gt += res[t].gt; T.ltCount += res[t].ltCount;
            if (res[t].maxExactBip > T.maxExactBip) { T.maxExactBip = res[t].maxExactBip; T.maxWit = res[t].maxWit; }
            for (size_t k = 0; k < res[t].violations.size() && T.violations.size() < 50; k++) T.violations.push_back(res[t].violations[k]);
            for (size_t k = 0; k < res[t].equalities.size() && T.equalities.size() < 50; k++) T.equalities.push_back(res[t].equalities[k]);
        }
        double t1 = (double)clock() / CLOCKS_PER_SEC;
        printf("GRAPH %s n=%d m=%d q=%d mode=%s thr=%d/%d | leaves=%lld orbitreps=%lld | certCache=%lld certLS=%lld exact=%lld | EQ=%lld GT=%lld | maxExactBip=%lld  q^2/25=%.4f | cpu=%.1fs\n",
               g.name.c_str(), n, g.m, q, strictMode ? "LT" : "LE", (int)NUM, (int)DEN, T.leaves, T.processed,
               T.certCache, T.certLS, T.exact, T.eq, T.gt, T.maxExactBip, q * q / 25.0, t1 - t0);
        for (size_t k = 0; k < T.violations.size(); k++) {
            printf("  VIOLATION a =");
            for (int v = 0; v < n; v++) printf(" %d", T.violations[k][v]);
            printf("\n");
        }
        for (size_t k = 0; k < T.equalities.size() && k < 12; k++) {
            printf("  EQUALITY  a =");
            for (int v = 0; v < n; v++) printf(" %d", T.equalities[k][v]);
            printf("\n");
        }
        if (T.eq > 12) printf("  ... %lld equality classes total\n", T.eq);
        fflush(stdout);
    }
    return 0;
}
