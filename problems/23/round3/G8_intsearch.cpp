// G8: exhaustive exact integer-weighting search on Andrasfai graphs.
//
// And(k) = circulant on Z_{3k-1}, connection {i : i = 1 mod 3}.
// bip(And(k)[a]) = min over cuts S of And(k) of sum_{monochromatic uv} a_u a_v.
// For each q we compute  M(q) = max over a>=0 with sum a = q  of that minimum,
// exactly in 64-bit integers, and compare 25*M(q) with q^2.
// 25*M(q) > q^2  for any q  ==>  the Erdos-Faudree-Pach-Spencer conjecture is FALSE.
//
// Zeros are allowed in a.  Rotation symmetry a_0 = max_v a_v is used (And(k) is
// vertex-transitive under v -> v+1), which is exact and loses nothing.
//
// build: clang++ -O3 -march=native -std=c++17 -fopenmp G8_intsearch.cpp -o G8_intsearch
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <thread>
#include <mutex>
#include <atomic>

using namespace std;

int n, K;
vector<pair<int,int>> edges;
vector<vector<pair<int,int>>> cuts;   // mono edge lists

static void build(int k) {
    K = k; n = 3*k - 1;
    vector<vector<char>> adj(n, vector<char>(n, 0));
    for (int v = 0; v < n; v++)
        for (int c = 1; c < n; c++)
            if (c % 3 == 1) { int u = (v + c) % n; adj[v][u] = adj[u][v] = 1; }
    edges.clear();
    for (int u = 0; u < n; u++) for (int v = u+1; v < n; v++) if (adj[u][v]) edges.push_back({u,v});
    cuts.clear();
    for (uint32_t mask = 0; mask < (1u << (n-1)); mask++) {
        vector<int> side(n, 0);
        for (int v = 1; v < n; v++) side[v] = (mask >> (v-1)) & 1;
        vector<pair<int,int>> mono;
        for (auto &e : edges) if (side[e.first] == side[e.second]) mono.push_back(e);
        cuts.push_back(mono);
    }
    // sort cuts by mono size ascending: small cuts usually decide fastest
    sort(cuts.begin(), cuts.end(),
         [](const vector<pair<int,int>> &a, const vector<pair<int,int>> &b){ return a.size() < b.size(); });
}

struct Res { long long best; vector<int> arg; };

static inline long long minmono(const int *a, long long cutoff) {
    // returns min over cuts of sum_{mono} a_u a_v, aborting early if <= cutoff
    long long best = INT64_MAX;
    for (size_t c = 0; c < cuts.size(); c++) {
        long long s = 0;
        const auto &mono = cuts[c];
        for (size_t t = 0; t < mono.size(); t++) {
            s += (long long)a[mono[t].first] * a[mono[t].second];
            if (s >= best) break;
        }
        if (s < best) { best = s; if (best <= cutoff) return best; }
    }
    return best;
}

int main(int argc, char **argv) {
    int k = atoi(argv[1]);
    int qmax = atoi(argv[2]);
    int nthreads = argc > 3 ? atoi(argv[3]) : 8;
    build(k);
    fprintf(stderr, "And(%d): n=%d |E|=%zu cuts=%zu\n", k, n, edges.size(), cuts.size());
    printf("# And(%d) n=%d\n# q  M(q)  25*M(q)  q^2  25M-q^2  argmax\n", k, n);
    fflush(stdout);

    for (int q = 1; q <= qmax; q++) {
        long long globalBest = 0;
        vector<int> globalArg(n, 0);
        // parallel over a_0 (which must be the max entry, so a_0 >= ceil(q/n))
        int lo = (q + n - 1) / n;
        atomic<int> next(lo);
        mutex mtx;
        auto worker = [&]() {
            long long myBest = 0; vector<int> myArg(n, 0);
            vector<int> a(n, 0);
            for (;;) {
                int a0 = next.fetch_add(1);
                if (a0 > q) break;
                a[0] = a0;
                struct Rec {
                    int n; int a0; long long *best; vector<int> *arg; int *a;
                    void go(int i, int rem) {
                        if (i == n-1) {
                            if (rem > a0) return;
                            a[i] = rem;
                            long long v = minmono(a, *best);
                            if (v > *best) { *best = v; arg->assign(a, a+n); }
                            a[i] = 0;
                            return;
                        }
                        int hi = rem < a0 ? rem : a0;
                        for (int t = 0; t <= hi; t++) { a[i] = t; go(i+1, rem - t); }
                        a[i] = 0;
                    }
                } rec{n, a0, &myBest, &myArg, a.data()};
                rec.go(1, q - a0);
            }
            lock_guard<mutex> g(mtx);
            if (myBest > globalBest) { globalBest = myBest; globalArg = myArg; }
        };
        {
            vector<thread> th;
            for (int t = 0; t < nthreads; t++) th.emplace_back(worker);
            for (auto &t : th) t.join();
        }
        long long lhs = 25 * globalBest, rhs = (long long)q * q;
        printf("%d %lld %lld %lld %lld  [", q, globalBest, lhs, rhs, lhs - rhs);
        for (int i = 0; i < n; i++) printf("%d%s", globalArg[i], i+1<n?",":"");
        printf("]%s\n", lhs > rhs ? "   *** COUNTEREXAMPLE ***" : "");
        fflush(stdout);
    }
    return 0;
}
