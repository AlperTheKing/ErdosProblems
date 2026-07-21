// bandscan9.cpp -- r=4 KTT census for WEIGHT BAND  W = |nu| in [91,140]  (hunter 9/12)
#include <array>
//
// MODULI FACT (re-verified independently in this run against hive4.py):
//   Q(lam,mu,nu) for r=4 depends on (lam,mu,nu) only through the 9 gaps
//     a = (l1-l2,l2-l3,l3-l4), b = (m1-m2,m2-m3,m3-m4), c = (n1-n2,n2-n3,n3-n4)
//   up to lattice translation of R^3.  Aw = a0+2a1+3a2 etc, D = Cw-Aw-Bw,
//   realisable iff 4 | D, and then |lam| = 4*l4+Aw, |mu| = 4*m4+Bw, |nu| = 4*n4+Cw
//   with l4+m4-n4 = D/4, l4,m4,n4 >= 0.
//
// BAND <-> GAP REGION (exact, proved in the report):
//   a gap vector with 4|D is realised by SOME triple with |nu| in [91,140]
//   iff  Aw+Bw <= 140  and  Cw <= 140.
//   (=>) Aw+Bw <= |lam|+|mu| = W <= 140, Cw <= |nu| = W <= 140.
//   (<=) pick n4 in [max(0,-D/4,ceil((91-Cw)/4)), floor((140-Cw)/4)] (nonempty
//        because the band is 50 wide >= 4 and Aw+Bw <= 140), then l4+m4 = D/4+n4 >= 0.
//   So the whole band is EXACTLY the gap region {Aw+Bw <= 140, Cw <= 140, 4|D},
//   of size 7 820 553 811 824.  Truncating at Aw+Bw <= S, Cw <= S gives an
//   exhaustive sub-census.
//
// EHRHART (deg P <= 3, P(0)=1 for Q nonempty; Derksen-Weyman/KTT polynomiality):
//   6*a1 = -11 + 18 L1 - 9 L2 + 2 L3 ,  V = 6*a3 = L3 - 3 L2 + 3 L1 - 1 ,
//   h*_1 = L1 - 4 when dim = 3 (V > 0).  KTT fails in this cell iff 6*a1 < 0.
// All integer arithmetic; no floating point in any decision.
//
// Build: clang++ -O3 -march=native -fopenmp -o bandscan9.exe bandscan9.cpp
// Modes:
//   --wcone S          exhaustive over {Aw+Bw<=S, Cw<=S, 4|D}
//   --one a0 a1 a2 b0 b1 b2 c0 c1 c2
//   --climb SECONDS CCAP SEED RESTARTS   volume-steered single-box climb in the band
//   --rand N SEED MAXW                   uniform random band triples

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <ctime>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;

struct Row { int s, q, r; ll rhs; };

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
    int nr = 0; bool infeasible = false;
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

struct Res { ll L1, L2, L3, six_a1, V; bool valid; };

static Res eval_triple(const ll lam[4], const ll mu[4], const ll nu[4]) {
    Res res; res.valid = false; res.L1 = res.L2 = res.L3 = 0; res.six_a1 = 0; res.V = 0;
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return res;                       // boundary rhombus violated => Q empty
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return res;
    res.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (res.L1 == 0) return res;                  // Q empty => P == 0, no coefficients
    res.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    res.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    res.six_a1 = -11 + 18 * res.L1 - 9 * res.L2 + 2 * res.L3;
    res.V = res.L3 - 3 * res.L2 + 3 * res.L1 - 1;
    res.valid = true;
    return res;
}

// canonical band representative of a gap vector: smallest n4 putting |nu| >= 91
static bool band_triple_from_gaps(const int a[3], const int b[3], const int c[3],
                                  ll lam[4], ll mu[4], ll nu[4], ll *Wout) {
    ll Aw = a[0] + 2LL * a[1] + 3LL * a[2];
    ll Bw = b[0] + 2LL * b[1] + 3LL * b[2];
    ll Cw = c[0] + 2LL * c[1] + 3LL * c[2];
    ll D = Cw - Aw - Bw;
    if (((D % 4) + 4) % 4 != 0) return false;
    ll k = D / 4;
    ll n4lo = 0;
    if (-k > n4lo) n4lo = -k;
    ll need = 91 - Cw; ll ce = (need <= 0) ? 0 : (need + 3) / 4;
    if (ce > n4lo) n4lo = ce;
    ll n4hi = (140 - Cw) >= 0 ? (140 - Cw) / 4 : -1;
    if (n4lo > n4hi) return false;
    ll n4 = n4lo, l4 = k + n4, m4 = 0;
    if (l4 < 0) return false;
    lam[3] = l4; lam[2] = l4 + a[2]; lam[1] = l4 + a[2] + a[1]; lam[0] = l4 + a[2] + a[1] + a[0];
    mu[3] = m4;  mu[2] = m4 + b[2];  mu[1] = m4 + b[2] + b[1];  mu[0] = m4 + b[2] + b[1] + b[0];
    nu[3] = n4;  nu[2] = n4 + c[2];  nu[1] = n4 + c[2] + c[1];  nu[0] = n4 + c[2] + c[1] + c[0];
    *Wout = nu[0] + nu[1] + nu[2] + nu[3];
    return true;
}

// how many ACTUAL band triples (lam,mu,nu), |nu| in [91,140], realise this gap class
static ll band_multiplicity(const int a[3], const int b[3], const int c[3]) {
    ll Aw = a[0] + 2LL * a[1] + 3LL * a[2];
    ll Bw = b[0] + 2LL * b[1] + 3LL * b[2];
    ll Cw = c[0] + 2LL * c[1] + 3LL * c[2];
    ll D = Cw - Aw - Bw;
    if (((D % 4) + 4) % 4 != 0) return 0;
    ll k = D / 4;
    ll lo = 0; if (-k > lo) lo = -k;
    ll need = 91 - Cw; ll ce = (need <= 0) ? 0 : (need + 3) / 4;
    if (ce > lo) lo = ce;
    ll hi = (140 - Cw) >= 0 ? (140 - Cw) / 4 : -1;
    ll tot = 0;
    for (ll n4 = lo; n4 <= hi; n4++) tot += (k + n4 + 1);   // choices of (l4,m4) with l4+m4=k+n4
    return tot;
}

struct Acc {
    ll tested = 0, nonempty = 0, dim3 = 0, neg = 0, bandTriples = 0;
    ll min6a1 = (1LL << 60); int argmin[9] = {0}; ll minV = 0, minL1 = 0;
    ll min6a1d3 = (1LL << 60); int argmind3[9] = {0}; ll minVd3 = 0, minL1d3 = 0;
    ll maxV4 = -1, maxV5 = -1, maxV6 = -1;
    ll maxV = -1; int argmaxV[9] = {0}; ll maxV_L1 = 0;
    ll maxV0 = -1; int argmaxV0[9] = {0};      // among L1 == 4  (h*_1 = 0)
    ll maxh2 = -1; int argmaxh2[9] = {0}; ll maxh2_six = 0;
    void take(const int g[9], const Res &r) {
        tested++;
        if (!r.valid) return;
        nonempty++;
        if (r.V > 0) dim3++;
        if (r.six_a1 < 0) neg++;
        if (r.six_a1 < min6a1) { min6a1 = r.six_a1; memcpy(argmin, g, 9 * sizeof(int)); minV = r.V; minL1 = r.L1; }
        if (r.V > 0 && r.six_a1 < min6a1d3) { min6a1d3 = r.six_a1; memcpy(argmind3, g, 9 * sizeof(int)); minVd3 = r.V; minL1d3 = r.L1; }
        if (r.V > maxV) { maxV = r.V; memcpy(argmaxV, g, 9 * sizeof(int)); maxV_L1 = r.L1; }
        if (r.V > 0 && r.L1 == 4 && r.V > maxV0) { maxV0 = r.V; memcpy(argmaxV0, g, 9 * sizeof(int)); }
        if (r.V > 0) {
            if (r.L1 == 4 && r.V > maxV4) maxV4 = r.V;
            if (r.L1 == 5 && r.V > maxV5) maxV5 = r.V;
            if (r.L1 == 6 && r.V > maxV6) maxV6 = r.V;
        }
        if (r.V > 0) {  // h*_2 = V - 1 - h*_1 - h*_3 ; use h*_1 = L1-4, h*_3 from 6a1
            ll h1 = r.L1 - 4;
            ll h2h3 = r.V - 1 - h1;              // h*_2 + h*_3
            ll t = r.six_a1 - 11 - 2 * h1;       // = -h*_2 + 2 h*_3
            // h*_2 = (2*h2h3 - t)/3
            ll h2 = (2 * h2h3 - t) / 3;
            if (h2 > maxh2) { maxh2 = h2; memcpy(argmaxh2, g, 9 * sizeof(int)); maxh2_six = r.six_a1; }
        }
    }
    void merge(const Acc &o) {
        tested += o.tested; nonempty += o.nonempty; dim3 += o.dim3; neg += o.neg; bandTriples += o.bandTriples;
        if (o.maxV4 > maxV4) maxV4 = o.maxV4;
        if (o.maxV5 > maxV5) maxV5 = o.maxV5;
        if (o.maxV6 > maxV6) maxV6 = o.maxV6;
        if (o.min6a1d3 < min6a1d3) { min6a1d3 = o.min6a1d3; memcpy(argmind3, o.argmind3, sizeof(argmind3)); minVd3 = o.minVd3; minL1d3 = o.minL1d3; }
        if (o.min6a1 < min6a1) { min6a1 = o.min6a1; memcpy(argmin, o.argmin, sizeof(argmin)); minV = o.minV; minL1 = o.minL1; }
        if (o.maxV > maxV) { maxV = o.maxV; memcpy(argmaxV, o.argmaxV, sizeof(argmaxV)); maxV_L1 = o.maxV_L1; }
        if (o.maxV0 > maxV0) { maxV0 = o.maxV0; memcpy(argmaxV0, o.argmaxV0, sizeof(argmaxV0)); }
        if (o.maxh2 > maxh2) { maxh2 = o.maxh2; memcpy(argmaxh2, o.argmaxh2, sizeof(argmaxh2)); maxh2_six = o.maxh2_six; }
    }
};

static void print_g(const char *tag, const int g[9]) {
    printf("%s a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)", tag,
           g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8]);
}

static void report(const char *mode, const Acc &A) {
    printf("MODE %s\n", mode);
    printf("tested=%lld nonempty(L1>0)=%lld dim3(V>0)=%lld NEGATIVE=%lld bandTriplesCovered=%lld\n",
           A.tested, A.nonempty, A.dim3, A.neg, A.bandTriples);
    printf("min 6a1 (all)  = %lld (V=%lld L1=%lld) at ", A.min6a1, A.minV, A.minL1);
    print_g("", A.argmin); printf("\n");
    printf("min 6a1 (dim3) = %lld (V=%lld L1=%lld) at ", A.min6a1d3, A.minVd3, A.minL1d3);
    print_g("", A.argmind3); printf("\n");
    printf("max V at L1=4/5/6 : %lld / %lld / %lld\n", A.maxV4, A.maxV5, A.maxV6);
    printf("max V   = %lld (L1=%lld) at ", A.maxV, A.maxV_L1); print_g("", A.argmaxV); printf("\n");
    printf("max V at h*_1=0 (L1=4) = %lld at ", A.maxV0); print_g("", A.argmaxV0); printf("\n");
    printf("max h*_2 = %lld (6a1=%lld) at ", A.maxh2, A.maxh2_six); print_g("", A.argmaxh2); printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: bandscan9 --wcone S | --one ... | --climb SEC CCAP SEED | --rand N SEED\n"); return 2; }

    if (!strcmp(argv[1], "--one")) {
        int g[9]; for (int i = 0; i < 9; i++) g[i] = atoi(argv[2 + i]);
        ll lam[4], mu[4], nu[4], W;
        if (!band_triple_from_gaps(g, g + 3, g + 6, lam, mu, nu, &W)) { printf("not band-realisable\n"); return 0; }
        Res r = eval_triple(lam, mu, nu);
        printf("W=%lld lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld) valid=%d L1=%lld L2=%lld L3=%lld 6a1=%lld V=%lld\n",
               W, lam[0], lam[1], lam[2], lam[3], mu[0], mu[1], mu[2], mu[3], nu[0], nu[1], nu[2], nu[3],
               (int)r.valid, r.L1, r.L2, r.L3, r.six_a1, r.V);
        return 0;
    }

    // --wbox SA SB SC : exhaustive over {Aw<=SA, Bw<=SB, Cw<=SC, 4|D} (band-realisable
    // requires SA+SB <= 140 and SC <= 140).  Covers the ASYMMETRIC corners of the band
    // region that the symmetric --wcone truncation misses.
    if (!strcmp(argv[1], "--wbox")) {
        int SA = atoi(argv[2]), SB = atoi(argv[3]), SC = atoi(argv[4]);
        int SM = std::max(SA, std::max(SB, SC));
        std::vector<std::vector<std::array<int, 3>>> G(SM + 1);
        for (int g2 = 0; 3 * g2 <= SM; g2++)
            for (int g1 = 0; 3 * g2 + 2 * g1 <= SM; g1++)
                for (int g0 = 0; 3 * g2 + 2 * g1 + g0 <= SM; g0++)
                    G[3 * g2 + 2 * g1 + g0].push_back({g0, g1, g2});
        struct Cell { int sa, sb, sc; };
        std::vector<Cell> cells;
        for (int sa = 0; sa <= SA; sa++) for (int sb = 0; sb <= SB; sb++) for (int sc = 0; sc <= SC; sc++)
            if ((((sc - sa - sb) % 4) + 4) % 4 == 0 && !G[sa].empty() && !G[sb].empty() && !G[sc].empty())
                cells.push_back({sa, sb, sc});
        fprintf(stderr, "wbox %d/%d/%d : %zu cells\n", SA, SB, SC, cells.size());
        Acc glob;
#pragma omp parallel
        {
            Acc loc;
#pragma omp for schedule(dynamic, 1)
            for (long long ci = 0; ci < (long long)cells.size(); ci++) {
                const Cell &C = cells[ci];
                for (const auto &A3 : G[C.sa]) for (const auto &B3 : G[C.sb]) for (const auto &C3 : G[C.sc]) {
                    int g[9] = {A3[0], A3[1], A3[2], B3[0], B3[1], B3[2], C3[0], C3[1], C3[2]};
                    ll lam[4], mu[4], nu[4], W;
                    if (!band_triple_from_gaps(g, g + 3, g + 6, lam, mu, nu, &W)) continue;
                    Res r = eval_triple(lam, mu, nu);
                    loc.take(g, r);
                    loc.bandTriples += band_multiplicity(g, g + 3, g + 6);
                    if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                        { printf("*** NEGATIVE a1 *** 6a1=%lld V=%lld L1=%lld L2=%lld L3=%lld ", r.six_a1, r.V, r.L1, r.L2, r.L3); print_g("", g); printf("\n"); fflush(stdout); }
                    }
                }
            }
#pragma omp critical
            glob.merge(loc);
        }
        char tag[96]; snprintf(tag, sizeof(tag), "wbox Aw<=%d Bw<=%d Cw<=%d (EXHAUSTIVE)", SA, SB, SC);
        report(tag, glob);
        return 0;
    }

    if (!strcmp(argv[1], "--wcone")) {
        int S = atoi(argv[2]);
        // gap vectors by weight
        std::vector<std::vector<std::array<int, 3>>> G(S + 1);
        for (int g2 = 0; 3 * g2 <= S; g2++)
            for (int g1 = 0; 3 * g2 + 2 * g1 <= S; g1++)
                for (int g0 = 0; 3 * g2 + 2 * g1 + g0 <= S; g0++)
                    G[3 * g2 + 2 * g1 + g0].push_back({g0, g1, g2});
        // cells
        struct Cell { int sa, sb, sc; };
        std::vector<Cell> cells;
        for (int sa = 0; sa <= S; sa++)
            for (int sb = 0; sa + sb <= S; sb++)
                for (int sc = 0; sc <= S; sc++)
                    if ((((sc - sa - sb) % 4) + 4) % 4 == 0 && !G[sa].empty() && !G[sb].empty() && !G[sc].empty())
                        cells.push_back({sa, sb, sc});
        fprintf(stderr, "wcone S=%d : %zu cells\n", S, cells.size());
        Acc glob;
        double t0 = (double)clock() / CLOCKS_PER_SEC;
#pragma omp parallel
        {
            Acc loc;
#pragma omp for schedule(dynamic, 1)
            for (long long ci = 0; ci < (long long)cells.size(); ci++) {
                const Cell &C = cells[ci];
                for (const auto &A3 : G[C.sa]) for (const auto &B3 : G[C.sb]) for (const auto &C3 : G[C.sc]) {
                    int g[9] = {A3[0], A3[1], A3[2], B3[0], B3[1], B3[2], C3[0], C3[1], C3[2]};
                    ll lam[4], mu[4], nu[4], W;
                    if (!band_triple_from_gaps(g, g + 3, g + 6, lam, mu, nu, &W)) continue;
                    Res r = eval_triple(lam, mu, nu);
                    loc.take(g, r);
                    loc.bandTriples += band_multiplicity(g, g + 3, g + 6);
                    if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                        { printf("*** NEGATIVE a1 *** 6a1=%lld V=%lld L1=%lld L2=%lld L3=%lld ", r.six_a1, r.V, r.L1, r.L2, r.L3); print_g("", g); printf("\n"); fflush(stdout); }
                    }
                }
            }
#pragma omp critical
            glob.merge(loc);
        }
        double t1 = (double)clock() / CLOCKS_PER_SEC;
        printf("wcone S=%d elapsed_cpu=%.1fs\n", S, t1 - t0);
        char tag[64]; snprintf(tag, sizeof(tag), "wcone S=%d (EXHAUSTIVE)", S);
        report(tag, glob);
        return 0;
    }

    // ---------------- volume-steered single-box climb in partition space -----
    if (!strcmp(argv[1], "--climb")) {
        double SEC = atof(argv[2]);
        ll CCAP = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 909ULL;
        Acc glob;
        ll gbestV = -1; ll gb[12]; ll gbestL1 = 0, gbestSix = 0;
        double wall0 = (double)time(0);
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 88172645463325252ULL;
            auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
            Acc loc;
            ll lbestV = -1; ll lb[12]; ll lbestL1 = 0, lbestSix = 0;
            ll lam[4], mu[4], nu[4];
            while ((double)time(0) - wall0 < SEC) {
                // random start: SMALL-GAP class (uniform band triples are nonempty with
                // probability ~1e-5, so seeding must be done in gap space), lifted into
                // the band by band_triple_from_gaps.
                bool ok = false;
                for (int tries = 0; tries < 400 && !ok; tries++) {
                    ll K = 1 + rnd(15);
                    int g[9];
                    for (int i = 0; i < 9; i++) g[i] = (int)rnd(K + 1);
                    ll Aw = g[0] + 2LL * g[1] + 3LL * g[2], Bw = g[3] + 2LL * g[4] + 3LL * g[5];
                    ll Cw = g[6] + 2LL * g[7] + 3LL * g[8];
                    ll rr = (((Cw - Aw - Bw) % 4) + 4) % 4;
                    g[6] += (int)((4 - rr) % 4);                       // fix 4 | D
                    ll W;
                    if (!band_triple_from_gaps(g, g + 3, g + 6, lam, mu, nu, &W)) continue;
                    Res r0 = eval_triple(lam, mu, nu);
                    if (r0.valid && r0.V > 0) ok = true;
                }
                if (!ok) continue;
                Res cur = eval_triple(lam, mu, nu);
                int stall = 0;
                while (stall < 250 && (double)time(0) - wall0 < SEC) {
                    // single-box perturbation
                    ll nl[4], nm[4], nn[4];
                    memcpy(nl, lam, sizeof(nl)); memcpy(nm, mu, sizeof(nm)); memcpy(nn, nu, sizeof(nn));
                    int which = (int)rnd(5);
                    int i = (int)rnd(4), j = (int)rnd(4);
                    ll d = 1 + rnd(3);
                    if (rnd(2)) d = -d;
                    if (which == 0) { nl[i] += d; nl[j] -= d; }
                    else if (which == 1) { nm[i] += d; nm[j] -= d; }
                    else if (which == 2) { nn[i] += d; nn[j] -= d; }
                    else if (which == 3) { nl[i] += d; nm[j] -= d; }
                    else { nl[i] += d; nn[j] += d; }
                    // validity: weakly decreasing, nonneg, weight, band
                    bool good = true;
                    for (int t = 0; t < 4; t++) if (nl[t] < 0 || nm[t] < 0 || nn[t] < 0) good = false;
                    for (int t = 0; t < 3 && good; t++) {
                        if (nl[t] < nl[t + 1] || nm[t] < nm[t + 1] || nn[t] < nn[t + 1]) good = false;
                    }
                    ll Wn = nn[0] + nn[1] + nn[2] + nn[3];
                    if (good && (nl[0] + nl[1] + nl[2] + nl[3] + nm[0] + nm[1] + nm[2] + nm[3] != Wn)) good = false;
                    if (good && (Wn < 91 || Wn > 140)) good = false;
                    if (!good) { stall++; continue; }
                    int g[9] = {(int)(nl[0] - nl[1]), (int)(nl[1] - nl[2]), (int)(nl[2] - nl[3]),
                                (int)(nm[0] - nm[1]), (int)(nm[1] - nm[2]), (int)(nm[2] - nm[3]),
                                (int)(nn[0] - nn[1]), (int)(nn[1] - nn[2]), (int)(nn[2] - nn[3])};
                    Res r = eval_triple(nl, nm, nn);
                    loc.take(g, r);
                    if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                        { printf("*** NEGATIVE a1 (climb) *** 6a1=%lld V=%lld lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
                                 r.six_a1, r.V, nl[0], nl[1], nl[2], nl[3], nm[0], nm[1], nm[2], nm[3], nn[0], nn[1], nn[2], nn[3]); fflush(stdout); }
                    }
                    // volume-steered at fixed small c : accept if L1 <= CCAP and V larger
                    bool accept = false;
                    if (r.valid && r.V > 0 && r.L1 <= CCAP) {
                        if (!(cur.valid && cur.V > 0 && cur.L1 <= CCAP)) accept = true;
                        else if (r.V > cur.V) accept = true;
                        else if (r.V == cur.V && rnd(8) == 0) accept = true;  // lateral drift
                    }
                    if (accept) {
                        memcpy(lam, nl, sizeof(nl)); memcpy(mu, nm, sizeof(nm)); memcpy(nu, nn, sizeof(nn));
                        cur = r; stall = 0;
                        if (r.L1 == 4 && r.V > lbestV) {
                            lbestV = r.V; lbestL1 = r.L1; lbestSix = r.six_a1;
                            for (int t = 0; t < 4; t++) { lb[t] = nl[t]; lb[4 + t] = nm[t]; lb[8 + t] = nn[t]; }
                        }
                    } else stall++;
                }
            }
#pragma omp critical
            {
                glob.merge(loc);
                if (lbestV > gbestV) { gbestV = lbestV; gbestL1 = lbestL1; gbestSix = lbestSix; memcpy(gb, lb, sizeof(gb)); }
            }
        }
        report("climb (volume-steered, single-box, band 91..140)", glob);
        if (gbestV >= 0)
            printf("climb best V at L1=4 : V=%lld 6a1=%lld lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
                   gbestV, gbestSix, gb[0], gb[1], gb[2], gb[3], gb[4], gb[5], gb[6], gb[7], gb[8], gb[9], gb[10], gb[11]);
        else printf("climb best V at L1=4 : none\n");
        return 0;
    }

    // ---------------- a1-STEERED descent: minimise 6a1 directly ---------------
    // The volume-steered climb maximises V; but the actual KTT objective is
    //     6a1 = 11 + 2 h*_1 - h*_2 + 2 h*_3      (negativity iff 6a1 < 0).
    // This mode descends 6a1 itself (accept strictly smaller, lateral drift on ties),
    // with random restarts, over the SAME band 91..140 and the SAME single-box moves.
    // -------- exhaustive box scan with a HISTOGRAM of 6a1 over dim-3 polytopes ----
    if (!strcmp(argv[1], "--whist")) {
        int SA = atoi(argv[2]), SB = atoi(argv[3]), SC = atoi(argv[4]);
        int SM = SA; if (SB > SM) SM = SB; if (SC > SM) SM = SC;
        std::vector<std::vector<std::array<int,3>>> G(SM + 1);
        for (int g2 = 0; 3*g2 <= SM; g2++)
            for (int g1 = 0; 3*g2 + 2*g1 <= SM; g1++)
                for (int g0 = 0; 3*g2 + 2*g1 + g0 <= SM; g0++)
                    G[3*g2 + 2*g1 + g0].push_back({g0,g1,g2});
        std::vector<std::array<int,3>> cells;
        for (int sa = 0; sa <= SA; sa++) { if (G[sa].empty()) continue;
          for (int sb = 0; sb <= SB; sb++) { if (G[sb].empty()) continue;
            for (int sc = 0; sc <= SC; sc++) { if (G[sc].empty()) continue;
              if ((((sc - sa - sb) % 4) + 4) % 4 != 0) continue;
              cells.push_back({sa,sb,sc}); } } }
        fprintf(stderr, "whist cells=%zu\n", cells.size());
        const int NB = 200;
        std::vector<ll> hist(NB + 2, 0);   // index 0 = 6a1 < 0 ; 1..NB = 6a1 = i-1 ; NB+1 = >= NB
        Acc glob;
        double t0 = (double)clock()/CLOCKS_PER_SEC;
#pragma omp parallel
        {
            Acc loc; std::vector<ll> lh(NB + 2, 0);
#pragma omp for schedule(dynamic,1)
            for (long long ci = 0; ci < (long long)cells.size(); ci++) {
                {
                    int sa = cells[ci][0], sb = cells[ci][1], sc = cells[ci][2];
                    {
                        for (const auto &A3 : G[sa]) for (const auto &B3 : G[sb]) for (const auto &C3 : G[sc]) {
                            int g[9] = {A3[0],A3[1],A3[2],B3[0],B3[1],B3[2],C3[0],C3[1],C3[2]};
                            ll lam[4],mu[4],nu[4],W;
                            if (!band_triple_from_gaps(g,g+3,g+6,lam,mu,nu,&W)) continue;
                            Res r = eval_triple(lam,mu,nu);
                            loc.take(g,r);
                            loc.bandTriples += band_multiplicity(g,g+3,g+6);
                            if (r.valid && r.V > 0) {
                                if (r.six_a1 < 0) lh[0]++;
                                else if (r.six_a1 >= NB) lh[NB+1]++;
                                else lh[1 + (int)r.six_a1]++;
                            }
                            if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                                { printf("*** NEGATIVE a1 *** 6a1=%lld V=%lld ", r.six_a1, r.V); print_g("", g); printf("\n"); fflush(stdout); }
                            }
                        }
                    }
                }
            }
#pragma omp critical
            { glob.merge(loc); for (int i = 0; i < NB+2; i++) hist[i] += lh[i]; }
        }
        double t1 = (double)clock()/CLOCKS_PER_SEC;
        char tag[96]; snprintf(tag,sizeof(tag),"whist Aw<=%d Bw<=%d Cw<=%d (EXHAUSTIVE)",SA,SB,SC);
        printf("whist elapsed=%.1fs\n", t1-t0);
        report(tag, glob);
        printf("HIST(6a1 over dim-3): neg=%lld", hist[0]);
        for (int i = 1; i <= NB; i++) if (hist[i]) printf(" %d:%lld", i-1, hist[i]);
        printf(" >=%d:%lld\n", NB, hist[NB+1]);
        fflush(stdout);
        return 0;
    }

    if (!strcmp(argv[1], "--aclimb")) {
        double SEC = atof(argv[2]);
        unsigned long long seed0 = (argc > 3) ? strtoull(argv[3], 0, 10) : 4242ULL;
        Acc glob;
        ll gbest = (1LL << 60); ll gb[12] = {0}; ll gbestV = 0, gbestL1 = 0;
        double wall0 = (double)time(0);
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 88172645463325252ULL;
            auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
            Acc loc;
            ll lbest = (1LL << 60); ll lb[12] = {0}; ll lbestV = 0, lbestL1 = 0;
            ll lam[4], mu[4], nu[4];
            while ((double)time(0) - wall0 < SEC) {
                bool ok = false;
                for (int tries = 0; tries < 400 && !ok; tries++) {
                    ll K = 1 + rnd(20);
                    int g[9];
                    for (int i = 0; i < 9; i++) g[i] = (int)rnd(K + 1);
                    ll Aw = g[0] + 2LL * g[1] + 3LL * g[2], Bw = g[3] + 2LL * g[4] + 3LL * g[5];
                    ll Cw = g[6] + 2LL * g[7] + 3LL * g[8];
                    ll rr = (((Cw - Aw - Bw) % 4) + 4) % 4;
                    g[6] += (int)((4 - rr) % 4);
                    ll W;
                    if (!band_triple_from_gaps(g, g + 3, g + 6, lam, mu, nu, &W)) continue;
                    Res r0 = eval_triple(lam, mu, nu);
                    if (r0.valid && r0.V > 0) ok = true;
                }
                if (!ok) continue;
                Res cur = eval_triple(lam, mu, nu);
                int stall = 0;
                while (stall < 400 && (double)time(0) - wall0 < SEC) {
                    ll nl[4], nm[4], nn[4];
                    memcpy(nl, lam, sizeof(nl)); memcpy(nm, mu, sizeof(nm)); memcpy(nn, nu, sizeof(nn));
                    int which = (int)rnd(5);
                    int i = (int)rnd(4), j = (int)rnd(4);
                    ll d = 1 + rnd(3);
                    if (rnd(2)) d = -d;
                    if (which == 0) { nl[i] += d; nl[j] -= d; }
                    else if (which == 1) { nm[i] += d; nm[j] -= d; }
                    else if (which == 2) { nn[i] += d; nn[j] -= d; }
                    else if (which == 3) { nl[i] += d; nm[j] -= d; }
                    else { nl[i] += d; nn[j] += d; }
                    bool good = true;
                    for (int t = 0; t < 4; t++) if (nl[t] < 0 || nm[t] < 0 || nn[t] < 0) good = false;
                    for (int t = 0; t < 3 && good; t++)
                        if (nl[t] < nl[t + 1] || nm[t] < nm[t + 1] || nn[t] < nn[t + 1]) good = false;
                    ll Wn = nn[0] + nn[1] + nn[2] + nn[3];
                    if (good && (nl[0] + nl[1] + nl[2] + nl[3] + nm[0] + nm[1] + nm[2] + nm[3] != Wn)) good = false;
                    if (good && (Wn < 91 || Wn > 140)) good = false;
                    if (!good) { stall++; continue; }
                    int g[9] = {(int)(nl[0] - nl[1]), (int)(nl[1] - nl[2]), (int)(nl[2] - nl[3]),
                                (int)(nm[0] - nm[1]), (int)(nm[1] - nm[2]), (int)(nm[2] - nm[3]),
                                (int)(nn[0] - nn[1]), (int)(nn[1] - nn[2]), (int)(nn[2] - nn[3])};
                    Res r = eval_triple(nl, nm, nn);
                    loc.take(g, r);
                    if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                        { printf("*** NEGATIVE a1 (aclimb) *** 6a1=%lld V=%lld lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
                                 r.six_a1, r.V, nl[0], nl[1], nl[2], nl[3], nm[0], nm[1], nm[2], nm[3], nn[0], nn[1], nn[2], nn[3]); fflush(stdout); }
                    }
                    bool accept = false;
                    if (r.valid && r.V > 0) {
                        if (!(cur.valid && cur.V > 0)) accept = true;
                        else if (r.six_a1 < cur.six_a1) accept = true;
                        else if (r.six_a1 == cur.six_a1 && rnd(4) == 0) accept = true;
                    }
                    if (accept) {
                        memcpy(lam, nl, sizeof(nl)); memcpy(mu, nm, sizeof(nm)); memcpy(nu, nn, sizeof(nn));
                        cur = r; stall = 0;
                        if (r.six_a1 < lbest) {
                            lbest = r.six_a1; lbestV = r.V; lbestL1 = r.L1;
                            for (int t = 0; t < 4; t++) { lb[t] = nl[t]; lb[4 + t] = nm[t]; lb[8 + t] = nn[t]; }
                        }
                    } else stall++;
                }
            }
#pragma omp critical
            {
                glob.merge(loc);
                if (lbest < gbest) { gbest = lbest; gbestV = lbestV; gbestL1 = lbestL1; memcpy(gb, lb, sizeof(gb)); }
            }
        }
        report("aclimb (a1-steered descent, single-box, band 91..140)", glob);
        printf("aclimb best 6a1 = %lld (V=%lld L1=%lld) lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
               gbest, gbestV, gbestL1, gb[0], gb[1], gb[2], gb[3], gb[4], gb[5], gb[6], gb[7], gb[8], gb[9], gb[10], gb[11]);
        return 0;
    }

    if (!strcmp(argv[1], "--rand")) {
        ll N = atoll(argv[2]);
        unsigned long long seed0 = (argc > 3) ? strtoull(argv[3], 0, 10) : 909ULL;
        Acc glob;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 999331ULL;
            auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
            Acc loc;
#pragma omp for schedule(dynamic, 4096)
            for (ll it = 0; it < N; it++) {
                ll W = 91 + rnd(50);
                ll lam[4], mu[4], nu[4];
                ll q[3] = {rnd(W + 1), rnd(W + 1), rnd(W + 1)}; std::sort(q, q + 3);
                nu[0] = W - q[2]; nu[1] = q[2] - q[1]; nu[2] = q[1] - q[0]; nu[3] = q[0];
                ll wa = rnd(W + 1), wb = W - wa;
                ll p[3] = {rnd(wa + 1), rnd(wa + 1), rnd(wa + 1)}; std::sort(p, p + 3);
                lam[0] = wa - p[2]; lam[1] = p[2] - p[1]; lam[2] = p[1] - p[0]; lam[3] = p[0];
                ll s[3] = {rnd(wb + 1), rnd(wb + 1), rnd(wb + 1)}; std::sort(s, s + 3);
                mu[0] = wb - s[2]; mu[1] = s[2] - s[1]; mu[2] = s[1] - s[0]; mu[3] = s[0];
                int g[9] = {(int)(lam[0] - lam[1]), (int)(lam[1] - lam[2]), (int)(lam[2] - lam[3]),
                            (int)(mu[0] - mu[1]), (int)(mu[1] - mu[2]), (int)(mu[2] - mu[3]),
                            (int)(nu[0] - nu[1]), (int)(nu[1] - nu[2]), (int)(nu[2] - nu[3])};
                Res r = eval_triple(lam, mu, nu);
                loc.take(g, r);
                if (r.valid && r.six_a1 < 0) {
#pragma omp critical
                    { printf("*** NEGATIVE a1 (rand) *** 6a1=%lld V=%lld lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
                             r.six_a1, r.V, lam[0], lam[1], lam[2], lam[3], mu[0], mu[1], mu[2], mu[3], nu[0], nu[1], nu[2], nu[3]); fflush(stdout); }
                }
            }
#pragma omp critical
            glob.merge(loc);
        }
        report("rand (uniform band triples 91..140)", glob);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 2;
}
