// band7.cpp -- BAND 7 of the r=4 Reeve-dimension sweep.
//
//   BAND:  W = |nu| in [46,60], nu STRUCTURED (near-staircase / near-rectangular),
//          ALL splits (lam,mu) with |lam|+|mu| = W.
//
// The rhombus-row builder and the exact integer lattice counter are COPIED
// VERBATIM from the already-validated gapscan.cpp (same r=4 hive convention as
// hive4.py / engine A / engine B).  Only the enumeration layer is new.
//
// For each triple we compute exactly
//   L(n) = #( n*Q cap Z^3 ) = c(n nu; n lam, n mu)      (Knutson-Tao)
// for n = 1,2,3 (P has degree <= 3 = dim), and then, with L(0) = 1,
//   6*a1 = -11 + 18 L1 -  9 L2 + 2 L3
//   6*a2 =   6 + 12 L2 - 15 L1 - 3 L3
//   V = 6*a3 = L3 - 3 L2 + 3 L1 - 1          (normalized volume)
//   h*_1 = L1 - 4 ,  h*_2 = L2 - 4 L1 + 6 ,  h*_3 = L3 - 4 L2 + 6 L1 - 4
// All integer arithmetic.  A NEG hit = any of 6a1, 6a2, V strictly < 0.
//
// PRUNE (rigorous): c(nu;lam,mu) != 0 requires lam subset nu and mu subset nu;
// and by Knutson-Tao saturation L(1) = 0 => L(n) = 0 for all n, i.e. P == 0,
// which has no negative coefficient.  Both prunes only remove P == 0 triples.
//
// Build: g++ -O3 -march=native -fopenmp -o band7.exe band7.cpp
// Usage: band7 WLO WHI [--sample K SEED outfile]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <array>
#include <algorithm>
#include <string>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;

struct Row { int s, q, r; ll rhs; };   // s*x + q*u + r*v <= rhs

// ---- VERBATIM from gapscan.cpp -------------------------------------------
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
// ---- end verbatim ---------------------------------------------------------

struct Rec {
    ll lam[4], mu[4], nu[4];
    ll L1, L2, L3, six_a1, six_a2, V, h1, h2, h3;
};

// evaluate one triple; returns false if P == 0 (nothing to test)
static bool eval_triple(const ll lam[4], const ll mu[4], const ll nu[4], Rec &out) {
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return false;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return false;
    ll L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (L1 == 0) return false;
    ll L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    ll L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    for (int i = 0; i < 4; i++) { out.lam[i] = lam[i]; out.mu[i] = mu[i]; out.nu[i] = nu[i]; }
    out.L1 = L1; out.L2 = L2; out.L3 = L3;
    out.six_a1 = -11 + 18 * L1 - 9 * L2 + 2 * L3;
    out.six_a2 = 6 + 12 * L2 - 15 * L1 - 3 * L3;
    out.V = L3 - 3 * L2 + 3 * L1 - 1;
    out.h1 = L1 - 4;
    out.h2 = L2 - 4 * L1 + 6;
    out.h3 = L3 - 4 * L2 + 6 * L1 - 4;
    return true;
}

// ---- band definition ------------------------------------------------------
// nu is IN BAND iff  |nu| = W in [WLO,WHI], nu has at most 4 parts, and either
//   (S) near-staircase : gaps c=(n1-n2,n2-n3,n3-n4) satisfy max(c)-min(c) <= 2
//   (R) near-rectangular: n1 - (smallest POSITIVE part) <= 2
static bool nu_in_band(const ll nu[4], int &fam) {
    ll c1 = nu[0] - nu[1], c2 = nu[1] - nu[2], c3 = nu[2] - nu[3];
    ll mx = std::max(c1, std::max(c2, c3)), mn = std::min(c1, std::min(c2, c3));
    bool S = (mx - mn <= 2);
    ll small = 0;
    for (int i = 3; i >= 0; i--) if (nu[i] > 0) { small = nu[i]; break; }
    bool Rr = (small > 0) && (nu[0] - small <= 2);
    fam = (S ? 1 : 0) | (Rr ? 2 : 0);
    return S || Rr;
}

static void gen_nus(int W, std::vector<std::array<ll,4>> &out) {
    for (ll a = W; a >= 1; a--) {
        if (4 * a < W) break;
        for (ll b = std::min(a, W - a); b >= 0; b--) {
            ll rem2 = W - a - b;
            if (3 * b < rem2) continue;
            for (ll c = std::min(b, rem2); c >= 0; c--) {
                ll d = rem2 - c;
                if (d < 0 || d > c) continue;
                ll nu[4] = {a, b, c, d};
                int fam;
                if (nu_in_band(nu, fam)) out.push_back({a, b, c, d});
            }
        }
    }
}

int main(int argc, char **argv) {
    int WLO = 46, WHI = 60;
    if (argc > 2) { WLO = atoi(argv[1]); WHI = atoi(argv[2]); }
    bool sample = false; ll SK = 0; unsigned long long SEED = 1; const char *sfile = 0;
    bool listnu = false;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--sample")) { sample = true; SK = atoll(argv[i+1]); SEED = strtoull(argv[i+2],0,10); sfile = argv[i+3]; }
        if (!strcmp(argv[i], "--listnu")) listnu = true;
    }

    // collect band nus
    std::vector<std::array<ll,4>> nus;
    std::vector<int> nuW;
    for (int W = WLO; W <= WHI; W++) {
        size_t before = nus.size();
        gen_nus(W, nus);
        for (size_t i = before; i < nus.size(); i++) nuW.push_back(W);
    }
    fprintf(stderr, "band nus: %zu (W in [%d,%d])\n", nus.size(), WLO, WHI);
    if (listnu) {
        for (size_t i = 0; i < nus.size(); i++) {
            int fam; ll t[4] = {nus[i][0],nus[i][1],nus[i][2],nus[i][3]}; nu_in_band(t, fam);
            printf("%lld %lld %lld %lld  W=%d fam=%d\n", t[0],t[1],t[2],t[3], nuW[i], fam);
        }
        return 0;
    }

    // global accumulators
    ll g_pairs = 0;        // (lam,mu) pairs in band up to lam<->mu symmetry
    ll g_pruned = 0;       // killed by containment
    ll g_zero = 0;         // P == 0 (L1 == 0)
    ll g_eval = 0;         // fully evaluated, P != 0
    ll g_dim3 = 0;
    ll g_min6a1 = (1LL << 62); Rec g_argmin;
    ll g_min6a1_d3 = (1LL << 62); Rec g_argmin_d3;
    ll g_min6a2 = (1LL << 62);
    ll g_maxV = -1; Rec g_argmaxV;
    ll g_maxVh1 = -1; Rec g_argmaxVh1;
    ll g_maxh2 = -1; Rec g_argmaxh2;
    ll g_neg = 0;
    ll g_h1zero = 0, g_h1zero_Vgt1 = 0, g_h3pos = 0;
    std::vector<Rec> g_hits;
    std::vector<Rec> g_samples;
    memset(&g_argmin, 0, sizeof(Rec)); memset(&g_argmin_d3, 0, sizeof(Rec)); memset(&g_argmaxV, 0, sizeof(Rec));
    memset(&g_argmaxVh1, 0, sizeof(Rec)); memset(&g_argmaxh2, 0, sizeof(Rec));

#pragma omp parallel
    {
        ll l_pairs=0, l_pruned=0, l_zero=0, l_eval=0, l_dim3=0, l_neg=0;
        ll l_h1zero=0, l_h1zero_Vgt1=0, l_h3pos=0;
        ll l_min6a1 = (1LL<<62), l_min6a1d3 = (1LL<<62), l_min6a2 = (1LL<<62), l_maxV=-1, l_maxVh1=-1, l_maxh2=-1;
        Rec l_argmin, l_argmind3, l_argmaxV, l_argmaxVh1, l_argmaxh2;
        memset(&l_argmin,0,sizeof(Rec)); memset(&l_argmind3,0,sizeof(Rec)); memset(&l_argmaxV,0,sizeof(Rec));
        memset(&l_argmaxVh1,0,sizeof(Rec)); memset(&l_argmaxh2,0,sizeof(Rec));
        std::vector<Rec> l_hits, l_samp;
        unsigned long long st = SEED * 6364136223846793005ULL + 1442695040888963407ULL;
#ifdef _OPENMP
        st += (unsigned long long)omp_get_thread_num() * 0x9E3779B97F4A7C15ULL;
#endif

#pragma omp for schedule(dynamic, 1)
        for (long long ni = 0; ni < (long long)nus.size(); ni++) {
            ll nu[4] = {nus[ni][0], nus[ni][1], nus[ni][2], nus[ni][3]};
            int W = nuW[ni];
            // all partitions lam with <=4 parts, lam subset nu, bucketed by weight
            std::vector<std::vector<std::array<ll,4>>> buck(W + 1);
            for (ll a = 0; a <= nu[0]; a++)
              for (ll b = 0; b <= std::min(a, nu[1]); b++)
                for (ll c = 0; c <= std::min(b, nu[2]); c++)
                  for (ll d = 0; d <= std::min(c, nu[3]); d++) {
                      ll w = a+b+c+d; if (w <= W) buck[w].push_back({a,b,c,d});
                  }
            for (int w = 0; w * 2 <= W; w++) {
                const auto &A = buck[w];
                const auto &B = buck[W - w];
                if (A.empty() || B.empty()) continue;
                for (size_t i = 0; i < A.size(); i++) {
                    size_t jstart = 0;
                    for (size_t j = jstart; j < B.size(); j++) {
                        if (2 * w == W && !(A[i] <= B[j])) continue;  // symmetry
                        l_pairs++;
                        ll lam[4] = {A[i][0],A[i][1],A[i][2],A[i][3]};
                        ll mu[4]  = {B[j][0],B[j][1],B[j][2],B[j][3]};
                        Rec rc;
                        if (!eval_triple(lam, mu, nu, rc)) { l_zero++; continue; }
                        l_eval++;
                        if (rc.V > 0) l_dim3++;
                        if (rc.six_a1 < l_min6a1) { l_min6a1 = rc.six_a1; l_argmin = rc; }
                        if (rc.V > 0 && rc.six_a1 < l_min6a1d3) { l_min6a1d3 = rc.six_a1; l_argmind3 = rc; }
                        if (rc.six_a2 < l_min6a2) l_min6a2 = rc.six_a2;
                        if (rc.V > l_maxV) { l_maxV = rc.V; l_argmaxV = rc; }
                        if (rc.V > 0 && rc.h1 == 0) { l_h1zero++; if (rc.V > 1) l_h1zero_Vgt1++; if (rc.V > l_maxVh1) { l_maxVh1 = rc.V; l_argmaxVh1 = rc; } }
                        if (rc.V > 0 && rc.h3 > 0) l_h3pos++;
                        if (rc.h2 > l_maxh2) { l_maxh2 = rc.h2; l_argmaxh2 = rc; }
                        if (rc.six_a1 < 0 || rc.six_a2 < 0 || rc.V < 0) { l_neg++; if (l_hits.size() < 200) l_hits.push_back(rc); }
                        if (sample) {
                            st ^= st << 13; st ^= st >> 7; st ^= st << 17;
                            if ((ll)l_samp.size() < SK && rc.V > 0 && (st % 251ULL) == 0ULL) l_samp.push_back(rc);
                        }
                    }
                }
            }
        }
#pragma omp critical
        {
            g_pairs += l_pairs; g_pruned += l_pruned; g_zero += l_zero;
            g_eval += l_eval; g_dim3 += l_dim3; g_neg += l_neg;
            g_h1zero += l_h1zero; g_h1zero_Vgt1 += l_h1zero_Vgt1; g_h3pos += l_h3pos;
            if (l_min6a1 < g_min6a1) { g_min6a1 = l_min6a1; g_argmin = l_argmin; }
            if (l_min6a1d3 < g_min6a1_d3) { g_min6a1_d3 = l_min6a1d3; g_argmin_d3 = l_argmind3; }
            if (l_min6a2 < g_min6a2) g_min6a2 = l_min6a2;
            if (l_maxV > g_maxV) { g_maxV = l_maxV; g_argmaxV = l_argmaxV; }
            if (l_maxVh1 > g_maxVh1) { g_maxVh1 = l_maxVh1; g_argmaxVh1 = l_argmaxVh1; }
            if (l_maxh2 > g_maxh2) { g_maxh2 = l_maxh2; g_argmaxh2 = l_argmaxh2; }
            for (auto &h : l_hits) g_hits.push_back(h);
            for (auto &s : l_samp) g_samples.push_back(s);
        }
    }

    auto pr = [](const char *tag, const Rec &r) {
        printf("%s lam=%lld,%lld,%lld,%lld mu=%lld,%lld,%lld,%lld nu=%lld,%lld,%lld,%lld "
               "L=(%lld,%lld,%lld) 6a1=%lld 6a2=%lld V=%lld hstar=[1,%lld,%lld,%lld]\n",
               tag, r.lam[0],r.lam[1],r.lam[2],r.lam[3], r.mu[0],r.mu[1],r.mu[2],r.mu[3],
               r.nu[0],r.nu[1],r.nu[2],r.nu[3], r.L1,r.L2,r.L3, r.six_a1, r.six_a2, r.V,
               r.h1, r.h2, r.h3);
    };
    printf("BAND7 W=[%d,%d] nus=%zu\n", WLO, WHI, nus.size());
    printf("pairs_in_band=%lld  P_identically_zero=%lld  evaluated=%lld  dim3=%lld  NEGATIVE=%lld\n",
           g_pairs, g_zero, g_eval, g_dim3, g_neg);
    printf("min6a1_dim3=%lld\n", g_min6a1_d3);
    printf("hstar1_zero_dim3=%lld  of_which_V_gt_1=%lld  dim3_with_hstar3_pos=%lld\n",
           g_h1zero, g_h1zero_Vgt1, g_h3pos);
    printf("min6a1=%lld  min6a2=%lld  maxV=%lld  maxV_at_hstar1_zero=%lld  maxhstar2=%lld\n",
           g_min6a1, g_min6a2, g_maxV, g_maxVh1, g_maxh2);
    pr("ARGMIN_A1", g_argmin);
    pr("ARGMIN_A1_DIM3", g_argmin_d3);
    pr("ARGMAX_V ", g_argmaxV);
    if (g_maxVh1 >= 0) pr("ARGMAX_V_H1ZERO", g_argmaxVh1);
    if (g_maxh2 >= 0) pr("ARGMAX_H2", g_argmaxh2);
    for (size_t i = 0; i < g_hits.size(); i++) pr("HIT", g_hits[i]);
    if (sample && sfile) {
        FILE *f = fopen(sfile, "w");
        ll n = 0;
        for (auto &r : g_samples) {
            if (n++ >= SK) break;
            fprintf(f, "%lld %lld %lld %lld;%lld %lld %lld %lld;%lld %lld %lld %lld;%lld;%lld;%lld;%lld;%lld;%lld\n",
                r.lam[0],r.lam[1],r.lam[2],r.lam[3], r.mu[0],r.mu[1],r.mu[2],r.mu[3],
                r.nu[0],r.nu[1],r.nu[2],r.nu[3], r.L1,r.L2,r.L3, r.six_a1, r.V, r.h1);
        }
        fclose(f);
        fprintf(stderr, "wrote %lld samples to %s\n", (n<SK?n:SK), sfile);
    }
    return 0;
}
