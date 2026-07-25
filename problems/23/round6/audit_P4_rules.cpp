// audit_P4_rules.cpp - test P4.md's SURVIVING SUGGESTION
//     R(mu) = min( min over arcs of length exactly 1/2 , min over arcs of length exactly 1/3 )
// against (i) exhaustive integer enumeration and (ii) directed max search.
//
// NOTE the trap: the family of ALL arc cuts is closed under complementation (a window of l points
// and its complement of M-l points give the SAME bipartition), so "min over all windows of size
// <= M/2" is just ARCBOUND and testing it proves nothing.  Here the two families are the EXACT
// lengths:
//    HALF  : window sizes realisable as grid n [a, a+1/2)   -> {M/2} (M even), {(M-1)/2,(M+1)/2}
//    THIRD : window sizes realisable as grid n (arc of length exactly 1/3)
//            -> {floor(M/3), ceil(M/3)} and, when 3|M, also M/3-1 and M/3+1 (open/closed ends;
//               endpoints at distance exactly 1/3 are NOT adjacent, so the closed arc is still
//               independent)
// All integer arithmetic; the test is  25 * minval  >  q^2  (a violation refutes the rule).
//
// build: clang++ -O3 -march=native -std=c++17 audit_P4_rules.cpp -o audit_P4_rules.exe
// usage: audit_P4_rules exhaust m q mode        mode = all | ht | third | half
//        audit_P4_rules search  m q mode iters seed
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <random>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>
using namespace std;

static int M, Q, DMIN;
static vector<int> SIZES;          // window sizes in the family
static std::mutex io_mtx;
static bool MODE_J1 = false;       // j1 : objective = min( A , min over 1/3-arcs ), scaled by M
static long long SC = 1;           // violation test is 25*val > SC*q^2

static void build_sizes(const string &mode) {
    SIZES.clear();
    vector<int> half, third;
    if (M % 2 == 0) half = {M / 2};
    else half = {M / 2, M / 2 + 1};
    if (M % 3 == 0) third = {M / 3 - 1, M / 3, M / 3 + 1};
    else third = {M / 3, M / 3 + 1};
    if (mode == "all") { for (int l = 1; l < M; l++) SIZES.push_back(l); }
    else if (mode == "half") SIZES = half;
    else if (mode == "third") SIZES = third;
    else if (mode == "j1") { SIZES = third; MODE_J1 = true; SC = M; }
    else { SIZES = half; for (int t : third) SIZES.push_back(t); }
    sort(SIZES.begin(), SIZES.end());
    SIZES.erase(unique(SIZES.begin(), SIZES.end()), SIZES.end());
    while (!SIZES.empty() && SIZES.back() >= M) SIZES.pop_back();
}

struct Eval {
    vector<long long> pref, g, wg;
    Eval() : pref(2 * M + 1, 0), g(M, 0), wg(M, 0) {}
    long long W;
    inline long long rangesum(int a, int b) { return pref[b + 1] - pref[a]; }

    long long value(const vector<int> &w) {
        for (int i = 0; i < 2 * M; i++) pref[i + 1] = pref[i] + w[i % M];
        long long tot = 0;
        for (int u = 0; u < M; u++) {
            long long s = 0;
            for (int j = DMIN; j <= M - DMIN; j++) s += w[(u + j) % M];
            g[u] = s; wg[u] = (long long)w[u] * s; tot += wg[u];
        }
        W = tot / 2;
        long long best = -1;
        for (int i = 0; i < M; i++) {
            long long inside = 0, sumwg = 0;
            size_t si = 0;
            for (int l = 0; l < M && si < SIZES.size(); l++) {
                int t = (i + l) % M;
                int hi = min(l, M - DMIN);
                long long ins = 0;
                if (hi >= DMIN) {
                    int a = ((t - hi) % M + M) % M;
                    ins = rangesum(a, a + (hi - DMIN));
                }
                inside += (long long)w[t] * ins;
                sumwg += wg[t];
                if ((int)(l + 1) == SIZES[si]) {
                    long long mono = W - sumwg + 2 * inside;
                    if (best < 0 || mono < best) best = mono;
                    si++;
                }
            }
        }
        if (MODE_J1) {
            long long Tint = 0;
            for (int u = 0; u < M; u++) {
                long long s2 = 0;
                for (int j = DMIN; j <= M - DMIN; j++) s2 += (long long)min(j, M - j) * w[(u + j) % M];
                Tint += (long long)w[u] * s2;
            }
            Tint /= 2;
            long long Ascaled = (long long)M * W - 2 * Tint;   // = A * M * q^2
            long long mm = (long long)M * best;                // = min_b m(b) * M * q^2
            return min(Ascaled, mm);
        }
        return best;
    }
};

// ------------------------------------------------------------------ exhaustive
struct Ex {
    Eval ev; vector<int> w; long long cnt = 0, viol = 0, eq = 0; long long bestv = -1; vector<int> bestw;
    Ex() : w(M, 0) {}
    void visit() {
        long long b = ev.value(w);
        cnt++;
        if (bestv < 0 || b * (long long)Q * Q > bestv * (long long)Q * Q) {}
        if (25 * b > SC * (long long)Q * Q) {
            viol++;
            lock_guard<std::mutex> lk(io_mtx);
            printf("VIOLATION m=%d q=%d w=", M, Q);
            for (int i = 0; i < M; i++) printf("%d%s", w[i], i + 1 < M ? "," : "");
            printf("  25*min=%lld SC*q^2=%lld\n", 25 * b, SC * (long long)Q * Q);
        } else if (25 * b == SC * (long long)Q * Q) eq++;
    }
    void rec(int idx, int rem) {
        if (idx == M - 1) { w[idx] = rem; visit(); return; }
        for (int v = 0; v <= rem; v++) { w[idx] = v; rec(idx + 1, rem - v); }
        w[idx] = 0;
    }
};

// ------------------------------------------------------------------ search
static void search(int iters, uint64_t seed) {
    std::mt19937_64 rng(seed);
    Eval ev;
    vector<int> w(M, 0), best(M, 0);
    long long bestval = -1;
    for (int it = 0; it < iters; it++) {
        // random start
        fill(w.begin(), w.end(), 0);
        for (int k = 0; k < Q; k++) w[rng() % M]++;
        long long cur = ev.value(w);
        bool improved = true;
        while (improved) {
            improved = false;
            for (int i = 0; i < M && !improved; i++) {
                if (!w[i]) continue;
                for (int j = 0; j < M && !improved; j++) {
                    if (i == j) continue;
                    w[i]--; w[j]++;
                    long long v = ev.value(w);
                    if (v > cur) { cur = v; improved = true; }
                    else { w[i]++; w[j]--; }
                }
            }
        }
        if (cur > bestval) {
            bestval = cur; best = w;
            lock_guard<std::mutex> lk(io_mtx);
            printf("  m=%d q=%d new best 25*val=%lld vs SC*q^2=%lld  ratio=%.6f  w=",
                   M, Q, 25 * cur, SC * (long long)Q * Q, 25.0 * cur / ((double)SC * Q * Q));
            for (int i = 0; i < M; i++) printf("%d%s", best[i], i + 1 < M ? "," : "");
            printf("%s\n", 25 * cur > SC * (long long)Q * Q ? "   *** VIOLATION ***" : "");
        }
    }
    printf("m=%d q=%d : best 25*val=%lld  q^2=%lld  (violation? %s)\n", M, Q, 25 * bestval,
           SC * (long long)Q * Q, 25 * bestval > SC * (long long)Q * Q ? "YES" : "no");
}

int main(int argc, char **argv) {
    if (argc < 5) { printf("usage: %s exhaust|search m q mode [iters seed]\n", argv[0]); return 1; }
    string cmd = argv[1];
    M = atoi(argv[2]); Q = atoi(argv[3]); DMIN = M / 3 + 1;
    build_sizes(argv[4]);
    printf("# Gamma_%d q=%d dmin=%d mode=%s window sizes={", M, Q, DMIN, argv[4]);
    for (size_t i = 0; i < SIZES.size(); i++) printf("%d%s", SIZES[i], i + 1 < SIZES.size() ? "," : "");
    printf("}\n");
    if (cmd == "search") { search(argc > 5 ? atoi(argv[5]) : 200, argc > 6 ? atoll(argv[6]) : 1); return 0; }
    if (cmd == "eval") {                       // audit_P4_rules eval m q mode w0,w1,...
        vector<int> w; char *p = strtok(argv[5], ",");
        while (p) { w.push_back(atoi(p)); p = strtok(nullptr, ","); }
        if ((int)w.size() != M) { printf("bad weight vector\n"); return 1; }
        Eval ev; long long b = ev.value(w);
        printf("min over family = %lld / q^2 = %lld ; 25*min = %lld vs q^2 = %lld -> %s\n",
               b, SC * (long long)Q * Q, 25 * b, SC * (long long)Q * Q,
               25 * b > SC * (long long)Q * Q ? "VIOLATION" : "ok");
        return 0;
    }
    int nthreads = min(8, Q + 1);
    vector<Ex> ws(Q + 1);
    vector<thread> th;
    std::atomic<int> next{0};
    for (int t = 0; t < nthreads; t++)
        th.emplace_back([&]() {
            for (;;) {
                int v0 = next.fetch_add(1);
                if (v0 > Q) break;
                Ex &wk = ws[v0];
                wk.w.assign(M, 0); wk.w[0] = v0;
                if (M == 1) { if (v0 == Q) wk.visit(); continue; }
                wk.rec(1, Q - v0);
            }
        });
    for (auto &x : th) x.join();
    long long c = 0, v = 0, e = 0;
    for (auto &wk : ws) { c += wk.cnt; v += wk.viol; e += wk.eq; }
    printf("Gamma_%d q=%d mode=%s : weightings=%lld violations=%lld equalities=%lld\n",
           M, Q, argv[4], c, v, e);
    return 0;
}
