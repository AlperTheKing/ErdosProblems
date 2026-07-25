// G10_hunt.cpp -- exact-integer max-min hunter for  max_x psi(H,x)  (Erdos #23).
//
//   psi(H,x) = min over cuts S of H of  sum_{uv monochromatic} x_u x_v
//   bip(H[a]) = min over cuts S of H of  sum_{uv monochromatic} a_u a_v   (integers)
//
// We maximise  bip(H[a]) / q^2   over integer a >= 0 with sum a = q, by an
// exact-integer multi-resolution steepest-ascent / basin-hopping search seeded
// from EVERY induced C5 concentration point, from uniform, and from random points.
// All arithmetic is 64-bit integer: no floating point anywhere on the accept path.
//
// Input file: one graph per line "name h E u1 v1 u2 v2 ..."
// Output    : one line per graph "name h bestF bestQ 25*bestF-bestQ^2 : a_0 ... a_{h-1}"
//
// build: clang++ -O3 -march=native -std=c++17 G10_hunt.cpp -o G10_hunt.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <thread>
#include <mutex>
#include <atomic>
#include <sstream>
#include <fstream>
#include <iostream>
#include <array>
using namespace std;

typedef long long ll;
static const ll INF = (ll)4e18;

struct Graph {
    string name;
    int h;
    vector<pair<int, int>> edges;
};

struct Engine {
    int h, E, NC;
    vector<pair<int, int>> edges;
    vector<uint32_t> adjm;   // adjacency bitmask per vertex
    vector<ll> Q;            // Q[c]
    vector<ll> M;            // M[c*h+v] = sum of a_u over neighbours u of v on v's side in cut c
    vector<ll> a;
    vector<int> crit;        // indices of cuts with (near-)minimal Q
    ll f;                    // current min over cuts
    static const int CRITK = 96;

    void init_graph(const Graph& g) {
        h = g.h; edges = g.edges; E = (int)edges.size();
        NC = 1 << (h - 1);
        adjm.assign(h, 0);
        for (auto& e : edges) { adjm[e.first] |= 1u << e.second; adjm[e.second] |= 1u << e.first; }
        Q.assign(NC, 0);
        M.assign((size_t)NC * h, 0);
        a.assign(h, 0);
    }

    inline uint32_t cutmask(int c) const { return ((uint32_t)c) << 1; }

    void recompute(const vector<ll>& aa) {
        a = aa;
        fill(M.begin(), M.end(), 0);
        for (int c = 0; c < NC; c++) {
            uint32_t m = cutmask(c);
            ll q = 0;
            ll* Mc = &M[(size_t)c * h];
            for (int k = 0; k < E; k++) {
                int u = edges[k].first, v = edges[k].second;
                if ((((m >> u) ^ (m >> v)) & 1u) == 0u) {
                    q += a[u] * a[v];
                    Mc[u] += a[v];
                    Mc[v] += a[u];
                }
            }
            Q[c] = q;
        }
        refresh();
    }

    void refresh() {
        // f = min Q ; crit = up to CRITK smallest-Q cut indices
        f = INF;
        for (int c = 0; c < NC; c++) if (Q[c] < f) f = Q[c];
        crit.clear();
        ll thr = f;
        // grow threshold until we have a decent pool (cheap: two passes max)
        for (int pass = 0; pass < 24 && (int)crit.size() < CRITK; pass++) {
            crit.clear();
            for (int c = 0; c < NC; c++) {
                if (Q[c] <= thr) { crit.push_back(c); if ((int)crit.size() >= CRITK) break; }
            }
            if ((int)crit.size() >= CRITK) break;
            thr = thr + 1 + thr / 8;
        }
    }

    // value of  min_c Q_c(a - e_i + e_j)  ; early-exits at <= cutoff returning that
    inline ll move_value(int i, int j, ll cutoff) const {
        bool adjij = (adjm[i] >> j) & 1u;
        ll best = INF;
        for (int t = 0; t < (int)crit.size(); t++) {
            int c = crit[t];
            const ll* Mc = &M[(size_t)c * h];
            ll v = Q[c] - Mc[i] + Mc[j];
            if (adjij) { uint32_t m = cutmask(c); if (((((m >> i) ^ (m >> j)) & 1u) == 0u)) v -= 1; }
            if (v < best) { best = v; if (best <= cutoff) return best; }
        }
        for (int c = 0; c < NC; c++) {
            const ll* Mc = &M[(size_t)c * h];
            ll v = Q[c] - Mc[i] + Mc[j];
            if (adjij) { uint32_t m = cutmask(c); if (((((m >> i) ^ (m >> j)) & 1u) == 0u)) v -= 1; }
            if (v < best) { best = v; if (best <= cutoff) return best; }
        }
        return best;
    }

    void apply_move(int i, int j) {
        bool adjij = (adjm[i] >> j) & 1u;
        uint32_t full = (h >= 32) ? 0xFFFFFFFFu : ((1u << h) - 1u);
        for (int c = 0; c < NC; c++) {
            uint32_t m = cutmask(c);
            ll* Mc = &M[(size_t)c * h];
            ll d = -Mc[i] + Mc[j];
            if (adjij && ((((m >> i) ^ (m >> j)) & 1u) == 0u)) d -= 1;
            Q[c] += d;
            uint32_t si = (m >> i) & 1u;
            uint32_t nb = adjm[i] & (si ? m : (~m & full));
            while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; Mc[u] -= 1; }
            uint32_t sj = (m >> j) & 1u;
            uint32_t nb2 = adjm[j] & (sj ? m : (~m & full));
            while (nb2) { int u = __builtin_ctz(nb2); nb2 &= nb2 - 1; Mc[u] += 1; }
        }
        a[i] -= 1; a[j] += 1;
        refresh();
    }

    // random walk on the PLATEAU {f unchanged}: escapes the ties that stall
    // strict steepest ascent (e.g. C7 at q not divisible by 7).
    void plateau_walk(int steps, mt19937_64& rng) {
        for (int t = 0; t < steps; t++) {
            int i = (int)(rng() % h);
            if (a[i] == 0) continue;
            int j = (int)(rng() % h);
            if (i == j) continue;
            ll v = move_value(i, j, f - 1);
            if (v >= f) apply_move(i, j);
        }
    }

    // steepest ascent with unit moves; returns final f
    ll climb(int maxsteps) {
        for (int s = 0; s < maxsteps; s++) {
            ll bestv = f; int bi = -1, bj = -1;
            for (int i = 0; i < h; i++) {
                if (a[i] == 0) continue;
                for (int j = 0; j < h; j++) {
                    if (i == j) continue;
                    ll v = move_value(i, j, bestv);
                    if (v > bestv) { bestv = v; bi = i; bj = j; }
                }
            }
            if (bi < 0) break;
            apply_move(bi, bj);
        }
        return f;
    }
};

// ---------------------------------------------------------------- induced C5s
static vector<array<int, 5>> induced_c5(int h, const vector<uint32_t>& adjm) {
    vector<array<int, 5>> out;
    for (int a = 0; a < h; a++)
        for (int b = a + 1; b < h; b++) {
            if (!((adjm[a] >> b) & 1u)) continue;
            for (int c = 0; c < h; c++) {
                if (c == a || c == b) continue;
                if (!((adjm[b] >> c) & 1u)) continue;
                if ((adjm[a] >> c) & 1u) continue;
                for (int d = 0; d < h; d++) {
                    if (d == a || d == b || d == c) continue;
                    if (!((adjm[c] >> d) & 1u)) continue;
                    if (((adjm[a] >> d) & 1u) || ((adjm[b] >> d) & 1u)) continue;
                    for (int e = d + 1; e < h; e++) {   // d<e to kill the reflection
                        if (e == a || e == b || e == c) continue;
                        if (!((adjm[d] >> e) & 1u)) continue;
                        if (!((adjm[e] >> a) & 1u)) continue;
                        if (((adjm[b] >> e) & 1u) || ((adjm[c] >> e) & 1u)) continue;
                        out.push_back({ a,b,c,d,e });
                    }
                }
            }
        }
    return out;
}

struct Result {
    string name; int h; ll bestF, bestQ; vector<ll> besta; ll c5count; bool c5conc;
};

static bool is_c5_concentration(const Engine& en, const vector<ll>& a) {
    vector<int> sup;
    for (int i = 0; i < en.h; i++) if (a[i] > 0) sup.push_back(i);
    if ((int)sup.size() != 5) return false;
    for (int i = 1; i < 5; i++) if (a[sup[i]] != a[sup[0]]) return false;
    uint32_t mask = 0; for (int v : sup) mask |= 1u << v;
    int deg = 0;
    for (int v : sup) { int d = __builtin_popcount(en.adjm[v] & mask); if (d != 2) return false; deg += d; }
    return deg == 10;
}

int NSEED_RAND = 24;
int QSTART = 60;
int NLEVEL = 4;
int MAXSTEP = 400;
int NPERTURB = 6;

static Result run_graph(const Graph& g, uint64_t seedbase) {
    Engine en; en.init_graph(g);
    auto c5s = induced_c5(en.h, en.adjm);
    Result R; R.name = g.name; R.h = g.h; R.bestF = -1; R.bestQ = 1; R.c5count = (ll)c5s.size(); R.c5conc = true;

    mt19937_64 rng(seedbase);
    vector<vector<ll>> seeds;
    // (1) every induced C5 concentration
    size_t c5cap = min<size_t>(c5s.size(), 60);
    for (size_t t = 0; t < c5cap; t++) {
        vector<ll> a(en.h, 0);
        for (int k = 0; k < 5; k++) a[c5s[t][k]] = QSTART / 5;
        seeds.push_back(a);
    }
    // (2) uniform
    {
        vector<ll> a(en.h, QSTART / en.h);
        int rem = QSTART - (QSTART / en.h) * en.h;
        for (int i = 0; i < rem; i++) a[i]++;
        seeds.push_back(a);
    }
    // (3) random compositions (zeros allowed)
    for (int t = 0; t < NSEED_RAND; t++) {
        vector<ll> a(en.h, 0);
        for (int u = 0; u < QSTART; u++) a[rng() % en.h]++;
        seeds.push_back(a);
    }
    // (4) random full-support
    for (int t = 0; t < NSEED_RAND; t++) {
        vector<ll> a(en.h, 1);
        for (int u = en.h; u < QSTART; u++) a[rng() % en.h]++;
        seeds.push_back(a);
    }

    for (auto& s0 : seeds) {
        vector<ll> cur = s0;
        ll q = 0; for (ll v : cur) q += v;
        en.recompute(cur);
        en.climb(MAXSTEP);
        vector<ll> bstA = en.a; ll bstF = en.f;
        // basin hopping + plateau walking at this resolution
        for (int p = 0; p < NPERTURB; p++) {
            vector<ll> pa = bstA;
            int nk = 2 + (int)(rng() % 4);
            for (int k = 0; k < nk; k++) {
                int i = (int)(rng() % en.h), j = (int)(rng() % en.h);
                if (i == j) continue;
                ll amt = 1 + (ll)(rng() % 3);
                amt = min(amt, pa[i]);
                pa[i] -= amt; pa[j] += amt;
            }
            en.recompute(pa);
            en.climb(MAXSTEP);
            for (int w = 0; w < 3; w++) { en.plateau_walk(8 * en.h, rng); en.climb(MAXSTEP); if (en.f > bstF) { bstF = en.f; bstA = en.a; } }
            if (en.f > bstF) { bstF = en.f; bstA = en.a; }
        }
        // multi-resolution refinement (a -> 2a keeps the ratio, then re-climb finer)
        for (int lev = 1; lev < NLEVEL; lev++) {
            vector<ll> na(en.h);
            for (int i = 0; i < en.h; i++) na[i] = bstA[i] * 2;
            en.recompute(na);
            en.climb(MAXSTEP);
            bstF = en.f; bstA = en.a;
            for (int p = 0; p < NPERTURB / 2 + 1; p++) {
                vector<ll> pa = bstA;
                int nk = 2 + (int)(rng() % 4);
                for (int k = 0; k < nk; k++) {
                    int i = (int)(rng() % en.h), j = (int)(rng() % en.h);
                    if (i == j) continue;
                    ll amt = 1 + (ll)(rng() % 4);
                    amt = min(amt, pa[i]);
                    pa[i] -= amt; pa[j] += amt;
                }
                en.recompute(pa);
                en.climb(MAXSTEP);
                for (int w = 0; w < 3; w++) { en.plateau_walk(8 * en.h, rng); en.climb(MAXSTEP); if (en.f > bstF) { bstF = en.f; bstA = en.a; } }
                if (en.f > bstF) { bstF = en.f; bstA = en.a; }
            }
            q = 0; for (ll v : bstA) q += v;
        }
        q = 0; for (ll v : bstA) q += v;
        // compare bstF/q^2 with R.bestF/R.bestQ^2   (exact integer cross-multiplication)
        if (R.bestF < 0 || (__int128)bstF * R.bestQ * R.bestQ > (__int128)R.bestF * q * q) {
            R.bestF = bstF; R.bestQ = q; R.besta = bstA;
            R.c5conc = is_c5_concentration(en, bstA);
        }
    }
    return R;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: G10_hunt in.txt out.txt [threads] [nrand] [qstart] [nlevel]\n"); return 1; }
    int nthreads = argc > 3 ? atoi(argv[3]) : 8;
    if (argc > 4) NSEED_RAND = atoi(argv[4]);
    if (argc > 5) QSTART = atoi(argv[5]);
    if (argc > 6) NLEVEL = atoi(argv[6]);

    vector<Graph> gs;
    { ifstream in(argv[1]); string line;
      while (getline(in, line)) {
        if (line.empty()) continue;
        istringstream ss(line); Graph g; int E;
        ss >> g.name >> g.h >> E;
        for (int k = 0; k < E; k++) { int u, v; ss >> u >> v; g.edges.push_back({ u,v }); }
        gs.push_back(g);
      } }
    fprintf(stderr, "loaded %zu graphs\n", gs.size());

    vector<Result> res(gs.size());
    atomic<size_t> next(0);
    atomic<int> hits(0);
    vector<thread> th;
    for (int t = 0; t < nthreads; t++) th.emplace_back([&]() {
        for (;;) {
            size_t i = next++;
            if (i >= gs.size()) break;
            res[i] = run_graph(gs[i], 0x9E3779B97F4A7C15ull * (i + 1) + 12345);
            if ((__int128)25 * res[i].bestF > (__int128)res[i].bestQ * res[i].bestQ) hits++;
        }
        });
    for (auto& x : th) x.join();

    FILE* out = fopen(argv[2], "w");
    for (size_t i = 0; i < gs.size(); i++) {
        Result& R = res[i];
        fprintf(out, "%s %d %lld %lld %lld %d %lld :", R.name.c_str(), R.h, R.bestF, R.bestQ,
            (ll)(25 * R.bestF - R.bestQ * R.bestQ), (int)R.c5conc, R.c5count);
        for (ll v : R.besta) fprintf(out, " %lld", v);
        fprintf(out, "\n");
    }
    fclose(out);
    fprintf(stderr, "done. strict-hits(25F>Q^2) = %d\n", (int)hits);
    return 0;
}
