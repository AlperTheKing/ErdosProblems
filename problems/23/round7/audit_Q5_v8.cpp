// A6: INDEPENDENT exhaustive integer-weight sweep looking for  psi > 1/25.
// With x = k/D,  psi(G,x) = M(k)/D^2,  M(k) = min over cuts of the monochromatic
// sum of k_u k_v, so a violation is exactly  25 * M(k) > D * D  -- pure integers.
// Zero weights ARE allowed (accepted base 2).  Own composition enumerator, own cut
// enumeration, no library, 8 threads.
//   usage: audit_Q5_v8.exe <D> [V8|And4|And5|C5|N14]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;

int N;
vector<pair<int,int>> E;
vector<vector<pair<int,int>>> monoOf;

static void build_cuts() {
    monoOf.clear();
    for (int m = 0; m < (1 << (N - 1)); m++) {
        int S = m << 1;
        vector<pair<int,int>> mo;
        for (auto &e : E)
            if ((((S >> e.first) ^ (S >> e.second)) & 1) == 0) mo.push_back(e);
        monoOf.push_back(mo);
    }
    sort(monoOf.begin(), monoOf.end(),
         [](const vector<pair<int,int>> &a, const vector<pair<int,int>> &b) {
             return a.size() < b.size(); });
}

static void circ(int n, int k) {          // Gamma_n with i~j iff 3*dist > n
    N = n;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
        int d = min((j - i + n) % n, (i - j + n) % n);
        if (3 * d > n) E.push_back({i, j});
    }
    (void)k;
}

// next composition of a fixed sum over parts lo..hi (lexicographic); false when done
static bool next_comp(vector<int> &k, int lo, int hi) {
    if (hi <= lo) return false;
    int i = hi - 1;
    while (i >= lo && k[i] == 0) i--;
    if (i < lo) return false;
    int v = k[hi];
    k[i] -= 1;
    k[i + 1] = v + 1;
    if (i + 1 != hi) k[hi] = 0;
    return true;
}

int main(int argc, char **argv) {
    int D = argc > 1 ? atoi(argv[1]) : 20;
    string g = argc > 2 ? argv[2] : "V8";
    // mode 0 (default): violation search only -- early exit as soon as the running
    //   min proves 25*M <= D^2 (SOUND for the violation test, the reported max is
    //   then only an upper-bound artefact and is suppressed).
    // mode 1: no early exit -- the true max of psi over the grid.
    int mode = argc > 3 ? atoi(argv[3]) : 0;
    if (g == "V8") {
        N = 8;
        for (int i = 0; i < 8; i++) {
            E.push_back({i, (i + 1) % 8});
            if (i < 4) E.push_back({i, i + 4});
        }
    } else if (g == "And4") circ(11, 4);
    else if (g == "And5")   circ(14, 5);
    else if (g == "C5")     circ(5, 2);
    else {                                        // graph6
        vector<int> d;
        for (char c : g) d.push_back((int)c - 63);
        N = d[0];
        vector<int> bits;
        for (size_t i = 1; i < d.size(); i++)
            for (int k = 5; k >= 0; k--) bits.push_back((d[i] >> k) & 1);
        int idx = 0;
        for (int j = 1; j < N; j++)
            for (int i = 0; i < j; i++) { if (bits[idx]) E.push_back({i, j}); idx++; }
    }
    build_cuts();
    printf("graph=%s N=%d |E|=%d cuts=%d D=%d\n", g.c_str(), N, (int)E.size(),
           (int)monoOf.size(), D);
    fflush(stdout);

    const long long thr = (long long)D * D;
    long long total = 0, bestG = -1, nviolG = 0;
    vector<int> bestvecG(N, 0);
    mutex mtx;
    int NT = 8;
    vector<thread> th;
    for (int t = 0; t < NT; t++) {
        th.emplace_back([&, t]() {
            vector<int> k(N, 0);
            long long lc = 0, lbest = -1, lviol = 0;
            vector<int> lbv(N, 0);
            for (int k0 = t; k0 <= D; k0 += NT) {
                for (int i = 0; i < N; i++) k[i] = 0;
                k[0] = k0;
                if (N > 1) k[1] = D - k0;
                while (true) {
                    lc++;
                    long long M = -1;
                    for (auto &mo : monoOf) {
                        long long s = 0;
                        for (auto &e : mo) s += (long long)k[e.first] * k[e.second];
                        if (M < 0 || s < M) { M = s; if (mode == 0 && 25 * M <= thr) break; }
                    }
                    if (M > lbest) { lbest = M; lbv = k; }
                    if (25 * M > thr) {
                        lviol++;
                        lock_guard<mutex> lg(mtx);
                        printf("VIOLATION 25*M=%lld > D^2=%lld  k=", 25 * M, thr);
                        for (int i = 0; i < N; i++) printf("%d%s", k[i], i + 1 < N ? "," : "\n");
                    }
                    if (N <= 1) break;
                    if (!next_comp(k, 1, N - 1)) break;
                }
            }
            lock_guard<mutex> lg(mtx);
            total += lc; nviolG += lviol;
            if (lbest > bestG) { bestG = lbest; bestvecG = lbv; }
        });
    }
    for (auto &x : th) x.join();
    printf("vectors enumerated: %lld  (expected C(D+N-1,N-1))\n", total);
    printf("violations (25*M > D^2): %lld\n", nviolG);
    if (mode == 1) {
        printf("TRUE max M = %lld at k=", bestG);
        for (int i = 0; i < N; i++) printf("%d%s", bestvecG[i], i + 1 < N ? "," : "\n");
        printf("TRUE max psi = %lld/%lld = %.10f  (1/25 = %.10f)\n", bestG, thr,
               (double)bestG / (double)thr, 1.0 / 25);
    } else {
        printf("(mode 0: max suppressed -- early exit makes it an artefact of the "
               "threshold; only the violation count is meaningful)\n");
    }
    return 0;
}
