// AUDIT of P2 section 6 -- INDEPENDENT re-implementation of the exhaustive integer sweep.
//
// Deliberately different internals from P2_exhaust.cpp:
//   * P2_exhaust carries the two SCALARS Wn,Tn incrementally down the DFS.
//     Here we carry the per-vertex VECTORS gn[j] = sum_{i~j} w_i and tn[j] = sum_{i~j} d_ij w_i,
//     and rebuild  Wn = (1/2) sum_j w_j gn_j ,  Tn = (1/2) sum_j w_j tn_j  at every leaf.
//     A bug in either incremental scheme therefore shows up as a mismatch of the totals.
//   * every acceptance test is an integer comparison; the running maxima are tracked as EXACT
//     rationals compared by __int128 cross-multiplication (P2_exhaust ranked with doubles).
//
// Reported per (m,q) and in total:
//   leaves                        (vectors with sum q, w_0 = max_i w_i, w_0 >= 1)
//   candidates                    (W in (0.12,0.2) and A > 1/25)
//   falsifiers                    (candidates with min_{b in supp} m(b) > 1/25  =>  every bound_k > 1/25)
//   max of  LO = min(A, min_b m(b))   <= CRIT   and   max of  HI = min(A, bound_0)  >= CRIT
//     (so if max LO == max HI the exact maximum of CRIT over the space is pinned)
//
// build: C:/msys64/mingw64/bin/clang++.exe -O3 -march=native -std=c++17 audit_P2_sweep.cpp -o audit_P2_sweep.exe
// run:   audit_P2_sweep.exe <mlo> <mhi> [qcap] [falsifier-dump-file]
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>
using namespace std;
typedef long long ll;
typedef __int128 lll;

struct Rat {                      // exact nonnegative rational num/den, den > 0
    lll num = -1, den = 1;
    bool less(const Rat &o) const { return num * o.den < o.num * den; }
};
static mutex g_mtx;

struct Cell {
    int m, q;
    ll leaves = 0, cand = 0, fals = 0;
    Rat lo, hi;                    // running maxima of LO and HI
    vector<int> loArg, hiArg;
    vector<vector<int>> fw;        // every falsifier weight vector
};

static void run_cell(Cell &C) {
    const int m = C.m, q = C.q;
    vector<vector<int>> nb(m);
    vector<vector<int>> dd(m, vector<int>(m, 0));
    for (int i = 0; i < m; i++)
        for (int j = 0; j < m; j++) {
            if (i == j) continue;
            int t = ((i - j) % m + m) % m, d = min(t, m - t);
            dd[i][j] = d;
            if (3 * d > m) nb[i].push_back(j);
        }
    vector<int> w(m, 0);
    vector<ll> gn(m, 0), tn(m, 0);
    const ll qq = (ll)q * q;

    // iterative DFS over compositions with w_0 = max
    // stack frame: current index i, current value c
    vector<int> cur(m, -1);
    int i = 0, rem = q;
    // manual recursion
    struct Frame { int i, c, hi, rem; };
    vector<Frame> st;
    st.push_back({0, 1, q, q});                    // w_0 in [1..q]
    auto assign = [&](int idx, int c) {
        w[idx] = c;
        if (c) for (int j : nb[idx]) { gn[j] += c; tn[j] += (ll)c * dd[idx][j]; }
    };
    auto unassign = [&](int idx) {
        int c = w[idx];
        if (c) for (int j : nb[idx]) { gn[j] -= c; tn[j] -= (ll)c * dd[idx][j]; }
        w[idx] = 0;
    };
    while (!st.empty()) {
        Frame &f = st.back();
        if (f.c > f.hi) { st.pop_back(); if (!st.empty()) unassign(st.back().i); continue; }
        int idx = f.i, c = f.c;
        f.c++;                                       // next sibling on return
        if (w[idx]) unassign(idx);
        assign(idx, c);
        int nrem = f.rem - c;
        if (nrem < 0) { unassign(idx); continue; }
        if (idx + 1 == m) {
            if (nrem == 0) {
                C.leaves++;
                ll Wn2 = 0;                          // 2*Wn
                for (int j = 0; j < m; j++) if (w[j]) Wn2 += (ll)w[j] * gn[j];
                ll Wn = Wn2 / 2;
                if (Wn2 % 2) { printf("PARITY BUG\n"); exit(1); }
                // W in (0.12,0.2):  25 Wn > 3 q^2   and   5 Wn < q^2
                if (25 * Wn > 3 * qq && 5 * Wn < qq) {
                    ll Tn2 = 0;
                    for (int j = 0; j < m; j++) if (w[j]) Tn2 += (ll)w[j] * tn[j];
                    ll Tn = Tn2 / 2;
                    ll An = Wn * (ll)m - 2 * Tn;      // A = An / (q^2 m)
                    if (25 * An > qq * (ll)m) {
                        C.cand++;
                        // m(b) = mnb / q^2
                        ll minmn = -1, sum_wm = 0, gmax = -1;
                        vector<ll> mnv(m, 0);
                        for (int b = 0; b < m; b++) {
                            if (!w[b]) continue;
                            ll s = 0;
                            for (int j : nb[b]) s += (ll)w[j] * gn[j];
                            ll mnb = Wn - s;
                            mnv[b] = mnb;
                            if (minmn < 0 || mnb < minmn) minmn = mnb;
                            sum_wm += (ll)w[b] * mnb;
                            if (gn[b] > gmax) gmax = gn[b];
                        }
                        bool isF = (25 * minmn > qq);
                        if (isF) { C.fals++; C.fw.push_back(w); }
                        // LIM = lim_k bound_k = average of m(b) over the argmax of g
                        ll ln = 0, ld = 0;
                        for (int b = 0; b < m; b++) if (w[b] && gn[b] == gmax) { ln += (ll)w[b] * mnv[b]; ld += w[b]; }
                        // LO = min(A, min_b m(b)) <= CRIT ;  HI = min(A, bound_0, LIM) >= CRIT
                        Rat A{(lll)An, (lll)qq * m}, MM{(lll)minmn, (lll)qq}, B0{(lll)sum_wm, (lll)qq * q};
                        Rat LM{(lll)ln, (lll)ld * qq};
                        Rat lo = A.less(MM) ? A : MM;
                        Rat hi = A.less(B0) ? A : B0;
                        if (LM.less(hi)) hi = LM;
                        if (C.lo.num < 0 || C.lo.less(lo)) { C.lo = lo; C.loArg = w; }
                        if (C.hi.num < 0 || C.hi.less(hi)) { C.hi = hi; C.hiArg = w; }
                    }
                }
            }
            unassign(idx);
            continue;
        }
        int nhi = min(nrem, w[0]);
        st.push_back({idx + 1, 0, nhi, nrem});
    }
}

int main(int argc, char **argv) {
    int mlo = argc > 1 ? atoi(argv[1]) : 5;
    int mhi = argc > 2 ? atoi(argv[2]) : 30;
    int qcap = argc > 3 ? atoi(argv[3]) : 0;
    const char *dump = argc > 4 ? argv[4] : nullptr;

    vector<Cell> cells;
    for (int m = mlo; m <= mhi; m++) {
        int qmax = (m <= 12) ? 20 : (m <= 18) ? 15 : (m <= 24) ? 12 : 10;
        if (qcap) qmax = min(qmax, qcap);
        for (int q = 2; q <= qmax; q++) cells.push_back(Cell{m, q});
    }
    vector<int> order(cells.size());
    for (size_t i = 0; i < order.size(); i++) order[i] = (int)i;
    sort(order.begin(), order.end(), [&](int a, int b) {
        return (double)cells[a].q * cells[a].m > (double)cells[b].q * cells[b].m; });

    atomic<int> next(0);
    auto worker = [&]() {
        while (true) {
            int k = next++;
            if (k >= (int)order.size()) break;
            run_cell(cells[order[k]]);
        }
    };
    vector<thread> th;
    for (int i = 0; i < 8; i++) th.emplace_back(worker);
    for (auto &t : th) t.join();

    ll L = 0, C = 0, Fz = 0;
    Rat LO, HI; vector<int> loArg, hiArg; int loM = 0, loQ = 0, hiM = 0, hiQ = 0;
    FILE *fp = dump ? fopen(dump, "w") : nullptr;
    for (auto &c : cells) {
        L += c.leaves; C += c.cand; Fz += c.fals;
        if (c.fals) printf("  m=%2d q=%2d leaves=%9lld cand=%8lld falsifiers=%lld\n",
                           c.m, c.q, c.leaves, c.cand, c.fals);
        if (c.lo.num >= 0 && (LO.num < 0 || LO.less(c.lo))) { LO = c.lo; loArg = c.loArg; loM = c.m; loQ = c.q; }
        if (c.hi.num >= 0 && (HI.num < 0 || HI.less(c.hi))) { HI = c.hi; hiArg = c.hiArg; hiM = c.m; hiQ = c.q; }
        if (fp) for (auto &v : c.fw) {
            fprintf(fp, "%d %d", c.m, c.q);
            for (int x : v) fprintf(fp, " %d", x);
            fprintf(fp, "\n");
        }
    }
    if (fp) fclose(fp);
    printf("\n=========== AUDIT SWEEP  m in [%d,%d] ===========\n", mlo, mhi);
    printf("leaves      = %lld\n", L);
    printf("candidates  = %lld\n", C);
    printf("falsifiers  = %lld\n", Fz);
    auto pr = [](const char *tag, Rat &r, vector<int> &a, int m, int q) {
        printf("%s = %lld/%lld = %.9f  at m=%d q=%d w=(", tag, (ll)r.num, (ll)r.den,
               (double)(ll)r.num / (double)(ll)r.den, m, q);
        for (size_t i = 0; i < a.size(); i++) printf("%d%s", a[i], i + 1 < a.size() ? "," : "");
        printf(")\n");
    };
    pr("max LO = max min(A, min_b m(b))  <= max CRIT ", LO, loArg, loM, loQ);
    pr("max HI = max min(A, bound_0)     >= max CRIT ", HI, hiArg, hiM, hiQ);
    printf("3/64 = %.9f\n", 3.0 / 64);
    return 0;
}
