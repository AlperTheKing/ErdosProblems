// gapscan.cpp -- exhaustive exact scan of the r=4 hive-polytope MODULI SPACE.
//
// MODULI REDUCTION (verified in gap_moduli.py):
//   Q(lam,mu,nu) for r = 4 depends on (lam,mu,nu) only through the 9 gaps
//     a = (l1-l2, l2-l3, l3-l4), b = (m1-m2, m2-m3, m3-m4), c = (n1-n2, n2-n3, n3-n4)
//   up to a lattice TRANSLATION of R^3 (the two "add a full column" symmetries
//   (lam,nu)->(lam+1^4,nu+1^4) and (mu,nu)->(mu+1^4,nu+1^4) act as translations).
//   The gap vector is realised by partitions iff D = Cw-Aw-Bw == 0 (mod 4),
//   Aw = 3a3+2a2+a1 etc.
//
// EHRHART CRITERION.  P(n) = c(n nu; n lam, n mu) = L(n) = #(nQ cap Z^3) is a
// polynomial of degree <= 3 (Knutson-Tao + Derksen-Weyman/KTT).  Hence with
// L(0) = 1:
//     6*a1 = -11 + 18 L(1) - 9 L(2) + 2 L(3)          (a1 = P'(0))
//     V    = 6*a3 = L(3) - 3 L(2) + 3 L(1) - 1        (normalized volume)
//     6*a2 = ... (not needed)
// so the King-Tollu-Toumazet conjecture fails in the r=4 cell iff some gap
// vector gives 18 L(1) - 9 L(2) + 2 L(3) < 11 (a1 < 0; a3 > 0 and a2 > 0 are
// automatic, a0 = 1).
//
// COUNTING.  In the unimodular coordinates (x,u,v) = (h11, h12-h11, h21-h11)
// every one of the 18 rhombus rows has all coefficients in {0,+-1}; the x
// coefficient is p+q+r.  So for FIXED INTEGER (u,v) the fibre is an integer
// interval, and L(n) = sum over integer (u,v) of (fibre length + 1).  Pure
// integer arithmetic throughout; no floating point.
//
// Build: clang++ -O3 -march=native -fopenmp -o gapscan gapscan.exe
// Usage: gapscan GMAX [--nmax N] [--one a1 a2 a3 b1 b2 b3 c1 c2 c3]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <string>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;

struct Row { int s, q, r; ll rhs; };   // s*x + q*u + r*v <= rhs

// Build the 18 rhombus rows for r = 4 from the boundary partial sums.
// Boundary convention identical to hive4.py / engine A:
//   B(0,y) = lam_1+...+lam_y ; B(x,4-x) = |lam|+mu_1+...+mu_x ; B(x,0) = nu_1+...+nu_x
static int build_rows(const ll lam[4], const ll mu[4], const ll nu[4], Row out[24]) {
    ll B[5][5];
    for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) B[i][j] = 0;
    ll sl = lam[0] + lam[1] + lam[2] + lam[3];
    ll acc = 0; for (int y = 0; y <= 4; y++) { B[0][y] = acc; if (y < 4) acc += lam[y]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][4 - x] = sl + acc; if (x < 4) acc += mu[x]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][0] = acc; if (x < 4) acc += nu[x]; }
    B[0][0] = 0;
    // interior indices
    auto isInt = [](int x, int y) { return (x == 1 && y == 1) || (x == 1 && y == 2) || (x == 2 && y == 1); };
    auto idx = [](int x, int y) { return (x == 1 && y == 1) ? 0 : (x == 1 && y == 2) ? 1 : 2; };
    int nr = 0;
    bool infeasible = false;
    auto add = [&](int px[2], int py[2], int mx[2], int my[2]) {
        // impose sum(plus) >= sum(minus)  <=>  sum(minus) - sum(plus) <= 0
        ll co[3] = {0, 0, 0}; ll cst = 0;
        for (int t = 0; t < 2; t++) {
            if (isInt(px[t], py[t])) co[idx(px[t], py[t])] -= 1; else cst -= B[px[t]][py[t]];
            if (isInt(mx[t], my[t])) co[idx(mx[t], my[t])] += 1; else cst += B[mx[t]][my[t]];
        }
        if (co[0] == 0 && co[1] == 0 && co[2] == 0) { if (cst > 0) infeasible = true; return; }
        // (x,y,z) row (co, rhs=-cst) -> (x,u,v): s = co0+co1+co2, q = co1, r = co2
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

// L(n) = #( nQ cap Z^3 ), exact, via integer fibres over (u,v).
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

struct Res { ll L1, L2, L3, six_a1, V; bool valid; };

static Res eval_gaps(const int a[3], const int b[3], const int c[3]) {
    Res res; res.valid = false; res.L1 = res.L2 = res.L3 = 0; res.six_a1 = 0; res.V = 0;
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
    if (nr < 0) { res.valid = true; res.L1 = res.L2 = res.L3 = 0; res.six_a1 = -11; res.V = -1; res.valid = false; return res; }
    // u = h12-h11 in [lam3, lam2]; v = h21-h11 in [nu3, nu2]   (1-indexed parts)
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return res;
    res.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    // Q empty  =>  P == 0 identically (Knutson-Tao saturation: L(1)=0 => L(n)=0
    // for all n).  P == 0 has no negative coefficient; it is NOT the L(0)=1 case,
    // so it must be excluded from the a1 formula.
    if (res.L1 == 0) { res.valid = false; return res; }
    res.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    res.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    res.six_a1 = -11 + 18 * res.L1 - 9 * res.L2 + 2 * res.L3;
    res.V = res.L3 - 3 * res.L2 + 3 * res.L1 - 1;
    res.valid = true;
    return res;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: gapscan GMAX | gapscan --one a1 a2 a3 b1 b2 b3 c1 c2 c3\n"); return 2; }
    if (!strcmp(argv[1], "--one")) {
        int a[3], b[3], c[3];
        for (int i = 0; i < 3; i++) { a[i] = atoi(argv[2 + i]); b[i] = atoi(argv[5 + i]); c[i] = atoi(argv[8 + i]); }
        Res r = eval_gaps(a, b, c);
        printf("valid=%d L1=%lld L2=%lld L3=%lld 6a1=%lld V=%lld\n", (int)r.valid, r.L1, r.L2, r.L3, r.six_a1, r.V);
        return 0;
    }
    // --rand KMAX NSAMPLES SEED : uniform random gap vectors in [0,KMAX]^9.
    // A chamber of the (fixed) wall arrangement in gap space is a cone, so every
    // FULL-DIMENSIONAL chamber is hit with probability proportional to its solid
    // angle; large KMAX probes chambers too thin to contain a small lattice point.
    if (!strcmp(argv[1], "--rand")) {
        ll K = atoll(argv[2]), N = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 20260721ULL;
        ll r_min = (1LL << 60); int r_arg[9] = {0}; ll r_neg = 0, r_valid = 0; ll r_minV = 0;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL;
            ll l_min = (1LL << 60); int l_arg[9] = {0}; ll l_neg = 0, l_valid = 0; ll l_minV = 0;
#pragma omp for schedule(dynamic, 4096)
            for (ll it = 0; it < N; it++) {
                int g[9];
                for (int i = 0; i < 9; i++) {
                    st ^= st << 13; st ^= st >> 7; st ^= st << 17;
                    g[i] = (int)(st % (unsigned long long)(K + 1));
                }
                Res r = eval_gaps(g, g + 3, g + 6);
                if (!r.valid || r.V <= 0) continue;
                l_valid++;
                if (r.six_a1 < l_min) { l_min = r.six_a1; l_minV = r.V; memcpy(l_arg, g, sizeof(g)); }
                if (r.six_a1 < 0) l_neg++;
            }
#pragma omp critical
            {
                r_valid += l_valid; r_neg += l_neg;
                if (l_min < r_min) { r_min = l_min; r_minV = l_minV; memcpy(r_arg, l_arg, sizeof(l_arg)); }
            }
        }
        printf("RAND KMAX=%lld N=%lld : dim3-valid=%lld  NEGATIVE=%lld  min6a1=%lld (V=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               K, N, r_valid, r_neg, r_min, r_minV, r_arg[0], r_arg[1], r_arg[2], r_arg[3], r_arg[4], r_arg[5], r_arg[6], r_arg[7], r_arg[8]);
        return 0;
    }

    // --climb KMAX RESTARTS SEED : scale-invariant descent on  6a1 / (1+sum g).
    // a1 is homogeneous of degree 1 on each chamber of gap space, so the ratio
    // 6a1/(1+sum g) is (asymptotically) chamber-constant: descending it selects
    // chambers, and it is < 0 exactly when a1 < 0.  This probes THIN chambers,
    // which uniform sampling can miss.
    if (!strcmp(argv[1], "--climb")) {
        ll K = atoll(argv[2]); ll RST = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 31337ULL;
        double best = 1e18; int bestg[9] = {0}; ll bestsix = 0, bestV = 0, bestL1 = 0; ll neg = 0;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 12345ULL;
            auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
            double l_best = 1e18; int l_bestg[9] = {0}; ll l_six = 0, l_V = 0, l_L1 = 0, l_neg = 0;
#pragma omp for schedule(dynamic, 1)
            for (ll rs = 0; rs < RST; rs++) {
                int g[9];
                for (int i = 0; i < 9; i++) g[i] = (int)rnd(K + 1);
                double cur = 1e18;
                for (int iter = 0; iter < 4000; iter++) {
                    int bi = -1, bd = 0; double bs = cur;
                    for (int i = 0; i < 9; i++) for (int d = -1; d <= 1; d += 2) {
                        int old = g[i]; int nv = old + d;
                        if (nv < 0 || nv > (int)K) continue;
                        g[i] = nv;
                        Res r = eval_gaps(g, g + 3, g + 6);
                        g[i] = old;
                        if (!r.valid || r.V <= 0) continue;
                        ll s = 0; for (int t = 0; t < 9; t++) s += g[t]; s += d;
                        double sc = (double)r.six_a1 / (double)(1 + s);
                        if (sc < bs) { bs = sc; bi = i; bd = d; }
                        if (r.six_a1 < 0) l_neg++;
                    }
                    if (bi < 0) {
                        // random kick
                        int i = (int)rnd(9); int d = (int)rnd(2) ? 1 : -1;
                        int nv = g[i] + d * (1 + (int)rnd(3));
                        if (nv >= 0 && nv <= (int)K) g[i] = nv; else break;
                        Res r = eval_gaps(g, g + 3, g + 6);
                        if (r.valid && r.V > 0) { ll s = 0; for (int t = 0; t < 9; t++) s += g[t]; cur = (double)r.six_a1 / (double)(1 + s); }
                        continue;
                    }
                    g[bi] += bd; cur = bs;
                    Res r = eval_gaps(g, g + 3, g + 6);
                    if (r.valid && r.V > 0 && cur < l_best) {
                        l_best = cur; memcpy(l_bestg, g, sizeof(g)); l_six = r.six_a1; l_V = r.V; l_L1 = r.L1;
                    }
                }
            }
#pragma omp critical
            {
                neg += l_neg;
                if (l_best < best) { best = l_best; memcpy(bestg, l_bestg, sizeof(l_bestg)); bestsix = l_six; bestV = l_V; bestL1 = l_L1; }
            }
        }
        printf("CLIMB KMAX=%lld restarts=%lld : NEGATIVE hits=%lld  best 6a1/(1+sum g)=%.6f  (6a1=%lld V=%lld c=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               K, RST, neg, best, bestsix, bestV, bestL1,
               bestg[0], bestg[1], bestg[2], bestg[3], bestg[4], bestg[5], bestg[6], bestg[7], bestg[8]);
        return 0;
    }

    // --find T G LIMIT : list gap vectors in [0,G]^9 with 6a1 == T  (near-miss stratum)
    if (!strcmp(argv[1], "--find")) {
        ll T = atoll(argv[2]); int G = atoi(argv[3]); ll LIM = (argc > 4) ? atoll(argv[4]) : 20;
        ll W = G + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
        ll found = 0;
        for (ll code = 0; code < TOT && found < LIM; code++) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
            Res r = eval_gaps(g, g + 3, g + 6);
            if (!r.valid || r.V <= 0 || r.six_a1 != T) continue;
            found++;
            printf("6a1=%lld V=%lld c=%lld L=(%lld,%lld,%lld) a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
                   r.six_a1, r.V, r.L1, r.L1, r.L2, r.L3, g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8]);
        }
        return 0;
    }

    int G = atoi(argv[1]);
    ll W = G + 1;
    ll TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
    fprintf(stderr, "scanning gaps in [0,%d]^9 : %lld vectors\n", G, TOT);

    ll g_min = (1LL << 60); int g_argmin[9] = {0}; ll g_neg = 0; ll g_valid = 0;
    ll g_maxV = 0; int g_argmaxV[9] = {0};
    ll g_maxVoverL1_num = 0, g_maxVoverL1_den = 1; int g_argVL[9] = {0};
    const int HB = 256;
    std::vector<ll> g_hist(HB, 0);
    ll g_minBig = (1LL << 60); int g_argminBig[9] = {0}; ll g_minBigV = 0;
    const int CB = 17;                      // max V achievable at each fixed L1 = c
    std::vector<ll> g_maxVc(CB, -1);
    std::vector<std::vector<int> > g_argVc(CB, std::vector<int>(9, 0));

#pragma omp parallel
    {
        ll l_min = (1LL << 60); int l_argmin[9] = {0}; ll l_neg = 0; ll l_valid = 0;
        ll l_maxV = 0; int l_argmaxV[9] = {0};
        ll l_vn = 0, l_vd = 1; int l_argvl[9] = {0};
        std::vector<ll> l_hist(HB, 0);
        ll l_minBig = (1LL << 60); int l_argminBig[9] = {0}; ll l_minBigV = 0;
        std::vector<ll> l_maxVc(CB, -1);
        std::vector<std::vector<int> > l_argVc(CB, std::vector<int>(9, 0));
#pragma omp for schedule(dynamic, 1024)
        for (ll code = 0; code < TOT; code++) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
            Res r = eval_gaps(g, g + 3, g + 6);
            if (!r.valid) continue;
            l_valid++;
            // deg P < 3 (V == 0) is Ehrhart-positive by classical d<=2 theory and
            // gives the trivial 6a1 = 0 for P == 1; the live stratum is V > 0.
            if (r.V > 0 && r.six_a1 < l_min) { l_min = r.six_a1; memcpy(l_argmin, g, sizeof(g)); }
            if (r.six_a1 < 0) l_neg++;
            if (r.V > l_maxV) { l_maxV = r.V; memcpy(l_argmaxV, g, sizeof(g)); }
            if (r.L1 > 0 && r.V * l_vd > l_vn * r.L1) { l_vn = r.V; l_vd = r.L1; memcpy(l_argvl, g, sizeof(g)); }
            if (r.V > 0 && r.six_a1 >= 0 && r.six_a1 < HB) l_hist[r.six_a1]++;
            if (r.V >= 200 && r.six_a1 < l_minBig) { l_minBig = r.six_a1; l_minBigV = r.V; memcpy(l_argminBig, g, sizeof(g)); }
            if (r.L1 < CB && r.V > l_maxVc[r.L1]) { l_maxVc[r.L1] = r.V; for (int i = 0; i < 9; i++) l_argVc[r.L1][i] = g[i]; }
        }
#pragma omp critical
        {
            g_valid += l_valid; g_neg += l_neg;
            if (l_min < g_min) { g_min = l_min; memcpy(g_argmin, l_argmin, sizeof(l_argmin)); }
            if (l_maxV > g_maxV) { g_maxV = l_maxV; memcpy(g_argmaxV, l_argmaxV, sizeof(l_argmaxV)); }
            if (l_vn * g_maxVoverL1_den > g_maxVoverL1_num * l_vd) {
                g_maxVoverL1_num = l_vn; g_maxVoverL1_den = l_vd; memcpy(g_argVL, l_argvl, sizeof(l_argvl));
            }
            for (int i = 0; i < HB; i++) g_hist[i] += l_hist[i];
            if (l_minBig < g_minBig) { g_minBig = l_minBig; g_minBigV = l_minBigV; memcpy(g_argminBig, l_argminBig, sizeof(l_argminBig)); }
            for (int k = 0; k < CB; k++) if (l_maxVc[k] > g_maxVc[k]) { g_maxVc[k] = l_maxVc[k]; g_argVc[k] = l_argVc[k]; }
        }
    }
    printf("GMAX=%d  vectors=%lld  realisable(4|D)=%lld\n", G, TOT, g_valid);
    printf("NEGATIVE a1 count = %lld\n", g_neg);
    printf("min 6a1 = %lld  at gaps a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", g_min,
           g_argmin[0], g_argmin[1], g_argmin[2], g_argmin[3], g_argmin[4], g_argmin[5],
           g_argmin[6], g_argmin[7], g_argmin[8]);
    printf("max V   = %lld  at gaps a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", g_maxV,
           g_argmaxV[0], g_argmaxV[1], g_argmaxV[2], g_argmaxV[3], g_argmaxV[4], g_argmaxV[5],
           g_argmaxV[6], g_argmaxV[7], g_argmaxV[8]);
    printf("max V/L1 = %lld/%lld at gaps a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_maxVoverL1_num, g_maxVoverL1_den,
           g_argVL[0], g_argVL[1], g_argVL[2], g_argVL[3], g_argVL[4], g_argVL[5],
           g_argVL[6], g_argVL[7], g_argVL[8]);
    printf("min 6a1 among V>=200 : %lld (V=%lld) at gaps a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_minBig, g_minBigV, g_argminBig[0], g_argminBig[1], g_argminBig[2], g_argminBig[3],
           g_argminBig[4], g_argminBig[5], g_argminBig[6], g_argminBig[7], g_argminBig[8]);
    printf("max normalized volume V at each fixed lattice-point count c = L(1)  [dim 3, V>0]:\n");
    for (int k = 1; k < CB; k++) if (g_maxVc[k] >= 0)
        printf("   c=%2d : Vmax=%4lld  6a1=%lld  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", k, g_maxVc[k],
               3LL * k /*+3i unknown here*/ - g_maxVc[k],
               g_argVc[k][0], g_argVc[k][1], g_argVc[k][2], g_argVc[k][3], g_argVc[k][4],
               g_argVc[k][5], g_argVc[k][6], g_argVc[k][7], g_argVc[k][8]);
    printf("6a1 histogram (V>0), first 40 nonzero bins:\n");
    int shown = 0;
    for (int i = 0; i < HB && shown < 40; i++) if (g_hist[i]) { printf("   6a1=%3d : %lld\n", i, g_hist[i]); shown++; }
    return 0;
}
