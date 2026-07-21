// band4.cpp -- EXHAUSTIVE weight-band census of the r = 4 hive cell.
//
// For every weight W in [WLO, WHI] this enumerates EVERY triple of partitions
//   nu  |- W      with at most 4 parts,
//   lam |- a      with at most 4 parts,
//   mu  |- W-a    with at most 4 parts,     a = 0..W
// (so |lam|+|mu| = |nu| = W, the full KTT admissibility condition for r = 4;
// partitions with more than 4 parts cannot occur since c(nu;lam,mu) != 0 forces
// l(lam), l(mu) <= l(nu) <= 4 once nu has at most 4 parts, and nu with more than
// 4 parts is outside the r = 4 cell by definition).
//
// NO symmetry reduction is applied: every ORDERED triple is evaluated, so the
// reported count is the plain exhaustive count.
//
// For each triple it computes, in EXACT integer arithmetic:
//   L(1), L(2), L(3) = #( n Q(lam,mu,nu) cap Z^3 )   by direct integer fibre count
// and, since P(n) = c(n nu; n lam, n mu) = L(n) is a polynomial of degree
// dim Q <= 3 with L(0) = 1 (Knutson-Tao + Derksen-Weyman/KTT),
//   6 a1 = -11 + 18 L1 -  9 L2 + 2 L3
//   2 a2 =  +2 -  5 L1 +  4 L2 -   L3        (i.e. a2 = (D2 - D3)/2)
//   6 a3 =  -1 +  3 L1 -  3 L2 +   L3 = V    (normalized volume)
//   h*_1 = L1 - 4,  h*_2 = L2 - 4 L1 + 6,  h*_3 = L3 - 4 L2 + 6 L1 - 4
// deg P = dim Q, so dim = 3 if a3 != 0 else 2 if a2 != 0 else 1 if a1 != 0 else 0.
//
// All arithmetic is integer (long long).  There is no floating point anywhere in
// the decision path.
//
// Build:  clang++ -O3 -march=native -fopenmp -o band4.exe band4.cpp
// Usage:  band4.exe WLO WHI [--out FILE]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <array>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>

typedef long long ll;

struct Row { int s, q, r; ll rhs; };   // s*x + q*u + r*v <= rhs

// ---------------------------------------------------------------------------
// the 18 rhombus rows for r = 4, in the unimodular coords (x,u,v) =
// (h11, h12-h11, h21-h11).  Identical construction to gapscan.cpp / hive4.py.
// Boundary: B(0,y)=lam_1+..+lam_y ; B(x,4-x)=|lam|+mu_1+..+mu_x ; B(x,0)=nu_1+..+nu_x
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

// ---------------------------------------------------------------------------
struct Rec {
    ll lam[4], mu[4], nu[4];
    ll L1, L2, L3, six_a1, two_a2, V;
    int dim;
};

static std::string pstr(const ll p[4]) {
    char buf[128]; int n = 0;
    n += snprintf(buf + n, sizeof(buf) - n, "[");
    bool first = true;
    for (int i = 0; i < 4; i++) { if (p[i] == 0) continue; n += snprintf(buf + n, sizeof(buf) - n, "%s%lld", first ? "" : ",", p[i]); first = false; }
    n += snprintf(buf + n, sizeof(buf) - n, "]");
    return std::string(buf);
}

struct Acc {
    ll nonempty = 0;
    ll dimhist[5] = {0, 0, 0, 0, 0};   // index 0..3 for dim, 4 = empty
    ll min6a1 = (1LL << 62); Rec argmin6a1;          // over dim >= 1 (non-constant P)
    ll min6a1_d3 = (1LL << 62); Rec argmin6a1_d3;    // over dim == 3 only
    ll maxV = -1; Rec argmaxV;
    ll maxVh1 = -1; Rec argmaxVh1;     // among h*_1 = 0 (L1 = dim+1)
    ll maxH2 = -(1LL << 62); Rec argmaxH2;
    std::vector<Rec> negs;
    std::vector<Rec> lowa1;            // every dim-3 triple with 6a1 <= 12 (a1 <= 2)
    ll dim1_minlen = (1LL << 62);
    ll a1hist_d3[64] = {0};            // dim-3 count by 6a1 value, 0..63
    ll h1zero_d3 = 0;                  // dim-3 triples with h*_1 = 0 (L1 = 4)
};

static void merge(Acc &A, const Acc &B) {
    A.nonempty += B.nonempty;
    for (int i = 0; i < 5; i++) A.dimhist[i] += B.dimhist[i];
    if (B.min6a1 < A.min6a1) { A.min6a1 = B.min6a1; A.argmin6a1 = B.argmin6a1; }
    if (B.min6a1_d3 < A.min6a1_d3) { A.min6a1_d3 = B.min6a1_d3; A.argmin6a1_d3 = B.argmin6a1_d3; }
    if (B.maxV > A.maxV) { A.maxV = B.maxV; A.argmaxV = B.argmaxV; }
    if (B.maxVh1 > A.maxVh1) { A.maxVh1 = B.maxVh1; A.argmaxVh1 = B.argmaxVh1; }
    if (B.maxH2 > A.maxH2) { A.maxH2 = B.maxH2; A.argmaxH2 = B.argmaxH2; }
    if (B.dim1_minlen < A.dim1_minlen) A.dim1_minlen = B.dim1_minlen;
    for (int i = 0; i < 64; i++) A.a1hist_d3[i] += B.a1hist_d3[i];
    A.h1zero_d3 += B.h1zero_d3;
    for (const Rec &r : B.negs) A.negs.push_back(r);
    for (const Rec &r : B.lowa1) if (A.lowa1.size() < 4000) A.lowa1.push_back(r);
}

// all partitions of a into at most 4 parts
static void gen_parts(int a, std::vector<std::array<ll, 4> > &out) {
    out.clear();
    for (int p1 = a; p1 >= 0; p1--) {
        if (p1 == 0) { if (a == 0) { std::array<ll, 4> z = {0, 0, 0, 0}; out.push_back(z); } break; }
        for (int p2 = std::min(p1, a - p1); p2 >= 0; p2--) {
            int rem2 = a - p1 - p2;
            if (rem2 < 0) continue;
            for (int p3 = std::min(p2, rem2); p3 >= 0; p3--) {
                int p4 = rem2 - p3;
                if (p4 < 0 || p4 > p3) continue;
                std::array<ll, 4> t = {(ll)p1, (ll)p2, (ll)p3, (ll)p4};
                out.push_back(t);
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: band4 WLO WHI [--out FILE]\n"); return 2; }
    // --one "l1,l2,l3,l4" "m1,.." "n1,.."  -> single-triple evaluation (validation hook)
    if (!strcmp(argv[1], "--one")) {
        ll lam[4] = {0, 0, 0, 0}, mu[4] = {0, 0, 0, 0}, nu[4] = {0, 0, 0, 0};
        ll *tgt[3] = {lam, mu, nu};
        for (int k = 0; k < 3; k++) {
            char buf[256]; strncpy(buf, argv[2 + k], sizeof(buf) - 1); buf[sizeof(buf) - 1] = 0;
            int i = 0; char *tok = strtok(buf, ",");
            while (tok && i < 4) { tgt[k][i++] = atoll(tok); tok = strtok(NULL, ","); }
        }
        Row R[24];
        int nr = build_rows(lam, mu, nu, R);
        if (nr < 0) { printf("EMPTY boundary\n"); return 0; }
        ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
        if (ulo > uhi || vlo > vhi) { printf("EMPTY box\n"); return 0; }
        ll L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
        ll L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
        ll L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
        ll L4 = lattice_count(R, nr, 4, ulo, uhi, vlo, vhi);
        ll L5 = lattice_count(R, nr, 5, ulo, uhi, vlo, vhi);
        ll six_a1 = -11 + 18 * L1 - 9 * L2 + 2 * L3;
        ll V = L3 - 3 * L2 + 3 * L1 - 1;
        ll two_a2 = 2 - 5 * L1 + 4 * L2 - L3;
        int dim = L1 == 0 ? -1 : (V != 0) ? 3 : (two_a2 != 0) ? 2 : (six_a1 != 0) ? 1 : 0;
        printf("L=%lld,%lld,%lld,%lld,%lld six_a1=%lld two_a2=%lld V=%lld dim=%d\n",
               L1, L2, L3, L4, L5, six_a1, two_a2, V, dim);
        return 0;
    }
    // --dumphi W VMIN [MAX] : list dim-3 triples of weight W with V >= VMIN
    if (!strcmp(argv[1], "--dumphi")) {
        int W = atoi(argv[2]); ll VMIN = atoll(argv[3]);
        int MAXOUT = (argc > 4) ? atoi(argv[4]) : 20;
        std::vector<std::vector<std::array<ll, 4> > > PT(W + 1);
        for (int a = 0; a <= W; a++) gen_parts(a, PT[a]);
        int shown = 0;
        for (size_t ni = 0; ni < PT[W].size() && shown < MAXOUT; ni++) {
            const std::array<ll, 4> &nu = PT[W][ni];
            for (int a = 0; a <= W && shown < MAXOUT; a++)
                for (size_t li = 0; li < PT[a].size() && shown < MAXOUT; li++)
                    for (size_t mi = 0; mi < PT[W - a].size() && shown < MAXOUT; mi++) {
                        const std::array<ll, 4> &lam = PT[a][li];
                        const std::array<ll, 4> &mu = PT[W - a][mi];
                        Row R[24];
                        int nr = build_rows(lam.data(), mu.data(), nu.data(), R);
                        if (nr < 0) continue;
                        ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
                        if (ulo > uhi || vlo > vhi) continue;
                        ll L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
                        if (L1 == 0) continue;
                        ll L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
                        ll L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
                        ll V = L3 - 3 * L2 + 3 * L1 - 1;
                        if (V < VMIN) continue;
                        printf("%lld,%lld,%lld,%lld;%lld,%lld,%lld,%lld;%lld,%lld,%lld,%lld L=%lld,%lld,%lld V=%lld 6a1=%lld\n",
                               lam[0], lam[1], lam[2], lam[3], mu[0], mu[1], mu[2], mu[3],
                               nu[0], nu[1], nu[2], nu[3], L1, L2, L3, V, -11 + 18 * L1 - 9 * L2 + 2 * L3);
                        shown++;
                    }
        }
        return 0;
    }
    int WLO = atoi(argv[1]), WHI = atoi(argv[2]);
    const char *outf = 0;
    for (int i = 3; i < argc; i++) if (!strcmp(argv[i], "--out") && i + 1 < argc) outf = argv[i + 1];

    FILE *fo = outf ? fopen(outf, "w") : stdout;
    Acc GLOB;
    ll grand_triples = 0;

    for (int W = WLO; W <= WHI; W++) {
        // partition tables
        std::vector<std::vector<std::array<ll, 4> > > PT(W + 1);
        for (int a = 0; a <= W; a++) gen_parts(a, PT[a]);
        const std::vector<std::array<ll, 4> > &NUS = PT[W];
        ll ntrip = 0;
        for (int a = 0; a <= W; a++) ntrip += (ll)PT[a].size() * (ll)PT[W - a].size();
        ntrip *= (ll)NUS.size();
        grand_triples += ntrip;

        Acc WA;
        int nnu = (int)NUS.size();
        std::atomic<int> next(0);
        std::mutex mtx;
        unsigned nth = std::thread::hardware_concurrency();
        if (nth == 0) nth = 1;
        if ((int)nth > nnu) nth = (unsigned)nnu;
        std::vector<std::thread> ths;
        for (unsigned t = 0; t < nth; t++) ths.push_back(std::thread([&]() {
            Acc LA;
            for (;;) {
                int ni = next.fetch_add(1);
                if (ni >= nnu) break;
                const std::array<ll, 4> &nu = NUS[ni];
                for (int a = 0; a <= W; a++) {
                    const std::vector<std::array<ll, 4> > &LS = PT[a];
                    const std::vector<std::array<ll, 4> > &MS = PT[W - a];
                    for (size_t li = 0; li < LS.size(); li++) {
                        const std::array<ll, 4> &lam = LS[li];
                        for (size_t mi = 0; mi < MS.size(); mi++) {
                            const std::array<ll, 4> &mu = MS[mi];
                            Row R[24];
                            int nr = build_rows(lam.data(), mu.data(), nu.data(), R);
                            if (nr < 0) { LA.dimhist[4]++; continue; }
                            ll ulo = lam[2], uhi = lam[1], vlo = nu[2], vhi = nu[1];
                            if (ulo > uhi || vlo > vhi) { LA.dimhist[4]++; continue; }
                            ll L1 = lattice_count(R, nr, 1, ulo, uhi, vlo, vhi);
                            if (L1 == 0) { LA.dimhist[4]++; continue; }
                            ll L2 = lattice_count(R, nr, 2, ulo, uhi, vlo, vhi);
                            ll L3 = lattice_count(R, nr, 3, ulo, uhi, vlo, vhi);
                            ll six_a1 = -11 + 18 * L1 - 9 * L2 + 2 * L3;
                            ll V = L3 - 3 * L2 + 3 * L1 - 1;          // 6*a3
                            ll two_a2 = 2 - 5 * L1 + 4 * L2 - L3;     // 2*a2
                            int dim = (V != 0) ? 3 : (two_a2 != 0) ? 2 : (six_a1 != 0) ? 1 : 0;
                            LA.nonempty++;
                            LA.dimhist[dim]++;
                            Rec rec;
                            for (int t = 0; t < 4; t++) { rec.lam[t] = lam[t]; rec.mu[t] = mu[t]; rec.nu[t] = nu[t]; }
                            rec.L1 = L1; rec.L2 = L2; rec.L3 = L3;
                            rec.six_a1 = six_a1; rec.two_a2 = two_a2; rec.V = V; rec.dim = dim;
                            if (dim >= 1 && six_a1 < LA.min6a1) { LA.min6a1 = six_a1; LA.argmin6a1 = rec; }
                            if (dim == 3 && six_a1 < LA.min6a1_d3) { LA.min6a1_d3 = six_a1; LA.argmin6a1_d3 = rec; }
                            if (V > LA.maxV) { LA.maxV = V; LA.argmaxV = rec; }
                            if (L1 == dim + 1 && V > LA.maxVh1) { LA.maxVh1 = V; LA.argmaxVh1 = rec; }
                            if (dim == 3) {
                                if (six_a1 >= 0 && six_a1 < 64) LA.a1hist_d3[six_a1]++;
                                if (L1 == 4) LA.h1zero_d3++;
                                ll h2 = L2 - 4 * L1 + 6;
                                if (h2 > LA.maxH2) { LA.maxH2 = h2; LA.argmaxH2 = rec; }
                            }
                            if (dim == 1 && six_a1 / 6 < LA.dim1_minlen) LA.dim1_minlen = six_a1 / 6;
                            if (six_a1 < 0 || two_a2 < 0 || V < 0) LA.negs.push_back(rec);
                            if (dim == 3 && six_a1 <= 12 && LA.lowa1.size() < 4000) LA.lowa1.push_back(rec);
                        }
                    }
                }
            }
            std::lock_guard<std::mutex> g(mtx);
            merge(WA, LA);
        }));
        for (auto &th : ths) th.join();
        merge(GLOB, WA);
        fprintf(fo, "W=%d triples=%lld nonempty=%lld dim0=%lld dim1=%lld dim2=%lld dim3=%lld min6a1=%lld min6a1_d3=%lld maxV=%lld maxV_h1zero=%lld maxH2=%lld NEG=%zu\n",
                W, ntrip, WA.nonempty, WA.dimhist[0], WA.dimhist[1], WA.dimhist[2], WA.dimhist[3],
                WA.min6a1, WA.min6a1_d3, WA.maxV, WA.maxVh1, WA.maxH2, WA.negs.size());
        fflush(fo);
    }

    fprintf(fo, "\n=== BAND [%d,%d] TOTALS ===\n", WLO, WHI);
    fprintf(fo, "triples=%lld nonempty=%lld empty=%lld\n", grand_triples, GLOB.nonempty, GLOB.dimhist[4]);
    fprintf(fo, "dim histogram: 0=%lld 1=%lld 2=%lld 3=%lld\n", GLOB.dimhist[0], GLOB.dimhist[1], GLOB.dimhist[2], GLOB.dimhist[3]);
    fprintf(fo, "min 6a1 = %lld  at lam=%s mu=%s nu=%s  (L=%lld,%lld,%lld dim=%d V=%lld)\n",
            GLOB.min6a1, pstr(GLOB.argmin6a1.lam).c_str(), pstr(GLOB.argmin6a1.mu).c_str(), pstr(GLOB.argmin6a1.nu).c_str(),
            GLOB.argmin6a1.L1, GLOB.argmin6a1.L2, GLOB.argmin6a1.L3, GLOB.argmin6a1.dim, GLOB.argmin6a1.V);
    fprintf(fo, "min 6a1 (dim3 only) = %lld  at lam=%s mu=%s nu=%s  (L=%lld,%lld,%lld V=%lld)\n",
            GLOB.min6a1_d3, pstr(GLOB.argmin6a1_d3.lam).c_str(), pstr(GLOB.argmin6a1_d3.mu).c_str(), pstr(GLOB.argmin6a1_d3.nu).c_str(),
            GLOB.argmin6a1_d3.L1, GLOB.argmin6a1_d3.L2, GLOB.argmin6a1_d3.L3, GLOB.argmin6a1_d3.V);
    fprintf(fo, "max V   = %lld  at lam=%s mu=%s nu=%s  (L=%lld,%lld,%lld 6a1=%lld)\n",
            GLOB.maxV, pstr(GLOB.argmaxV.lam).c_str(), pstr(GLOB.argmaxV.mu).c_str(), pstr(GLOB.argmaxV.nu).c_str(),
            GLOB.argmaxV.L1, GLOB.argmaxV.L2, GLOB.argmaxV.L3, GLOB.argmaxV.six_a1);
    fprintf(fo, "max V at h*_1=0 = %lld  at lam=%s mu=%s nu=%s  (L=%lld,%lld,%lld dim=%d 6a1=%lld)\n",
            GLOB.maxVh1, pstr(GLOB.argmaxVh1.lam).c_str(), pstr(GLOB.argmaxVh1.mu).c_str(), pstr(GLOB.argmaxVh1.nu).c_str(),
            GLOB.argmaxVh1.L1, GLOB.argmaxVh1.L2, GLOB.argmaxVh1.L3, GLOB.argmaxVh1.dim, GLOB.argmaxVh1.six_a1);
    fprintf(fo, "max h*_2 (dim3) = %lld at lam=%s mu=%s nu=%s (L=%lld,%lld,%lld V=%lld 6a1=%lld)\n",
            GLOB.maxH2, pstr(GLOB.argmaxH2.lam).c_str(), pstr(GLOB.argmaxH2.mu).c_str(), pstr(GLOB.argmaxH2.nu).c_str(),
            GLOB.argmaxH2.L1, GLOB.argmaxH2.L2, GLOB.argmaxH2.L3, GLOB.argmaxH2.V, GLOB.argmaxH2.six_a1);
    fprintf(fo, "min dim-1 lattice length = %lld\n", GLOB.dim1_minlen);
    fprintf(fo, "dim-3 triples with h*_1 = 0 (L1 = 4): %lld  (all of normalized volume <= %lld)\n",
            GLOB.h1zero_d3, GLOB.maxVh1);
    fprintf(fo, "dim-3 histogram of 6*a1 (value:count), 6a1 <= 63:\n");
    for (int i = 0; i < 64; i++) if (GLOB.a1hist_d3[i]) fprintf(fo, "  6a1=%d : %lld\n", i, GLOB.a1hist_d3[i]);
    fprintf(fo, "TRIPLES WITH ANY NEGATIVE COEFFICIENT: %zu\n", GLOB.negs.size());
    for (size_t i = 0; i < GLOB.negs.size() && i < 200; i++) {
        const Rec &r = GLOB.negs[i];
        fprintf(fo, "NEG %s;%s;%s L=%lld,%lld,%lld 6a1=%lld 2a2=%lld V=%lld dim=%d\n",
                pstr(r.lam).c_str(), pstr(r.mu).c_str(), pstr(r.nu).c_str(),
                r.L1, r.L2, r.L3, r.six_a1, r.two_a2, r.V, r.dim);
    }
    fprintf(fo, "LOW-a1 SAMPLES (6a1 <= 12), %zu shown:\n", GLOB.lowa1.size());
    for (size_t i = 0; i < GLOB.lowa1.size() && i < 400; i++) {
        const Rec &r = GLOB.lowa1[i];
        fprintf(fo, "LOW %s;%s;%s L=%lld,%lld,%lld 6a1=%lld V=%lld dim=%d\n",
                pstr(r.lam).c_str(), pstr(r.mu).c_str(), pstr(r.nu).c_str(),
                r.L1, r.L2, r.L3, r.six_a1, r.V, r.dim);
    }
    if (outf) fclose(fo);
    return 0;
}
