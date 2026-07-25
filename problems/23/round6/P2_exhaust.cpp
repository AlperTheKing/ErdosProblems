// P2 / round 6 - assignment (b): EXHAUSTIVE integer weightings on the circle graphs Gamma_m.
//
// For every m in [MLO,MHI] and every total weight q <= qmax(m), enumerate all weight vectors
// w in Z_{>=0}^m with sum q (up to rotation, by demanding w_0 = max_i w_i), and compute EXACTLY
//
//    W  = Wn/q^2,          Wn = sum_{i<j, adj} w_i w_j
//    T  = Tn/(q^2 m),      Tn = sum_{i<j, adj} d_ij w_i w_j          (d_ij = index distance)
//    A  = W - 2T          = (Wn*m - 2*Tn) / (q^2 m)
//    g_i = gn_i/q,         gn_i = sum_{j adj i} w_j
//    m_b = mn_b/q^2,       mn_b = Wn - sum_{j adj b} w_j gn_j
//    bound_k = sum_b w_b gn_b^k mn_b / (q^2 sum_b w_b gn_b^k)
//    CRIT = min(A, bound_0..bound_K)
//
// All acceptance tests are integer comparisons (no floating point on any acceptance path):
//    A > 1/25          <=>  25*(Wn*m - 2*Tn) > q*q*m
//    bound_k > 1/25    <=>  25*sum_b w_b gn_b^k mn_b > q*q*sum_b w_b gn_b^k     (__int128)
//
// Doubles are used ONLY to rank/report the running maximum.
//
// build: clang++ -O3 -march=native -std=c++17 P2_exhaust.cpp -o P2_exhaust.exe
// run:   P2_exhaust.exe <mlo> <mhi> <qcap>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>
using namespace std;
typedef long long ll;
typedef __int128 lll;

static const int KMAX = 8;          // levels bound_0 .. bound_KMAX
static mutex g_mtx;

struct Best {
    double crit = -1;
    int m = 0, q = 0;
    vector<int> w;
};

struct Task { int m, q; };

// ---------------------------------------------------------------- per-(m,q) exhaustive DFS
struct Runner {
    int m, q;
    vector<vector<int>> nb;      // neighbours
    vector<vector<int>> dist;    // index distance
    vector<int> w;
    ll Wn = 0, Tn = 0;
    ll leaves = 0, cand = 0, fals = 0;
    Best best;
    vector<vector<int>> falsifiers;

    Runner(int m_, int q_) : m(m_), q(q_), nb(m_), dist(m_, vector<int>(m_, 0)), w(m_, 0) {
        for (int i = 0; i < m; i++)
            for (int j = 0; j < m; j++) {
                if (i == j) continue;
                int t = ((i - j) % m + m) % m;
                int d = min(t, m - t);
                dist[i][j] = d;
                if (3 * d > m) nb[i].push_back(j);
            }
    }

    // full exact evaluation at a leaf; returns CRIT as double, fills flags
    double evaluate(bool &isFals) {
        vector<ll> gn(m, 0), mn(m, 0);
        for (int i = 0; i < m; i++) {
            if (!w[i]) continue;
            ll s = 0;
            for (int j : nb[i]) s += w[j];
            gn[i] = s;
        }
        for (int b = 0; b < m; b++) {
            if (!w[b]) continue;
            ll s = 0;
            for (int j : nb[b]) s += (ll)w[j] * gn[j];
            mn[b] = Wn - s;
        }
        ll qq = (ll)q * q;
        // A
        double A = (double)(Wn * (ll)m - 2 * Tn) / (double)(qq * (ll)m);
        bool aOK = (25 * (Wn * (ll)m - 2 * Tn) > qq * (ll)m);
        double crit = A;
        // RIGOROUS test, valid for EVERY k in [0,infinity): every bound_k is a weighted average
        // of the numbers m(b), hence bound_k >= min_b m(b).  So  A > 1/25  and  min_b m(b) > 1/25
        // together imply CRIT > 1/25 with no truncation of the hierarchy.
        bool allOK = aOK;
        for (int b = 0; b < m; b++) if (w[b] && !(25 * mn[b] > qq)) allOK = false;
        for (int k = 0; k <= KMAX; k++) {
            lll num = 0, den = 0;
            for (int b = 0; b < m; b++) {
                if (!w[b]) continue;
                lll gk = 1;
                for (int t = 0; t < k; t++) gk *= gn[b];
                num += (lll)w[b] * gk * mn[b];
                den += (lll)w[b] * gk;
            }
            if (den == 0) continue;
            double bk = (double)(long double)num / ((double)(long double)den * (double)qq);
            crit = min(crit, bk);
        }
        isFals = allOK;
        return crit;
    }

    void dfs(int i, int rem) {
        if (i == m) {
            if (rem) return;
            leaves++;
            ll qq = (ll)q * q;
            // cheap necessary filters: W in (0.12,0.2) and A > 1/25
            if (25 * Wn <= 3 * qq) return;                       // W <= 0.12
            if (5 * Wn >= qq) return;                            // W >= 0.2
            if (!(25 * (Wn * (ll)m - 2 * Tn) > qq * (ll)m)) return;   // A <= 1/25
            cand++;
            bool isF = false;
            double c = evaluate(isF);
            if (c > best.crit) { best.crit = c; best.m = m; best.q = q; best.w = w; }
            if (isF) { fals++; if ((int)falsifiers.size() < 40) falsifiers.push_back(w); }
            return;
        }
        int hi = (i == 0) ? rem : min(rem, w[0]);   // w_0 must be the maximum (rotation reduction)
        for (int c = (i == 0 ? 1 : 0); c <= hi; c++) {
            // incremental update: edges from i to already-assigned j < i
            ll dW = 0, dT = 0;
            if (c) {
                for (int j : nb[i]) if (j < i && w[j]) { dW += (ll)c * w[j]; dT += (ll)c * w[j] * dist[i][j]; }
            }
            w[i] = c; Wn += dW; Tn += dT;
            dfs(i + 1, rem - c);
            Wn -= dW; Tn -= dT; w[i] = 0;
        }
    }
};

int main(int argc, char **argv) {
    int mlo = argc > 1 ? atoi(argv[1]) : 5;
    int mhi = argc > 2 ? atoi(argv[2]) : 30;
    int qcapArg = argc > 3 ? atoi(argv[3]) : 0;

    vector<Task> tasks;
    for (int m = mlo; m <= mhi; m++) {
        int qmax;
        if (m <= 12) qmax = 20;
        else if (m <= 18) qmax = 15;
        else if (m <= 24) qmax = 12;
        else qmax = 10;
        if (qcapArg) qmax = min(qmax, qcapArg);
        for (int q = 2; q <= qmax; q++) tasks.push_back({m, q});
    }
    // heaviest first so the 8 threads finish together
    sort(tasks.begin(), tasks.end(), [](const Task &a, const Task &b) {
        return (double)a.q * a.m > (double)b.q * b.m; });

    atomic<int> next(0);
    Best gbest;
    ll totLeaves = 0, totCand = 0, totFals = 0;
    vector<string> report;

    auto worker = [&]() {
        while (true) {
            int idx = next++;
            if (idx >= (int)tasks.size()) break;
            Runner r(tasks[idx].m, tasks[idx].q);
            r.dfs(0, r.q);
            lock_guard<mutex> lk(g_mtx);
            totLeaves += r.leaves; totCand += r.cand; totFals += r.fals;
            if (r.best.crit > gbest.crit) gbest = r.best;
            for (auto &f : r.falsifiers) {
                char buf[512]; int p = 0;
                p += snprintf(buf + p, sizeof(buf) - p, "FALSIFIER m=%d q=%d w=(", r.m, r.q);
                for (int i = 0; i < r.m; i++) p += snprintf(buf + p, sizeof(buf) - p, "%d%s", f[i], i + 1 < r.m ? "," : "");
                snprintf(buf + p, sizeof(buf) - p, ")");
                report.push_back(buf);
            }
            if (r.cand)
                printf("  m=%2d q=%2d  leaves=%lld  candidates(A>1/25)=%lld  falsifiers=%lld  bestCRIT=%.6f\n",
                       r.m, r.q, r.leaves, r.cand, r.fals, r.best.crit);
            fflush(stdout);
        }
    };
    vector<thread> th;
    int nt = 8;
    for (int i = 0; i < nt; i++) th.emplace_back(worker);
    for (auto &t : th) t.join();

    printf("\n================ SUMMARY  m in [%d,%d] ================\n", mlo, mhi);
    printf("total leaves      = %lld\n", totLeaves);
    printf("A > 1/25 candidates= %lld\n", totCand);
    printf("CRIT > 1/25 (criterion falsifiers) = %lld\n", totFals);
    if (gbest.crit > 0) {
        printf("max CRIT over the candidate set = %.8f  (1/25 = %.8f)  at m=%d q=%d w=(",
               gbest.crit, 0.04, gbest.m, gbest.q);
        for (int i = 0; i < gbest.m; i++) printf("%d%s", gbest.w[i], i + 1 < gbest.m ? "," : "");
        printf(")\n");
    } else {
        printf("no weighting anywhere in this range even has A > 1/25 together with W in (0.12,0.2)\n");
    }
    for (auto &s : report) printf("%s\n", s.c_str());
    return 0;
}
