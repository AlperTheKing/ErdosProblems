// bandscan.cpp -- EXHAUSTIVE r=4 weight-band census for the KTT positivity hunt.
//
// For every weight W in [WMIN, WMAX] this enumerates EVERY triple of partitions
// (lam, mu, nu) with at most 4 parts each and |lam| + |mu| = |nu| = W, and
// computes -- exactly, in integers -- the stretched Littlewood-Richardson
// polynomial P(n) = c(n nu; n lam, n mu) = #(nQ cap Z^3) of the Knutson-Tao
// hive polytope Q(lam,mu,nu) (r = 4  =>  ambient dimension 3, the REEVE
// dimension), together with its coefficients and the h*-data.
//
// Reductions used, each a theorem (no heuristic pruning anywhere):
//   (S1) c(nu;lam,mu) = c(nu;mu,lam)  =>  P is symmetric in lam <-> mu, so only
//        unordered pairs {lam,mu} are evaluated.  The ordered census is the
//        image of this one under the swap.
//   (S2) c(nu;lam,mu) != 0  =>  lam subset nu and mu subset nu (containment of
//        Young diagrams).  So for lam not subset nu, P(n) = c(n nu; n lam, n mu)
//        = 0 for EVERY n (n lam subset n nu fails for every n >= 1), i.e.
//        P == 0, which has no negative coefficient.  Such triples are counted
//        as tested with dim = -1.
//   (S3) Knutson-Tao saturation: c(nu;lam,mu) = 0 => c(n nu;n lam,n mu) = 0 for
//        all n.  So L(1) = 0 => P == 0 and no further counting is needed.
//   (S4) Derksen-Weyman / Knutson-Tao: P is a POLYNOMIAL of degree <= dim Q <= 3.
//        Hence P is determined by L(0)=1, L(1), L(2), L(3), and
//           6 a3 = L3 - 3 L2 + 3 L1 - 1     (= normalized volume when dim = 3)
//           2 a2 = 2 - 5 L1 + 4 L2 - L3
//           6 a1 = -11 + 18 L1 - 9 L2 + 2 L3
//              a0 = 1.
//        (Independently re-verified against L(4), L(5) by --verify.)
//
// Lattice counting is done in the unimodular coordinates (x,u,v) =
// (h11, h12-h11, h21-h11), in which every rhombus row has coefficients in
// {0,+-1} and, for fixed integer (u,v), the x-fibre is an integer interval;
// u ranges over [lam3, lam2] and v over [nu3, nu2].  Pure integer arithmetic.
//
// Build: clang++ -O3 -march=native -fopenmp -o bandscan.exe bandscan.cpp
// Usage: bandscan WMIN WMAX [--out FILE] [--verify N SEED]

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

// ---------------------------------------------------------------------------
// build the 18 rhombus rows for r = 4 (boundary convention of hive4.py / eng A)
// ---------------------------------------------------------------------------
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
    auto add = [&](int p0x, int p0y, int p1x, int p1y, int m0x, int m0y, int m1x, int m1y) {
        ll co[3] = {0, 0, 0}; ll cst = 0;
        int px[2] = {p0x, p1x}, py[2] = {p0y, p1y}, mx[2] = {m0x, m1x}, my[2] = {m0y, m1y};
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
        if (x + y <= 2)               add(x + 1, y, x, y + 1, x, y, x + 1, y + 1);
        if (y >= 1 && x + y <= 3)     add(x, y, x + 1, y, x, y + 1, x + 1, y - 1);
        if (x >= 1 && x + y <= 3)     add(x, y, x, y + 1, x + 1, y, x - 1, y + 1);
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
    ll L1, L2, L3, L4, L5;
    ll six_a1, two_a2, six_a3;
    int dim;          // -1 empty, else deg P
    ll Vnorm;         // d! * a_d
    ll hstar1;        // L1 - (dim+1)
    bool zero;        // P == 0
};

static Res eval(const ll lam[4], const ll mu[4], const ll nu[4], int extra) {
    Res r; memset(&r, 0, sizeof(r)); r.zero = true; r.dim = -1;
    Row R[24];
    int nr = build_rows(lam, mu, nu, R);
    if (nr < 0) return r;
    ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
    if (ulo > uhi || vlo > vhi) return r;
    r.L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
    if (r.L1 == 0) return r;               // saturation => P == 0
    r.zero = false;
    r.L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
    r.L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
    r.six_a3 = r.L3 - 3 * r.L2 + 3 * r.L1 - 1;
    r.two_a2 = 2 - 5 * r.L1 + 4 * r.L2 - r.L3;
    r.six_a1 = -11 + 18 * r.L1 - 9 * r.L2 + 2 * r.L3;
    if (r.six_a3 != 0)      { r.dim = 3; r.Vnorm = r.six_a3; }
    else if (r.two_a2 != 0) { r.dim = 2; r.Vnorm = r.two_a2; }
    else if (r.six_a1 != 0) { r.dim = 1; r.Vnorm = r.six_a1 / 6; }
    else                    { r.dim = 0; r.Vnorm = 1; }
    r.hstar1 = r.L1 - (r.dim + 1);
    if (extra) {
        r.L4 = lattice_count(R, nr, 4, ulo, uhi, vlo, vhi);
        r.L5 = lattice_count(R, nr, 5, ulo, uhi, vlo, vhi);
    }
    return r;
}

// ---------------------------------------------------------------------------
// partition enumeration
// ---------------------------------------------------------------------------
struct P4 { int p[4]; };
static inline unsigned enc(const int p[4]) {
    return ((unsigned)p[0] << 21) | ((unsigned)p[1] << 14) | ((unsigned)p[2] << 7) | (unsigned)p[3];
}

static void gen_parts_le4(int W, std::vector<P4> &out) {
    out.clear();
    for (int a = W; a >= 1; a--) {
        if (a * 4 < W) break;
        int rem = W - a;
        for (int b = std::min(a, rem); b >= 0; b--) {
            int rem2 = rem - b;
            for (int c = std::min(b, rem2); c >= 0; c--) {
                int d = rem2 - c;
                if (d > c) continue;
                if (d < 0) continue;
                P4 q; q.p[0] = a; q.p[1] = b; q.p[2] = c; q.p[3] = d;
                out.push_back(q);
            }
        }
    }
    if (W == 0) { P4 q; q.p[0] = q.p[1] = q.p[2] = q.p[3] = 0; out.push_back(q); }
}

// all sub-partitions lam of nu (lam_i <= nu_i, weakly decreasing, 4 slots),
// bucketed by weight.
static void gen_parts_le4_pad(int k, std::vector<P4> &out) {
    gen_parts_le4(k, out);
}

static void gen_subparts(const int nu[4], std::vector<std::vector<P4>> &bucket) {
    int W = nu[0] + nu[1] + nu[2] + nu[3];
    bucket.assign(W + 1, std::vector<P4>());
    for (int a = 0; a <= nu[0]; a++)
        for (int b = 0; b <= std::min(a, nu[1]); b++)
            for (int c = 0; c <= std::min(b, nu[2]); c++)
                for (int d = 0; d <= std::min(c, nu[3]); d++) {
                    P4 q; q.p[0] = a; q.p[1] = b; q.p[2] = c; q.p[3] = d;
                    bucket[a + b + c + d].push_back(q);
                }
}

struct Acc {
    ll tested = 0, nonzero = 0, zero = 0;
    ll dimhist[5] = {0, 0, 0, 0, 0};   // index dim+1 : -1,0,1,2,3
    ll min6a1 = (1LL << 60); int min_lam[4] = {0}, min_mu[4] = {0}, min_nu[4] = {0}; ll min_L[3] = {0};
    ll min6a1d3 = (1LL << 60); int m3_lam[4] = {0}, m3_mu[4] = {0}, m3_nu[4] = {0}; ll m3_L[3] = {0};
    ll maxV = -1; int mv_lam[4] = {0}, mv_mu[4] = {0}, mv_nu[4] = {0}; ll mv_L[3] = {0};
    ll maxV_h0 = -1; int mh_lam[4] = {0}, mh_mu[4] = {0}, mh_nu[4] = {0}; ll mh_L[3] = {0};
    ll maxV_h0_any = -1; int ma_lam[4] = {0}, ma_mu[4] = {0}, ma_nu[4] = {0}; int ma_dim = 0;
    ll maxhstar2 = -(1LL << 60); int m2_lam[4] = {0}, m2_mu[4] = {0}, m2_nu[4] = {0};
    ll nneg = 0;
    ll audited = 0, audit_fail = 0, noncontained_nonzero = 0;
    ll n_d3_h1zero = 0, n_d3_h1zero_Vgt1 = 0;
    std::vector<std::string> negs;
};

static void merge(Acc &A, const Acc &B) {
    A.tested += B.tested; A.nonzero += B.nonzero; A.zero += B.zero; A.nneg += B.nneg;
    A.audited += B.audited; A.audit_fail += B.audit_fail; A.noncontained_nonzero += B.noncontained_nonzero;
    A.n_d3_h1zero += B.n_d3_h1zero; A.n_d3_h1zero_Vgt1 += B.n_d3_h1zero_Vgt1;
    for (int i = 0; i < 5; i++) A.dimhist[i] += B.dimhist[i];
    if (B.min6a1 < A.min6a1) { A.min6a1 = B.min6a1; memcpy(A.min_lam, B.min_lam, 16); memcpy(A.min_mu, B.min_mu, 16); memcpy(A.min_nu, B.min_nu, 16); memcpy(A.min_L, B.min_L, sizeof(A.min_L)); }
    if (B.min6a1d3 < A.min6a1d3) { A.min6a1d3 = B.min6a1d3; memcpy(A.m3_lam, B.m3_lam, 16); memcpy(A.m3_mu, B.m3_mu, 16); memcpy(A.m3_nu, B.m3_nu, 16); memcpy(A.m3_L, B.m3_L, sizeof(A.m3_L)); }
    if (B.maxV > A.maxV) { A.maxV = B.maxV; memcpy(A.mv_lam, B.mv_lam, 16); memcpy(A.mv_mu, B.mv_mu, 16); memcpy(A.mv_nu, B.mv_nu, 16); memcpy(A.mv_L, B.mv_L, sizeof(A.mv_L)); }
    if (B.maxV_h0 > A.maxV_h0) { A.maxV_h0 = B.maxV_h0; memcpy(A.mh_lam, B.mh_lam, 16); memcpy(A.mh_mu, B.mh_mu, 16); memcpy(A.mh_nu, B.mh_nu, 16); memcpy(A.mh_L, B.mh_L, sizeof(A.mh_L)); }
    if (B.maxV_h0_any > A.maxV_h0_any) { A.maxV_h0_any = B.maxV_h0_any; memcpy(A.ma_lam, B.ma_lam, 16); memcpy(A.ma_mu, B.ma_mu, 16); memcpy(A.ma_nu, B.ma_nu, 16); A.ma_dim = B.ma_dim; }
    if (B.maxhstar2 > A.maxhstar2) { A.maxhstar2 = B.maxhstar2; memcpy(A.m2_lam, B.m2_lam, 16); memcpy(A.m2_mu, B.m2_mu, 16); memcpy(A.m2_nu, B.m2_nu, 16); }
    for (size_t i = 0; i < B.negs.size(); i++) A.negs.push_back(B.negs[i]);
}

static std::string ps(const int p[4]) {
    char buf[64]; int n = 0; buf[0] = 0;
    for (int i = 0; i < 4; i++) if (p[i] > 0) n += snprintf(buf + n, 60 - n, "%s%d", n ? "," : "", p[i]);
    if (n == 0) return std::string("0");
    return std::string(buf);
}

int main(int argc, char **argv) {
    if (argc >= 2 && !strcmp(argv[1], "--one")) {
        // --one l1 l2 l3 l4 m1 m2 m3 m4 n1 n2 n3 n4
        ll lam[4], mu[4], nu[4];
        for (int i = 0; i < 4; i++) { lam[i] = atoll(argv[2 + i]); mu[i] = atoll(argv[6 + i]); nu[i] = atoll(argv[10 + i]); }
        Res r = eval(lam, mu, nu, 1);
        printf("{\"zero\":%d,\"dim\":%d,\"L\":[1,%lld,%lld,%lld,%lld,%lld],\"six_a1\":%lld,\"two_a2\":%lld,\"six_a3\":%lld,\"hstar1\":%lld}\n",
               (int)r.zero, r.dim, r.L1, r.L2, r.L3, r.L4, r.L5, r.six_a1, r.two_a2, r.six_a3, r.hstar1);
        return 0;
    }
    if (argc < 3) { fprintf(stderr, "usage: bandscan WMIN WMAX [--out FILE]\n"); return 2; }
    int WMIN = atoi(argv[1]), WMAX = atoi(argv[2]);
    const char *outfile = 0;
    int FULLAUDIT = 0;
    int NOFILTER = 0;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--out") && i + 1 < argc) outfile = argv[i + 1];
        if (!strcmp(argv[i], "--full")) FULLAUDIT = 1;
        if (!strcmp(argv[i], "--nofilter")) NOFILTER = 1;
    }

    // task list: (W, nu index)
    struct Task { int W; P4 nu; };
    std::vector<Task> tasks;
    for (int W = WMIN; W <= WMAX; W++) {
        std::vector<P4> nus; gen_parts_le4(W, nus);
        for (size_t i = 0; i < nus.size(); i++) { Task t; t.W = W; t.nu = nus[i]; tasks.push_back(t); }
    }
    fprintf(stderr, "tasks (nu count) = %zu\n", tasks.size());
    // sort tasks descending by expected cost so the long ones start first
    std::sort(tasks.begin(), tasks.end(), [](const Task &a, const Task &b) {
        ll ca = (ll)(a.nu.p[1] - a.nu.p[2] + 1) * (a.nu.p[0] + 1) * (a.nu.p[1] + 1);
        ll cb = (ll)(b.nu.p[1] - b.nu.p[2] + 1) * (b.nu.p[0] + 1) * (b.nu.p[1] + 1);
        return ca > cb;
    });

    Acc G;
    ll done = 0;
#pragma omp parallel
    {
        Acc L;
        std::vector<std::vector<P4>> bucket;
#pragma omp for schedule(dynamic, 1)
        for (long long ti = 0; ti < (long long)tasks.size(); ti++) {
            const Task &T = tasks[ti];
            int W = T.W;
            ll nu[4] = {T.nu.p[0], T.nu.p[1], T.nu.p[2], T.nu.p[3]};
            if (NOFILTER) {
                bucket.assign(W + 1, std::vector<P4>());
                for (int k = 0; k <= W; k++) gen_parts_le4_pad(k, bucket[k]);
            } else {
                gen_subparts(T.nu.p, bucket);
            }
            for (int k = 0; 2 * k <= W; k++) {
                const std::vector<P4> &A = bucket[k];
                const std::vector<P4> &B = bucket[W - k];
                if (A.empty() || B.empty()) continue;
                for (size_t i = 0; i < A.size(); i++) {
                    unsigned ea = enc(A[i].p);
                    ll lam[4] = {A[i].p[0], A[i].p[1], A[i].p[2], A[i].p[3]};
                    for (size_t j = 0; j < B.size(); j++) {
                        if (2 * k == W && enc(B[j].p) < ea) continue;  // unordered pairs
                        ll mu[4] = {B[j].p[0], B[j].p[1], B[j].p[2], B[j].p[3]};
                        L.tested++;
                        Res r = eval(lam, mu, nu, FULLAUDIT);
                        if (r.zero) { L.zero++; L.dimhist[0]++; continue; }
                        L.nonzero++;
                        {
                            bool cont = true;
                            for (int t = 0; t < 4; t++) if (lam[t] > nu[t] || mu[t] > nu[t]) cont = false;
                            if (!cont) L.noncontained_nonzero++;
                        }
                        if (FULLAUDIT) {
                            // P interpolated from L(0..3) must reproduce the
                            // independently counted L(4) and L(5).
                            ll p4 = -1 + 4 * r.L1 - 6 * r.L2 + 4 * r.L3;
                            ll p5 = -4 + 15 * r.L1 - 20 * r.L2 + 10 * r.L3;
                            L.audited++;
                            if (p4 != r.L4 || p5 != r.L5) L.audit_fail++;
                        }
                        L.dimhist[r.dim + 1]++;
                        if (r.six_a1 < L.min6a1) {
                            L.min6a1 = r.six_a1;
                            for (int t = 0; t < 4; t++) { L.min_lam[t] = (int)lam[t]; L.min_mu[t] = (int)mu[t]; L.min_nu[t] = (int)nu[t]; }
                            L.min_L[0] = r.L1; L.min_L[1] = r.L2; L.min_L[2] = r.L3;
                        }
                        if (r.dim == 3) {
                            if (r.six_a1 < L.min6a1d3) {
                                L.min6a1d3 = r.six_a1;
                                for (int t = 0; t < 4; t++) { L.m3_lam[t] = (int)lam[t]; L.m3_mu[t] = (int)mu[t]; L.m3_nu[t] = (int)nu[t]; }
                                L.m3_L[0] = r.L1; L.m3_L[1] = r.L2; L.m3_L[2] = r.L3;
                            }
                            if (r.six_a3 > L.maxV) {
                                L.maxV = r.six_a3;
                                for (int t = 0; t < 4; t++) { L.mv_lam[t] = (int)lam[t]; L.mv_mu[t] = (int)mu[t]; L.mv_nu[t] = (int)nu[t]; }
                                L.mv_L[0] = r.L1; L.mv_L[1] = r.L2; L.mv_L[2] = r.L3;
                            }
                            // h*_2 = L2 - 4 L1 + 6   (d = 3)
                            ll h2 = r.L2 - 4 * r.L1 + 6;
                            if (h2 > L.maxhstar2) {
                                L.maxhstar2 = h2;
                                for (int t = 0; t < 4; t++) { L.m2_lam[t] = (int)lam[t]; L.m2_mu[t] = (int)mu[t]; L.m2_nu[t] = (int)nu[t]; }
                            }
                            if (r.hstar1 == 0) { L.n_d3_h1zero++; if (r.six_a3 > 1) L.n_d3_h1zero_Vgt1++; }
                            if (r.hstar1 == 0 && r.six_a3 > L.maxV_h0) {
                                L.maxV_h0 = r.six_a3;
                                for (int t = 0; t < 4; t++) { L.mh_lam[t] = (int)lam[t]; L.mh_mu[t] = (int)mu[t]; L.mh_nu[t] = (int)nu[t]; }
                                L.mh_L[0] = r.L1; L.mh_L[1] = r.L2; L.mh_L[2] = r.L3;
                            }
                        }
                        if (r.hstar1 == 0 && r.Vnorm > L.maxV_h0_any) {
                            L.maxV_h0_any = r.Vnorm;
                            for (int t = 0; t < 4; t++) { L.ma_lam[t] = (int)lam[t]; L.ma_mu[t] = (int)mu[t]; L.ma_nu[t] = (int)nu[t]; }
                            L.ma_dim = r.dim;
                        }
                        if (r.six_a1 < 0 || r.two_a2 < 0 || r.six_a3 < 0) {
                            L.nneg++;
                            if (L.negs.size() < 500) {
                                char buf[512];
                                snprintf(buf, sizeof(buf), "%s;%s;%s|L=%lld,%lld,%lld|6a1=%lld|2a2=%lld|6a3=%lld|dim=%d",
                                         ps(A[i].p).c_str(), ps(B[j].p).c_str(), ps(T.nu.p).c_str(),
                                         r.L1, r.L2, r.L3, r.six_a1, r.two_a2, r.six_a3, r.dim);
                                L.negs.push_back(std::string(buf));
                            }
                        }
                    }
                }
            }
#pragma omp atomic
            done++;
            if ((done & 255) == 0) {
#pragma omp critical
                fprintf(stderr, "\r nu tasks done %lld / %zu   ", done, tasks.size());
            }
        }
#pragma omp critical
        merge(G, L);
    }
    fprintf(stderr, "\n");

    FILE *f = outfile ? fopen(outfile, "w") : stdout;
    fprintf(f, "{\n");
    fprintf(f, " \"band\": [%d,%d],\n", WMIN, WMAX);
    fprintf(f, " \"unordered_triples_tested\": %lld,\n", G.tested);
    fprintf(f, " \"nonzero\": %lld,\n", G.nonzero);
    fprintf(f, " \"identically_zero\": %lld,\n", G.zero);
    fprintf(f, " \"dim_histogram\": {\"-1\": %lld, \"0\": %lld, \"1\": %lld, \"2\": %lld, \"3\": %lld},\n",
            G.dimhist[0], G.dimhist[1], G.dimhist[2], G.dimhist[3], G.dimhist[4]);
    fprintf(f, " \"min_six_a1\": %lld,\n", G.min6a1);
    fprintf(f, " \"min_a1_triple\": \"%s;%s;%s\",\n", ps(G.min_lam).c_str(), ps(G.min_mu).c_str(), ps(G.min_nu).c_str());
    fprintf(f, " \"min_a1_L\": [%lld,%lld,%lld],\n", G.min_L[0], G.min_L[1], G.min_L[2]);
    fprintf(f, " \"min_six_a1_dim3\": %lld,\n", G.min6a1d3);
    fprintf(f, " \"min_a1_dim3_triple\": \"%s;%s;%s\",\n", ps(G.m3_lam).c_str(), ps(G.m3_mu).c_str(), ps(G.m3_nu).c_str());
    fprintf(f, " \"min_a1_dim3_L\": [%lld,%lld,%lld],\n", G.m3_L[0], G.m3_L[1], G.m3_L[2]);
    fprintf(f, " \"max_volume\": %lld,\n", G.maxV);
    fprintf(f, " \"max_volume_triple\": \"%s;%s;%s\",\n", ps(G.mv_lam).c_str(), ps(G.mv_mu).c_str(), ps(G.mv_nu).c_str());
    fprintf(f, " \"max_volume_L\": [%lld,%lld,%lld],\n", G.mv_L[0], G.mv_L[1], G.mv_L[2]);
    fprintf(f, " \"max_volume_hstar1_zero\": %lld,\n", G.maxV_h0);
    fprintf(f, " \"max_volume_hstar1_zero_triple\": \"%s;%s;%s\",\n", ps(G.mh_lam).c_str(), ps(G.mh_mu).c_str(), ps(G.mh_nu).c_str());
    fprintf(f, " \"max_volume_hstar1_zero_L\": [%lld,%lld,%lld],\n", G.mh_L[0], G.mh_L[1], G.mh_L[2]);
    fprintf(f, " \"max_volume_hstar1_zero_anydim\": %lld,\n", G.maxV_h0_any);
    fprintf(f, " \"max_volume_hstar1_zero_anydim_dim\": %d,\n", G.ma_dim);
    fprintf(f, " \"max_volume_hstar1_zero_anydim_triple\": \"%s;%s;%s\",\n", ps(G.ma_lam).c_str(), ps(G.ma_mu).c_str(), ps(G.ma_nu).c_str());
    fprintf(f, " \"max_hstar2\": %lld,\n", G.maxhstar2);
    fprintf(f, " \"max_hstar2_triple\": \"%s;%s;%s\",\n", ps(G.m2_lam).c_str(), ps(G.m2_mu).c_str(), ps(G.m2_nu).c_str());
    fprintf(f, " \"n_dim3_hstar1_zero\": %lld,\n", G.n_d3_h1zero);
    fprintf(f, " \"n_dim3_hstar1_zero_volume_gt_1\": %lld,\n", G.n_d3_h1zero_Vgt1);
    fprintf(f, " \"nofilter\": %d,\n", NOFILTER);
    fprintf(f, " \"noncontained_nonzero\": %lld,\n", G.noncontained_nonzero);
    fprintf(f, " \"full_audit\": %d,\n", FULLAUDIT);
    fprintf(f, " \"audited_L4_L5\": %lld,\n", G.audited);
    fprintf(f, " \"audit_failures\": %lld,\n", G.audit_fail);
    fprintf(f, " \"n_negative\": %lld,\n", G.nneg);
    fprintf(f, " \"negatives\": [");
    for (size_t i = 0; i < G.negs.size(); i++) fprintf(f, "%s\"%s\"", i ? ", " : "", G.negs[i].c_str());
    fprintf(f, "]\n}\n");
    if (outfile) fclose(f);
    return 0;
}
