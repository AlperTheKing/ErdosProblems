// G10_exh.cpp -- EXHAUSTIVE exact integer search:  over ALL a >= 0 (zeros allowed)
// with sum a = q, maximise  bip(H[a]) = min over cuts of sum_{mono} a_u a_v.
// Complete at grid resolution 1/q; all arithmetic is 64-bit integer.
//
// usage: G10_exh in.txt q [threads]
// output per graph: name h q bestF 25*bestF-q^2 : a_0 ... a_{h-1}
//
// build: clang++ -O3 -march=native -std=c++17 G10_exh.cpp -o G10_exh.exe

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
#include <sstream>
#include <fstream>
using namespace std;
typedef long long ll;

struct Graph { string name; int h; vector<pair<int, int>> edges; };

struct Solver {
    int h, NC, Q;
    vector<uint32_t> adjm;
    // monoNb[c*h+v] = bitmask of neighbours of v on v's side of cut c
    vector<uint32_t> monoNb;
    vector<ll> Qacc;     // (h+1) * NC   partial cut sums
    vector<ll> Sacc;     // (h+1) * NC * h  partial "assigned mono-neighbour weight" per vertex
    vector<ll> a;
    ll best; vector<ll> besta;
    ll target = -1;                 // if >=0: ENUMERATE every a with bip >= target
    ll besthit = -1;
    vector<vector<ll>> hits;

    void init(const Graph& g, int q) {
        h = g.h; Q = q; NC = 1 << (h - 1);
        adjm.assign(h, 0);
        for (auto& e : g.edges) { adjm[e.first] |= 1u << e.second; adjm[e.second] |= 1u << e.first; }
        monoNb.assign((size_t)NC * h, 0);
        uint32_t full = (1u << h) - 1u;
        for (int c = 0; c < NC; c++) {
            uint32_t m = ((uint32_t)c) << 1;
            for (int v = 0; v < h; v++) {
                uint32_t side = (m >> v) & 1u;
                monoNb[(size_t)c * h + v] = adjm[v] & (side ? m : (~m & full));
            }
        }
        Qacc.assign((size_t)(h + 1) * NC, 0);
        Sacc.assign((size_t)(h + 1) * NC * h, 0);
        a.assign(h, 0);
        best = -1; besta.assign(h, 0);
    }

    void dfs(int j, ll rem) {
        ll* Qp = &Qacc[(size_t)j * NC];
        ll* Sp = &Sacc[(size_t)j * NC * h];
        if (j == h - 1) {
            a[j] = rem;
            ll mn = (ll)4e18;
            for (int c = 0; c < NC; c++) {
                ll v = Qp[c] + rem * Sp[(size_t)c * h + j];
                if (v < mn) { mn = v; if (mn <= best) break; }
            }
            // In ENUMERATION mode `best` must stay pinned at target-1: the early exit
            // above is only sound as "mn < target", and updating best would both
            // record non-minimal mn and prune away genuine hits.
            if (target >= 0) { if (mn >= target) { hits.push_back(a); if (mn > besthit) { besthit = mn; besta = a; } } return; }
            if (mn > best) { best = mn; besta = a; }
            return;
        }
        ll* Qn = &Qacc[(size_t)(j + 1) * NC];
        ll* Sn = &Sacc[(size_t)(j + 1) * NC * h];
        for (ll k = 0; k <= rem; k++) {
            a[j] = k;
            // propagate
            for (int c = 0; c < NC; c++) {
                const ll* Sc = &Sp[(size_t)c * h];
                ll* Sd = &Sn[(size_t)c * h];
                Qn[c] = Qp[c] + k * Sc[j];
                for (int v = 0; v < h; v++) Sd[v] = Sc[v];
                if (k) { uint32_t nb = monoNb[(size_t)c * h + j]; while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; Sd[u] += k; } }
            }
            // upper bound: any completion adds at most  rem2 * max_u>j S + rem2^2/4
            // (Motzkin-Straus: sum over edges of a triangle-free graph <= (sum a)^2/4)
            ll rem2 = rem - k;
            if (best >= 0) {
                ll ub = (ll)4e18;
                for (int c = 0; c < NC; c++) {
                    const ll* Sd = &Sn[(size_t)c * h];
                    ll mx = 0; for (int v = j + 1; v < h; v++) if (Sd[v] > mx) mx = Sd[v];
                    ll b = Qn[c] + rem2 * mx + rem2 * rem2 / 4;
                    if (b < ub) { ub = b; if (ub <= best) break; }
                }
                if (ub <= best) continue;
            }
            dfs(j + 1, rem2);
        }
        a[j] = 0;
    }
};

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: G10_exh in.txt q [threads]\n"); return 1; }
    int q = atoi(argv[2]);
    int nthreads = argc > 3 ? atoi(argv[3]) : 8;
    ll TARGET = argc > 4 ? atoll(argv[4]) : -1;
    vector<Graph> gs;
    { ifstream in(argv[1]); string line;
      while (getline(in, line)) { if (line.empty()) continue; istringstream ss(line); Graph g; int E; ss >> g.name >> g.h >> E; for (int k = 0; k < E; k++) { int u, v; ss >> u >> v; g.edges.push_back({ u,v }); } gs.push_back(g); } }
    fprintf(stderr, "loaded %zu graphs, q=%d\n", gs.size(), q);
    vector<ll> bestF(gs.size(), -1); vector<vector<ll>> bestA(gs.size());
    atomic<size_t> next(0);
    vector<thread> th;
    mutex mu;
    for (int t = 0; t < nthreads; t++) th.emplace_back([&]() {
        for (;;) { size_t i = next++; if (i >= gs.size()) break;
            Solver S; S.init(gs[i], q); S.target = TARGET; if (TARGET >= 0) S.best = TARGET - 1; S.dfs(0, q);
            lock_guard<mutex> lk(mu); bestF[i] = (TARGET>=0? S.besthit : S.best); bestA[i] = S.besta;
            if (TARGET >= 0) { printf("#HITS %s %zu\n", gs[i].name.c_str(), S.hits.size());
                for (auto& v : S.hits) { printf("HIT %s :", gs[i].name.c_str()); for (ll z : v) printf(" %lld", z); printf("\n"); } } } });
    for (auto& x : th) x.join();
    for (size_t i = 0; i < gs.size(); i++) {
        printf("%s %d %d %lld %lld :", gs[i].name.c_str(), gs[i].h, q, bestF[i], (ll)(25 * bestF[i] - (ll)q * q));
        for (ll v : bestA[i]) printf(" %lld", v);
        printf("\n");
    }
    return 0;
}
