// band8_gapscan.cpp -- EXHAUSTIVE r=4 hive census of the weight band W=|nu| in [61,90],
// carried out on the GAP MODULI SPACE rather than on raw triples.
//
// MODULI REDUCTION (this is what makes the whole band reachable).
//   L(n) = c(n nu; n lam, n mu) is invariant under
//        (lam, nu) -> (lam + 1^4, nu + 1^4)      and      (mu, nu) -> (mu + 1^4, nu + 1^4)
//   so it depends on (lam, mu, nu) only through the 9 gaps
//        a_i = lam_i - lam_{i+1},  b_i = mu_i - mu_{i+1},  c_i = nu_i - nu_{i+1}   (i=1,2,3)
//   Put  Aw = a1+2a2+3a3 = |lam| - 4 lam_4,   Bw, Cw likewise.
//   A gap class (a,b,c) is realised by a triple of weight W = |nu| iff
//        Cw <= W,  4 | (W - Cw),  Aw + Bw <= W,  4 | (W - Aw - Bw),
//   and then the realising triples of weight W are in bijection with the choices
//   nu_4 = (W-Cw)/4  (forced) and  (lam_4, mu_4) with lam_4 + mu_4 = (W-Aw-Bw)/4,
//   i.e. exactly  (W-Aw-Bw)/4 + 1  ordered triples.
//
//   Hence the class region for a single weight W is
//        R(W) = { Cw <= W, Cw = W (mod 4), Aw+Bw <= W, Aw+Bw = W (mod 4) }
//   and for the band, R = union_{W=61..90} R(W).  Both are enumerated EXACTLY here.
//
//   GATE: sum over R(W) of the multiplicity (W-Aw-Bw)/4 + 1 must equal the exact
//   number of ordered triples of weight W (band_size.json).  --count checks this.
//
// EXACTNESS.  All 64-bit integer arithmetic; no floating point anywhere.
// build_rows / lattice_count / the Res statistics are taken VERBATIM from the
// validated bandscan.cpp (itself verbatim from gapscan.cpp, cross-calibrated
// against hive4.py, lr_hive.exe and engineB_lrrule.py).
//
// P(n) = L(n) is the Ehrhart polynomial of the (dim <= 3) hive polytope, P(0)=1, so
//     6 a1 = -11 + 18 L1 - 9 L2 + 2 L3 ,   V = L3 - 3 L2 + 3 L1 - 1 ,
//     h*_1 = L1-4, h*_2 = L2-4L1+6, h*_3 = L3-4L2+6L1-4,
//     V = 1+h1+h2+h3 ,  6 a1 = 11 + 2h1 - h2 + 2h3 ,  6 a1 = 3(L1 + h*_3) - V.
// A KTT counterexample in this cell is exactly  6 a1 < 0, i.e. h*_2 > 11 + 2h*_1 + 2h*_3.
//
// Build: clang++ -O3 -march=native -fopenmp -o band8_gapscan.exe band8_gapscan.cpp
// Usage: band8_gapscan --count | --band | --W W | --one a1 a2 a3 b1 b2 b3 c1 c2 c3

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;

static const ll WLO = 61, WHI = 90;

struct Row { int s, q, r; ll rhs; };   // s*x + q*u + r*v <= rhs

// ---- VERBATIM from bandscan.cpp -------------------------------------------
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

// ---- ALGEBRAICALLY IDENTICAL fast rewrite of lattice_count --------------------
// Every row of the r=4 rhombus system has s,r in {-1,0,+1} (checked at runtime;
// if that ever fails we fall back to the reference routine above).  Writing
// base_k(u) = n*rhs_k - q_k*u, the constraint of row k on the fibre over (u,v) is
//     s=+1 :  x <= base_k - r_k v      s=-1 :  x >= -(base_k - r_k v)
//     s= 0 :        base_k - r_k v >= 0
// so, grouping rows by (sign s, r), the whole 18-row loop collapses to three
// min/max aggregates per side, computed ONCE per u, and the v-loop becomes
//     hi = min(hi0, hip - v, him + v),  lo = max(lo0, lop + v, lom - v).
// This is an exact algebraic regrouping, not an approximation; --verify checks
// it against the reference routine on random classes.
struct FastRows {
    bool ok;
    int nHP0, nHPp, nHPm, nLN0, nLNp, nLNm, nZ0, nZp, nZm;
    ll HP0q[24], HP0r[24];   // (q, rhs) pairs per group
    ll HPpq[24], HPpr[24];
    ll HPmq[24], HPmr[24];
    ll LN0q[24], LN0r[24];
    ll LNpq[24], LNpr[24];
    ll LNmq[24], LNmr[24];
    ll Z0q[24],  Z0r[24];
    ll Zpq[24],  Zpr[24];
    ll Zmq[24],  Zmr[24];
};

static void split_rows(const Row *R, int nr, FastRows &F) {
    F.ok = true;
    F.nHP0 = F.nHPp = F.nHPm = F.nLN0 = F.nLNp = F.nLNm = F.nZ0 = F.nZp = F.nZm = 0;
    for (int k = 0; k < nr; k++) {
        int s = R[k].s, r = R[k].r;
        if (s < -1 || s > 1 || r < -1 || r > 1) { F.ok = false; return; }
        ll q = R[k].q, rhs = R[k].rhs;
        if (s > 0) {
            if (r == 0)      { F.HP0q[F.nHP0] = q; F.HP0r[F.nHP0++] = rhs; }
            else if (r == 1) { F.HPpq[F.nHPp] = q; F.HPpr[F.nHPp++] = rhs; }
            else             { F.HPmq[F.nHPm] = q; F.HPmr[F.nHPm++] = rhs; }
        } else if (s < 0) {
            if (r == 0)      { F.LN0q[F.nLN0] = q; F.LN0r[F.nLN0++] = rhs; }
            else if (r == 1) { F.LNpq[F.nLNp] = q; F.LNpr[F.nLNp++] = rhs; }
            else             { F.LNmq[F.nLNm] = q; F.LNmr[F.nLNm++] = rhs; }
        } else {
            if (r == 0)      { F.Z0q[F.nZ0] = q;  F.Z0r[F.nZ0++] = rhs; }
            else if (r == 1) { F.Zpq[F.nZp] = q;  F.Zpr[F.nZp++] = rhs; }
            else             { F.Zmq[F.nZm] = q;  F.Zmr[F.nZm++] = rhs; }
        }
    }
}

static ll lattice_count_fast(const FastRows &F, ll n, ll ulo, ll uhi, ll vlo, ll vhi) {
    const ll INF = (1LL << 60);
    ll total = 0;
    ll nulo = n * ulo, nuhi = n * uhi, nvlo = n * vlo, nvhi = n * vhi;
    for (ll u = nulo; u <= nuhi; u++) {
        ll hi0 = INF, hip = INF, him = INF;
        ll lo0 = -INF, lop = -INF, lom = -INF;
        ll vmin = nvlo, vmax = nvhi;
        bool dead = false;
        for (int k = 0; k < F.nHP0; k++) { ll b = n * F.HP0r[k] - F.HP0q[k] * u; if (b < hi0) hi0 = b; }
        for (int k = 0; k < F.nHPp; k++) { ll b = n * F.HPpr[k] - F.HPpq[k] * u; if (b < hip) hip = b; }
        for (int k = 0; k < F.nHPm; k++) { ll b = n * F.HPmr[k] - F.HPmq[k] * u; if (b < him) him = b; }
        for (int k = 0; k < F.nLN0; k++) { ll b = n * F.LN0r[k] - F.LN0q[k] * u; if (-b > lo0) lo0 = -b; }
        for (int k = 0; k < F.nLNp; k++) { ll b = n * F.LNpr[k] - F.LNpq[k] * u; if (-b > lop) lop = -b; }
        for (int k = 0; k < F.nLNm; k++) { ll b = n * F.LNmr[k] - F.LNmq[k] * u; if (-b > lom) lom = -b; }
        for (int k = 0; k < F.nZ0 && !dead; k++) { ll b = n * F.Z0r[k] - F.Z0q[k] * u; if (b < 0) dead = true; }
        for (int k = 0; k < F.nZp; k++) { ll b = n * F.Zpr[k] - F.Zpq[k] * u; if (b < vmax) vmax = b; }
        for (int k = 0; k < F.nZm; k++) { ll b = n * F.Zmr[k] - F.Zmq[k] * u; if (-b > vmin) vmin = -b; }
        if (dead) continue;
        for (ll v = vmin; v <= vmax; v++) {
            ll hi = hi0;
            { ll t = hip - v; if (t < hi) hi = t; t = him + v; if (t < hi) hi = t; }
            ll lo = lo0;
            { ll t = lop + v; if (t > lo) lo = t; t = lom - v; if (t > lo) lo = t; }
            if (hi >= lo) total += hi - lo + 1;
        }
    }
    return total;
}
// ---- end fast rewrite ---------------------------------------------------------

struct Res {
    bool valid;
    ll L1, L2, L3;
    ll six_a1, V, two_a2, h1, h2, h3;
};

static Res eval_triple(const ll lam[4], const ll mu[4], const ll nu[4]) {
    Res r; r.valid = false; r.L1 = r.L2 = r.L3 = 0; r.six_a1 = 0; r.V = 0; r.two_a2 = 0;
    r.h1 = r.h2 = r.h3 = 0;
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return r;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return r;
    FastRows F; split_rows(R, nr, F);
    if (!F.ok) {   // never observed for r=4; exact reference path
        r.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
        if (r.L1 == 0) return r;
        r.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
        r.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    } else {
    r.L1 = lattice_count_fast(F, 1, ulo, uhi, vlo, vhi);
    if (r.L1 == 0) return r;
    r.L2 = lattice_count_fast(F, 2, ulo, uhi, vlo, vhi);
    r.L3 = lattice_count_fast(F, 3, ulo, uhi, vlo, vhi);
    }
    r.six_a1 = -11 + 18 * r.L1 - 9 * r.L2 + 2 * r.L3;
    r.two_a2 = 2 - 5 * r.L1 + 4 * r.L2 - r.L3;
    r.V = r.L3 - 3 * r.L2 + 3 * r.L1 - 1;
    r.h1 = r.L1 - 4;
    r.h2 = r.L2 - 4 * r.L1 + 6;
    r.h3 = r.L3 - 4 * r.L2 + 6 * r.L1 - 4;
    r.valid = true;
    return r;
}
// ---- end verbatim ---------------------------------------------------------

struct Acc {
    ll tested, nonempty, dim3, neg;
    ll mult;                          // band triples covered (exact multiplicity sum)
    ll min6a1, min6a1_V, argmin[12];
    ll maxV, argmaxV[12];
    ll maxV_h1z, argmaxV_h1z[12];
    ll maxh2, argmaxh2[12];
    static const int CB = 24;
    ll maxVc[CB], argVc[CB][12];
    ll hist[64];
    ll minBig, minBigV, argminBig[12];
    ll ratN, ratD, argRat[12];
    ll min2a2, argmin2a2[12], neg_a2;
    std::vector<ll> hits;
    Acc() { tested = nonempty = dim3 = neg = 0; mult = 0; min6a1 = (1LL<<60); min6a1_V = 0;
            maxV = -1; maxV_h1z = -1; maxh2 = -1;
            memset(argmin,0,sizeof(argmin)); memset(argmaxV,0,sizeof(argmaxV));
            memset(argmaxV_h1z,0,sizeof(argmaxV_h1z)); memset(argmaxh2,0,sizeof(argmaxh2));
            for (int i=0;i<CB;i++){ maxVc[i] = -1; memset(argVc[i],0,sizeof(argVc[i])); }
            memset(hist,0,sizeof(hist)); minBig=(1LL<<60); minBigV=0; memset(argminBig,0,sizeof(argminBig));
            ratN=0; ratD=1; memset(argRat,0,sizeof(argRat));
            min2a2=(1LL<<60); neg_a2=0; memset(argmin2a2,0,sizeof(argmin2a2)); }
};

static void setarg(ll *dst, const ll lam[4], const ll mu[4], const ll nu[4]) {
    for (int i=0;i<4;i++){ dst[i]=lam[i]; dst[4+i]=mu[i]; dst[8+i]=nu[i]; }
}

// w = 1 or 2 : the multiplicity of the class under the lam <-> mu swap, which
// leaves c(n nu; n lam, n mu) invariant and hence leaves L1,L2,L3 -- and every
// statistic below -- invariant.  Scanning only Aw <= Bw (and ia <= ib when
// Aw == Bw) with w = 2 off the diagonal is therefore EXACTLY equivalent to the
// full scan, at half the cost.
static void feed(Acc &A, const ll lam[4], const ll mu[4], const ll nu[4], const Res &r, ll w) {
    A.tested += w;
    if (!r.valid) return;
    A.nonempty += w;
    if (r.V <= 0) return;
    A.dim3 += w;
    if (r.six_a1 < A.min6a1) { A.min6a1 = r.six_a1; A.min6a1_V = r.V; setarg(A.argmin, lam, mu, nu); }
    if (r.V > A.maxV) { A.maxV = r.V; setarg(A.argmaxV, lam, mu, nu); }
    if (r.h1 == 0 && r.V > A.maxV_h1z) { A.maxV_h1z = r.V; setarg(A.argmaxV_h1z, lam, mu, nu); }
    if (r.h2 > A.maxh2) { A.maxh2 = r.h2; setarg(A.argmaxh2, lam, mu, nu); }
    if (r.L1 < Acc::CB && r.V > A.maxVc[r.L1]) { A.maxVc[r.L1] = r.V; setarg(A.argVc[r.L1], lam, mu, nu); }
    if (r.six_a1 >= 0 && r.six_a1 < 64) A.hist[r.six_a1] += w;
    if (r.two_a2 < A.min2a2) { A.min2a2 = r.two_a2; setarg(A.argmin2a2, lam, mu, nu); }
    if (r.two_a2 < 0) A.neg_a2 += w;
    { ll den = r.L1 + r.h3;
      if (den > 0 && r.V * A.ratD > A.ratN * den) { A.ratN = r.V; A.ratD = den; setarg(A.argRat, lam, mu, nu); } }
    if (r.V >= 100 && r.six_a1 < A.minBig) { A.minBig = r.six_a1; A.minBigV = r.V; setarg(A.argminBig, lam, mu, nu); }
    if (r.six_a1 < 0) {
        A.neg += w;
        for (int i=0;i<4;i++) A.hits.push_back(lam[i]);
        for (int i=0;i<4;i++) A.hits.push_back(mu[i]);
        for (int i=0;i<4;i++) A.hits.push_back(nu[i]);
        A.hits.push_back(r.L1); A.hits.push_back(r.L2); A.hits.push_back(r.L3);
        A.hits.push_back(r.six_a1); A.hits.push_back(r.V);
    }
}

static void merge(Acc &G, const Acc &L) {
    G.tested += L.tested; G.nonempty += L.nonempty; G.dim3 += L.dim3; G.neg += L.neg;
    G.mult += L.mult;
    if (L.min6a1 < G.min6a1) { G.min6a1 = L.min6a1; G.min6a1_V = L.min6a1_V; memcpy(G.argmin, L.argmin, sizeof(G.argmin)); }
    if (L.maxV > G.maxV) { G.maxV = L.maxV; memcpy(G.argmaxV, L.argmaxV, sizeof(G.argmaxV)); }
    if (L.maxV_h1z > G.maxV_h1z) { G.maxV_h1z = L.maxV_h1z; memcpy(G.argmaxV_h1z, L.argmaxV_h1z, sizeof(G.argmaxV_h1z)); }
    if (L.maxh2 > G.maxh2) { G.maxh2 = L.maxh2; memcpy(G.argmaxh2, L.argmaxh2, sizeof(G.argmaxh2)); }
    for (int k = 0; k < Acc::CB; k++) if (L.maxVc[k] > G.maxVc[k]) { G.maxVc[k] = L.maxVc[k]; memcpy(G.argVc[k], L.argVc[k], sizeof(G.argVc[k])); }
    for (int k = 0; k < 64; k++) G.hist[k] += L.hist[k];
    G.neg_a2 += L.neg_a2;
    if (L.min2a2 < G.min2a2) { G.min2a2 = L.min2a2; memcpy(G.argmin2a2, L.argmin2a2, sizeof(G.argmin2a2)); }
    if (L.ratN * G.ratD > G.ratN * L.ratD) { G.ratN = L.ratN; G.ratD = L.ratD; memcpy(G.argRat, L.argRat, sizeof(G.argRat)); }
    if (L.minBig < G.minBig) { G.minBig = L.minBig; G.minBigV = L.minBigV; memcpy(G.argminBig, L.argminBig, sizeof(G.argminBig)); }
    for (size_t i = 0; i < L.hits.size(); i++) G.hits.push_back(L.hits[i]);
}

static void pr_arg(const char *tag, const ll *a) {
    printf("%s lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
           tag, a[0],a[1],a[2],a[3], a[4],a[5],a[6],a[7], a[8],a[9],a[10],a[11]);
}

static void report(const char *tag, const Acc &G) {
    printf("[%s] classes=%lld band_triples_covered=%lld nonempty=%lld dim3=%lld NEG=%lld\n",
           tag, G.tested, G.mult, G.nonempty, G.dim3, G.neg);
    if (G.dim3 > 0) {
        printf("[%s] min6a1=%lld (V=%lld)\n", tag, G.min6a1, G.min6a1_V); pr_arg("      argmin6a1:", G.argmin);
        printf("[%s] maxV=%lld\n", tag, G.maxV); pr_arg("      argmaxV  :", G.argmaxV);
        printf("[%s] maxV_hstar1_zero=%lld\n", tag, G.maxV_h1z); pr_arg("      argmaxVh0:", G.argmaxV_h1z);
        printf("[%s] max_hstar2=%lld\n", tag, G.maxh2); pr_arg("      argmaxh2 :", G.argmaxh2);
        for (int k = 0; k < Acc::CB; k++) if (G.maxVc[k] >= 0) {
            printf("[%s] maxV_at_c=%d : V=%lld  lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
                   tag, k, G.maxVc[k], G.argVc[k][0],G.argVc[k][1],G.argVc[k][2],G.argVc[k][3],
                   G.argVc[k][4],G.argVc[k][5],G.argVc[k][6],G.argVc[k][7],
                   G.argVc[k][8],G.argVc[k][9],G.argVc[k][10],G.argVc[k][11]);
        }
        for (int k = 0; k < 64; k++) if (G.hist[k]) printf("[%s] hist6a1 %d %lld\n", tag, k, G.hist[k]);
        printf("[%s] min_2a2=%lld  NEG_a2=%lld\n", tag, G.min2a2, G.neg_a2);
        pr_arg("      argmin2a2:", G.argmin2a2);
        printf("[%s] max_V_over_L1plus_hstar3 = %lld/%lld  (a1<0 iff > 3)\n", tag, G.ratN, G.ratD);
        pr_arg("      argmaxrat:", G.argRat);
        if (G.minBigV > 0) {
            printf("[%s] min6a1_at_V_ge_100=%lld (V=%lld)\n", tag, G.minBig, G.minBigV);
            pr_arg("      argminBig:", G.argminBig);
        }
    }
    for (size_t i = 0; i + 17 <= G.hits.size(); i += 17) {
        const ll *h = &G.hits[i];
        printf("[%s] HIT lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld) L=(%lld,%lld,%lld) 6a1=%lld V=%lld\n",
               tag, h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11],h[12],h[13],h[14],h[15],h[16]);
    }
    fflush(stdout);
}

// --------------------------------------------------------------------------
//  gap lists:  G[w] = all (g1,g2,g3) >= 0 with g1 + 2 g2 + 3 g3 = w
// --------------------------------------------------------------------------
struct G3 { int g[3]; };
static std::vector< std::vector<G3> > GL;

static void build_gaplists(int WMAX) {
    GL.assign(WMAX + 1, std::vector<G3>());
    for (int w = 0; w <= WMAX; w++)
        for (int g3 = 0; 3 * g3 <= w; g3++)
            for (int g2 = 0; 2 * g2 + 3 * g3 <= w; g2++) {
                G3 t; t.g[0] = w - 2 * g2 - 3 * g3; t.g[1] = g2; t.g[2] = g3;
                GL[w].push_back(t);
            }
}

// smallest W in [WLO,WHI] realising the class (Aw,Bw,Cw); -1 if none.
// Requires Cw = Aw+Bw (mod 4) (checked by caller).
static inline ll first_W(ll Aw, ll Bw, ll Cw) {
    ll m = std::max(Cw, Aw + Bw);
    ll lo = std::max(m, WLO);
    if (lo > WHI) return -1;
    ll d = ((Cw - lo) % 4 + 4) % 4;
    ll W = lo + d;
    return (W <= WHI) ? W : -1;
}

// exact number of ordered band triples represented by the class
static inline ll multiplicity(ll Aw, ll Bw, ll Cw) {
    ll tot = 0;
    for (ll W = WLO; W <= WHI; W++) {
        if (W < Cw || W < Aw + Bw) continue;
        if (((W - Cw) % 4 + 4) % 4) continue;
        if (((W - Aw - Bw) % 4 + 4) % 4) continue;
        tot += (W - Aw - Bw) / 4 + 1;
    }
    return tot;
}

static inline ll multiplicity_W(ll W, ll Aw, ll Bw, ll Cw) {
    if (W < Cw || W < Aw + Bw) return 0;
    if (((W - Cw) % 4 + 4) % 4) return 0;
    if (((W - Aw - Bw) % 4 + 4) % 4) return 0;
    return (W - Aw - Bw) / 4 + 1;
}

// materialise a genuine BAND triple representing the class at weight W
static inline void band_triple(ll W, const int a[3], const int b[3], const int c[3],
                               ll Aw, ll Bw, ll Cw, ll lam[4], ll mu[4], ll nu[4]) {
    ll n4 = (W - Cw) / 4;
    ll l4 = (W - Aw - Bw) / 4;
    ll m4 = 0;
    lam[0] = l4 + a[0] + a[1] + a[2]; lam[1] = l4 + a[1] + a[2]; lam[2] = l4 + a[2]; lam[3] = l4;
    mu[0]  = m4 + b[0] + b[1] + b[2]; mu[1]  = m4 + b[1] + b[2]; mu[2]  = m4 + b[2]; mu[3]  = m4;
    nu[0]  = n4 + c[0] + c[1] + c[2]; nu[1]  = n4 + c[1] + c[2]; nu[2]  = n4 + c[2]; nu[3]  = n4;
}

// --------------------------------------------------------------------------
//  the scan.  Wfix = -1 : union region over the whole band; else the region R(W).
// --------------------------------------------------------------------------
struct Task { int Cw, Aw, Bw; };

static void run_scan(ll Wfix, const char *tag, int CwLo = 0, int CwHi = (int)WHI) {
    std::vector<Task> tasks;
    for (int Cw = CwLo; Cw <= CwHi; Cw++) {
        for (int S = 0; S <= (int)WHI; S++) {
            if (((Cw - S) % 4 + 4) % 4) continue;
            if (Wfix >= 0) {
                if (Cw > Wfix || S > Wfix) continue;
                if (((Wfix - Cw) % 4 + 4) % 4) continue;
                if (((Wfix - S) % 4 + 4) % 4) continue;
            } else {
                if (first_W(S, 0, Cw) < 0) continue;   // uses Aw+Bw = S only
            }
            for (int Aw = 0; 2 * Aw <= S; Aw++) {      // lam <-> mu symmetry: Aw <= Bw
                Task t; t.Cw = Cw; t.Aw = Aw; t.Bw = S - Aw;
                tasks.push_back(t);
            }
        }
    }
    // longest-processing-time-first ordering: the exact enumeration is unchanged,
    // only the order in which the (Cw,Aw,Bw) blocks are handed to threads.
    {
        std::vector<ll> cost(tasks.size());
        for (size_t i = 0; i < tasks.size(); i++) {
            const Task &T = tasks[i];
            ll sa = 0; for (size_t k = 0; k < GL[T.Aw].size(); k++) sa += GL[T.Aw][k].g[1] + 1;
            ll sc = 0; for (size_t k = 0; k < GL[T.Cw].size(); k++) sc += GL[T.Cw][k].g[1] + 1;
            cost[i] = sa * sc * (ll)GL[T.Bw].size();
        }
        std::vector<size_t> ord(tasks.size());
        for (size_t i = 0; i < ord.size(); i++) ord[i] = i;
        std::sort(ord.begin(), ord.end(), [&](size_t x, size_t y) { return cost[x] > cost[y]; });
        std::vector<Task> t2(tasks.size());
        for (size_t i = 0; i < ord.size(); i++) t2[i] = tasks[ord[i]];
        tasks.swap(t2);
    }
    Acc G;
    ll NT = (ll)tasks.size();
    ll donecnt = 0;
#pragma omp parallel
    {
        Acc L;
#pragma omp for schedule(dynamic, 1)
        for (ll ti = 0; ti < NT; ti++) {
            const Task &T = tasks[ti];
            ll Aw = T.Aw, Bw = T.Bw, Cw = T.Cw;
            ll W = (Wfix >= 0) ? Wfix : first_W(Aw, Bw, Cw);
            if (W < 0) continue;
            ll mult = (Wfix >= 0) ? multiplicity_W(Wfix, Aw, Bw, Cw) : multiplicity(Aw, Bw, Cw);
            const std::vector<G3> &LA = GL[Aw];
            const std::vector<G3> &LB = GL[Bw];
            const std::vector<G3> &LC = GL[Cw];
            bool diag = (Aw == Bw);
            for (size_t ic = 0; ic < LC.size(); ic++)
                for (size_t ia = 0; ia < LA.size(); ia++)
                    for (size_t ib = (diag ? ia : 0); ib < LB.size(); ib++) {
                        ll w = (diag && ib == ia) ? 1 : 2;
                        ll lam[4], mu[4], nu[4];
                        band_triple(W, LA[ia].g, LB[ib].g, LC[ic].g, Aw, Bw, Cw, lam, mu, nu);
                        Res r = eval_triple(lam, mu, nu);
                        feed(L, lam, mu, nu, r, w);
                        L.mult += mult * w;
                    }
#pragma omp atomic
            donecnt++;
            if ((donecnt & 1023) == 0) fprintf(stderr, "  ... tasks %lld / %lld\n", donecnt, NT);
        }
#pragma omp critical
        merge(G, L);
    }
    report(tag, G);
}

// counting-only pass: region size + exact band coverage (the multiplicity GATE)
static void run_count() {
    ll classes = 0, cover = 0, cost = 0;
    ll perW[128]; memset(perW, 0, sizeof(perW));
    ll perWclasses[128]; memset(perWclasses, 0, sizeof(perWclasses));
    for (int Cw = 0; Cw <= (int)WHI; Cw++)
        for (int S = 0; S <= (int)WHI; S++) {
            if (((Cw - S) % 4 + 4) % 4) continue;
            if (first_W(S, 0, Cw) < 0) continue;
            for (int Aw = 0; Aw <= S; Aw++) {
                ll Bw = S - Aw;
                ll n = (ll)GL[Aw].size() * (ll)GL[Bw].size() * (ll)GL[Cw].size();
                classes += n;
                cover += n * multiplicity(Aw, Bw, Cw);
                // cost proxy: sum over classes of (a2+1)*(c2+1)
                ll sa = 0; for (size_t i = 0; i < GL[Aw].size(); i++) sa += GL[Aw][i].g[1] + 1;
                ll sc = 0; for (size_t i = 0; i < GL[Cw].size(); i++) sc += GL[Cw][i].g[1] + 1;
                cost += sa * sc * (ll)GL[Bw].size();
                for (ll W = WLO; W <= WHI; W++) {
                    ll m = multiplicity_W(W, Aw, Bw, Cw);
                    if (m) { perW[W] += n * m; perWclasses[W] += n; }
                }
            }
        }
    printf("REGION classes=%lld band_triples_covered=%lld cost_proxy=%lld\n", classes, cover, cost);
    for (ll W = WLO; W <= WHI; W++)
        printf("  W=%lld classes=%lld triples=%lld\n", W, perWclasses[W], perW[W]);
    fflush(stdout);
}

// reference evaluation using the ORIGINAL (unoptimised) lattice_count
static Res eval_triple_ref(const ll lam[4], const ll mu[4], const ll nu[4]) {
    Res r; r.valid = false; r.L1 = r.L2 = r.L3 = 0; r.six_a1 = 0; r.V = 0; r.two_a2 = 0;
    r.h1 = r.h2 = r.h3 = 0;
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return r;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return r;
    r.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (r.L1 == 0) return r;
    r.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    r.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    r.six_a1 = -11 + 18 * r.L1 - 9 * r.L2 + 2 * r.L3;
    r.two_a2 = 2 - 5 * r.L1 + 4 * r.L2 - r.L3;
    r.V = r.L3 - 3 * r.L2 + 3 * r.L1 - 1;
    r.h1 = r.L1 - 4; r.h2 = r.L2 - 4 * r.L1 + 6; r.h3 = r.L3 - 4 * r.L2 + 6 * r.L1 - 4;
    r.valid = true;
    return r;
}

// --verify N SEED : N random classes of the band region, fast vs reference
static void run_verify(ll N, unsigned long long seed) {
    ll bad = 0, nonempty = 0, done = 0;
#pragma omp parallel reduction(+:bad,nonempty,done)
    {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        unsigned long long st = seed * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 7ULL;
        auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
#pragma omp for schedule(static)
        for (ll t = 0; t < N; t++) {
            ll Cw = rnd(WHI + 1);
            ll S = rnd(WHI + 1);
            if (((Cw - S) % 4 + 4) % 4) continue;
            if (first_W(S, 0, Cw) < 0) continue;
            ll Aw = rnd(S + 1), Bw = S - Aw;
            if (GL[Aw].empty() || GL[Bw].empty() || GL[Cw].empty()) continue;
            const G3 &a = GL[Aw][rnd((ll)GL[Aw].size())];
            const G3 &b = GL[Bw][rnd((ll)GL[Bw].size())];
            const G3 &c = GL[Cw][rnd((ll)GL[Cw].size())];
            ll W = first_W(Aw, Bw, Cw);
            ll lam[4], mu[4], nu[4];
            band_triple(W, a.g, b.g, c.g, Aw, Bw, Cw, lam, mu, nu);
            Res f = eval_triple(lam, mu, nu);
            Res g = eval_triple_ref(lam, mu, nu);
            done++;
            if (f.valid) nonempty++;
            if (f.valid != g.valid || f.L1 != g.L1 || f.L2 != g.L2 || f.L3 != g.L3) {
                bad++;
#pragma omp critical
                printf("MISMATCH lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld) fast=(%lld,%lld,%lld) ref=(%lld,%lld,%lld)\n",
                       lam[0],lam[1],lam[2],lam[3],mu[0],mu[1],mu[2],mu[3],nu[0],nu[1],nu[2],nu[3],
                       f.L1,f.L2,f.L3,g.L1,g.L2,g.L3);
            }
        }
    }
    printf("VERIFY sampled=%lld nonempty=%lld mismatches=%lld : %s\n", done, nonempty, bad,
           bad ? "FAIL" : "PASS");
    fflush(stdout);
}

int main(int argc, char **argv) {
    build_gaplists((int)WHI);
    if (argc >= 2 && !strcmp(argv[1], "--verify")) {
        run_verify(atoll(argv[2]), argc > 3 ? strtoull(argv[3], 0, 10) : 20260721ULL);
        return 0;
    }
    if (argc < 2) { fprintf(stderr, "usage: band8_gapscan --count | --band | --W W | --one a1 a2 a3 b1 b2 b3 c1 c2 c3\n"); return 2; }
    if (!strcmp(argv[1], "--count")) { run_count(); return 0; }
    if (!strcmp(argv[1], "--band")) { run_scan(-1, "BAND8-GAPCLASS-EXHAUSTIVE"); return 0; }
    if (!strcmp(argv[1], "--chunk")) {      // Cw slice of the band union region
        int lo = atoi(argv[2]), hi = atoi(argv[3]);
        char tag[64]; snprintf(tag, sizeof(tag), "BAND8-CHUNK-Cw%d..%d", lo, hi);
        run_scan(-1, tag, lo, hi);
        return 0;
    }
    if (!strcmp(argv[1], "--W")) {
        ll W = atoll(argv[2]);
        char tag[64]; snprintf(tag, sizeof(tag), "W%lld-GAPCLASS-EXHAUSTIVE", W);
        run_scan(W, tag);
        return 0;
    }
    if (!strcmp(argv[1], "--one")) {
        int a[3], b[3], c[3];
        for (int i = 0; i < 3; i++) { a[i] = atoi(argv[2+i]); b[i] = atoi(argv[5+i]); c[i] = atoi(argv[8+i]); }
        ll Aw = a[0]+2*a[1]+3*a[2], Bw = b[0]+2*b[1]+3*b[2], Cw = c[0]+2*c[1]+3*c[2];
        ll W = first_W(Aw, Bw, Cw);
        printf("Aw=%lld Bw=%lld Cw=%lld firstW=%lld mult=%lld\n", Aw, Bw, Cw, W, multiplicity(Aw,Bw,Cw));
        if (W < 0) return 0;
        ll lam[4], mu[4], nu[4];
        band_triple(W, a, b, c, Aw, Bw, Cw, lam, mu, nu);
        Res r = eval_triple(lam, mu, nu);
        printf("lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
               lam[0],lam[1],lam[2],lam[3],mu[0],mu[1],mu[2],mu[3],nu[0],nu[1],nu[2],nu[3]);
        printf("valid=%d L=(%lld,%lld,%lld) 6a1=%lld V=%lld h*=(1,%lld,%lld,%lld)\n",
               (int)r.valid, r.L1, r.L2, r.L3, r.six_a1, r.V, r.h1, r.h2, r.h3);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 2;
}
