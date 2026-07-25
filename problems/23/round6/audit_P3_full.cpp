// audit_P3_full.cpp -- exact bip at FULL-SUPPORT weightings, which P3.md never tested.
//
// P3's exhaustive runs use q <= 14 (n=11) down to q = 8 (n=31).  Since the support of an integer
// weighting of total q has at most q atoms, NO weighting with more than 14 non-zero vertices was
// ever tested on ANY Vega graph, and for i >= 5 the uniform weighting (q = n) was never tested at
// all.  This program computes the exact bip by a Gray-code walk over all 2^(n-1) cuts -- no local
// search, no cut cache, no automorphism reduction, no support restriction -- for
//   (1) the uniform weighting a_v = 1,
//   (2) the paper's regular weight function,
//   (3) random weightings with FULL support,
// and compares against the ARCPLUS minimum (P3's claimed exact family) and against 1/25.
//
// usage: audit_P3_full <input.txt> <name|ALL> <UNIFORM|REGULAR|RAND:k:q> [threads]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <set>
#include <algorithm>
#include <thread>
#include <atomic>
using namespace std;
static const int MAXN = 40;

struct Graph {
    string name; int i, n, m;
    vector<int> eu, ev; vector<string> role; vector<long long> weight;
    uint32_t adj[MAXN]; int L; int posOf[MAXN]; int vtxAt[MAXN]; vector<int> specials;
};
static vector<Graph> GS;

static void readInput(const char* path) {
    FILE* f = fopen(path, "r"); if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    static char buf[1 << 16]; Graph* g = 0;
    while (fgets(buf, sizeof(buf), f)) {
        if (!strncmp(buf, "NAME", 4)) {
            GS.push_back(Graph()); g = &GS.back();
            char nm[128]; int ii, nn, mm; sscanf(buf, "NAME %s %d %d %d", nm, &ii, &nn, &mm);
            g->name = nm; g->i = ii; g->n = nn; g->m = mm; g->L = 3 * ii - 1;
            for (int k = 0; k < MAXN; k++) { g->adj[k] = 0; g->posOf[k] = -1; g->vtxAt[k] = -1; }
        } else if (!strncmp(buf, "EDGES", 5)) {
            char* p = buf + 5;
            for (int k = 0; k < g->m; k++) { int a, b, c; sscanf(p, "%d %d%n", &a, &b, &c); p += c;
                g->eu.push_back(a); g->ev.push_back(b); g->adj[a] |= 1u << b; g->adj[b] |= 1u << a; }
        } else if (!strncmp(buf, "ROLE", 4)) {
            char* p = buf + 4;
            for (int k = 0; k < g->n; k++) { char t[32]; int c; sscanf(p, "%s%n", t, &c); p += c;
                g->role.push_back(t);
                if (t[0] >= '0' && t[0] <= '9') { int pos = atoi(t); g->posOf[k] = pos; g->vtxAt[pos] = k; }
                else g->specials.push_back(k); }
        } else if (!strncmp(buf, "WEIGHT", 6)) {
            char* p = buf + 6;
            for (int k = 0; k < g->n; k++) { long long v; int c; sscanf(p, "%lld%n", &v, &c); p += c; g->weight.push_back(v); }
        }
    }
    fclose(f);
}

// ---- exact bip by Gray-code over all 2^(n-1) cuts, split over threads by the top bits
static long long exactBipGray(const Graph& g, const vector<long long>& a, int nthreads, uint32_t& argMask) {
    int n = g.n;
    int freeBits = n - 1;                 // vertex n-1 fixed on side 0
    int topBits = 0; while ((1 << topBits) < nthreads && topBits < freeBits) topBits++;
    int lowBits = freeBits - topBits;
    vector<long long> best(1 << topBits, -1);
    vector<uint32_t> bestM(1 << topBits, 0);
    atomic<int> next(0);
    vector<thread> th;
    for (int t = 0; t < nthreads; t++) th.push_back(thread([&]() {
        for (;;) {
            int blk = next.fetch_add(1); if (blk >= (1 << topBits)) break;
            // initial mask for this block: low bits 0, top bits = blk
            uint32_t mask = ((uint32_t)blk) << lowBits;
            vector<long long> same(n, 0), tot(n, 0);
            for (int v = 0; v < n; v++) { uint32_t s = g.adj[v];
                while (s) { int u = __builtin_ctz(s); s &= s - 1; tot[v] += a[u];
                    if (((mask >> u) & 1u) == ((mask >> v) & 1u)) same[v] += a[u]; } }
            long long cur = 0;
            for (int e = 0; e < g.m; e++) { int u = g.eu[e], v = g.ev[e];
                if (((mask >> u) & 1u) == ((mask >> v) & 1u)) cur += a[u] * a[v]; }
            long long b = cur; uint32_t bm = mask;
            long long lim = 1LL << lowBits;
            for (long long k = 1; k < lim; k++) {
                int v = __builtin_ctzll((unsigned long long)k);   // Gray-code bit to flip
                cur += a[v] * (tot[v] - 2 * same[v]);
                mask ^= (1u << v);
                uint32_t s = g.adj[v];
                while (s) { int u = __builtin_ctz(s); s &= s - 1;
                    if (((mask >> u) & 1u) == ((mask >> v) & 1u)) same[u] += a[v]; else same[u] -= a[v]; }
                same[v] = tot[v] - same[v];
                if (cur < b) { b = cur; bm = mask; }
            }
            best[blk] = b; bestM[blk] = bm;
        }
    }));
    for (size_t t = 0; t < th.size(); t++) th[t].join();
    long long B = -1; uint32_t BM = 0;
    for (size_t k = 0; k < best.size(); k++) if (best[k] >= 0 && (B < 0 || best[k] < B)) { B = best[k]; BM = bestM[k]; }
    argMask = BM; return B;
}

static void buildArcPlus(const Graph& g, vector<uint32_t>& out) {
    set<uint32_t> seen; int L = g.L;
    vector<uint32_t> arcs;
    for (int s = 1; s <= L; s++) for (int len = 0; len <= L; len++) {
        uint32_t A = 0;
        for (int t = 0; t < len; t++) { int p = (s - 1 + t) % L + 1; int vv = g.vtxAt[p]; if (vv >= 0) A |= 1u << vv; }
        arcs.push_back(A);
    }
    sort(arcs.begin(), arcs.end()); arcs.erase(unique(arcs.begin(), arcs.end()), arcs.end());
    int ns = (int)g.specials.size();
    for (size_t k = 0; k < arcs.size(); k++) for (uint32_t T = 0; T < (1u << ns); T++) {
        uint32_t mk = arcs[k];
        for (int t = 0; t < ns; t++) if ((T >> t) & 1u) mk |= 1u << g.specials[t];
        if (seen.insert(mk).second) out.push_back(mk);
    }
}

static long long monoOf(const Graph& g, const vector<long long>& a, uint32_t mask) {
    long long s = 0;
    for (int e = 0; e < g.m; e++) { int u = g.eu[e], v = g.ev[e];
        if (((mask >> u) & 1u) == ((mask >> v) & 1u)) s += a[u] * a[v]; }
    return s;
}

static long long gcdll(long long x, long long y) { while (y) { long long t = x % y; x = y; y = t; } return x < 0 ? -x : x; }

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s <input> <name|ALL> <UNIFORM|REGULAR|RAND:k:q> [threads]\n", argv[0]); return 1; }
    readInput(argv[1]);
    string want = argv[2], mode = argv[3];
    int nthreads = argc > 4 ? atoi(argv[4]) : 8;
    for (size_t gi = 0; gi < GS.size(); gi++) {
        Graph& g = GS[gi];
        if (want != "ALL" && want != g.name) continue;
        vector<uint32_t> AP; buildArcPlus(g, AP);
        int nrun = 1; long long rq = 0;
        uint64_t rs = 0x243F6A8885A308D3ULL ^ (uint64_t)gi * 1000003ULL;
        if (mode.substr(0, 5) == "RAND:") { sscanf(mode.c_str() + 5, "%d:%lld", &nrun, &rq); }
        for (int run = 0; run < nrun; run++) {
            vector<long long> a(g.n, 1);
            if (mode == "REGULAR") for (int v = 0; v < g.n; v++) a[v] = g.weight[v];
            else if (mode.substr(0, 5) == "RAND:") {
                for (int v = 0; v < g.n; v++) a[v] = 1;
                for (long long c = g.n; c < rq; c++) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; a[rs % g.n]++; }
            }
            long long q = 0; for (int v = 0; v < g.n; v++) q += a[v];
            uint32_t am;
            double t0 = (double)clock() / CLOCKS_PER_SEC;
            long long bip = exactBipGray(g, a, nthreads, am);
            double t1 = (double)clock() / CLOCKS_PER_SEC;
            long long apm = -1; uint32_t apbest = 0;
            for (size_t k = 0; k < AP.size(); k++) { long long s = monoOf(g, a, AP[k]); if (apm < 0 || s < apm) { apm = s; apbest = AP[k]; } }
            long long lhs = 25 * bip, rhs = q * q;
            long long gcd = gcdll(bip, q * q);
            printf("%-12s n=%2d m=%3d %-8s q=%4lld | bip=%6lld  psi=%lld/%lld=%.8f | 25*bip<=q^2 : %s | "
                   "ARCPLUSmin=%6lld  EXACT: %s | cpu=%.1fs\n",
                   g.name.c_str(), g.n, g.m, mode.substr(0, 7).c_str(), q, bip,
                   gcd ? bip / gcd : bip, gcd ? q * q / gcd : q * q, (double)bip / (double)(q * q),
                   lhs <= rhs ? "YES" : "*** NO -- ERDOS 23 VIOLATION ***",
                   apm, apm == bip ? "yes" : "*** NO -- ARCPLUS NOT EXACT ***", t1 - t0);
            if (apm != bip) {
                printf("   ARCPLUS GAP witness a ="); for (int v = 0; v < g.n; v++) printf(" %lld", a[v]);
                printf("   bip=%lld arcplusmin=%lld\n", bip, apm);
            }
            fflush(stdout);
        }
    }
    return 0;
}
