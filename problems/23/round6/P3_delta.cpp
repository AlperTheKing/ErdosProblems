// P3_delta.cpp -- max psi over the DELTA-CONSTRAINED polytope.
//
// The Brandt-Thomasse reduction does NOT need max_x psi(H,x) over the whole simplex.  Unwinding it:
//   G triangle-free, delta(G) > n/3  ==>  G is a spanning subgraph of a maximal triangle-free G'
//   with the same or larger min degree; psi is monotone under adding edges; contracting the twin
//   classes of G' turns psi(G',uniform) into psi(H,omega) where (H,omega) is a twin-free maximal
//   triangle-free WEIGHTED graph with delta(H,omega) > 1/3, so H = Gamma_i or a Vega graph.
// Hence the delta > n/3 case of Erdos 23 needs only
//        psi(H,omega) <= 1/25   for omega in  P(H) = { omega >= 0 : sum omega = 1,
//                                                       omega(N(v)) > 1/3 for every v }.
// This program computes, exactly, the maximum of psi over the rational points of P(H) with
// denominator q, by exhaustive enumeration of integer weightings a >= 0 with sum a = q that
// satisfy 3*a(N(v)) > q for every v, and an exact min over all 2^(s-1) cuts of the support.
//
// Usage: P3_delta <input.txt> <name|ALL> <q> [threads] [maxn]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <atomic>
using namespace std;
static const int MAXN = 40;

struct Graph { string name; int i, n, m; vector<int> eu, ev; vector<string> role;
               vector<vector<int> > auts; uint32_t adj[MAXN]; vector<long long> weight; };
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
        } else if (!strncmp(buf, "AUT", 3)) { int k; sscanf(buf, "AUT %d", &k);
            for (int j = 0; j < k; j++) { if (!fgets(buf, sizeof(buf), f)) break; vector<int> p(g->n); char* q = buf;
                for (int t = 0; t < g->n; t++) { int c; sscanf(q, "%d%n", &p[t], &c); q += c; } g->auts.push_back(p); }
        } else if (!strncmp(buf, "WEIGHT", 6)) { char* p = buf + 6;
            for (int k = 0; k < g->n; k++) { long long v; int c; sscanf(p, "%lld%n", &v, &c); p += c; g->weight.push_back(v); } }
    }
    fclose(f);
}

struct Res { long long leaves, feas, reps; long long maxBip; vector<int> arg;
             Res() : leaves(0), feas(0), reps(0), maxBip(-1) {} };

struct W {
    const Graph* g; int q, n; Res R; int a[MAXN];
    int sup[MAXN], supIdx[MAXN]; int seu[600], sev[600]; long long sw[600];
    long long exactBip() {
        int s = 0; for (int v = 0; v < n; v++) if (a[v] > 0) { supIdx[v] = s; sup[s++] = v; } else supIdx[v] = -1;
        int me = 0;
        for (int t = 0; t < g->m; t++) { int u = g->eu[t], v = g->ev[t];
            if (a[u] > 0 && a[v] > 0) { seu[me] = supIdx[u]; sev[me] = supIdx[v]; sw[me] = (long long)a[u] * a[v]; me++; } }
        long long best = -1; uint32_t lim = (s <= 1) ? 1u : (1u << (s - 1));
        for (uint32_t mask = 0; mask < lim; mask++) { long long tot = 0;
            for (int t = 0; t < me; t++) if (((mask >> seu[t]) & 1u) == ((mask >> sev[t]) & 1u)) tot += sw[t];
            if (best < 0 || tot < best) best = tot; }
        return best < 0 ? 0 : best;
    }
    bool lexMin() const { for (size_t k = 0; k < g->auts.size(); k++) { const vector<int>& p = g->auts[k];
            for (int t = 0; t < n; t++) { int x = a[p[t]], y = a[t]; if (x < y) return false; if (x > y) break; } } return true; }
    bool feasible() const {
        for (int v = 0; v < n; v++) { long long s = 0; uint32_t t = g->adj[v];
            while (t) { int u = __builtin_ctz(t); t &= t - 1; s += a[u]; }
            if (3 * s <= q) return false; }
        return true;
    }
    void leaf() { R.leaves++; if (!feasible()) return; R.feas++; if (!lexMin()) return; R.reps++;
        long long bp = exactBip(); if (bp > R.maxBip) { R.maxBip = bp; R.arg.assign(a, a + n); } }
    // prune: at depth d, vertex v can still reach at most (assigned nbr mass) + rem if it has a free nbr
    bool prune(int d, int rem) const {
        uint32_t assignedMask = (d >= 32) ? 0xffffffffu : ((1u << d) - 1);
        for (int v = 0; v < n; v++) { long long s = 0; uint32_t t = g->adj[v] & assignedMask;
            while (t) { int u = __builtin_ctz(t); t &= t - 1; s += a[u]; }
            long long cap = s + ((g->adj[v] & ~assignedMask) ? rem : 0);
            if (3 * cap <= q) return true; }
        return false;
    }
    void rec(int d, int rem) {
        if (d == n - 1) { a[d] = rem; leaf(); return; }
        if (prune(d, rem)) { R.leaves += 0; return; }
        for (int t = rem; t >= 0; t--) { a[d] = t; rec(d + 1, rem - t); }
    }
};

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s <input> <name|ALL> <q> [threads] [maxn]\n", argv[0]); return 1; }
    readInput(argv[1]); string want = argv[2]; int q = atoi(argv[3]);
    int nthreads = argc > 4 ? atoi(argv[4]) : 8; int maxn = argc > 5 ? atoi(argv[5]) : 64;
    for (size_t gi = 0; gi < GS.size(); gi++) {
        Graph& g = GS[gi]; if (want != "ALL" && want != g.name) continue; if (g.n > maxn) continue;
        int n = g.n;
        int P = 1; while (P < n - 1) { double cnt = 1; for (int k = 1; k <= P; k++) cnt = cnt * (q + k) / k; if (cnt >= 512) break; P++; }
        vector<vector<int> > tasks; { vector<int> cur(P, 0);
            struct Gen { static void go(int d, int P, int rem, vector<int>& cur, vector<vector<int> >& out) {
                if (d == P) { out.push_back(cur); return; }
                for (int t = rem; t >= 0; t--) { cur[d] = t; go(d + 1, P, rem - t, cur, out); } } };
            Gen::go(0, P, q, cur, tasks); }
        atomic<size_t> next(0); vector<Res> res(nthreads); vector<thread> th;
        double t0 = (double)clock() / CLOCKS_PER_SEC;
        for (int t = 0; t < nthreads; t++) th.push_back(thread([&, t]() {
            W ww; ww.g = &g; ww.q = q; ww.n = n;
            for (;;) { size_t k = next.fetch_add(1); if (k >= tasks.size()) break;
                int s = 0; for (int d = 0; d < P; d++) { ww.a[d] = tasks[k][d]; s += tasks[k][d]; }
                if (P == n - 1) { ww.a[n - 1] = q - s; ww.leaf(); } else ww.rec(P, q - s); }
            res[t] = ww.R; }));
        for (int t = 0; t < nthreads; t++) th[t].join();
        Res T; for (int t = 0; t < nthreads; t++) { T.leaves += res[t].leaves; T.feas += res[t].feas; T.reps += res[t].reps;
            if (res[t].maxBip > T.maxBip) { T.maxBip = res[t].maxBip; T.arg = res[t].arg; } }
        double t1 = (double)clock() / CLOCKS_PER_SEC;
        printf("DELTA %-12s n=%2d m=%3d q=%3d | visited=%lld feasible=%lld orbitreps=%lld | maxBip=%lld  psi=%lld/%d=%.7f  (1/25=0.04)  %s | cpu=%.1fs\n",
               g.name.c_str(), n, g.m, q, T.leaves, T.feas, T.reps, T.maxBip, T.maxBip, q * q,
               T.maxBip < 0 ? 0.0 : (double)T.maxBip / (q * q),
               (T.maxBip >= 0 && 25 * T.maxBip > (long long)q * q) ? "*** EXCEEDS 1/25 ***" : "<= 1/25", t1 - t0);
        if (T.maxBip >= 0) { printf("   argmax a =");
            for (int v = 0; v < n; v++) printf(" %d", T.arg[v]);
            printf("   roles ="); for (int v = 0; v < n; v++) printf(" %s", g.role[v].c_str());
            printf("\n"); }
        fflush(stdout);
    }
    return 0;
}
