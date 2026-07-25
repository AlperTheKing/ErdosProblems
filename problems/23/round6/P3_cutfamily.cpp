// P3_cutfamily.cpp -- the Vega analogue of the ARC-CUT test.
//
// A Vega graph is  Gamma_i (= the circle graph And(i) on 3i-1 points, possibly minus the point 2i)
// together with 8 (or 7, or 6) "special" vertices x,y,a,b,c,u,v,w.  The circle skeleton is exactly
// the one the round-5 arc-cut work uses; the question is which structured cut family replaces the
// arc family.  Families implemented:
//
//   ARCPLUS : S = A u T,  A a cyclic interval of the circle {1..3i-1}, T an arbitrary subset of
//             the special vertices.  (Contains every neighbourhood cut: N(j) = arc u {2 specials},
//             N(a) = X u {v,w,x}, N(x) = {y,a,b,c}, ... )
//   NBHD    : S = N(t), t a vertex.  (the m(b) cuts of the root chain)
//   ARCFREE : S = A only, specials all on side 0.
//   ARC3    : S = A u T with T ranging only over the 8 "coherent" sets determined by the arc:
//             each special sits at a circle position (a,u at 2i;  b,v at 1;  c,w at i+1/2;
//             x,y have no position) -- T contains a special iff its position is in A, XOR a
//             global choice for each of the three doubled pairs and for x,y.  See buildARC3.
//
// For every integer weighting a >= 0 with sum a = q the program asks for a member S of the family
// with   DEN * mono_S(a) <= NUM * q * q   (exact 64-bit integers; default 1/25).  Failures are
// reported together with the TRUE bip(a) (exact, by enumerating all cuts of the support), so a
// failure of the family is distinguished from a violation of Erdos 23.
//
// Usage: P3_cutfamily <input.txt> <name|ALL> <q> [threads] [family] [NUM] [DEN] [maxn]
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
    vector<int> eu, ev;
    vector<string> role;
    vector<vector<int> > auts;
    uint32_t adj[MAXN];
    // circle data
    int L;                       // 3i-1
    int posOf[MAXN];             // circle position 1..L, or -1
    int vtxAt[MAXN];             // circle position -> vertex index, or -1
    vector<int> specials;        // vertex indices of x,y,a,b,c,u,v,w present
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
        } else if (!strncmp(buf, "AUT", 3)) {
            int k; sscanf(buf, "AUT %d", &k);
            for (int j = 0; j < k; j++) { if (!fgets(buf, sizeof(buf), f)) break;
                vector<int> p(g->n); char* q = buf;
                for (int t = 0; t < g->n; t++) { int c; sscanf(q, "%d%n", &p[t], &c); q += c; }
                g->auts.push_back(p); }
        }
    }
    fclose(f);
}

struct Cut { uint32_t mask; vector<uint8_t> eu, ev; long long hits; };

static void materialise(const Graph& g, const vector<uint32_t>& masks, vector<Cut>& out) {
    set<uint32_t> seen;
    for (size_t k = 0; k < masks.size(); k++) {
        uint32_t mk = masks[k];
        uint32_t full = (g.n >= 32) ? 0xffffffffu : ((1u << g.n) - 1);
        uint32_t canon = min(mk & full, (~mk) & full);
        if (seen.count(canon)) continue; seen.insert(canon);
        Cut C; C.mask = mk; C.hits = 0;
        for (int t = 0; t < g.m; t++) { int u = g.eu[t], v = g.ev[t];
            if (((mk >> u) & 1u) == ((mk >> v) & 1u)) { C.eu.push_back((uint8_t)u); C.ev.push_back((uint8_t)v); } }
        out.push_back(C);
    }
    sort(out.begin(), out.end(), [](const Cut& A, const Cut& B) { return A.eu.size() < B.eu.size(); });
}

static void buildFamily(const Graph& g, const string& fam, vector<Cut>& out) {
    vector<uint32_t> masks;
    int L = g.L;
    if (fam == "NBHD") {
        for (int v = 0; v < g.n; v++) masks.push_back(g.adj[v]);
    } else if (fam == "ARCFREE" || fam == "ARCPLUS" || fam == "ARC3") {
        vector<uint32_t> arcs;
        for (int s = 1; s <= L; s++) for (int len = 0; len <= L; len++) {
            uint32_t A = 0;
            for (int t = 0; t < len; t++) { int p = (s - 1 + t) % L + 1; int vv = g.vtxAt[p]; if (vv >= 0) A |= 1u << vv; }
            arcs.push_back(A);
        }
        sort(arcs.begin(), arcs.end()); arcs.erase(unique(arcs.begin(), arcs.end()), arcs.end());
        int ns = (int)g.specials.size();
        if (fam == "ARCFREE") { masks = arcs; }
        else if (fam == "ARCPLUS") {
            for (size_t k = 0; k < arcs.size(); k++)
                for (uint32_t T = 0; T < (1u << ns); T++) {
                    uint32_t mk = arcs[k];
                    for (int t = 0; t < ns; t++) if ((T >> t) & 1u) mk |= 1u << g.specials[t];
                    masks.push_back(mk);
                }
        } else { // ARC3 : specials follow their circle position, with 4 global sign choices
            // circle position of each special: a,u -> 2i ; b,v -> 1 ; c,w -> i+1/2 (between i,i+1)
            // "in the arc" for the half-integer position means: the arc contains the gap (i,i+1).
            int I = g.i;
            for (size_t k = 0; k < arcs.size(); k++) {
                // recompute membership of positions 2i, 1 and the gap (i,i+1) for this arc
                // (we re-derive from the arc's vertex set: position p in arc iff its vertex is set;
                //  the gap is in the arc iff both i and i+1 are, or the arc wraps through it)
                uint32_t A = arcs[k];
                int in2i = (g.vtxAt[2 * I] >= 0) ? (int)((A >> g.vtxAt[2 * I]) & 1u) : -1;
                int in1 = (int)((A >> g.vtxAt[1]) & 1u);
                int inI = (int)((A >> g.vtxAt[I]) & 1u);
                int inI1 = (int)((A >> g.vtxAt[I + 1]) & 1u);
                int ingap = (inI && inI1) ? 1 : 0;
                if (in2i < 0) in2i = in1;   // vertex 2i deleted: fall back
                for (uint32_t sgn = 0; sgn < 16; sgn++) {
                    uint32_t mk = A;
                    int sa = in2i ^ ((sgn >> 0) & 1), su = in2i ^ ((sgn >> 0) & 1) ^ 1;
                    int sb = in1 ^ ((sgn >> 1) & 1), sv = in1 ^ ((sgn >> 1) & 1) ^ 1;
                    int sc = ingap ^ ((sgn >> 2) & 1), sw = ingap ^ ((sgn >> 2) & 1) ^ 1;
                    int sx = (sgn >> 3) & 1, sy = sx ^ 1;
                    for (size_t t = 0; t < g.specials.size(); t++) {
                        const string& r = g.role[g.specials[t]];
                        int bit = 0;
                        if (r == "a") bit = sa; else if (r == "u") bit = su;
                        else if (r == "b") bit = sb; else if (r == "v") bit = sv;
                        else if (r == "c") bit = sc; else if (r == "w") bit = sw;
                        else if (r == "x") bit = sx; else bit = sy;
                        if (bit) mk |= 1u << g.specials[t];
                    }
                    masks.push_back(mk);
                }
            }
        }
    } else { fprintf(stderr, "unknown family %s\n", fam.c_str()); exit(1); }
    materialise(g, masks, out);
}

struct Res {
    long long leaves, reps, ok, fail;
    long long maxFamMono, maxGap, nGap;  // CMP mode: max family value, max famMin-trueBip, #gaps
    vector<vector<int> > failW;
    vector<long long> failFam, failBip;
    vector<long long> used;              // USED mode: per-cut certification counts
    Res() : leaves(0), reps(0), ok(0), fail(0), maxFamMono(-1), maxGap(0), nGap(0) {}
};

struct W {
    const Graph* g; int q, n; long long NUM, DEN;
    vector<Cut>* fam;
    bool cmpMode, usedMode;
    Res R; int a[MAXN];
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
    bool lexMin() const {
        for (size_t k = 0; k < g->auts.size(); k++) { const vector<int>& p = g->auts[k];
            for (int t = 0; t < n; t++) { int x = a[p[t]], y = a[t]; if (x < y) return false; if (x > y) break; } }
        return true;
    }
    bool exactchkMode;
    void leaf() {
        R.leaves++; if (!lexMin()) return; R.reps++;
        long long rhs = NUM * (long long)q * (long long)q;
        long long best = -1;
        vector<Cut>& F = *fam;
        if (exactchkMode) {
            // EXHAUSTIVE exactness test: does the family attain the true bip?  early exit at <= bip
            long long bp = exactBip();
            for (size_t k = 0; k < F.size(); k++) {
                long long s = 0; const Cut& C = F[k]; int ne = (int)C.eu.size();
                for (int t = 0; t < ne; t++) { s += (long long)a[C.eu[t]] * a[C.ev[t]]; if (s > bp) break; }
                if (s <= bp) { R.ok++; return; }
            }
            R.fail++;
            if (R.failW.size() < 40) { R.failW.push_back(vector<int>(a, a + n)); R.failFam.push_back(-1); R.failBip.push_back(bp); }
            return;
        }
        if (cmpMode || usedMode) {          // exhaustive scan, no early exit
            size_t argb = 0;
            for (size_t k = 0; k < F.size(); k++) {
                long long s = 0; const Cut& C = F[k]; int ne = (int)C.eu.size();
                for (int t = 0; t < ne; t++) s += (long long)a[C.eu[t]] * a[C.ev[t]];
                if (best < 0 || s < best) { best = s; argb = k; }
            }
            if (usedMode) { if (R.used.size() < F.size()) R.used.assign(F.size(), 0); R.used[argb]++; }
            if (cmpMode) {
                long long bp = exactBip();
                if (best > R.maxFamMono) R.maxFamMono = best;
                if (best - bp > R.maxGap) R.maxGap = best - bp;
                if (best > bp) R.nGap++;
            }
            if (DEN * best <= rhs) { R.ok++; return; }
            R.fail++;
            long long bp2 = exactBip();
            if (R.failW.size() < 40) { R.failW.push_back(vector<int>(a, a + n)); R.failFam.push_back(best); R.failBip.push_back(bp2); }
            return;
        }
        for (size_t k = 0; k < F.size(); k++) {
            long long s = 0; const Cut& C = F[k]; int ne = (int)C.eu.size();
            for (int t = 0; t < ne; t++) s += (long long)a[C.eu[t]] * a[C.ev[t]];
            if (best < 0 || s < best) best = s;
            if (DEN * s <= rhs) { R.ok++; return; }
        }
        R.fail++;
        long long bp = exactBip();
        if (R.failW.size() < 40) { R.failW.push_back(vector<int>(a, a + n)); R.failFam.push_back(best); R.failBip.push_back(bp); }
    }
    void rec(int d, int rem) { if (d == n - 1) { a[d] = rem; leaf(); return; }
        for (int t = rem; t >= 0; t--) { a[d] = t; rec(d + 1, rem - t); } }
};

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s <input> <name|ALL> <q> [threads] [family] [NUM] [DEN] [maxn]\n", argv[0]); return 1; }
    readInput(argv[1]);
    string want = argv[2]; int q = atoi(argv[3]);
    int nthreads = argc > 4 ? atoi(argv[4]) : 8;
    string fam = argc > 5 ? argv[5] : "ARCPLUS";
    long long NUM = argc > 6 ? atoll(argv[6]) : 1, DEN = argc > 7 ? atoll(argv[7]) : 25;
    int maxn = argc > 8 ? atoi(argv[8]) : 64;
    string extra = argc > 9 ? argv[9] : "";
    bool cmpMode = (extra == "CMP"), usedMode = (extra == "USED");
    bool exactchkMode = (extra == "EXACTCHK");
    long long randN = 0;
    if (extra.size() > 5 && extra.substr(0, 5) == "RAND:") { randN = atoll(extra.c_str() + 5); cmpMode = true; }
    for (size_t gi = 0; gi < GS.size(); gi++) {
        Graph& g = GS[gi];
        if (want != "ALL" && want != g.name) continue;
        if (g.n > maxn) continue;
        vector<Cut> F; buildFamily(g, fam, F);
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
            W ww; ww.g = &g; ww.q = q; ww.n = n; ww.NUM = NUM; ww.DEN = DEN; ww.fam = &F;
            ww.cmpMode = cmpMode; ww.usedMode = usedMode; ww.exactchkMode = exactchkMode;
            if (randN) {
                uint64_t rs = 88172645463325252ULL + 1000003ULL * (t + 1);
                long long share = randN / nthreads + 1;
                for (long long r = 0; r < share; r++) {
                    for (int v = 0; v < n; v++) ww.a[v] = 0;
                    for (int c = 0; c < q; c++) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; ww.a[rs % n]++; }
                    ww.leaf();
                }
                res[t] = ww.R; return;
            }
            for (;;) { size_t k = next.fetch_add(1); if (k >= tasks.size()) break;
                int s = 0; for (int d = 0; d < P; d++) { ww.a[d] = tasks[k][d]; s += tasks[k][d]; }
                if (P == n - 1) { ww.a[n - 1] = q - s; ww.leaf(); } else ww.rec(P, q - s); }
            res[t] = ww.R; }));
        for (int t = 0; t < nthreads; t++) th[t].join();
        Res T; T.used.assign(F.size(), 0);
        for (int t = 0; t < nthreads; t++) { T.leaves += res[t].leaves; T.reps += res[t].reps;
            T.ok += res[t].ok; T.fail += res[t].fail;
            if (res[t].maxFamMono > T.maxFamMono) T.maxFamMono = res[t].maxFamMono;
            if (res[t].maxGap > T.maxGap) T.maxGap = res[t].maxGap;
            T.nGap += res[t].nGap;
            for (size_t k = 0; k < res[t].used.size(); k++) T.used[k] += res[t].used[k];
            for (size_t k = 0; k < res[t].failW.size() && T.failW.size() < 40; k++) {
                T.failW.push_back(res[t].failW[k]); T.failFam.push_back(res[t].failFam[k]); T.failBip.push_back(res[t].failBip[k]); } }
        double t1 = (double)clock() / CLOCKS_PER_SEC;
        printf("FAMILY %-8s %-12s n=%d m=%d q=%d |F|=%zu | leaves=%lld reps=%lld | certified=%lld FAILED=%lld | cpu=%.1fs\n",
               fam.c_str(), g.name.c_str(), n, g.m, q, F.size(), T.leaves, T.reps, T.ok, T.fail, t1 - t0);
        if (exactchkMode)
            printf("   EXACTCHK: family attains the true bip for %lld of %lld orbit reps; EXACTNESS FAILURES = %lld\n", T.ok, T.reps, T.fail);
        if (cmpMode)
            printf("   CMP: max familyMin=%lld (q^2/25=%.3f)  #(familyMin>trueBip)=%lld  max gap=%lld\n",
                   T.maxFamMono, q * q / 25.0, T.nGap, T.maxGap);
        if (usedMode) {
            long long nz = 0; for (size_t k = 0; k < T.used.size(); k++) if (T.used[k]) nz++;
            printf("   USED: %lld of %zu family members are the unique argmin for some weighting\n", nz, F.size());
            vector<pair<long long, size_t> > srt;
            for (size_t k = 0; k < T.used.size(); k++) if (T.used[k]) srt.push_back(make_pair(-T.used[k], k));
            sort(srt.begin(), srt.end());
            for (size_t k = 0; k < srt.size() && k < 15; k++) {
                size_t idx = srt[k].second; printf("      %8lld  mask side0 = {", -srt[k].first);
                for (int v = 0; v < n; v++) if (!((F[idx].mask >> v) & 1u)) printf(" %s", g.role[v].c_str());
                printf(" }\n");
            }
        }
        for (size_t k = 0; k < T.failW.size(); k++) {
            printf("   FAIL a =");
            for (int v = 0; v < n; v++) printf(" %d", T.failW[k][v]);
            printf("   famMin=%lld  trueBip=%lld  (q^2/25=%.3f)%s\n", T.failFam[k], T.failBip[k], q * q / 25.0,
                   25 * T.failBip[k] > (long long)q * q ? "  <<< ERDOS-23 VIOLATION" : "  (family gap only)");
        }
        fflush(stdout);
    }
    return 0;
}
