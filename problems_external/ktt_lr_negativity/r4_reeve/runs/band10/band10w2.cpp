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


// ===================== BAND 10 WAVE-2 (hunter 10, second pass) ==============
//
// NEW MODE  --ladder v1,v2,...,vk
//   Exhaustive scan of the 9-dim gap lattice over a user-supplied VALUE LADDER
//   (typically geometric).  Rationale: a_1 is HOMOGENEOUS OF DEGREE 1 in the
//   gap vector g (verified exactly in b10w2_verify.py: a_k(t g) = t^k a_k(g)),
//   so { g : a_1(g) < 0 } is a CONE and only the DIRECTION of g matters.  A box
//   [0,G]^9 can only realise coordinate ratios up to G; a geometric ladder
//   reaches ratios far beyond that at the same vector count, probing chamber
//   directions no box census of comparable cost can see.
//
//   Reported, all exact integer:
//     min 6a1 (a_1 < 0 iff 6a1 < 0), count of negatives,
//     max V, max V at c = L(1) = 4  (h*_1 = 0: the Reeve stratum),
//     max V at every c <= 24, min 6a1 restricted to c <= 8, and the full
//     (c,V) argmin data.
//
//   NOTE on a display bug inherited from gapscan.cpp: its per-c table printed
//   "6a1 = 3c - V", omitting the +3i interior term.  Here the true 6a1 is
//   stored and printed.

static void parse_ladder(const char *s, std::vector<int> &out) {
    std::string t(s); size_t p = 0;
    while (p < t.size()) {
        size_t q = t.find(',', p);
        if (q == std::string::npos) q = t.size();
        out.push_back(atoi(t.substr(p, q - p).c_str()));
        p = q + 1;
    }
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
}


// --slab MAXUV v1,v2,...  : the two gaps a2 = lam2-lam3 (= g[1]) and
// c2 = nu2-nu3 (= g[7]) are exactly the widths of the (u,v) fibre grid over
// which L(n) is summed; dim Q = 3 forces both to be >= 1, and SMALL values of
// them are precisely the regime in which Q can have few lattice points while
// being long in the x direction -- i.e. the only regime in which the Reeve
// mechanism (c = 4 with large V) could possibly live.  They are also the two
// coordinates that dominate the evaluation cost, so holding them small lets
// the OTHER SEVEN gaps range over a ladder reaching far beyond any box census.
static int slab_mode(int MAXUV, const std::vector<int> &LAD) {
    int W = (int)LAD.size();
    ll TOT7 = 1; for (int i = 0; i < 7; i++) TOT7 *= (ll)W;
    ll TOT = TOT7 * (ll)(MAXUV) * (ll)(MAXUV);
    fprintf(stderr, "slab: uv in [1,%d]^2, 7 free gaps over ladder size %d, %lld vectors\n", MAXUV, W, TOT);
    const int CB = 25;
    ll g_min = (1LL << 60); int g_argmin[9] = {0}; ll g_minV = 0, g_minC = 0;
    ll g_neg = 0, g_valid = 0;
    ll g_maxV = 0; int g_argmaxV[9] = {0}; ll g_maxVC = 0;
    std::vector<ll> g_maxVc(CB, -1);
    std::vector<std::vector<int> > g_argVc(CB, std::vector<int>(9, 0));
#pragma omp parallel
    {
        ll l_min = (1LL << 60); int l_argmin[9] = {0}; ll l_minV = 0, l_minC = 0;
        ll l_neg = 0, l_valid = 0;
        ll l_maxV = 0; int l_argmaxV[9] = {0}; ll l_maxVC = 0;
        std::vector<ll> l_maxVc(CB, -1);
        std::vector<std::vector<int> > l_argVc(CB, std::vector<int>(9, 0));
#pragma omp for schedule(dynamic, 256)
        for (ll code = 0; code < TOT; code++) {
            ll t = code;
            int uv1 = 1 + (int)(t % (ll)MAXUV); t /= (ll)MAXUV;
            int uv2 = 1 + (int)(t % (ll)MAXUV); t /= (ll)MAXUV;
            int g[9];
            int free_idx[7] = {0, 2, 3, 4, 5, 6, 8};
            for (int i = 0; i < 7; i++) { g[free_idx[i]] = LAD[(int)(t % (ll)W)]; t /= (ll)W; }
            g[1] = uv1; g[7] = uv2;
            Res r = eval_gaps(g, g + 3, g + 6);
            if (!r.valid) continue;
            l_valid++;
            if (r.six_a1 < 0) l_neg++;
            if (r.V > 0 && r.six_a1 < l_min) { l_min = r.six_a1; l_minV = r.V; l_minC = r.L1; memcpy(l_argmin, g, sizeof(g)); }
            if (r.V > l_maxV) { l_maxV = r.V; l_maxVC = r.L1; memcpy(l_argmaxV, g, sizeof(g)); }
            if (r.L1 < CB && r.V > l_maxVc[r.L1]) { l_maxVc[r.L1] = r.V; for (int i = 0; i < 9; i++) l_argVc[r.L1][i] = g[i]; }
        }
#pragma omp critical
        {
            g_valid += l_valid; g_neg += l_neg;
            if (l_min < g_min) { g_min = l_min; g_minV = l_minV; g_minC = l_minC; memcpy(g_argmin, l_argmin, sizeof(l_argmin)); }
            if (l_maxV > g_maxV) { g_maxV = l_maxV; g_maxVC = l_maxVC; memcpy(g_argmaxV, l_argmaxV, sizeof(l_argmaxV)); }
            for (int k = 0; k < CB; k++) if (l_maxVc[k] > g_maxVc[k]) { g_maxVc[k] = l_maxVc[k]; g_argVc[k] = l_argVc[k]; }
        }
    }
    printf("SLAB MAXUV=%d ladder[", MAXUV);
    for (int i = 0; i < W; i++) printf("%s%d", i ? "," : "", LAD[i]);
    printf("]  vectors=%lld realisable=%lld\n", TOT, g_valid);
    printf("NEGATIVE a1 count = %lld\n", g_neg);
    printf("min 6a1 = %lld (c=%lld V=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_min, g_minC, g_minV, g_argmin[0], g_argmin[1], g_argmin[2], g_argmin[3],
           g_argmin[4], g_argmin[5], g_argmin[6], g_argmin[7], g_argmin[8]);
    printf("max V = %lld (c=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_maxV, g_maxVC, g_argmaxV[0], g_argmaxV[1], g_argmaxV[2], g_argmaxV[3],
           g_argmaxV[4], g_argmaxV[5], g_argmaxV[6], g_argmaxV[7], g_argmaxV[8]);
    printf("max V at each c = L(1):\n");
    for (int k = 1; k < CB; k++) if (g_maxVc[k] >= 0)
        printf("   c=%2d : Vmax=%8lld  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               k, g_maxVc[k], g_argVc[k][0], g_argVc[k][1], g_argVc[k][2], g_argVc[k][3],
               g_argVc[k][4], g_argVc[k][5], g_argVc[k][6], g_argVc[k][7], g_argVc[k][8]);
    printf("REEVE STRATUM: max V at c=4 (h*_1=0) = %lld\n", g_maxVc[4]);
    return 0;
}

int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "--slab")) {
        std::vector<int> L2; parse_ladder(argv[3], L2);
        return slab_mode(atoi(argv[2]), L2);
    }
    if (argc < 3 || strcmp(argv[1], "--ladder")) {
        fprintf(stderr, "usage: band10w2 --ladder v1,..,vk | --slab MAXUV v1,..,vk\n");
        return 2;
    }
    std::vector<int> LAD;
    parse_ladder(argv[2], LAD);
    int W = (int)LAD.size();
    ll TOT = 1; for (int i = 0; i < 9; i++) TOT *= (ll)W;
    fprintf(stderr, "ladder size %d, vectors %lld, max value %d\n", W, TOT, LAD.back());

    const int CB = 25;
    ll g_min = (1LL << 60); int g_argmin[9] = {0}; ll g_minV = 0, g_minC = 0;
    ll g_neg = 0, g_valid = 0, g_nonempty = 0;
    ll g_maxV = 0; int g_argmaxV[9] = {0}; ll g_maxVc_ = 0;
    std::vector<ll> g_maxVc(CB, -1);
    std::vector<std::vector<int> > g_argVc(CB, std::vector<int>(9, 0));
    ll g_minSC = (1LL << 60); int g_argSC[9] = {0}; ll g_scV = 0, g_scC = 0;

#pragma omp parallel
    {
        ll l_min = (1LL << 60); int l_argmin[9] = {0}; ll l_minV = 0, l_minC = 0;
        ll l_neg = 0, l_valid = 0, l_nonempty = 0;
        ll l_maxV = 0; int l_argmaxV[9] = {0}; ll l_maxVc_ = 0;
        std::vector<ll> l_maxVc(CB, -1);
        std::vector<std::vector<int> > l_argVc(CB, std::vector<int>(9, 0));
        ll l_minSC = (1LL << 60); int l_argSC[9] = {0}; ll l_scV = 0, l_scC = 0;
#pragma omp for schedule(dynamic, 512)
        for (ll code = 0; code < TOT; code++) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = LAD[(int)(t % (ll)W)]; t /= (ll)W; }
            Res r = eval_gaps(g, g + 3, g + 6);
            if (!r.valid) continue;
            l_valid++;
            if (r.L1 > 0) l_nonempty++;
            if (r.six_a1 < 0) l_neg++;
            if (r.V > 0 && r.six_a1 < l_min) {
                l_min = r.six_a1; l_minV = r.V; l_minC = r.L1; memcpy(l_argmin, g, sizeof(g));
            }
            if (r.V > l_maxV) { l_maxV = r.V; l_maxVc_ = r.L1; memcpy(l_argmaxV, g, sizeof(g)); }
            if (r.L1 < CB && r.V > l_maxVc[r.L1]) {
                l_maxVc[r.L1] = r.V; for (int i = 0; i < 9; i++) l_argVc[r.L1][i] = g[i];
            }
            if (r.V > 0 && r.L1 <= 8 && r.six_a1 < l_minSC) {
                l_minSC = r.six_a1; l_scV = r.V; l_scC = r.L1; memcpy(l_argSC, g, sizeof(g));
            }
        }
#pragma omp critical
        {
            g_valid += l_valid; g_neg += l_neg; g_nonempty += l_nonempty;
            if (l_min < g_min) { g_min = l_min; g_minV = l_minV; g_minC = l_minC; memcpy(g_argmin, l_argmin, sizeof(l_argmin)); }
            if (l_maxV > g_maxV) { g_maxV = l_maxV; g_maxVc_ = l_maxVc_; memcpy(g_argmaxV, l_argmaxV, sizeof(l_argmaxV)); }
            for (int k = 0; k < CB; k++) if (l_maxVc[k] > g_maxVc[k]) { g_maxVc[k] = l_maxVc[k]; g_argVc[k] = l_argVc[k]; }
            if (l_minSC < g_minSC) { g_minSC = l_minSC; g_scV = l_scV; g_scC = l_scC; memcpy(g_argSC, l_argSC, sizeof(l_argSC)); }
        }
    }
    printf("LADDER [");
    for (int i = 0; i < W; i++) printf("%s%d", i ? "," : "", LAD[i]);
    printf("]  vectors=%lld  realisable(4|D)=%lld  nonempty=%lld\n", TOT, g_valid, g_nonempty);
    printf("NEGATIVE a1 count = %lld\n", g_neg);
    printf("min 6a1 = %lld  (c=%lld V=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_min, g_minC, g_minV, g_argmin[0], g_argmin[1], g_argmin[2], g_argmin[3],
           g_argmin[4], g_argmin[5], g_argmin[6], g_argmin[7], g_argmin[8]);
    printf("min 6a1 with c<=8 = %lld (c=%lld V=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_minSC, g_scC, g_scV, g_argSC[0], g_argSC[1], g_argSC[2], g_argSC[3],
           g_argSC[4], g_argSC[5], g_argSC[6], g_argSC[7], g_argSC[8]);
    printf("max V = %lld (at c=%lld) at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           g_maxV, g_maxVc_, g_argmaxV[0], g_argmaxV[1], g_argmaxV[2], g_argmaxV[3],
           g_argmaxV[4], g_argmaxV[5], g_argmaxV[6], g_argmaxV[7], g_argmaxV[8]);
    printf("max V at each c = L(1):\n");
    for (int k = 1; k < CB; k++) if (g_maxVc[k] >= 0)
        printf("   c=%2d : Vmax=%6lld  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
               k, g_maxVc[k], g_argVc[k][0], g_argVc[k][1], g_argVc[k][2], g_argVc[k][3],
               g_argVc[k][4], g_argVc[k][5], g_argVc[k][6], g_argVc[k][7], g_argVc[k][8]);
    printf("REEVE STRATUM: max V at c=4 (h*_1=0) = %lld\n", g_maxVc[4]);
    return 0;
}
