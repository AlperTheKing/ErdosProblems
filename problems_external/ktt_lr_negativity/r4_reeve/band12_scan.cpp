// band12_scan.cpp -- exhaustive r=4 hive-polytope Ehrhart census (band 12).
//
// Mirrors E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/hive4.py
// EXACTLY: same boundary convention, same 18 rhombus rows, same integer lattice
// counting.  All arithmetic is exact 64-bit integer; no floating point anywhere.
//
// For each triple (lam,mu,nu), lam,mu,nu partitions with <= 4 parts,
// |lam|+|mu|=|nu|=W, lam,mu contained in nu (necessary for Q nonempty), it
// computes L(n) = #(nQ cap Z^3) for n = 0..5, the exact Ehrhart / stretched LR
// polynomial P (denominator 6), the h*-vector, the normalized volume, and flags
// any strictly negative coefficient.
//
// build: clang++ -O3 -march=native -std=c++17 band12_scan.cpp -o band12_scan.exe
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <climits>
#include <numeric>
#include <vector>
#include <array>
#include <string>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>
using namespace std;
typedef long long ll;

// ------------------------------------------------------------------ template
struct RowT {
    int co[3];          // interior coefficients (entries in {0,+-1})
    int nb;             // number of boundary terms
    int bp[8];          // boundary point index (5*x+y)
    int bs[8];          // +1 if the point sits on the "plus" side
};
static vector<RowT> ROWS;   // rows with co != 0   (18 of them)
static vector<RowT> CHKS;   // rows with co == 0   (pure boundary feasibility)

static inline int iidx(int x, int y) {
    if (x == 1 && y == 1) return 0;
    if (x == 1 && y == 2) return 1;
    if (x == 2 && y == 1) return 2;
    return -1;
}

static void addTemplate(int px[2], int py[2], int mx[2], int my[2]) {
    RowT r; memset(&r, 0, sizeof(r));
    for (int k = 0; k < 2; k++) {
        int i = iidx(px[k], py[k]);
        if (i >= 0) r.co[i] -= 1;
        else { r.bp[r.nb] = 5 * px[k] + py[k]; r.bs[r.nb] = +1; r.nb++; }
    }
    for (int k = 0; k < 2; k++) {
        int i = iidx(mx[k], my[k]);
        if (i >= 0) r.co[i] += 1;
        else { r.bp[r.nb] = 5 * mx[k] + my[k]; r.bs[r.nb] = -1; r.nb++; }
    }
    if (r.co[0] == 0 && r.co[1] == 0 && r.co[2] == 0) CHKS.push_back(r);
    else ROWS.push_back(r);
}

static void buildTemplate() {
    const int R = 4;
    for (int x = 0; x <= R; x++) for (int y = 0; y <= R; y++) {
        if (x + y <= R - 2) {            // (A)
            int px[2] = {x + 1, x}, py[2] = {y, y + 1};
            int mx[2] = {x, x + 1}, my[2] = {y, y + 1};
            addTemplate(px, py, mx, my);
        }
        if (y >= 1 && x + y <= R - 1) {  // (B)
            int px[2] = {x, x + 1}, py[2] = {y, y};
            int mx[2] = {x, x + 1}, my[2] = {y + 1, y - 1};
            addTemplate(px, py, mx, my);
        }
        if (x >= 1 && x + y <= R - 1) {  // (C)
            int px[2] = {x, x}, py[2] = {y, y + 1};
            int mx[2] = {x + 1, x - 1}, my[2] = {y, y + 1};
            addTemplate(px, py, mx, my);
        }
    }
}

// ------------------------------------------------------------------ polytope
struct Poly {           // Q = { h in Z^3 : co . h <= b }
    int  co[24][3];
    ll   b[24];
    int  n;
    int  i0[8], n0;     // rows with co[1]==0 && co[2]==0
    int  i1[8], n1;     // rows with co[1]!=0 && co[2]==0
    int  i2[24], n2;    // rows with co[2]!=0
};

// returns false if the pure-boundary rhombus checks already fail (Q empty)
static bool buildPoly(const int lam[4], const int mu[4], const int nu[4], Poly &P) {
    {   // |lam| + |mu| must equal |nu|  (same guard as hive4.build_hive4)
        ll a = 0, c = 0;
        for (int i = 0; i < 4; i++) { a += lam[i] + mu[i]; c += nu[i]; }
        if (a != c) return false;
    }
    ll B[25];
    for (int i = 0; i < 25; i++) B[i] = 0;
    ll s = 0;
    for (int y = 0; y <= 4; y++) { B[5 * 0 + y] = s; if (y < 4) s += lam[y]; }
    ll slam = 0; for (int i = 0; i < 4; i++) slam += lam[i];
    s = slam;
    for (int x = 0; x <= 4; x++) { B[5 * x + (4 - x)] = s; if (x < 4) s += mu[x]; }
    s = 0;
    for (int x = 0; x <= 4; x++) { B[5 * x + 0] = s; if (x < 4) s += nu[x]; }
    B[0] = 0;

    for (size_t k = 0; k < CHKS.size(); k++) {
        const RowT &r = CHKS[k];
        ll c = 0;
        for (int j = 0; j < r.nb; j++) c -= (ll)r.bs[j] * B[r.bp[j]];
        if (c > 0) return false;   // boundary_rhombus_violated
    }
    P.n = 0; P.n0 = 0; P.n1 = 0; P.n2 = 0;
    for (size_t k = 0; k < ROWS.size(); k++) {
        const RowT &r = ROWS[k];
        ll c = 0;
        for (int j = 0; j < r.nb; j++) c -= (ll)r.bs[j] * B[r.bp[j]];
        int i = P.n++;
        P.co[i][0] = r.co[0]; P.co[i][1] = r.co[1]; P.co[i][2] = r.co[2];
        P.b[i] = -c;
        if (r.co[1] == 0 && r.co[2] == 0) P.i0[P.n0++] = i;
        else if (r.co[2] == 0)            P.i1[P.n1++] = i;
        else                              P.i2[P.n2++] = i;
    }
    return true;
}

// exact #(n*Q cap Z^3);  all coefficients are in {0,+-1} so no division is used
static ll countLat(const Poly &P, int n) {
    if (n == 0) return 1;
    ll lo0 = LLONG_MIN / 4, hi0 = LLONG_MAX / 4;
    for (int k = 0; k < P.n0; k++) {
        int i = P.i0[k]; ll r = P.b[i] * n;
        if (P.co[i][0] > 0) { if (r < hi0) hi0 = r; }
        else                { if (-r > lo0) lo0 = -r; }
    }
    if (lo0 > hi0) return 0;
    ll total = 0;
    for (ll h0 = lo0; h0 <= hi0; h0++) {
        ll lo1 = LLONG_MIN / 4, hi1 = LLONG_MAX / 4;
        for (int k = 0; k < P.n1; k++) {
            int i = P.i1[k]; ll rem = P.b[i] * n - (ll)P.co[i][0] * h0;
            if (P.co[i][1] > 0) { if (rem < hi1) hi1 = rem; }
            else                { if (-rem > lo1) lo1 = -rem; }
        }
        if (lo1 > hi1) continue;
        for (ll h1 = lo1; h1 <= hi1; h1++) {
            ll lo2 = LLONG_MIN / 4, hi2 = LLONG_MAX / 4;
            for (int k = 0; k < P.n2; k++) {
                int i = P.i2[k];
                ll rem = P.b[i] * n - (ll)P.co[i][0] * h0 - (ll)P.co[i][1] * h1;
                if (P.co[i][2] > 0) { if (rem < hi2) hi2 = rem; }
                else                { if (-rem > lo2) lo2 = -rem; }
                if (lo2 > hi2) break;
            }
            if (lo2 <= hi2) total += hi2 - lo2 + 1;
        }
    }
    return total;
}

// ------------------------------------------------------------------ analysis
struct Res {
    ll L[6];
    ll c6[4];   // 6 * a_k , k = 0..3   (a_0 = 1)
    int deg;    // degree of trimmed P  ( = dim Q )
    ll hs[4];   // h*-vector (valid when deg == 3)
    ll V;       // normalized volume 3! * vol  ( = 6 a_3 )
    bool neg;
    bool verify_fail;
};

static void analyze(const Poly &P, Res &R, bool full) {
    R.L[0] = 1;
    R.L[1] = countLat(P, 1);
    R.L[2] = R.L[3] = R.L[4] = R.L[5] = -1;
    R.neg = false; R.verify_fail = false;
    R.V = 0; R.deg = -1;
    R.c6[0] = 6; R.c6[1] = R.c6[2] = R.c6[3] = 0;
    R.hs[0] = R.hs[1] = R.hs[2] = R.hs[3] = 0;
    (void)full;
    if (R.L[1] == 0) { R.deg = -1; return; }          // Q empty (saturation)
    R.L[2] = countLat(P, 2);
    R.L[3] = countLat(P, 3);
    ll d1 = R.L[1] - R.L[0];
    ll d2 = R.L[2] - R.L[1];
    ll d3 = R.L[3] - R.L[2];
    ll dd1 = d2 - d1, dd2 = d3 - d2;
    ll ddd = dd2 - dd1;
    R.c6[3] = ddd;
    R.c6[2] = 3 * dd1 - 3 * ddd;
    R.c6[1] = 6 * d1 - 3 * dd1 + 2 * ddd;
    R.deg = R.c6[3] ? 3 : (R.c6[2] ? 2 : (R.c6[1] ? 1 : 0));
    R.V = ddd;
    R.neg = (R.c6[1] < 0) || (R.c6[2] < 0) || (R.c6[3] < 0);
    R.hs[0] = 1;
    R.hs[1] = R.L[1] - 4;
    R.hs[2] = R.L[2] - 4 * R.L[1] + 6;
    R.hs[3] = R.L[3] - 4 * R.L[2] + 6 * R.L[1] - 4;
    // verification: the degree-3 fit through L(0..3) must also hit L(4), L(5)
    R.L[4] = countLat(P, 4);
    ll p4 = (R.c6[3] * 64 + R.c6[2] * 16 + R.c6[1] * 4 + R.c6[0]) / 6;
    ll r4 = (R.c6[3] * 64 + R.c6[2] * 16 + R.c6[1] * 4 + R.c6[0]) % 6;
    if (r4 != 0 || p4 != R.L[4]) R.verify_fail = true;
    if (R.deg == 3 || R.verify_fail) {
        R.L[5] = countLat(P, 5);
        ll s = R.c6[3] * 125 + R.c6[2] * 25 + R.c6[1] * 5 + R.c6[0];
        if (s % 6 != 0 || s / 6 != R.L[5]) R.verify_fail = true;
    }
}

// ------------------------------------------------------------------ band def
// band-12 degeneracy predicate:  empty, OR a repeated part (this covers all
// rectangles a^k, k>=2, and all columns 1^k, k>=2), OR a hook (a,1^k), k>=0
// (this covers all single rows and the column 1).
static inline bool degenerate(const int p[4]) {
    int len = 0; while (len < 4 && p[len] > 0) len++;
    if (len == 0) return true;                     // empty partition
    for (int i = 0; i + 1 < len; i++) if (p[i] == p[i + 1]) return true;  // repeated
    bool hook = true; for (int i = 1; i < len; i++) if (p[i] != 1) hook = false;
    if (hook) return true;                         // hook / row / column
    return false;
}

// strict as a length-4 vector:  p1 > p2 > p3 > p4 >= 0
static inline bool strict(const int p[4]) {
    return p[0] > p[1] && p[1] > p[2] && p[2] > p[3] && p[3] >= 0;
}

// ------------------------------------------------------------------- stats
struct Hit { int lam[4], mu[4], nu[4]; ll c6[4], L[6], hs[4], V; };
struct Stats {
    ll total = 0, band = 0, bandlm = 0;
    ll dimhist[6] = {0,0,0,0,0,0};          // index dim+1 : -1..3  (0..4)
    ll bdimhist[6] = {0,0,0,0,0,0};
    ll mina1 = LLONG_MAX;  int mla[4], mmu[4], mnu[4];   // over band, 6*a1
    ll minany = LLONG_MAX;
    ll mina1_full = LLONG_MAX; int Mla[4], Mmu[4], Mnu[4];
    ll maxV = -1;          int vla[4], vmu[4], vnu[4];
    ll maxV_full = -1;     int Vla[4], Vmu[4], Vnu[4];
    ll maxVh1 = -1;        int wla[4], wmu[4], wnu[4];
    ll maxVh1_full = -1;   int Wla[4], Wmu[4], Wnu[4];
    ll maxh2 = -1;         int hla[4], hmu[4], hnu[4];
    ll maxh2_full = -1;    int Hla[4], Hmu[4], Hnu[4];
    ll nverify_fail = 0;
    ll dim3_nonstrict = 0; int nsla[4], nsmu[4], nsnu[4];
    vector<Hit> hits;
    vector<Hit> anomalies;
};

static void mergeStats(Stats &A, const Stats &B) {
    A.total += B.total; A.band += B.band; A.bandlm += B.bandlm;
    for (int i = 0; i < 6; i++) { A.dimhist[i] += B.dimhist[i]; A.bdimhist[i] += B.bdimhist[i]; }
    if (B.mina1 < A.mina1) { A.mina1 = B.mina1; memcpy(A.mla,B.mla,16); memcpy(A.mmu,B.mmu,16); memcpy(A.mnu,B.mnu,16); }
    if (B.minany < A.minany) A.minany = B.minany;
    if (B.mina1_full < A.mina1_full) { A.mina1_full = B.mina1_full; memcpy(A.Mla,B.Mla,16); memcpy(A.Mmu,B.Mmu,16); memcpy(A.Mnu,B.Mnu,16); }
    if (B.maxV > A.maxV) { A.maxV = B.maxV; memcpy(A.vla,B.vla,16); memcpy(A.vmu,B.vmu,16); memcpy(A.vnu,B.vnu,16); }
    if (B.maxV_full > A.maxV_full) { A.maxV_full = B.maxV_full; memcpy(A.Vla,B.Vla,16); memcpy(A.Vmu,B.Vmu,16); memcpy(A.Vnu,B.Vnu,16); }
    if (B.maxVh1 > A.maxVh1) { A.maxVh1 = B.maxVh1; memcpy(A.wla,B.wla,16); memcpy(A.wmu,B.wmu,16); memcpy(A.wnu,B.wnu,16); }
    if (B.maxVh1_full > A.maxVh1_full) { A.maxVh1_full = B.maxVh1_full; memcpy(A.Wla,B.Wla,16); memcpy(A.Wmu,B.Wmu,16); memcpy(A.Wnu,B.Wnu,16); }
    if (B.maxh2 > A.maxh2) { A.maxh2 = B.maxh2; memcpy(A.hla,B.hla,16); memcpy(A.hmu,B.hmu,16); memcpy(A.hnu,B.hnu,16); }
    if (B.maxh2_full > A.maxh2_full) { A.maxh2_full = B.maxh2_full; memcpy(A.Hla,B.Hla,16); memcpy(A.Hmu,B.Hmu,16); memcpy(A.Hnu,B.Hnu,16); }
    A.nverify_fail += B.nverify_fail;
    if (B.dim3_nonstrict) { if (!A.dim3_nonstrict) { memcpy(A.nsla,B.nsla,16); memcpy(A.nsmu,B.nsmu,16); memcpy(A.nsnu,B.nsnu,16); } A.dim3_nonstrict += B.dim3_nonstrict; }
    for (auto &h : B.hits) A.hits.push_back(h);
    for (auto &h : B.anomalies) A.anomalies.push_back(h);
}

// -------------------------------------------------------------- enumeration
struct Task { int nu[4]; int W; };
static vector<Task> TASKS;
static atomic<size_t> NEXT(0);
static int  FULLMODE = 0;   // 1 -> also compute polynomials for L(1)==1 cases

static void enumSub(const int nu[4], vector<array<int,4>> *byW, int W) {
    int p[4];
    for (p[0] = 0; p[0] <= nu[0]; p[0]++)
      for (p[1] = 0; p[1] <= min(p[0], nu[1]); p[1]++)
        for (p[2] = 0; p[2] <= min(p[1], nu[2]); p[2]++)
          for (p[3] = 0; p[3] <= min(p[2], nu[3]); p[3]++) {
              int s = p[0] + p[1] + p[2] + p[3];
              if (s <= W) byW[s].push_back({p[0], p[1], p[2], p[3]});
          }
}

static void recordHit(vector<Hit> &v, const int lam[4], const int mu[4],
                      const int nu[4], const Res &R) {
    Hit h; memcpy(h.lam, lam, 16); memcpy(h.mu, mu, 16); memcpy(h.nu, nu, 16);
    for (int i = 0; i < 4; i++) { h.c6[i] = R.c6[i]; h.hs[i] = R.hs[i]; }
    for (int i = 0; i < 6; i++) h.L[i] = R.L[i];
    h.V = R.V;
    v.push_back(h);
}

static void worker(Stats *out) {
    Stats S;
    Poly P;
    Res R;
    for (;;) {
        size_t t = NEXT.fetch_add(1);
        if (t >= TASKS.size()) break;
        const Task &T = TASKS[t];
        int W = T.W;
        vector<array<int,4>> byW[61];
        enumSub(T.nu, byW, W);
        bool dnu = degenerate(T.nu);
        for (int a = 0; a <= W; a++) {
            int bwt = W - a;
            if (bwt < 0 || bwt > 60) continue;
            for (auto &lam : byW[a]) {
                bool dl = degenerate(lam.data());
                for (auto &mu : byW[bwt]) {
                    if (mu < lam) continue;          // c is symmetric in lam<->mu
                    S.total++;
                    bool dm = degenerate(mu.data());
                    bool inband = dl || dnu || dm;
                    if (inband) S.band++;
                    if (dl || dm) S.bandlm++;
                    if (!buildPoly(lam.data(), mu.data(), T.nu, P)) {
                        S.dimhist[0]++; if (inband) S.bdimhist[0]++;
                        continue;
                    }
                    analyze(P, R, FULLMODE);
                    S.dimhist[R.deg + 1]++; if (inband) S.bdimhist[R.deg + 1]++;
                    if (R.deg < 0) continue;
                    if (R.deg >= 1) {
                        if (R.c6[1] < S.mina1_full) {
                            S.mina1_full = R.c6[1];
                            memcpy(S.Mla, lam.data(), 16); memcpy(S.Mmu, mu.data(), 16); memcpy(S.Mnu, T.nu, 16);
                        }
                        if (inband && R.c6[1] < S.mina1) {
                            S.mina1 = R.c6[1];
                            memcpy(S.mla, lam.data(), 16); memcpy(S.mmu, mu.data(), 16); memcpy(S.mnu, T.nu, 16);
                        }
                    }
                    if (R.deg == 3) {
                        if (!(strict(lam.data()) && strict(mu.data()) && strict(T.nu))) {
                            if (!S.dim3_nonstrict) {
                                memcpy(S.nsla, lam.data(), 16); memcpy(S.nsmu, mu.data(), 16); memcpy(S.nsnu, T.nu, 16);
                            }
                            S.dim3_nonstrict++;
                        }
                        if (R.V > S.maxV_full) {
                            S.maxV_full = R.V;
                            memcpy(S.Vla, lam.data(), 16); memcpy(S.Vmu, mu.data(), 16); memcpy(S.Vnu, T.nu, 16);
                        }
                        if (inband && R.V > S.maxV) {
                            S.maxV = R.V;
                            memcpy(S.vla, lam.data(), 16); memcpy(S.vmu, mu.data(), 16); memcpy(S.vnu, T.nu, 16);
                        }
                        if (R.hs[1] == 0) {
                            if (R.V > S.maxVh1_full) {
                                S.maxVh1_full = R.V;
                                memcpy(S.Wla, lam.data(), 16); memcpy(S.Wmu, mu.data(), 16); memcpy(S.Wnu, T.nu, 16);
                            }
                            if (inband && R.V > S.maxVh1) {
                                S.maxVh1 = R.V;
                                memcpy(S.wla, lam.data(), 16); memcpy(S.wmu, mu.data(), 16); memcpy(S.wnu, T.nu, 16);
                            }
                        }
                        if (R.hs[2] > S.maxh2_full) {
                            S.maxh2_full = R.hs[2];
                            memcpy(S.Hla, lam.data(), 16); memcpy(S.Hmu, mu.data(), 16); memcpy(S.Hnu, T.nu, 16);
                        }
                        if (inband && R.hs[2] > S.maxh2) {
                            S.maxh2 = R.hs[2];
                            memcpy(S.hla, lam.data(), 16); memcpy(S.hmu, mu.data(), 16); memcpy(S.hnu, T.nu, 16);
                        }
                    }
                    if (inband && R.deg >= 0) {
                        ll m = 6;   // a_0 = 1
                        for (int k = 1; k <= R.deg; k++) if (R.c6[k] < m) m = R.c6[k];
                        if (m < S.minany) S.minany = m;
                    }
                    if (R.neg) recordHit(S.hits, lam.data(), mu.data(), T.nu, R);
                    if (R.verify_fail) { S.nverify_fail++; recordHit(S.anomalies, lam.data(), mu.data(), T.nu, R); }
                }
            }
        }
    }
    *out = move(S);
}

// ---------------------------------------------------------------- partitions
static void gen4(int W, vector<array<int,4>> &out) {
    for (int a = W; a >= 1; a--)
      for (int b = min(a, W - a); b >= 0; b--)
        for (int c = min(b, W - a - b); c >= 0; c--) {
            int d = W - a - b - c;
            if (d >= 0 && d <= c) out.push_back({a, b, c, d});
        }
}

static string fmt(const int p[4]) {
    for (int i = 0; i < 4; i++) if (p[i] < 0 || p[i] > 100000) return "\"none\"";
    string s = "["; bool f = true;
    for (int i = 0; i < 4; i++) if (p[i] > 0) { if (!f) s += ","; s += to_string(p[i]); f = false; }
    return s + "]";
}
static string frac6(ll x) {
    ll g = __gcd(x < 0 ? -x : x, (ll)6); if (g == 0) g = 6;
    ll n = x / g, d = 6 / g;
    return d == 1 ? to_string(n) : (to_string(n) + "/" + to_string(d));
}

int main(int argc, char **argv) {
    int Wlo = 1, Whi = 20, nthr = 1;
    const char *jsonPath = nullptr;
    const char *checkPath = nullptr;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--wlo")) Wlo = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--whi")) Whi = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--threads")) nthr = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--json")) jsonPath = argv[++i];
        else if (!strcmp(argv[i], "--check")) checkPath = argv[++i];
        else if (!strcmp(argv[i], "--full")) FULLMODE = 1;
    }
    buildTemplate();
    fprintf(stderr, "template: %zu inequality rows, %zu pure-boundary checks\n",
            ROWS.size(), CHKS.size());
    // boundedness guard: each coordinate must be bounded from both sides by rows
    // that involve no later coordinate (otherwise countLat would run forever)
    {
        int s0p=0,s0m=0,s1p=0,s1m=0,s2p=0,s2m=0;
        for (auto &r : ROWS) {
            if (r.co[1]==0 && r.co[2]==0) { if (r.co[0]>0) s0p++; if (r.co[0]<0) s0m++; }
            else if (r.co[2]==0)          { if (r.co[1]>0) s1p++; if (r.co[1]<0) s1m++; }
            else                          { if (r.co[2]>0) s2p++; if (r.co[2]<0) s2m++; }
        }
        if (!(s0p&&s0m&&s1p&&s1m&&s2p&&s2m)) { fprintf(stderr,"UNBOUNDED TEMPLATE\n"); return 2; }
        fprintf(stderr, "row split: R0=%d R1=%d R2=%d (signs ok)\n",
                s0p+s0m, s1p+s1m, s2p+s2m);
    }

    if (checkPath) {   // per-triple dump for cross-validation against hive4.py
        FILE *f = fopen(checkPath, "r");
        if (!f) { fprintf(stderr, "cannot open %s\n", checkPath); return 2; }
        char line[512];
        while (fgets(line, sizeof(line), f)) {
            int lam[4] = {0,0,0,0}, mu[4] = {0,0,0,0}, nu[4] = {0,0,0,0};
            char *save = nullptr;
            char *fields[3]; int nf = 0;
            for (char *tk = strtok_r(line, ";\n\r", &save); tk && nf < 3;
                 tk = strtok_r(nullptr, ";\n\r", &save)) fields[nf++] = tk;
            if (nf < 3) continue;
            int *dst[3] = {lam, mu, nu};
            for (int k = 0; k < 3; k++) {
                char *s2 = nullptr; int j = 0;
                for (char *tk = strtok_r(fields[k], ",", &s2); tk && j < 4;
                     tk = strtok_r(nullptr, ",", &s2)) dst[k][j++] = atoi(tk);
            }
            Poly P; Res R;
            if (!buildPoly(lam, mu, nu, P)) { printf("dim=-1 c=0 V=0 P=0\n"); continue; }
            analyze(P, R, 1);
            if (R.deg < 0) { printf("dim=-1 c=0 V=0 P=0\n"); continue; }
            printf("dim=%d c=%lld V=%lld P=", R.deg, R.L[1], R.deg == 3 ? R.V : 0);
            for (int k = 0; k <= R.deg; k++) printf("%s%s", k ? "," : "", frac6(R.c6[k]).c_str());
            printf(" h*=%lld,%lld,%lld,%lld L=%lld,%lld,%lld,%lld,%lld\n",
                   R.hs[0], R.hs[1], R.hs[2], R.hs[3],
                   R.L[0], R.L[1], R.L[2], R.L[3], R.L[4]);
        }
        fclose(f);
        return 0;
    }

    Stats G;
    for (int W = Wlo; W <= Whi; W++) {
        vector<array<int,4>> nus; gen4(W, nus);
        TASKS.clear();
        for (auto &n : nus) { Task T; memcpy(T.nu, n.data(), 16); T.W = W; TASKS.push_back(T); }
        // big nu first for load balance
        sort(TASKS.begin(), TASKS.end(), [](const Task &a, const Task &b) {
            ll pa = 1, pb = 1;
            for (int i = 0; i < 4; i++) { pa *= (a.nu[i] + 1); pb *= (b.nu[i] + 1); }
            return pa > pb;
        });
        NEXT = 0;
        vector<Stats> per(nthr);
        vector<thread> th;
        for (int i = 0; i < nthr; i++) th.emplace_back(worker, &per[i]);
        for (auto &t : th) t.join();
        Stats SW;
        for (int i = 0; i < nthr; i++) mergeStats(SW, per[i]);
        printf("W=%-3d triples=%-12lld band=%-12lld dim3(all)=%-9lld dim3(band)=%-9lld "
               "min6a1(band)=%lld maxV(band)=%lld maxV(all)=%lld hits=%zu vfail=%lld\n",
               W, SW.total, SW.band, SW.dimhist[4], SW.bdimhist[4],
               SW.mina1 == LLONG_MAX ? 0 : SW.mina1, SW.maxV, SW.maxV_full,
               SW.hits.size(), SW.nverify_fail);
        fflush(stdout);
        mergeStats(G, SW);
    }

    printf("\n=== BAND 12 CENSUS  W in [%d,%d] ===\n", Wlo, Whi);
    printf("triples enumerated (lam<=mu symmetry applied): %lld\n", G.total);
    printf("band-12 triples (deg(lam) or deg(mu) or deg(nu)): %lld\n", G.band);
    printf("band-12 core     (deg(lam) or deg(mu))          : %lld\n", G.bandlm);
    printf("dim histogram (all): -1:%lld 0:%lld 1:%lld 2:%lld 3:%lld\n",
           G.dimhist[0], G.dimhist[1], G.dimhist[2], G.dimhist[3], G.dimhist[4]);
    printf("dim histogram (band): -1:%lld 0:%lld 1:%lld 2:%lld 3:%lld\n",
           G.bdimhist[0], G.bdimhist[1], G.bdimhist[2], G.bdimhist[3], G.bdimhist[4]);
    printf("min a_1 (band)  = %s at lam=%s mu=%s nu=%s\n", frac6(G.mina1).c_str(),
           fmt(G.mla).c_str(), fmt(G.mmu).c_str(), fmt(G.mnu).c_str());
    printf("min a_1 (all)   = %s at lam=%s mu=%s nu=%s\n", frac6(G.mina1_full).c_str(),
           fmt(G.Mla).c_str(), fmt(G.Mmu).c_str(), fmt(G.Mnu).c_str());
    printf("min coeff (band, over a1,a2,a3) = %s\n", frac6(G.minany).c_str());
    printf("max V (band)    = %lld at lam=%s mu=%s nu=%s\n", G.maxV,
           fmt(G.vla).c_str(), fmt(G.vmu).c_str(), fmt(G.vnu).c_str());
    printf("max V (all)     = %lld at lam=%s mu=%s nu=%s\n", G.maxV_full,
           fmt(G.Vla).c_str(), fmt(G.Vmu).c_str(), fmt(G.Vnu).c_str());
    printf("max V | h*_1=0 (band) = %lld at lam=%s mu=%s nu=%s\n", G.maxVh1,
           fmt(G.wla).c_str(), fmt(G.wmu).c_str(), fmt(G.wnu).c_str());
    printf("max V | h*_1=0 (all)  = %lld at lam=%s mu=%s nu=%s\n", G.maxVh1_full,
           fmt(G.Wla).c_str(), fmt(G.Wmu).c_str(), fmt(G.Wnu).c_str());
    printf("record h*_2 (band) = %lld at lam=%s mu=%s nu=%s\n", G.maxh2,
           fmt(G.hla).c_str(), fmt(G.hmu).c_str(), fmt(G.hnu).c_str());
    printf("record h*_2 (all)  = %lld at lam=%s mu=%s nu=%s\n", G.maxh2_full,
           fmt(G.Hla).c_str(), fmt(G.Hmu).c_str(), fmt(G.Hnu).c_str());
    printf("dim-3 triples violating strictness of lam/mu/nu: %lld\n", G.dim3_nonstrict);
    printf("verification failures: %lld\n", G.nverify_fail);
    printf("TRIPLES WITH A STRICTLY NEGATIVE COEFFICIENT: %zu\n", G.hits.size());
    for (size_t i = 0; i < G.hits.size() && i < 100; i++) {
        Hit &h = G.hits[i];
        printf("   HIT %s;%s;%s  P=[%s,%s,%s,%s] L=%lld,%lld,%lld,%lld,%lld,%lld h*=%lld,%lld,%lld,%lld V=%lld\n",
               fmt(h.lam).c_str(), fmt(h.mu).c_str(), fmt(h.nu).c_str(),
               frac6(h.c6[0]).c_str(), frac6(h.c6[1]).c_str(), frac6(h.c6[2]).c_str(), frac6(h.c6[3]).c_str(),
               h.L[0], h.L[1], h.L[2], h.L[3], h.L[4], h.L[5],
               h.hs[0], h.hs[1], h.hs[2], h.hs[3], h.V);
    }
    for (size_t i = 0; i < G.anomalies.size() && i < 50; i++) {
        Hit &h = G.anomalies[i];
        printf("   ANOMALY %s;%s;%s L=%lld,%lld,%lld,%lld,%lld,%lld\n",
               fmt(h.lam).c_str(), fmt(h.mu).c_str(), fmt(h.nu).c_str(),
               h.L[0], h.L[1], h.L[2], h.L[3], h.L[4], h.L[5]);
    }
    if (jsonPath) {
        FILE *f = fopen(jsonPath, "w");
        fprintf(f, "{\n \"Wlo\": %d, \"Whi\": %d,\n", Wlo, Whi);
        fprintf(f, " \"triples_total\": %lld,\n \"triples_band\": %lld,\n \"triples_band_lam_mu\": %lld,\n",
                G.total, G.band, G.bandlm);
        fprintf(f, " \"dim_hist_all\": {\"-1\": %lld, \"0\": %lld, \"1\": %lld, \"2\": %lld, \"3\": %lld},\n",
                G.dimhist[0], G.dimhist[1], G.dimhist[2], G.dimhist[3], G.dimhist[4]);
        fprintf(f, " \"dim_hist_band\": {\"-1\": %lld, \"0\": %lld, \"1\": %lld, \"2\": %lld, \"3\": %lld},\n",
                G.bdimhist[0], G.bdimhist[1], G.bdimhist[2], G.bdimhist[3], G.bdimhist[4]);
        fprintf(f, " \"min_a1_band\": \"%s\", \"min_a1_band_at\": [\"%s\",\"%s\",\"%s\"],\n",
                frac6(G.mina1).c_str(), fmt(G.mla).c_str(), fmt(G.mmu).c_str(), fmt(G.mnu).c_str());
        fprintf(f, " \"min_a1_all\": \"%s\", \"min_a1_all_at\": [\"%s\",\"%s\",\"%s\"],\n",
                frac6(G.mina1_full).c_str(), fmt(G.Mla).c_str(), fmt(G.Mmu).c_str(), fmt(G.Mnu).c_str());
        fprintf(f, " \"dim3_nonstrict\": %lld,\n", G.dim3_nonstrict);
        fprintf(f, " \"record_hstar2_all\": %lld, \"record_hstar2_all_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxh2_full, fmt(G.Hla).c_str(), fmt(G.Hmu).c_str(), fmt(G.Hnu).c_str());
        fprintf(f, " \"min_coeff_band\": \"%s\",\n", frac6(G.minany).c_str());
        fprintf(f, " \"max_V_band\": %lld, \"max_V_band_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxV, fmt(G.vla).c_str(), fmt(G.vmu).c_str(), fmt(G.vnu).c_str());
        fprintf(f, " \"max_V_all\": %lld, \"max_V_all_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxV_full, fmt(G.Vla).c_str(), fmt(G.Vmu).c_str(), fmt(G.Vnu).c_str());
        fprintf(f, " \"max_V_hstar1_zero_band\": %lld, \"max_V_hstar1_zero_band_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxVh1, fmt(G.wla).c_str(), fmt(G.wmu).c_str(), fmt(G.wnu).c_str());
        fprintf(f, " \"max_V_hstar1_zero_all\": %lld, \"max_V_hstar1_zero_all_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxVh1_full, fmt(G.Wla).c_str(), fmt(G.Wmu).c_str(), fmt(G.Wnu).c_str());
        fprintf(f, " \"record_hstar2_band\": %lld, \"record_hstar2_band_at\": [\"%s\",\"%s\",\"%s\"],\n",
                G.maxh2, fmt(G.hla).c_str(), fmt(G.hmu).c_str(), fmt(G.hnu).c_str());
        fprintf(f, " \"verification_failures\": %lld,\n", G.nverify_fail);
        fprintf(f, " \"n_negative\": %zu,\n \"negatives\": [", G.hits.size());
        for (size_t i = 0; i < G.hits.size(); i++) {
            Hit &h = G.hits[i];
            fprintf(f, "%s\n  {\"lam\": %s, \"mu\": %s, \"nu\": %s, \"P\": [\"%s\",\"%s\",\"%s\",\"%s\"], \"L\": [%lld,%lld,%lld,%lld,%lld,%lld], \"hstar\": [%lld,%lld,%lld,%lld], \"V\": %lld}",
                    i ? "," : "", fmt(h.lam).c_str(), fmt(h.mu).c_str(), fmt(h.nu).c_str(),
                    frac6(h.c6[0]).c_str(), frac6(h.c6[1]).c_str(), frac6(h.c6[2]).c_str(), frac6(h.c6[3]).c_str(),
                    h.L[0], h.L[1], h.L[2], h.L[3], h.L[4], h.L[5],
                    h.hs[0], h.hs[1], h.hs[2], h.hs[3], h.V);
        }
        fprintf(f, "\n ],\n \"n_anomalies\": %zu,\n \"anomalies\": [", G.anomalies.size());
        for (size_t i = 0; i < G.anomalies.size(); i++) {
            Hit &h = G.anomalies[i];
            fprintf(f, "%s\n  {\"lam\": %s, \"mu\": %s, \"nu\": %s, \"L\": [%lld,%lld,%lld,%lld,%lld,%lld]}",
                    i ? "," : "", fmt(h.lam).c_str(), fmt(h.mu).c_str(), fmt(h.nu).c_str(),
                    h.L[0], h.L[1], h.L[2], h.L[3], h.L[4], h.L[5]);
        }
        fprintf(f, "\n ]\n}\n");
        fclose(f);
    }
    return 0;
}
