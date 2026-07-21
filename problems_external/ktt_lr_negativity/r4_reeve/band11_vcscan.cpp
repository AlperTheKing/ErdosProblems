// band11_vcscan.cpp -- BAND 11 (r=4 Reeve-dimension census, hunter 11/12).
//
// BAND: unbounded weight, TARGETED -- maximise V/c over all shapes.
//
// Derived from gapscan.cpp (same verified r=4 hive core; eval kernel unchanged,
// statistics extended).  All arithmetic is exact integer arithmetic; no float
// is used in any comparison that decides anything (V/c records are compared by
// cross-multiplication of integers).
//
// MODULI.  Q(lam,mu,nu) for r=4 depends on (lam,mu,nu) only through the 9 gaps
//   a = (l1-l2,l2-l3,l3-l4), b = (m1-m2,m2-m3,m3-m4), c = (n1-n2,n2-n3,n3-n4),
// up to an INTEGER translation of R^3, hence L(n) = #(nQ cap Z^3) depends only
// on the gaps.  Realisable by partitions iff D = Cw-Aw-Bw == 0 (mod 4).
// Scanning [0,G]^9 in gap space is therefore an EXHAUSTIVE census of ALL r=4
// triples of EVERY weight whose consecutive-part gaps are all <= G.
//
// EHRHART.  P(n) = L(n), deg <= 3, L(0)=1:
//   V   = 6a3 = L3 - 3L2 + 3L1 - 1                    (normalized volume)
//   6a1 = -11 + 18L1 - 9L2 + 2L3
//   h* = (1, h1, h2, h3), h1 = L1-4, h3 = L3 - 4L2 + 6L1 - 4  (= # interior pts)
//   IDENTITY (exact):  6a1 = 3*L1 + 3*h3 - V.   So
//        a1 < 0  <==>  V > 3*(c + h3),   c = L1.
//   In particular V/c > 3 is NECESSARY for a KTT counterexample here, and when
//   c = 4 (h*_1 = 0, an empty lattice 3-polytope, e.g. a Reeve simplex) the
//   condition is exactly V >= 13.
//
// Build: clang++ -O3 -march=native -fopenmp -o band11_vcscan.exe band11_vcscan.cpp
// Usage:
//   band11_vcscan G                 exhaustive scan of [0,G]^9
//   band11_vcscan --one g1..g9      single gap vector, full record
//   band11_vcscan --smallc G CMAX   exhaustive [0,G]^9 but L2,L3 only when L1<=CMAX
//   band11_vcscan --climb K RST SEED  targeted maximisation of V/c
//   band11_vcscan --rand K N SEED   uniform random gap vectors in [0,K]^9

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;

struct Row { int s, q, r; ll rhs; };   // s*x + q*u + r*v <= rhs

static int build_rows(const ll lam[4], const ll mu[4], const ll nu[4], Row out[24]) {
    ll B[5][5];
    for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) B[i][j] = 0;
    ll sl = lam[0] + lam[1] + lam[2] + lam[3];
    ll acc = 0; for (int y = 0; y <= 4; y++) { B[0][y] = acc; if (y < 4) acc += lam[y]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][4 - x] = sl + acc; if (x < 4) acc += mu[x]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][0] = acc; if (x < 4) acc += nu[x]; }
    B[0][0] = 0;
    auto isInt = [](int x, int y) { return (x == 1 && y == 1) || (x == 1 && y == 2) || (x == 2 && y == 1); };
    auto idx = [](int x, int y) { return (x == 1 && y == 1) ? 0 : (x == 1 && y == 2) ? 1 : 2; };
    int nr = 0;
    bool infeasible = false;
    auto add = [&](int px[2], int py[2], int mx[2], int my[2]) {
        ll co[3] = {0, 0, 0}; ll cst = 0;
        for (int t = 0; t < 2; t++) {
            if (isInt(px[t], py[t])) co[idx(px[t], py[t])] -= 1; else cst -= B[px[t]][py[t]];
            if (isInt(mx[t], my[t])) co[idx(mx[t], my[t])] += 1; else cst += B[mx[t]][my[t]];
        }
        if (co[0] == 0 && co[1] == 0 && co[2] == 0) { if (cst > 0) infeasible = true; return; }
        out[nr].s = (int)(co[0] + co[1] + co[2]);
        out[nr].q = (int)co[1];
        out[nr].r = (int)co[2];
        out[nr].rhs = -cst;
        nr++;
    };
    for (int x = 0; x <= 4; x++) for (int y = 0; y <= 4; y++) {
        if (x + y <= 2) { int px[2] = {x + 1, x}, py[2] = {y, y + 1}, mx[2] = {x, x + 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
        if (y >= 1 && x + y <= 3) { int px[2] = {x, x + 1}, py[2] = {y, y}, mx[2] = {x, x + 1}, my[2] = {y + 1, y - 1}; add(px, py, mx, my); }
        if (x >= 1 && x + y <= 3) { int px[2] = {x, x}, py[2] = {y, y + 1}, mx[2] = {x + 1, x - 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
    }
    if (infeasible) return -1;
    return nr;
}

static ll lattice_count(const Row *R, int nr, ll n, ll ulo, ll uhi, ll vlo, ll vhi) {
    ll total = 0;
    ll nulo = n * ulo, nuhi = n * uhi, nvlo = n * vlo, nvhi = n * vhi;
    for (ll u = nulo; u <= nuhi; u++) {
        for (ll v = nvlo; v <= nvhi; v++) {
            ll lo = -(1LL << 60), hi = (1LL << 60);
            bool ok = true;
            for (int k = 0; k < nr; k++) {
                ll rem = n * R[k].rhs - (ll)R[k].q * u - (ll)R[k].r * v;
                if (R[k].s == 0) { if (rem < 0) { ok = false; break; } }
                else if (R[k].s > 0) { if (rem < hi) hi = rem; }
                else { if (-rem > lo) lo = -rem; }
                if (lo > hi) { ok = false; break; }
            }
            if (ok && hi >= lo) total += hi - lo + 1;
        }
    }
    return total;
}

struct Res {
    ll L1, L2, L3, six_a1, V, h1, h2, h3;
    bool valid;
};

// c1flag: if >=0, compute L2,L3 only when L1 <= c1flag (cheap pre-filter mode).
static Res eval_gaps(const int a[3], const int b[3], const int c[3], ll cmax_filter = -1) {
    Res res; res.valid = false;
    res.L1 = res.L2 = res.L3 = 0; res.six_a1 = 0; res.V = 0;
    res.h1 = res.h2 = res.h3 = 0;
    ll Aw = 3LL * a[2] + 2LL * a[1] + a[0];
    ll Bw = 3LL * b[2] + 2LL * b[1] + b[0];
    ll Cw = 3LL * c[2] + 2LL * c[1] + c[0];
    ll D = Cw - Aw - Bw;
    if (((D % 4) + 4) % 4 != 0) return res;
    ll k = D / 4;
    ll l4 = 0, m4 = 0, n4 = 0;
    if (k >= 0) l4 = k; else n4 = -k;
    ll lam[4] = {l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4};
    ll mu[4] = {m4 + b[2] + b[1] + b[0], m4 + b[2] + b[1], m4 + b[2], m4};
    ll nu[4] = {n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4};
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return res;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return res;
    res.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (res.L1 == 0) return res;               // Q empty => P == 0, excluded
    if (cmax_filter >= 0 && res.L1 > cmax_filter) { res.valid = false; res.h1 = 1; return res; }
    res.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    res.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    res.six_a1 = -11 + 18 * res.L1 - 9 * res.L2 + 2 * res.L3;
    res.V = res.L3 - 3 * res.L2 + 3 * res.L1 - 1;
    res.h1 = res.L1 - 4;
    res.h2 = res.L2 - 4 * res.L1 + 6;
    res.h3 = res.L3 - 4 * res.L2 + 6 * res.L1 - 4;
    res.valid = true;
    return res;
}

static void print_one(const int *g, const Res &r) {
    printf("a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d) | L=(%lld,%lld,%lld) V=%lld c=%lld "
           "h*=(1,%lld,%lld,%lld) 6a1=%lld %s\n",
           g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8],
           r.L1, r.L2, r.L3, r.V, r.L1, r.h1, r.h2, r.h3, r.six_a1,
           r.six_a1 < 0 ? "*** NEGATIVE ***" : "");
}

// ---------------- record aggregation ----------------
struct Rec {
    ll valid = 0, neg = 0;
    ll min6a1 = (1LL << 60); int argmin[9] = {0}; ll min6a1_V = 0, min6a1_c = 0;
    ll maxV = -1; int argmaxV[9] = {0}; ll maxV_c = 0, maxV_6a1 = 0;
    // max V/c by exact cross multiplication
    ll vcn = -1, vcd = 1; int argvc[9] = {0}; ll vc_6a1 = 0, vc_h3 = 0;
    // max V/(c+h3): a1<0 iff this exceeds 3
    ll wn = -1, wd = 1; int argw[9] = {0}; ll w_V = 0, w_c = 0, w_h3 = 0, w_6a1 = 0;
    ll maxV_c4 = -1; int argV_c4[9] = {0};   // max V among c == 4  (h*_1 = 0)
#ifndef CBMAX
#define CBMAX 41
#endif
    static const int CB = CBMAX;
    ll maxVc[CB]; int argVc[CB][9]; ll a1Vc[CB];
    ll negs_listed = 0;
    Rec() { for (int i = 0; i < CB; i++) { maxVc[i] = -1; a1Vc[i] = 0; for (int j = 0; j < 9; j++) argVc[i][j] = 0; } }
    void feed(const int *g, const Res &r) {
        if (!r.valid) return;
        valid++;
        if (r.six_a1 < 0) {
            neg++;
            if (negs_listed < 50) { negs_listed++; printf("NEGATIVE "); print_one(g, r); }
        }
        if (r.V > 0 && r.six_a1 < min6a1) { min6a1 = r.six_a1; min6a1_V = r.V; min6a1_c = r.L1; memcpy(argmin, g, 9 * sizeof(int)); }
        if (r.V > maxV) { maxV = r.V; maxV_c = r.L1; maxV_6a1 = r.six_a1; memcpy(argmaxV, g, 9 * sizeof(int)); }
        if (r.L1 > 0 && r.V * vcd > vcn * r.L1) { vcn = r.V; vcd = r.L1; vc_6a1 = r.six_a1; vc_h3 = r.h3; memcpy(argvc, g, 9 * sizeof(int)); }
        ll den = r.L1 + r.h3;
        if (den > 0 && r.V * wd > wn * den) { wn = r.V; wd = den; w_V = r.V; w_c = r.L1; w_h3 = r.h3; w_6a1 = r.six_a1; memcpy(argw, g, 9 * sizeof(int)); }
        if (r.L1 == 4 && r.V > maxV_c4) { maxV_c4 = r.V; memcpy(argV_c4, g, 9 * sizeof(int)); }
        if (r.L1 >= 0 && r.L1 < CB && r.V > maxVc[r.L1]) { maxVc[r.L1] = r.V; a1Vc[r.L1] = r.six_a1; memcpy(argVc[r.L1], g, 9 * sizeof(int)); }
    }
    void merge(const Rec &o) {
        valid += o.valid; neg += o.neg;
        if (o.min6a1 < min6a1) { min6a1 = o.min6a1; min6a1_V = o.min6a1_V; min6a1_c = o.min6a1_c; memcpy(argmin, o.argmin, sizeof(argmin)); }
        if (o.maxV > maxV) { maxV = o.maxV; maxV_c = o.maxV_c; maxV_6a1 = o.maxV_6a1; memcpy(argmaxV, o.argmaxV, sizeof(argmaxV)); }
        if (o.vcn >= 0 && o.vcn * vcd > vcn * o.vcd) { vcn = o.vcn; vcd = o.vcd; vc_6a1 = o.vc_6a1; vc_h3 = o.vc_h3; memcpy(argvc, o.argvc, sizeof(argvc)); }
        if (o.wn >= 0 && o.wn * wd > wn * o.wd) { wn = o.wn; wd = o.wd; w_V = o.w_V; w_c = o.w_c; w_h3 = o.w_h3; w_6a1 = o.w_6a1; memcpy(argw, o.argw, sizeof(argw)); }
        if (o.maxV_c4 > maxV_c4) { maxV_c4 = o.maxV_c4; memcpy(argV_c4, o.argV_c4, sizeof(argV_c4)); }
        for (int i = 0; i < CB; i++) if (o.maxVc[i] > maxVc[i]) { maxVc[i] = o.maxVc[i]; a1Vc[i] = o.a1Vc[i]; memcpy(argVc[i], o.argVc[i], sizeof(argVc[i])); }
    }
    void report(const char *tag) const {
        printf("=== BAND11 REPORT [%s] ===\n", tag);
        printf("valid dim<=3 polytopes (nonempty Q, realisable 4|D) = %lld\n", valid);
        printf("NEGATIVE-a1 triples = %lld\n", neg);
        printf("min 6a1 = %lld  (V=%lld c=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               min6a1, min6a1_V, min6a1_c, argmin[0], argmin[1], argmin[2], argmin[3], argmin[4], argmin[5], argmin[6], argmin[7], argmin[8]);
        printf("max V = %lld (c=%lld 6a1=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               maxV, maxV_c, maxV_6a1, argmaxV[0], argmaxV[1], argmaxV[2], argmaxV[3], argmaxV[4], argmaxV[5], argmaxV[6], argmaxV[7], argmaxV[8]);
        printf("MAX V/c = %lld/%lld (6a1=%lld h3=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               vcn, vcd, vc_6a1, vc_h3, argvc[0], argvc[1], argvc[2], argvc[3], argvc[4], argvc[5], argvc[6], argvc[7], argvc[8]);
        printf("MAX V/(c+h3) = %lld/%lld (V=%lld c=%lld h3=%lld 6a1=%lld)  [a1<0 iff > 3] at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               wn, wd, w_V, w_c, w_h3, w_6a1, argw[0], argw[1], argw[2], argw[3], argw[4], argw[5], argw[6], argw[7], argw[8]);
        printf("MAX V at c=4 (h*_1=0) = %lld at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)   [Reeve statistic: need >= 13]\n",
               maxV_c4, argV_c4[0], argV_c4[1], argV_c4[2], argV_c4[3], argV_c4[4], argV_c4[5], argV_c4[6], argV_c4[7], argV_c4[8]);
        printf("max V at each fixed c = L(1):\n");
        for (int k = 1; k < CB; k++) if (maxVc[k] >= 0)
            printf("   c=%2d Vmax=%6lld 6a1=%lld  a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
                   k, maxVc[k], a1Vc[k], argVc[k][0], argVc[k][1], argVc[k][2], argVc[k][3], argVc[k][4], argVc[k][5], argVc[k][6], argVc[k][7], argVc[k][8]);
    }
};

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: band11_vcscan G | --one g1..g9 | --smallc G CMAX | --climb K RST SEED | --rand K N SEED\n"); return 2; }

    if (!strcmp(argv[1], "--one")) {
        int g[9]; for (int i = 0; i < 9; i++) g[i] = atoi(argv[2 + i]);
        Res r = eval_gaps(g, g + 3, g + 6);
        if (!r.valid) { printf("INVALID (not realisable, Q empty, or degenerate)\n"); return 0; }
        print_one(g, r);
        return 0;
    }

    // --ray T g1..g9 : evaluate t*g for t = 1..T (scaling behaviour of V/c)
    if (!strcmp(argv[1], "--ray")) {
        int T = atoi(argv[2]);
        int g0[9]; for (int i = 0; i < 9; i++) g0[i] = atoi(argv[3 + i]);
        for (int t = 1; t <= T; t++) {
            int g[9]; for (int i = 0; i < 9; i++) g[i] = t * g0[i];
            Res r = eval_gaps(g, g + 3, g + 6);
            if (!r.valid) { printf("t=%d INVALID\n", t); continue; }
            printf("t=%2d V=%lld c=%lld h3=%lld 6a1=%lld V/c=%.6f V/(c+h3)=%.6f\n",
                   t, r.V, r.L1, r.h3, r.six_a1,
                   r.L1 ? (double)r.V / (double)r.L1 : 0.0,
                   (r.L1 + r.h3) ? (double)r.V / (double)(r.L1 + r.h3) : 0.0);
        }
        return 0;
    }

    if (!strcmp(argv[1], "--rand")) {
        ll K = atoll(argv[2]), N = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 11ULL;
        Rec G;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 7ULL;
            Rec L;
#pragma omp for schedule(dynamic, 4096)
            for (ll it = 0; it < N; it++) {
                int g[9];
                for (int i = 0; i < 9; i++) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; g[i] = (int)(st % (unsigned long long)(K + 1)); }
                Res r = eval_gaps(g, g + 3, g + 6);
                L.feed(g, r);
            }
#pragma omp critical
            G.merge(L);
        }
        printf("RAND K=%lld N=%lld\n", K, N);
        G.report("rand");
        return 0;
    }

    // targeted V/c maximisation: hill-climb on the exact ratio V/c with restarts
    if (!strcmp(argv[1], "--climb")) {
        ll K = atoll(argv[2]); ll RST = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 1111ULL;
        // OBJ selector: 0 = V/c, 1 = V/(c+h3)  (the sharp negativity ratio)
        int OBJ = (argc > 5) ? atoi(argv[5]) : 0;
        Rec G;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 999ULL;
            auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
            Rec L;
#pragma omp for schedule(dynamic, 1)
            for (ll rs = 0; rs < RST; rs++) {
                int g[9];
                for (int i = 0; i < 9; i++) g[i] = (int)rnd(K + 1);
                ll bn = -1, bd = 1;             // current best ratio num/den
                for (int iter = 0; iter < 2000; iter++) {
                    int bi = -1, bdir = 0, bstep = 0; ll cn = bn, cd = bd;
                    for (int i = 0; i < 9; i++) for (int dir = -1; dir <= 1; dir += 2) for (int step = 1; step <= 3; step++) {
                        int old = g[i]; int nv = old + dir * step;
                        if (nv < 0 || nv > (int)K) continue;
                        g[i] = nv;
                        Res r = eval_gaps(g, g + 3, g + 6);
                        L.feed(g, r);
                        g[i] = old;
                        if (!r.valid || r.V <= 0 || r.L1 <= 0) continue;
                        ll num = r.V, den = (OBJ == 0) ? r.L1 : (r.L1 + r.h3);
                        if (den <= 0) continue;
                        if (num * cd > cn * den) { cn = num; cd = den; bi = i; bdir = dir; bstep = step; }
                    }
                    if (bi < 0) {
                        int i = (int)rnd(9); int dir = rnd(2) ? 1 : -1; int nv = g[i] + dir * (1 + (int)rnd(4));
                        if (nv >= 0 && nv <= (int)K) g[i] = nv; else break;
                        bn = -1; bd = 1;
                        continue;
                    }
                    g[bi] += bdir * bstep; bn = cn; bd = cd;
                }
            }
#pragma omp critical
            G.merge(L);
        }
        printf("CLIMB K=%lld restarts=%lld obj=%s\n", K, RST, (argc > 5 && atoi(argv[5]) == 1) ? "V/(c+h3)" : "V/c");
        G.report("climb");
        return 0;
    }

    // --simplex S : EXHAUSTIVE over every gap vector g >= 0 with g1+...+g9 <= S.
    // This L1-ball region is NOT contained in any cube scanned before: it reaches
    // single gaps as large as S (very elongated / thin shapes) while staying finite.
    if (!strcmp(argv[1], "--simplex")) {
        int S = atoi(argv[2]);
        fprintf(stderr, "exhaustive simplex scan sum(g) <= %d\n", S);
        Rec G;
        std::vector<std::pair<int,int> > seeds;
        for (int g0 = 0; g0 <= S; g0++) for (int g1 = 0; g1 + g0 <= S; g1++) seeds.push_back(std::make_pair(g0, g1));
        ll counted = 0;
#pragma omp parallel
        {
            Rec L; ll lcount = 0;
#pragma omp for schedule(dynamic, 1)
            for (ll si = 0; si < (ll)seeds.size(); si++) {
                int g[9];
                g[0] = seeds[si].first; g[1] = seeds[si].second;
                int budget0 = S - g[0] - g[1];
                // iterative nested loops over g[2..8]
                for (int a2 = 0; a2 <= budget0; a2++) {
                 int b2 = budget0 - a2; g[2] = a2;
                 for (int a3 = 0; a3 <= b2; a3++) {
                  int b3 = b2 - a3; g[3] = a3;
                  for (int a4 = 0; a4 <= b3; a4++) {
                   int b4 = b3 - a4; g[4] = a4;
                   for (int a5 = 0; a5 <= b4; a5++) {
                    int b5 = b4 - a5; g[5] = a5;
                    for (int a6 = 0; a6 <= b5; a6++) {
                     int b6 = b5 - a6; g[6] = a6;
                     for (int a7 = 0; a7 <= b6; a7++) {
                      int b7 = b6 - a7; g[7] = a7;
                      for (int a8 = 0; a8 <= b7; a8++) {
                       g[8] = a8;
                       lcount++;
                       Res r = eval_gaps(g, g + 3, g + 6);
                       L.feed(g, r);
                      }}}}}}}
            }
#pragma omp critical
            { G.merge(L); counted += lcount; }
        }
        printf("SIMPLEX S=%d vectors=%lld\n", S, counted);
        G.report("simplex");
        return 0;
    }

    if (!strcmp(argv[1], "--smallc")) {
        int Gm = atoi(argv[2]); ll CMAX = atoll(argv[3]);
        ll W = Gm + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
        fprintf(stderr, "smallc scan [0,%d]^9 = %lld vectors, full eval only when L1 <= %lld\n", Gm, TOT, CMAX);
        Rec G; ll skipped = 0;
#pragma omp parallel
        {
            Rec L; ll lskip = 0;
#pragma omp for schedule(dynamic, 4096)
            for (ll code = 0; code < TOT; code++) {
                int g[9]; ll t = code;
                for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
                Res r = eval_gaps(g, g + 3, g + 6, CMAX);
                if (!r.valid && r.h1 == 1) { lskip++; continue; }
                L.feed(g, r);
            }
#pragma omp critical
            { G.merge(L); skipped += lskip; }
        }
        printf("SMALLC G=%d CMAX=%lld vectors=%lld skipped(L1>CMAX)=%lld\n", Gm, CMAX, TOT, skipped);
        G.report("smallc");
        return 0;
    }

    int Gm = atoi(argv[1]);
    ll W = Gm + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
    fprintf(stderr, "exhaustive gap scan [0,%d]^9 : %lld vectors\n", Gm, TOT);
    Rec G;
#pragma omp parallel
    {
        Rec L;
#pragma omp for schedule(dynamic, 2048)
        for (ll code = 0; code < TOT; code++) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
            Res r = eval_gaps(g, g + 3, g + 6);
            L.feed(g, r);
        }
#pragma omp critical
        G.merge(L);
    }
    printf("EXHAUSTIVE G=%d vectors=%lld\n", Gm, TOT);
    G.report("exhaustive");
    return 0;
}
