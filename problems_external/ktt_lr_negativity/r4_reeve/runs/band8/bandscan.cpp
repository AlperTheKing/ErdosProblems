// bandscan.cpp -- r=4 hive-polytope census restricted to a WEIGHT BAND W=|nu|.
//
// Band 8 of the Reeve-dimension sweep:  W in [61,90].
//
// EXACTNESS.  Everything is 64-bit integer arithmetic.  There is no floating
// point in any decision path (the only doubles appear in the hill-climb
// *heuristic* score, which never decides a verdict).
//
// P(n) = c(n nu; n lam, n mu) = L(n) = #(nQ cap Z^3) is a polynomial of degree
// <= 3 with P(0) = 1 (Knutson-Tao: Q is the r=4 hive polytope, dim <= 3, and
// stretching dilates it).  Hence, with L(0)=1,
//     6*a1 = -11 + 18 L(1) - 9 L(2) + 2 L(3)
//     V    = 6*a3 = L(3) - 3 L(2) + 3 L(1) - 1        (normalized volume)
//     6*a2 = 6 + 3(L(1)... )  -- not needed; a2 >= 0 automatically (see below)
// and the h*-vector of the (dim<=3) polytope is
//     h*_0 = 1, h*_1 = L1-4, h*_2 = L2-4L1+6, h*_3 = L3-4L2+6L1-4,
// giving the identities  V = 1+h1+h2+h3  and  6 a1 = 11 + 2h1 - h2 + 2h3.
// So a KTT counterexample in this cell is exactly  h*_2 > 11 + 2h*_1 + 2h*_3.
//
// The rhombus rows and the fibre-counting routine are taken VERBATIM from the
// validated engine gapscan.cpp (which is itself cross-calibrated against
// hive4.py, lr_hive.exe and engineB_lrrule.py).
//
// Build:  clang++ -O3 -march=native -fopenmp -o bandscan.exe bandscan.cpp

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
    bool valid;      // Q nonempty (so P is a genuine Ehrhart polynomial with P(0)=1)
    ll L1, L2, L3;
    ll six_a1, V;
    ll h1, h2, h3;
};

// Fast NECESSARY condition for c(nu;lam,mu) > 0: lam and mu must both fit
// inside nu.  If it fails, c(n nu; n lam, n mu) = 0 for EVERY n >= 1, so
// P == 0 identically and there is no negative coefficient.
static inline bool contained(const ll p[4], const ll nu[4]) {
    return p[0] <= nu[0] && p[1] <= nu[1] && p[2] <= nu[2] && p[3] <= nu[3];
}

static Res eval_triple(const ll lam[4], const ll mu[4], const ll nu[4]) {
    Res r; r.valid = false; r.L1 = r.L2 = r.L3 = 0; r.six_a1 = 0; r.V = 0; r.h1 = r.h2 = r.h3 = 0;
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return r;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return r;
    r.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (r.L1 == 0) return r;              // Q empty  =>  P == 0
    r.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    r.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    r.six_a1 = -11 + 18 * r.L1 - 9 * r.L2 + 2 * r.L3;
    r.V = r.L3 - 3 * r.L2 + 3 * r.L1 - 1;
    r.h1 = r.L1 - 4;
    r.h2 = r.L2 - 4 * r.L1 + 6;
    r.h3 = r.L3 - 4 * r.L2 + 6 * r.L1 - 4;
    r.valid = true;
    return r;
}

// --------------------------------------------------------------------------
//  partitions with at most 4 parts
// --------------------------------------------------------------------------
struct P4 { ll p[4]; };

static void gen_parts(ll N, ll cap, std::vector<P4> &out) {
    // all partitions of N into at most 4 parts, each part <= cap
    out.clear();
    P4 cur;
    for (ll a = std::min(N, cap); a >= (N + 3) / 4; a--) {
        ll r1 = N - a;
        if (r1 == 0) { cur.p[0] = a; cur.p[1] = cur.p[2] = cur.p[3] = 0; out.push_back(cur); continue; }
        for (ll b = std::min(r1, a); b >= (r1 + 2) / 3; b--) {
            ll r2 = r1 - b;
            if (r2 == 0) { cur.p[0] = a; cur.p[1] = b; cur.p[2] = cur.p[3] = 0; out.push_back(cur); continue; }
            for (ll c = std::min(r2, b); c >= (r2 + 1) / 2; c--) {
                ll d = r2 - c;
                if (d > c) continue;
                cur.p[0] = a; cur.p[1] = b; cur.p[2] = c; cur.p[3] = d; out.push_back(cur);
            }
        }
    }
    if (N == 0) { cur.p[0] = cur.p[1] = cur.p[2] = cur.p[3] = 0; out.push_back(cur); }
}

// --------------------------------------------------------------------------
//  accumulator
// --------------------------------------------------------------------------
struct Acc {
    ll tested;          // triples enumerated
    ll pruned;          // triples rejected by containment (P == 0)
    ll nonempty;        // Q nonempty
    ll dim3;            // V > 0
    ll neg;             // six_a1 < 0
    ll min6a1; ll min6a1_V; ll argmin[12];
    ll maxV;  ll argmaxV[12];
    ll maxV_h1z; ll argmaxV_h1z[12];   // max V among h*_1 = 0 (L1 = 4)
    ll maxh2; ll argmaxh2[12];
    // Reeve-relevant stratification: the largest normalized volume seen at each
    // fixed lattice-point count c = L(1).  The Reeve tetrahedron T_q lives at
    // c = 4 (= dim+1, h*_1 = 0) with V = q unbounded; a KTT counterexample of
    // Reeve type would need V >= 13 there.
    static const int CB = 24;
    ll maxVc[CB]; ll argVc[CB][12];
    ll hist[64];                       // histogram of 6a1 for 0 <= 6a1 < 64
    ll minBig; ll minBigV; ll argminBig[12];   // min 6a1 restricted to V >= 100
    std::vector<ll> hits;              // flattened negative records
    Acc() { tested = pruned = nonempty = dim3 = neg = 0; min6a1 = (1LL<<60); min6a1_V = 0;
            maxV = -1; maxV_h1z = -1; maxh2 = -1;
            memset(argmin,0,sizeof(argmin)); memset(argmaxV,0,sizeof(argmaxV));
            memset(argmaxV_h1z,0,sizeof(argmaxV_h1z)); memset(argmaxh2,0,sizeof(argmaxh2));
            for (int i=0;i<CB;i++){ maxVc[i] = -1; memset(argVc[i],0,sizeof(argVc[i])); }
            memset(hist,0,sizeof(hist)); minBig=(1LL<<60); minBigV=0; memset(argminBig,0,sizeof(argminBig)); }
};

static void setarg(ll *dst, const ll lam[4], const ll mu[4], const ll nu[4]) {
    for (int i=0;i<4;i++){ dst[i]=lam[i]; dst[4+i]=mu[i]; dst[8+i]=nu[i]; }
}

static void feed(Acc &A, const ll lam[4], const ll mu[4], const ll nu[4], const Res &r) {
    A.tested++;
    if (!r.valid) return;
    A.nonempty++;
    if (r.V <= 0) return;               // dim <= 2 : Ehrhart-positive classically
    A.dim3++;
    if (r.six_a1 < A.min6a1) { A.min6a1 = r.six_a1; A.min6a1_V = r.V; setarg(A.argmin, lam, mu, nu); }
    if (r.V > A.maxV) { A.maxV = r.V; setarg(A.argmaxV, lam, mu, nu); }
    if (r.h1 == 0 && r.V > A.maxV_h1z) { A.maxV_h1z = r.V; setarg(A.argmaxV_h1z, lam, mu, nu); }
    if (r.h2 > A.maxh2) { A.maxh2 = r.h2; setarg(A.argmaxh2, lam, mu, nu); }
    if (r.L1 < Acc::CB && r.V > A.maxVc[r.L1]) { A.maxVc[r.L1] = r.V; setarg(A.argVc[r.L1], lam, mu, nu); }
    if (r.six_a1 >= 0 && r.six_a1 < 64) A.hist[r.six_a1]++;
    if (r.V >= 100 && r.six_a1 < A.minBig) { A.minBig = r.six_a1; A.minBigV = r.V; setarg(A.argminBig, lam, mu, nu); }
    if (r.six_a1 < 0) {
        A.neg++;
        for (int i=0;i<4;i++) A.hits.push_back(lam[i]);
        for (int i=0;i<4;i++) A.hits.push_back(mu[i]);
        for (int i=0;i<4;i++) A.hits.push_back(nu[i]);
        A.hits.push_back(r.L1); A.hits.push_back(r.L2); A.hits.push_back(r.L3);
        A.hits.push_back(r.six_a1); A.hits.push_back(r.V);
    }
}

static void merge(Acc &G, const Acc &L) {
    G.tested += L.tested; G.pruned += L.pruned; G.nonempty += L.nonempty;
    G.dim3 += L.dim3; G.neg += L.neg;
    if (L.min6a1 < G.min6a1) { G.min6a1 = L.min6a1; G.min6a1_V = L.min6a1_V; memcpy(G.argmin, L.argmin, sizeof(G.argmin)); }
    if (L.maxV > G.maxV) { G.maxV = L.maxV; memcpy(G.argmaxV, L.argmaxV, sizeof(G.argmaxV)); }
    if (L.maxV_h1z > G.maxV_h1z) { G.maxV_h1z = L.maxV_h1z; memcpy(G.argmaxV_h1z, L.argmaxV_h1z, sizeof(G.argmaxV_h1z)); }
    if (L.maxh2 > G.maxh2) { G.maxh2 = L.maxh2; memcpy(G.argmaxh2, L.argmaxh2, sizeof(G.argmaxh2)); }
    for (int k = 0; k < Acc::CB; k++) if (L.maxVc[k] > G.maxVc[k]) { G.maxVc[k] = L.maxVc[k]; memcpy(G.argVc[k], L.argVc[k], sizeof(G.argVc[k])); }
    for (int k = 0; k < 64; k++) G.hist[k] += L.hist[k];
    if (L.minBig < G.minBig) { G.minBig = L.minBig; G.minBigV = L.minBigV; memcpy(G.argminBig, L.argminBig, sizeof(G.argminBig)); }
    for (size_t i = 0; i < L.hits.size(); i++) G.hits.push_back(L.hits[i]);
}

static void pr_arg(const char *tag, const ll *a) {
    printf("%s lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld)\n",
           tag, a[0],a[1],a[2],a[3], a[4],a[5],a[6],a[7], a[8],a[9],a[10],a[11]);
}

static void report(const char *tag, const Acc &G) {
    printf("[%s] tested=%lld pruned_contain=%lld nonempty=%lld dim3=%lld NEG=%lld\n",
           tag, G.tested, G.pruned, G.nonempty, G.dim3, G.neg);
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
    }
    for (size_t i = 0; i + 16 <= G.hits.size(); i += 17) {
        const ll *h = &G.hits[i];
        printf("[%s] HIT lam=(%lld,%lld,%lld,%lld) mu=(%lld,%lld,%lld,%lld) nu=(%lld,%lld,%lld,%lld) L=(%lld,%lld,%lld) 6a1=%lld V=%lld\n",
               tag, h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11],h[12],h[13],h[14],h[15],h[16]);
    }
    fflush(stdout);
}

// --------------------------------------------------------------------------
//  MODES
// --------------------------------------------------------------------------

// exhaustive over ALL ordered splits (lam,mu) of a FIXED nu
static Acc nusplits(const ll nu[4], bool verbose) {
    ll W = nu[0] + nu[1] + nu[2] + nu[3];
    Acc G;
    std::vector< std::vector<P4> > byweight(W + 1);
    for (ll A = 0; A <= W; A++) gen_parts(A, nu[0], byweight[A]);
#pragma omp parallel
    {
        Acc L;
#pragma omp for schedule(dynamic, 1)
        for (ll A = 0; A <= W; A++) {
            const std::vector<P4> &LA = byweight[A];
            const std::vector<P4> &MB = byweight[W - A];
            for (size_t i = 0; i < LA.size(); i++) {
                if (!contained(LA[i].p, nu)) { L.tested += MB.size(); L.pruned += MB.size(); continue; }
                for (size_t j = 0; j < MB.size(); j++) {
                    if (!contained(MB[j].p, nu)) { L.tested++; L.pruned++; continue; }
                    Res r = eval_triple(LA[i].p, MB[j].p, nu);
                    feed(L, LA[i].p, MB[j].p, nu, r);
                }
            }
        }
#pragma omp critical
        merge(G, L);
    }
    if (verbose) {
        char tag[128];
        snprintf(tag, sizeof(tag), "nu=%lld,%lld,%lld,%lld", nu[0],nu[1],nu[2],nu[3]);
        report(tag, G);
    }
    return G;
}

// exhaustive over ALL triples at a fixed weight W:  every nu with at most 4
// parts and |nu| = W, and every ordered split (lam,mu) with at most 4 parts
// each and |lam|+|mu| = W.  Parallelised over the (nu, |lam|) task grid.
static Acc wexh(ll W) {
    std::vector<P4> NUS; gen_parts(W, W, NUS);
    std::vector< std::vector<P4> > byweight(W + 1);
    for (ll A = 0; A <= W; A++) gen_parts(A, W, byweight[A]);
    ll NT = (ll)NUS.size() * (W + 1);
    Acc G;
#pragma omp parallel
    {
        Acc L;
#pragma omp for schedule(dynamic, 1)
        for (ll task = 0; task < NT; task++) {
            ll k = task / (W + 1), A = task % (W + 1);
            const ll *nu = NUS[k].p;
            const std::vector<P4> &LA = byweight[A];
            const std::vector<P4> &MB = byweight[W - A];
            for (size_t i = 0; i < LA.size(); i++) {
                if (!contained(LA[i].p, nu)) { L.tested += MB.size(); L.pruned += MB.size(); continue; }
                for (size_t j = 0; j < MB.size(); j++) {
                    if (!contained(MB[j].p, nu)) { L.tested++; L.pruned++; continue; }
                    Res r = eval_triple(LA[i].p, MB[j].p, nu);
                    feed(L, LA[i].p, MB[j].p, nu, r);
                }
            }
        }
#pragma omp critical
        merge(G, L);
    }
    char tag[64]; snprintf(tag, sizeof(tag), "W%lld-EXHAUSTIVE-nu%zu", W, NUS.size());
    report(tag, G);
    return G;
}

// randomized hill-climb maximizing V within the band
static void climbV(ll Wlo, ll Whi, ll restarts, unsigned long long seed0) {
    Acc G;
#pragma omp parallel
    {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        unsigned long long st = seed0 * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 7ULL;
        auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
        Acc L;
#pragma omp for schedule(dynamic, 1)
        for (ll rs = 0; rs < restarts; rs++) {
            ll W = Wlo + rnd(Whi - Wlo + 1);
            // random nu with 4 parts of weight W, random split
            ll lam[4], mu[4], nu[4];
            // build a random weakly-decreasing nu of weight W
            auto randparts = [&](ll S, ll out[4]) {
                ll x[3];
                for (int i = 0; i < 3; i++) x[i] = rnd(S + 1);
                std::sort(x, x + 3);
                ll q[4] = {x[0], x[1]-x[0], x[2]-x[1], S-x[2]};
                std::sort(q, q + 4);
                out[0]=q[3]; out[1]=q[2]; out[2]=q[1]; out[3]=q[0];
            };
            randparts(W, nu);
            ll A = rnd(W + 1);
            randparts(A, lam); randparts(W - A, mu);
            ll bestV = -1;
            for (int iter = 0; iter < 3000; iter++) {
                // neighbourhood: move one unit between two parts of lam (keeping |lam|),
                // between two parts of mu, or between lam and mu (keeping |lam|+|mu|=W),
                // or between two parts of nu.
                ll blam[4], bmu[4], bnu[4]; ll bV = bestV; bool improved = false;
                ll tl[4], tm[4], tn[4];
                for (int which = 0; which < 3; which++) {
                    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) {
                        if (i == j) continue;
                        memcpy(tl, lam, sizeof(tl)); memcpy(tm, mu, sizeof(tm)); memcpy(tn, nu, sizeof(tn));
                        ll *tgt = (which == 0) ? tl : (which == 1) ? tm : tn;
                        if (tgt[i] == 0) continue;
                        tgt[i]--; tgt[j]++;
                        std::sort(tl, tl+4); std::reverse(tl, tl+4);
                        std::sort(tm, tm+4); std::reverse(tm, tm+4);
                        std::sort(tn, tn+4); std::reverse(tn, tn+4);
                        if (!contained(tl, tn) || !contained(tm, tn)) continue;
                        Res r = eval_triple(tl, tm, tn);
                        feed(L, tl, tm, tn, r);
                        if (r.valid && r.V > bV) { bV = r.V; memcpy(blam,tl,sizeof(tl)); memcpy(bmu,tm,sizeof(tm)); memcpy(bnu,tn,sizeof(tn)); improved = true; }
                    }
                }
                // move a unit from lam to mu (and back)
                for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) {
                    for (int dir = 0; dir < 2; dir++) {
                        memcpy(tl, lam, sizeof(tl)); memcpy(tm, mu, sizeof(tm)); memcpy(tn, nu, sizeof(tn));
                        if (dir == 0) { if (tl[i] == 0) continue; tl[i]--; tm[j]++; }
                        else { if (tm[i] == 0) continue; tm[i]--; tl[j]++; }
                        std::sort(tl, tl+4); std::reverse(tl, tl+4);
                        std::sort(tm, tm+4); std::reverse(tm, tm+4);
                        if (!contained(tl, tn) || !contained(tm, tn)) continue;
                        Res r = eval_triple(tl, tm, tn);
                        feed(L, tl, tm, tn, r);
                        if (r.valid && r.V > bV) { bV = r.V; memcpy(blam,tl,sizeof(tl)); memcpy(bmu,tm,sizeof(tm)); memcpy(bnu,tn,sizeof(tn)); improved = true; }
                    }
                }
                if (!improved) break;
                memcpy(lam, blam, sizeof(lam)); memcpy(mu, bmu, sizeof(mu)); memcpy(nu, bnu, sizeof(nu));
                bestV = bV;
            }
        }
#pragma omp critical
        merge(G, L);
    }
    report("CLIMB-V", G);
}

// For each nu of weight W, hill-climb over SPLITS (lam,mu) only, maximizing V.
// Prints "V nu1 nu2 nu3 nu4" for every nu, sorted descending -- this is the
// steering step that selects the "best nu shapes" for exhaustive splitting.
static void nutop(ll W, ll restarts, unsigned long long seed0) {
    std::vector<P4> NUS; gen_parts(W, W, NUS);
    std::vector<ll> bestV(NUS.size(), -1);
    std::vector<ll> bestL(NUS.size() * 8, 0);
    Acc G;
#pragma omp parallel
    {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        unsigned long long st = seed0 * 0x2545F4914F6CDD1DULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 99ULL;
        auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
        Acc L;
#pragma omp for schedule(dynamic, 4)
        for (long long k = 0; k < (long long)NUS.size(); k++) {
            const ll *nu = NUS[k].p;
            ll bV = -1; ll bl[4] = {0,0,0,0}, bm[4] = {0,0,0,0};
            for (ll rs = 0; rs < restarts; rs++) {
                ll lam[4], mu[4];
                for (int i = 0; i < 4; i++) { ll t = rnd(nu[i] + 1); lam[i] = t; mu[i] = nu[i] - t; }
                std::sort(lam, lam+4); std::reverse(lam, lam+4);
                std::sort(mu, mu+4); std::reverse(mu, mu+4);
                ll cur = -1;
                for (int iter = 0; iter < 400; iter++) {
                    bool improved = false; ll nl[4], nm[4], tl[4], tm[4];
                    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) for (int dir = 0; dir < 2; dir++) {
                        memcpy(tl, lam, sizeof(tl)); memcpy(tm, mu, sizeof(tm));
                        if (dir == 0) { if (tl[i] == 0) continue; tl[i]--; tm[j]++; }
                        else { if (tm[i] == 0) continue; tm[i]--; tl[j]++; }
                        std::sort(tl, tl+4); std::reverse(tl, tl+4);
                        std::sort(tm, tm+4); std::reverse(tm, tm+4);
                        if (!contained(tl, nu) || !contained(tm, nu)) continue;
                        Res r = eval_triple(tl, tm, nu);
                        feed(L, tl, tm, nu, r);
                        if (r.valid && r.V > cur) { cur = r.V; memcpy(nl,tl,sizeof(tl)); memcpy(nm,tm,sizeof(tm)); improved = true; }
                    }
                    if (!improved) break;
                    memcpy(lam, nl, sizeof(lam)); memcpy(mu, nm, sizeof(mu));
                }
                if (cur > bV) { bV = cur; memcpy(bl, lam, sizeof(bl)); memcpy(bm, mu, sizeof(bm)); }
            }
            bestV[k] = bV;
            for (int i = 0; i < 4; i++) { bestL[k*8+i] = bl[i]; bestL[k*8+4+i] = bm[i]; }
        }
#pragma omp critical
        merge(G, L);
    }
    std::vector<size_t> ord(NUS.size());
    for (size_t i = 0; i < ord.size(); i++) ord[i] = i;
    std::sort(ord.begin(), ord.end(), [&](size_t a, size_t b) { return bestV[a] > bestV[b]; });
    printf("NUTOP W=%lld nu_shapes=%zu\n", W, NUS.size());
    for (size_t t = 0; t < ord.size() && t < 25; t++) {
        size_t k = ord[t];
        printf("  V=%lld nu=%lld,%lld,%lld,%lld  bestlam=%lld,%lld,%lld,%lld bestmu=%lld,%lld,%lld,%lld\n",
               bestV[k], NUS[k].p[0], NUS[k].p[1], NUS[k].p[2], NUS[k].p[3],
               bestL[k*8],bestL[k*8+1],bestL[k*8+2],bestL[k*8+3],
               bestL[k*8+4],bestL[k*8+5],bestL[k*8+6],bestL[k*8+7]);
    }
    char tag[64]; snprintf(tag, sizeof(tag), "NUTOP-W%lld", W);
    report(tag, G);
}


// Uniform random census of the band: nu drawn uniformly from the compositions
// of W into 4 nonnegative parts (then sorted), split drawn uniformly per part.
// This is an unbiased-by-construction probe of the band interior; it decides
// nothing by itself, it only supplies statistics.
static void randband(ll Wlo, ll Whi, ll N, unsigned long long seed0) {
    Acc G;
#pragma omp parallel
    {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL;
        auto rnd = [&](ll m) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (ll)(st % (unsigned long long)m); };
        Acc L;
#pragma omp for schedule(dynamic, 8192)
        for (ll it = 0; it < N; it++) {
            ll W = Wlo + rnd(Whi - Wlo + 1);
            ll x[3]; for (int i = 0; i < 3; i++) x[i] = rnd(W + 1);
            std::sort(x, x + 3);
            ll q[4] = {x[0], x[1]-x[0], x[2]-x[1], W-x[2]};
            std::sort(q, q + 4);
            ll nu[4] = {q[3], q[2], q[1], q[0]};
            ll lam[4], mu[4];
            for (int i = 0; i < 4; i++) { ll t = rnd(nu[i] + 1); lam[i] = t; mu[i] = nu[i] - t; }
            std::sort(lam, lam+4); std::reverse(lam, lam+4);
            std::sort(mu, mu+4); std::reverse(mu, mu+4);
            if (!contained(lam, nu) || !contained(mu, nu)) { L.tested++; L.pruned++; continue; }
            Res r = eval_triple(lam, mu, nu);
            feed(L, lam, mu, nu, r);
        }
#pragma omp critical
        merge(G, L);
    }
    report("RANDBAND", G);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: bandscan --one l1 l2 l3 l4 m1..m4 n1..n4 | --nu n1 n2 n3 n4 | --wexh W | --climbv Wlo Whi RESTARTS SEED\n"); return 2; }
    if (!strcmp(argv[1], "--one")) {
        ll lam[4], mu[4], nu[4];
        for (int i=0;i<4;i++){ lam[i]=atoll(argv[2+i]); mu[i]=atoll(argv[6+i]); nu[i]=atoll(argv[10+i]); }
        Res r = eval_triple(lam, mu, nu);
        printf("valid=%d L1=%lld L2=%lld L3=%lld 6a1=%lld V=%lld hstar=(1,%lld,%lld,%lld)\n",
               (int)r.valid, r.L1, r.L2, r.L3, r.six_a1, r.V, r.h1, r.h2, r.h3);
        return 0;
    }
    if (!strcmp(argv[1], "--nu")) {
        ll nu[4]; for (int i=0;i<4;i++) nu[i]=atoll(argv[2+i]);
        nusplits(nu, true);
        return 0;
    }
    if (!strcmp(argv[1], "--wexh")) { wexh(atoll(argv[2])); return 0; }
    if (!strcmp(argv[1], "--rand")) { randband(atoll(argv[2]), atoll(argv[3]), atoll(argv[4]), argc>5?strtoull(argv[5],0,10):20260721ULL); return 0; }
    if (!strcmp(argv[1], "--nutop")) {
        nutop(atoll(argv[2]), argc > 3 ? atoll(argv[3]) : 3, argc > 4 ? strtoull(argv[4],0,10) : 20260721ULL);
        return 0;
    }
    if (!strcmp(argv[1], "--climbv")) {
        climbV(atoll(argv[2]), atoll(argv[3]), atoll(argv[4]), argc > 5 ? strtoull(argv[5],0,10) : 20260721ULL);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 2;
}
