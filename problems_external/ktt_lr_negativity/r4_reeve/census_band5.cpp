// census_band5.cpp -- EXHAUSTIVE r=4 hive-polytope Ehrhart census over a weight band.
//
// TARGET: a King-Tollu-Toumazet counterexample = a triple (lam,mu,nu) of partitions
// with at most 4 parts, |lam|+|mu|=|nu|=W, whose stretched LR polynomial
//   P(n) = c(n nu; n lam, n mu) = #( n*Q(lam,mu,nu) cap Z^3 )
// has a strictly negative coefficient.  r=4  =>  dim ambient = 3 = the Reeve dimension.
//
// EXACTNESS.  Everything here is integer arithmetic on long long.  Ehrhart values
// L(n) = #(nQ cap Z^3) are obtained by DIRECT enumeration with exact integer
// interval propagation (no floating point anywhere).  P is recovered from the exact
// finite differences of L(0..3) -- legitimate because deg P = dim Q <= 3 and P is a
// genuine polynomial (Derksen-Weyman / Rassart), and it is re-VERIFIED against
// independently enumerated L(4) and L(5) for every 3-dimensional polytope.
//
//   Delta1 = L1-1, Delta2 = L2-2L1+1, Delta3 = L3-3L2+3L1-1
//   6*a1 = 18 L1 - 9 L2 + 2 L3 - 11      (= 11 + 2h*_1 - h*_2 + 2h*_3)
//   2*a2 = -L3 + 4 L2 - 5 L1 + 2
//   V    = 6*a3 = Delta3                  (normalized volume)
//   h*   = (1, L1-4, L2-4L1+6, L3-4L2+6L1-4)   for dim 3
//
// The rhombus-row builder build_rows_xyz is copied verbatim from the already
// validated vcheck.cpp / typescan.cpp (which agree with hive4.py).
//
// Build: g++ -O3 -march=native -fopenmp -o census_band5 census_band5.cpp
// Usage: census_band5 WMIN WMAX [outprefix]
//        census_band5 --check FILE     ("lam;mu;nu" lines -> full per-triple record)

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <array>
#include <string>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;
static const ll BIGP = 1LL << 50;
static const ll BIGN = -(1LL << 50);

struct Row { int p, q, r; ll rhs; };

// ---------------------------------------------------------------- rhombus rows
static int build_rows_xyz(const ll lam[4], const ll mu[4], const ll nu[4], Row out[24]) {
    ll B[5][5];
    for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) B[i][j] = 0;
    ll sl = lam[0] + lam[1] + lam[2] + lam[3];
    ll acc = 0; for (int y = 0; y <= 4; y++) { B[0][y] = acc; if (y < 4) acc += lam[y]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][4 - x] = sl + acc; if (x < 4) acc += mu[x]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][0] = acc; if (x < 4) acc += nu[x]; }
    B[0][0] = 0;
    auto isInt = [](int x, int y) { return (x == 1 && y == 1) || (x == 1 && y == 2) || (x == 2 && y == 1); };
    auto idx = [](int x, int y) { return (x == 1 && y == 1) ? 0 : (x == 1 && y == 2) ? 1 : 2; };
    int nr = 0; bool bad = false;
    auto add = [&](int px[2], int py[2], int mx[2], int my[2]) {
        ll co[3] = {0, 0, 0}; ll cst = 0;
        for (int t = 0; t < 2; t++) {
            if (isInt(px[t], py[t])) co[idx(px[t], py[t])] -= 1; else cst -= B[px[t]][py[t]];
            if (isInt(mx[t], my[t])) co[idx(mx[t], my[t])] += 1; else cst += B[mx[t]][my[t]];
        }
        if (!co[0] && !co[1] && !co[2]) { if (cst > 0) bad = true; return; }
        out[nr].p = (int)co[0]; out[nr].q = (int)co[1]; out[nr].r = (int)co[2]; out[nr].rhs = -cst; nr++;
    };
    for (int x = 0; x <= 4; x++) for (int y = 0; y <= 4; y++) {
        if (x + y <= 2) { int px[2] = {x + 1, x}, py[2] = {y, y + 1}, mx[2] = {x, x + 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
        if (y >= 1 && x + y <= 3) { int px[2] = {x, x + 1}, py[2] = {y, y}, mx[2] = {x, x + 1}, my[2] = {y + 1, y - 1}; add(px, py, mx, my); }
        if (x >= 1 && x + y <= 3) { int px[2] = {x, x}, py[2] = {y, y + 1}, mx[2] = {x + 1, x - 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
    }
    return bad ? -1 : nr;
}

// ---------------------------------------------------------------- integer division
static inline ll fdiv(ll a, ll b) { /* floor(a/b), b > 0 */
    return (a >= 0) ? (a / b) : (-(((-a) + b - 1) / b));
}

// grouped row indices (by highest coordinate used)
struct Groups { int g0[24], n0, g1[24], n1, g2[24], n2; };
static void group_rows(const Row *R, int nr, Groups &G) {
    G.n0 = G.n1 = G.n2 = 0;
    for (int i = 0; i < nr; i++) {
        if (R[i].r != 0) G.g2[G.n2++] = i;
        else if (R[i].q != 0) G.g1[G.n1++] = i;
        else G.g0[G.n0++] = i;
    }
}

// L(n) = #( nQ cap Z^3 ), exact, by interval propagation.  n >= 1.
static ll lattice_count(const Row *R, const Groups &G, ll n) {
    ll xlo = BIGN, xhi = BIGP;
    for (int t = 0; t < G.n0; t++) {
        const Row &w = R[G.g0[t]]; ll rem = w.rhs * n;
        if (w.p > 0) { ll v = fdiv(rem, w.p); if (v < xhi) xhi = v; }
        else { ll v = -fdiv(rem, -w.p); if (v > xlo) xlo = v; }
    }
    if (xlo > xhi) return 0;
    if (xlo <= BIGN || xhi >= BIGP) { fprintf(stderr, "FATAL: unbounded x\n"); exit(3); }
    ll total = 0;
    for (ll x = xlo; x <= xhi; x++) {
        ll ylo = BIGN, yhi = BIGP;
        for (int t = 0; t < G.n1; t++) {
            const Row &w = R[G.g1[t]]; ll rem = w.rhs * n - (ll)w.p * x;
            if (w.q > 0) { ll v = fdiv(rem, w.q); if (v < yhi) yhi = v; }
            else { ll v = -fdiv(rem, -w.q); if (v > ylo) ylo = v; }
            if (ylo > yhi) break;
        }
        if (ylo > yhi) continue;
        for (ll y = ylo; y <= yhi; y++) {
            ll zlo = BIGN, zhi = BIGP;
            for (int t = 0; t < G.n2; t++) {
                const Row &w = R[G.g2[t]]; ll rem = w.rhs * n - (ll)w.p * x - (ll)w.q * y;
                if (w.r > 0) { ll v = fdiv(rem, w.r); if (v < zhi) zhi = v; }
                else { ll v = -fdiv(rem, -w.r); if (v > zlo) zlo = v; }
                if (zlo > zhi) break;
            }
            if (zhi >= zlo) total += zhi - zlo + 1;
        }
    }
    return total;
}

// ---------------------------------------------------------------- vertices (audit)
static ll det3(ll a, ll b, ll c, ll d, ll e, ll f, ll g, ll h, ll i) {
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}
static ll gcdl(ll a, ll b) { a = a < 0 ? -a : a; b = b < 0 ? -b : b; while (b) { ll t = a % b; a = b; b = t; } return a; }

// returns number of distinct vertices; sets maxden.  (used only on dim-3 triples)
static int vertex_audit(const Row *R, int nr, ll &maxden) {
    std::vector<std::array<ll, 4> > vs; vs.reserve(32); maxden = 1;
    for (int i = 0; i < nr; i++) for (int j = i + 1; j < nr; j++) for (int k = j + 1; k < nr; k++) {
        ll D = det3(R[i].p, R[i].q, R[i].r, R[j].p, R[j].q, R[j].r, R[k].p, R[k].q, R[k].r);
        if (D == 0) continue;
        ll b1 = R[i].rhs, b2 = R[j].rhs, b3 = R[k].rhs;
        ll nx = det3(b1, R[i].q, R[i].r, b2, R[j].q, R[j].r, b3, R[k].q, R[k].r);
        ll ny = det3(R[i].p, b1, R[i].r, R[j].p, b2, R[j].r, R[k].p, b3, R[k].r);
        ll nz = det3(R[i].p, R[i].q, b1, R[j].p, R[j].q, b2, R[k].p, R[k].q, b3);
        if (D < 0) { D = -D; nx = -nx; ny = -ny; nz = -nz; }
        bool ok = true;
        for (int t = 0; t < nr; t++) {
            if ((ll)R[t].p * nx + (ll)R[t].q * ny + (ll)R[t].r * nz > R[t].rhs * D) { ok = false; break; }
        }
        if (!ok) continue;
        ll g = gcdl(gcdl(gcdl(nx, ny), nz), D); if (g == 0) g = D;
        ll rx = nx / g, ry = ny / g, rz = nz / g, rd = D / g;
        std::array<ll, 4> v = {{rx, ry, rz, rd}};
        if (std::find(vs.begin(), vs.end(), v) == vs.end()) { vs.push_back(v); if (rd > maxden) maxden = rd; }
    }
    return (int)vs.size();
}

// ---------------------------------------------------------------- per-triple record
struct Rec {
    ll L[6];
    int dim;
    ll a1num;   // 6*a1
    ll a2num;   // 2*a2
    ll V;       // 6*a3 = normalized volume
    ll hs[4];
    bool empty, neg, verified, anomaly;
};

static void analyze(const ll lam[4], const ll mu[4], const ll nu[4], Rec &out, bool full) {
    Row R[24]; int nr = build_rows_xyz(lam, mu, nu, R);
    memset(&out, 0, sizeof(out));
    out.verified = true;
    if (nr < 0) { out.empty = true; out.dim = -1; return; }
    Groups G; group_rows(R, nr, G);
    out.L[0] = 1;
    out.L[1] = lattice_count(R, G, 1);
    out.L[2] = lattice_count(R, G, 2);
    out.L[3] = lattice_count(R, G, 3);
    if (out.L[1] == 0 && out.L[2] == 0 && out.L[3] == 0) {
        // Q has no lattice point in Q, 2Q, 3Q.  For a rational polytope with vertex
        // denominators <= 4 this still leaves 4Q; check it and flag if nonempty.
        ll L4 = lattice_count(R, G, 4);
        if (L4 != 0) { out.anomaly = true; out.L[4] = L4; }
        out.empty = true; out.dim = -1; return;
    }
    ll L1 = out.L[1], L2 = out.L[2], L3 = out.L[3];
    ll d1 = L1 - 1, d2 = L2 - 2 * L1 + 1, d3 = L3 - 3 * L2 + 3 * L1 - 1;
    out.V = d3;
    out.a1num = 18 * L1 - 9 * L2 + 2 * L3 - 11;
    out.a2num = -L3 + 4 * L2 - 5 * L1 + 2;
    out.dim = d3 != 0 ? 3 : (d2 != 0 ? 2 : (d1 != 0 ? 1 : 0));
    out.hs[0] = 1; out.hs[1] = L1 - 4; out.hs[2] = L2 - 4 * L1 + 6; out.hs[3] = L3 - 4 * L2 + 6 * L1 - 4;
    // negativity of the TRIMMED coefficient list
    bool neg = false;
    if (out.dim == 3) { if (out.a1num < 0 || out.a2num < 0 || out.V < 0) neg = true; }
    else if (out.dim == 2) { if (out.a1num < 0 || out.a2num < 0) neg = true; }
    else if (out.dim == 1) { if (out.a1num < 0) neg = true; }
    out.neg = neg;
    if (out.dim == 3 || full || neg) {
        // exact re-verification of P at n = 4, 5 against direct enumeration
        out.L[4] = lattice_count(R, G, 4);
        out.L[5] = lattice_count(R, G, 5);
        // P(t) = 1 + d1*C(t,1) + d2*C(t,2) + d3*C(t,3)
        for (int n = 4; n <= 5; n++) {
            ll p = 1 + d1 * n + d2 * (ll)n * (n - 1) / 2 + d3 * (ll)n * (n - 1) * (n - 2) / 6;
            if (p != out.L[n]) out.verified = false;
        }
    }
}

// ---------------------------------------------------------------- partitions
static void parts_le4(int N, std::vector<std::array<ll, 4> > &out) {
    out.clear();
    std::array<ll, 4> cur = {{0, 0, 0, 0}};
    // p1 >= p2 >= p3 >= p4 >= 0, sum = N
    for (ll p1 = N; p1 >= (N + 3) / 4; p1--) {
        ll r1 = N - p1;
        for (ll p2 = std::min(p1, r1); p2 >= (r1 + 2) / 3; p2--) {
            ll r2 = r1 - p2;
            for (ll p3 = std::min(p2, r2); p3 >= (r2 + 1) / 2; p3--) {
                ll p4 = r2 - p3;
                if (p4 > p3) continue;
                cur[0] = p1; cur[1] = p2; cur[2] = p3; cur[3] = p4;
                out.push_back(cur);
            }
        }
    }
    if (N == 0) { cur[0] = cur[1] = cur[2] = cur[3] = 0; out.clear(); out.push_back(cur); }
}

// ---------------------------------------------------------------- accumulators
struct Hit { ll lam[4], mu[4], nu[4]; Rec rec; };
struct Acc {
    ll nTriples, nEmpty, dimh[5];      // dimh[0..3] for dim 0..3, dimh[4] unused
    bool haveA1; ll bestA1; ll bA1lam[4], bA1mu[4], bA1nu[4]; ll bA1hs[4];
    bool haveA1p; ll bestA1p; ll bA1plam[4], bA1pmu[4], bA1pnu[4]; int bA1pdim; // dim >= 1
    bool haveA13; ll bestA13; ll bA13lam[4], bA13mu[4], bA13nu[4]; ll bA13hs[4]; // dim == 3
    ll minA2; ll bA2lam[4], bA2mu[4], bA2nu[4];                                  // dim >= 2
    ll maxV; ll bVlam[4], bVmu[4], bVnu[4]; ll bVhs[4]; ll bVL1;
    ll maxV0; ll bV0lam[4], bV0mu[4], bV0nu[4]; ll bV0hs[4];
    ll maxH2; ll bH2lam[4], bH2mu[4], bH2nu[4]; ll bH2hs[4];
    ll maxDen; ll nDim3Audited; ll nVerifyFail; ll nAnomaly; ll nH1zero; ll nH1zeroV1;
    std::vector<Hit> hits;
    std::vector<Hit> audits;   // verify failures / anomalies / non-lattice
};
static void acc_init(Acc &a) {
    a.nTriples = a.nEmpty = 0; for (int i = 0; i < 5; i++) a.dimh[i] = 0;
    a.haveA1 = false; a.bestA1 = 0; a.maxV = -1; a.maxV0 = -1; a.maxH2 = -1;
    a.haveA1p = false; a.bestA1p = 0; a.bA1pdim = -1;
    a.haveA13 = false; a.bestA13 = 0; a.minA2 = (1LL << 60);
    a.maxDen = 1; a.nDim3Audited = 0; a.nVerifyFail = 0; a.nAnomaly = 0; a.nH1zero = 0; a.nH1zeroV1 = 0;
    a.hits.clear(); a.audits.clear();
}
static void cp4(ll d[4], const ll s[4]) { for (int i = 0; i < 4; i++) d[i] = s[i]; }

static void acc_update(Acc &A, const ll lam[4], const ll mu[4], const ll nu[4], const Rec &r) {
    A.nTriples++;
    if (r.empty) {
        A.nEmpty++;
        if (r.anomaly) { A.nAnomaly++; Hit h; cp4(h.lam, lam); cp4(h.mu, mu); cp4(h.nu, nu); h.rec = r; A.audits.push_back(h); }
        return;
    }
    A.dimh[r.dim]++;
    if (!r.verified) { A.nVerifyFail++; Hit h; cp4(h.lam, lam); cp4(h.mu, mu); cp4(h.nu, nu); h.rec = r; A.audits.push_back(h); }
    if (!A.haveA1 || r.a1num < A.bestA1) {
        A.haveA1 = true; A.bestA1 = r.a1num;
        cp4(A.bA1lam, lam); cp4(A.bA1mu, mu); cp4(A.bA1nu, nu); cp4(A.bA1hs, r.hs);
    }
    if (r.dim >= 1 && (!A.haveA1p || r.a1num < A.bestA1p)) {
        A.haveA1p = true; A.bestA1p = r.a1num; A.bA1pdim = r.dim;
        cp4(A.bA1plam, lam); cp4(A.bA1pmu, mu); cp4(A.bA1pnu, nu);
    }
    if (r.dim >= 2 && r.a2num < A.minA2) {
        A.minA2 = r.a2num; cp4(A.bA2lam, lam); cp4(A.bA2mu, mu); cp4(A.bA2nu, nu);
    }
    if (r.dim == 3) {
        if (!A.haveA13 || r.a1num < A.bestA13) {
            A.haveA13 = true; A.bestA13 = r.a1num;
            cp4(A.bA13lam, lam); cp4(A.bA13mu, mu); cp4(A.bA13nu, nu); cp4(A.bA13hs, r.hs);
        }
        if (r.V > A.maxV) { A.maxV = r.V; cp4(A.bVlam, lam); cp4(A.bVmu, mu); cp4(A.bVnu, nu); cp4(A.bVhs, r.hs); A.bVL1 = r.L[1]; }
        if (r.hs[1] == 0) {
            A.nH1zero++; if (r.V == 1) A.nH1zeroV1++;
            if (r.V > A.maxV0) { A.maxV0 = r.V; cp4(A.bV0lam, lam); cp4(A.bV0mu, mu); cp4(A.bV0nu, nu); cp4(A.bV0hs, r.hs); }
        }
        if (r.hs[2] > A.maxH2) { A.maxH2 = r.hs[2]; cp4(A.bH2lam, lam); cp4(A.bH2mu, mu); cp4(A.bH2nu, nu); cp4(A.bH2hs, r.hs); }
    }
    if (r.neg) { Hit h; cp4(h.lam, lam); cp4(h.mu, mu); cp4(h.nu, nu); h.rec = r; A.hits.push_back(h); }
}
static void acc_merge(Acc &A, const Acc &B) {
    A.nTriples += B.nTriples; A.nEmpty += B.nEmpty;
    for (int i = 0; i < 5; i++) A.dimh[i] += B.dimh[i];
    A.nDim3Audited += B.nDim3Audited; A.nVerifyFail += B.nVerifyFail; A.nAnomaly += B.nAnomaly;
    A.nH1zero += B.nH1zero; A.nH1zeroV1 += B.nH1zeroV1;
    if (B.maxDen > A.maxDen) A.maxDen = B.maxDen;
    if (B.haveA1 && (!A.haveA1 || B.bestA1 < A.bestA1)) {
        A.haveA1 = true; A.bestA1 = B.bestA1;
        cp4(A.bA1lam, B.bA1lam); cp4(A.bA1mu, B.bA1mu); cp4(A.bA1nu, B.bA1nu); cp4(A.bA1hs, B.bA1hs);
    }
    if (B.haveA1p && (!A.haveA1p || B.bestA1p < A.bestA1p)) {
        A.haveA1p = true; A.bestA1p = B.bestA1p; A.bA1pdim = B.bA1pdim;
        cp4(A.bA1plam, B.bA1plam); cp4(A.bA1pmu, B.bA1pmu); cp4(A.bA1pnu, B.bA1pnu);
    }
    if (B.haveA13 && (!A.haveA13 || B.bestA13 < A.bestA13)) {
        A.haveA13 = true; A.bestA13 = B.bestA13;
        cp4(A.bA13lam, B.bA13lam); cp4(A.bA13mu, B.bA13mu); cp4(A.bA13nu, B.bA13nu); cp4(A.bA13hs, B.bA13hs);
    }
    if (B.minA2 < A.minA2) { A.minA2 = B.minA2; cp4(A.bA2lam, B.bA2lam); cp4(A.bA2mu, B.bA2mu); cp4(A.bA2nu, B.bA2nu); }
    if (B.maxV > A.maxV) { A.maxV = B.maxV; cp4(A.bVlam, B.bVlam); cp4(A.bVmu, B.bVmu); cp4(A.bVnu, B.bVnu); cp4(A.bVhs, B.bVhs); A.bVL1 = B.bVL1; }
    if (B.maxV0 > A.maxV0) { A.maxV0 = B.maxV0; cp4(A.bV0lam, B.bV0lam); cp4(A.bV0mu, B.bV0mu); cp4(A.bV0nu, B.bV0nu); cp4(A.bV0hs, B.bV0hs); }
    if (B.maxH2 > A.maxH2) { A.maxH2 = B.maxH2; cp4(A.bH2lam, B.bH2lam); cp4(A.bH2mu, B.bH2mu); cp4(A.bH2nu, B.bH2nu); cp4(A.bH2hs, B.bH2hs); }
    for (size_t i = 0; i < B.hits.size(); i++) A.hits.push_back(B.hits[i]);
    for (size_t i = 0; i < B.audits.size(); i++) A.audits.push_back(B.audits[i]);
}

static std::string pstr(const ll p[4]) {
    std::string s; char buf[32];
    for (int i = 0; i < 4; i++) { if (p[i] == 0) break; if (!s.empty()) s += ","; snprintf(buf, 32, "%lld", p[i]); s += buf; }
    if (s.empty()) s = "0";
    return s;
}

// containment nu >= lam (necessary for c != 0, hence for Q nonempty by saturation)
static inline bool contained(const ll a[4], const ll b[4]) {
    return a[0] <= b[0] && a[1] <= b[1] && a[2] <= b[2] && a[3] <= b[3];
}

int main(int argc, char **argv) {
    if (argc >= 3 && !strcmp(argv[1], "--check")) {
        FILE *f = fopen(argv[2], "r"); if (!f) { perror("open"); return 2; }
        char line[512];
        while (fgets(line, sizeof(line), f)) {
            char *nl = strchr(line, '\n'); if (nl) *nl = 0;
            if (!line[0] || line[0] == '#') continue;
            ll P[3][4]; for (int i = 0; i < 3; i++) for (int j = 0; j < 4; j++) P[i][j] = 0;
            {   // portable parse of "a,b,c;d,e;f,g,h,i"
                int fi = 0, k = 0; const char *p = line;
                while (*p && fi < 3) {
                    if (*p == ';') { fi++; k = 0; p++; continue; }
                    if (*p == ',' || *p == ' ') { p++; continue; }
                    char *end; ll v = strtoll(p, &end, 10);
                    if (end == p) { p++; continue; }
                    if (k < 4) P[fi][k++] = v;
                    p = end;
                }
            }
            Rec r; analyze(P[0], P[1], P[2], r, true);
            ll den = 1; int nv = 0;
            if (!r.empty) { Row R[24]; int nr = build_rows_xyz(P[0], P[1], P[2], R); nv = vertex_audit(R, nr, den); }
            printf("%s;%s;%s | dim=%d L=%lld,%lld,%lld,%lld,%lld,%lld c=%lld V=%lld hstar=%lld,%lld,%lld,%lld 6a1=%lld 2a2=%lld nv=%d den=%lld %s%s\n",
                   pstr(P[0]).c_str(), pstr(P[1]).c_str(), pstr(P[2]).c_str(), r.dim,
                   r.L[0], r.L[1], r.L[2], r.L[3], r.L[4], r.L[5], r.empty ? 0 : r.L[1], r.empty ? 0 : r.V,
                   r.empty ? 0 : r.hs[0], r.empty ? 0 : r.hs[1], r.empty ? 0 : r.hs[2], r.empty ? 0 : r.hs[3],
                   r.empty ? 0 : r.a1num, r.empty ? 0 : r.a2num, nv, den,
                   r.neg ? "NEG" : "pos", r.verified ? "" : " !!VERIFY_FAIL");
        }
        fclose(f); return 0;
    }
    if (argc < 3) { fprintf(stderr, "usage: census_band5 WMIN WMAX [outprefix]\n"); return 2; }
    int WMIN = atoi(argv[1]), WMAX = atoi(argv[2]);
    const char *outpre = argc > 3 ? argv[3] : "band5";
    bool useFilter = true, nu4only = false;
    for (int i = 4; i < argc; i++) {
        if (!strcmp(argv[i], "nofilter")) useFilter = false;
        if (!strcmp(argv[i], "nu4")) nu4only = true;
    }
    fprintf(stderr, "containment prefilter: %s ; nu restricted to exactly 4 parts: %s\n",
            useFilter ? "ON" : "OFF", nu4only ? "YES" : "NO");

    Acc GLOB; acc_init(GLOB);
    ll grand = 0;
    std::string perW;
    char buf[4096];

    for (int W = WMIN; W <= WMAX; W++) {
        double t0 = 0;
#ifdef _OPENMP
        t0 = omp_get_wtime();
#endif
        std::vector<std::vector<std::array<ll, 4> > > PN(W + 1);
        for (int n = 0; n <= W; n++) parts_le4(n, PN[n]);
        std::vector<std::array<ll, 4> > NUSV = PN[W];
        if (nu4only) {
            std::vector<std::array<ll, 4> > t;
            for (size_t i = 0; i < NUSV.size(); i++) if (NUSV[i][3] > 0) t.push_back(NUSV[i]);
            NUSV.swap(t);
        }
        const std::vector<std::array<ll, 4> > &NUS = NUSV;
        // task list: (a, index in PN[a]) for a <= W/2
        std::vector<std::pair<int, int> > tasks;
        for (int a = 0; a * 2 <= W; a++) for (size_t i = 0; i < PN[a].size(); i++) tasks.push_back(std::make_pair(a, (int)i));
        Acc WA; acc_init(WA);
        int nth = 1;
#ifdef _OPENMP
        nth = omp_get_max_threads();
#endif
        std::vector<Acc> TA(nth); for (int i = 0; i < nth; i++) acc_init(TA[i]);
#pragma omp parallel for schedule(dynamic, 1)
        for (long long ti = 0; ti < (long long)tasks.size(); ti++) {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            Acc &A = TA[tid];
            int a = tasks[ti].first;
            const ll *lam = PN[a][tasks[ti].second].data();
            const std::vector<std::array<ll, 4> > &MUS = PN[W - a];
            for (size_t mi = 0; mi < MUS.size(); mi++) {
                const ll *mu = MUS[mi].data();
                if (2 * a == W) { // tie-break: lam <= mu lexicographically
                    bool skip = false;
                    for (int k = 0; k < 4; k++) { if (lam[k] != mu[k]) { skip = (lam[k] > mu[k]); break; } }
                    if (skip) continue;
                }
                for (size_t ni = 0; ni < NUS.size(); ni++) {
                    const ll *nu = NUS[ni].data();
                    if (useFilter && (!contained(lam, nu) || !contained(mu, nu))) {
                        // c = 0 and (saturation) Q = empty: P == 0, no coefficient
                        A.nTriples++; A.nEmpty++; continue;
                    }
                    Rec r; analyze(lam, mu, nu, r, false);
                    acc_update(A, lam, mu, nu, r);
                    if (r.dim == 3) {
                        A.nDim3Audited++;
                        {   // full vertex/denominator audit of EVERY 3-dimensional hive polytope
                            Row R[24]; int nr = build_rows_xyz(lam, mu, nu, R); ll den;
                            vertex_audit(R, nr, den);
                            if (den > A.maxDen) A.maxDen = den;
                        }
                    }
                }
            }
        }
        for (int i = 0; i < nth; i++) acc_merge(WA, TA[i]);
        double dt = 0;
#ifdef _OPENMP
        dt = omp_get_wtime() - t0;
#endif
        grand += WA.nTriples;
        snprintf(buf, sizeof(buf),
                 "W=%d triples=%lld empty=%lld dim0=%lld dim1=%lld dim2=%lld dim3=%lld "
                 "min6a1(all)=%lld min6a1(dim>=1)=%lld min6a1(dim3)=%lld min2a2=%lld maxV=%lld maxV(h1=0)=%lld maxh2=%lld "
                 "negs=%zu verifyfail=%lld anomaly=%lld maxden=%lld %.1fs\n",
                 W, WA.nTriples, WA.nEmpty, WA.dimh[0], WA.dimh[1], WA.dimh[2], WA.dimh[3],
                 WA.bestA1, WA.bestA1p, WA.bestA13, WA.minA2,
                 WA.maxV, WA.maxV0, WA.maxH2, WA.hits.size(), WA.nVerifyFail, WA.nAnomaly, WA.maxDen, dt);
        fputs(buf, stdout); fflush(stdout);
        perW += buf;
        for (size_t i = 0; i < WA.hits.size(); i++) {
            const Hit &h = WA.hits[i];
            printf("*** NEGATIVE *** %s;%s;%s dim=%d L=%lld,%lld,%lld,%lld,%lld,%lld 6a1=%lld 2a2=%lld V=%lld hstar=%lld,%lld,%lld,%lld ver=%d\n",
                   pstr(h.lam).c_str(), pstr(h.mu).c_str(), pstr(h.nu).c_str(), h.rec.dim,
                   h.rec.L[0], h.rec.L[1], h.rec.L[2], h.rec.L[3], h.rec.L[4], h.rec.L[5],
                   h.rec.a1num, h.rec.a2num, h.rec.V, h.rec.hs[0], h.rec.hs[1], h.rec.hs[2], h.rec.hs[3],
                   (int)h.rec.verified);
        }
        fflush(stdout);
        acc_merge(GLOB, WA);
    }

    printf("\n=== BAND [%d,%d] EXHAUSTIVE (r<=4 partitions, lam<->mu symmetry applied) ===\n", WMIN, WMAX);
    printf("triples tested            : %lld\n", GLOB.nTriples);
    printf("empty (P == 0)            : %lld\n", GLOB.nEmpty);
    printf("dim histogram 0/1/2/3     : %lld %lld %lld %lld\n", GLOB.dimh[0], GLOB.dimh[1], GLOB.dimh[2], GLOB.dimh[3]);
    printf("min a1 = %lld/6 at %s;%s;%s  h*=%lld,%lld,%lld,%lld\n", GLOB.bestA1,
           pstr(GLOB.bA1lam).c_str(), pstr(GLOB.bA1mu).c_str(), pstr(GLOB.bA1nu).c_str(),
           GLOB.bA1hs[0], GLOB.bA1hs[1], GLOB.bA1hs[2], GLOB.bA1hs[3]);
    printf("max normalized volume     : %lld at %s;%s;%s h*=%lld,%lld,%lld,%lld c=%lld\n", GLOB.maxV,
           pstr(GLOB.bVlam).c_str(), pstr(GLOB.bVmu).c_str(), pstr(GLOB.bVnu).c_str(),
           GLOB.bVhs[0], GLOB.bVhs[1], GLOB.bVhs[2], GLOB.bVhs[3], GLOB.bVL1);
    printf("max volume with h*_1 = 0  : %lld at %s;%s;%s h*=%lld,%lld,%lld,%lld\n", GLOB.maxV0,
           pstr(GLOB.bV0lam).c_str(), pstr(GLOB.bV0mu).c_str(), pstr(GLOB.bV0nu).c_str(),
           GLOB.bV0hs[0], GLOB.bV0hs[1], GLOB.bV0hs[2], GLOB.bV0hs[3]);
    printf("record h*_2               : %lld at %s;%s;%s h*=%lld,%lld,%lld,%lld\n", GLOB.maxH2,
           pstr(GLOB.bH2lam).c_str(), pstr(GLOB.bH2mu).c_str(), pstr(GLOB.bH2nu).c_str(),
           GLOB.bH2hs[0], GLOB.bH2hs[1], GLOB.bH2hs[2], GLOB.bH2hs[3]);
    printf("min a1 over dim>=1        : %lld/6 (dim %d) at %s;%s;%s\n", GLOB.bestA1p, GLOB.bA1pdim,
           pstr(GLOB.bA1plam).c_str(), pstr(GLOB.bA1pmu).c_str(), pstr(GLOB.bA1pnu).c_str());
    printf("min a1 over dim==3        : %lld/6 at %s;%s;%s h*=%lld,%lld,%lld,%lld\n", GLOB.bestA13,
           pstr(GLOB.bA13lam).c_str(), pstr(GLOB.bA13mu).c_str(), pstr(GLOB.bA13nu).c_str(),
           GLOB.bA13hs[0], GLOB.bA13hs[1], GLOB.bA13hs[2], GLOB.bA13hs[3]);
    printf("min a2 over dim>=2        : %lld/2 at %s;%s;%s\n", GLOB.minA2,
           pstr(GLOB.bA2lam).c_str(), pstr(GLOB.bA2mu).c_str(), pstr(GLOB.bA2nu).c_str());
    printf("dim-3 with h*_1 = 0 (c=4) : %lld  of which V = 1: %lld\n", GLOB.nH1zero, GLOB.nH1zeroV1);
    printf("dim-3 triples             : %lld  (vertex/denominator-audited: %lld)\n", GLOB.dimh[3], GLOB.nDim3Audited);
    printf("max vertex denominator    : %lld (audited subset)\n", GLOB.maxDen);
    printf("interpolation verify fails: %lld\n", GLOB.nVerifyFail);
    printf("empty-with-L4>0 anomalies : %lld\n", GLOB.nAnomaly);
    printf("TRIPLES WITH A NEGATIVE COEFFICIENT: %zu\n", GLOB.hits.size());

    // JSON
    std::string jf = std::string(outpre) + "_summary.json";
    FILE *f = fopen(jf.c_str(), "w");
    fprintf(f, "{\n \"wmin\": %d, \"wmax\": %d,\n", WMIN, WMAX);
    fprintf(f, " \"triples_tested\": %lld,\n \"empty\": %lld,\n", GLOB.nTriples, GLOB.nEmpty);
    fprintf(f, " \"dim_histogram\": {\"-1\": %lld, \"0\": %lld, \"1\": %lld, \"2\": %lld, \"3\": %lld},\n",
            GLOB.nEmpty, GLOB.dimh[0], GLOB.dimh[1], GLOB.dimh[2], GLOB.dimh[3]);
    fprintf(f, " \"min_a1_times6\": %lld,\n \"min_a1\": \"%lld/6\",\n", GLOB.bestA1, GLOB.bestA1);
    fprintf(f, " \"min_a1_witness\": [\"%s\",\"%s\",\"%s\"],\n", pstr(GLOB.bA1lam).c_str(), pstr(GLOB.bA1mu).c_str(), pstr(GLOB.bA1nu).c_str());
    fprintf(f, " \"min_a1_dim_ge1\": \"%lld/6\",\n \"min_a1_dim_ge1_dim\": %d,\n \"min_a1_dim_ge1_witness\": [\"%s\",\"%s\",\"%s\"],\n",
            GLOB.bestA1p, GLOB.bA1pdim, pstr(GLOB.bA1plam).c_str(), pstr(GLOB.bA1pmu).c_str(), pstr(GLOB.bA1pnu).c_str());
    fprintf(f, " \"min_a1_dim3\": \"%lld/6\",\n \"min_a1_dim3_witness\": [\"%s\",\"%s\",\"%s\"],\n \"min_a1_dim3_hstar\": [%lld,%lld,%lld,%lld],\n",
            GLOB.bestA13, pstr(GLOB.bA13lam).c_str(), pstr(GLOB.bA13mu).c_str(), pstr(GLOB.bA13nu).c_str(),
            GLOB.bA13hs[0], GLOB.bA13hs[1], GLOB.bA13hs[2], GLOB.bA13hs[3]);
    fprintf(f, " \"min_a2_dim_ge2\": \"%lld/2\",\n \"min_a2_dim_ge2_witness\": [\"%s\",\"%s\",\"%s\"],\n",
            GLOB.minA2, pstr(GLOB.bA2lam).c_str(), pstr(GLOB.bA2mu).c_str(), pstr(GLOB.bA2nu).c_str());
    fprintf(f, " \"max_volume\": %lld,\n \"max_volume_witness\": [\"%s\",\"%s\",\"%s\"],\n \"max_volume_hstar\": [%lld,%lld,%lld,%lld],\n",
            GLOB.maxV, pstr(GLOB.bVlam).c_str(), pstr(GLOB.bVmu).c_str(), pstr(GLOB.bVnu).c_str(),
            GLOB.bVhs[0], GLOB.bVhs[1], GLOB.bVhs[2], GLOB.bVhs[3]);
    fprintf(f, " \"max_volume_hstar1_zero\": %lld,\n \"max_volume_hstar1_zero_witness\": [\"%s\",\"%s\",\"%s\"],\n \"max_volume_hstar1_zero_hstar\": [%lld,%lld,%lld,%lld],\n",
            GLOB.maxV0, pstr(GLOB.bV0lam).c_str(), pstr(GLOB.bV0mu).c_str(), pstr(GLOB.bV0nu).c_str(),
            GLOB.bV0hs[0], GLOB.bV0hs[1], GLOB.bV0hs[2], GLOB.bV0hs[3]);
    fprintf(f, " \"record_hstar2\": %lld,\n \"record_hstar2_witness\": [\"%s\",\"%s\",\"%s\"],\n",
            GLOB.maxH2, pstr(GLOB.bH2lam).c_str(), pstr(GLOB.bH2mu).c_str(), pstr(GLOB.bH2nu).c_str());
    fprintf(f, " \"dim3_hstar1_zero_count\": %lld,\n \"dim3_hstar1_zero_volume1_count\": %lld,\n",
            GLOB.nH1zero, GLOB.nH1zeroV1);
    fprintf(f, " \"max_vertex_denominator_audited\": %lld,\n \"verify_failures\": %lld,\n \"anomalies\": %lld,\n",
            GLOB.maxDen, GLOB.nVerifyFail, GLOB.nAnomaly);
    fprintf(f, " \"negatives\": [");
    for (size_t i = 0; i < GLOB.hits.size(); i++) {
        const Hit &h = GLOB.hits[i];
        fprintf(f, "%s\n  {\"lam\":\"%s\",\"mu\":\"%s\",\"nu\":\"%s\",\"dim\":%d,\"L\":[%lld,%lld,%lld,%lld,%lld,%lld],\"6a1\":%lld,\"2a2\":%lld,\"V\":%lld,\"hstar\":[%lld,%lld,%lld,%lld],\"verified\":%s}",
                i ? "," : "", pstr(h.lam).c_str(), pstr(h.mu).c_str(), pstr(h.nu).c_str(), h.rec.dim,
                h.rec.L[0], h.rec.L[1], h.rec.L[2], h.rec.L[3], h.rec.L[4], h.rec.L[5],
                h.rec.a1num, h.rec.a2num, h.rec.V, h.rec.hs[0], h.rec.hs[1], h.rec.hs[2], h.rec.hs[3],
                h.rec.verified ? "true" : "false");
    }
    std::string pw = perW;
    for (size_t i = 0; i < pw.size(); i++) if (pw[i] == '\n') pw[i] = '|';
    fprintf(f, "\n ],\n \"per_W\": \"%s\"\n}\n", pw.c_str());
    fclose(f);
    fprintf(stderr, "wrote %s\n", jf.c_str());
    return 0;
}
