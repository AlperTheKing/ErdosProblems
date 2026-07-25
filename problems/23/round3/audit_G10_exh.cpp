// audit_G10_exh.cpp -- INDEPENDENT exhaustive exact-integer verification of the
// claims in round3/G10.md section 3(d).
//
// For a graph H (h <= 16), a budget q and a threshold T, enumerate EVERY integer
// weight vector a >= 0 with sum a = q (zeros allowed) such that
//        bip(H[a]) = min over all 2^(h-1) cuts of sum_{mono} a_u a_v   >=  T
// and print them.  Running with T and with T+1 pins the exact maximum.
//
// Deliberately DIFFERENT from G10_exh.cpp: plain recursive composition enumeration
// with NO incremental Q/S propagation and NO Motzkin-Straus bound; each candidate is
// scored from scratch against precomputed monochromatic edge lists, aborting as soon
// as one cut falls below T (which is the only sound early exit for a >= T test).
// All arithmetic is 64-bit integer.
//
// usage: audit_G10_exh graphs.txt q T [threads]
// build: clang++ -O3 -march=native -std=c++17 audit_G10_exh.cpp -o audit_G10_exh.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <fstream>
#include <sstream>
#include <algorithm>
using namespace std;
typedef long long ll;

struct G { string name; int h; vector<pair<int, int>> e; };

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: audit_G10_exh graphs.txt q T [threads]\n"); return 1; }
    int q = atoi(argv[2]);
    ll T = atoll(argv[3]);
    int nth = argc > 4 ? atoi(argv[4]) : 8;
    vector<G> gs;
    { ifstream in(argv[1]); string line;
      while (getline(in, line)) { if (line.size() < 3) continue; istringstream ss(line); G g; int E;
          ss >> g.name >> g.h >> E; for (int k = 0; k < E; k++) { int u, v; ss >> u >> v; g.e.push_back({u, v}); } gs.push_back(g); } }

    for (auto& g : gs) {
        int h = g.h, NC = 1 << (h - 1);
        // monochromatic edge lists, one flat array per cut
        vector<vector<pair<int,int>>> mono(NC);
        for (int c = 0; c < NC; c++) {
            uint32_t m = ((uint32_t)c) << 1;          // vertex 0 always on side 0
            for (auto& p : g.e) if ((((m >> p.first) ^ (m >> p.second)) & 1u) == 0u) mono[c].push_back(p);
        }
        // order cuts by increasing number of monochromatic edges: cheap cuts first,
        // they are the ones most likely to kill a candidate immediately.
        vector<int> ord(NC); for (int i = 0; i < NC; i++) ord[i] = i;
        stable_sort(ord.begin(), ord.end(), [&](int x, int y) { return mono[x].size() < mono[y].size(); });

        atomic<ll> nhit(0);
        vector<ll> scannedv(nth, 0);
        vector<vector<vector<ll>>> hits(nth);
        vector<ll> maxseen(nth, -1);
        vector<thread> th;
        atomic<int> nextfirst(0);
        for (int t = 0; t < nth; t++) th.emplace_back([&, t]() {
            vector<ll> a(h, 0);
            for (;;) {
                int a0 = nextfirst++;
                if (a0 > q) break;
                a[0] = a0;
                // recursive enumeration of a[1..h-1] summing to q-a0
                struct Rec {
                    int h; ll T; const vector<vector<pair<int,int>>>* mono; const vector<int>* ord;
                    vector<ll>* a; atomic<ll>* nhit; ll* scanned; vector<vector<ll>>* hits; ll* maxseen;
                    void go(int j, ll rem) {
                        vector<ll>& A = *a;
                        if (j == h - 1) {
                            A[j] = rem;
                            (*scanned)++;
                            ll mn = -1;
                            bool ok = true;
                            for (int k = 0; k < (int)ord->size(); k++) {
                                const vector<pair<int,int>>& M = (*mono)[(*ord)[k]];
                                ll s = 0;
                                for (size_t z = 0; z < M.size(); z++) s += A[M[z].first] * A[M[z].second];
                                if (mn < 0 || s < mn) mn = s;
                                if (mn < T) { ok = false; break; }
                            }
                            if (ok) { (*nhit)++; hits->push_back(A); if (mn > *maxseen) *maxseen = mn; }
                            return;
                        }
                        for (ll k = 0; k <= rem; k++) { A[j] = k; go(j + 1, rem - k); }
                        A[j] = 0;
                    }
                } R{h, T, &mono, &ord, &a, &nhit, &scannedv[t], &hits[t], &maxseen[t]};
                if (h == 1) { if (a0 == q) {} }
                else R.go(1, q - a0);
            }
        });
        for (auto& x : th) x.join();
        ll mx = -1; ll tot = 0; ll scanned = 0; for (int t = 0; t < nth; t++) scanned += scannedv[t];
        vector<vector<ll>> all;
        for (int t = 0; t < nth; t++) { if (maxseen[t] > mx) mx = maxseen[t]; tot += (ll)hits[t].size(); for (auto& v : hits[t]) all.push_back(v); }
        sort(all.begin(), all.end());
        printf("#GRAPH %s h=%d q=%d T=%lld  scanned=%lld  hits=%lld  max_among_hits=%lld\n",
               g.name.c_str(), h, q, T, scanned, tot, mx);
        for (auto& v : all) { printf("HIT %s :", g.name.c_str()); for (ll z : v) printf(" %lld", z); printf("\n"); }
        fflush(stdout);
    }
    return 0;
}
