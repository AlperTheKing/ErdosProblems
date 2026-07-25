// audit_P4_exhaust.cpp - INDEPENDENT exhaustive integer re-verification of item 3 / P4.md (c).
//
// For the circle graph Gamma_m (u ~ v iff 3*circdist(u,v) > m) and every integer weighting
// w >= 0 with sum(w) = q, check the integer inequality   25 * min_over_arc_cuts(mono) <= q^2 .
// Optionally dump the equality configurations.
//
// mono(S) = W - cross(S),  cross(S) = sum_{u in S} w_u g_u - 2*inside(S),
//   so mono(S) = W - sum_{u in S} w_u g_u + 2*inside(S).
// For an arc S = [t-l, t) the incremental step uses
//   inside(S + {t}) = inside(S) + w_t * sum_{j=dmin}^{min(l, m-dmin)} w_{t-j} .
// Everything is 64-bit integer; nothing floating point anywhere.
//
// build: clang++ -O3 -march=native -std=c++17 audit_P4_exhaust.cpp -o audit_P4_exhaust.exe
// usage: audit_P4_exhaust m q [dumpEqualityFile]
#include <cstdio>
#include <cstdint>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <string>
#include <algorithm>
using namespace std;

static int M, Q, DMIN;
static std::mutex io_mtx;
static std::atomic<long long> total_count{0}, viol_count{0}, eq_count{0};
static FILE *eqf = nullptr;

struct Worker {
    vector<int> w;              // weights
    vector<long long> g;        // g_u = sum of w over neighbours
    vector<long long> pref;     // prefix sums of w over doubled array
    long long W;                // total adjacent weight sum_{u<v adj} w_u w_v
    vector<long long> wg;       // w_u * g_u
    long long best;             // min over arcs
    long long cnt = 0, viol = 0, eq = 0;
    vector<vector<int>> eqs;

    Worker() : w(M, 0), g(M, 0), pref(2 * M + 1, 0), wg(M, 0) {}

    inline long long rangesum(int a, int b) {   // sum of w over indices a..b (cyclic, a<=b, b-a<M)
        return pref[b + 1] - pref[a];
    }

    void prep() {
        for (int i = 0; i < 2 * M; i++) pref[i + 1] = pref[i] + w[i % M];
        for (int u = 0; u < M; u++) {
            long long s = 0;
            for (int j = DMIN; j <= M - DMIN; j++) s += w[(u + j) % M];
            g[u] = s;
            wg[u] = (long long)w[u] * s;
        }
        long long tot = 0;
        for (int u = 0; u < M; u++) tot += (long long)w[u] * g[u];
        W = tot / 2;
    }

    long long arcmin() {
        long long bst = W;                          // l = 0 : S empty, mono = W
        for (int i = 0; i < M; i++) {
            long long inside = 0, sumwg = 0;
            for (int l = 0; l < M; l++) {
                int t = (i + l) % M;
                // add t to S = [i, i+l)
                int hi = min(l, M - DMIN);
                long long ins = 0;
                if (hi >= DMIN) {
                    // sum_{j=DMIN..hi} w_{t-j}  == indices t-hi .. t-DMIN
                    int a = ((t - hi) % M + M) % M;
                    ins = rangesum(a, a + (hi - DMIN));
                }
                inside += (long long)w[t] * ins;
                sumwg += wg[t];
                long long mono = W - sumwg + 2 * inside;
                if (mono < bst) bst = mono;
            }
        }
        return bst;
    }

    void visit() {
        prep();
        long long b = arcmin();
        cnt++;
        if (25 * b > (long long)Q * Q) {
            viol++;
            lock_guard<std::mutex> lk(io_mtx);
            printf("VIOLATION m=%d q=%d w=", M, Q);
            for (int i = 0; i < M; i++) printf("%d%s", w[i], i + 1 < M ? "," : "");
            printf("  25*min=%lld  q^2=%lld\n", 25 * b, (long long)Q * Q);
        } else if (25 * b == (long long)Q * Q) {
            eq++;
            if (eqf) eqs.push_back(w);
        }
    }

    void rec(int idx, int rem) {
        if (idx == M - 1) { w[idx] = rem; visit(); return; }
        for (int v = 0; v <= rem; v++) { w[idx] = v; rec(idx + 1, rem - v); }
        w[idx] = 0;
    }
};

int main(int argc, char **argv) {
    if (argc < 3) { printf("usage: %s m q [eqfile]\n", argv[0]); return 1; }
    M = atoi(argv[1]); Q = atoi(argv[2]);
    DMIN = M / 3 + 1;
    string eqname = (argc > 3) ? argv[3] : "";
    if (!eqname.empty()) eqf = fopen(eqname.c_str(), "w");

    int nthreads = min(8, Q + 1);
    vector<Worker> ws(Q + 1);
    vector<thread> th;
    std::atomic<int> next{0};
    for (int t = 0; t < nthreads; t++) {
        th.emplace_back([&]() {
            for (;;) {
                int v0 = next.fetch_add(1);
                if (v0 > Q) break;
                Worker &wk = ws[v0];
                wk.w.assign(M, 0);
                wk.w[0] = v0;
                if (M == 1) { if (v0 == Q) wk.visit(); continue; }
                wk.rec(1, Q - v0);
            }
        });
    }
    for (auto &x : th) x.join();
    long long c = 0, v = 0, e = 0;
    for (auto &wk : ws) {
        c += wk.cnt; v += wk.viol; e += wk.eq;
        if (eqf) for (auto &ww : wk.eqs) {
            for (int i = 0; i < M; i++) fprintf(eqf, "%d%s", ww[i], i + 1 < M ? "," : "\n");
        }
    }
    if (eqf) fclose(eqf);
    printf("Gamma_%d q=%d dmin=%d : weightings=%lld  violations(25*min>q^2)=%lld  equalities=%lld\n",
           M, Q, DMIN, c, v, e);
    return 0;
}
