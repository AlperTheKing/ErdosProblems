// AUDIT of G8 section 5: independent exact integer-weighting search.
//
// Independent choices vs the target:
//   * the graph is built in the CIRCULAR COMPLETE form K_{p/k}: i~j iff k <= (i-j) mod p <= p-k
//     (isomorphic to the target's circulant, but a different code path);
//   * for k=3 NO symmetry reduction is used at all (full enumeration of every
//     composition of q into n nonnegative parts);
//   * cuts are stored as 64-bit side masks and mono values recomputed from the
//     edge list each time (no presorted cut pool).
//
// M(q) = max_{a>=0, sum a = q} min_{cuts S} sum_{mono uv} a_u a_v = max_a bip(And(k)[a]).
// Reports 25*M(q) vs q^2.
//
// build: clang++ -O3 -march=native -std=c++17 audit_G8_int.cpp -o audit_G8_int
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <thread>
#include <mutex>
#include <atomic>
using namespace std;

static int n, K;
static vector<pair<int,int>> E;
static vector<vector<pair<int,int>>> mono;   // per cut

static void build(int k) {
    K = k; n = 3*k - 1;
    E.clear();
    for (int i = 0; i < n; i++)
        for (int j = i+1; j < n; j++) {
            int d = (j - i) % n;
            if (d >= k && d <= n - k) E.push_back({i,j});
        }
    mono.clear();
    for (uint32_t m = 0; m < (1u << (n-1)); m++) {
        vector<int> side(n,0);
        for (int v = 1; v < n; v++) side[v] = (m >> (v-1)) & 1;
        vector<pair<int,int>> mo;
        for (auto &e : E) if (side[e.first] == side[e.second]) mo.push_back(e);
        mono.push_back(mo);
    }
}

static inline long long minval(const int *a, long long cutoff) {
    long long best = INT64_MAX;
    for (size_t c = 0; c < mono.size(); c++) {
        long long s = 0;
        const auto &mo = mono[c];
        for (size_t t = 0; t < mo.size(); t++) {
            s += (long long)a[mo[t].first] * a[mo[t].second];
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
    int usesym = argc > 4 ? atoi(argv[4]) : 0;      // 0 = full enumeration, 1 = a_0 = max
    build(k);
    fprintf(stderr, "K_{%d/%d}: n=%d |E|=%zu cuts=%zu sym=%d\n", n, k, n, E.size(), mono.size(), usesym);
    printf("# And(%d) as K_{%d/%d}, n=%d, sym=%d\n# q M(q) 25M q^2 25M-q^2 argmax\n", k, n, k, n, usesym);
    for (int q = 1; q <= qmax; q++) {
        long long gbest = 0; vector<int> garg(n,0);
        atomic<int> nxt(0);
        mutex mtx;
        int a0hi = usesym ? q : q;
        int a0lo = usesym ? (q + n - 1)/n : 0;
        auto worker = [&]() {
            long long mybest = 0; vector<int> myarg(n,0);
            vector<int> a(n,0);
            for (;;) {
                int a0 = a0lo + nxt.fetch_add(1);
                if (a0 > a0hi) break;
                a[0] = a0;
                // recursive fill of a[1..n-1] summing to q-a0
                struct R {
                    int n, a0, usesym; long long *best; vector<int> *arg; int *a;
                    void go(int i, int rem) {
                        if (i == n-1) {
                            if (usesym && rem > a0) return;
                            a[i] = rem;
                            long long v = minval(a, *best);
                            if (v > *best) { *best = v; arg->assign(a, a+n); }
                            a[i] = 0; return;
                        }
                        int hi = rem;
                        if (usesym && a0 < hi) hi = a0;
                        for (int t = 0; t <= hi; t++) { a[i] = t; go(i+1, rem-t); }
                        a[i] = 0;
                    }
                } r{n, a0, usesym, &mybest, &myarg, a.data()};
                r.go(1, q - a0);
            }
            lock_guard<mutex> g(mtx);
            if (mybest > gbest) { gbest = mybest; garg = myarg; }
        };
        vector<thread> th;
        for (int t = 0; t < nthreads; t++) th.emplace_back(worker);
        for (auto &t : th) t.join();
        long long lhs = 25*gbest, rhs = (long long)q*q;
        printf("%d %lld %lld %lld %lld [", q, gbest, lhs, rhs, lhs-rhs);
        for (int i = 0; i < n; i++) printf("%d%s", garg[i], i+1<n?",":"");
        printf("]%s%s\n", lhs > rhs ? "  *** COUNTEREXAMPLE ***" : "", lhs == rhs ? "  EQUALITY" : "");
        fflush(stdout);
    }
    return 0;
}
