// G10_hunt2.cpp -- DEGREE-CONSTRAINED exact-integer max-min hunter for Erdos #23.
//
// Fact 7 of the brief: a triangle-free G with delta(G) > floor(3N/8) is homomorphic to C5,
// and H -> C5 forces bip <= N^2/25.  Hence EVERY counterexample G (not just a minimal one)
// satisfies delta(G) <= floor(3N/8).   For a blow-up G = H[a] with N = q = sum a,
// delta(G) = min over i in supp(a) of  d_a(i) = sum_{u ~ i} a_u.
//
// So the counterexample question is EXACTLY:
//     is there H triangle-free and integer a >= 0, q = sum a, with
//         (i)  exists i with a_i >= 1 and d_a(i) <= floor(NUM*q/DEN)      [NUM/DEN = 3/8]
//         (ii) bip(H[a]) = min_cuts sum_{mono} a_u a_v  >  q^2/25 .
// The C5 uniform point has d = 2q/5 = 0.4q > 0.375q, so it is INFEASIBLE here:
// the 1/25 plateau is removed and the reported maximum is a genuine margin.
//
// build: clang++ -O3 -march=native -std=c++17 G10_hunt2.cpp -o G10_hunt2.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <thread>
#include <atomic>
#include <sstream>
#include <fstream>
#include <array>
using namespace std;
typedef long long ll;
static const ll INF = (ll)4e18;

int NUMER = 3, DENOM = 8;   // delta <= floor(NUMER*q/DENOM)

struct Graph { string name; int h; vector<pair<int, int>> edges; };

struct Engine {
    int h, E, NC;
    vector<pair<int, int>> edges;
    vector<uint32_t> adjm;
    vector<ll> Q, M, a, deg;
    vector<int> crit;
    ll f, q, DB;
    static const int CRITK = 96;

    void init_graph(const Graph& g) {
        h = g.h; edges = g.edges; E = (int)edges.size(); NC = 1 << (h - 1);
        adjm.assign(h, 0);
        for (auto& e : edges) { adjm[e.first] |= 1u << e.second; adjm[e.second] |= 1u << e.first; }
        Q.assign(NC, 0); M.assign((size_t)NC * h, 0); a.assign(h, 0); deg.assign(h, 0);
    }
    inline uint32_t cutmask(int c) const { return ((uint32_t)c) << 1; }

    void recompute(const vector<ll>& aa) {
        a = aa; q = 0; for (ll v : a) q += v; DB = (ll)NUMER * q / DENOM;
        fill(M.begin(), M.end(), 0);
        for (int c = 0; c < NC; c++) {
            uint32_t m = cutmask(c); ll s = 0; ll* Mc = &M[(size_t)c * h];
            for (int k = 0; k < E; k++) {
                int u = edges[k].first, v = edges[k].second;
                if ((((m >> u) ^ (m >> v)) & 1u) == 0u) { s += a[u] * a[v]; Mc[u] += a[v]; Mc[v] += a[u]; }
            }
            Q[c] = s;
        }
        for (int v = 0; v < h; v++) { ll s = 0; uint32_t nb = adjm[v]; while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; s += a[u]; } deg[v] = s; }
        refresh();
    }
    void refresh() {
        f = INF; for (int c = 0; c < NC; c++) if (Q[c] < f) f = Q[c];
        crit.clear(); ll thr = f;
        for (int pass = 0; pass < 24 && (int)crit.size() < CRITK; pass++) {
            crit.clear();
            for (int c = 0; c < NC; c++) if (Q[c] <= thr) { crit.push_back(c); if ((int)crit.size() >= CRITK) break; }
            if ((int)crit.size() >= CRITK) break;
            thr = thr + 1 + thr / 8;
        }
    }
    bool feasible_now() const { for (int v = 0; v < h; v++) if (a[v] >= 1 && deg[v] <= DB) return true; return false; }
    // feasibility after moving one unit i -> j
    bool feasible_move(int i, int j) const {
        for (int v = 0; v < h; v++) {
            ll av = a[v] - (v == i) + (v == j);
            if (av < 1) continue;
            ll dv = deg[v] - (ll)((adjm[v] >> i) & 1u) + (ll)((adjm[v] >> j) & 1u);
            if (dv <= DB) return true;
        }
        return false;
    }
    inline ll move_value(int i, int j, ll cutoff) const {
        bool adjij = (adjm[i] >> j) & 1u; ll best = INF;
        for (size_t t = 0; t < crit.size(); t++) {
            int c = crit[t]; const ll* Mc = &M[(size_t)c * h];
            ll v = Q[c] - Mc[i] + Mc[j];
            if (adjij) { uint32_t m = cutmask(c); if ((((m >> i) ^ (m >> j)) & 1u) == 0u) v -= 1; }
            if (v < best) { best = v; if (best <= cutoff) return best; }
        }
        for (int c = 0; c < NC; c++) {
            const ll* Mc = &M[(size_t)c * h];
            ll v = Q[c] - Mc[i] + Mc[j];
            if (adjij) { uint32_t m = cutmask(c); if ((((m >> i) ^ (m >> j)) & 1u) == 0u) v -= 1; }
            if (v < best) { best = v; if (best <= cutoff) return best; }
        }
        return best;
    }
    void apply_move(int i, int j) {
        bool adjij = (adjm[i] >> j) & 1u;
        uint32_t full = (h >= 32) ? 0xFFFFFFFFu : ((1u << h) - 1u);
        for (int c = 0; c < NC; c++) {
            uint32_t m = cutmask(c); ll* Mc = &M[(size_t)c * h];
            ll d = -Mc[i] + Mc[j];
            if (adjij && ((((m >> i) ^ (m >> j)) & 1u) == 0u)) d -= 1;
            Q[c] += d;
            uint32_t si = (m >> i) & 1u, nb = adjm[i] & (si ? m : (~m & full));
            while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; Mc[u] -= 1; }
            uint32_t sj = (m >> j) & 1u, nb2 = adjm[j] & (sj ? m : (~m & full));
            while (nb2) { int u = __builtin_ctz(nb2); nb2 &= nb2 - 1; Mc[u] += 1; }
        }
        a[i] -= 1; a[j] += 1;
        uint32_t nb = adjm[i]; while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; deg[u] -= 1; }
        uint32_t nb2 = adjm[j]; while (nb2) { int u = __builtin_ctz(nb2); nb2 &= nb2 - 1; deg[u] += 1; }
        refresh();
    }
    void plateau_walk(int steps, mt19937_64& rng) {
        for (int t = 0; t < steps; t++) {
            int i = (int)(rng() % h); if (a[i] == 0) continue;
            int j = (int)(rng() % h); if (i == j) continue;
            if (!feasible_move(i, j)) continue;
            if (move_value(i, j, f - 1) >= f) apply_move(i, j);
        }
    }
    ll climb(int maxsteps) {
        for (int s = 0; s < maxsteps; s++) {
            ll bestv = f; int bi = -1, bj = -1;
            for (int i = 0; i < h; i++) {
                if (a[i] == 0) continue;
                for (int j = 0; j < h; j++) {
                    if (i == j) continue;
                    if (!feasible_move(i, j)) continue;
                    ll v = move_value(i, j, bestv);
                    if (v > bestv) { bestv = v; bi = i; bj = j; }
                }
            }
            if (bi < 0) break;
            apply_move(bi, bj);
        }
        return f;
    }
    // move weight around until the degree constraint holds (or give up)
    bool repair(mt19937_64& rng, int tries) {
        for (int t = 0; t < tries; t++) {
            if (feasible_now()) return true;
            // find the support vertex with the smallest degree and drain its neighbours
            int bv = -1; ll bd = INF;
            for (int v = 0; v < h; v++) if (a[v] >= 1 && deg[v] < bd) { bd = deg[v]; bv = v; }
            if (bv < 0) return false;
            // pick a neighbour of bv with positive weight, push its weight to a non-neighbour
            vector<int> nbs, others;
            for (int u = 0; u < h; u++) {
                if (((adjm[bv] >> u) & 1u) && a[u] > 0) nbs.push_back(u);
                else if (u != bv && !((adjm[bv] >> u) & 1u)) others.push_back(u);
            }
            if (nbs.empty() || others.empty()) return false;
            int i = nbs[rng() % nbs.size()], j = others[rng() % others.size()];
            // direct integer update
            vector<ll> na = a; na[i] -= 1; na[j] += 1; recompute(na);
        }
        return feasible_now();
    }
};

static vector<array<int, 5>> induced_c5(int h, const vector<uint32_t>& adjm) {
    vector<array<int, 5>> out;
    for (int a = 0; a < h; a++) for (int b = a + 1; b < h; b++) {
        if (!((adjm[a] >> b) & 1u)) continue;
        for (int c = 0; c < h; c++) { if (c == a || c == b) continue; if (!((adjm[b] >> c) & 1u)) continue; if ((adjm[a] >> c) & 1u) continue;
            for (int d = 0; d < h; d++) { if (d == a || d == b || d == c) continue; if (!((adjm[c] >> d) & 1u)) continue; if (((adjm[a] >> d) & 1u) || ((adjm[b] >> d) & 1u)) continue;
                for (int e = d + 1; e < h; e++) { if (e == a || e == b || e == c) continue; if (!((adjm[d] >> e) & 1u)) continue; if (!((adjm[e] >> a) & 1u)) continue; if (((adjm[b] >> e) & 1u) || ((adjm[c] >> e) & 1u)) continue; out.push_back({ a,b,c,d,e }); } } } }
    return out;
}

int NSEED_RAND = 60, QSTART = 64, NLEVEL = 4, MAXSTEP = 400, NPERTURB = 6;

struct Result { string name; int h; ll bestF, bestQ; vector<ll> besta; bool found; };

static Result run_graph(const Graph& g, uint64_t sb) {
    Engine en; en.init_graph(g);
    auto c5s = induced_c5(en.h, en.adjm);
    Result R; R.name = g.name; R.h = g.h; R.bestF = -1; R.bestQ = 1; R.found = false;
    mt19937_64 rng(sb);
    vector<vector<ll>> seeds;
    // C5 concentrations perturbed towards feasibility (pure C5 point is infeasible: d = 2q/5)
    size_t cap = min<size_t>(c5s.size(), 40);
    for (size_t t = 0; t < cap; t++) {
        for (int rep = 0; rep < 3; rep++) {
            vector<ll> a(en.h, 0);
            for (int k = 0; k < 5; k++) a[c5s[t][k]] = QSTART / 5;
            ll spare = QSTART - 5 * (QSTART / 5);
            // bleed weight off two C5 vertices onto vertices outside the C5
            int nout = 0; vector<int> outs;
            for (int v = 0; v < en.h; v++) { bool inc = false; for (int k = 0; k < 5; k++) if (c5s[t][k] == v) inc = true; if (!inc) outs.push_back(v); }
            if (!outs.empty()) {
                int amt = 2 + (int)(rng() % 8);
                for (int s = 0; s < amt; s++) { int k = (int)(rng() % 5); if (a[c5s[t][k]] > 0) { a[c5s[t][k]]--; a[outs[rng() % outs.size()]]++; } }
            }
            a[0] += spare; (void)nout;
            seeds.push_back(a);
        }
    }
    { vector<ll> a(en.h, QSTART / en.h); int rem = QSTART - (QSTART / en.h) * en.h; for (int i = 0; i < rem; i++) a[i]++; seeds.push_back(a); }
    for (int t = 0; t < NSEED_RAND; t++) { vector<ll> a(en.h, 0); for (int u = 0; u < QSTART; u++) a[rng() % en.h]++; seeds.push_back(a); }
    for (int t = 0; t < NSEED_RAND; t++) { vector<ll> a(en.h, 1); for (int u = en.h; u < QSTART; u++) a[rng() % en.h]++; seeds.push_back(a); }

    for (auto& s0 : seeds) {
        en.recompute(s0);
        if (!en.repair(rng, 40)) continue;
        en.climb(MAXSTEP);
        vector<ll> bstA = en.a; ll bstF = en.f;
        for (int p = 0; p < NPERTURB; p++) {
            vector<ll> pa = bstA; int nk = 2 + (int)(rng() % 4);
            for (int k = 0; k < nk; k++) { int i = (int)(rng() % en.h), j = (int)(rng() % en.h); if (i == j) continue; ll amt = 1 + (ll)(rng() % 3); amt = min(amt, pa[i]); pa[i] -= amt; pa[j] += amt; }
            en.recompute(pa); if (!en.repair(rng, 40)) continue;
            en.climb(MAXSTEP);
            for (int w = 0; w < 3; w++) { en.plateau_walk(8 * en.h, rng); en.climb(MAXSTEP); if (en.f > bstF && en.feasible_now()) { bstF = en.f; bstA = en.a; } }
            if (en.f > bstF && en.feasible_now()) { bstF = en.f; bstA = en.a; }
        }
        for (int lev = 1; lev < NLEVEL; lev++) {
            vector<ll> na(en.h); for (int i = 0; i < en.h; i++) na[i] = bstA[i] * 2;
            en.recompute(na); if (!en.repair(rng, 40)) break;
            en.climb(MAXSTEP); bstF = en.f; bstA = en.a;
            for (int p = 0; p < NPERTURB / 2 + 1; p++) {
                vector<ll> pa = bstA; int nk = 2 + (int)(rng() % 4);
                for (int k = 0; k < nk; k++) { int i = (int)(rng() % en.h), j = (int)(rng() % en.h); if (i == j) continue; ll amt = 1 + (ll)(rng() % 4); amt = min(amt, pa[i]); pa[i] -= amt; pa[j] += amt; }
                en.recompute(pa); if (!en.repair(rng, 40)) continue;
                en.climb(MAXSTEP);
                for (int w = 0; w < 3; w++) { en.plateau_walk(8 * en.h, rng); en.climb(MAXSTEP); if (en.f > bstF && en.feasible_now()) { bstF = en.f; bstA = en.a; } }
                if (en.f > bstF && en.feasible_now()) { bstF = en.f; bstA = en.a; }
            }
        }
        ll q = 0; for (ll v : bstA) q += v;
        if (bstF >= 0 && (R.bestF < 0 || (__int128)bstF * R.bestQ * R.bestQ > (__int128)R.bestF * q * q)) { R.bestF = bstF; R.bestQ = q; R.besta = bstA; R.found = true; }
    }
    return R;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: G10_hunt2 in.txt out.txt [threads] [nrand] [qstart] [nlevel] [num] [den]\n"); return 1; }
    int nthreads = argc > 3 ? atoi(argv[3]) : 8;
    if (argc > 4) NSEED_RAND = atoi(argv[4]);
    if (argc > 5) QSTART = atoi(argv[5]);
    if (argc > 6) NLEVEL = atoi(argv[6]);
    if (argc > 7) NUMER = atoi(argv[7]);
    if (argc > 8) DENOM = atoi(argv[8]);
    vector<Graph> gs;
    { ifstream in(argv[1]); string line;
      while (getline(in, line)) { if (line.empty()) continue; istringstream ss(line); Graph g; int E; ss >> g.name >> g.h >> E; for (int k = 0; k < E; k++) { int u, v; ss >> u >> v; g.edges.push_back({ u,v }); } gs.push_back(g); } }
    fprintf(stderr, "loaded %zu graphs, degree cap = floor(%d q / %d)\n", gs.size(), NUMER, DENOM);
    vector<Result> res(gs.size()); atomic<size_t> next(0); atomic<int> hits(0);
    vector<thread> th;
    for (int t = 0; t < nthreads; t++) th.emplace_back([&]() {
        for (;;) { size_t i = next++; if (i >= gs.size()) break;
            res[i] = run_graph(gs[i], 0x9E3779B97F4A7C15ull * (i + 7) + 999);
            if (res[i].found && (__int128)25 * res[i].bestF > (__int128)res[i].bestQ * res[i].bestQ) hits++; } });
    for (auto& x : th) x.join();
    FILE* out = fopen(argv[2], "w");
    for (size_t i = 0; i < gs.size(); i++) { Result& R = res[i];
        fprintf(out, "%s %d %lld %lld %lld %d :", R.name.c_str(), R.h, R.bestF, R.bestQ, (ll)(25 * R.bestF - R.bestQ * R.bestQ), (int)R.found);
        for (ll v : R.besta) fprintf(out, " %lld", v);
        fprintf(out, "\n"); }
    fclose(out);
    fprintf(stderr, "done. strict-hits(25F>Q^2) = %d\n", (int)hits);
    return 0;
}
